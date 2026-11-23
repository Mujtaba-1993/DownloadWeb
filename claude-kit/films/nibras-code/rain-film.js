// Nibras · "How to let the rain into your house" (reverse tutorial). Bright explainer cards, drawn in canvas. render(t) is pure.
const W = 1080, H = 1920, DUR = 22.4; window.DUR = DUR;
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x)), seg = (t, a, b) => clamp((t - a) / (b - a)), lerp = (a, b, p) => a + (b - a) * p;
const eo = p => 1 - Math.pow(1 - p, 3), eio = p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
const back = p => { const c = 1.7; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); };
function hash(i, j) { let h = Math.imul(i | 0, 374761393) + Math.imul(j | 0, 668265263) | 0; h = Math.imul(h ^ h >>> 13, 1274126177); return ((h ^ h >>> 16) >>> 0) / 4294967296; }
const C = { navy: '#1F2A6B', orange: '#F2641C', dark: '#C2410C', water: '#3D8BFF', waterD: '#1F5FD1', alu: '#C9D0D8', aluD: '#8E99A6', dust: '#D8B77A', dustD: '#B8934F', cream: '#F7F1E6', wood: '#E7D3B5', rug: '#E4572E', gasket: '#23262B', red: '#E53935', green: '#22B07D' };
const B = [3.0, 7.4, 10.9, 13.6, 18.4];
const CX = 90, CY = 400, CW = 900, CH = 840;                    // the card

// ---------- helpers ----------
function rr(x, y, w, h, r, fill, stroke, lw = 4) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); if (fill) { ctx.fillStyle = fill; ctx.fill(); } if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.stroke(); } }
function poly(pts, fill, stroke, lw = 4) { ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); if (fill) { ctx.fillStyle = fill; ctx.fill(); } if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.lineJoin = 'round'; ctx.stroke(); } }
function txt(s, x, y, size, o = {}) { ctx.save(); ctx.font = `${size}px ${o.font || 'Plex'}`; ctx.textAlign = o.align || 'center'; ctx.textBaseline = 'middle'; ctx.direction = o.ltr ? 'ltr' : 'rtl'; ctx.globalAlpha = o.a == null ? 1 : o.a; if (o.shadow) { ctx.shadowColor = 'rgba(0,20,80,.35)'; ctx.shadowBlur = 14; ctx.shadowOffsetY = 4; } ctx.fillStyle = o.c || C.navy; ctx.fillText(s, x, y); ctx.restore(); }
function drop(x, y, r, c = C.water) { ctx.fillStyle = c; ctx.beginPath(); ctx.moveTo(x, y - r * 1.8); ctx.quadraticCurveTo(x + r, y - r * .2, x + r, y + r * .2); ctx.arc(x, y + r * .2, r, 0, Math.PI); ctx.quadraticCurveTo(x - r, y - r * .2, x, y - r * 1.8); ctx.fill(); }
function label(s, x, y, p, o = {}) { if (p <= 0) return; ctx.save(); ctx.globalAlpha = eo(p); ctx.font = `${o.size || 40}px Plex`; ctx.direction = 'rtl'; const w = ctx.measureText(s).width + 40, h = (o.size || 40) * 1.6; const s2 = lerp(.7, 1, back(p)); ctx.translate(x, y); ctx.scale(s2, s2); rr(-w / 2, -h / 2, w, h, h / 2, o.bg || C.navy); ctx.fillStyle = o.c || '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(s, 0, 3); ctx.restore(); }
function arrow(x0, y0, x1, y1, p, c = C.navy) { if (p <= 0) return; const x = lerp(x0, x1, eo(p)), y = lerp(y0, y1, eo(p)); ctx.save(); ctx.strokeStyle = c; ctx.fillStyle = c; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x, y); ctx.stroke(); const a = Math.atan2(y1 - y0, x1 - x0); ctx.beginPath(); ctx.moveTo(x + Math.cos(a) * 6, y + Math.sin(a) * 6); ctx.lineTo(x - Math.cos(a - .5) * 26, y - Math.sin(a - .5) * 26); ctx.lineTo(x - Math.cos(a + .5) * 26, y - Math.sin(a + .5) * 26); ctx.fill(); ctx.restore(); }
function cross(x, y, r, p) { if (p <= 0) return; ctx.save(); ctx.translate(x, y); ctx.scale(back(p), back(p)); ctx.fillStyle = C.red; ctx.beginPath(); ctx.arc(0, 0, r, 0, 7); ctx.fill(); ctx.strokeStyle = '#fff'; ctx.lineWidth = r * .22; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-r * .4, -r * .4); ctx.lineTo(r * .4, r * .4); ctx.moveTo(r * .4, -r * .4); ctx.lineTo(-r * .4, r * .4); ctx.stroke(); ctx.restore(); }
function tick(x, y, r, p) { if (p <= 0) return; ctx.save(); ctx.translate(x, y); ctx.scale(back(p), back(p)); ctx.fillStyle = C.green; ctx.beginPath(); ctx.arc(0, 0, r, 0, 7); ctx.fill(); ctx.strokeStyle = '#fff'; ctx.lineWidth = r * .22; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.beginPath(); ctx.moveTo(-r * .45, 0); ctx.lineTo(-r * .1, r * .35); ctx.lineTo(r * .45, -r * .35); ctx.stroke(); ctx.restore(); }

