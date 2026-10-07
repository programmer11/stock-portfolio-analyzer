import json
import subprocess
from pathlib import Path
import imageio_ffmpeg
from PIL import Image,ImageDraw

root=Path(__file__).resolve().parent
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
video=root/'stock-portfolio-demo.mp4'
result=subprocess.run([ffmpeg,'-hide_banner','-i',str(video)],capture_output=True,text=True)
print(result.stderr)
assert 'Video: h264' in result.stderr
assert 'Audio: aac' in result.stderr
timeline=json.loads((root/'timeline.json').read_text())
assert 60<=timeline['duration']<=120
decoded=subprocess.run([ffmpeg,'-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True)
assert decoded.returncode==0,decoded.stderr
assert not decoded.stderr,decoded.stderr
volume=subprocess.run([ffmpeg,'-hide_banner','-i',str(video),'-vn','-af','volumedetect','-f','null','-'],capture_output=True,text=True)
print('\n'.join(x for x in volume.stderr.splitlines() if 'volume:' in x))
assert 'max_volume: -inf' not in volume.stderr
sheet=Image.new('RGB',(800,1080),'#0c172a')
for i,scene in enumerate(timeline['scenes']):
    frame=root/'assets'/f'verified-{i+1}.png'
    subprocess.run([ffmpeg,'-y','-v','error','-ss',str(scene['start']+1),'-i',str(video),'-frames:v','1',str(frame)],check=True)
    img=Image.open(frame).resize((400,270))
    sheet.paste(img,((i%2)*400,(i//2)*270))
sheet.save(root/'contact-sheet.jpg')
print(f'PASS: all frames decode; H.264 video and AAC audio; {timeline["duration"]} seconds; {video.stat().st_size/1e6:.1f} MB.')
