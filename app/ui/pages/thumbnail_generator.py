import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QComboBox, QScrollArea, QFrame, QGridLayout,
    QSplitter, QSizePolicy, QApplication, QFileDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont, QImage

from app.ui.components.cards import SectionHeader, Card
from app.core.worker import GenerationWorker
from app.core.media_worker import ImageGenerationWorker
from app.core.media_generator import IMAGE_PROVIDERS
from app.core.ai_providers import create_provider
import app.core.content_generator as cg


class ThumbnailConceptCard(QFrame):
    generate_image = Signal(str, int)   # prompt, card_index

    def __init__(self, number: int, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.number = number
        self._card_index = number - 1
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

        # Status label (shows errors/progress without overwriting concept text)
        self.img_status_lbl = QLabel("")
        self.img_status_lbl.setObjectName("caption")
        self.img_status_lbl.setWordWrap(True)
        layout.addWidget(self.img_status_lbl)

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
        if not text.strip():
            self._dalle_prompt = ""
            self.gen_img_btn.setEnabled(False)
            return

        # Try to extract an explicit DALL-E / image prompt section first
        prompt_lines = []
        if "DALL-E" in text.upper() or "IMAGE PROMPT" in text.upper():
            in_prompt = False
            for line in text.split("\n"):
                if "DALL-E" in line.upper() or "IMAGE PROMPT" in line.upper():
                    in_prompt = True
                    continue
                if in_prompt and line.strip():
                    prompt_lines.append(line.strip())
                    if len(prompt_lines) >= 4:
                        break

        if prompt_lines:
            self._dalle_prompt = " ".join(prompt_lines)
        else:
            # No explicit prompt section — build one from the concept description
            # Strip markdown markers and take the most descriptive lines
            clean_lines = [
                l.strip().lstrip("#*-•").strip()
                for l in text.split("\n")
                if l.strip() and not l.strip().startswith("**Concept")
            ]
            self._dalle_prompt = " ".join(clean_lines[:6])

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
            self.generate_image.emit(self._dalle_prompt, self._card_index)


class ThumbnailGeneratorPage(QWidget):
    def __init__(self, config, db, parent=None):
        super().__init__(parent)
        self.config = config
        self.db = db
        self._gen_worker = None
        # Per-card image workers so multiple cards can generate in parallel
        self._img_workers: dict = {}
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

        bar_lay.addWidget(QLabel("Image Provider:"))
        self.img_provider_combo = QComboBox()
        self.img_provider_combo.setFixedHeight(38)
        self.img_provider_combo.setMinimumWidth(220)
        for p in IMAGE_PROVIDERS:
            self.img_provider_combo.addItem(p["label"], p["key"])
        bar_lay.addWidget(self.img_provider_combo)
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

    def _generate_image(self, dalle_prompt: str, card_index: int):
        # Allow each card to generate independently in parallel
        existing = self._img_workers.get(card_index)
        if existing and existing.isRunning():
            return

        provider_key = self.img_provider_combo.currentData()
        provider = next((p for p in IMAGE_PROVIDERS if p["key"] == provider_key), None)
        if not provider:
            return

        api_key = self.config.get(provider["config_key"], "")
        # DALL-E 3 shares the OpenAI key
        if not api_key and provider_key == "dalle3":
            api_key = self.config.get("openai_api_key", "")

        card = self._concept_cards[card_index] if 0 <= card_index < len(self._concept_cards) else None
        if not card:
            return

        if not api_key:
            card.img_status_lbl.setText(
                f"⚠️ No API key for {provider['label']}. Set it in AI Settings → Media API Keys."
            )
            return

        card.img_status_lbl.setText("⏳ Generating image…")
        card.gen_img_btn.setEnabled(False)
        card.gen_img_btn.setText("⏳ Generating…")

        worker = ImageGenerationWorker(
            provider_key=provider_key,
            prompt=dalle_prompt,
            config=self.config,
            size_key="Landscape 16:9  (1792×1024)",
            n=1,
        )
        self._img_workers[card_index] = worker
        worker.images_ready.connect(
            lambda imgs, ci=card_index: self._on_image_ready(imgs, ci)
        )
        worker.error.connect(
            lambda m, ci=card_index: self._on_image_error(m, ci)
        )
        worker.finished.connect(
            lambda ci=card_index: self._on_image_done(ci)
        )
        worker.start()

    def _on_image_error(self, msg: str, card_index: int):
        card = self._concept_cards[card_index] if 0 <= card_index < len(self._concept_cards) else None
        if card:
            card.img_status_lbl.setText(f"❌ {msg}")

    def _on_image_done(self, card_index: int):
        card = self._concept_cards[card_index] if 0 <= card_index < len(self._concept_cards) else None
        if card:
            card.gen_img_btn.setEnabled(True)
            card.gen_img_btn.setText("🎨 Generate Image")

    def _on_image_ready(self, img_bytes_list: list, card_index: int):
        if not img_bytes_list:
            return
        card = self._concept_cards[card_index] if 0 <= card_index < len(self._concept_cards) else None
        if card:
            card.set_image(img_bytes_list[0])
            card.img_status_lbl.setText("✅ Image generated")
