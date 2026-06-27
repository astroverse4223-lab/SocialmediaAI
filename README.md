<div align="center">

# 🎬 AI YouTube Studio

**Transform any YouTube video into a complete suite of AI-generated content — in one click.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PySide6](https://img.shields.io/badge/PySide6-6.6%2B-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://doc.qt.io/qtforpython)
[![License: MIT](https://img.shields.io/badge/License-MIT-7C3AED?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://github.com)

*A polished, production-quality Windows desktop app — paste a URL, click Generate, get everything.*

---

</div>

## ✨ What It Does

Paste a YouTube URL and AI YouTube Studio fetches the transcript, then generates **26+ pieces of content** simultaneously using your choice of AI provider:

| Content Type | Examples |
|---|---|
| 📋 **Summaries** | Executive, bullet-point, key takeaways |
| 📝 **Blog Posts** | Long-form (3,000+ words), medium, short, tutorial |
| 📱 **Social Media** | Twitter threads, LinkedIn, Facebook, Instagram, TikTok, Threads |
| 🔍 **SEO** | Full SEO package, keywords, meta descriptions |
| 🎬 **Video Assets** | Titles, timestamps, thumbnail concepts, press release |
| 📧 **Extras** | Newsletter, podcast show notes, CTAs, quotes, FAQ |
| 🖼️ **AI Images** | DALL-E 3, FLUX, Stability AI, Replicate models |
| 🎥 **AI Videos** | Kling, MiniMax, Wan, LTX, Runway, Luma, Hunyuan |

---

## 🚀 Features

- **Multi-Provider AI** — OpenAI GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, or local Ollama
- **AI Image Generation** — 10 providers: DALL-E 3, Stability AI, FLUX Schnell/Dev/Pro, Recraft v3, Ideogram v2, SDXL via Replicate
- **AI Video Generation** — 11 providers: fal.ai (Kling, MiniMax, Wan, LTX, CogVideoX), RunwayML Gen-4, Luma Dream Machine, Hunyuan, Replicate SVD
- **Dark / Light Theme** — Polished dark UI with accent color system
- **Project Management** — Save, load, and manage multiple projects with SQLite
- **Content Library** — Browse all generated content across projects
- **Export Center** — Export to TXT, Markdown, JSON, HTML, DOCX, and PDF
- **Template System** — Save and reuse custom prompts
- **SEO Tools** — Dedicated keyword and metadata generation
- **Thumbnail Generator** — AI concept + DALL-E image generation pipeline
- **History** — Full audit trail of all generation activity
- **Auto-save** — Configurable auto-save interval

---

## 📋 Requirements

- **OS:** Windows 10 / 11
- **Python:** 3.10 or newer
- **At least one AI API key** (see [Configuration](#-configuration))

---

## 🛠 Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/ai-youtube-studio.git
cd ai-youtube-studio

# 2. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the app
python main.py
```

---

## 🔑 Configuration

On first launch the app creates `C:\Users\<you>\.ai_youtube_studio\config.json`.  
You can set all API keys from **Settings → AI Settings** inside the app.

### Text AI Providers

| Provider | Required Key | Get Key |
|---|---|---|
| **OpenAI** (GPT-4o, DALL-E 3) | `openai_api_key` | [platform.openai.com](https://platform.openai.com/api-keys) |
| **Anthropic** (Claude 3.5) | `anthropic_api_key` | [console.anthropic.com](https://console.anthropic.com) |
| **Google** (Gemini 1.5 Pro) | `gemini_api_key` | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| **Ollama** (local, free) | *(no key needed)* | [ollama.com](https://ollama.com) |

### Media Generation Providers

| Provider | Key | Models Included |
|---|---|---|
| **fal.ai** | `fal_api_key` | FLUX Schnell/Dev/Pro, Recraft v3, Kling 1.6, MiniMax, Wan 2.1, LTX, CogVideoX |
| **Stability AI** | `stability_api_key` | Stable Image Core |
| **RunwayML** | `runway_api_key` | Gen-4 Turbo |
| **Luma AI** | `luma_api_key` | Dream Machine |
| **Replicate** | `replicate_api_key` | FLUX Schnell/Dev, SDXL, Ideogram v2, LTX, Hunyuan, SVD |

> **Tip:** You only need keys for providers you want to use. OpenAI covers both text (GPT-4o) and images (DALL-E 3) with one key.

---

## 🖥 Usage

### Basic Workflow

```
1. Click "New Project" in the sidebar
2. Paste a YouTube URL → click Load (or press Enter)
3. Wait for transcript to load (~5 seconds)
4. Click "⚡ Generate All Content"
5. Browse tabs: Summary · Blog · Social Media · SEO · Timestamps · Extras · Video Assets
6. Click "📋 Copy" on any card, or go to Export Center to export everything
```

### AI Media Generator

```
1. Click "🎨 AI Media Generator" in the sidebar
2. Image tab → type a prompt → choose provider → click Generate
3. Click "🎬 Use as Ref" to send a generated image to the Video tab
4. Video tab → type a prompt → choose provider → click Generate Video
5. Jobs poll automatically every 15 seconds; download when ready
```

### Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+N` | New Project |
| `Ctrl+P` | Projects |
| `Ctrl+D` | Dashboard |
| `Ctrl+E` | Export Center |
| `Ctrl+,` | Preferences |

---

## 📁 Project Structure

```
ai-youtube-studio/
├── main.py                        # App entry point & splash screen
├── requirements.txt
├── app/
│   ├── config.py                  # JSON config, API keys, preferences
│   ├── core/
│   │   ├── youtube.py             # YouTube metadata + transcript (yt-dlp, youtube-transcript-api)
│   │   ├── ai_providers.py        # Multi-provider AI abstraction (OpenAI, Claude, Gemini, Ollama)
│   │   ├── content_generator.py   # 26+ generation functions
│   │   ├── media_generator.py     # Image & video generation (10 image + 11 video providers)
│   │   ├── media_worker.py        # QThread workers for media generation
│   │   ├── worker.py              # QThread workers for YouTube + AI generation
│   │   └── exporter.py            # TXT, MD, JSON, HTML, DOCX, PDF export
│   ├── database/
│   │   ├── models.py              # SQLAlchemy ORM models
│   │   └── manager.py             # CRUD operations
│   ├── styles/
│   │   └── themes.py              # Dark/Light QSS themes
│   └── ui/
│       ├── main_window.py         # Main application window
│       ├── components/
│       │   ├── sidebar.py         # Navigation sidebar
│       │   ├── cards.py           # Reusable card widgets
│       │   └── dialogs.py         # Modal dialogs
│       └── pages/
│           ├── dashboard.py
│           ├── new_project.py     # Main workflow page
│           ├── projects.py
│           ├── content_library.py
│           ├── media_generator.py # AI Image + Video generator UI
│           ├── blog_generator.py
│           ├── social_media.py
│           ├── thumbnail_generator.py
│           ├── seo_tools.py
│           ├── export_center.py
│           ├── templates.py
│           ├── history.py
│           ├── preferences.py
│           └── ai_settings.py
```

---

## 🤖 Supported AI Models

### Text Generation
- **OpenAI:** `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-3.5-turbo`
- **Anthropic:** `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`, `claude-3-opus`
- **Google:** `gemini-1.5-pro`, `gemini-1.5-flash`, `gemini-2.0-flash`
- **Ollama:** Any locally installed model (llama3.2, mistral, etc.)

### Image Generation
| Provider | Models |
|---|---|
| OpenAI | DALL-E 3 (HD) |
| Stability AI | Stable Image Core |
| fal.ai | FLUX Schnell, FLUX Dev, FLUX Pro 1.1, Recraft v3 |
| Replicate | FLUX Schnell, FLUX Dev, SDXL, Ideogram v2 |

### Video Generation
| Provider | Models |
|---|---|
| fal.ai | MiniMax Hailuo, Kling 1.6 Pro/Std, Wan 2.1, LTX Video, CogVideoX-5B |
| RunwayML | Gen-4 Turbo |
| Luma AI | Dream Machine |
| Replicate | LTX Video, Hunyuan Video, Stable Video Diffusion |

---

## 📦 Dependencies

```
PySide6          # Qt6 desktop UI framework
SQLAlchemy       # Database ORM
yt-dlp           # YouTube video metadata
youtube-transcript-api  # Transcript fetching
openai           # GPT-4o + DALL-E 3
anthropic        # Claude
google-generativeai     # Gemini
fal-client       # fal.ai image & video generation
runwayml         # RunwayML Gen-4
lumaai           # Luma Dream Machine
replicate        # Replicate.com models
Pillow           # Image processing
python-docx      # DOCX export
reportlab        # PDF export
markdown         # Markdown rendering
requests         # HTTP client
aiohttp          # Async HTTP
beautifulsoup4   # HTML parsing
```

---

## 🗄 Data Storage

All app data is stored in `C:\Users\<you>\.ai_youtube_studio\`:

```
~/.ai_youtube_studio/
├── config.json      # Settings & API keys
├── studio.db        # SQLite database (projects, content, history)
├── exports/         # Exported files
├── thumbnails/      # Cached video thumbnails
└── cache/           # Temporary files
```

---

## 🔒 Privacy & Security

- API keys are stored **locally only** in `config.json` — never transmitted anywhere except to their respective provider APIs
- All data stays on your machine in `~/.ai_youtube_studio/`
- No telemetry, no analytics, no remote connections except AI provider APIs

---

## 🐛 Known Issues & Troubleshooting

**Transcript not loading?**
> Make sure `youtube-transcript-api >= 1.0.0` is installed. Older versions use a different API. Run `pip install -U youtube-transcript-api`.

**App closes but process keeps running?**
> Fixed in latest version — the splash screen and background timers are now properly cleaned up on exit.

**Video generation job stuck at "Queued"?**
> Video generation can take 2–10 minutes depending on the model. Jobs auto-poll every 15 seconds. Click "🔄 Refresh All" to manually check.

**Copy/Paste not working?**
> All text areas are fully editable — click inside the text area first, then use `Ctrl+A` to select all and `Ctrl+C` to copy. The "📋 Copy" button also copies the full content.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

```bash
# Development setup
git clone https://github.com/yourusername/ai-youtube-studio.git
cd ai-youtube-studio
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## 📄 License

[MIT](LICENSE) — free to use, modify, and distribute.

---

<div align="center">

Built with ❤️ using **Python**, **PySide6**, and the power of modern AI APIs.

⭐ **Star this repo if you find it useful!** ⭐

</div>
