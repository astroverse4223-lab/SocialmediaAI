"""New Project page — the core workflow of the application."""
import re
from typing import Optional, Dict

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QScrollArea, QFrame, QSplitter,
    QTabWidget, QProgressBar, QSizePolicy, QApplication,
    QGridLayout, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QUrl

from app.ui.components.cards import Card, ContentCard, SectionHeader, InfoRow
from app.ui.components.dialogs import NotificationBanner
from app.core.worker import YouTubeWorker, BatchGenerationWorker, GenerationWorker
from app.core.ai_providers import create_provider
from app.core import content_generator as cg


class VideoInfoPanel(QFrame):
    """Displays fetched YouTube video information."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self._nam = QNetworkAccessManager(self)
        self._setup()
        self.hide()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # Title bar
        title_row = QHBoxLayout()
        self.thumb_lbl = QLabel("▶️")
        self.thumb_lbl.setFont(QFont("Segoe UI", 32))
        self.thumb_lbl.setFixedSize(120, 68)
        self.thumb_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_lbl.setStyleSheet(
            "background: #1E1E2E; border-radius: 8px;"
        )
        title_row.addWidget(self.thumb_lbl)

        right_col = QVBoxLayout()
        right_col.setSpacing(4)
        self.title_lbl = QLabel("Video Title")
        self.title_lbl.setObjectName("h3")
        self.title_lbl.setWordWrap(True)
        right_col.addWidget(self.title_lbl)

        self.channel_lbl = QLabel("Channel Name")
        self.channel_lbl.setObjectName("subtitle")
        right_col.addWidget(self.channel_lbl)
        title_row.addLayout(right_col, 1)
        layout.addLayout(title_row)

        # Meta grid
        self.dur_row = InfoRow("Duration")
        self.views_row = InfoRow("Views")
        self.date_row = InfoRow("Published")
        self.lang_row = InfoRow("Language")
        for row in [self.dur_row, self.views_row, self.date_row, self.lang_row]:
            layout.addWidget(row)

    def populate(self, info: dict):
        from app.core.youtube import format_publish_date, format_view_count
        self.title_lbl.setText(info.get("title", "")[:100])
        self.channel_lbl.setText(f"📺 {info.get('channel', '')}")
        dur = info.get("duration", 0)
        self.dur_row.set_value(
            f"{dur // 60}:{dur % 60:02d}" if dur else "Unknown"
        )
        self.views_row.set_value(format_view_count(info.get("views", 0)))
        self.date_row.set_value(format_publish_date(info.get("publish_date", "")))
        self.show()

        # Load thumbnail
        thumb_url = info.get("thumbnail_url", "")
        if thumb_url:
            req = QNetworkRequest(QUrl(thumb_url))
            reply = self._nam.get(req)
            reply.finished.connect(lambda r=reply: self._on_thumb(r))

    def _on_thumb(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            data = reply.readAll()
            pix = QPixmap()
            pix.loadFromData(bytes(data))
            if not pix.isNull():
                self.thumb_lbl.setPixmap(
                    pix.scaled(120, 68, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
                )
        reply.deleteLater()


class TranscriptPanel(QFrame):
    """Transcript viewer/editor."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        header = QHBoxLayout()
        lbl = QLabel("📜 Transcript")
        lbl.setObjectName("h3")
        header.addWidget(lbl)
        header.addStretch()

        self.stats_lbl = QLabel("")
        self.stats_lbl.setObjectName("caption")
        header.addWidget(self.stats_lbl)

        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.setObjectName("ghost")
        self.edit_btn.setFixedHeight(28)
        self.edit_btn.clicked.connect(self._toggle_edit)
        header.addWidget(self.edit_btn)
        layout.addLayout(header)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        self.text_edit.setMinimumHeight(140)
        self.text_edit.setMaximumHeight(200)
        self.text_edit.setPlaceholderText(
            "Transcript will appear here after loading the video…"
        )
        layout.addWidget(self.text_edit)

        self.status_lbl = QLabel("No transcript loaded")
        self.status_lbl.setObjectName("caption")
        layout.addWidget(self.status_lbl)

        self._editing = False

    def set_transcript(self, data: dict):
        self.text_edit.setPlainText(data.get("text", ""))
        wc = data.get("word_count", 0)
        reading_min = max(1, wc // 200)
        self.stats_lbl.setText(
            f"{wc:,} words  •  ~{reading_min} min read  •  "
            f"{data.get('language', 'en').upper()}"
        )
        self.status_lbl.setText("✅ Transcript loaded")

    def set_loading(self):
        self.status_lbl.setText("⏳ Loading transcript…")

    def set_error(self, msg: str):
        self.status_lbl.setText(f"❌ {msg}")

    def get_text(self) -> str:
        return self.text_edit.toPlainText()

    def _toggle_edit(self):
        self._editing = not self._editing
        self.text_edit.setReadOnly(not self._editing)
        if self._editing:
            # Fully editable
            self.text_edit.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextEditorInteraction
            )
        else:
            # Read-only but still keyboard-selectable/copyable
            self.text_edit.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse |
                Qt.TextInteractionFlag.TextSelectableByKeyboard
            )
        self.edit_btn.setText("💾 Save" if self._editing else "✏️ Edit")


