#!/usr/bin/env python3
"""ลบคลิปและไฟล์ประกอบทั้งหมดที่สคริปต์เคยใส่ไว้ออกจากโปรเจกต์ CapCut 1021 แล้วลบโฟลเดอร์ broll/

- ต้องปิด CapCut ก่อนรัน
- ลบเฉพาะคลิป/รายการใน media library ที่ชี้ไปโฟลเดอร์ broll/ (ซับ เสียง และของอื่นไม่ถูกแตะ)
- สำรอง draft ก่อนแก้ไว้ที่ <project>/backup_before_broll/
"""
import json, os, shutil, subprocess, sys, time

PROJECT = "/Users/donutsped/Movies/CapCut/User Data/Projects/com.lveditor.draft/1021"
BROLL = "/Users/donutsped/code/start/BizShorts/ep3_amd/broll"

if subprocess.run(["pgrep", "-x", "CapCut"], capture_output=True).returncode == 0:
    sys.exit("CapCut ยังเปิดอยู่ กรุณาปิด CapCut (Cmd+Q) ก่อน แล้วรันใหม่")

info = json.load(open(os.path.join(PROJECT, "draft_info.json")))
meta = json.load(open(os.path.join(PROJECT, "draft_meta_info.json")))
mats = info["materials"]

ours = {m["id"] for m in mats["videos"] if m.get("path", "").startswith(BROLL)}
dead_refs, removed = set(), 0
for t in info["tracks"]:
    if t["type"] != "video":
        continue
    keep = []
    for s in t["segments"]:
        if s["material_id"] in ours:
            dead_refs.update(s["extra_material_refs"]); removed += 1
        else:
            keep.append(s)
    t["segments"] = keep
first_video = next(t for t in info["tracks"] if t["type"] == "video")
info["tracks"] = [t for t in info["tracks"] if not (t["type"] == "video" and t is not first_video and not t["segments"])]
mats["videos"] = [m for m in mats["videos"] if m["id"] not in ours]
for k in ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "vocal_separations"):
    mats[k] = [m for m in mats[k] if m["id"] not in dead_refs]
lib = next(g for g in meta["draft_materials"] if g["type"] == 0)
before = len(lib["value"])
lib["value"] = [m for m in lib["value"] if not m["file_Path"].startswith(BROLL)]
info["update_time"] = int(time.time() * 1_000_000)
meta["tm_draft_modified"] = int(time.time() * 1_000_000)

bk = os.path.join(PROJECT, "backup_before_broll"); os.makedirs(bk, exist_ok=True)
now = int(time.time())
for f in ("draft_info.json", "draft_meta_info.json"):
    shutil.copy2(os.path.join(PROJECT, f), os.path.join(bk, f"{f}.{now}.bak"))
with open(os.path.join(PROJECT, "draft_info.json"), "w") as f:
    json.dump(info, f, ensure_ascii=False)
with open(os.path.join(PROJECT, "draft_meta_info.json"), "w") as f:
    json.dump(meta, f, ensure_ascii=False)
print(f"ลบคลิปออกจากไทม์ไลน์ {removed} ชิ้น · ลบออกจาก media library {before - len(lib['value'])} รายการ")
print("แทร็กที่เหลือ:", [(t["type"], len(t["segments"])) for t in info["tracks"]])

if os.path.isdir(BROLL):
    shutil.rmtree(BROLL)
    print("ลบโฟลเดอร์ไฟล์ต้นฉบับแล้ว:", BROLL)
