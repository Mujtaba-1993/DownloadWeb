import React from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, spring, useCurrentFrame, useVideoConfig, interpolate, staticFile, Img, Easing} from 'remotion';

const css = `@font-face{font-family:Plex;src:url(${staticFile('Plex.woff2')})}@font-face{font-family:Ami;src:url(${staticFile('AmiriIt.woff2')})}@font-face{font-family:Taj;src:url(${staticFile('Tajawal-Bold.ttf')})}`;
const OR = '#F2641C', WARM = '#FFB46B', NAVY = '#1F2A6B';
const S = (s: number) => Math.round(s * 30);
const ip = (f: number, a: number[], b: number[]) => interpolate(f, a, b, {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.65, 0, 0.35, 1)});
export const FL = [
  {t: 0.05, d: 2.03, ar: 'تبغى جدار كامل… يختفي؟'},
  {t: 2.3, d: 0.94, ar: 'شوف هذا'},
  {t: 4.6, d: 1.86, ar: 'دفّة وحدة… وينطوي'},
  {t: 12.4, d: 2.37, ar: 'وصارت الصالة على الحوش'},
  {t: 15.0, d: 3.69, ar: 'أبواب فولدنق: فتحة كاملة، ألمنيوم نحيف، زجاج دبل'},
  {t: 19.0, d: 2.28, ar: 'اكتب «فولدنق» ونرسل لك السعر'},
];
export const DUR_FOLD = S(21.8);

const Card: React.FC<{children: React.ReactNode; bg: React.ReactNode}> = ({children, bg}) => (
  <AbsoluteFill style={{background: '#0d0e11'}}>
    <AbsoluteFill style={{filter: 'blur(40px) brightness(.45)', transform: 'scale(1.3)'}}>{bg}</AbsoluteFill>
    <div style={{position: 'absolute', left: 20, right: 20, top: 560, height: 580, borderRadius: 34, overflow: 'hidden', boxShadow: '0 40px 80px rgba(0,0,0,.5)'}}>{children}</div>
  </AbsoluteFill>
);
const Pic: React.FC<{src: string; z0?: number; z1?: number; dur: number}> = ({src, z0 = 1, z1 = 1.08, dur}) => {
  const f = useCurrentFrame(); const z = interpolate(f, [0, dur], [z0, z1]);
  return <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${z})`}} />;
};
const Vid: React.FC<{from?: number}> = ({from = 0}) => <OffthreadVideo src={staticFile('fold.mp4')} startFrom={from} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />;

// João-style: bold burned caption, words pop in
const Cap: React.FC<{txt: string; dur: number}> = ({txt, dur}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const w = txt.split(' '); const step = Math.max(3, Math.floor(dur * .7 / w.length));
  return <div style={{position: 'absolute', top: 1220, left: 50, right: 50, display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '6px 18px', direction: 'rtl'}}>
    {w.map((x, i) => { const s = spring({frame: f - i * step, fps, config: {damping: 12}}); const hot = /يختفي|فولدنق|الحوش|ينطوي|السعر/.test(x);
      return <span key={i} style={{fontFamily: 'Plex', fontSize: 82, color: hot ? WARM : 'white', WebkitTextStroke: '3px rgba(0,0,0,.9)', paintOrder: 'stroke', textShadow: '0 6px 20px rgba(0,0,0,.6)', opacity: s, transform: `scale(${0.7 + 0.3 * s})`, display: 'inline-block'}}>{x}</span>; })}
  </div>;
};
const Label: React.FC = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const s = spring({frame: f, fps, config: {damping: 12}});
  return <div style={{position: 'absolute', top: 300, right: 50, background: 'white', color: '#111', fontFamily: 'Plex', fontSize: 46, padding: '10px 24px', borderRadius: 12, direction: 'rtl', transform: `scale(${s})`, transformOrigin: 'right center', boxShadow: '0 10px 30px rgba(0,0,0,.3)'}}>
    أبواب فولدنق <span style={{color: OR}}>• قبل وبعد</span></div>;
};

const BeforeAfter: React.FC = () => {
  const f = useCurrentFrame(); const x = ip(f, [10, 60], [100, 0]) ;
  const chips = ['فتحة كاملة', 'ألمنيوم نحيف', 'زجاج دبل'];
  const {fps} = useVideoConfig();
  return <Card bg={<Img src={staticFile('fold_open.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />}>
    <Img src={staticFile('fold_open.jpg')} style={{position: 'absolute', width: '100%', height: '100%', objectFit: 'cover'}} />
    <div style={{position: 'absolute', inset: 0, clipPath: `inset(0 ${100 - x}% 0 0)`}}><Img src={staticFile('fold_closed.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} /></div>
    <div style={{position: 'absolute', top: 0, bottom: 0, left: `${x}%`, width: 10, background: 'white', boxShadow: '0 0 20px rgba(0,0,0,.6)'}} />
    <div style={{position: 'absolute', bottom: 20, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 14, direction: 'rtl'}}>
      {chips.map((c, i) => { const s = spring({frame: f - 40 - i * 10, fps, config: {damping: 11}}); return <div key={c} style={{background: OR, color: 'white', fontFamily: 'Plex', fontSize: 40, padding: '8px 22px', borderRadius: 40, transform: `scale(${s})`}}>{c}</div>; })}
    </div>
  </Card>;
};

const End: React.FC = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const sp = (a: number, d = 11) => spring({frame: f - a, fps, config: {damping: d}});
  return <AbsoluteFill style={{background: '#0d0e11'}}>
    <AbsoluteFill style={{filter: 'blur(40px) brightness(.35)', transform: 'scale(1.3)'}}><Img src={staticFile('fold_open.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} /></AbsoluteFill>
    <div style={{position: 'absolute', top: 200, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: 84, color: 'white', opacity: sp(2)}}>اكتب <span style={{fontFamily: 'Ami', color: WARM, fontSize: 100}}>«فولدنق»</span><br />ونرسل لك السعر</div>
    <div style={{position: 'absolute', top: 560, left: 110, right: 110, background: 'white', borderRadius: 34, padding: '34px 40px', direction: 'rtl', transform: `scale(${sp(0)})`, boxShadow: '0 30px 60px rgba(0,0,0,.4)'}}>
      <div style={{fontFamily: 'Plex', fontSize: 38, color: '#888', marginBottom: 14}}>التعليقات</div>
      <div style={{display: 'flex', alignItems: 'center', gap: 22}}>
        <div style={{width: 70, height: 70, borderRadius: 35, background: `radial-gradient(circle at 34% 28%, #fff, ${NAVY} 45%)`}} />
        <div style={{fontFamily: 'Plex', fontSize: 64, color: '#111'}}>فولدنق<span style={{opacity: Math.floor(f / 8) % 2}}>|</span></div>
      </div>
    </div>
    <Img src={staticFile('logo.png')} style={{position: 'absolute', top: 860, left: 450, width: 180, height: 180, borderRadius: 90, transform: `scale(${sp(12, 9)})`}} />
    <div style={{position: 'absolute', top: 1070, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: 80, color: 'white', opacity: sp(18)}}>النبراس <span style={{fontFamily: 'Ami', color: WARM}}>للألمنيوم</span></div>
    <div style={{position: 'absolute', top: 1220, width: '100%', display: 'flex', justifyContent: 'center', transform: `scale(${sp(26, 9)})`}}>
      <div style={{background: OR, color: 'white', borderRadius: 70, padding: '18px 52px', fontFamily: 'Taj', fontSize: 56, direction: 'rtl'}}>واتساب 0594774046</div></div>
  </AbsoluteFill>;
};

