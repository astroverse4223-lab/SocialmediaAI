import sys
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QPainter, QLinearGradient, QColor, QFont, QBrush


class _Splash(QSplashScreen):
    """Splash that ignores mouse clicks so it can't be accidentally dismissed."""
    def mousePressEvent(self, event):
        pass  # Do NOT hide on click — prevents the 'app restarted' effect


def _create_splash() -> QSplashScreen:
    pix = QPixmap(640, 380)
    pix.fill(QColor("#0D0D14"))

    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Accent bar
    grad = QLinearGradient(0, 0, 640, 0)
    grad.setColorAt(0.0, QColor("#7C3AED"))
    grad.setColorAt(0.5, QColor("#6366F1"))
    grad.setColorAt(1.0, QColor("#4F46E5"))
    p.fillRect(0, 0, 640, 5, QBrush(grad))

    # App icon emoji
    p.setPen(QColor("#E2E2F0"))
    p.setFont(QFont("Segoe UI Emoji", 40))
    p.drawText(0, 80, 640, 70, Qt.AlignmentFlag.AlignCenter, "🎬")

    # Title
    p.setFont(QFont("Segoe UI Variable", 34, QFont.Weight.Bold))
    p.drawText(0, 150, 640, 60, Qt.AlignmentFlag.AlignCenter, "AI YouTube Studio")

    # Tagline
    p.setPen(QColor("#8080BB"))
    p.setFont(QFont("Segoe UI", 13))
    p.drawText(0, 215, 640, 36, Qt.AlignmentFlag.AlignCenter,
               "Transform Videos Into Content with AI")

    # Version
    p.setPen(QColor("#4A4A70"))
    p.setFont(QFont("Segoe UI", 10))
    p.drawText(0, 340, 640, 30, Qt.AlignmentFlag.AlignCenter,
               "v1.0.0  •  OpenAI · Claude · Gemini · Ollama")

    p.end()
    return _Splash(pix, Qt.WindowType.WindowStaysOnTopHint)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AI YouTube Studio")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("AI Studio")

    # Set default font
    font = QFont("Segoe UI Variable", 10)
    if not font.exactMatch():
        font = QFont("Segoe UI", 10)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)

    # Splash
    splash = _create_splash()
    splash.show()
    app.processEvents()

    # Initialize config & database
    from app.config import Config
    from app.database.manager import DatabaseManager

    config = Config()
    db = DatabaseManager(config.db_path)
    db.initialize()

    # Apply initial theme
    from app.styles.themes import apply_theme
    apply_theme(app, config.get("theme", "dark") == "dark")

    # Create main window
    from app.ui.main_window import MainWindow
    window = MainWindow(config, db)

    # Show window after splash
    def _launch():
        splash.finish(window)
        window.show()
        window.raise_()
        window.activateWindow()

    QTimer.singleShot(1800, _launch)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
