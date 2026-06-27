"""
AI Image and Video generation – multi-provider support.

Image providers:  DALL-E 3, Stability AI, fal.ai (FLUX Schnell/Dev/Pro)
Video providers:  fal.ai (MiniMax Hailuo, Kling, Wan), RunwayML, Luma AI
"""
import os
import base64
import requests
from typing import Optional, Dict, Any

# ═══════════════════════════════════════════════════════
#  IMAGE GENERATION
# ═══════════════════════════════════════════════════════

IMAGE_STYLE_PRESETS = [
    "None",
    "photorealistic",
    "cinematic",
    "digital-art",
    "anime",
    "illustration",
    "3d-model",
    "enhance",
    "neon-punk",
    "pixel-art",
    "fantasy-art",
    "origami",
    "line-art",
    "isometric",
    "lowpoly",
    "modeling-compound",
]

IMAGE_SIZES = {
    "Square 1:1  (1024×1024)":     {"dalle": "1024x1024", "stability_w": 1024, "stability_h": 1024, "fal": "square_hd"},
    "Landscape 16:9  (1792×1024)": {"dalle": "1792x1024", "stability_w": 1536, "stability_h": 1024, "fal": "landscape_16_9"},
    "Portrait 9:16  (1024×1792)":  {"dalle": "1024x1792", "stability_w": 1024, "stability_h": 1536, "fal": "portrait_16_9"},
    "Wide 3:2  (1536×1024)":       {"dalle": "1792x1024", "stability_w": 1536, "stability_h": 1024, "fal": "landscape_4_3"},
}

IMAGE_PROVIDERS = [
    {"label": "DALL-E 3  (OpenAI)",           "key": "dalle3",            "config_key": "openai_api_key"},
    {"label": "Stable Image Core  (Stability)","key": "stability",         "config_key": "stability_api_key"},
    {"label": "FLUX Schnell  (fal.ai)",        "key": "fal_flux_schnell",  "config_key": "fal_api_key",  "model": "fal-ai/flux/schnell"},
    {"label": "FLUX Dev  (fal.ai)",            "key": "fal_flux_dev",      "config_key": "fal_api_key",  "model": "fal-ai/flux/dev"},
    {"label": "FLUX Pro 1.1  (fal.ai)",        "key": "fal_flux_pro",      "config_key": "fal_api_key",  "model": "fal-ai/flux-pro/v1.1"},
    {"label": "Recraft v3  (fal.ai)",          "key": "fal_recraft",       "config_key": "fal_api_key",  "model": "fal-ai/recraft-v3"},
    {"label": "FLUX Schnell  (Replicate)",     "key": "rep_flux_schnell",  "config_key": "replicate_api_key", "model": "black-forest-labs/flux-schnell"},
    {"label": "FLUX Dev  (Replicate)",         "key": "rep_flux_dev",      "config_key": "replicate_api_key", "model": "black-forest-labs/flux-dev"},
    {"label": "SDXL  (Replicate)",             "key": "rep_sdxl",          "config_key": "replicate_api_key", "model": "stability-ai/sdxl"},
    {"label": "Ideogram v2  (Replicate)",      "key": "rep_ideogram",      "config_key": "replicate_api_key", "model": "ideogram-ai/ideogram-v2"},
]

