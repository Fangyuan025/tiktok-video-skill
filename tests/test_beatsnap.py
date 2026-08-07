"""Offline test: compose.plan_timeline snaps scene and shot cuts onto the
beat grid without ever eating into the voiceover. No ffmpeg, no network.

Run: python tests/test_beatsnap.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from compose import MIN_PAD, MIN_SHOT, plan_timeline  # noqa: E402

FPS = 30
sb = {"fps": FPS, "beat_sync": True,
      "scenes": [{"badge": None}, {"badge": None}, {"badge": None}]}
timing = {
    1: {"audio_dur": 4.6, "vo_end": 4.10},
    2: {"audio_dur": 5.1, "vo_end": 4.55},
    3: {"audio_dur": 3.9, "vo_end": 3.30},
}
manifest = {1: [{}, {}], 2: [{}, {}], 3: [{}]}   # shots per scene
# steady 120 BPM grid
beats_info = {"bpm": 120.0, "confidence": 5.0,
              "beats": [round(0.5 * k, 3) for k in range(1, 90)]}

plan, synced = plan_timeline(sb, timing, manifest, beats_info)
assert synced

grid = set(beats_info["beats"])


def on_beat(t, tol=1.5 / FPS):
    return any(abs(t - b) <= tol for b in grid)


cum = 0.0
for spec, si in zip(plan, (1, 2, 3)):
    vo_trim = spec["vo_trim"]
    # VO never truncated: scene holds at least the voiceover plus minimal pad
    assert spec["scene_dur"] + 1e-6 >= vo_trim + MIN_PAD, (si, spec)
    cum += spec["scene_dur"]
    if si < 3:  # every scene boundary lands on a beat (within one video frame)
        assert on_beat(cum), f"scene {si} boundary {cum} off-beat"
    # intra-scene shot cuts land on beats and respect the minimum shot length
    acc = 0
    for f in spec["fsplit"][:-1]:
        acc += f
        assert f >= MIN_SHOT * FPS - 1, spec
        cut = cum - spec["scene_dur"] + acc / FPS
        assert on_beat(cut), f"shot cut {cut} in scene {si} off-beat"

# without beats: natural pacing, no snapping
plan2, synced2 = plan_timeline(sb, timing, manifest, None)
assert not synced2
assert abs(plan2[0]["scene_dur"] - (timing[1]["vo_end"] + 0.24 + 0.12)) < 1 / FPS

# low confidence grid is ignored
_, synced3 = plan_timeline(sb, timing, manifest, {**beats_info, "confidence": 0.5})
assert not synced3

print("beat snapping OK")
