---
name: tiktok-video
description: >
  Generate complete TikTok / Douyin(抖音) / YouTube Shorts / Reels short videos
  from a one-line brief, end to end: script writing, free stock footage & image
  download, TTS voiceover (Chinese & English), word-level karaoke captions,
  background music, and ffmpeg composition into a finished 1080x1920 MP4.
  Use when the user asks to create, make, or generate a short video
  (短视频/抖音视频/TikTok video) on any topic.
---

# TikTok / Douyin Short Video Generator

You (the agent) do the **creative** work — script, scene breakdown, search
keywords, style choices, and quality review. The scripts in `scripts/` do the
**mechanical** work — TTS with word timestamps, asset search & download,
caption rendering, ffmpeg composition, loudness normalization.

Everything runs with core ffmpeg only (no libass/drawtext needed) plus a
Python venv. Works with zero API keys; `PEXELS_API_KEY` / `PIXABAY_API_KEY`
env vars unlock real stock video clips (better) when present.

## Workflow

### 0. One-time setup (skip if `.venv/` and `assets/fonts/` exist)

```bash
bash scripts/setup.sh
```

### 1. Write the script + storyboard

Read `references/writing-guide.md` for the script formulas (hook types,
pacing, scene structure). Then create `projects/<slug>/storyboard.json`:

```json
{
  "title": "深海里最诡异的5种生物",
  "lang": "zh",
  "aspect": "9:16",
  "voice": "zh-CN-YunjianNeural",
  "rate": "+10%",
  "caption_style": "karaoke",
  "bgm": {"mood": "mystery", "gain_db": -16},
  "hook": {"text": "深海禁区", "seconds": 2.3},
  "scenes": [
    {
      "text": "你知道吗?在阳光永远照不到的深海,藏着比科幻电影更诡异的生物。",
      "keywords": ["deep sea NOAA ocean exploration", "submarine dark ocean"],
      "providers": ["openverse", "wikimedia"],
      "badge": null,
      "effect": "kb_in"
    },
    {
      "text": "第一名,鮟鱇鱼……",
      "keywords": ["humpback anglerfish", "anglerfish museum"],
      "badge": "第1名"
    }
  ]
}
```

Field reference:

| field | values | notes |
|---|---|---|
| `lang` | `zh` \| `en` | sets caption grouping + default voice |
| `aspect` | `9:16` (default) \| `16:9` \| `1:1` | |
| `voice` | any edge-tts voice | zh: `zh-CN-YunjianNeural`(磁性男声) `zh-CN-XiaoxiaoNeural`(女声) `zh-CN-YunxiNeural`(阳光男声); en: `en-US-ChristopherNeural` `en-US-AriaNeural` `en-US-GuyNeural` |
| `rate` | e.g. `+10%` | 营销号 pacing: zh `+8%`~`+15%`, en `+5%`~`+10%` |
| `caption_style` | `karaoke` \| `pop` \| `none` | karaoke = word-by-word highlight (recommended) |
| `bgm` | `{"mood": ...}` \| `{"file": "path.mp3"}` \| `{"mood":"none"}` | moods: upbeat funny inspiring chill tech mystery epic sad horror |
| `hook` | `{"text","seconds"}` | big top title card shown at the start, ≤ 8 chars/words |
| `sticky_title` | `{"text": ...}` | optional persistent topic bar at the top; off by default — only add if the user asks for one |
| `sfx` | `true` (default) \| `false` | whoosh sound on scene transitions |
| scene `keywords` | list of **English, concrete-noun** queries | **each entry = one shot (visual)**; the video cuts to a new visual every ~3s, so give 2–3 queries for scenes longer than ~4s (extra shots are auto-added cycling your queries if you give fewer) |
| scene `badge` | e.g. `"第1名"` / `"TOP 1"` | big stamped label shown at the scene start — use for listicles |
| scene `providers` | list | keyless: `openverse` `wikimedia` `nasa`; with keys: `pexels_video` `pexels_photo` `pixabay_video` |
| scene `effect` | `auto` `kb_in` `kb_out` `pan_left` `pan_right` `static` | first shot's Ken Burns motion; later shots auto-cycle |
| scene `emphasis` | list of substrings | permanently highlighted words (pop style) |
| scene `media` | file path | bypass search, use your own file (e.g. one you downloaded yourself) |

**Rules of thumb (publish bar): total 45–75s, 6–9 scenes, one idea per scene,
2–3 shots per scene.** Scene text 20–45 Chinese chars / 14–30 English words.
Anything under ~40s or with single-shot scenes throughout will feel thin — don't
ship it.

### 2. Run the pipeline

```bash
.venv/bin/python scripts/pipeline.py projects/<slug>
```

Or stage by stage: `tts.py` → `assets.py` → `bgm.py` → `compose.py` → `check.py`.

### 3. REVIEW — this is what makes the difference (mandatory)

Free-image search is imperfect. **Always view these two files with your image
tool and judge them like a human editor:**

1. `projects/<slug>/media/assets_sheet.jpg` — after the assets stage.
   Shots are labeled `01a 01b 02a …`. For every shot that does not clearly
   match the narration, refetch it:

   ```bash
   .venv/bin/python scripts/assets.py projects/<slug> --scene 3 --shot 2 --keywords "better english nouns"
   ```

   (Refetching automatically blacklists the rejected asset. Repeat until all
   scenes match. You may also download an image yourself with your own tools
   and point scene `media` at it.)

2. `projects/<slug>/review/contact_sheet.jpg` — after compose+check.
   Verify: captions readable & synced, no wrong/ugly frames, hook visible.
   Fix issues (edit storyboard → rerun compose, it's fast) until it looks
   like a video a 营销号 editor would actually publish.

`review/report.txt` contains duration/loudness checks and a ready-to-paste
**attribution block** (CC-BY sources + music credit) — always give it to the
user together with `final.mp4`.

### Asset search tips (biggest quality lever)

- Keywords must be **English**, 1–4 words, **concrete visible nouns**
  ("humpback anglerfish", "scuba diver silhouette"), never abstract concepts
  ("mystery", "success").
- `wikimedia` is best for animals/science/history/places; `openverse`
  (Flickr etc.) for lifestyle/scenery/mood; `nasa` for space; keys unlock
  `pexels_video`/`pixabay_video` real footage — prefer those when available.
- Add a context word to disambiguate: "NOAA", "museum", "aquarium", "macro".
- If a scene keeps failing, change the visual concept, not just the words
  (e.g. for "5% explored" show a diver silhouette, not "statistics").

### Troubleshooting

- `edge-tts` network errors: it retries 4×; rerun `tts.py` if it still fails.
- BGM download fails: rerun `bgm.py` (retries + cache), or `--mood none`,
  or drop an mp3 into `assets/bgm/` and set `bgm.file`.
- A provider erroring/empty is fine — others cover it; check per-scene logs.
- Recompose after any storyboard edit is cheap (`--skip-tts --skip-assets`
  via pipeline.py, or run compose.py directly). Changing scene *text*
  requires rerunning `tts.py`.
- Emoji in captions render on macOS (Apple Color Emoji); on Linux they are
  dropped unless NotoColorEmoji is installed. Never rely on emoji for meaning.

### Deliver

Give the user: `final.mp4`, the attribution block from `review/report.txt`,
and (if asked) `review/cover.jpg` as the cover image.