// ---------- background ----------
function bg(t) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#2A5FEA'); g.addColorStop(1, '#4F90FF'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.strokeStyle = 'rgba(255,255,255,.07)'; ctx.lineWidth = 2; const o = (t * 12) % 60;
  for (let x = -60 + o; x < W; x += 60) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = -60 + o; y < H; y += 60) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
  ctx.strokeStyle = 'rgba(255,255,255,.16)'; ctx.lineWidth = 3;                                   // light rain over the whole frame
  for (let i = 0; i < 46; i++) { const x = hash(i, 1) * W, sp = 900 + hash(i, 2) * 500, y = ((hash(i, 3) * H + t * sp) % (H + 200)) - 100; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - 10, y + 34); ctx.stroke(); }
}

// ---------- scene 1 · the living room, rain leaking in ----------
function s1(t) {
  const z1 = lerp(1.14, 1.3, eo(seg(t, 0, 3))); ctx.translate(330, 600); ctx.scale(z1, z1); ctx.translate(-330, -600);
  rr(0, 0, CW, CH, 0, C.cream); ctx.fillStyle = C.wood; ctx.fillRect(0, 600, CW, 240);
  ctx.strokeStyle = 'rgba(150,110,60,.25)'; ctx.lineWidth = 3; for (let y = 640; y < CH; y += 50) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(CW, y); ctx.stroke(); }
  const g = ctx.createLinearGradient(0, 90, 0, 500); g.addColorStop(0, '#3B4766'); g.addColorStop(1, '#7E8CAA'); rr(190, 90, 520, 410, 6, g);
  const fl = Math.max(0, 1 - Math.abs(t - .1) / .2) + Math.max(0, 1 - Math.abs(t - 1.6) / .12) * .6; if (fl > 0) { ctx.fillStyle = `rgba(255,255,255,${.75 * fl})`; ctx.fillRect(190, 90, 520, 410); }
  ctx.save(); ctx.beginPath(); ctx.rect(190, 90, 520, 410); ctx.clip(); ctx.strokeStyle = 'rgba(220,235,255,.75)'; ctx.lineWidth = 3;
  for (let i = 0; i < 40; i++) { const x = 190 + hash(i, 7) * 560, y = 90 + ((hash(i, 8) * 410 + t * 1100) % 470) - 40; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - 14, y + 40); ctx.stroke(); }
  for (let i = 0; i < 14; i++) { const x = 205 + hash(i, 9) * 490, y = 110 + ((hash(i, 10) * 380 + t * 160) % 380); drop(x, y, 5, 'rgba(220,235,255,.8)'); }
  ctx.restore();
  ctx.lineWidth = 22; ctx.strokeStyle = C.alu; ctx.strokeRect(190, 90, 520, 410); ctx.fillStyle = C.alu; ctx.fillRect(440, 90, 20, 410); ctx.lineWidth = 3; ctx.strokeStyle = C.aluD; ctx.strokeRect(179, 79, 542, 432);
  rr(160, 505, 580, 28, 6, '#FFFFFF', '#D6CCBC', 3);                                                // sill
  const sheet = ctx.createLinearGradient(0, 533, 0, 690); sheet.addColorStop(0, 'rgba(61,139,255,.55)'); sheet.addColorStop(1, 'rgba(61,139,255,.15)'); poly([[180, 533], [214, 533], [222, 690], [176, 690]], sheet);   // water down the wall
  poly([[90, 680], [810, 680], [860, 820], [40, 820]], C.rug); ctx.strokeStyle = 'rgba(255,255,255,.55)'; ctx.lineWidth = 6; ctx.strokeRect(150, 710, 600, 80);
  const pr = 70 + 120 * eo(seg(t, 0, 2.2)); ctx.fillStyle = 'rgba(61,139,255,.75)'; ctx.beginPath(); ctx.ellipse(205, 725, pr * 1.6, pr * .45, 0, 0, 7); ctx.fill();
  for (let k = 0; k < 3; k++) { const u = (t * 1.6 + k / 3) % 1; drop(200, lerp(540, 710, u * u), 9); const rp = (t * 1.6 + k / 3) % 1; if (rp < .25) { ctx.strokeStyle = 'rgba(255,255,255,.8)'; ctx.lineWidth = 3; ctx.beginPath(); ctx.ellipse(205, 725, 20 + rp * 160, 6 + rp * 40, 0, 0, 7); ctx.stroke(); } }
  rr(600, 560, 260, 120, 30, '#6C7A89'); rr(620, 520, 220, 70, 24, '#7F8EA0');                     // sofa
}

