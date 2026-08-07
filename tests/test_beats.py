"""Beat detection accuracy on a synthetic 120 BPM click track (needs ffmpeg).

Run: python tests/test_beats.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from beats import analyze  # noqa: E402

tmp = Path(tempfile.mkdtemp()) / "click120.wav"
subprocess.run(
    ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
     "-i", "aevalsrc='sin(880*2*PI*t)*lt(mod(t,0.5),0.06)':s=22050:d=30", str(tmp)],
    check=True)

r = analyze(tmp)
gaps = [round(b - a, 4) for a, b in zip(r["beats"], r["beats"][1:])]
mean = sum(gaps) / len(gaps)
var = sum((g - mean) ** 2 for g in gaps) / len(gaps)
assert abs(r["bpm"] - 120) < 1.5, f"BPM {r['bpm']} (expected ~120)"
assert abs(mean - 0.5) < 0.01, f"mean gap {mean}"
assert var ** 0.5 < 0.02, f"jittery grid (std {var ** 0.5:.4f})"
assert r["confidence"] >= 2, r["confidence"]
print(f"beat detection OK ({r['bpm']} BPM, gap std {var ** 0.5 * 1000:.1f}ms)")
