"""Assemble a Remotion image sequence using the app's compatible FFmpeg."""
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "voiceover.json").read_text())
TIMING = json.loads((ROOT / "voiceover-timing.json").read_text())
FRAMES = ROOT / "out" / "american-frames"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
OUTPUT = ROOT.parent / "demo" / "stock-portfolio-american.mp4"

assert CONFIG["audioDirectory"] == "american", "Select the American narration before exporting."
assert len(list(FRAMES.glob("element-*.jpeg"))) == TIMING["totalFrames"]
inputs = [FFMPEG, "-y", "-framerate", "30", "-i", str(FRAMES / "element-%04d.jpeg")]
filters = []
for index, (scene, timing) in enumerate(zip(CONFIG["scenes"], TIMING["scenes"])):
    inputs += ["-i", str(ROOT / "public" / "audio" / "american" / (scene["asset"] + ".mp3"))]
    duration = timing["frames"] / 30
    filters.append(f"[{index + 1}:a]aresample=48000,apad,atrim=duration={duration:.9f},asetpts=PTS-STARTPTS[a{index}]")
filters.append("".join(f"[a{i}]" for i in range(len(CONFIG["scenes"]))) + f"concat=n={len(CONFIG['scenes'])}:v=0:a=1[audio]")
command = inputs + [
    "-filter_complex", ";".join(filters), "-map", "0:v", "-map", "[audio]",
    "-frames:v", str(TIMING["totalFrames"]), "-c:v", "libx264", "-preset", "fast",
    "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
    "-movflags", "+faststart", str(OUTPUT),
]
subprocess.run(command, check=True)
print(f"Created {OUTPUT}", flush=True)
