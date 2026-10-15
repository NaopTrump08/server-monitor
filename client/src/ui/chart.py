"""AreaChart — a single-series smooth area chart (gradient fill + line + end dot)."""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget


class AreaChart(QWidget):
    def __init__(self, parent=None, color="#9b6cff"):
        super().__init__(parent)
        self._values = []
        self._color = QColor(color)
        self._fixed = None  # (lo, hi) or None for auto range
        self._show_endpoint = True
        self.setMinimumHeight(60)

    def set_values(self, values):
        self._values = list(values)
        self.update()

    def set_color(self, color):
        self._color = QColor(color)
        self.update()

    def set_fixed_range(self, lo, hi):
        self._fixed = (lo, hi)
        self.update()

    def _smooth_path(self, pts):
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
            c1x = x1 + (x2 - x0) / 6.0
            c1y = y1 + (y2 - y0) / 6.0
            c2x = x2 - (x3 - x1) / 6.0
            c2y = y2 - (y3 - y1) / 6.0
            path.cubicTo(c1x, c1y, c2x, c2y, x2, y2)
        return path

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(1, 2, -1, -2)
        if rect.width() <= 0 or rect.height() <= 0:
            p.end()
            return

        # baseline
        base_pen = QPen(QColor(255, 255, 255, 24))
        base_pen.setWidth(1)
        p.setPen(base_pen)
        p.drawLine(rect.bottomLeft(), rect.bottomRight())

        if len(self._values) < 2:
            p.end()
            return

        vals = self._values
        if self._fixed:
            lo, hi = self._fixed
        else:
            lo, hi = min(vals), max(vals)
        if hi - lo < 1e-6:
            hi = lo + 1.0

        n = len(vals)
        pts = []
        for i, v in enumerate(vals):
            x = rect.left() + i / (n - 1) * rect.width()
            y = rect.bottom() - (v - lo) / (hi - lo) * rect.height()
            pts.append((x, y))

        line_path = self._smooth_path(pts)

        # gradient area fill
        fill_path = QPainterPath(line_path)
        fill_path.lineTo(rect.right(), rect.bottom())
        fill_path.lineTo(rect.left(), rect.bottom())
        fill_path.closeSubpath()
        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        top = QColor(self._color)
        top.setAlpha(70)
        grad.setColorAt(0.0, top)
        grad.setColorAt(1.0, QColor(self._color.red(), self._color.green(), self._color.blue(), 0))
        p.fillPath(fill_path, grad)

        # line
        pen = QPen(self._color, 2.4)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawPath(line_path)

        # endpoint dot + halo
        if self._show_endpoint:
            ex, ey = pts[-1]
            p.setPen(QPen(QColor(self._color.red(), self._color.green(), self._color.blue(), 90), 1.4))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPointF(ex, ey), 8, 8)
            p.setPen(Qt.NoPen)
            p.setBrush(self._color)
            p.drawEllipse(QPointF(ex, ey), 4, 4)

        p.end()
