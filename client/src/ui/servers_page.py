"""ServersPage — server management view (list of glass rows with actions)."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .card import StatusDot
from .glass import GlassFrame


class ServerRow(GlassFrame):
    def __init__(self, server_id, cfg, on_vnc=None, on_edit=None, on_delete=None, parent=None):
        super().__init__(parent, radius=20)
        self.server_id = server_id
        self._on_vnc = on_vnc
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._build_ui()
        self.set_cfg(cfg)

    def _build_ui(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(14)

        self.dot = StatusDot()
        lay.addWidget(self.dot)

        col = QVBoxLayout()
        col.setSpacing(2)
        self.name_lbl = QLabel("Server")
        self.name_lbl.setObjectName("cardTitle")
        self.host_lbl = QLabel("")
        self.host_lbl.setObjectName("cardHost")
        col.addWidget(self.name_lbl)
        col.addWidget(self.host_lbl)
        lay.addLayout(col)
        lay.addStretch(1)

        self.lat_lbl = QLabel("—")
        self.lat_lbl.setObjectName("latencyValue")
        self.lat_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lay.addWidget(self.lat_lbl)

        self.vnc_btn = QPushButton("远程桌面")
        self.vnc_btn.setObjectName("ghostButton")
        self.vnc_btn.setProperty("accent", "true")
        self.vnc_btn.setCursor(Qt.PointingHandCursor)
        self.vnc_btn.clicked.connect(lambda: self._on_vnc and self._on_vnc(self.server_id))
        lay.addWidget(self.vnc_btn)

        self.edit_btn = QPushButton("编辑")
        self.edit_btn.setObjectName("ghostButton")
        self.edit_btn.setCursor(Qt.PointingHandCursor)
        self.edit_btn.clicked.connect(lambda: self._on_edit and self._on_edit(self.server_id))
        lay.addWidget(self.edit_btn)

        self.del_btn = QPushButton("删除")
        self.del_btn.setObjectName("dangerButton")
        self.del_btn.setCursor(Qt.PointingHandCursor)
        self.del_btn.clicked.connect(lambda: self._on_delete and self._on_delete(self.server_id))
        lay.addWidget(self.del_btn)

    def set_cfg(self, cfg):
        self.name_lbl.setText(cfg.get("name") or cfg.get("host") or "Server")
        port = cfg.get("port", 8899)
        vnc = f" · VNC:{cfg.get('vnc_port')}" if cfg.get("vnc_port") else ""
        self.host_lbl.setText(f"{cfg.get('host', '')}:{port}{vnc}")

    def update_status(self, data):
        self.dot.set_online(bool(data.get("online")))
        lat = data.get("latency_ms")
        self.lat_lbl.setText(f"{int(lat)} ms" if lat is not None else "—")


class ServersPage(GlassFrame):
    def __init__(self, on_add=None, on_edit=None, on_delete=None, on_vnc=None, parent=None):
        super().__init__(parent, radius=26)
        self._on_add = on_add
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._on_vnc = on_vnc
        self._rows = {}
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        # header
        head = QHBoxLayout()
        head.setSpacing(12)
        title = QLabel("服务器管理")
        title.setObjectName("sectionTitle")
        head.addWidget(title)
        self.sub_lbl = QLabel("")
        self.sub_lbl.setObjectName("appSubtitle")
        head.addWidget(self.sub_lbl)
        head.addStretch(1)
        add_btn = QPushButton("＋  添加服务器")
        add_btn.setObjectName("primaryButton")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._on_add)
        head.addWidget(add_btn)
        lay.addLayout(head)

        # scroll list
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.NoFrame)
        self._scroll.viewport().setAutoFillBackground(False)
        self._container = QWidget()
        self._container.setAutoFillBackground(False)
        self._rows_lay = QVBoxLayout(self._container)
        self._rows_lay.setContentsMargins(0, 0, 0, 0)
        self._rows_lay.setSpacing(12)
        self._rows_lay.addStretch(1)
        self._scroll.setWidget(self._container)
        lay.addWidget(self._scroll, 1)

        # empty state
        self._empty = GlassFrame(radius=22)
        el = QVBoxLayout(self._empty)
        el.setContentsMargins(24, 40, 24, 40)
        et = QLabel("还没有服务器")
        et.setObjectName("appTitle")
        et.setAlignment(Qt.AlignCenter)
        eh = QLabel("点击右上角「添加服务器」，接入第一台主机。")
        eh.setObjectName("appSubtitle")
        eh.setAlignment(Qt.AlignCenter)
        el.addStretch(1)
        el.addWidget(et)
        el.addWidget(eh)
        el.addStretch(1)
        self._rows_lay.addWidget(self._empty)
        self._empty.hide()

    def set_servers(self, servers):
        while self._rows_lay.count():
            item = self._rows_lay.takeAt(0)
            w = item.widget()
            if w is not None and w is not self._empty:
                w.deleteLater()
        self._rows.clear()

        if not servers:
            self._rows_lay.addWidget(self._empty)
            self._empty.show()
            self.sub_lbl.setText("0 台服务器")
            return
        self._empty.hide()

        for i, s in enumerate(servers):
            row = ServerRow(i, s, on_vnc=self._on_vnc, on_edit=self._on_edit, on_delete=self._on_delete)
            self._rows_lay.insertWidget(self._rows_lay.count() - 1, row)
            self._rows[i] = row
        self.sub_lbl.setText(f"{len(servers)} 台服务器")

    def update_snapshot(self, snapshot):
        for sid, data in snapshot.items():
            row = self._rows.get(sid)
            if row:
                row.update_status(data)
