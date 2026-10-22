#!/usr/bin/env python3
"""ใส่ภาพ/คลิปประกอบ 10 วินาทีแรกของ EP3 ลงโปรเจกต์ CapCut 1021

ต้องปิด CapCut ก่อนรัน (สคริปต์จะหยุดเองถ้า CapCut ยังเปิดอยู่)
สำรอง draft_info.json และ draft_meta_info.json ไว้ที่ <project>/backup_before_broll/ ก่อนแก้ทุกครั้ง

ใช้:  python3 import_broll_to_capcut.py            # ใส่จริง
      python3 import_broll_to_capcut.py --dry-run  # เขียนผลลัพธ์ลงโฟลเดอร์ทดสอบ ไม่แตะโปรเจกต์
"""
import json, os, shutil, subprocess, sys, time, uuid

PROJECT = "/Users/donutsped/Movies/CapCut/User Data/Projects/com.lveditor.draft/1021"
BROLL = "/Users/donutsped/code/start/BizShorts/ep3_amd/broll"
DRY = "--dry-run" in sys.argv
OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else PROJECT

US = 1_000_000  # microseconds
PHOTO_DURATION = 10_800_000_000  # ค่าที่ CapCut ใช้กับภาพนิ่ง (3 ชม.)

# ไฟล์ทั้งหมดที่จะเพิ่มเข้า media library ของโปรเจกต์: (ชื่อไฟล์, ชนิด, กว้าง, สูง, ความยาว us)
LIBRARY = [
    ("01_amd_ryzen9_7900x_CristoCalis_CC-BY-SA4.jpg", "photo", 3068, 3068, 0),
    ("01b_amd_ryzen5_7600_Smial_FAL.jpg", "photo", 4888, 4888, 0),
    ("01c_amd_logo_publicdomain.png", "photo", 1920, 458, 0),
    ("02_amd_hq_santaclara_Coolcaesar_CC-BY-SA4.jpg", "photo", 4312, 3188, 0),
    ("03_intel_logo_2023_publicdomain.png", "photo", 1920, 745, 0),
    ("03b_intel_hq_2023_Coolcaesar_CC-BY-SA4.jpg", "photo", 4863, 3249, 0),
    ("04_lisa_su_sxsw2024_Fuzheado_CC-BY4_upright.jpg", "photo", 3072, 4608, 0),
    ("04b_lisa_su_ornl2019_GenevieveMartin_CC-BY2.jpg", "photo", 3000, 2000, 0),
    ("pexels_6755168_motherboard_vertical.mp4", "video", 1080, 1920, 23_920_000),
    ("pexels_35977437_circuit_processor.mp4", "video", 1920, 1080, 20_875_000),
    ("pexels_7140928_cpu_closeup.mp4", "video", 3840, 2160, 9_375_000),
]

# จังหวะตามไฟล์ subtitle (วินาที)
T1, T2, T3, T4, T5 = 0.0, 3.366, 5.766, 7.300, 11.100

# แทร็กหลัก (ชั้นล่าง): (ไฟล์, เริ่ม, จบ, scale, x, y, volume)
MAIN = [
    ("pexels_6755168_motherboard_vertical.mp4", T1, T2, 1.0, 0.0, 0.0, 0.0),   # พื้นหลังชิป 0-3.4 วิ ปิดเสียง
    ("02_amd_hq_santaclara_Coolcaesar_CC-BY-SA4.jpg", T2, T3, 2.4, -0.65, 0.0, 1.0),  # ตึก AMD ขยายเต็มจอ เลื่อนให้เห็นป้าย AMD ขวามือ
    ("03b_intel_hq_2023_Coolcaesar_CC-BY-SA4.jpg", T3, T4, 2.66, 0.0, 0.0, 1.0),  # ตึก Intel เต็มจอ
    ("04_lisa_su_sxsw2024_Fuzheado_CC-BY4_upright.jpg", T4, T5, 1.2, 0.0, 0.0, 1.0),  # Lisa Su
]
# แทร็กซ้อน (ชั้นบน)
OVERLAY = [
    ("01_amd_ryzen9_7900x_CristoCalis_CC-BY-SA4.jpg", T1, T2, 0.9, 0.0, 0.0, 1.0),  # ชิป Ryzen ลอยบนพื้นหลัง
    ("03_intel_logo_2023_publicdomain.png", T3, T4, 0.6, 0.0, 0.0, 1.0),  # โลโก้ Intel ทับตึก
]


