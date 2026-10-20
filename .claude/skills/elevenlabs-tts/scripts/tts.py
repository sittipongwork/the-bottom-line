#!/usr/bin/env python3
"""ElevenLabs Eleven v4 TTS for Thai business-talk / interview scripts.

Script format (see templates/script-template.md):
    ---
    model: eleven_v4
    voices:
      HOST: "@mc1"        # registry key from voices.json (Voice Design voice)
      GUEST: <voice_id>   # or a raw ElevenLabs voice ID
    ---
    HOST: [warm] สวัสดีครับ ...
    GUEST: [thoughtful] อืม... ...

Plain transcript format (see templates/plain-template.md) — no front matter, no SPEAKER: labels,
one paragraph per beat, for pasting into the ElevenLabs app (no API). `check` detects it automatically:
    [warm] สวัสดีครับ ... [short pause] ...

    [thoughtful] ย่อหน้าถัดไป ...

Subcommands:
    check     <script.md | transcript.md>      lint the script/transcript (tags, numbers, lengths, voices)
    generate  <script.md> [--out F] [--dry-run] [--only 2-4,7] [--force]
    voices    [--search TEXT]                  list voices available to your API key
    design    <key>                            generate Voice Design previews for voices.json[key]
    design    <key> --save <generated_voice_id>  create the chosen preview as a voice, store its voice_id

Requires ELEVENLABS_API_KEY in the environment for `generate`, `voices` and `design`.
Python 3.9+, standard library only. Uses ffmpeg for concatenation when available.
"""
import argparse
import base64
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import wave
from pathlib import Path

API_BASE = os.environ.get("ELEVENLABS_API_BASE", "https://api.elevenlabs.io")
REGISTRY_PATH = Path(__file__).resolve().parent.parent / "voices.json"

DEFAULTS = {
    "model": "eleven_v4",
    "language": "th",
    "mode": "dialogue",
    "output_format": "mp3_44100_128",
    "stability": 0.5,
    "similarity": 0.75,
    "speed": 1.0,
    "seed": None,
    "max_chars": None,
}
DIALOGUE_MAX_CHARS = 2000
SINGLE_MAX_CHARS = 5000
TURN_WARN_CHARS = 400
PLAIN_PARA_WARN_CHARS = 600   # plain transcript: one paragraph per beat
APP_MAX_CHARS = 5000          # assumed per-generation limit in the ElevenLabs app (check the UI)

# Mirrors references/audio-tags.md
RECOMMENDED_TAGS = {
    # tone
    "warm", "professional", "friendly", "confident", "enthusiastic", "excited", "happy",
    "intrigued", "grateful", "curious", "questioning", "thoughtful", "reflective", "serious",
    "calm", "reassuring", "sympathetic", "matter-of-fact", "impressed", "surprised",
    "skeptical", "cautiously", "proud", "humble", "playful", "mischievously", "sarcastic",
    # reactions
    "chuckles", "laughs", "laughing", "sighs", "exhales", "inhales deeply", "clears throat",
    "short pause", "long pause", "pause",
    # dialogue
    "interrupting", "overlapping", "jumping in", "agreeing",
    # allowed for intro/outro only
    "applause", "clapping",
}
AVOID_TAGS = {
    "gunshot", "explosion", "fart", "sings", "woo", "crying", "wheezing", "snorts",
    "whispers", "whisper", "whispering", "angry", "appalled", "panicking", "robotic voice",
}

TURN_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_\-]*)\s*:\s*(.+)$")
TAG_RE = re.compile(r"\[([^\[\]]+)\]")


# ---------------------------------------------------------------- voice registry

