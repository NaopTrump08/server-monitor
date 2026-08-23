"""Add/Edit server dialog."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QColorDialog,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class ServerDialog(QDialog):
    def __init__(self, parent=None, server=None):
        super().__init__(parent)
        self._server = dict(server) if server else {}
        self.setWindowTitle("Edit Server" if server else "Add Server")
        self.setMinimumWidth(420)
        self._color = self._server.get("color", "#2563eb")
        self._build_ui()
        if server:
            self._load_values()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(14)

        title = QLabel("Edit Server" if self._server else "Add Server")
        title.setObjectName("dialogTitle")
        lay.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g. WHZT Server")
        form.addRow("Name", self.name_edit)

        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("e.g. 192.168.1.100")
        form.addRow("Host / IP", self.host_edit)

        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(8899)
        form.addRow("Agent Port", self.port_spin)

        self.token_edit = QLineEdit()
        self.token_edit.setPlaceholderText("Agent auth token (optional)")
        self.token_edit.setEchoMode(QLineEdit.Password)
        form.addRow("Auth Token", self.token_edit)

        self.vnc_port_spin = QSpinBox()
        self.vnc_port_spin.setRange(0, 65535)
        self.vnc_port_spin.setValue(5901)
        form.addRow("VNC Port", self.vnc_port_spin)

        self.vnc_pass_edit = QLineEdit()
        self.vnc_pass_edit.setPlaceholderText("VNC password")
        self.vnc_pass_edit.setEchoMode(QLineEdit.Password)
        form.addRow("VNC Password", self.vnc_pass_edit)

        color_row = QHBoxLayout()
        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self._pick_color)
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(20, 20)
        self.color_preview.setStyleSheet(
            f"background-color: {self._color}; border-radius: 4px;"
        )
        color_row.addWidget(self.color_btn)
        color_row.addWidget(self.color_preview)
        color_row.addStretch(1)
        form.addRow("Accent Color", color_row)

        lay.addLayout(form)

        hint = QLabel("Agent must expose /api/stats on the monitor port.")
        hint.setObjectName("hint")
        lay.addWidget(hint)

        btns = QHBoxLayout()
        btns.addStretch(1)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        ok = QPushButton("Save")
        ok.setObjectName("primaryButton")
        ok.clicked.connect(self._on_ok)
        btns.addWidget(cancel)
        btns.addWidget(ok)
        lay.addLayout(btns)

    def _load_values(self):
        self.name_edit.setText(self._server.get("name", ""))
        self.host_edit.setText(self._server.get("host", ""))
        self.port_spin.setValue(int(self._server.get("port", 8899)))
        self.token_edit.setText(self._server.get("token", ""))
        self.vnc_port_spin.setValue(int(self._server.get("vnc_port", 0) or 0))
        self.vnc_pass_edit.setText(self._server.get("vnc_password", ""))

    def _pick_color(self):
        color = QColorDialog.getColor(
            QColor(self._color), self, "Choose Accent Color"
        )
        if color.isValid():
            self._color = color.name()
            self.color_preview.setStyleSheet(
                f"background-color: {self._color}; border-radius: 4px;"
            )

    def _on_ok(self):
        name = self.name_edit.text().strip()
        host = self.host_edit.text().strip()
        if not host:
            QMessageBox.warning(self, "Invalid", "Host / IP is required.")
            return
        if not name:
            name = host
        self._server = {
            "name": name,
            "host": host,
            "port": self.port_spin.value(),
            "token": self.token_edit.text().strip(),
            "vnc_port": self.vnc_port_spin.value(),
            "vnc_password": self.vnc_pass_edit.text().strip(),
            "color": self._color,
        }
        self.accept()

    def result_server(self):
        return self._server


from PySide6.QtGui import QColor  # noqa: E402
