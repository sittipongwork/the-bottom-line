#!/usr/bin/env python3
"""ตัดต่อ BizShorts EP3 (10 เรื่อง AMD) ทั้งตอนลงโปรเจกต์ CapCut 1021 ตามจังหวะไฟล์ subtitle

- ต้องปิด CapCut ก่อนรัน (สคริปต์หยุดเองถ้ายังเปิดอยู่)
- สำรอง draft_info.json / draft_meta_info.json ไว้ที่ <project>/backup_before_broll/ ก่อนแก้
- รันซ้ำได้: สคริปต์จะลบคลิปที่มันเคยวางไว้ (ทุกคลิปที่ชี้ไปโฟลเดอร์ broll/) แล้ววางใหม่ทั้งหมด
  ซับ เสียง และของที่คุณเพิ่มเองไม่ถูกแตะ

ใช้:  python3 build_ep3_capcut.py              # ใส่จริง
      python3 build_ep3_capcut.py --dry-run --out <โฟลเดอร์>   # ทดสอบ ไม่แตะโปรเจกต์
"""
import glob, json, os, shutil, subprocess, sys, time, uuid

PROJECT = "/Users/donutsped/Movies/CapCut/User Data/Projects/com.lveditor.draft/1021"
BROLL = "/Users/donutsped/code/start/BizShorts/ep3_amd/broll"
DRY = "--dry-run" in sys.argv
OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else PROJECT

CANVAS_W, CANVAS_H = 1080, 1920
US = 1_000_000
PHOTO_DURATION = 10_800_000_000  # ค่าที่ CapCut ใช้กับภาพนิ่ง
ZOOM = 1.08  # ซูมช้า ๆ 8% ตลอดช็อต

# ขนาดไฟล์ (กว้าง, สูง, ความยาววินาที สำหรับวิดีโอ)
ASSETS = {
    "01_amd_ryzen9_7900x_CristoCalis_CC-BY-SA4.jpg": (3068, 3068, 0),
    "01b_amd_ryzen5_7600_Smial_FAL.jpg": (4888, 4888, 0),
    "01c_amd_logo_publicdomain.png": (1920, 458, 0),
    "02_amd_hq_santaclara_Coolcaesar_CC-BY-SA4.jpg": (4312, 3188, 0),
    "03_intel_logo_2023_publicdomain.png": (1920, 745, 0),
    "03b_intel_hq_2023_Coolcaesar_CC-BY-SA4.jpg": (4863, 3249, 0),
    "04_lisa_su_sxsw2024_Fuzheado_CC-BY4_upright.jpg": (3072, 4608, 0),
    "04b_lisa_su_ornl2019_GenevieveMartin_CC-BY2.jpg": (3000, 2000, 0),
    "05_bangkok_skyline_2024_OPK_CC-BY-SA4.jpg": (3200, 1800, 0),
    "06_jensen_huang_stanford2026_Anderseidesvik_CC-BY-SA4.jpg": (3888, 5184, 0),
    "07_nvidia_hq_Coolcaesar_CC-BY-SA4.jpg": (4662, 2852, 0),
    "08_radeon_rx7900xtx_Geni_CC-BY-SA4.jpg": (5956, 3728, 0),
    "09_ati_logo_publicdomain.png": (1920, 1216, 0),
    "09b_ati_building_Coolcaesar_CC-BY-SA3.jpg": (1253, 911, 0),
    "10_jerry_sanders_PhilKonstantin_publicdomain.jpg": (355, 450, 0),
    "10b_fairchild_logo_publicdomain.png": (1920, 683, 0),
    "11_ibm_pc_1981_TheWub_CC-BY-SA4.jpg": (4729, 2956, 0),
    "11b_amd_am9080_KonstantinLanzet_CC-BY-SA3.jpg": (1377, 693, 0),
    "11c_intel_8088_JudMcCranie_CC-BY-SA4.jpg": (6001, 2278, 0),
    "13_athlon_thunderbird_1100_Krdan_CC-BY3.jpg": (1395, 1360, 0),
    "13b_pentium3_Misterrf_CC-BY-SA4.jpg": (5370, 4634, 0),
    "14_frontier_supercomputer_1_ORNL_CC-BY2.jpg": (3000, 1992, 0),
    "14b_frontier_supercomputer_2_ORNL_CC-BY2.jpg": (3000, 2460, 0),
    "15_openai_logo_publicdomain.png": (1920, 517, 0),
    "15b_openai_icon_hand_FoxTPNL_CC-BY4.jpg": (1313, 1751, 0),
    "16_athlon64_3200_ThomasNguyen_CC-BY-SA4.jpg": (4000, 4000, 0),
    "16b_intel_itanium2_KonstantinLanzet_CC-BY-SA3.jpg": (2085, 1221, 0),
    "16c_surface_laptop_CC0.jpg": (3072, 4096, 0),
    "pexels_6755168_motherboard_vertical.mp4": (1080, 1920, 23.92),
    "pexels_35977437_circuit_processor.mp4": (1920, 1080, 20.875),
    "pexels_7140928_cpu_closeup.mp4": (3840, 2160, 9.387),
    "pexels_10374892_typing_laptop.mp4": (1080, 1920, 8.542),
    "pexels_28679682_vintage_living_room_vertical.mp4": (1080, 1920, 3.7),
    "pexels_32625859_bangkok_traffic_vertical.mp4": (1080, 1920, 59.7),
    "pexels_6101348_judge_gavel_vertical.mp4": (2160, 4096, 7.273),
    "pexels_6326861_counting_banknotes.mp4": (1440, 2732, 18.44),
    "pexels_7579561_stock_exchange_display.mp4": (1440, 2732, 22.08),
    "pexels_8480284_person_stock_chart.mp4": (1080, 1920, 29.802),
}

