import React from 'react';
import {AbsoluteFill, Sequence, spring, useCurrentFrame, useVideoConfig, interpolate, staticFile, Img, Easing} from 'remotion';

const css = `@font-face{font-family:Plex;src:url(${staticFile('Plex.woff2')})}@font-face{font-family:Ami;src:url(${staticFile('AmiriIt.woff2')})}@font-face{font-family:Taj;src:url(${staticFile('Tajawal-Bold.ttf')})}`;
const INK = '#14171c', CREAM = '#F3EEE6', BR = '#8E5B2B', OR = '#F2641C', WARM = '#FFB46B';
const ip = (f: number, a: number[], b: number[]) => interpolate(f, a, b, {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.65, 0, 0.35, 1)});
const S = (s: number) => Math.round(s * 30);
export const TL = [
  {t: 0.05, d: 2.07, ar: 'وقف تخمين… كم بتكلفك شبابيكك؟'},
  {t: 2.27, d: 2.15, ar: 'سوّينا لك أداتين مجانية تحسبها عنك'},
  {t: 4.57, d: 1.94, ar: 'الأداة الأولى: اكتب العرض والارتفاع…'},
  {t: 6.66, d: 1.64, ar: 'وشوف شباكك ينرسم قدامك'},
  {t: 8.45, d: 2.69, ar: 'بس الأداة الثانية… هي اللي الكل يحبها'},
  {t: 11.29, d: 2.01, ar: 'صمّمه بنفسك: اختار الشكل،'},
  {t: 13.45, d: 1.92, ar: 'اللون، المقاس، وحتى الباب'},
  {t: 15.52, d: 2.41, ar: 'وأرسله لنا واتساب بضغطة وحدة'},
  {t: 18.08, d: 2.3, ar: 'الرابط في البايو… جرّبها الحين، مجاناً'},
];
export const DUR_TOOLS = S(20.9);

// phone with a sequence of screens: [startFrame, src, tap?[x,y], zoom?]
type Step = {at: number; src: string; tap?: [number, number]; zoom?: number; zy?: number};
const Phone: React.FC<{steps: Step[]; x?: number; y?: number; w?: number; rot?: number}> = ({steps, x = 540, y = 1000, w = 640, rot = 0}) => {
  const f = useCurrentFrame(); const h = w * 2532 / 1170;
  let cur = 0; steps.forEach((s, i) => { if (f >= s.at) cur = i; });
  const st = steps[cur]; const prev = steps[cur - 1];
  const fade = prev ? ip(f, [st.at, st.at + 6], [0, 1]) : 1;
  const z = st.zoom ? interpolate(f, [st.at, st.at + 20], [prev?.zoom ?? 1, st.zoom], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)}) : 1;
  const tp = st.tap; const tf = f - st.at + 4;
  return <div style={{position: 'absolute', left: x - w / 2 - 22, top: y - h / 2 - 22, width: w + 44, height: h + 44, borderRadius: 86, background: '#0d0f12', boxShadow: '0 50px 90px rgba(0,0,0,.35), inset 0 0 0 3px #3a3d44', transform: `rotate(${rot}deg)`}}>
    <div style={{position: 'absolute', left: 22, top: 22, width: w, height: h, borderRadius: 66, overflow: 'hidden', background: '#fff'}}>
      <div style={{position: 'absolute', inset: 0, transform: `scale(${z})`, transformOrigin: `50% ${(st.zy ?? 0.4) * 100}%`}}>
        {prev && fade < 1 && <Img src={staticFile(prev.src)} style={{position: 'absolute', width: '100%', height: '100%'}} />}
        <Img src={staticFile(st.src)} style={{position: 'absolute', width: '100%', height: '100%', opacity: fade}} />
        {tp && tf > 0 && tf < 22 && <div style={{position: 'absolute', left: tp[0] * w - 45, top: tp[1] * h - 45, width: 90, height: 90, borderRadius: 45, border: `6px solid ${OR}`, background: 'rgba(242,100,28,.25)', transform: `scale(${0.5 + tf / 14})`, opacity: 1 - tf / 22}} />}
      </div>
    </div>
    <div style={{position: 'absolute', left: (w + 44) / 2 - 70, top: 34, width: 140, height: 34, borderRadius: 17, background: '#000'}} />
  </div>;
};

const Sub: React.FC<{txt: string; dark?: boolean}> = ({txt, dark}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const s = spring({frame: f - 1, fps, config: {damping: 14}});
  return <div style={{position: 'absolute', bottom: 120, left: 50, right: 50, display: 'flex', justifyContent: 'center', opacity: s, transform: `translateY(${(1 - s) * 30}px)`}}>
    <div style={{background: dark ? 'rgba(255,255,255,.12)' : INK, color: 'white', fontFamily: 'Plex', fontSize: 56, lineHeight: 1.35, padding: '14px 32px', borderRadius: 22, direction: 'rtl', textAlign: 'center'}}>{txt}</div>
  </div>;
};
const Tag: React.FC<{txt: React.ReactNode; y?: number; at?: number}> = ({txt, y = 120, at = 0}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const s = spring({frame: f - at, fps, config: {damping: 12}});
  return <div style={{position: 'absolute', top: y, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: 80, color: INK, opacity: s, transform: `translateY(${(1 - s) * 40}px)`}}>{txt}</div>;
};