export const Fold: React.FC = () => {
  const vStart = S(2.2), vEnd = S(12.3);
  return <AbsoluteFill style={{background: '#0d0e11'}}>
    <style>{css}</style>
    <Sequence from={0} durationInFrames={vStart + 4}>
      <Card bg={<Img src={staticFile('fold_closed.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />}><Pic src="fold_closed.jpg" dur={vStart} z0={1.15} z1={1.0} /></Card>
    </Sequence>
    <Sequence from={vStart} durationInFrames={vEnd - vStart + 4}>
      <Card bg={<Vid />}><Vid /></Card>
    </Sequence>
    <Sequence from={vEnd} durationInFrames={S(15.0) - vEnd + 4}>
      <Card bg={<Img src={staticFile('fold_open.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />}><Pic src="fold_open.jpg" dur={S(2.7)} z0={1.0} z1={1.12} /></Card>
    </Sequence>
    <Sequence from={S(15.0)} durationInFrames={S(19.0) - S(15.0) + 4}><BeforeAfter /></Sequence>
    <Sequence from={S(19.0) - 6}><End /></Sequence>
    <Sequence from={0} durationInFrames={S(19.0)}><Label /></Sequence>
    {FL.map((L, i) => i < 5 && <Sequence key={i} from={S(L.t)} durationInFrames={(i < 4 ? S(FL[i + 1].t) : S(19.0)) - S(L.t)}><Cap txt={L.ar} dur={S(L.d)} /></Sequence>)}
  </AbsoluteFill>;
};
