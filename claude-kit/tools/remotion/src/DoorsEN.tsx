import React from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, spring, useCurrentFrame, useVideoConfig, interpolate, staticFile, Img, Easing} from 'remotion';

const css = `@font-face{font-family:Plex;src:url(${staticFile('Plex.woff2')})}@font-face{font-family:Ami;src:url(${staticFile('AmiriIt.woff2')})}@font-face{font-family:Taj;src:url(${staticFile('Tajawal-Bold.ttf')})}`;
const NAVY = '#1F2A6B', OR = '#F2641C', WARM = '#FFB46B';
const ip = (f: number, a: number[], b: number[]) => interpolate(f, a, b, {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.65, 0, 0.35, 1)});
const SRC = staticFile('doors.mp4');
const S = (s: number) => Math.round(s * 30);
const DOOR = [{n: '١', from: 0.1}, {n: '٢', from: 1.6}, {n: '٣', from: 3.1}, {n: '٤', from: 4.6}];

// voice timeline (seconds) + Arabic subtitle for each English line
export const LINES: {t: number; d: number; ar: string; scene: string; k?: number}[] = [
  {t: 0.05, d: 2.05, ar: 'بابك يقول كل شي عنك', scene: 'flash'},
  {t: 2.2, d: 2.15, ar: 'اختار رقم… وأقول لك مين أنت', scene: 'grid'},
  {t: 4.45, d: 2.37, ar: '١ أبيض: هادي وراقي', scene: 'door', k: 0},
  {t: 6.9, d: 2.15, ar: '٢ أسود: فخم وواثق', scene: 'door', k: 1},
  {t: 9.15, d: 2.52, ar: 'بس انتظر… رقم ٣ يفاجئ الكل', scene: 'loop'},
  {t: 11.75, d: 1.92, ar: '٣ خشبي: كلاسيكي ودافي', scene: 'door', k: 2},
  {t: 13.75, d: 2.37, ar: 'ورقم ٤؟ هنا أغلب الناس يغلطون', scene: 'loop'},
  {t: 16.2, d: 3.65, ar: '٤ رمادي: عصري وعملي… وما يطلع من الموضة', scene: 'door', k: 3},
  {t: 19.95, d: 2.52, ar: 'طيب… أنت أي رقم؟ اكتبه في التعليقات', scene: 'cta'},
  {t: 22.55, d: 3.0, ar: 'النبراس للألمنيوم… نفصّله على ذوقك', scene: 'end'},
];
export const DUR_EN = S(26.2);

const Clip: React.FC<{from: number; rate?: number}> = ({from, rate = 1}) => (
  <OffthreadVideo src={SRC} startFrom={Math.round(from * 30)} playbackRate={rate} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
);

const Sub: React.FC<{txt: string; dark?: boolean}> = ({txt, dark}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const s = spring({frame: f - 1, fps, config: {damping: 14}});
  return <div style={{position: 'absolute', bottom: 230, left: 60, right: 60, display: 'flex', justifyContent: 'center', opacity: s, transform: `translateY(${(1 - s) * 30}px)`}}>
    <div style={{background: dark ? 'rgba(10,12,20,.78)' : 'rgba(31,42,107,.92)', color: 'white', fontFamily: 'Plex', fontSize: 58, lineHeight: 1.35, padding: '16px 34px', borderRadius: 24, direction: 'rtl', textAlign: 'center'}}>{txt}</div>
  </div>;
};

