from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QComboBox, QScrollArea, QFrame, QSplitter, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from app.ui.components.cards import SectionHeader, Card
from app.core.worker import GenerationWorker
from app.core.ai_providers import create_provider
import app.core.content_generator as cg


class BlogGeneratorPage(QWidget):
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
            "Blog Generator",
            "Generate blog posts in multiple formats from your video transcripts."
        )
        layout.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── LEFT: Controls ──────────────────────────────
        left = QWidget()
        left.setMinimumWidth(300)
        left.setMaximumWidth(380)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(20, 20, 10, 20)
        left_layout.setSpacing(14)

        # Project selector
        proj_card = Card()
        proj_card.layout.addWidget(QLabel("📁 Select Project"))
        self.project_combo = QComboBox()
        self.project_combo.setFixedHeight(38)
        proj_card.layout.addWidget(self.project_combo)
        left_layout.addWidget(proj_card)

        # Blog format
        fmt_card = Card()
        fmt_card.layout.addWidget(QLabel("📝 Blog Format"))
        self.format_combo = QComboBox()
        self.format_combo.setFixedHeight(38)
        for label, key in [
            ("Long-Form SEO Article", "blog_long_form"),
            ("Medium Article", "blog_medium"),
            ("Short Blog Post", "blog_short"),
            ("Tutorial / Guide", "blog_tutorial"),
        ]:
            self.format_combo.addItem(label, key)
        fmt_card.layout.addWidget(self.format_combo)

        self.gen_btn = QPushButton("⚡ Generate Blog")
        self.gen_btn.setObjectName("primary")
        self.gen_btn.setFixedHeight(42)
        self.gen_btn.clicked.connect(self._generate)
        fmt_card.layout.addWidget(self.gen_btn)
        left_layout.addWidget(fmt_card)

        # Export options
        export_card = Card()
        export_card.layout.addWidget(QLabel("📤 Export"))
        export_row = QHBoxLayout()
        for fmt in ["TXT", "MD", "HTML", "DOCX"]:
            btn = QPushButton(fmt)
            btn.setFixedHeight(34)
            btn.clicked.connect(lambda _, f=fmt: self._export(f))
            export_row.addWidget(btn)
        export_card.layout.addLayout(export_row)
        left_layout.addWidget(export_card)
        left_layout.addStretch()

        splitter.addWidget(left)

        # ── RIGHT: Output ───────────────────────────────
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(10, 20, 20, 20)
        right_layout.setSpacing(8)

        out_header = QHBoxLayout()
        self.output_title = QLabel("Generated Blog Post")
        self.output_title.setObjectName("h2")
        out_header.addWidget(self.output_title)
        out_header.addStretch()

        copy_btn = QPushButton("📋 Copy All")
        copy_btn.setObjectName("ghost")
        copy_btn.clicked.connect(
            lambda: QApplication.clipboard().setText(self.output.toPlainText())
        )
        out_header.addWidget(copy_btn)
        right_layout.addLayout(out_header)

        self.output = QTextEdit()
        self.output.setReadOnly(False)
        self.output.setPlaceholderText(
            "Select a project and format, then click Generate Blog…"
        )
        right_layout.addWidget(self.output)
        self.word_count_lbl = QLabel("")
        self.word_count_lbl.setObjectName("caption")
        right_layout.addWidget(self.word_count_lbl)
        self.output.textChanged.connect(self._update_word_count)

        splitter.addWidget(right)
        splitter.setSizes([340, 700])

        content = QWidget()
        content.setObjectName("content_area")
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.addWidget(splitter)
        layout.addWidget(content, 1)

    def refresh(self):
        self.project_combo.clear()
        projects = self.db.get_all_projects(limit=100)
        for p in projects:
            self.project_combo.addItem(p.title[:50], p.id)

    def _generate(self):
        project_id = self.project_combo.currentData()
        if not project_id:
            return
        transcript = self.db.get_transcript(project_id)
        if not transcript or not transcript.content:
            self.output.setPlainText("❌ No transcript found for this project.")
            return
        project = self.db.get_project(project_id)
        fmt_key = self.format_combo.currentData()
        title = project.title if project else ""

        func_map = {
            "blog_long_form": (cg.gen_blog_long_form, ["title"]),
            "blog_medium":    (cg.gen_blog_medium,    ["title"]),
            "blog_short":     (cg.gen_blog_short,     ["title"]),
            "blog_tutorial":  (cg.gen_blog_tutorial,  ["title"]),
        }
        func, extra = func_map.get(fmt_key, (cg.gen_blog_long_form, ["title"]))
        kwargs = {"transcript": transcript.content, "provider": create_provider(self.config)}
        if "title" in extra:
            kwargs["title"] = title

        self.output.setPlainText("⏳ Generating blog post…")
        self.gen_btn.setEnabled(False)

        if self._worker and self._worker.isRunning():
            self._worker.cancel()

        self._worker = GenerationWorker(fmt_key, func, kwargs)
        self._worker.result.connect(self._on_done)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(lambda: self.gen_btn.setEnabled(True))
        self._worker.start()

    def _on_done(self, key, content, pt, ct):
        self.output.setPlainText(content)
        project_id = self.project_combo.currentData()
        if project_id:
            self.db.save_content(
                project_id=project_id, content_type=key, content=content,
                ai_provider=self.config.get("ai_provider", ""),
                tokens_used=pt + ct, prompt_tokens=pt
            )

    def _on_error(self, key, msg):
        self.output.setPlainText(f"❌ Error: {msg}")

    def _export(self, fmt: str):
        content = self.output.toPlainText()
        if not content:
            return
        project_id = self.project_combo.currentData()
        project = self.db.get_project(project_id) if project_id else None
        title = project.title if project else "blog_post"

        from app.core import exporter
        out_dir = self.config.get("export_dir", "")
        try:
            if fmt == "TXT":
                path = exporter.export_txt({self.format_combo.currentText(): content}, title, out_dir)
            elif fmt == "MD":
                path = exporter.export_markdown({self.format_combo.currentText(): content}, title, out_dir)
            elif fmt == "HTML":
                path = exporter.export_html({self.format_combo.currentText(): content}, title, out_dir)
            elif fmt == "DOCX":
                path = exporter.export_docx({self.format_combo.currentText(): content}, title, out_dir)
            else:
                return
            import os
            os.startfile(os.path.dirname(path))
        except Exception as e:
            self.output.setPlainText(f"❌ Export error: {e}")

    def _update_word_count(self):
        text = self.output.toPlainText()
        wc = len(text.split()) if text else 0
        self.word_count_lbl.setText(f"Word count: {wc:,}")