VIDEO_PROVIDERS = [
    {"label": "MiniMax Hailuo  (fal.ai)",     "key": "fal_minimax",   "config_key": "fal_api_key",    "model": "fal-ai/minimax/video-01",                      "durations": ["5", "10"]},
    {"label": "Kling 1.6 Pro  (fal.ai)",      "key": "fal_kling",     "config_key": "fal_api_key",    "model": "fal-ai/kling-video/v1.6/pro/text-to-video",    "durations": ["5", "10"]},
    {"label": "Kling 1.6 Std  (fal.ai)",      "key": "fal_kling_std", "config_key": "fal_api_key",    "model": "fal-ai/kling-video/v1.6/standard/text-to-video","durations": ["5", "10"]},
    {"label": "Wan 2.1  (fal.ai)",            "key": "fal_wan",       "config_key": "fal_api_key",    "model": "fal-ai/wan-pro",                               "durations": ["5"]},
    {"label": "LTX Video  (fal.ai)",          "key": "fal_ltx",       "config_key": "fal_api_key",    "model": "fal-ai/ltx-video",                             "durations": ["5"]},
    {"label": "CogVideoX-5B  (fal.ai)",       "key": "fal_cogvideo",  "config_key": "fal_api_key",    "model": "fal-ai/cogvideox-5b",                          "durations": ["5", "10"]},
    {"label": "Luma Dream Machine",           "key": "luma",          "config_key": "luma_api_key",   "durations": ["5s", "9s"]},
    {"label": "RunwayML Gen-4 Turbo",         "key": "runway",        "config_key": "runway_api_key", "durations": ["5", "10"]},
    {"label": "LTX Video  (Replicate)",       "key": "rep_ltx",       "config_key": "replicate_api_key", "model": "lightricks/ltx-video",       "durations": ["5"]},
    {"label": "Hunyuan Video  (Replicate)",   "key": "rep_hunyuan",   "config_key": "replicate_api_key", "model": "tencent/hunyuan-video",      "durations": ["5"]},
    {"label": "Stable Video Diffusion  (Replicate)", "key": "rep_svd", "config_key": "replicate_api_key", "model": "stability-ai/stable-video-diffusion", "durations": ["4"]},
]

VIDEO_ASPECT_RATIOS = ["16:9", "9:16", "1:1", "4:3", "3:4", "21:9"]


# ──────────────────────────────────────────────────────
#  IMAGE FUNCTIONS
# ──────────────────────────────────────────────────────

def generate_image_dalle(
    prompt: str,
    api_key: str,
    size: str = "1792x1024",
    quality: str = "hd",
    n: int = 1,
) -> list[bytes]:
    """Generate 1-4 images via OpenAI DALL-E 3. Returns list of PNG bytes."""
    import openai
    client = openai.OpenAI(api_key=api_key)
    # DALL-E 3 only supports n=1 per call; batch via multiple calls
    results = []
    for _ in range(max(1, n)):
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            response_format="b64_json",
            n=1,
        )
        results.append(base64.b64decode(response.data[0].b64_json))
    return results


