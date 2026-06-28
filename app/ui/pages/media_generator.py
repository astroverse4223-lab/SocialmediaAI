"""
AI Media Generator page — Image & Video generation.
Tabs: Image Generator | Video Generator
"""
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QComboBox, QScrollArea, QFrame,
    QTabWidget, QSplitter, QFileDialog, QApplication,
    QGridLayout, QSizePolicy, QSpinBox, QProgressBar,
    QCheckBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QPixmap, QFont, QImage, QDragEnterEvent, QDropEvent

from app.ui.components.cards import SectionHeader, Card
from app.core.media_generator import IMAGE_PROVIDERS, VIDEO_PROVIDERS, IMAGE_SIZES, IMAGE_STYLE_PRESETS, VIDEO_ASPECT_RATIOS
from app.core.media_worker import ImageGenerationWorker, VideoSubmitWorker, VideoPollWorker, VideoDownloadWorker


# ─────────────────────────────────────────────────────────
#  IMAGE RESULT CARD
# ─────────────────────────────────────────────────────────

class ImageResultCard(QFrame):
    """Displays a single generated image with action buttons."""
    use_as_ref = Signal(bytes)

    def __init__(self, img_bytes: bytes, prompt: str, provider: str,
                 save_dir: str, parent=None):
        super().__init__(parent)
        self.img_bytes = img_bytes
        self.save_dir = save_dir
        self.setObjectName("card")
        self.setFixedWidth(320)
        self._setup(prompt, provider)

    def _setup(self, prompt: str, provider: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Image display
        self.img_lbl = QLabel()
        self.img_lbl.setFixedSize(300, 169)
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_lbl.setStyleSheet("background: #1A1A2E; border-radius: 8px;")
        pix = QPixmap()
        pix.loadFromData(self.img_bytes)
        if not pix.isNull():
            self.img_lbl.setPixmap(
                pix.scaled(300, 169,
                           Qt.AspectRatioMode.KeepAspectRatio,
                           Qt.TransformationMode.SmoothTransformation)
            )
        layout.addWidget(self.img_lbl)

        # Prompt
        prompt_lbl = QLabel(prompt[:80] + ("…" if len(prompt) > 80 else ""))
        prompt_lbl.setObjectName("caption")
        prompt_lbl.setWordWrap(True)
        layout.addWidget(prompt_lbl)

        # Provider
        prov_lbl = QLabel(f"🤖 {provider}")
        prov_lbl.setObjectName("caption")
        prov_lbl.setStyleSheet("color: #7C3AED;")
        layout.addWidget(prov_lbl)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        save_btn = QPushButton("💾 Save")
        save_btn.setFixedHeight(30)
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        copy_btn = QPushButton("📋 Copy")
        copy_btn.setFixedHeight(30)
        copy_btn.clicked.connect(self._copy)
        btn_row.addWidget(copy_btn)

        ref_btn = QPushButton("🎬 Use as Ref")
        ref_btn.setObjectName("ghost")
        ref_btn.setFixedHeight(30)
        ref_btn.setToolTip("Use this image as reference for video generation")
        ref_btn.clicked.connect(lambda: self.use_as_ref.emit(self.img_bytes))
        btn_row.addWidget(ref_btn)

        layout.addLayout(btn_row)

    def _save(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = os.path.join(self.save_dir, f"ai_image_{ts}.png")
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", default_name, "PNG Images (*.png)"
        )
        if path:
            with open(path, "wb") as f:
                f.write(self.img_bytes)

    def _copy(self):
        pix = QPixmap()
        pix.loadFromData(self.img_bytes)
        QApplication.clipboard().setPixmap(pix)


# ─────────────────────────────────────────────────────────
#  VIDEO JOB CARD
# ─────────────────────────────────────────────────────────

class VideoJobCard(QFrame):
    """Displays a video generation job with live status."""
    download_requested = Signal(dict)  # task_info

    STATUS_STYLE = {
        "queued":     ("🕐 Queued",     "#8080A0"),
        "processing": ("⏳ Processing…", "#F59E0B"),
        "completed":  ("✅ Ready",       "#10B981"),
        "failed":     ("❌ Failed",      "#EF4444"),
        "unknown":    ("❓ Unknown",     "#8080A0"),
    }

    def __init__(self, task_info: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.task_info = task_info
        self.setObjectName("card")
        self.setFixedHeight(120)
        self._setup()
        self.update_status(task_info)

    def _setup(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        # Video icon placeholder
        icon_lbl = QLabel("🎬")
        icon_lbl.setFont(QFont("Segoe UI", 28))
        icon_lbl.setFixedWidth(50)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_lbl)

        # Info
        info = QVBoxLayout()
        info.setSpacing(4)
        self.prompt_lbl = QLabel("")
        self.prompt_lbl.setObjectName("h3")
        self.prompt_lbl.setWordWrap(False)
        info.addWidget(self.prompt_lbl)

        self.provider_lbl = QLabel("")
        self.provider_lbl.setObjectName("subtitle")
        info.addWidget(self.provider_lbl)

        self.status_lbl = QLabel("")
        info.addWidget(self.status_lbl)
        layout.addLayout(info, 1)

        # Actions
        actions = QVBoxLayout()
        actions.setSpacing(6)
        actions.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        self.dl_btn = QPushButton("⬇️ Download")
        self.dl_btn.setObjectName("success")
        self.dl_btn.setFixedHeight(30)
        self.dl_btn.setEnabled(False)
        self.dl_btn.clicked.connect(lambda: self.download_requested.emit(self.task_info))
        actions.addWidget(self.dl_btn)

        open_btn = QPushButton("🌐 Open URL")
        open_btn.setObjectName("ghost")
        open_btn.setFixedHeight(28)
        open_btn.clicked.connect(self._open_url)
        self._open_btn = open_btn
        self._open_btn.setEnabled(False)
        actions.addWidget(open_btn)

        layout.addLayout(actions)

    def update_status(self, task_info: Dict[str, Any]):
        self.task_info = task_info
        prompt = task_info.get("prompt", "")
        self.prompt_lbl.setText(prompt[:65] + ("…" if len(prompt) > 65 else ""))
        self.provider_lbl.setText(f"🤖 {task_info.get('provider_label', task_info.get('provider', ''))}")

        status = task_info.get("status", "unknown")
        label, color = self.STATUS_STYLE.get(status, ("❓ Unknown", "#8080A0"))
        self.status_lbl.setText(label)
        self.status_lbl.setStyleSheet(f"color: {color}; font-weight: 600; font-size: 12px;")

        has_url = bool(task_info.get("video_url"))
        self.dl_btn.setEnabled(has_url)
        self._open_btn.setEnabled(has_url)

    def _open_url(self):
        import webbrowser
        url = self.task_info.get("video_url", "")
        if url:
            webbrowser.open(url)


# ─────────────────────────────────────────────────────────
#  IMAGE GENERATOR TAB
# ─────────────────────────────────────────────────────────

class ImageGeneratorTab(QWidget):
    use_image_as_ref = Signal(bytes)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self._worker: Optional[ImageGenerationWorker] = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── LEFT: Controls ──────────────────────────────
        left = QWidget()
        left.setFixedWidth(370)
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(16, 16, 8, 16)
        left_lay.setSpacing(12)

        # Prompt
        prompt_card = Card()
        prompt_card.layout.addWidget(QLabel("✏️ Image Prompt"))
        self.prompt = QTextEdit()
        self.prompt.setMaximumHeight(110)
        self.prompt.setPlaceholderText(
            "A cinematic YouTube thumbnail showing a surprised person, "
            "bold text 'SHOCKING', dramatic lighting, high contrast…"
        )
        prompt_card.layout.addWidget(self.prompt)

        prompt_card.layout.addWidget(QLabel("🚫 Negative Prompt  (optional)"))
        self.negative = QLineEdit()
        self.negative.setPlaceholderText("blurry, watermark, text, ugly, deformed…")
        prompt_card.layout.addWidget(self.negative)
        left_lay.addWidget(prompt_card)

        # Settings card
        settings_card = Card()

        settings_card.layout.addWidget(QLabel("🤖 Provider"))
        self.provider_combo = QComboBox()
        self.provider_combo.setFixedHeight(36)
        for p in IMAGE_PROVIDERS:
            self.provider_combo.addItem(p["label"], p["key"])
        settings_card.layout.addWidget(self.provider_combo)

        settings_card.layout.addWidget(QLabel("📐 Size / Aspect Ratio"))
        self.size_combo = QComboBox()
        self.size_combo.setFixedHeight(36)
        for label in IMAGE_SIZES.keys():
            self.size_combo.addItem(label, label)
        self.size_combo.setCurrentIndex(1)   # default landscape
        settings_card.layout.addWidget(self.size_combo)

        settings_card.layout.addWidget(QLabel("🎨 Style Preset"))
        self.style_combo = QComboBox()
        self.style_combo.setFixedHeight(36)
        for s in IMAGE_STYLE_PRESETS:
            self.style_combo.addItem(s)
        settings_card.layout.addWidget(self.style_combo)

        count_row = QHBoxLayout()
        count_row.addWidget(QLabel("# Images:"))
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 4)
        self.count_spin.setValue(2)
        self.count_spin.setFixedHeight(34)
        count_row.addWidget(self.count_spin)
        count_row.addStretch()
        settings_card.layout.addLayout(count_row)
        left_lay.addWidget(settings_card)

        # Generate button
        self.gen_btn = QPushButton("⚡ Generate Images")
        self.gen_btn.setObjectName("primary")
        self.gen_btn.setFixedHeight(46)
        self.gen_btn.clicked.connect(self._generate)
        left_lay.addWidget(self.gen_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.hide()
        left_lay.addWidget(self.progress_bar)

        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("caption")
        self.status_lbl.setWordWrap(True)
        left_lay.addWidget(self.status_lbl)
        left_lay.addStretch()

        splitter.addWidget(left)

        # ── RIGHT: Gallery ──────────────────────────────
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(8, 16, 16, 16)
        right_lay.setSpacing(8)

        gallery_header = QHBoxLayout()
        gallery_title = QLabel("Generated Images")
        gallery_title.setObjectName("h2")
        gallery_header.addWidget(gallery_title)
        gallery_header.addStretch()
        clear_btn = QPushButton("🗑 Clear Gallery")
        clear_btn.setObjectName("ghost")
        clear_btn.setFixedHeight(32)
        clear_btn.clicked.connect(self._clear_gallery)
        gallery_header.addWidget(clear_btn)
        right_lay.addLayout(gallery_header)

        self.gallery_scroll = QScrollArea()
        self.gallery_scroll.setWidgetResizable(True)
        self.gallery_scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.gallery_widget = QWidget()
        self.gallery_layout = QGridLayout(self.gallery_widget)
        self.gallery_layout.setSpacing(12)
        self.gallery_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.gallery_scroll.setWidget(self.gallery_widget)

        self._empty_lbl = QLabel("✨ Generated images will appear here")
        self._empty_lbl.setObjectName("subtitle")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gallery_layout.addWidget(self._empty_lbl, 0, 0, 1, 2)

        right_lay.addWidget(self.gallery_scroll)
        splitter.addWidget(right)
        splitter.setSizes([370, 700])

        layout.addWidget(splitter)

    def _generate(self):
        prompt = self.prompt.toPlainText().strip()
        if not prompt:
            self.status_lbl.setText("⚠️ Please enter an image prompt")
            return

        provider_key = self.provider_combo.currentData()
        provider = next((p for p in IMAGE_PROVIDERS if p["key"] == provider_key), None)
        api_key = self.config.get(provider["config_key"], "") if provider else ""
        if not api_key and provider_key not in ("dalle3",):
            self.status_lbl.setText(
                f"⚠️ API key required. Go to AI Settings → Media API Keys."
            )
        if not api_key and provider_key == "dalle3":
            api_key = self.config.get("openai_api_key", "")
        if not api_key:
            self.status_lbl.setText("⚠️ API key not configured for this provider")
            return

        if self._worker and self._worker.isRunning():
            return

        self.gen_btn.setEnabled(False)
        self.progress_bar.show()
        self.status_lbl.setText("⏳ Generating images…")

        self._worker = ImageGenerationWorker(
            provider_key=provider_key,
            prompt=prompt,
            config=self.config,
            negative_prompt=self.negative.text().strip(),
            size_key=self.size_combo.currentData(),
            style_preset=self.style_combo.currentText(),
            n=self.count_spin.value(),
        )
        self._worker.images_ready.connect(self._on_images_ready)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._on_done)
        self._worker.start()

    def _on_images_ready(self, images: list):
        # Remove empty label
        if self._empty_lbl.isVisible():
            self._empty_lbl.hide()

        provider = next(
            (p for p in IMAGE_PROVIDERS if p["key"] == self.provider_combo.currentData()),
            {"label": "AI"}
        )

        total = self.gallery_layout.count() - (0 if self._empty_lbl.isHidden() else 1)
        row_offset = (total) // 2
        for i, img_bytes in enumerate(images):
            idx = total + i
            card = ImageResultCard(
                img_bytes,
                self.prompt.toPlainText().strip(),
                provider["label"],
                str(self.config.thumbnails_dir),
            )
            card.use_as_ref.connect(self.use_image_as_ref.emit)
            self.gallery_layout.addWidget(card, idx // 2, idx % 2)

        self.status_lbl.setText(f"✅ {len(images)} image(s) generated")

    def _on_error(self, msg: str):
        self.status_lbl.setText(f"❌ {msg}")

    def _on_done(self):
        self.gen_btn.setEnabled(True)
        self.progress_bar.hide()

    def _clear_gallery(self):
        while self.gallery_layout.count():
            item = self.gallery_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._empty_lbl = QLabel("✨ Generated images will appear here")
        self._empty_lbl.setObjectName("subtitle")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gallery_layout.addWidget(self._empty_lbl, 0, 0, 1, 2)


# ─────────────────────────────────────────────────────────
#  VIDEO GENERATOR TAB
# ─────────────────────────────────────────────────────────

class RefImageDropZone(QLabel):
    """Drag & drop zone for reference images."""
    image_dropped = Signal(bytes)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._img_bytes: Optional[bytes] = None
        self.setText("🖼️\nDrop reference image\nor click to browse")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(160, 90)
        self.setStyleSheet(
            "background: #13131C; border: 2px dashed #3A3A5A; "
            "border-radius: 8px; color: #6060A0; font-size: 11px;"
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Reference Image", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if path:
            with open(path, "rb") as f:
                self._set_image(f.read())
        super().mousePressEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() or event.mimeData().hasImage():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path and os.path.isfile(path):
                    with open(path, "rb") as f:
                        self._set_image(f.read())
                    break
        event.acceptProposedAction()

    def _set_image(self, data: bytes):
        self._img_bytes = data
        pix = QPixmap()
        pix.loadFromData(data)
        if not pix.isNull():
            self.setPixmap(
                pix.scaled(160, 90,
                           Qt.AspectRatioMode.KeepAspectRatio,
                           Qt.TransformationMode.SmoothTransformation)
            )
        self.image_dropped.emit(data)

    def set_image_bytes(self, data: bytes):
        self._set_image(data)

    def clear_image(self):
        self._img_bytes = None
        self.clear()
        self.setText("🖼️\nDrop reference image\nor click to browse")

    def get_image_bytes(self) -> Optional[bytes]:
        return self._img_bytes


class VideoGeneratorTab(QWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self._submit_worker: Optional[VideoSubmitWorker] = None
        self._job_cards: Dict[str, VideoJobCard] = {}   # task_id → card
        self._active_jobs: List[Dict[str, Any]] = []     # live task_info list
        self._poll_workers: List[Any] = []               # keep poll workers alive
        self._dl_workers: List[Any] = []                 # keep download workers alive
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_all_jobs)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── LEFT: Controls ──────────────────────────────
        left = QWidget()
        left.setFixedWidth(380)
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(16, 16, 8, 16)
        left_lay.setSpacing(12)

        # Prompt card
        prompt_card = Card()
        prompt_card.layout.addWidget(QLabel("🎬 Video Prompt"))
        self.prompt = QTextEdit()
        self.prompt.setMaximumHeight(120)
        self.prompt.setPlaceholderText(
            "A cinematic shot of a glowing city at night, "
            "camera slowly zooming out, 8K, ultra detailed…"
        )
        prompt_card.layout.addWidget(self.prompt)
        left_lay.addWidget(prompt_card)

        # Reference image
        ref_card = Card()
        ref_header = QHBoxLayout()
        ref_header.addWidget(QLabel("🖼️ Reference Image  (optional)"))
        ref_header.addStretch()
        clear_ref_btn = QPushButton("✕")
        clear_ref_btn.setObjectName("ghost")
        clear_ref_btn.setFixedSize(24, 24)
        clear_ref_btn.clicked.connect(self._clear_ref)
        ref_header.addWidget(clear_ref_btn)
        ref_card.layout.addLayout(ref_header)

        self.ref_zone = RefImageDropZone()
        ref_card.layout.addWidget(self.ref_zone, alignment=Qt.AlignmentFlag.AlignLeft)
        left_lay.addWidget(ref_card)

        # Settings
        settings_card = Card()
        settings_card.layout.addWidget(QLabel("🤖 Video Provider"))
        self.provider_combo = QComboBox()
        self.provider_combo.setFixedHeight(36)
        for p in VIDEO_PROVIDERS:
            self.provider_combo.addItem(p["label"], p["key"])
        self.provider_combo.currentIndexChanged.connect(self._on_provider_change)
        settings_card.layout.addWidget(self.provider_combo)

        dur_ratio_row = QHBoxLayout()
        dur_ratio_row.setSpacing(10)
        dur_col = QVBoxLayout()
        dur_col.addWidget(QLabel("⏱ Duration"))
        self.duration_combo = QComboBox()
        self.duration_combo.setFixedHeight(34)
        dur_col.addWidget(self.duration_combo)
        dur_ratio_row.addLayout(dur_col)

        ratio_col = QVBoxLayout()
        ratio_col.addWidget(QLabel("📐 Aspect Ratio"))
        self.ratio_combo = QComboBox()
        self.ratio_combo.setFixedHeight(34)
        for r in VIDEO_ASPECT_RATIOS:
            self.ratio_combo.addItem(r, r)
        ratio_col.addWidget(self.ratio_combo)
        dur_ratio_row.addLayout(ratio_col)
        settings_card.layout.addLayout(dur_ratio_row)
        left_lay.addWidget(settings_card)

        # Generate button
        self.gen_btn = QPushButton("🎬 Generate Video")
        self.gen_btn.setObjectName("primary")
        self.gen_btn.setFixedHeight(46)
        self.gen_btn.clicked.connect(self._submit)
        left_lay.addWidget(self.gen_btn)

        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("caption")
        self.status_lbl.setWordWrap(True)
        left_lay.addWidget(self.status_lbl)

        info_lbl = QLabel(
            "💡 Videos are generated asynchronously.\n"
            "Jobs auto-poll every 15 seconds."
        )
        info_lbl.setObjectName("caption")
        info_lbl.setWordWrap(True)
        left_lay.addWidget(info_lbl)
        left_lay.addStretch()

        splitter.addWidget(left)

        # ── RIGHT: Job Queue ────────────────────────────
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(8, 16, 16, 16)
        right_lay.setSpacing(8)

        queue_header = QHBoxLayout()
        queue_title = QLabel("Video Generation Queue")
        queue_title.setObjectName("h2")
        queue_header.addWidget(queue_title)
        queue_header.addStretch()

        poll_btn = QPushButton("🔄 Refresh All")
        poll_btn.setObjectName("ghost")
        poll_btn.setFixedHeight(32)
        poll_btn.clicked.connect(self._poll_all_jobs)
        queue_header.addWidget(poll_btn)

        clear_queue_btn = QPushButton("🗑 Clear Done")
        clear_queue_btn.setObjectName("ghost")
        clear_queue_btn.setFixedHeight(32)
        clear_queue_btn.clicked.connect(self._clear_done)
        queue_header.addWidget(clear_queue_btn)

        right_lay.addLayout(queue_header)

        self.jobs_scroll = QScrollArea()
        self.jobs_scroll.setWidgetResizable(True)
        self.jobs_scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.jobs_widget = QWidget()
        self.jobs_layout = QVBoxLayout(self.jobs_widget)
        self.jobs_layout.setContentsMargins(0, 0, 0, 0)
        self.jobs_layout.setSpacing(10)

        self._empty_jobs_lbl = QLabel("🎬 Generated videos will appear here")
        self._empty_jobs_lbl.setObjectName("subtitle")
        self._empty_jobs_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.jobs_layout.addWidget(self._empty_jobs_lbl)
        self.jobs_layout.addStretch()

        self.jobs_scroll.setWidget(self.jobs_widget)
        right_lay.addWidget(self.jobs_scroll)

        splitter.addWidget(right)
        splitter.setSizes([380, 690])
        layout.addWidget(splitter)

        # Init duration options for first provider
        self._on_provider_change()

    def _on_provider_change(self):
        provider_key = self.provider_combo.currentData()
        provider = next((p for p in VIDEO_PROVIDERS if p["key"] == provider_key), None)
        self.duration_combo.clear()
        if provider:
            for d in provider.get("durations", ["5"]):
                self.duration_combo.addItem(f"{d}s", d)

    def _clear_ref(self):
        self.ref_zone.clear_image()

    def _submit(self):
        prompt = self.prompt.toPlainText().strip()
        if not prompt:
            self.status_lbl.setText("⚠️ Please enter a video prompt")
            return

        provider_key = self.provider_combo.currentData()
        provider = next((p for p in VIDEO_PROVIDERS if p["key"] == provider_key), None)
        api_key = self.config.get(provider["config_key"], "") if provider else ""
        if not api_key:
            self.status_lbl.setText(f"⚠️ API key not configured. Go to AI Settings.")
            return

        if self._submit_worker and self._submit_worker.isRunning():
            self.status_lbl.setText("⏳ Previous job still submitting…")
            return

        self.gen_btn.setEnabled(False)
        self.status_lbl.setText("⏳ Submitting video job…")

        self._submit_worker = VideoSubmitWorker(
            provider_key=provider_key,
            prompt=prompt,
            config=self.config,
            duration=self.duration_combo.currentData() or "5",
            aspect_ratio=self.ratio_combo.currentData() or "16:9",
            image_bytes=self.ref_zone.get_image_bytes(),
        )
        self._submit_worker.job_submitted.connect(self._on_job_submitted)
        self._submit_worker.error.connect(
            lambda m: (self.status_lbl.setText(f"❌ {m}"), self.gen_btn.setEnabled(True))
        )
        self._submit_worker.finished.connect(lambda: self.gen_btn.setEnabled(True))
        self._submit_worker.start()

    def _on_job_submitted(self, task_info: Dict[str, Any]):
        task_id = task_info.get("task_id", str(uuid.uuid4()))
        task_info["task_id"] = task_id
        self._active_jobs.append(task_info)

        # Remove empty label
        if self._empty_jobs_lbl.isVisible():
            self._empty_jobs_lbl.hide()

        card = VideoJobCard(task_info)
        card.download_requested.connect(self._download_video)
        self._job_cards[task_id] = card
        # Insert before stretch
        count = self.jobs_layout.count()
        self.jobs_layout.insertWidget(count - 1, card)

        self.status_lbl.setText(f"✅ Job submitted: {task_id[:12]}…")

        # Start auto-polling
        if not self._poll_timer.isActive():
            self._poll_timer.start(15000)  # every 15 seconds

    def _poll_all_jobs(self):
        pending = [j for j in self._active_jobs
                   if j.get("status") not in ("completed", "failed")]
        if not pending:
            self._poll_timer.stop()
            return
        for task_info in pending:
            worker = VideoPollWorker(task_info, self.config)
            self._poll_workers.append(worker)
            worker.status_updated.connect(self._on_status_updated)
            worker.finished.connect(lambda w=worker: self._poll_workers.remove(w) if w in self._poll_workers else None)
            worker.start()

    def _on_status_updated(self, updated: Dict[str, Any]):
        task_id = updated.get("task_id", "")
        # Update in active jobs list
        for i, j in enumerate(self._active_jobs):
            if j.get("task_id") == task_id:
                self._active_jobs[i] = updated
                break
        # Update card
        card = self._job_cards.get(task_id)
        if card:
            card.update_status(updated)

    def _download_video(self, task_info: Dict[str, Any]):
        url = task_info.get("video_url", "")
        if not url:
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = os.path.join(
            str(self.config.exports_dir), f"ai_video_{ts}.mp4"
        )
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Video", default_name, "MP4 Video (*.mp4)"
        )
        if not path:
            return

        task_id = task_info.get("task_id", "")
        card = self._job_cards.get(task_id)
        if card:
            card.dl_btn.setEnabled(False)
            card.dl_btn.setText("⬇️ Downloading…")

        dl_worker = VideoDownloadWorker(url, path)
        self._dl_workers.append(dl_worker)
        dl_worker.done.connect(lambda p: self._on_download_done(p, task_id))
        dl_worker.error.connect(lambda m: self.status_lbl.setText(f"❌ Download: {m}"))
        dl_worker.finished.connect(lambda w=dl_worker: self._dl_workers.remove(w) if w in self._dl_workers else None)
        dl_worker.start()

    def _on_download_done(self, path: str, task_id: str):
        self.status_lbl.setText(f"✅ Saved: {path}")
        card = self._job_cards.get(task_id)
        if card:
            card.dl_btn.setText("✅ Saved")
        import os as _os
        _os.startfile(_os.path.dirname(path))

    def _clear_done(self):
        done_ids = [j["task_id"] for j in self._active_jobs
                    if j.get("status") in ("completed", "failed")]
        for tid in done_ids:
            card = self._job_cards.pop(tid, None)
            if card:
                card.deleteLater()
        self._active_jobs = [j for j in self._active_jobs
                              if j.get("status") not in ("completed", "failed")]

    def receive_ref_image(self, img_bytes: bytes):
        """Receive a reference image forwarded from the Image tab."""
        self.ref_zone.set_image_bytes(img_bytes)


# ─────────────────────────────────────────────────────────
#  MAIN PAGE
# ─────────────────────────────────────────────────────────

class MediaGeneratorPage(QWidget):
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

        header = SectionHeader(
            "AI Media Generator",
            "Generate images with DALL-E/FLUX and videos with Kling, Hailuo, Runway & more."
        )
        layout.addWidget(header)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.image_tab = ImageGeneratorTab(self.config)
        self.video_tab = VideoGeneratorTab(self.config)

        # Wire "Use as Ref" from image gallery → video tab
        self.image_tab.use_image_as_ref.connect(self._forward_ref_to_video)

        self.tabs.addTab(self.image_tab, "🖼️  Image Generator")
        self.tabs.addTab(self.video_tab, "🎬  Video Generator")

        content = QWidget()
        content.setObjectName("content_area")
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.addWidget(self.tabs)
        layout.addWidget(content, 1)

    def _forward_ref_to_video(self, img_bytes: bytes):
        self.video_tab.receive_ref_image(img_bytes)
        self.tabs.setCurrentIndex(1)   # switch to video tab

    def refresh(self):
        pass
