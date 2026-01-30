from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

assets = Path("assets")
assets.mkdir(exist_ok=True)
size = 512
bg = (15, 23, 42)  # #0f172a
accent = (56, 189, 248)  # #38bdf8
text = (229, 231, 235)  # #e5e7eb

img = Image.new("RGBA", (size, size), bg)
draw = ImageDraw.Draw(img)

margin = 48
ring_box = [margin, margin, size - margin, size - margin]
draw.ellipse(ring_box, outline=accent, width=16)

inner_margin = 96
inner_box = [inner_margin, inner_margin, size - inner_margin, size - inner_margin]
draw.rounded_rectangle(inner_box, radius=48, fill=(17, 24, 39), outline=(31, 41, 68), width=6)

try:
    font = ImageFont.truetype("arial.ttf", 180)
except Exception:
    font = ImageFont.load_default()

text_value = "IA"
text_bbox = draw.textbbox((0, 0), text_value, font=font)
text_w = text_bbox[2] - text_bbox[0]
text_h = text_bbox[3] - text_bbox[1]
text_x = (size - text_w) // 2
text_y = (size - text_h) // 2 - 12

draw.text((text_x, text_y), text_value, fill=text, font=font)

png_path = assets / "infinity_alamo_demo.png"
ico_path = assets / "infinity_alamo_demo.ico"
img.save(png_path)
sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
img.save(ico_path, sizes=sizes)

print("Wrote", png_path, "and", ico_path)
