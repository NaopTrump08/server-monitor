"""RingGauge — a circular progress ring with track, coloured arc and centre text."""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui import theme


class RingGauge(QWidget):
    def __init__(self, parent=None, color="#9b6cff", thickness=12):
        super().__init__(parent)
        self._value = 0.0
        self._color = QColor(color)
        self._thickness = thickness
        self._suffix = "%"
        self.setMinimumSize(76, 76)

    def set_value(self, value):
        self._value = max(0.0, min(100.0, float(value)))
        self.update()

    def set_color(self, color):
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(self._thickness / 2 + 2,
                                           self._thickness / 2 + 2,
                                           -(self._thickness / 2 + 2),
                                           -(self._thickness / 2 + 2))
        track = QColor(255, 255, 255, 30)
        pen = QPen(track, self._thickness)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.drawArc(rect, 0, 360 * 16)

        if self._value > 0:
            pen.setColor(self._color)
            p.setPen(pen)
            p.drawArc(rect, 90 * 16, -int(360 * self._value / 100.0 * 16))

        # centre value
        dark = theme.current() == "dark"
        p.setPen(QColor(theme.tokens()["text"]))
        font = QFont()
        font.setPixelSize(int(self.height() * 0.26))
        font.setWeight(QFont.DemiBold)
        p.setFont(font)
        p.drawText(self.rect(), Qt.AlignCenter, str(int(round(self._value))))
        p.end()
