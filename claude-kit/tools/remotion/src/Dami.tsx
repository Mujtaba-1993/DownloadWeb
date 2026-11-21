import React from 'react';
import {AbsoluteFill, spring, useCurrentFrame, useVideoConfig, interpolate, staticFile, Img, Easing} from 'remotion';

const css = `@font-face{font-family:Plex;src:url(${staticFile('Plex.woff2')})}@font-face{font-family:Ami;src:url(${staticFile('AmiriIt.woff2')})}@font-face{font-family:Taj;src:url(${staticFile('Tajawal-Bold.ttf')})}`;
const OR = '#F2641C', NAVY = '#24307A', INK = '#16161A', BG = '#EEEDEA';
const E = Easing.bezier(0.65, 0, 0.35, 1);
const ip = (f: number, a: number[], b: number[], e = E) => interpolate(f, a, b, {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});
const sp = (f: number, at: number, fps: number, d = 12) => spring({frame: f - at, fps, config: {damping: d, mass: 0.7}});

const shade = (c: string, k: number) => {
  const n = parseInt(c.slice(1), 16); const ch = (s: number) => Math.max(0, Math.min(255, Math.round(((n >> s) & 255) * k)));
  return `rgb(${ch(16)},${ch(8)},${ch(0)})`;
};
const Ball: React.FC<{x: number; y: number; r: number; c?: string; sx?: number; sy?: number; o?: number; children?: React.ReactNode}> = ({x, y, r, c = OR, sx = 1, sy = 1, o = 1, children}) => (
  <div style={{position: 'absolute', left: x - r, top: y - r, width: 2 * r, height: 2 * r, borderRadius: '50%', opacity: o, transform: `scale(${sx},${sy})`, transformOrigin: '50% 100%',
    background: `radial-gradient(circle at 34% 28%, #ffffff 0%, ${shade(c, 1.35)} 9%, ${c} 38%, ${shade(c, 0.62)} 100%)`,
    boxShadow: `0 ${r * 0.45}px ${r * 0.6}px rgba(0,0,0,.16), inset -${r * 0.1}px -${r * 0.16}px ${r * 0.28}px rgba(0,0,0,.22)`}}>{children}</div>
);
// mascot = glossy ball with eyes
const Mascot: React.FC<{x: number; y: number; r: number; look?: number; sx?: number; sy?: number; o?: number}> = ({x, y, r, look = 0, sx, sy, o}) => {
  const f = useCurrentFrame(); const blink = (f % 70) > 64 ? 0.12 : 1;
  const eye = (dx: number) => (
    <div style={{position: 'absolute', left: r + dx - r * 0.17, top: r * 0.62, width: r * 0.34, height: r * 0.44, borderRadius: '50%', background: 'white', transform: `scaleY(${blink})`, boxShadow: 'inset 0 -3px 6px rgba(0,0,0,.15)'}}>
      <div style={{position: 'absolute', left: r * 0.08 + look * r * 0.07, top: r * 0.12, width: r * 0.18, height: r * 0.22, borderRadius: '50%', background: INK}} />
    </div>);
  return <Ball x={x} y={y} r={r} sx={sx} sy={sy} o={o}>{eye(-r * 0.24)}{eye(r * 0.24)}</Ball>;
};
// small floating balls around (Dami look)
const DOTS = [[120, 300, 16, OR], [960, 420, 22, '#F6B48C'], [180, 1500, 26, NAVY], [900, 1380, 14, OR], [80, 980, 12, '#F6B48C'], [1000, 900, 18, OR], [300, 1700, 12, OR], [760, 1700, 20, '#F6B48C'], [620, 240, 12, NAVY], [430, 520, 10, OR]] as const;
const Dots: React.FC<{o?: number}> = ({o = 1}) => {
  const f = useCurrentFrame();
  return <>{DOTS.map(([x, y, r, c], i) => <Ball key={i} x={x + Math.sin(f / 23 + i) * 14} y={y + Math.cos(f / 19 + i * 2) * 18} r={r} c={c} o={o} />)}</>;
};
const H: React.FC<{y: number; at: number; size?: number; children: React.ReactNode; out?: number}> = ({y, at, size = 96, children, out = 9999}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const s = sp(f, at, fps, 14); const o = ip(f, [out, out + 6], [0, 1]);
  return <div style={{position: 'absolute', top: y, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: size, color: INK, lineHeight: 1.15,
    opacity: s * (1 - o), transform: `translateY(${(1 - s) * 50 - o * 60}px)`, filter: `blur(${o * 10 + (1 - s) * 6}px)`}}>{children}</div>;
};
const It: React.FC<{c: string; color?: string}> = ({c, color = OR}) => <span style={{fontFamily: 'Ami', color, fontSize: '1.15em'}}>{c}</span>;

