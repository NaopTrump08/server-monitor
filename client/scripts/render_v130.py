"""Render the v1.3.0 main window + a card close-up to PNG for visual review."""

import os
import sys
import json

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.*=false")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QTimer

app = QApplication([])

from ui.theme import STYLE_SHEET
from ui.main_window import MainWindow
from config import Config

app.setStyleSheet(STYLE_SHEET)

cfg_path = "/tmp/v130_shot_cfg.json"
demo = {
    "servers": [
        {"name": "WHZT Server", "host": "107.151.245.201", "port": 8899,
         "vnc_port": 5901, "token": "", "vnc_password": "", "color": "#7b4dff"},
        {"name": "Office NAS", "host": "192.168.1.50", "port": 8899,
         "vnc_port": 0, "token": "", "vnc_password": "", "color": "#4a8cff"},
        {"name": "Edge Node", "host": "10.0.0.8", "port": 8899,
         "vnc_port": 0, "token": "", "vnc_password": "", "color": "#ff6fa8"},
        {"name": "Backup Box", "host": "10.0.0.12", "port": 8899,
         "vnc_port": 0, "token": "", "vnc_password": "", "color": "#ff9f0a"},
    ],
    "refresh_interval": 3,
}
with open(cfg_path, "w") as f:
    json.dump(demo, f)

cfg = Config(cfg_path)
win = MainWindow(cfg)
win.resize(1280, 820)
win.show()

# inject synthetic status so cards look alive
status = {
    "online": True,
    "error": None,
    "data": {
        "cpu": {"percent": 42.3},
        "memory": {"percent": 61.8},
        "disk": [{"percent": 73.5}],
        "network": {"rx_rate": 1_234_567, "tx_rate": 890_123},
        "system": {"uptime": 259200},
    },
    "latency_ms": 12,
    "last_update": 1784808000,
    "history": [
        (i, (i * 7) % 100, (i * 13) % 100, i * 200_000, i * 150_000)
        for i in range(1, 61)
    ],
}
for i, card in win._cards.items():
    card.update_status(status)

out_dir = "/tmp/v130_shots"
os.makedirs(out_dir, exist_ok=True)


def shoot():
    app.processEvents()
    win.grab().save(os.path.join(out_dir, "main_window.png"))
    c0 = win._cards[0]
    c0.grab().save(os.path.join(out_dir, "card0.png"))
    for name, chart in c0.charts.items():
        chart.grab().save(os.path.join(out_dir, f"chart_{name.replace('%', 'pct').replace(' ', '')}.png"))
    # dark mode
    win._toggle_theme()
    app.processEvents()
    win.grab().save(os.path.join(out_dir, "main_window_dark.png"))
    c0.grab().save(os.path.join(out_dir, "card0_dark.png"))
    win.close()
    app.quit()


QTimer.singleShot(400, shoot)
app.exec()
print("saved to", out_dir)