def generate_image_stability(
    prompt: str,
    api_key: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    style_preset: str = "",
    n: int = 1,
) -> list[bytes]:
    """Generate images via Stability AI Stable Image Core."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*",
    }
    results = []
    for _ in range(max(1, n)):
        body: Dict[str, Any] = {
            "prompt": prompt,
            "output_format": "png",
            "width": width,
            "height": height,
        }
        if negative_prompt:
            body["negative_prompt"] = negative_prompt
        if style_preset and style_preset != "None":
            body["style_preset"] = style_preset

        resp = requests.post(
            "https://api.stability.ai/v2beta/stable-image/generate/core",
            headers=headers,
            files={"none": ""},
            data=body,
            timeout=120,
        )
        resp.raise_for_status()
        results.append(resp.content)
    return results


def generate_image_fal(
    prompt: str,
    api_key: str,
    model: str = "fal-ai/flux/schnell",
    image_size: str = "landscape_16_9",
    negative_prompt: str = "",
    n: int = 1,
) -> list[bytes]:
    """Generate images via fal.ai (FLUX, Recraft, etc.). Returns list of PNG bytes."""
    import fal_client
    os.environ["FAL_KEY"] = api_key

    args: Dict[str, Any] = {
        "prompt": prompt,
        "image_size": image_size,
        "num_images": min(n, 4),
        "enable_safety_checker": False,
    }
    if negative_prompt:
        args["negative_prompt"] = negative_prompt
    if "schnell" in model:
        args["num_inference_steps"] = 4
    elif "dev" in model:
        args["num_inference_steps"] = 28

    result = fal_client.subscribe(model, arguments=args)
    images = result.get("images", [])
    out = []
    for img in images:
        url = img.get("url", "")
        if url.startswith("data:"):
            # base64 data URL
            b64 = url.split(",", 1)[1]
            out.append(base64.b64decode(b64))
        elif url:
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            out.append(r.content)
    return out


# ──────────────────────────────────────────────────────
#  VIDEO FUNCTIONS
# ──────────────────────────────────────────────────────

def submit_video_fal(
    prompt: str,
    api_key: str,
    model: str = "fal-ai/minimax/video-01",
    duration: str = "5",
    aspect_ratio: str = "16:9",
    image_bytes: Optional[bytes] = None,
) -> Dict[str, Any]:
    """Submit async video generation to fal.ai. Returns handle info."""
    import fal_client
    os.environ["FAL_KEY"] = api_key

    args: Dict[str, Any] = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
    }
    # Duration field varies by model
    if "kling" in model or "minimax" in model or "cogvideo" in model:
        args["duration"] = duration
    elif "wan" in model or "ltx" in model:
        args["num_frames"] = 81  # ~5s @ 16fps

    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode()
        args["image_url"] = f"data:image/png;base64,{b64}"

    handle = fal_client.submit(model, arguments=args)
    return {
        "task_id": handle.request_id,
        "status": "queued",
        "provider": "fal",
        "model": model,
        "_queue_url": handle._queue_url,
        "_request_id": handle.request_id,
    }


def poll_video_fal(task_info: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    """Poll fal.ai queue for video generation status."""
    import fal_client
    os.environ["FAL_KEY"] = api_key

    class _Handle:
        def __init__(self, queue_url, request_id):
            self._queue_url = queue_url
            self.request_id = request_id

    handle = _Handle(task_info["_queue_url"], task_info["_request_id"])
    try:
        status = fal_client.status(handle._queue_url, handle.request_id, with_logs=False)
        status_name = type(status).__name__.lower()

        updated = dict(task_info)
        if "completed" in status_name or "success" in status_name:
            output = fal_client.result(handle._queue_url, handle.request_id)
            video = output.get("video", {})
            updated["status"] = "completed"
            updated["video_url"] = video.get("url", "") if isinstance(video, dict) else str(video)
        elif "failed" in status_name or "error" in status_name:
            updated["status"] = "failed"
        elif "in_progress" in status_name:
            updated["status"] = "processing"
        else:
            updated["status"] = "queued"
        return updated
    except Exception as exc:
        updated = dict(task_info)
        updated["status"] = "failed"
        updated["error"] = str(exc)
        return updated


def download_video(url: str, save_path: str) -> str:
    """Download a video from URL to save_path. Returns the local path."""
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()
    with open(save_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=65536):
            f.write(chunk)
    return save_path


def submit_video_runway(
    prompt: str,
    api_key: str,
    duration: int = 5,
    ratio: str = "1280:720",
    image_bytes: Optional[bytes] = None,
) -> Dict[str, Any]:
    """Submit video generation to RunwayML Gen-4 Turbo."""
    import runwayml
    client = runwayml.RunwayML(api_key=api_key)
    kwargs: Dict[str, Any] = {
        "model": "gen4_turbo",
        "prompt_text": prompt,
        "ratio": ratio,
        "duration": duration,
    }
    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode()
        kwargs["prompt_image"] = f"data:image/png;base64,{b64}"
    task = client.image_to_video.create(**kwargs)
    return {"task_id": task.id, "status": task.status, "provider": "runway"}


def poll_video_runway(task_id: str, api_key: str) -> Dict[str, Any]:
    import runwayml
    client = runwayml.RunwayML(api_key=api_key)
    task = client.tasks.retrieve(task_id)
    result: Dict[str, Any] = {
        "task_id": task_id,
        "status": task.status.lower() if task.status else "unknown",
        "provider": "runway",
        "video_url": None,
    }
    if task.status in ("SUCCEEDED", "succeeded"):
        result["status"] = "completed"
        result["video_url"] = task.output[0] if task.output else None
    elif task.status in ("FAILED", "failed"):
        result["status"] = "failed"
    return result


def submit_video_luma(
    prompt: str,
    api_key: str,
    aspect_ratio: str = "16:9",
    duration: str = "5s",
    image_bytes: Optional[bytes] = None,
) -> Dict[str, Any]:
    """Submit video generation to Luma AI Dream Machine."""
    import lumaai
    client = lumaai.LumaAI(auth_token=api_key)
    kwargs: Dict[str, Any] = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "loop": False,
    }
    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode()
        kwargs["keyframes"] = {
            "frame0": {"type": "image", "url": f"data:image/png;base64,{b64}"}
        }
    generation = client.generations.create(**kwargs)
    return {"task_id": generation.id, "status": str(generation.state), "provider": "luma"}


def poll_video_luma(task_id: str, api_key: str) -> Dict[str, Any]:
    import lumaai
    client = lumaai.LumaAI(auth_token=api_key)
    gen = client.generations.get(task_id)
    result: Dict[str, Any] = {
        "task_id": task_id,
        "status": str(gen.state).lower(),
        "provider": "luma",
        "video_url": None,
    }
    if gen.state in ("completed", "done"):
        result["status"] = "completed"
        if gen.assets and hasattr(gen.assets, "video"):
            result["video_url"] = gen.assets.video
    elif gen.state in ("failed", "error"):
        result["status"] = "failed"
    return result


# ──────────────────────────────────────────────────────
#  REPLICATE FUNCTIONS
# ──────────────────────────────────────────────────────

def generate_image_replicate(
    prompt: str,
    api_key: str,
    model: str = "black-forest-labs/flux-schnell",
    negative_prompt: str = "",
    image_size: str = "landscape_16_9",
    n: int = 1,
) -> list[bytes]:
    """Generate images synchronously via Replicate. Returns list of PNG bytes."""
    import replicate

    # Map our size keys to width/height for models that need it
    _size_map = {
        "square_hd":       (1024, 1024),
        "landscape_16_9":  (1344, 768),
        "portrait_16_9":   (768, 1344),
        "landscape_4_3":   (1152, 896),
    }
    w, h = _size_map.get(image_size, (1344, 768))

    client = replicate.Client(api_token=api_key)
    input_args: Dict[str, Any] = {
        "prompt": prompt,
        "width": w,
        "height": h,
        "num_outputs": min(n, 4),
    }
    if negative_prompt and "flux" not in model:
        input_args["negative_prompt"] = negative_prompt

    output = client.run(model, input=input_args)
    results = []
    # output is a list of FileOutput objects or URLs
    items = list(output) if not isinstance(output, list) else output
    for item in items:
        if hasattr(item, "read"):
            results.append(item.read())
        else:
            url = str(item)
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            results.append(resp.content)
    return results


def submit_video_replicate(
    prompt: str,
    api_key: str,
    model: str = "lightricks/ltx-video",
    aspect_ratio: str = "16:9",
    image_bytes: Optional[bytes] = None,
) -> Dict[str, Any]:
    """Submit async video generation to Replicate. Returns task info dict."""
    import replicate

    client = replicate.Client(api_token=api_key)
    input_args: Dict[str, Any] = {"prompt": prompt}
    if image_bytes:
        import io
        input_args["image"] = io.BytesIO(image_bytes)
    # aspect ratio handling per model
    if "ltx" in model or "hunyuan" in model:
        w, h = (768, 432) if aspect_ratio == "16:9" else (432, 768)
        input_args["width"] = w
        input_args["height"] = h
    elif "stable-video" in model:
        # SVD takes an image; if none given it won't work well
        input_args.pop("prompt", None)

    prediction = client.predictions.create(model=model, input=input_args)
    return {
        "task_id": prediction.id,
        "status": "queued",
        "provider": "replicate",
        "model": model,
        "prompt": prompt,
    }


def poll_video_replicate(task_id: str, api_key: str) -> Dict[str, Any]:
    """Poll Replicate prediction status."""
    import replicate

    client = replicate.Client(api_token=api_key)
    prediction = client.predictions.get(task_id)
    status = prediction.status  # "starting" | "processing" | "succeeded" | "failed" | "canceled"

    status_map = {
        "starting":   "queued",
        "processing": "processing",
        "succeeded":  "completed",
        "failed":     "failed",
        "canceled":   "failed",
    }
    result: Dict[str, Any] = {
        "task_id": task_id,
        "status": status_map.get(status, "unknown"),
        "provider": "replicate",
        "video_url": None,
    }
    if status == "succeeded" and prediction.output:
        out = prediction.output
        if isinstance(out, list):
            result["video_url"] = str(out[0])
        else:
            result["video_url"] = str(out)
    elif status in ("failed", "canceled"):
        result["error"] = prediction.error or "Generation failed"
    return result