def uid():
    return str(uuid.uuid4()).upper()


def us(sec):
    return int(round(sec * US))


def media_material(fn, kind, w, h, dur):
    """รายการใน draft_info.materials.videos (ใช้โครงเดียวกับที่ CapCut 9.6 เขียน)"""
    return {
        "aigc_history_id": "", "aigc_item_id": "", "aigc_type": "none", "audio_fade": None,
        "beauty_body_auto_preset": None, "beauty_body_preset_id": "",
        "beauty_face_auto_preset": {"name": "", "preset_id": "", "rate_map": "", "scene": ""},
        "beauty_face_auto_preset_infos": [], "beauty_face_preset_infos": [],
        "cartoon_path": "", "category_id": "", "category_name": "local", "check_flag": 62978047,
        "content_feature_info": None, "corner_pin": None,
        "crop": {"lower_left_x": 0.0, "lower_left_y": 1.0, "lower_right_x": 1.0, "lower_right_y": 1.0,
                 "upper_left_x": 0.0, "upper_left_y": 0.0, "upper_right_x": 1.0, "upper_right_y": 0.0},
        "crop_ratio": "free", "crop_scale": 1.0,
        "duration": PHOTO_DURATION if kind == "photo" else dur,
        "extra_type_option": 0, "formula_id": "", "freeze": None,
        "has_audio": kind == "video", "has_sound_separated": False,
        "height": h, "id": uid(),
        "intensifies_audio_path": "", "intensifies_path": "",
        "is_ai_generate_content": False, "is_copyright": False, "is_set_beauty_mode": False,
        "is_text_edit_overdub": False, "is_unified_beauty_mode": False, "is_video_copilot_aigc_content": False,
        "live_photo_cover_path": "", "live_photo_timestamp": -1,
        "local_id": "", "local_material_from": "", "local_material_id": "", "material_id": "",
        "material_name": fn, "material_url": "",
        "matting": {"cloud_product_fps": 0.0, "custom_matting_id": "", "enable_matting_stroke": False,
                    "expansion": 0, "feather": 0, "flag": 0, "has_use_quick_brush": False,
                    "has_use_quick_eraser": False, "interactiveTime": [], "is_clould": False,
                    "mask_video_path": "", "path": "", "reverse": False, "strokes": []},
        "media_path": "", "multi_camera_info": None, "object_locked": None, "origin_material_id": "",
        "path": os.path.join(BROLL, fn),
        "picture_from": "none", "picture_set_category_id": "", "picture_set_category_name": "",
        "pre_applied_vip_materials": [], "request_id": "", "reverse_intensifies_path": "", "reverse_path": "",
        "smart_match_info": None, "smart_motion": None, "source": 0, "source_platform": 0,
        "stable": {"matrix_path": "", "stable_level": 0, "time_range": {"duration": 0, "start": 0}},
        "surface_trackings": [], "team_id": "", "type": kind, "unique_id": "",
        "video_algorithm": {"ai_background_configs": [], "ai_expression_driven": None, "ai_in_painting_config": [],
                            "ai_motion_driven": None, "aigc_generate": None, "aigc_generate_list": [],
                            "algorithms": [], "complement_frame_config": None, "deflicker": None,
                            "gameplay_configs": [], "image_interpretation": None, "motion_blur_config": None,
                            "mouth_shape_driver": None, "noise_reduction": None, "path": "",
                            "quality_enhance": None, "skip_algorithm_index": [], "smart_complement_frame": None,
                            "story_video_modify_video_config": {"generate_card_id": "", "generate_id": "",
                                                                "is_overwrite_last_video": False, "task_id": "",
                                                                "tracker_task_id": ""},
                            "super_resolution": None, "time_range": None},
        "video_mask_shadow": {"alpha": 0.0, "angle": 0.0, "blur": 0.0, "color": "", "distance": 0.0,
                              "path": "", "resource_id": ""},
        "video_mask_stroke": {"alpha": 0.0, "color": "", "distance": 0.0, "horizontal_shift": 0.0, "path": "",
                              "resource_id": "", "size": 0.0, "texture": 0.0, "type": "", "vertical_shift": 0.0},
        "width": w, "workflow_node_id": "",
    }


