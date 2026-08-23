"""Lightweight live chart widget drawn with QPainter."""

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from . import theme


class LiveChart(QWidget):
    """Multi-series line chart. data: list of (ts, v1, v2, v3, v4)."""

    def __init__(self, parent=None, column=None):
        super().__init__(parent)
        self._data = []
        self._labels = []
        self._colors = []
        self._keys = []
        self._column = column
        self._max_points = 120
        self._normalize = False
        self.setMinimumHeight(140)
        self.setObjectName("chartWidget")

    def setSeries(self, keys, labels, colors, normalize=False):
        self._keys = keys
        self._labels = labels
        self._colors = colors
        self._normalize = normalize
        self.update()

    def setData(self, data):
        self._data = data[-self._max_points:]
        self.update()

    def _series_values(self, idx):
        if self._column is not None:
            return [row[self._column] for row in self._data if len(row) > self._column]
        return [row[idx + 1] for row in self._data]

    def _smooth_path(self, pts):
        """Catmull-Rom -> cubic Bezier smoothing of the given (x, y) points."""
        path = QPainterPath()
        n = len(pts)
        if n == 0:
            return path
        path.moveTo(pts[0][0], pts[0][1])
        if n == 1:
            return path
        for i in range(n - 1):
            x0, y0 = pts[i - 1] if i > 0 else pts[i]
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            x3, y3 = pts[i + 2] if i + 2 < n else pts[i + 1]
            c1x = x1 + (x2 - x0) / 6
            c1y = y1 + (y2 - y0) / 6
            c2x = x2 - (x3 - x1) / 6
            c2y = y2 - (y3 - y1) / 6
            path.cubicTo(c1x, c1y, c2x, c2y, x2, y2)
        return path

    def paintEvent(self, event):
        tk = theme.tokens()
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(4, 4, -4, -4)

        # background
        p.fillRect(rect, QColor(tk["chart_bg"]))

        if not self._data or not self._keys:
            p.setPen(QColor(tk["chart_empty"]))
            p.drawText(rect, Qt.AlignCenter, "Waiting for data...")
            return

        # grid
        grid_pen = QPen(QColor(tk["chart_grid"]))
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

        def series_points(si):
            vals = self._series_values(si)
            pts = []
            for i, v in enumerate(vals):
                x = x_of(i)
                if self._normalize:
                    smax = max(vals) or 1
                    y = rect.bottom() - (v / smax) * rect.height()
                else:
                    y = y_of(v)
                pts.append((x, y))
            return pts

        # draw series (fill first, then line on top)
        for si, key in enumerate(self._keys):
            color = QColor(self._colors[si] if si < len(self._colors) else "#7b4dff")
            pts = series_points(si)
            if len(pts) < 2:
                continue
            line_path = self._smooth_path(pts)

            # gradient area fill
            fill_path = QPainterPath(line_path)
            fill_path.lineTo(rect.right(), rect.bottom())
            fill_path.lineTo(rect.left(), rect.bottom())
            fill_path.closeSubpath()
            grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            top = QColor(color)
            top.setAlpha(70)
            grad.setColorAt(0.0, top)
            grad.setColorAt(1.0, QColor(tk["chart_bg"]))
            p.fillPath(fill_path, grad)

            # smooth line
            pen = QPen(color)
            pen.setWidth(2)
            p.setPen(pen)
            p.drawPath(line_path)

            # last point dot
            last_x, last_y = pts[-1]
            p.setBrush(color)
            p.setPen(Qt.NoPen)
            p.drawEllipse(QRectF(last_x - 3, last_y - 3, 6, 6))

        # legend (skip for single-series mini charts, which carry their own header)
        if len(self._labels) > 1:
            font = QFont()
            font.setPointSize(8)
            p.setFont(font)
            x = rect.left() + 8
            for si, label in enumerate(self._labels):
                color = QColor(self._colors[si] if si < len(self._colors) else "#7b4dff")
                p.setPen(Qt.NoPen)
                p.setBrush(color)
                p.drawRoundedRect(QRectF(x, rect.top() + 6, 8, 8), 2, 2)
                p.setPen(QColor(tk["chart_legend"]))
                p.drawText(x + 12, rect.top() + 14, label)
                x += 12 + p.fontMetrics().horizontalAdvance(label) + 16

        p.end()
