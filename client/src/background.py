"""Ambient background widget — paints the dark/light base and glowing colour
blobs that the translucent glass panels refract."""

from PySide6.QtGui import QColor, QPainter, QRadialGradient
from PySide6.QtWidgets import QWidget

from ui import theme


class AmbientBackground(QWidget):
    """Paints the ambient glow. NOTE: must NOT set WA_TransparentForMouseEvents
    here — it is the parent of every interactive widget and that attribute
    would swallow mouse events for the whole window (all children included)."""

    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            p.end()
            return

        dark = theme.current() == "dark"
        p.fillRect(self.rect(), QColor(theme.tokens()["window_bg"]))

        if dark:
            blobs = [
                (0.04, -0.02, 0.46, (124, 77, 255, 160)),
                (0.93, 0.06, 0.42, (47, 107, 255, 140)),
                (0.28, 1.02, 0.46, (193, 59, 255, 130)),
                (0.74, 1.04, 0.34, (255, 77, 158, 95)),
                (0.46, 0.10, 0.28, (30, 200, 255, 70)),
            ]
        else:
            blobs = [
                (0.04, -0.02, 0.46, (124, 77, 255, 55)),
                (0.93, 0.06, 0.42, (47, 107, 255, 50)),
                (0.28, 1.02, 0.46, (255, 120, 200, 45)),
                (0.74, 1.04, 0.34, (255, 170, 90, 40)),
                (0.46, 0.10, 0.28, (30, 200, 255, 38)),
            ]

        span = max(w, h)
        for (cx, cy, radius, (r, g, b, a)) in blobs:
            grad = QRadialGradient(cx * w, cy * h, radius * span)
            core = QColor(r, g, b, a)
            edge = QColor(r, g, b, 0)
            grad.setColorAt(0.0, core)
            grad.setColorAt(1.0, edge)
            p.fillRect(self.rect(), grad)

        p.end()
