---
name: next-frontier-pattern
description: Content pattern for "Next Frontier" — the THE BOTTOM LINE channel's solo-MC (MC1) Thai show that breaks down how AI startups win, for business people interested in AI startups. Use when researching, outlining, writing, rewriting or reviewing a Next Frontier episode script/transcript (files under NextFrontier/), choosing an episode's hook, logline or structure, or when the user says a script is confusing/boring/unclear. Pair with the elevenlabs-tts skill for TTS formatting and tags.
---

# Next Frontier — Episode Pattern (THE BOTTOM LINE)

Distilled from research into ลงทุนแมน, The Indicator (NPR), The Daily (NYT), Acquired, Modern MBA, How I Built This and writing-for-the-ear guides. Full research notes (Thai): [references/research-notes.md](references/research-notes.md). Reference shows and what each teaches: [references/reference-shows.md](references/reference-shows.md).

## Show identity (fixed)

| Item | Value |
|---|---|
| Channel | **THE BOTTOM LINE** (in spoken text write `The Bottom Line`; all-caps may be read letter by letter) |
| Show | **Next Frontier** |
| Promise | ถอดเกมธุรกิจของสตาร์ทอัพ AI ทั่วโลก ว่าเขาชนะกันได้ยังไง |
| Audience | นักธุรกิจที่สนใจสตาร์ทอัพ AI (founders, investors, business owners) |
| Host | MC1 (`@mc1`) is **female**: `ค่ะ` for statements, `คะ` for questions and after `นะ`/`ล่ะ`; never `ครับ`. Self-reference `เรา` (e.g. "วันนี้เราจะ…"), avoid `ผม`. |
| Format | Solo MC (`@mc1`), Thai, 5–8 min, ~4,000–5,000 chars (fits one paste in the ElevenLabs app) |
| Output | Plain transcript (elevenlabs-tts "plain" format) at `NextFrontier/ep<N>_<slug>/transcript_v<N>.md` — never overwrite an earlier version |
| Reference episode | [references/example-episode.md](references/example-episode.md) (snapshot of EP1 Tolan `transcript_v4.md`) — structure and tone only; it still uses the male particle `ครับ`, and its opening paragraph predates the "name the company in the opening" rule, so follow [Opening paragraph](#opening-paragraph-ช่วงเปิด) instead |
| Still undecided | Signature line (like "ลงทุนแมนจะเล่าให้ฟัง") — ask the user before inventing one |

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
| 1 | **Opening (ช่วงเปิด)** — the whole first paragraph | 0:00–0:15 | 150–250 | Its own paragraph. **Names the company in the first or second sentence** + one concrete, surprising fact or contradiction + twist. No greeting. See [Opening paragraph](#opening-paragraph-ช่วงเปิด). | `[intrigued]` |
| 2 | What it does + central question | 0:15–0:30 | 200 | The company is already named, so don't re-introduce it: say what it does in the simplest Thai, then the episode's question | `[curious]` → `[thoughtful]` |
| 3 | Show intro + promise | 0:30–0:45 | 200 | "สวัสดีค่ะ ยินดีต้อนรับเข้าสู่ Next Frontier ทางช่อง The Bottom Line รายการที่จะพาไปถอดเกมธุรกิจของสตาร์ทอัพ AI ทั่วโลก ว่าเขาชนะกันได้ยังไง" + "วันนี้เราจะตอบคำถามนี้ผ่านสามเรื่อง คือ…" (name the 3) | `[warm]` |
| 4 | Context | 0:45–1:45 | 500–600 | The market problem and why others can't solve it — so a newcomer can follow | `[professional]` `[thoughtful]` |
| 5 | Points 1–3 | 1:45–5:30 | ~700 each | Each: claim → example/scene → one number → "แปลว่า…" (business meaning) | `[confident]` `[matter-of-fact]` `[warm]` |
| 6 | Other side of the coin | 5:30–6:30 | 400–500 | Max 2–3 risks or open problems | `[serious]` `[calm]` |
| 7 | Recap + answer + lesson | 6:30–7:15 | 400–600 | Recap the 3 points by number, answer the opening question in one sentence, one lesson for founders/investors + a memorable metaphor | `[calm]` → `[thoughtful]` → `[warm]` `[confident]` |
| 8 | CTA + sign-off | 7:15–7:30 | 200–300 | Question that continues the content, aimed at founders/investors; "กด Like กด Subscribe ช่อง The Bottom Line"; "แล้วพบกันใหม่ใน Next Frontier ตอนหน้า… สวัสดีค่ะ" | `[friendly]` → `[enthusiastic]` → `[warm]` |

The structure is also an **open loop**: the question asked in section 2 must be answered explicitly in section 7 ("กลับมาที่คำถามตอนต้น…").

## Writing rules

1. **One episode = one question.** Cut any paragraph that doesn't help answer it.
2. **First paragraph** answers: which company, and why it's worth hearing. **First 30 seconds** add: what it does, and what I'll get.
3. **Say what it is before describing how it looks** — the listener can't see; audio alone must make sense.
4. **Max 3 points**, always numbered aloud ("เรื่องแรก…", "เรื่องที่สอง…"), recapped before the close.
5. **Max 1–2 numbers per sentence.** Round them and make them tangible ("สิบคน มีเจ็ดคน…", "แทบจะทุกวัน"). Convert big USD to baht once ("ราวพันล้านบาท"). Derived numbers ("หารคร่าว ๆ…") must say they're rough.
6. **Names only when they matter.** Otherwise use roles ("อดีตซีอีโอของ GitHub", "นักเขียนนิยายไซไฟ"). Investors are worth naming only with a one-phrase credential ("กองทุนที่เคยลงทุนช่วงแรกใน…").
7. **Business jargon is allowed for this audience** (switching cost, ARR/เอเออาร์, valuation) but explain it in Thai the first time. Prefer Thai when English adds nothing.
8. **Every point ends with "แปลว่า…"** — the business takeaway, not just the fact.
9. **Lesson speaks to founders/investors directly** and ends with an everyday Thai metaphor (e.g., "โมเดลคือเมล็ดกาแฟที่ทุกร้านสั่งจากเจ้าเดียวกัน แต่ไม่ใช่ทุกร้านที่จำได้ว่าลูกค้าสั่งหวานน้อย").
10. **Writing for the ear:** one idea per sentence, short sentences, few "และ/แต่" chains, spoken Thai (ยังไง not อย่างไร), read aloud to test.
11. **Fact discipline:** never present unverified claims as fact in the hook; flag unverified items to the user every time.

## Opening paragraph (ช่วงเปิด)

The first paragraph of the transcript is a self-contained opening segment. A listener who stops after it must already know **which company** the episode is about and **why it's worth hearing**.

Rules:
1. **One paragraph, one segment.** The opening is paragraph 1 only, ~150–250 characters (~10–15 seconds), separated by a blank line from section 2. It starts with `[intrigued]`.
2. **Company name in the first or second sentence.** Say it by name (`DeepSeek`, `Tolan`), not "บริษัทเล็ก ๆ แห่งหนึ่ง", and never hold it back as a reveal for paragraph 2. If the name alone means nothing to a Thai listener, attach a 2–4 word tag: "DeepSeek บริษัท AI จากจีน", "Tolan แอปเพื่อนคุย AI".
3. **It must be interesting, not just a definition.** Name + one concrete surprising fact (money, scale, speed, or impact on a giant) + a twist/contradiction. "DeepSeek คือบริษัท AI จากจีน" alone is a definition, not an opening.
4. **One fact, max 2 numbers.** Leave the product explanation to section 2 and the backstory to section 4/5.
5. **No greeting, no show name** — those belong to section 3.
6. **Verified facts only** in the opening (rule 11).

Formulas (company name **bold** for illustration only — never use markdown in the transcript):
- **Name + impact on a giant + twist:** "ต้นปีที่แล้ว บริษัท AI จากจีนชื่อ **DeepSeek** ทำให้หุ้น Nvidia ร่วงจนมูลค่าหายไปเกือบยี่สิบล้านล้านบาท ภายในวันเดียว [short pause] ที่น่าทึ่งกว่านั้นคือ... บริษัทนี้ไม่ได้เกิดในซิลิคอนแวลลีย์ แต่เกิดมาจากกองทุนเทรดหุ้น"
- **Name + money + contradiction:** "นักลงทุนเพิ่งทุ่มเงินราวพันล้านบาท ให้กับ **Tolan**... [short pause] แอปที่ไม่ได้ช่วยเขียนโค้ด ไม่ได้ช่วยทำงาน แต่เป็นเอเลี่ยนตัวการ์ตูน ที่มีหน้าที่อย่างเดียว... คือคุยเป็นเพื่อนเรา"
- **Shocking result → "แต่ที่เด็ดกว่านั้นคือ…"** (ลงทุนแมน), with the company named in the result sentence.
- **Direct question → name as the answer:** "ถ้าต้องสร้าง AI ระดับโลกด้วยงบไม่ถึงหนึ่งในสิบของคู่แข่ง คุณจะทำได้ไหม? [short pause] **DeepSeek** ทำมาแล้ว..."

Avoid: an unnamed "บริษัทหนึ่ง…" opening that reveals the name later, generic openers ("ทุกวันนี้…", "ในยุคที่…" without a concrete fact), long scenes before the topic is named, greetings in the first seconds.

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
| ~25-second scene before the topic is named | Opening ≤ 15 seconds, then define |
| Company name held back until paragraph 2 (EP1 v4, EP2 v1 open with "a cartoon alien" / "a small company from Hangzhou") | Name the company in the opening's first or second sentence |

## Pre-delivery checklist

- [ ] Logline (question + one-sentence answer) written
- [ ] Paragraph 1 is a standalone opening: company named in sentence 1–2, one surprising fact + twist, ≤ ~250 chars, no greeting
- [ ] First 30 s: what it does / why interesting / what you'll get
- [ ] Show + channel named in section 3; 3 points named up front
- [ ] ≤ 3 numbered points, each ending with "แปลว่า…"
- [ ] Every paragraph serves the question; opening question answered in the close
- [ ] No sentence with more than 2 numbers; unofficial numbers attributed
- [ ] Remaining proper names are essential
- [ ] Lesson aimed at founders/investors + metaphor; CTA continues the content
- [ ] ~4,000–5,000 chars; `tts.py check` passes with 0 errors / 0 warnings
- [ ] Unverified facts listed for the user
