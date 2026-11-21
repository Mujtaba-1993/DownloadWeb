import React from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, spring, useCurrentFrame, useVideoConfig, interpolate, staticFile, Img, Easing} from 'remotion';

const css = `@font-face{font-family:Plex;src:url(${staticFile('Plex.woff2')})}@font-face{font-family:Ami;src:url(${staticFile('AmiriIt.woff2')})}@font-face{font-family:Taj;src:url(${staticFile('Tajawal-Bold.ttf')})}`;
const NAVY = '#1F2A6B', OR = '#F2641C', WARM = '#FFB46B';
const ip = (f: number, a: number[], b: number[]) => interpolate(f, a, b, {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.65, 0, 0.35, 1)});
const SRC = staticFile('doors.mp4');
const D = [
  {n: '١', from: 0.1, a: 'هادي', b: 'وراقي'},
  {n: '٢', from: 1.6, a: 'فخم', b: 'وواثق'},
  {n: '٣', from: 3.1, a: 'كلاسيكي', b: 'ودافي'},
  {n: '٤', from: 4.6, a: 'عصري', b: 'وعملي'},
];
const FL = 36, GRID1 = 118, SEG = 60, CTA = GRID1 + 4 * SEG, END = CTA + 60;

const Clip: React.FC<{from: number; rate?: number}> = ({from, rate = 1}) => (
  <OffthreadVideo src={SRC} startFrom={Math.round(from * 30)} playbackRate={rate} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
);
const T: React.FC<{y: number; at: number; size?: number; children: React.ReactNode; color?: string}> = ({y, at, size = 92, children, color = 'white'}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const s = spring({frame: f - at, fps, config: {damping: 12}});
  return <div style={{position: 'absolute', top: y, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: size, color, lineHeight: 1.15,
    transform: `translateY(${(1 - s) * 60}px) scale(${0.85 + 0.15 * s})`, opacity: s, textShadow: color === 'white' ? '0 6px 30px rgba(0,0,0,.6)' : 'none'}}>{children}</div>;
};
const Grid: React.FC<{title: React.ReactNode; foot?: React.ReactNode}> = ({title, foot}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  return <AbsoluteFill style={{background: '#F2ECE1'}}>
    <style>{css}</style>
    <div style={{position: 'absolute', top: 110, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: 84, color: NAVY, lineHeight: 1.2, opacity: spring({frame: f, fps})}}>{title}</div>
    {D.map((c, k) => {
      const s = spring({frame: f - 3 - k * 3, fps, config: {damping: 12}});
      const x = 60 + (k % 2 === 0 ? 500 : 0), y = 400 + Math.floor(k / 2) * 640;
      return <div key={k} style={{position: 'absolute', left: x, top: y, width: 460, height: 600, borderRadius: 28, overflow: 'hidden', boxShadow: '0 24px 50px rgba(0,0,0,.22)', transform: `scale(${s})`}}>
        <Img src={staticFile(`door_${k + 1}.jpg`)} style={{position: 'absolute', left: -190, top: -330, width: 840, height: 1493, objectFit: 'cover'}} />
        <div style={{position: 'absolute', bottom: 16, right: 16, width: 96, height: 96, borderRadius: 48, background: OR, color: 'white', fontFamily: 'Taj', fontSize: 66, display: 'flex', alignItems: 'center', justifyContent: 'center', border: '4px solid white'}}>{c.n}</div>
      </div>;
    })}
    {foot}
  </AbsoluteFill>;
};

export const Doors: React.FC = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  return <AbsoluteFill style={{background: '#111'}}>
    <style>{css}</style>
    {/* 0-1.2 s: flash of all four with the question on screen from frame 0 */}
    <Sequence from={0} durationInFrames={FL}>
      <FlashCut />
    </Sequence>
    {/* the four doors side by side while the question is spoken */}
    <Sequence from={FL} durationInFrames={GRID1 - FL + 6}>
      <Grid title={<>بابك يقول عن <span style={{fontFamily: 'Ami', color: OR, fontSize: 104}}>شخصيتك</span><br />أي واحد أنت؟</>} />
    </Sequence>
    {/* each door with its personality */}
    {D.map((c, k) => <Sequence key={k} from={GRID1 + k * SEG} durationInFrames={SEG + 8}><One c={c} first={k === 0} /></Sequence>)}
    {/* CTA grid */}
    <Sequence from={CTA} durationInFrames={END - CTA + 8}>
      <Grid title={<>وأنت؟ <span style={{fontFamily: 'Ami', color: OR, fontSize: 104}}>أي رقم؟</span></>}
        foot={<CtaFoot />} />
    </Sequence>
    <Sequence from={END}><EndCard /></Sequence>
  </AbsoluteFill>;
};

