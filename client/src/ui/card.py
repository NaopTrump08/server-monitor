"""Server status card widget."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .chart import LiveChart
from .format import format_bytes, format_rate, format_time, format_uptime
from . import theme


class ServerCard(QFrame):
    def __init__(self, server_id, on_vnc, on_edit=None, on_delete=None, parent=None):
        super().__init__(parent)
        self.server_id = server_id
        self._on_vnc = on_vnc
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._server_cfg = {}
        self._history = []
        self.setObjectName("serverCard")
        self.setMinimumWidth(420)

        self._build_ui()
        self._apply_status(online=False, error="Waiting...")

    ACCENTS = ["purple", "blue", "pink", "orange"]

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 14)
        outer.setSpacing(0)

        # ---------- gradient banner ----------
        banner = QWidget()
        self.accent = self.ACCENTS[self.server_id % len(self.ACCENTS)]
        banner.setObjectName("cardBanner")
        banner.setProperty("accent", self.accent)
        banner.setStyleSheet(
            "border-top-left-radius: 20px; border-top-right-radius: 20px;"
        )
        h = QHBoxLayout(banner)
        h.setContentsMargins(18, 14, 18, 14)
        h.setSpacing(8)

        self.status_dot = QLabel()
        self.status_dot.setFixedSize(10, 10)
        self.status_dot.setObjectName("statusDot")

        name_col = QVBoxLayout()
        name_col.setSpacing(0)
        self.name_label = QLabel("Server")
        self.name_label.setObjectName("serverName")
        self.host_label = QLabel("")
        self.host_label.setObjectName("serverHost")
        name_col.addWidget(self.name_label)
        name_col.addWidget(self.host_label)

        h.addWidget(self.status_dot)
        h.addLayout(name_col)
        h.addStretch(1)

        self.latency_label = QLabel("")
        self.latency_label.setObjectName("serverHost")

        self.status_label = QLabel("OFFLINE")
        self.status_label.setObjectName("statusLabel")

        self.vnc_btn = QPushButton("VNC")
        self.vnc_btn.setObjectName("primaryButton")
        self.vnc_btn.setFixedHeight(28)
        self.vnc_btn.setCursor(Qt.PointingHandCursor)
        self.vnc_btn.clicked.connect(self._vnc_clicked)

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setObjectName("secondaryButton")
        self.edit_btn.setFixedHeight(28)
        self.edit_btn.setCursor(Qt.PointingHandCursor)
        self.edit_btn.clicked.connect(self._edit_clicked)

        self.del_btn = QPushButton("Delete")
        self.del_btn.setObjectName("dangerButton")
        self.del_btn.setFixedHeight(28)
        self.del_btn.setCursor(Qt.PointingHandCursor)
        self.del_btn.clicked.connect(self._delete_clicked)

        h.addWidget(self.latency_label)
        h.addWidget(self.status_label)
        h.addWidget(self.vnc_btn)
        h.addWidget(self.edit_btn)
        h.addWidget(self.del_btn)
        outer.addWidget(banner)

        # ---------- body ----------
        body = QVBoxLayout()
        body.setContentsMargins(16, 14, 16, 0)
        body.setSpacing(10)

        # metrics row
        metrics = QHBoxLayout()
        metrics.setSpacing(10)
        self.cpu_value = _MetricValue()
        self.mem_value = _MetricValue()
        self.disk_value = _MetricValue()
        self.cpu_value.set_title("CPU")
        self.mem_value.set_title("Memory")
        self.disk_value.set_title("Disk")
        self.cpu_value.set_accent(self.accent)
        self.mem_value.set_accent(self.accent)
        self.disk_value.set_accent(self.accent)
        metrics.addWidget(self.cpu_value)
        metrics.addWidget(self.mem_value)
        metrics.addWidget(self.disk_value)
        body.addLayout(metrics)

        # ---------- gauges ----------
        self.cpu_bar = _Gauge("CPU Usage", "#3b82f6", "gaugeCpu")
        self.mem_bar = _Gauge("Memory", "#a855f7", "gaugeMem")
        body.addWidget(self.cpu_bar)
        body.addWidget(self.mem_bar)

        # ---------- network + info row ----------
        info_row = QHBoxLayout()
        info_row.setSpacing(10)

        left_col = QVBoxLayout()
        left_col.setSpacing(6)
        left_col.addWidget(_MetricLine("RX", "0 B/s", "#3b82f6"))
        left_col.addWidget(_MetricLine("TX", "0 B/s", "#22c55e"))
        self.rx_line = left_col.itemAt(0).widget()
        self.tx_line = left_col.itemAt(1).widget()
        info_row.addLayout(left_col)

        right_col = QVBoxLayout()
        right_col.setSpacing(6)
        right_col.addWidget(_MetricLine("Uptime", "-", "#eab308"))
        right_col.addWidget(_MetricLine("Updated", "-", "#86868b"))
        self.uptime_line = right_col.itemAt(0).widget()
        self.update_line = right_col.itemAt(1).widget()
        info_row.addLayout(right_col)

        info_row.addStretch(1)
        body.addLayout(info_row)

        # ---------- charts: one mini chart per metric ----------
        grid = QHBoxLayout()
        grid.setSpacing(10)
        self.charts = {}
        specs = [
            ("CPU %", "#7b4dff", 1),
            ("MEM %", "#4a8cff", 2),
            ("RX", "#34c759", 3),
            ("TX", "#ff9f0a", 4),
        ]
        tiles = []
        for label, color, col in specs:
            tile = _ChartTile(label, color, col)
            tiles.append(tile)
            self.charts[label] = tile.chart
        grid.addWidget(tiles[0])
        grid.addWidget(tiles[1])
        grid.addWidget(tiles[2])
        grid.addWidget(tiles[3])
        body.addLayout(grid)

        outer.addLayout(body)

    def _vnc_clicked(self):
        if self._on_vnc:
            self._on_vnc(self.server_id)

    def _edit_clicked(self):
        if self._on_edit:
            self._on_edit(self.server_id)

    def _delete_clicked(self):
        if self._on_delete:
            self._on_delete(self.server_id)

    def set_server_config(self, cfg):
        self._server_cfg = cfg
        self.name_label.setText(cfg.get("name", cfg.get("host", "")))
        self.host_label.setText(cfg.get("host", ""))
        self.vnc_btn.setEnabled(bool(cfg.get("vnc_port")))

    def refresh_theme(self):
        """Re-apply theme-dependent inline colours after a mode switch."""
        tk = theme.tokens()
        for widget in self.findChildren(_MetricValue):
            widget.set_title(widget._title or widget.label.text())
        for widget in self.findChildren(_MetricLine):
            widget.refresh_colour(tk)
        for widget in self.findChildren(_ChartTile):
            widget.refresh_colour(tk)
        self.update()

    def update_status(self, status):
        self._apply_status(
            online=status.get("online", False),
            error=status.get("error"),
            data=status.get("data", {}),
            latency=status.get("latency_ms"),
            last_update=status.get("last_update"),
        )
        history = status.get("history", [])
        if history != self._history:
            self._history = history
            for name, chart in self.charts.items():
                chart.setData(history)

    def _apply_status(self, online, error=None, data=None, latency=None, last_update=None):
        data = data or {}
        if online:
            self.status_dot.setProperty("class", "")
            self.status_label.setProperty("class", "")
            self.status_label.setText("ONLINE")
        else:
            self.status_dot.setProperty("class", "offline")
            self.status_label.setProperty("class", "offline")
            self.status_label.setText("OFFLINE")
        self.status_dot.style().unpolish(self.status_dot)
        self.status_dot.style().polish(self.status_dot)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

        if latency is not None:
            self.latency_label.setText(f"{latency} ms")
        else:
            self.latency_label.setText("")

        cpu = data.get("cpu", {})
        mem = data.get("memory", {})
        disk = data.get("disk", [])

        cpu_pct = cpu.get("percent", 0) if online else 0
        mem_pct = mem.get("percent", 0) if online else 0
        disk_pct = disk[0].get("percent", 0) if disk and online else 0

        self.cpu_value.set_value(cpu_pct, "%")
        self.mem_value.set_value(mem_pct, "%")
        self.disk_value.set_value(disk_pct, "%")

        self.cpu_bar.set_value(cpu_pct)
        self.mem_bar.set_value(mem_pct)

        net = data.get("network", {})
        if online:
            self.rx_line.set_value(format_rate(net.get("rx_rate", 0)))
            self.tx_line.set_value(format_rate(net.get("tx_rate", 0)))
            sysinfo = data.get("system", {})
            self.uptime_line.set_value(format_uptime(sysinfo.get("uptime", 0)))
            self.update_line.set_value(format_time(last_update))
        else:
            self.rx_line.set_value("-")
            self.tx_line.set_value("-")
            self.uptime_line.set_value("-")
            self.update_line.set_value("-")


class _MetricValue(QWidget):
    ACCENT_COLORS = {
        "purple": "#7b4dff",
        "blue": "#4a8cff",
        "pink": "#ff6fa8",
        "orange": "#ff9f0a",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("metricCard")
        self._accent = "purple"
        self._title = "-"
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(2)
        self.value = QLabel("--")
        self.value.setObjectName("metricValue")
        self.label = QLabel("-")
        self.label.setObjectName("metricLabel")
        lay.addWidget(self.value)
        lay.addWidget(self.label)

    def set_accent(self, accent):
        self._accent = accent
        color = self.ACCENT_COLORS.get(accent, "#7b4dff")
        self.value.setStyleSheet(f"color: {color};")

    def set_value(self, value, unit):
        if value is None:
            self.value.setText("--")
            return
        if isinstance(value, float):
            text = f"{value:.1f}"
        else:
            text = str(value)
        self.value.setText(text + unit)

    def set_title(self, title):
        self._title = title
        self.label.setText(title)
        tk = theme.tokens()
        self.label.setStyleSheet(
            f"font-weight: 600; color: {tk['text']};"
        )


class _Gauge(QWidget):
    def __init__(self, title, color, obj_name, parent=None):
        super().__init__(parent)
        self.setObjectName(obj_name)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 2, 0, 2)
        lay.setSpacing(4)
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        self.title = QLabel(title)
        self.title.setObjectName("metricLabel")
        self.pct = QLabel("0%")
        self.pct.setObjectName("metricLabel")
        row.addWidget(self.title)
        row.addStretch(1)
        row.addWidget(self.pct)
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(False)
        lay.addLayout(row)
        lay.addWidget(self.bar)

    def set_value(self, value):
        self.bar.setValue(int(value))
        self.pct.setText(f"{value:.0f}%")


class _MetricLine(QWidget):
    def __init__(self, label, value, color, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        self._color = color
        self.key = QLabel(label)
        self.key.setObjectName("metricLabel")
        self.val = QLabel(value)
        self.val.setObjectName("metricLabel")
        lay.addWidget(self.key)
        lay.addWidget(self.val)
        lay.addStretch(1)
        self.refresh_colour(theme.tokens())

    def refresh_colour(self, tk):
        color = self._color
        if color in ("#86868b",):
            color = tk["text_soft"]
        self.key.setStyleSheet(f"color: {color};")

    def set_value(self, text):
        self.val.setText(text)


class _ChartTile(QWidget):
    """A single-metric mini chart with a coloured header."""

    def __init__(self, title, color, column, parent=None):
        super().__init__(parent)
        self.setObjectName("chartTile")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        header = QHBoxLayout()
        header.setContentsMargins(8, 6, 8, 0)
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(
            f"background-color: {color}; border-radius: 4px;"
        )
        self.title = QLabel(title)
        self.title.setObjectName("chartTitle")
        self.title.setStyleSheet(f"color: {color}; font-weight: 600;")
        header.addWidget(dot)
        header.addWidget(self.title)
        header.addStretch(1)
        lay.addLayout(header)
        self.chart = LiveChart(column=column)
        self.chart.setSeries([title], [title], [color], normalize=True)
        self.chart.setMinimumHeight(120)
        lay.addWidget(self.chart)

    def refresh_colour(self, tk):
        self.chart.update()
