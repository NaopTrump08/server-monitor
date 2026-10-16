"""Main application window — liquid-glass dashboard layout."""

import logging

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from background import AmbientBackground
from config import Config
from monitor import ServerMonitor
from ui import theme
from ui.card import ServerCard
from ui.format import format_rate
from ui.glass import GlassFrame
from ui.server_dialog import ServerDialog
from ui.trend import MetricIcon, TrendPanel
from ui.vnc_window import VNCWindow

log = logging.getLogger("main")


class LogoMark(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(44, 44)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect().adjusted(1, 1, -1, -1)
        grad = QLinearGradient(r.topLeft(), r.bottomRight())
        grad.setColorAt(0.0, QColor("#9b6cff"))
        grad.setColorAt(0.6, QColor("#4d7cff"))
        grad.setColorAt(1.0, QColor("#37c8ff"))
        p.setPen(Qt.NoPen)
        p.setBrush(grad)
        p.drawRoundedRect(r, 14, 14)

        pen = QPen(QColor("#ffffff"), 2.2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        w, h = self.width(), self.height()
        pts = [(0.16, 0.5), (0.38, 0.5), (0.48, 0.30), (0.58, 0.70), (0.68, 0.5), (0.86, 0.5)]
        path = QPainterPath()
        path.moveTo(pts[0][0] * w, pts[0][1] * h)
        for x, y in pts[1:]:
            path.lineTo(x * w, y * h)
        p.drawPath(path)
        p.end()


class MainWindow(QMainWindow):
    def __init__(self, config=None):
        super().__init__()
        self.setWindowTitle("Server Monitor")
        self.resize(1600, 1000)
        self.config = config or Config()
        self._cards = {}
        self._vnc_windows = []

        self.monitor = ServerMonitor(self.config)
        self.monitor.start()

        self._build_ui()
        self._rebuild_cards()
        self._apply_theme(self.config.theme, save=False)

        self._ui_timer = QTimer(self)
        self._ui_timer.timeout.connect(self._refresh_ui)
        self._ui_timer.start(1000)

        self._cfg_timer = QTimer(self)
        self._cfg_timer.timeout.connect(self._check_cfg_change)
        self._cfg_timer.start(2000)

    # ---------------------------------------------------------------- UI build
    def _build_ui(self):
        central = AmbientBackground()
        root = QHBoxLayout(central)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(18)

        # sidebar
        sidebar = GlassFrame(radius=26)
        sidebar.setFixedWidth(252)
        root.addWidget(sidebar)
        self._build_sidebar(sidebar)

        # right pane
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(18)
        root.addWidget(right, 1)
        self._build_right(right_lay)

        self.setCentralWidget(central)

    def _build_sidebar(self, sidebar):
        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(18, 24, 18, 24)
        lay.setSpacing(6)

        # logo
        logo_row = QHBoxLayout()
        logo_row.setSpacing(12)
        logo_row.addWidget(LogoMark())
        name_col = QVBoxLayout()
        name_col.setSpacing(1)
        brand = QLabel("Server Monitor")
        brand.setObjectName("brandName")
        sub = QLabel("服务器监控")
        sub.setObjectName("brandSub")
        name_col.addWidget(brand)
        name_col.addWidget(sub)
        logo_row.addLayout(name_col)
        logo_row.addStretch(1)
        lay.addLayout(logo_row)
        lay.addSpacing(22)

        nav_label = QLabel("导航")
        nav_label.setObjectName("navLabel")
        nav_label.setContentsMargins(10, 0, 0, 0)
        lay.addWidget(nav_label)
        lay.addSpacing(2)

        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)
        self._add_nav(lay, "总览", checked=True)
        self._add_nav(lay, "服务器")
        self._add_nav(lay, "远程桌面 VNC", on_click=self._open_vnc_nav)
        self._add_nav(lay, "告警中心", badge="2")
        self._add_nav(lay, "设置", on_click=self._open_settings)

        lay.addStretch(1)

        # user card
        user = GlassFrame(radius=16)
        user_lay = QHBoxLayout(user)
        user_lay.setContentsMargins(12, 10, 12, 10)
        user_lay.setSpacing(12)
        avatar = QLabel("B")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(40, 40)
        avatar.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #ff9a5a, stop:1 #ff5ea8);"
            " color: white; font-weight: 700; border-radius: 20px;"
        )
        user_lay.addWidget(avatar)
        uc = QVBoxLayout()
        uc.setSpacing(1)
        uname = QLabel("BossYu")
        uname.setObjectName("userName")
        umail = QLabel("管理员 · Pro")
        umail.setObjectName("userMail")
        uc.addWidget(uname)
        uc.addWidget(umail)
        user_lay.addLayout(uc)
        user_lay.addStretch(1)
        lay.addWidget(user)

    def _add_nav(self, lay, text, checked=False, badge=None, on_click=None):
        row = QHBoxLayout()
        row.setSpacing(0)
        b = QPushButton(text)
        b.setObjectName("navButton")
        b.setCheckable(True)
        b.setChecked(checked)
        b.setCursor(Qt.PointingHandCursor)
        if on_click:
            b.clicked.connect(on_click)
        self._nav_group.addButton(b)
        row.addWidget(b, 1)
        if badge:
            lab = QLabel(badge)
            lab.setAlignment(Qt.AlignCenter)
            lab.setFixedSize(24, 18)
            lab.setStyleSheet(
                "color: #ff8aa6; background: rgba(255,94,120,0.22);"
                " border: 1px solid rgba(255,94,120,0.35); border-radius: 9px; font-size: 11px; font-weight: 700;"
            )
            row.addWidget(lab)
        lay.addLayout(row)
        return b

    def _build_right(self, right_lay):
        # topbar
        topbar = GlassFrame(radius=26)
        topbar.setFixedHeight(86)
        top = QHBoxLayout(topbar)
        top.setContentsMargins(24, 16, 20, 16)
        top.setSpacing(14)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        self.title_lbl = QLabel("总览")
        self.title_lbl.setObjectName("appTitle")
        self.sub_lbl = QLabel("")
        self.sub_lbl.setObjectName("appSubtitle")
        title_col.addWidget(self.title_lbl)
        title_col.addWidget(self.sub_lbl)
        top.addLayout(title_col)
        top.addStretch(1)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索服务器、指标…")
        self.search_edit.setFixedWidth(300)
        self.search_edit.textChanged.connect(self._on_search)
        top.addWidget(self.search_edit)

        self.theme_btn = QPushButton("☀")
        self.theme_btn.setObjectName("iconButton")
        self.theme_btn.setFixedSize(44, 44)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self._toggle_theme)
        top.addWidget(self.theme_btn)

        add_btn = QPushButton("＋  添加服务器")
        add_btn.setObjectName("primaryButton")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._add_server)
        top.addWidget(add_btn)

        right_lay.addWidget(topbar)

        # tiles
        tiles = QHBoxLayout()
        tiles.setSpacing(18)
        self.tile_online_val, self.tile_online_trend = self._build_tile(tiles, "server", "#34c759", "在线服务器")
        self.tile_cpu_val, self.tile_cpu_trend = self._build_tile(tiles, "cpu", "#9b6cff", "平均 CPU 负载")
        self.tile_net_val, self.tile_net_trend = self._build_tile(tiles, "net", "#38e0ff", "总网络吞吐")
        right_lay.addLayout(tiles)

        # cards scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.NoFrame)
        self._scroll.viewport().setAutoFillBackground(False)
        self._container = QWidget()
        self._container.setAutoFillBackground(False)
        self._grid = QGridLayout(self._container)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setHorizontalSpacing(18)
        self._grid.setVerticalSpacing(18)
        for col in range(3):
            self._grid.setColumnStretch(col, 1)
        self._grid.setRowStretch(60, 1)

        self._empty_box = GlassFrame(radius=26)
        empty_lay = QVBoxLayout(self._empty_box)
        empty_lay.setContentsMargins(24, 40, 24, 40)
        empty_lay.setSpacing(8)
        et = QLabel("还没有服务器")
        et.setObjectName("appTitle")
        et.setAlignment(Qt.AlignCenter)
        eh = QLabel("点击右上角「添加服务器」，接入第一台主机。")
        eh.setObjectName("appSubtitle")
        eh.setAlignment(Qt.AlignCenter)
        empty_lay.addStretch(1)
        empty_lay.addWidget(et)
        empty_lay.addWidget(eh)
        empty_lay.addStretch(1)
        self._grid.addWidget(self._empty_box, 0, 0, 1, 3)
        self._empty_box.hide()

        self._scroll.setWidget(self._container)
        right_lay.addWidget(self._scroll, 1)

        # trend panel
        self.trend = TrendPanel()
        self.trend.setFixedHeight(300)
        right_lay.addWidget(self.trend)

    def _build_tile(self, layout, icon_kind, color, label):
        tile = GlassFrame(radius=24)
        tile.setFixedHeight(110)
        lay = QHBoxLayout(tile)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(14)
        icon = MetricIcon(icon_kind, color)
        lay.addWidget(icon)
        v = QVBoxLayout()
        v.setSpacing(1)
        val = QLabel("—")
        val.setObjectName("tileNum")
        lbl = QLabel(label)
        lbl.setObjectName("tileLbl")
        v.addWidget(val)
        v.addWidget(lbl)
        lay.addLayout(v)
        lay.addStretch(1)
        trend = QLabel("")
        trend.setObjectName("tileTrend")
        lay.addWidget(trend)
        layout.addWidget(tile, 1)
        return val, trend

    # ---------------------------------------------------------------- cards
    def _rebuild_cards(self):
        servers = self.config.servers
        while self._grid.count():
            item = self._grid.takeAt(0)
            w = item.widget()
            if w is not None and w is not self._empty_box:
                w.deleteLater()
        self._cards.clear()

        if not servers:
            self._grid.addWidget(self._empty_box, 0, 0, 1, 3)
            self._empty_box.show()
            return
        self._empty_box.hide()

        for i, s in enumerate(servers):
            card = ServerCard(i, on_vnc=self._open_vnc, on_edit=self._edit_server, on_delete=self._delete_server)
            card.set_server_config(s)
            row, col = divmod(i, 3)
            self._grid.addWidget(card, row, col)
            self._cards[i] = card

    def _check_cfg_change(self):
        if len(self.config.servers) != len(self._cards):
            self._rebuild_cards()

    def _refresh_ui(self):
        snapshot = self.monitor.snapshot()
        for sid, data in snapshot.items():
            card = self._cards.get(sid)
            if card:
                card.update_status(data)
        self.trend.update_data(snapshot)

        online = sum(1 for v in snapshot.values() if v.get("online"))
        total = len(snapshot)
        self.sub_lbl.setText(f"{online} / {total} 台服务器在线")

        # tiles
        self.tile_online_val.setText(f"{online} / {total}")
        if total and online == total:
            self.tile_online_trend.setText("● 健康")
            self.tile_online_trend.setStyleSheet("color: #34c759;")
        elif total:
            self.tile_online_trend.setText("● 部分离线")
            self.tile_online_trend.setStyleSheet("color: #ff9f0a;")
        else:
            self.tile_online_trend.setText("—")
            self.tile_online_trend.setStyleSheet("color: #8a8ea6;")

        data_list = [v.get("data") or {} for v in snapshot.values() if v.get("online")]
        n = len(data_list)
        if n:
            cpu = sum(d.get("cpu", {}).get("percent", 0) for d in data_list) / n
            rx = sum(d.get("network", {}).get("rx_rate", 0) for d in data_list)
            tx = sum(d.get("network", {}).get("tx_rate", 0) for d in data_list)
            self.tile_cpu_val.setText(f"{cpu:.0f}%")
            self.tile_net_val.setText(format_rate(rx + tx))
            if cpu < 50:
                self.tile_cpu_trend.setText("● 正常")
                self.tile_cpu_trend.setStyleSheet("color: #34c759;")
            elif cpu < 80:
                self.tile_cpu_trend.setText("● 偏高")
                self.tile_cpu_trend.setStyleSheet("color: #ff9f0a;")
            else:
                self.tile_cpu_trend.setText("● 告警")
                self.tile_cpu_trend.setStyleSheet("color: #ff3b30;")
            self.tile_net_trend.setText("● 实时")
            self.tile_net_trend.setStyleSheet("color: #38e0ff;")
        else:
            self.tile_cpu_val.setText("—")
            self.tile_net_val.setText("—")
            self.tile_cpu_trend.setText("")
            self.tile_net_trend.setText("")

    def _on_search(self, text):
        q = text.strip().lower()
        for sid, card in self._cards.items():
            s = self.config.get_server(sid) or {}
            hay = f"{s.get('name','')} {s.get('host','')}".lower()
            card.setVisible((not q) or (q in hay))

    # ---------------------------------------------------------------- actions
    def _add_server(self):
        dlg = ServerDialog(self)
        if dlg.exec():
            self.config.add_server(dlg.result_server())
            self._rebuild_cards()

    def _edit_server(self, server_id):
        cfg = self.config.get_server(server_id)
        if not cfg:
            return
        dlg = ServerDialog(self, server=cfg)
        if dlg.exec():
            if self.config.update_server(server_id, dlg.result_server()):
                self._rebuild_cards()

    def _delete_server(self, server_id):
        cfg = self.config.get_server(server_id)
        if not cfg:
            return
        name = cfg.get("name", cfg.get("host", "此服务器"))
        from PySide6.QtWidgets import QMessageBox
        ret = QMessageBox.question(self, "删除服务器", f"确定移除「{name}」吗？",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ret == QMessageBox.Yes:
            if self.config.remove_server(server_id):
                self._rebuild_cards()

    def _open_settings(self):
        dlg = SettingsDialog(self, current=self.config.refresh_interval)
        if dlg.exec():
            self._set_interval(dlg.interval())

    def _open_vnc(self, server_id):
        cfg = self.config.get_server(server_id)
        if not cfg:
            return
        if not cfg.get("vnc_port"):
            QMessageBox.information(self, "VNC", "该服务器未配置 VNC 端口。")
            return
        win = VNCWindow(cfg)
        self._vnc_windows.append(win)
        win.destroyed.connect(lambda: self._remove_vnc(win))
        win.show()
        win.raise_()
        win.activateWindow()

    def _open_vnc_nav(self):
        """Sidebar VNC entry: connect to the only VNC server, pick from a menu, or hint."""
        vnc_servers = [(i, s) for i, s in enumerate(self.config.servers) if s.get("vnc_port")]
        if not vnc_servers:
            QMessageBox.information(
                self,
                "远程桌面 VNC",
                "还没有配置 VNC 端口的服务器。\n\n"
                "点击服务器卡片上的「编辑」，填写 VNC 端口（默认 5901）后即可远程连接。",
            )
            return
        if len(vnc_servers) == 1:
            self._open_vnc(vnc_servers[0][0])
            return
        menu = QMenu(self)
        for i, s in vnc_servers:
            act = menu.addAction(f"{s.get('name') or s.get('host')}  ·  {s.get('host')}:{s.get('vnc_port')}")
            act.triggered.connect(lambda checked=False, sid=i: self._open_vnc(sid))
        btn = self.sender()
        if btn is not None:
            menu.exec(btn.mapToGlobal(QPoint(btn.width(), btn.height() // 2)))

    def _remove_vnc(self, win):
        if win in self._vnc_windows:
            self._vnc_windows.remove(win)

    def _set_interval(self, seconds):
        self.config.refresh_interval = seconds
        self.monitor.stop()
        self.monitor.start()

    def _apply_theme(self, mode, save=True):
        theme.apply_theme(QApplication.instance(), mode)
        if save:
            self.config.theme = mode
        self.theme_btn.setText("☀" if mode == "dark" else "☾")
        for card in self._cards.values():
            card.refresh_theme()
        self.repaint()

    def _toggle_theme(self):
        mode = "light" if theme.current() == "dark" else "dark"
        self._apply_theme(mode)

    def closeEvent(self, event):
        self.monitor.stop()
        for w in self._vnc_windows:
            try:
                w.close()
            except RuntimeError:
                pass
        super().closeEvent(event)


class SettingsDialog(QDialog):
    def __init__(self, parent=None, current=3):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setMinimumWidth(400)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(26, 24, 26, 24)
        lay.setSpacing(18)

        title = QLabel("设置")
        title.setObjectName("dialogTitle")
        lay.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        self._interval = QComboBox()
        for secs in (2, 3, 5, 10, 15):
            self._interval.addItem(f"{secs} 秒", secs)
        idx = self._interval.findData(current)
        self._interval.setCurrentIndex(idx if idx >= 0 else 1)
        form.addRow("刷新间隔", self._interval)
        lay.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def interval(self):
        return self._interval.currentData()
