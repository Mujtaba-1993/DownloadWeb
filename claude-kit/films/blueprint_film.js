// Nibras · "We don't sell pens — we draw windows" · direction B (riso blueprint). Protagonist: the pen from the film.
const DUR = 15.5;
const N = { navy: '#1F2A6B', orange: '#F2641C', ink: '#101114', cream: '#F2ECE1', warm: '#FFD9A0' };
const AR = (w, s, fam = 'Plex') => `${w} ${s}px ${fam}`;
let LOGO = null;

// ---------- helpers ----------
function paperBg(oy = 0) {
  ctx.fillStyle = N.cream; ctx.fillRect(0, 0, W, H);
  ctx.strokeStyle = 'rgba(31,42,107,.08)'; ctx.lineWidth = 2;
  const o = ((oy % 54) + 54) % 54;
  for (let x = 0; x < W; x += 54) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = -o; y < H; y += 54) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
}
// straight-line stroke drawn on by progress p; returns the tip (where the pen is)
function S(pts, p, w = 7, c = N.navy, seed = 1) {
  const q = partial(pts, clamp(p)); if (q.length < 2) return null;
  ctx.save(); ctx.strokeStyle = c; ctx.lineWidth = w; ctx.lineJoin = 'miter'; ctx.lineCap = 'square'; ctx.beginPath();
  q.forEach(([x, y], i) => { const jx = (hash(seed * 13 + i + BOIL) - .5) * 2.2, jy = (hash(seed * 7 + i * 3 + BOIL) - .5) * 2.2; i ? ctx.lineTo(x + jx, y + jy) : ctx.moveTo(x + jx, y + jy); });
  ctx.stroke(); ctx.restore(); return q[q.length - 1];
}
const RECT = (x, y, w, h) => [[x, y], [x + w, y], [x + w, y + h], [x, y + h], [x, y]];
// RTL text revealed right→left like handwriting; returns the writing edge
function writeAr(txt, x, y, font, color, p, { glow = 0 } = {}) {
  if (p <= 0) return null;
  ctx.save(); ctx.font = font; ctx.direction = 'rtl'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  const w = ctx.measureText(txt).width + 40, edge = x + w / 2 - w * clamp(p);
  ctx.beginPath(); ctx.rect(edge, y - 300, w * clamp(p) + 10, 600); ctx.clip();
  ctx.fillStyle = color; ctx.fillText(txt, x, y); ctx.restore();
  return [edge, y + 20];
}
function pen(x, y, rot = -0.9, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  ctx.shadowColor = 'rgba(20,20,40,.25)'; ctx.shadowBlur = 24; ctx.shadowOffsetY = 14;
  ctx.fillStyle = N.ink; rr(ctx, 40, -15, 400, 30, 15); ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.fillStyle = '#c9a45c'; ctx.fillRect(70, -16, 28, 32); ctx.fillRect(300, -21, 120, 7);
  ctx.fillStyle = '#cfcfcf'; ctx.beginPath(); ctx.moveTo(42, -13); ctx.lineTo(0, 0); ctx.lineTo(42, 13); ctx.fill();
  ctx.restore();
}
function risoFill(x, y, w, h, p, col = N.orange, a = .9) { // slams down from the top, misregistered
  if (p <= 0) return; ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = a; ctx.fillStyle = col;
  ctx.fillRect(x + 12, y + 9, w, h * clamp(eback(clamp(p)), 0, 1.08)); ctx.restore();
}
function halftoneRect(x, y, w, h, p, col = 'rgba(31,42,107,.45)') {
  if (p <= 0) return; for (let yy = y + 20; yy < y + h - 10; yy += 22) for (let xx = x + 20; xx < x + w - 10; xx += 22) { const d = (1 + 4 * ((yy - y) / h)) * clamp(p * 1.6 - (yy - y) / h * .6); if (d > 0) disc(xx + ((yy - y) % 44 ? 11 : 0), yy, d, col); }
}
const arNum = n => Math.round(n).toLocaleString('ar-EG', { useGrouping: false });

