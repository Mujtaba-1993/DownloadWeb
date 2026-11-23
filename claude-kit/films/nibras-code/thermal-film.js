// Nibras · "Thermal camera" — the room seen in heat. Everything drawn in canvas; render(t) is pure.
const W = 1080, H = 1920, DUR = 16.4; window.DUR = DUR;
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x)), seg = (t, a, b) => clamp((t - a) / (b - a)), lerp = (a, b, p) => a + (b - a) * p;
const eio = p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2, eo = p => 1 - Math.pow(1 - p, 3);
const back = p => { const c = 1.9; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); };
const ORANGE = '#F2641C', ISO = [43, 209, 74], VERDICT = '#7DFFA0', LO = 20, HI = 45, THR = 35;

// ---------- iron palette LUT ----------
const STOPS = ['#000008', '#120554', '#4D0894', '#991294', '#DB3352', '#FA7812', '#FFBF21', '#FFFADB'].map(h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16)));
const LUT = new Uint8ClampedArray(256 * 3);
for (let i = 0; i < 256; i++) { const x = i / 255 * (STOPS.length - 1), k = Math.min(STOPS.length - 2, Math.floor(x)), f = x - k; for (let c = 0; c < 3; c++) LUT[i * 3 + c] = lerp(STOPS[k][c], STOPS[k + 1][c], f); }
const ironCSS = v => { const i = Math.round(clamp(v) * 255) * 3; return `rgb(${LUT[i]},${LUT[i + 1]},${LUT[i + 2]})`; };

// ---------- noise ----------
function hash(x, y) { let h = Math.imul(x | 0, 374761393) + Math.imul(y | 0, 668265263) | 0; h = Math.imul(h ^ h >>> 13, 1274126177); return ((h ^ h >>> 16) >>> 0) / 4294967296; }
function vn(x, y) { const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi, u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf); const a = hash(xi, yi), b = hash(xi + 1, yi), c = hash(xi, yi + 1), d = hash(xi + 1, yi + 1); return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v; }

// ---------- the room (world px, 1080 x 1920) ----------
const FX0 = 240, FX1 = 840, FY0 = 520, FY1 = 1300, FW = 40, FLOOR = 1600;
function temp(x, y, t, s) {
  let T; const inOuter = x >= FX0 && x <= FX1 && y >= FY0 && y <= FY1;
  if (y > FLOOR) {
    T = 25.2 + .6 * vn(x / 90, y / 90); const k = (y - FLOOR) / 320, xl = lerp(300, 170, k), xr = lerp(780, 910, k);
    if (x > xl && x < xr && k < 1) T += 8.2 * (1 - k * .55) * clamp((x - xl) / 40) * clamp((xr - x) / 40);
  } else if (inOuter) {
    const glass = x > FX0 + FW && x < FX1 - FW && y > FY0 + FW && y < FY1 - FW && !(x > 520 && x < 560);
    T = glass ? 31.2 + 1.8 * (1 - (y - FY0) / (FY1 - FY0)) + .4 * vn(x / 70, y / 70) : 28.6 - 2.4 * s + .5 * vn(x / 40, y / 40);
  } else {
    T = 24 + 1.4 * (1 - y / FLOOR) + .35 * vn(x / 120, y / 120);
    T += 2.4 * clamp((y - 455) / 18) * clamp((FY0 - y) / 6) * clamp((x - FX0 + 70) / 20) * clamp((FX1 + 70 - x) / 20);   // concrete lintel (bridge)
    if (y > FLOOR - 40) T -= .8;                                                                                              // skirting
  }
  const L = 1 - s; if (L > 0) {
    const dx = Math.max(FX0 - x, 0, x - FX1), dy = Math.max(FY0 - y, 0, y - FY1);
    let d = Math.hypot(dx, dy); if (inOuter) d = Math.max(0, 12 - Math.min(x - FX0, FX1 - x, y - FY0, FY1 - y)) > 0 ? 0 : 99;
    const cd = Math.min(Math.hypot(x - FX0, y - FY0), Math.hypot(x - FX1, y - FY0), Math.hypot(x - FX0, y - FY1), Math.hypot(x - FX1, y - FY1));
    const leak = 12.5 * Math.exp(-d / 13) * (1 + .8 * Math.exp(-cd * cd / 4200)) * (.72 + .5 * vn(x / 22 + t * .35, y / 22));
    let plume = 0; if (y < FY0 && y > 120) { const h = FY0 - y; plume = 9 * Math.exp(-h / 190) * clamp((x - FX0 + 40) / 60) * clamp((FX1 + 40 - x) / 60) * (.35 + .95 * vn(x / 55, y / 70 + t * 1.1)); }
    T = Math.min(T + L * (leak + plume), 43.2 + .6 * vn(x / 30, y / 30 + t));
  }
  return T;
}

