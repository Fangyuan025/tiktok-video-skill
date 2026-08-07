"""Offline test: content-level (sha1) dedupe in assets.fetch_shot.

Two candidates with DIFFERENT URLs but IDENTICAL bytes — the second fetch must
reject the duplicate and, having no other candidates, exit non-zero.
No network, no ffmpeg: gather/download/media_info are stubbed.

Run: python tests/test_dedupe.py
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import assets  # noqa: E402

URLS = ["https://mirror-a.example/valdivia.jpg",
        "https://mirror-b.example/other-landing-page/original.jpg"]
SAME_BYTES = b"\xff\xd8identical-engraving-bytes" * 100


def fake_gather(scene, W, H):
    return [{"url": u, "kind": "image", "w": 1200, "h": 1600, "dur": 0,
             "title": "vampire squid engraving", "creator": "t", "license": "CC0",
             "source": u, "provider": "wikimedia"} for u in URLS]


def fake_download(url, dest, **kw):
    Path(dest).write_bytes(SAME_BYTES)
    return True


assets.gather = fake_gather
assets.download = fake_download
assets.media_info = lambda p: ("image", 1200, 1600, 0)

tmp = Path(tempfile.mkdtemp())
(tmp / "media").mkdir()
paths = {"media": tmp / "media"}
sb = {"aspect": "9:16"}
scene = {"keywords": ["vampire squid"], "providers": ["wikimedia"]}
excluded, used_urls, used_hashes = set(), set(), set()

shot1 = assets.fetch_shot(1, 1, "vampire squid", scene, sb, paths,
                          excluded, used_urls, used_hashes)
assert shot1["sha1"], "first shot must record a sha1"
assert shot1["url"] == URLS[0]
assert len(used_hashes) == 1

# second fetch: URL dedupe passes (different URL), sha1 dedupe must reject,
# leaving no candidates -> fetch_shot dies (SystemExit)
try:
    assets.fetch_shot(1, 2, "vampire squid", scene, sb, paths,
                      excluded, used_urls, used_hashes)
except SystemExit:
    pass
else:
    raise AssertionError("duplicate-content candidate was accepted")

assert not (paths["media"] / "scene_01b.jpg").exists(), "dup file must be cleaned up"
assert URLS[1] in excluded, "dup URL must be blacklisted for future runs"
print("content dedupe OK")
