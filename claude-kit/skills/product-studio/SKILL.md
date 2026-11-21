---
name: product-studio
description: Turn raw phone photos of products (aluminum windows, doors, kitchens, any item) into clean professional product shots for Instagram - cut out the background with rembg, place on a branded gradient or blurred scene with a soft shadow, add an Arabic headline and logo, export post 1080x1350 / story 1080x1920 / square. Use when the user says قص الصورة, شيل الخلفية, صور منتجات, مونتاج صور, product photo, remove background, or sends product photos for posting.
---

# product-studio

Script: `python3 ~/.claude/skills/product-studio/studio.py IN OUTDIR [options]`
(needs `pip install "rembg[cpu]" pillow`; Arabic fonts Tajawal/Cairo in ~/.fonts).

Options: `--bg "#hex" --bg2 "#hex"` gradient (top, floor) · `--scene photo.jpg` blurred real
background instead · `--title "عنوان"` `--sub "سطر ثاني"` Arabic text (RTL shaped) ·
`--logo logo.png` bottom corner · `--sizes post,story,square` · `--fill 0.72` product size ·
`--model isnet-general-use` (try `u2net` or `birefnet-general` if the edge is poor).

## Workflow
1. Put each input in its own folder; outputs go to a scratch folder.
2. Run, then **look at the `_cutout.png`** first. Glass windows and thin frames are hard:
   if parts of the frame vanished or the room shows through the glass, retry with
   `--model birefnet-general`, or use `--scene` with the original photo so leftovers blend.
3. Look at each export at phone size. Product fills about 70%, text readable, nothing on the
   bottom 15% of a story (Instagram UI covers it).
4. Brand defaults for Al Nibras: warm neutrals `#f4f1ec`/`#d8d1c4`, or dark `#2b2b2b`/`#111111`
   for black/champagne frames. Title max ~5 words, one offer line (e.g. المعاينة مجانية).
5. Send the user the files; never post for them.