BG = "pexels_6755168_motherboard_vertical.mp4"
AMD = "01c_amd_logo_publicdomain.png"
INTEL = "03_intel_logo_2023_publicdomain.png"

# ---------------------------------------------------------------------------
# ช็อตลิสต์: (เลเยอร์ 1=ล่าง 2=กลาง 3=บน, ไฟล์, เริ่ม, จบ, โหมด, x, y, ซูม)
#   โหมด: "cover" = ขยายเต็มจอ 9:16, "contain" = ใส่พอดีจอ (ค่าเริ่มต้นของ CapCut) หรือตัวเลข = คูณจาก contain
#   x, y: เลื่อนตำแหน่ง หน่วย = ครึ่งความกว้างจอ (x=1 คือขอบขวา), y บวก = ขึ้น
#   ซูม: "in" ซูมเข้าช้า ๆ, "out" ซูมออก, None นิ่ง
# เวลาอ้างอิงจากไฟล์ subtitle
# ---------------------------------------------------------------------------
SHOTS = [
    # --- เปิด 0:00–0:11 ---
    (1, BG, 0.0, 3.366, "cover", 0, 0, None),
    (2, "01_amd_ryzen9_7900x_CristoCalis_CC-BY-SA4.jpg", 0.0, 3.366, 0.9, 0, 0, "in"),
    (1, "02_amd_hq_santaclara_Coolcaesar_CC-BY-SA4.jpg", 3.366, 5.766, "cover", -1.3, 0, None),   # เลื่อนให้เห็นป้าย AMD ขวาตึก
    (1, "03b_intel_hq_2023_Coolcaesar_CC-BY-SA4.jpg", 5.766, 7.3, "cover", 0, 0, "in"),
    (3, INTEL, 5.766, 7.3, 0.6, 0, 0, None),
    (1, "04_lisa_su_sxsw2024_Fuzheado_CC-BY4_upright.jpg", 7.3, 11.1, "cover", 0, 0, "in"),
    # --- ข้อ 1 มูลค่า 30 ล้านล้าน > GDP ไทย ---
    (1, "pexels_7579561_stock_exchange_display.mp4", 11.1, 15.7, "cover", 0, 0, None),
    (3, AMD, 11.1, 15.7, 0.45, 0, 0.55, None),
    (1, "pexels_32625859_bangkok_traffic_vertical.mp4", 15.7, 18.633, "cover", 0, 0, None),
    # --- ข้อ 2 Lisa Su กับ Jensen Huang เป็นญาติ ---
    (1, "04b_lisa_su_ornl2019_GenevieveMartin_CC-BY2.jpg", 18.633, 22.1, "cover", 0, 0, "in"),
    (1, "06_jensen_huang_stanford2026_Anderseidesvik_CC-BY-SA4.jpg", 22.1, 24.6, "cover", 0, 0.1, "in"),
    (1, BG, 24.6, 30.2, "cover", 0, 0, None),
    (2, "04b_lisa_su_ornl2019_GenevieveMartin_CC-BY2.jpg", 24.6, 30.2, 0.62, -0.3, 0.35, None),   # สองคนเฉียงกัน
    (3, "06_jensen_huang_stanford2026_Anderseidesvik_CC-BY-SA4.jpg", 24.6, 30.2, 0.6, 0.3, -0.35, None),
    (1, "02_amd_hq_santaclara_Coolcaesar_CC-BY-SA4.jpg", 30.2, 32.633, "cover", -1.3, 0, None),   # คนละเส้นทาง: AMD
    (1, "07_nvidia_hq_Coolcaesar_CC-BY-SA4.jpg", 32.633, 36.2, "cover", 0, 0, "out"),             # ... กับ NVIDIA
    # --- ข้อ 3 Radeon ซื้อมาจาก ATI ---
    (1, BG, 36.2, 43.4, "cover", 0, 0, None),
    (2, "08_radeon_rx7900xtx_Geni_CC-BY-SA4.jpg", 36.2, 39.7, "contain", 0, 0, "in"),
    (2, "09b_ati_building_Coolcaesar_CC-BY-SA3.jpg", 39.7, 43.4, "contain", 0, 0, None),
    (3, "09_ati_logo_publicdomain.png", 41.4, 43.4, 0.45, 0, -0.55, None),
    # --- ข้อ 4 เริ่มในห้องนั่งเล่น / Jerry Sanders ---
    (1, "pexels_28679682_vintage_living_room_vertical.mp4", 43.4, 47.1, "cover", 0, 0, None),
    (1, BG, 47.1, 53.566, "cover", 0, 0, None),
    (3, AMD, 47.1, 49.033, 0.6, 0, 0, None),
    (2, "10_jerry_sanders_PhilKonstantin_publicdomain.jpg", 49.033, 53.566, 0.85, 0, 0.12, None),
    (3, "10b_fairchild_logo_publicdomain.png", 50.933, 53.566, 0.45, 0, -0.6, None),            # บริษัทเก่าที่ไล่เขาออก
    # --- ข้อ 5 IBM PC ใช้ชิป AMD ---
    (1, "11_ibm_pc_1981_TheWub_CC-BY-SA4.jpg", 53.566, 58.566, "cover", 0, 0, "out"),
    (1, BG, 58.566, 64.533, "cover", 0, 0, None),
    (2, "11c_intel_8088_JudMcCranie_CC-BY-SA4.jpg", 58.566, 61.4, "contain", 0, 0, "in"),
    (2, "11b_amd_am9080_KonstantinLanzet_CC-BY-SA3.jpg", 61.4, 64.533, "contain", 0, 0, "in"),
    (3, AMD, 61.4, 64.533, 0.4, 0, -0.6, None),
    # --- ข้อ 6 ฟ้องกัน Intel จ่าย 4 หมื่นล้าน ---
    (1, "pexels_6101348_judge_gavel_vertical.mp4", 64.533, 69.666, "cover", 0, 0, None),
    (1, "pexels_6326861_counting_banknotes.mp4", 69.666, 74.266, "cover", 0, 0, None),
    (3, INTEL, 69.666, 74.266, 0.45, 0, 0.55, None),
    (2, AMD, 69.666, 74.266, 0.45, 0, -0.55, None),
    # --- ข้อ 7 ชิป 1 GHz เจ้าแรก ---
    (1, BG, 74.266, 81.866, "cover", 0, 0, None),
    (2, "13_athlon_thunderbird_1100_Krdan_CC-BY3.jpg", 74.266, 79.6, "contain", 0, 0, "in"),
    (2, "13b_pentium3_Misterrf_CC-BY-SA4.jpg", 79.6, 81.866, "contain", 0, 0, "in"),
    # --- ข้อ 8 ซูเปอร์คอมพิวเตอร์ Frontier ---
    (1, "14_frontier_supercomputer_1_ORNL_CC-BY2.jpg", 81.866, 87.266, "cover", 0, 0, "in"),
    (1, "14b_frontier_supercomputer_2_ORNL_CC-BY2.jpg", 87.266, 90.7, "cover", 0, 0, "out"),
    # --- ข้อ 9 OpenAI ซื้อชิป ได้สิทธิ์ซื้อหุ้น ---
    (1, "15b_openai_icon_hand_FoxTPNL_CC-BY4.jpg", 90.7, 94.633, "cover", 0, 0, "in"),
    (1, "pexels_8480284_person_stock_chart.mp4", 94.633, 99.6, "cover", 0, 0, None),
    (3, AMD, 94.633, 99.6, 0.45, 0, 0.55, None),
    (1, "pexels_7140928_cpu_closeup.mp4", 99.6, 103.3, "cover", 0, 0, None),
    # --- ข้อ 10 64-bit ที่ AMD คิด ---
    (1, "pexels_10374892_typing_laptop.mp4", 103.3, 107.033, "cover", 0, 0, None),
    (1, "16c_surface_laptop_CC0.jpg", 107.033, 109.2, "cover", 0, 0, "in"),
    (1, "16_athlon64_3200_ThomasNguyen_CC-BY-SA4.jpg", 109.2, 112.6, "cover", 0, 0, "in"),
    (1, BG, 112.6, 115.733, "cover", 0, 0, None),
    (2, "16b_intel_itanium2_KonstantinLanzet_CC-BY-SA3.jpg", 112.6, 115.733, "contain", 0, 0, "in"),
    (3, INTEL, 112.6, 115.733, 0.4, 0, 0.6, None),
    (1, "16_athlon64_3200_ThomasNguyen_CC-BY-SA4.jpg", 115.733, 118.433, "cover", 0, 0, "out"),
    # --- ปิด: โรงงานสำรอง → Intel ต้องเดินตาม + CTA ---
    (1, "03b_intel_hq_2023_Coolcaesar_CC-BY-SA4.jpg", 118.433, 120.866, "cover", 0, 0, "out"),
    (1, "02_amd_hq_santaclara_Coolcaesar_CC-BY-SA4.jpg", 120.866, 124.8, "cover", -1.3, 0, "in"),
    (1, BG, 124.8, 130.166, "cover", 0, 0, None),
    (2, AMD, 124.8, 130.166, 0.6, 0, 0, None),
]


