"""
Generate neutral procedural placeholder SVG images for all 10 e-waste materials.
Each image clearly displays the material name, icon, and 'DEMO PLACEHOLDER' watermark.
Complies with Section 6.4 (no copyrighted web scrape, size < 150KB).
"""
import os

MATERIALS = [
    ("PCB", "Circuit Boards (PCB)", "#059669", "#064e3b", "CPU"),
    ("BATTERY_LI", "Lithium-Ion Batteries", "#d97706", "#78350f", "BAT"),
    ("MAGNET", "Rare-Earth Magnets", "#dc2626", "#7f1d1d", "MAG"),
    ("CRT", "CRT Monitors & TV Glass", "#4b5563", "#1f2937", "CRT"),
    ("LCD", "LCD / LED Displays", "#2563eb", "#1e3a8a", "LCD"),
    ("CABLES", "Copper Cables & Wires", "#ea580c", "#7c2d12", "CBL"),
    ("MOTORS", "Electric Motors & Compressors", "#0891b2", "#164e63", "MTR"),
    ("BATTERY_LEAD", "Lead Acid Batteries", "#9333ea", "#581c87", "LEAD"),
    ("PLASTIC_MIX", "Mixed E-Waste Plastics", "#65a30d", "#365314", "PLS"),
    ("COPPER_WIRE", "Clean Stripped Copper Wire", "#b45309", "#78350f", "CU")
]

def generate_svg(code: str, name: str, color: str, dark_color: str, tag: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="400" height="300">
  <defs>
    <linearGradient id="bg_{code}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#18181b"/>
      <stop offset="100%" stop-color="#27272a"/>
    </linearGradient>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>
    </pattern>
  </defs>

  <!-- Background -->
  <rect width="400" height="300" fill="url(#bg_{code})" rx="12"/>
  <rect width="400" height="300" fill="url(#grid)" rx="12"/>

  <!-- Border accent -->
  <rect x="2" y="2" width="396" height="296" fill="none" stroke="{color}" stroke-width="2" opacity="0.3" rx="10"/>

  <!-- Center Badge / Icon Container -->
  <rect x="140" y="70" width="120" height="90" rx="16" fill="{dark_color}" stroke="{color}" stroke-width="2"/>
  <text x="200" y="125" font-family="system-ui, -apple-system, sans-serif" font-size="32" font-weight="bold" fill="#ffffff" text-anchor="middle" dominant-baseline="middle">{tag}</text>

  <!-- Material Label -->
  <text x="200" y="195" font-family="system-ui, -apple-system, sans-serif" font-size="18" font-weight="600" fill="#f4f4f5" text-anchor="middle">{name}</text>
  <text x="200" y="218" font-family="system-ui, -apple-system, sans-serif" font-size="12" fill="#a1a1aa" text-anchor="middle">Material Code: {code}</text>

  <!-- Watermark / Demo Disclaimer -->
  <rect x="90" y="248" width="220" height="24" rx="6" fill="rgba(0,0,0,0.6)" stroke="rgba(255,255,255,0.1)"/>
  <text x="200" y="264" font-family="system-ui, -apple-system, sans-serif" font-size="10" font-weight="600" fill="#fbbf24" text-anchor="middle" letter-spacing="1">DEMO PLACEHOLDER PHOTO</text>
</svg>"""

def main():
    dirs = [
        os.path.join("d:", os.sep, "PROJECTS", "kabadiwala", "web", "public", "photos"),
        os.path.join("d:", os.sep, "PROJECTS", "kabadiwala", "seed", "photos", "placeholders")
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    for code, name, color, dark_color, tag in MATERIALS:
        content = generate_svg(code, name, color, dark_color, tag)
        for d in dirs:
            file_path = os.path.join(d, f"placeholder_{code.lower()}.svg")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Generated {file_path} ({len(content)} bytes)")

if __name__ == "__main__":
    main()
