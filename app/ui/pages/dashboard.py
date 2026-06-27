from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QGridLayout, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPainter, QColor, QLinearGradient, QBrush, QPen
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

from app.ui.components.cards import StatCard, Card, SectionHeader, EmptyState


class RecentProjectCard(QFrame):
    open_requested = Signal(int)

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setObjectName("card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(100)
        self._setup()

    def _setup(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        # Thumbnail placeholder
        thumb = QLabel("▶️")
        thumb.setFont(QFont("Segoe UI", 24))
        thumb.setFixedSize(60, 60)
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb.setStyleSheet(
            "background: #2A2A40; border-radius: 8px;"
        )
        layout.addWidget(thumb)

        # Info
        info = QVBoxLayout()
        info.setSpacing(3)
        title = QLabel(self.project.title[:60] + ("…" if len(self.project.title) > 60 else ""))
        title.setObjectName("h3")
        info.addWidget(title)

        channel = QLabel(f"📺 {self.project.channel or 'Unknown'}")
        channel.setObjectName("subtitle")
        info.addWidget(channel)

        meta = QLabel(
            f"📄 {self.project.content_count} pieces  •  "
            f"🕒 {self.project.created_at.strftime('%b %d, %Y')}"
        )
        meta.setObjectName("caption")
        info.addWidget(meta)
        layout.addLayout(info, 1)

        # Status badge
        status_colors = {
            "complete": "#10B981", "processing": "#F59E0B",
            "error": "#EF4444", "pending": "#6060AA"
        }
        color = status_colors.get(self.project.status, "#6060AA")
        status = QLabel(self.project.status.title())
        status.setStyleSheet(
            f"color: {color}; background: transparent; "
            f"font-size: 11px; font-weight: 600;"
        )
        layout.addWidget(status, alignment=Qt.AlignmentFlag.AlignTop)

    def mousePressEvent(self, event):
        self.open_requested.emit(self.project.id)
        super().mousePressEvent(event)


class DashboardPage(QWidget):
    navigate_to = Signal(str)
    open_project = Signal(int)

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
        header = SectionHeader(
            "Dashboard",
            "Welcome to AI YouTube Studio — your content creation hub."
        )
        new_btn = QPushButton("✨ New Project")
        new_btn.setObjectName("primary")
        new_btn.setFixedHeight(38)
        new_btn.clicked.connect(lambda: self.navigate_to.emit("new_project"))
        header.add_action(new_btn)
        layout.addWidget(header)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content.setObjectName("content_area")
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(28, 24, 28, 28)
        self.content_layout.setSpacing(24)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        self._build_stats()
        self._build_recent()

    def _build_stats(self):
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)

        self.stat_projects = StatCard("📁", "Total Projects", "0", "#7C3AED")
        self.stat_content = StatCard("📄", "Content Pieces", "0", "#4F46E5")
        self.stat_blogs = StatCard("📝", "Blog Posts", "0", "#10B981")
        self.stat_social = StatCard("📱", "Social Posts", "0", "#F59E0B")
        self.stat_tokens = StatCard("🤖", "Tokens Used", "0", "#EF4444")

        for card in [self.stat_projects, self.stat_content, self.stat_blogs,
                     self.stat_social, self.stat_tokens]:
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            card.setFixedHeight(160)
            stats_row.addWidget(card)

        stats_widget = QWidget()
        stats_widget.setLayout(stats_row)
        self.content_layout.addWidget(stats_widget)

    def _build_recent(self):
        self.recent_header = QLabel("Recent Projects")
        self.recent_header.setObjectName("h2")
        self.content_layout.addWidget(self.recent_header)

        self.recent_container = QVBoxLayout()
        self.recent_container.setSpacing(10)
        self.content_layout.addLayout(self.recent_container)

        # Quick actions
        actions_label = QLabel("Quick Actions")
        actions_label.setObjectName("h2")
        self.content_layout.addWidget(actions_label)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(12)

        action_items = [
            ("✨", "New Project", "new_project", "#7C3AED"),
            ("🤖", "AI Settings", "ai_settings", "#4F46E5"),
            ("📤", "Export Center", "export", "#10B981"),
            ("🗂️", "Templates", "templates", "#F59E0B"),
        ]
        for icon, label, key, color in action_items:
            btn_card = QFrame()
            btn_card.setObjectName("card")
            btn_card.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_card.setFixedHeight(90)
            btn_layout = QVBoxLayout(btn_card)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ico = QLabel(icon)
            ico.setFont(QFont("Segoe UI", 22))
            ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color: {color}; font-weight: 600;")
            btn_layout.addWidget(ico)
            btn_layout.addWidget(lbl)

            k = key  # capture for lambda
            btn_card.mousePressEvent = (
                lambda e, k=k: self.navigate_to.emit(k)
            )
            actions_row.addWidget(btn_card)

        actions_widget = QWidget()
        actions_widget.setLayout(actions_row)
        self.content_layout.addWidget(actions_widget)
        self.content_layout.addStretch()

    def refresh(self):
        stats = self.db.get_dashboard_stats()
        self.stat_projects.set_value(str(stats["project_count"]))
        self.stat_content.set_value(str(stats["content_count"]))
        self.stat_blogs.set_value(str(stats["blog_count"]))
        self.stat_social.set_value(str(stats["social_count"]))
        self.stat_tokens.set_value(f"{stats['total_tokens']:,}")

        # Clear and rebuild recent projects
        while self.recent_container.count():
            item = self.recent_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        projects = self.db.get_recent_projects(6)
        if not projects:
            empty = EmptyState(
                "📁", "No Projects Yet",
                "Create your first project by pasting a YouTube URL.",
                "✨ New Project"
            )
            empty.action_clicked.connect(lambda: self.navigate_to.emit("new_project"))
            empty.setFixedHeight(180)
            self.recent_container.addWidget(empty)
        else:
            for project in projects:
                card = RecentProjectCard(project)
                card.open_requested.connect(self.open_project.emit)
                self.recent_container.addWidget(card)