// ---------- scene 2 / 5 · the window sill in section ----------
// channel: outer lip x 230-262, inner lip x 618-650, floor y 600-640; weep hole in the outer lip at y 572-598
function section(t, o) {
  rr(0, 0, CW, CH, 0, '#EEF5FF'); ctx.fillStyle = '#DCE9FB'; ctx.fillRect(0, 0, 230, CH);
  txt('برّا', 115, 70, 44, { c: C.waterD }); txt('داخل البيت', 740, 70, 44);
  const g = ctx.createLinearGradient(380, 0, 440, 0); g.addColorStop(0, '#BFE0FF'); g.addColorStop(1, '#9CCBF6'); rr(392, 40, 36, 400, 4, g, '#7FB2E5', 3);    // glass
  rr(350, 430, 120, 74, 10, C.alu, C.aluD, 4); rr(360, 504, 22, 20, 4, C.gasket); rr(438, 504, 22, 20, 4, C.gasket);                                // sash + gaskets
  poly([[230, 520], [262, 520], [262, 600], [618, 600], [618, 470], [650, 470], [650, 640], [230, 640]], C.alu, C.aluD, 5);                          // frame channel
  rr(404, 526, 14, 74, 4, C.aluD);                                                                                                                  // track
  ctx.fillStyle = '#EEF5FF'; ctx.fillRect(228, 572, 36, 26);                                                                                       // weep hole
  ctx.strokeStyle = C.aluD; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(230, 572); ctx.lineTo(262, 572); ctx.moveTo(230, 598); ctx.lineTo(262, 598); ctx.stroke();
  ctx.fillStyle = '#C9B79C'; ctx.fillRect(0, 640, CW, 200); ctx.fillStyle = '#B9A688'; ctx.fillRect(650, 640, CW, 8);                                 // wall/floor below
  // rain hitting the glass and running into the channel
  ctx.strokeStyle = 'rgba(61,139,255,.7)'; ctx.lineWidth = 4; for (let i = 0; i < 14; i++) { const u = (t * 1.3 + i / 14) % 1, x = lerp(40, 388, u), y = 60 + i * 26 + u * 60; ctx.beginPath(); ctx.moveTo(x - 20, y - 8); ctx.lineTo(x, y); ctx.stroke(); }
  for (let k = 0; k < 4; k++) { const u = (t * .9 + k / 4) % 1; drop(386, lerp(90, 500, u), 7); }
  // dust: blows in and plugs the weep hole
  const dp = o.dust; if (dp > 0) {
    for (let i = 0; i < 60; i++) { const s = hash(i, 21), d = clamp(dp * 1.6 - s * .6), x = lerp(-40 - s * 200, 232 + hash(i, 22) * 26, eo(d)), y = lerp(520 + hash(i, 23) * 140, 574 + hash(i, 24) * 22, eo(d)); ctx.fillStyle = hash(i, 25) > .5 ? C.dust : C.dustD; ctx.beginPath(); ctx.arc(x, y, 4 + hash(i, 26) * 4, 0, 7); ctx.fill(); }
    ctx.fillStyle = C.dust; ctx.globalAlpha = clamp(dp * 1.4 - .3); ctx.fillRect(230, 574, 32, 24); ctx.globalAlpha = 1;
    ctx.strokeStyle = 'rgba(255,255,255,.5)'; ctx.lineWidth = 3; for (let i = 0; i < 6; i++) { const y = 470 + i * 40, x = ((t * 500 + i * 140) % 500) - 260; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + 120, y + 6); ctx.stroke(); }   // wind
  }
  // water in the channel
  const lvl = o.level; if (lvl > 0) {
    const top = lerp(600, 470, lvl), wv = t * 6;
    ctx.save(); ctx.beginPath(); ctx.moveTo(262, 600); for (let x = 262; x <= 618; x += 6) ctx.lineTo(x, top + Math.sin(x / 22 + wv) * 4); ctx.lineTo(618, 600); ctx.closePath(); ctx.fillStyle = 'rgba(61,139,255,.8)'; ctx.fill(); ctx.restore();
    rr(404, 526, 14, 74, 4, C.aluD);
  }
  if (o.spill > 0) { const sp = o.spill; ctx.fillStyle = 'rgba(61,139,255,.85)'; poly([[618, 466], [652, 466], [662, 480], [672, lerp(480, 640, eo(sp))], [656, lerp(480, 640, eo(sp))], [650, 482]], 'rgba(61,139,255,.85)');
    ctx.beginPath(); ctx.ellipse(700, 648, 30 + 140 * eo(seg(sp, .3, 1)), 10 + 14 * eo(seg(sp, .3, 1)), 0, 0, 7); ctx.fill();
    for (let k = 0; k < 3; k++) { const u = (t * 2 + k / 3) % 1; drop(668, lerp(490, 630, u), 7); } }
  if (o.drain > 0) { for (let k = 0; k < 5; k++) { const u = (t * 1.4 + k / 5) % 1; drop(lerp(250, 60, u), lerp(586, 700, u * u), 7); } }
}
function s2(t) {
  const tt = t - B[0]; ctx.save(); const z = lerp(1.25, 1.36, seg(tt, 0, 4.4)); ctx.translate(450, 470); ctx.scale(z, z); ctx.translate(-450, -470);
  section(t, { dust: seg(tt, .1, 1.9), level: eio(seg(tt, 2.0, 3.6)), spill: seg(tt, 3.35, 4.3) });
  ctx.restore();
  label('فتحة التصريف', 230, 250, seg(tt, .3, .6), { size: 52 }); arrow(215, 285, 190, 560, seg(tt, .5, .9));
  cross(285, 520, 34, seg(tt, 1.9, 2.15)); label('انسدّت بالغبار', 250, 790, seg(tt, 2.0, 2.3), { bg: C.red, size: 52 });
  label('ويفيض لداخل البيت', 620, 250, seg(tt, 3.5, 3.8), { bg: C.waterD, size: 50 });
}

