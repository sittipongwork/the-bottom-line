#!/usr/bin/env python3
"""วางเลเยอร์ข้อความของ BizShorts (คำโปรย + ตัวเลขเน้น + จัดสไตล์ซับ) ลงโปรเจกต์ CapCut จากช็อตลิสต์

อ่านตาราง `เวลา | ซับ | คำโปรย | ตัวเลขเน้น | ...` ใน shotlist แล้วสร้าง
  - แทร็กข้อความ "BizShorts-คำโปรย": 1 ชิ้นต่อแถว ขาว ฟอนต์ไทยแบบ display/ลายมือ ขนาด 26 (ลดอัตโนมัติถึง 16
    ให้พอดี ≤2 บรรทัดใน 80% ของจอ ตัดบรรทัดที่ขอบคำไทย) ที่ y ≈ +0.40 ขึ้นตั้งแต่ต้นแถวจนถึงต้นแถวถัดไป
  - แทร็กข้อความ "BizShorts-ตัวเลข": เหลือง #FFD700 ตัวหนา ขอบดำหนา ขนาด 24 (ลดถึง 14) ที่ y ≈ -0.30 นาน 2–3.5 วิ
    ขึ้นตอนบรรทัดซับที่มีตัวเลขนั้นเริ่มพูด (คั่นหลายชิ้นในแถวเดียวด้วย " / ")
  - อนิเมชันเข้า 0.25 วิ ทุกชิ้น: ใช้อนิเมชัน "In" ที่ผู้ใช้เคยใส่ให้ข้อความชิ้นใดก็ได้ในโปรเจกต์ ถ้าไม่มีใช้ keyframe
    ขยาย 0.85→1.0 + โผล่ 0→1 แทน (--anim keyframes|none)
  - ปรับสไตล์แทร็กซับของ CapCut ในที่เดิม: ย้ายขึ้นโซน A (y ≈ +0.80) ขนาด ~15 พื้นดำโปร่ง alpha ~0.6

เวลาในคอลัมน์ `เวลา` เขียนหยาบ ๆ เป็น m:ss ได้ สคริปต์จะจับคู่กับบรรทัดในไฟล์ subtitle (SRT) ที่เวลาเริ่มปัด
เป็นวินาทีเดียวกัน แล้วใช้เวลาจริงของบรรทัดนั้น ถ้าเขียนทศนิยม (m:ss.mmm) จะใช้ค่านั้นตรง ๆ

- ต้องปิด CapCut ก่อนรัน (สคริปต์หยุดเองถ้ายังเปิดอยู่)
- สำรอง draft_info.json ไว้ที่ <project>/backup_before_text/ ก่อนแก้
- รันซ้ำได้: ลบเฉพาะข้อความที่สคริปต์เคยใส่ (ดูจากชื่อ material ที่ขึ้นต้นด้วย "BizShorts-") แล้ววางใหม่
  ซับ เสียง ภาพ และของที่เพิ่มเองไม่ถูกลบ (ซับถูกปรับสไตล์เท่านั้น ปิดด้วย --keep-subtitle)

ใช้:  python3 build_ep3_text.py                               # ใส่จริงลงโปรเจกต์ 1021
      python3 build_ep3_text.py --dry-run --out <โฟลเดอร์>    # ทดสอบ ไม่แตะโปรเจกต์
      python3 build_ep3_text.py --list-fonts                  # ดูฟอนต์ไทยที่ CapCut แคชไว้
      python3 build_ep3_text.py --project <path> --shotlist <md> --subtitle <srt> --font Mali
"""
import argparse, glob, json, os, re, shutil, struct, subprocess, sys, time, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PROJECT = "/Users/donutsped/Movies/CapCut/User Data/Projects/com.lveditor.draft/1021"
FONT_CACHE = "/Users/donutsped/Movies/CapCut/User Data/Cache/effect"
US = 1_000_000
MARK_KW = "BizShorts-คำโปรย"
MARK_NUM = "BizShorts-ตัวเลข"

# ---- สไตล์ (หน่วยของ CapCut: ขนาดตัวอักษรตามช่อง size, ตำแหน่ง y: ครึ่งจอ = 1, บวก = ขึ้น) ----
SUB_Y, SUB_SIZE, SUB_BG_ALPHA, SUB_BG_RADIUS = 0.80, 15, 0.6, 0.15
KW_Y, KW_SIZE_MAX, KW_SIZE_MIN, KW_MAX_LINES = 0.40, 26, 16, 2
NUM_Y, NUM_SIZE_MAX, NUM_SIZE_MIN, NUM_MAX_LINES = -0.30, 24, 14, 2
NUM_COLOR = (1.0, 0.843, 0.0)          # #FFD700
NUM_MIN_S, NUM_MAX_S = 2.0, 3.5
KW_STROKE, NUM_STROKE = 0.06, 0.12     # border_width (ค่าใน content = ×0.75 ตามที่ CapCut เก็บ)
# ขนาดตัวอักษรของ CapCut 1 หน่วย ≈ 5.9 px ของ em บน canvas กว้าง 1080 (วัดจาก draft_cover.jpg ของ 1021:
# ขนาด 38 → em ≈ 225 px) · ข้อความกว้างได้ไม่เกิน LINE_FRAC ของจอ ที่เหลือเผื่อปุ่ม YouTube ด้านขวา
CANVAS_W, PX_PER_SIZE, LINE_FRAC = 1080, 5.9, 0.80
ANIM_IN_US, ANIM_SCALE_FROM = 250_000, 0.85   # อนิเมชันเข้า 0.25 วิ (ใช้ทั้ง resource ของ CapCut และ keyframe สำรอง)
# ลำดับฟอนต์คำโปรยที่ชอบ (ชื่อ family) — ลายมือไทยก่อน แล้วค่อย display แล้วค่อยฟอนต์ซับ
FONT_PREFERENCE = ["Mali", "Itim", "Charm", "Charmonman", "Pattaya", "Sriracha", "Srisakdi", "Kodchasan",
                   "Chonburi", "Kanit", "Prompt", "Mitr", "IBM Plex Sans Thai"]
