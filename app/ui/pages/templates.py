from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QComboBox, QScrollArea, QFrame,
    QSplitter, QListWidget, QListWidgetItem, QApplication
)
from PySide6.QtCore import Qt

from app.ui.components.cards import SectionHeader, Card
from app.ui.components.dialogs import ConfirmDialog


class TemplatesPage(QWidget):
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
            "Templates",
            "Manage AI prompt templates for custom content styles."
        )
        layout.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Left: Template list ─────────────────────────
        left = QWidget()
        left.setMinimumWidth(260)
        left.setMaximumWidth(340)
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(20, 16, 8, 20)
        left_lay.setSpacing(8)

        self.template_list = QListWidget()
        self.template_list.currentItemChanged.connect(self._on_select)
        left_lay.addWidget(self.template_list)

        btn_row = QHBoxLayout()
        new_btn = QPushButton("+ New")
        new_btn.setObjectName("primary")
        new_btn.setFixedHeight(34)
        new_btn.clicked.connect(self._new_template)
        del_btn = QPushButton("Delete")
        del_btn.setObjectName("danger")
        del_btn.setFixedHeight(34)
        del_btn.clicked.connect(self._delete_template)
        btn_row.addWidget(new_btn)
        btn_row.addWidget(del_btn)
        left_lay.addLayout(btn_row)

        splitter.addWidget(left)

        # ── Right: Template editor ──────────────────────
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(8, 16, 20, 20)
        right_lay.setSpacing(10)

        right_lay.addWidget(QLabel("Template Name"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., MrBeast Style Blog")
        right_lay.addWidget(self.name_input)

        right_lay.addWidget(QLabel("Content Type"))
        self.type_combo = QComboBox()
        self.type_combo.setFixedHeight(36)
        for t in ["blog", "social", "seo", "podcast", "summary", "custom"]:
            self.type_combo.addItem(t.title(), t)
        right_lay.addWidget(self.type_combo)

        right_lay.addWidget(QLabel("Description"))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Brief description of this template")
        right_lay.addWidget(self.desc_input)

        right_lay.addWidget(QLabel("System Prompt"))
        self.system_edit = QTextEdit()
        self.system_edit.setMaximumHeight(100)
        self.system_edit.setPlaceholderText("System instructions for the AI (tone, style, etc.)")
        right_lay.addWidget(self.system_edit)

        right_lay.addWidget(QLabel("Prompt Template (use {transcript} and {title} as placeholders)"))
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText(
            "Write a blog post in [style] about the following video:\n\n{transcript}"
        )
        right_lay.addWidget(self.prompt_edit)

        save_btn = QPushButton("💾 Save Template")
        save_btn.setObjectName("primary")
        save_btn.setFixedHeight(40)
        save_btn.clicked.connect(self._save_template)
        right_lay.addWidget(save_btn)

        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("caption")
        right_lay.addWidget(self.status_lbl)

        splitter.addWidget(right)
        splitter.setSizes([300, 600])

        content = QWidget()
        content.setObjectName("content_area")
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.addWidget(splitter)
        layout.addWidget(content, 1)

    def refresh(self):
        self.template_list.clear()
        templates = self.db.get_all_templates()
        for tmpl in templates:
            item = QListWidgetItem(
                ("🔒 " if tmpl.is_builtin else "📝 ") + tmpl.name
            )
            item.setData(Qt.ItemDataRole.UserRole, tmpl.id)
            item.setData(Qt.ItemDataRole.UserRole + 1, tmpl)
            self.template_list.addItem(item)

    def _on_select(self, current, previous):
        if not current:
            return
        tmpl = current.data(Qt.ItemDataRole.UserRole + 1)
        self.name_input.setText(tmpl.name)
        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) == tmpl.content_type:
                self.type_combo.setCurrentIndex(i)
        self.desc_input.setText(tmpl.description or "")
        self.system_edit.setPlainText(tmpl.system_prompt or "")
        self.prompt_edit.setPlainText(tmpl.user_prompt_template or "")

    def _new_template(self):
        self.template_list.clearSelection()
        self.name_input.clear()
        self.desc_input.clear()
        self.system_edit.clear()
        self.prompt_edit.clear()
        self.name_input.setFocus()

    def _save_template(self):
        name = self.name_input.text().strip()
        if not name:
            self.status_lbl.setText("❌ Template name is required")
            return
        self.db.save_template(
            name=name,
            content_type=self.type_combo.currentData(),
            user_prompt_template=self.prompt_edit.toPlainText(),
            system_prompt=self.system_edit.toPlainText(),
            description=self.desc_input.text().strip(),
        )
        self.status_lbl.setText("✅ Template saved!")
        self.refresh()

    def _delete_template(self):
        item = self.template_list.currentItem()
        if not item:
            return
        tmpl_id = item.data(Qt.ItemDataRole.UserRole)
        dlg = ConfirmDialog(
            "Delete Template", "Delete this template permanently?",
            danger=True, parent=self
        )
        if dlg.exec():
            self.db.delete_template(tmpl_id)
            self.refresh()