// ---------- scene 3 · the gasket in the sun ----------
const CRACKS = [[300, 8.6], [470, 9.1], [620, 9.6]];
function s3(t) {
  const tt = t - B[1]; rr(0, 0, CW, CH, 0, '#FFF6E3');
  const sun = 1 + .04 * Math.sin(t * 6); ctx.save(); ctx.translate(740, 150); ctx.rotate(t * .6); ctx.fillStyle = '#FFC531'; for (let i = 0; i < 12; i++) { ctx.rotate(Math.PI / 6); ctx.beginPath(); ctx.roundRect(90, -9, 46 * sun, 18, 9); ctx.fill(); } ctx.beginPath(); ctx.arc(0, 0, 76 * sun, 0, 7); ctx.fill(); ctx.restore();
  ctx.strokeStyle = 'rgba(255,170,40,.35)'; ctx.lineWidth = 4; for (let i = 0; i < 5; i++) { const y = 300 + i * 26, ph = t * 4 + i; ctx.beginPath(); for (let x = 120; x <= 780; x += 10) ctx.lineTo(x, y + Math.sin(x / 40 + ph) * 6); ctx.stroke(); }   // heat shimmer
  rr(80, 470, 740, 130, 16, C.alu, C.aluD, 4); rr(80, 380, 740, 90, 12, '#D9E7F5', '#9CB3CC', 3);                                                    // frame + glass edge
  const age = seg(tt, .6, 1.9), gc = Math.round(lerp(35, 110, age)); rr(110, 440, 680, 46, 23, `rgb(${gc},${gc - 4},${gc - 10})`);              // gasket
  CRACKS.forEach(([x, tc], i) => { const p = seg(t, tc, tc + .18); if (p <= 0) return; ctx.save(); ctx.strokeStyle = '#F7F1E6'; ctx.lineWidth = 6; ctx.lineJoin = 'round'; ctx.beginPath(); const pts = [[x, 440], [x + 10, 452], [x - 8, 463], [x + 9, 474], [x, 486]]; trunc(pts, p).forEach(([a, b], k) => k ? ctx.lineTo(a, b) : ctx.moveTo(a, b)); ctx.stroke(); ctx.restore(); });
  if (tt > 2.4) for (let k = 0; k < 9; k++) { const [x] = CRACKS[k % 3], u = (t * 1.2 + k / 9) % 1; drop(x + 4, lerp(330, 760, u), 9); }
  label('الجلد المطاطي', 450, 570, seg(tt, .3, .6), { size: 56 });
  label('يتشقق', 470, 700, seg(tt, 1.5, 1.8), { bg: C.red, size: 62 });
}
function trunc(pts, p) { if (p >= 1) return pts; let L = 0; const ls = []; for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); ls.push(d); L += d; } let T = L * p; const o = [pts[0]]; for (let i = 1; i < pts.length; i++) { if (T >= ls[i - 1]) { o.push(pts[i]); T -= ls[i - 1]; } else { const k = T / ls[i - 1]; o.push([lerp(pts[i - 1][0], pts[i][0], k), lerp(pts[i - 1][1], pts[i][1], k)]); break; } } return o; }

