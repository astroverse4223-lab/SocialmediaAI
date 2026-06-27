import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QListWidget, QListWidgetItem, QCheckBox,
    QScrollArea, QFrame, QFileDialog, QApplication,
    QProgressBar, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QThread

from app.ui.components.cards import SectionHeader, Card


class ExportWorker(QThread):
    done = Signal(str)
    error = Signal(str)

    def __init__(self, fmt, content_map, title, out_dir, metadata=None):
        super().__init__()
        self.fmt = fmt
        self.content_map = content_map
        self.title = title
        self.out_dir = out_dir
        self.metadata = metadata or {}

    def run(self):
        from app.core import exporter
        try:
            fmt = self.fmt.upper()
            if fmt == "TXT":
                path = exporter.export_txt(self.content_map, self.title, self.out_dir)
            elif fmt == "MARKDOWN" or fmt == "MD":
                path = exporter.export_markdown(self.content_map, self.title, self.out_dir)
            elif fmt == "JSON":
                path = exporter.export_json(self.content_map, self.title, self.out_dir, self.metadata)
            elif fmt == "HTML":
                path = exporter.export_html(self.content_map, self.title, self.out_dir)
            elif fmt == "DOCX":
                path = exporter.export_docx(self.content_map, self.title, self.out_dir)
            elif fmt == "PDF":
                path = exporter.export_pdf(self.content_map, self.title, self.out_dir)
            else:
                self.error.emit(f"Unknown format: {fmt}")
                return
            self.done.emit(path)
        except Exception as e:
            self.error.emit(str(e))


