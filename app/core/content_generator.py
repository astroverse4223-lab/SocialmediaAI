"""Content generation functions – one per content type."""
from typing import Optional, Tuple, Dict, Any
from .ai_providers import AIProvider

_SYSTEM = (
    "You are an expert content strategist, copywriter, and digital marketing specialist "
    "with deep expertise in YouTube, SEO, and multi-platform content distribution. "
    "Produce high-quality, platform-native content that drives engagement and results. "
    "Always follow the exact format requested."
)

MAX_TRANSCRIPT = 10_000  # chars sent to AI


def _call(provider: AIProvider, prompt: str,
          system: str = _SYSTEM,
          temperature: float = 0.72,
          max_tokens: int = 4096) -> Tuple[str, int, int]:
    try:
        return provider.generate(prompt, system_prompt=system,
                                 temperature=temperature, max_tokens=max_tokens)
    except Exception as exc:
        raise RuntimeError(str(exc)) from exc


def _trim(text: str, chars: int = MAX_TRANSCRIPT) -> str:
    return text[:chars]


# ═══════════════════════════════════════════════════════
#  SUMMARIES
# ═══════════════════════════════════════════════════════

def gen_executive_summary(transcript: str, provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Based on the YouTube video transcript below, write a concise **Executive Summary** \
(200-300 words) covering:
• The main topic and purpose
• Key insights and findings
• Notable statistics or data
• Overall conclusions

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=600)


