---
name: bizshorts-pattern
description: Content pattern for "BizShorts" — the THE BOTTOM LINE channel's 60–120-second vertical Shorts (solo MC1, Thai) that tell one surprising business story with one strategy and one lesson, or a "10 things you didn't know about X" list. Use when researching, writing, rewriting or reviewing a BizShorts script/outline (files under BizShorts/), picking a hook, closing line, format or next episode topic, or when the user gives feedback on a BizShorts episode ("ข้อนี้ไม่น่ารู้", "ปิดท้ายงง", "ยาวไป"). Also covers the CapCut 9:16 editing style (shotlist, คำโปรย on-screen keywords, b-roll, build_capcut script) modelled on the Lab.เล่าหุ้น channel. Pair with the elevenlabs-tts skill for TTS formatting and tags. Not for the long-form Next Frontier show (use next-frontier-pattern).
---

# BizShorts — Shorts Pattern (THE BOTTOM LINE)

The full Thai spec, including the reference-clip analysis (ASML by คุณบอม), YouTube Shorts metrics, every hook and closing formula with examples, and the DeepSeek example script, lives in [BizShorts/note.md](../../../BizShorts/note.md). **Read note.md sections 4–6 before writing a new episode.** This skill gives the workflow, the three formats, and the lessons from user feedback that note.md doesn't cover yet. What each past episode used is in [references/episode-log.md](references/episode-log.md). The CapCut 9:16 editing template (screen zones, คำโปรย keywords, b-roll, layer order, per-episode steps) is in [references/capcut-style.md](references/capcut-style.md).

## Show identity (fixed)

| Item | Value |
|---|---|
| Channel / show | The Bottom Line / **BizShorts** (in spoken text write `BizShorts` and `The Bottom Line`, never all caps, or TTS reads them letter by letter) |
| Promise | เรื่องธุรกิจที่ "ไม่น่าเชื่อ" ในนาทีเดียว พร้อมบทเรียน 1 ข้อที่เอาไปใช้ได้ |
| Audience | คนทำงาน เจ้าของธุรกิจ และนักลงทุน ที่ไถเจอใน feed โดยยังไม่รู้จักช่อง |
| Host | MC1 (`@mc1`), **female**: `ค่ะ` for statements, `คะ` for questions and after `นะ`/`ล่ะ`; never `ครับ` |
| Length | Target 60–90 s ≈ 900–1,300 chars including tags. **In practice the user accepts ~1,400–1,600** (EP3–EP5) and trims during editing; the hard ceiling is **2 minutes ≈ 1,800 chars**. Don't cut good content just to hit 1,300. Report the count and suggest which part to cut. |
| Output | Plain transcript (elevenlabs-tts "plain" format) at `BizShorts/ep<N>_<slug>/transcript_v<N>.md` + `outline.md` in the same folder. **Never overwrite an earlier version.** Every round of feedback becomes a new `transcript_v<N+1>.md`. Editing files live in the same folder: `subtitle` (SRT from CapCut), `shotlist.md`, `broll/`, `build_ep<N>_capcut.py`. |
| CTA | Ends with "กดติดตาม The Bottom Line ไว้นะคะ". The signature line (like "ติดตามคุณบอมไว้ได้เลย") is **still undecided**, so ask the user and don't invent one. |

## Workflow

