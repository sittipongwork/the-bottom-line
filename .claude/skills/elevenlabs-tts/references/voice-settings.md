# Voice Settings & API Reference (Eleven v4)

## Model

| Item | Value |
|---|---|
| `model_id` | `eleven_v4` (latest; supports Thai `th`, multi-speaker dialogue, audio tags) |
| `language_code` | `th` — enforces Thai language and normalization |
| Limits | Single TTS: 10,000 chars/request · Text to Dialogue: ~2,000 chars/request, max 10 voices per request |
| Not supported | SSML `<break>`, phoneme tags (Flash v2 only) |

## Endpoints

| Mode | Endpoint | Use for |
|---|---|---|
| Dialogue (multi-voice) | `POST https://api.elevenlabs.io/v1/text-to-dialogue` | Interviews, host–guest talk — **skill default** (`mode: dialogue`) |
| Single voice | `POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}` | Solo MC, narrator, intro/outro — supports `speed` (`mode: single`) |
| Voice Design previews | `POST https://api.elevenlabs.io/v1/text-to-voice/design` | Generate preview voices from a text description |
| Voice Design create | `POST https://api.elevenlabs.io/v1/text-to-voice` | Turn a chosen `generated_voice_id` into a permanent `voice_id` |

Headers: `xi-api-key: $ELEVENLABS_API_KEY`, `Content-Type: application/json`

## Stability — how strongly tags are followed

v3/v4 recommend three standard levels (some API versions accept only these values):

| Value | Name | Effect | Use for |
|---|---|---|---|
| `0.0` | Creative | Follows tags fully, wide emotional range, may drift | Teasers, dramatic storytelling |
| `0.5` | Natural | Balanced, sounds like real conversation — **recommended for business talk/interview** | Whole show |
| `1.0` | Robust | Very steady and consistent, responds less to tags | News reads, announcements, disclaimers, sponsor reads |

`similarity` (dialogue) / `similarity_boost` (single): `0.75` is a good default.

## Per-role presets

| Role | Voice | stability | speed (single mode) | Main tags | Voice character |
|---|---|---|---|---|---|
| HOST / MC | `@mc1` | 0.5 | 1.05 | `[professional]` `[confident]` `[warm]` `[curious]` | Young Thai tech/business narrator, news-podcast pace |
| GUEST — executive / founder | ask user | 0.5 | 0.95 | `[confident]` `[thoughtful]` `[reflective]` | Calm, deeper than host, assured |
| GUEST — expert / academic | ask user | 0.5–1.0 | 0.95 | `[calm]` `[matter-of-fact]` `[thoughtful]` | Articulate, slower |
| COHOST | ask user | 0.5 | 1.05 | `[friendly]` `[playful]` `[agreeing]` | Clearly different from MC1 (gender/pitch) |
| NARRATOR / VO intro-outro | `@mc1` or other | 1.0 | 0.95–1.0 | `[professional]` `[confident]` | Steady, trailer-like |
| AD READ / sponsor | `@mc1` | 1.0 | 1.0 | `[friendly]` `[enthusiastic]` | |

Voice selection principles:
- Every speaker must be instantly distinguishable by voice (different gender, or clearly different pitch). MC1 is medium-pitch, so pick guests that are noticeably lower or higher.
- Choose voices that sound natural in Thai (filter the Voice Library by Thai, or use Voice Design with a Thai preview text).
- Note: `mode: dialogue` has no `speed` parameter — MC1's fast-to-moderate pacing comes from the voice itself. Use `mode: single` when exact speed control matters.

## Voice Design

Registry: [../voices.json](../voices.json). Each entry:

| Field | Meaning |
|---|---|
| `name` | Voice name saved on the ElevenLabs account |
| `description` | Voice Design prompt (English) |
| `design_model` | `eleven_ttv_v3` (default, better multilingual) or `eleven_multilingual_ttv_v2` |
| `preview_text` | Thai sample text the previews speak (100–1,000 chars) — keeps previews in Thai |
| `settings` | Recommended stability / similarity / speed for this voice |
| `primary_tags` / `avoid_tags` | Tagging guidance for this voice |
| `voice_id` | Filled by `tts.py design <key> --save <generated_voice_id>`; `null` = not created yet |

Design API options (via `tts.py design` flags): `guidance_scale` (default 5; lower for long, detailed prompts — sounds more natural), `loudness` (-1..1, default 0.5), `seed` (reproducible previews).

Workflow: `design mc1` → user listens to `output/voice-design/mc1/*.mp3` → `design mc1 --save <id>` → scripts use `"@mc1"`.

To add a new designed voice, add an entry to `voices.json` with `name`, `description`, `preview_text` (Thai, 100–1,000 chars) and `voice_id: null`, then run the same workflow.

## Output format (query `output_format`)

| Use | Recommended | Notes |
|---|---|---|
| Podcast / general | `mp3_44100_128` | Default |
| High-quality podcast | `mp3_44100_192` | Creator tier or above |
| Editing (DAW / Premiere) | `wav_44100` or `pcm_44100` | Pro tier or above · otherwise `wav_24000` |
| Quick preview, small files | `mp3_22050_32` | |
| YouTube / video | `wav_48000` or `opus_48000_128` | |

## Other fields the skill sends

| Field | Value | Why |
|---|---|---|
| `seed` | fixed number, e.g. `20251020` | Similar results on regeneration (best effort, not guaranteed) |
| `apply_text_normalization` | `auto` | Numbers are spelled out already, kept on as a safety net |
| `pronunciation_dictionary_locators` | (optional, not wired into `tts.py` yet) | For brand/person names that are consistently misread — create a dictionary on elevenlabs.io, max 3 per request |
