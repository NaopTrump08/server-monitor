"""Liquid-glass theme — palette tokens + QSS for the Server Monitor client.

The ambient background widget (background.py) paints the colourful glow blobs;
glass panels are translucent so that glow refracts through. Tokens are kept in
one place and injected into a string.Template QSS, with a light/dark switch.
"""

import string

from PySide6.QtWidgets import QApplication

TOKENS = {
    "dark": {
        "window_bg": "#07080f",
        "text": "#f5f6fb",
        "text_dim": "#b6b9cc",
        "text_soft": "#8a8ea6",
        "glass_hi": "rgba(255, 255, 255, 42)",
        "glass_lo": "rgba(255, 255, 255, 8)",
        "glass_border": "rgba(255, 255, 255, 54)",
        "glass_border_soft": "rgba(255, 255, 255, 34)",
        "hover": "rgba(255, 255, 255, 26)",
        "input_bg": "rgba(255, 255, 255, 22)",
        "input_border": "rgba(255, 255, 255, 36)",
        "btn_ghost_bg": "rgba(255, 255, 255, 20)",
        "btn_ghost_border": "rgba(255, 255, 255, 36)",
        "btn_ghost_hover": "rgba(255, 255, 255, 34)",
        "scroll_handle": "rgba(255, 255, 255, 60)",
        "menu_bg": "rgba(26, 26, 36, 245)",
    },
    "light": {
        "window_bg": "#eef0f7",
        "text": "#1b1c28",
        "text_dim": "#5a5d72",
        "text_soft": "#8a8ea6",
        "glass_hi": "rgba(255, 255, 255, 210)",
        "glass_lo": "rgba(255, 255, 255, 120)",
        "glass_border": "rgba(255, 255, 255, 220)",
        "glass_border_soft": "rgba(30, 30, 60, 30)",
        "hover": "rgba(255, 255, 255, 150)",
        "input_bg": "rgba(255, 255, 255, 190)",
        "input_border": "rgba(30, 30, 60, 40)",
        "btn_ghost_bg": "rgba(255, 255, 255, 170)",
        "btn_ghost_border": "rgba(30, 30, 60, 36)",
        "btn_ghost_hover": "rgba(255, 255, 255, 230)",
        "scroll_handle": "rgba(30, 30, 60, 60)",
        "menu_bg": "rgba(255, 255, 255, 250)",
    },
}

BRAND = {
    "purple": "#9b6cff",
    "blue": "#5aa7ff",
    "cyan": "#38e0ff",
    "green": "#34c759",
    "orange": "#ff9f0a",
    "pink": "#ff5ea8",
    "red": "#ff3b30",
}

_CURRENT = "dark"


def current():
    return _CURRENT


def tokens():
    return TOKENS[_CURRENT]


def set_mode(name):
    global _CURRENT
    if name in TOKENS:
        _CURRENT = name


