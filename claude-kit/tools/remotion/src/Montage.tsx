import React from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, spring, useCurrentFrame, useVideoConfig, interpolate, staticFile, Img, Easing} from 'remotion';
import M from './montage_cuts.json';

const css = `@font-face{font-family:Plex;src:url(${staticFile('Plex.woff2')})}@font-face{font-family:Ami;src:url(${staticFile('AmiriIt.woff2')})}@font-face{font-family:Taj;src:url(${staticFile('Tajawal-Bold.ttf')})}`;
const BODY = M.total; export const DUR_MONT = BODY + 105;
const CH_AR = ['الصفر', 'الورشة', 'التركيب', 'الإطار', 'النور', 'الباب', 'البيت', 'الحياة'];

export const Montage: React.FC = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const lastCut = [...M.cuts].reverse().find((c) => c <= f) ?? 0; const since = f - lastCut;
  const chIdx = M.chapters.filter((c) => c <= f).length - 1; const chSince = f - M.chapters[Math.max(0, chIdx)];
  // the "window" motif: a thin frame that kicks on every cut (match-cut thread)
  const kick = Math.max(0, 1 - since / 6);
  const fw = 620 + kick * 40, fh = 1000 + kick * 60;
  const flash = chSince < 4 && chIdx > 0 ? (1 - chSince / 4) * 0.85 : 0;
  const endP = interpolate(f, [BODY - 10, BODY + 10], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const e = (a: number, d = 12) => spring({frame: f - BODY - a, fps, config: {damping: d}});
  return <AbsoluteFill style={{background: '#000'}}>
    <style>{css}</style>
    <OffthreadVideo src={staticFile('montage_body.mp4')} muted style={{width: '100%', height: '100%', filter: `saturate(1.12) contrast(1.06)`}} />
    {/* film look: vignette + grain-ish */}
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 45%, rgba(0,0,0,.55) 100%)'}} />
    {/* window frame motif */}
    {f < BODY && <div style={{position: 'absolute', left: 540 - fw / 2, top: 960 - fh / 2, width: fw, height: fh, border: `${2 + kick * 2}px solid rgba(255,255,255,${0.18 + kick * 0.3})`, borderRadius: 10, boxShadow: '0 0 30px rgba(0,0,0,.4)'}} />}
    {/* chapter word flashes in the corner like a counter */}
    {f < BODY && <div style={{position: 'absolute', top: 120, width: '100%', textAlign: 'center', fontFamily: 'Ami', fontSize: 86, color: '#FFD9A0', textShadow: '0 4px 20px rgba(0,0,0,.8)', opacity: Math.min(1, chSince / 3) * (chIdx >= 0 ? 1 : 0)}}>{CH_AR[Math.max(0, chIdx)]}</div>}
    {f < BODY && <div style={{position: 'absolute', bottom: 140, width: '100%', textAlign: 'center', fontFamily: 'Taj', fontSize: 40, color: 'rgba(255,255,255,.8)', letterSpacing: 6}}>{String(chIdx + 1).padStart(2, '0')} / 08</div>}
    <AbsoluteFill style={{background: '#fff', opacity: flash}} />
    {/* THE END */}
    <AbsoluteFill style={{background: '#0b0b0d', opacity: endP}}>
      {f >= BODY - 4 && <>
        <Img src={staticFile('logo.png')} style={{position: 'absolute', top: 470, left: 450, width: 180, height: 180, borderRadius: 90, transform: `scale(${e(4, 10)})`}} />
        <div style={{position: 'absolute', top: 760, width: '100%', textAlign: 'center', fontFamily: 'Ami', fontSize: 190, color: '#F2ECE1', opacity: e(14), transform: `scale(${0.9 + 0.1 * e(14)})`, letterSpacing: 4}}>النهاية</div>
        <div style={{position: 'absolute', top: 1010, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: 62, color: '#FFB46B', opacity: e(30)}}>…وبداية بيتك</div>
        <div style={{position: 'absolute', top: 1200, width: '100%', textAlign: 'center', direction: 'rtl', fontFamily: 'Plex', fontSize: 44, color: '#aaa', opacity: e(44)}}>النبراس للألمنيوم · <span style={{fontFamily: 'Taj'}}>0594774046</span></div>
      </>}
    </AbsoluteFill>
  </AbsoluteFill>;
};
