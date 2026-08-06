#!/usr/bin/env bash
# One-time setup for the tiktok-video skill: venv + deps + CJK font.
# Idempotent — safe to rerun.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ERROR: ffmpeg not found. Install it first (macOS: brew install ffmpeg | debian: apt install ffmpeg)"
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found"
  exit 1
fi

if [ ! -x .venv/bin/python ]; then
  echo "[setup] creating venv…"
  python3 -m venv .venv
fi
echo "[setup] installing python deps…"
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q edge-tts requests pillow

mkdir -p assets/fonts assets/bgm
FONT=assets/fonts/NotoSansCJKsc-Black.otf
if [ ! -s "$FONT" ]; then
  echo "[setup] downloading Noto Sans CJK SC Black (~17MB, one time)…"
  curl -fsSL -o "$FONT" \
    "https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Black.otf" \
    || { echo "font download failed — retry or place any bold CJK .otf at $FONT"; exit 1; }
fi

.venv/bin/python - <<'EOF'
from PIL import ImageFont
f = ImageFont.truetype("assets/fonts/NotoSansCJKsc-Black.otf", 40)
print("[setup] font OK:", f.getname())
EOF

echo "[setup] done. Optional: export PEXELS_API_KEY / PIXABAY_API_KEY for stock video clips."