1. **Pick the angle.** Read [references/episode-log.md](references/episode-log.md) so the strategy, lesson and format don't repeat the last episodes. A company can come back (AMD: EP3 and EP6) if the angle is new. Default to **Format A**. Use B or C when the user asks for them or when the last two episodes used A.
2. **Research and verify** with web search. Mark every fact ✅ (confirmed, with source) or 🟡 (needs a check on release day / sources disagree). The market cap must be converted to baht, with the date, the source and the exchange rate recorded. Non-official numbers must name who says them in the script ("มีรายงานว่า…", "ตามรายงานของนักลงทุนรายหนึ่ง").
3. **Write `outline.md`** with these sections, in Thai, following the existing episodes:
   - header line: date · main transcript link · seconds · char count · `tts.py check` result
   - why this format/angle (vs. earlier EPs)
   - Logline: เรื่อง / กลยุทธ์ 1 ข้อ / บทเรียน
   - beat table (# / จังหวะ / เวลา / ใจความ / Tag)
   - Hook สำรอง
   - title + backup title + description block + on-screen notes for the editor
   - fact table (ในบท / ข้อเท็จจริง / สถานะ / แหล่ง)
   - facts cut (kept for future clips)
   - links to earlier EPs
   - ประวัติเวอร์ชัน: what each version changed and **why**, including the user's feedback in their own words
4. **Write the transcript** in plain format. One paragraph per beat (Format C: one per item), with a tone tag at the start.
5. **Lint and count**, from the project root:
   ```bash
   python3 .claude/skills/elevenlabs-tts/scripts/tts.py check BizShorts/ep<N>_<slug>/transcript_v<N>.md
   ```
   It must pass with 0 errors and 0 warnings. INFO lines about `AMD`-style acronyms are fine when earlier episodes kept the acronym in English.
6. **Report to the user in Thai.** Cover where the file is, the length, what changed and why, and the 🟡 facts they must check before release. Then update the outline's header and version history.
7. **Editing (only when the user asks, after the script is final).** Follow [references/capcut-style.md](references/capcut-style.md) section 7: get the `subtitle` SRT from CapCut auto-captions, write `shotlist.md` (one row per subtitle line: เวลา · ซับ · คำโปรย · ตัวเลขเน้น · ภาพ ล่าง/กลาง/บน), collect licensed b-roll into `broll/`, copy and adapt `BizShorts/ep3_amd/build_ep3_capcut.py`, and list what the user still has to do by hand in CapCut (subtitle track to the top, คำโปรย text layer, yellow numbers, channel logo).

## Formats

### Format A — default (EP1, EP2, EP4, EP5)
The 7-beat underdog structure in note.md section 4:
1. hook "นี่คือบริษัทที่…!"
2. name + rank-type accomplishment + "แต่คุณเชื่อไหมคะว่า…"
3. why they should have lost
4. one strategy
5. peak with the market cap in baht
6. one closing sentence
7. CTA

### Format B — "เลือกข้าง" (EP3, experimental)
- **Hook:** the viewer picks first ("ย้อนไปสิบปี ถ้าให้เลือกลงทุนได้บริษัทเดียว… A หรือ B?"), then the answer flips right away.
- **Protagonist:** one person instead of the company.
- **Villain:** speaks through a real quote, which comes back as the punchline.
- **Close:** ask the viewer to pick a side again ("คอมเมนต์ชื่อทิ้งไว้ อีกสิบปีกลับมาดูกัน").

### Format C — "ลิสต์สิบข้อ" (EP6, experimental)
The topic itself breaks note rule 1 ("1 story 1 strategy 1 lesson"), so the outline must say so. Rules learned from EP6 feedback:
- **Hook:** promise the count and open a loop on the last item ("สิบเรื่องที่คุณอาจไม่รู้เกี่ยวกับ X… และข้อสุดท้าย [คู่แข่ง] คงไม่อยากให้คุณรู้ค่ะ"). The last item must pay that loop off.
- **1 item = 1 paragraph**, and say **"ข้อ + number" for every item** ("ข้อแรก", "ข้อสอง", … "และข้อสุดท้าย"). Never put two items in one paragraph and never use a bare number: in v2 the even items sat mid-paragraph, so the user read it as "ข้อแรก สาม ห้า เจ็ด เก้า", and "หก สองบริษัทนี้…" put two numbers side by side.
- **Items must be genuinely surprising.** "Product X uses their chip" facts (consoles, Tesla screens) were rejected as "ไม่น่ารู้เท่าไร". Prefer big numbers, famous people, money between rivals, firsts, and ironies.
- **Open with the strongest items.** Item 1 = market cap in baht with a vivid comparison (it then leaves the hook, so don't say it twice). Item 2 = the most "wait, what?" people fact.
- **Be specific, not vague.** Name the people in origin stories (founders' names, not "ผู้ร่วมก่อตั้งคนหนึ่ง") and spell out relationships ("คุณตาของลิซ่า ซู เป็นพี่ชายของแม่เจนเซน หวง", not just "เป็นญาติกัน").
- **Numbers:** relax the ≤3 rule to about 1–2 per item. Item numbers don't count. The outline must list the count.
- **Close:** one sentence that calls back an earlier item ("จากโรงงานสำรองของ Intel ในวันนั้น วันนี้ AMD กลายเป็นคนที่ Intel ต้องเดินตาม"), then "ข้อไหนที่คุณไม่เคยรู้มาก่อน คอมเมนต์เลขข้อทิ้งไว้". Numbered comments are the easiest to write, and they show which item deserves its own Format A clip.
- **Length:** 10 items push the script to ~1,750–1,850 chars. Offer the weakest 1–2 items as the cut and change the hook count to match ("แปดเรื่อง").

## Editing style — CapCut 9:16 (modelled on Lab.เล่าหุ้น)

Full spec with measurements in [references/capcut-style.md](references/capcut-style.md). The short version, which also affects how the script is written:

- **One fixed screen template for every episode.** Top: the spoken sentence as a small white subtitle. Below it: the channel logo. Middle: a big handwritten-style **คำโปรย** of 2–6 words lifted from the sentence being spoken. Lower half: one image per idea (product, logo, person, white icon, self-made bar chart) over a dark blurred background. Numbers pop up in yellow with a black outline. The bottom 20% and right 15% stay empty because YouTube's UI covers them.
- **Rhythm comes from the words, not the footage.** The คำโปรย changes every sentence (~3–5 s). The image changes every idea (~5–10 s) and may stay for 15–20 s if the keywords keep moving. Every number that is spoken appears on screen as Arabic digits.
- **Voice-over only.** No presenter on camera, stock clips muted, music very low if any.
- **Script consequence:** every strategy needs a one-word metaphor that can be the คำโปรย ("ไม่แข่งกับลูกค้า", "โรงงานสำรอง", "เสือนอนกิน"). If a beat has nothing worth putting on screen, the beat is too abstract. A Lab.เล่าหุ้น-style title ("[เหตุการณ์ที่คนเห็นอยู่]! แต่ [สิ่งที่คนไม่รู้]") and the hook "ที่ผ่านมา… แต่วันนี้…" are allowed alternatives when the episode rides a current news event.
- **Not adopted:** "ครับ", ~2-minute length, stock-pick framing. BizShorts still ends on one business lesson and the MC1 CTA.

## Lessons from user feedback (all formats)

| Feedback / problem | Rule | From |
|---|---|---|
| "บทเรียนคือ…" sounds like a teacher and breaks rhythm | Never open the close with it. Use note section 5.1 formulas ("ความลับของ X จึงไม่ใช่… แต่คือ…", "X ไม่ได้ชนะเพราะ A แต่ชนะเพราะ B") | EP1 v3, EP2 v2 |
| Closing line "ฟังแล้วไม่รู้ว่าสื่ออะไร" | Say the close **with the same concrete words used in the story** (บริษัท, ความปลอดภัย), not abstractions ("ลูกค้าตัวจริง", "จุดที่คนมองว่าช้า"). Use two short sentences: what the company did, then what it means for you. | EP5 v3 |
| Lesson sounded soft | Lesson tag `[confident]`, never `[warm]` | EP1 v2 |
| TTS paused after "ยากจน" before "Nikon" | Put a linker (ขนาด, อย่าง, ของ, ให้, กับ, โดย) before a company or person name, or start a new sentence with it. Write Thai-script names without a space after the linker ("ของจอห์น แครี่") | EP1 v2, EP6 |
| Viewer doesn't know how big the company is | Every clip needs a rank phrase (beat 2) **and** the market cap in baht (peak, or item 1 in Format C) | EP1 v4, EP2 v3 |
| Stale market cap ("ทะลุสามสิบ" had gone out of date) | Re-check the market cap on release day and use "กว่า / เกือบ" | EP2 v3 |
| Script about Anthropic/Claude | Disclose in the outline that Claude drafted it, use only external sources, avoid cheerleading, and suggest a transparency line in the description | EP5 |
| Over the length target | The user trims in editing. Deliver the stronger script and say what could be cut | EP3, EP4, EP5 |

## Self-review checklist
- [ ] No greeting and no show name before the hook. The hook is a verified fact.
- [ ] Company named within 10 s, with a 2–4-word description of who they are.
- [ ] Rank phrase + market cap in baht (date, source and rate in the outline).
- [ ] Format A/B: there is a "why they should have lost" beat, 1 strategy, a closing sentence that doesn't start with "บทเรียนคือ", and 1 CTA. Format C: 10 numbered paragraphs, "ข้อ…" on each, and the last item pays off the hook.
- [ ] Numbers: ≤3 (A/B) or ~1–2 per item (C), never two in one sentence, spelled as Thai words.
- [ ] Something new every 5–10 s. Sentences ≤ ~40 chars, one idea each.
- [ ] People and relationships named concretely. Unofficial figures attributed.
- [ ] No relative time ("เมื่อวาน", "ปีที่แล้ว"). Use the year or month.
- [ ] `tts.py check` 0/0. Char count reported.
- [ ] Outline complete (sections in step 3), and the version history records the user's feedback.
- [ ] [references/episode-log.md](references/episode-log.md) has a row for the new episode.
- [ ] Every strategy/lesson beat has a 2–6-word คำโปรย and a concrete image the editor can show (see [references/capcut-style.md](references/capcut-style.md) section 4). List them in the outline's on-screen notes.
- [ ] If editing was requested: `shotlist.md` has one row per subtitle line, numbers appear as Arabic digits in the คำโปรย column, b-roll credits are listed, and the capcut-style checklist (section 8) passes.
