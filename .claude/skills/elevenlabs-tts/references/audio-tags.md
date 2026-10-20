# Audio Tags for Business Talk / Interview (Eleven v4, Thai speech)

Audio tags are English instructions in square brackets `[ ]` that tell Eleven v4 how to deliver a line.
They are **not spoken** (when the model understands them). Always write tags in English, even though the spoken text is Thai.

```text
HOST: [warm] สวัสดีครับ ยินดีต้อนรับเข้าสู่รายการครับ
GUEST: [thoughtful] อืม... คำถามนี้น่าสนใจมากครับ
```

## Reliability levels

| Level | Meaning |
|---|---|
| ✅ Official | In ElevenLabs' official v3/v4 tag list or the Enhance tag list — safe to use. |
| 🟡 Descriptive | Delivery descriptors that v4 interprets well (used in ElevenLabs examples) — fine, but test with the chosen voice. |
| ⛔ Avoid | Not suitable for this format. |

## 1. Tone tags — start of a turn, set the tone of the whole turn

| Tag | Level | Use when |
|---|---|---|
| `[warm]` | 🟡 | Greetings, show opening, thanking the guest, closing |
| `[professional]` | 🟡 | Introducing the guest, reading a bio, getting into serious content |
| `[friendly]` | 🟡 | Casual conversation, small talk |
| `[confident]` | 🟡 | Numbers, results, vision statements, conclusions |
| `[enthusiastic]` | 🟡 | Show opening, inviting listeners to stay tuned — energetic but polite |
| `[excited]` | ✅ | Good news, product launch, results beyond expectations (use sparingly) |
| `[intrigued]` | 🟡 | Teasers, setting up a hook |
| `[grateful]` | 🟡 | Thanking guest / listeners |
| `[happy]` | ✅ | Positive stories, relaxed moments |
| `[curious]` | ✅ | Asking questions, asking the guest to elaborate |
| `[questioning]` | 🟡 | Probing / follow-up questions |
| `[thoughtful]` | ✅ | Answers that need thought, explaining ideas |
| `[reflective]` | 🟡 | Looking back, lessons learned, failures |
| `[serious]` | 🟡 | Risks, crises, warnings |
| `[calm]` | 🟡 | Explaining complex topics, recaps |
| `[reassuring]` | 🟡 | Encouraging listeners, addressing concerns |
| `[sympathetic]` | 🟡 | Responding to the guest's hardships |
| `[matter-of-fact]` | 🟡 | Facts, figures, market data |
| `[impressed]` | 🟡 | Host reacting to the guest's achievements |
| `[surprised]` | ✅ | Unexpected numbers or information |
| `[skeptical]` / `[cautiously]` | 🟡 | Challenging questions, devil's advocate |
| `[proud]` | 🟡 | Guest describing the team's success |
| `[humble]` | 🟡 | Guest talking about themselves, crediting the team |
| `[playful]` / `[mischievously]` | 🟡 / ✅ | Light jokes, friendly teasing (very rare) |
| `[sarcastic]` | ✅ | Light ironic humor — careful, can sound impolite in Thai context |

## 2. Reaction tags — can go mid-sentence

| Tag | Level | Use when |
|---|---|---|
| `[chuckles]` | ✅ | Soft laugh — **the main laugh for business talk** |
| `[laughs]` | ✅ | Clear laugh at an actual joke |
| `[laughing]` | ✅ | Speaking while laughing |
| `[sighs]` | ✅ | Before a hard story / relief |
| `[exhales]` | ✅ | After telling something heavy |
| `[inhales deeply]` | ✅ | Before an important story |
| `[clears throat]` | ✅ | Segment change / getting serious |
| `[short pause]` | ✅ | Brief pause for emphasis, before a number or punchline |
| `[long pause]` | ✅ | Big beat, topic change (rare) |

## 3. Dialogue tags — control timing between speakers

| Tag | Level | Use when |
|---|---|---|
| `[interrupting]` | 🟡 | Cutting in — pair with `—` at the end of the previous turn |
| `[overlapping]` | 🟡 | Talking over / instant agreement |
| `[jumping in]` | 🟡 | Picking up immediately |
| `[agreeing]` | 🟡 | Short acknowledgements: "ใช่ครับ", "ถูกต้องเลยค่ะ" |

```text
HOST: [curious] แล้วตอนที่ยอดขายตกลงครึ่งหนึ่ง คุณ—
GUEST: [interrupting] —ตอนนั้นเกือบปิดบริษัทเลยครับ [sighs] จริง ๆ นะ
```

