"""Application-wide QSS stylesheet — purple-brand light dashboard theme."""

STYLE_SHEET = """
* {
    font-family: "SF Pro Text", "SF Pro Display", "Segoe UI", "PingFang SC",
                 "Microsoft YaHei", sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #f6f7fb;
    color: #1e1e2a;
}

QWidget {
    background-color: transparent;
    color: #1e1e2a;
}

/* ---------- Sidebar ---------- */
#sideBar {
    background-color: #ffffff;
    border-right: 1px solid #ececf1;
}

#brandRow {
    background-color: transparent;
}

#brandIcon {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #7b4dff, stop:1 #9a6bff);
    border-radius: 9px;
}

#brandName {
    font-size: 16px;
    font-weight: 700;
    color: #1e1e2a;
}

/* sidebar nav buttons */
QPushButton#navButton {
    background-color: transparent;
    color: #7a7a86;
    border: none;
    border-radius: 12px;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 500;
    text-align: left;
}

QPushButton#navButton:hover {
    background-color: #f0f0f6;
    color: #1e1e2a;
}

QPushButton#navButton:checked {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #7b4dff, stop:1 #9a6bff);
    color: #ffffff;
    font-weight: 600;
}

/* ---------- Top bar ---------- */
#topBar {
    background-color: rgba(255, 255, 255, 0.92);
    border-bottom: 1px solid #ececf1;
}

#appTitle {
    font-size: 22px;
    font-weight: 700;
    color: #1e1e2a;
}

#appSubtitle {
    font-size: 12px;
    color: #9a9aa8;
}

/* ---------- Scroll area ---------- */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #d5d5de;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #bcbcc9;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* ---------- Server card ---------- */
#serverCard {
    background-color: #ffffff;
    border: 1px solid #ececf1;
    border-radius: 20px;
}

#serverCard:hover {
    border-color: #d8d8e4;
}

#cardBanner {
    background-color: transparent;
}

#serverName {
    font-size: 15px;
    font-weight: 700;
    color: #1e1e2a;
}

#serverHost {
    font-size: 11px;
    color: #9a9aa8;
}

#statusDot {
    background-color: #34c759;
    border-radius: 5px;
    min-width: 10px;
    max-width: 10px;
    min-height: 10px;
    max-height: 10px;
}

#statusDot.offline {
    background-color: #ff3b30;
}

#statusLabel {
    font-size: 12px;
    font-weight: 600;
    color: #34c759;
}

#statusLabel.offline {
    color: #ff3b30;
}

/* accent tint applied to the banner via dynamic property */
#cardBanner[accent="purple"] { background-color: rgba(123, 77, 255, 0.06); }
#cardBanner[accent="blue"]   { background-color: rgba(74, 140, 255, 0.06); }
#cardBanner[accent="pink"]   { background-color: rgba(255, 111, 168, 0.06); }
#cardBanner[accent="orange"] { background-color: rgba(255, 201, 74, 0.08); }

#metricValue {
    font-size: 24px;
    font-weight: 700;
    color: #1e1e2a;
}

#metricValue.small {
    font-size: 18px;
}

#metricLabel {
    font-size: 11px;
    font-weight: 500;
    color: #9a9aa8;
}

#metricCard {
    background-color: #f6f7fb;
    border-radius: 14px;
}

#metricCard:hover {
    background-color: #f0f0f6;
}

/* ---------- Progress bar (used as gauge) ---------- */
QProgressBar {
    background-color: #f0f0f6;
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
        stop:0 #7b4dff, stop:1 #9a6bff);
}
#gaugeMem QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4a8cff, stop:1 #6c9bff);
}

/* ---------- Chart ---------- */
#chartWidget {
    background-color: #f6f7fb;
    border-radius: 14px;
}

#chartTitle {
    font-size: 11px;
    color: #9a9aa8;
}

/* ---------- Buttons ---------- */
QPushButton {
    background-color: #ffffff;
    color: #1e1e2a;
    border: 1px solid #e3e3ea;
    border-radius: 10px;
    padding: 7px 16px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #f6f6fb;
    border-color: #d0d0dc;
}

QPushButton:pressed {
    background-color: #eef0f6;
}

QPushButton:disabled {
    color: #bcbcc9;
    background-color: #f6f7fb;
    border-color: #ececf1;
}

QPushButton#primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7b4dff, stop:1 #9a6bff);
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
    color: #7b4dff;
    border: 1px solid #e3e3ea;
    border-radius: 10px;
}

QPushButton#secondaryButton:hover {
    background-color: rgba(123, 77, 255, 0.08);
    border-color: #7b4dff;
}

QPushButton#dangerButton {
    background-color: transparent;
    color: #ff3b30;
    border: 1px solid #f3dcdc;
    border-radius: 10px;
}

QPushButton#dangerButton:hover {
    background-color: rgba(255, 59, 48, 0.08);
    border-color: #ff3b30;
}

QPushButton#iconButton {
    background-color: transparent;
    border: none;
    padding: 4px 8px;
    color: #9a9aa8;
}

QPushButton#iconButton:hover {
    color: #1e1e2a;
    background-color: #f0f0f6;
}

/* ---------- Inputs ---------- */
QLineEdit, QSpinBox {
    background-color: #ffffff;
    border: 1px solid #e3e3ea;
    border-radius: 10px;
    padding: 7px 12px;
    color: #1e1e2a;
    selection-background-color: #7b4dff;
}

QLineEdit:focus, QSpinBox:focus {
    border-color: #7b4dff;
}

QLineEdit[echoMode="2"] {
    /* password field */
}

/* ---------- Menus ---------- */
QMenu {
    background-color: #ffffff;
    border: 1px solid #ececf1;
    border-radius: 12px;
    padding: 6px;
}

QMenu::item {
    padding: 7px 24px;
    border-radius: 8px;
}

QMenu::item:selected {
    background-color: #7b4dff;
    color: #ffffff;
}

QToolTip {
    background-color: #ffffff;
    color: #1e1e2a;
    border: 1px solid #ececf1;
    padding: 6px;
}

/* ---------- Status bar ---------- */
QStatusBar {
    background-color: #ffffff;
    color: #9a9aa8;
    border-top: 1px solid #ececf1;
}

QStatusBar::item {
    border: none;
}

/* ---------- Dialogs ---------- */
QDialog {
    background-color: #ffffff;
}

#dialogTitle {
    font-size: 17px;
    font-weight: 700;
    color: #1e1e2a;
}

QLabel#hint {
    color: #9a9aa8;
    font-size: 12px;
}

/* ---------- Empty state ---------- */
#emptyBox {
    background-color: #ffffff;
    border: 1px dashed #d5d5de;
    border-radius: 20px;
}

#emptyTitle {
    font-size: 18px;
    font-weight: 700;
    color: #1e1e2a;
}

#emptyHint {
    font-size: 13px;
    color: #9a9aa8;
}

/* ---------- VNC window toolbar ---------- */
#vncToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #ececf1;
}
"""
