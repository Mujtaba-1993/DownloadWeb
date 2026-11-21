---
name: format-finder
description: Build a formats x visual-styles matrix of what works / is crowded / is an open gap in the Al Nibras (Saudi aluminium windows & doors) niche, and pick today's reel so every day uses a DIFFERENT format. Use when the user asks for a new video idea, "different format", "what should we post today", or to refresh the competitor matrix.
---
# Format Finder (own version of sandcastles.ai Format Finder, ref kallawaymarketing DfZmV6px5n3)
## Refresh the matrix (monthly)
1. Competitors: firecrawl_search `site:instagram.com ألمنيوم شبابيك أبواب الرياض الدمام جدة` -> GETANYAPI_GET_INSTAGRAM_POST(url, max_cost_usd "0.05") to get owners -> GETANYAPI_INSTAGRAM_USER_REELS(handle, max_cost_usd "0.10") for each (+ aluminum25_alnbras). Drop non-niche accounts (2026-11: saudsase15, faisalalbasri).
2. Classify each reel with invoke_llm (workbench) by caption+duration into FORMAT x STYLE:
   F = قبل/بعد, مراحل التركيب, عرض منتج/جولة, نصيحة/معلومة, مقارنة/تصويت, كلام للكاميرا, عرض/خصم سعر, رأي عميل, كواليس الورشة, ترند/كوميدي, مرضي/ASMR, مشكلة وحل
   V = تصوير جوال خام, شخص يتكلم, مونتاج سينمائي, موشن/3D, نص على الشاشة, صور سلايد
3. Matrix: median views per cell, n>=8 = crowded, empty = GAP. Render HTML -> PNG (playwright). Data: c.json, image: matrix.png in this folder.
## Findings 2026-11-21 (121 niche reels, 11 accounts)
- CROWDED + weak: product tour/showcase (67 reels, median ~280), slideshows (median ~180), tip with text-only (8 reels, ~208).
- STRONG: talking person (best style), price offer with cinematic edit (16.9k median), talking-to-camera with text (5k).
- OUR OWN HIT: water-insulation test, raw phone, problem->solution = 93,304 views (best in whole niche!) -> repost/remake every 4-6 weeks with new hook.
- OPEN GAPS: before/after (all styles), comparison/vote with person or motion, customer testimonial (person/raw), ASMR/satisfying (glass, sliding, locking sounds), motion/3D for almost every format, problem->solution with motion/text.
## Daily rotation (never repeat a cell two days running; log what was used in history.md)
Day pattern: 1 problem->solution test (raw) · 2 before/after (motion) · 3 vote/compare (person or motion) · 4 ASMR satisfying (cinematic close-ups) · 5 talking-to-camera tip (João style) · 6 customer testimonial (raw) · 7 offer with cinematic edit · then repeat with different products (windows/doors/folding/sliding/kitchens).
Always: voice from frame 0, hook question, open loop, CTA comment keyword; score with Higgsfield virality_predictor before posting.
