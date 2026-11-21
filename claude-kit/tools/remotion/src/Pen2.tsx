import React from 'react';
import {AbsoluteFill, spring, useCurrentFrame, useVideoConfig, interpolate, staticFile, Img, Easing} from 'remotion';

const css = `@font-face{font-family:Plex;src:url(${staticFile('Plex.woff2')})}@font-face{font-family:Ami;src:url(${staticFile('AmiriIt.woff2')})}@font-face{font-family:AmiN;src:url(${staticFile('Amiri.woff2')})}@font-face{font-family:Taj;src:url(${staticFile('Tajawal-Bold.ttf')})}`;
const INK = '#141414', CREAM = '#EEE8DD', GOLD = '#B8873A', RED = '#D9432F', ALU = '#2A2C30';
const E = Easing.bezier(0.65, 0, 0.35, 1);
const useF = () => { const r = useCurrentFrame(); return r < 150 ? r : r < 300 ? 150 + (r - 150) * 0.6 : 240 + (r - 300) * (90 / 135); };
const ip = (f: number, a: number[], b: number[], e = E) => interpolate(f, a, b, {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});

const T: React.FC<{c: React.ReactNode; y: number; at: number; out?: number; size: number; font?: string; color?: string; reveal?: number}> = ({c, y, at, out = 9999, size, font = 'Plex', color = INK, reveal}) => {
  const f = useF(); const {fps} = useVideoConfig();
  const s = spring({frame: f - at, fps, config: {damping: 14, mass: 0.6}});
  const o = ip(f, [out, out + 10], [0, 1]);
  const clip = reveal === undefined ? 'none' : `inset(-20% 0 -20% ${100 - reveal * 100}%)`;
  return <div style={{position: 'absolute', top: y, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: font, fontSize: size, color, lineHeight: 1.1,
    opacity: (reveal === undefined ? s : 1) * (1 - o), transform: `translateY(${(1 - s) * 60 - o * 80}px)`, filter: `blur(${o * 8}px)`, clipPath: clip}}>{c}</div>;
};

const PenSvg: React.FC = () => (
  <svg width={420} height={46} viewBox="0 0 420 46">
    <defs><linearGradient id="pb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#3a3d44" /><stop offset=".5" stopColor="#15161a" /><stop offset="1" stopColor="#0a0a0c" /></linearGradient>
      <linearGradient id="pg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#f3d999" /><stop offset=".5" stopColor="#b8873a" /><stop offset="1" stopColor="#7a5520" /></linearGradient></defs>
    <path d="M0 23 L40 12 L40 34 Z" fill="#c9c9c9" /><rect x={38} y={10} width={30} height={26} rx={4} fill="url(#pg)" />
    <rect x={66} y={8} width={330} height={30} rx={14} fill="url(#pb)" /><rect x={250} y={2} width={130} height={8} rx={4} fill="url(#pg)" />
  </svg>
);

