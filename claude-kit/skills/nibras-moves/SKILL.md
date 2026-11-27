---
name: nibras-moves
description: Named motion-graphics moves (215) for Al Nibras canvas reels. Use when the user asks for a move by its Arabic name (تمدّد، نطّة، تظليل، سحب الستارة، ارجع ورا…), for kinetic typography, text animation, transitions, counters, camera moves, or says "طبّق حركة" / "استخدم مكتبة الحركات".
---

# Nibras moves library

215 named moves in `moves.js` (same folder). Copy `moves.js` next to the film page and load it before the film script: `<script src="moves.js"></script>`. Everything hangs off `window.MV`.

The owner asks for a move by its **Arabic name**; look it up in the tables below and call it by family and key.

## How to call each family

| Family | Call | Notes |
|---|---|---|
| IN / OUT (text entrances and exits) | `MV.textIn(g, key, p, text, cx, cy, size, colour, weight, MV.IN or MV.OUT)` | p goes 0→1. Word-by-word, typing and number-scramble keys are handled inside. |
| EM (looping emphasis) | `MV.apply(g, MV.EM[key][1](tSeconds), cx, cy, w, h, drawFn)` | Get w,h from `MV.measure(g, text, size)`. |
| DECO (highlight, underline, circle…) | `MV.DECO[key][1](g, p, cx, cy, w, h, colour)` | If the entry has a third item `1`, draw it BEFORE the text (it sits under it). |
| TR (transitions) | `MV.TR[key][1](g, p, drawOld, drawNew, W, H, colour)` | Both scenes are functions. About 7 frames reads well. |
| DATA (counters, charts, badges) | `MV.DATA[key][1](g, p, cx, cy, size, {bg,fg,ac,dim}, opts)` | opts: from/to/suf, vals, items, t. |
| CAM (whole-frame camera) | `g.save(); MV.cam(g, MV.CAM[key][1](p), W, H); …draw…; g.restore()` | |
| BG (backgrounds) | `MV.BG[key][1](g, tSeconds, W, H, palette)` | |
| UI (cursor, typing box, ticker…) | `MV.UI[key][1](g, p, cx, cy, size, palette, opts)` | |

Easings are in `MV.E` (out, io, back, elastic, bounce). Brand palette in `MV.PAL`.

## Rules learned with this owner
- Arabic letters are joined, so never animate letter by letter; use the word-by-word moves.
- Put a hit of the music on every cut and every reveal: build the mix with `mkmix.py` (parts FL, B1, B2, G1, G2, G3 of the original excerpt) and use the cut frames it prints.
- Keep text between y 300 and 1540 on a 1080x1920 frame; the thin news ticker sits at y 236.
- Only facts the owner gave may appear as numbers.
- `catalog.html` renders every move in a tile (8 pages); render it after any edit to check nothing throws. `demo.js` is a worked example (9 boards + pull-back).

## Moves by family

### IN — دخول (52)

| Arabic name | key |
|---|---|
| ظهور | `fade` |
| طلوع من تحت | `up` |
| نزول من فوق | `down` |
| دخول من اليسار | `left` |
| دخول من اليمين | `right` |
| فرقعة | `pop` |
| نطّة | `bounce` |
| سقوط ونطّة | `drop` |
| تمدّد بالعرض | `stretchX` |
| تمدّد بالطول | `stretchY` |
| هرسة | `squash` |
| تكبير | `zoomIn` |
| من كبير لصغير | `zoomBig` |
| دخول بلفّة | `rotateIn` |
| تأرجح | `swing` |
| قلبة أفقية | `flipX` |
| قلبة عمودية | `flipY` |
| ميلان | `skew` |
| من ضباب | `blur` |
| كشف لفوق | `maskUp` |
| كشف لتحت | `maskDown` |
| كشف من اليمين | `maskRight` |
| كشف من اليسار | `maskLeft` |
| كشف من النص | `maskCenter` |
| طلوع من السطر | `riseLine` |
| نزول على السطر | `fallLine` |
| خبطة | `slam` |
| ختم | `stamp` |
| مطّاط | `elastic` |
| تشويش | `glitch` |
| وميض | `flicker` |
| دخول بدوران | `spinIn` |
| دخول مايل | `tiltIn` |
| انفراد لتحت | `unfoldV` |
| انفراد لليسار | `unfoldH` |
| نمو من السطر | `growLine` |
| دحرجة | `roll` |
| دخول قطري | `diag` |
| طلوع بزيادة | `overUp` |
| طفو | `floatIn` |
| طقّة | `snap` |
| انكماش العرض | `track` |
| عصرة | `squeeze` |
| لكمة | `punch` |
| طلوع بضباب | `riseBlur` |
| كلمة كلمة لفوق | `wordsUp` |
| كلمة كلمة فرقعة | `wordsPop` |
| كلمة كلمة سقوط | `wordsDrop` |
| كلمة كلمة ظهور | `wordsFade` |
| كلمة كلمة قلبة | `wordsFlip` |
| كتابة | `type` |
| أرقام تتلخبط | `scramble` |

