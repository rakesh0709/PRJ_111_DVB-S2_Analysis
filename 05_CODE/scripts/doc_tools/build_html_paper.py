"""
PRJ_111 IEEE Research Paper HTML Generator
Produces an authentic, publication-grade IEEE two-column HTML research paper.
Reads paper_template.html and substitutes base64 assets.
"""

import os
import base64
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
REPORTS_DIR = BASE_DIR / "07_DOCUMENTATION" / "RESEARCH_PAPER"
ASSETS_DIR = REPORTS_DIR / "assets"
TEMPLATE_PATH = REPORTS_DIR / "paper_template.html"
MD_PATH = REPORTS_DIR / "PRJ_111_RESEARCH_PAPER_DRAFT.md"
HTML_OUTPUT_PATH = REPORTS_DIR / "PRJ_111_RESEARCH_PAPER_DRAFT.html"
ARTIFACT_DIR = REPORTS_DIR / "assets"

def get_base64_image(filename):
    img_path = ASSETS_DIR / filename
    if not img_path.exists():
        img_path = ARTIFACT_DIR / filename
    if not img_path.exists():
        print(f"Warning: {filename} not found!")
        return ""
    ext = img_path.suffix.lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    with open(img_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{data}"

print("Encoding image assets...")
b64_map = {
    "__ASSET_ARCH__": get_base64_image("architecture_diagram.png"),
    "__ASSET_FIG2__": get_base64_image("fig2_dashboard_empty.png"),
    "__ASSET_FIG3__": get_base64_image("fig_dashboard_analyzed.png"),
    "__ASSET_FIG4__": get_base64_image("fig_comparison_view.png"),
    "__ASSET_FIG5__": get_base64_image("fig_timeline_view.png"),
    "__ASSET_FIG6__": get_base64_image("fig_anomaly_view.png"),
    "__ASSET_FIG7__": get_base64_image("fig_report_view.png"),
    "__ASSET_SAMAD__": get_base64_image("author_samad.jpg"),
    "__ASSET_VENGALA__": get_base64_image("author_vengala_rao.jpg"),
    "__ASSET_RAKESHWAR__": get_base64_image("author_rakeshwar.jpg"),
    "__ASSET_TEAM__": get_base64_image("team_presentation.jpg"),
}

for k, v in b64_map.items():
    print(f"  {k}: {len(v)} chars")

print(f"Reading template from {TEMPLATE_PATH}...")
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

print("Substituting asset placeholders...")
for placeholder, b64_str in b64_map.items():
    if placeholder not in content:
        print(f"Warning: {placeholder} not found in template!")
    content = content.replace(placeholder, b64_str)

print(f"Writing output to {HTML_OUTPUT_PATH}...")
with open(HTML_OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(content)

size_mb = HTML_OUTPUT_PATH.stat().st_size / (1024 * 1024)
print(f"HTML paper generated successfully: {size_mb:.2f} MB ({HTML_OUTPUT_PATH.stat().st_size} bytes)")

# Also copy to brain artifact directory
artifact_html = ARTIFACT_DIR / "PRJ_111_RESEARCH_PAPER_DRAFT.html"
with open(artifact_html, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Copied HTML to artifact directory: {artifact_html}")

artifact_md = ARTIFACT_DIR / "PRJ_111_RESEARCH_PAPER_DRAFT.md"
with open(MD_PATH, "r", encoding="utf-8") as f_in:
    with open(artifact_md, "w", encoding="utf-8") as f_out:
        f_out.write(f_in.read())
print(f"Copied markdown to artifact directory: {artifact_md}")
print("ALL DONE.")