// ---------- sensor: field -> iron image ----------
const SCALE = 6, sensors = {};
function thermal(cam, sAt, rx, ry, rw, rh, t, iso) {
  const sw = Math.round(rw / SCALE), sh = Math.round(rh / SCALE), key = sw + 'x' + sh;
  if (!sensors[key]) { const c = document.createElement('canvas'); c.width = sw; c.height = sh; sensors[key] = { c, x: c.getContext('2d'), im: c.getContext('2d').createImageData(sw, sh) }; }
  const S = sensors[key], D = S.im.data, fi = Math.round(t * 30), tq = Math.floor(t * 30) / 30;
  for (let j = 0; j < sh; j++) for (let i = 0; i < sw; i++) {
    const sx = rx + (i + .5) * rw / sw, sy = ry + (j + .5) * rh / sh;
    const wx = cam.x + (sx - rx - rw / 2) / cam.z, wy = cam.y + (sy - ry - rh / 2) / cam.z;
    let T = temp(wx, wy, tq, sAt(sx, sy)) + (hash(i + fi * 977, j + fi * 131) - .5) * .3 + (hash(i, 7) - .5) * .18;
    const u = i / sw - .5, v = j / sh - .5; T -= .9 * (u * u + v * v);
    const o = (j * sw + i) * 4;
    if (iso && T > THR) { D[o] = ISO[0]; D[o + 1] = ISO[1]; D[o + 2] = ISO[2]; }
    else { const k = Math.round(clamp((T - LO) / (HI - LO)) * 255) * 3; D[o] = LUT[k]; D[o + 1] = LUT[k + 1]; D[o + 2] = LUT[k + 2]; }
    D[o + 3] = 255;
  }
  S.x.putImageData(S.im, 0, 0);
  ctx.save(); ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high'; ctx.filter = 'blur(2px)'; ctx.drawImage(S.c, rx - 3, ry - 3, rw + 6, rh + 6); ctx.restore();
}

