// Nibras · "كيف يشتغل؟ #1 — المكيف" (Trial Reel, lane A). Bright explainer cards. Timings from timings.js (VO line starts/durations).
const W = 1080, H = 1920, L = TIM.start, D = TIM.dur, DUR = TIM.total; window.DUR = DUR;
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x)), seg = (t, a, b) => clamp((t - a) / (b - a)), lerp = (a, b, p) => a + (b - a) * p;
const eo = p => 1 - Math.pow(1 - p, 3), eio = p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
const back = p => { const c = 1.7; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); };
function hash(i, j) { let h = Math.imul(i | 0, 374761393) + Math.imul(j | 0, 668265263) | 0; h = Math.imul(h ^ h >>> 13, 1274126177); return ((h ^ h >>> 16) >>> 0) / 4294967296; }
const C = { navy: '#1F2A6B', orange: '#F2641C', dark: '#C2410C', cold: '#3D8BFF', coldL: '#9CC9FF', hot: '#F04A2A', warm: '#FF9A3D', cu: '#C77A45', cream: '#F7F1E6', wall: '#D9D2C5', red: '#E53935', green: '#22B07D', gray: '#6B7280' };
const CX = 90, CY = 400, CW = 900, CH = 840;
const S = { s2: L[2], s3: L[6], s4: L[8], end: 999 };
const WIDE = L[5] + D[5] - 1.0;
const BOUNDS = [S.s2, S.s3, S.s4];

// ---------- helpers ----------
function rr(x, y, w, h, r, fill, stroke, lw = 4) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); if (fill) { ctx.fillStyle = fill; ctx.fill(); } if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.stroke(); } }
function txt(s, x, y, size, o = {}) { ctx.save(); ctx.font = `${size}px ${o.font || 'Plex'}`; ctx.textAlign = o.align || 'center'; ctx.textBaseline = 'middle'; ctx.direction = o.ltr ? 'ltr' : 'rtl'; ctx.globalAlpha = o.a == null ? 1 : o.a; if (o.shadow) { ctx.shadowColor = 'rgba(0,20,80,.35)'; ctx.shadowBlur = 14; ctx.shadowOffsetY = 4; } ctx.fillStyle = o.c || C.navy; ctx.fillText(s, x, y); ctx.restore(); }
function label(s, x, y, p, o = {}) { if (p <= 0) return; ctx.save(); ctx.globalAlpha = eo(p) * (o.a == null ? 1 : o.a); const sz = o.size || 46; ctx.font = `${sz}px Plex`; ctx.direction = 'rtl'; const w = ctx.measureText(s).width + 44, h = sz * 1.6; ctx.translate(x, y); const k = lerp(.7, 1, back(p)) / (o.z || 1); ctx.scale(k, k); rr(-w / 2, -h / 2, w, h, h / 2, o.bg || C.navy); ctx.fillStyle = o.c || '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(s, 0, 3); ctx.restore(); }
function arrow(x0, y0, x1, y1, p, c = C.navy, lw = 7) { if (p <= 0) return; const x = lerp(x0, x1, eo(p)), y = lerp(y0, y1, eo(p)); ctx.save(); ctx.strokeStyle = c; ctx.fillStyle = c; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x, y); ctx.stroke(); const a = Math.atan2(y1 - y0, x1 - x0); ctx.beginPath(); ctx.moveTo(x + Math.cos(a) * 8, y + Math.sin(a) * 8); ctx.lineTo(x - Math.cos(a - .5) * 30, y - Math.sin(a - .5) * 30); ctx.lineTo(x - Math.cos(a + .5) * 30, y - Math.sin(a + .5) * 30); ctx.fill(); ctx.restore(); }
function cross(x, y, r, p) { if (p <= 0) return; ctx.save(); ctx.translate(x, y); ctx.scale(back(p), back(p)); ctx.fillStyle = C.red; ctx.beginPath(); ctx.arc(0, 0, r, 0, 7); ctx.fill(); ctx.strokeStyle = '#fff'; ctx.lineWidth = r * .22; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-r * .4, -r * .4); ctx.lineTo(r * .4, r * .4); ctx.moveTo(r * .4, -r * .4); ctx.lineTo(-r * .4, r * .4); ctx.stroke(); ctx.restore(); }
function drop(x, y, r, c = C.cold) { ctx.fillStyle = c; ctx.beginPath(); ctx.moveTo(x, y - r * 1.8); ctx.quadraticCurveTo(x + r, y - r * .2, x + r, y + r * .2); ctx.arc(x, y + r * .2, r, 0, Math.PI); ctx.quadraticCurveTo(x - r, y - r * .2, x, y - r * 1.8); ctx.fill(); }
function wave(x, y, len, t, c, lw = 6, amp = 8) { ctx.save(); ctx.strokeStyle = c; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.beginPath(); for (let i = 0; i <= 20; i++) { const u = i / 20; ctx.lineTo(x + u * len, y + Math.sin(u * 9 + t * 8) * amp); } ctx.stroke(); ctx.restore(); }
function plen(p) { let s = 0; for (let i = 1; i < p.length; i++) s += Math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1]); return s; }
function at(p, u) { let T = plen(p) * ((u % 1 + 1) % 1); for (let i = 1; i < p.length; i++) { const d = Math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1]); if (T <= d) { const k = T / d; return [lerp(p[i - 1][0], p[i][0], k), lerp(p[i - 1][1], p[i][1], k), i]; } T -= d; } return [...p[p.length - 1], p.length - 1]; }