def uid():
    return str(uuid.uuid4()).upper()


def us(sec):
    return int(round(sec * US))


def kind_of(fn):
    return "video" if fn.endswith(".mp4") else "photo"


def base_scale(fn, mode):
    w, h, _ = ASSETS[fn]
    fit = min(CANVAS_W / w, CANVAS_H / h)          # scale 1.0 ของ CapCut = ใส่พอดีจอ
    cover = max(CANVAS_W / w, CANVAS_H / h) / fit
    if mode == "cover":
        return round(cover, 4)
    if mode == "contain":
        return 1.0
    return float(mode)


def media_material(fn):
    w, h, dur = ASSETS[fn]
    kind = kind_of(fn)
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
        "duration": PHOTO_DURATION if kind == "photo" else us(dur),
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


def keyframe(t_us, value):
    return {"curveType": "Line", "graphID": "", "id": uid(), "left_control": {"x": 0.0, "y": 0.0},
            "right_control": {"x": 0.0, "y": 0.0}, "time_offset": t_us, "values": [value]}


def segment(material_id, start, end, scale, x, y, zoom, volume, refs, render_index, track_render_index):
    dur = us(end) - us(start)
    kf = []
    if zoom == "in":
        kf = [{"id": uid(), "keyframe_list": [keyframe(0, scale), keyframe(dur, round(scale * ZOOM, 4))],
               "material_id": "", "property_type": "KFTypeScaleX"}]
    elif zoom == "out":
        kf = [{"id": uid(), "keyframe_list": [keyframe(0, round(scale * ZOOM, 4)), keyframe(dur, scale)],
               "material_id": "", "property_type": "KFTypeScaleX"}]
    return {
        "caption_info": None, "cartoon": False,
        "clip": {"alpha": 1.0, "flip": {"horizontal": False, "vertical": False}, "rotation": 0.0,
                 "rotation3d": [], "scale": {"x": scale, "y": scale}, "transform": {"x": float(x), "y": float(y)}},
        "color_correct_alg_result": "", "common_keyframes": kf, "desc": "", "digital_human_template_group_id": "",
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


def validate():
    """ตรวจว่าช็อตในเลเยอร์เดียวกันไม่ทับกัน และคลิปวิดีโอไม่ยาวเกินไฟล์ต้นฉบับ"""
    by_layer = {}
    for layer, fn, a, b, *_ in SHOTS:
        if fn not in ASSETS:
            sys.exit(f"ไม่รู้จักไฟล์ {fn}")
        if b <= a:
            sys.exit(f"เวลาผิด {fn} {a}-{b}")
        if kind_of(fn) == "video" and b - a > ASSETS[fn][2] + 1e-6:
            sys.exit(f"คลิป {fn} ยาว {ASSETS[fn][2]} วิ แต่ใช้ {b - a:.3f} วิ ({a}-{b})")
        by_layer.setdefault(layer, []).append((a, b, fn))
    for layer, items in by_layer.items():
        items.sort()
        for (a1, b1, f1), (a2, b2, f2) in zip(items, items[1:]):
            if a2 < b1 - 1e-6:
                sys.exit(f"เลเยอร์ {layer}: {f1} ({a1}-{b1}) ทับกับ {f2} ({a2}-{b2})")


def strip_previous(info, meta):
    """ลบทุกอย่างที่สคริปต์นี้ (หรือ import_broll_to_capcut.py) เคยใส่ไว้ โดยดูจาก path ในโฟลเดอร์ broll"""
    mats = info["materials"]
    ours = {m["id"] for m in mats["videos"] if m.get("path", "").startswith(BROLL)}
    dead_refs = set()
    for t in info["tracks"]:
        if t["type"] != "video":
            continue
        keep = []
        for s in t["segments"]:
            if s["material_id"] in ours:
                dead_refs.update(s["extra_material_refs"])
            else:
                keep.append(s)
        t["segments"] = keep
    first_video = next(t for t in info["tracks"] if t["type"] == "video")
    info["tracks"] = [t for t in info["tracks"] if not (t["type"] == "video" and t is not first_video and not t["segments"])]
    mats["videos"] = [m for m in mats["videos"] if m["id"] not in ours]
    for k in ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "vocal_separations"):
        mats[k] = [m for m in mats[k] if m["id"] not in dead_refs]
    lib = next(g for g in meta["draft_materials"] if g["type"] == 0)
    lib["value"] = [m for m in lib["value"] if not m["file_Path"].startswith(BROLL)]
    return len(ours)


