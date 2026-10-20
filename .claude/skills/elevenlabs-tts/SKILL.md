---
name: elevenlabs-tts
description: Turn Thai business-talk / interview / podcast scripts into speech with ElevenLabs Eleven v4 — format the Thai text for TTS, add [audio tags] that match the emotion of each line, and either deliver a plain tagged transcript to paste into the ElevenLabs app (default, no API) or an API script rendered via Text to Dialogue; also manages Voice Design voices (e.g. the MC1 host voice). Use when the user asks for text-to-speech, MC/host voice-over, interview audio, emotion tags for a script, Voice Design, or mentions ElevenLabs.
---

# ElevenLabs TTS — Thai Business Talk & Interview (Eleven v4)

Converts Thai scripts (host/MC, interviewer, guests) into natural-sounding business-talk audio using:
- **Model:** `eleven_v4` with `language_code: th` (spoken content is always Thai)
- **Audio tags:** English instructions in square brackets, e.g. `[warm]`, `[thoughtful]`, `[short pause]`
- **Voices:** a local registry ([voices.json](voices.json)) of Voice Design voices, referenced in scripts as `"@key"`

## Two output formats — pick one before writing

| Format | When | Layout | Template |
|---|---|---|---|
| **Plain transcript** (default) | User checks/prepares a transcript, will paste it into the ElevenLabs app (Studio / Text to Speech), or doesn't mention the API | Thai paragraphs with inline `[tags]`, a blank line between paragraphs. **No** front matter, speaker labels, `#` headings or comments (full-length example: [../next-frontier-pattern/references/example-episode.md](../next-frontier-pattern/references/example-episode.md), below its header) | [templates/plain-template.md](templates/plain-template.md) |
| **API script** | User explicitly wants audio generated via `tts.py generate` / the API, or needs several voices in one dialogue | Front matter + one `SPEAKER: [tag] Thai text` turn per line | [templates/script-template.md](templates/script-template.md) |

If the source file is already in plain format, keep the plain format. All Thai-formatting and tagging rules (steps 2–3) apply to both.

## Files

| File | Purpose |
|---|---|
| [references/audio-tags.md](references/audio-tags.md) | Tag palette + "content → tag" mapping for business/interview shows. **Read before tagging any script.** |
| [references/thai-formatting.md](references/thai-formatting.md) | Rules for writing Thai text that v4 reads correctly (numbers, English terms, pauses, turn length). |
| [references/voice-settings.md](references/voice-settings.md) | Model/API limits, stability, per-role presets, output formats, Voice Design workflow. |
| [voices.json](voices.json) | Voice registry. `mc1` = the main host/MC voice (Voice Design). |
| [templates/plain-template.md](templates/plain-template.md) | Plain transcript layout (paragraphs with inline tags, no API). **Default deliverable.** |
| [templates/script-template.md](templates/script-template.md) | API script layout (front matter + `SPEAKER: [tag] Thai text` lines). |
| [scripts/tts.py](scripts/tts.py) | CLI: `check` (auto-detects plain vs API script), `generate`, `voices`, `design`. Python 3.9+ stdlib only. |

All commands below run from the project root; `TTS=.claude/skills/elevenlabs-tts/scripts/tts.py`.

## Voices

| Key | Role | Source | Notes |
|---|---|---|---|
| `mc1` | HOST / MC | Voice Design | **Female**, 25-year-old Thai, clear, professional, medium pitch, fast-to-moderate news-podcast pacing, tech & business narrator. Full prompt in [voices.json](voices.json). |

- **MC1 is the default voice for the `HOST` speaker** in every script unless the user says otherwise: `HOST: "@mc1"`.
- MC1's style is crisp narrator — favor `[professional]`, `[confident]`, `[warm]`, `[curious]`, `[short pause]`; keep big emotional tags (`[laughs]`, `[excited]`, `[playful]`) rare.
- **MC1 is female** (decided 2026-10-20). In every HOST line use `ค่ะ` for statements and `คะ` for questions and after `นะ` / `ล่ะ` (`นะคะ`, `ล่ะคะ`, `ไหมคะ?`). Never `ครับ`. For self-reference prefer `เรา`; use `ดิฉัน` only when a first-person singular is unavoidable. Guests use the particle matching their own voice.
- Never guess voice IDs. For other speakers (guests), ask the user for a voice ID, or add a new Voice Design entry to `voices.json`.

### Creating a Voice Design voice (one-time per voice)
`voices.json` → `mc1.voice_id` is `null` until the voice is created on the user's ElevenLabs account.
1. Generate previews (costs credits — confirm with the user first):
   ```bash
   python3 $TTS design mc1
   ```
   Writes preview MP3s to `output/voice-design/mc1/` and prints each `generated_voice_id`.
