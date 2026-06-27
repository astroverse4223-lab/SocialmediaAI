from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QScrollArea, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QFont


NAV_ITEMS = [
    ("dashboard",    "🏠", "Dashboard"),
    ("new_project",  "✨", "New Project"),
    ("projects",     "📁", "Projects"),
    ("content",      "📚", "Content Library"),
    ("media",        "🎨", "AI Media Generator"),
    ("thumbnail",    "🖼️", "Thumbnail Generator"),
    ("blog",         "📝", "Blog Generator"),
    ("social",       "📱", "Social Media"),
    ("seo",          "🔍", "SEO Tools"),
    ("templates",    "🗂️", "Templates"),
    ("history",      "🕐", "History"),
    ("export",       "📤", "Export Center"),
]

NAV_SETTINGS = [
    ("ai_settings",  "🤖", "AI Settings"),
    ("preferences",  "⚙️", "Preferences"),
]


class SidebarNavButton(QPushButton):
    def __init__(self, icon: str, label: str, key: str, parent=None):
        super().__init__(parent)
        self.key = key
        self._icon = icon
        self._label = label
        self._active = False
        self._setup()

    def _setup(self):
        self.setObjectName("sidebar_btn")
        self.setCheckable(False)
        self.setFixedHeight(44)
        self.setText(f"  {self._icon}  {self._label}")
        self.setToolTip(self._label)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_active(self, active: bool):
        if self._active == active:
            return
        self._active = active
        self.setObjectName("sidebar_btn_active" if active else "sidebar_btn")
        self.style().unpolish(self)
        self.style().polish(self)

    @property
    def is_active(self) -> bool:
        return self._active


class Sidebar(QWidget):
    page_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(230)
        self._buttons: dict[str, SidebarNavButton] = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Logo / Header ─────────────────────────────────
        header = QWidget()
        header.setObjectName("sidebar_header")
        header.setFixedHeight(68)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(18, 0, 18, 0)

        logo_lbl = QLabel("🎬")
        logo_lbl.setFont(QFont("Segoe UI", 22))

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        app_name = QLabel("AI YouTube")
        app_name.setObjectName("h3")
        app_sub = QLabel("Studio")
        app_sub.setObjectName("accent")
        title_col.addWidget(app_name)
        title_col.addWidget(app_sub)

        h_lay.addWidget(logo_lbl)
        h_lay.addSpacing(8)
        h_lay.addLayout(title_col)
        h_lay.addStretch()
        layout.addWidget(header)

        # ── Scroll area for nav ───────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(8, 12, 8, 12)
        nav_layout.setSpacing(2)

        # Section: Navigation
        section_label = QLabel("NAVIGATION")
        section_label.setObjectName("caption")
        section_label.setContentsMargins(12, 8, 0, 4)
        nav_layout.addWidget(section_label)

        for key, icon, label in NAV_ITEMS:
            btn = SidebarNavButton(icon, label, key)
            btn.clicked.connect(lambda checked, k=key: self._on_nav(k))
            self._buttons[key] = btn
            nav_layout.addWidget(btn)

        nav_layout.addSpacing(16)

        # Section: Settings
        settings_label = QLabel("SETTINGS")
        settings_label.setObjectName("caption")
        settings_label.setContentsMargins(12, 8, 0, 4)
        nav_layout.addWidget(settings_label)

        for key, icon, label in NAV_SETTINGS:
            btn = SidebarNavButton(icon, label, key)
            btn.clicked.connect(lambda checked, k=key: self._on_nav(k))
            self._buttons[key] = btn
            nav_layout.addWidget(btn)

        nav_layout.addStretch()
        scroll.setWidget(nav_widget)
        layout.addWidget(scroll, 1)

        # ── Footer ────────────────────────────────────────
        footer = QWidget()
        footer.setFixedHeight(48)
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(14, 0, 14, 0)
        ver = QLabel("v1.0.0")
        ver.setObjectName("caption")
        f_lay.addWidget(ver)
        f_lay.addStretch()
        layout.addWidget(footer)

    def _on_nav(self, key: str):
        self.set_active(key)
        self.page_requested.emit(key)

    def set_active(self, key: str):
        for k, btn in self._buttons.items():
            btn.set_active(k == key)

    def get_active_key(self) -> str:
        for k, btn in self._buttons.items():
            if btn.is_active:
                return k
        return ""
