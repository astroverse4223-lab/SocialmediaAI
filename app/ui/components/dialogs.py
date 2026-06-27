"""Reusable dialog windows."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QWidget, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class ConfirmDialog(QDialog):
    def __init__(self, title: str, message: str,
                 confirm_text: str = "Confirm",
                 danger: bool = False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(420, 200)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self._setup(title, message, confirm_text, danger)

    def _setup(self, title, message, confirm_text, danger):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("h3")
        layout.addWidget(title_lbl)

        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setObjectName("subtitle")
        layout.addWidget(msg_lbl)

        layout.addStretch()

        btns = QHBoxLayout()
        btns.setSpacing(8)

        cancel = QPushButton("Cancel")
        cancel.setObjectName("ghost")
        cancel.clicked.connect(self.reject)
        btns.addWidget(cancel)

        btns.addStretch()

        confirm = QPushButton(confirm_text)
        confirm.setObjectName("danger" if danger else "primary")
        confirm.clicked.connect(self.accept)
        btns.addWidget(confirm)

        layout.addLayout(btns)


class ContentViewDialog(QDialog):
    """Full-screen view of a content piece."""
    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 620)
        self._setup(title, content)

    def _setup(self, title, content):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setObjectName("h2")
        header.addWidget(title_lbl)
        header.addStretch()

        copy_btn = QPushButton("📋 Copy All")
        copy_btn.setObjectName("ghost")
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(
            self.text_edit.toPlainText()
        ))
        header.addWidget(copy_btn)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("ghost")
        close_btn.setFixedSize(32, 32)
        close_btn.clicked.connect(self.accept)
        header.addWidget(close_btn)

        layout.addLayout(header)

        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(content)
        self.text_edit.setReadOnly(False)
        layout.addWidget(self.text_edit)

        save_btn = QPushButton("Save Changes")
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self.accept)
        layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def get_content(self) -> str:
        return self.text_edit.toPlainText()


class NotificationBanner(QWidget):
    """Inline notification banner."""
    def __init__(self, message: str, kind: str = "info", parent=None):
        super().__init__(parent)
        colors = {
            "info":    ("#1E1E3E", "#4F46E5"),
            "success": ("#0D2A1E", "#10B981"),
            "warning": ("#2A1E0A", "#F59E0B"),
            "error":   ("#2A0E0E", "#EF4444"),
        }
        bg, accent = colors.get(kind, colors["info"])
        self.setStyleSheet(
            f"background-color: {bg}; border-left: 3px solid {accent}; "
            f"border-radius: 8px; padding: 8px 14px;"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
        icon_lbl = QLabel(icons.get(kind, "ℹ️"))
        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        close = QPushButton("✕")
        close.setObjectName("ghost")
        close.setFixedSize(24, 24)
        close.clicked.connect(self.hide)
        layout.addWidget(icon_lbl)
        layout.addWidget(msg_lbl, 1)
        layout.addWidget(close)
