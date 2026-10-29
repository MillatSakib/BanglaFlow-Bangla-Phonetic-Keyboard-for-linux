#!/usr/bin/env python3
"""Generate high-resolution PNG cheat sheet for BanglaFlow keyboard mappings."""

import subprocess
import tempfile
from pathlib import Path

HTML_CONTENT = """<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@500;600&family=Noto+Sans+Bengali:wght@400;600;700;800&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1400px;
    background: linear-gradient(135deg, #090d16 0%, #0f172a 100%);
    font-family: 'Noto Sans Bengali', -apple-system, sans-serif;
    color: #f1f5f9;
    padding: 36px 40px;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #1e293b;
    padding-bottom: 20px;
    margin-bottom: 28px;
  }
  .title-group h1 {
    font-size: 32px;
    font-weight: 800;
    color: #38bdf8;
    letter-spacing: -0.5px;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .title-group h1 span {
    color: #10b981;
  }
  .title-group p {
    font-size: 15px;
    color: #94a3b8;
    margin-top: 4px;
  }
  .badges {
    display: flex;
    gap: 10px;
  }
  .badge {
    background: #1e293b;
    border: 1px solid #334155;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    color: #38bdf8;
  }
  .badge.green { color: #34d399; border-color: #059669; background: #064e3b33; }

  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 22px;
  }
  .grid-full {
    grid-column: span 2;
  }

  .card {
    background: #111827cc;
    border: 1px solid #1f2937;
    border-radius: 14px;
    padding: 20px 22px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
  }
  .card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid #1f2937;
  }
  .card-icon {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 700;
  }
  .card-title {
    font-size: 18px;
    font-weight: 700;
    color: #f8fafc;
  }

  /* Table styling */
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th {
    text-align: left;
    font-size: 12px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding-bottom: 8px;
    border-bottom: 1px solid #1e293b;
  }
  td {
    padding: 6px 4px;
    font-size: 15px;
    border-bottom: 1px solid #1e293b33;
  }

  /* Key badge */
  kbd, .key {
    display: inline-block;
    font-family: 'Fira Code', monospace;
    font-size: 13px;
    font-weight: 600;
    background: #1e293b;
    border: 1px solid #334155;
    color: #f59e0b;
    padding: 3px 8px;
    border-radius: 5px;
    box-shadow: 0 2px 0 #0f172a;
    margin: 1px 2px;
  }
  .bn {
    font-weight: 700;
    font-size: 18px;
    color: #f1f5f9;
  }
  .kar {
    color: #38bdf8;
    font-weight: 700;
    font-size: 18px;
  }

  /* Consonant Grid */
  .consonant-group {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 8px;
    margin-bottom: 12px;
  }
  .consonant-box {
    background: #0f172a80;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 8px 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }
  .consonant-box .char {
    font-size: 22px;
    font-weight: 700;
    color: #38bdf8;
  }

  /* Pills Grid */
  .pills-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
  }
  .pill-item {
    background: #0f172a80;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 8px 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .footer {
    margin-top: 24px;
    padding-top: 16px;
    border-top: 1px solid #1e293b;
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    color: #64748b;
  }
</style>
</head>
<body>

<div class="header">
  <div class="title-group">
    <h1>BanglaFlow <span>(বাংলাফ্লো)</span> Phonetic Layout</h1>
    <p>Complete Bengali Character & Keystroke Mapping Reference Guide (IBus Linux / Wayland & X11)</p>
  </div>
  <div class="badges">
    <span class="badge green">● IBus Native</span>
    <span class="badge">Avro Phonetic Compatible</span>
    <span class="badge">100% Offline & Pure</span>
  </div>
</div>

<div class="grid">

  <!-- VOWELS & KAR -->
  <div class="card">
    <div class="card-header">
      <div class="card-icon" style="background: #0284c722; color: #38bdf8;">অ</div>
      <div class="card-title">স্বরবর্ণ ও স্বরচিহ্ন (Vowels & Matra/Kar)</div>
    </div>
    <table>
      <thead>
        <tr>
          <th>বর্ণ</th>
          <th>কার</th>
          <th>টাইপিং কী (Keys)</th>
          <th>উদাহরণ (Example)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><span class="bn">অ</span></td>
          <td><span style="color:#64748b;">—</span></td>
          <td><span class="key">o</span> / <span class="key">a</span></td>
          <td>onek → অনেক</td>
        </tr>
        <tr>
          <td><span class="bn">আ</span></td>
          <td><span class="kar">া</span></td>
          <td><span class="key">a</span> / <span class="key">A</span> / <span class="key">aa</span></td>
          <td>amar → আমার, gan → গান</td>
        </tr>
        <tr>
          <td><span class="bn">ই</span></td>
          <td><span class="kar">ি</span></td>
          <td><span class="key">i</span></td>
          <td>iti → ইতি, likhi → লিখি</td>
        </tr>
        <tr>
          <td><span class="bn">ঈ</span></td>
          <td><span class="kar">ী</span></td>
          <td><span class="key">I</span> / <span class="key">ee</span></td>
          <td>Ishor → ঈশ্বর, nodI → নদী</td>
        </tr>
        <tr>
          <td><span class="bn">উ</span></td>
          <td><span class="kar">ু</span></td>
          <td><span class="key">u</span></td>
          <td>upor → উপর, tumi → তুমি</td>
        </tr>
        <tr>
          <td><span class="bn">ঊ</span></td>
          <td><span class="kar">ূ</span></td>
          <td><span class="key">U</span> / <span class="key">oo</span></td>
          <td>Usha → ঊষা, mUlo → মূলো</td>
        </tr>
        <tr>
          <td><span class="bn">ঋ</span></td>
          <td><span class="kar">ৃ</span></td>
          <td><span class="key">rri</span></td>
          <td>rritu → ঋতু, krriShi → কৃষি</td>
        </tr>
        <tr>
          <td><span class="bn">এ</span></td>
          <td><span class="kar">ে</span></td>
          <td><span class="key">e</span></td>
          <td>ekhon → এখন, desh → দেশ</td>
        </tr>
        <tr>
          <td><span class="bn">ঐ</span></td>
          <td><span class="kar">ৈ</span></td>
          <td><span class="key">OI</span></td>
          <td>OIkkho → ঐক্য, tOiri → তৈরি</td>
        </tr>
        <tr>
          <td><span class="bn">ও</span></td>
          <td><span class="kar">ো</span></td>
          <td><span class="key">O</span> / <span class="key">o`</span></td>
          <td>Oshudh → ওষুধ, kOno → কোনো</td>
        </tr>
        <tr>
          <td><span class="bn">ঔ</span></td>
          <td><span class="kar">ৌ</span></td>
          <td><span class="key">OU</span></td>
          <td>OUshodh → ঔষধ, nOUka → নৌকা</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- CONSONANTS -->
  <div class="card">
    <div class="card-header">
      <div class="card-icon" style="background: #10b98122; color: #10b981;">ক</div>
      <div class="card-title">ব্যঞ্জনবর্ণ (Consonants)</div>
    </div>

    <!-- ক বর্গ -->
    <div class="consonant-group">
      <div class="consonant-box"><span class="char">ক</span><span class="key">k</span></div>
      <div class="consonant-box"><span class="char">খ</span><span class="key">kh</span></div>
      <div class="consonant-box"><span class="char">গ</span><span class="key">g</span></div>
      <div class="consonant-box"><span class="char">ঘ</span><span class="key">gh</span></div>
      <div class="consonant-box"><span class="char">ঙ</span><span class="key">Ng</span></div>
    </div>

    <!-- চ বর্গ -->
    <div class="consonant-group">
      <div class="consonant-box"><span class="char">চ</span><span class="key">c / ch</span></div>
      <div class="consonant-box"><span class="char">ছ</span><span class="key">ch / chh</span></div>
      <div class="consonant-box"><span class="char">জ</span><span class="key">j</span></div>
      <div class="consonant-box"><span class="char">ঝ</span><span class="key">jh</span></div>
      <div class="consonant-box"><span class="char">ঞ</span><span class="key">NG</span></div>
    </div>

    <!-- ট বর্গ -->
    <div class="consonant-group">
      <div class="consonant-box"><span class="char">ট</span><span class="key">T</span></div>
      <div class="consonant-box"><span class="char">ঠ</span><span class="key">Th</span></div>
      <div class="consonant-box"><span class="char">ড</span><span class="key">D</span></div>
      <div class="consonant-box"><span class="char">ঢ</span><span class="key">Dh</span></div>
      <div class="consonant-box"><span class="char">ণ</span><span class="key">N</span></div>
    </div>

    <!-- ত বর্গ -->
    <div class="consonant-group">
      <div class="consonant-box"><span class="char">ত</span><span class="key">t</span></div>
      <div class="consonant-box"><span class="char">থ</span><span class="key">th</span></div>
      <div class="consonant-box"><span class="char">দ</span><span class="key">d</span></div>
      <div class="consonant-box"><span class="char">ধ</span><span class="key">dh</span></div>
      <div class="consonant-box"><span class="char">ন</span><span class="key">n</span></div>
    </div>

    <!-- প বর্গ -->
    <div class="consonant-group">
      <div class="consonant-box"><span class="char">প</span><span class="key">p</span></div>
      <div class="consonant-box"><span class="char">ফ</span><span class="key">f / ph</span></div>
      <div class="consonant-box"><span class="char">ব</span><span class="key">b</span></div>
      <div class="consonant-box"><span class="char">ভ</span><span class="key">bh / v</span></div>
      <div class="consonant-box"><span class="char">ম</span><span class="key">m</span></div>
    </div>

    <!-- অবশিষ্ট ও বিশেষ ব্যঞ্জনবর্ণ -->
    <div class="consonant-group" style="grid-template-columns: repeat(6, 1fr); margin-bottom: 8px;">
      <div class="consonant-box"><span class="char">য</span><span class="key">z</span></div>
      <div class="consonant-box"><span class="char">র</span><span class="key">r</span></div>
      <div class="consonant-box"><span class="char">ল</span><span class="key">l</span></div>
      <div class="consonant-box"><span class="char">শ</span><span class="key">S / sh</span></div>
      <div class="consonant-box"><span class="char">ষ</span><span class="key">Sh</span></div>
      <div class="consonant-box"><span class="char">স</span><span class="key">s</span></div>
    </div>

    <div class="consonant-group" style="grid-template-columns: repeat(5, 1fr); margin-bottom: 0;">
      <div class="consonant-box"><span class="char">হ</span><span class="key">h</span></div>
      <div class="consonant-box"><span class="char">ড়</span><span class="key">R</span></div>
      <div class="consonant-box"><span class="char">ঢ়</span><span class="key">Rh</span></div>
      <div class="consonant-box"><span class="char">য়</span><span class="key">y / Y</span></div>
      <div class="consonant-box"><span class="char">ৎ</span><span class="key">t`` / tt</span></div>
    </div>
  </div>

  <!-- SPECIAL CHARACTERS & PUNCTUATION -->
  <div class="card">
    <div class="card-header">
      <div class="card-icon" style="background: #f59e0b22; color: #f59e0b;">৳</div>
      <div class="card-title">বিশেষ চিহ্ন ও বিরামচিহ্ন (Marks & Punctuation)</div>
    </div>
    <div class="pills-grid" style="grid-template-columns: repeat(2, 1fr);">
      <div class="pill-item">
        <span>অনুস্বার (<span class="bn">ং</span>)</span>
        <span class="key">ng</span>
      </div>
      <div class="pill-item">
        <span>বিসর্গ (<span class="bn">ঃ</span>)</span>
        <span class="key">:</span>
      </div>
      <div class="pill-item">
        <span>চন্দ্রবিন্দু (<span class="bn">ঁ</span>)</span>
        <span class="key">^</span>
      </div>
      <div class="pill-item">
        <span>হসন্ত (<span class="bn">্</span>)</span>
        <span class="key">,,</span> বা <span class="key">`</span>
      </div>
      <div class="pill-item">
        <span>দাঁড়ি (<span class="bn">।</span>)</span>
        <span class="key">.</span>
      </div>
      <div class="pill-item">
        <span>দ্বিদাঁড়ি (<span class="bn">॥</span>)</span>
        <span class="key">..</span>
      </div>
      <div class="pill-item">
        <span>টাকা (<span class="bn">৳</span>)</span>
        <span class="key">$</span>
      </div>
      <div class="pill-item">
        <span>যুক্তাক্ষর রোধ</span>
        <span class="key">k`kh → কখ</span>
      </div>
    </div>

    <!-- DIGITS -->
    <div style="margin-top: 18px; padding-top: 14px; border-top: 1px solid #1e293b;">
      <div style="font-size: 14px; font-weight: 700; color: #94a3b8; margin-bottom: 10px;">
        বাংলা সংখ্যা (Bengali Digits & NumPad Supported)
      </div>
      <div style="display: flex; gap: 8px;">
        <div class="consonant-box" style="flex: 1;"><span class="char">০</span><span class="key">0</span></div>
        <div class="consonant-box" style="flex: 1;"><span class="char">১</span><span class="key">1</span></div>
        <div class="consonant-box" style="flex: 1;"><span class="char">২</span><span class="key">2</span></div>
        <div class="consonant-box" style="flex: 1;"><span class="char">৩</span><span class="key">3</span></div>
        <div class="consonant-box" style="flex: 1;"><span class="char">৪</span><span class="key">4</span></div>
        <div class="consonant-box" style="flex: 1;"><span class="char">৫</span><span class="key">5</span></div>
        <div class="consonant-box" style="flex: 1;"><span class="char">৬</span><span class="key">6</span></div>
        <div class="consonant-box" style="flex: 1;"><span class="char">৭</span><span class="key">7</span></div>
        <div class="consonant-box" style="flex: 1;"><span class="char">৮</span><span class="key">8</span></div>
        <div class="consonant-box" style="flex: 1;"><span class="char">৯</span><span class="key">9</span></div>
      </div>
    </div>
  </div>

  <!-- CONJUNCTS & SPECIAL COMBINATIONS -->
  <div class="card">
    <div class="card-header">
      <div class="card-icon" style="background: #a855f722; color: #c084fc;">ক্ষ</div>
      <div class="card-title">সাধারণ যুক্তাক্ষর ও নিয়মাবলী (Common Conjuncts)</div>
    </div>
    <div class="pills-grid" style="grid-template-columns: repeat(2, 1fr);">
      <div class="pill-item">
        <span>ক্ষ (ক+ষ)</span>
        <span class="key">kSh</span>
      </div>
      <div class="pill-item">
        <span>জ্ঞ (জ+ঞ)</span>
        <span class="key">jG / jNG</span>
      </div>
      <div class="pill-item">
        <span>ঞ্চ (ঞ+চ)</span>
        <span class="key">nch / NGc</span>
      </div>
      <div class="pill-item">
        <span>ঞ্জ (ঞ+জ)</span>
        <span class="key">nj / NGj</span>
      </div>
      <div class="pill-item">
        <span>ষ্ণ (ষ+ণ)</span>
        <span class="key">ShN</span>
      </div>
      <div class="pill-item">
        <span>ঙ্ক (ঙ+ক)</span>
        <span class="key">ngk / Ngk</span>
      </div>
      <div class="pill-item">
        <span>ঙ্গ (ঙ+গ)</span>
        <span class="key">ngg / Ngg</span>
      </div>
      <div class="pill-item">
        <span>হ্ম (হ+ম)</span>
        <span class="key">hm / hM</span>
      </div>
      <div class="pill-item">
        <span>রেফ (র্ক)</span>
        <span class="key">rrk (rr+consonant)</span>
      </div>
      <div class="pill-item">
        <span>র-ফলা (ক্র)</span>
        <span class="key">kr (consonant+r)</span>
      </div>
      <div class="pill-item">
        <span>য-ফলা (ক্য)</span>
        <span class="key">ky / kZ</span>
      </div>
      <div class="pill-item">
        <span>ঋ-কার (কৃ)</span>
        <span class="key">krri</span>
      </div>
    </div>

    <div style="margin-top: 14px; background: #0f172a80; border: 1px solid #1e293b; border-radius: 8px; padding: 10px 14px; font-size: 13px; color: #94a3b8;">
      💡 <strong style="color: #38bdf8;">টিপস:</strong> যে কোনো দুটি বর্ণের মাঝে <span class="key">`</span> (Backtick) দিলে যুক্তাক্ষর তৈরি বন্ধ হয়ে বর্ণ দুটি আলাদা থাকবে (যেমন: <span class="key">k`kh</span> → <strong style="color: #f1f5f9;">কখ</strong>)।
    </div>
  </div>

</div>

<div class="footer">
  <div>BanglaFlow Bengali Phonetic Input Method — Ubuntu GNOME Linux (IBus Native)</div>
  <div>Candidate navigation: <span class="key">↑</span> <span class="key">↓</span> | Selection: <span class="key">1-9</span>, <span class="key">Space</span>, <span class="key">Enter</span></div>
</div>

</body>
</html>
"""


def main():
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / "docs" / "images"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_png = out_dir / "banglaflow-keyboard-layout.png"

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(HTML_CONTENT)
        tmp_html = f.name

    try:
        cmd = [
            "google-chrome",
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            "--force-device-scale-factor=2",
            f"--screenshot={out_png}",
            "--window-size=1400,1500",
            tmp_html,
        ]
        subprocess.run(cmd, check=True)
        print(f"Generated cheat sheet successfully: {out_png}")
    finally:
        Path(tmp_html).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
