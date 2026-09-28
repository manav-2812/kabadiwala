"""
generate_pwa_icons.py — Generate high-resolution PWA icons for Kabadiwala Connect (§2.3)
Generates:
  - web/public/icons/icon-192x192.png (any)
  - web/public/icons/icon-512x512.png (any)
  - web/public/icons/icon-maskable-512x512.png (maskable, safe-zone padded)
"""

import os
from PIL import Image, ImageDraw

ICONS_DIR = os.path.join(os.path.dirname(__file__), "..", "web", "public", "icons")
os.makedirs(ICONS_DIR, exist_ok=True)

# Theme colors
BG_COLOR = (11, 61, 46, 255)       # #0B3D2E deep forest green
GOLD_COLOR = (233, 163, 16, 255)   # #E9A310 recycling gold
GREEN_ACC = (46, 158, 91, 255)     # #2E9E5B vibrant emerald
WHITE_COLOR = (255, 255, 255, 255)

def draw_logo(size: int, is_maskable: bool = False) -> Image.Image:
    # 4x supersampling for ultra-crisp antialiased edges
    scale = 4
    canvas_size = size * scale
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # In maskable icons, background extends 100% edge-to-edge, graphic scaled to 75% for safe zone
    if is_maskable:
        draw.rectangle([0, 0, canvas_size, canvas_size], fill=BG_COLOR)
        margin = int(canvas_size * 0.15)
        box_w = canvas_size - 2 * margin
        box_h = canvas_size - 2 * margin
        ox = margin
        oy = margin
    else:
        # Standard icon: rounded rect with subtle padding
        r = int(canvas_size * 0.22)
        pad = int(canvas_size * 0.04)
        draw.rounded_rectangle([pad, pad, canvas_size - pad, canvas_size - pad], radius=r, fill=BG_COLOR)
        ox = pad
        oy = pad
        box_w = canvas_size - 2 * pad
        box_h = canvas_size - 2 * pad

    # Normalized coordinates inside box_w, box_h (viewBox 0 0 100 100)
    def px(x_pct: float) -> float:
        return ox + (x_pct / 100.0) * box_w

    def py(y_pct: float) -> float:
        return oy + (y_pct / 100.0) * box_h

    # Glow / subtle circle
    glow_r = (32.0 / 100.0) * box_w
    cx, cy = px(50), py(50)
    glow_color = (46, 158, 91, 50)
    draw.ellipse([cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r], fill=glow_color)

    # Gold triangle
    stroke_w = int((6.0 / 100.0) * box_w)
    p1 = (px(50), py(24))
    p2 = (px(72), py(68))
    p3 = (px(28), py(68))

    draw.line([p1, p2, p3, p1], fill=GOLD_COLOR, width=stroke_w, joint="curve")

    # Center dot
    dot_r = (7.0 / 100.0) * box_w
    dot_cx, dot_cy = px(50), py(54)
    draw.ellipse([dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r], fill=GREEN_ACC)

    # White horizontal base bar
    bar_w = int((4.0 / 100.0) * box_w)
    draw.line([(px(38), py(74)), (px(62), py(74))], fill=WHITE_COLOR, width=bar_w)

    # Downsample with Lanczos filter for crisp antialiasing
    final_img = img.resize((size, size), Image.Resampling.LANCZOS)
    return final_img

# Generate the three standard PWA icons
icon_192 = draw_logo(192, is_maskable=False)
icon_192.save(os.path.join(ICONS_DIR, "icon-192x192.png"), "PNG")
print(f"Generated {os.path.join(ICONS_DIR, 'icon-192x192.png')}")

icon_512 = draw_logo(512, is_maskable=False)
icon_512.save(os.path.join(ICONS_DIR, "icon-512x512.png"), "PNG")
print(f"Generated {os.path.join(ICONS_DIR, 'icon-512x512.png')}")

icon_maskable = draw_logo(512, is_maskable=True)
icon_maskable.save(os.path.join(ICONS_DIR, "icon-maskable-512x512.png"), "PNG")
print(f"Generated {os.path.join(ICONS_DIR, 'icon-maskable-512x512.png')}")
