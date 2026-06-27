from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QListWidget, QListWidgetItem,
    QSplitter, QTextEdit, QApplication, QComboBox
)
from PySide6.QtCore import Qt

from app.ui.components.cards import SectionHeader, EmptyState
from app.ui.components.dialogs import ConfirmDialog


class HistoryPage(QWidget):
    def __init__(self, config, db, parent=None):
        super().__init__(parent)
        self.config = config
        self.db = db
        self.setObjectName("content_area")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = SectionHeader(
            "History",
            "Browse all past projects and generated content."
        )
        layout.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Project list with export history
        left = QWidget()
        left.setMinimumWidth(280)
        left.setMaximumWidth(360)
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(20, 16, 8, 20)
        left_lay.setSpacing(8)

        left_lay.addWidget(QLabel("📁 All Projects"))
        self.project_list = QListWidget()
        self.project_list.currentItemChanged.connect(self._on_project_select)
        left_lay.addWidget(self.project_list)

        splitter.addWidget(left)

        # Right: Project detail and export history
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(8, 16, 20, 20)
        right_lay.setSpacing(8)

        self.detail_title = QLabel("Select a project")
        self.detail_title.setObjectName("h2")
        right_lay.addWidget(self.detail_title)

        self.detail_meta = QLabel("")
        self.detail_meta.setObjectName("subtitle")
        right_lay.addWidget(self.detail_meta)

        right_lay.addWidget(QLabel("📤 Export History"))
        self.export_list = QListWidget()
        self.export_list.setMaximumHeight(150)
        right_lay.addWidget(self.export_list)

        right_lay.addWidget(QLabel("📄 Content Summary"))
        self.content_list = QListWidget()
        right_lay.addWidget(self.content_list)

        splitter.addWidget(right)
        splitter.setSizes([320, 680])

        content = QWidget()
        content.setObjectName("content_area")
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.addWidget(splitter)
        layout.addWidget(content, 1)

    def refresh(self):
        self.project_list.clear()
        projects = self.db.get_all_projects(limit=200)
        for p in projects:
            item = QListWidgetItem(
                f"{p.title[:40]}\n"
                f"{p.created_at.strftime('%b %d, %Y')}"
            )
            item.setData(Qt.ItemDataRole.UserRole, p.id)
            self.project_list.addItem(item)

    def _on_project_select(self, current, previous):
        if not current:
            return
        project_id = current.data(Qt.ItemDataRole.UserRole)
        project = self.db.get_project(project_id)
        if not project:
            return

        self.detail_title.setText(project.title[:60])
        self.detail_meta.setText(
            f"📺 {project.channel or 'Unknown'}  •  "
            f"⏱ {project.duration_str}  •  "
            f"🕒 {project.created_at.strftime('%B %d, %Y %H:%M')}"
        )

        # Export history
        self.export_list.clear()
        for exp in project.exports:
            self.export_list.addItem(
                f"{exp.format} — {exp.created_at.strftime('%b %d %H:%M')} "
                f"({(exp.file_size or 0) // 1024}KB)"
            )

        # Content items
        self.content_list.clear()
        for item in project.content_items:
            self.content_list.addItem(
                f"✅ {item.content_type.replace('_', ' ').title()}"
            )