const Hook: React.FC = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const wins = ['win1.jpg', 'win3.jpg', 'door2.jpg', 'win2.jpg'];
  return <AbsoluteFill style={{background: CREAM}}>
    {wins.map((w, i) => { const s = spring({frame: f - i * 5, fps, config: {damping: 11}}); const ang = (i - 1.5) * 9; const x = 540 + (i - 1.5) * 200; const isDoor = w.startsWith('door');
      return <div key={i} style={{position: 'absolute', left: x - 170, top: 820 - (isDoor ? 120 : 0), width: 340, height: isDoor ? 560 : 320, borderRadius: 22, overflow: 'hidden', border: '10px solid white', boxShadow: '0 30px 60px rgba(0,0,0,.25)', transform: `rotate(${ang}deg) scale(${s}) translateY(${(1 - s) * 200}px)`}}>
        <Img src={staticFile(w)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        <div style={{position: 'absolute', top: 14, left: 14, background: OR, color: 'white', fontFamily: 'Taj', fontSize: 44, borderRadius: 14, padding: '2px 18px', transform: `rotate(${Math.sin(f / 3 + i) * 8}deg)`}}>؟ ريال</div>
      </div>; })}
    <Tag y={250} txt={<>كم بتكلفك <span style={{fontFamily: 'Ami', color: OR, fontSize: 110}}>شبابيكك؟</span></>} />
  </AbsoluteFill>;
};

const Promise2: React.FC = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const st = spring({frame: f - 20, fps, config: {damping: 8}});
  return <AbsoluteFill style={{background: CREAM}}>
    <Tag y={150} txt={<>أداتين <span style={{fontFamily: 'Ami', color: OR, fontSize: 110}}>مجانية</span></>} />
    <div style={{position: 'absolute', inset: 0, transform: `translateX(${(1 - spring({frame: f, fps, config: {damping: 13}})) * -700}px)`}}><Phone steps={[{at: 0, src: 'c3.png'}]} x={300} y={1080} w={400} rot={-5} /></div>
    <div style={{position: 'absolute', inset: 0, transform: `translateX(${(1 - spring({frame: f - 5, fps, config: {damping: 13}})) * 700}px)`}}><Phone steps={[{at: 0, src: 'd2.png'}]} x={780} y={1080} w={400} rot={5} /></div>
    <div style={{position: 'absolute', top: 1560, left: 120, fontFamily: 'Plex', fontSize: 46, color: INK, direction: 'rtl'}}>حاسبة المقاسات</div>
    <div style={{position: 'absolute', top: 1560, right: 140, fontFamily: 'Plex', fontSize: 46, color: INK, direction: 'rtl'}}>صمّم بنفسك</div>
    <div style={{position: 'absolute', top: 360, left: 380, transform: `rotate(-10deg) scale(${2 - st})`, opacity: st, border: `8px solid ${OR}`, color: OR, borderRadius: 20, padding: '6px 30px', fontFamily: 'Taj', fontSize: 70}}>FREE</div>
  </AbsoluteFill>;
};

const Calc: React.FC = () => <AbsoluteFill style={{background: CREAM}}>
  <Tag y={70} txt={<><span style={{fontFamily: 'Taj', color: OR}}>١</span> حاسبة <span style={{fontFamily: 'Ami', color: BR, fontSize: 100}}>المقاسات</span></>} />
  <Phone x={540} y={1000} w={600} steps={[
    {at: 0, src: 'c1.png'}, {at: 22, src: 'c2.png', tap: [0.764, 0.393]}, {at: 44, src: 'c3.png', tap: [0.33, 0.393]},
    {at: 66, src: 'c3.png', zoom: 1.45, zy: 0.12}, {at: 88, src: 'c4.png', tap: [0.5, 0.56], zoom: 1.45, zy: 0.12}]} />
</AbsoluteFill>;

const Loop: React.FC<{txt: string; dur: number}> = ({txt, dur}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const words = txt.split(' '); const step = Math.max(4, Math.floor(dur * .8 / words.length));
  return <AbsoluteFill style={{background: '#0b0b0d', alignItems: 'center', justifyContent: 'center'}}>
    <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '10px 26px', direction: 'rtl', padding: '0 70px'}}>
      {words.map((w, i) => { const s = spring({frame: f - i * step, fps, config: {damping: 13}}); const hot = /الثانية|يحبها/.test(w);
        return <span key={i} style={{fontFamily: hot ? 'Ami' : 'Plex', fontSize: hot ? 150 : 118, color: hot ? WARM : 'white', opacity: s, transform: `translateY(${(1 - s) * 40}px)`, display: 'inline-block'}}>{w}</span>; })}
    </div>
  </AbsoluteFill>;
};

