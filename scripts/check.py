"""Stage 5 — quality check. Produces everything an agent needs to VERIFY the
video with its own eyes before delivering:

  review/contact_sheet.jpg  — tiled frames of the whole video (view this!)
  review/cover.jpg          — cover frame
  review/report.txt         — duration/resolution/loudness + attribution block

Usage: python scripts/check.py <project_dir>
"""
import json
import math
import re
import sys

from common import die, ffprobe_json, load_storyboard, log, project_paths, run


def fps_of(v):
    num, _, den = (v.get("avg_frame_rate") or "30/1").partition("/")
    try:
        return float(num) / float(den or 1)
    except (ValueError, ZeroDivisionError):
        return 0.0


def main(project_dir):
    sb = load_storyboard(project_dir)
    paths = project_paths(project_dir)
    final = paths["final"]
    if not final.exists():
        die("final.mp4 not found — run scripts/compose.py first")
    paths["review"].mkdir(exist_ok=True)

    info = ffprobe_json(final)
    dur = float(info["format"]["duration"])
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)

    # loudness
    p = run(["ffmpeg", "-hide_banner", "-i", final, "-af", "ebur128", "-f", "null", "-"],
            check=False)
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", p.stderr)
    lufs = m[-1] if m else "?"

    # contact sheet: evenly spaced frames extracted individually (reliable),
    # assembled into a labeled grid with Pillow
    from PIL import Image, ImageDraw

    n = 15
    cols = 5
    rows = math.ceil(n / cols)
    tiles = []
    for i in range(n):
        t = dur * (i + 0.5) / n
        f = paths["work"] / f"sheet_{i:02d}.jpg"
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", final,
             "-frames:v", "1", "-vf", "scale=250:-2", f])
        tiles.append((t, f))
    im0 = Image.open(tiles[0][1])
    tw, th = im0.size
    sheet = Image.new("RGB", (cols * tw, rows * (th + 20)), (10, 10, 10))
    d = ImageDraw.Draw(sheet)
    for i, (t, f) in enumerate(tiles):
        sheet.paste(Image.open(f), ((i % cols) * tw, (i // cols) * (th + 20)))
        d.text(((i % cols) * tw + 4, (i // cols) * (th + 20) + th + 3),
               f"t={t:.1f}s", fill=(255, 225, 77))
    sheet.save(paths["review"] / "contact_sheet.jpg", quality=87)
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.4", "-i", final,
         "-frames:v", "1", paths["review"] / "cover.jpg"])

    # attribution block
    credits = []
    if paths["manifest"].exists():
        for mft in json.loads(paths["manifest"].read_text()):
            for s in mft.get("shots") or [mft]:
                if s.get("provider") == "local":
                    continue
                c = f"{s.get('title','')[:60]}".strip() or s.get("file", "")
                credits.append(f"  - {c} — {s.get('creator','')} ({s.get('license','')}) {s.get('source','')}")
    bgm_credit = ""
    bc = paths["root"] / "bgm_credit.json"
    if bc.exists():
        bgm_credit = json.loads(bc.read_text()).get("credit", "")

    lines = [
        f"file:        {final}",
        f"duration:    {dur:.1f}s",
        f"video:       {v['width']}x{v['height']} @ {fps_of(v):.1f}fps {v['codec_name']}",
        f"audio:       {'MISSING!' if not a else a['codec_name'] + ' ' + str(a.get('channels')) + 'ch'}",
        f"loudness:    {lufs} LUFS (target ~ -15)",
        f"size:        {int(info['format']['size']) / 1e6:.1f} MB",
        "",
        "== checks ==",
        f"[{'x' if 20 <= dur <= 95 else '!'}] duration in short-form range (20–95s)",
        f"[{'x' if a else '!'}] has audio stream",
        f"[{'x' if lufs != '?' and abs(float(lufs) + 15) < 2.5 else '!'}] loudness near target",
        "",
        "== attribution (paste into video description) ==",
        bgm_credit,
        *credits,
    ]
    report = "\n".join(lines)
    (paths["review"] / "report.txt").write_text(report)
    print(report)
    log("\n[check] NOW view review/contact_sheet.jpg with your image tool and verify: "
        "captions readable & correctly timed, assets match the narration, no black/blank frames.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        die("usage: python scripts/check.py <project_dir>")
    main(sys.argv[1])