// ---------- background ----------
function bg(t) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#2A5FEA'); g.addColorStop(1, '#4F90FF'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.strokeStyle = 'rgba(255,255,255,.07)'; ctx.lineWidth = 2; const o = (t * 12) % 60;
  for (let x = -60 + o; x < W; x += 60) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = -60 + o; y < H; y += 60) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
}
function indoorUnit(x, y, w, h, t, o = {}) {
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.18)'; ctx.shadowBlur = 20; ctx.shadowOffsetY = 8; rr(x, y, w, h, 26, '#FFFFFF', '#D5DBE3', 4); ctx.restore();
  rr(x + 30, y + h - 34, w - 60, 14, 7, '#E3E8EE'); ctx.fillStyle = '#22C55E'; ctx.beginPath(); ctx.arc(x + w - 40, y + 30, 7, 0, 7); ctx.fill();
  if (o.cold) for (let i = 0; i < 4; i++) { const u = (t * .8 + i / 4) % 1; ctx.save(); ctx.globalAlpha = (1 - u) * o.cold; wave(x + 60 + i * (w - 120) / 4, y + h + 20 + u * 220, 110, t + i, C.coldL, 7, 6); ctx.restore(); }
}

// ---------- scene 1 · the hook ----------
function s1(t) {
  rr(0, 0, CW, CH, 0, C.cream); ctx.fillStyle = '#EADFCB'; ctx.fillRect(0, 640, CW, 200);
  const z = lerp(1.08, 1, eo(seg(t, 0, 1.2))); ctx.save(); ctx.translate(450, 400); ctx.scale(z, z); ctx.translate(-450, -400);
  indoorUnit(150, 150, 600, 200, t, { cold: 1 });
  // heat blobs in the room
  for (let i = 0; i < 16; i++) { const hx = 80 + hash(i, 1) * 740, hy = 430 + hash(i, 2) * 230, m = seg(t, L[1] + .2 + i * .05, L[1] + 1.4 + i * .05);
    const x = lerp(hx, 450, eo(m)), y = lerp(hy, 260, eo(m)), r = 18 + hash(i, 3) * 14, a = 1 - seg(m, .8, 1);
    const g = ctx.createRadialGradient(x, y, 0, x, y, r * 2); g.addColorStop(0, `rgba(255,120,40,${.85 * a})`); g.addColorStop(1, 'rgba(255,120,40,0)'); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y + Math.sin(t * 3 + i) * 6, r * 2, 0, 7); ctx.fill(); }
  ctx.restore();
  const xp = seg(t, .35, .6); if (xp > 0) { label('يصنع برودة؟', 450, 470, xp, { size: 58 }); cross(640, 450, 40, seg(t, .9, 1.1)); }
  const out = seg(t, L[1] + 1.3, L[1] + 2.0); if (out > 0) { ctx.fillStyle = C.wall; ctx.fillRect(840, 0, 60, CH); arrow(760, 250, 880, 250, out, C.hot, 12); label('برّا', 780, 160, seg(t, L[1] + 1.6, L[1] + 1.9), { bg: C.hot, size: 50 }); }
}

