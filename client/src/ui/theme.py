"""Application-wide QSS — purple-brand dashboard theme with light/dark modes.

Colours are kept in TOKENS and injected into the QSS template. Widgets that
paint with QPainter (chart.py) read theme.current() for their palette so a
theme switch recolours them without a restart.
"""

import string

TOKENS = {
    "light": {
        "window_bg": "#f6f7fb",
        "card_bg": "#ffffff",
        "card_hover_border": "#d8d8e4",
        "border": "#ececf1",
        "border_strong": "#e3e3ea",
        "text": "#1e1e2a",
        "text_dim": "#9a9aa8",
        "text_soft": "#86868b",
        "sidebar_bg": "#ffffff",
        "hover": "#f0f0f6",
        "topbar_bg": "rgba(255, 255, 255, 0.92)",
        "chart_bg": "#f6f7fb",
        "chart_grid": "#e8e8ef",
        "chart_empty": "#aeaeb2",
        "chart_legend": "#86868b",
        "tile_bg": "#fafafd",
        "metric_bg": "#f6f7fb",
        "metric_hover": "#f0f0f6",
        "gauge_track": "#f0f0f6",
        "scroll_handle": "#d5d5de",
        "scroll_handle_hover": "#bcbcc9",
        "menu_bg": "#ffffff",
        "input_bg": "#ffffff",
        "btn_bg": "#ffffff",
        "btn_hover": "#f6f6fb",
        "btn_pressed": "#eef0f6",
        "btn_disabled_text": "#bcbcc9",
        "btn_disabled_bg": "#f6f7fb",
        "empty_border": "#d5d5de",
        "statusbar_bg": "#ffffff",
        "dialog_bg": "#ffffff",
        "window_frame": "#d8d8e4",
    },
    "dark": {
        "window_bg": "#15151c",
        "card_bg": "#1f1f28",
        "card_hover_border": "#3a3a46",
        "border": "#2b2b36",
        "border_strong": "#3a3a46",
        "text": "#ececf1",
        "text_dim": "#9a9ab0",
        "text_soft": "#8a8a9c",
        "sidebar_bg": "#1b1b23",
        "hover": "#2a2a35",
        "topbar_bg": "rgba(27, 27, 35, 0.92)",
        "chart_bg": "#23232d",
        "chart_grid": "#33333f",
        "chart_empty": "#7a7a8c",
        "chart_legend": "#9a9ab0",
        "tile_bg": "#262630",
        "metric_bg": "#262630",
        "metric_hover": "#2e2e3a",
        "gauge_track": "#33333f",
        "scroll_handle": "#3c3c49",
        "scroll_handle_hover": "#4a4a58",
        "menu_bg": "#1f1f28",
        "input_bg": "#262630",
        "btn_bg": "#262630",
        "btn_hover": "#2e2e3a",
        "btn_pressed": "#33333f",
        "btn_disabled_text": "#5a5a6a",
        "btn_disabled_bg": "#1f1f28",
        "empty_border": "#3a3a46",
        "statusbar_bg": "#1b1b23",
        "dialog_bg": "#1f1f28",
        "window_frame": "#3a3a46",
    },
}

# brand accents stay the same in both modes
BRAND = {
    "purple": "#7b4dff",
    "purple_end": "#9a6bff",
    "blue": "#4a8cff",
    "green": "#34c759",
    "orange": "#ff9f0a",
    "pink": "#ff6fa8",
    "red": "#ff3b30",
    "yellow": "#eab308",
}

_CURRENT = "light"


def current():
    """Return the active mode name ('light' | 'dark')."""
    return _CURRENT


def tokens():
    """Return the active token dict."""
    return TOKENS[_CURRENT]


def set_mode(name):
    """Switch the module-level mode (used by QPainter widgets)."""
    global _CURRENT
    if name in TOKENS:
        _CURRENT = name