// ---------- scene 4 · months go by, the puddle grows ----------
const MONTHS = ['سبتمبر', 'أكتوبر', 'نوفمبر'];
function s4(t) {
  const tt = t - B[2]; rr(0, 0, CW, CH, 0, C.cream); ctx.fillStyle = C.wood; ctx.fillRect(0, 560, CW, 280);
  const cx = 300, cy = 150; rr(cx, cy, 300, 320, 24, '#fff', '#D6CCBC', 4); rr(cx, cy, 300, 70, 24, C.red); ctx.fillStyle = C.red; ctx.fillRect(cx, cy + 40, 300, 30);
  const flips = [.15, .6, 1.05]; let shown = 0; flips.forEach((f, i) => { if (tt > f + .35) shown = i + 1; });
  txt(MONTHS[Math.min(2, shown)], cx + 150, cy + 200, 64);
  if (shown >= 2) { ctx.fillStyle = '#9AA8BD'; ctx.beginPath(); ctx.arc(cx + 120, cy + 285, 24, 0, 7); ctx.arc(cx + 160, cy + 275, 32, 0, 7); ctx.arc(cx + 195, cy + 288, 22, 0, 7); ctx.fill(); for (let k = 0; k < 3; k++) drop(cx + 125 + k * 32, cy + 312 + ((t * 80 + k * 9) % 14), 5); }
  flips.forEach((f, i) => { const p = seg(tt, f, f + .45); if (p <= 0 || p >= 1) return; ctx.save(); ctx.translate(cx + 150, cy + 70); ctx.rotate(p * .9); ctx.translate(0, p * p * 420); ctx.globalAlpha = 1 - p; rr(-150, 0, 300, 250, 12, '#fff', '#D6CCBC', 3); txt(MONTHS[Math.max(0, i - 1)] || 'أغسطس', 0, 130, 60); ctx.restore(); });
  const pw = 160 + 300 * seg(tt, 0, 2.7); ctx.fillStyle = 'rgba(61,139,255,.75)'; ctx.beginPath(); ctx.ellipse(450, 700, pw, pw * .22, 0, 0, 7); ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,.6)'; ctx.lineWidth = 3; for (let k = 0; k < 3; k++) { const u = (t * .9 + k / 3) % 1; ctx.globalAlpha = 1 - u; ctx.beginPath(); ctx.ellipse(450, 700, pw * u, pw * .22 * u, 0, 0, 7); ctx.stroke(); } ctx.globalAlpha = 1;
  const sp = seg(tt, 1.3, 1.7); if (sp > 0) { const bob = Math.sin(t * 3.2) * 8, x = 470 + Math.sin(t * .9) * 40; ctx.save(); ctx.translate(x, 690 + bob - (1 - eo(sp)) * 60); ctx.rotate(.25 + Math.sin(t * 2) * .08); rr(-90, -30, 180, 60, 30, '#2BA8A0'); ctx.strokeStyle = '#F2641C'; ctx.lineWidth = 12; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-50, -12); ctx.lineTo(-10, 4); ctx.lineTo(-50, 20); ctx.stroke(); ctx.restore(); }
}