export const Pen2: React.FC = () => {
  const f = useF(); const {fps} = useVideoConfig();
  // ---------- scene A: pen strikes "أقلام"
  const penIn = spring({frame: f - 8, fps, config: {damping: 16}});
  const strike = ip(f, [26, 40], [0, 1]);
  const flick = ip(f, [44, 56], [0, 1], Easing.in(Easing.cubic));
  const penX = interpolate(penIn, [0, 1], [1300, 760]) - strike * 420 - flick * 900;
  const penY = 905 + interpolate(penIn, [0, 1], [-500, 0]) + flick * 700;
  const penR = interpolate(penIn, [0, 1], [-60, -14]) + flick * -120;
  // ---------- scene B/C: window -> door frame morph
  const draw = ip(f, [60, 84], [0, 1]);
  const morph = ip(f, [152, 176], [0, 1]);
  const fw = interpolate(morph, [0, 1], [820, 560]), fh = interpolate(morph, [0, 1], [620, 1000]);
  const cx = 540, cy = interpolate(morph, [0, 1], [1080, 1130]);
  const glassIn = ip(f, [74, 90], [0, 1]);
  const sash = ip(f, [96, 128], [0, 1]);
  const sweep = ip(f, [130, 150], [-0.4, 1.4]);
  const sashFade = ip(f, [150, 160], [1, 0]);
  const leafIn = ip(f, [168, 180], [0, 1]);
  const open = ip(f, [192, 222], [0, 1]);
  const flood = ip(f, [222, 240], [0, 1], Easing.in(Easing.quad));
  const frameOut = ip(f, [236, 244], [1, 0]);
  const perim = 2 * (820 + 620);
  return (
    <AbsoluteFill style={{background: CREAM}}>
      <style>{css}</style>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(255,255,255,.55) 0%, rgba(0,0,0,0) 55%, rgba(60,40,20,.10) 100%)'}} />
      <div style={{position: 'absolute', top: 70, right: 70, fontFamily: 'Taj', fontSize: 30, color: '#0007', direction: 'ltr'}}>@aluminum25_alnbras</div>

      {/* ---------- A ---------- */}
      {f < 70 && <>
        <T c="ما نبيع" y={720} at={2} out={54} size={150} />
        <div style={{position: 'absolute', top: 880, width: '100%', textAlign: 'center', opacity: 1 - ip(f, [54, 64], [0, 1])}}>
          <span style={{position: 'relative', display: 'inline-block', fontFamily: 'Ami', fontSize: 210, color: GOLD,
            transform: `scale(${spring({frame: f - 10, fps, config: {damping: 11}})})`}}>أقلام
            <span style={{position: 'absolute', left: -24, right: -24, top: '54%', height: 16, background: RED, borderRadius: 8,
              transform: `scaleX(${strike}) rotate(-3deg)`, transformOrigin: 'right'}} /></span>
        </div>
        <div style={{position: 'absolute', left: penX, top: penY, transform: `rotate(${penR}deg)`, transformOrigin: '0 23px', filter: 'drop-shadow(0 18px 18px rgba(0,0,0,.25))'}}><PenSvg /></div>
      </>}

      {/* ---------- B text ---------- */}
      {f >= 62 && f < 176 && <>
        <T c="نبيع" y={330} at={64} out={152} size={120} />
        <T c="نوافذ" y={470} at={0} out={152} size={200} font="Ami" color={GOLD} reveal={sash} />
      </>}
      {f >= 170 && f < 246 && <T c="وأبواب" y={260} at={0} out={226} size={210} font="Ami" color={GOLD} reveal={ip(f, [172, 192], [0, 1])} />}

      {/* ---------- frame (window -> door) ---------- */}
      {f >= 60 && f < 246 && (
        <div style={{position: 'absolute', left: cx - fw / 2, top: cy - fh / 2, width: fw, height: fh, opacity: frameOut, perspective: 1800}}>
          {/* light behind door */}
          <div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 40%, #fff6dc 0%, #f4c76a 45%, #8a5a1c 100%)', opacity: open}} />
          {/* glass (window) */}
          <div style={{position: 'absolute', inset: 0, opacity: glassIn * sashFade, overflow: 'hidden',
            background: 'linear-gradient(160deg, #cfdde6 0%, #9fb4c2 55%, #b9c9d3 100%)'}}>
            <div style={{position: 'absolute', top: '-50%', height: '200%', width: 120, left: `${sweep * 100}%`, transform: 'rotate(20deg)', background: 'linear-gradient(90deg, transparent, rgba(255,255,255,.75), transparent)'}} />
            {/* fixed half mullion + sliding sash */}
            <div style={{position: 'absolute', top: 0, bottom: 0, width: '50%', right: `${sash * 50}%`, border: `14px solid ${ALU}`, boxSizing: 'border-box',
              background: 'linear-gradient(160deg, rgba(255,255,255,.25), rgba(255,255,255,0))', boxShadow: '0 0 30px rgba(0,0,0,.25)'}}>
              <div style={{position: 'absolute', left: 14, top: '42%', width: 10, height: 90, borderRadius: 5, background: '#d9d9d9'}} />
            </div>
          </div>
          {/* door leaf */}
          <div style={{position: 'absolute', inset: 0, opacity: leafIn, transformOrigin: 'right center', transform: `rotateY(${open * 78}deg)`,
            background: 'linear-gradient(90deg, #1d1f23, #34373d 55%, #202226)', boxShadow: `${open * 40}px 0 60px rgba(0,0,0,.5)`}}>
            {[0.22, 0.34, 0.46, 0.58, 0.70].map((y) => <div key={y} style={{position: 'absolute', top: `${y * 100}%`, left: '14%', width: '58%', height: 12, background: 'linear-gradient(90deg,#9fb4c2,#e6eef2)'}} />)}
            <div style={{position: 'absolute', right: 56, top: '25%', height: '50%', width: 14, borderRadius: 7, background: 'linear-gradient(90deg,#8d8d8d,#f4f4f4,#9a9a9a)'}} />
          </div>
          {/* aluminium outer frame (self-drawing) */}
          <svg width={fw + 40} height={fh + 40} style={{position: 'absolute', left: -20, top: -20, overflow: 'visible'}}>
            <rect x={20} y={20} width={fw} height={fh} fill="none" stroke={ALU} strokeWidth={26} strokeDasharray={perim + 400} strokeDashoffset={(perim + 400) * (1 - draw)} />
          </svg>
        </div>
      )}
      {/* light cone on the floor */}
      {f >= 192 && f < 246 && <div style={{position: 'absolute', left: 0, right: 0, top: cy + fh / 2, height: 420, opacity: open * frameOut,
        background: 'linear-gradient(180deg, rgba(244,199,106,.55), rgba(244,199,106,0))', clipPath: `polygon(${50 - fw / 21.6}% 0, ${50 + fw / 21.6}% 0, 95% 100%, 5% 100%)`}} />}
      {/* flood to cream */}
      {f >= 222 && f < 252 && <div style={{position: 'absolute', left: 540, top: cy, width: 10, height: 10, borderRadius: '50%', background: '#fff3d6',
        transform: `translate(-50%,-50%) scale(${flood * 420})`, opacity: 1 - ip(f, [242, 252], [0, 1])}} />}

      {/* ---------- D end card ---------- */}
      {f >= 240 && <>
        <Img src={staticFile('logo.png')} style={{position: 'absolute', top: 360, left: 430, width: 220, height: 220, borderRadius: 110, boxShadow: '0 20px 40px rgba(0,0,0,.25)',
          transform: `translateY(${(1 - spring({frame: f - 242, fps, config: {damping: 9}})) * -600}px)`}} />
        <T c="النبراس" y={630} at={250} size={150} />
        <T c="للألمنيوم" y={835} at={256} size={130} font="Ami" color={GOLD} />
        {[['معاينة', 'مجانية'], ['تفصيل', 'على مقاسك'], ['تركيب', 'وضمان']].map(([a, b], i) => {
          const at = 266 + i * 10; const s = spring({frame: f - at, fps, config: {damping: 14}});
          return <div key={a} style={{position: 'absolute', top: 1060 + i * 120, right: 230, direction: 'rtl', display: 'flex', alignItems: 'center', gap: 34, opacity: s, transform: `translateX(${(1 - s) * -60}px)`}}>
            <div style={{width: 30, height: 30, borderRadius: 15, background: RED, boxShadow: '0 0 20px rgba(217,67,47,.6)'}} />
            <span style={{fontFamily: 'Plex', fontSize: 68, color: INK}}>{a} <span style={{fontFamily: 'Ami', color: GOLD}}>{b}</span></span>
          </div>;
        })}
        <div style={{position: 'absolute', right: 244, top: 1090, width: 3, height: ip(f, [266, 290], [0, 240]), background: '#0003'}} />
        <div style={{position: 'absolute', top: 1470, width: '100%', display: 'flex', justifyContent: 'center', opacity: spring({frame: f - 296, fps}), transform: `scale(${spring({frame: f - 296, fps, config: {damping: 10}})})`}}>
          <div style={{background: INK, color: 'white', borderRadius: 70, padding: '26px 60px', fontFamily: 'Plex', fontSize: 58, direction: 'rtl'}}>
            واتساب <span style={{color: '#E9C27A', fontFamily: 'Taj'}}>0594774046</span></div>
        </div>
        <div style={{position: 'absolute', top: 1630, width: '100%', textAlign: 'center', fontSize: 60, color: INK, opacity: ip(f, [306, 312], [0, 1]),
          transform: `translateY(${Math.sin(f / 5) * 10}px)`}}>↓</div>
      </>}
    </AbsoluteFill>
  );
};
