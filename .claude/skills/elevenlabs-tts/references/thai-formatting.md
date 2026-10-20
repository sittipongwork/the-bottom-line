# Formatting Thai Text for Eleven v4

Goal: the model reads correctly, without stumbling, and sounds like people **talking**, not someone reading a document.
All spoken content is Thai; examples below show the Thai text to write.

## 1. Write spoken Thai, not written Thai

| Written Thai (avoid) | Spoken Thai (use) |
|---|---|
| บริษัทมีการเติบโตอย่างต่อเนื่อง | บริษัทโตต่อเนื่องมาตลอดเลยครับ |
| ท่านมีความคิดเห็นอย่างไร | คุณมองเรื่องนี้ยังไงบ้างครับ |
| ดังนั้นจึงสรุปได้ว่า | สรุปง่าย ๆ ก็คือ... |
| ทั้งนี้ทั้งนั้น | แต่ยังไงก็ตาม |

- Use ending particles that match the speaker's voice gender (`ครับ` / `ค่ะ` / `คะ`) and keep them consistent across the whole script.
- Spoken connectors: `คือ...`, `แบบว่า`, `ซึ่ง`, `ก็เลย`, `ทีนี้` — in moderation, not every sentence.
- Fillers add naturalness but max 1 per turn: `อืม...`, `เอ่อ...`

## 2. Numbers, currency, units → spell out in Thai words

Text normalization can misread numbers in context (e.g. 2025 as "สองศูนย์สองห้า"), so spell them out yourself.

| Source | Write as |
|---|---|
| 2,500 ล้านบาท | สองพันห้าร้อยล้านบาท |
| 12.5% | สิบสองจุดห้าเปอร์เซ็นต์ |
| ปี 2568 / ค.ศ. 2025 | ปีสองห้าหกแปด / ปีสองพันยี่สิบห้า |
| Q3 | ไตรมาสสาม |
| 3x / 3 เท่า | สามเท่า |
| $10M | สิบล้านดอลลาร์ |
| 1:1 (one-on-one meeting) | วันออนวัน |
| 24/7 | ยี่สิบสี่ชั่วโมงเจ็ดวัน |
| 08:30 น. | แปดโมงครึ่ง |
| 02-123-4567 | ศูนย์สอง หนึ่งสองสาม สี่ห้าหกเจ็ด |

## 3. English words and acronyms

- Loanwords Thai speakers normally say in English → **keep in English**: `startup`, `marketing`, `AI`, `data`, `business model`
- Letter-by-letter acronyms → write the Thai pronunciation: `ROI` → `อาร์โอไอ`, `KPI` → `เคพีไอ`, `SME` → `เอสเอ็มอี`, `CEO` → `ซีอีโอ`
- Acronyms read as words → keep, or write phonetically: `SaaS` → `แซส`, `OKR` → `โอเคอาร์`
- English company/brand names → keep in English; if misread, write the Thai phonetic spelling
- Thai personal names → prefix `คุณ`; if a name has an unusual reading, write it phonetically

## 4. Punctuation and pacing

| Mark | Effect | Example |
|---|---|---|
| space | Short pause between phrases (normal Thai) | `ตอนนั้นเราไม่มีเงินเลย ทีมก็มีแค่สามคน` |
| `...` | Thinking, hesitation, added weight | `แล้ววันหนึ่ง... ลูกค้ารายใหญ่ก็ยกเลิกสัญญา` |
| `—` (em dash) | Cut-off / interruption | `คุณหมายถึง—` |
| `?` | Question intonation — always add, even with `ไหม` / `หรือเปล่า` | `ทำไมถึงเลือกตลาดนี้ครับ?` |
| `!` | Higher energy — use sparingly in business shows | `ยินดีต้อนรับครับ!` |
| `,` | Works, but Thai normally uses a space instead | |

- **Do not use** SSML `<break time="1s"/>` (unsupported in v4) → use `[short pause]`, `[long pause]` or `...`
- Separate `ๆ` with spaces: `ช้า ๆ` ✅ `ช้าๆเลย` ⚠️
- Don't use `ฯลฯ` or `ฯ` → write `และอื่น ๆ` / the full name
- No emoji, markdown (`**bold**`), bullets or headings on spoken lines
- No explanatory parentheses `( )` in spoken text — the model reads them aloud

## 5. Length and turn splitting

- One line = one turn (`SPEAKER: text`)
- ~15–40 words per sentence, 1–4 sentences per turn (≤ ~400 characters)
- Long guest answers → split into several consecutive GUEST turns, or insert a short HOST reaction (`HOST: [agreeing] ครับ`)
- Text to Dialogue accepts ~2,000 characters per request — `tts.py` chunks automatically at turn boundaries
