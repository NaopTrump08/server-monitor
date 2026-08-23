"""Application-wide QSS stylesheet — clean dark theme."""

STYLE_SHEET = """
* {
    font-family: "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #0f1420;
    color: #e6edf3;
}

QWidget {
    background-color: transparent;
    color: #e6edf3;
}

/* ---------- Top bar ---------- */
#topBar {
    background-color: #151b2b;
    border-bottom: 1px solid #232c40;
}

#appTitle {
    font-size: 17px;
    font-weight: 600;
    color: #ffffff;
}

#appSubtitle {
    font-size: 12px;
    color: #8b96ab;
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
    background: #2a3448;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #3a4763;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* ---------- Server card ---------- */
#serverCard {
    background-color: #161d2e;
    border: 1px solid #222b40;
    border-radius: 12px;
}

#serverCard:hover {
    border-color: #3b82f6;
}

#cardHeader {
    background-color: transparent;
}

#serverName {
    font-size: 15px;
    font-weight: 600;
    color: #ffffff;
}

#serverHost {
    font-size: 11px;
    color: #8b96ab;
}

#statusDot {
    background-color: #22c55e;
    border-radius: 5px;
    min-width: 10px;
    max-width: 10px;
    min-height: 10px;
    max-height: 10px;
}

#statusDot.offline {
    background-color: #ef4444;
}

#statusLabel {
    font-size: 12px;
    font-weight: 600;
    color: #22c55e;
}

#statusLabel.offline {
    color: #ef4444;
}

#metricValue {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
}

#metricValue.small {
    font-size: 18px;
}

#metricLabel {
    font-size: 11px;
    color: #8b96ab;
}

#metricCard {
    background-color: #1a2235;
    border-radius: 8px;
}

#metricCard:hover {
    background-color: #1e2740;
}

/* ---------- Progress bar (used as gauge) ---------- */
QProgressBar {
    background-color: #1a2235;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    border-radius: 4px;
}

#gaugeCpu QProgressBar::chunk { background-color: #3b82f6; }
#gaugeMem QProgressBar::chunk { background-color: #a855f7; }

/* ---------- Chart ---------- */
#chartWidget {
    background-color: #1a2235;
    border-radius: 8px;
}

#chartTitle {
    font-size: 11px;
    color: #8b96ab;
}

/* ---------- Buttons ---------- */
QPushButton {
    background-color: #1e2740;
    color: #e6edf3;
    border: 1px solid #2a3448;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #26325a;
    border-color: #3b82f6;
}

QPushButton:pressed {
    background-color: #1a2340;
}

QPushButton:disabled {
    color: #5b657a;
    background-color: #1a2030;
    border-color: #232c40;
}

QPushButton#primaryButton {
    background-color: #3b82f6;
    color: #ffffff;
    border: none;
}

QPushButton#primaryButton:hover {
    background-color: #2563eb;
}

QPushButton#dangerButton {
    background-color: transparent;
    color: #ef4444;
    border: 1px solid #3a2a35;
}

QPushButton#dangerButton:hover {
    background-color: rgba(239, 68, 68, 0.12);
    border-color: #ef4444;
}

QPushButton#iconButton {
    background-color: transparent;
    border: none;
    padding: 4px 8px;
    color: #8b96ab;
}

QPushButton#iconButton:hover {
    color: #ffffff;
    background-color: #1a2235;
}

/* ---------- Inputs ---------- */
QLineEdit, QSpinBox {
    background-color: #0f1420;
    border: 1px solid #2a3448;
    border-radius: 6px;
    padding: 6px 10px;
    color: #e6edf3;
    selection-background-color: #3b82f6;
}

QLineEdit:focus, QSpinBox:focus {
    border-color: #3b82f6;
}

QLineEdit[echoMode="2"] {
    /* password field */
}

/* ---------- Tables ---------- */
QTableWidget {
    background-color: #161d2e;
    border: 1px solid #222b40;
    border-radius: 8px;
    gridline-color: #222b40;
}

QTableWidget::item {
    padding: 4px;
}

QTableWidget QHeaderView::section {
    background-color: #1a2235;
    color: #8b96ab;
    border: none;
    border-bottom: 1px solid #2a3448;
    padding: 6px;
    font-weight: 600;
}

/* ---------- Menus ---------- */
QMenu {
    background-color: #161d2e;
    border: 1px solid #2a3448;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #3b82f6;
    color: #ffffff;
}

QToolTip {
    background-color: #1a2235;
    color: #e6edf3;
    border: 1px solid #2a3448;
    padding: 6px;
}

/* ---------- Status bar ---------- */
QStatusBar {
    background-color: #151b2b;
    color: #8b96ab;
    border-top: 1px solid #232c40;
}

QStatusBar::item {
    border: none;
}

/* ---------- Dialogs ---------- */
QDialog {
    background-color: #0f1420;
}

#dialogTitle {
    font-size: 16px;
    font-weight: 600;
    color: #ffffff;
}

QLabel#hint {
    color: #8b96ab;
    font-size: 12px;
}
"""
