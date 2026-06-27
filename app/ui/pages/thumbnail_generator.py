import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QComboBox, QScrollArea, QFrame, QGridLayout,
    QSplitter, QSizePolicy, QApplication, QFileDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont, QImage

from app.ui.components.cards import SectionHeader, Card
from app.core.worker import GenerationWorker, ThumbnailWorker
from app.core.ai_providers import create_provider
import app.core.content_generator as cg


class ThumbnailConceptCard(QFrame):
    generate_image = Signal(str)

    def __init__(self, number: int, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.number = number
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        lbl = QLabel(f"Concept {self.number}")
        lbl.setObjectName("h3")
        header.addWidget(lbl)
        header.addStretch()

        self.gen_img_btn = QPushButton("🎨 Generate Image")
        self.gen_img_btn.setObjectName("success")
        self.gen_img_btn.setFixedHeight(30)
        self.gen_img_btn.setEnabled(False)
        self.gen_img_btn.clicked.connect(self._on_gen_image)
        header.addWidget(self.gen_img_btn)
        layout.addLayout(header)

        self.concept_text = QTextEdit()
        self.concept_text.setReadOnly(True)
        self.concept_text.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        self.concept_text.setMaximumHeight(140)
        self.concept_text.setPlaceholderText("Concept details will appear here…")
        layout.addWidget(self.concept_text)

        # Image preview
        self.image_label = QLabel()
        self.image_label.setFixedSize(320, 180)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(
            "background: #1E1E2E; border-radius: 8px; color: #6060A0;"
        )
        self.image_label.setText("Image will appear here")
        layout.addWidget(self.image_label)

        self._dalle_prompt = ""

    def set_concept(self, text: str):
        self.concept_text.setPlainText(text)
        # Extract DALL-E prompt if present
        if "DALL-E PROMPT" in text.upper() or "DALL-E 3" in text.upper():
            lines = text.split("\n")
            in_prompt = False
            prompt_lines = []
            for line in lines:
                if "DALL-E" in line.upper():
                    in_prompt = True
                    continue
                if in_prompt and line.strip():
                    prompt_lines.append(line)
                    if len(prompt_lines) > 3:
                        break
            self._dalle_prompt = " ".join(prompt_lines)
            self.gen_img_btn.setEnabled(bool(self._dalle_prompt))

    def set_image(self, img_bytes: bytes):
        pix = QPixmap()
        pix.loadFromData(img_bytes)
        if not pix.isNull():
            scaled = pix.scaled(
                320, 180,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
            self.image_label.setText("")

    def _on_gen_image(self):
        if self._dalle_prompt:
            self.generate_image.emit(self._dalle_prompt)


class ThumbnailGeneratorPage(QWidget):
    def __init__(self, config, db, parent=None):
        super().__init__(parent)
        self.config = config
        self.db = db
        self._gen_worker = None
        self._img_worker = None
        self._concept_cards = []
        self.setObjectName("content_area")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = SectionHeader(
            "Thumbnail Generator",
            "Generate AI thumbnail concepts and images for your videos."
        )
        layout.addWidget(header)

        # Controls
        bar = QWidget()
        bar_lay = QHBoxLayout(bar)
        bar_lay.setContentsMargins(24, 14, 24, 14)
        bar_lay.setSpacing(12)

        bar_lay.addWidget(QLabel("Project:"))
        self.project_combo = QComboBox()
        self.project_combo.setFixedHeight(38)
        self.project_combo.setMinimumWidth(260)
        bar_lay.addWidget(self.project_combo)

        gen_btn = QPushButton("🖼️ Generate Concepts")
        gen_btn.setObjectName("primary")
        gen_btn.setFixedHeight(38)
        gen_btn.clicked.connect(self._generate_concepts)
        bar_lay.addWidget(gen_btn)

        bar_lay.addStretch()

        note = QLabel("💡 Image generation requires OpenAI DALL-E 3")
        note.setObjectName("caption")
        bar_lay.addWidget(note)
        layout.addWidget(bar)

        # Scroll area with concept cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.concepts_widget = QWidget()
        self.concepts_widget.setObjectName("content_area")
        self.concepts_layout = QVBoxLayout(self.concepts_widget)
        self.concepts_layout.setContentsMargins(24, 12, 24, 24)
        self.concepts_layout.setSpacing(14)

        # Pre-create 5 concept cards
        for i in range(1, 6):
            card = ThumbnailConceptCard(i)
            card.generate_image.connect(self._generate_image)
            self._concept_cards.append(card)
            self.concepts_layout.addWidget(card)

        self.concepts_layout.addStretch()
        scroll.setWidget(self.concepts_widget)
        layout.addWidget(scroll, 1)

    def refresh(self):
        self.project_combo.clear()
        for p in self.db.get_all_projects(limit=100):
            self.project_combo.addItem(p.title[:50], p.id)

    def _generate_concepts(self):
        project_id = self.project_combo.currentData()
        if not project_id:
            return
        transcript = self.db.get_transcript(project_id)
        if not transcript or not transcript.content:
            return
        project = self.db.get_project(project_id)
        title = project.title if project else ""
        provider = create_provider(self.config)

        if self._gen_worker and self._gen_worker.isRunning():
            return

        self._gen_worker = GenerationWorker(
            "thumbnail_ideas",
            cg.gen_thumbnail_ideas,
            {"transcript": transcript.content, "title": title, "provider": provider}
        )
        self._gen_worker.result.connect(self._on_concepts_ready)
        self._gen_worker.error.connect(
            lambda k, m: [c.concept_text.setPlainText(f"❌ {m}")
                          for c in self._concept_cards]
        )
        self._gen_worker.start()
        for card in self._concept_cards:
            card.concept_text.setPlainText("⏳ Generating concepts…")

    def _on_concepts_ready(self, key, content, pt, ct):
        # Parse concept sections from the content
        sections = content.split("**Concept ")
        for i, card in enumerate(self._concept_cards):
            if i + 1 < len(sections):
                card.set_concept("**Concept " + sections[i + 1])
            else:
                card.set_concept(content if i == 0 else "")

    def _generate_image(self, dalle_prompt: str):
        provider = create_provider(self.config)
        if not hasattr(provider, "generate_image"):
            return

        if self._img_worker and self._img_worker.isRunning():
            return

        self._img_worker = ThumbnailWorker(dalle_prompt, provider)
        self._img_worker.image_ready.connect(self._on_image_ready)
        self._img_worker.start()

    def _on_image_ready(self, img_bytes: bytes):
        # Save to thumbnails dir and show in first card that requested it
        for card in self._concept_cards:
            if card.gen_img_btn.isEnabled():
                card.set_image(img_bytes)
                break