2. The **user** listens and picks one. Do not pick on their behalf.
3. Save the chosen preview as a permanent voice (creates a voice on their account — confirm first):
   ```bash
   python3 $TTS design mc1 --save <generated_voice_id>
   ```
   This writes `voice_id` back into `voices.json`. Scripts using `"@mc1"` now resolve automatically.

Options: `--seed N` (reproducible previews), `--guidance-scale` (default 5; lower = more natural, higher = stricter prompt adherence), `--model eleven_multilingual_ttv_v2` (fallback if `eleven_ttv_v3` gives poor Thai).

## Workflow

### 1. Gather content and assign speakers
- Source material: raw scripts, transcripts, or bullet points (e.g. `MC/`, `NextFrontier/`).
- **Plain transcript:** skip speaker labels and voice mapping; one paragraph = one beat/topic (≤ ~600 characters), starting with a tone tag. Tone tags may change mid-paragraph when the emotion changes.
- **API script only:** speaker labels are uppercase ASCII without spaces: `HOST`, `GUEST`, `COHOST`, `NARRATOR`.
- Map voices in front matter: `HOST: "@mc1"`, others → registry key or raw voice ID. Leave `<VOICE_ID>` placeholders if unknown and tell the user.

### 2. Format the Thai text
Follow [references/thai-formatting.md](references/thai-formatting.md). Key rules:
- Write **spoken** Thai, not written Thai (natural connectors, consistent ending particles).
- Spell out numbers, currency, percentages, dates in Thai words (`2.5 พันล้านบาท` → `สองจุดห้าพันล้านบาท`).
- Keep common English loanwords in English (`AI`, `startup`); spell letter-by-letter acronyms in Thai (`ROI` → `อาร์โอไอ`).
- Pauses: `...` (hesitation/weight), `—` (cut-off), `[short pause]` / `[long pause]`. **v4 does not support SSML `<break>`.**
- API script: one line = one speaker turn, 1–4 sentences, ≤ ~400 characters. Plain transcript: one paragraph per beat, ≤ ~600 characters.

### 3. Add audio tags that match the content
Follow [references/audio-tags.md](references/audio-tags.md). Key rules:
- **Tags are always English**, the spoken text is always Thai: `HOST: [warm] สวัสดีค่ะทุกท่าน`
- Put a tone tag at the **start** of a turn; only short reactions (`[chuckles]`, `[short pause]`) go mid-sentence.
- Max 2 tags stacked; ~1 tag per 1–3 sentences. Business talk must sound credible, not theatrical.
- Change the tag when the emotion of the content changes (failure story → `[reflective]`, results → `[confident]`).
- Never use sound-effect/experimental tags (`[gunshot]`, `[fart]`, `[sings]`, `[strong X accent]`) in this format.

### 4. Lint
```bash
python3 $TTS check path/to/script.md
```
Works on both formats (a file with no front matter and no `SPEAKER:` lines is linted as a plain transcript). Flags: unknown/avoid-list tags, Arabic digits, unspaced `ๆ`, stacked tags, unresolved voices (`@mc1` without `voice_id`), long turns, parentheses, markdown, emoji. Fix all errors; fix warnings or confirm with the user.

### 5. Deliver the plain transcript, or dry run and generate (API script only)
For a plain transcript, stop after lint: the user pastes it into the ElevenLabs app. `check` reports the total characters; if it exceeds ~5,000, tell the user to paste it in parts split at paragraph breaks. Do not call the API.

For an API script:
Text to Dialogue accepts ~2,000 characters per request; the script auto-chunks at turn boundaries.
```bash
python3 $TTS generate path/to/script.md --dry-run
python3 $TTS generate path/to/script.md --out output/ep1.mp3
```
- Requires `ELEVENLABS_API_KEY` in the environment. **Never write the key into project files or print it in chat**; if missing, tell the user to `export` it themselves.
- Generation spends the user's credits: show the dry-run (chunk count, characters) and get confirmation before the first real run.
- `--only 3-5` regenerates specific chunks; existing parts are otherwise skipped (`--force` to overwrite).
- Output: per-chunk files in `<out>_parts/` plus a merged file (ffmpeg if installed, otherwise MP3 byte-concat / WAV merge).

### 6. Listen and iterate
See the Troubleshooting table at the end of [references/audio-tags.md](references/audio-tags.md#troubleshooting) (tags read aloud, over-acting, misread numbers, voice drift between chunks).

## Deliverable format
When the user asks to "prepare / tag / check a transcript", write a new **plain transcript** following [templates/plain-template.md](templates/plain-template.md) next to the source (e.g. `NextFrontier/ep1_tolan/transcript_v5.md`). Write an API script following [templates/script-template.md](templates/script-template.md) (e.g. `MC/MC_1_tts.md`) only when the user wants API generation. Never overwrite the original. Then briefly summarize what changed (tags, numbers, wording) and anything the user should verify. Reply to the user in the language they wrote in.