// ---------- scene 2 · the full cycle ----------
const LOOP = [[120, 190], [450, 190], [490, 175], [700, 175], [700, 560], [660, 664], [694, 700], [730, 590], [865, 590], [865, 745], [730, 745], [640, 745], [640, 215], [505, 215], [120, 215], [120, 190]];
// temperature by loop segment index: 1-2 evaporator (cold), 3-5 suction (cool), 6 compressor out (hot), 7-10 condenser (hot->warm), 11-13 liquid (warm), 14-15 after valve (cold)
const SEGC = [null, C.cold, C.coldL, C.coldL, C.coldL, C.coldL, C.hot, C.hot, C.hot, C.warm, C.warm, C.warm, C.warm, C.warm, C.cold, C.cold];
function pipes(t) {
  ctx.save(); ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  for (let i = 2; i < LOOP.length - 1; i++) { if (i >= 7 && i <= 10) continue; ctx.strokeStyle = C.cu; ctx.lineWidth = 16; ctx.beginPath(); ctx.moveTo(...LOOP[i - 1]); ctx.lineTo(...LOOP[i]); ctx.stroke(); ctx.strokeStyle = SEGC[i]; ctx.globalAlpha = .55; ctx.lineWidth = 8; ctx.stroke(); ctx.globalAlpha = 1; }
  ctx.restore();
}
const CAM = () => [[S.s2, 300, 200, 1.9], [L[3], 300, 300, 1.45], [L[4], 640, 380, 1.2], [L[5], 745, 660, 1.85], [WIDE, 450, 430, .98]];
function cam(t) { const c = CAM(); let i = 0; while (i < c.length - 1 && c[i + 1][0] <= t) i++; const a = c[Math.max(0, i - 1)], b = c[i], p = eio(seg(t, b[0], b[0] + .7)); return i === 0 ? { x: b[1], y: b[2], z: b[3] } : { x: lerp(a[1], b[1], p), y: lerp(a[2], b[2], p), z: lerp(a[3], b[3], p) }; }
function s2(t) {
  const c = cam(t); ctx.save(); ctx.translate(450, 420); ctx.scale(c.z, c.z); ctx.translate(-c.x, -c.y);
  ctx.fillStyle = C.cream; ctx.fillRect(-600, -600, 1160, 2100); const sky = ctx.createLinearGradient(0, -600, 0, 800); sky.addColorStop(0, '#BFE3FF'); sky.addColorStop(1, '#FFE7B8'); ctx.fillStyle = sky; ctx.fillRect(600, -600, 1400, 1400); ctx.fillStyle = '#E8CF9E'; ctx.fillRect(600, 780, 1400, 800); ctx.fillStyle = '#EADFCB'; ctx.fillRect(-600, 780, 1160, 800);
  ctx.fillStyle = C.wall; ctx.fillRect(560, -600, 40, 2200); ctx.fillStyle = '#FFD45A'; ctx.beginPath(); ctx.arc(950, -40, 60, 0, 7); ctx.fill();
  indoorUnit(90, 120, 400, 150, t, { cold: seg(t, L[3], L[3] + .5) });
  ctx.save(); ctx.beginPath(); ctx.roundRect(100, 150, 380, 80, 14); ctx.clip(); ctx.fillStyle = 'rgba(61,139,255,.12)'; ctx.fillRect(100, 150, 380, 80); ctx.strokeStyle = '#B9C6D6'; ctx.lineWidth = 3; for (let x = 104; x < 480; x += 12) { ctx.beginPath(); ctx.moveTo(x, 150); ctx.lineTo(x, 230); ctx.stroke(); } ctx.restore();   // coil fins
  pipes(t);
  rr(610, 560, 270, 200, 22, '#F3F4F6', '#C8CDD4', 4);                                                     // outdoor unit
  ctx.save(); ctx.beginPath(); ctx.roundRect(720, 575, 150, 170, 14); ctx.clip(); ctx.strokeStyle = '#C2C8CF'; ctx.lineWidth = 3; for (let y = 580; y < 745; y += 10) { ctx.beginPath(); ctx.moveTo(720, y); ctx.lineTo(870, y); ctx.stroke(); } ctx.restore();
  ctx.save(); ctx.strokeStyle = C.hot; ctx.lineWidth = 10; ctx.lineJoin = 'round'; ctx.beginPath(); [LOOP[6], LOOP[7], LOOP[8], LOOP[9], LOOP[10]].forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.globalAlpha = .5; ctx.stroke(); ctx.restore();
  ctx.save(); ctx.translate(795, 668); ctx.rotate(t * 9); ctx.fillStyle = 'rgba(80,90,105,.85)'; for (let k = 0; k < 4; k++) { ctx.rotate(Math.PI / 2); ctx.beginPath(); ctx.ellipse(0, -30, 14, 30, 0, 0, 7); ctx.fill(); } ctx.restore();
  const hotC = .6 + .4 * Math.sin(t * 8) * (t > L[5] ? 1 : 0); ctx.fillStyle = `rgba(240,74,42,${t > L[5] ? hotC : .35})`; ctx.beginPath(); ctx.arc(665, 700, 34, 0, 7); ctx.fill(); ctx.strokeStyle = '#7C2D12'; ctx.lineWidth = 4; ctx.stroke();
  // flow dots around the loop
  const speed = t < L[3] ? .05 : .09; for (let k = 0; k < 34; k++) { const [x, y, i] = at(LOOP, t * speed + k / 34); ctx.fillStyle = SEGC[i] || C.cold; ctx.beginPath(); ctx.arc(x, y, 8, 0, 7); ctx.fill(); ctx.strokeStyle = '#fff'; ctx.lineWidth = 2; ctx.stroke(); }
  // indoor airflow: hot room air in, cold out
  if (t > L[3]) { for (let i = 0; i < 3; i++) { const u = (t * .9 + i / 3) % 1; ctx.save(); ctx.globalAlpha = 1 - u; wave(110 + i * 120, 60 - u * 30, 90, t + i, C.warm, 7, 6); ctx.restore(); } }
  // outdoor heat out to the street
  if (t > L[5]) for (let i = 0; i < 4; i++) { const u = (t * .8 + i / 4) % 1; ctx.save(); ctx.globalAlpha = 1 - u; wave(885 + u * 140, 600 + i * 40, 110, t + i, C.hot, 7, 7); ctx.restore(); }
  // loop arrow for "repeat the cycle"
  const rp = seg(t, WIDE + .2, WIDE + 1.0); if (rp > 0) { ctx.save(); ctx.strokeStyle = C.green; ctx.lineWidth = 14; ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(450, 450, 150, -Math.PI / 2, -Math.PI / 2 + eo(rp) * Math.PI * 1.75); ctx.stroke(); ctx.restore(); }
  ctx.restore();
  const z = c.z;
  if (t > L[2] && t < L[3]) { label('مادة تبريد باردة', 450, 120, seg(t, L[2] + .3, L[2] + .6), { bg: C.cold, size: 50 }); label('أنابيب نحاس', 640, 700, seg(t, L[2] + 1.2, L[2] + 1.5), { bg: C.cu, size: 50 }); }
  if (t > L[3] && t < L[4]) { label('هوا حار', 250, 90, seg(t, L[3] + .2, L[3] + .5), { bg: C.warm, size: 50 }); label('هوا بارد', 300, 690, seg(t, L[3] + 1.2, L[3] + 1.5), { bg: C.cold, size: 50 }); }
  if (t > L[4] && t < L[5]) label('الحرارة تطلع للوحدة اللي برّا', 450, 110, seg(t, L[4] + .3, L[4] + .6), { size: 44 });
  if (t > L[5] && t < WIDE) { label('الكمبروسر', 300, 640, seg(t, L[5] + .3, L[5] + .6), { bg: C.hot, size: 54 }); label('حرارة للشارع', 640, 150, seg(t, L[5] + 1.5, L[5] + 1.8), { bg: C.hot, size: 50 }); }
  if (t > WIDE) label('وتعيد الدورة', 450, 760, seg(t, WIDE + .3, WIDE + .6), { bg: C.green, size: 54 });
}

