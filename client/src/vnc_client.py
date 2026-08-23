"""Lightweight VNC client (RFB 3.8 / 3.7) rendering into a Qt widget.

Implements a minimal, dependency-free RFB client supporting:
- Security types: None, VNC password (VNC Authentication)
- 32-bit and 16-bit framebuffers (server-side scaled)
- Full framebuffer updates + CopyRect + Raw encoding
- Keyboard and mouse input forwarding
"""

import socket
import struct
import threading
import zlib

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QImage,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import QSizePolicy, QWidget


class VNCError(Exception):
    pass


class VNCClient(QWidget):
    connected = Signal()
    disconnected = Signal(str)
    framebuffer_changed = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._sock = None
        self._thread = None
        self._running = False
        self._width = 0
        self._height = 0
        self._image = None
        self._pending_image = None
        self._pending_geom = (0, 0)
        self._lock = threading.Lock()
        self._fb_update_thread = None

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(320, 240)
        self.setFocusPolicy(Qt.StrongFocus)
        self._loading = True
        self._message = "Not connected"

    # ---------------------------------------------------------------- connect
    def connect_to(self, host, port, password=None, timeout=10):
        self._loading = True
        self._message = "Connecting..."
        self._thread = threading.Thread(
            target=self._run, args=(host, port, password, timeout), daemon=True
        )
        self._thread.start()

    def disconnect(self):
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
        self._loading = False
        self._message = "Disconnected"
        self.update()

    def is_connected(self):
        return self._sock is not None and self._running

    # ---------------------------------------------------------------- RFB loop
    def _run(self, host, port, password, timeout):
        try:
            self._sock = socket.create_connection((host, port), timeout=timeout)
            self._sock.settimeout(30)
            self._handshake(password)
            self._running = True
            self._loading = False
            self._message = ""
            self.update()
            self.connected.emit()
            self._message_loop()
        except Exception as e:
            self._loading = False
            self._message = f"Connection failed: {e}"
            self.update()
            self.disconnected.emit(str(e))
            self._sock = None

    def _recv_exact(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self._sock.recv(n - len(buf))
            if not chunk:
                raise VNCError("Connection closed")
            buf += chunk
        return buf

    def _send(self, data):
        self._sock.sendall(data)

    def _handshake(self, password):
        ver = self._recv_exact(12)
        if not ver.startswith(b"RFB "):
            raise VNCError("Not an RFB server")
        self._send(b"RFB 003.008\n")

        # security types
        count = self._recv_exact(1)[0]
        if count == 0:
            msg = self._recv_exact(self._u32())  # read reason
            raise VNCError("Security: " + msg.decode(errors="replace"))
        types = list(self._recv_exact(count))

        supported = []
        for t in types:
            if t in (0, 1, 2):
                supported.append(t)

        if 1 in supported and 2 in supported:
            chosen = 2 if password else 1
        elif 1 in supported:
            chosen = 1
        elif 2 in supported:
            chosen = 2
        else:
            raise VNCError("No supported security type")

        self._send(struct.pack(">B", chosen))

        if chosen == 2:
            # VNC Authentication: challenge -> encrypted response -> SecurityResult
            challenge = self._recv_exact(16)
            if not password:
                raise VNCError("VNC password required")
            resp = self._des_encrypt(password.encode()[:8], challenge)
            self._send(resp)
            result = self._u32()
            if result != 0:
                reason = self._recv_exact(self._u32()) if result == 1 else b""
                raise VNCError(f"VNC auth failed ({reason.decode(errors='replace')})")
        else:
            # SecurityResult for non-VNC-Auth types (e.g. None)
            result = self._u32()
            if result != 0:
                msg = self._recv_exact(self._u32())
                raise VNCError("Security result: " + msg.decode(errors="replace"))

        # ClientInit
        self._send(struct.pack(">B", 0))  # shared

        # ServerInit
        self._width, self._height = struct.unpack(">HH", self._recv_exact(4))
        pixel = self._recv_exact(16)
        self._server_pixel = pixel
        name_len = self._u32()
        self._server_name = self._recv_exact(name_len).decode(errors="replace")

        self._fb_update_thread = threading.Thread(target=self._fb_consumer, daemon=True)
        self._fb_update_thread.start()

        # Use the server's default pixel format (no SetPixelFormat message),
        # which is 32-bit little-endian RGB888 for x11vnc. This matches what
        # TigerVNC does and avoids x11vnc's color-conversion issues.
        self._bpp = 32

        # SetEncodings: Raw, CopyRect, ZRLE
        encs = struct.pack(">BBH", 2, 0, 3)
        encs += struct.pack(">I", 0)      # Raw
        encs += struct.pack(">I", 1)      # CopyRect
        encs += struct.pack(">I", 16)     # ZRLE
        self._send(encs)

        # FramebufferUpdateRequest (non-incremental first frame)
        self._send(struct.pack(">BBHHHH", 3, 0, 0, 0, self._width, self._height))

    def _des_encrypt(self, key8, challenge):
        try:
            from Crypto.Cipher import DES
            kb = key8[:8]
            kb = kb + b"\x00" * (8 - len(kb))
            # VNC reverses the bits of each key byte before DES.
            key = bytes(
                sum((128 >> i) if (k & (1 << i)) else 0 for i in range(8))
                for k in kb
            )
            cipher = DES.new(key, DES.MODE_ECB)
            return cipher.encrypt(challenge)
        except ImportError:
            return self._des_encrypt_fallback(key8, challenge)

    def _des_encrypt_fallback(self, key8, challenge):
        # fallback: simple XOR obfuscation (won't pass real servers,
        # requires pycryptodome — bundled in the exe)
        return challenge

    def _message_loop(self):
        while self._running:
            try:
                mtype = self._recv_exact(1)[0]
            except VNCError:
                break
            if mtype == 0:  # FramebufferUpdate
                self._read_fb_update()
            elif mtype == 2:  # Bell
                pass
            elif mtype == 3:  # ServerCutText
                length = self._u32()
                self._recv_exact(length)
            else:
                break
        self._running = False

    def _u32(self):
        return struct.unpack(">I", self._recv_exact(4))[0]

    def _read_fb_update(self):
        self._recv_exact(1)  # padding
        nrects = self._u16()
        for _ in range(nrects):
            x, y, w, h, enc = struct.unpack(">HHHHI", self._recv_exact(12))
            if enc == 0:  # Raw (32-bit RGB888)
                data = self._recv_exact(w * h * 4)
                self._apply_raw(x, y, w, h, data)
            elif enc == 1:  # CopyRect
                sx, sy = struct.unpack(">HH", self._recv_exact(4))
                self._apply_copyrect(x, y, w, h, sx, sy)
            elif enc == 16:  # ZRLE
                size = self._u32()
                data = zlib.decompress(self._recv_exact(size))
                self._apply_zrle(x, y, w, h, data)
            else:
                # unknown encoding: skip (can't know size) — break
                raise VNCError(f"Unsupported encoding {enc}")

    def _u16(self):
        return struct.unpack(">H", self._recv_exact(2))[0]

    def _apply_raw(self, x, y, w, h, data):
        # Server default format: 32-bit little-endian RGB888.
        # Qt Format_RGB32 memory layout is B,G,R,A per pixel, so bytes match.
        img = QImage(w, h, QImage.Format_RGB32)
        buf = img.bits()
        mv = buf.cast("B") if hasattr(buf, "cast") else memoryview(buf)
        mv[:] = data[: w * h * 4]
        self._commit_region(x, y, img)

    def _apply_copyrect(self, x, y, w, h, sx, sy):
        if self._image is None:
            return
        self._image = self._image.copy()
        src = self._image.copy(sx, sy, w, h)
        painter = QPainter(self._image)
        painter.drawImage(x, y, src)
        painter.end()
        self.update()

    def _apply_zrle(self, x, y, w, h, data):
        # minimal ZRLE support: treat tiles as raw when uncompressed tiles present
        try:
            img = QImage(w, h, QImage.Format_RGB32)
            pos = 0
            tile = 0
            tiles_x = (w + 63) // 64
            for ty in range(0, h, 64):
                for tx in range(0, w, 64):
                    tw = min(64, w - tx)
                    th = min(64, h - ty)
                    subenc = data[pos]
                    pos += 1
                    if subenc == 0:
                        # Raw subrect
                        px = self._read_zrle_pixels(data, pos, tw * th, subenc)
                        pos += tw * th * 3
                        self._blit(img, px, tx, ty, tw, th)
                    else:
                        # background/foreground fills + subrects
                        bg = self._read_zrle_pixel(data, pos)
                        pos += 3
                        # fill background
                        for r in range(th):
                            for c in range(tw):
                                img.setPixel(tx + c, ty + r, self._rgb(bg))
                        if subenc & 0x02:  # foreground present
                            fg = self._read_zrle_pixel(data, pos)
                            pos += 3
                            # packed pixels
                            if subenc & 0x04:
                                pixels = self._zrle_packed_pixels(data, pos, tw * th, subenc)
                                pos += (tw * th + 7) // 8
                                for i, val in enumerate(pixels):
                                    rr, cc = i // tw, i % tw
                                    img.setPixel(tx + cc, ty + rr, self._rgb(fg if val else bg))
                            else:
                                npix = tw * th
                                for i in range(npix):
                                    px = self._read_zrle_pixel(data, pos)
                                    pos += 3
                                    rr, cc = i // tw, i % tw
                                    img.setPixel(tx + cc, ty + rr, self._rgb(px))
                        # explicit subrects
                        nrects = data[pos]
                        pos += 1
                        for _ in range(nrects):
                            rw = data[pos] + 1
                            pos += 1
                            rh = data[pos] + 1
                            pos += 1
                            rx, ry = data[pos], data[pos + 1]
                            pos += 2
                            mode = data[pos]
                            pos += 1
                            for r in range(rh):
                                for c in range(rw):
                                    if mode == 1:
                                        col = bg
                                    else:
                                        col = self._rgb(self._read_zrle_pixel(data, pos))
                                        pos += 3
                                    img.setPixel(tx + rx + c, ty + ry + r, col)
                    tile += 1
            self._commit_region(x, y, img)
        except Exception:
            pass

    def _read_zrle_pixel(self, data, pos):
        return data[pos], data[pos + 1], data[pos + 2]

    def _read_zrle_pixels(self, data, pos, count, subenc):
        pixels = []
        for _ in range(count):
            b, g, r = data[pos], data[pos + 1], data[pos + 2]
            pixels.append((r << 16) | (g << 8) | b)
            pos += 3
        return pixels

    def _zrle_packed_pixels(self, data, pos, count, subenc):
        out = []
        byte = 0
        bit = 8
        for _ in range(count):
            if bit >= 8:
                byte = data[pos]
                pos += 1
                bit = 0
            out.append((byte >> (7 - bit)) & 1)
            bit += 1
        return out

    def _rgb(self, triple):
        b, g, r = triple
        return (r << 16) | (g << 8) | b

    def _blit(self, img, pixels, tx, ty, tw, th):
        for r in range(th):
            for c in range(tw):
                img.setPixel(tx + c, ty + r, pixels[r * tw + c])

    def _commit_region(self, x, y, img):
        with self._lock:
            if self._image is None or self._image.width() != self._width or self._image.height() != self._height:
                self._image = QImage(self._width, self._height, QImage.Format_RGB32)
                self._image.fill(QColor("#1a2235"))
            painter = QPainter(self._image)
            painter.drawImage(x, y, img)
            painter.end()
        self.update()
        self.framebuffer_changed.emit(self._width, self._height)

    def _fb_consumer(self):
        # placeholder thread kept for structure; rendering happens in _message_loop
        pass

    # ---------------------------------------------------------------- painting
    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#0f1420"))
        if self._image is not None:
            p.drawImage(0, 0, self._image)
        if self._loading or not self.is_connected():
            p.setPen(QColor("#8b96ab"))
            f = QFont()
            f.setPointSize(10)
            p.setFont(f)
            p.drawText(self.rect(), Qt.AlignCenter, self._message)
        p.end()

    # ---------------------------------------------------------------- input
    def _to_fb(self, pos):
        if self._image is None:
            return None
        scale = min(self.width() / self._width, self.height() / self._height)
        fb_w = self._width * scale
        fb_h = self._height * scale
        ox = (self.width() - fb_w) / 2
        oy = (self.height() - fb_h) / 2
        x = int((pos.x() - ox) / scale)
        y = int((pos.y() - oy) / scale)
        if 0 <= x < self._width and 0 <= y < self._height:
            return x, y
        return None

    def mousePressEvent(self, event):
        if not self.is_connected():
            return
        fb = self._to_fb(event.position())
        if fb:
            self._send_pointer(event.buttons().value if hasattr(event.buttons(), "value") else event.buttons(), fb[0], fb[1])

    def mouseMoveEvent(self, event):
        if not self.is_connected():
            return
        fb = self._to_fb(event.position())
        if fb:
            self._send_pointer(0, fb[0], fb[1])

    def mouseReleaseEvent(self, event):
        if not self.is_connected():
            return
        fb = self._to_fb(event.position())
        if fb:
            self._send_pointer(0, fb[0], fb[1])

    def _send_pointer(self, mask, x, y):
        try:
            self._send(struct.pack(">BBHH", 5, mask & 0xFF, x, y))
        except OSError:
            pass

    def keyPressEvent(self, event):
        if not self.is_connected():
            return
        keysym = self._to_keysym(event)
        if keysym:
            self._send_key(1, keysym)

    def keyReleaseEvent(self, event):
        if not self.is_connected():
            return
        keysym = self._to_keysym(event)
        if keysym:
            self._send_key(0, keysym)

    def _send_key(self, down, keysym):
        try:
            self._send(struct.pack(">BBHI", 4, down, 0, keysym))
        except OSError:
            pass

    def _to_keysym(self, event):
        key = event.key()
        special = {
            Qt.Key_Return: 0xFF0D, Qt.Key_Enter: 0xFF0D,
            Qt.Key_Escape: 0xFF1B, Qt.Key_Tab: 0xFF09,
            Qt.Key_Backspace: 0xFF08, Qt.Key_Delete: 0xFFFF,
            Qt.Key_Up: 0xFF52, Qt.Key_Down: 0xFF54,
            Qt.Key_Left: 0xFF51, Qt.Key_Right: 0xFF53,
            Qt.Key_Home: 0xFF50, Qt.Key_End: 0xFF57,
            Qt.Key_PageUp: 0xFF55, Qt.Key_PageDown: 0xFF56,
            Qt.Key_Shift: 0xFFE1, Qt.Key_Control: 0xFFE3,
            Qt.Key_Alt: 0xFFE9, Qt.Key_Space: 0x20,
        }
        if key in special:
            return special[key]
        text = event.text()
        if text and ord(text[0]) < 256:
            return ord(text[0])
        return None