def segment(material_id, start, end, scale, x, y, volume, refs, render_index, track_render_index):
    dur = us(end) - us(start)
    return {
        "caption_info": None, "cartoon": False,
        "clip": {"alpha": 1.0, "flip": {"horizontal": False, "vertical": False}, "rotation": 0.0,
                 "rotation3d": [], "scale": {"x": scale, "y": scale}, "transform": {"x": x, "y": y}},
        "color_correct_alg_result": "", "common_keyframes": [], "desc": "", "digital_human_template_group_id": "",
        "enable_adjust": True, "enable_adjust_mask": False, "enable_color_adjust_pro": False,
        "enable_color_correct_adjust": False, "enable_color_curves": True, "enable_color_match_adjust": False,
        "enable_color_wheels": True, "enable_hsl": False, "enable_hsl_curves": True, "enable_lut": True,
        "enable_mask_shadow": False, "enable_mask_stroke": False, "enable_smart_color_adjust": False,
        "enable_video_mask": True, "extra_material_refs": refs, "group_id": "",
        "hdr_settings": None, "hdr_vivid_settings": None, "id": uid(),
        "intensifies_audio": False, "is_loop": False, "is_placeholder": False, "is_tone_modify": False,
        "keyframe_refs": [], "last_nonzero_volume": 1.0, "lyric_keyframes": None,
        "material_id": material_id, "raw_segment_id": "", "render_index": render_index,
        "render_timerange": {"duration": 0, "start": 0},
        "responsive_layout": {"enable": False, "horizontal_pos_layout": 0, "size_layout": 0,
                              "target_follow": "", "vertical_pos_layout": 0},
        "reverse": False, "segment_color_tag": "", "source": "segmentsourcenormal",
        "source_timerange": {"duration": dur, "start": 0}, "speed": 1.0, "state": 0,
        "target_timerange": {"duration": dur, "start": us(start)},
        "template_id": "", "template_scene": "default", "track_attribute": 0,
        "track_render_index": track_render_index,
        "uniform_scale": {"on": True, "value": scale}, "visible": True, "volume": volume,
    }