def gen_short_summary(transcript: str, provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Write a punchy 2-3 sentence summary of this YouTube video transcript.
Make it compelling and quotable.

Transcript:
{_trim(transcript, 6000)}"""
    return _call(provider, p, max_tokens=200)


def gen_detailed_summary(transcript: str, provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Write a comprehensive detailed summary of this YouTube video transcript.

Structure:
## Overview
[2-3 sentences]

## Main Topics Covered
[Bullet list]

## Key Points & Explanations
[Detailed breakdown]

## Supporting Details
[Examples, statistics, case studies mentioned]

## Conclusions & Recommendations
[What the creator recommends]

## Action Items
[Specific things viewers can do]

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=2500)


def gen_bullet_summary(transcript: str, provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Convert this YouTube video transcript into a clean bullet-point summary.

Rules:
• 15-25 bullets
• One key idea per bullet (1-2 sentences)
• Most important points first
• Clear, direct language

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=1200)


def gen_key_takeaways(transcript: str, provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Extract the top 10 key takeaways from this YouTube video transcript.

For each:
**[Bold 3-5 word title]**
[2-3 sentence explanation + why it matters]

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=1500)


def gen_quotes(transcript: str, provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Extract the most powerful, quotable statements from this transcript.

## 🎯 Motivational Quotes (3-5)
## 💡 Key Insight Quotes (3-5)
## 📊 Data & Statistics (if any)
## 🔥 Tweetable Quotes (5, each under 280 chars)
## 😂 Memorable/Funny Moments (if any)

Format: "Quote text" — [context if needed]

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=1500)


def gen_faq(transcript: str, provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Create a comprehensive FAQ (10-15 Q&A pairs) based on this YouTube video transcript.
Cover common viewer questions, how-to questions, and clarifying questions.

Format:
**Q: [Question]**
A: [Detailed answer based on the transcript]

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=2000)


def gen_action_items(transcript: str, provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Extract all actionable advice and action items from this transcript.

Format as a numbered checklist with:
1. [ ] [Specific action] — *Why: brief explanation*

Group by category if relevant. Include difficulty level (Easy/Medium/Hard).

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=1200)


# ═══════════════════════════════════════════════════════
#  BLOG POSTS
# ═══════════════════════════════════════════════════════

def gen_blog_long_form(transcript: str, title: str,
                       provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Write a comprehensive long-form SEO blog post based on this YouTube video.

Video Title: {title}

Requirements:
- 1800-2500 words
- Start with: [META: <155-char meta description>]
- H1 title (compelling, SEO-optimized)
- Engaging introduction with a hook
- 5-7 H2 sections with H3 sub-sections where appropriate
- Include [IMAGE: description] placeholders
- Natural keyword integration
- Conclusion with strong CTA
- End with: **Related Topics:** [5 suggestions]

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=4096)


def gen_blog_medium(transcript: str, title: str,
                    provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Write a Medium-style thought leadership article based on this YouTube video.

Video Title: {title}
Length: 900-1200 words

Style: Conversational, insightful, personal experience woven in.
Structure: Hook → Context → 3-4 core insight sections → Reflection → Takeaway

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=2000)


def gen_blog_short(transcript: str, title: str,
                   provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Write a short, punchy blog post based on this YouTube video.

Video Title: {title}
Length: 400-600 words

Rules:
- Bold all key points
- Short paragraphs (2-3 sentences)
- One clear takeaway per section
- End with a strong CTA

Transcript:
{_trim(transcript, 6000)}"""
    return _call(provider, p, max_tokens=1000)


def gen_blog_tutorial(transcript: str, title: str,
                      provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Write a step-by-step tutorial/how-to blog post based on this YouTube video.

Video Title: {title}

Structure:
# [Tutorial Title: How to ...]
## What You'll Learn
## Prerequisites
## Step 1: [Title]
[Detailed instructions]
## Step 2: [Title]
...
## Common Mistakes to Avoid
## Final Result
## Next Steps

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=3000)


# ═══════════════════════════════════════════════════════
#  SOCIAL MEDIA
# ═══════════════════════════════════════════════════════

def gen_twitter_thread(transcript: str, provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Create a viral Twitter/X thread (12-15 tweets) based on this transcript.

Rules:
- Each tweet MUST be under 280 characters
- Number format: 1/ 2/ 3/ etc.
- Tweet 1: Scroll-stopping hook
- Tweets 2-11: One insight per tweet, standalone value
- Tweet 12-13: Power conclusion
- Last tweet: CTA + 3-5 hashtags

Use line breaks for readability. 1-2 emojis per tweet.

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=2000)


def gen_linkedin_post(transcript: str, provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Write a high-engagement LinkedIn post based on this transcript.

Requirements:
- 1200-1800 characters
- Do NOT start with "I"
- Hook: Bold surprising claim or insight
- Body: 5-7 bullet takeaways using →
- Professional tone with personality
- End: Thought-provoking question
- Footer: 4-5 hashtags

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=800)


def gen_facebook_post(transcript: str, provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Create 3 Facebook post variations based on this transcript.

**Variation 1 — Informative (350-400 words)**
[Educational, share key insights]

**Variation 2 — Engagement (150-200 words)**
[Ask a compelling question, encourage comments]

**Variation 3 — Story (200-300 words)**
[Relatable narrative, emotional angle]

Each: strong opener, 2-3 emojis, CTA, relevant hashtags.

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=1800)


def gen_instagram_captions(transcript: str,
                            provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Create 5 Instagram captions based on this transcript.

For each caption:
**Caption [#] — [Style]**
[Caption body: 150-300 chars]
.
.
.
[20-30 hashtags: mix popular + niche]

Styles: 1-Inspirational, 2-Educational, 3-Personal/BTS, 4-Question, 5-Bold Statement

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=2000)


def gen_tiktok_content(transcript: str, provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Create a complete TikTok content package based on this transcript.

## 🎬 HOOKS (3 options for first 3 seconds)
[Hook 1]
[Hook 2]
[Hook 3]

## 📝 CAPTION (100-150 chars)
[Caption]

## 📖 DESCRIPTION (500-700 chars)
[Story-driven, conversational]

## #️⃣ HASHTAGS (25 tags)
[Mix trending + niche]

## 📌 PINNED COMMENT
[Add value / answer anticipated questions]

## 🎤 VOICEOVER SCRIPT (30-60 sec)
[Engaging script for the TikTok]

## 🔥 TRENDING TITLE IDEAS (5 options)
[Use TikTok formats: "POV:", "The truth about...", etc.]

## 🎯 ENDING CTA (3 options)
[Last 3 seconds]

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=2500)


def gen_threads_post(transcript: str, provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Create 3 Threads (Meta) posts based on this transcript.

Style: Conversational, Twitter-like but more personal
Each post: 300-500 characters, authentic voice, minimal hashtags

Post 1: Main insight
Post 2: Controversial/bold take
Post 3: Question to community

Transcript:
{_trim(transcript, 6000)}"""
    return _call(provider, p, max_tokens=600)


def gen_youtube_community(transcript: str,
                           provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Create 3 YouTube Community post ideas based on this transcript.

**Post 1 — Behind the Scenes**
[What went into making this content]

**Post 2 — Poll**
[Relevant poll question with 4 options]

**Post 3 — Announcement/Teaser**
[Tease upcoming related content]

Transcript:
{_trim(transcript, 5000)}"""
    return _call(provider, p, max_tokens=800)


# ═══════════════════════════════════════════════════════
#  SEO
# ═══════════════════════════════════════════════════════

def gen_seo_package(transcript: str, title: str,
                    provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Create a complete SEO package for this YouTube video content.

Video Title: {title}

## 🎯 PRIMARY KEYWORDS (5)
[keyword — search volume tier: High/Med/Low]

## 🔑 SECONDARY KEYWORDS (10)
## 🔗 LSI / SEMANTIC KEYWORDS (15)

## 📄 META TITLE (55-60 chars)
## 📝 META DESCRIPTION (150-160 chars, includes CTA)
## 🔗 URL SLUG (3-6 hyphenated words)

## 🏷️ TAGS (20 YouTube/article tags)

## 🔍 SEARCH INTENT
[Primary intent + explanation]

## 📊 CONTENT GAPS (5 related topics not covered)

## 🔗 INTERNAL LINK OPPORTUNITIES (5 topic suggestions)

## 📋 FAQ SCHEMA (5 Q&A pairs in plain text)

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=2500)


def gen_keywords_only(transcript: str, title: str,
                      provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Extract 30 SEO keywords from this content. Group by:
Primary (5), Secondary (10), Long-tail (10), Questions (5).

Title: {title}
Transcript: {_trim(transcript, 5000)}"""
    return _call(provider, p, max_tokens=800)


# ═══════════════════════════════════════════════════════
#  TIMESTAMPS
# ═══════════════════════════════════════════════════════

def gen_timestamps(transcript: str, duration: int,
                   provider: AIProvider) -> Tuple[str, int, int]:
    dur_str = f"{duration // 60}:{duration % 60:02d}" if duration else "unknown"
    p = f"""Generate YouTube chapter timestamps for this video.

Duration: {dur_str}

Rules:
- 8-15 chapters
- EXACT format: MM:SS Chapter Title (or HH:MM:SS for >1hr)
- First must be: 00:00 Introduction
- Titles: descriptive, 3-6 words, make viewers want to jump there
- Distribute evenly across the video

Then add:
**CHAPTER DESCRIPTIONS** — one sentence per chapter explaining what's covered.

Transcript (with timing clues):
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=1200)


# ═══════════════════════════════════════════════════════
#  NEWSLETTER
# ═══════════════════════════════════════════════════════

def gen_newsletter(transcript: str, title: str,
                   provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Write a professional email newsletter based on this YouTube video.

Video Title: {title}

**SUBJECT LINE OPTIONS (5):**
[A/B testable, curiosity-driving]

**PREVIEW TEXT (50-90 chars):**

---

**EMAIL BODY (400-600 words):**

[Warm personal greeting + hook]

[What this email is about]

**This Week's Key Insights:**
• [Insight 1]
• [Insight 2]
• [Insight 3]

**The #1 Takeaway:**
[Bold, memorable single point]

**Your Action Item This Week:**
[One specific thing to do]

**Resources Mentioned:**
[Any tools/books/links mentioned]

[Closing + CTA to watch the video]

[Sign-off]

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=1800)


# ═══════════════════════════════════════════════════════
#  PODCAST NOTES
# ═══════════════════════════════════════════════════════

def gen_podcast_notes(transcript: str, title: str,
                      provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Create professional podcast show notes.

Episode Title: {title}

## EPISODE DESCRIPTION (150-200 words for podcast directories)

## TIMESTAMPS
00:00 — Introduction
[MM:SS — Topic]
...

## KEY TAKEAWAYS (7 bullet points)

## RESOURCES MENTIONED
[Tools, books, websites, people]

## EPISODE HIGHLIGHTS (3 golden-nugget quotes)

## LISTENER QUESTIONS (5 for community engagement)

## EPISODE TAGS (12 podcast SEO tags)

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=2000)


# ═══════════════════════════════════════════════════════
#  VIDEO ASSETS
# ═══════════════════════════════════════════════════════

def gen_video_titles(transcript: str, original_title: str,
                     provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Generate 20 compelling YouTube title alternatives.

Original: {original_title}

Categories:
**🧠 Curiosity Titles (5)** — knowledge-gap hooks
**📋 How-To Titles (3)** — clear instructional format
**🔢 List Titles (3)** — number-based
**❓ Question Titles (3)** — thought-provoking
**⚡ Bold/Controversial Titles (3)** — challenge norms
**📖 Story Titles (3)** — narrative hooks

Rate each: 🔥 High CTR / ⚡ Medium / 📊 Standard

**THUMBNAIL TEXT IDEAS (5 options):**
[2-5 bold words for thumbnail overlay]

Transcript:
{_trim(transcript, 5000)}"""
    return _call(provider, p, max_tokens=1800)


def gen_thumbnail_ideas(transcript: str, title: str,
                        provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Generate 5 creative YouTube thumbnail concepts.

Video Title: {title}

For each:
**Concept [#]: [Style Name]**
🖼️ Visual: [What to show]
📝 Text Overlay: [Bold overlay text, max 5 words]
🎨 Colors: [Primary color scheme]
😮 Expression: [Emotion/facial expression if person shown]
🏞️ Background: [Background description]
📐 Reference Style: [e.g., MrBeast, minimal, dark, etc.]
💡 Why It Works: [Psychological hook]

**DALL-E PROMPT for Concept 1:**
[Detailed AI image generation prompt for this thumbnail, suitable for DALL-E 3]

Transcript:
{_trim(transcript, 5000)}"""
    return _call(provider, p, max_tokens=2500)


def gen_thumbnail_dalle_prompt(concept: str, title: str,
                                provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Create an optimized DALL-E 3 image generation prompt for a YouTube thumbnail.

Video Title: {title}
Thumbnail Concept: {concept}

Generate a detailed, specific DALL-E 3 prompt that:
- Creates a 1792x1024 thumbnail
- Has high contrast and visual impact
- Is photorealistic unless otherwise noted
- Includes all visual elements needed
- Avoids text in the image (handled separately)

Output ONLY the image generation prompt, nothing else."""
    return _call(provider, p, max_tokens=400)


# ═══════════════════════════════════════════════════════
#  PRESS RELEASE & EXTRAS
# ═══════════════════════════════════════════════════════

def gen_press_release(transcript: str, title: str,
                      provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Write a professional press release based on this YouTube video content.

Video Title: {title}

Format:
FOR IMMEDIATE RELEASE

**[Headline]**
**[Subheadline]**

[City, Date] — [Opening paragraph: who, what, when, where, why]

[Body: 2-3 paragraphs with key findings/announcements]

[Quote from creator]

[About section placeholder]

###

Contact: [Name], [Email], [Phone]

Transcript:
{_trim(transcript)}"""
    return _call(provider, p, max_tokens=1200)


def gen_ctas(transcript: str, provider: AIProvider) -> Tuple[str, int, int]:
    p = f"""Generate 15 compelling Call-to-Action (CTA) options based on this video content.

Categories:
**Subscribe CTAs (3)**
**Comment CTAs (3)**
**Like CTAs (3)**
**Share CTAs (3)**
**Link-in-bio CTAs (3)**

Make them specific to the content, not generic.

Transcript:
{_trim(transcript, 5000)}"""
    return _call(provider, p, max_tokens=800)


# ═══════════════════════════════════════════════════════
#  BATCH GENERATION
# ═══════════════════════════════════════════════════════

CONTENT_TASKS = [
    ("executive_summary",    "Executive Summary",      gen_executive_summary,    []),
    ("bullet_summary",       "Bullet Summary",         gen_bullet_summary,       []),
    ("key_takeaways",        "Key Takeaways",          gen_key_takeaways,        []),
    ("quotes",               "Key Quotes",             gen_quotes,               []),
    ("faq",                  "FAQ",                    gen_faq,                  []),
    ("twitter_thread",       "Twitter Thread",         gen_twitter_thread,       []),
    ("linkedin_post",        "LinkedIn Post",          gen_linkedin_post,        []),
    ("instagram_captions",   "Instagram Captions",     gen_instagram_captions,   []),
    ("tiktok_content",       "TikTok Content",         gen_tiktok_content,       []),
    ("blog_long_form",       "Long-Form Blog",         gen_blog_long_form,       ["title"]),
    ("blog_medium",          "Medium Article",         gen_blog_medium,          ["title"]),
    ("seo_package",          "SEO Package",            gen_seo_package,          ["title"]),
    ("timestamps",           "Timestamps",             gen_timestamps,           ["duration"]),
    ("video_titles",         "Video Title Ideas",      gen_video_titles,         ["original_title"]),
    ("newsletter",           "Email Newsletter",       gen_newsletter,           ["title"]),
    ("podcast_notes",        "Podcast Show Notes",     gen_podcast_notes,        ["title"]),
    ("thumbnail_ideas",      "Thumbnail Concepts",     gen_thumbnail_ideas,      ["title"]),
    ("ctas",                 "Call-to-Actions",        gen_ctas,                 []),
]


def generate_all(transcript: str, title: str, duration: int,
                 provider: AIProvider,
                 progress_cb=None) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    total = len(CONTENT_TASKS)
    for i, (key, label, func, extra_args) in enumerate(CONTENT_TASKS):
        if progress_cb:
            progress_cb(i, total, label)
        kwargs: dict = {"transcript": transcript, "provider": provider}
        if "title" in extra_args or "original_title" in extra_args:
            kwargs["title"] = title
        if "duration" in extra_args:
            kwargs["duration"] = duration
        try:
            text, pt, ct = func(**kwargs)
            results[key] = {"content": text, "prompt_tokens": pt,
                            "completion_tokens": ct, "error": None}
        except Exception as exc:
            results[key] = {"content": "", "prompt_tokens": 0,
                            "completion_tokens": 0, "error": str(exc)}
    if progress_cb:
        progress_cb(total, total, "Complete")
    return results