// ---------- scene 3 · why it drips ----------
function s3(t) {
  const tt = t - S.s3; rr(0, 0, CW, CH, 0, '#EEF5FF');
  const fins = ctx.createLinearGradient(0, 80, 0, 420); fins.addColorStop(0, '#DCE7F3'); fins.addColorStop(1, '#B9CCE0'); rr(80, 80, 520, 340, 18, fins, '#9FB3C8', 4);
  ctx.strokeStyle = '#A5B8CC'; ctx.lineWidth = 6; for (let x = 100; x < 600; x += 26) { ctx.beginPath(); ctx.moveTo(x, 90); ctx.lineTo(x, 410); ctx.stroke(); }
  ctx.strokeStyle = C.cu; ctx.lineWidth = 16; for (let y = 140; y < 400; y += 80) { ctx.beginPath(); ctx.moveTo(80, y); ctx.lineTo(600, y); ctx.stroke(); }
  const cond = seg(tt, .3, 1.8); for (let i = 0; i < 40; i++) { const x = 95 + hash(i, 5) * 500, y0 = 100 + hash(i, 6) * 290, s = clamp(cond * 1.5 - hash(i, 7) * .5); if (s <= 0) continue; const sl = Math.max(0, (t * .35 + hash(i, 8)) % 1.4 - .4) * 300 * (tt > 1.5 ? 1 : 0); drop(x, Math.min(y0 + sl, 415), 4 + 5 * s, 'rgba(61,139,255,.85)'); }
  // the cold glass inset
  const gp = seg(tt, .8, 1.2); if (gp > 0) { ctx.save(); ctx.globalAlpha = gp; ctx.translate(735, 220); rr(-110, -150, 220, 300, 110, '#fff', '#D5DBE3', 4); ctx.fillStyle = 'rgba(180,215,255,.55)'; ctx.beginPath(); ctx.moveTo(-55, -100); ctx.lineTo(55, -100); ctx.lineTo(45, 90); ctx.lineTo(-45, 90); ctx.closePath(); ctx.fill(); ctx.strokeStyle = '#8FB5E0'; ctx.lineWidth = 4; ctx.stroke(); ctx.fillStyle = 'rgba(120,180,255,.6)'; ctx.fillRect(-50, -40, 100, 128); for (let i = 0; i < 10; i++) drop(-40 + hash(i, 30) * 80, -80 + hash(i, 31) * 160 + ((t * 20 + i * 7) % 18), 4, 'rgba(61,139,255,.9)'); ctx.restore(); label('مثل الكاس البارد', 690, 420, seg(tt, 1.1, 1.4), { size: 36, bg: C.cold }); }
  // tray, drain hose, then the clog
  const tp = seg(t, L[7], L[7] + .4); if (tp > 0) {
    rr(70, 450, 560, 40, 10, '#CBD5E1', '#94A3B8', 3); ctx.fillStyle = C.wall; ctx.fillRect(820, 0, 40, CH);
    ctx.strokeStyle = '#94A3B8'; ctx.lineWidth = 18; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(620, 480); ctx.quadraticCurveTo(720, 520, 900, 560); ctx.stroke();
    const clog = seg(t, L[7] + 1.9, L[7] + 2.3); if (clog > 0) { ctx.fillStyle = '#8B6B3E'; ctx.beginPath(); ctx.ellipse(740, 522, 26 * eo(clog), 14 * eo(clog), .3, 0, 7); ctx.fill(); }
    const lvl = clog > 0 ? lerp(0, 1, seg(t, L[7] + 2.2, L[7] + 3.0)) : .3; ctx.fillStyle = 'rgba(61,139,255,.8)'; ctx.fillRect(74, 486 - 30 * lvl, 552, 30 * lvl);
    if (clog <= 0) for (let k = 0; k < 4; k++) { const u = (t * 1.2 + k / 4) % 1; const x = lerp(640, 890, u), y = lerp(486, 556, u); drop(x, y, 7); }
    if (lvl >= 1) { for (let k = 0; k < 5; k++) { const u = (t * 1.4 + k / 5) % 1; drop(90, lerp(500, 800, u), 9); } ctx.fillStyle = 'rgba(61,139,255,.35)'; ctx.fillRect(78, 500, 18, 300); cross(250, 640, 40, seg(t, L[7] + 3.0, L[7] + 3.25)); label('لي التصريف انسد', 450, 760, seg(t, L[7] + 3.0, L[7] + 3.3), { bg: C.red, size: 50 }); }
    label('لي التصريف', 720, 610, seg(t, L[7] + .4, L[7] + .7) * (1 - seg(t, L[7] + 2.8, L[7] + 3.0)), { size: 42 });
  }
}

