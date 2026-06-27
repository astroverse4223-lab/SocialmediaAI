"""QThread workers for AI image and video generation."""
from PySide6.QtCore import QThread, Signal
from typing import Optional, Dict, Any


class ImageGenerationWorker(QThread):
    """Generates images from a prompt using the selected provider."""

    images_ready = Signal(list)      # list of bytes objects
    progress = Signal(str)
    error = Signal(str)
    finished = Signal()

    def __init__(self, provider_key: str, prompt: str, config,
                 negative_prompt: str = "", size_key: str = "Square 1:1  (1024×1024)",
                 style_preset: str = "None", n: int = 1):
        super().__init__()
        self.provider_key = provider_key
        self.prompt = prompt
        self.config = config
        self.negative_prompt = negative_prompt
        self.size_key = size_key
        self.style_preset = style_preset
        self.n = n
        self._cancelled = False

    def cancel(self):
        self._cancelled = True
        self.requestInterruption()

    def run(self):
        from app.core.media_generator import (
            IMAGE_SIZES, IMAGE_PROVIDERS,
            generate_image_dalle,
            generate_image_stability,
            generate_image_fal,
            generate_image_replicate,
        )
        try:
            self.progress.emit("Generating image…")
            size_info = IMAGE_SIZES.get(
                self.size_key,
                {"dalle": "1792x1024", "stability_w": 1536, "stability_h": 1024, "fal": "landscape_16_9"}
            )

            provider = next(
                (p for p in IMAGE_PROVIDERS if p["key"] == self.provider_key), None
            )
            if not provider:
                self.error.emit(f"Unknown provider: {self.provider_key}")
                return

            api_key = self.config.get(provider["config_key"], "")

            if self.provider_key == "dalle3":
                images = generate_image_dalle(
                    self.prompt, api_key,
                    size=size_info["dalle"], n=self.n
                )
            elif self.provider_key == "stability":
                images = generate_image_stability(
                    self.prompt, api_key,
                    negative_prompt=self.negative_prompt,
                    width=size_info["stability_w"],
                    height=size_info["stability_h"],
                    style_preset=self.style_preset if self.style_preset != "None" else "",
                    n=self.n,
                )
            elif self.provider_key.startswith("rep_"):
                model = provider.get("model", "black-forest-labs/flux-schnell")
                images = generate_image_replicate(
                    self.prompt, api_key,
                    model=model,
                    negative_prompt=self.negative_prompt,
                    image_size=size_info["fal"],
                    n=self.n,
                )
            else:
                # fal.ai provider
                model = provider.get("model", "fal-ai/flux/schnell")
                images = generate_image_fal(
                    self.prompt, api_key,
                    model=model,
                    image_size=size_info["fal"],
                    negative_prompt=self.negative_prompt,
                    n=self.n,
                )

            if not self._cancelled:
                self.images_ready.emit(images)
        except Exception as exc:
            if not self._cancelled:
                self.error.emit(str(exc))
        finally:
            self.finished.emit()