// scene wrapper with Dami-style zoom/blur transitions
const Scene: React.FC<{from: number; to: number; children: React.ReactNode}> = ({from, to, children}) => {
  const f = useCurrentFrame(); if (f < from - 1 || f > to + 7) return null;
  const i = ip(f, [from, from + 7], [0, 1]); const o = ip(f, [to, to + 7], [0, 1]);
  return <AbsoluteFill style={{opacity: i * (1 - o), transform: `scale(${0.92 + 0.08 * i + 0.25 * o})`, filter: `blur(${(1 - i) * 14 + o * 18}px)`}}>{children}</AbsoluteFill>;
};

const PenSvg: React.FC<{w?: number}> = ({w = 360}) => (
  <svg width={w} height={w * 0.11} viewBox="0 0 420 46"><path d="M0 23 L40 12 L40 34 Z" fill="#c9c9c9" /><rect x={38} y={10} width={30} height={26} rx={4} fill="#c9a45c" />
    <rect x={66} y={8} width={330} height={30} rx={14} fill={INK} /><rect x={250} y={2} width={130} height={8} rx={4} fill="#c9a45c" /></svg>
);

export const Dami: React.FC = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  // S1 mascot bounce + kick the pen
  const land = sp(f, 4, fps, 7); const squash = 1 + Math.max(0, Math.sin((f - 10) / 3)) * 0.12 * ip(f, [10, 30], [1, 0]);
  const kick = ip(f, [44, 58], [0, 1], Easing.in(Easing.cubic));
  const strike = ip(f, [36, 46], [0, 1]);
  // S2 window
  const slide = ip(f, [100, 130], [0, 1]); const sun = ip(f, [110, 150], [0, 1], Easing.out(Easing.cubic));
  // S3 door
  const open = ip(f, [190, 220], [0, 1]);
  // S4
  const card = sp(f, 300, fps, 13);
  return (
    <AbsoluteFill style={{background: BG}}>
      <style>{css}</style>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 40%, rgba(255,255,255,.9), rgba(255,255,255,0) 60%)'}} />
      <Dots />

      {/* S1: we don't sell pens */}
      <Scene from={0} to={66}>
        <H y={330} at={6}>احنا ما نبيع</H>
        <div style={{position: 'absolute', top: 450, width: '100%', textAlign: 'center', opacity: sp(f, 14, fps)}}>
          <span style={{position: 'relative', fontFamily: 'Ami', fontSize: 190, color: OR}}>أقلام
            <span style={{position: 'absolute', left: -20, right: -20, top: '56%', height: 14, background: INK, borderRadius: 7, transform: `scaleX(${strike}) rotate(-4deg)`, transformOrigin: 'right'}} /></span>
        </div>
        <Mascot x={540} y={interpolate(land, [0, 1], [-200, 1150])} r={190} sx={squash} sy={2 - squash} look={ip(f, [20, 40], [0, -1])} />
        <div style={{position: 'absolute', left: 250 - kick * 700, top: 1330 - kick * 500, transform: `rotate(${-12 - kick * 300}deg)`, opacity: sp(f, 18, fps), filter: 'drop-shadow(0 14px 14px rgba(0,0,0,.2))'}}><PenSvg /></div>
        <div style={{position: 'absolute', top: 1410, width: '100%', textAlign: 'center', fontFamily: 'Ami', fontSize: 64, color: '#0006', opacity: ip(f, [30, 38], [0, 1])}}>(لا والله)</div>
      </Scene>

      {/* S2: windows that open the world */}
      <Scene from={66} to={168}>
        <H y={300} at={70}>نبيع <It c="نوافذ" /></H>
        <div style={{position: 'absolute', left: 140, top: 640, width: 800, height: 640, borderRadius: 36, overflow: 'hidden', transform: `scale(${sp(f, 72, fps, 13)})`,
          boxShadow: '0 40px 80px rgba(0,0,0,.18)', background: `linear-gradient(180deg, ${interpolate(sun, [0, 1], [0, 1]) > .5 ? '#ffd9a8' : '#cfdbe4'} 0%, #f7efe2 100%)`}}>
          <Ball x={400} y={interpolate(sun, [0, 1], [760, 330])} r={130} c="#FFB23F" />
          {/* sliding sash */}
          <div style={{position: 'absolute', top: 0, bottom: 0, left: `${50 * slide}%`, width: '50%', border: '18px solid #2b2d31', borderRadius: 4, boxSizing: 'border-box', background: 'linear-gradient(160deg, rgba(190,210,225,.85), rgba(160,185,205,.75))'}} />
          <div style={{position: 'absolute', top: 0, bottom: 0, right: 0, width: '50%', border: '18px solid #2b2d31', boxSizing: 'border-box', background: 'linear-gradient(160deg, rgba(190,210,225,.55), rgba(160,185,205,.45))'}} />
          <div style={{position: 'absolute', inset: 0, border: '26px solid #1f2125', borderRadius: 36}} />
        </div>
        <H y={1350} at={128} size={84}>تفتح لك <It c="الدنيا." /></H>
        <Mascot x={interpolate(sp(f, 96, fps), [0, 1], [-200, 170])} y={1610} r={95} look={1} />
      </Scene>

      {/* S3: doors that welcome your family */}
      <Scene from={168} to={236}>
        <H y={280} at={170} size={110}><It c="وأبواب" /></H>
        <div style={{position: 'absolute', left: 290, top: 560, width: 500, height: 860, perspective: 1600, transform: `scale(${sp(f, 172, fps, 13)})`}}>
          <div style={{position: 'absolute', inset: 0, borderRadius: 16, background: 'radial-gradient(ellipse at 50% 45%, #fff6dc 0%, #f6c66e 50%, #b66d1f 100%)', boxShadow: '0 40px 80px rgba(0,0,0,.2)'}} />
          <div style={{position: 'absolute', inset: 0, borderRadius: 16, transformOrigin: 'right center', transform: `rotateY(${open * 80}deg)`, background: 'linear-gradient(90deg,#1d1f23,#363940 55%,#202226)', boxShadow: '0 30px 60px rgba(0,0,0,.35)'}}>
            {[0.22, 0.34, 0.46, 0.58, 0.7].map((y) => <div key={y} style={{position: 'absolute', top: `${y * 100}%`, left: '14%', width: '56%', height: 12, background: 'linear-gradient(90deg,#9fb4c2,#e6eef2)'}} />)}
            <div style={{position: 'absolute', left: 50, top: '25%', height: '50%', width: 14, borderRadius: 7, background: 'linear-gradient(90deg,#8d8d8d,#f4f4f4,#9a9a9a)'}} />
          </div>
          <div style={{position: 'absolute', inset: -22, border: '22px solid #1f2125', borderRadius: 26}} />
        </div>
        {/* family = 3 mascots popping out of the light */}
        {[[-150, 70, OR], [0, 90, NAVY], [150, 60, '#F6B48C']].map(([dx, r, c], i) => {
          const s = sp(f, 212 + i * 4, fps, 9);
          return <Ball key={i} x={540 + (dx as number) * s} y={1330 - s * 40} r={(r as number) * s} c={c as string} />;
        })}
        <H y={1500} at={214} size={84}>تستقبل فيها <It c="أهلك." /></H>
      </Scene>

      {/* S4: brand + comment card CTA */}
      <Scene from={236} to={9999}>
        <Img src={staticFile('logo.png')} style={{position: 'absolute', top: 260, left: 440, width: 200, height: 200, borderRadius: 100, boxShadow: '0 20px 40px rgba(0,0,0,.2)',
          transform: `translateY(${(1 - sp(f, 240, fps, 8)) * -500}px)`}} />
        <H y={500} at={246} size={130}>النبراس</H>
        <H y={700} at={252} size={110}><It c="للألمنيوم" color={NAVY} /></H>
        <div style={{position: 'absolute', left: 110, right: 110, top: 960, background: 'white', borderRadius: 34, padding: '34px 40px', boxShadow: '0 30px 70px rgba(0,0,0,.14)', direction: 'rtl',
          transform: `translateY(${(1 - card) * 300}px)`, opacity: card}}>
          <div style={{fontFamily: 'Plex', fontSize: 40, color: INK, marginBottom: 24}}>التعليقات</div>
          {[['أنت', 'كم سعر المعاينة؟', NAVY, 300], ['النبراس للألمنيوم', 'المعاينة مجانية ✓', OR, 316]].map(([n, t, c, at]) => {
            const s = sp(f, at as number, fps, 14);
            return <div key={n as string} style={{display: 'flex', alignItems: 'center', gap: 22, marginBottom: 22, opacity: s, transform: `translateX(${(1 - s) * -40}px)`}}>
              <div style={{width: 64, height: 64, borderRadius: 32, background: `radial-gradient(circle at 34% 28%, #fff, ${c} 40%)`}} />
              <div><div style={{fontFamily: 'Taj', fontSize: 32, color: '#0008'}}>{n}</div><div style={{fontFamily: 'Plex', fontSize: 46, color: INK}}>{t}</div></div>
            </div>;
          })}
        </div>
        <div style={{position: 'absolute', top: 1420, width: '100%', display: 'flex', justifyContent: 'center', transform: `scale(${sp(f, 334, fps, 9)})`}}>
          <div style={{background: OR, color: 'white', borderRadius: 80, padding: '28px 64px', fontFamily: 'Plex', fontSize: 58, direction: 'rtl', boxShadow: '0 20px 40px rgba(242,100,28,.35), inset 0 -6px 12px rgba(0,0,0,.15)'}}>
            واتساب <span style={{fontFamily: 'Taj'}}>0594774046</span></div>
        </div>
        <Mascot x={880} y={1640} r={90} look={-1} o={ip(f, [340, 348], [0, 1])} />
      </Scene>
    </AbsoluteFill>
  );
};