// ---------- the visible picture ----------
function visible(cam) {
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(cam.z, cam.z); ctx.translate(-cam.x, -cam.y);
  let g = ctx.createLinearGradient(0, 0, 0, FLOOR); g.addColorStop(0, '#d9cbb3'); g.addColorStop(1, '#eadfcc'); ctx.fillStyle = g; ctx.fillRect(-400, -400, 1880, FLOOR + 400);
  g = ctx.createLinearGradient(0, FLOOR, 0, 2300); g.addColorStop(0, '#b89a78'); g.addColorStop(1, '#8a6e52'); ctx.fillStyle = g; ctx.fillRect(-400, FLOOR, 1880, 900);
  ctx.fillStyle = '#f4efe6'; ctx.fillRect(-400, FLOOR - 40, 1880, 40);
  ctx.fillStyle = 'rgba(255,236,190,.55)'; ctx.beginPath(); ctx.moveTo(300, FLOOR); ctx.lineTo(780, FLOOR); ctx.lineTo(910, 1920); ctx.lineTo(170, 1920); ctx.fill();   // sun patch
  g = ctx.createLinearGradient(0, FY0, 0, FY1); g.addColorStop(0, '#5fa8e8'); g.addColorStop(1, '#cfe6f5'); ctx.fillStyle = g; ctx.fillRect(FX0, FY0, FX1 - FX0, FY1 - FY0);
  const sun = ctx.createRadialGradient(720, 640, 10, 720, 640, 260); sun.addColorStop(0, 'rgba(255,255,240,1)'); sun.addColorStop(.25, 'rgba(255,245,200,.7)'); sun.addColorStop(1, 'rgba(255,245,200,0)'); ctx.fillStyle = sun; ctx.fillRect(FX0, FY0, FX1 - FX0, FY1 - FY0);
  ctx.fillStyle = '#3d4a3a'; ctx.beginPath(); ctx.moveTo(360, FY1 - 40); ctx.quadraticCurveTo(372, 960, 352, 820); ctx.lineTo(364, 820); ctx.quadraticCurveTo(388, 960, 380, FY1 - 40); ctx.fill();   // palm
  for (let a = 0; a < 7; a++) { const an = -Math.PI / 2 + (a - 3) * .42; ctx.beginPath(); ctx.moveTo(358, 822); ctx.quadraticCurveTo(358 + Math.cos(an) * 90, 822 + Math.sin(an) * 70 - 20, 358 + Math.cos(an) * 170, 822 + Math.sin(an) * 70 + 40); ctx.lineWidth = 14; ctx.strokeStyle = '#3d4a3a'; ctx.stroke(); }
  ctx.fillStyle = '#c7c9cc'; ctx.strokeStyle = '#9a9da2'; ctx.lineWidth = 3;
  [[FX0, FY0, FX1 - FX0, FW], [FX0, FY1 - FW, FX1 - FX0, FW], [FX0, FY0, FW, FY1 - FY0], [FX1 - FW, FY0, FW, FY1 - FY0], [520, FY0, 40, FY1 - FY0]].forEach(r => { ctx.fillRect(...r); ctx.strokeRect(...r); });
  ctx.fillStyle = '#efe7da'; ctx.fillRect(FX0 - 70, FY0 - 65, FX1 - FX0 + 140, 18); ctx.fillRect(FX0 - 40, FY1, FX1 - FX0 + 80, 22);
  ctx.restore();
}

// ---------- camera ----------
const CAM = [[0, 540, 930, 1.0], [2.6, 540, 930, 1.06, 'lin'], [2.6, 560, 900, 1.12, 'cut'], [4.9, 570, 890, 1.2, 'lin'], [4.9, 790, 575, 2.35, 'cut'], [7.8, 800, 570, 2.55, 'lin'], [7.8, 540, 930, 1.05, 'cut'], [10.9, 540, 930, 1.08, 'lin']];
function cam(t) { let i = 0; while (i < CAM.length - 1 && CAM[i + 1][0] <= t) i++; const a = CAM[i], b = CAM[Math.min(i + 1, CAM.length - 1)]; if (a === b || b[4] === 'cut') return { x: a[1], y: a[2], z: a[3] }; let p = seg(t, a[0], b[0]); if (b[4] !== 'lin') p = eio(p); return { x: lerp(a[1], b[1], p), y: lerp(a[2], b[2], p), z: lerp(a[3], b[3], p) }; }
const w2s = (c, x, y, rx = 0, ry = 0, rw = W, rh = H) => [rx + rw / 2 + (x - c.x) * c.z, ry + rh / 2 + (y - c.y) * c.z];

