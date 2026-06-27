import re
from typing import Optional, Dict, Any, List


def extract_video_id(url: str) -> Optional[str]:
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)",
        r"youtube\.com/shorts/([^&\n?#]+)",
        r"youtube\.com/v/([^&\n?#]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def validate_youtube_url(url: str) -> bool:
    return extract_video_id(url.strip()) is not None


def get_video_info(url: str) -> Dict[str, Any]:
    import yt_dlp

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        tags = info.get("tags") or []
        return {
            "title": info.get("title", "Unknown Title"),
            "video_id": info.get("id", ""),
            "channel": info.get("channel") or info.get("uploader", ""),
            "duration": info.get("duration", 0),
            "views": info.get("view_count", 0),
            "thumbnail_url": info.get("thumbnail", ""),
            "description": (info.get("description") or "")[:2000],
            "publish_date": info.get("upload_date", ""),
            "tags": ",".join(tags[:20]) if tags else "",
            "url": url,
        }


def get_transcript(video_id: str, language: str = "en") -> Dict[str, Any]:
    """Fetch transcript – compatible with youtube-transcript-api v1.x+."""
    from youtube_transcript_api import (
        YouTubeTranscriptApi,
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
    )

    # v1.x uses an instance; instantiating is safe for both v0.x and v1.x
    api = YouTubeTranscriptApi()

    try:
        transcript_list = api.list(video_id)
    except TranscriptsDisabled:
        raise RuntimeError("Transcripts are disabled for this video.")
    except VideoUnavailable:
        raise RuntimeError("This video is unavailable.")
    except Exception as exc:
        raise RuntimeError(f"Could not list transcripts: {exc}") from exc

    # Try languages in priority order
    transcript_obj = None
    for lang in [language, "en", "en-US", "en-GB"]:
        try:
            transcript_obj = transcript_list.find_transcript([lang])
            break
        except NoTranscriptFound:
            continue

    # Fallback: auto-generated English, then any available
    if transcript_obj is None:
        try:
            transcript_obj = transcript_list.find_generated_transcript(["en"])
        except NoTranscriptFound:
            available = list(transcript_list)
            if available:
                transcript_obj = available[0]
            else:
                raise RuntimeError("No transcripts available for this video.")

    try:
        fetched = transcript_obj.fetch()
    except Exception as exc:
        raise RuntimeError(f"Could not fetch transcript: {exc}") from exc

    # v1.x entries are FetchedTranscriptSnippet objects (.text, .start)
    # v0.x entries were plain dicts with ["text"], ["start"]
    def _text(e) -> str:
        return (e.get("text", "") if isinstance(e, dict) else getattr(e, "text", "")).strip()

    def _start(e) -> float:
        return e.get("start", 0.0) if isinstance(e, dict) else float(getattr(e, "start", 0.0))

    entries = list(fetched)
    full_text = " ".join(_text(e) for e in entries)
    timestamped = "\n".join(
        f"[{_fmt_time(_start(e))}] {_text(e)}" for e in entries
    )
    word_count = len(full_text.split())

    return {
        "text": full_text,
        "timestamped": timestamped,
        "entries": [{"start": _start(e), "text": _text(e)} for e in entries],
        "language": transcript_obj.language_code,
        "word_count": word_count,
        "char_count": len(full_text),
    }


def _fmt_time(seconds: float) -> str:
    s = int(seconds)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def format_publish_date(raw: str) -> str:
    if not raw or len(raw) < 8:
        return raw
    try:
        from datetime import datetime
        dt = datetime.strptime(raw, "%Y%m%d")
        return dt.strftime("%B %d, %Y")
    except Exception:
        return raw


def format_view_count(views: int) -> str:
    if views >= 1_000_000:
        return f"{views / 1_000_000:.1f}M"
    if views >= 1_000:
        return f"{views / 1_000:.1f}K"
    return str(views)