// ---------- scene 4 · save + follow + next part ----------
function s4(t) {
  const tt = t - S.s4; rr(0, 0, CW, CH, 0, '#F5F8FF');
  const b = seg(tt, .1, .4); if (b > 0) { ctx.save(); ctx.translate(290, 260); ctx.scale(back(b), back(b)); const filled = tt > .9; ctx.fillStyle = filled ? C.navy : '#fff'; ctx.strokeStyle = C.navy; ctx.lineWidth = 12; ctx.beginPath(); ctx.moveTo(-70, -100); ctx.lineTo(70, -100); ctx.lineTo(70, 110); ctx.lineTo(0, 55); ctx.lineTo(-70, 110); ctx.closePath(); ctx.fill(); ctx.stroke(); ctx.restore(); txt('احفظه', 290, 410, 54); }
  const f = seg(tt, .5, .8); if (f > 0) { ctx.save(); ctx.translate(620, 260); ctx.scale(back(f), back(f)); const done = tt > 1.4; rr(-150, -60, 300, 120, 60, done ? '#E5E7EB' : C.orange); txt(done ? 'تتابعنا ✓' : 'تابع +', 0, 4, 52, { c: done ? C.navy : '#fff' }); ctx.restore(); }
  const n = seg(tt, 1.0, 1.4); if (n > 0) { ctx.save(); ctx.globalAlpha = eo(n); ctx.translate(0, (1 - eo(n)) * 40); rr(90, 540, 720, 220, 30, '#fff', '#C7D2FE', 4); txt('الجزء الجاي', 450, 600, 40, { c: C.gray }); txt('كيف يمنع الزجاج الدبل الحرارة؟', 450, 680, 52); ctx.restore(); }
  txt('@aluminum25_alnbras', 450, 470, 44, { font: 'Taj', ltr: 1, c: C.orange, a: seg(tt, .6, .9) });
}