NUM_FONT_PREFERENCE = ["Chonburi", "Kanit", "Prompt", "Mitr", "IBM Plex Sans Thai"]


def uid():
    return str(uuid.uuid4()).upper()


def us(sec):
    return int(round(sec * US))


# ---------------------------------------------------------------------------
# ฟอนต์: อ่าน name + cmap ของไฟล์ ttf/otf ในแคชของ CapCut เอง (ไม่พึ่ง fontTools)
# ---------------------------------------------------------------------------
def _font_tables(d):
    n = struct.unpack(">H", d[4:6])[0]
    return {struct.unpack(">4s", d[12 + 16 * i:16 + 16 * i])[0].decode("latin1"):
            struct.unpack(">II", d[20 + 16 * i:28 + 16 * i]) for i in range(n)}


def _font_family(d, t):
    off, _ = t["name"]
    _, count, str_off = struct.unpack(">HHH", d[off:off + 6])
    best = {}
    for i in range(count):
        pid, _, _, nid, ln, o = struct.unpack(">HHHHHH", d[off + 6 + 12 * i:off + 18 + 12 * i])
        raw = d[off + str_off + o:off + str_off + o + ln]
        try:
            s = raw.decode("utf-16-be") if pid in (0, 3) else raw.decode("latin1")
        except UnicodeDecodeError:
            continue
        best.setdefault(nid, s)
    return best.get(1) or best.get(4) or ""


