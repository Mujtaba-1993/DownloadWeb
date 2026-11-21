import React from 'react';
import {Composition} from 'remotion';
import {Kinetic} from './Kinetic';
import {Hook} from './Hook';
import {Pen} from './Pen';
import {Pen2} from './Pen2';
import {Dami} from './Dami';
import {Colors} from './Colors';
import {Doors} from './Doors';
import {DoorsEN, DUR_EN} from './DoorsEN';
import {ToolsReel, DUR_TOOLS} from './ToolsReel';
import {Fold, DUR_FOLD} from './Fold';
import {Montage, DUR_MONT} from './Montage';
export const Root: React.FC = () => (<>
  <Composition id="Kinetic" component={Kinetic} durationInFrames={90} fps={30} width={1080} height={1920} defaultProps={{line1: 'تحسبه جدار زجاج ثابت؟', line2: 'شوف'}} />
  <Composition id="Hook" component={Hook} durationInFrames={75} fps={30} width={1080} height={1920} defaultProps={{line1: 'تحسبه جدار زجاج ثابت؟', line2: 'شوف', top: 430}} />
  <Composition id="Payoff" component={Hook} durationInFrames={100} fps={30} width={1080} height={1920} defaultProps={{line1: "الصالة انفتحت كلها", line2: "على الحوش", top: 380, outAt: 2.9}} />
  <Composition id="RocketTxt" component={Hook} durationInFrames={75} fps={30} width={1080} height={1920} defaultProps={{line1: "ناسا أطلقت صاروخها للقمر", line2: "", top: 1300, outAt: 2.1}} />
  <Composition id="Launched" component={Hook} durationInFrames={48} fps={30} width={1080} height={1920} defaultProps={{line1: "واحنا أطلقنا", line2: "هذا", top: 430, outAt: 1.3}} />
  <Composition id="Pen" component={Pen} durationInFrames={420} fps={30} width={1080} height={1920} />
  <Composition id="Pen2" component={Pen2} durationInFrames={435} fps={30} width={1080} height={1920} />
  <Composition id="Dami" component={Dami} durationInFrames={380} fps={30} width={1080} height={1920} />
  <Composition id="Colors" component={Colors} durationInFrames={458} fps={30} width={1080} height={1920} />
  <Composition id="Doors" component={Doors} durationInFrames={540} fps={30} width={1080} height={1920} />
  <Composition id="DoorsEN" component={DoorsEN} durationInFrames={DUR_EN} fps={30} width={1080} height={1920} />
  <Composition id="ToolsReel" component={ToolsReel} durationInFrames={DUR_TOOLS} fps={30} width={1080} height={1920} />
  <Composition id="Fold" component={Fold} durationInFrames={DUR_FOLD} fps={30} width={1080} height={1920} />
  <Composition id="Montage" component={Montage} durationInFrames={DUR_MONT} fps={30} width={1080} height={1920} />
</>);