// ---------- scene 5 · rewind, fix, send a photo ----------
function phone(t) {
  const tt = t - 14.9, up = eo(seg(tt, 0, .35)); ctx.save(); ctx.translate(0, (1 - up) * 900);
  rr(200, 60, 500, 760, 56, '#111827'); rr(220, 80, 460, 720, 40, '#ECE5DD'); rr(220, 80, 460, 90, 40, '#1F2A6B'); ctx.fillStyle = '#1F2A6B'; ctx.fillRect(220, 130, 460, 40);
  txt('النبراس للألمنيوم', 450, 126, 34, { c: '#fff' });
  const m1 = seg(tt, .3, .55); if (m1 > 0) { ctx.save(); ctx.globalAlpha = m1; ctx.translate(0, (1 - eo(m1)) * 40); rr(250, 210, 300, 250, 22, '#D9FDD3'); const g = ctx.createLinearGradient(0, 230, 0, 420); g.addColorStop(0, '#5C6B8A'); g.addColorStop(1, '#93A2BF'); rr(266, 226, 268, 190, 14, g); ctx.strokeStyle = C.alu; ctx.lineWidth = 10; ctx.strokeRect(300, 246, 200, 150); ctx.fillStyle = C.alu; ctx.fillRect(396, 246, 8, 150); txt('شباك الصالة', 400, 440, 28); ctx.restore(); }
  const ty = seg(tt, 1.0, 1.15) * (1 - seg(tt, 1.6, 1.7)); if (ty > 0) { rr(400, 500, 140, 64, 30, '#fff'); for (let k = 0; k < 3; k++) { ctx.fillStyle = `rgba(80,90,110,${.4 + .6 * Math.max(0, Math.sin(t * 9 - k))})`; ctx.beginPath(); ctx.arc(440 + k * 30, 532, 9, 0, 7); ctx.fill(); } }
  const m2 = seg(tt, 1.6, 1.85); if (m2 > 0) { ctx.save(); ctx.globalAlpha = m2; ctx.translate(0, (1 - eo(m2)) * 40); rr(300, 500, 360, 150, 22, '#fff'); txt('وصلت الصورة…', 480, 545, 34); txt('بنقولك وين بيدخل المطر', 480, 600, 34, { c: C.dark }); ctx.restore(); }
  ctx.restore();
}
function s5(t) {
  const tt = t - B[3];
  if (t < 14.9) {
    const rw = seg(tt, 0, .5), fix = seg(t, 14.1, 14.9);
    section(t, { dust: t < 14.1 ? 1 - rw : 0, level: t < 14.1 ? 1 - eio(rw) : 0, spill: 0, drain: t >= 14.1 ? 1 : 0 });
    if (t < 14.1) { ctx.fillStyle = 'rgba(31,42,107,.18)'; ctx.fillRect(0, 0, CW, CH); ctx.save(); ctx.translate(450, 300); ctx.fillStyle = '#fff'; for (let k = 0; k < 2; k++) { ctx.beginPath(); ctx.moveTo(-10 + k * 70, -50); ctx.lineTo(-80 + k * 70, 0); ctx.lineTo(-10 + k * 70, 50); ctx.fill(); } ctx.restore();
      ctx.strokeStyle = 'rgba(255,255,255,.6)'; ctx.lineWidth = 3; for (let i = 0; i < 10; i++) { const y = hash(i, 40) * CH, x = ((t * 3000 + i * 260) % 1300) - 200; ctx.beginPath(); ctx.moveTo(CW - x, y); ctx.lineTo(CW - x + 200, y); ctx.stroke(); } }
    else { tick(250, 500, 34, seg(fix, .1, .4)); label('مفتوحة', 250, 770, seg(fix, .2, .5), { bg: C.green, size: 54 }); arrow(220, 660, 70, 740, seg(fix, .2, .6), C.green); }
  } else { rr(0, 0, CW, CH, 0, '#EAF2FF'); phone(t); }
}

