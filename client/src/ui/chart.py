"""Lightweight live chart widget drawn with QPainter."""

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget


class LiveChart(QWidget):
    """Multi-series line chart. data: list of (ts, v1, v2, v3, v4)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []
        self._labels = []
        self._colors = []
        self._keys = []
        self._max_points = 120
        self.setMinimumHeight(140)
        self.setObjectName("chartWidget")

    def setSeries(self, keys, labels, colors):
        self._keys = keys
        self._labels = labels
        self._colors = colors
        self.update()

    def setData(self, data):
        self._data = data[-self._max_points:]
        self.update()

    def _series_values(self, idx):
        return [row[idx + 1] for row in self._data]

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(4, 4, -4, -4)

        # background
        p.fillRect(rect, QColor("#1a2235"))

        if not self._data or not self._keys:
            p.setPen(QColor("#5b657a"))
            p.drawText(rect, Qt.AlignCenter, "Waiting for data...")
            return

        # grid
        grid_pen = QPen(QColor("#232c40"))
        grid_pen.setWidth(1)
        p.setPen(grid_pen)
        for i in range(1, 4):
            y = rect.top() + rect.height() * i / 4
            p.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))

        # value range
        all_vals = []
        for idx in range(len(self._keys)):
            all_vals.extend(self._series_values(idx))
        if not all_vals:
            return
        vmax = max(all_vals) * 1.05 or 1
        vmin = 0

        def y_of(v):
            if vmax == vmin:
                return rect.bottom()
            return rect.bottom() - (v - vmin) / (vmax - vmin) * rect.height()

        def x_of(i):
            n = len(self._data)
            if n <= 1:
                return rect.left() + rect.width() / 2
            return rect.left() + i / (n - 1) * rect.width()

        # draw series
        for si, key in enumerate(self._keys):
            vals = self._series_values(si)
            color = QColor(self._colors[si] if si < len(self._colors) else "#3b82f6")
            pen = QPen(color)
            pen.setWidth(2)
            p.setPen(pen)
            path = QPainterPath()
            for i, v in enumerate(vals):
                x = x_of(i)
                y = y_of(v)
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            p.drawPath(path)

            # last point dot
            if vals:
                last_x = x_of(len(vals) - 1)
                last_y = y_of(vals[-1])
                p.setBrush(color)
                p.setPen(Qt.NoPen)
                p.drawEllipse(QRectF(last_x - 3, last_y - 3, 6, 6))

        # legend
        font = QFont()
        font.setPointSize(8)
        p.setFont(font)
        x = rect.left() + 8
        for si, label in enumerate(self._labels):
            color = QColor(self._colors[si] if si < len(self._colors) else "#3b82f6")
            p.setPen(Qt.NoPen)
            p.setBrush(color)
            p.drawRect(x, rect.top() + 6, 8, 8)
            p.setPen(QColor("#c3ccdb"))
            p.drawText(x + 12, rect.top() + 14, label)
            x += 12 + p.fontMetrics().horizontalAdvance(label) + 16

        p.end()
