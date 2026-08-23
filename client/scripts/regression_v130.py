"""Off-screen regression checks for the v1.3.0 purple-brand light theme."""

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.*=false")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt

app = QApplication([])

from ui.theme import STYLE_SHEET
from ui.card import ServerCard
from ui.chart import LiveChart
from ui.main_window import MainWindow, SettingsDialog

app.setStyleSheet(STYLE_SHEET)

failures = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}: {name} {detail}")
    if not cond:
        failures.append(name)


def sample(widget, x, y):
    pix = widget.grab().toImage()
    c = pix.pixelColor(x, y)
    return c.name().upper()


# ---------- MainWindow layout ----------
cfg_path = os.path.join(os.path.dirname(__file__), "..", "src", "_regression_cfg.json")
import json

demo = {
    "servers": [
        {
            "name": "WHZT Server",
            "host": "107.151.245.201",
            "port": 8899,
            "vnc_port": 5901,
            "token": "",
            "vnc_password": "",
            "color": "#7b4dff",
        },
        {
            "name": "Office NAS",
            "host": "192.168.1.50",
            "port": 8899,
            "vnc_port": 0,
            "token": "",
            "vnc_password": "",
            "color": "#4a8cff",
        },
    ],
    "refresh_interval": 3,
}
with open(cfg_path, "w") as f:
    json.dump(demo, f)

from config import Config

cfg = Config(cfg_path)
win = MainWindow(cfg)
win.resize(1280, 800)
win.show()
app.processEvents()
win.grab()
app.processEvents()

# sidebar visible & fixed width
side = win.findChild(type(win.centralWidget()), "sideBar")
if side is not None:
    check("sidebar exists", True, f"w={side.width()}")
    check("sidebar width ~210", abs(side.width() - 210) < 5, f"w={side.width()}")
else:
    check("sidebar exists", False, "sideBar not found")

# nav buttons present & Dashboard checked
nav = [b for b in win.findChildren(type(win._nav_btns[0])) if b.objectName() == "navButton"]
check("nav button count >= 3", len(nav) >= 3, f"count={len(nav)}")
check("dashboard nav checked", nav[0].isChecked() if nav else False)

# two cards built
cards = win._cards
check("two cards built", len(cards) == 2, f"count={len(cards)}")

# card banner accents
for i, card in cards.items():
    banner = card.findChild(QWidget, "cardBanner")
    accent = card.accent
    check(f"card {i} accent set", accent in ("purple", "blue", "pink", "orange"), accent)
    check(f"card {i} banner present", banner is not None)
    if banner is not None:
        check(
            f"card {i} banner has accent prop",
            banner.property("accent") == accent,
            str(banner.property("accent")),
        )

# accent colors alternate for consecutive servers
accents = [c.accent for c in cards.values()]
check("accents alternate", len(set(accents)) == len(accents), str(accents))

# metric values carry accent color (inline stylesheet)
c0 = cards[0]
cpu_val = c0.cpu_value.value
check(
    "metric value purple tint",
    "7B4DFF" in cpu_val.styleSheet().upper(),
    cpu_val.styleSheet(),
)

# simulate online data -> labels populated
status = {
    "online": True,
    "error": None,
    "data": {
        "cpu": {"percent": 42.3},
        "memory": {"percent": 61.8},
        "disk": [{"percent": 73.5}],
        "network": {"rx_rate": 1_234_567, "tx_rate": 890_123},
        "system": {"uptime": 86400 * 3},
    },
    "latency_ms": 12,
    "last_update": 1784808000,
    "history": [
        (1, 10, 20, 30, 40),
        (2, 20, 30, 40, 50),
        (3, 30, 40, 50, 60),
        (4, 40, 50, 60, 70),
        (5, 50, 60, 70, 80),
    ],
}
c0.update_status(status)
app.processEvents()

check("cpu value text", c0.cpu_value.value.text() == "42.3%", c0.cpu_value.value.text())
check("mem value text", c0.mem_value.value.text() == "61.8%", c0.mem_value.value.text())
check("disk value text", c0.disk_value.value.text() == "73.5%", c0.disk_value.value.text())
check(
    "rx line populated",
    c0.rx_line.val.text().endswith("/s"),
    c0.rx_line.val.text(),
)
check("uptime populated", "d" in c0.uptime_line.val.text().lower(), c0.uptime_line.val.text())
check("status ONLINE", c0.status_label.text() == "ONLINE", c0.status_label.text())

# four independent mini charts, each single-series
check("chart tile count", len(c0.charts) == 4, str(list(c0.charts.keys())))
check(
    "chart keys present",
    set(c0.charts.keys()) == {"CPU %", "MEM %", "RX", "TX"},
    str(list(c0.charts.keys())),
)
cpu_chart = c0.charts["CPU %"]
check("cpu chart single series", len(cpu_chart._keys) == 1, str(cpu_chart._keys))
check("cpu chart purple", cpu_chart._colors[0] == "#7b4dff", str(cpu_chart._colors))
check(
    "cpu chart column=1",
    cpu_chart._column == 1,
    f"column={cpu_chart._column}",
)
rx_chart = c0.charts["RX"]
check("rx chart green", rx_chart._colors[0] == "#34c759", str(rx_chart._colors))
check("rx chart column=3", rx_chart._column == 3, f"column={rx_chart._column}")

# each mini chart renders with the injected history
cpu_chart.resize(220, 120)
cpu_chart.grab()
app.processEvents()
img = cpu_chart.grab().toImage()
col = img.pixelColor(110, 60).name().upper()
check("cpu chart renders non-blank", img.pixel(110, 60) != img.pixel(0, 0), col)

# ---------- SettingsDialog ----------
dlg = SettingsDialog(current=5)
check("settings dialog interval", dlg.interval() == 5, str(dlg.interval()))

# ---------- empty state ----------
from config import Config as C2

cfg2 = C2(cfg_path)
while cfg2.servers:
    cfg2.remove_server(0)
win2 = MainWindow(cfg2)
win2.show()
app.processEvents()
win2.grab()
app.processEvents()
check("empty state visible", win2._empty_box.isVisible())
check("no cards on empty", len(win2._cards) == 0)

# cleanup
win.close()
win2.close()

if failures:
    print(f"\n{len(failures)} FAILURES: {failures}")
    sys.exit(1)
print("\nALL CHECKS PASSED")