// ---------- overlays ----------
function txt(s, x, y, size, o = {}) { ctx.save(); ctx.font = `${size}px ${o.font || 'Plex'}`; ctx.textAlign = o.align || 'center'; ctx.textBaseline = 'middle'; ctx.direction = o.ltr ? 'ltr' : 'rtl'; ctx.globalAlpha = o.a == null ? 1 : o.a; ctx.lineJoin = 'round'; ctx.strokeStyle = 'rgba(0,0,0,.75)'; ctx.lineWidth = o.halo == null ? size * .16 : o.halo; ctx.strokeText(s, x, y); ctx.fillStyle = o.c || '#fff'; ctx.fillText(s, x, y); ctx.restore(); }
function typed(s, x, y, size, p, o = {}) { if (p <= 0) return; ctx.save(); ctx.font = `${size}px ${o.font || 'Plex'}`; const w = ctx.measureText(s).width + 40; ctx.beginPath(); if (o.ltr) ctx.rect(x - w / 2, y - size, w * p, size * 2); else ctx.rect(x + w / 2 - w * p, y - size, w * p, size * 2); ctx.clip(); txt(s, x, y, size, o); ctx.restore(); }
const reading = (x, y, t, s) => temp(x, y, Math.floor(t * 6) / 6, s);
const BAND = (() => { const p = []; for (let i = 0; i <= 40; i++) { const x = lerp(FX0, FX1, i / 40); p.push([x, FY0 - 4], [x, FY1 + 4]); } for (let i = 0; i <= 50; i++) { const y = lerp(FY0, FY1, i / 50); p.push([FX0 - 4, y], [FX1 + 4, y]); } return p; })();
const bandMax = (t, s) => Math.max(...BAND.map(([x, y]) => reading(x, y, t, s)));
function crosshair(x, y, p, label, val, o = {}) {
  if (p <= 0) return; const r = lerp(140, 26, eo(p)); ctx.save(); ctx.strokeStyle = o.c || '#fff'; ctx.lineWidth = 3; ctx.shadowColor = '#000'; ctx.shadowBlur = 6;
  ctx.beginPath(); [[-1, 0], [1, 0], [0, -1], [0, 1]].forEach(([a, b]) => { ctx.moveTo(x + a * r, y + b * r); ctx.lineTo(x + a * (r + 22), y + b * (r + 22)); }); ctx.stroke();
  ctx.strokeRect(x - 5, y - 5, 10, 10); ctx.restore();
  if (p >= 1 && label) txt(`${label} ${val.toFixed(1)}°C`, x + (o.left ? -50 : 50), y - 52, 38, { font: 'Taj', ltr: 1, align: o.left ? 'right' : 'left', c: o.c });
}
function box(x0, y0, x1, y1, label, val, o = {}) { ctx.save(); ctx.strokeStyle = o.c || '#fff'; ctx.lineWidth = o.lw || 3; ctx.shadowColor = '#000'; ctx.shadowBlur = 6; ctx.setLineDash(o.dash || []); ctx.strokeRect(x0, y0, x1 - x0, y1 - y0); ctx.restore(); txt(`${label}  MAX ${val.toFixed(1)}°C`, x0 + 8, y0 - 30, 34, { font: 'Taj', ltr: 1, align: 'left', c: o.c }); }
function leader(x0, y0, x1, y1, s, p) { if (p <= 0) return; ctx.save(); ctx.strokeStyle = '#fff'; ctx.lineWidth = 2.5; ctx.shadowColor = '#000'; ctx.shadowBlur = 5; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(lerp(x0, x1, eo(p)), lerp(y0, y1, eo(p))); ctx.stroke(); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(x0, y0, 6, 0, 7); ctx.fill(); ctx.restore(); typed(s, x1, y1 - 34, 44, seg(p, .5, 1)); }
function hud(t, iso) {
  const g = ctx.createLinearGradient(0, 560, 0, 1360); for (let i = 0; i <= 10; i++) g.addColorStop(i / 10, ironCSS(1 - i / 10));
  ctx.fillStyle = g; ctx.fillRect(1010, 560, 30, 800); ctx.strokeStyle = 'rgba(255,255,255,.8)'; ctx.lineWidth = 2; ctx.strokeRect(1010, 560, 30, 800);
  if (iso) { const y = lerp(1360, 560, (THR - LO) / (HI - LO)); ctx.fillStyle = `rgb(${ISO})`; ctx.fillRect(1004, 560, 42, y - 560); ctx.globalAlpha = .0; }
  ctx.globalAlpha = 1; txt('45.0', 1025, 525, 30, { font: 'Taj', ltr: 1 }); txt('20.0', 1025, 1395, 30, { font: 'Taj', ltr: 1 }); txt('°C', 1025, 1435, 26, { font: 'Taj', ltr: 1, a: .8 });
  const sec = String(7 + Math.floor(t)).padStart(2, '0'); txt(`JUL 14  15:02:${sec}`, 40, 1860, 30, { font: 'Taj', ltr: 1, align: 'left', a: .9 });
  txt('OUT 48.6°C', 40, 1815, 30, { font: 'Taj', ltr: 1, align: 'left', a: .9 }); txt('IR  20–45°C', 1040, 1860, 30, { font: 'Taj', ltr: 1, align: 'right', a: .9 });
  if (iso) txt(`ISO > ${THR}°C`, 1040, 1815, 30, { font: 'Taj', ltr: 1, align: 'right', c: `rgb(${ISO})` });
}
const SUBS = [[0, 2.55, 'لو تشوف بيتك بكاميرا حرارية…'], [2.75, 4.85, 'هنا يدخل الحر'], [5.0, 7.75, 'من الفراغات حول الشباك القديم'], [7.9, 10.85, 'قطاع محكم وجلد مطاطي… والحر يبقى برّا'], [11.0, 13.3, 'نفس الغرفة… نفس الحر برّا']];
function subs(t) { const s = SUBS.find(s => t >= s[0] && t < s[1]); if (s) typed(s[2], W / 2, 250, 60, seg(t, s[0], s[0] + .35)); }
function scanLine(x, warmLeft) { ctx.save(); const g = ctx.createLinearGradient(x - 60, 0, x + 60, 0); g.addColorStop(warmLeft ? 0 : 1, 'rgba(250,120,18,0)'); g.addColorStop(.5, 'rgba(250,150,40,.35)'); g.addColorStop(warmLeft ? 1 : 0, 'rgba(250,120,18,0)'); ctx.fillStyle = g; ctx.fillRect(x - 60, 0, 120, H); ctx.fillStyle = '#fff'; ctx.shadowColor = '#fff'; ctx.shadowBlur = 18; ctx.fillRect(x - 2, 0, 4, H); ctx.restore(); }