class GenerationControlPanel(QFrame):
    """Controls for triggering AI content generation."""
    generate_all = Signal()
    generate_one = Signal(str, str)   # key, label

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setObjectName("card")
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # Provider display
        provider_row = QHBoxLayout()
        provider_lbl = QLabel("🤖 AI Provider:")
        provider_lbl.setObjectName("subtitle")
        self.provider_val = QLabel(self.config.get("ai_provider", "openai").title())
        self.provider_val.setObjectName("accent")
        provider_row.addWidget(provider_lbl)
        provider_row.addWidget(self.provider_val)
        provider_row.addStretch()
        layout.addLayout(provider_row)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.progress_lbl = QLabel("")
        self.progress_lbl.setObjectName("caption")
        self.progress_lbl.hide()
        layout.addWidget(self.progress_lbl)

        # Generate All button
        self.gen_all_btn = QPushButton("⚡ Generate All Content")
        self.gen_all_btn.setObjectName("primary")
        self.gen_all_btn.setFixedHeight(44)
        self.gen_all_btn.setEnabled(False)
        self.gen_all_btn.clicked.connect(self.generate_all.emit)
        layout.addWidget(self.gen_all_btn)

        self.cancel_btn = QPushButton("⏹ Cancel")
        self.cancel_btn.setObjectName("danger")
        self.cancel_btn.setFixedHeight(36)
        self.cancel_btn.hide()
        layout.addWidget(self.cancel_btn)

        # Quick generate buttons (2 columns)
        quick_lbl = QLabel("Or generate individually:")
        quick_lbl.setObjectName("subtitle")
        layout.addWidget(quick_lbl)

        grid = QGridLayout()
        grid.setSpacing(6)

        quick_items = [
            ("executive_summary", "📋 Summary"),
            ("twitter_thread",    "🐦 Twitter"),
            ("linkedin_post",     "💼 LinkedIn"),
            ("instagram_captions","📸 Instagram"),
            ("tiktok_content",    "🎵 TikTok"),
            ("blog_long_form",    "📝 Blog Post"),
            ("seo_package",       "🔍 SEO"),
            ("timestamps",        "⏱ Timestamps"),
            ("video_titles",      "🎬 Titles"),
            ("newsletter",        "📧 Newsletter"),
        ]

        self._quick_btns = {}
        for i, (key, label) in enumerate(quick_items):
            btn = QPushButton(label)
            btn.setFixedHeight(32)
            btn.setEnabled(False)
            btn.clicked.connect(lambda _, k=key, l=label: self.generate_one.emit(k, l))
            self._quick_btns[key] = btn
            grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(grid)

    def set_ready(self, ready: bool):
        self.gen_all_btn.setEnabled(ready)
        for btn in self._quick_btns.values():
            btn.setEnabled(ready)

    def set_generating(self, generating: bool):
        self.gen_all_btn.setVisible(not generating)
        self.cancel_btn.setVisible(generating)
        self.progress_bar.setVisible(generating)
        self.progress_lbl.setVisible(generating)
        if not generating:
            self.progress_bar.setValue(0)
            self.progress_lbl.setText("")

    def update_progress(self, pct: int, label: str):
        self.progress_bar.setValue(pct)
        self.progress_lbl.setText(label)

    def refresh_provider(self):
        self.provider_val.setText(self.config.get("ai_provider", "openai").title())