### OUT — خروج (22)

| Arabic name | key |
|---|---|
| اختفاء | `fade` |
| خروج لفوق | `up` |
| خروج لتحت | `down` |
| خروج لليسار | `left` |
| خروج لليمين | `right` |
| انكماش | `shrink` |
| انتفاخ واختفاء | `grow` |
| سقوط | `fall` |
| طيران | `fly` |
| ذوبان بضباب | `blur` |
| اختراق | `through` |
| مسح لفوق | `wipeUp` |
| مسح لتحت | `wipeDown` |
| مسح لليسار | `wipeLeft` |
| مسح لليمين | `wipeRight` |
| تسطيح | `flat` |
| خروج بدوران | `spin` |
| تشويش وخروج | `glitch` |
| وميض وخروج | `flicker` |
| طيّة | `fold` |
| ميلة وسقوط | `tiltFall` |
| غطس تحت السطر | `sink` |

### EM — تأكيد (20)

| Arabic name | key |
|---|---|
| نبض | `pulse` |
| هزّة | `shake` |
| تمايل | `wiggle` |
| إيماءة | `nod` |
| جيلي | `jello` |
| دقّة قلب | `heart` |
| طفو مستمر | `float` |
| ميلة | `tilt` |
| لفّة كاملة | `spin` |
| نطنطة | `hop` |
| تنفّس | `breathe` |
| ترنّح | `sway` |
| رمشة | `blink` |
| مطّ وعصر | `wobble` |
| تا-دا | `tada` |
| رجفة | `vibrate` |
| انجراف | `drift` |
| انحناءة | `lean` |
| شدّة مطاط | `rubber` |
| هزّ يمين يسار | `rock` |

### DECO — تحديد وزينة (20)

| Arabic name | key |
|---|---|
| تظليل | `highlight` |
| خط تحت | `underline` |
| خطين تحت | `underline2` |
| شطب | `strike` |
| تحديد بدائرة | `circle` |
| تحديد بمربع | `box` |
| أقواس | `brackets` |
| زوايا تحديد | `corners` |
| تحديد بمقابض | `select` |
| سهم يأشّر | `arrow` |
| نقاط تحت | `dots` |
| خط متعرّج | `zigzag` |
| توهّج | `glow` |
| لمعة | `shine` |
| كشّاف | `spotlight` |
| ظل بارز | `shadow` |
| كبسولة | `pill` |
| ملصق | `tag` |
| شرارات حول الكلمة | `burst` |
| نجوم | `stars` |

### TR — انتقال (31)

