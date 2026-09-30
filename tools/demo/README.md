# Demo GIF

README 데모 GIF(`assets/demo-en.gif`, `assets/demo-ko.gif`)를 다시 만드는 개발 도구. 스킬 자체는 이 도구에 의존하지 않는다.

```bash
node tools/demo/frames.js examples/cobro-mcp/recipes/R-001-cross-tab-drafts/recipe.en.html /tmp/fr-en [gaegu.ttf]
python3 tools/demo/mkgif.py /tmp/fr-en assets/demo-en.gif 128 none
```

필요: Playwright(Chromium), Pillow. 레시피의 `window.renderAt(t, boil)`로 시각을 정해 캡처하므로 매번 같은 결과가 나온다.