def main():
    if not DRY and subprocess.run(["pgrep", "-x", "CapCut"], capture_output=True).returncode == 0:
        sys.exit("CapCut ยังเปิดอยู่ กรุณาปิด CapCut (Cmd+Q) ก่อน แล้วรันใหม่ ไม่งั้น CapCut จะเขียนทับที่แก้ไป")
    for fn, *_ in LIBRARY:
        p = os.path.join(BROLL, fn)
        if not os.path.exists(p):
            sys.exit(f"ไม่พบไฟล์ {p}")

    info = json.load(open(os.path.join(PROJECT, "draft_info.json")))
    meta = json.load(open(os.path.join(PROJECT, "draft_meta_info.json")))
    mats = info["materials"]
    now = int(time.time())

    # ---------- 1) media library (draft_meta_info.json) ----------
    lib = next(g for g in meta["draft_materials"] if g["type"] == 0)
    existing = {m["file_Path"] for m in lib["value"]}
    for fn, kind, w, h, dur in LIBRARY:
        p = os.path.join(BROLL, fn)
        if p in existing:
            continue
        d = PHOTO_DURATION if kind == "photo" else dur
        lib["value"].append({
            "ai_group_type": "", "create_time": now, "duration": d, "enter_from": 0, "extra_info": fn,
            "file_Path": p, "height": h, "id": str(uuid.uuid4()), "import_time": now,
            "import_time_ms": int(time.time() * 1_000_000), "item_source": 1, "material_color_tag": "",
            "md5": "", "metetype": kind, "roughcut_time_range": {"duration": d, "start": 0},
            "sub_time_range": {"duration": -1, "start": -1}, "type": 0, "width": w,
        })

    # ---------- 2) timeline (draft_info.json) ----------
    byname = {fn: (kind, w, h, dur) for fn, kind, w, h, dur in LIBRARY}
    mat_ids = {}
    for fn in {s[0] for s in MAIN + OVERLAY}:
        kind, w, h, dur = byname[fn]
        m = media_material(fn, kind, w, h, dur)
        mats["videos"].append(m)
        mat_ids[fn] = m["id"]

    def make_refs():
        sp = {"id": uid(), "type": "speed", "mode": 0, "speed": 1.0, "curve_speed": None}
        ph = {"id": uid(), "type": "placeholder_info", "meta_type": "none", "error_path": "", "error_text": "",
              "res_path": "", "res_text": ""}
        cv = {"id": uid(), "type": "canvas_color", "album_image": "", "blur": 0.0, "color": "", "image": "",
              "image_id": "", "image_name": "", "source_platform": 0, "team_id": ""}
        sc = {"id": uid(), "type": "none", "audio_channel_mapping": 0, "is_config_open": False}
        vs = {"id": uid(), "type": "vocal_separation", "choice": 0, "removed_sounds": [], "time_range": None,
              "production_path": "", "final_algorithm": "", "enter_from": ""}
        mats["speeds"].append(sp); mats["placeholder_infos"].append(ph); mats["canvases"].append(cv)
        mats["sound_channel_mappings"].append(sc); mats["vocal_separations"].append(vs)
        return [sp["id"], ph["id"], cv["id"], sc["id"], vs["id"]]

    main_track = next(t for t in info["tracks"] if t["type"] == "video")
    if main_track["segments"]:
        sys.exit("แทร็กวิดีโอหลักมีคลิปอยู่แล้ว หยุดเพื่อไม่ให้ทับของเดิม")
    for fn, a, b, sc, x, y, vol in MAIN:
        main_track["segments"].append(segment(mat_ids[fn], a, b, sc, x, y, vol, make_refs(), 0, 0))

    overlay = {"id": uid(), "type": "video", "segments": [], "flag": 0, "attribute": 0,
               "name": "", "is_default_name": True}
    for fn, a, b, sc, x, y, vol in OVERLAY:
        overlay["segments"].append(segment(mat_ids[fn], a, b, sc, x, y, vol, make_refs(), 1, 1))
    # แทรกไว้ถัดจากแทร็กวิดีโอหลัก (ใต้แทร็กข้อความ) เพื่อให้ซับยังอยู่บนสุด
    idx = info["tracks"].index(main_track)
    info["tracks"].insert(idx + 1, overlay)

    info["update_time"] = int(time.time() * 1_000_000)
    meta["tm_draft_modified"] = int(time.time() * 1_000_000)

    # ---------- 3) write ----------
    os.makedirs(OUT, exist_ok=True)
    if not DRY:
        bk = os.path.join(PROJECT, "backup_before_broll")
        os.makedirs(bk, exist_ok=True)
        for f in ("draft_info.json", "draft_meta_info.json"):
            shutil.copy2(os.path.join(PROJECT, f), os.path.join(bk, f"{f}.{now}.bak"))
        print("สำรองไฟล์เดิมไว้ที่", bk)
    with open(os.path.join(OUT, "draft_info.json"), "w") as f:
        json.dump(info, f, ensure_ascii=False)
    with open(os.path.join(OUT, "draft_meta_info.json"), "w") as f:
        json.dump(meta, f, ensure_ascii=False)
    print(f"เสร็จ: เพิ่ม {len(LIBRARY)} ไฟล์เข้า media library, "
          f"{len(MAIN)} คลิปบนแทร็กหลัก, {len(OVERLAY)} คลิปบนแทร็กซ้อน -> {OUT}")


if __name__ == "__main__":
    main()