## 4. ⛔ Avoid in business / interview content
`[gunshot]`, `[explosion]`, `[fart]`, `[sings]`, `[woo]`, `[strong X accent]`, `[crying]`, `[wheezing]`, `[snorts]`, `[whispers]` (except an intentional teaser), `[angry]`, `[appalled]`, `[panicking]`, `[robotic voice]`
- `[applause]` / `[clapping]` only in show intro/outro if the user wants it — adding SFX in post-production gives more control.

---

## Content → tag mapping

| Segment / content type | Speaker | Recommended tags | Notes |
|---|---|---|---|
| Cold open / teaser | HOST | `[intrigued]` `[curious]` `[short pause]` | Hook attention, no shouting |
| Show opening, greeting | HOST | `[warm]` → `[enthusiastic]` | Slightly higher energy than elsewhere |
| Guest introduction / bio | HOST | `[professional]` `[warm]` | Respectful tone |
| Guest greets back | GUEST | `[friendly]` `[chuckles]` | |
| Opening / background question | HOST | `[curious]` | |
| Origin story | GUEST | `[reflective]` `[thoughtful]` | |
| Failure / crisis story | GUEST | `[serious]` `[sighs]` `[reflective]` | More `...` pauses |
| Host acknowledges hardship | HOST | `[sympathetic]` | Short, e.g. "เข้าใจเลยครับ" |
| Turning point | GUEST | `[inhales deeply]` → `[confident]` | |
| Numbers / business results | GUEST | `[confident]` `[matter-of-fact]`, `[short pause]` before the number | |
| Host surprised by a number | HOST | `[surprised]` `[impressed]` | |
| Strategy / framework explanation | GUEST | `[thoughtful]` `[calm]` | |
| Probing / challenging question | HOST | `[skeptical]` `[questioning]` `[cautiously]` | Stay polite |
| Joke / fun anecdote | both | `[playful]` `[chuckles]` `[laughs]` | Max 1–2 per segment |
| Advice to listeners | GUEST | `[reassuring]` `[warm]` | |
| Good news / product launch | GUEST | `[excited]` `[proud]` | |
| Recap | HOST | `[calm]` `[confident]` | |
| Thank guest / close / CTA | HOST | `[warm]` `[grateful]` | |

## Tagging rules

1. **Density:** 1 tag per 1–3 sentences (~1 tag per 30–60 Thai words). Tagging every phrase sounds like a soap opera.
2. **Max 2 stacked tags:** `[warm] [chuckles]` OK — `[warm] [excited] [laughs] [curious]` not OK.
3. **Tag must not contradict content:** `[excited]` + "บริษัทขาดทุนหนัก" sounds wrong.
4. **Match the voice's character:** a calm executive voice (or the narrator-style MC1) should rarely get `[giggles]` / `[playful]`.
5. **Re-tag long turns:** if a turn runs past 3–4 sentences, repeat or change the tag mid-turn so the emotion doesn't drift.
6. **Thai has no capital letters** — emphasize with `[short pause]` before the key word, or place the key word at the end of the sentence.
7. **Thai fillers/interjections are text, not tags:** `อืม...`, `เอ่อ...`, `โห`, `ว้าว`, `จริงเหรอครับ` sound more natural than `[hmm]`.
8. **Tags not on this list:** descriptive phrases work, e.g. `[low, steady voice]`, `[speaking slowly]` — test before relying on them.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Tag is read aloud | Switch to a ✅ Official tag or a clearer descriptor; make sure it uses ASCII `[ ]`, not `( )` or `【 】` |
| Over-acted, theatrical | Fewer tags; raise `stability` (0.5 Natural → 1.0 Robust); replace `[excited]` with `[enthusiastic]`/`[warm]` |
| Flat, no emotion | Lower `stability` (→ 0.0 Creative); add a tone tag at the start; make the text itself expressive (interjections, particles) |
| Numbers / acronyms misread | Spell them out in Thai per [thai-formatting.md](thai-formatting.md) |
| Same voice sounds different across chunks | Set `seed` in front matter; raise stability; avoid chunk breaks in the middle of an emotional moment |
| Laugh too long/loud | Use `[chuckles]` instead of `[laughs]` |
| Pacing too fast | Add `...` and `[short pause]`; split long sentences; or use `mode: single` with `speed` (0.7–1.2) |
