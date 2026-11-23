// Nibras · "Water test" — blueprint-style film drawn entirely in canvas. render(t) is pure.
const W = 1080, H = 1920, SW = 2400, SH = 3100, OX = 1740;
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const DUR = 17.0; window.DUR = DUR;
const INK = '#E7F0F9', HOLLOW = '#1b3a78', ORANGE = '#F2641C';
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x)), seg = (t, a, b) => clamp((t - a) / (b - a)), lerp = (a, b, p) => a + (b - a) * p;
const eio = p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2, eo = p => 1 - Math.pow(1 - p, 3);
const back = p => { const c = 1.9; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); };
function rng(s) { return () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

// ---------- paper (built once) ----------
let paper, grain;
function buildPaper() {
  const s = .5; paper = document.createElement('canvas'); paper.width = SW * s; paper.height = SH * s;
  const p = paper.getContext('2d'), r = rng(7); p.scale(s, s);
  const g = p.createLinearGradient(0, 0, SW, SH); g.addColorStop(0, '#1b3a7a'); g.addColorStop(.5, '#234c96'); g.addColorStop(1, '#19356f');
  p.fillStyle = g; p.fillRect(0, 0, SW, SH);
  for (let i = 0; i < 260; i++) { const x = r() * SW, y = r() * SH, R = 120 + r() * 420; const b = p.createRadialGradient(x, y, 0, x, y, R); const l = r() > .5; b.addColorStop(0, l ? 'rgba(70,120,200,.10)' : 'rgba(8,20,60,.12)'); b.addColorStop(1, 'rgba(0,0,0,0)'); p.fillStyle = b; p.fillRect(x - R, y - R, 2 * R, 2 * R); }
  for (let i = 0; i < 90; i++) { const y = r() * SH; p.fillStyle = `rgba(${r() > .5 ? '120,160,230' : '5,15,50'},${.03 + r() * .04})`; p.fillRect(0, y, SW, 2 + r() * 14); }
  p.strokeStyle = 'rgba(231,240,249,.07)'; p.lineWidth = 1;                      // drafting grid
  for (let x = 0; x <= SW; x += 60) { p.beginPath(); p.moveTo(x, 0); p.lineTo(x, SH); p.stroke(); }
  for (let y = 0; y <= SH; y += 60) { p.beginPath(); p.moveTo(0, y); p.lineTo(SW, y); p.stroke(); }
  [[1200, 0, 1200, SH], [0, 1500, SW, 1500]].forEach(([a, b, c, d]) => {       // fold creases
    p.strokeStyle = 'rgba(200,225,255,.20)'; p.lineWidth = 3; p.beginPath(); p.moveTo(a, b); p.lineTo(c, d); p.stroke();
    p.strokeStyle = 'rgba(5,15,50,.30)'; p.lineWidth = 4; p.beginPath(); p.moveTo(a + 4, b + 4); p.lineTo(c + 4, d + 4); p.stroke();
  });
  p.strokeStyle = 'rgba(231,240,249,.55)'; p.lineWidth = 4; p.strokeRect(26, 26, SW - 52, SH - 52); p.lineWidth = 1.5; p.strokeRect(40, 40, SW - 80, SH - 80);
  grain = document.createElement('canvas'); grain.width = W / 2; grain.height = H / 2;
  const q = grain.getContext('2d'), im = q.createImageData(W / 2, H / 2), r2 = rng(3);
  for (let i = 0; i < im.data.length; i += 4) { const v = r2() * 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 22; } q.putImageData(im, 0, 0);
}

// ---------- drafting engine ----------
let Z = 1, LW = 1;
const plen = pts => { let L = 0; for (let i = 1; i < pts.length; i++) L += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); return L; };
function trunc(pts, p) { if (p >= 1) return pts; const T = plen(pts) * p; let L = 0; const o = [pts[0]]; for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); if (L + d >= T) { const k = (T - L) / (d || 1); o.push([lerp(pts[i - 1][0], pts[i][0], k), lerp(pts[i - 1][1], pts[i][1], k)]); return o; } L += d; o.push(pts[i]); } return o; }
const at = (pts, p) => { const o = trunc(pts, clamp(p)); return o[o.length - 1]; };
function line(pts, p, w, o = {}) {
  if (p <= 0) return; const q = trunc(pts, p);
  ctx.save(); ctx.lineWidth = w * LW; ctx.strokeStyle = o.c || INK; ctx.globalAlpha = o.a == null ? 1 : o.a; ctx.lineJoin = ctx.lineCap = 'round';
  ctx.shadowColor = 'rgba(231,240,249,.5)'; ctx.shadowBlur = o.glow == null ? 5 : o.glow;
  if (o.dash) { ctx.setLineDash(o.dash); ctx.lineDashOffset = o.off || 0; ctx.lineCap = 'butt'; }
  ctx.beginPath(); q.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.stroke();
  if (p < 1 && !o.nonib) { const h = q[q.length - 1]; ctx.setLineDash([]); ctx.shadowBlur = 26; ctx.shadowColor = '#fff'; ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(h[0], h[1], 4.5 * LW, 0, 7); ctx.fill(); }
  ctx.restore();
}
const rect = (x, y, w, h) => [[x, y], [x + w, y], [x + w, y + h], [x, y + h], [x, y]];
function fill(pts, c) { ctx.save(); ctx.fillStyle = c; ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); ctx.fill(); ctx.restore(); }
function hatch(pts, p, sp = 12, dir = 1, a = .55) {
  if (p <= 0) return; let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9; pts.forEach(([x, y]) => { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); });
  ctx.save(); ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); ctx.clip();
  ctx.strokeStyle = INK; ctx.globalAlpha = a; ctx.lineWidth = .9 * LW; const h = y1 - y0, n = Math.ceil((x1 - x0 + h) / sp);
  ctx.beginPath(); for (let i = 0; i < n * p; i++) { const x = x0 - h + i * sp; if (dir > 0) { ctx.moveTo(x, y1); ctx.lineTo(x + h, y0); } else { ctx.moveTo(x + h, y1); ctx.lineTo(x, y0); } } ctx.stroke(); ctx.restore();
}
// text lettered on (RTL reveal: p from the right edge)
function text(s, x, y, size, p, o = {}) {
  if (p <= 0) return; ctx.save(); ctx.font = `${size}px ${o.font || 'Plex'}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.direction = o.ltr ? 'ltr' : 'rtl';
  const w = ctx.measureText(s).width + 20, h = size * 1.7;
  if (p < 1) { const e = eo(p); ctx.globalAlpha = e; y += (1 - e) * size * .35; }
  ctx.fillStyle = o.c || INK; ctx.globalAlpha *= o.a == null ? 1 : o.a; ctx.shadowColor = 'rgba(231,240,249,.45)'; ctx.shadowBlur = o.glow == null ? 6 : o.glow; ctx.fillText(s, x, y); ctx.restore();
}

// ---------- camera ----------
const CAM = [[0, 520, 790, 1.32], [2.3, 520, 790, 1.4, 'lin'], [2.3, 540, 960, 1.72, 'cut'], [4.5, 540, 960, 1.84, 'lin'],
[4.9, OX - 70, 900, 2.1], [6.45, OX - 70, 905, 2.14, 'lin'], [6.95, OX - 125, 1060, 2.3], [7.95, OX - 125, 1064, 2.33, 'lin'],
[8.45, OX - 185, 1150, 2.3], [9.75, OX - 185, 1156, 2.33, 'lin'], [10.25, OX + 90, 900, 1.25], [12.6, OX + 90, 900, 1.29, 'lin'],
[13.25, OX, 2110, 1.0], [DUR + .1, OX, 2110, 1.03, 'lin']];
function cam(t) {
  let i = 0; while (i < CAM.length - 1 && CAM[i + 1][0] <= t) i++;
  const a = CAM[i], b = CAM[Math.min(i + 1, CAM.length - 1)]; if (a === b || b[4] === 'cut') return { x: a[1], y: a[2], z: a[3] };
  let p = seg(t, a[0], b[0]); if (b[4] !== 'lin') p = eio(p);
  return { x: lerp(a[1], b[1], p), y: lerp(a[2], b[2], p), z: Math.exp(lerp(Math.log(a[3]), Math.log(b[3]), p)) };
}

// ---------- FIG. 1 · elevation + water test ----------
const JETS = [[330, 540], [420, 700], [380, 900], [500, 620], [600, 820], [690, 560], [740, 960], [560, 1010], [660, 700]];
const DROPS = (() => { const r = rng(11); return Array.from({ length: 34 }, () => ({ x: 300 + r() * 480, sp: .35 + r() * .5, ph: r(), len: 18 + r() * 26 })); })();
function fig1(t) {
  const d = (a, dur) => seg(t, a - 1.6, a - 1.6 + dur);
  line([[540, 340], [540, 1200]], d(0, .25), .9, { dash: [30, 8, 6, 8], a: .7 }); line([[190, 760], [890, 760]], d(.05, .25), .9, { dash: [30, 8, 6, 8], a: .7 });
  line(rect(240, 400, 600, 720), d(.02, .4), 3.6); line(rect(274, 434, 532, 652), d(.15, .35), 2);
  line(rect(274, 434, 274, 652), d(.3, .3), 2); line(rect(532, 434, 274, 652), d(.3, .3), 2);
  fill(rect(302, 462, 218, 596), `rgba(231,240,249,${.07 * d(.5, .3)})`); fill(rect(560, 462, 218, 596), `rgba(231,240,249,${.07 * d(.5, .3)})`);
  line(rect(302, 462, 218, 596), d(.45, .3), 1.25); line(rect(560, 462, 218, 596), d(.45, .3), 1.25);
  line(rect(522, 730, 14, 76), d(.6, .2), 2); line(rect(210, 1120, 660, 30), d(.5, .25), 3.6);
  [[320, 640, 420, 500], [340, 760, 500, 540], [580, 700, 700, 520], [600, 860, 760, 620]].forEach(([a, b, c, e], i) => line([[a, b], [c, e]], d(.7 + i * .05, .2), .9, { a: .5 }));
  // dimensions
    line([[880, 400], [880, 1120]], d(1, .35), 1.25); line([[862, 400], [898, 400]], d(1, .35), 1.25); line([[862, 1120], [898, 1120]], d(1, .35), 1.25);
  ctx.save(); ctx.translate(912, 760); ctx.rotate(Math.PI / 2); text('1500', 0, 0, 30, d(1.2, .3), { font: 'Taj', ltr: 1 }); ctx.restore();
  // nozzle + jets
  line([[120, 688], [200, 676], [200, 724], [120, 712], [120, 688]], d(.08, .25), 2.5); line([[120, 700], [100, 760], [104, 1000]], d(.15, .3), 2.5);
  const j = 1, wOn = 1;
  JETS.forEach(([x, y], i) => {
    line([[202, 700], [x, y]], j, 5.5, { dash: [44, 14], off: -t * 1300 - i * 9, nonib: 1, c: '#A8ECFF', glow: 18 });
    if (j >= 1) { const k = (t * 7 + i * .37) % 1, R = 16 + k * 52; ctx.save(); ctx.strokeStyle = '#A8ECFF'; ctx.globalAlpha = 1 - k; ctx.lineWidth = 4 * LW; for (let a = 0; a < 7; a++) { const an = a * .9 + i; ctx.beginPath(); ctx.moveTo(x + Math.cos(an) * R * .5, y + Math.sin(an) * R * .5); ctx.lineTo(x + Math.cos(an) * R, y + Math.sin(an) * R); ctx.stroke(); } ctx.restore(); }
  });
  // water running down the glass and dripping off the sill
  DROPS.forEach(o => { const u = (t * o.sp + o.ph) % 1, y = 470 + u * 650; ctx.save(); ctx.globalAlpha = wOn * .85; ctx.strokeStyle = INK; ctx.lineWidth = 2.2 * LW; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(o.x, y - o.len); ctx.lineTo(o.x, y); ctx.stroke(); ctx.fillStyle = INK; ctx.beginPath(); ctx.arc(o.x, y, 3.2, 0, 7); ctx.fill(); ctx.restore(); });
  for (let i = 0; i < 12; i++) { const u = (t * 1.3 + i * .21) % 1, x = 250 + i * 52, y = 1152 + u * u * 150; ctx.save(); ctx.globalAlpha = wOn * (1 - u); ctx.fillStyle = INK; ctx.beginPath(); ctx.ellipse(x, y, 3, 6, 0, 0, 7); ctx.fill(); ctx.restore(); }
  // the question
  const qp = seg(t, 2.42, 2.75); if (qp > 0) { const s = back(qp) * (1 + .03 * Math.sin((t - 2.42) * 5)); ctx.save(); ctx.translate(540, 835); ctx.scale(s, s); ctx.rotate(-.06 + .03 * Math.sin((t - 2.42) * 3)); ctx.fillStyle = 'rgba(27,58,120,.86)'; ctx.beginPath(); ctx.ellipse(0, 0, 120, 150, 0, 0, 7); ctx.fill(); line(Array.from({ length: 41 }, (_, i) => [Math.cos(i / 40 * 6.2832) * 120, Math.sin(i / 40 * 6.2832) * 150]), seg(t, 2.42, 2.9), 2); text('؟', 0, 0, 230, 1, { glow: 22 }); ctx.restore(); }
}

// ---------- FIG. 2 · section through the sill ----------
const o = OX;
const RAIL = [[o - 130, 900], [o - 90, 900], [o - 90, 990], [o + 70, 990], [o + 70, 900], [o + 110, 900], [o + 110, 1080], [o - 130, 1080], [o - 130, 900]];
const SILL = [[o - 190, 1060], [o - 150, 1060], [o - 150, 1118], [o + 130, 1100], [o + 130, 1000], [o + 170, 1000], [o + 170, 1300], [o - 190, 1300], [o - 190, 1060]];
const WPATH = [[o - 76, 380], [o - 76, 896], [o - 96, 898], [o - 136, 900], [o - 141, 916], [o - 140, 1110], [o - 152, 1113], [o - 198, 1115], [o - 202, 1132], [o - 202, 1600]];
const MARK = [[o - 80, 915, 5.0, 'جلد مطاطي', o - 235, 800], [o - 140, 1105, 6.5, 'مجرى التصريف', o - 240, 985], [o - 172, 1110, 8.0, 'فتحة تصريف', o - 300, 1225]];
function fig2(t) {
  const T = 4.4, d = (a, dur) => seg(t, T + a, T + a + dur); if (t < T) return;
  text('شكل ٢ — مقطع عرضي', o, 300, 50, d(.2, .5)); text('برّا', o - 255, 450, 46, d(.5, .3), { a: .85 }); text('داخل البيت', o + 335, 500, 50, d(.5, .4));
  // glass unit
  fill(rect(o - 70, 380, 20, 600), `rgba(231,240,249,${.18 * d(.1, .3)})`); fill(rect(o + 30, 380, 20, 600), `rgba(231,240,249,${.18 * d(.1, .3)})`);
  line([[o - 70, 380], [o - 70, 980], [o - 50, 980], [o - 50, 380]], d(0, .35), 2.4); line([[o + 30, 380], [o + 30, 980], [o + 50, 980], [o + 50, 380]], d(.05, .35), 2.4);
  line([[o - 110, 392], [o - 60, 372], [o - 20, 392], [o + 20, 372], [o + 60, 392], [o + 90, 376]], d(.3, .2), 1.25);
  hatch(rect(o - 50, 930, 80, 30), d(.35, .2), 7, -1, .8); line(rect(o - 50, 930, 80, 30), d(.3, .2), 1.6);
  // sash rail + frame sill (cut aluminium = hatched, hollow chambers)
  fill(RAIL, `rgba(90,140,215,${.22 * d(.1, .3)})`); fill(SILL, `rgba(90,140,215,${.22 * d(.2, .3)})`);
  hatch(RAIL, d(.35, .35), 11, 1, .5); hatch(SILL, d(.45, .35), 11, 1, .5);
  if (d(.3, .1) > 0) { fill(rect(o - 110, 1010, 200, 50), HOLLOW); fill(rect(o - 170, 1150, 150, 120), HOLLOW); fill(rect(o, 1150, 150, 120), HOLLOW); fill(rect(o - 193, 1098, 46, 22), HOLLOW); }
  line(RAIL, d(.1, .4), 3.4); line(SILL, d(.2, .45), 3.4);
  line(rect(o - 110, 1010, 200, 50), d(.4, .25), 1.6); line(rect(o - 170, 1150, 150, 120), d(.5, .25), 1.6); line(rect(o, 1150, 150, 120), d(.55, .25), 1.6);
  line([[o - 193, 1098], [o - 147, 1098]], d(.6, .15), 1.25, { dash: [6, 5] }); line([[o - 193, 1120], [o - 147, 1120]], d(.6, .15), 1.25, { dash: [6, 5] });
  fill(rect(o - 90, 900, 20, 30), `rgba(231,240,249,${.95 * d(.5, .15)})`); fill(rect(o + 50, 900, 20, 30), `rgba(231,240,249,${.95 * d(.5, .15)})`);   // gaskets
  hatch(rect(o - 190, 1300, 420, 120), d(.6, .35), 17, -1, .45); line(rect(o - 190, 1300, 420, 120), d(.55, .3), 2);
  // rain + the water's way out
  const w = seg(t, 4.9, 5.2); if (w > 0) {
    for (let i = 0; i < 16; i++) { const u = (t * 1.6 + i * .173) % 1, y0 = 400 + (i * 97) % 470, x = lerp(o - 330, o - 80, u); ctx.save(); ctx.globalAlpha = w * .7 * (1 - u * .3); ctx.strokeStyle = INK; ctx.lineWidth = 1.8 * LW; ctx.beginPath(); ctx.moveTo(x - 30, y0 + u * 40 - 9); ctx.lineTo(x, y0 + u * 40); ctx.stroke(); ctx.restore(); }
    line(WPATH, w, 1.4, { a: .35, nonib: 1, dash: [10, 8], off: -t * 120 });
    for (let k = 0; k < 16; k++) { const u = (t * .2 + k / 16) % 1, [x, y] = at(WPATH, u), [x2, y2] = at(WPATH, Math.max(0, u - .012)); ctx.save(); ctx.globalAlpha = w; ctx.strokeStyle = INK; ctx.lineWidth = 3 * LW; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(x2, y2); ctx.lineTo(x, y); ctx.stroke(); ctx.fillStyle = '#fff'; ctx.shadowColor = '#fff'; ctx.shadowBlur = 10; ctx.beginPath(); ctx.arc(x, y, 5, 0, 7); ctx.fill(); ctx.restore(); }
  }
  // part markers with leaders
  MARK.forEach(([x, y, t0, label, lx, ly]) => { const p = seg(t, t0 + .15, t0 + .45), fa = 1 - seg(t, t0 + 1.45, t0 + 1.7), ga = 1 - seg(t, 9.75, 10); if (p <= 0 || ga <= 0) return; const pulse = 1 + .25 * Math.sin((t - t0) * 7) * (t < t0 + 1.6 ? 1 : 0);
    line(Array.from({ length: 25 }, (_, i) => [x + Math.cos(i / 24 * 6.2832) * 17 * pulse, y + Math.sin(i / 24 * 6.2832) * 17 * pulse]), p, 2.6, { glow: 14, a: ga });
    if (fa > 0) { line([[x - 16, y + (ly < y ? -8 : 8)], [lx + 80, ly + (ly < y ? 28 : -28)]], seg(t, t0 + .3, t0 + .55), 1.25, { a: fa }); text(label, lx, ly, 32, seg(t, t0 + .45, t0 + .8), { a: fa }); } });
}

// ---------- title block (end card) ----------
function titleBlock(t) {
  const T = 12.5, d = (a, dur) => seg(t, T + a, T + a + dur); if (t < T) return;
  line(rect(o - 420, 1560, 840, 880), d(0, .6), 3.4); line([[o - 420, 1650], [o + 420, 1650]], d(.3, .3), 1.6); line([[o - 420, 2300], [o + 420, 2300]], d(.4, .3), 1.6); line([[o, 1560], [o, 1650]], d(.45, .15), 1.6);
  text('DWG 02 · REV A', o - 210, 1606, 30, d(.6, .3), { font: 'Taj', ltr: 1, a: .8 }); text('STATUS: PASSED', o + 210, 1606, 30, d(.7, .3), { font: 'Taj', ltr: 1, a: .8 });
  text('النبراس للألمنيوم', o, 1800, 104, d(.55, .5), { glow: 14 }); text('المعاينة مجانية', o, 1925, 86, d(1.15, .45), { font: 'AmiriIt' }); text('صوّر شباكك وأرسله لنا واتساب', o, 2040, 50, d(1.4, .4));
  const p = d(1.6, .35); if (p > 0) { const s = back(p); ctx.save(); ctx.translate(o, 2170); ctx.scale(s, s); ctx.fillStyle = '#C2410C'; ctx.shadowColor = 'rgba(242,100,28,.6)'; ctx.shadowBlur = 30; ctx.beginPath(); ctx.roundRect(-380, -78, 760, 156, 78); ctx.fill(); ctx.shadowBlur = 0; ctx.fillStyle = '#fff'; ctx.textBaseline = 'middle'; ctx.textAlign = 'center'; ctx.font = '60px Plex'; ctx.direction = 'rtl'; ctx.fillText('واتساب', 245, 2); ctx.font = '80px Taj'; ctx.direction = 'ltr'; ctx.fillText('0594774046', -95, 6); ctx.restore(); }
  text('الدمام · الخبر · القطيف', o, 2370, 40, d(1.9, .4), { a: .85 });
}

// ---------- subtitles: drawing notes, screen space ----------
const SUBS = [[-1, 2.25, 'رشّينا هالشباك بالماء… بقوة', 300], [2.35, 4.45, 'تتوقع كم قطرة دخلت؟', 300], [5.05, 6.4, 'الجلد المطاطي يوقفه', 300], [6.5, 7.9, 'المجرى يجمعه', 300], [8.0, 9.7, 'وفتحة التصريف تطلّعه برّا', 300]];
function subs(t) {
  const s = SUBS.find(s => t >= s[0] && t < s[1]); if (!s) return; const p = seg(t, s[0], s[0] + .3);
  ctx.save(); ctx.globalAlpha = eo(p); ctx.font = '58px Plex'; const w = Math.min(960, ctx.measureText(s[2]).width + 110), h = 124, x = W / 2 - w / 2, y = s[3] - h / 2;
  ctx.fillStyle = 'rgba(16,36,84,.88)'; ctx.fillRect(x, y, w, h); ctx.strokeStyle = INK; ctx.lineWidth = 3; ctx.strokeRect(x, y, w, h); ctx.lineWidth = 1.2; ctx.strokeRect(x + 8, y + 8, w - 16, h - 16);
  ctx.beginPath(); ctx.moveTo(W / 2 - 16, y + h); ctx.lineTo(W / 2, y + h + 16); ctx.lineTo(W / 2 + 16, y + h); ctx.stroke(); ctx.restore();
  Z = 1; LW = 1; text(s[2], W / 2, s[3] + 4, 58, 1, { glow: 4 });
}

// ---------- frame ----------
function render(t) {
  t = Math.round(t * 24) / 24;
  const c = cam(t), bump = t >= 12.07 && t < 12.4 ? Math.sin((t - 12.07) * 70) * 16 * (1 - seg(t, 12.07, 12.4)) : 0;
  Z = c.z; LW = Math.pow(Z, .65) / Z;
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#0d1116'; ctx.fillRect(0, 0, W, H);
  ctx.translate(W / 2, H / 2 + bump); ctx.scale(Z, Z); ctx.translate(-c.x, -c.y);
  ctx.imageSmoothingQuality = 'high'; ctx.drawImage(paper, 0, 0, SW, SH);
  fig1(t); fig2(t); titleBlock(t);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  const pan = t > 4.5 && t < 4.9 ? Math.sin(seg(t, 4.5, 4.9) * Math.PI) : 0;                    // whip-pan streaks
  if (pan > 0) { const r = rng(5); ctx.strokeStyle = INK; for (let i = 0; i < 46; i++) { const y = r() * H, x = r() * W, l = 200 + r() * 700; ctx.globalAlpha = pan * .45 * r(); ctx.lineWidth = 1 + r() * 3; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + l, y); ctx.stroke(); } ctx.globalAlpha = 1; }
  const v = ctx.createRadialGradient(W / 2, H / 2, 500, W / 2, H / 2, 1250); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(3,8,26,.5)'); ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
  ctx.globalCompositeOperation = 'overlay'; ctx.drawImage(grain, 0, 0, W, H); ctx.globalCompositeOperation = 'source-over';
  const pz = seg(t, 10.25, 10.6), pf = 1 - seg(t, 12.45, 12.75);
  if (pz > 0 && pf > 0) {
    ctx.save(); ctx.globalAlpha = Math.min(eo(pz), pf); ctx.fillStyle = 'rgba(14,32,78,.9)'; ctx.beginPath(); ctx.roundRect(110, 380, 860, 820, 40); ctx.fill();
    ctx.strokeStyle = INK; ctx.lineWidth = 3; ctx.stroke(); ctx.lineWidth = 1.2; ctx.beginPath(); ctx.roundRect(124, 394, 832, 792, 32); ctx.stroke(); ctx.restore();
    const ps = seg(t, 10.35, 10.6); if (ps > 0 && pf > 0) { ctx.save(); ctx.globalAlpha = pf; ctx.translate(540, 640); const k = back(ps); ctx.scale(k, k); text('صفر', 0, 0, 250, 1, { glow: 30 }); ctx.restore(); }
    ctx.save(); ctx.globalAlpha = pf; text('ولا قطرة دخلت', 540, 870, 84, seg(t, 10.8, 11.1)); ctx.restore();
    const sp = seg(t, 11.95, 12.07); if (sp > 0) { const k = lerp(2.4, 1, eo(sp)); ctx.save(); ctx.translate(540, 1050); ctx.rotate(-.08); ctx.scale(k, k); ctx.globalAlpha = sp * pf; ctx.strokeStyle = ORANGE; ctx.lineWidth = 8; ctx.strokeRect(-230, -70, 460, 140); ctx.lineWidth = 3; ctx.strokeRect(-216, -56, 432, 112); ctx.font = '72px Plex'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.direction = 'rtl'; ctx.fillStyle = ORANGE; ctx.fillText('اجتاز الاختبار', 0, 4); ctx.restore(); }
  }
  subs(t);
}
window.render = render;
window.READY = Promise.all(['58px Plex', '58px AmiriIt', '58px Taj'].map(f => document.fonts.load(f, 'ا0'))).then(() => { buildPaper(); render(0); });
