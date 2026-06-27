from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QStatusBar, QLabel, QApplication,
    QMenuBar, QMenu, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QAction, QKeySequence

from app.ui.components.sidebar import Sidebar
from app.styles.themes import get_theme


class MainWindow(QMainWindow):
    def __init__(self, config, db):
        super().__init__()
        self.config = config
        self.db = db
        self._is_dark = config.get("theme", "dark") == "dark"
        self._setup_window()
        self._setup_ui()
        self._apply_theme()
        self._setup_menu()
        self._setup_shortcuts()
        self._setup_autosave()
        # Navigate to dashboard on start
        self._navigate("dashboard")

    # ──────────────────── WINDOW SETUP ────────────────────

    def _setup_window(self):
        self.setWindowTitle("AI YouTube Studio")
        w = self.config.get("window_width", 1400)
        h = self.config.get("window_height", 900)
        self.resize(w, h)
        self.setMinimumSize(1050, 680)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.page_requested.connect(self._navigate)
        root.addWidget(self.sidebar)

        # Page stack
        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        # Instantiate all pages
        self._pages: dict = {}
        self._init_pages()

        # Status bar
        self._setup_status_bar()

    def _init_pages(self):
        from app.ui.pages.dashboard import DashboardPage
        from app.ui.pages.new_project import NewProjectPage
        from app.ui.pages.projects import ProjectsPage
        from app.ui.pages.content_library import ContentLibraryPage
        from app.ui.pages.blog_generator import BlogGeneratorPage
        from app.ui.pages.social_media import SocialMediaPage
        from app.ui.pages.thumbnail_generator import ThumbnailGeneratorPage
        from app.ui.pages.media_generator import MediaGeneratorPage
        from app.ui.pages.seo_tools import SEOToolsPage
        from app.ui.pages.templates import TemplatesPage
        from app.ui.pages.history import HistoryPage
        from app.ui.pages.export_center import ExportCenterPage
        from app.ui.pages.ai_settings import AISettingsPage
        from app.ui.pages.preferences import PreferencesPage

        # dashboard
        dash = DashboardPage(self.config, self.db)
        dash.navigate_to.connect(self._navigate)
        dash.open_project.connect(self._open_project_in_editor)
        self._add_page("dashboard", dash)

        # new_project
        new_proj = NewProjectPage(self.config, self.db)
        new_proj.project_saved.connect(self._on_project_saved)
        self._add_page("new_project", new_proj)

        # projects
        projects = ProjectsPage(self.config, self.db)
        projects.open_project.connect(self._open_project_in_editor)
        projects.new_project_requested.connect(lambda: self._navigate("new_project"))
        self._add_page("projects", projects)

        # content library
        self._add_page("content", ContentLibraryPage(self.config, self.db))

        # media generator (images + videos)
        self._add_page("media", MediaGeneratorPage(self.config, self.db))

        # thumbnail
        self._add_page("thumbnail", ThumbnailGeneratorPage(self.config, self.db))

        # blog
        self._add_page("blog", BlogGeneratorPage(self.config, self.db))

        # social
        self._add_page("social", SocialMediaPage(self.config, self.db))

        # seo
        self._add_page("seo", SEOToolsPage(self.config, self.db))

        # templates
        self._add_page("templates", TemplatesPage(self.config, self.db))

        # history
        self._add_page("history", HistoryPage(self.config, self.db))

        # export
        self._add_page("export", ExportCenterPage(self.config, self.db))

        # ai settings
        ai_settings = AISettingsPage(self.config, self.db)
        ai_settings.settings_changed.connect(self._on_settings_changed)
        self._add_page("ai_settings", ai_settings)

        # preferences
        prefs = PreferencesPage(self.config, self.db)
        prefs.theme_changed.connect(self._on_theme_changed)
        self._add_page("preferences", prefs)

    def _add_page(self, key: str, page: QWidget):
        self._pages[key] = page
        self.stack.addWidget(page)

    def _setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_lbl = QLabel("Ready")
        self.status_bar.addWidget(self.status_lbl, 1)

        self.provider_lbl = QLabel("")
        self.status_bar.addPermanentWidget(self.provider_lbl)
        self._update_status_provider()

        ver_lbl = QLabel("AI YouTube Studio v1.0.0")
        ver_lbl.setStyleSheet("color: #606090; padding: 0 8px;")
        self.status_bar.addPermanentWidget(ver_lbl)

    def _update_status_provider(self):
        provider = self.config.get("ai_provider", "openai")
        model = self.config.get("ai_model", "")
        indicator = "🟢" if self.config.is_ai_configured() else "🔴"
        self.provider_lbl.setText(
            f"{indicator} {provider.title()} · {model}"
        )

    # ──────────────────── NAVIGATION ──────────────────────

    def _navigate(self, key: str):
        if key not in self._pages:
            return
        page = self._pages[key]
        self.stack.setCurrentWidget(page)
        self.sidebar.set_active(key)

        # Refresh pages that need live data
        if hasattr(page, "refresh"):
            page.refresh()

        self.status_lbl.setText(f"📍 {key.replace('_', ' ').title()}")

    def _open_project_in_editor(self, project_id: int):
        """Open an existing project in the new_project editor."""
        self._navigate("new_project")
        page = self._pages.get("new_project")
        if page and hasattr(page, "load_project"):
            page.load_project(project_id)

    def _on_project_saved(self, project_id: int):
        self.status_lbl.setText(f"✅ Project #{project_id} saved")

    def _on_settings_changed(self):
        self._update_status_provider()
        # Also refresh new_project panel provider display
        new_proj = self._pages.get("new_project")
        if new_proj and hasattr(new_proj, "gen_panel"):
            new_proj.gen_panel.refresh_provider()

    def _on_theme_changed(self, is_dark: bool):
        self._is_dark = is_dark
        self._apply_theme()

    # ──────────────────── THEME ───────────────────────────

    def _apply_theme(self):
        QApplication.instance().setStyleSheet(get_theme(self._is_dark))

    # ──────────────────── MENU ────────────────────────────

    def _setup_menu(self):
        mb = self.menuBar()

        # File
        file_menu = mb.addMenu("File")
        new_act = QAction("New Project", self)
        new_act.setShortcut(QKeySequence.StandardKey.New)
        new_act.triggered.connect(lambda: self._navigate("new_project"))
        file_menu.addAction(new_act)

        file_menu.addSeparator()
        export_act = QAction("Export Center", self)
        export_act.triggered.connect(lambda: self._navigate("export"))
        file_menu.addAction(export_act)

        file_menu.addSeparator()
        quit_act = QAction("Quit", self)
        quit_act.setShortcut(QKeySequence.StandardKey.Quit)
        quit_act.triggered.connect(QApplication.quit)
        file_menu.addAction(quit_act)

        # View
        view_menu = mb.addMenu("View")
        dash_act = QAction("Dashboard", self)
        dash_act.triggered.connect(lambda: self._navigate("dashboard"))
        view_menu.addAction(dash_act)

        proj_act = QAction("Projects", self)
        proj_act.triggered.connect(lambda: self._navigate("projects"))
        view_menu.addAction(proj_act)

        view_menu.addSeparator()
        theme_act = QAction("Toggle Dark/Light Mode", self)
        theme_act.triggered.connect(self._toggle_theme)
        view_menu.addAction(theme_act)

        # AI
        ai_menu = mb.addMenu("AI")
        settings_act = QAction("AI Settings", self)
        settings_act.triggered.connect(lambda: self._navigate("ai_settings"))
        ai_menu.addAction(settings_act)

        templates_act = QAction("Templates", self)
        templates_act.triggered.connect(lambda: self._navigate("templates"))
        ai_menu.addAction(templates_act)

        # Help
        help_menu = mb.addMenu("Help")
        about_act = QAction("About", self)
        about_act.triggered.connect(self._show_about)
        help_menu.addAction(about_act)

    def _toggle_theme(self):
        self._is_dark = not self._is_dark
        self.config.set("theme", "dark" if self._is_dark else "light")
        self._apply_theme()

    def _show_about(self):
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("About AI YouTube Studio")
        msg.setText(
            "<b>AI YouTube Studio v1.0.0</b><br><br>"
            "Transform YouTube videos into comprehensive content suites using AI.<br><br>"
            "Supports: OpenAI · Anthropic Claude · Google Gemini · Ollama<br><br>"
            "Built with Python & PySide6"
        )
        msg.exec()

    # ──────────────────── SHORTCUTS ───────────────────────

    def _setup_shortcuts(self):
        from PySide6.QtGui import QShortcut

        shortcuts = [
            ("Ctrl+N", "new_project"),
            ("Ctrl+P", "projects"),
            ("Ctrl+D", "dashboard"),
            ("Ctrl+E", "export"),
            ("Ctrl+,", "preferences"),
        ]
        for key_seq, page in shortcuts:
            sc = QShortcut(QKeySequence(key_seq), self)
            sc.activated.connect(lambda p=page: self._navigate(p))

    # ──────────────────── AUTO-SAVE ───────────────────────

    def _setup_autosave(self):
        interval = self.config.get("auto_save_interval", 30) * 1000
        self._autosave_timer = QTimer(self)
        self._autosave_timer.timeout.connect(self._autosave)
        if self.config.get("auto_save", True):
            self._autosave_timer.start(interval)

    def _autosave(self):
        self.config.save()

    # ──────────────────── CLOSE ───────────────────────────

    def closeEvent(self, event):
        self.config.set("window_width", self.width())
        self.config.set("window_height", self.height())
        self.config.save()

        # Stop all timers first so nothing fires during teardown
        if hasattr(self, "_autosave_timer"):
            self._autosave_timer.stop()
        for key, page in self._pages.items():
            # Stop video poll timer in media generator
            if hasattr(page, "video_tab") and hasattr(page.video_tab, "_poll_timer"):
                page.video_tab._poll_timer.stop()
            # Stop any export/thumbnail timers
            for attr in ("_timer", "_poll_timer", "_refresh_timer"):
                timer = getattr(page, attr, None)
                if timer and hasattr(timer, "stop"):
                    timer.stop()

        # Stop any running workers
        for key, page in self._pages.items():
            if hasattr(page, "_batch_worker") and page._batch_worker:
                if page._batch_worker.isRunning():
                    page._batch_worker.cancel()
                    page._batch_worker.wait(2000)
            if hasattr(page, "_yt_worker") and page._yt_worker:
                if page._yt_worker.isRunning():
                    page._yt_worker.cancel()
                    page._yt_worker.wait(2000)
            if hasattr(page, "_worker") and page._worker:
                if page._worker.isRunning():
                    page._worker.requestInterruption()
                    page._worker.wait(1000)

        super().closeEvent(event)
