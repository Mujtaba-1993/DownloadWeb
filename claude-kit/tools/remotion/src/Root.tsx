import React from 'react';
import {Composition} from 'remotion';
import {Kinetic} from './Kinetic';
export const Root: React.FC = () => (
  <Composition id="Kinetic" component={Kinetic} durationInFrames={90} fps={30} width={1080} height={1920}
    defaultProps={{line1: 'تحسبه جدار زجاج ثابت؟', line2: 'شوف'}} />
);
