from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QComboBox, QScrollArea, QFrame, QTabWidget, QApplication
)
from PySide6.QtCore import Qt, Signal

from app.ui.components.cards import SectionHeader, Card
from app.core.worker import GenerationWorker
from app.core.ai_providers import create_provider
import app.core.content_generator as cg


class SocialMediaPage(QWidget):
    def __init__(self, config, db, parent=None):
        super().__init__(parent)
        self.config = config
        self.db = db
        self._workers = {}
        self.setObjectName("content_area")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = SectionHeader(
            "Social Media Generator",
            "Create platform-optimized posts for every channel."
        )
        layout.addWidget(header)

        # Controls bar
        bar = QWidget()
        bar_lay = QHBoxLayout(bar)
        bar_lay.setContentsMargins(24, 14, 24, 14)
        bar_lay.setSpacing(12)

        bar_lay.addWidget(QLabel("Project:"))
        self.project_combo = QComboBox()
        self.project_combo.setFixedHeight(38)
        self.project_combo.setMinimumWidth(250)
        bar_lay.addWidget(self.project_combo)

        gen_all_btn = QPushButton("⚡ Generate All Platforms")
        gen_all_btn.setObjectName("primary")
        gen_all_btn.setFixedHeight(38)
        gen_all_btn.clicked.connect(self._generate_all)
        bar_lay.addWidget(gen_all_btn)

        bar_lay.addStretch()
        layout.addWidget(bar)

        # Platform tabs
        self.tabs = QTabWidget()

        self._platform_areas = {}
        platforms = [
            ("🐦 Twitter/X",       "twitter_thread",     cg.gen_twitter_thread,     []),
            ("💼 LinkedIn",         "linkedin_post",      cg.gen_linkedin_post,      []),
            ("👍 Facebook",         "facebook_post",      cg.gen_facebook_post,      []),
            ("📸 Instagram",        "instagram_captions", cg.gen_instagram_captions, []),
            ("🎵 TikTok",           "tiktok_content",     cg.gen_tiktok_content,     []),
            ("🧵 Threads",          "threads_post",       cg.gen_threads_post,       []),
            ("▶️ YT Community",     "youtube_community",  cg.gen_youtube_community,  []),
        ]

        for tab_label, key, func, extra in platforms:
            tab = QWidget()
            tab_lay = QVBoxLayout(tab)
            tab_lay.setContentsMargins(16, 12, 16, 12)
            tab_lay.setSpacing(8)

            # Header row
            h_row = QHBoxLayout()
            h_row.addStretch()
            gen_btn = QPushButton(f"⚡ Generate {tab_label.split(' ', 1)[-1].strip()}")
            gen_btn.setObjectName("primary")
            gen_btn.setFixedHeight(36)
            gen_btn.clicked.connect(
                lambda _, k=key, f=func, ex=extra: self._generate_one(k, f, ex)
            )
            h_row.addWidget(gen_btn)
            copy_btn = QPushButton("📋 Copy")
            copy_btn.setObjectName("ghost")
            copy_btn.setFixedHeight(36)
            copy_btn.clicked.connect(
                lambda _, k=key: self._copy(k)
            )
            h_row.addWidget(copy_btn)
            tab_lay.addLayout(h_row)

            text_edit = QTextEdit()
            text_edit.setReadOnly(False)
            text_edit.setPlaceholderText(
                f"Click 'Generate {tab_label.split()[-1]}' to create platform-optimized content."
            )
            tab_lay.addWidget(text_edit)

            char_lbl = QLabel("")
            char_lbl.setObjectName("caption")
            tab_lay.addWidget(char_lbl)
            text_edit.textChanged.connect(
                lambda t=text_edit, l=char_lbl: l.setText(
                    f"{len(t.toPlainText()):,} characters"
                )
            )

            self._platform_areas[key] = text_edit
            self.tabs.addTab(tab, tab_label)

        content = QWidget()
        content.setObjectName("content_area")
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(24, 0, 24, 24)
        c_lay.addWidget(self.tabs)
        layout.addWidget(content, 1)

    def refresh(self):
        self.project_combo.clear()
        for p in self.db.get_all_projects(limit=100):
            self.project_combo.addItem(p.title[:50], p.id)

    def _get_context(self):
        project_id = self.project_combo.currentData()
        if not project_id:
            return None, None, None
        transcript = self.db.get_transcript(project_id)
        if not transcript or not transcript.content:
            return None, None, None
        project = self.db.get_project(project_id)
        return project_id, transcript.content, project.title if project else ""

    def _generate_one(self, key: str, func, extra_args: list):
        project_id, transcript, title = self._get_context()
        if not transcript:
            return
        provider = create_provider(self.config)
        kwargs = {"transcript": transcript, "provider": provider}
        if "title" in extra_args:
            kwargs["title"] = title

        area = self._platform_areas.get(key)
        if area:
            area.setPlainText("⏳ Generating…")

        if key in self._workers and self._workers[key].isRunning():
            self._workers[key].cancel()

        worker = GenerationWorker(key, func, kwargs)
        worker.result.connect(lambda k, c, pt, ct: self._on_done(k, c, pt, ct, project_id))
        worker.error.connect(lambda k, m: self._on_error(k, m))
        self._workers[key] = worker
        worker.start()

    def _generate_all(self):
        platforms = [
            ("twitter_thread",    cg.gen_twitter_thread,    []),
            ("linkedin_post",     cg.gen_linkedin_post,     []),
            ("facebook_post",     cg.gen_facebook_post,     []),
            ("instagram_captions",cg.gen_instagram_captions,[]),
            ("tiktok_content",    cg.gen_tiktok_content,    []),
        ]
        for key, func, extra in platforms:
            self._generate_one(key, func, extra)

    def _on_done(self, key, content, pt, ct, project_id):
        area = self._platform_areas.get(key)
        if area:
            area.setPlainText(content)
        if project_id:
            self.db.save_content(
                project_id=project_id, content_type=key, content=content,
                ai_provider=self.config.get("ai_provider", ""),
                tokens_used=pt + ct, prompt_tokens=pt
            )

    def _on_error(self, key, msg):
        area = self._platform_areas.get(key)
        if area:
            area.setPlainText(f"❌ Error: {msg}")

    def _copy(self, key: str):
        area = self._platform_areas.get(key)
        if area:
            QApplication.clipboard().setText(area.toPlainText())