// ---------- end card (silent) ----------
function endCard(t) {
  const tt = t - S.end, p = seg(tt, 0, .14); ctx.save(); ctx.translate(540, 900); ctx.scale(lerp(.9, 1, back(p)), lerp(.9, 1, back(p))); ctx.shadowColor = 'rgba(0,20,80,.35)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 14; rr(-430, -300, 860, 600, 48, '#fff'); ctx.restore();
  txt('كيف يشتغل؟', 540, 740, 104, { a: seg(tt, .05, .3) });
  txt('سلسلة من النبراس للألمنيوم', 540, 880, 50, { c: C.gray, a: seg(tt, .25, .5) });
  txt('@aluminum25_alnbras', 540, 1010, 54, { font: 'Taj', ltr: 1, c: C.orange, a: seg(tt, .45, .7) });
}

// ---------- header, series badge, captions ----------
function header(t) {
  if (t >= S.end) return;
  const H0 = [[0, 'مكيفك ما يبرّد!'], [L[1], 'وآخر المقطع: ليش يقطّر على جدارك؟'], [L[2], 'الوحدة اللي فوق'], [L[3], 'المروحة'], [L[4], 'الأنابيب'], [L[5], 'الوحدة الخارجية'], [WIDE, 'الدورة كاملة'], [S.s3, 'ليش يقطّر؟'], [S.s4, 'الحلقة الجاية']];
  const h = [...H0].reverse().find(h => t >= h[0]); const p = seg(t, h[0] - (h[0] ? .1 : 1), h[0] + .25);
  ctx.save(); ctx.globalAlpha = eo(p); ctx.translate(0, (1 - eo(p)) * 20); txt(h[1], 540, 268, h[0] === 0 ? 96 : (h[0] === L[1] ? 52 : 62), { c: h[0] === L[1] ? '#FFE3B3' : '#fff', shadow: 1 }); ctx.restore();
  ctx.save(); rr(60, 150, 420, 64, 32, 'rgba(255,255,255,.18)'); txt('كيف يشتغل؟ الحلقة ١ — النبراس', 270, 184, 32, { c: '#fff' }); ctx.restore();
}
const KEY = ['برودة', 'البيت.', 'نحاس.', 'فيبرد.', 'الخارجية.', 'الكمبروسر', 'يقطّر؟', 'جدارك.', 'احفظ'];
function captions(t) {
  let i = -1; for (let k = 0; k < L.length; k++) if (t >= L[k] - (k === 0 ? 3 : .1) && t < L[k] + D[k] + .25) i = k; if (i < 0) return;
  const words = TIM.text[i].split(' '), size = 60, s0 = i === 0 ? L[0] - 2.4 : L[i], dur = (i === 0 ? D[0] + 2.4 : D[i]) * .85;
  ctx.save(); ctx.font = `${size}px Plex`; ctx.direction = 'rtl'; const sp = 16, ws = words.map(w => ctx.measureText(w).width);
  const lines = [[]]; let lw = 0; words.forEach((w, j) => { if (lw + ws[j] > 880 && lines[lines.length - 1].length) { lines.push([]); lw = 0; } lines[lines.length - 1].push(j); lw += ws[j] + sp; });
  const tot = TIM.text[i].length; let acc = 0; const st = words.map(w => { const v = s0 + dur * acc / tot; acc += w.length + 1; return v; });
  lines.forEach((ln, li) => { const wide = ln.reduce((a, j) => a + ws[j] + sp, -sp); let x = 540 + wide / 2; const y = 1395 + li * 88;
    ln.forEach(j => { const p = seg(t, st[j], st[j] + .16); if (p > 0) { const key = words[j] === KEY[i]; ctx.save(); ctx.globalAlpha = eo(p); const k = lerp(.6, 1, back(p)); ctx.translate(x - ws[j] / 2, y); ctx.scale(k, k);
      if (key) rr(-ws[j] / 2 - 14, -size * .62, ws[j] + 28, size * 1.24, 14, C.orange);
      ctx.fillStyle = '#fff'; ctx.shadowColor = key ? 'transparent' : 'rgba(0,20,80,.45)'; ctx.shadowBlur = 12; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(words[j], 0, 4); ctx.restore(); }
      x -= ws[j] + sp; }); });
  ctx.restore();
}

