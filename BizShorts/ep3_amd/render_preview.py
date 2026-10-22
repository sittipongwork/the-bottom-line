#!/usr/bin/env python3
"""เรนเดอร์พรีวิว MP4 ช่วงสั้น ๆ ของ BizShorts ด้วย ffmpeg จากสเปกเดียวกับโปรเจกต์ CapCut

ใช้เช็กว่าเลเยอร์ข้อความ (ซับ คำโปรย ตัวเลขเน้น) ที่ build_ep3_text.py ใส่ใน CapCut มีขนาด/ตำแหน่งถูกต้องจริง
โดยไม่ต้อง export จาก CapCut · พื้นหลังเป็นคลิปวิดีโอตาม SHOTS ด้านล่าง (ไม่ใช้ภาพนิ่งต่อกัน)

ขั้นตอน: อ่านข้อความจาก draft_info.json → render_text_png.swift วาดเป็น PNG โปร่งใสเต็มเฟรม (CoreText จัดรูปอักษรไทย
ถูกต้อง ffmpeg ของ brew ไม่มี drawtext) → ffmpeg ครอปคลิปพื้นหลังเป็น 9:16 ต่อกัน แล้ว overlay PNG ตามเวลา พร้อมอนิเมชันเข้า
(ขยาย 0.85→1 + โผล่ 0→1 ใน 0.25 วิ เหมือน keyframe ที่ใส่ใน CapCut) + เสียง TTS

ใช้:  python3 render_preview.py --end 11.1 --out preview_0-11s.mp4
ต้องมี ffmpeg (brew install ffmpeg) และ swift (Xcode)
"""
import argparse, json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = "/Users/donutsped/Movies/CapCut/User Data/Projects/com.lveditor.draft/1021"
BROLL = os.path.join(HERE, "broll")
AUDIO = "/Users/donutsped/Desktop/BizShorts_ep3_10thing.mp3"
W, H, FPS = 1080, 1920, 30
PX_PER_SIZE = 5.9        # ขนาดตัวอักษร CapCut 1 หน่วย ≈ 5.9 px em บนจอกว้าง 1080 (ดู capcut-style.md §5)
DARKEN = 0.30            # ชั้นดำโปร่งทับพื้นหลังให้ตัวหนังสือขาวอ่านออก
ANIM = 0.25

# พื้นหลัง: (ไฟล์ใน broll/, เริ่มในไทม์ไลน์, จบ, เริ่มในไฟล์ต้นฉบับ, ครอป (w,h,x,y) ในพิกเซลต้นฉบับ หรือ None = ครอปกลางเต็มจอ)
SHOTS = [
    # ชิป Ryzen 9800X3D บนแท่น พื้นน้ำเงิน (Geekerwan CC BY 3.0) ช่วงที่ไม่มีตัวหนังสือในภาพ
    ("commons_amd_ryzen_9800x3d_Geekerwan_CC-BY3.webm", 0.0, 3.366, 18.6, None),
    # มือถือชิป (Pexels)
    ("pexels_12611453_hand_holding_processor.mp4", 3.366, 5.766, 0.5, None),
    # เมนบอร์ดแนวตั้ง (Pexels)
    ("pexels_6755168_motherboard_vertical.mp4", 5.766, 7.3, 2.0, None),
    # Lisa Su คนเดียวกลางเฟรม (Geekerwan CC BY 3.0) ครอปตัดซับฝังด้านล่างออก (สูง 620 จาก 720)
    ("commons_lisa_su_interview_Geekerwan_CC-BY3_720p.webm", 7.3, 11.1, 134.0, (349, 620, 590, 0)),
]


