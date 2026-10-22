// เรนเดอร์เลเยอร์ข้อความของ BizShorts เป็น PNG โปร่งใสเต็มเฟรม 1080×1920 ด้วย CoreText (จัดรูปอักษรไทยถูกต้อง)
// ใช้โดย render_preview.py:  swift render_text_png.swift <spec.json> <outdir>
// spec.json = {"width","height","px_per_size","texts":[{"text","size","color":[r,g,b],"stroke","font","y","bg_alpha","max_width"}]}
//   max_width = สัดส่วนความกว้างจอที่ข้อความกว้างได้ (เท่ากับ line_max_width ของ CapCut) ตัดบรรทัดอัตโนมัติด้วย CTFramesetter
import Foundation
import CoreGraphics
import CoreText
import ImageIO
import UniformTypeIdentifiers

struct Spec: Decodable {
    let width: Int; let height: Int; let px_per_size: Double; let texts: [TextItem]
}
struct TextItem: Decodable {
    let text: String; let size: Double; let color: [Double]; let stroke: Double
    let font: String; let y: Double; let bg_alpha: Double; let max_width: Double
}

var fontCache: [String: CGFont] = [:]
func loadFont(_ path: String) -> CGFont? {
    if let f = fontCache[path] { return f }
    guard let dp = CGDataProvider(url: URL(fileURLWithPath: path) as CFURL), let f = CGFont(dp) else { return nil }
    fontCache[path] = f
    return f
}

let args = CommandLine.arguments
guard args.count >= 3 else { fputs("usage: render_text_png.swift spec.json outdir\n", stderr); exit(2) }
let spec = try! JSONDecoder().decode(Spec.self, from: Data(contentsOf: URL(fileURLWithPath: args[1])))
let outdir = args[2]
try? FileManager.default.createDirectory(atPath: outdir, withIntermediateDirectories: true)

let W = spec.width, H = spec.height
let cs = CGColorSpaceCreateDeviceRGB()
let black = CGColor(colorSpace: cs, components: [0, 0, 0, 1])!

/// สร้าง attributed string ของทั้งข้อความ (จัดกลาง) · pass "stroke" = ขอบอย่างเดียว, "fill" = ไส้อย่างเดียว
func attributed(_ text: String, font: CTFont, fill: CGColor, strokePct: Double, pass: String, lineSpacing: CGFloat) -> CFAttributedString {
    var alignment = CTTextAlignment.center
    var spacing = lineSpacing
    let settings = [
        CTParagraphStyleSetting(spec: .alignment, valueSize: MemoryLayout<CTTextAlignment>.size, value: &alignment),
        CTParagraphStyleSetting(spec: .lineSpacingAdjustment, valueSize: MemoryLayout<CGFloat>.size, value: &spacing),
    ]
    let para = CTParagraphStyleCreate(settings, settings.count)
    var attrs: [CFString: Any] = [kCTFontAttributeName: font, kCTParagraphStyleAttributeName: para]
    if pass == "stroke" {
        attrs[kCTForegroundColorAttributeName] = black
        attrs[kCTStrokeColorAttributeName] = black
        attrs[kCTStrokeWidthAttributeName] = strokePct * 2      // บวก = ขอบอย่างเดียว กว้าง 2 เท่าเพราะครึ่งหนึ่งจะถูกไส้ทับ
    } else {
        attrs[kCTForegroundColorAttributeName] = fill
    }
    return CFAttributedStringCreate(nil, text as CFString, attrs as CFDictionary)!
}

for (i, t) in spec.texts.enumerated() {
    guard let ctx = CGContext(data: nil, width: W, height: H, bitsPerComponent: 8, bytesPerRow: 0, space: cs,
                              bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { continue }
    ctx.clear(CGRect(x: 0, y: 0, width: W, height: H))
    guard let cgFont = loadFont(t.font) else { fputs("font not found: \(t.font)\n", stderr); continue }
    let em = t.size * spec.px_per_size
    let ctFont = CTFontCreateWithGraphicsFont(cgFont, CGFloat(em), nil, nil)
    let fill = CGColor(colorSpace: cs, components: [CGFloat(t.color[0]), CGFloat(t.color[1]), CGFloat(t.color[2]), 1])!
    let strokePct = t.stroke * 100.0        // ขอบของ CapCut 0.06–0.12 ≈ 6–12% ของขนาดฟอนต์
    let maxW = Double(W) * t.max_width
    let lineSpacing = CGFloat(em * 0.08)

    // วัดขนาดที่ตัดบรรทัดแล้ว
    let measure = attributed(t.text, font: ctFont, fill: fill, strokePct: strokePct, pass: "fill", lineSpacing: lineSpacing)
    let fs = CTFramesetterCreateWithAttributedString(measure)
    let fitted = CTFramesetterSuggestFrameSizeWithConstraints(fs, CFRange(location: 0, length: 0), nil,
                                                               CGSize(width: maxW, height: 100000), nil)
    let boxW = ceil(fitted.width) + em * 0.1, boxH = ceil(fitted.height) + em * 0.15
    let yc = Double(H) / 2 + t.y * Double(H) / 2          // CapCut: y บวก = ขึ้น · CG: origin ล่างซ้าย
    let frameRect = CGRect(x: Double(W) / 2 - boxW / 2, y: yc - boxH / 2, width: boxW, height: boxH)

    if t.bg_alpha > 0 {
        let pad = em * 0.3
        let rect = frameRect.insetBy(dx: -pad, dy: -pad * 0.5)
        let path = CGPath(roundedRect: rect, cornerWidth: em * 0.2, cornerHeight: em * 0.2, transform: nil)
        ctx.setFillColor(CGColor(colorSpace: cs, components: [0, 0, 0, CGFloat(t.bg_alpha)])!)
        ctx.addPath(path); ctx.fillPath()
    }
    ctx.setLineJoin(.round)
    for pass in ["stroke", "fill"] {
        let astr = attributed(t.text, font: ctFont, fill: fill, strokePct: strokePct, pass: pass, lineSpacing: lineSpacing)
        let fs2 = CTFramesetterCreateWithAttributedString(astr)
        let frame = CTFramesetterCreateFrame(fs2, CFRange(location: 0, length: 0), CGPath(rect: frameRect, transform: nil), nil)
        CTFrameDraw(frame, ctx)
    }
    let lines = CTFrameGetLines(CTFramesetterCreateFrame(fs, CFRange(location: 0, length: 0), CGPath(rect: frameRect, transform: nil), nil)) as! [CTLine]
    let img = ctx.makeImage()!
    let url = URL(fileURLWithPath: "\(outdir)/text_\(i).png") as CFURL
    let dest = CGImageDestinationCreateWithURL(url, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(dest, img, nil)
    CGImageDestinationFinalize(dest)
    print("text_\(i).png  size \(t.size) (\(Int(em)) px)  \(lines.count) line(s)  box \(Int(boxW))x\(Int(boxH)) px  \(t.text.replacingOccurrences(of: "\n", with: " ⏎ "))")
}
