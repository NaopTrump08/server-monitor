"""TrendPanel — three self-contained metric cards (CPU / 内存 / 网络) with big
current values, status badges and solo area charts. Aggregates across servers."""

from collections import deque

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .chart import AreaChart
from .format import format_rate
from .glass import GlassFrame


class MetricIcon(QWidget):
    """Rounded chip with a simple CPU / RAM / network glyph."""

    def __init__(self, kind, color, parent=None):
        super().__init__(parent)
        self._kind = kind
        self._color = QColor(color)
        self.setFixedSize(34, 34)

    def set_color(self, color):
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)

        # chip background
        bg = QColor(self._color)
        bg.setAlpha(42)
        p.setPen(Qt.NoPen)
        p.setBrush(bg)
        p.drawRoundedRect(r, 11, 11)

        pen = QPen(self._color, 1.7)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        cx, cy = self.width() / 2.0, self.height() / 2.0
        s = self.width() / 2.0

        if self._kind == "cpu":
            p.drawRoundedRect(QRectF(cx - s * 0.42, cy - s * 0.42, s * 0.84, s * 0.84), 3, 3)
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                p.drawLine(QPointF(cx + dx * s * 0.68, cy + dy * s * 0.68),
                           QPointF(cx + dx * s * 1.12, cy + dy * s * 1.12))
        elif self._kind == "mem":
            p.drawRoundedRect(QRectF(cx - s * 0.6, cy - s * 0.46, s * 1.2, s * 0.92), 3, 3)
            for t in (-0.26, 0.0, 0.26):
                p.drawLine(QPointF(cx + s * 0.6 * t, cy - s * 0.46 + 2),
                           QPointF(cx + s * 0.6 * t, cy + s * 0.46 - 2))
        elif self._kind == "server":
            p.drawRoundedRect(QRectF(cx - s * 0.62, cy - s * 0.52, s * 1.24, s * 0.44), 2, 2)
            p.drawRoundedRect(QRectF(cx - s * 0.62, cy + s * 0.08, s * 1.24, s * 0.44), 2, 2)
        elif self._kind == "net":
            p.drawLine(QPointF(cx, cy - s * 0.7), QPointF(cx, cy + s * 0.7))
            p.drawLine(QPointF(cx - s * 0.34, cy - s * 0.3), QPointF(cx, cy - s * 0.7))
            p.drawLine(QPointF(cx + s * 0.34, cy - s * 0.3), QPointF(cx, cy - s * 0.7))
            p.drawLine(QPointF(cx - s * 0.34, cy + s * 0.3), QPointF(cx, cy + s * 0.7))
            p.drawLine(QPointF(cx + s * 0.34, cy + s * 0.3), QPointF(cx, cy + s * 0.7))
        p.end()


class MetricCard(GlassFrame):
    def __init__(self, title, kind, color, parent=None):
        super().__init__(parent, radius=22)
        self._title = title
        self._kind = kind
        self._color = color
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 14)
        lay.setSpacing(8)

        # row 1: icon + name + status badge
        head = QHBoxLayout()
        head.setSpacing(10)
        self.icon = MetricIcon(self._kind, self._color)
        self.name_lbl = QLabel(self._title)
        self.name_lbl.setObjectName("metricName")
        head.addWidget(self.icon)
        head.addWidget(self.name_lbl)
        head.addStretch(1)
        self.status_lbl = QLabel("—")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        head.addWidget(self.status_lbl)
        lay.addLayout(head)

        # row 2: big value + delta
        self.value_lbl = QLabel("—")
        self.value_lbl.setObjectName("metricValue")
        lay.addWidget(self.value_lbl)
        self.delta_lbl = QLabel("")
        self.delta_lbl.setObjectName("metricDelta")
        self.delta_lbl.setStyleSheet(f"color: {self._color};")
        lay.addWidget(self.delta_lbl)

        # row 3: area chart
        self.chart = AreaChart(color=self._color)
        lay.addWidget(self.chart, 1)

        # row 4: note
        self.note_lbl = QLabel("")
        self.note_lbl.setObjectName("metricNote")
        lay.addWidget(self.note_lbl)

    def set_status(self, text, color):
        self.status_lbl.setText(text)
        self.status_lbl.setStyleSheet(
            f"color: {color}; background: rgba({self._rgb(color)}, 0.24);"
            f" border: 1px solid rgba({self._rgb(color)}, 0.5);"
            f" border-radius: 11px; padding: 3px 10px; font-size: 11px; font-weight: 600;"
        )

    @staticmethod
    def _rgb(color):
        c = QColor(color)
        return f"{c.red()}, {c.green()}, {c.blue()}"

    def update_metric(self, value_text, delta_text, values, note):
        self.value_lbl.setText(value_text)
        self.delta_lbl.setText(delta_text)
        self.chart.set_values(values)
        self.note_lbl.setText(note)


