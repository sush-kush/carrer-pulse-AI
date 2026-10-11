"""
Patch all existing page files to use the new design system tokens.
Run once: python patch_pages.py
"""
import os, re

PAGES_DIR = "pages"


def _fix_ui_import(existing: str) -> str:
    """Ensure CHART_LAYOUT and section_label are in the ui_components import."""
    needs = ["CHART_LAYOUT", "section_label"]
    items = [x.strip() for x in existing.split(",")]
    for need in needs:
        if need not in items:
            items.append(need)
    return f"from modules.ui_components import {', '.join(items)}"


# 1. Replace old _LAYOUT dict with import+use of CHART_LAYOUT
OLD_LAYOUT_DICT = '''_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#9ca3c0", family="Inter"),
    margin=dict(l=10, r=10, t=30, b=10),
)'''

# 2. Old import line patterns to extend
OLD_IMPORT_UI = "from modules.ui_components import page_header"

# 3. Old page_header call pattern: page_header("Title", "subtitle", "icon")
# New: page_header("Title", "subtitle", badge="BADGE")

files_patched = []

for fname in os.listdir(PAGES_DIR):
    if not fname.endswith(".py") or fname in ("__init__.py", "home.py"):
        continue
    
    path = os.path.join(PAGES_DIR, fname)
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    
    original = src
    
    # ── Replace _LAYOUT dict with CHART_LAYOUT import ─────────────────────
    src = re.sub(
        r'_LAYOUT = dict\(\s*paper_bgcolor="rgba\(0,0,0,0\)",\s*plot_bgcolor="rgba\(0,0,0,0\)",\s*font=dict\(color="#9ca3c0", family="Inter"\),\s*margin=dict\(l=10, r=10, t=30, b=10\),\s*\)',
        '',
        src,
        flags=re.DOTALL,
    )
    
    # ── Add CHART_LAYOUT to ui_components import ───────────────────────────
    src = re.sub(
        r'from modules\.ui_components import (page_header[^\n]*)',
        lambda m: _fix_ui_import(m.group(1)),
        src,
    )
    
    # ── Replace **_LAYOUT with **CHART_LAYOUT ─────────────────────────────
    src = src.replace("**_LAYOUT,", "**CHART_LAYOUT,")
    src = src.replace("**_LAYOUT)", "**CHART_LAYOUT)")
    
    # ── Replace page_header(title, sub, icon) → page_header(title, sub, badge=icon) ──
    # pattern: page_header("...", "...", "icon_text")
    src = re.sub(
        r'page_header\("([^"]*)",\s*"([^"]*)",\s*"([^"]*)"\)',
        r'page_header("\1", "\2", badge="\3")',
        src,
    )
    
    # ── Replace old score-bar CSS classes ─────────────────────────────────
    src = src.replace('"score-bar-outer"', '"cp-bar-outer"')
    src = src.replace('"score-bar-inner"', '"cp-bar-inner"')
    
    # ── Replace old disclaimer CSS class ──────────────────────────────────
    src = src.replace('"disclaimer"', '"cp-disclaimer"')
    
    # ── Replace old chat bubble classes ───────────────────────────────────
    src = src.replace('"chat-user"', '"cp-chat-user"')
    src = src.replace('"chat-ai"', '"cp-chat-ai"')
    src = src.replace('"chat-ai-label"', '"cp-chat-ai-badge"')
    
    # ── Replace old kpi-card class ─────────────────────────────────────────
    # We do NOT replace kpi_card() function call args because new signature differs
    # Just update the class name in raw HTML if any
    src = src.replace('class="kpi-card"', 'class="cp-kpi"')
    src = src.replace('class="kpi-value"', 'class="cp-kpi-val"')
    src = src.replace('class="kpi-label"', 'class="cp-kpi-label"')
    
    # ── Replace old skill pill classes ─────────────────────────────────────
    src = src.replace('"skill-pill skill-pill-present"', '"cp-pill cp-pill-green"')
    src = src.replace('"skill-pill skill-pill-missing"', '"cp-pill cp-pill-red"')
    src = src.replace('"skill-pill"', '"cp-pill cp-pill-blue"')
    
    # ── Remove duplicate blank lines ───────────────────────────────────────
    src = re.sub(r'\n{4,}', '\n\n\n', src)
    
    if src != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(src)
        files_patched.append(fname)

print(f"Patched {len(files_patched)} files:")
for f in files_patched:
    print(f"  ✓ {f}")
