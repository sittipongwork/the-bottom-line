---
name: next-frontier-pattern
description: Content pattern for "Next Frontier" — the THE BOTTOM LINE channel's solo-MC (MC1) Thai show that breaks down how AI startups win, for business people interested in AI startups. Use when researching, outlining, writing, rewriting or reviewing a Next Frontier episode script/transcript (files under NextFrontier/), choosing an episode's hook, logline or structure, or when the user says a script is confusing/boring/unclear. Pair with the elevenlabs-tts skill for TTS formatting and tags.
---

# Next Frontier — Episode Pattern (THE BOTTOM LINE)

Distilled from research into ลงทุนแมน, The Indicator (NPR), The Daily (NYT), Acquired, Modern MBA, How I Built This and writing-for-the-ear guides. Full research notes: [NextFrontier/note.md](../../../NextFrontier/note.md). Reference shows and what each teaches: [references/reference-shows.md](references/reference-shows.md).

## Show identity (fixed)

| Item | Value |
|---|---|
| Channel | **THE BOTTOM LINE** (in spoken text write `The Bottom Line`; all-caps may be read letter by letter) |
| Show | **Next Frontier** |
| Promise | ถอดเกมธุรกิจของสตาร์ทอัพ AI ทั่วโลก ว่าเขาชนะกันได้ยังไง |
| Audience | นักธุรกิจที่สนใจสตาร์ทอัพ AI (founders, investors, business owners) |
| Format | Solo MC (`@mc1`), Thai, 5–8 min, ~4,000–5,000 chars (fits one paste in the ElevenLabs app) |
| Output | Plain transcript (elevenlabs-tts "plain" format) at `NextFrontier/ep<N>_<slug>/transcript_v<N>.md` — never overwrite an earlier version |
| Reference episode | [NextFrontier/ep1_tolan/transcript_v4.md](../../../NextFrontier/ep1_tolan/transcript_v4.md) |
| Still undecided | Signature line (like "ลงทุนแมนจะเล่าให้ฟัง"), MC1 ending particle (ครับ for now) — ask the user before inventing a signature line |

## Workflow

1. **Research and verify.** Collect facts from the user's source and confirm the key numbers (funding, valuation, users, revenue) with news sources. Mark anything unconfirmed; non-official numbers must name who says so in the script ("นักวิเคราะห์ประเมินว่า…").
2. **Write the logline first** (template: [templates/episode-outline.md](templates/episode-outline.md)).
   - Question — a business question: "ทำไม [บริษัท] ถึง [ผลลัพธ์น่าตกใจ] ทั้งที่ [สิ่งที่ขัดความคาดหมาย]?" e.g. moat, why investors pay this valuation, how they chose customers.
   - Answer in one sentence: "เพราะ…"
3. **Pick max 3 points** that answer the question. Everything else goes to on-screen text or the video description.
4. **Outline** with the 8-section template below, then write the script.
5. **Format for TTS** with the `elevenlabs-tts` skill (Thai-word numbers, English tags, spaced `ๆ`, no parentheses), then run `python3 .claude/skills/elevenlabs-tts/scripts/tts.py check <file>`.
6. **Self-review** with the checklist, then summarize changes + facts the user must verify.

## Episode template (8 sections)

| # | Section | Time | ~Chars | Must contain | MC1 tags |
|---|---|---|---|---|---|
| 1 | Hook | 0:00–0:15 | 150 | One concrete, surprising fact or contradiction + twist. No greeting. | `[intrigued]` |
| 2 | What it is + central question | 0:15–0:30 | 200 | What the company/product is in the simplest Thai, then the episode's question | `[curious]` → `[thoughtful]` |
| 3 | Show intro + promise | 0:30–0:45 | 200 | "สวัสดีครับ ยินดีต้อนรับเข้าสู่ Next Frontier ทางช่อง The Bottom Line รายการที่จะพาไปถอดเกมธุรกิจของสตาร์ทอัพ AI ทั่วโลก ว่าเขาชนะกันได้ยังไง" + "วันนี้ผมจะตอบคำถามนี้ผ่านสามเรื่อง คือ…" (name the 3) | `[warm]` |
| 4 | Context | 0:45–1:45 | 500–600 | The market problem and why others can't solve it — so a newcomer can follow | `[professional]` `[thoughtful]` |
| 5 | Points 1–3 | 1:45–5:30 | ~700 each | Each: claim → example/scene → one number → "แปลว่า…" (business meaning) | `[confident]` `[matter-of-fact]` `[warm]` |
| 6 | Other side of the coin | 5:30–6:30 | 400–500 | Max 2–3 risks or open problems | `[serious]` `[calm]` |
| 7 | Recap + answer + lesson | 6:30–7:15 | 400–600 | Recap the 3 points by number, answer the opening question in one sentence, one lesson for founders/investors + a memorable metaphor | `[calm]` → `[thoughtful]` → `[warm]` `[confident]` |
| 8 | CTA + sign-off | 7:15–7:30 | 200–300 | Question that continues the content, aimed at founders/investors; "กด Like กด Subscribe ช่อง The Bottom Line"; "แล้วพบกันใหม่ใน Next Frontier ตอนหน้า… สวัสดีครับ" | `[friendly]` → `[enthusiastic]` → `[warm]` |

