import React from 'react';
import {AbsoluteFill, spring, useCurrentFrame, useVideoConfig, interpolate, staticFile, Img} from 'remotion';
import {ThreeCanvas} from '@remotion/three';

const css = `@font-face{font-family:Taj;src:url(${staticFile('Tajawal-Bold.ttf')})}@font-face{font-family:Lal;src:url(${staticFile('Lalezar.ttf')})}`;
const GOLD = '#F2C95C';
const ALU = {color: '#5a5e66', metalness: 0.7, roughness: 0.28};
const GLASS = {color: '#9fd3ff', metalness: 0.1, roughness: 0.05, transparent: true, opacity: 0.35};

const Bar: React.FC<{p: [number, number, number]; s: [number, number, number]}> = ({p, s}) => (
  <mesh position={p}><boxGeometry args={s} /><meshStandardMaterial {...ALU} /></mesh>
);

// Sliding window with grid bars (like the villa windows)
const Window3D: React.FC<{slide: number}> = ({slide}) => {
  const W = 3.2, H = 2.0, t = 0.12, d = 0.18;
  return (
    <group>
      <Bar p={[0, H / 2, 0]} s={[W, t, d]} /><Bar p={[0, -H / 2, 0]} s={[W, t, d]} />
      <Bar p={[-W / 2, 0, 0]} s={[t, H, d]} /><Bar p={[W / 2, 0, 0]} s={[t, H, d]} />
      {[0, 1].map((k) => {
        const x = (k === 0 ? -W / 4 + slide * (W / 2) : W / 4); const z = k === 0 ? 0.05 : -0.05;
        return (
          <group key={k} position={[x, 0, z]}>
            <Bar p={[0, H / 2 - 0.1, 0]} s={[W / 2, 0.07, 0.08]} /><Bar p={[0, -H / 2 + 0.1, 0]} s={[W / 2, 0.07, 0.08]} />
            <Bar p={[-W / 4 + 0.04, 0, 0]} s={[0.07, H - 0.2, 0.08]} /><Bar p={[W / 4 - 0.04, 0, 0]} s={[0.07, H - 0.2, 0.08]} />
            <mesh><boxGeometry args={[W / 2 - 0.1, H - 0.25, 0.02]} /><meshStandardMaterial {...GLASS} /></mesh>
            {[-0.45, 0.45].map((gx) => <Bar key={gx} p={[gx, 0, 0.02]} s={[0.025, H - 0.3, 0.02]} />)}
            {[0.6, -0.6].map((gy) => <Bar key={gy} p={[0, gy, 0.02]} s={[W / 2 - 0.15, 0.025, 0.02]} />)}
          </group>
        );
      })}
    </group>
  );
};

// Entrance door with horizontal glass strips + long stainless handle (like the 3mm door)
const Door3D: React.FC<{open: number}> = ({open}) => {
  const W = 1.3, H = 2.6, t = 0.12, d = 0.2;
  return (
    <group>
      <Bar p={[0, H / 2, 0]} s={[W + 0.24, t, d]} /><Bar p={[-W / 2 - 0.06, 0, 0]} s={[t, H, d]} /><Bar p={[W / 2 + 0.06, 0, 0]} s={[t, H, d]} />
      <group position={[-W / 2, 0, 0]} rotation={[0, -open * 1.25, 0]}>
        <group position={[W / 2, 0, 0]}>
          <mesh><boxGeometry args={[W, H - 0.1, 0.07]} /><meshStandardMaterial color="#2a2c30" metalness={0.75} roughness={0.35} /></mesh>
          {[-0.8, -0.4, 0, 0.4, 0.8].map((y) => (
            <mesh key={y} position={[0.05, y, 0.04]}><boxGeometry args={[W - 0.35, 0.07, 0.01]} /><meshStandardMaterial {...GLASS} opacity={0.8} color="#cfe8ff" /></mesh>
          ))}
          <mesh position={[W / 2 - 0.16, 0, 0.12]}><cylinderGeometry args={[0.025, 0.025, 1.4, 24]} /><meshStandardMaterial color="#e8e8e8" metalness={1} roughness={0.12} /></mesh>
          {[0.6, -0.6].map((y) => <mesh key={y} position={[W / 2 - 0.16, y, 0.07]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.02, 0.02, 0.1, 16]} /><meshStandardMaterial color="#e8e8e8" metalness={1} roughness={0.12} /></mesh>)}
        </group>
      </group>
    </group>
  );
};