const Design: React.FC<{part: number}> = ({part}) => <AbsoluteFill style={{background: CREAM}}>
  <Tag y={70} txt={<><span style={{fontFamily: 'Taj', color: OR}}>٢</span> صمّم <span style={{fontFamily: 'Ami', color: BR, fontSize: 100}}>بنفسك</span></>} />
  <Phone x={540} y={1000} w={600} steps={part === 0
    ? [{at: 0, src: 'd1.png'}, {at: 24, src: 'd2.png'}, {at: 40, src: 'd2.png', tap: [0.29, 0.62]}]
    : [{at: 0, src: 'd3.png', zoom: 1.15, zy: 0.3}, {at: 20, src: 'd4.png', tap: [0.29, 0.38]}, {at: 40, src: 'd5.png', tap: [0.71, 0.8]}]} />
</AbsoluteFill>;

const Send: React.FC = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const b = spring({frame: f - 22, fps, config: {damping: 9}});
  return <AbsoluteFill style={{background: CREAM}}>
    <Tag y={70} txt={<>أرسله <span style={{fontFamily: 'Ami', color: '#1FA855', fontSize: 100}}>واتساب</span></>} />
    <Phone x={540} y={1000} w={600} steps={[{at: 0, src: 'd7.png', tap: [0.5, 0.81]}]} />
    <div style={{position: 'absolute', left: 560, top: 1220, transform: `scale(${b})`, transformOrigin: 'left top', background: '#DCF8C6', borderRadius: '30px 30px 30px 6px', padding: '24px 34px', boxShadow: '0 20px 40px rgba(0,0,0,.2)', direction: 'rtl', fontFamily: 'Plex', fontSize: 40, color: INK, width: 420}}>
      طلب جديد ✓<br /><span style={{fontSize: 32, color: '#555'}}>شباك سحاب ٣ درف · باب درفتين + قوس</span></div>
  </AbsoluteFill>;
};

const End: React.FC = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const sp = (a: number, d = 11) => spring({frame: f - a, fps, config: {damping: d}});
  return <AbsoluteFill style={{background: INK}}>
    <Img src={staticFile('logo.png')} style={{position: 'absolute', top: 420, left: 430, width: 220, height: 220, borderRadius: 110, transform: `scale(${sp(0, 10)})`}} />
    <div style={{position: 'absolute', top: 700, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: 100, color: 'white', opacity: sp(6)}}>الرابط في <span style={{fontFamily: 'Ami', color: WARM}}>البايو</span></div>
    <div style={{position: 'absolute', top: 860, width: '100%', textAlign: 'center', fontSize: 110, color: WARM, transform: `translateY(${Math.sin(f / 4) * 14}px)`, opacity: sp(10)}}>↑</div>
    <div style={{position: 'absolute', top: 1040, width: '100%', display: 'flex', justifyContent: 'center', transform: `scale(${sp(14, 8)})`}}>
      <div style={{background: OR, color: 'white', borderRadius: 70, padding: '20px 60px', fontFamily: 'Plex', fontSize: 64, direction: 'rtl'}}>جرّبها الحين… مجاناً</div></div>
    <div style={{position: 'absolute', top: 1200, width: '100%', textAlign: 'center', fontFamily: 'Taj', fontSize: 46, color: '#aaa', direction: 'ltr'}}>@aluminum25_alnbras</div>
  </AbsoluteFill>;
};

export const ToolsReel: React.FC = () => {
  const scenes = [<Hook />, <Promise2 />, <Calc />, null, <Loop txt={TL[4].ar} dur={S(TL[4].d) + 8} />, <Design part={0} />, <Design part={1} />, <Send />, <End />];
  // scene k spans line k start → next scene start; Calc covers lines 2-3
  const starts = [0, S(TL[1].t) - 3, S(TL[2].t) - 3, -1, S(TL[4].t) - 3, S(TL[5].t) - 3, S(TL[6].t) - 3, S(TL[7].t) - 3, S(TL[8].t) - 3];
  const ends = [starts[1], starts[2], starts[4], -1, starts[5], starts[6], starts[7], starts[8], DUR_TOOLS];
  return <AbsoluteFill style={{background: CREAM}}>
    <style>{css}</style>
    {scenes.map((el, k) => el && <Sequence key={k} from={starts[k]} durationInFrames={ends[k] - starts[k]}>
      <AbsoluteFill style={{opacity: 1}}>{el}</AbsoluteFill>
    </Sequence>)}
    {TL.map((L, i) => i !== 4 && i !== 8 && <Sequence key={'s' + i} from={S(L.t)} durationInFrames={S(L.d) + 6}><Sub txt={L.ar} /></Sequence>)}
  </AbsoluteFill>;
};