// ---------- end card (no voice) ----------
function endCard(t) {
  const tt = t - B[4], p = seg(tt, 0, .14); ctx.save(); ctx.translate(540, 900); const s = lerp(.85, 1, back(p)); ctx.scale(s, s);
  ctx.shadowColor = 'rgba(0,20,80,.35)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 14; rr(-430, -380, 860, 760, 48, '#fff'); ctx.restore();
  txt('النبراس للألمنيوم', 540, 650, 96, { a: seg(tt, .05, .3) });
  txt('المعاينة مجانية', 540, 800, 84, { font: 'AmiriIt', c: C.orange, a: seg(tt, .25, .5) });
  txt('صوّر شباكك من تحت عند المجرى… وأرسله', 540, 905, 44, { c: '#4B5563', a: seg(tt, .4, .65) });
  const q = seg(tt, .5, .8); if (q > 0) { ctx.save(); ctx.translate(540, 1050); const k = back(q) * (1 + .035 * Math.sin(Math.max(0, tt - .9) * 6)); ctx.scale(k, k); rr(-390, -80, 780, 160, 80, C.dark); ctx.fillStyle = '#fff'; ctx.textBaseline = 'middle'; ctx.textAlign = 'center'; ctx.font = '60px Plex'; ctx.direction = 'rtl'; ctx.fillText('واتساب', 250, 3); ctx.font = '80px Taj'; ctx.direction = 'ltr'; ctx.fillText('0594774046', -95, 7); ctx.restore(); }
  txt('الدمام · الخبر · القطيف', 540, 1195, 44, { c: '#6B7280', a: seg(tt, .7, 1.0) });
}

// ---------- header + word-by-word captions ----------
const HEAD = [[0, 'دخّل المطر بيتك'], [B[0], 'داخل الشباك'], [B[1], 'الجلد المطاطي'], [B[2], 'الأرصاد: أمطار فوق المعدل هالشهر'], [B[3], 'الحل']];
const SUBS = [[-3.2, 2.95, 'ودّك المطرة الجاية تدخل صالتك؟ سهلة…', 'صالتك؟'], [3.35, 7.3, 'خلّ غبار العجّة يسد فتحة التصريف', 'يسد'], [7.55, 10.85, 'وركّب جلد رخيص… والشمس تكمّل الباقي', 'رخيص…'],
  [11.0, 13.55, 'ولا تشيك عليه قبل الشتا', 'الشتا'], [13.8, 16.0, 'أو… صوّر شباكك وأرسله لنا', 'صوّر'], [16.4, 18.35, 'ونقولك وين بيدخل المطر', 'المطر']];