const Word: React.FC<{text: string; at: number; size: number; color?: string; font?: string; y: number}> = ({text, at, size, color = 'white', font = 'Taj', y}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const s = spring({frame: f - at, fps, config: {damping: 10, mass: 0.7}});
  return <div style={{position: 'absolute', top: y, width: '100%', textAlign: 'center', fontFamily: font, fontSize: size, color,
    transform: `translateY(${interpolate(s, [0, 1], [80, 0])}px) scale(${interpolate(s, [0, 1], [0.5, 1])})`, opacity: s, direction: 'rtl'}}>{text}</div>;
};

export const Pen: React.FC = () => {
  const f = useCurrentFrame(); const {fps, width, height} = useVideoConfig();
  const sec = f / fps;
  const strike = interpolate(f, [28, 40], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const phase1 = interpolate(f, [60, 70], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const winIn = spring({frame: f - 80, fps, config: {damping: 14}});
  const winOut = interpolate(f, [160, 172], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const doorIn = spring({frame: f - 172, fps, config: {damping: 14}});
  const doorOpen = interpolate(f, [205, 245], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const show3d = f >= 70;
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 45%, #2a2a2a 0%, #0f0f0f 70%)'}}>
      <style>{css}</style>
      {/* phase 1: we don't sell pens */}
      <div style={{opacity: phase1}}>
        <Word text="ما نبيع" at={4} size={110} y={720} />
        <div style={{position: 'absolute', top: 860, width: '100%', textAlign: 'center'}}>
          <span style={{position: 'relative', fontFamily: 'Lal', fontSize: 200, color: GOLD, display: 'inline-block',
            transform: `scale(${spring({frame: f - 12, fps, config: {damping: 9}})})`}}>أقلام
            <span style={{position: 'absolute', left: -20, right: -20, top: '52%', height: 14, background: '#e04545', borderRadius: 7,
              transform: `scaleX(${strike}) rotate(-6deg)`, transformOrigin: 'right'}} /></span>
        </div>
      </div>
      {/* 3D stage */}
      {show3d && (
        <ThreeCanvas width={width} height={height} camera={{position: [0, 0.2, 6.2], fov: 42}} style={{position: 'absolute'}}>
          <ambientLight intensity={0.55} />
          <directionalLight position={[3, 4, 5]} intensity={2.2} />
          <directionalLight position={[-4, 2, -3]} intensity={1.2} color="#ffd89a" />
          <directionalLight position={[0, 3, 4]} intensity={1.4} />
          <group position={[0, -0.6, 0]} scale={winIn * winOut} rotation={[0.08, -0.5 + sec * 0.35, 0]} visible={winOut > 0.01}>
            <Window3D slide={interpolate(f, [110, 150], [0, 0.85], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
          </group>
          <group position={[0, -0.7, 0]} scale={doorIn} rotation={[0.05, 0.45 - (sec - 5.7) * 0.25, 0]} visible={f >= 172}>
            <Door3D open={doorOpen} />
          </group>
        </ThreeCanvas>
      )}
      {f >= 70 && f < 172 && <><Word text="نبيع" at={72} size={90} y={330} /><Word text="نوافذ" at={84} size={190} y={430} color={GOLD} font="Lal" /></>}
      {f >= 172 && f < 260 && <Word text="وأبواب" at={174} size={190} y={400} color={GOLD} font="Lal" />}
      {f >= 260 && <>
        <Img src={staticFile('logo.png')} style={{position: 'absolute', top: 520, left: 400, width: 280, height: 280, borderRadius: 140,
          transform: `scale(${spring({frame: f - 260, fps, config: {damping: 10}})})`}} />
        <Word text="النبراس للألمنيوم" at={266} size={84} y={860} color={GOLD} />
        <Word text="المعاينة مجانية" at={274} size={70} y={990} />
        <Word text="واتساب 0594774046" at={282} size={60} y={1100} />
      </>}
    </AbsoluteFill>
  );
};
