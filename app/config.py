import json
import os
from pathlib import Path


class Config:
    APP_NAME = "AI YouTube Studio"
    APP_VERSION = "1.0.0"

    def __init__(self):
        self.app_dir = Path.home() / ".ai_youtube_studio"
        self.app_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = str(self.app_dir / "studio.db")

        self.exports_dir = self.app_dir / "exports"
        self.exports_dir.mkdir(exist_ok=True)

        self.thumbnails_dir = self.app_dir / "thumbnails"
        self.thumbnails_dir.mkdir(exist_ok=True)

        self.cache_dir = self.app_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)

        self.config_file = self.app_dir / "config.json"
        self._data = self._load()

    def _load(self) -> dict:
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                defaults = self._defaults()
                defaults.update(saved)
                return defaults
            except Exception:
                pass
        return self._defaults()

    def _defaults(self) -> dict:
        return {
            "theme": "dark",
            "ai_provider": "openai",
            "ai_model": "gpt-4o",
            "temperature": 0.7,
            "max_tokens": 4096,
            "openai_api_key": "",
            "anthropic_api_key": "",
            "gemini_api_key": "",
            "ollama_base_url": "http://localhost:11434",
            "ollama_model": "llama3.2",
            # Media generation
            "fal_api_key": "",
            "stability_api_key": "",
            "runway_api_key": "",
            "luma_api_key": "",
            "replicate_api_key": "",
            "auto_save": True,
            "auto_save_interval": 30,
            "language": "en",
            "export_dir": str(self.exports_dir),
            "window_width": 1400,
            "window_height": 900,
            "sidebar_collapsed": False,
            "recent_projects": [],
            "total_tokens_used": 0,
        }

    def save(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value):
        self._data[key] = value
        self.save()

    def get_active_provider_name(self) -> str:
        return self.get("ai_provider", "openai")

    def get_active_api_key(self) -> str:
        provider = self.get("ai_provider", "openai")
        key_map = {
            "openai": "openai_api_key",
            "claude": "anthropic_api_key",
            "gemini": "gemini_api_key",
        }
        return self.get(key_map.get(provider, "openai_api_key"), "")

    def is_ai_configured(self) -> bool:
        provider = self.get("ai_provider", "openai")
        if provider == "ollama":
            return True
        return bool(self.get_active_api_key())

    def add_recent_project(self, project_id: int):
        recents = self.get("recent_projects", [])
        if project_id in recents:
            recents.remove(project_id)
        recents.insert(0, project_id)
        self.set("recent_projects", recents[:10])
