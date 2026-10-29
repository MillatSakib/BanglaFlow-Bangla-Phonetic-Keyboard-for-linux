#!/usr/bin/env python3
"""Generate modern, professional vector and multi-resolution PNG icons for BanglaFlow."""

import subprocess
import tempfile
from pathlib import Path
from PIL import Image

SVG_CONTENT = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <!-- Background Gradient: Deep Oceanic Slate into Emerald Dark -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b132b" />
      <stop offset="50%" stop-color="#0f172a" />
      <stop offset="100%" stop-color="#022c22" />
    </linearGradient>

    <!-- Glowing Text Gradient: Electric Cyan into Vibrant Emerald -->
    <linearGradient id="textGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8" />
      <stop offset="45%" stop-color="#2dd4bf" />
      <stop offset="100%" stop-color="#34d399" />
    </linearGradient>

    <!-- Border Accent Gradient -->
    <linearGradient id="borderGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.8" />
      <stop offset="50%" stop-color="#2dd4bf" stop-opacity="0.3" />
      <stop offset="100%" stop-color="#10b981" stop-opacity="0.7" />
    </linearGradient>

    <!-- Flow Stream Wave Gradient -->
    <linearGradient id="waveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.1" />
      <stop offset="50%" stop-color="#2dd4bf" stop-opacity="0.85" />
      <stop offset="100%" stop-color="#34d399" stop-opacity="0.2" />
    </linearGradient>

    <!-- Soft Glow Filter -->
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="10" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- Background Squircle with Precision Rounded Corners -->
  <rect x="18" y="18" width="476" height="476" rx="108" fill="url(#bgGrad)" stroke="url(#borderGrad)" stroke-width="4.5" />

  <!-- Inner Subtle Glassmorphism Highlight -->
  <rect x="34" y="34" width="444" height="444" rx="92" fill="#ffffff" fill-opacity="0.025" stroke="#ffffff" stroke-opacity="0.08" stroke-width="1.5" />

  <!-- Dynamic Fluid Waves (Symbolizing 'Flow' of Typing) -->
  <path d="M 50 365 C 130 320, 200 415, 305 372 C 375 342, 420 375, 465 352" fill="none" stroke="url(#waveGrad)" stroke-width="7" stroke-linecap="round" opacity="0.75" />
  <path d="M 65 392 C 145 352, 215 435, 315 398 C 385 372, 425 395, 455 385" fill="none" stroke="url(#waveGrad)" stroke-width="3.5" stroke-linecap="round" opacity="0.45" />

  <!-- Central Bengali Letter 'বা' with Radiant Gradient & Glow -->
  <g filter="url(#glow)">
    <text x="256" y="326" text-anchor="middle" font-family="'Noto Sans Bengali', 'Mukti', sans-serif" font-size="246" font-weight="800" fill="url(#textGrad)">বা</text>
  </g>

  <!-- AI / Speed Kinetic Particle -->
  <circle cx="392" cy="136" r="9" fill="#38bdf8" filter="url(#glow)" />
  <circle cx="392" cy="136" r="4.5" fill="#ffffff" />
</svg>
"""


def main():
    repo_root = Path(__file__).resolve().parent.parent
    icons_dir = repo_root / "data" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)

    svg_path = icons_dir / "banglaflow.svg"
    svg_path.write_text(SVG_CONTENT, encoding="utf-8")
    print(f"Saved SVG to: {svg_path}")

    # Render master high-res PNG (1024x1024) via Chrome Headless
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as tmp:
        tmp.write(SVG_CONTENT)
        tmp_svg = tmp.name

    master_png = Path(tempfile.gettempdir()) / "banglaflow_master_1024.png"

    try:
        cmd = [
            "google-chrome",
            "--headless",
            "--disable-gpu",
            "--default-background-color=00000000",
            f"--screenshot={master_png}",
            "--window-size=512,512",
            "--force-device-scale-factor=2",
            f"file://{tmp_svg}",
        ]
        subprocess.run(cmd, check=True)

        im = Image.open(master_png)

        # Generate all standard resolutions
        sizes = [
            (512, "banglaflow-512.png"),
            (256, "banglaflow-256.png"),
            (128, "banglaflow-128.png"),
            (64, "banglaflow-64.png"),
            (48, "banglaflow.png"),      # Primary IBus & desktop icon
            (32, "banglaflow-32.png"),
            (24, "banglaflow-24.png"),
        ]

        for size, filename in sizes:
            out_file = icons_dir / filename
            resized = im.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(out_file, format="PNG", optimize=True)
            print(f"Generated {size}x{size} icon -> {out_file}")

    finally:
        Path(tmp_svg).unlink(missing_ok=True)
        master_png.unlink(missing_ok=True)


if __name__ == "__main__":
    main()