class NewProjectPage(QWidget):
    """Main workflow page: URL → Transcript → Generate → Review."""
    project_saved = Signal(int)

    # Content tab definitions: (tab_label, [(content_key, display_name, icon)])
    CONTENT_TABS = [
        ("📋 Summary", [
            ("executive_summary",  "Executive Summary",  "📊"),
            ("bullet_summary",     "Bullet Summary",     "•"),
            ("key_takeaways",      "Key Takeaways",      "🎯"),
            ("quotes",             "Key Quotes",         "💬"),
            ("faq",                "FAQ",                "❓"),
            ("action_items",       "Action Items",       "✅"),
        ]),
        ("📝 Blog", [
            ("blog_long_form",  "Long-Form SEO Blog",  "📄"),
            ("blog_medium",     "Medium Article",      "✍️"),
            ("blog_short",      "Short Blog",          "⚡"),
            ("blog_tutorial",   "Tutorial / Guide",    "📚"),
        ]),
        ("📱 Social Media", [
            ("twitter_thread",      "Twitter / X Thread",  "🐦"),
            ("linkedin_post",       "LinkedIn Post",        "💼"),
            ("facebook_post",       "Facebook Post",        "👍"),
            ("instagram_captions",  "Instagram Captions",   "📸"),
            ("tiktok_content",      "TikTok Content",       "🎵"),
            ("threads_post",        "Threads",              "🧵"),
            ("youtube_community",   "YouTube Community",    "▶️"),
        ]),
        ("🔍 SEO", [
            ("seo_package",    "Full SEO Package",  "🔑"),
        ]),
        ("⏱ Timestamps", [
            ("timestamps",  "Chapter Timestamps",  "🕐"),
        ]),
        ("📧 Extras", [
            ("newsletter",     "Email Newsletter",    "📧"),
            ("podcast_notes",  "Podcast Show Notes",  "🎙️"),
            ("press_release",  "Press Release",       "📰"),
            ("ctas",           "Call-to-Actions",     "🎯"),
        ]),
        ("🎬 Video Assets", [
            ("video_titles",      "Title Ideas",         "🏷️"),
            ("thumbnail_ideas",   "Thumbnail Concepts",  "🖼️"),
        ]),
    ]

    def __init__(self, config, db, parent=None):
        super().__init__(parent)
        self.config = config
        self.db = db
        self.setObjectName("content_area")
        self._current_project_id: Optional[int] = None
        self._current_info: Optional[dict] = None
        self._workers = []
        self._content_cards: Dict[str, ContentCard] = {}
        self._yt_worker: Optional[YouTubeWorker] = None
        self._batch_worker: Optional[BatchGenerationWorker] = None
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        self.header = SectionHeader(
            "New Project",
            "Paste a YouTube URL to transform it into content."
        )
        clear_btn = QPushButton("🗑 Clear")
        clear_btn.setObjectName("ghost")
        clear_btn.clicked.connect(self._clear)
        self.header.add_action(clear_btn)
        main_layout.addWidget(self.header)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(3)

        # ── LEFT PANEL ─────────────────────────────────────
        left_widget = QWidget()
        left_widget.setMinimumWidth(360)
        left_widget.setMaximumWidth(460)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(20, 20, 10, 20)
        left_layout.setSpacing(14)

        # URL input card
        url_card = Card()
        url_card.layout.addWidget(QLabel("🔗  YouTube URL"))

        url_row = QHBoxLayout()
        url_row.setSpacing(8)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        self.url_input.returnPressed.connect(self._load_video)
        url_row.addWidget(self.url_input)

        paste_btn = QPushButton("📋")
        paste_btn.setObjectName("icon_btn")
        paste_btn.setFixedSize(38, 38)
        paste_btn.setToolTip("Paste from clipboard")
        paste_btn.clicked.connect(self._paste_url)
        url_row.addWidget(paste_btn)
        url_card.layout.addLayout(url_row)

        self.load_btn = QPushButton("🔍 Load Video")
        self.load_btn.setObjectName("primary")
        self.load_btn.setFixedHeight(40)
        self.load_btn.clicked.connect(self._load_video)
        url_card.layout.addWidget(self.load_btn)

        self.url_status = QLabel("")
        self.url_status.setObjectName("caption")
        url_card.layout.addWidget(self.url_status)

        left_layout.addWidget(url_card)

        # Video info panel
        self.video_info = VideoInfoPanel()
        left_layout.addWidget(self.video_info)

        # Transcript panel
        self.transcript_panel = TranscriptPanel()
        left_layout.addWidget(self.transcript_panel)

        # Generation controls
        self.gen_panel = GenerationControlPanel(self.config)
        self.gen_panel.generate_all.connect(self._generate_all)
        self.gen_panel.generate_one.connect(self._generate_one)
        left_layout.addWidget(self.gen_panel)
        left_layout.addStretch()

        splitter.addWidget(left_widget)

        # ── RIGHT PANEL ────────────────────────────────────
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 20, 20, 20)
        right_layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        for tab_label, items in self.CONTENT_TABS:
            tab_widget = QWidget()
            tab_scroll = QScrollArea()
            tab_scroll.setWidgetResizable(True)
            tab_scroll.setFrameShape(QFrame.Shape.NoFrame)

            tab_inner = QWidget()
            tab_inner_layout = QVBoxLayout(tab_inner)
            tab_inner_layout.setContentsMargins(4, 8, 4, 8)
            tab_inner_layout.setSpacing(12)

            for key, label, icon in items:
                card = ContentCard(label, key, icon)
                card.regenerate_requested.connect(self._on_regenerate)
                card.copy_requested.connect(self._on_copy_notice)
                self._content_cards[key] = card
                tab_inner_layout.addWidget(card)

            tab_inner_layout.addStretch()
            tab_scroll.setWidget(tab_inner)

            outer_layout = QVBoxLayout(tab_widget)
            outer_layout.setContentsMargins(0, 0, 0, 0)
            outer_layout.addWidget(tab_scroll)

            self.tabs.addTab(tab_widget, tab_label)

        right_layout.addWidget(self.tabs)
        splitter.addWidget(right_widget)

        splitter.setSizes([400, 700])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter, 1)

    # ──────────────────── ACTIONS ─────────────────────────

    def _paste_url(self):
        clipboard = QApplication.clipboard().text().strip()
        if clipboard:
            self.url_input.setText(clipboard)
            self._load_video()

    def _clear(self):
        self.url_input.clear()
        self.url_status.setText("")
        self.video_info.hide()
        self.transcript_panel.text_edit.clear()
        self.transcript_panel.stats_lbl.setText("")
        self.transcript_panel.status_lbl.setText("No transcript loaded")
        self.gen_panel.set_ready(False)
        for card in self._content_cards.values():
            card.text_edit.clear()
            card.status_lbl.setText("Not generated")
            card.token_lbl.setText("")
        self._current_project_id = None
        self._current_info = None

    def _load_video(self):
        url = self.url_input.text().strip()
        if not url:
            self.url_status.setText("⚠️ Please enter a YouTube URL")
            return

        from app.core.youtube import validate_youtube_url
        if not validate_youtube_url(url):
            self.url_status.setText("❌ Invalid YouTube URL")
            return

        self.load_btn.setEnabled(False)
        self.url_status.setText("⏳ Loading video…")

        if self._yt_worker and self._yt_worker.isRunning():
            self._yt_worker.cancel()
            self._yt_worker.wait()

        self._yt_worker = YouTubeWorker(url, fetch_transcript=True)
        self._yt_worker.info_ready.connect(self._on_info_ready)
        self._yt_worker.transcript_ready.connect(self._on_transcript_ready)
        self._yt_worker.progress.connect(
            lambda msg: self.url_status.setText(f"⏳ {msg}")
        )
        self._yt_worker.error.connect(self._on_load_error)
        self._yt_worker.finished.connect(
            lambda: self.load_btn.setEnabled(True)
        )
        self._yt_worker.start()

    def _on_info_ready(self, info: dict):
        self._current_info = info
        self.video_info.populate(info)
        self.url_status.setText("✅ Video loaded")

        # Create or update DB project
        project = self.db.create_project(
            youtube_url=info["url"],
            title=info["title"],
            video_id=info["video_id"],
            channel=info["channel"],
            duration=info["duration"],
            views=info["views"],
            thumbnail_url=info["thumbnail_url"],
            description=info["description"],
            publish_date=info["publish_date"],
            tags=info["tags"],
        )
        self._current_project_id = project.id
        self.config.add_recent_project(project.id)
        self.transcript_panel.set_loading()

    def _on_transcript_ready(self, data: dict):
        self.transcript_panel.set_transcript(data)
        if self._current_project_id:
            self.db.save_transcript(
                self._current_project_id,
                content=data["text"],
                timestamped=data.get("timestamped", ""),
                language=data.get("language", "en"),
            )
        self.gen_panel.set_ready(True)

    def _on_load_error(self, msg: str):
        self.url_status.setText(f"❌ {msg}")
        self.transcript_panel.set_error(msg)
        self.load_btn.setEnabled(True)

    def _generate_all(self):
        if not self._check_ready():
            return
        transcript = self.transcript_panel.get_text()
        title = self._current_info.get("title", "") if self._current_info else ""
        duration = self._current_info.get("duration", 0) if self._current_info else 0
        provider = create_provider(self.config)

        if self._batch_worker and self._batch_worker.isRunning():
            return

        self._batch_worker = BatchGenerationWorker(
            transcript=transcript, title=title,
            duration=duration, provider=provider
        )
        self._batch_worker.task_started.connect(self._on_task_started)
        self._batch_worker.task_done.connect(self._on_task_done)
        self._batch_worker.task_error.connect(self._on_task_error)
        self._batch_worker.progress_pct.connect(
            lambda pct: self.gen_panel.update_progress(pct, "")
        )
        self._batch_worker.all_done.connect(self._on_all_done)
        self.gen_panel.cancel_btn.clicked.connect(self._batch_worker.cancel)
        self.gen_panel.set_generating(True)
        self._batch_worker.start()

    def _generate_one(self, key: str, label: str):
        if not self._check_ready():
            return
        transcript = self.transcript_panel.get_text()
        title = self._current_info.get("title", "") if self._current_info else ""
        duration = self._current_info.get("duration", 0) if self._current_info else 0
        provider = create_provider(self.config)

        task_map = {t[0]: (t[2], t[3]) for t in cg.CONTENT_TASKS}
        if key not in task_map:
            return

        func, extra_args = task_map[key]
        kwargs = {"transcript": transcript, "provider": provider}
        if "title" in extra_args or "original_title" in extra_args:
            kwargs["title"] = title
        if "duration" in extra_args:
            kwargs["duration"] = duration

        if key in self._content_cards:
            self._content_cards[key].set_loading()

        worker = GenerationWorker(key, func, kwargs)
        worker.result.connect(self._on_single_done)
        worker.error.connect(self._on_task_error)
        self._workers.append(worker)
        worker.finished.connect(lambda w=worker: self._workers.discard(w)
                                 if hasattr(self._workers, 'discard')
                                 else None)
        worker.start()

    def _on_regenerate(self, key: str):
        label_map = {k: l for _, items in self.CONTENT_TABS
                     for k, l, _ in items}
        label = label_map.get(key, key)
        self._generate_one(key, label)

    def _on_task_started(self, key: str, label: str, current: int, total: int):
        if key in self._content_cards:
            self._content_cards[key].set_loading()
        self.gen_panel.update_progress(
            int((current - 1) / total * 100),
            f"Generating {label}… ({current}/{total})"
        )

    def _on_task_done(self, key: str, content: str, pt: int, ct: int):
        if key in self._content_cards:
            self._content_cards[key].set_content(content, pt + ct)
        if self._current_project_id and content:
            self.db.save_content(
                project_id=self._current_project_id,
                content_type=key,
                content=content,
                ai_provider=self.config.get("ai_provider", "openai"),
                model=self.config.get("ai_model", ""),
                tokens_used=pt + ct,
                prompt_tokens=pt,
            )

    def _on_single_done(self, key: str, content: str, pt: int, ct: int):
        self._on_task_done(key, content, pt, ct)

    def _on_task_error(self, key: str, msg: str):
        if key in self._content_cards:
            self._content_cards[key].set_error(msg)

    def _on_all_done(self, results: dict):
        self.gen_panel.set_generating(False)
        if self._current_project_id:
            self.db.update_project(self._current_project_id, status="complete")
            self.project_saved.emit(self._current_project_id)

    def _on_copy_notice(self, key: str):
        # Brief status flash
        pass

    def _check_ready(self) -> bool:
        if not self.transcript_panel.get_text():
            self.url_status.setText("⚠️ No transcript available")
            return False
        if not self.config.is_ai_configured():
            self.url_status.setText(
                "⚠️ AI provider not configured — go to AI Settings"
            )
            return False
        return True

    def load_project(self, project_id: int):
        """Load an existing project into this page."""
        project = self.db.get_project(project_id)
        if not project:
            return

        self.url_input.setText(project.youtube_url)
        self._current_project_id = project_id
        self._current_info = {
            "title": project.title,
            "video_id": project.video_id or "",
            "channel": project.channel or "",
            "duration": project.duration or 0,
            "views": project.views or 0,
            "thumbnail_url": project.thumbnail_url or "",
            "description": project.description or "",
            "publish_date": project.publish_date or "",
            "tags": project.tags or "",
            "url": project.youtube_url,
        }
        self.video_info.populate(self._current_info)

        transcript = self.db.get_transcript(project_id)
        if transcript:
            self.transcript_panel.set_transcript({
                "text": transcript.content or "",
                "word_count": transcript.word_count or 0,
                "language": transcript.language or "en",
            })
            self.gen_panel.set_ready(True)

        # Load all existing generated content
        content_items = self.db.get_all_content_for_project(project_id)
        for item in content_items:
            key = item.content_type
            if key in self._content_cards:
                self._content_cards[key].set_content(
                    item.content or "", item.tokens_used or 0
                )
