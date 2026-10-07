"""Regenerate local Mac narration and synchronize the Remotion timeline."""
from pathlib import Path
import json, math, re, subprocess

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "voiceover.json").read_text())
# Use the parent app's existing imageio-ffmpeg installation.
import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
OUTPUT = ROOT / "public" / "audio" / "american"
OUTPUT.mkdir(parents=True, exist_ok=True)
frames = []
for scene in CONFIG["scenes"]:
    text = OUTPUT / (scene["asset"] + ".txt")
    source = OUTPUT / (scene["asset"] + ".aiff")
    target = OUTPUT / (scene["asset"] + ".mp3")
    text.write_text(scene["text"])
    subprocess.run(["say", "-v", CONFIG["voice"], "-r", str(CONFIG["rate"]), "-f", str(text), "-o", str(source)], check=True)
    assert source.is_file() and source.stat().st_size > 1000, source
    subprocess.run([FFMPEG, "-y", "-i", str(source), "-c:a", "libmp3lame", "-b:a", "160k", str(target)], check=True, capture_output=True)
    probe = subprocess.run([FFMPEG, "-i", str(target)], capture_output=True, text=True).stderr
    duration = re.search(r"Duration: (\d+):(\d+):([\d.]+)", probe)
    assert duration, target
    hours, minutes, seconds = map(float, duration.groups())
    seconds += hours * 3600 + minutes * 60
    count = math.ceil((seconds + CONFIG["pauseSeconds"]) * 30)
    frames.append(count)
    print(scene["component"], f"{seconds:.2f}s audio; {count} frames", flush=True)
composition = ROOT / "src" / "Composition.tsx"
content = composition.read_text()
for scene, count in zip(CONFIG["scenes"], frames):
    name = scene["component"]
    content, changes = re.subn(r'(name="' + name + r'" durationInFrames=)\{\d+\}', lambda m: m[1] + "{" + str(count) + "}", content)
    assert changes == 1
    content, changes = re.subn(r'(id="' + name + r'"[^\n]*durationInFrames=)\{\d+\}', lambda m: m[1] + "{" + str(count) + "}", content)
    assert changes == 1
content, changes = re.subn(r'(id="StockPortfolioDemo"[^\n]*durationInFrames=)\{\d+\}', lambda m: m[1] + "{" + str(sum(frames)) + "}", content)
assert changes == 1
composition.write_text(content)
(ROOT / "voiceover-timing.json").write_text(json.dumps({"fps": 30, "totalFrames": sum(frames), "durationSeconds": sum(frames)/30, "scenes": [{"component": s["component"], "frames": f} for s, f in zip(CONFIG["scenes"], frames)]}, indent=2) + "\n")
print(f"Total: {sum(frames)/30:.2f}s", flush=True)