The structure is also an **open loop**: the question asked in section 2 must be answered explicitly in section 7 ("กลับมาที่คำถามตอนต้น…").

## Writing rules

1. **One episode = one question.** Cut any paragraph that doesn't help answer it.
2. **First 30 seconds** answer: what is it, why is it interesting, what will I get.
3. **Say what it is before describing how it looks** — the listener can't see; audio alone must make sense.
4. **Max 3 points**, always numbered aloud ("เรื่องแรก…", "เรื่องที่สอง…"), recapped before the close.
5. **Max 1–2 numbers per sentence.** Round them and make them tangible ("สิบคน มีเจ็ดคน…", "แทบจะทุกวัน"). Convert big USD to baht once ("ราวพันล้านบาท"). Derived numbers ("หารคร่าว ๆ…") must say they're rough.
6. **Names only when they matter.** Otherwise use roles ("อดีตซีอีโอของ GitHub", "นักเขียนนิยายไซไฟ"). Investors are worth naming only with a one-phrase credential ("กองทุนที่เคยลงทุนช่วงแรกใน…").
7. **Business jargon is allowed for this audience** (switching cost, ARR/เอเออาร์, valuation) but explain it in Thai the first time. Prefer Thai when English adds nothing.
8. **Every point ends with "แปลว่า…"** — the business takeaway, not just the fact.
9. **Lesson speaks to founders/investors directly** and ends with an everyday Thai metaphor (e.g., "โมเดลคือเมล็ดกาแฟที่ทุกร้านสั่งจากเจ้าเดียวกัน แต่ไม่ใช่ทุกร้านที่จำได้ว่าลูกค้าสั่งหวานน้อย").
10. **Writing for the ear:** one idea per sentence, short sentences, few "และ/แต่" chains, spoken Thai (ยังไง not อย่างไร), read aloud to test.
11. **Fact discipline:** never present unverified claims as fact in the hook; flag unverified items to the user every time.

## Hook formulas that worked

- **Context contrast + money + twist** (EP1 v4): "ในวันที่ใคร ๆ ก็สร้างแชตบอตได้ภายในสุดสัปดาห์เดียว… นักลงทุนกลับเพิ่งทุ่มเงินราวพันล้านบาท ให้กับเอเลี่ยนตัวการ์ตูน… หน้าที่ของมันมีอยู่อย่างเดียว… คือคุยเป็นเพื่อนเรา"
- Shocking result → "แต่ที่เด็ดกว่านั้นคือ…" (ลงทุนแมน)
- A direct question to the listener ("ถ้าต้อง…คุณจะ…?")

Avoid: generic openers ("ทุกวันนี้…", "ในยุคที่…" without a concrete fact), long scenes before saying what the topic is, greetings in the first seconds.

## Anti-patterns (why EP1 v1/v2 failed)

| Anti-pattern | Fix |
|---|---|
| No show name / purpose | Section 3 identity line |
| Never says plainly what the product is | Section 2 one-line definition |
| No central question; jumps between founders, design, pricing, investors, ethics, competitors | Logline + cut |
| 6–8 points in 7 minutes ("สามความลับ + สามโจทย์") | Max 3 points + max 3 risks |
| 4–5 numbers in one paragraph | Max 1–2 per sentence |
| Many English names (founders, every investor, data vendors) | Roles instead of names |
| Philosophical ending with no takeaway | Lesson for founders/investors + metaphor |
| ~25-second scene before the topic is named | Hook ≤ 15 seconds, then define |

## Pre-delivery checklist

- [ ] Logline (question + one-sentence answer) written
- [ ] First 30 s: what / why interesting / what you'll get
- [ ] Show + channel named in section 3; 3 points named up front
- [ ] ≤ 3 numbered points, each ending with "แปลว่า…"
- [ ] Every paragraph serves the question; opening question answered in the close
- [ ] No sentence with more than 2 numbers; unofficial numbers attributed
- [ ] Remaining proper names are essential
- [ ] Lesson aimed at founders/investors + metaphor; CTA continues the content
- [ ] ~4,000–5,000 chars; `tts.py check` passes with 0 errors / 0 warnings
- [ ] Unverified facts listed for the user
