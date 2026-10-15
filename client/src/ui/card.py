"""ServerCard — a liquid-glass server status card with rings, network and sparkline."""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QRadialGradient
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .chart import AreaChart
from .format import format_rate
from .glass import GlassFrame
from .ring_gauge import RingGauge


class StatusDot(QWidget):
    """Small glowing status dot (green = online, red = offline)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._online = False
        self.setFixedSize(14, 14)

    def set_online(self, online):
        self._online = bool(online)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        c = QColor("#34c759") if self._online else QColor("#ff3b30")
        g = QRadialGradient(QPointF(7, 7), 8)
        g.setColorAt(0.0, QColor(c.red(), c.green(), c.blue(), 120))
        g.setColorAt(1.0, QColor(c.red(), c.green(), c.blue(), 0))
        p.fillRect(self.rect(), g)
        p.setPen(Qt.NoPen)
        p.setBrush(c)
        p.drawEllipse(QPointF(7, 7), 4, 4)
        p.end()


class ServerCard(GlassFrame):
    ACCENTS = ["#9b6cff", "#5aa7ff", "#38e0ff", "#34c759", "#ff9f0a", "#ff5ea8"]

    def __init__(self, server_id, on_vnc=None, on_edit=None, on_delete=None, parent=None):
        super().__init__(parent, radius=26)
        self.server_id = server_id
        self._on_vnc = on_vnc
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._name = "Server"
        self._host = ""
        self._accent = self.ACCENTS[server_id % len(self.ACCENTS)]
        self.setMinimumWidth(360)
        self._build_ui()
        self._apply_offline()

    # ------------------------------------------------------------------ build
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 18, 20, 18)
        outer.setSpacing(14)

        # header
        head = QHBoxLayout()
        head.setSpacing(10)
        self.dot = StatusDot()
        name_col = QVBoxLayout()
        name_col.setSpacing(2)
        self.name_lbl = QLabel(self._name)
        self.name_lbl.setObjectName("cardTitle")
        self.host_lbl = QLabel("")
        self.host_lbl.setObjectName("cardHost")
        name_col.addWidget(self.name_lbl)
        name_col.addWidget(self.host_lbl)
        head.addWidget(self.dot)
        head.addLayout(name_col)
        head.addStretch(1)
        lat_col = QVBoxLayout()
        lat_col.setSpacing(0)
        self.lat_val = QLabel("—")
        self.lat_val.setObjectName("latencyValue")
        self.lat_val.setAlignment(Qt.AlignRight)
        self.lat_lbl = QLabel("延迟")
        self.lat_lbl.setObjectName("latencyLbl")
        self.lat_lbl.setAlignment(Qt.AlignRight)
        lat_col.addWidget(self.lat_val)
        lat_col.addWidget(self.lat_lbl)
        head.addLayout(lat_col)
        outer.addLayout(head)

        # rings
        rings = QHBoxLayout()
        rings.setSpacing(8)
        self.gauge_cpu = RingGauge(color=self._accent)
        self.gauge_mem = RingGauge(color="#5aa7ff")
        self.gauge_disk = RingGauge(color="#38e0ff")
        for gauge, label in ((self.gauge_cpu, "CPU"), (self.gauge_mem, "内存"), (self.gauge_disk, "磁盘")):
            box = QVBoxLayout()
            box.setSpacing(4)
            box.addWidget(gauge, 0, Qt.AlignHCenter)
            lab = QLabel(label)
            lab.setObjectName("metricNote")
            lab.setAlignment(Qt.AlignCenter)
            box.addWidget(lab)
            rings.addLayout(box)
        outer.addLayout(rings)

        # network
        net = QHBoxLayout()
        net.setSpacing(6)
        net.setContentsMargins(4, 0, 4, 0)
        self._rx_arrow = QLabel("↓")
        self._rx_arrow.setStyleSheet("color: #38e0ff; font-weight: 700;")
        self.rx_val = QLabel("—")
        self.rx_val.setObjectName("latencyValue")
        self.rx_lbl = QLabel("下行")
        self.rx_lbl.setObjectName("cardHost")
        net.addWidget(self._rx_arrow)
        net.addWidget(self.rx_val)
        net.addWidget(self.rx_lbl)
        net.addSpacing(18)
        self._tx_arrow = QLabel("↑")
        self._tx_arrow.setStyleSheet("color: #34c759; font-weight: 700;")
        self.tx_val = QLabel("—")
        self.tx_val.setObjectName("latencyValue")
        self.tx_lbl = QLabel("上行")
        self.tx_lbl.setObjectName("cardHost")
        net.addWidget(self._tx_arrow)
        net.addWidget(self.tx_val)
        net.addWidget(self.tx_lbl)
        net.addStretch(1)
        outer.addLayout(net)

        # sparkline (CPU history)
        self.spark = AreaChart(color=self._accent)
        self.spark.set_fixed_range(0, 100)
        self.spark.setFixedHeight(52)
        outer.addWidget(self.spark)

        # footer buttons
        foot = QHBoxLayout()
        foot.setSpacing(8)
        self.vnc_btn = QPushButton("远程桌面")
        self.vnc_btn.setObjectName("ghostButton")
        self.vnc_btn.setProperty("accent", "true")
        self.vnc_btn.setCursor(Qt.PointingHandCursor)
        self.vnc_btn.clicked.connect(lambda: self._on_vnc and self._on_vnc(self.server_id))
        self.edit_btn = QPushButton("编辑")
        self.edit_btn.setObjectName("ghostButton")
        self.edit_btn.setCursor(Qt.PointingHandCursor)
        self.edit_btn.clicked.connect(lambda: self._on_edit and self._on_edit(self.server_id))
        self.del_btn = QPushButton("删除")
        self.del_btn.setObjectName("dangerButton")
        self.del_btn.setCursor(Qt.PointingHandCursor)
        self.del_btn.clicked.connect(lambda: self._on_delete and self._on_delete(self.server_id))
        foot.addWidget(self.vnc_btn)
        foot.addWidget(self.edit_btn)
        foot.addWidget(self.del_btn)
        outer.addLayout(foot)

    # ---------------------------------------------------------------- updates
    def set_server_config(self, cfg):
        self._name = cfg.get("name") or cfg.get("host") or "Server"
        self._host = cfg.get("host", "")
        self._accent = cfg.get("color") or self.ACCENTS[self.server_id % len(self.ACCENTS)]
        self.name_lbl.setText(self._name)
        self.host_lbl.setText(self._host)
        self.gauge_cpu.set_color(self._accent)
        self.spark.set_color(self._accent)

    def _apply_offline(self):
        self.dot.set_online(False)
        self.gauge_cpu.set_value(0)
        self.gauge_mem.set_value(0)
        self.gauge_disk.set_value(0)
        self.rx_val.setText("—")
        self.tx_val.setText("—")
        self.lat_val.setText("—")

    def update_status(self, data):
        online = bool(data.get("online"))
        self.dot.set_online(online)
        d = data.get("data") or {}

        cpu = d.get("cpu", {}).get("percent", 0)
        mem = d.get("memory", {}).get("percent", 0)
        disks = d.get("disk") or []
        disk = max((x.get("percent", 0) for x in disks), default=0)
        net = d.get("network", {})
        rx = net.get("rx_rate", 0)
        tx = net.get("tx_rate", 0)

        self.gauge_cpu.set_value(cpu)
        self.gauge_mem.set_value(mem)
        self.gauge_disk.set_value(disk)
        self.rx_val.setText(format_rate(rx))
        self.tx_val.setText(format_rate(tx))

        lat = data.get("latency_ms")
        self.lat_val.setText(f"{int(lat)} ms" if lat is not None else "—")

        self.name_lbl.setText(data.get("name") or self._name)
        self.host_lbl.setText(data.get("host") or self._host)

        hist = data.get("history") or []
        self.spark.set_values([h[1] for h in hist][-60:])

    def refresh_theme(self):
        self.spark.update()
        self.gauge_cpu.update()
        self.gauge_mem.update()
        self.gauge_disk.update()
        self.update()