// ---------- frame ----------
function render(t) {
  t = Math.round(t * 30) / 30; ctx.setTransform(1, 0, 0, 1, 0, 0); bg(t);
  if (t < S.end) {
    let d = 1; BOUNDS.forEach(b => { d = Math.min(d, Math.abs(t - b) / .14); }); const sx = Math.max(.02, Math.min(1, d));
    ctx.save(); ctx.translate(540, CY + CH / 2); ctx.scale(sx * 1.12, 1.12); ctx.translate(-540, -(CY + CH / 2));
    ctx.save(); ctx.shadowColor = 'rgba(0,20,80,.35)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 14; rr(CX, CY, CW, CH, 40, '#fff'); ctx.restore();
    ctx.save(); ctx.beginPath(); ctx.roundRect(CX, CY, CW, CH, 40); ctx.clip(); ctx.translate(CX, CY);
    if (t < S.s2) s1(t); else if (t < S.s3) s2(t); else if (t < S.s4) s3(t); else s4(t);
    ctx.restore(); ctx.restore();
  } else endCard(t);
  header(t); captions(t);
}
window.render = render;
window.READY = Promise.all(['58px Plex', '58px AmiriIt', '58px Taj'].map(f => document.fonts.load(f, 'ا0'))).then(() => render(0));