class VideoSubmitWorker(QThread):
    """Submits a video generation job and returns the task info dict."""

    job_submitted = Signal(dict)     # task info dict
    error = Signal(str)
    finished = Signal()

    def __init__(self, provider_key: str, prompt: str, config,
                 duration: str = "5", aspect_ratio: str = "16:9",
                 image_bytes: Optional[bytes] = None):
        super().__init__()
        self.provider_key = provider_key
        self.prompt = prompt
        self.config = config
        self.duration = duration
        self.aspect_ratio = aspect_ratio
        self.image_bytes = image_bytes

    def run(self):
        from app.core.media_generator import (
            VIDEO_PROVIDERS,
            submit_video_fal,
            submit_video_runway,
            submit_video_luma,
            submit_video_replicate,
        )
        try:
            provider = next(
                (p for p in VIDEO_PROVIDERS if p["key"] == self.provider_key), None
            )
            if not provider:
                self.error.emit(f"Unknown video provider: {self.provider_key}")
                return

            api_key = self.config.get(provider["config_key"], "")
            task_info: Dict[str, Any] = {}

            if self.provider_key.startswith("fal_"):
                model = provider.get("model", "fal-ai/minimax/video-01")
                task_info = submit_video_fal(
                    self.prompt, api_key,
                    model=model,
                    duration=self.duration,
                    aspect_ratio=self.aspect_ratio,
                    image_bytes=self.image_bytes,
                )
            elif self.provider_key == "runway":
                dur_int = int(self.duration) if self.duration.isdigit() else 5
                ratio_map = {"16:9": "1280:720", "9:16": "720:1280", "1:1": "720:720"}
                ratio = ratio_map.get(self.aspect_ratio, "1280:720")
                task_info = submit_video_runway(
                    self.prompt, api_key,
                    duration=dur_int, ratio=ratio,
                    image_bytes=self.image_bytes,
                )
            elif self.provider_key == "luma":
                task_info = submit_video_luma(
                    self.prompt, api_key,
                    aspect_ratio=self.aspect_ratio,
                    duration=self.duration,
                    image_bytes=self.image_bytes,
                )
            elif self.provider_key.startswith("rep_"):
                model = provider.get("model", "lightricks/ltx-video")
                task_info = submit_video_replicate(
                    self.prompt, api_key,
                    model=model,
                    aspect_ratio=self.aspect_ratio,
                    image_bytes=self.image_bytes,
                )

            task_info["prompt"] = self.prompt
            task_info["provider_label"] = provider["label"]
            self.job_submitted.emit(task_info)

        except Exception as exc:
            self.error.emit(str(exc))
        finally:
            self.finished.emit()


class VideoPollWorker(QThread):
    """Polls a single video generation job for its current status."""

    status_updated = Signal(dict)   # updated task info
    finished = Signal()

    def __init__(self, task_info: Dict[str, Any], config):
        super().__init__()
        self.task_info = task_info
        self.config = config

    def run(self):
        from app.core.media_generator import (
            VIDEO_PROVIDERS, poll_video_fal, poll_video_runway, poll_video_luma,
            poll_video_replicate,
        )
        try:
            provider_key = self.task_info.get("provider_key",
                           "fal" if self.task_info.get("provider") == "fal" else
                           self.task_info.get("provider", "fal"))
            api_key = ""

            if self.task_info.get("provider") == "fal":
                p = next((p for p in VIDEO_PROVIDERS if p["key"].startswith("fal_")), None)
                if p:
                    api_key = self.config.get(p["config_key"], "")
                updated = poll_video_fal(self.task_info, api_key)
            elif self.task_info.get("provider") == "runway":
                api_key = self.config.get("runway_api_key", "")
                updated = poll_video_runway(self.task_info["task_id"], api_key)
                updated["prompt"] = self.task_info.get("prompt", "")
                updated["provider_label"] = self.task_info.get("provider_label", "RunwayML")
            elif self.task_info.get("provider") == "luma":
                api_key = self.config.get("luma_api_key", "")
                updated = poll_video_luma(self.task_info["task_id"], api_key)
                updated["prompt"] = self.task_info.get("prompt", "")
                updated["provider_label"] = self.task_info.get("provider_label", "Luma AI")
            elif self.task_info.get("provider") == "replicate":
                api_key = self.config.get("replicate_api_key", "")
                updated = poll_video_replicate(self.task_info["task_id"], api_key)
                updated["prompt"] = self.task_info.get("prompt", "")
                updated["provider_label"] = self.task_info.get("provider_label", "Replicate")
            else:
                updated = dict(self.task_info)
                updated["status"] = "unknown"

            self.status_updated.emit(updated)
        except Exception as exc:
            updated = dict(self.task_info)
            updated["status"] = "failed"
            updated["error"] = str(exc)
            self.status_updated.emit(updated)
        finally:
            self.finished.emit()


class VideoDownloadWorker(QThread):
    """Downloads a completed video to disk."""

    done = Signal(str)    # local file path
    error = Signal(str)
    finished = Signal()

    def __init__(self, url: str, save_path: str):
        super().__init__()
        self.url = url
        self.save_path = save_path

    def run(self):
        from app.core.media_generator import download_video
        try:
            path = download_video(self.url, self.save_path)
            self.done.emit(path)
        except Exception as exc:
            self.error.emit(str(exc))
        finally:
            self.finished.emit()
