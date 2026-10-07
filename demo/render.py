"""Build a narrated MP4 from real app captures; run with the project venv."""
import json
import re
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SCENES = [
 ('01-input', 'Your trades. Your portfolio. One clear view.', 'Welcome to Stock Portfolio Analyzer. Turn your transaction history into a clear picture of what you own, how your investments are allocated, and how your portfolio has performed.'),
 ('02-loaded', '01  Import your transaction history', 'Start in Input Transactions. Upload a CSV with the ticker, date, buy or sell type, quantity, and price. Here, we load the included sample data: trades in Apple, Microsoft, and Tesla.'),
 ('03-manual', '02  Add trades manually', 'You can also enter an individual trade. Choose the date and transaction type, then enter the symbol, quantity, and price per share. Review the details, then use Add transaction to save it.'),
 ('04-portfolio', '03  See what you own today', 'Next, open Current Portfolio. The summary shows the value of your remaining shares, their cost basis, unrealized gains, and profit already realized through sales. The allocation chart shows how much each stock contributes.'),
 ('05-breakdown', '04  Understand each holding', 'The stock breakdown lets you compare quantities, average cost, prices, gains, and allocation. This demo uses last transaction prices, with live pricing switched off. The Price Source column makes that clear.'),
 ('06-performance', '05  Check your lifetime returns', 'Historical Performance brings the full journey together: total investment, sales, remaining value, and total return. X I R R is the annualized return that accounts for the timing of each buy and sell.'),
 ('07-trend', '06  Follow value over time', 'Finally, compare portfolio value with net money invested over time. With live pricing off, this chart uses transaction prices. Enable Yahoo Finance pricing for market data when available.'),
 ('08-close', 'Import trades → Explore holdings → Track performance', 'That is Stock Portfolio Analyzer: import your trades, understand your holdings, and track performance in one place. Try the sample portfolio to explore the app before adding your own transactions.'),
]

def run(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

def font(size):
    return ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', size)

def timestamp(seconds):
    ms=round(seconds*1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'

timeline=[]
subtitles=[]
elapsed=0
for index,(name,title,narration) in enumerate(SCENES):
    print(f'Rendering {index+1}/8: {name}',flush=True)
    txt=ASSETS/f'{name}.txt'
    txt.write_text(narration)
    audio=ASSETS/f'{name}.aiff'
    if '--reuse-audio' not in sys.argv or not audio.exists():
        run(['say','-v','Samantha','-r','165','-f',str(txt),'-o',str(audio)])
    probe=subprocess.run([FFMPEG,'-i',str(audio)],capture_output=True,text=True).stderr
    match=re.search(r'Duration: (\d+):(\d+):([\d.]+)',probe)
    assert match,probe
    hours,minutes,seconds=map(float,match.groups())
    duration=hours*3600+minutes*60+seconds+0.65
    canvas=Image.new('RGB',(1600,1080),'#0c172a')
    canvas.paste(Image.open(ASSETS/f'{name}.png').convert('RGB'),(0,95))
    draw=ImageDraw.Draw(canvas)
    draw.text((42,28),title,font=font(31),fill='white')
    draw.text((42,1018),'SAMPLE PORTFOLIO  •  Last-trade prices  •  Live pricing off',font=font(23),fill='#b9c6dc')
    draw.text((1440,1018),f'{index+1:02} / 08',font=font(23),fill='#b9c6dc')
    draw.rectangle((0,1073,int(1600*(index+1)/8),1079),fill='#4e9cff')
    image=ASSETS/f'{name}-framed.png'
    canvas.save(image)
    segment=ASSETS/f'{name}.mp4'
    if '--refresh-framing' not in sys.argv or name in ['05-breakdown','07-trend']:
        run([FFMPEG,'-y','-loop','1','-framerate','24','-i',str(image),'-i',str(audio),'-t',str(duration),'-vf','fade=t=in:st=0:d=0.3','-af','apad','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000',str(segment)])
    chunks=re.split(r'(?<=[.!?])\s+',narration)
    weights=[len(x.split()) for x in chunks]
    total=sum(weights)
    cursor=elapsed
    for chunk,weight in zip(chunks,weights):
        end=cursor+(duration-0.65)*weight/total
        subtitles.append(f'{len(subtitles)+1}\n{timestamp(cursor)} --> {timestamp(end)}\n{chunk}\n')
        cursor=end
    timeline.append({'scene':name,'title':title,'start':round(elapsed,2),'duration':round(duration,2),'narration':narration})
    elapsed+=duration

listing=ASSETS/'concat.txt'
listing.write_text(''.join(f"file '{name}.mp4'\n" for name,_,_ in SCENES))
run([FFMPEG,'-y','-f','concat','-safe','0','-i',str(listing),'-c','copy','-movflags','+faststart',str(ROOT/'stock-portfolio-demo.mp4')])
(ROOT/'stock-portfolio-demo.srt').write_text('\n'.join(subtitles))
(ROOT/'timeline.json').write_text(json.dumps({'duration':round(elapsed,2),'scenes':timeline},indent=2))
(ROOT/'narration.txt').write_text('\n\n'.join(f'{title}\n{narration}' for _,title,narration in SCENES))
assert 60<=elapsed<=120,elapsed
print(f'Created video: {elapsed:.2f}s',flush=True)
