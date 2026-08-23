"""VNC remote desktop window."""

import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QToolBar,
    QWidget,
)

from vnc_client import VNCClient

log = logging.getLogger("vncwin")


class VNCWindow(QMainWindow):
    def __init__(self, server_cfg, parent=None):
        super().__init__(parent)
        self._cfg = server_cfg
        self.setWindowTitle(f"VNC — {server_cfg.get('name', server_cfg.get('host', ''))}")
        self.resize(1100, 700)
        self._build_ui()
        self._connect()

    def _build_ui(self):
        central = QWidget()
        lay = QHBoxLayout(central)
        lay.setContentsMargins(0, 0, 0, 0)
        self.viewer = VNCClient()
        self.viewer.connected.connect(self._on_connected)
        self.viewer.disconnected.connect(self._on_disconnected)
        lay.addWidget(self.viewer)
        self.setCentralWidget(central)

        # toolbar
        tb = QToolBar("Tools")
        tb.setMovable(False)
        self.addToolBar(tb)

        self.status_label = QLabel(" Connecting...")
        tb.addWidget(self.status_label)
        tb.addSeparator()

        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self._refresh)
        tb.addWidget(refresh)

        disconnect = QPushButton("Disconnect")
        disconnect.clicked.connect(self._disconnect)
        tb.addWidget(disconnect)

    def _connect(self):
        host = self._cfg.get("host", "")
        port = int(self._cfg.get("vnc_port") or 5901)
        password = self._cfg.get("vnc_password", "")
        log.info("VNCWindow._connect host=%s port=%s has_password=%s", host, port, bool(password))
        self.viewer.connect_to(host, port, password=password)
        log.info("VNCWindow._connect thread started")

    def _refresh(self):
        self.viewer.disconnect()
        self.status_label.setText(" Reconnecting...")
        self._connect()

    def _disconnect(self):
        self.viewer.disconnect()
        self.status_label.setText(" Disconnected")

    def _on_connected(self):
        self.status_label.setText(
            f" Connected to {self._cfg.get('host', '')}:{int(self._cfg.get('vnc_port') or 5901)}"
        )

    def _on_disconnected(self, reason):
        self.status_label.setText(f" Disconnected — {reason}")
        if self.isVisible() and reason:
            QMessageBox.information(self, "VNC", f"Connection closed: {reason}")

    def closeEvent(self, event):
        self.viewer.disconnect()
        super().closeEvent(event)
