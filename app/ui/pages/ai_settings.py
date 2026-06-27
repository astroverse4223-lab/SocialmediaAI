from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QSlider, QDoubleSpinBox, QSpinBox,
    QScrollArea, QFrame, QGroupBox, QCheckBox, QListWidget,
    QListWidgetItem
)
from PySide6.QtCore import Qt, Signal

from app.ui.components.cards import SectionHeader, Card
from app.core.ai_providers import (
    OPENAI_MODELS, CLAUDE_MODELS, GEMINI_MODELS,
    OllamaProvider
)


class AISettingsPage(QWidget):
    settings_changed = Signal()

    def __init__(self, config, db, parent=None):
        super().__init__(parent)
        self.config = config
        self.db = db
        self.setObjectName("content_area")
        self._setup_ui()
        self._load_values()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = SectionHeader(
            "AI Settings",
            "Configure your AI provider, models, and generation parameters."
        )
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content.setObjectName("content_area")
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(28, 20, 28, 28)
        c_lay.setSpacing(20)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        # ── Provider Selection ──────────────────────────
        provider_card = Card()
        provider_card.layout.addWidget(QLabel("🤖 AI Provider"))
        self.provider_combo = QComboBox()
        self.provider_combo.setFixedHeight(40)
        for label, key in [
            ("OpenAI (GPT-4o, GPT-4, etc.)", "openai"),
            ("Anthropic Claude (Claude 3.5)", "claude"),
            ("Google Gemini (Gemini 1.5 Pro)", "gemini"),
            ("Ollama (Local Models)", "ollama"),
        ]:
            self.provider_combo.addItem(label, key)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_change)
        provider_card.layout.addWidget(self.provider_combo)
        c_lay.addWidget(provider_card)

        # ── OpenAI Settings ─────────────────────────────
        self.openai_card = Card()
        self.openai_card.layout.addWidget(QLabel("🔑 OpenAI API Key"))
        self.openai_key = QLineEdit()
        self.openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key.setPlaceholderText("sk-…")
        self.openai_card.layout.addWidget(self.openai_key)

        self.openai_card.layout.addWidget(QLabel("📦 OpenAI Model"))
        self.openai_model = QComboBox()
        self.openai_model.setFixedHeight(38)
        for m in OPENAI_MODELS:
            self.openai_model.addItem(m, m)
        self.openai_card.layout.addWidget(self.openai_model)
        c_lay.addWidget(self.openai_card)

        # ── Claude Settings ─────────────────────────────
        self.claude_card = Card()
        self.claude_card.layout.addWidget(QLabel("🔑 Anthropic API Key"))
        self.claude_key = QLineEdit()
        self.claude_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.claude_key.setPlaceholderText("sk-ant-…")
        self.claude_card.layout.addWidget(self.claude_key)

        self.claude_card.layout.addWidget(QLabel("📦 Claude Model"))
        self.claude_model = QComboBox()
        self.claude_model.setFixedHeight(38)
        for m in CLAUDE_MODELS:
            self.claude_model.addItem(m, m)
        self.claude_card.layout.addWidget(self.claude_model)
        c_lay.addWidget(self.claude_card)

        # ── Gemini Settings ─────────────────────────────
        self.gemini_card = Card()
        self.gemini_card.layout.addWidget(QLabel("🔑 Google AI API Key"))
        self.gemini_key = QLineEdit()
        self.gemini_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.gemini_key.setPlaceholderText("AIza…")
        self.gemini_card.layout.addWidget(self.gemini_key)

        self.gemini_card.layout.addWidget(QLabel("📦 Gemini Model"))
        self.gemini_model = QComboBox()
        self.gemini_model.setFixedHeight(38)
        for m in GEMINI_MODELS:
            self.gemini_model.addItem(m, m)
        self.gemini_card.layout.addWidget(self.gemini_model)
        c_lay.addWidget(self.gemini_card)

        # ── Ollama Settings ─────────────────────────────
        self.ollama_card = Card()
        self.ollama_card.layout.addWidget(QLabel("🌐 Ollama Base URL"))
        self.ollama_url = QLineEdit()
        self.ollama_url.setPlaceholderText("http://localhost:11434")
        self.ollama_card.layout.addWidget(self.ollama_url)

        self.ollama_card.layout.addWidget(QLabel("📦 Ollama Model"))
        self.ollama_model_input = QLineEdit()
        self.ollama_model_input.setPlaceholderText("llama3.2")
        self.ollama_card.layout.addWidget(self.ollama_model_input)

        check_btn = QPushButton("🔍 Check Connection & List Models")
        check_btn.setFixedHeight(36)
        check_btn.clicked.connect(self._check_ollama)
        self.ollama_card.layout.addWidget(check_btn)

        self.ollama_models_list = QListWidget()
        self.ollama_models_list.setMaximumHeight(100)
        self.ollama_models_list.setVisible(False)
        self.ollama_card.layout.addWidget(self.ollama_models_list)
        self.ollama_models_list.itemClicked.connect(
            lambda item: self.ollama_model_input.setText(item.text())
        )

        self.ollama_status = QLabel("")
        self.ollama_status.setObjectName("caption")
        self.ollama_card.layout.addWidget(self.ollama_status)
        c_lay.addWidget(self.ollama_card)

        # ── Generation Parameters ───────────────────────
        params_card = Card()
        params_card.layout.addWidget(QLabel("⚙️ Generation Parameters"))

        # Temperature
        temp_row = QHBoxLayout()
        temp_row.addWidget(QLabel("Temperature:"))
        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(0, 100)
        self.temp_slider.setValue(70)
        self.temp_slider.valueChanged.connect(
            lambda v: self.temp_lbl.setText(f"{v / 100:.2f}")
        )
        temp_row.addWidget(self.temp_slider)
        self.temp_lbl = QLabel("0.70")
        self.temp_lbl.setFixedWidth(40)
        temp_row.addWidget(self.temp_lbl)
        params_card.layout.addLayout(temp_row)

        # Max tokens
        tok_row = QHBoxLayout()
        tok_row.addWidget(QLabel("Max Tokens:"))
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(256, 16000)
        self.max_tokens_spin.setValue(4096)
        self.max_tokens_spin.setSingleStep(256)
        self.max_tokens_spin.setFixedHeight(36)
        tok_row.addWidget(self.max_tokens_spin)
        tok_row.addStretch()
        params_card.layout.addLayout(tok_row)

        c_lay.addWidget(params_card)

        # ── Media Generation API Keys ───────────────────
        media_card = Card()
        media_card.layout.addWidget(QLabel("🎨 Media Generation API Keys"))

        media_note = QLabel(
            "These keys are used by the AI Media Generator for image & video generation."
        )
        media_note.setObjectName("subtitle")
        media_note.setWordWrap(True)
        media_card.layout.addWidget(media_note)

        media_card.layout.addWidget(QLabel("fal.ai API Key  (FLUX, Kling, MiniMax, Wan…)"))
        self.fal_key = QLineEdit()
        self.fal_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.fal_key.setPlaceholderText("fal-…")
        media_card.layout.addWidget(self.fal_key)

        media_card.layout.addWidget(QLabel("Stability AI API Key"))
        self.stability_key = QLineEdit()
        self.stability_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.stability_key.setPlaceholderText("sk-…")
        media_card.layout.addWidget(self.stability_key)

        media_card.layout.addWidget(QLabel("RunwayML API Key"))
        self.runway_key = QLineEdit()
        self.runway_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.runway_key.setPlaceholderText("key_…")
        media_card.layout.addWidget(self.runway_key)

        media_card.layout.addWidget(QLabel("Luma AI API Key"))
        self.luma_key = QLineEdit()
        self.luma_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.luma_key.setPlaceholderText("luma-…")
        media_card.layout.addWidget(self.luma_key)

        media_card.layout.addWidget(QLabel("Replicate API Key"))
        self.replicate_key = QLineEdit()
        self.replicate_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.replicate_key.setPlaceholderText("r8_…")
        media_card.layout.addWidget(self.replicate_key)

        c_lay.addWidget(media_card)

        # ── Save Button ─────────────────────────────────
        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("subtitle")
        c_lay.addWidget(self.status_lbl)

        save_btn = QPushButton("💾 Save Settings")
        save_btn.setObjectName("primary")
        save_btn.setFixedHeight(44)
        save_btn.clicked.connect(self._save)
        c_lay.addWidget(save_btn)

        test_btn = QPushButton("🧪 Test Connection")
        test_btn.setFixedHeight(36)
        test_btn.clicked.connect(self._test)
        c_lay.addWidget(test_btn)

        c_lay.addStretch()

    def _load_values(self):
        provider = self.config.get("ai_provider", "openai")
        for i in range(self.provider_combo.count()):
            if self.provider_combo.itemData(i) == provider:
                self.provider_combo.setCurrentIndex(i)
                break

        self.openai_key.setText(self.config.get("openai_api_key", ""))
        self.claude_key.setText(self.config.get("anthropic_api_key", ""))
        self.gemini_key.setText(self.config.get("gemini_api_key", ""))
        self.ollama_url.setText(self.config.get("ollama_base_url", "http://localhost:11434"))
        self.ollama_model_input.setText(self.config.get("ollama_model", "llama3.2"))

        # Media keys
        self.fal_key.setText(self.config.get("fal_api_key", ""))
        self.stability_key.setText(self.config.get("stability_api_key", ""))
        self.runway_key.setText(self.config.get("runway_api_key", ""))
        self.luma_key.setText(self.config.get("luma_api_key", ""))
        self.replicate_key.setText(self.config.get("replicate_api_key", ""))

        # Models
        self._set_combo(self.openai_model, self.config.get("ai_model", "gpt-4o"))
        self._set_combo(self.claude_model, self.config.get("ai_model", "claude-3-5-sonnet-20241022"))
        self._set_combo(self.gemini_model, self.config.get("ai_model", "gemini-1.5-pro"))

        temp = int(self.config.get("temperature", 0.7) * 100)
        self.temp_slider.setValue(temp)
        self.max_tokens_spin.setValue(self.config.get("max_tokens", 4096))

        self._on_provider_change()

    def _set_combo(self, combo, value):
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return

    def _on_provider_change(self):
        provider = self.provider_combo.currentData()
        self.openai_card.setVisible(provider == "openai")
        self.claude_card.setVisible(provider == "claude")
        self.gemini_card.setVisible(provider == "gemini")
        self.ollama_card.setVisible(provider == "ollama")

    def _save(self):
        provider = self.provider_combo.currentData()
        self.config.set("ai_provider", provider)
        self.config.set("openai_api_key", self.openai_key.text().strip())
        self.config.set("anthropic_api_key", self.claude_key.text().strip())
        self.config.set("gemini_api_key", self.gemini_key.text().strip())
        self.config.set("ollama_base_url", self.ollama_url.text().strip())
        self.config.set("ollama_model", self.ollama_model_input.text().strip())
        self.config.set("temperature", self.temp_slider.value() / 100)
        self.config.set("max_tokens", self.max_tokens_spin.value())
        # Media keys
        self.config.set("fal_api_key", self.fal_key.text().strip())
        self.config.set("stability_api_key", self.stability_key.text().strip())
        self.config.set("runway_api_key", self.runway_key.text().strip())
        self.config.set("luma_api_key", self.luma_key.text().strip())
        self.config.set("replicate_api_key", self.replicate_key.text().strip())

        model_map = {
            "openai": self.openai_model.currentData(),
            "claude": self.claude_model.currentData(),
            "gemini": self.gemini_model.currentData(),
        }
        self.config.set("ai_model", model_map.get(provider, "gpt-4o"))

        self.status_lbl.setText("✅ Settings saved successfully!")
        self.settings_changed.emit()

    def _test(self):
        from app.core.ai_providers import create_provider
        provider = create_provider(self.config)
        if not provider.is_available():
            self.status_lbl.setText("❌ Provider not available (check API key or connection)")
            return
        self.status_lbl.setText("⏳ Testing connection…")
        try:
            content, _, _ = provider.generate(
                "Reply with exactly: Connection OK",
                max_tokens=20, temperature=0
            )
            self.status_lbl.setText(f"✅ Connection successful: {content[:50]}")
        except Exception as e:
            self.status_lbl.setText(f"❌ Test failed: {e}")

    def _check_ollama(self):
        url = self.ollama_url.text().strip() or "http://localhost:11434"
        provider = OllamaProvider(base_url=url)
        if provider.is_available():
            models = provider.list_local_models()
            self.ollama_status.setText(f"✅ Connected — {len(models)} model(s) available")
            self.ollama_models_list.clear()
            for m in models:
                self.ollama_models_list.addItem(m)
            self.ollama_models_list.setVisible(bool(models))
        else:
            self.ollama_status.setText("❌ Cannot connect to Ollama. Is it running?")
            self.ollama_models_list.setVisible(False)

    def refresh(self):
        pass