const Grid: React.FC<{title: React.ReactNode; foot?: React.ReactNode}> = ({title, foot}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  return <AbsoluteFill style={{background: '#F2ECE1'}}>
    <div style={{position: 'absolute', top: 110, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: 84, color: NAVY, lineHeight: 1.2, opacity: spring({frame: f, fps})}}>{title}</div>
    {DOOR.map((c, k) => {
      const s = spring({frame: f - 3 - k * 3, fps, config: {damping: 12}});
      const x = 60 + (k % 2 === 0 ? 500 : 0), y = 330 + Math.floor(k / 2) * 620;
      return <div key={k} style={{position: 'absolute', left: x, top: y, width: 460, height: 580, borderRadius: 28, overflow: 'hidden', boxShadow: '0 24px 50px rgba(0,0,0,.22)', transform: `scale(${s})`}}>
        <Img src={staticFile(`door_${k + 1}.jpg`)} style={{position: 'absolute', left: -190, top: -340, width: 840, height: 1493, objectFit: 'cover'}} />
        <div style={{position: 'absolute', bottom: 16, right: 16, width: 96, height: 96, borderRadius: 48, background: OR, color: 'white', fontFamily: 'Taj', fontSize: 66, display: 'flex', alignItems: 'center', justifyContent: 'center', border: '4px solid white'}}>{c.n}</div>
      </div>;
    })}
    {foot}
  </AbsoluteFill>;
};

const Flash: React.FC = () => {
  const f = useCurrentFrame(); const k = Math.min(3, Math.floor(f / 9) % 4);
  return <AbsoluteFill>
    <Clip from={DOOR[k].from + 0.4} />
    <AbsoluteFill style={{background: `rgba(255,255,255,${Math.max(0, 0.55 - (f % 9) / 9)})`}} />
    <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,12,20,.85) 0%, rgba(10,12,20,0) 32%)'}} />
    <div style={{position: 'absolute', top: 150, width: '100%', textAlign: 'center', fontFamily: 'Taj', fontSize: 280, color: 'white', textShadow: '0 10px 40px rgba(0,0,0,.6)', transform: `scale(${1.3 - (f % 9) / 30})`}}>{DOOR[k].n}</div>
  </AbsoluteFill>;
};

const Door: React.FC<{k: number; dur: number}> = ({k, dur}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const rev = ip(f, [0, 8], [0, 1]); const z = interpolate(f, [0, dur], [1.0, 1.1]);
  const rate = Math.max(0.4, Math.min(1, 1.45 * 30 / dur));
  const s = spring({frame: f - 4, fps, config: {damping: 11}});
  return <AbsoluteFill style={{clipPath: `inset(0 0 0 ${(1 - rev) * 100}%)`}}>
    <AbsoluteFill style={{transform: `scale(${z})`}}><Clip from={DOOR[k].from} rate={rate} /></AbsoluteFill>
    {rev < 1 && <div style={{position: 'absolute', top: 0, bottom: 0, left: `${(1 - rev) * 100}%`, width: 26, background: 'linear-gradient(90deg,#555,#ddd,#666)'}} />}
    <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,12,20,.7) 0%, rgba(10,12,20,0) 26%, rgba(10,12,20,0) 66%, rgba(10,12,20,.75) 100%)'}} />
    <div style={{position: 'absolute', top: 150, width: '100%', display: 'flex', justifyContent: 'center', transform: `scale(${s})`}}>
      <div style={{width: 160, height: 160, borderRadius: 80, background: OR, color: 'white', fontFamily: 'Taj', fontSize: 118, display: 'flex', alignItems: 'center', justifyContent: 'center', border: '6px solid white', boxShadow: '0 16px 40px rgba(0,0,0,.4)'}}>{DOOR[k].n}</div>
    </div>
  </AbsoluteFill>;
};

// open loop: black screen, Arabic words land one by one
const Loop: React.FC<{txt: string; dur: number}> = ({txt, dur}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const words = txt.split(' '); const step = Math.max(4, Math.floor((dur * 0.8) / words.length));
  return <AbsoluteFill style={{background: '#0b0b0d', alignItems: 'center', justifyContent: 'center'}}>
    <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '10px 26px', direction: 'rtl', padding: '0 70px', maxWidth: 1000}}>
      {words.map((w, i) => { const s = spring({frame: f - i * step, fps, config: {damping: 13}}); const hot = /٣|٤|يفاجئ|يغلطون/.test(w);
        return <span key={i} style={{fontFamily: hot ? 'Ami' : 'Plex', fontSize: hot ? 150 : 118, color: hot ? WARM : 'white', opacity: s, transform: `translateY(${(1 - s) * 40}px) scale(${0.8 + 0.2 * s})`, display: 'inline-block'}}>{w}</span>; })}
    </div>
  </AbsoluteFill>;
};