def load_texts(end):
    info = json.load(open(os.path.join(PROJECT, "draft_info.json"), encoding="utf-8"))
    byid = {t["id"]: t for t in info["materials"]["texts"]}
    out = []
    for tr in info["tracks"]:
        if tr["type"] != "text":
            continue
        for s in tr["segments"]:
            t0 = s["target_timerange"]["start"] / 1e6
            t1 = t0 + s["target_timerange"]["duration"] / 1e6
            if t0 >= end:
                continue
            m = byid[s["material_id"]]
            c = json.loads(m["content"])
            st = c["styles"][0]
            out.append({
                "text": c["text"], "t0": round(t0, 3), "t1": round(min(t1, end), 3), "size": st["size"],
                "color": st["fill"]["content"]["solid"]["color"], "stroke": m["border_width"],
                "font": st["font"]["path"], "y": s["clip"]["transform"]["y"],
                "bg_alpha": m["background_alpha"] if m.get("type") == "subtitle" else 0.0,
                "max_width": m.get("line_max_width") or 0.82,
                "anim": bool(s["common_keyframes"]), "order": (s["render_index"], t0),
            })
    return sorted(out, key=lambda x: x["order"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--end", type=float, default=11.1)
    ap.add_argument("--out", default=os.path.join(HERE, "preview_0-11s.mp4"))
    ap.add_argument("--no-text", action="store_true")
    a = ap.parse_args()
    shots = [s for s in SHOTS if s[1] < a.end]
    for fn, *_ in shots:
        if not os.path.exists(os.path.join(BROLL, fn)):
            sys.exit(f"ไม่พบ {fn} ใน {BROLL}")
    tmp = tempfile.mkdtemp(prefix="bizshorts_preview_")

    # 1) ข้อความ → PNG
    texts = [] if a.no_text else load_texts(a.end)
    if texts:
        spec = {"width": W, "height": H, "px_per_size": PX_PER_SIZE, "texts": texts}
        json.dump(spec, open(os.path.join(tmp, "spec.json"), "w", encoding="utf-8"), ensure_ascii=False)
        r = subprocess.run(["swift", os.path.join(HERE, "render_text_png.swift"), os.path.join(tmp, "spec.json"), tmp],
                           capture_output=True, text=True)
        if r.returncode:
            sys.exit("swift ล้มเหลว:\n" + r.stderr[-3000:])
        print(r.stdout)

    # 2) พื้นหลัง: ครอป 9:16 ต่อกัน
    inputs, chains, concat = [], [], []
    for i, (fn, t0, t1, src, crop) in enumerate(shots):
        dur = round(min(t1, a.end) - t0, 3)
        inputs += ["-ss", f"{src:.3f}", "-t", f"{dur + 0.5:.3f}", "-i", os.path.join(BROLL, fn)]
        pre = f"crop={crop[0]}:{crop[1]}:{crop[2]}:{crop[3]}," if crop else ""
        chains.append(f"[{i}:v]{pre}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                      f"fps={FPS},setsar=1,format=yuv420p,"
                      f"drawbox=x=0:y=0:w={W}:h={H}:color=black@{DARKEN}:t=fill,"
                      f"trim=duration={dur:.3f},setpts=PTS-STARTPTS[v{i}]")
        concat.append(f"[v{i}]")
    n_shots = len(shots)
    graph = ";".join(chains) + ";" + "".join(concat) + f"concat=n={n_shots}:v=1:a=0[bg]"
    last = "bg"

    # 3) ซ้อนข้อความ: PNG วนซ้ำเป็นวิดีโอ เลื่อนเวลาไปที่ t0 ใส่ขยาย+โผล่ 0.25 วิ แล้ว overlay ช่วง t0–t1
    for i, t in enumerate(texts):
        idx = n_shots + 1 + i                      # input: shots..., audio, png...
        dur = t["t1"] - t["t0"]
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", os.path.join(tmp, f"text_{i}.png")]
        anim = ""
        if t["anim"]:
            anim = (f"scale=w='iw*(0.85+0.15*min(1,t/{ANIM}))':h='ih*(0.85+0.15*min(1,t/{ANIM}))':eval=frame,"
                    f"fade=t=in:st=0:d={ANIM}:alpha=1,")
        graph += (f";[{idx}:v]format=rgba,{anim}setpts=PTS+{t['t0']:.3f}/TB[p{i}]"
                  f";[{last}][p{i}]overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2:"
                  f"enable='between(t,{t['t0']:.3f},{t['t1']:.3f})':eof_action=pass[o{i}]")
        last = f"o{i}"

    cmd = ["ffmpeg", "-y", *inputs[: 6 * n_shots], "-ss", "0", "-t", f"{a.end:.3f}", "-i", AUDIO,
           *inputs[6 * n_shots:], "-filter_complex", graph, "-map", f"[{last}]", "-map", f"{n_shots}:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "160k", "-t", f"{a.end:.3f}", a.out]
    open(os.path.join(tmp, "cmd.txt"), "w").write(" ".join(cmd) + "\n\n" + graph)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-4000:] + f"\n(คำสั่งเต็มอยู่ที่ {tmp}/cmd.txt)")
    print("เขียนแล้ว:", a.out, "· ไฟล์ชั่วคราว:", tmp)


if __name__ == "__main__":
    main()