const FlashCut: React.FC = () => {
  const f = useCurrentFrame(); const k = Math.min(3, Math.floor(f / 9));
  return <AbsoluteFill>
    <style>{css}</style>
    <Clip from={D[k].from + 0.4} />
    <AbsoluteFill style={{background: `rgba(255,255,255,${Math.max(0, 0.55 - (f % 9) / 9)})`}} />
    <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,12,20,.85) 0%, rgba(10,12,20,0) 32%)'}} />
    <div style={{position: 'absolute', top: 140, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: 96, color: 'white', textShadow: '0 6px 30px rgba(0,0,0,.6)'}}>
      بابك يقول عن <span style={{fontFamily: 'Ami', color: WARM, fontSize: 116}}>شخصيتك</span></div>
    <div style={{position: 'absolute', bottom: 260, width: '100%', textAlign: 'center', fontFamily: 'Taj', fontSize: 280, color: 'white', textShadow: '0 10px 40px rgba(0,0,0,.6)', transform: `scale(${1.3 - (f % 9) / 30})`}}>{D[k].n}</div>
  </AbsoluteFill>;
};

const One: React.FC<{c: typeof D[0]; first: boolean}> = ({c, first}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const rev = first ? ip(f, [0, 8], [0, 1]) : ip(f, [0, 8], [0, 1]);
  const z = interpolate(f, [0, SEG], [1.0, 1.08]);
  const s = spring({frame: f - 6, fps, config: {damping: 11}});
  return <AbsoluteFill style={{clipPath: `inset(0 0 0 ${(1 - rev) * 100}%)`}}>
    <style>{css}</style>
    <AbsoluteFill style={{transform: `scale(${z})`}}><Clip from={c.from} rate={0.75} /></AbsoluteFill>
    {rev < 1 && <div style={{position: 'absolute', top: 0, bottom: 0, left: `${(1 - rev) * 100}%`, width: 26, background: 'linear-gradient(90deg,#555,#ddd,#666)'}} />}
    <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,12,20,.75) 0%, rgba(10,12,20,0) 28%, rgba(10,12,20,0) 70%, rgba(10,12,20,.7) 100%)'}} />
    <div style={{position: 'absolute', top: 150, width: '100%', display: 'flex', justifyContent: 'center', transform: `scale(${s})`}}>
      <div style={{width: 150, height: 150, borderRadius: 75, background: OR, color: 'white', fontFamily: 'Taj', fontSize: 110, display: 'flex', alignItems: 'center', justifyContent: 'center', border: '6px solid white', boxShadow: '0 16px 40px rgba(0,0,0,.4)'}}>{c.n}</div>
    </div>
    <T y={1500} at={8} size={110}>{c.a} <span style={{fontFamily: 'Ami', color: WARM, fontSize: 126}}>{c.b}</span></T>
  </AbsoluteFill>;
};

const CtaFoot: React.FC = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  return <div style={{position: 'absolute', bottom: 90, width: '100%', display: 'flex', justifyContent: 'center', transform: `scale(${spring({frame: f - 6, fps, config: {damping: 9}})})`}}>
    <div style={{background: NAVY, color: 'white', borderRadius: 70, padding: '22px 50px', fontFamily: 'Plex', fontSize: 60, direction: 'rtl'}}>
      اكتب رقمك في التعليقات <span style={{display: 'inline-block', transform: `translateY(${Math.sin(f / 4) * 10}px)`}}>↓</span></div>
  </div>;
};

const EndCard: React.FC = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const s = spring({frame: f - 4, fps, config: {damping: 12}});
  return <AbsoluteFill style={{clipPath: `inset(0 0 0 ${ip(f, [0, 8], [100, 0])}%)`}}>
    <style>{css}</style>
    <OffthreadVideo src={staticFile('door_modern.mp4')} startFrom={60} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
    <AbsoluteFill style={{background: 'rgba(12,14,24,.62)', opacity: ip(f, [20, 32], [0, 1])}} />
    <T y={190} at={2} size={84}>نفصّله <span style={{fontFamily: 'Ami', color: WARM, fontSize: 104}}>على ذوقك</span></T>
    <Img src={staticFile('logo.png')} style={{position: 'absolute', top: 640, left: 420, width: 240, height: 240, borderRadius: 120, transform: `scale(${spring({frame: f - 24, fps, config: {damping: 10}})})`, boxShadow: '0 20px 50px rgba(0,0,0,.4)'}} />
    <T y={930} at={30} size={90}>النبراس <span style={{fontFamily: 'Ami', color: WARM}}>للألمنيوم</span></T>
    <T y={1100} at={38} size={62}>المعاينة مجانية</T>
    <div style={{position: 'absolute', top: 1240, width: '100%', display: 'flex', justifyContent: 'center', transform: `scale(${spring({frame: f - 44, fps, config: {damping: 9}})})`}}>
      <div style={{background: OR, color: 'white', borderRadius: 70, padding: '22px 56px', fontFamily: 'Taj', fontSize: 60, direction: 'rtl'}}>واتساب 0594774046</div></div>
    <div style={{opacity: s}} />
  </AbsoluteFill>;
};