const CtaFoot: React.FC = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  return <div style={{position: 'absolute', bottom: 90, width: '100%', display: 'flex', justifyContent: 'center', transform: `scale(${spring({frame: f - 6, fps, config: {damping: 9}})})`}}>
    <div style={{background: OR, color: 'white', borderRadius: 70, padding: '20px 50px', fontFamily: 'Plex', fontSize: 58, direction: 'rtl'}}>
      اكتب رقمك في التعليقات <span style={{display: 'inline-block', transform: `translateY(${Math.sin(f / 4) * 10}px)`}}>↓</span></div>
  </div>;
};

const End: React.FC = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const sp = (a: number, d = 11) => spring({frame: f - a, fps, config: {damping: d}});
  return <AbsoluteFill style={{clipPath: `inset(0 0 0 ${ip(f, [0, 8], [100, 0])}%)`}}>
    <OffthreadVideo src={staticFile('door_modern.mp4')} startFrom={60} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
    <AbsoluteFill style={{background: 'rgba(12,14,24,.66)', opacity: ip(f, [10, 22], [0, 1])}} />
    <Img src={staticFile('logo.png')} style={{position: 'absolute', top: 520, left: 420, width: 240, height: 240, borderRadius: 120, transform: `scale(${sp(12, 10)})`, boxShadow: '0 20px 50px rgba(0,0,0,.4)'}} />
    <div style={{position: 'absolute', top: 820, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: 90, color: 'white', opacity: sp(18)}}>النبراس <span style={{fontFamily: 'Ami', color: WARM}}>للألمنيوم</span></div>
    <div style={{position: 'absolute', top: 990, width: '100%', textAlign: 'center', fontFamily: 'Plex', fontSize: 58, color: 'white', direction: 'rtl', opacity: sp(26)}}>المعاينة مجانية</div>
    <div style={{position: 'absolute', top: 1110, width: '100%', display: 'flex', justifyContent: 'center', transform: `scale(${sp(32, 9)})`}}>
      <div style={{background: OR, color: 'white', borderRadius: 70, padding: '20px 54px', fontFamily: 'Taj', fontSize: 58, direction: 'rtl'}}>واتساب 0594774046</div></div>
  </AbsoluteFill>;
};

export const DoorsEN: React.FC = () => {
  return <AbsoluteFill style={{background: '#111'}}>
    <style>{css}</style>
    {LINES.map((L, i) => {
      const from = i === 0 ? 0 : S(L.t) - 3; const to = i === LINES.length - 1 ? DUR_EN : S(LINES[i + 1].t) - 3; const dur = to - from;
      const sc = L.scene;
      return <Sequence key={i} from={from} durationInFrames={dur + (sc === 'loop' ? 0 : 8)}>
        {sc === 'flash' && <Flash />}
        {sc === 'grid' && <Grid title={<>بابك يقول عن <span style={{fontFamily: 'Ami', color: OR, fontSize: 104}}>شخصيتك</span></>} />}
        {sc === 'door' && <Door k={L.k!} dur={dur} />}
        {sc === 'loop' && <Loop txt={L.ar} dur={dur} />}
        {sc === 'cta' && <Grid title={<>وأنت؟ <span style={{fontFamily: 'Ami', color: OR, fontSize: 104}}>أي رقم؟</span></>} foot={<CtaFoot />} />}
        {sc === 'end' && <End />}
        {sc !== 'loop' && sc !== 'end' && <Sub txt={L.ar} dark={sc !== 'grid' && sc !== 'cta'} />}
      </Sequence>;
    })}
  </AbsoluteFill>;
};