| Arabic name | key |
|---|---|
| قطع | `cut` |
| تلاشي | `fade` |
| فلاش | `flash` |
| مسحة لليسار | `wipeL` |
| مسحة لليمين | `wipeR` |
| مسحة لفوق | `wipeU` |
| مسحة لتحت | `wipeD` |
| دفعة لليسار | `pushL` |
| دفعة لليمين | `pushR` |
| دفعة لفوق | `pushU` |
| دفعة لتحت | `pushD` |
| فتحة دائرة | `iris` |
| فتحة مربعة | `irisBox` |
| ستائر أفقية | `blindsH` |
| ستائر عمودية | `blindsV` |
| سحب الستارة | `curtain` |
| بابين ينفتحون | `doors` |
| مسحة قطرية | `diag` |
| عقرب ساعة | `clock` |
| شرائط متتابعة | `stripes` |
| مربعات | `checker` |
| لوح لون يعبر | `blockL` |
| لوح لون يطلع | `blockU` |
| تكبير وعبور | `zoomIn` |
| تصغير وعبور | `zoomOut` |
| عبّي الحبر | `ink` |
| موجة دوائر | `ripple` |
| شريطين يقفلون | `bars` |
| كرت يطلع | `card` |
| غالق كاميرا | `shutter` |
| بكسلة | `pixel` |

### DATA — أرقام وأشكال (25)

| Arabic name | key |
|---|---|
| عدّاد | `counter` |
| عدّاد دوّار | `odometer` |
| حلقة نسبة | `ring` |
| شريط تقدّم | `progress` |
| رصّ الأعمدة | `stack` |
| أعمدة تكبر | `bars` |
| ارسم خط | `line` |
| خط وانفجار | `lineBurst` |
| دائرة تتعبّى | `pie` |
| علامة صح | `check` |
| علامة خطأ | `cross` |
| سهم يطلع | `arrowUp` |
| شبكة نقاط | `dotsGrid` |
| انفجار نجمة | `clash` |
| قصاصات | `confetti` |
| لمعات | `sparkle` |
| حلقات نبض | `rings` |
| فقاعة كلام | `bubble` |
| شارة | `badge` |
| دائرة عرض | `offer` |
| ختم دائري | `stampC` |
| احفظ | `bookmark` |
| قلب | `heart` |
| مؤقّت | `timer` |
| قائمة تتأشّر | `checklist` |

### CAM — كاميرا (18)

| Arabic name | key |
|---|---|
| غوص | `pushIn` |
| ارجع ورا | `pullBack` |
| سحبة لليسار | `panL` |
| سحبة لليمين | `panR` |
| سحبة لفوق | `panU` |
| سحبة لتحت | `panD` |
| خطفة لليسار | `whipL` |
| خطفة لليمين | `whipR` |
| ميلة كاميرا | `roll` |
| رجّة كاميرا | `shake` |
| نبضة زوم | `punch` |
| انجراف هادي | `drift` |
| طيّر الكاميرا | `fly` |
| نزلة كاميرا | `drop` |
| نطّة كاميرا | `bounce` |
| زوم بلفّة | `zoomRot` |
| رفعة | `tiltUp` |
| كل اللوحات | `board` |

### BG — خلفية (12)

| Arabic name | key |
|---|---|
| لون سادة | `solid` |
| تدرّج يتحرك | `grad` |
| خطوط تمشي | `stripes` |
| نقاط تنجرف | `dots` |
| شبكة | `grid` |
| أشعة تدور | `sunburst` |
| مربعات تمشي | `checker` |
| إطار ظل ينبض | `vignette` |
| حبيبات | `noise` |
| نقط هافتون | `halftone` |
| قلبة لون | `flip` |
| ألوان تتبدّل | `cycle` |

### UI — واجهة (15)

| Arabic name | key |
|---|---|
| مؤشر يتحرك | `cursor` |
| نقرة مؤشر | `click` |
| خانة كتابة | `typeBox` |
| زر إرسال | `send` |
| شريحة عنوان | `chip` |
| إشعار ينزل | `notif` |
| رقم اللوحة | `index` |
| علامات الزوايا | `plus` |
| شريط سفلي | `lower` |
| كبسولة شرح | `caption` |
| شريط أخبار | `ticker` |
| إطار جوال | `phone` |
| خط قياس | `ruler` |
| زر تشغيل | `toggle` |
| منزلقة | `slider` |
