"""프레임 PNG → GIF (개발 도구 — 스킬 의존성 아님, Pillow 필요)
사용: python3 tools/demo/mkgif.py <frames-dir> <out.gif> [colors=128] [dither=none|fs] [width]
공통 팔레트 하나로 양자화해 프레임 간 색 번쩍임을 막고, 테마 핵심 색은 면적이 작아도 팔레트에 넣는다.
"""
import sys, glob
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
colors = int(sys.argv[3]) if len(sys.argv) > 3 else 128
dither = len(sys.argv) > 4 and sys.argv[4] == 'fs'
files = sorted(glob.glob(src + '/*.png'))
W = int(sys.argv[5]) if len(sys.argv) > 5 else 0
frames = [Image.open(f).convert('RGB') for f in files]
if W: frames = [im.resize((W, round(im.height * W / im.width)), Image.Resampling.LANCZOS) for im in frames]
# 공통 팔레트: 프레임 표본을 이어 붙여 한 번에 양자화
sample = frames[::3]
w, h = sample[0].size
KEY = ['#2F7D4F', '#B2432F', '#C98A2B', '#F5DC5A', '#4F6F95', '#7A5EA3', '#D9EDD6', '#F4D3CB', '#2E2622', '#B4532A']
sw = h // 2   # 테마 핵심 색은 면적이 작아도 팔레트에 꼭 들어가게 큰 견본으로 붙인다
sheet = Image.new('RGB', (w, h * len(sample) + sw))
for i, im in enumerate(sample): sheet.paste(im, (0, i * h))
for k, c in enumerate(KEY): sheet.paste(Image.new('RGB', (w // len(KEY) + 1, sw), c), (k * (w // len(KEY)), h * len(sample)))
pal = sheet.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
d = Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE
q = [im.quantize(palette=pal, dither=d) for im in frames]
durs = [100] * len(q); durs[-1] = 2500          # 마지막 장면(교훈)은 잠시 멈춘다
q[0].save(out, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=True, disposal=1)
import os; print(out, f'{os.path.getsize(out)/1e6:.2f} MB', len(q), 'frames')