_QSS = string.Template("""
* {
    font-family: "Segoe UI", "Microsoft YaHei UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}

QMainWindow {
    background: transparent;
    color: $text;
}
QDialog {
    background: $window_bg;
    color: $text;
}

QScrollArea {
    background: transparent;
    border: none;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}

QLabel {
    background: transparent;
    color: $text;
}
QLabel#appTitle { font-size: 22px; font-weight: 700; letter-spacing: 0.3px; }
QLabel#appSubtitle { font-size: 12px; color: $text_soft; }
QLabel#brandName { font-size: 17px; font-weight: 700; }
QLabel#brandSub { font-size: 11px; color: $text_soft; }
QLabel#sectionTitle { font-size: 15px; font-weight: 600; }
QLabel#cardTitle { font-size: 16px; font-weight: 600; }
QLabel#cardHost { font-size: 11px; color: $text_soft; }
QLabel#latencyValue { font-size: 13px; font-weight: 600; }
QLabel#latencyLbl { font-size: 10px; color: $text_soft; }
QLabel#tileNum { font-size: 26px; font-weight: 700; }
QLabel#tileLbl { font-size: 12px; color: $text_soft; }
QLabel#tileTrend { font-size: 12px; font-weight: 600; }
QLabel#metricName { font-size: 14px; font-weight: 600; }
QLabel#metricValue { font-size: 28px; font-weight: 700; }
QLabel#metricDelta { font-size: 12px; font-weight: 600; }
QLabel#metricNote { font-size: 11px; color: $text_soft; }
QLabel#dialogTitle { font-size: 18px; font-weight: 700; }
QLabel#hint { color: $text_soft; font-size: 12px; }
QLabel#navLabel { font-size: 11px; color: $text_soft; letter-spacing: 1.5px; }
QLabel#userName { font-size: 13px; font-weight: 600; }
QLabel#userMail { font-size: 11px; color: $text_soft; }

QPushButton {
    border: none;
    background: transparent;
    color: $text;
    outline: none;
}
QPushButton#primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9b6cff, stop:1 #4d7cff);
    color: #ffffff;
    font-weight: 600;
    border-radius: 16px;
    padding: 11px 20px;
}
QPushButton#primaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ab7dff, stop:1 #5f8bff);
}
QPushButton#primaryButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8b5cef, stop:1 #3f6ef0);
}
QPushButton#ghostButton {
    background: $btn_ghost_bg;
    border: 1px solid $btn_ghost_border;
    border-radius: 13px;
    padding: 9px 0;
    color: $text_dim;
    font-weight: 550;
}
QPushButton#ghostButton:hover {
    background: $btn_ghost_hover;
    color: $text;
}
QPushButton#ghostButton[accent="true"] {
    background: $btn_ghost_hover;
    color: $text;
    border-color: rgba(255, 255, 255, 70);
}
QPushButton#dangerButton {
    background: rgba(255, 59, 48, 34);
    border: 1px solid rgba(255, 59, 48, 80);
    border-radius: 13px;
    padding: 9px 0;
    color: #ff8a80;
}
QPushButton#dangerButton:hover {
    background: rgba(255, 59, 48, 60);
}
QPushButton#iconButton {
    background: $btn_ghost_bg;
    border: 1px solid $btn_ghost_border;
    border-radius: 15px;
    color: $text;
}
QPushButton#iconButton:hover { background: $btn_ghost_hover; }
QPushButton#navButton {
    text-align: left;
    padding: 11px 14px;
    border-radius: 14px;
    color: $text_dim;
    font-size: 14px;
    font-weight: 500;
}
QPushButton#navButton:hover { color: $text; }
QPushButton#navButton:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255,255,255,44), stop:1 rgba(255,255,255,14));
    border: 1px solid $glass_border;
    color: $text;
    font-weight: 600;
}

QLineEdit, QSpinBox {
    background: $input_bg;
    border: 1px solid $input_border;
    border-radius: 12px;
    padding: 9px 12px;
    color: $text;
}
QLineEdit:focus, QSpinBox:focus {
    border: 1px solid rgba(255, 255, 255, 80);
}

QComboBox {
    background: $input_bg;
    border: 1px solid $input_border;
    border-radius: 12px;
    padding: 8px 12px;
    color: $text;
}
QComboBox QAbstractItemView {
    background: $menu_bg;
    border: 1px solid $glass_border_soft;
    border-radius: 10px;
    selection-background-color: $hover;
    color: $text;
}

QToolTip {
    background: #1f1f28;
    color: #f5f6fb;
    border: 1px solid rgba(255, 255, 255, 40);
    padding: 6px 10px;
}
QMenu {
    background: $menu_bg;
    border: 1px solid $glass_border_soft;
    border-radius: 12px;
    padding: 6px;
}
QMenu::item {
    padding: 8px 24px;
    border-radius: 8px;
    color: $text_dim;
}
QMenu::item:selected {
    background: $hover;
    color: $text;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: $scroll_handle;
    border-radius: 5px;
    min-height: 40px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }

QStatusBar {
    background: transparent;
    color: $text_soft;
}
""")


def build_stylesheet(mode=None):
    if mode:
        set_mode(mode)
    return _QSS.substitute(TOKENS[_CURRENT])


def apply_theme(app, mode):
    set_mode(mode)
    app.setStyleSheet(build_stylesheet())