// ---------- frame ----------
function render(t) {
  t = Math.round(t * 30) / 30; ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  if (t < 10.9) {
    const c = cam(t);
    const sx = t < 7.8 ? -1 : W - W * eio(seg(t, 8.3, 9.8));                                  // install scan (right -> left)
    const sAt = (x) => t < 8.3 ? 0 : (x > sx ? 1 : 0);
    const iso = t >= 3.35 && t < 4.9;
    const open = W * eio(seg(t, 0, 1.4));                                                      // opening scan (left -> right)
    if (open < W) { visible(c); ctx.save(); ctx.beginPath(); ctx.rect(0, 0, open, H); ctx.clip(); thermal(c, sAt, 0, 0, W, H, t, iso); ctx.restore(); scanLine(open, true); }
    else thermal(c, sAt, 0, 0, W, H, t, iso);
    if (t >= 8.3 && t < 9.8) scanLine(sx, false);
    hud(t, iso);
    // wall spot -> tracker jump to the hottest corner
    if (t >= 1.0 && t < 4.9) {
      if (t < 2.8) { const [x, y] = w2s(c, 540, 1460); crosshair(x, y, seg(t, 1.0, 1.35), 'SP1', reading(540, 1460, t, 0)); }
      else { const [x, y] = w2s(c, 846, 514), v = reading(846, 514, t, 0), r = seg(t, 2.8, 3.2); crosshair(x, y, seg(t, 2.8, 3.05), 'MAX', lerp(24.2, v, eo(r)), { left: 1 }); }
    }
    if (t >= 3.6 && t < 4.9) { const [a, b] = w2s(c, FX0 - 30, FY0 - 30), [d, e] = w2s(c, FX1 + 30, FY1 + 30); box(a, b, d, e, 'BX1', bandMax(t, 0)); }
    if (t >= 4.9 && t < 7.8) {
      const [gx, gy] = w2s(c, FX1 + 4, 700), [px, py] = w2s(c, 760, 400);
      leader(gx, gy, 720, 1250, 'فراغ حول الإطار', seg(t, 5.3, 5.9)); leader(px, py, 470, 640, 'هواء حار يدخل', seg(t, 6.2, 6.8));
    }
    if (t >= 9.9) { const [a, b] = w2s(c, FX0 - 30, FY0 - 30), [d, e] = w2s(c, FX1 + 30, FY1 + 30), p = seg(t, 9.9, 10.2); ctx.globalAlpha = p; box(a, b, d, e, 'BX1', bandMax(t, 1), { c: VERDICT, lw: 4 }); ctx.globalAlpha = 1; }
  } else if (t < 13.4) {                                                                       // same scale, two times
    const c = { x: 540, y: 920, z: .8 }, half = 1135, R1 = 320, RH = 780;
    thermal(c, () => 0, 0, R1, W, RH, t, true); thermal(c, () => 1, 0, half, W, RH, t, false);
    ctx.fillStyle = '#fff'; ctx.fillRect(0, half - 5, W, 10);
    const [a1, b1] = w2s(c, FX0 - 30, FY0 - 30, 0, R1, W, RH), [d1, e1] = w2s(c, FX1 + 30, FY1 + 30, 0, R1, W, RH);
    box(a1, b1, d1, e1, 'BEFORE', bandMax(t, 0));
    const [a2, b2] = w2s(c, FX0 - 30, FY0 - 30, 0, half, W, RH), [d2, e2] = w2s(c, FX1 + 30, FY1 + 30, 0, half, W, RH);
    box(a2, b2, d2, e2, 'AFTER', bandMax(t, 1), { c: seg(t, 11.6, 11.7) > 0 ? VERDICT : '#fff', lw: 4 });
    txt('قبل', 950, R1 + 75, 60); txt('بعد', 950, half + 75, 60, { c: seg(t, 11.6, 11.7) > 0 ? VERDICT : '#fff' });
    const p = seg(t, 11.6, 11.85); if (p > 0) { ctx.save(); ctx.strokeStyle = VERDICT; ctx.lineWidth = 8; ctx.globalAlpha = p; ctx.strokeRect(6, half + 6, W - 12, RH - 12); ctx.restore(); }
    hud(t, false);
  } else {                                                                                     // end card: the last warm thing (no voice)
    const tt = t - 13.4, g = ctx.createRadialGradient(540, 960, 100, 540, 960, 1300); g.addColorStop(0, '#2a0a6a'); g.addColorStop(1, '#03011a'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    for (let i = 0; i < 900; i++) { const x = hash(i, 3) * W, y = hash(i, 9) * H; ctx.fillStyle = `rgba(150,60,170,${.08 + .1 * hash(i, Math.round(t * 30))})`; ctx.fillRect(x, y, 6, 6); }
    const heat = seg(tt, .2, 1.0); ctx.save(); ctx.font = '108px Plex'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.direction = 'rtl';
    const gg = ctx.createLinearGradient(0, 700, 0, 820); gg.addColorStop(0, ironCSS(lerp(.35, 1, heat))); gg.addColorStop(1, ironCSS(lerp(.25, .82, heat)));
    ctx.shadowColor = `rgba(250,120,18,${.7 * heat})`; ctx.shadowBlur = 50; ctx.fillStyle = gg; ctx.globalAlpha = seg(tt, 0, .4); ctx.fillText('النبراس للألمنيوم', 540, 760); ctx.restore();
    typed('المعاينة مجانية', 540, 920, 88, seg(tt, .9, 1.4), { font: 'AmiriIt', c: '#FFBF21' });
    const p = seg(tt, 1.5, 1.85); if (p > 0) { const s = back(p); ctx.save(); ctx.translate(540, 1100); ctx.scale(s, s); ctx.fillStyle = ORANGE; ctx.shadowColor = 'rgba(242,100,28,.7)'; ctx.shadowBlur = 40; ctx.beginPath(); ctx.roundRect(-345, -68, 690, 136, 68); ctx.fill(); ctx.shadowBlur = 0; ctx.fillStyle = '#fff'; ctx.textBaseline = 'middle'; ctx.textAlign = 'center'; ctx.font = '58px Plex'; ctx.direction = 'rtl'; ctx.fillText('واتساب', 215, 2); ctx.font = '60px Taj'; ctx.direction = 'ltr'; ctx.fillText('0594774046', -95, 5); ctx.restore(); }
    if (tt >= 2.3) { ctx.save(); ctx.strokeStyle = '#fff'; ctx.lineWidth = 3; ctx.strokeRect(195 - 0, 1022, 690, 156); ctx.restore(); }
    typed('الدمام · الخبر · القطيف', 540, 1290, 44, seg(tt, 2.2, 2.6), { a: .9 });
  }
  subs(t);
}
window.render = render;
window.READY = Promise.all(['58px Plex', '58px AmiriIt', '58px Taj'].map(f => document.fonts.load(f, 'ا0'))).then(() => render(0));
