import React from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, spring, useCurrentFrame, useVideoConfig, interpolate, staticFile, Img, Easing} from 'remotion';

const css = `@font-face{font-family:Plex;src:url(${staticFile('Plex.woff2')})}@font-face{font-family:Ami;src:url(${staticFile('AmiriIt.woff2')})}@font-face{font-family:Taj;src:url(${staticFile('Tajawal-Bold.ttf')})}`;
const NAVY = '#1F2A6B', OR = '#F2641C';
const ip = (f: number, a: number[], b: number[]) => interpolate(f, a, b, {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.65, 0, 0.35, 1)});
const SRC = staticFile('colors.mp4');
// source segments (seconds) for each colour
const COLS = [
  {n: '١', name: 'أسود', from: 0.3, sw: '#151515'},
  {n: '٢', name: 'سلفر', from: 3.3, sw: '#9aa0a6'},
  {n: '٣', name: 'خشبي', from: 6.3, sw: '#8a5a2b'},
  {n: '٤', name: 'شامبين', from: 12.3, sw: '#b9a27e'},
];
const SEG = 48; const START = 15; // colour k shows from START+k*SEG

const Clip: React.FC<{from: number; style?: React.CSSProperties}> = ({from, style}) => (
  <OffthreadVideo src={SRC} startFrom={Math.round(from * 30)} muted style={{width: '100%', height: '100%', objectFit: 'cover', ...style}} />
);

const Label: React.FC<{n: string; name: string; at: number; sw: string}> = ({n, name, at, sw}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const s = spring({frame: f - at, fps, config: {damping: 13}});
  return <div style={{position: 'absolute', bottom: 300, width: '100%', display: 'flex', justifyContent: 'center', transform: `translateY(${(1 - s) * 160}px)`, opacity: s}}>
    <div style={{display: 'flex', alignItems: 'center', gap: 26, background: 'rgba(16,17,20,.82)', borderRadius: 90, padding: '18px 44px 18px 22px', direction: 'rtl', boxShadow: '0 20px 50px rgba(0,0,0,.35)'}}>
      <div style={{width: 110, height: 110, borderRadius: 55, background: OR, color: 'white', fontFamily: 'Taj', fontSize: 76, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${spring({frame: f - at - 4, fps, config: {damping: 8}})})`}}>{n}</div>
      <div style={{fontFamily: 'Plex', fontSize: 78, color: 'white'}}>{name}</div>
      <div style={{width: 54, height: 54, borderRadius: 12, background: sw, border: '4px solid white'}} />
    </div>
  </div>;
};

const Body: React.FC = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const gridAt = START + 4 * SEG; const openAt = gridAt + 90; const endAt = openAt + 60;
  const hook = spring({frame: f - 2, fps, config: {damping: 12}});
  return (
    <AbsoluteFill style={{background: '#111'}}>
      <style>{css}</style>
      {/* colour segments with sash-style sweep reveals */}
      {COLS.map((c, k) => {
        const at = START + k * SEG; const from = k === 0 ? 0 : at - 8;
        return <Sequence key={k} from={from} durationInFrames={(k === 3 ? gridAt + 8 : at + SEG + 8) - from}>
          <SegView c={c} k={k} at={at} />
        </Sequence>;
      })}
      {/* hook */}
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,12,20,.85) 0%, rgba(10,12,20,0) 30%)', opacity: ip(f, [gridAt - 10, gridAt], [1, 0])}} />
      <div style={{position: 'absolute', top: 150, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: 96, color: 'white', lineHeight: 1.15,
        transform: `scale(${hook})`, opacity: ip(f, [gridAt - 10, gridAt], [1, 0]), textShadow: '0 6px 30px rgba(0,0,0,.6)'}}>
        أي لون <span style={{fontFamily: 'Ami', color: '#FFB46B', fontSize: 120}}>يناسب بيتك؟</span>
      </div>
      {/* chips row: lights up the current colour */}
      <div style={{position: 'absolute', top: 340, width: '100%', display: 'flex', justifyContent: 'center', gap: 22, direction: 'rtl', opacity: ip(f, [8, 18], [0, 1]) * ip(f, [gridAt - 10, gridAt], [1, 0])}}>
        {COLS.map((c, k) => { const on = f >= START + k * SEG; return <div key={k} style={{width: 92, height: 92, borderRadius: 46, background: on ? OR : 'rgba(255,255,255,.18)', border: '3px solid rgba(255,255,255,.7)', color: 'white', fontFamily: 'Taj', fontSize: 58, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${on ? 1 + .25 * Math.max(0, 1 - (f - START - k * SEG) / 8) : .9})`}}>{c.n}</div>; })}
      </div>

      {/* grid: all four side by side */}
      <Sequence from={gridAt} durationInFrames={openAt - gridAt + 8}>
        <Grid />
      </Sequence>
      {/* payoff: the window opens */}
      <Sequence from={openAt} durationInFrames={1000}>
        <Opening endIn={endAt - openAt} />
      </Sequence>
    </AbsoluteFill>
  );
};

const SegView: React.FC<{c: typeof COLS[0]; k: number; at: number}> = ({c, k, at}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); // local frame
  const local0 = k === 0 ? at : 8; // where the colour "lands" in local time
  const rev = k === 0 ? 1 : ip(f, [0, 8], [0, 1]);
  const edge = (1 - rev) * 100;
  return <AbsoluteFill style={{clipPath: `inset(0 0 0 ${edge}%)`}}>
    <Clip from={c.from - (k === 0 ? 0 : 8 / 30)} />
    {rev < 1 && <div style={{position: 'absolute', top: 0, bottom: 0, left: `${edge}%`, width: 26, background: 'linear-gradient(90deg,#555,#ddd,#666)', boxShadow: '0 0 40px rgba(0,0,0,.5)'}} />}
    <Label n={c.n} name={c.name} at={k === 0 ? 40 : local0 + 2} sw={c.sw} />
  </AbsoluteFill>;
};

