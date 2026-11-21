// Nibras · editorial collage (ref: jordans.archivess "Change") — 24 fps, paper ↔ black, duotone, light streaks, object ring, word cards
const DUR = 14;
const C = { paper: '#EFEDE8', ink: '#141414', orange: '#F2641C', warm: '#FFB46B', cyan: '#39D7FF', blue: '#2F6BFF', navy: '#1F2A6B' };
const AR = (w, s, fam = 'Plex') => `${w} ${s}px ${fam}`;
let I = {};

function arWords(words, x, y, size, t0, step, { color = C.ink, hot = [], fam = 'Plex', gap = 22 } = {}) {
  ctx.save(); ctx.direction = 'rtl'; ctx.textBaseline = 'middle';
  const fonts = words.map((w, i) => hot.includes(i) ? AR(400, size * 1.2, 'Ami') : AR(700, size, fam));
  const ws = words.map((w, i) => { ctx.font = fonts[i]; return ctx.measureText(w).width; });
  let cx = x + (ws.reduce((a, b) => a + b, 0) + gap * (words.length - 1)) / 2;
  words.forEach((w, i) => {
    const p = seg(T, t0 + i * step, t0 + i * step + .18);
    if (p > 0) { ctx.save(); ctx.font = fonts[i]; ctx.textAlign = 'right'; ctx.globalAlpha = clamp(p * 2);
      ctx.translate(cx, y + (1 - eox(p)) * 40); ctx.fillStyle = hot.includes(i) ? C.orange : color; ctx.fillText(w, 0, 0); ctx.restore(); }
    cx -= ws[i] + gap;
  });
  ctx.restore();
}
function cursor(x, y, h, color = '#fff') { if (Math.floor(T * 2.4) % 2 === 0) { ctx.fillStyle = color; ctx.fillRect(x, y - h / 2, 6, h); } }
// cyan/blue anamorphic light streak sweeping across, p 0..1
function streak(p, y = H * .45) {
  if (p <= 0 || p >= 1) return; const x = lerp(-300, W + 300, eio(p));
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (const [c, sx, sy, a] of [[C.blue, 900, 160, .55], [C.cyan, 520, 60, .8], ['#ffffff', 220, 18, 1]]) {
    ctx.save(); ctx.translate(x, y); ctx.scale(sx / 100, sy / 100); const g = ctx.createRadialGradient(0, 0, 0, 0, 0, 100);
    g.addColorStop(0, `rgba(255,255,255,${a})`); g.addColorStop(.25, c); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.globalAlpha = a; ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, 100, 0, 7); ctx.fill(); ctx.restore(); }
  ctx.restore();
  ctx.fillStyle = `rgba(255,255,255,${Math.sin(p * Math.PI) * .35})`; ctx.fillRect(0, 0, W, H);
}
function vignette(dark = false) { const g = ctx.createRadialGradient(W / 2, H / 2, 300, W / 2, H / 2, 1200); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, dark ? 'rgba(0,0,0,.6)' : 'rgba(60,50,40,.18)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }
function img(k, cx, cy, h, { rot = 0, alpha = 1, shadow = true } = {}) { // photo card: white border, rounded, soft shadow
  const im = I[k]; if (!im) return; const w = h * im.width / im.height, b = Math.max(6, h * .025), r = h * .035;
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot); ctx.globalAlpha = alpha;
  if (shadow) { ctx.shadowColor = 'rgba(0,0,0,.3)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 22; }
  ctx.fillStyle = '#fff'; rr(ctx, -w / 2 - b, -h / 2 - b, w + 2 * b, h + 2 * b, r + b); ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.save(); rr(ctx, -w / 2, -h / 2, w, h, r); ctx.clip(); ctx.drawImage(im, -w / 2, -h / 2, w, h); ctx.restore();
  ctx.restore();
}
// warm duotone of an image (silhouette look) on black
function duotone(k, cx, cy, h, p = 1) {
  const im = I[k]; if (!im) return; const w = h * im.width / im.height;
  const L = layer('duo', () => { ctx.clearRect(0, 0, W, H); ctx.filter = 'grayscale(1) contrast(1.5) brightness(1.2)'; ctx.drawImage(im, cx - w / 2, cy - h / 2, w, h); ctx.filter = 'none';
    ctx.globalCompositeOperation = 'multiply'; const g = ctx.createLinearGradient(0, cy - h / 2, 0, cy + h / 2); g.addColorStop(0, '#FF3B1F'); g.addColorStop(.6, '#FF8A1F'); g.addColorStop(1, '#FFD36B'); ctx.fillStyle = g; ctx.fillRect(cx - w / 2, cy - h / 2, w, h); ctx.globalCompositeOperation = 'source-over'; });
  ctx.save(); ctx.globalAlpha = p; ctx.shadowColor = 'rgba(255,110,30,.6)'; ctx.shadowBlur = 80; ctx.drawImage(L, 0, 0); ctx.restore();
}

// ---------- scenes ----------
function sA(t) { // 0-3.3 paper: "how do you show people your home changed?"
  ctx.fillStyle = C.paper; ctx.fillRect(0, 0, W, H); vignette();
  // tiny objects tumble in like the reference opening
  [['wblack', 270, 360, 250, -.12, .1], ['leaf_wood', 830, 380, 360, .1, .25], ['wwood', 250, 1480, 250, .12, .4], ['leaf_black', 830, 1480, 360, -.1, .55]].forEach(([k, x, y, h, r, d]) => {
    const p = spring(seg(t, d, d + .9), 6, 10); if (p > 0) img(k, x, y + (1 - p) * -200, h * p, { rot: r * (1 + Math.sin(t * 2) * .1) }); });
  arWords(['كيف', 'توري', 'الناس'], 540, 820, 120, .25, .2);
  arWords(['إن', 'بيتك', 'تغيّر؟'], 540, 1010, 120, .95, .22, { hot: [2] });
  // hand scribble under the hot word
  const sp = seg(t, 1.7, 2.3); if (sp > 0) doodle([[640, 1110], [560, 1122], [470, 1112], [400, 1126]].map(([x, y]) => [x - 80, y]), { prog: eox(sp), color: C.orange, w: 10, seed: 3 });
  streak(seg(t, 2.95, 3.35));
}
function sB(t) { // 3.3-4.6 black + duotone door: "you don't tell them."
  ctx.fillStyle = '#0b0b0d'; ctx.fillRect(0, 0, W, H);
  duotone('leaf_wood', 700, 980, 1150 + (t - 3.3) * 60, clamp(seg(t, 3.3, 3.6) * 1.2));
  arWords(['ما', 'تقولها.'], 330, 980, 104, 3.45, .2, { color: '#fff' }); if (t > 3.8) cursor(120, 980, 110);
  vignette(true);
}
function sC(t) { // 4.6-5.9 paper, full colour door: "you just show it."
  ctx.fillStyle = C.paper; ctx.fillRect(0, 0, W, H); vignette();
  const p = spring(seg(t, 4.6, 5.2), 6, 9); img('leaf_wood', 730, 980, 1150 * (0.9 + 0.1 * p), {});
  arWords(['تورّيها.'], 190, 980, 120, 4.75, .2, { hot: [0] });
  const sp = seg(t, 5.0, 5.6); if (sp > 0) doodle(ellP(730, 980, 390, 680, 40, -1.4, 1.05), { prog: eox(sp), color: C.orange, w: 9, seed: 7 });
  const f = seg(t, 4.6, 4.75); if (f < 1) { ctx.fillStyle = `rgba(255,255,255,${1 - f})`; ctx.fillRect(0, 0, W, H); }
}
const RING = ['leaf_black', 'wblack', 'leaf_wood', 'logo', 'wwood', 'leaf_white', 'leaf_grey'];
function ring(t, t0) { // rotating collage ring of products
  ctx.fillStyle = C.paper; ctx.fillRect(0, 0, W, H); vignette();
  const step = (t - t0) * 1.4 + spring(seg(t, t0, t0 + .5), 6, 10) * 1.5;
  for (const it of ring3d(RING.length, step, { R: 400, cx: W / 2 })) {
    const k = RING[it.i], h = (k === 'logo' ? 230 : k[0] === 'w' ? 300 : 460) * it.depth;
    ctx.save(); ctx.globalAlpha = clamp(.3 + it.z * .7);
    if (k === 'logo') { ctx.save(); ctx.translate(it.x, 980); ctx.beginPath(); ctx.arc(0, 0, h / 2, 0, 7); ctx.clip(); ctx.drawImage(I.logo, -h / 2, -h / 2, h, h); ctx.restore(); }
    else img(k, it.x, 980 + Math.sin(it.a) * 60, h, { rot: Math.sin(it.a + t) * .06 });
    ctx.restore();
  }
}
function card(t, t0, word, k, glowCol) { // black word card with cursor + one object
  ctx.fillStyle = '#0b0b0d'; ctx.fillRect(0, 0, W, H);
  const p = spring(seg(t, t0, t0 + .5), 7, 11);
  if (glowCol) { ctx.save(); ctx.globalCompositeOperation = 'lighter'; const g = ctx.createRadialGradient(330, 980, 10, 330, 980, 420); g.addColorStop(0, glowCol); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.globalAlpha = p; ctx.fillStyle = g; ctx.fillRect(0, 500, 700, 960); ctx.restore(); }
  img(k, 320, 980, (k[0] === 'w' ? 400 : 720) * (0.7 + 0.3 * p), { rot: (1 - p) * .4, shadow: false });
  ctx.save(); ctx.direction = 'rtl'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.font = AR(700, 110); ctx.fillStyle = '#fff'; ctx.globalAlpha = clamp(p * 1.5); ctx.fillText(word, 600, 985); ctx.restore();
  cursor(580, 985, 120);
  vignette(true);
}
function sE(t) { // 9.6-14 "HOME" with the logo as the O, then contact
  ctx.fillStyle = C.paper; ctx.fillRect(0, 0, W, H); vignette();
  const L = ['H', 'O', 'M', 'E'], xs = [255, 445, 650, 840];
  L.forEach((l, i) => { const p = spring(seg(t, 10.0 + i * .14, 10.6 + i * .14), 7, 10); if (p <= 0) return;
    ctx.save(); ctx.translate(xs[i], 860 - (1 - p) * 140); ctx.globalAlpha = clamp(p * 2);
    if (l === 'O') { ctx.beginPath(); ctx.arc(0, 0, 82 * p, 0, 7); ctx.clip(); ctx.drawImage(I.logo, -82, -82, 164, 164); }
    else { ctx.font = '600 190px "Helvetica Neue", Arial, sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = C.ink; ctx.fillText(l, 0, 8); }
    ctx.restore(); });
  arWords(['النبراس', 'للألمنيوم'], 540, 1090, 78, 10.9, .2, { hot: [1] });
  arWords(['بيتك…', 'نفصّله', 'على', 'ذوقك'], 540, 1230, 60, 11.5, .14, { color: '#555' });
  const b = spring(seg(t, 12.2, 12.8), 7, 9);
  if (b > 0) { ctx.save(); ctx.translate(540, 1420); ctx.scale(b, b); ctx.fillStyle = C.orange; rr(ctx, -330, -62, 660, 124, 62); ctx.fill();
    ctx.font = AR(700, 60, 'Taj'); ctx.direction = 'rtl'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = '#fff'; ctx.fillText('واتساب 0594774046', 0, 4); ctx.restore(); }
  const f = seg(t, 9.6, 9.75); if (f < 1) { ctx.fillStyle = `rgba(255,255,255,${1 - f})`; ctx.fillRect(0, 0, W, H); }
}

function render(t) {
  if (t < 3.3) sA(t);
  else if (t < 4.6) sB(t);
  else if (t < 5.9) sC(t);
  else if (t < 6.05) ring(t, 5.9);
  else if (t < 6.95) card(t, 6.05, 'نور.', 'wblack', 'rgba(255,190,110,.9)');
  else if (t < 7.25) ring(t, 6.95);
  else if (t < 8.2) card(t, 7.25, 'خصوصية.', 'leaf_black', 'rgba(60,110,255,.6)');
  else if (t < 8.5) ring(t, 8.2);
  else if (t < 9.45) card(t, 8.5, 'هدوء.', 'wwood', 'rgba(57,215,255,.45)');
  else if (t < 9.6) ring(t, 9.45);
  else sE(t);
  if (t > 5.8 && t < 5.95) streak(seg(t, 5.8, 5.95), H * .5);
  grain(t, .09);
}
startFilm({ dur: DUR, render, setup: async () => {
  for (const f of ['Plex', 'Ami', 'Taj']) await document.fonts.load(`100px ${f}`, 'بيت');
  I = await loadImages({ leaf_black: 'assets/img/door2.jpg', leaf_wood: 'assets/img/door3.jpg', leaf_white: 'assets/img/door1.jpg', leaf_grey: 'assets/img/door4.jpg', wblack: 'assets/img/win1.jpg', wwood: 'assets/img/win3.jpg', logo: 'assets/logo.png' });
} });
