from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QScrollArea, QFrame, QListWidget,
    QListWidgetItem, QSplitter, QApplication, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from app.ui.components.cards import SectionHeader, EmptyState


class ContentLibraryPage(QWidget):
    open_project = Signal(int)

    def __init__(self, config, db, parent=None):
        super().__init__(parent)
        self.config = config
        self.db = db
        self._current_item = None
        self.setObjectName("content_area")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = SectionHeader(
            "Content Library",
            "Browse all AI-generated content across your projects."
        )
        layout.addWidget(header)

        # Filter bar
        bar = QWidget()
        bar_lay = QHBoxLayout(bar)
        bar_lay.setContentsMargins(24, 12, 24, 12)
        bar_lay.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search content…")
        self.search_input.setFixedHeight(38)
        self.search_input.textChanged.connect(self.refresh)
        bar_lay.addWidget(self.search_input, 1)

        self.type_filter = QComboBox()
        self.type_filter.setFixedHeight(38)
        self.type_filter.addItem("All Types")
        for t in ["executive_summary", "blog_long_form", "twitter_thread",
                  "linkedin_post", "instagram_captions", "tiktok_content",
                  "seo_package", "timestamps", "newsletter"]:
            self.type_filter.addItem(t.replace("_", " ").title(), t)
        self.type_filter.currentIndexChanged.connect(self.refresh)
        bar_lay.addWidget(self.type_filter)

        layout.addWidget(bar)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: item list
        self.item_list = QListWidget()
        self.item_list.setMinimumWidth(280)
        self.item_list.setMaximumWidth(360)
        self.item_list.currentItemChanged.connect(self._on_select)
        splitter.addWidget(self.item_list)

        # Right: content viewer
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(16, 8, 8, 8)
        right_layout.setSpacing(8)

        self.content_title = QLabel("Select an item to view")
        self.content_title.setObjectName("h2")
        right_layout.addWidget(self.content_title)

        meta_row = QHBoxLayout()
        self.content_meta = QLabel("")
        self.content_meta.setObjectName("subtitle")
        meta_row.addWidget(self.content_meta)
        meta_row.addStretch()
        copy_btn = QPushButton("📋 Copy")
        copy_btn.setObjectName("ghost")
        copy_btn.setFixedHeight(30)
        copy_btn.clicked.connect(self._copy_content)
        meta_row.addWidget(copy_btn)
        right_layout.addLayout(meta_row)

        self.content_view = QTextEdit()
        self.content_view.setReadOnly(True)
        self.content_view.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        right_layout.addWidget(self.content_view)

        splitter.addWidget(right)
        splitter.setSizes([300, 700])

        content_widget = QWidget()
        content_widget.setObjectName("content_area")
        c_lay = QVBoxLayout(content_widget)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.addWidget(splitter)

        layout.addWidget(content_widget, 1)

    def refresh(self):
        from app.database.models import GeneratedContent
        self.item_list.clear()
        query = self.search_input.text().strip()
        type_filter = self.type_filter.currentData()

        with self.db.get_session() as session:
            q = session.query(GeneratedContent)
            if type_filter:
                q = q.filter(GeneratedContent.content_type == type_filter)
            items = q.order_by(GeneratedContent.created_at.desc()).limit(500).all()

        for item in items:
            if query and query.lower() not in (item.content or "").lower():
                continue
            label = item.content_type.replace("_", " ").title()
            # Get project title
            project = self.db.get_project(item.project_id)
            proj_title = project.title[:30] if project else "Unknown"
            display = f"{label}\n{proj_title}"
            li = QListWidgetItem(display)
            li.setData(Qt.ItemDataRole.UserRole, item.id)
            li.setData(Qt.ItemDataRole.UserRole + 1, item.content or "")
            li.setData(Qt.ItemDataRole.UserRole + 2, label)
            li.setData(Qt.ItemDataRole.UserRole + 3,
                       item.created_at.strftime("%b %d, %Y") if item.created_at else "")
            self.item_list.addItem(li)

    def _on_select(self, current, previous):
        if not current:
            return
        content = current.data(Qt.ItemDataRole.UserRole + 1)
        title = current.data(Qt.ItemDataRole.UserRole + 2)
        date = current.data(Qt.ItemDataRole.UserRole + 3)
        self.content_title.setText(title)
        self.content_meta.setText(f"Generated: {date}")
        self.content_view.setPlainText(content)

    def _copy_content(self):
        text = self.content_view.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