def main():
    validate()
    if not DRY and subprocess.run(["pgrep", "-x", "CapCut"], capture_output=True).returncode == 0:
        sys.exit("CapCut ยังเปิดอยู่ กรุณาปิด CapCut (Cmd+Q) ก่อน แล้วรันใหม่")
    for fn in ASSETS:
        if not os.path.exists(os.path.join(BROLL, fn)):
            sys.exit(f"ไม่พบไฟล์ {fn} ใน {BROLL}")

    info = json.load(open(os.path.join(PROJECT, "draft_info.json")))
    meta = json.load(open(os.path.join(PROJECT, "draft_meta_info.json")))
    removed = strip_previous(info, meta)
    mats = info["materials"]
    now = int(time.time())

    # 1) media library
    lib = next(g for g in meta["draft_materials"] if g["type"] == 0)
    for fn, (w, h, dur) in ASSETS.items():
        kind = kind_of(fn)
        d = PHOTO_DURATION if kind == "photo" else us(dur)
        lib["value"].append({
            "ai_group_type": "", "create_time": now, "duration": d, "enter_from": 0, "extra_info": fn,
            "file_Path": os.path.join(BROLL, fn), "height": h, "id": str(uuid.uuid4()), "import_time": now,
            "import_time_ms": int(time.time() * US), "item_source": 1, "material_color_tag": "",
            "md5": "", "metetype": kind, "roughcut_time_range": {"duration": d, "start": 0},
            "sub_time_range": {"duration": -1, "start": -1}, "type": 0, "width": w,
        })

    # 2) timeline
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
        sys.exit("แทร็กวิดีโอหลักมีคลิปที่ไม่ใช่ของสคริปต์อยู่ หยุดเพื่อไม่ให้ทับ")
    tracks = {1: main_track}
    for layer in (2, 3):
        tracks[layer] = {"id": uid(), "type": "video", "segments": [], "flag": 0, "attribute": 0,
                         "name": "", "is_default_name": True}

    for layer, fn, a, b, mode, x, y, zoom in sorted(SHOTS, key=lambda s: (s[0], s[2])):
        m = media_material(fn)
        mats["videos"].append(m)
        scale = base_scale(fn, mode)
        volume = 0.0 if kind_of(fn) == "video" else 1.0   # ปิดเสียงคลิปสต็อกทุกตัว
        ri = 0 if layer == 1 else layer - 1
        tracks[layer]["segments"].append(segment(m["id"], a, b, scale, x, y, zoom, volume, make_refs(), ri, ri))

    idx = info["tracks"].index(main_track)
    info["tracks"].insert(idx + 1, tracks[2])
    info["tracks"].insert(idx + 2, tracks[3])
    info["update_time"] = int(time.time() * US)
    meta["tm_draft_modified"] = int(time.time() * US)

    # 3) write
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
    n = {l: len(t["segments"]) for l, t in tracks.items()}
    print(f"ลบของเดิม {removed} คลิป · วางใหม่ {sum(n.values())} คลิป "
          f"(ล่าง {n[1]}, กลาง {n[2]}, บน {n[3]}) · media library {len(ASSETS)} ไฟล์ -> {OUT}")


if __name__ == "__main__":
    main()
