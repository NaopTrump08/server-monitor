"""Add/Edit server dialog (glass-styled)."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
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
        self.setWindowTitle("编辑服务器" if server else "添加服务器")
        self.setMinimumWidth(440)
        self._color = self._server.get("color", "#7b4dff")
        self._build_ui()
        if server:
            self._load_values()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(26, 24, 26, 24)
        lay.setSpacing(16)

        title = QLabel("编辑服务器" if self._server else "添加服务器")
        title.setObjectName("dialogTitle")
        lay.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如：生产 · Web 集群")
        form.addRow("名称", self.name_edit)

        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("例如：192.168.1.100")
        form.addRow("主机 / IP", self.host_edit)

        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(8899)
        form.addRow("Agent 端口", self.port_spin)

        self.token_edit = QLineEdit()
        self.token_edit.setPlaceholderText("Agent 鉴权 token（可选）")
        self.token_edit.setEchoMode(QLineEdit.Password)
        form.addRow("鉴权 Token", self.token_edit)

        self.vnc_port_spin = QSpinBox()
        self.vnc_port_spin.setRange(0, 65535)
        self.vnc_port_spin.setValue(5901)
        form.addRow("VNC 端口", self.vnc_port_spin)

        self.vnc_pass_edit = QLineEdit()
        self.vnc_pass_edit.setPlaceholderText("VNC 密码")
        self.vnc_pass_edit.setEchoMode(QLineEdit.Password)
        form.addRow("VNC 密码", self.vnc_pass_edit)

        color_row = QHBoxLayout()
        self.color_btn = QPushButton("选择颜色")
        self.color_btn.setObjectName("ghostButton")
        self.color_btn.setCursor(Qt.PointingHandCursor)
        self.color_btn.clicked.connect(self._pick_color)
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(22, 22)
        self.color_preview.setStyleSheet(f"background: {self._color}; border-radius: 7px; border: 1px solid rgba(255,255,255,60);")
        color_row.addWidget(self.color_btn)
        color_row.addWidget(self.color_preview)
        color_row.addStretch(1)
        form.addRow("强调色", color_row)

        lay.addLayout(form)

        hint = QLabel("Agent 需在监控端口上暴露 /api/stats 接口。")
        hint.setObjectName("hint")
        lay.addWidget(hint)

        btns = QHBoxLayout()
        btns.addStretch(1)
        cancel = QPushButton("取消")
        cancel.setObjectName("ghostButton")
        cancel.setCursor(Qt.PointingHandCursor)
        cancel.clicked.connect(self.reject)
        ok = QPushButton("保存")
        ok.setObjectName("primaryButton")
        ok.setCursor(Qt.PointingHandCursor)
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
        color = QColorDialog.getColor(QColor(self._color), self, "选择强调色")
        if color.isValid():
            self._color = color.name()
            self.color_preview.setStyleSheet(
                f"background: {self._color}; border-radius: 7px; border: 1px solid rgba(255,255,255,60);"
            )

    def _on_ok(self):
        name = self.name_edit.text().strip()
        host = self.host_edit.text().strip()
        if not host:
            QMessageBox.warning(self, "无效输入", "主机 / IP 不能为空。")
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