const Grid: React.FC = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  return <AbsoluteFill style={{background: '#F2ECE1'}}>
    <div style={{position: 'absolute', top: 120, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: 88, color: NAVY, opacity: spring({frame: f, fps})}}>
      وأنت؟ <span style={{fontFamily: 'Ami', color: OR, fontSize: 110}}>أي رقم؟</span></div>
    {COLS.map((c, k) => {
      const s = spring({frame: f - 4 - k * 4, fps, config: {damping: 13}});
      const x = 60 + (k % 2 === 0 ? 500 : 0), y = 330 + Math.floor(k / 2) * 640;
      return <div key={k} style={{position: 'absolute', left: x, top: y, width: 460, height: 600, borderRadius: 28, overflow: 'hidden', boxShadow: '0 24px 50px rgba(0,0,0,.25)', transform: `scale(${s})`}}>
        <div style={{position: 'absolute', left: -40, top: -95, width: 560, height: 996}}><Clip from={c.from + 0.5} /></div>
        <div style={{position: 'absolute', bottom: 18, right: 18, width: 96, height: 96, borderRadius: 48, background: OR, color: 'white', fontFamily: 'Taj', fontSize: 66, display: 'flex', alignItems: 'center', justifyContent: 'center', border: '4px solid white'}}>{c.n}</div>
      </div>;
    })}
    <div style={{position: 'absolute', bottom: 120, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: 64, color: NAVY, opacity: spring({frame: f - 25, fps})}}>
      اكتب رقمك في التعليقات <span style={{display: 'inline-block', transform: `translateY(${Math.sin(f / 4) * 10}px)`}}>↓</span></div>
  </AbsoluteFill>;
};

const Opening: React.FC<{endIn: number}> = ({endIn}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const z = interpolate(f, [0, 120], [1.0, 1.12]);
  const end = spring({frame: f - endIn, fps, config: {damping: 13}});
  return <AbsoluteFill style={{clipPath: `inset(0 0 0 ${ip(f, [0, 8], [100, 0])}%)`}}>
    <AbsoluteFill style={{transform: `scale(${z})`}}><Clip from={16.0} /></AbsoluteFill>
    <div style={{position: 'absolute', top: 170, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: 84, color: 'white', textShadow: '0 6px 30px rgba(0,0,0,.7)', opacity: spring({frame: f - 6, fps})}}>
      نفصّله <span style={{fontFamily: 'Ami', color: '#FFB46B', fontSize: 104}}>بأي لون تختاره</span></div>
    <AbsoluteFill style={{background: 'rgba(12,14,24,.72)', opacity: end}} />
    <Img src={staticFile('logo.png')} style={{position: 'absolute', top: 560, left: 420, width: 240, height: 240, borderRadius: 120, transform: `scale(${end})`, boxShadow: '0 20px 50px rgba(0,0,0,.4)'}} />
    <div style={{position: 'absolute', top: 860, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: 90, color: 'white', opacity: end}}>النبراس <span style={{fontFamily: 'Ami', color: '#FFB46B'}}>للألمنيوم</span></div>
    <div style={{position: 'absolute', top: 1040, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: 62, color: 'white', opacity: spring({frame: f - endIn - 8, fps})}}>المعاينة مجانية</div>
    <div style={{position: 'absolute', top: 1180, width: '100%', display: 'flex', justifyContent: 'center', transform: `scale(${spring({frame: f - endIn - 14, fps, config: {damping: 9}})})`}}>
      <div style={{background: OR, color: 'white', borderRadius: 70, padding: '22px 56px', fontFamily: 'Taj', fontSize: 60, direction: 'rtl'}}>واتساب 0594774046</div></div>
  </AbsoluteFill>;
};

// v2 hook: 4 colours flash in the first 1.2 s, the question is on screen from frame 0
const FL = 36;
const Flash: React.FC = () => {
  const f = useCurrentFrame(); const k = Math.min(3, Math.floor(f / 9));
  return <AbsoluteFill style={{background: '#111'}}>
    <style>{css}</style>
    <Clip from={COLS[k].from + 0.5} />
    <AbsoluteFill style={{background: `rgba(255,255,255,${Math.max(0, 0.5 - (f % 9) / 9)})`}} />
    <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,12,20,.85) 0%, rgba(10,12,20,0) 30%)'}} />
    <div style={{position: 'absolute', top: 150, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: 104, color: 'white', textShadow: '0 6px 30px rgba(0,0,0,.6)'}}>
      أي لون <span style={{fontFamily: 'Ami', color: '#FFB46B', fontSize: 130}}>يناسب بيتك؟</span></div>
    <div style={{position: 'absolute', bottom: 330, width: '100%', textAlign: 'center', fontFamily: 'Taj', fontSize: 260, color: 'white', textShadow: '0 10px 40px rgba(0,0,0,.6)', transform: `scale(${1.3 - (f % 9) / 30})`}}>{COLS[k].n}</div>
  </AbsoluteFill>;
};
export const Colors: React.FC = () => <AbsoluteFill>
  <Sequence from={0} durationInFrames={FL}><Flash /></Sequence>
  <Sequence from={FL}><Body /></Sequence>
</AbsoluteFill>;