// ---------- scene 1 · 0 → 2.4 · "ما نبيع أقلام" — the pen arrives and strikes the word ----------
function s1(t, oy = 0) {
  ctx.save(); ctx.translate(0, oy);
  const tip1 = writeAr('احنا ما نبيع', 540, 590, AR(700, 104), N.navy, seg(t, .25, .8));
  const tip2 = writeAr('أقلام', 540, 900, AR(400, 260, 'Ami'), N.navy, seg(t, .75, 1.2));
  const sp = seg(t, 1.3, 1.65); let tip3 = null;
  if (sp > 0) tip3 = S([[770, 925], [310, 885]], eox(sp), 18, N.orange, 9);
  ctx.restore();
  // pen follows the writing; enters from the corner
  const enter = eox(seg(t, 0, .35));
  let px = lerp(1250, 800, enter), py = lerp(-150, 650 + oy, enter);
  const tip = tip3 || tip2 || tip1; if (tip && t > .3) { px = tip[0]; py = tip[1] + oy; }
  if (t > 1.95) { const k = ein(seg(t, 1.95, 2.35)); px = lerp(px, 540, k); py = lerp(py, 1900, k); }
  return [px, py];
}

// ---------- scene 2 · 2.3 → 6.4 · "نبيع نوافذ… تفتح لك الدنيا" — the pen draws a sliding window ----------
const WX = 210, WY = 600, WW = 660, WH = 760;
function s2(t, oy = 0) {
  ctx.save(); ctx.translate(0, oy);
  writeAr('نبيع', 540, 190, AR(700, 100), N.navy, seg(t, 2.55, 2.85));
  writeAr('نوافذ', 540, 350, AR(400, 210, 'Ami'), N.orange, seg(t, 2.85, 3.3));
  let tip = S(RECT(WX, WY, WW, WH), eio(seg(t, 2.5, 3.3)), 10, N.navy, 1);
  const slide = eio(seg(t, 4.4, 5.3)); // right sash slides over the left one
  // the world outside: sun rising behind the opening
  if (slide > 0) {
    ctx.save(); ctx.beginPath(); ctx.rect(WX + WW / 2, WY, WW / 2, WH); ctx.clip();
    const sy = lerp(WY + WH + 200, WY + WH * .42, eox(seg(t, 4.6, 5.6)));
    ctx.fillStyle = 'rgba(242,100,28,.18)'; ctx.fillRect(WX + WW / 2, WY, WW / 2, WH);
    for (let yy = sy - 160; yy < sy + 160; yy += 18) for (let xx = WX + WW * .75 - 160; xx < WX + WW * .75 + 160; xx += 18) { const d = Math.hypot(xx - (WX + WW * .75), yy - sy); if (d < 150) disc(xx, yy, 6 * (1 - d / 170), N.orange); }
    S([[WX + WW / 2, WY + WH * .7], [WX + WW, WY + WH * .7]], 1, 4, N.navy, 30);
    ctx.restore();
  }
  const m = S([[WX + WW / 2, WY], [WX + WW / 2, WY + WH]], seg(t, 3.3, 3.5), 8, N.navy, 2); tip = m || tip;
  const sx = -slide * (WW / 2 - 24);
  const a = S(RECT(WX + 24, WY + 24, WW / 2 - 36, WH - 48), seg(t, 3.5, 3.9), 4, N.navy, 3); tip = a || tip;
  halftoneRect(WX + 24, WY + 24, WW / 2 - 36, WH - 48, seg(t, 4.0, 4.4));
  ctx.save(); ctx.translate(sx, 0);
  risoFill(WX + WW / 2 + 12, WY + 24, WW / 2 - 36, WH - 48, seg(t, 3.95, 4.25));
  const b = S(RECT(WX + WW / 2 + 12, WY + 24, WW / 2 - 36, WH - 48), seg(t, 3.5, 3.9), 4, N.navy, 4);
  ctx.restore(); if (b && t < 3.95) tip = [b[0] + sx, b[1]];
  // dimension lines with counting numbers
  const dp = seg(t, 4.2, 4.6);
  S([[WX, WY - 70], [WX + WW, WY - 70]], dp, 3, N.navy, 7); S([[WX + WW + 70, WY], [WX + WW + 70, WY + WH]], dp, 3, N.navy, 10);
  if (dp > 0) { ctx.save(); ctx.font = AR(700, 44); ctx.fillStyle = N.navy; ctx.textAlign = 'center'; ctx.fillText(arNum(1500 * eox(dp)), WX + WW / 2, WY - 100);
    ctx.translate(WX + WW + 120, WY + WH / 2); ctx.rotate(-Math.PI / 2); ctx.fillText(arNum(1800 * eox(dp)), 0, 0); ctx.restore(); }
  const tt = writeAr('تفتح لك الدنيا', 540, 1500, AR(400, 110, 'Ami'), N.navy, seg(t, 4.5, 5.4));
  if (t > 4.4 && t < 5.4) tip = [WX + WW / 2 + 40 + sx, WY + WH * .5]; else if (tt && t >= 5.4) tip = tt;
  ctx.restore();
  return tip ? [tip[0], tip[1] + oy] : [540, 1900];
}