def _font_has(d, t, cp):
    off, _ = t["cmap"]
    for i in range(struct.unpack(">H", d[off + 2:off + 4])[0]):
        sub = off + struct.unpack(">I", d[off + 8 + 8 * i:off + 12 + 8 * i])[0]
        fmt = struct.unpack(">H", d[sub:sub + 2])[0]
        if fmt == 4:
            seg2 = struct.unpack(">H", d[sub + 6:sub + 8])[0]
            ends = struct.unpack(">%dH" % (seg2 // 2), d[sub + 14:sub + 14 + seg2])
            starts = struct.unpack(">%dH" % (seg2 // 2), d[sub + 16 + seg2:sub + 16 + 2 * seg2])
            if any(s <= cp <= e and s != 0xFFFF for s, e in zip(starts, ends)):
                return True
        elif fmt == 12:
            for g in range(struct.unpack(">I", d[sub + 12:sub + 16])[0]):
                s, e, _ = struct.unpack(">III", d[sub + 16 + 12 * g:sub + 28 + 12 * g])
                if s <= cp <= e:
                    return True
    return False


def cached_thai_fonts():
    """คืน list ของ {family, path, resource_id} เฉพาะฟอนต์ที่มีตัวอักษรไทย (ก = U+0E01)"""
    out = []
    for p in glob.glob(os.path.join(FONT_CACHE, "*", "*", "*")):
        if not p.lower().endswith((".ttf", ".otf")):
            continue
        try:
            d = open(p, "rb").read()
            t = _font_tables(d)
            if "name" not in t or "cmap" not in t or not _font_has(d, t, 0x0E01):
                continue
            out.append({"family": _font_family(d, t), "path": p,
                        "resource_id": os.path.basename(os.path.dirname(os.path.dirname(p)))})
        except Exception:
            continue
    return out


class FontMetrics:
    """ความกว้างตัวอักษร (หน่วย em) จาก cmap + hmtx ของไฟล์ฟอนต์ ใช้ประมาณความกว้างข้อความที่ CapCut จะวาด"""

    def __init__(self, path):
        d = self.d = open(path, "rb").read()
        t = _font_tables(d)
        self.upm = struct.unpack(">H", d[t["head"][0] + 18:t["head"][0] + 20])[0]
        hh = t["hhea"][0]
        self.asc, self.desc = struct.unpack(">hh", d[hh + 4:hh + 8])
        n = struct.unpack(">H", d[hh + 34:hh + 36])[0]
        hm = t["hmtx"][0]
        self.adv = [struct.unpack(">H", d[hm + 4 * i:hm + 4 * i + 2])[0] for i in range(n)]
        self.sub4 = self.sub12 = None
        co = t["cmap"][0]
        for i in range(struct.unpack(">H", d[co + 2:co + 4])[0]):
            off = co + struct.unpack(">I", d[co + 8 + 8 * i:co + 12 + 8 * i])[0]
            fmt = struct.unpack(">H", d[off:off + 2])[0]
            if fmt == 4 and self.sub4 is None:
                self.sub4 = off
            elif fmt == 12 and self.sub12 is None:
                self.sub12 = off
        if self.sub4:
            s = self.sub4
            seg2 = struct.unpack(">H", d[s + 6:s + 8])[0]
            self.seg = seg2 // 2
            self.ends = struct.unpack(">%dH" % self.seg, d[s + 14:s + 14 + seg2])
            self.starts = struct.unpack(">%dH" % self.seg, d[s + 16 + seg2:s + 16 + 2 * seg2])
            self.deltas = struct.unpack(">%dh" % self.seg, d[s + 16 + 2 * seg2:s + 16 + 3 * seg2])
            self.ro_off = s + 16 + 3 * seg2
            self.ros = struct.unpack(">%dH" % self.seg, d[self.ro_off:self.ro_off + seg2])
        self.cache = {}

    def gid(self, cp):
        if cp in self.cache:
            return self.cache[cp]
        g = 0
        if self.sub4 and cp <= 0xFFFF:
            for i in range(self.seg):
                if self.starts[i] <= cp <= self.ends[i]:
                    if self.ros[i] == 0:
                        g = (cp + self.deltas[i]) & 0xFFFF
                    else:
                        a = self.ro_off + 2 * i + self.ros[i] + 2 * (cp - self.starts[i])
                        raw = struct.unpack(">H", self.d[a:a + 2])[0]
                        g = (raw + self.deltas[i]) & 0xFFFF if raw else 0
                    break
        if not g and self.sub12:
            s = self.sub12
            for k in range(struct.unpack(">I", self.d[s + 12:s + 16])[0]):
                a, b, sg = struct.unpack(">III", self.d[s + 16 + 12 * k:s + 28 + 12 * k])
                if a <= cp <= b:
                    g = sg + (cp - a)
                    break
        self.cache[cp] = g
        return g

    def width_em(self, text):
        return sum(self.adv[min(self.gid(ord(c)), len(self.adv) - 1)] for c in text) / self.upm


def thai_pieces(text):
    """ตัดข้อความเป็นชิ้นตามขอบคำไทยด้วย CFStringTokenizer ของ macOS (ICU) ถ้าใช้ไม่ได้ก็ตัดที่ช่องว่างแทน"""
    try:
        import ctypes
        CF = ctypes.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")

        class CFRange(ctypes.Structure):
            _fields_ = [("location", ctypes.c_long), ("length", ctypes.c_long)]
        CF.CFStringCreateWithBytes.restype = ctypes.c_void_p
        CF.CFStringCreateWithBytes.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_long, ctypes.c_uint32, ctypes.c_bool]
        CF.CFLocaleCreate.restype = ctypes.c_void_p
        CF.CFLocaleCreate.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        CF.CFStringTokenizerCreate.restype = ctypes.c_void_p
        CF.CFStringTokenizerCreate.argtypes = [ctypes.c_void_p, ctypes.c_void_p, CFRange, ctypes.c_ulong, ctypes.c_void_p]
        CF.CFStringTokenizerAdvanceToNextToken.restype = ctypes.c_ulong
        CF.CFStringTokenizerAdvanceToNextToken.argtypes = [ctypes.c_void_p]
        CF.CFStringTokenizerGetCurrentTokenRange.restype = CFRange
        CF.CFStringTokenizerGetCurrentTokenRange.argtypes = [ctypes.c_void_p]
        CF.CFRelease.argtypes = [ctypes.c_void_p]
        u = text.encode("utf-16-le")
        cs = CF.CFStringCreateWithBytes(None, u, len(u), 0x14000100, False)       # kCFStringEncodingUTF16LE
        lid = CF.CFStringCreateWithBytes(None, b"th_TH", 5, 0x08000100, False)   # UTF-8
        loc = CF.CFLocaleCreate(None, lid)
        tk = CF.CFStringTokenizerCreate(None, cs, CFRange(0, len(u) // 2), 4, loc)  # 4 = UnitWordBoundary
        out = []
        while CF.CFStringTokenizerAdvanceToNextToken(tk):
            r = CF.CFStringTokenizerGetCurrentTokenRange(tk)
            out.append(u[2 * r.location:2 * (r.location + r.length)].decode("utf-16-le"))
        for o in (tk, loc, lid, cs):
            CF.CFRelease(o)
        if "".join(out) == text:
            return out
    except Exception:
        pass
    return re.findall(r"\s+|\S+", text)


def _is_word(p):
    return bool(re.search(r"[\w]", p)) and p not in ("·", "ฯ", "ๆ", "ฯลฯ")


def _breaks(pieces):
    """ตำแหน่งที่ตัดบรรทัดได้ (ก่อนชิ้น i) พร้อมค่าปรับ: 0 ถ้าตัดที่ช่องว่าง, 1 ถ้าตัดกลางคำไทยติดกัน"""
    out = []
    for i in range(1, len(pieces)):
        if not _is_word(pieces[i]) or pieces[i - 1] in ('"', "“", "(", "'"):
            continue
        out.append((i, 0 if pieces[i - 1].isspace() else 1))
    return out


def _line(pieces):
    return "".join(pieces).strip()


def fit_text(text, fm, size_max, size_min, max_lines):
    """ลดขนาดทีละ 1 จาก size_max และตัดบรรทัดที่ขอบคำ (ชอบตัดที่ช่องว่างก่อน) ให้ทุกบรรทัดกว้างไม่เกิน
    LINE_FRAC ของจอ คืน (ข้อความที่ใส่ \\n แล้ว, ขนาด, จำนวนบรรทัด, พอดีไหม)"""
    max_px = CANVAS_W * LINE_FRAC
    pieces = thai_pieces(text.replace("\n", " "))
    if not pieces:
        return text, size_max, 1, True
    breaks = _breaks(pieces)
    penalty_px = 0.35 * CANVAS_W   # ยอมให้บรรทัดกว้างขึ้นเท่านี้เพื่อแลกกับการตัดที่ช่องว่างแทนกลางคำไทย
    line_px = 0.5 * CANVAS_W       # ค่าปรับต่อบรรทัดที่เพิ่ม: ถ้าบรรทัดเดียวพอดีก็ไม่ต้องตัด

    def candidates(k):
        if k == 1:
            yield [pieces], 0
            return
        import itertools
        for combo in itertools.combinations(breaks, k - 1):
            idx = [0] + [c[0] for c in combo] + [len(pieces)]
            yield [pieces[a:b] for a, b in zip(idx, idx[1:])], sum(c[1] for c in combo)

    def best_at(size):
        """ทางเลือกที่ดีที่สุด ณ ขนาดนี้: (penalty รวม, split) หรือ None"""
        px = size * PX_PER_SIZE
        best = None
        for k in range(1, max_lines + 1):
            for split, pen in candidates(k):
                widths = [fm.width_em(_line(l)) * px for l in split]
                score = max(widths) + pen * penalty_px + (k - 1) * line_px
                if max(widths) <= max_px and (best is None or score < best[0]):
                    best = (score, pen, split)
        return best

    first = None
    for size in range(size_max, size_min - 1, -1):
        b = best_at(size)
        if not b:
            continue
        if first is None:
            first = (size, b)
            if b[1] == 0:
                break
        elif b[1] == 0 and size >= first[0] - 4:   # ยอมเล็กลงไม่เกิน 4 ขนาด เพื่อให้ตัดที่ช่องว่างแทนกลางคำ
            first = (size, b)
            break
        elif size < first[0] - 4:
            break
    if first:
        size, (_, _, split) = first
        return "\n".join(_line(l) for l in split), size, len(split), True
    # ไม่พอดีแม้ขนาดเล็กสุด: ตัดแบบโลภที่ขนาดเล็กสุด แล้วให้ผู้ใช้ย่อคำใน shotlist
    px = size_min * PX_PER_SIZE
    ok_at = {i for i, _ in breaks}
    lines, cur = [], []
    for i, p in enumerate(pieces):
        if cur and i in ok_at and fm.width_em(_line(cur + [p])) * px > max_px:
            lines.append(cur); cur = []
        cur.append(p)
    lines.append(cur)
    return "\n".join(_line(l) for l in lines), size_min, len(lines), False


def pick_font(fonts, want, preference):
    def find(name):
        for f in fonts:
            if f["family"].lower().startswith(name.lower()):
                return f
    if want:
        f = find(want)
        if not f:
            sys.exit(f"ไม่พบฟอนต์ '{want}' ที่มีตัวอักษรไทยในแคช CapCut (ดู --list-fonts) "
                     "เลือกฟอนต์นั้นในหน้าต่างข้อความของ CapCut สักครั้งให้มันโหลดมาก่อน")
        return f
    for name in preference:
        f = find(name)
        if f:
            return f
    return fonts[0] if fonts else None


# ---------------------------------------------------------------------------
# อ่าน subtitle (SRT) และ shotlist (ตาราง markdown)
# ---------------------------------------------------------------------------
def parse_srt(path):
    cues = []
    for block in re.split(r"\n\s*\n", open(path, encoding="utf-8").read().strip()):
        lines = [l for l in block.strip().split("\n") if l.strip()]
        if len(lines) < 2:
            continue
        m = re.match(r"(\d+):(\d\d):(\d\d)[,.](\d{3})\s*-->\s*(\d+):(\d\d):(\d\d)[,.](\d{3})", lines[1])
        if not m:
            continue
        v = [int(x) for x in m.groups()]
        a = v[0] * 3600 + v[1] * 60 + v[2] + v[3] / 1000
        b = v[4] * 3600 + v[5] * 60 + v[6] + v[7] / 1000
        cues.append({"start": a, "end": b, "text": " ".join(lines[2:])})
    if not cues:
        sys.exit(f"อ่าน SRT ไม่ได้: {path}")
    return cues


def parse_clock(s):
    """'1:05' -> (65.0, exact=False), '1:05.366' -> (65.366, exact=True)"""
    m = re.match(r"^(\d+):(\d\d)(?:\.(\d+))?$", s.strip())
    if not m:
        return None
    sec = int(m.group(1)) * 60 + int(m.group(2))
    if m.group(3):
        return sec + float("0." + m.group(3)), True
    return float(sec), False


def parse_shotlist(path):
    rows, header = [], None
    for ln in open(path, encoding="utf-8"):
        ln = ln.strip()
        if not ln.startswith("|"):
            header = None if header and not rows else header
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if header is None:
            if "เวลา" in cells and "คำโปรย" in cells:
                header = cells
            continue
        if set(ln) <= set("|-: "):
            continue
        rec = dict(zip(header, cells))
        t = rec.get("เวลา", "")
        a, _, b = t.replace("—", "–").replace("-", "–").partition("–")
        pa, pb = parse_clock(a), parse_clock(b)
        if not pa:
            continue
        rows.append({"start": pa[0], "start_exact": pa[1], "end": pb[0] if pb else None,
                     "sub": rec.get("ซับ", ""), "kw": rec.get("คำโปรย", "").strip(),
                     "num": rec.get("ตัวเลขเน้น", "").strip()})
    if not rows:
        sys.exit(f"ไม่พบตารางที่มีคอลัมน์ เวลา/คำโปรย ใน {path}")
    return rows


def resolve_times(rows, cues):
    """เติม t0 (วินาทีจริง) ให้ทุกแถว โดยจับคู่กับบรรทัดซับที่เวลาเริ่มปัดเป็นวินาทีเดียวกัน"""
    for r in rows:
        if r["start_exact"]:
            r["t0"] = r["start"]
        else:
            hit = [c for c in cues if round(c["start"]) == r["start"]]
            if not hit:
                near = min(cues, key=lambda c: abs(c["start"] - r["start"]))
                hit = [near] if abs(near["start"] - r["start"]) <= 0.75 else []
            r["t0"] = hit[0]["start"] if hit else r["start"]
    if not rows[0]["start_exact"]:
        rows[0]["t0"] = 0.0          # คำโปรย hook ต้องอยู่ตั้งแต่เฟรมแรก เพราะเป็นภาพปก
    for i, r in enumerate(rows):
        r["t1"] = rows[i + 1]["t0"] if i + 1 < len(rows) else max(c["end"] for c in cues)
        r["cues"] = [c for c in cues if r["t0"] - 1e-6 <= c["start"] < r["t1"] - 1e-6]
        if r["t1"] <= r["t0"]:
            sys.exit(f"แถว {r['sub'][:30]!r}: เวลาเริ่ม {r['t0']} ไม่น้อยกว่าแถวถัดไป {r['t1']}")
    return rows


def number_start(r, piece):
    """หาบรรทัดซับในแถวที่พูดตัวเลข/ชื่อนั้น: ดูจาก token ที่มีตัวเลขก่อน แล้วค่อยคำแรก"""
    toks = [t for t in re.split(r"\s+", piece) if t]
    digit_toks = [t for t in toks if re.search(r"\d", t)]
    for cand in (digit_toks, toks[:1]):
        for c in r["cues"]:
            if any(t in c["text"] for t in cand):
                return c["start"]
    return r["t0"]


# ---------------------------------------------------------------------------
# JSON ของ CapCut: material ข้อความ + segment (ถอดแบบจากซับที่ CapCut สร้างในโปรเจกต์ 1021)
# ---------------------------------------------------------------------------
def text_content(text, size, color, stroke_w, font, bold=True):
    return json.dumps({
        "styles": [{
            "fill": {"content": {"solid": {"color": list(color)}, "render_type": "solid"}},
            "range": [0, len(text)],
            "strokes": [{"width": round(stroke_w * 0.75, 4), "mode": 0,
                         "content": {"solid": {"color": [0, 0, 0]}, "render_type": "solid"}}],
            "useLetterColor": True, "size": size, "bold": bold,
            "font": {"path": font["path"], "id": font["resource_id"]},
        }],
        "text": text,
    }, ensure_ascii=False)


def hex_color(rgb):
    return "#%02x%02x%02x" % tuple(int(round(c * 255)) for c in rgb)


def text_material(name, text, size, color, stroke_w, font, *, shadow=False, line_width=0.82):
    return {
        "recognize_task_id": "", "id": uid(), "name": name, "recognize_text": "", "recognize_model": "",
        "punc_model": "", "type": "text",
        "content": text_content(text, size, color, stroke_w, font),
        "base_content": "",
        "words": {"start_time": [], "end_time": [], "text": []},
        "current_words": {"start_time": [], "end_time": [], "text": []},
        "global_alpha": 1.0, "combo_info": {"text_templates": []},
        "caption_template_info": {"resource_id": "", "third_resource_id": "", "resource_name": "", "category_id": "",
                                  "category_name": "", "effect_id": "", "request_id": "", "path": "", "is_new": False,
                                  "source_platform": 0},
        "layer_weight": 1, "letter_spacing": 0.0, "text_curve": None, "text_loop_on_path": False,
        "offset_on_path": 0.0, "enable_path_typesetting": False, "text_exceeds_path_process_type": 0,
        "text_typesetting_paths": None, "text_typesetting_paths_file": "", "text_typesetting_path_index": 0,
        "line_spacing": 0.02,
        "has_shadow": shadow, "shadow_color": "#000000", "shadow_alpha": 0.8, "shadow_smoothing": 0.45,
        "shadow_distance": 5.0, "shadow_point": {"x": 0.6363961030678928, "y": -0.6363961030678927},
        "shadow_angle": -45.0, "shadow_thickness_projection_enable": False,
        "shadow_thickness_projection_angle": 0.0, "shadow_thickness_projection_distance": 0.0,
        "border_alpha": 1.0, "border_color": "#000000", "border_width": stroke_w, "border_mode": 0,
        "style_name": "", "text_color": hex_color(color), "text_alpha": 1.0,
        "font_name": "", "font_title": "none", "font_size": float(size), "font_path": font["path"], "font_id": "",
        "font_resource_id": font["resource_id"], "initial_scale": 1.0, "font_url": "",
        "typesetting": 0, "alignment": 1, "line_feed": 1, "use_effect_default_color": True, "is_rich_text": False,
        "shape_clip_x": False, "shape_clip_y": False, "ktv_color": "", "text_to_audio_ids": [],
        "bold_width": 0.00800000037997961, "italic_degree": 0, "underline": False, "underline_width": 0.05,
        "underline_offset": 0.22, "sub_type": 0, "check_flag": 15, "text_size": 30,
        "font_category_name": "", "font_source_platform": 1, "font_third_resource_id": "", "font_category_id": "",
        "add_type": 0, "operation_type": 0, "recognize_type": 0,
        "fonts": [{"id": uid(), "resource_id": font["resource_id"], "third_resource_id": "", "category_id": "",
                   "category_name": "", "source_platform": 1, "path": font["path"],
                   "effect_id": font["resource_id"], "title": font["family"], "team_id": "", "file_uri": "",
                   "request_id": ""}],
        "background_color": "#000000", "background_alpha": 0.0, "background_style": 0,
        "background_round_radius": 0.0, "background_width": 0.14, "background_height": 0.14,
        "background_vertical_offset": 0.0, "background_horizontal_offset": 0.0, "background_fill": "",
        "single_char_bg_enable": False, "single_char_bg_color": "", "single_char_bg_alpha": 1.0,
        "single_char_bg_round_radius": 0.3, "single_char_bg_width": 0.0, "single_char_bg_height": 0.0,
        "single_char_bg_vertical_offset": 0.0, "single_char_bg_horizontal_offset": 0.0,
        "font_team_id": "", "tts_auto_update": False, "text_preset_resource_id": "", "group_id": "",
        "preset_id": "", "preset_name": "", "preset_category": "", "preset_category_id": "", "preset_index": 0,
        "preset_has_set_alignment": False, "force_apply_line_max_width": True, "language": "",
        "relevance_segment": [], "original_size": [], "fixed_width": -1.0, "fixed_height": -1.0,
        "autoAdaptCanvasEnabled": False, "line_max_width": line_width, "oneline_cutoff": False,
        "cutoff_postfix": "", "subtitle_template_original_fontsize": 0.0, "subtitle_keywords": None,
        "inner_padding": -1.0, "multi_language_current": "none", "source_from": "", "is_lyric_effect": False,
        "lyric_group_id": "",
        "lyrics_template": {"resource_id": "", "resource_name": "", "panel": "", "effect_id": "", "path": "",
                            "category_id": "", "category_name": "", "request_id": ""},
        "is_batch_replace": False, "is_words_linear": False, "ssml_content": "", "subtitle_keywords_config": None,
        "sub_template_id": -1, "translate_original_text": "", "adjust_params": [],
    }


def find_in_animation(info):
    """หาอนิเมชันเข้า (type "in") ที่ผู้ใช้เคยใส่ให้ข้อความชิ้นใดก็ได้ในโปรเจกต์ เพื่อเอามาใช้ซ้ำทุกชิ้น"""
    for a in info["materials"].get("material_animations", []):
        for an in a.get("animations", []):
            if an.get("type") == "in" and an.get("resource_id"):
                return an
    return None


def animation_material(template=None):
    anims = []
    if template:
        an = dict(template)
        an["duration"] = ANIM_IN_US
        an["start"] = 0
        anims.append(an)
    return {"id": uid(), "type": "sticker_animation", "animations": anims, "multi_language_current": "none"}


def keyframe(t_us, value):
    return {"curveType": "Line", "graphID": "", "id": uid(), "left_control": {"x": 0.0, "y": 0.0},
            "right_control": {"x": 0.0, "y": 0.0}, "time_offset": t_us, "values": [value]}


def enter_keyframes():
    """สำรอง: ขยาย 0.85→1.0 และโผล่ 0→1 ใน 0.25 วิ (แบบเดียวกับ KFTypeScaleX ของคลิปวิดีโอใน build_ep3_capcut.py)"""
    out = []
    for prop, v0, v1 in (("KFTypeScaleX", ANIM_SCALE_FROM, 1.0), ("KFTypeScaleY", ANIM_SCALE_FROM, 1.0),
                         ("KFTypeAlpha", 0.0, 1.0)):
        out.append({"id": uid(), "keyframe_list": [keyframe(0, v0), keyframe(ANIM_IN_US, v1)],
                    "material_id": "", "property_type": prop})
    return out


def text_segment(material_id, anim_id, start, end, y, render_index, track_render_index, keyframes=None):
    return {
        "id": uid(), "source_timerange": None,
        "target_timerange": {"start": us(start), "duration": us(end) - us(start)},
        "render_timerange": {"start": 0, "duration": 0},
        "desc": "", "state": 0, "speed": 1.0, "is_loop": False, "is_tone_modify": False, "reverse": False,
        "intensifies_audio": False, "cartoon": False, "volume": 1.0, "last_nonzero_volume": 1.0,
        "clip": {"scale": {"x": 1.0, "y": 1.0}, "rotation": 0.0, "rotation3d": [],
                 "transform": {"x": 0.0, "y": float(y)}, "flip": {"vertical": False, "horizontal": False},
                 "alpha": 1.0},
        "uniform_scale": {"on": True, "value": 1.0},
        "material_id": material_id, "extra_material_refs": [anim_id],
        "render_index": render_index, "keyframe_refs": [], "enable_lut": False, "enable_adjust": False,
        "enable_hsl": False, "visible": True, "group_id": "", "enable_color_curves": True,
        "enable_hsl_curves": True, "track_render_index": track_render_index, "hdr_settings": None,
        "hdr_vivid_settings": None, "enable_color_wheels": True, "track_attribute": 0, "is_placeholder": False,
        "template_id": "", "enable_smart_color_adjust": False, "template_scene": "default",
        "common_keyframes": keyframes or [], "caption_info": None,
        "responsive_layout": {"enable": False, "target_follow": "", "size_layout": 0,
                              "horizontal_pos_layout": 0, "vertical_pos_layout": 0},
        "enable_color_match_adjust": False, "enable_color_correct_adjust": False, "enable_adjust_mask": False,
        "raw_segment_id": "", "lyric_keyframes": None, "enable_video_mask": True,
        "digital_human_template_group_id": "", "color_correct_alg_result": "", "source": "segmentsourcenormal",
        "enable_mask_stroke": False, "enable_mask_shadow": False, "enable_color_adjust_pro": False,
        "segment_color_tag": "",
    }


def text_track(name):
    return {"id": uid(), "type": "text", "flag": 0, "attribute": 0, "name": name,
            "is_default_name": False, "segments": []}


# ---------------------------------------------------------------------------
def strip_previous(info):
    """ลบ material/segment/track ที่สคริปต์นี้เคยใส่ (ชื่อขึ้นต้น BizShorts-)"""
    mats = info["materials"]
    ours = {m["id"] for m in mats["texts"] if str(m.get("name", "")).startswith("BizShorts-")}
    dead = set()
    for t in info["tracks"]:
        if t["type"] != "text":
            continue
        keep = []
        for s in t["segments"]:
            if s["material_id"] in ours:
                dead.update(s["extra_material_refs"])
            else:
                keep.append(s)
        t["segments"] = keep
    info["tracks"] = [t for t in info["tracks"]
                      if not (t["type"] == "text" and not t["segments"] and str(t.get("name", "")).startswith("BizShorts-"))]
    mats["texts"] = [m for m in mats["texts"] if m["id"] not in ours]
    mats["material_animations"] = [m for m in mats["material_animations"] if m["id"] not in dead]
    return len(ours)


def restyle_subtitles(info):
    """ย้ายซับ auto-caption ขึ้นโซน A ลดขนาด ลดพื้นดำ (แก้ในที่ ไม่สร้างใหม่)"""
    mats = info["materials"]
    subs = {m["id"] for m in mats["texts"] if m.get("type") == "subtitle"}
    for m in mats["texts"]:
        if m["id"] not in subs:
            continue
        m["font_size"] = float(SUB_SIZE)
        m["background_alpha"] = SUB_BG_ALPHA
        m["background_round_radius"] = SUB_BG_RADIUS
        try:
            c = json.loads(m["content"])
            for st in c.get("styles", []):
                st["size"] = SUB_SIZE
            m["content"] = json.dumps(c, ensure_ascii=False)
        except (ValueError, TypeError):
            pass
    n = 0
    for t in info["tracks"]:
        if t["type"] != "text":
            continue
        for s in t["segments"]:
            if s["material_id"] in subs and s.get("clip"):
                s["clip"]["transform"]["y"] = SUB_Y
                n += 1
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default=DEFAULT_PROJECT)
    ap.add_argument("--shotlist", default=os.path.join(HERE, "shotlist_full.md"))
    ap.add_argument("--subtitle", default=os.path.join(HERE, "subtitle"))
    ap.add_argument("--dry-run", action="store_true", help="ไม่แตะโปรเจกต์ เขียนผลไปที่ --out")
    ap.add_argument("--out", help="โฟลเดอร์ปลายทาง (ค่าเริ่มต้น = โปรเจกต์)")
    ap.add_argument("--font", help="ชื่อฟอนต์คำโปรย (family) ที่มีในแคช CapCut เช่น Mali, Chonburi")
    ap.add_argument("--num-font", help="ชื่อฟอนต์ตัวเลขเน้น")
    ap.add_argument("--keep-subtitle", action="store_true", help="ไม่ปรับสไตล์แทร็กซับ")
    ap.add_argument("--anim", choices=["auto", "keyframes", "none"], default="auto",
                    help="auto = ใช้อนิเมชันเข้าที่ผู้ใช้เคยใส่ในโปรเจกต์ ถ้าไม่มีใช้ keyframe ขยาย+โผล่")
    ap.add_argument("--list-fonts", action="store_true")
    a = ap.parse_args()

    fonts = cached_thai_fonts()
    if a.list_fonts:
        for f in fonts:
            print(f"{f['family']:30s} {f['resource_id']:22s} {f['path']}")
        return
    if not fonts:
        sys.exit("ไม่พบฟอนต์ที่มีตัวอักษรไทยในแคช CapCut เลย เปิด CapCut แล้วเลือกฟอนต์ไทยในหน้าต่างข้อความสักครั้ง")
    kw_font = pick_font(fonts, a.font, FONT_PREFERENCE)
    num_font = pick_font(fonts, a.num_font, NUM_FONT_PREFERENCE)
    out = a.out or a.project
    if not a.dry_run and subprocess.run(["pgrep", "-x", "CapCut"], capture_output=True).returncode == 0:
        sys.exit("CapCut ยังเปิดอยู่ กรุณาปิด CapCut (Cmd+Q) ก่อน แล้วรันใหม่")

    cues = parse_srt(a.subtitle)
    rows = resolve_times(parse_shotlist(a.shotlist), cues)
    kw_fm, num_fm = FontMetrics(kw_font["path"]), FontMetrics(num_font["path"])

    info = json.load(open(os.path.join(a.project, "draft_info.json"), encoding="utf-8"))
    total = info.get("duration") or us(max(c["end"] for c in cues))
    anim_tpl = find_in_animation(info) if a.anim == "auto" else None
    use_kf = a.anim == "keyframes" or (a.anim == "auto" and anim_tpl is None)
    removed = strip_previous(info)
    mats = info["materials"]

    def add(track, name, text, fm, size_max, size_min, max_lines, color, stroke, font, t0, t1, y, ri, tri, shadow):
        fitted, size, nlines, ok = fit_text(text, fm, size_max, size_min, max_lines)
        if not ok:
            print(f"  เตือน: {text!r} กว้างเกินจอแม้ขนาด {size_min} ({nlines} บรรทัด) ย่อคำใน shotlist")
        elif nlines > max_lines:
            print(f"  เตือน: {text!r} ต้องใช้ {nlines} บรรทัด")
        m = text_material(name, fitted, size, color, stroke, font, shadow=shadow, line_width=LINE_FRAC)
        an = animation_material(anim_tpl)
        mats["texts"].append(m); mats["material_animations"].append(an)
        seg = text_segment(m["id"], an["id"], t0, t1, y, ri, tri, enter_keyframes() if use_kf else None)
        track["segments"].append(seg)
        return fitted, size

    # 1) คำโปรย: ต่อเนื่องจากต้นแถวถึงต้นแถวถัดไป
    kw_track, kw_log = text_track(MARK_KW), []
    for i, r in enumerate(rows):
        if not r["kw"] or r["kw"] in ("-", "—"):
            continue
        end = min(r["t1"], total / US)
        kw_log.append(add(kw_track, MARK_KW, r["kw"], kw_fm, KW_SIZE_MAX, KW_SIZE_MIN, KW_MAX_LINES,
                          (1.0, 1.0, 1.0), KW_STROKE, kw_font, r["t0"], end, KW_Y, 15000 + i, 2, True))

    # 2) ตัวเลขเน้น: เริ่มตอนบรรทัดซับที่พูดถึง นาน 2–3.5 วิ ไม่ทับชิ้นถัดไป
    pieces = []
    for r in rows:
        for piece in [p.strip() for p in r["num"].split(" / ") if p.strip()]:
            pieces.append((number_start(r, piece), piece))
    pieces.sort()
    num_track, num_log = text_track(MARK_NUM), []
    for i, (t0, piece) in enumerate(pieces):
        nxt = pieces[i + 1][0] if i + 1 < len(pieces) else total / US
        end = min(t0 + NUM_MAX_S, nxt, total / US)
        if end - t0 < NUM_MIN_S:
            end = min(t0 + NUM_MIN_S, nxt, total / US)
        if end <= t0:
            print(f"  ข้าม: ตัวเลขเน้น {piece!r} ที่ {t0:.2f}s ไม่มีที่ว่าง")
            continue
        num_log.append((t0, add(num_track, MARK_NUM, piece, num_fm, NUM_SIZE_MAX, NUM_SIZE_MIN, NUM_MAX_LINES,
                                NUM_COLOR, NUM_STROKE, num_font, t0, end, NUM_Y, 16000 + i, 3, False)))

    # 3) ซับ
    moved = 0 if a.keep_subtitle else restyle_subtitles(info)

    # วางแทร็กใหม่ถัดจากแทร็กข้อความเดิม (ถ้าไม่มี ก็ต่อท้ายวิดีโอ)
    idx = max([i for i, t in enumerate(info["tracks"]) if t["type"] in ("video", "text")] or [-1])
    info["tracks"].insert(idx + 1, kw_track)
    info["tracks"].insert(idx + 2, num_track)
    info["update_time"] = int(time.time() * US)

    # 4) เขียนไฟล์
    os.makedirs(out, exist_ok=True)
    if not a.dry_run:
        bk = os.path.join(a.project, "backup_before_text")
        os.makedirs(bk, exist_ok=True)
        now = int(time.time())
        for f in ("draft_info.json", "draft_meta_info.json"):
            src = os.path.join(a.project, f)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(bk, f"{f}.{now}.bak"))
        print("สำรองไฟล์เดิมไว้ที่", bk)
        meta_p = os.path.join(a.project, "draft_meta_info.json")
        if os.path.exists(meta_p):
            meta = json.load(open(meta_p, encoding="utf-8"))
            meta["tm_draft_modified"] = int(time.time() * US)
            with open(meta_p, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False)
    with open(os.path.join(out, "draft_info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False)

    anim_desc = ("อนิเมชันเข้าของ CapCut: " + (anim_tpl.get("name") or anim_tpl["resource_id"])) if anim_tpl else \
        ("keyframe ขยาย+โผล่ 0.25 วิ" if use_kf else "ไม่มี")
    print(f"ฟอนต์คำโปรย: {kw_font['family']} · ฟอนต์ตัวเลข: {num_font['family']} · อนิเมชัน: {anim_desc}")
    print(f"ลบของเดิม {removed} ชิ้น · คำโปรย {len(kw_track['segments'])} ชิ้น · ตัวเลขเน้น "
          f"{len(num_track['segments'])} ชิ้น · ปรับซับ {moved} ชิ้น -> {out}")
    if a.dry_run:
        for s, (fitted, size) in zip(kw_track["segments"], kw_log):
            t = s["target_timerange"]
            print(f"  คำโปรย {t['start'] / US:7.3f}–{(t['start'] + t['duration']) / US:7.3f} ขนาด {size:2d}  "
                  + fitted.replace("\n", " ⏎ "))
        for s, (t0, (fitted, size)) in zip(num_track["segments"], num_log):
            t = s["target_timerange"]
            print(f"  ตัวเลข {t['start'] / US:7.3f}–{(t['start'] + t['duration']) / US:7.3f} ขนาด {size:2d}  "
                  + fitted.replace("\n", " ⏎ "))


if __name__ == "__main__":
    main()
