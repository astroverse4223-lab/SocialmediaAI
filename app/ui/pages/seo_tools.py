from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QComboBox, QScrollArea, QFrame, QApplication
)
from PySide6.QtCore import Qt

from app.ui.components.cards import SectionHeader, Card
from app.core.worker import GenerationWorker
from app.core.ai_providers import create_provider
import app.core.content_generator as cg


class SEOToolsPage(QWidget):
    def __init__(self, config, db, parent=None):
        super().__init__(parent)
        self.config = config
        self.db = db
        self._worker = None
        self.setObjectName("content_area")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = SectionHeader(
            "SEO Tools",
            "Generate comprehensive SEO packages for your video content."
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
        self.project_combo.setMinimumWidth(260)
        bar_lay.addWidget(self.project_combo)

        gen_btn = QPushButton("🔍 Generate Full SEO Package")
        gen_btn.setObjectName("primary")
        gen_btn.setFixedHeight(38)
        gen_btn.clicked.connect(self._generate)
        bar_lay.addWidget(gen_btn)

        self.kw_btn = QPushButton("🔑 Keywords Only")
        self.kw_btn.setFixedHeight(38)
        self.kw_btn.clicked.connect(self._gen_keywords)
        bar_lay.addWidget(self.kw_btn)

        bar_lay.addStretch()

        copy_btn = QPushButton("📋 Copy All")
        copy_btn.setObjectName("ghost")
        copy_btn.setFixedHeight(38)
        copy_btn.clicked.connect(
            lambda: QApplication.clipboard().setText(self.output.toPlainText())
        )
        bar_lay.addWidget(copy_btn)
        layout.addWidget(bar)

        # Output
        content = QWidget()
        content.setObjectName("content_area")
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(24, 8, 24, 24)
        c_lay.setSpacing(8)

        self.output = QTextEdit()
        self.output.setReadOnly(False)
        self.output.setPlaceholderText(
            "Select a project and click 'Generate Full SEO Package' to get:\n\n"
            "• Primary & secondary keywords\n"
            "• Meta title & description\n"
            "• URL slug\n"
            "• Tags (20 YouTube tags)\n"
            "• Search intent analysis\n"
            "• Content gaps\n"
            "• Internal link opportunities\n"
            "• FAQ schema"
        )
        c_lay.addWidget(self.output)

        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("caption")
        c_lay.addWidget(self.status_lbl)

        layout.addWidget(content, 1)

    def refresh(self):
        self.project_combo.clear()
        for p in self.db.get_all_projects(limit=100):
            self.project_combo.addItem(p.title[:50], p.id)

    def _generate(self):
        self._run(cg.gen_seo_package, "seo_package", ["title"])

    def _gen_keywords(self):
        self._run(cg.gen_keywords_only, "seo_keywords", ["title"])

    def _run(self, func, key: str, extra_args: list):
        project_id = self.project_combo.currentData()
        if not project_id:
            return
        transcript = self.db.get_transcript(project_id)
        if not transcript or not transcript.content:
            self.status_lbl.setText("❌ No transcript for this project")
            return
        project = self.db.get_project(project_id)
        title = project.title if project else ""
        provider = create_provider(self.config)

        kwargs = {"transcript": transcript.content, "provider": provider}
        if "title" in extra_args:
            kwargs["title"] = title

        self.output.setPlainText("⏳ Generating SEO package…")
        self.status_lbl.setText("")

        if self._worker and self._worker.isRunning():
            self._worker.cancel()

        self._worker = GenerationWorker(key, func, kwargs)
        self._worker.result.connect(self._on_done)
        self._worker.error.connect(
            lambda k, m: (
                self.output.setPlainText(f"❌ Error: {m}"),
                self.status_lbl.setText("Generation failed")
            )
        )
        self._worker.start()

    def _on_done(self, key, content, pt, ct):
        self.output.setPlainText(content)
        self.status_lbl.setText(f"✅ Generated using {pt + ct:,} tokens")
        project_id = self.project_combo.currentData()
        if project_id:
            self.db.save_content(
                project_id=project_id, content_type=key, content=content,
                ai_provider=self.config.get("ai_provider", ""),
                tokens_used=pt + ct, prompt_tokens=pt
            )