def load_registry():
    if not REGISTRY_PATH.exists():
        return {}
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def save_registry(registry):
    REGISTRY_PATH.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_voices(voices):
    """Replace '@key' references with registry voice IDs. Returns (resolved, problems)."""
    registry = load_registry()
    resolved, problems = {}, []
    for speaker, value in voices.items():
        value = "" if value is None else str(value)
        if value.startswith("@"):
            key = value[1:]
            entry = registry.get(key)
            if entry is None:
                problems.append(f"speaker {speaker}: {value} is not in {REGISTRY_PATH.name}")
            elif not entry.get("voice_id"):
                problems.append(f"speaker {speaker}: {value} has no voice_id yet — run `tts.py design {key}` then `--save`")
            else:
                resolved[speaker] = entry["voice_id"]
        elif value and not value.startswith("<"):
            resolved[speaker] = value
    return resolved, problems


# ---------------------------------------------------------------- parsing

def parse_scalar(value):
    value = value.strip()
    if value.startswith(("'", '"')) and value.endswith(value[0]) and len(value) >= 2:
        return value[1:-1]
    if value.lower() in ("null", "none", "~", ""):
        return None
    for cast in (int, float):
        try:
            return cast(value)
        except ValueError:
            pass
    return value


def parse_script(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    config = dict(DEFAULTS)
    voices = {}
    body_start = 0

    if lines and lines[0].strip() == "---":
        try:
            end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
        except StopIteration:
            sys.exit(f"{path}: front matter starts with --- but never closes")
        in_voices = False
        for raw in lines[1:end]:
            line = raw.split(" #", 1)[0].rstrip()
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if in_voices and raw[:1] in (" ", "\t"):
                key, _, val = line.strip().partition(":")
                voices[key.strip()] = parse_scalar(val)
                continue
            in_voices = False
            key, _, val = line.partition(":")
            key = key.strip()
            if key == "voices":
                in_voices = True
            else:
                config[key] = parse_scalar(val)
        body_start = end + 1

    if body_start == 0 and not any(TURN_RE.match(l.strip()) for l in lines):
        return parse_plain(lines)

    turns = []  # dicts: speaker, text, line
    stray = []
    for idx in range(body_start, len(lines)):
        line = lines[idx].strip()
        if not line or line.startswith(("#", "<!--", ">")):
            continue
        m = TURN_RE.match(line)
        if m:
            turns.append({"speaker": m.group(1), "text": m.group(2).strip(), "line": idx + 1})
        elif turns:
            turns[-1]["text"] += " " + line  # continuation of the previous turn
        else:
            stray.append(idx + 1)
    return config, voices, turns, stray


def parse_plain(lines):
    """Plain transcript: blank-line separated paragraphs, no front matter or speaker labels."""
    config = dict(DEFAULTS, format="plain")
    turns, markup = [], []
    current = None
    for idx, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line:
            current = None
            continue
        if re.match(r"^(#|[-*+] |\d+\. |---)", line):
            markup.append(idx)
        if current is None:
            current = {"speaker": "PARAGRAPH", "text": line, "line": idx}
            turns.append(current)
        else:
            current["text"] += " " + line
    config["markup_lines"] = markup
    return config, {}, turns, []


# ---------------------------------------------------------------- lint

def spoken_text(text):
    return TAG_RE.sub("", text)


def check_script(config, voices, turns, stray, require_voices=False):
    """Return (errors, warnings, infos) as lists of strings."""
    errors, warnings, infos = [], [], []
    if config.get("format") == "plain":
        return check_plain(config, turns)
    for ln in stray:
        warnings.append(f"L{ln}: text before the first 'SPEAKER:' line is ignored")
    if not turns:
        errors.append("no turns found — lines must look like 'HOST: [tag] ข้อความ'")
        return errors, warnings, infos

    if config.get("model") != "eleven_v4":
        warnings.append(f"model is {config.get('model')!r}; this skill is tuned for eleven_v4")
    if config.get("mode") not in ("dialogue", "single"):
        errors.append(f"mode must be 'dialogue' or 'single', got {config.get('mode')!r}")
    stab = config.get("stability")
    if stab not in (0, 0.0, 0.5, 1, 1.0):
        warnings.append(f"stability {stab} — v3/v4 work best with 0.0 (Creative), 0.5 (Natural) or 1.0 (Robust)")

    speakers = sorted({t["speaker"] for t in turns})
    resolved, problems = resolve_voices(voices)
    voice_issues = errors if require_voices else warnings
    voice_issues.extend(problems)
    for sp in speakers:
        if sp not in resolved and not any(p.startswith(f"speaker {sp}:") for p in problems):
            voice_issues.append(f"speaker {sp} has no voice ID in front matter 'voices:'")
    for sp in voices:
        if sp not in speakers:
            infos.append(f"voice {sp} is defined but never speaks")
    if config.get("mode") == "dialogue" and len(speakers) > 10:
        errors.append("Text to Dialogue allows at most 10 voices per request")

    tag_count = check_lines(turns, warnings, errors, infos)
    for t in turns:
        ln, n = t["line"], len(t["text"])
        if n > DIALOGUE_MAX_CHARS:
            errors.append(f"L{ln}: turn is {n} chars (> {DIALOGUE_MAX_CHARS}) — split it into several turns")
        elif n > TURN_WARN_CHARS:
            warnings.append(f"L{ln}: turn is {n} chars — consider splitting (target ≤ {TURN_WARN_CHARS})")

    untagged = sum(1 for t in turns if not TAG_RE.search(t["text"]))
    total_chars = sum(len(t["text"]) for t in turns)
    infos.append(
        f"{len(turns)} turns · {len(speakers)} speakers ({', '.join(speakers)}) · "
        f"{tag_count} tags · {untagged} untagged turns · {total_chars} chars"
    )
    if tag_count > len(turns) * 2:
        warnings.append("tag density is high (> 2 per turn on average) — business talk should sound natural, not theatrical")
    return errors, warnings, infos


def check_lines(turns, warnings, errors, infos):
    """Text-level checks shared by script and plain formats; returns the tag count."""
    tag_count = 0
    unknown = {}
    for t in turns:
        ln, text = t["line"], t["text"]
        tags = [x.strip() for x in TAG_RE.findall(text)]
        tag_count += len(tags)
        for tag in tags:
            low = tag.lower()
            if low in AVOID_TAGS:
                warnings.append(f"L{ln}: [{tag}] is on the avoid list for business/interview content")
            elif low not in RECOMMENDED_TAGS:
                unknown.setdefault(tag, []).append(ln)
        if re.search(r"(\[[^\[\]]+\]\s*){3,}", text):
            warnings.append(f"L{ln}: 3+ tags stacked together — keep it to 2 at most")
        if "<break" in text:
            errors.append(f"L{ln}: SSML <break> is not supported by Eleven v4 — use [short pause] or ...")
        if re.search(r"[【】（）]", text):
            warnings.append(f"L{ln}: use ASCII [ ] for tags, not full-width brackets")

        spoken = spoken_text(text)
        if not spoken.strip():
            errors.append(f"L{ln}: line has tags but nothing to say")
        digits = re.findall(r"\d[\d,\.:/%]*", spoken)
        if digits:
            warnings.append(f"L{ln}: digits {digits} — spell numbers out in Thai words (see thai-formatting.md)")
        if re.search(r"\([^)]*\)", spoken):
            warnings.append(f"L{ln}: parentheses will be read aloud — remove or rephrase")
        if re.search(r"\*\*|__|`", spoken):
            warnings.append(f"L{ln}: markdown formatting in spoken text")
        if re.search("[\U0001F300-\U0001FAFF☀-➿]", spoken):
            warnings.append(f"L{ln}: emoji in spoken text")
        if "ฯ" in spoken:
            warnings.append(f"L{ln}: 'ฯ' / 'ฯลฯ' — write the full words instead")
        if re.search(r"[ก-๙]ๆ|ๆ[ก-๙A-Za-z]", spoken):
            warnings.append(f"L{ln}: put spaces around ๆ (e.g. จริง ๆ)")
        acronyms = sorted(set(re.findall(r"\b[A-Z]{2,5}\b", spoken)) - {"AI"})
        if acronyms:
            infos.append(f"L{ln}: acronyms {acronyms} — consider Thai spelling (e.g. ROI → อาร์โอไอ) if misread")
    for tag, lns in sorted(unknown.items()):
        infos.append(f"[{tag}] (L{','.join(map(str, lns))}) is not in the recommended list — test it with your voice")
    return tag_count


def check_plain(config, turns):
    errors, warnings, infos = [], [], []
    if not turns:
        errors.append("transcript is empty")
        return errors, warnings, infos
    for ln in config.get("markup_lines", []):
        warnings.append(f"L{ln}: heading/bullet/markdown line — the plain transcript is pasted as-is, keep spoken text only")
    tag_count = check_lines(turns, warnings, errors, infos)
    for t in turns:
        n = len(t["text"])
        if n > PLAIN_PARA_WARN_CHARS:
            warnings.append(f"L{t['line']}: paragraph is {n} chars — consider splitting (target ≤ {PLAIN_PARA_WARN_CHARS})")
        if not t["text"].lstrip().startswith("["):
            warnings.append(f"L{t['line']}: paragraph does not start with a tone tag")
    total = sum(len(t["text"]) for t in turns)
    pastes = -(-total // APP_MAX_CHARS)
    infos.append(f"plain transcript · {len(turns)} paragraphs · {tag_count} tags · {total} chars")
    if pastes > 1:
        infos.append(f"> {APP_MAX_CHARS} chars — paste into the ElevenLabs app in ~{pastes} parts, split at paragraph breaks")
    if tag_count > len(turns) * 4:
        warnings.append("tag density is high (> 4 per paragraph on average) — business talk should sound natural, not theatrical")
    return errors, warnings, infos


def print_report(errors, warnings, infos):
    for e in errors:
        print(f"ERROR  {e}")
    for w in warnings:
        print(f"WARN   {w}")
    for i in infos:
        print(f"INFO   {i}")
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")


# ---------------------------------------------------------------- chunking

def split_long_text(text, limit):
    parts, current = [], ""
    for piece in re.split(r"(?<=\s)", text):
        if current and len(current) + len(piece) > limit:
            parts.append(current.strip())
            current = ""
        current += piece
    if current.strip():
        parts.append(current.strip())
    return parts


def build_chunks(config, turns):
    mode = config["mode"]
    limit = int(config.get("max_chars") or (DIALOGUE_MAX_CHARS if mode == "dialogue" else SINGLE_MAX_CHARS))
    chunks = []

    if mode == "dialogue":
        current, size = [], 0
        for t in turns:
            for text in split_long_text(t["text"], limit):
                if current and size + len(text) > limit:
                    chunks.append(current)
                    current, size = [], 0
                current.append({"speaker": t["speaker"], "text": text})
                size += len(text)
        if current:
            chunks.append(current)
    else:
        # single: merge consecutive turns of the same speaker
        for t in turns:
            last = chunks[-1] if chunks else None
            if last and last[0]["speaker"] == t["speaker"] and len(last[0]["text"]) + len(t["text"]) + 1 <= limit:
                last[0]["text"] += " " + t["text"]
            else:
                for text in split_long_text(t["text"], limit):
                    chunks.append([{"speaker": t["speaker"], "text": text}])
    return chunks


def parse_only(spec, total):
    if not spec:
        return set(range(1, total + 1))
    selected = set()
    for part in spec.split(","):
        a, _, b = part.strip().partition("-")
        selected.update(range(int(a), int(b or a) + 1))
    return {i for i in selected if 1 <= i <= total}


# ---------------------------------------------------------------- API

def api_key():
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("ELEVENLABS_API_KEY is not set. Run: export ELEVENLABS_API_KEY=... (do not commit it)")
    return key


def http(method, path, payload=None, query=None, retries=3):
    url = API_BASE + path + ("?" + urllib.parse.urlencode(query) if query else "")
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    headers = {"xi-api-key": api_key(), "Accept": "*/*"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                return resp.read(), resp.headers
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                wait = 2 ** (attempt + 1)
                print(f"  HTTP {e.code}, retrying in {wait}s ...", file=sys.stderr)
                time.sleep(wait)
                continue
            sys.exit(f"HTTP {e.code} from {path}: {body}")
        except urllib.error.URLError as e:
            if attempt < retries:
                time.sleep(2 ** (attempt + 1))
                continue
            sys.exit(f"network error calling {path}: {e.reason}")


def common_fields(config):
    fields = {"model_id": config["model"], "apply_text_normalization": "auto"}
    if config.get("language"):
        fields["language_code"] = config["language"]
    if config.get("seed") is not None:
        fields["seed"] = int(config["seed"])
    return fields


def synth_dialogue(config, voices, chunk):
    payload = common_fields(config)
    payload["inputs"] = [{"text": t["text"], "voice_id": voices[t["speaker"]]} for t in chunk]
    payload["settings"] = {"stability": float(config["stability"]), "similarity": float(config["similarity"])}
    audio, _ = http("POST", "/v1/text-to-dialogue", payload, {"output_format": config["output_format"]})
    return audio


def synth_single(config, voices, chunk):
    turn = chunk[0]
    payload = common_fields(config)
    payload["text"] = turn["text"]
    payload["voice_settings"] = {
        "stability": float(config["stability"]),
        "similarity_boost": float(config["similarity"]),
        "speed": float(config["speed"]),
    }
    voice_id = urllib.parse.quote(str(voices[turn["speaker"]]))
    audio, _ = http("POST", f"/v1/text-to-speech/{voice_id}", payload, {"output_format": config["output_format"]})
    return audio


# ---------------------------------------------------------------- output

def extension(output_format):
    codec = output_format.split("_", 1)[0]
    return {"mp3": "mp3", "wav": "wav", "pcm": "pcm", "opus": "opus", "ulaw": "ulaw", "alaw": "alaw"}.get(codec, "bin")


def concat(parts, out):
    if shutil.which("ffmpeg") and out.suffix in (".mp3", ".wav", ".opus"):
        listing = out.with_suffix(".concat.txt")
        listing.write_text("".join(f"file '{p.resolve()}'\n" for p in parts), encoding="utf-8")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(out)]
        try:
            subprocess.run(cmd, check=True)
            return "ffmpeg"
        finally:
            listing.unlink(missing_ok=True)
    if out.suffix == ".wav":
        with wave.open(str(parts[0]), "rb") as first:
            params = first.getparams()
        with wave.open(str(out), "wb") as dst:
            dst.setparams(params)
            for p in parts:
                with wave.open(str(p), "rb") as src:
                    dst.writeframes(src.readframes(src.getnframes()))
        return "wave"
    if out.suffix in (".mp3", ".pcm", ".ulaw", ".alaw"):
        with open(out, "wb") as dst:
            for p in parts:
                dst.write(p.read_bytes())
        return "byte-concat"
    return None


# ---------------------------------------------------------------- commands

def cmd_check(args):
    config, voices, turns, stray = parse_script(args.script)
    errors, warnings, infos = check_script(config, voices, turns, stray)
    print_report(errors, warnings, infos)
    return 1 if errors else 0


def cmd_generate(args):
    config, voices, turns, stray = parse_script(args.script)
    if config.get("format") == "plain":
        print("this is a plain transcript (no front matter / SPEAKER: lines) — paste it into the ElevenLabs app,\n"
              "or convert it to an API script with templates/script-template.md to use `generate`")
        return 1
    if args.output_format:
        config["output_format"] = args.output_format
    errors, warnings, _ = check_script(config, voices, turns, stray, require_voices=not args.dry_run)
    if errors:
        print_report(errors, warnings, [])
        return 1
    if warnings:
        print(f"{len(warnings)} warning(s) — run `check` to see them\n")

    chunks = build_chunks(config, turns)
    selected = parse_only(args.only, len(chunks))
    total_chars = sum(len(t["text"]) for c in chunks for t in c)
    print(
        f"model={config['model']} language={config['language']} mode={config['mode']} "
        f"format={config['output_format']} stability={config['stability']} seed={config.get('seed')}"
    )
    print(f"{len(chunks)} chunk(s), {total_chars} chars total, generating {len(selected)} chunk(s)\n")
    for i, chunk in enumerate(chunks, 1):
        mark = "*" if i in selected else " "
        size = sum(len(t["text"]) for t in chunk)
        who = ",".join(dict.fromkeys(t["speaker"] for t in chunk))
        preview = chunk[0]["text"][:60].replace("\n", " ")
        print(f" {mark} #{i:02d}  {size:5d} chars  {len(chunk):3d} turns  [{who}]  {preview}…")
    if args.dry_run:
        print("\n(dry run — nothing sent to ElevenLabs)")
        return 0

    voices, _ = resolve_voices(voices)
    out = Path(args.out or Path("output") / Path(args.script).stem).with_suffix("." + extension(config["output_format"]))
    parts_dir = out.parent / (out.stem + "_parts")
    parts_dir.mkdir(parents=True, exist_ok=True)
    synth = synth_dialogue if config["mode"] == "dialogue" else synth_single

    parts = []
    for i, chunk in enumerate(chunks, 1):
        part = parts_dir / f"{i:03d}{out.suffix}"
        parts.append(part)
        if i not in selected:
            continue
        if part.exists() and not args.force and not args.only:
            print(f"#{i:02d} exists, skipping (use --force to regenerate)")
            continue
        print(f"#{i:02d} generating ...", flush=True)
        part.write_bytes(synth(config, voices, chunk))

    missing = [p for p in parts if not p.exists()]
    if missing:
        print(f"\n{len(missing)} part(s) not generated yet; skipping merge. Parts in {parts_dir}/")
        return 0
    method = concat(parts, out)
    if method:
        print(f"\nmerged {len(parts)} part(s) via {method} → {out}")
        if method == "byte-concat" and out.suffix == ".mp3":
            print("tip: install ffmpeg (brew install ffmpeg) for a cleaner merge")
    else:
        print(f"\ncannot merge {out.suffix} without ffmpeg; parts are in {parts_dir}/")
    return 0


def cmd_voices(args):
    raw, _ = http("GET", "/v1/voices")
    data = json.loads(raw)
    needle = (args.search or "").lower()
    for v in data.get("voices", []):
        labels = v.get("labels") or {}
        line = f"{v.get('voice_id')}  {v.get('name')}  " + " ".join(f"{k}={val}" for k, val in labels.items())
        if needle in line.lower():
            print(line)
    return 0


def cmd_design(args):
    registry = load_registry()
    entry = registry.get(args.key)
    if entry is None:
        sys.exit(f"'{args.key}' is not in {REGISTRY_PATH} — add an entry with at least 'name' and 'description'")
    preview_dir = Path(args.preview_dir) / args.key

    if args.save:
        if entry.get("voice_id") and not args.force:
            sys.exit(f"'{args.key}' already has voice_id {entry['voice_id']} — pass --force to replace it")
        played = []
        meta = preview_dir / "previews.json"
        if meta.exists():
            played = [p for p in json.loads(meta.read_text(encoding="utf-8"))["generated_voice_ids"] if p != args.save]
        payload = {
            "voice_name": args.name or entry.get("name") or args.key,
            "voice_description": entry["description"],
            "generated_voice_id": args.save,
            "labels": {"language": "th", "use_case": "business podcast", "registry_key": args.key},
        }
        if played:
            payload["played_not_selected_voice_ids"] = played
        raw, _ = http("POST", "/v1/text-to-voice", payload)
        voice_id = json.loads(raw)["voice_id"]
        entry.update({
            "voice_id": voice_id,
            "generated_voice_id": args.save,
            "created_at": datetime.date.today().isoformat(),
        })
        save_registry(registry)
        print(f"created voice {voice_id} for '{args.key}' and saved it to {REGISTRY_PATH.name}")
        print(f"use it in a script front matter as:  HOST: \"@{args.key}\"")
        return 0

    payload = {
        "voice_description": entry["description"],
        "model_id": args.model or entry.get("design_model") or "eleven_ttv_v3",
        "guidance_scale": args.guidance_scale,
        "loudness": args.loudness,
    }
    text = entry.get("preview_text")
    if text and 100 <= len(text) <= 1000:
        payload["text"] = text
    else:
        if text:
            print(f"preview_text is {len(text)} chars (needs 100-1000); using auto-generated text", file=sys.stderr)
        payload["auto_generate_text"] = True
    if args.seed is not None:
        payload["seed"] = args.seed

    print(f"designing '{args.key}' with {payload['model_id']} ...", flush=True)
    raw, _ = http("POST", "/v1/text-to-voice/design", payload, {"output_format": "mp3_44100_128"})
    data = json.loads(raw)
    preview_dir.mkdir(parents=True, exist_ok=True)
    ids = []
    for i, p in enumerate(data.get("previews", []), 1):
        gid = p["generated_voice_id"]
        ids.append(gid)
        path = preview_dir / f"preview_{i}_{gid}.mp3"
        path.write_bytes(base64.b64decode(p["audio_base_64"]))
        print(f"  #{i}  {gid}  {p.get('duration_secs', 0):.1f}s  {path}")
    (preview_dir / "previews.json").write_text(
        json.dumps({"generated_voice_ids": ids, "text": data.get("text"), "request": payload}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nlisten to the previews, then keep one with:\n  tts.py design {args.key} --save <generated_voice_id>")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("check", help="lint a script")
    p.add_argument("script")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("generate", help="generate audio")
    p.add_argument("script")
    p.add_argument("--out", help="output file (extension follows output_format); default output/<script>.<ext>")
    p.add_argument("--output-format", help="override output_format from the front matter")
    p.add_argument("--only", help="chunk numbers to (re)generate, e.g. 3 or 2-4,7")
    p.add_argument("--dry-run", action="store_true", help="show chunks without calling the API")
    p.add_argument("--force", action="store_true", help="regenerate parts that already exist")
    p.set_defaults(func=cmd_generate)

    p = sub.add_parser("voices", help="list voices on your account")
    p.add_argument("--search", help="filter by name/label text")
    p.set_defaults(func=cmd_voices)

    p = sub.add_parser("design", help="Voice Design: preview or create a voice from voices.json")
    p.add_argument("key", help="registry key in voices.json, e.g. mc1")
    p.add_argument("--save", metavar="GENERATED_VOICE_ID", help="create this preview as a permanent voice")
    p.add_argument("--name", help="voice name when saving (default: registry 'name')")
    p.add_argument("--model", help="design model: eleven_ttv_v3 (default) or eleven_multilingual_ttv_v2")
    p.add_argument("--guidance-scale", type=float, default=5.0, help="prompt adherence (default 5; lower for long prompts)")
    p.add_argument("--loudness", type=float, default=0.5, help="-1..1 (default 0.5)")
    p.add_argument("--seed", type=int, help="seed for reproducible previews")
    p.add_argument("--preview-dir", default="output/voice-design", help="where preview mp3s are written")
    p.add_argument("--force", action="store_true", help="replace an existing voice_id when saving")
    p.set_defaults(func=cmd_design)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