// ---------- scene 3 · 6.4 → 10 · "وأبواب… تستقبل فيها أهلك" — the pen draws a door that opens ----------
const DX = 330, DY = 560, DW = 420, DH = 880;
function s3(t) {
  writeAr('وأبواب', 540, 330, AR(400, 220, 'Ami'), N.orange, seg(t, 6.6, 7.1));
  let tip = S([[DX, DY + DH], [DX, DY], [DX + DW, DY], [DX + DW, DY + DH], [DX - 60, DY + DH], [DX + DW + 60, DY + DH]], eio(seg(t, 6.6, 7.5)), 12, N.navy, 21);
  const open = eio(seg(t, 8.2, 8.9));
  // warm opening behind the leaf
  if (open > 0) { risoFill(DX, DY, DW, DH, open * 1.2, N.orange, .55); ctx.save(); ctx.globalAlpha = open; const g = ctx.createRadialGradient(DX + DW / 2, DY + DH * .45, 20, DX + DW / 2, DY + DH * .45, 520); g.addColorStop(0, 'rgba(255,240,210,.95)'); g.addColorStop(1, 'rgba(255,217,160,0)'); ctx.fillStyle = g; ctx.fillRect(DX, DY, DW, DH); ctx.restore(); }
  // family drawn inside the light
  const fam = [[DX + DW * .32, 1.0], [DX + DW * .55, 1.15], [DX + DW * .74, .8]];
  fam.forEach(([fx, s], i) => { const p = seg(t, 8.6 + i * .15, 9.1 + i * .15); if (p <= 0) return; const hy = DY + DH - 270 * s;
    S(ellP(fx, hy, 34 * s, 34 * s, 24, -1.6, 1), p, 6, N.navy, 40 + i);
    S([[fx - 50 * s, DY + DH - 10], [fx - 40 * s, hy + 60 * s], [fx + 40 * s, hy + 60 * s], [fx + 50 * s, DY + DH - 10]], p, 6, N.navy, 50 + i); });
  // the leaf: closed rectangle → swings outward (perspective trapezoid hinged on the left)
  const lw = DW * (1 - .78 * open), lift = 70 * open;
  const leaf = [[DX, DY], [DX + lw, DY - lift], [DX + lw, DY + DH + lift], [DX, DY + DH], [DX, DY]];
  const lp = seg(t, 7.4, 7.7);
  if (lp > 0) { ctx.save(); ctx.globalAlpha = .92 * clamp(lp * 2); ctx.fillStyle = '#2a2d33'; ctx.beginPath(); leaf.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.fill(); ctx.restore(); }
  for (let i = 0; i < 5; i++) { const fy = .22 + i * .12, p = seg(t, 7.6 + i * .06, 7.8 + i * .06); const y0 = lerp(DY, DY + DH, fy);
    const yl = y => lerp(y, lerp(DY - lift, DY + DH + lift, (y - DY) / DH), 1);
    const q = S([[DX + 30 * (1 - open * .8), y0], [DX + lw * .7, yl(y0)]], p, 7, '#BFD2DE', 60 + i); if (q && t < 7.95) tip = q; }
  const hp = seg(t, 7.95, 8.15); const hx = DX + lw * .86;
  const h = S([[hx, lerp(DY + DH * .3, DY + DH * .3 - lift * .4, 1)], [hx, DY + DH * .62 + lift * .3]], hp, 9, '#E6E6E6', 70); if (h && t < 8.2) tip = h;
  const tt = writeAr('تستقبل فيها أهلك', 540, 1610, AR(400, 104, 'Ami'), N.navy, seg(t, 8.4, 9.4));
  if (t > 8.15 && t < 8.4) tip = [hx, DY + DH * .5]; if (tt && t >= 8.4) tip = tt;
  return tip || [540, 1900];
}

