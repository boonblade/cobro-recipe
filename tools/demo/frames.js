// README 데모 GIF용 프레임 캡처 (개발 도구 — 스킬 의존성 아님)
// 사용: node tools/demo/frames.js <recipe.html> <out-dir> [gaegu.ttf]
//   Playwright 필요. gaegu.ttf를 주면 폰트를 로컬로 공급한다(오프라인 캡처).
// 구간: 제목 → 문제 → 실패 → 발견(줌인) → 마무리(줌아웃·교훈). 880×770, 10fps 기준.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [file, out, font] = process.argv.slice(2);
(async () => {
  fs.rmSync(out, { recursive: true, force: true }); fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch();
  const p = await (await b.newContext({ viewport: { width: 880, height: 770 } })).newPage();
  if (font) {
    await p.route('https://fonts.googleapis.com/**', r => r.fulfill({ contentType: 'text/css',
      body: "@font-face{font-family:'Gaegu';font-weight:700;src:url(https://fonts.gstatic.com/gaegu.ttf) format('truetype');}" }));
    await p.route('https://fonts.gstatic.com/**', r => r.fulfill({ contentType: 'font/ttf', body: fs.readFileSync(font) }));
  }
  await p.goto('file://' + path.resolve(file));
  await p.evaluate(() => { window.recipeNoVignette = true; });   // 색 수가 적은 GIF에서 음영이 띠로 깨지지 않게
  await p.waitForTimeout(2500);
  const tl = await p.evaluate(() => window.recipeTimeline()), S = tl.scenes;
  const segs = [[0, S[0].hop[0], .16], [S[0].hop[0], S[0].part + 2.6, .28], [S[3].hop[0], S[3].part + 2.4, .28],
                [S[4].hop[0], S[4].part + 3.2, .3], [tl.outro, tl.D, .26]];
  let n = 0;
  for (const [a, z, dt] of segs) for (let t = a; t < z; t += dt) {
    await p.evaluate(([t, k]) => { window.renderAt(t, k); document.getElementById('play').textContent = '❚❚'; }, [t, Math.floor(n / 3)]);
    await p.screenshot({ path: `${out}/${String(n++).padStart(4, '0')}.png` });
  }
  console.log('frames', n); await b.close();
})();
