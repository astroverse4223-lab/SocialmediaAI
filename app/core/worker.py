from PySide6.QtCore import QThread, Signal
from typing import Optional, Dict, Any


class YouTubeWorker(QThread):
    """Fetches video metadata and transcript from YouTube."""

    info_ready = Signal(dict)
    transcript_ready = Signal(dict)
    progress = Signal(str)
    error = Signal(str)
    finished = Signal()

    def __init__(self, url: str, fetch_transcript: bool = True,
                 language: str = "en"):
        super().__init__()
        self.url = url
        self.fetch_transcript = fetch_transcript
        self.language = language
        self._cancelled = False

    def cancel(self):
        self._cancelled = True
        self.requestInterruption()

    def run(self):
        try:
            from app.core.youtube import get_video_info, get_transcript
            self.progress.emit("Fetching video information…")
            info = get_video_info(self.url)
            if self._cancelled:
                return
            self.info_ready.emit(info)

            if self.fetch_transcript:
                self.progress.emit("Retrieving transcript…")
                try:
                    transcript_data = get_transcript(
                        info["video_id"], self.language
                    )
                    if not self._cancelled:
                        self.transcript_ready.emit(transcript_data)
                except RuntimeError as exc:
                    self.error.emit(f"Transcript: {exc}")
        except Exception as exc:
            self.error.emit(str(exc))
        finally:
            self.finished.emit()


class GenerationWorker(QThread):
    """Runs AI generation for a single content type."""

    result = Signal(str, str, int, int)   # key, content, prompt_tok, comp_tok
    progress = Signal(str)
    error = Signal(str, str)              # key, error message
    finished = Signal()

    def __init__(self, key: str, func, kwargs: dict):
        super().__init__()
        self.key = key
        self.func = func
        self.kwargs = kwargs
        self._cancelled = False

    def cancel(self):
        self._cancelled = True
        self.requestInterruption()

    def run(self):
        try:
            self.progress.emit(f"Generating {self.key.replace('_', ' ').title()}…")
            text, pt, ct = self.func(**self.kwargs)
            if not self._cancelled:
                self.result.emit(self.key, text, pt, ct)
        except Exception as exc:
            if not self._cancelled:
                self.error.emit(self.key, str(exc))
        finally:
            self.finished.emit()


class BatchGenerationWorker(QThread):
    """Runs all AI generation tasks sequentially."""

    task_started = Signal(str, str, int, int)   # key, label, current, total
    task_done = Signal(str, str, int, int)       # key, content, pt, ct
    task_error = Signal(str, str)                # key, message
    all_done = Signal(dict)
    progress_pct = Signal(int)
    error = Signal(str)

    def __init__(self, transcript: str, title: str, duration: int,
                 provider, tasks=None):
        super().__init__()
        self.transcript = transcript
        self.title = title
        self.duration = duration
        self.provider = provider
        self.tasks = tasks  # None = all tasks
        self._cancelled = False

    def cancel(self):
        self._cancelled = True
        self.requestInterruption()

    def run(self):
        from app.core.content_generator import CONTENT_TASKS
        tasks = self.tasks or CONTENT_TASKS
        results: Dict[str, Any] = {}
        total = len(tasks)

        for i, (key, label, func, extra_args) in enumerate(tasks):
            if self._cancelled:
                break
            self.task_started.emit(key, label, i + 1, total)
            self.progress_pct.emit(int((i / total) * 100))

            kwargs: dict = {
                "transcript": self.transcript,
                "provider": self.provider,
            }
            if "title" in extra_args or "original_title" in extra_args:
                kwargs["title"] = self.title
            if "duration" in extra_args:
                kwargs["duration"] = self.duration

            try:
                text, pt, ct = func(**kwargs)
                results[key] = {
                    "content": text, "prompt_tokens": pt,
                    "completion_tokens": ct, "error": None,
                }
                self.task_done.emit(key, text, pt, ct)
            except Exception as exc:
                msg = str(exc)
                results[key] = {
                    "content": "", "prompt_tokens": 0,
                    "completion_tokens": 0, "error": msg,
                }
                self.task_error.emit(key, msg)

        self.progress_pct.emit(100)
        self.all_done.emit(results)


class ThumbnailWorker(QThread):
    """Generates a thumbnail image via DALL-E."""

    image_ready = Signal(bytes)
    error = Signal(str)
    finished = Signal()

    def __init__(self, prompt: str, provider):
        super().__init__()
        self.prompt = prompt
        self.provider = provider

    def run(self):
        try:
            import base64
            b64 = self.provider.generate_image(self.prompt)
            img_bytes = base64.b64decode(b64)
            self.image_ready.emit(img_bytes)
        except AttributeError:
            self.error.emit("Image generation is only supported with OpenAI (DALL-E 3).")
        except Exception as exc:
            self.error.emit(str(exc))
        finally:
            self.finished.emit()
