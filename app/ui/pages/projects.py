from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QFrame, QGridLayout, QSizePolicy,
    QMenu, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QCursor

from app.ui.components.cards import SectionHeader, EmptyState
from app.ui.components.dialogs import ConfirmDialog


class ProjectCard(QFrame):
    open_requested = Signal(int)
    delete_requested = Signal(int)
    favorite_toggled = Signal(int)

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setObjectName("card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(130)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._setup()

    def _setup(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)

        # Thumbnail
        thumb = QLabel("▶️")
        thumb.setFont(QFont("Segoe UI", 28))
        thumb.setFixedSize(80, 80)
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb.setStyleSheet("background: #1E1E2E; border-radius: 10px;")
        layout.addWidget(thumb)

        # Info
        info = QVBoxLayout()
        info.setSpacing(4)

        title = QLabel(
            self.project.title[:70] + ("…" if len(self.project.title) > 70 else "")
        )
        title.setObjectName("h3")
        title.setWordWrap(False)
        info.addWidget(title)

        channel = QLabel(f"📺 {self.project.channel or 'Unknown Channel'}")
        channel.setObjectName("subtitle")
        info.addWidget(channel)

        meta_text = (
            f"📄 {self.project.content_count} items  •  "
            f"⏱ {self.project.duration_str}  •  "
            f"🕒 {self.project.created_at.strftime('%b %d, %Y')}"
        )
        meta = QLabel(meta_text)
        meta.setObjectName("caption")
        info.addWidget(meta)

        tags_text = self.project.tags or ""
        if tags_text:
            tags_lbl = QLabel(tags_text[:80])
            tags_lbl.setObjectName("caption")
            tags_lbl.setStyleSheet("color: #7070C0;")
            info.addWidget(tags_lbl)

        layout.addLayout(info, 1)

        # Right side
        right = QVBoxLayout()
        right.setSpacing(6)
        right.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        # Status
        status_map = {
            "complete": ("✅", "#10B981"),
            "processing": ("⏳", "#F59E0B"),
            "error": ("❌", "#EF4444"),
            "pending": ("🕐", "#8080A0"),
        }
        icon, color = status_map.get(self.project.status, ("🕐", "#8080A0"))
        status_lbl = QLabel(f"{icon} {self.project.status.title()}")
        status_lbl.setStyleSheet(f"color: {color}; font-weight: 600; font-size: 11px;")
        right.addWidget(status_lbl)

        # Favorite
        fav = "⭐" if self.project.is_favorite else "☆"
        fav_btn = QPushButton(fav)
        fav_btn.setObjectName("icon_btn")
        fav_btn.setFixedSize(30, 30)
        fav_btn.clicked.connect(lambda: self.favorite_toggled.emit(self.project.id))
        right.addWidget(fav_btn)

        # More button
        more_btn = QPushButton("⋯")
        more_btn.setObjectName("icon_btn")
        more_btn.setFixedSize(30, 30)
        more_btn.clicked.connect(self._show_context_menu)
        right.addWidget(more_btn)

        layout.addLayout(right)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_requested.emit(self.project.id)
        super().mousePressEvent(event)

    def _show_context_menu(self):
        menu = QMenu(self)
        open_act = menu.addAction("📂 Open Project")
        fav_act = menu.addAction("⭐ Toggle Favorite")
        menu.addSeparator()
        del_act = menu.addAction("🗑 Delete Project")

        action = menu.exec(QCursor.pos())
        if action == open_act:
            self.open_requested.emit(self.project.id)
        elif action == fav_act:
            self.favorite_toggled.emit(self.project.id)
        elif action == del_act:
            self.delete_requested.emit(self.project.id)


class ProjectsPage(QWidget):
    open_project = Signal(int)
    new_project_requested = Signal()

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

        # Header
        header = SectionHeader("Projects", "All your AI-generated content projects.")
        new_btn = QPushButton("✨ New Project")
        new_btn.setObjectName("primary")
        new_btn.setFixedHeight(38)
        new_btn.clicked.connect(self.new_project_requested.emit)
        header.add_action(new_btn)
        layout.addWidget(header)

        # Search / filter bar
        bar = QWidget()
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(24, 12, 24, 12)
        bar_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search projects…")
        self.search_input.setFixedHeight(38)
        self.search_input.textChanged.connect(self._filter)
        bar_layout.addWidget(self.search_input, 1)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setFixedHeight(38)
        refresh_btn.clicked.connect(self.refresh)
        bar_layout.addWidget(refresh_btn)

        layout.addWidget(bar)

        # Project list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.list_widget = QWidget()
        self.list_widget.setObjectName("content_area")
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(24, 4, 24, 24)
        self.list_layout.setSpacing(10)
        self.list_layout.addStretch()

        scroll.setWidget(self.list_widget)
        layout.addWidget(scroll, 1)

    def refresh(self):
        self._filter(self.search_input.text())

    def _filter(self, query: str = ""):
        # Clear existing
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        projects = self.db.get_all_projects(limit=200, search=query)

        if not projects:
            empty = EmptyState(
                "📁", "No Projects Found",
                "No projects match your search." if query else
                "Create your first project to get started.",
                "" if query else "✨ New Project"
            )
            empty.action_clicked.connect(self.new_project_requested.emit)
            empty.setFixedHeight(280)
            self.list_layout.insertWidget(0, empty)
        else:
            for i, project in enumerate(projects):
                card = ProjectCard(project)
                card.open_requested.connect(self.open_project.emit)
                card.delete_requested.connect(self._delete_project)
                card.favorite_toggled.connect(self._toggle_favorite)
                self.list_layout.insertWidget(i, card)

    def _delete_project(self, project_id: int):
        dlg = ConfirmDialog(
            "Delete Project",
            "Are you sure you want to delete this project? "
            "All generated content will be permanently removed.",
            confirm_text="Delete",
            danger=True,
            parent=self,
        )
        if dlg.exec():
            self.db.delete_project(project_id)
            self.refresh()

    def _toggle_favorite(self, project_id: int):
        self.db.toggle_favorite(project_id)
        self.refresh()