function header(t) { if (t >= B[4]) return; const h = [...HEAD].reverse().find(h => t >= h[0]); const p = seg(t, h[0] - (h[0] ? .1 : .5), h[0] + .25); ctx.save(); ctx.globalAlpha = eo(p); ctx.translate(0, (1 - eo(p)) * 20); txt(h[1], 540, h[0] === 0 ? 300 : 320, h[0] === 0 ? 96 : (h[0] === B[2] ? 52 : 60), { c: '#fff', shadow: 1 }); if (h[0] === B[2]) txt('على أجزاء من الشرقية', 540, 372, 38, { c: '#FFE3B3', shadow: 1 }); ctx.restore(); }
function captions(t) {
  const s = SUBS.find(s => t >= s[0] && t < s[1]); if (!s) return; const words = s[2].split(' '), size = 64;
  ctx.save(); ctx.font = `${size}px Plex`; ctx.direction = 'rtl'; const sp = 18, ws = words.map(w => ctx.measureText(w).width);
  const lines = [[]]; let lw = 0; words.forEach((w, i) => { if (lw + ws[i] > 880 && lines[lines.length - 1].length) { lines.push([]); lw = 0; } lines[lines.length - 1].push(i); lw += ws[i] + sp; });
  const dur = (s[1] - s[0]) * .7, tot = s[2].length; let acc = 0; const start = words.map(w => { const v = s[0] + dur * acc / tot; acc += w.length + 1; return v; });
  lines.forEach((ln, li) => { const wide = ln.reduce((a, i) => a + ws[i] + sp, -sp); let x = 540 + wide / 2; const y = 1345 + li * 92;
    ln.forEach(i => { const p = seg(t, start[i], start[i] + .18); if (p > 0) { const key = words[i] === s[3]; ctx.save(); ctx.globalAlpha = eo(p); const k = lerp(.6, 1, back(p)); ctx.translate(x - ws[i] / 2, y); ctx.scale(k, k);
      if (key) { rr(-ws[i] / 2 - 14, -size * .62, ws[i] + 28, size * 1.24, 14, C.orange); }
      ctx.fillStyle = '#fff'; ctx.shadowColor = key ? 'transparent' : 'rgba(0,20,80,.45)'; ctx.shadowBlur = 12; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(words[i], 0, 4); ctx.restore(); }
      x -= ws[i] + sp; }); });
  ctx.restore();
}

// ---------- frame ----------
function render(t) {
  t = Math.round(t * 30) / 30; ctx.setTransform(1, 0, 0, 1, 0, 0); bg(t);
  if (t < B[4]) {
    let d = 1; B.slice(0, 4).forEach(b => { d = Math.min(d, Math.abs(t - b) / .14); }); const sx = Math.max(.02, Math.min(1, d)), pop = seg(t, 0, .01);
    ctx.save(); ctx.translate(540, CY + CH / 2); ctx.scale(sx, 1); ctx.translate(-540, -(CY + CH / 2));
    ctx.save(); ctx.shadowColor = 'rgba(0,20,80,.35)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 14; rr(CX, CY, CW, CH, 40, '#fff'); ctx.restore();
    ctx.save(); ctx.beginPath(); ctx.roundRect(CX, CY, CW, CH, 40); ctx.clip(); ctx.translate(CX, CY);
    if (t < B[0]) s1(t); else if (t < B[1]) s2(t); else if (t < B[2]) s3(t); else if (t < B[3]) s4(t); else s5(t);
    ctx.restore(); ctx.restore();
    header(t);
  } else endCard(t);
  captions(t);
}
window.render = render;
window.READY = Promise.all(['58px Plex', '58px AmiriIt', '58px Taj'].map(f => document.fonts.load(f, 'ا0'))).then(() => render(0));
