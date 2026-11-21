import React from 'react';
import {AbsoluteFill, spring, useCurrentFrame, useVideoConfig, interpolate, staticFile} from 'remotion';
const css = `@font-face{font-family:Taj;src:url(${staticFile('Tajawal-Bold.ttf')})}@font-face{font-family:Lal;src:url(${staticFile('Lalezar.ttf')})}`;
export const Kinetic: React.FC<{line1: string; line2: string}> = ({line1, line2}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const words = line1.split(' ');
  const s2 = spring({frame: f - 8 - words.length * 4, fps, config: {damping: 9, mass: 0.6}});
  return (
    <AbsoluteFill style={{background: '#141414', justifyContent: 'center', alignItems: 'center', direction: 'rtl'}}>
      <style>{css}</style>
      <div style={{display: 'flex', gap: 22, flexWrap: 'wrap', justifyContent: 'center', width: 940}}>
        {words.map((w, i) => {
          const s = spring({frame: f - i * 4, fps, config: {damping: 12}});
          return <span key={i} style={{fontFamily: 'Taj', fontSize: 92, color: 'white', display: 'inline-block',
            transform: `translateY(${interpolate(s, [0, 1], [60, 0])}px) scale(${interpolate(s, [0, 1], [0.6, 1])})`, opacity: s}}>{w}</span>;
        })}
      </div>
      <div style={{fontFamily: 'Lal', fontSize: 230, color: '#F2C95C', marginTop: 30, transform: `scale(${s2}) rotate(${interpolate(s2, [0, 1], [-8, 0])}deg)`}}>{line2}</div>
      <div style={{position: 'absolute', bottom: 760, width: interpolate(f, [20, 40], [0, 300], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}), height: 8, background: '#C9A45C', borderRadius: 4}} />
    </AbsoluteFill>
  );
};
