"""Main application window."""

import logging

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from config import Config
from monitor import ServerMonitor
from ui.card import ServerCard
from ui.server_dialog import ServerDialog
from ui.vnc_window import VNCWindow
from ui.format import format_time

log = logging.getLogger("main")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Server Monitor")
        self.resize(1100, 780)
        self.config = Config()
        self._cards = {}
        self._vnc_windows = []

        self.monitor = ServerMonitor(self.config)
        self.monitor.start()

        self._build_ui()
        self._rebuild_cards()

        # UI refresh pump: pull the latest monitor snapshot on the main
        # thread. The monitor thread never touches Qt, so there is no
        # cross-thread signal that could stall the GUI on Windows.
        self._ui_timer = QTimer(self)
        self._ui_timer.timeout.connect(self._refresh_ui)
        self._ui_timer.start(1000)

        # periodic card rebuild when server list changes
        self._cfg_check_timer = QTimer(self)
        self._cfg_check_timer.timeout.connect(self._check_cfg_change)
        self._cfg_check_timer.start(2000)

    # ---------------------------------------------------------------- UI build
    def _build_ui(self):
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # top bar
        top = QWidget()
        top.setObjectName("topBar")
        top.setFixedHeight(52)
        top_lay = QHBoxLayout(top)
        top_lay.setContentsMargins(20, 0, 20, 0)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        title = QLabel("Server Monitor")
        title.setObjectName("appTitle")
        sub = QLabel("Multi-server monitoring with VNC remote desktop")
        sub.setObjectName("appSubtitle")
        title_col.addWidget(title)
        title_col.addWidget(sub)

        top_lay.addLayout(title_col)
        top_lay.addStretch(1)

        add_btn = QPushButton("+ Add Server")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self._add_server)
        top_lay.addWidget(add_btn)

        menu_btn = QPushButton("•••")
        menu_btn.setObjectName("iconButton")
        menu_btn.setFixedWidth(36)
        menu = QMenu(self)
        act_refresh = menu.addAction("Refresh now")
        act_interval_1 = menu.addAction("Refresh: 2s")
        act_interval_3 = menu.addAction("Refresh: 3s")
        act_interval_5 = menu.addAction("Refresh: 5s")
        act_interval_10 = menu.addAction("Refresh: 10s")
        act_about = menu.addAction("About")
        menu_btn.setMenu(menu)
        top_lay.addWidget(menu_btn)

        act_refresh.triggered.connect(self._refresh_now)
        act_interval_1.triggered.connect(lambda: self._set_interval(2))
        act_interval_3.triggered.connect(lambda: self._set_interval(3))
        act_interval_5.triggered.connect(lambda: self._set_interval(5))
        act_interval_10.triggered.connect(lambda: self._set_interval(10))
        act_about.triggered.connect(self._about)

        root.addWidget(top)

        # scrollable card area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setObjectName("cardScroll")
        self._scroll.setStyleSheet(
            "QScrollArea#cardScroll, QScrollArea#cardScroll > QWidget > QWidget { background-color: #f5f5f7; }"
        )
        self._container = QWidget()
        self._cards_layout = QVBoxLayout(self._container)
        self._cards_layout.setContentsMargins(20, 16, 20, 16)
        self._cards_layout.setSpacing(14)
        self._cards_layout.addStretch(1)
        self._scroll.setWidget(self._container)
        root.addWidget(self._scroll, 1)

        # empty-state placeholder (hidden when servers exist)
        self._empty_box = QWidget()
        self._empty_box.setObjectName("emptyBox")
        empty_lay = QVBoxLayout(self._empty_box)
        empty_lay.setContentsMargins(24, 24, 24, 24)
        empty_lay.setSpacing(10)
        empty_title = QLabel("No servers yet")
        empty_title.setObjectName("emptyTitle")
        empty_title.setAlignment(Qt.AlignCenter)
        empty_hint = QLabel("Click \u201c+ Add Server\u201d in the top bar to add your first server.")
        empty_hint.setObjectName("emptyHint")
        empty_hint.setAlignment(Qt.AlignCenter)
        empty_lay.addStretch(1)
        empty_lay.addWidget(empty_title)
        empty_lay.addWidget(empty_hint)
        empty_lay.addStretch(1)
        self._empty_box.hide()
        self._cards_layout.addWidget(self._empty_box)
        self._cards_layout.setStretchFactor(self._empty_box, 1)

        self.setCentralWidget(central)

        # status bar
        sb = QStatusBar()
        self._status_label = QLabel("")
        sb.addWidget(self._status_label)
        self.setStatusBar(sb)

    # ---------------------------------------------------------------- cards
    def _rebuild_cards(self):
        servers = self.config.servers
        # remove all existing cards
        for card in list(self._cards.values()):
            self._cards_layout.removeWidget(card)
            card.deleteLater()
        self._cards.clear()
        # add cards
        for i, s in enumerate(servers):
            card = ServerCard(i, on_vnc=self._open_vnc, on_edit=self._edit_server, on_delete=self._delete_server)
            card.set_server_config(s)
            self._cards_layout.insertWidget(self._cards_layout.count() - 2, card)
            self._cards[i] = card
        # empty state
        self._empty_box.setVisible(len(servers) == 0)

    def _check_cfg_change(self):
        servers = self.config.servers
        if len(servers) != len(self._cards):
            self._rebuild_cards()

    def _refresh_ui(self):
        snapshot = self.monitor.snapshot()
        for sid, data in snapshot.items():
            card = self._cards.get(sid)
            if card:
                card.update_status(data)
        online = sum(1 for v in snapshot.values() if v.get("online"))
        total = len(snapshot)
        ts = ""
        if snapshot:
            ts = format_time(max((v.get("last_update") or 0) for v in snapshot.values()))
        self._status_label.setText(f"{online}/{total} servers online   Last update: {ts}")

    # ---------------------------------------------------------------- actions
    def _add_server(self):
        dlg = ServerDialog(self)
        if dlg.exec():
            self.config.add_server(dlg.result_server())
            self._rebuild_cards()
            self._refresh_now()

    def _edit_server(self, server_id):
        cfg = self.config.get_server(server_id)
        if not cfg:
            return
        dlg = ServerDialog(self, server=cfg)
        if dlg.exec():
            if self.config.update_server(server_id, dlg.result_server()):
                self._rebuild_cards()
                self._refresh_now()

    def _delete_server(self, server_id):
        cfg = self.config.get_server(server_id)
        if not cfg:
            return
        name = cfg.get("name", cfg.get("host", "this server"))
        ret = QMessageBox.question(
            self,
            "Delete Server",
            f"Remove {name} from the list?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ret == QMessageBox.Yes:
            if self.config.remove_server(server_id):
                self._rebuild_cards()
                self._refresh_now()

    def _open_vnc(self, server_id):
        cfg = self.config.get_server(server_id)
        if not cfg:
            log.warning("open_vnc: no config for server %s", server_id)
            return
        log.info("open_vnc: server %s cfg=%s", server_id, cfg.get("host"))
        if not cfg.get("vnc_port"):
            QMessageBox.information(self, "VNC", "No VNC port configured for this server.")
            return
        log.info("open_vnc: creating VNCWindow")
        win = VNCWindow(cfg)
        self._vnc_windows.append(win)
        win.closed = None
        win.destroyed.connect(lambda: self._remove_vnc(win))
        log.info("open_vnc: showing window")
        win.show()
        win.raise_()
        win.activateWindow()
        log.info("open_vnc: done")

    def _remove_vnc(self, win):
        if win in self._vnc_windows:
            self._vnc_windows.remove(win)

    def _refresh_now(self):
        # force immediate poll by restarting loop briefly
        self.monitor.stop()
        self.monitor.start()

    def _set_interval(self, seconds):
        self.config.refresh_interval = seconds
        self.monitor.stop()
        self.monitor.start()

    def _about(self):
        QMessageBox.about(
            self,
            "About Server Monitor",
            "Server Monitor v1.2.0\n\n"
            "Multi-server monitoring with live charts and VNC remote desktop.\n\n"
            "Uses a lightweight agent (monitor_agent.py) running on each server.",
        )

    def closeEvent(self, event):
        self.monitor.stop()
        for w in self._vnc_windows:
            try:
                w.close()
            except RuntimeError:
                pass
        super().closeEvent(event)
