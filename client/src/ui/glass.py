"""GlassFrame — a translucent rounded panel with specular highlight and a soft
diagonal reflection, emulating iOS "liquid glass"."""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QFrame

from ui import theme


class GlassFrame(QFrame):
    def __init__(self, parent=None, radius=26):
        super().__init__(parent)
        self._radius = radius
        self.setAttribute(Qt.WA_StyledBackground, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def setRadius(self, radius):
        self._radius = radius
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(r, self._radius, self._radius)

        dark = theme.current() == "dark"
        hi_a, lo_a = (46, 10) if dark else (215, 130)
        border_a = 54 if dark else 220
        streak_a = 22 if dark else 70
        top_hl_a = 90 if dark else 200

        # base translucent gradient (brighter top-left -> dimmer bottom-right)
        grad = QLinearGradient(r.topLeft(), r.bottomRight())
        grad.setColorAt(0.0, QColor(255, 255, 255, hi_a))
        grad.setColorAt(1.0, QColor(255, 255, 255, lo_a))
        p.fillPath(path, grad)

        # soft diagonal reflection streak
        p.save()
        p.setClipPath(path)
        streak = QLinearGradient(
            QPointF(r.left(), r.top() + r.height() * 0.15),
            QPointF(r.right(), r.top() + r.height() * 0.62),
        )
        streak.setColorAt(0.0, QColor(255, 255, 255, 0))
        streak.setColorAt(0.5, QColor(255, 255, 255, streak_a))
        streak.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.fillPath(path, streak)
        p.restore()

        # border
        pen = QPen(QColor(255, 255, 255, border_a))
        pen.setWidth(1)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)

        # crisp top specular highlight
        p.setPen(QPen(QColor(255, 255, 255, top_hl_a), 1))
        inset = max(3, self._radius * 0.4)
        p.drawLine(
            QPointF(r.left() + inset, r.top() + 1.5),
            QPointF(r.right() - inset, r.top() + 1.5),
        )

        p.end()
