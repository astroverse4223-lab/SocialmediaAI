"""Application QSS themes (dark and light)."""

DARK = """
/* ─── GLOBAL ─────────────────────────────────────────────── */
* {
    font-family: "Segoe UI Variable", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 12px;
    color: #E2E2F0;
    outline: none;
}
QMainWindow, QDialog {
    background-color: #0D0D14;
}
QWidget {
    background-color: transparent;
    color: #E2E2F0;
}
QFrame {
    background-color: transparent;
}

/* ─── SCROLLBARS ──────────────────────────────────────────── */
QScrollBar:vertical {
    background: #15151F;
    width: 7px;
    border-radius: 3px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #383855;
    border-radius: 3px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover { background: #5A5A8A; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

QScrollBar:horizontal {
    background: #15151F;
    height: 7px;
    border-radius: 3px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: #383855;
    border-radius: 3px;
    min-width: 24px;
}
QScrollBar::handle:horizontal:hover { background: #5A5A8A; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ─── BUTTONS ─────────────────────────────────────────────── */
QPushButton {
    background-color: #1E1E2E;
    color: #E2E2F0;
    border: 1px solid #2D2D42;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: 500;
    min-height: 32px;
}
QPushButton:hover {
    background-color: #252535;
    border-color: #4F46E5;
}
QPushButton:pressed { background-color: #1A1A28; }
QPushButton:disabled {
    background-color: #141420;
    color: #3A3A5A;
    border-color: #1E1E2E;
}
QPushButton#primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7C3AED, stop:1 #4F46E5);
    color: #FFFFFF;
    border: none;
    font-weight: 700;
}
QPushButton#primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #8B4AF5, stop:1 #5F56F0);
}
QPushButton#primary:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6B2ADB, stop:1 #3F36D0);
}
QPushButton#primary:disabled {
    background: #2A2A42;
    color: #5A5A7A;
}
QPushButton#success {
    background-color: #059669;
    color: #FFFFFF;
    border: none;
    font-weight: 600;
}
QPushButton#success:hover { background-color: #10B981; }
QPushButton#success:pressed { background-color: #047857; }

QPushButton#warning {
    background-color: #D97706;
    color: #FFFFFF;
    border: none;
    font-weight: 600;
}
QPushButton#danger {
    background-color: transparent;
    color: #EF4444;
    border: 1px solid #EF4444;
}
QPushButton#danger:hover {
    background-color: #EF4444;
    color: #FFFFFF;
}
QPushButton#ghost {
    background-color: transparent;
    border: none;
    color: #8080A0;
    padding: 6px 10px;
}
QPushButton#ghost:hover {
    background-color: #1E1E2E;
    color: #E2E2F0;
}
QPushButton#icon_btn {
    background-color: transparent;
    border: none;
    color: #8080A0;
    padding: 4px;
    border-radius: 6px;
    font-size: 16px;
}
QPushButton#icon_btn:hover {
    background-color: #252535;
    color: #E2E2F0;
}
QPushButton#sidebar_btn {
    background-color: transparent;
    border: none;
    border-radius: 10px;
    color: #8080A0;
    padding: 10px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
}
QPushButton#sidebar_btn:hover {
    background-color: #1E1E2E;
    color: #D0D0F0;
}
QPushButton#sidebar_btn_active {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(124,58,237,0.25), stop:1 rgba(79,70,229,0.15));
    border: none;
    border-left: 3px solid #7C3AED;
    border-radius: 0px 10px 10px 0px;
    color: #C4B5FD;
    padding: 10px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
}

/* ─── INPUTS ──────────────────────────────────────────────── */
QLineEdit {
    background-color: #13131C;
    color: #E2E2F0;
    border: 1.5px solid #2D2D42;
    border-radius: 9px;
    padding: 10px 14px;
    font-size: 13px;
    selection-background-color: #4F46E5;
    selection-color: #FFFFFF;
}
QLineEdit:focus {
    border-color: #7C3AED;
    background-color: #17172A;
}
QLineEdit:hover:!focus { border-color: #404060; }
QLineEdit[placeholderText]:!focus { color: #E2E2F0; }

QTextEdit, QPlainTextEdit {
    background-color: #13131C;
    color: #E2E2F0;
    border: 1.5px solid #2D2D42;
    border-radius: 9px;
    padding: 12px;
    font-size: 13px;
    line-height: 1.6;
    selection-background-color: #4F46E5;
    selection-color: #FFFFFF;
}
QTextEdit:focus, QPlainTextEdit:focus { border-color: #7C3AED; }

/* ─── LABELS ──────────────────────────────────────────────── */
QLabel {
    color: #E2E2F0;
    background: transparent;
}
QLabel#h1 { font-size: 26px; font-weight: 800; color: #FFFFFF; }
QLabel#h2 { font-size: 20px; font-weight: 700; color: #EFEFFF; }
QLabel#h3 { font-size: 15px; font-weight: 600; color: #D0D0F0; }
QLabel#subtitle { font-size: 12px; color: #7070A0; }
QLabel#caption { font-size: 11px; color: #5A5A80; }
QLabel#accent { color: #A78BFA; font-weight: 600; }
QLabel#success { color: #34D399; }
QLabel#error { color: #F87171; }
QLabel#warning { color: #FBBF24; }
QLabel#badge {
    background-color: #7C3AED;
    color: white;
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}

/* ─── TABS ────────────────────────────────────────────────── */
QTabWidget::pane {
    background-color: #13131C;
    border: 1px solid #2D2D42;
    border-radius: 10px;
    border-top-left-radius: 0px;
    padding: 4px;
}
QTabBar {
    background: transparent;
}
QTabBar::tab {
    background-color: #1A1A26;
    color: #7070A0;
    padding: 9px 20px;
    border: 1px solid #2D2D42;
    border-bottom: none;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-size: 12px;
    font-weight: 500;
}
QTabBar::tab:selected {
    background-color: #13131C;
    color: #E2E2F0;
    border-bottom: 2.5px solid #7C3AED;
    font-weight: 700;
}
QTabBar::tab:hover:!selected {
    background-color: #1E1E30;
    color: #B0B0D0;
}
QTabBar::scroller {
    width: 0;
}

/* ─── COMBOBOX ────────────────────────────────────────────── */
QComboBox {
    background-color: #13131C;
    color: #E2E2F0;
    border: 1.5px solid #2D2D42;
    border-radius: 8px;
    padding: 8px 36px 8px 14px;
    font-size: 12px;
    min-width: 100px;
}
QComboBox:hover { border-color: #404060; }
QComboBox:focus { border-color: #7C3AED; }
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border: none;
    border-left: 1px solid #2D2D42;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
    background: transparent;
}
QComboBox::down-arrow {
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #8080A0;
    margin-right: 4px;
}
QComboBox QAbstractItemView {
    background-color: #1E1E2E;
    color: #E2E2F0;
    border: 1px solid #2D2D42;
    border-radius: 8px;
    selection-background-color: #4F46E5;
    selection-color: white;
    outline: none;
    padding: 4px;
}
QComboBox QAbstractItemView::item {
    padding: 8px 14px;
    border-radius: 4px;
    min-height: 28px;
}

/* ─── PROGRESS BAR ────────────────────────────────────────── */
QProgressBar {
    background-color: #1E1E2E;
    border: none;
    border-radius: 5px;
    height: 8px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7C3AED, stop:1 #4F46E5);
    border-radius: 5px;
}

/* ─── SPLITTER ────────────────────────────────────────────── */
QSplitter::handle {
    background-color: #1E1E2E;
    width: 2px;
    height: 2px;
}
QSplitter::handle:hover {
    background-color: #7C3AED;
}

/* ─── LIST / TREE ─────────────────────────────────────────── */
QListWidget, QTreeWidget {
    background-color: #13131C;
    color: #E2E2F0;
    border: 1px solid #2D2D42;
    border-radius: 10px;
    outline: none;
    padding: 6px;
}
QListWidget::item, QTreeWidget::item {
    padding: 9px 12px;
    border-radius: 7px;
    margin: 1px 2px;
}
QListWidget::item:selected, QTreeWidget::item:selected {
    background-color: #4F46E5;
    color: white;
}
QListWidget::item:hover:!selected, QTreeWidget::item:hover:!selected {
    background-color: #1E1E2E;
}
QTreeWidget::branch {
    background: transparent;
}

/* ─── CHECKBOXES & RADIO ──────────────────────────────────── */
QCheckBox, QRadioButton {
    color: #C0C0E0;
    spacing: 8px;
    font-size: 12px;
}
QCheckBox::indicator {
    width: 17px; height: 17px;
    border: 2px solid #3A3A5A;
    border-radius: 4px;
    background: #13131C;
}
QCheckBox::indicator:checked {
    background-color: #7C3AED;
    border-color: #7C3AED;
    image: url("data:image/svg+xml,<svg/>"); /* placeholder */
}
QCheckBox::indicator:hover { border-color: #7C3AED; }
QRadioButton::indicator {
    width: 17px; height: 17px;
    border: 2px solid #3A3A5A;
    border-radius: 9px;
    background: #13131C;
}
QRadioButton::indicator:checked {
    background-color: #7C3AED;
    border-color: #7C3AED;
}

/* ─── SLIDER ──────────────────────────────────────────────── */
QSlider::groove:horizontal {
    background: #2A2A3E;
    height: 5px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #7C3AED;
    width: 18px; height: 18px;
    margin: -7px 0;
    border-radius: 9px;
}
QSlider::handle:horizontal:hover { background: #9C5AFF; }
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7C3AED, stop:1 #4F46E5);
    border-radius: 2px;
}

/* ─── SPIN BOX ────────────────────────────────────────────── */
QSpinBox, QDoubleSpinBox {
    background-color: #13131C;
    color: #E2E2F0;
    border: 1.5px solid #2D2D42;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
}
QSpinBox:focus, QDoubleSpinBox:focus { border-color: #7C3AED; }
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: transparent;
    border: none;
    width: 22px;
}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #8080A0;
}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #8080A0;
}

/* ─── MENU ────────────────────────────────────────────────── */
QMenuBar {
    background-color: #0D0D14;
    color: #C0C0E0;
    border-bottom: 1px solid #1E1E2E;
    padding: 2px 8px;
    font-size: 12px;
}
QMenuBar::item { padding: 6px 12px; border-radius: 5px; }
QMenuBar::item:selected { background-color: #1E1E2E; }
QMenu {
    background-color: #1A1A28;
    border: 1px solid #2D2D42;
    border-radius: 10px;
    padding: 6px;
    font-size: 12px;
}
QMenu::item { padding: 9px 24px; border-radius: 6px; }
QMenu::item:selected { background-color: #4F46E5; color: white; }
QMenu::separator {
    background-color: #2D2D42;
    height: 1px;
    margin: 4px 10px;
}

/* ─── STATUS BAR ──────────────────────────────────────────── */
QStatusBar {
    background-color: #0D0D14;
    color: #6060A0;
    border-top: 1px solid #1E1E2E;
    font-size: 11px;
    padding: 0 8px;
}
QStatusBar::item { border: none; }

/* ─── TOOLTIP ─────────────────────────────────────────────── */
QToolTip {
    background-color: #1E1E2E;
    color: #E2E2F0;
    border: 1px solid #4F46E5;
    border-radius: 7px;
    padding: 7px 12px;
    font-size: 11px;
}

/* ─── SCROLL AREA ─────────────────────────────────────────── */
QScrollArea {
    border: none;
    background: transparent;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}

/* ─── SIDEBAR ─────────────────────────────────────────────── */
QWidget#sidebar {
    background-color: #0D0D14;
    border-right: 1px solid #1E1E2E;
}
QWidget#sidebar_header {
    background-color: #0D0D14;
    border-bottom: 1px solid #1E1E2E;
}

/* ─── CARDS ───────────────────────────────────────────────── */
QFrame#card {
    background-color: #15151F;
    border: 1px solid #2A2A3A;
    border-radius: 14px;
}
QFrame#card_elevated {
    background-color: #1A1A28;
    border: 1px solid #2D2D42;
    border-radius: 14px;
}
QFrame#accent_card {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(124,58,237,0.15), stop:1 rgba(79,70,229,0.08));
    border: 1px solid rgba(124,58,237,0.4);
    border-radius: 14px;
}
QFrame#stat_card {
    background-color: #15151F;
    border: 1px solid #2A2A3A;
    border-radius: 14px;
    padding: 6px;
}

/* ─── HEADER BAR ──────────────────────────────────────────── */
QWidget#page_header {
    background-color: #0F0F1A;
    border-bottom: 1px solid #1E1E2E;
}
QWidget#content_area {
    background-color: #0D0D14;
}
"""