class ExportCenterPage(QWidget):
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
            "Export Center",
            "Export your generated content in multiple formats."
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

        # ── Project Selection ───────────────────────────
        proj_card = Card()
        proj_card.layout.addWidget(QLabel("📁 Select Project to Export"))
        self.project_combo = QComboBox()
        self.project_combo.setFixedHeight(40)
        self.project_combo.currentIndexChanged.connect(self._load_content_list)
        proj_card.layout.addWidget(self.project_combo)
        c_lay.addWidget(proj_card)

        # ── Content Selection ───────────────────────────
        select_card = Card()
        select_header = QHBoxLayout()
        select_header.addWidget(QLabel("📄 Select Content to Export"))
        select_header.addStretch()
        sel_all = QPushButton("Select All")
        sel_all.setObjectName("ghost")
        sel_all.setFixedHeight(28)
        sel_all.clicked.connect(self._select_all)
        sel_none = QPushButton("Deselect All")
        sel_none.setObjectName("ghost")
        sel_none.setFixedHeight(28)
        sel_none.clicked.connect(self._deselect_all)
        select_header.addWidget(sel_all)
        select_header.addWidget(sel_none)
        select_card.layout.addLayout(select_header)

        self.content_list = QListWidget()
        self.content_list.setMaximumHeight(220)
        select_card.layout.addWidget(self.content_list)
        c_lay.addWidget(select_card)

        # ── Format Selection ────────────────────────────
        fmt_card = Card()
        fmt_card.layout.addWidget(QLabel("📦 Export Format"))
        fmt_row = QHBoxLayout()
        self.fmt_btns = {}
        for fmt in ["TXT", "Markdown", "HTML", "JSON", "DOCX", "PDF"]:
            btn = QPushButton(fmt)
            btn.setCheckable(True)
            btn.setFixedHeight(36)
            btn.clicked.connect(lambda _, f=fmt: self._on_fmt_select(f))
            self.fmt_btns[fmt] = btn
            fmt_row.addWidget(btn)
        fmt_card.layout.addLayout(fmt_row)
        self.fmt_btns["TXT"].setChecked(True)
        self._selected_fmt = "TXT"
        c_lay.addWidget(fmt_card)

        # ── Output Directory ────────────────────────────
        dir_card = Card()
        dir_card.layout.addWidget(QLabel("📂 Output Directory"))
        dir_row = QHBoxLayout()
        self.dir_lbl = QLabel(self.config.get("export_dir", ""))
        self.dir_lbl.setStyleSheet("color: #9090BB;")
        dir_row.addWidget(self.dir_lbl, 1)
        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedHeight(36)
        browse_btn.clicked.connect(self._browse_dir)
        dir_row.addWidget(browse_btn)
        dir_card.layout.addLayout(dir_row)
        c_lay.addWidget(dir_card)

        # ── Export Button ───────────────────────────────
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(8)
        self.progress.hide()
        c_lay.addWidget(self.progress)

        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("subtitle")
        c_lay.addWidget(self.status_lbl)

        export_btn = QPushButton("📤 Export Now")
        export_btn.setObjectName("primary")
        export_btn.setFixedHeight(48)
        export_btn.clicked.connect(self._export)
        c_lay.addWidget(export_btn)

        open_dir_btn = QPushButton("📂 Open Export Folder")
        open_dir_btn.setObjectName("ghost")
        open_dir_btn.clicked.connect(self._open_dir)
        c_lay.addWidget(open_dir_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        c_lay.addStretch()

    def refresh(self):
        self.project_combo.clear()
        for p in self.db.get_all_projects(limit=100):
            self.project_combo.addItem(p.title[:50], p.id)

    def _load_content_list(self):
        self.content_list.clear()
        project_id = self.project_combo.currentData()
        if not project_id:
            return
        items = self.db.get_all_content_for_project(project_id)
        for item in items:
            label = item.content_type.replace("_", " ").title()
            li = QListWidgetItem(f"  {label}")
            li.setData(Qt.ItemDataRole.UserRole, item.content_type)
            li.setData(Qt.ItemDataRole.UserRole + 1, item.content or "")
            li.setCheckState(Qt.CheckState.Checked)
            self.content_list.addItem(li)

    def _select_all(self):
        for i in range(self.content_list.count()):
            self.content_list.item(i).setCheckState(Qt.CheckState.Checked)

    def _deselect_all(self):
        for i in range(self.content_list.count()):
            self.content_list.item(i).setCheckState(Qt.CheckState.Unchecked)

    def _on_fmt_select(self, fmt: str):
        self._selected_fmt = fmt
        for f, btn in self.fmt_btns.items():
            btn.setChecked(f == fmt)

    def _browse_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Select Export Directory",
                                                 self.config.get("export_dir", ""))
        if path:
            self.config.set("export_dir", path)
            self.dir_lbl.setText(path)

    def _export(self):
        project_id = self.project_combo.currentData()
        project = self.db.get_project(project_id) if project_id else None
        if not project:
            self.status_lbl.setText("❌ No project selected")
            return

        content_map = {}
        for i in range(self.content_list.count()):
            item = self.content_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                key = item.data(Qt.ItemDataRole.UserRole)
                content = item.data(Qt.ItemDataRole.UserRole + 1)
                if content:
                    content_map[key] = content

        if not content_map:
            self.status_lbl.setText("❌ No content selected")
            return

        out_dir = self.config.get("export_dir", "")
        if not out_dir or not os.path.isdir(out_dir):
            self.status_lbl.setText("❌ Invalid output directory")
            return

        self.progress.show()
        self.status_lbl.setText("⏳ Exporting…")

        self._worker = ExportWorker(
            self._selected_fmt, content_map, project.title, out_dir,
            metadata={"url": project.youtube_url, "channel": project.channel or ""}
        )
        self._worker.done.connect(self._on_done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_done(self, path: str):
        self.progress.hide()
        self.status_lbl.setText(f"✅ Exported to: {path}")
        project_id = self.project_combo.currentData()
        if project_id:
            self.db.save_export(
                project_id=project_id,
                fmt=self._selected_fmt,
                content_types=",".join([
                    self.content_list.item(i).data(Qt.ItemDataRole.UserRole)
                    for i in range(self.content_list.count())
                    if self.content_list.item(i).checkState() == Qt.CheckState.Checked
                ]),
                file_path=path,
                file_size=os.path.getsize(path) if os.path.isfile(path) else 0
            )

    def _on_error(self, msg: str):
        self.progress.hide()
        self.status_lbl.setText(f"❌ Export failed: {msg}")

    def _open_dir(self):
        out_dir = self.config.get("export_dir", "")
        if out_dir and os.path.isdir(out_dir):
            os.startfile(out_dir)
