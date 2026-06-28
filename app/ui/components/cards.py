"""Reusable card and widget components."""
from PySide6.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QSizePolicy, QScrollArea,
    QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QClipboard


class Card(QFrame):
    """Basic card container."""
    def __init__(self, parent=None, elevated: bool = False):
        super().__init__(parent)
        self.setObjectName("card_elevated" if elevated else "card")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 16, 20, 16)
        self._layout.setSpacing(10)

    @property
    def layout(self):
        return self._layout


class StatCard(QFrame):
    """Dashboard statistics card."""
    clicked = Signal()

    def __init__(self, icon: str, label: str, value: str = "0",
                 color: str = "#7C3AED", parent=None):
        super().__init__(parent)
        self.setObjectName("stat_card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._color = color
        self._setup(icon, label, value)

    def _setup(self, icon, label, value):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        # Icon row
        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI", 26))
        layout.addWidget(icon_lbl)

        # Value
        self.value_lbl = QLabel(value)
        self.value_lbl.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self.value_lbl.setStyleSheet(f"color: {self._color};")
        layout.addWidget(self.value_lbl)

        # Label
        label_lbl = QLabel(label)
        label_lbl.setObjectName("subtitle")
        layout.addWidget(label_lbl)

    def set_value(self, value: str):
        self.value_lbl.setText(value)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class ContentCard(QFrame):
    """Card for displaying a single piece of generated content."""
    regenerate_requested = Signal(str)   # content_key
    copy_requested = Signal(str)         # content_key

    def __init__(self, title: str, key: str, icon: str = "📄",
                 parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.title = title
        self.key = key
        self._setup(icon, title)

    def _setup(self, icon, title):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # Header row
        header = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI", 16))
        title_lbl = QLabel(title)
        title_lbl.setObjectName("h3")
        header.addWidget(icon_lbl)
        header.addWidget(title_lbl)
        header.addStretch()

        self.status_lbl = QLabel("Not generated")
        self.status_lbl.setObjectName("caption")
        header.addWidget(self.status_lbl)

        copy_btn = QPushButton("📋 Copy")
        copy_btn.setObjectName("ghost")
        copy_btn.setFixedHeight(30)
        copy_btn.clicked.connect(self._on_copy)
        header.addWidget(copy_btn)

        regen_btn = QPushButton("🔄")
        regen_btn.setObjectName("ghost")
        regen_btn.setFixedSize(30, 30)
        regen_btn.setToolTip(f"Regenerate {title}")
        regen_btn.clicked.connect(lambda: self.regenerate_requested.emit(self.key))
        header.addWidget(regen_btn)

        layout.addLayout(header)

        # Text area — fully editable so Ctrl+C/V/A work natively
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(
            f"Click 'Generate All' or the regenerate button to generate {title}."
        )
        self.text_edit.setMinimumHeight(180)
        self.text_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.text_edit)

        # Token info
        self.token_lbl = QLabel("")
        self.token_lbl.setObjectName("caption")
        layout.addWidget(self.token_lbl)

    def set_content(self, text: str, tokens: int = 0):
        self.text_edit.setPlainText(text)
        if tokens:
            self.token_lbl.setText(f"Tokens used: {tokens:,}")
        self.status_lbl.setText("✅ Generated")

    def set_loading(self):
        self.text_edit.setPlainText("")
        self.text_edit.setPlaceholderText("⏳ Generating…")
        self.status_lbl.setText("⏳ Generating…")

    def set_error(self, msg: str):
        self.text_edit.setPlainText(f"❌ Error: {msg}")
        self.status_lbl.setText("❌ Error")

    def get_content(self) -> str:
        return self.text_edit.toPlainText()

    def _on_copy(self):
        text = self.text_edit.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
        self.copy_requested.emit(self.key)


class SectionHeader(QWidget):
    """Page header with title and optional action buttons."""
    def __init__(self, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("page_header")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(16)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        title_lbl = QLabel(title)
        title_lbl.setObjectName("h2")
        text_col.addWidget(title_lbl)
        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setObjectName("subtitle")
            text_col.addWidget(sub_lbl)
        layout.addLayout(text_col)
        layout.addStretch()

        self._actions = QHBoxLayout()
        self._actions.setSpacing(8)
        layout.addLayout(self._actions)

    def add_action(self, btn: QPushButton):
        self._actions.addWidget(btn)


class InfoRow(QWidget):
    """Key-value info row."""
    def __init__(self, key: str, value: str = "", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(8)
        key_lbl = QLabel(f"{key}:")
        key_lbl.setObjectName("subtitle")
        key_lbl.setFixedWidth(120)
        self.value_lbl = QLabel(value)
        self.value_lbl.setWordWrap(True)
        layout.addWidget(key_lbl)
        layout.addWidget(self.value_lbl, 1)

    def set_value(self, value: str):
        self.value_lbl.setText(value)


class EmptyState(QWidget):
    """Empty state placeholder widget."""
    action_clicked = Signal()

    def __init__(self, icon: str, title: str, message: str,
                 action_label: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI", 48))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("h2")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)

        msg_lbl = QLabel(message)
        msg_lbl.setObjectName("subtitle")
        msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_lbl.setWordWrap(True)
        msg_lbl.setMaximumWidth(420)
        layout.addWidget(msg_lbl)

        if action_label:
            btn = QPushButton(action_label)
            btn.setObjectName("primary")
            btn.setFixedWidth(200)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(self.action_clicked.emit)
            layout.addSpacing(8)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