// ---------- scene 4 · 10 → 15.5 · logo, title block, stamp, WhatsApp ----------
function s4(t) {
  paperBg(t * 20);
  const lp = spring(seg(t, 10.35, 11.2), 6, 10);
  if (LOGO && lp > 0) { ctx.save(); ctx.translate(540, 560); ctx.scale(lp, lp); ctx.beginPath(); ctx.arc(0, 0, 150, 0, 7); ctx.clip(); ctx.drawImage(LOGO, -150, -150, 300, 300); ctx.restore(); }
  let tip = S(ellP(540, 560, 178, 178, 60, -1.6, 1), eio(seg(t, 10.4, 11.0)), 6, N.navy, 80);
  const bp = seg(t, 10.9, 11.5);
  const b = S([...RECT(110, 860, 860, 230), [540, 860], [540, 1090]], bp, 5, N.navy, 81); if (b) tip = b;
  const w1 = writeAr('النبراس للألمنيوم', 755, 975, AR(700, 56), N.navy, seg(t, 11.1, 11.7)); if (w1 && t < 11.7) tip = w1;
  writeAr('الدمام · الشرقية', 325, 975, AR(400, 52, 'Ami'), N.orange, seg(t, 11.6, 12.0));
  // stamp slam on "المعاينة مجانية"
  const st = seg(t, 12.35, 12.75);
  if (st > 0) { const s = lerp(2.2, 1, eback(st)); ctx.save(); ctx.translate(540, 1300); ctx.rotate(-.12); ctx.scale(s, s); ctx.globalAlpha = clamp(st * 3);
    ctx.globalCompositeOperation = 'multiply'; ctx.strokeStyle = N.orange; ctx.lineWidth = 10; rr(ctx, -330, -95, 660, 190, 26); ctx.stroke();
    ctx.font = AR(700, 96); ctx.direction = 'rtl'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = N.orange; ctx.fillText('المعاينة مجانية', 6, 8); ctx.restore(); }
  const w2 = writeAr('واتساب 0594774046', 540, 1560, AR(700, 78, 'Taj'), N.navy, seg(t, 13.3, 14.2)); if (w2 && t < 14.3) tip = w2;
  if (t >= 14.3) { const u = S([[300, 1625], [780, 1625]], seg(t, 14.3, 14.8), 8, N.orange, 90); if (u) tip = u; }
  return tip || [800, 1700];
}

function render(t) {
  let pp;
  if (t < 2.4) {                                  // s1, then camera pans down the sheet into s2
    const pan = ein(seg(t, 1.95, 2.4)) * -H;
    paperBg(-pan); pp = s1(t, pan);
    if (pan < 0) { ctx.save(); ctx.translate(0, pan + H); s2(t); ctx.restore(); }
  } else if (t < 5.75) { paperBg(H); pp = s2(t); }
  else if (t < 6.45) {                            // zoom through the open window into the door sheet
    const p = seg(t, 5.75, 6.45);
    zoomThrough(() => { paperBg(H); s2(5.75); }, () => { paperBg(0); s3(6.45); }, p, { cx: WX + WW * .75, cy: WY + WH * .45, hole: 150, maxZoom: 14, flash: .15 });
    pp = [lerp(WX + WW * .75, 540, p), lerp(WY + WH * .5, 1900, p)];
  } else if (t < 10.1) { paperBg(0); pp = s3(t); }
  else if (t < 10.4) {                            // everything collapses into the nib
    const p = ein(seg(t, 10.1, 10.4)); paperBg(0);
    ctx.save(); ctx.translate(540, 560); ctx.scale(1 - p * .97, 1 - p * .97); ctx.translate(-540, -560); s3(10.1); ctx.restore(); pp = [540, 560];
  } else pp = s4(t);
  // the protagonist pen
  const bob = Math.sin(t * 9) * 4;
  if (pp) pen(pp[0], pp[1] + bob, -0.9 + Math.sin(t * 3) * .05, t > 10.1 && t < 10.5 ? 1 + Math.sin(seg(t, 10.1, 10.5) * Math.PI) * .3 : 1);
  grain(t, .07);
}
startFilm({ dur: DUR, render, setup: async () => {
  for (const f of ['Plex', 'Ami', 'Taj']) await document.fonts.load(`100px ${f}`, 'نبيع');
  LOGO = await new Promise(r => { const i = new Image(); i.onload = () => r(i); i.onerror = () => r(null); i.src = 'assets/logo.png'; });
} });