class TrendPanel(GlassFrame):
    def __init__(self, parent=None):
        super().__init__(parent, radius=26)
        self._cpu_hist = deque(maxlen=120)
        self._mem_hist = deque(maxlen=120)
        self._net_hist = deque(maxlen=120)
        self._prev_cpu = None
        self._prev_mem = None
        self._prev_net = None
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 18, 24, 18)
        lay.setSpacing(14)

        head = QHBoxLayout()
        title = QLabel("实时负载趋势")
        title.setObjectName("sectionTitle")
        head.addWidget(title)
        self.sub_lbl = QLabel("最近 30 分钟 · 每 3 秒刷新")
        self.sub_lbl.setObjectName("appSubtitle")
        head.addWidget(self.sub_lbl)
        head.addStretch(1)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        for text, checked in (("30 分钟", True), ("1 小时", False), ("24 小时", False)):
            b = QPushButton(text)
            b.setObjectName("ghostButton")
            b.setCheckable(True)
            b.setChecked(checked)
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedWidth(72)
            self._group.addButton(b)
            head.addWidget(b)
        lay.addLayout(head)

        cards = QHBoxLayout()
        cards.setSpacing(18)
        self.cpu_card = MetricCard("CPU", "cpu", "#a78bfa")
        self.mem_card = MetricCard("内存", "mem", "#34d399")
        self.net_card = MetricCard("网络", "net", "#fbbf24")
        self.cpu_card.chart.set_fixed_range(0, 100)
        self.mem_card.chart.set_fixed_range(0, 100)
        cards.addWidget(self.cpu_card, 1)
        cards.addWidget(self.mem_card, 1)
        cards.addWidget(self.net_card, 1)
        lay.addLayout(cards, 1)

    def _threshold(self, pct):
        if pct < 50:
            return "正常", "#34c759"
        if pct < 80:
            return "偏高", "#ff9f0a"
        return "告警", "#ff3b30"

    def update_data(self, snapshot):
        online = [v for v in snapshot.values() if v.get("online")]
        n = len(online)

        if n == 0:
            self.cpu_card.set_status("离线", "#8a8ea6")
            self.mem_card.set_status("离线", "#8a8ea6")
            self.net_card.set_status("离线", "#8a8ea6")
            self.cpu_card.update_metric("—", "", [], "")
            self.mem_card.update_metric("—", "", [], "")
            self.net_card.update_metric("—", "", [], "")
            return

        data_list = [v.get("data") or {} for v in online]
        cpu = sum(d.get("cpu", {}).get("percent", 0) for d in data_list) / n
        mem = sum(d.get("memory", {}).get("percent", 0) for d in data_list) / n
        rx = sum(d.get("network", {}).get("rx_rate", 0) for d in data_list)
        tx = sum(d.get("network", {}).get("tx_rate", 0) for d in data_list)
        net = rx + tx

        self._cpu_hist.append(cpu)
        self._mem_hist.append(mem)
        self._net_hist.append(net)

        # deltas
        cpu_d = cpu - (self._prev_cpu if self._prev_cpu is not None else cpu)
        mem_d = mem - (self._prev_mem if self._prev_mem is not None else mem)
        net_d = net - (self._prev_net if self._prev_net is not None else net)
        self._prev_cpu, self._prev_mem, self._prev_net = cpu, mem, net

        def arrow(v):
            return "↑" if v >= 0 else "↓"

        # CPU
        s_cpu, c_cpu = self._threshold(cpu)
        self.cpu_card.set_status(s_cpu, c_cpu)
        self.cpu_card.update_metric(
            f"{cpu:.0f}%",
            f"{arrow(cpu_d)} {abs(cpu_d):.1f}%",
            list(self._cpu_hist),
            self._note(self._cpu_hist, "%"),
        )
        # 内存
        s_mem, c_mem = self._threshold(mem)
        self.mem_card.set_status(s_mem, c_mem)
        self.mem_card.update_metric(
            f"{mem:.0f}%",
            f"{arrow(mem_d)} {abs(mem_d):.1f}%",
            list(self._mem_hist),
            self._note(self._mem_hist, "%"),
        )
        # 网络
        self.net_card.set_status("繁忙" if net > 1e9 else "正常", "#38e0ff" if net > 1e9 else "#34c759")
        self.net_card.update_metric(
            format_rate(net),
            f"{arrow(net_d)} {format_rate(abs(net_d))}",
            list(self._net_hist),
            f"下行 {format_rate(rx)} · 上行 {format_rate(tx)}",
        )

    @staticmethod
    def _note(hist, unit):
        if not hist:
            return ""
        peak = max(hist)
        avg = sum(hist) / len(hist)
        valley = min(hist)
        return f"峰值 {peak:.0f}{unit} · 平均 {avg:.0f}{unit} · 谷值 {valley:.0f}{unit}"
