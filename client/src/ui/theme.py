"""Application-wide QSS stylesheet — Apple-inspired light theme."""

STYLE_SHEET = """
* {
    font-family: "SF Pro Text", "SF Pro Display", "Segoe UI", "PingFang SC",
                 "Microsoft YaHei", sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #f5f5f7;
    color: #1d1d1f;
}

QWidget {
    background-color: transparent;
    color: #1d1d1f;
}

/* ---------- Top bar ---------- */
#topBar {
    background-color: rgba(250, 250, 252, 0.85);
    border-bottom: 1px solid #e3e3e8;
}

#appTitle {
    font-size: 17px;
    font-weight: 600;
    color: #1d1d1f;
}

#appSubtitle {
    font-size: 12px;
    color: #86868b;
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
    background: #c7c7cc;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #aeaeb2;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* ---------- Server card ---------- */
#serverCard {
    background-color: #ffffff;
    border: 1px solid #e3e3e8;
    border-radius: 16px;
}

#serverCard:hover {
    border-color: #d0d0d5;
}

#cardHeader {
    background-color: transparent;
}

#serverName {
    font-size: 15px;
    font-weight: 600;
    color: #1d1d1f;
}

#serverHost {
    font-size: 11px;
    color: #86868b;
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

#metricValue {
    font-size: 22px;
    font-weight: 700;
    color: #1d1d1f;
}

#metricValue.small {
    font-size: 18px;
}

#metricLabel {
    font-size: 11px;
    color: #86868b;
}

#metricCard {
    background-color: #f5f5f7;
    border-radius: 12px;
}

#metricCard:hover {
    background-color: #efeff1;
}

/* ---------- Progress bar (used as gauge) ---------- */
QProgressBar {
    background-color: #ececf0;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    border-radius: 4px;
}

#gaugeCpu QProgressBar::chunk { background-color: #0071e3; }
#gaugeMem QProgressBar::chunk { background-color: #af52de; }

/* ---------- Chart ---------- */
#chartWidget {
    background-color: #f5f5f7;
    border-radius: 12px;
}

#chartTitle {
    font-size: 11px;
    color: #86868b;
}

/* ---------- Buttons ---------- */
QPushButton {
    background-color: #f5f5f7;
    color: #1d1d1f;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #ebebf0;
    border-color: #c7c7cc;
}

QPushButton:pressed {
    background-color: #e3e3e8;
}

QPushButton:disabled {
    color: #aeaeb2;
    background-color: #f5f5f7;
    border-color: #e3e3e8;
}

QPushButton#primaryButton {
    background-color: #0071e3;
    color: #ffffff;
    border: none;
    border-radius: 8px;
}

QPushButton#primaryButton:hover {
    background-color: #0077ed;
}

QPushButton#secondaryButton {
    background-color: transparent;
    color: #0071e3;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
}

QPushButton#secondaryButton:hover {
    background-color: rgba(0, 113, 227, 0.08);
    border-color: #0071e3;
}

QPushButton#dangerButton {
    background-color: transparent;
    color: #ff3b30;
    border: 1px solid #f0d2d0;
    border-radius: 8px;
}

QPushButton#dangerButton:hover {
    background-color: rgba(255, 59, 48, 0.08);
    border-color: #ff3b30;
}

QPushButton#iconButton {
    background-color: transparent;
    border: none;
    padding: 4px 8px;
    color: #86868b;
}

QPushButton#iconButton:hover {
    color: #1d1d1f;
    background-color: #ebebf0;
}

/* ---------- Inputs ---------- */
QLineEdit, QSpinBox {
    background-color: #ffffff;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    padding: 6px 10px;
    color: #1d1d1f;
    selection-background-color: #0071e3;
}

QLineEdit:focus, QSpinBox:focus {
    border-color: #0071e3;
}

QLineEdit[echoMode="2"] {
    /* password field */
}

/* ---------- Tables ---------- */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e3e3e8;
    border-radius: 8px;
    gridline-color: #e3e3e8;
}

QTableWidget::item {
    padding: 4px;
}

QTableWidget QHeaderView::section {
    background-color: #f5f5f7;
    color: #86868b;
    border: none;
    border-bottom: 1px solid #e3e3e8;
    padding: 6px;
    font-weight: 600;
}

/* ---------- Menus ---------- */
QMenu {
    background-color: #ffffff;
    border: 1px solid #e3e3e8;
    border-radius: 10px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px;
    border-radius: 6px;
}

QMenu::item:selected {
    background-color: #0071e3;
    color: #ffffff;
}

QToolTip {
    background-color: #ffffff;
    color: #1d1d1f;
    border: 1px solid #e3e3e8;
    padding: 6px;
}

/* ---------- Status bar ---------- */
QStatusBar {
    background-color: #f5f5f7;
    color: #86868b;
    border-top: 1px solid #e3e3e8;
}

QStatusBar::item {
    border: none;
}

/* ---------- Dialogs ---------- */
QDialog {
    background-color: #ffffff;
}

#dialogTitle {
    font-size: 16px;
    font-weight: 600;
    color: #1d1d1f;
}

QLabel#hint {
    color: #86868b;
    font-size: 12px;
}

/* ---------- Empty state ---------- */
#emptyBox {
    background-color: #ffffff;
    border: 1px dashed #c7c7cc;
    border-radius: 16px;
}

#emptyTitle {
    font-size: 18px;
    font-weight: 600;
    color: #1d1d1f;
}

#emptyHint {
    font-size: 13px;
    color: #86868b;
}
"""