LIGHT = """
/* ─── GLOBAL ─────────────────────────────────────────────── */
* {
    font-family: "Segoe UI Variable", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 12px;
    color: #1A1A2E;
    outline: none;
}
QMainWindow, QDialog { background-color: #F2F2F7; }
QWidget { background-color: transparent; color: #1A1A2E; }
QFrame { background-color: transparent; }

QScrollBar:vertical {
    background: #E8E8F0; width: 7px; border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #BBBBD0; border-radius: 3px; min-height: 24px;
}
QScrollBar::handle:vertical:hover { background: #9090C0; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: #E8E8F0; height: 7px; border-radius: 3px;
}
QScrollBar::handle:horizontal {
    background: #BBBBD0; border-radius: 3px; min-width: 24px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

QPushButton {
    background-color: #FFFFFF;
    color: #1A1A2E;
    border: 1px solid #DDDDE8;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: 500;
    min-height: 32px;
}
QPushButton:hover { background-color: #F0F0F8; border-color: #7C3AED; }
QPushButton:pressed { background-color: #E8E8F5; }
QPushButton:disabled { color: #AAAACC; border-color: #E0E0EE; }

QPushButton#primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7C3AED, stop:1 #4F46E5);
    color: white; border: none; font-weight: 700;
}
QPushButton#primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #8B4AF5, stop:1 #5F56F0);
}
QPushButton#primary:disabled { background: #CCCCEE; color: #888899; }

QPushButton#success { background-color: #059669; color: white; border: none; font-weight: 600; }
QPushButton#success:hover { background-color: #10B981; }
QPushButton#danger { color: #DC2626; border: 1px solid #DC2626; background: transparent; }
QPushButton#danger:hover { background: #DC2626; color: white; }
QPushButton#ghost { background: transparent; border: none; color: #6060AA; }
QPushButton#ghost:hover { background: #F0F0F8; color: #1A1A2E; }
QPushButton#icon_btn { background: transparent; border: none; color: #6060AA; font-size: 16px; border-radius: 6px; padding: 4px; }
QPushButton#icon_btn:hover { background: #E8E8F5; color: #1A1A2E; }
QPushButton#sidebar_btn {
    background: transparent; border: none; border-radius: 10px;
    color: #5A5A8A; padding: 10px 16px; text-align: left; font-size: 13px; font-weight: 500;
}
QPushButton#sidebar_btn:hover { background: #EBEBF5; color: #2A2A4E; }
QPushButton#sidebar_btn_active {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(124,58,237,0.15), stop:1 rgba(79,70,229,0.08));
    border: none; border-left: 3px solid #7C3AED;
    border-radius: 0px 10px 10px 0px;
    color: #7C3AED; padding: 10px 16px; text-align: left;
    font-size: 13px; font-weight: 600;
}

QLineEdit {
    background-color: #FFFFFF; color: #1A1A2E;
    border: 1.5px solid #DDDDE8; border-radius: 9px;
    padding: 10px 14px; font-size: 13px;
    selection-background-color: #7C3AED; selection-color: white;
}
QLineEdit:focus { border-color: #7C3AED; }
QLineEdit:hover:!focus { border-color: #AAAACC; }

QTextEdit, QPlainTextEdit {
    background-color: #FFFFFF; color: #1A1A2E;
    border: 1.5px solid #DDDDE8; border-radius: 9px;
    padding: 12px; font-size: 13px;
    selection-background-color: #7C3AED; selection-color: white;
}
QTextEdit:focus, QPlainTextEdit:focus { border-color: #7C3AED; }

QLabel { color: #1A1A2E; background: transparent; }
QLabel#h1 { font-size: 26px; font-weight: 800; color: #0D0D1A; }
QLabel#h2 { font-size: 20px; font-weight: 700; }
QLabel#h3 { font-size: 15px; font-weight: 600; }
QLabel#subtitle { font-size: 12px; color: #6060AA; }
QLabel#caption { font-size: 11px; color: #8888AA; }
QLabel#accent { color: #7C3AED; font-weight: 600; }
QLabel#success { color: #059669; }
QLabel#error { color: #DC2626; }

QTabWidget::pane {
    background-color: #FFFFFF; border: 1px solid #DDDDE8;
    border-radius: 10px; border-top-left-radius: 0px;
}
QTabBar::tab {
    background-color: #EBEBF5; color: #6060AA;
    padding: 9px 20px; border: 1px solid #DDDDE8;
    border-bottom: none; margin-right: 2px;
    border-top-left-radius: 8px; border-top-right-radius: 8px;
}
QTabBar::tab:selected {
    background-color: #FFFFFF; color: #1A1A2E;
    border-bottom: 2.5px solid #7C3AED; font-weight: 700;
}
QTabBar::tab:hover:!selected { background-color: #E0E0F0; }

QComboBox {
    background-color: #FFFFFF; color: #1A1A2E;
    border: 1.5px solid #DDDDE8; border-radius: 8px;
    padding: 8px 36px 8px 14px; font-size: 12px;
}
QComboBox:focus { border-color: #7C3AED; }
QComboBox::drop-down { border: none; width: 28px; border-left: 1px solid #DDDDE8; background: transparent; }
QComboBox::down-arrow { border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid #6060AA; margin-right: 4px; }
QComboBox QAbstractItemView {
    background: #FFFFFF; color: #1A1A2E;
    border: 1px solid #DDDDE8; border-radius: 8px;
    selection-background-color: #7C3AED; selection-color: white; padding: 4px;
}

QProgressBar {
    background-color: #E8E8F0; border: none; border-radius: 5px; height: 8px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7C3AED, stop:1 #4F46E5);
    border-radius: 5px;
}

QSplitter::handle { background-color: #DDDDE8; width: 2px; height: 2px; }
QSplitter::handle:hover { background-color: #7C3AED; }

QListWidget, QTreeWidget {
    background-color: #FFFFFF; color: #1A1A2E;
    border: 1px solid #DDDDE8; border-radius: 10px; padding: 6px;
}
QListWidget::item, QTreeWidget::item { padding: 9px 12px; border-radius: 7px; margin: 1px 2px; }
QListWidget::item:selected, QTreeWidget::item:selected { background-color: #7C3AED; color: white; }
QListWidget::item:hover:!selected, QTreeWidget::item:hover:!selected { background-color: #F0F0F8; }

QCheckBox, QRadioButton { color: #1A1A2E; spacing: 8px; font-size: 12px; }
QCheckBox::indicator { width: 17px; height: 17px; border: 2px solid #C0C0D5; border-radius: 4px; background: white; }
QCheckBox::indicator:checked { background-color: #7C3AED; border-color: #7C3AED; }
QRadioButton::indicator { width: 17px; height: 17px; border: 2px solid #C0C0D5; border-radius: 9px; background: white; }
QRadioButton::indicator:checked { background-color: #7C3AED; border-color: #7C3AED; }

QSlider::groove:horizontal { background: #E0E0EE; height: 5px; border-radius: 2px; }
QSlider::handle:horizontal { background: #7C3AED; width: 18px; height: 18px; margin: -7px 0; border-radius: 9px; }
QSlider::sub-page:horizontal { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7C3AED, stop:1 #4F46E5); border-radius: 2px; }

QSpinBox, QDoubleSpinBox {
    background-color: #FFFFFF; color: #1A1A2E;
    border: 1.5px solid #DDDDE8; border-radius: 8px; padding: 8px 12px;
}
QSpinBox:focus, QDoubleSpinBox:focus { border-color: #7C3AED; }
QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: transparent; border: none; width: 22px;
}

QMenuBar { background-color: #F2F2F7; color: #1A1A2E; border-bottom: 1px solid #DDDDE8; padding: 2px 8px; }
QMenuBar::item { padding: 6px 12px; border-radius: 5px; }
QMenuBar::item:selected { background-color: #E0E0F0; }
QMenu { background-color: #FFFFFF; border: 1px solid #DDDDE8; border-radius: 10px; padding: 6px; }
QMenu::item { padding: 9px 24px; border-radius: 6px; }
QMenu::item:selected { background-color: #7C3AED; color: white; }
QMenu::separator { background-color: #DDDDE8; height: 1px; margin: 4px 10px; }

QStatusBar { background-color: #F2F2F7; color: #6060AA; border-top: 1px solid #DDDDE8; font-size: 11px; }
QToolTip { background-color: #FFFFFF; color: #1A1A2E; border: 1px solid #7C3AED; border-radius: 7px; padding: 7px 12px; }
QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }

QWidget#sidebar { background-color: #EBEBF5; border-right: 1px solid #DDDDE8; }
QWidget#sidebar_header { background-color: #EBEBF5; border-bottom: 1px solid #DDDDE8; }
QFrame#card { background-color: #FFFFFF; border: 1px solid #E0E0EE; border-radius: 14px; }
QFrame#card_elevated { background-color: #FAFAFF; border: 1px solid #E0E0EE; border-radius: 14px; }
QFrame#accent_card { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(124,58,237,0.08), stop:1 rgba(79,70,229,0.04)); border: 1px solid rgba(124,58,237,0.3); border-radius: 14px; }
QFrame#stat_card { background-color: #FFFFFF; border: 1px solid #E0E0EE; border-radius: 14px; }
QWidget#page_header { background-color: #EBEBF5; border-bottom: 1px solid #DDDDE8; }
QWidget#content_area { background-color: #F2F2F7; }
"""


def get_theme(is_dark: bool = True) -> str:
    return DARK if is_dark else LIGHT


def apply_theme(app, is_dark: bool = True):
    app.setStyleSheet(get_theme(is_dark))