_QSS_TEMPLATE = string.Template("""
* {
    font-family: "SF Pro Text", "SF Pro Display", "Segoe UI", "PingFang SC",
                 "Microsoft YaHei", sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: $window_bg;
    color: $text;
}

QMainWindow {
    border: 1px solid $window_frame;
}

QWidget {
    background-color: transparent;
    color: $text;
}

/* ---------- Sidebar ---------- */
#sideBar {
    background-color: $sidebar_bg;
    border-right: 1px solid $border;
}

#brandRow {
    background-color: transparent;
}

#brandIcon {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 $purple, stop:1 $purple_end);
    border-radius: 9px;
}

#brandName {
    font-size: 16px;
    font-weight: 700;
    color: $text;
}

/* sidebar nav buttons */
QPushButton#navButton {
    background-color: transparent;
    color: $text_dim;
    border: none;
    border-radius: 12px;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 500;
    text-align: left;
}

QPushButton#navButton:hover {
    background-color: $hover;
    color: $text;
}

QPushButton#navButton:checked {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 $purple, stop:1 $purple_end);
    color: #ffffff;
    font-weight: 600;
}

/* theme toggle button sits in the sidebar */
QPushButton#themeButton {
    background-color: transparent;
    color: $text_dim;
    border: 1px solid $border;
    border-radius: 12px;
    padding: 9px 14px;
    font-size: 13px;
    font-weight: 500;
    text-align: left;
}

QPushButton#themeButton:hover {
    background-color: $hover;
    color: $text;
    border-color: $border_strong;
}

/* ---------- Top bar ---------- */
#topBar {
    background-color: $topbar_bg;
    border-bottom: 1px solid $border;
}

#appTitle {
    font-size: 22px;
    font-weight: 700;
    color: $text;
}

#appSubtitle {
    font-size: 12px;
    color: $text_dim;
}

/* ---------- Scroll area ---------- */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

QScrollArea#cardScroll, QScrollArea#cardScroll > QWidget > QWidget {
    background-color: $window_bg;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: $scroll_handle;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: $scroll_handle_hover;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* ---------- Server card ---------- */
#serverCard {
    background-color: $card_bg;
    border: 1px solid $border;
    border-radius: 20px;
}

#serverCard:hover {
    border-color: $card_hover_border;
}

#cardBanner {
    background-color: transparent;
}

#serverName {
    font-size: 15px;
    font-weight: 700;
    color: $text;
}

#serverHost {
    font-size: 11px;
    color: $text_dim;
}

#statusDot {
    background-color: $green;
    border-radius: 5px;
    min-width: 10px;
    max-width: 10px;
    min-height: 10px;
    max-height: 10px;
}

#statusDot.offline {
    background-color: $red;
}

#statusLabel {
    font-size: 12px;
    font-weight: 600;
    color: $green;
}

#statusLabel.offline {
    color: $red;
}

/* accent tint applied to the banner via dynamic property */
#cardBanner[accent="purple"] { background-color: rgba(123, 77, 255, 0.06); }
#cardBanner[accent="blue"]   { background-color: rgba(74, 140, 255, 0.06); }
#cardBanner[accent="pink"]   { background-color: rgba(255, 111, 168, 0.06); }
#cardBanner[accent="orange"] { background-color: rgba(255, 201, 74, 0.08); }

#metricValue {
    font-size: 24px;
    font-weight: 700;
    color: $text;
}

#metricValue.small {
    font-size: 18px;
}

#metricLabel {
    font-size: 11px;
    font-weight: 500;
    color: $text_dim;
}

#metricCard {
    background-color: $metric_bg;
    border-radius: 14px;
}

#metricCard:hover {
    background-color: $metric_hover;
}

/* ---------- Progress bar (used as gauge) ---------- */
QProgressBar {
    background-color: $gauge_track;
    border: none;
    border-radius: 5px;
    height: 9px;
    text-align: center;
}

QProgressBar::chunk {
    border-radius: 5px;
}

#gaugeCpu QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 $purple, stop:1 $purple_end);
}
#gaugeMem QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 $blue, stop:1 #6c9bff);
}

/* ---------- Chart ---------- */
#chartWidget {
    background-color: $chart_bg;
    border-radius: 14px;
}

#chartTitle {
    font-size: 11px;
    color: $text_dim;
}

#chartTile {
    background-color: $tile_bg;
    border: 1px solid $border;
    border-radius: 14px;
}

/* ---------- Buttons ---------- */
QPushButton {
    background-color: $btn_bg;
    color: $text;
    border: 1px solid $border_strong;
    border-radius: 10px;
    padding: 7px 16px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: $btn_hover;
    border-color: #d0d0dc;
}

QPushButton:pressed {
    background-color: $btn_pressed;
}

QPushButton:disabled {
    color: $btn_disabled_text;
    background-color: $btn_disabled_bg;
    border-color: $border;
}

QPushButton#primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 $purple, stop:1 $purple_end);
    color: #ffffff;
    border: none;
    border-radius: 10px;
}

QPushButton#primaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6f3dff, stop:1 #8a5cff);
}

QPushButton#secondaryButton {
    background-color: transparent;
    color: $purple;
    border: 1px solid $border_strong;
    border-radius: 10px;
}

QPushButton#secondaryButton:hover {
    background-color: rgba(123, 77, 255, 0.08);
    border-color: $purple;
}

QPushButton#dangerButton {
    background-color: transparent;
    color: $red;
    border: 1px solid #f3dcdc;
    border-radius: 10px;
}

QPushButton#dangerButton:hover {
    background-color: rgba(255, 59, 48, 0.08);
    border-color: $red;
}

QPushButton#iconButton {
    background-color: transparent;
    border: none;
    padding: 4px 8px;
    color: $text_dim;
}

QPushButton#iconButton:hover {
    color: $text;
    background-color: $hover;
}

/* ---------- Inputs ---------- */
QLineEdit, QSpinBox {
    background-color: $input_bg;
    border: 1px solid $border_strong;
    border-radius: 10px;
    padding: 7px 12px;
    color: $text;
    selection-background-color: $purple;
}

QLineEdit:focus, QSpinBox:focus {
    border-color: $purple;
}

/* ---------- Menus ---------- */
QMenu {
    background-color: $menu_bg;
    border: 1px solid $border;
    border-radius: 12px;
    padding: 6px;
}

QMenu::item {
    padding: 7px 24px;
    border-radius: 8px;
}

QMenu::item:selected {
    background-color: $purple;
    color: #ffffff;
}

QToolTip {
    background-color: $card_bg;
    color: $text;
    border: 1px solid $border;
    padding: 6px;
}

/* ---------- Status bar ---------- */
QStatusBar {
    background-color: $statusbar_bg;
    color: $text_dim;
    border-top: 1px solid $border;
}

QStatusBar::item {
    border: none;
}

/* ---------- Dialogs ---------- */
QDialog {
    background-color: $dialog_bg;
}

#dialogTitle {
    font-size: 17px;
    font-weight: 700;
    color: $text;
}

QLabel#hint {
    color: $text_dim;
    font-size: 12px;
}

/* ---------- Empty state ---------- */
#emptyBox {
    background-color: $card_bg;
    border: 1px dashed $empty_border;
    border-radius: 20px;
}

#emptyTitle {
    font-size: 18px;
    font-weight: 700;
    color: $text;
}

#emptyHint {
    font-size: 13px;
    color: $text_dim;
}

/* ---------- VNC window toolbar ---------- */
#vncToolBar {
    background-color: $statusbar_bg;
    border-bottom: 1px solid $border;
}
""")


def build_stylesheet(mode="light"):
    """Render the QSS template for the given mode."""
    t = TOKENS.get(mode, TOKENS["light"])
    t = dict(t)
    t.update(BRAND)
    return _QSS_TEMPLATE.substitute(t)


def apply_theme(app, mode="light"):
    """Set the active mode and re-apply the stylesheet app-wide."""
    set_mode(mode)
    app.setStyleSheet(build_stylesheet(mode))


STYLE_SHEET = build_stylesheet("light")
