from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QSpinBox, QLineEdit,
    QScrollArea, QFrame, QFileDialog
)
from PySide6.QtCore import Qt, Signal

from app.ui.components.cards import SectionHeader, Card


class PreferencesPage(QWidget):
    theme_changed = Signal(bool)   # True = dark

    def __init__(self, config, db, parent=None):
        super().__init__(parent)
        self.config = config
        self.db = db
        self.setObjectName("content_area")
        self._setup_ui()
        self._load()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = SectionHeader("Preferences", "Customize the application behaviour and appearance.")
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

        # ── Appearance ──────────────────────────────────
        app_card = Card()
        app_card.layout.addWidget(QLabel("🎨 Appearance"))

        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.setFixedHeight(38)
        self.theme_combo.addItem("Dark", "dark")
        self.theme_combo.addItem("Light", "light")
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch()
        app_card.layout.addLayout(theme_row)
        c_lay.addWidget(app_card)

        # ── Auto-Save ───────────────────────────────────
        save_card = Card()
        save_card.layout.addWidget(QLabel("💾 Auto-Save"))

        self.auto_save_chk = QCheckBox("Enable auto-save")
        save_card.layout.addWidget(self.auto_save_chk)

        interval_row = QHBoxLayout()
        interval_row.addWidget(QLabel("Auto-save interval (seconds):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(10, 300)
        self.interval_spin.setValue(30)
        self.interval_spin.setFixedHeight(36)
        interval_row.addWidget(self.interval_spin)
        interval_row.addStretch()
        save_card.layout.addLayout(interval_row)
        c_lay.addWidget(save_card)

        # ── Export Directory ────────────────────────────
        exp_card = Card()
        exp_card.layout.addWidget(QLabel("📂 Default Export Directory"))
        exp_row = QHBoxLayout()
        self.export_dir_lbl = QLabel("")
        self.export_dir_lbl.setStyleSheet("color: #9090BB;")
        self.export_dir_lbl.setWordWrap(True)
        exp_row.addWidget(self.export_dir_lbl, 1)
        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedHeight(36)
        browse_btn.clicked.connect(self._browse)
        exp_row.addWidget(browse_btn)
        exp_card.layout.addLayout(exp_row)
        c_lay.addWidget(exp_card)

        # ── Language ────────────────────────────────────
        lang_card = Card()
        lang_card.layout.addWidget(QLabel("🌐 Preferred Transcript Language"))
        self.lang_combo = QComboBox()
        self.lang_combo.setFixedHeight(38)
        for label, code in [
            ("English", "en"), ("Spanish", "es"), ("French", "fr"),
            ("German", "de"), ("Portuguese", "pt"), ("Italian", "it"),
            ("Japanese", "ja"), ("Korean", "ko"), ("Chinese", "zh"),
            ("Arabic", "ar"), ("Hindi", "hi"),
        ]:
            self.lang_combo.addItem(label, code)
        lang_card.layout.addWidget(self.lang_combo)
        c_lay.addWidget(lang_card)

        # ── Data Management ─────────────────────────────
        data_card = Card()
        data_card.layout.addWidget(QLabel("🗄️ Data Management"))
        open_dir_btn = QPushButton("📂 Open App Data Folder")
        open_dir_btn.setFixedHeight(36)
        open_dir_btn.clicked.connect(self._open_data_dir)
        data_card.layout.addWidget(open_dir_btn)

        stats_lbl = QLabel(
            f"Database: {self.config.db_path}"
        )
        stats_lbl.setObjectName("caption")
        stats_lbl.setWordWrap(True)
        data_card.layout.addWidget(stats_lbl)
        c_lay.addWidget(data_card)

        # ── Save ────────────────────────────────────────
        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("subtitle")
        c_lay.addWidget(self.status_lbl)

        save_btn = QPushButton("💾 Save Preferences")
        save_btn.setObjectName("primary")
        save_btn.setFixedHeight(44)
        save_btn.clicked.connect(self._save)
        c_lay.addWidget(save_btn)
        c_lay.addStretch()

    def _load(self):
        theme = self.config.get("theme", "dark")
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == theme:
                self.theme_combo.setCurrentIndex(i)
                break
        self.auto_save_chk.setChecked(self.config.get("auto_save", True))
        self.interval_spin.setValue(self.config.get("auto_save_interval", 30))
        self.export_dir_lbl.setText(self.config.get("export_dir", ""))
        lang = self.config.get("language", "en")
        for i in range(self.lang_combo.count()):
            if self.lang_combo.itemData(i) == lang:
                self.lang_combo.setCurrentIndex(i)
                break

    def _save(self):
        theme = self.theme_combo.currentData()
        old_theme = self.config.get("theme", "dark")
        self.config.set("theme", theme)
        self.config.set("auto_save", self.auto_save_chk.isChecked())
        self.config.set("auto_save_interval", self.interval_spin.value())
        self.config.set("language", self.lang_combo.currentData())
        self.status_lbl.setText("✅ Preferences saved!")
        if theme != old_theme:
            self.theme_changed.emit(theme == "dark")

    def _browse(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select Export Directory",
            self.config.get("export_dir", "")
        )
        if path:
            self.config.set("export_dir", path)
            self.export_dir_lbl.setText(path)

    def _open_data_dir(self):
        import os
        os.startfile(str(self.config.app_dir))

    def refresh(self):
        self._load()
