"""
Generate end-to-end flow diagrams for Oracle HRMS v2 Architecture.
Produces a multi-page PDF with 6 diagrams.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
from matplotlib.gridspec import GridSpec
import numpy as np
import os

OUT_DIR = r"c:\rev-eng1 test oracle new\automated-reverse-engineering-pipeline-main\automated-reverse-engineering-pipeline-main\docs"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Color Palette ─────────────────────────────────────────────────────────────
C = {
    "bg":         "#0F1117",
    "bg2":        "#1A1D27",
    "bg3":        "#22263A",
    "border":     "#2E3350",
    "red":        "#8B1A1A",
    "red2":       "#C0392B",
    "amber":      "#7D5A00",
    "amber2":     "#E67E22",
    "blue":       "#1A3A5C",
    "blue2":      "#2980B9",
    "blue3":      "#5DADE2",
    "purple":     "#4A235A",
    "purple2":    "#8E44AD",
    "purple3":    "#BB8FCE",
    "green":      "#1E4D2B",
    "green2":     "#27AE60",
    "green3":     "#82E0AA",
    "teal":       "#1A4A4A",
    "teal2":      "#17A589",
    "teal3":      "#76D7C4",
    "white":      "#FFFFFF",
    "gray":       "#8892A4",
    "gray2":      "#C0C8D8",
    "yellow":     "#FFD700",
    "orange":     "#FF8C00",
}

def setup_ax(fig, ax, title="", bg=None):
    bg = bg or C["bg"]
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    if title:
        ax.set_title(title, color=C["white"], fontsize=13, fontweight='bold',
                     pad=12, fontfamily='monospace')

def box(ax, x, y, w, h, label, sublabel="", fill=None, edge=None,
        fontsize=9, radius=0.015, bold=False, text_color=None):
    fill = fill or C["bg3"]
    edge = edge or C["border"]
    text_color = text_color or C["white"]
    rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                          boxstyle=f"round,pad=0,rounding_size={radius}",
                          facecolor=fill, edgecolor=edge, linewidth=1.5, zorder=3)
    ax.add_patch(rect)
    lbl = ax.text(x, y + (0.012 if sublabel else 0), label,
                  ha='center', va='center', fontsize=fontsize,
                  color=text_color, fontweight='bold' if bold else 'normal',
                  fontfamily='monospace', zorder=4, wrap=True)
    if sublabel:
        ax.text(x, y - 0.022, sublabel, ha='center', va='center',
                fontsize=fontsize - 1.5, color=C["gray2"],
                fontfamily='monospace', zorder=4)
    return rect

def arrow(ax, x1, y1, x2, y2, label="", color=None, style="->", lw=1.5):
    color = color or C["blue3"]
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color,
                                lw=lw, connectionstyle="arc3,rad=0.0"),
                zorder=2)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx + 0.01, my + 0.01, label, fontsize=7.5,
                color=color, fontfamily='monospace', zorder=5,
                bbox=dict(boxstyle='round,pad=0.2', facecolor=C["bg"], alpha=0.8, edgecolor='none'))

def curved_arrow(ax, x1, y1, x2, y2, label="", color=None, rad=0.2, lw=1.5):
    color = color or C["blue3"]
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=color,
                                lw=lw, connectionstyle=f"arc3,rad={rad}"),
                zorder=2)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx + 0.02, my, label, fontsize=7, color=color,
                fontfamily='monospace', zorder=5,
                bbox=dict(boxstyle='round,pad=0.2', facecolor=C["bg"], alpha=0.8, edgecolor='none'))

def phase_band(ax, x, y, w, h, label, color, alpha=0.12):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0,rounding_size=0.01",
                          facecolor=color, edgecolor=color,
                          linewidth=1, alpha=alpha, zorder=1)
    ax.add_patch(rect)
    ax.text(x + 0.008, y + h/2, label, ha='left', va='center',
            fontsize=7.5, color=color, fontweight='bold',
            fontfamily='monospace', zorder=2, rotation=90)

def legend_item(ax, x, y, color, label):
    rect = FancyBboxPatch((x, y), 0.025, 0.018,
                          boxstyle="round,pad=0,rounding_size=0.003",
                          facecolor=color, edgecolor=color, linewidth=1, zorder=3)
    ax.add_patch(rect)
    ax.text(x + 0.032, y + 0.009, label, ha='left', va='center',
            fontsize=7.5, color=C["gray2"], fontfamily='monospace')

# ══════════════════════════════════════════════════════════════════════════════
# DIAGRAM 1 — System Overview
# ══════════════════════════════════════════════════════════════════════════════
def diagram1():
    fig, ax = plt.subplots(figsize=(18, 11))
    setup_ax(fig, ax, "DIAGRAM 1 — Oracle HRMS v2 System Overview")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    # Title banner
    ax.add_patch(FancyBboxPatch((0.01, 0.92), 0.98, 0.065,
                  boxstyle="round,pad=0,rounding_size=0.01",
                  facecolor=C["red"], edgecolor=C["red2"], linewidth=2, zorder=3))
    ax.text(0.5, 0.953, "Oracle HRMS Reverse Engineering Pipeline  —  v2 Architecture",
            ha='center', va='center', fontsize=15, color=C["white"],
            fontweight='bold', fontfamily='monospace', zorder=4)

    # SOURCE LAYER
    phase_band(ax, 0.02, 0.73, 0.96, 0.16, "SOURCE", C["green2"])
    box(ax, 0.13, 0.81, 0.16, 0.06, "42 Source Files",
        "22 PL/SQL + 6 Forms + 14 SQL", C["green"], C["green2"], 8.5)
    box(ax, 0.35, 0.81, 0.14, 0.06, "file_cache.json",
        "382 KB — all 42 files", C["green"], C["green2"], 8.5)
    box(ax, 0.55, 0.81, 0.14, 0.06, "schema-catalogue.json",
        "103 KB — real DDL", C["green"], C["green2"], 8.5)
    box(ax, 0.75, 0.81, 0.14, 0.06, "implicit_rules.json",
        "310 rules", C["green"], C["green2"], 8.5)
    arrow(ax, 0.21, 0.81, 0.275, 0.81, color=C["green3"])
    arrow(ax, 0.42, 0.81, 0.475, 0.81, color=C["green3"])
    arrow(ax, 0.62, 0.81, 0.675, 0.81, color=C["green3"])

    # MCP SERVER
    phase_band(ax, 0.02, 0.58, 0.96, 0.13, "MCP SERVER", C["teal2"])
    ax.add_patch(FancyBboxPatch((0.05, 0.595), 0.90, 0.10,
                  boxstyle="round,pad=0,rounding_size=0.012",
                  facecolor=C["teal"], edgecolor=C["teal2"], linewidth=2,
                  linestyle='--', zorder=2))
    ax.text(0.5, 0.698, "MCP Server  —  Single Source of Truth", ha='center',
            va='center', fontsize=9, color=C["teal3"], fontweight='bold',
            fontfamily='monospace')
    tools = [("Source\nTools", 0.14), ("Schema\nTools", 0.27),
             ("Rules\nTools", 0.40), ("Task List\nTools", 0.54),
             ("KG\nTools", 0.67), ("Validation\nTools", 0.81)]
    for lbl, cx in tools:
        box(ax, cx, 0.635, 0.10, 0.055, lbl, "", C["teal"], C["teal3"], 7.5)

    # Arrows from source to MCP
    for sx in [0.13, 0.35, 0.55, 0.75]:
        arrow(ax, sx, 0.78, sx, 0.70, color=C["teal3"], lw=1.2)

    # AGENT TEAM LAYER
    phase_band(ax, 0.02, 0.27, 0.96, 0.285, "AGENT TEAMS", C["purple2"])
    box(ax, 0.5, 0.515, 0.22, 0.045, "Orchestrator / Coordinator",
        "", C["red"], C["red2"], 8.5, bold=True)
    arrow(ax, 0.5, 0.492, 0.5, 0.455, color=C["purple3"])

    agents = [
        ("BA Track\nba_scout + ba_analyst", 0.12, C["amber"], C["amber2"]),
        ("DA Track\nda_scout + da_analyst", 0.30, C["blue"], C["blue2"]),
        ("TA Track\nta_scout + ta_analyst", 0.50, C["teal"], C["teal2"]),
        ("AA Track\naa_scout + aa_analyst", 0.70, C["green"], C["green2"]),
        ("Evidence\nValidator", 0.88, C["purple"], C["purple2"]),
    ]
    for lbl, cx, fc, ec in agents:
        box(ax, cx, 0.42, 0.135, 0.055, lbl, "", fc, ec, 7.5)
        arrow(ax, 0.5, 0.492, cx, 0.448, color=C["purple3"], lw=1.0)

    # Phase 4-6 agents
    box(ax, 0.25, 0.335, 0.18, 0.05, "Contradiction\nResolver", "", C["red"], C["red2"], 8)
    box(ax, 0.50, 0.335, 0.18, 0.05, "Gap Hunter", "", C["amber"], C["amber2"], 8)
    box(ax, 0.75, 0.335, 0.18, 0.05, "Foundation\nSynthesis", "", C["blue"], C["blue2"], 8)
    for cx in [0.25, 0.50, 0.75]:
        arrow(ax, cx, 0.392, cx, 0.36, color=C["purple3"], lw=1.2)
    arrow(ax, 0.34, 0.335, 0.41, 0.335, color=C["purple3"])
    arrow(ax, 0.59, 0.335, 0.66, 0.335, color=C["purple3"])

    # All agents → MCP (bi-directional)
    ax.text(0.5, 0.585, "All agents query MCP tools — no direct file access",
            ha='center', va='center', fontsize=8, color=C["teal3"],
            fontfamily='monospace', style='italic')
    for cx in [0.12, 0.30, 0.50, 0.70, 0.88, 0.25, 0.75]:
        ax.annotate("", xy=(cx, 0.595), xytext=(cx, 0.448 if cx in [0.12,0.30,0.50,0.70,0.88] else 0.36),
                    arrowprops=dict(arrowstyle="<->", color=C["teal3"], lw=0.8,
                                   connectionstyle="arc3,rad=0.0"), zorder=2)

    # OUTPUT LAYER
    phase_band(ax, 0.02, 0.03, 0.96, 0.22, "OUTPUTS", C["blue2"])
    outputs = [
        ("task_list.json\nShared findings", 0.13, C["purple"], C["purple2"]),
        ("knowledge_graph\n/kg.json", 0.30, C["teal"], C["teal2"]),
        ("25 Architecture\nDocuments", 0.50, C["blue"], C["blue2"]),
        ("Validation\nReports", 0.70, C["green"], C["green2"]),
        ("~97–99%\nAccuracy", 0.87, C["red"], C["red2"]),
    ]
    for lbl, cx, fc, ec in outputs:
        box(ax, cx, 0.135, 0.155, 0.06, lbl, "", fc, ec, 8)
    arrow(ax, 0.75, 0.31, 0.5, 0.165, color=C["blue3"], lw=1.5)
    arrow(ax, 0.5, 0.165, 0.87, 0.165, color=C["blue3"], lw=1.2)

    # Legend
    ax.text(0.03, 0.025, "Legend:", fontsize=7.5, color=C["gray2"],
            fontfamily='monospace', fontweight='bold')
    items = [
        (C["green2"], "Source Data"),
        (C["teal2"], "MCP Server"),
        (C["purple2"], "Agent Team"),
        (C["blue2"], "Output"),
    ]
    for i, (c, l) in enumerate(items):
        legend_item(ax, 0.12 + i*0.18, 0.012, c, l)

    plt.tight_layout(pad=0.5)
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# DIAGRAM 2 — MCP Server Detail
# ══════════════════════════════════════════════════════════════════════════════
def diagram2():
    fig, ax = plt.subplots(figsize=(18, 11))
    setup_ax(fig, ax, "DIAGRAM 2 — MCP Server — Tool Groups & Data Sources")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    # MCP server center
    ax.add_patch(FancyBboxPatch((0.32, 0.35), 0.36, 0.32,
                  boxstyle="round,pad=0,rounding_size=0.02",
                  facecolor=C["teal"], edgecolor=C["teal2"], linewidth=2.5,
                  linestyle='--', zorder=2))
    ax.text(0.50, 0.675, "MCP SERVER", ha='center', va='center',
            fontsize=13, color=C["teal3"], fontweight='bold', fontfamily='monospace')
    ax.text(0.50, 0.650, "oracle-hrms  /  server.py", ha='center', va='center',
            fontsize=8.5, color=C["gray2"], fontfamily='monospace')

    # Tool groups inside MCP
    tools_inside = [
        ("get_source_file()\nlist_source_files()\nsearch_source()\nget_source_excerpt()\nget_package_interface()", 0.395, 0.575, C["green"], C["green2"], "Source Tools"),
        ("get_table()\nget_column()\nfind_foreign_keys()\nsearch_schema()\nlist_tables()", 0.605, 0.575, C["blue"], C["blue2"], "Schema Tools"),
        ("get_rules_by_category()\nsearch_rules()\nadd_rule()", 0.395, 0.455, C["amber"], C["amber2"], "Rules Tools"),
        ("create_task()  claim_task()\nupdate_task()  list_tasks()\nget_track_summary()", 0.605, 0.455, C["purple"], C["purple2"], "Task List Tools"),
        ("add_node()  add_edge()\nquery_graph()\nfind_orphan_nodes()\nfind_conflicts()", 0.395, 0.395, C["teal"], C["teal2"], "KG Tools"),  # moved lower
        ("validate_claim()\ncross_check_tracks()\nrecord_contradiction()", 0.605, 0.395, C["red"], C["red2"], "Validation Tools"),
    ]

    # Reposition
    tool_boxes = [
        (0.395, 0.565, C["green"], C["green2"], "Source\nTools",
         "get_source_file()\nlist_source_files()\nsearch_source()\nget_source_excerpt()\nget_package_interface()"),
        (0.605, 0.565, C["blue"], C["blue2"], "Schema\nTools",
         "get_table() · get_column()\nfind_foreign_keys()\nsearch_schema() · list_tables()"),
        (0.395, 0.475, C["amber"], C["amber2"], "Rules\nTools",
         "get_rules_by_category()\nsearch_rules() · add_rule()"),
        (0.605, 0.475, C["purple"], C["purple2"], "Task List\nTools",
         "create_task() · claim_task()\nupdate_task() · list_tasks()"),
        (0.395, 0.400, C["teal"], C["teal2"], "KG\nTools",
         "add_node() · add_edge()\nquery_graph() · find_conflicts()"),
        (0.605, 0.400, C["red"], C["red2"], "Validation\nTools",
         "validate_claim()\ncross_check_tracks()\nrecord_contradiction()"),
    ]
    for cx, cy, fc, ec, lbl, detail in tool_boxes:
        ax.add_patch(FancyBboxPatch((cx-0.12, cy-0.055), 0.24, 0.11,
                      boxstyle="round,pad=0,rounding_size=0.01",
                      facecolor=fc, edgecolor=ec, linewidth=1.5, zorder=3))
        ax.text(cx, cy+0.025, lbl, ha='center', va='center',
                fontsize=8.5, color=C["white"], fontweight='bold',
                fontfamily='monospace', zorder=4)
        ax.text(cx, cy-0.018, detail, ha='center', va='center',
                fontsize=6.5, color=C["gray2"], fontfamily='monospace', zorder=4)

    # DATA SOURCES (left side)
    ax.text(0.13, 0.92, "DATA SOURCES", ha='center', fontsize=10,
            color=C["green3"], fontweight='bold', fontfamily='monospace')

    ds = [
        ("source_index.json", "42 files, 382 KB\n(from file_cache.json)", 0.13, 0.80, C["green"]),
        ("schema_catalogue.json", "31 tables, all columns\n(from da-outputs/)", 0.13, 0.67, C["blue"]),
        ("implicit_rules.json", "310 rules, 4 categories", 0.13, 0.55, C["amber"]),
        ("task_list.json", "Live agent findings\n(runtime)", 0.13, 0.42, C["purple"]),
        ("kg.json", "Live knowledge graph\n(built incrementally)", 0.13, 0.29, C["teal"]),
    ]
    for lbl, sub, cx, cy, fc in ds:
        box(ax, cx, cy, 0.20, 0.075, lbl, sub, fc, fc, 8)

    # Arrows from data sources to MCP
    for _, _, cx, cy, fc in ds:
        arrow(ax, cx + 0.10, cy, 0.32, cy, color=C["gray2"], lw=1.2)

    # AGENTS (right side)
    ax.text(0.87, 0.92, "AGENTS", ha='center', fontsize=10,
            color=C["purple3"], fontweight='bold', fontfamily='monospace')

    ag = [
        ("BA Analyst", 0.87, 0.82, C["amber"]),
        ("DA Analyst", 0.87, 0.72, C["blue"]),
        ("TA Analyst", 0.87, 0.62, C["teal"]),
        ("AA Analyst", 0.87, 0.52, C["green"]),
        ("Gap Hunter", 0.87, 0.42, C["amber"]),
        ("Foundation", 0.87, 0.32, C["blue"]),
        ("Ev. Validator", 0.87, 0.22, C["purple"]),
    ]
    for lbl, cx, cy, fc in ag:
        box(ax, cx, cy, 0.16, 0.045, lbl, "", fc, fc, 8)
        # bi-directional arrows
        ax.annotate("", xy=(0.68, cy), xytext=(cx - 0.08, cy),
                    arrowprops=dict(arrowstyle="<->", color=C["gray2"], lw=1.0), zorder=2)

    # Key principle box
    ax.add_patch(FancyBboxPatch((0.28, 0.09), 0.44, 0.065,
                  boxstyle="round,pad=0,rounding_size=0.01",
                  facecolor=C["bg3"], edgecolor=C["yellow"], linewidth=1.5, zorder=3))
    ax.text(0.50, 0.123, "KEY PRINCIPLE: No agent reads files directly.",
            ha='center', va='center', fontsize=9, color=C["yellow"],
            fontweight='bold', fontfamily='monospace', zorder=4)
    ax.text(0.50, 0.103, "All source access goes through MCP tools  →  eliminates hallucination + handoff failures",
            ha='center', va='center', fontsize=8, color=C["gray2"],
            fontfamily='monospace', zorder=4)

    plt.tight_layout(pad=0.5)
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# DIAGRAM 3 — Execution Phases & Parallelism
# ══════════════════════════════════════════════════════════════════════════════
def diagram3():
    fig, ax = plt.subplots(figsize=(18, 11))
    setup_ax(fig, ax, "DIAGRAM 3 — Execution Phases & Parallelism (~3.5–4 hrs total)")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    phases = [
        ("PHASE 0\nBOOTSTRAP",    0.93, 0.04, C["gray"],    "~2 min",   [
            ("Build source_index.json", 0.18),
            ("Copy schema-catalogue → MCP", 0.35),
            ("Start MCP server", 0.52),
            ("Pre-load 7 contradictions", 0.68),
            ("Health check all tools", 0.82),
        ]),
        ("PHASE 1\nSCOUT WAVE",   0.80, 0.10, C["green2"],  "~15 min",  [
            ("ba_scout", 0.22),
            ("da_scout", 0.50),
            ("ta_scout", 0.78),
        ]),
        ("PHASE 2\nANALYST WAVE", 0.60, 0.12, C["blue2"],   "~45-60 min",[
            ("ba_analyst\n(Opus)", 0.18),
            ("da_analyst\n(Opus)", 0.40),
            ("ta_analyst\n(Opus)", 0.62),
            ("evidence_validator\n(background)", 0.84),
        ]),
        ("PHASE 3\nAPP ANALYSIS", 0.45, 0.08, C["amber2"],  "~25 min",  [
            ("aa_scout\n(Sonnet)", 0.35),
            ("aa_analyst\n(Opus)", 0.65),
        ]),
        ("PHASE 4\nCONTRADICTION\nRESOLVE", 0.32, 0.10, C["red2"], "~20 min", [
            ("contradiction_resolver\n(Opus)", 0.50),
        ]),
        ("PHASE 5\nGAP HUNTER",   0.20, 0.08, C["amber2"],  "~30 min",  [
            ("gap_hunter\n(Opus)", 0.50),
        ]),
        ("PHASE 6\nFOUNDATION",   0.06, 0.12, C["purple2"], "~40 min",  [
            ("Sub-A\ndocs 01-08", 0.25),
            ("Sub-B\ndocs 09-16", 0.50),
            ("Sub-C\ndocs 17-25", 0.75),
        ]),
    ]

    for (label, cy, h, color, time, agents) in phases:
        # Phase band
        ax.add_patch(FancyBboxPatch((0.04, cy - h/2), 0.92, h,
                      boxstyle="round,pad=0,rounding_size=0.008",
                      facecolor=color, edgecolor=color,
                      linewidth=1.5, alpha=0.15, zorder=1))
        # Phase label (left)
        ax.add_patch(FancyBboxPatch((0.04, cy - h/2), 0.10, h,
                      boxstyle="round,pad=0,rounding_size=0.008",
                      facecolor=color, edgecolor=color,
                      linewidth=1.5, alpha=0.5, zorder=2))
        ax.text(0.09, cy, label, ha='center', va='center',
                fontsize=7, color=C["white"], fontweight='bold',
                fontfamily='monospace', zorder=3)
        # Time label (right)
        ax.text(0.955, cy, time, ha='right', va='center',
                fontsize=7.5, color=color, fontfamily='monospace',
                fontweight='bold')
        # Agent boxes
        aw = min(0.14, 0.72/max(len(agents), 1) - 0.02)
        ah = h * 0.62
        for (albl, ax_pos) in agents:
            bx = 0.15 + ax_pos * 0.74
            ax.add_patch(FancyBboxPatch((bx - aw/2, cy - ah/2), aw, ah,
                          boxstyle="round,pad=0,rounding_size=0.006",
                          facecolor=color, edgecolor=C["white"],
                          linewidth=1.2, alpha=0.8, zorder=3))
            ax.text(bx, cy, albl, ha='center', va='center',
                    fontsize=7, color=C["white"], fontfamily='monospace', zorder=4)

    # Vertical flow arrows between phases
    phase_centers = [cy for (_, cy, _, _, _, _) in phases]
    phase_heights = [h for (_, _, h, _, _, _) in phases]
    for i in range(len(phases)-1):
        y1 = phases[i][1] - phases[i][2]/2
        y2 = phases[i+1][1] + phases[i+1][2]/2
        arrow(ax, 0.50, y1 - 0.005, 0.50, y2 + 0.005, color=C["gray2"], lw=2)

    # Parallel indicator for phases 1, 2, 6
    for cy, label in [(0.80, "← 3 agents in parallel →"),
                      (0.60, "← 3 analysts + 1 validator in parallel →"),
                      (0.06, "← 3 sub-agents in parallel →")]:
        ax.text(0.50, cy - 0.063, label, ha='center', va='center',
                fontsize=7, color=C["yellow"], fontfamily='monospace',
                style='italic')

    # evidence_validator continuous arrow
    ax.annotate("", xy=(0.93, 0.45), xytext=(0.93, 0.65),
                arrowprops=dict(arrowstyle="->", color=C["purple2"], lw=1.5,
                               connectionstyle="arc3,rad=0.0"), zorder=5)
    ax.text(0.965, 0.55, "continuous\nvalidation", ha='center', va='center',
            fontsize=6.5, color=C["purple3"], fontfamily='monospace')

    # Total time
    ax.add_patch(FancyBboxPatch((0.30, 0.008), 0.40, 0.028,
                  boxstyle="round,pad=0,rounding_size=0.005",
                  facecolor=C["bg3"], edgecolor=C["yellow"], linewidth=1.5, zorder=3))
    ax.text(0.50, 0.022, "Total wall-clock: ~3.5–4 hours  |  463 Claude calls  |  ~$22",
            ha='center', va='center', fontsize=8.5, color=C["yellow"],
            fontweight='bold', fontfamily='monospace', zorder=4)

    plt.tight_layout(pad=0.5)
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# DIAGRAM 4 — Task List & Agent Communication
# ══════════════════════════════════════════════════════════════════════════════
def diagram4():
    fig, ax = plt.subplots(figsize=(18, 11))
    setup_ax(fig, ax, "DIAGRAM 4 — Shared Task List: How Agents Communicate")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    # V1 vs V2 split
    ax.axvline(0.50, color=C["border"], lw=1.5, linestyle='--', zorder=1)
    ax.text(0.25, 0.955, "v1  (BROKEN — stdout summaries)", ha='center',
            fontsize=11, color=C["red2"], fontweight='bold', fontfamily='monospace')
    ax.text(0.75, 0.955, "v2  (FIXED — shared task list)", ha='center',
            fontsize=11, color=C["green3"], fontweight='bold', fontfamily='monospace')

    # V1 flow
    v1_steps = [
        ("DA Agent 1", 0.25, 0.85, C["blue"]),
        ("Writes da-outputs/\nschema-catalogue.json\n(103KB real DDL)", 0.25, 0.72, C["green"]),
        ("Prints to stdout:\n'All 14 files written'\n(1,721 chars)", 0.25, 0.59, C["red"]),
        ("foundation_runner.py\nreads stdout only", 0.25, 0.46, C["amber"]),
        ("Foundation gets\nZERO DDL data", 0.25, 0.33, C["red"]),
        ("Fabricates tables:\nJOB_POSITIONS,\nBENEFIT_PLANS...", 0.25, 0.19, C["red"]),
    ]
    for lbl, cx, cy, fc in v1_steps:
        box(ax, cx, cy, 0.32, 0.07, lbl, "", fc, fc, 8)

    for i in range(len(v1_steps)-1):
        y1 = v1_steps[i][2] - 0.035
        y2 = v1_steps[i+1][2] + 0.035
        col = C["red2"] if i >= 2 else C["gray2"]
        arrow(ax, 0.25, y1, 0.25, y2, color=col, lw=1.5)

    ax.text(0.25, 0.08, "RESULT: 48% column accuracy\n6 fabricated tables",
            ha='center', va='center', fontsize=9, color=C["red2"],
            fontweight='bold', fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=C["red"], alpha=0.3,
                      edgecolor=C["red2"]))

    # V2 flow
    v2_steps = [
        ("DA Analyst Agent", 0.75, 0.88, C["blue"]),
        ("calls get_table(\"EMPLOYEES\")\nvia MCP → gets 34 real columns", 0.75, 0.76, C["teal"]),
        ("writes finding to task_list.json:\nclaim + evidence + line numbers", 0.75, 0.63, C["green"]),
        ("evidence_validator confirms\nagainst source_index.json", 0.75, 0.51, C["purple"]),
        ("Foundation reads\ntask_list.json findings\n(all 34 columns, verified)", 0.75, 0.39, C["green"]),
        ("Generates docs with\nexact DDL column names:\nEMP_ID, EMP_NUMBER...", 0.75, 0.25, C["green"]),
    ]
    for lbl, cx, cy, fc in v2_steps:
        box(ax, cx, cy, 0.38, 0.075, lbl, "", fc, fc, 8)

    for i in range(len(v2_steps)-1):
        y1 = v2_steps[i][2] - 0.038
        y2 = v2_steps[i+1][2] + 0.038
        arrow(ax, 0.75, y1, 0.75, y2, color=C["green3"], lw=1.5)

    ax.text(0.75, 0.09, "RESULT: ~98% column accuracy\nNo fabricated tables",
            ha='center', va='center', fontsize=9, color=C["green3"],
            fontweight='bold', fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=C["green"], alpha=0.3,
                      edgecolor=C["green2"]))

    # Task schema callout
    ax.add_patch(FancyBboxPatch((0.51, 0.35), 0.20, 0.32,
                  boxstyle="round,pad=0,rounding_size=0.01",
                  facecolor=C["bg3"], edgecolor=C["teal2"], linewidth=1.5, zorder=5))
    schema_text = ('task_list.json entry:\n'
                   '{\n'
                   ' "task_id": "T-DA-0003",\n'
                   ' "status": "complete",\n'
                   ' "findings": [{\n'
                   '  "claim": "EMPLOYEES has\n'
                   '   34 cols, EMP_ID as PK",\n'
                   '  "confidence": 0.99,\n'
                   '  "evidence": [{\n'
                   '   "file": "01_core_tables.sql",\n'
                   '   "line": 12,\n'
                   '   "excerpt": "EMP_ID NUMBER"\n'
                   '  }]\n'
                   ' }]\n'
                   '}')
    ax.text(0.605, 0.51, schema_text, ha='center', va='center',
            fontsize=6, color=C["teal3"], fontfamily='monospace', zorder=6)

    plt.tight_layout(pad=0.5)
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# DIAGRAM 5 — Gap Hunter v1 vs v2
# ══════════════════════════════════════════════════════════════════════════════
def diagram5():
    fig, ax = plt.subplots(figsize=(18, 11))
    setup_ax(fig, ax, "DIAGRAM 5 — Gap Hunter: v1 vs v2 Comparison")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    ax.axvline(0.50, color=C["border"], lw=1.5, linestyle='--', zorder=1)
    ax.text(0.25, 0.955, "Gap Hunter v1  (self-referential)", ha='center',
            fontsize=11, color=C["red2"], fontweight='bold', fontfamily='monospace')
    ax.text(0.75, 0.955, "Gap Hunter v2  (MCP-grounded)", ha='center',
            fontsize=11, color=C["green3"], fontweight='bold', fontfamily='monospace')

    # V1 problems
    v1 = [
        ("Scans 25 Markdown docs\nfor MISSING/TBD markers", 0.25, 0.86, C["amber"]),
        ("Finds markers Foundation\nalready admitted", 0.25, 0.74, C["amber"]),
        ("CANNOT detect fabricated content\n(no MISSING marker on JOB_POSITIONS)", 0.25, 0.62, C["red"]),
        ("Asks Claude what source\nfile might fix the gap", 0.25, 0.50, C["amber"]),
        ("Patches snippet back\ninto Markdown file", 0.25, 0.38, C["amber"]),
        ("482 gaps found, 256 filled\n226 unfillable\nFabrications never touched", 0.25, 0.24, C["red"]),
    ]
    for lbl, cx, cy, fc in v1:
        box(ax, cx, cy, 0.38, 0.072, lbl, "", fc, fc, 8)
    for i in range(len(v1)-1):
        arrow(ax, 0.25, v1[i][2]-0.036, 0.25, v1[i+1][2]+0.036, color=C["red2"], lw=1.5)

    ax.text(0.25, 0.10, "Column accuracy still 48% after Gap Hunter\nFabricated tables still present",
            ha='center', fontsize=8.5, color=C["red2"], fontweight='bold',
            fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=C["red"], alpha=0.3,
                      edgecolor=C["red2"]))

    # V2 5-pass algorithm
    v2 = [
        ("PASS 1: get_package_interface() × 11\nCheck every public proc/func in task findings", 0.75, 0.88, C["green"]),
        ("PASS 2: get_table() × 31\nCheck every column against evidence excerpts", 0.75, 0.76, C["green"]),
        ("PASS 3: find_orphan_nodes()\nKG nodes with no connections → investigate", 0.75, 0.64, C["teal"]),
        ("PASS 4: Hard-coded critical checks\nHOH tax bug · rehire · EMPLOYEE_HISTORY\nrace condition · hardcoded AES key", 0.75, 0.51, C["amber"]),
        ("PASS 5: get_validation_status()\nRe-try all 'unverifiable' claims with\nbroader search_source() queries", 0.75, 0.38, C["blue"]),
        ("Fills gaps into task_list.json\nwith evidence — not into Markdown", 0.75, 0.25, C["green"]),
    ]
    for lbl, cx, cy, fc in v2:
        box(ax, cx, cy, 0.42, 0.08, lbl, "", fc, fc, 8)
    for i in range(len(v2)-1):
        arrow(ax, 0.75, v2[i][2]-0.04, 0.75, v2[i+1][2]+0.04, color=C["green3"], lw=1.5)

    ax.text(0.75, 0.105, "Every package procedure verified\nEvery table column verified against source",
            ha='center', fontsize=8.5, color=C["green3"], fontweight='bold',
            fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=C["green"], alpha=0.3,
                      edgecolor=C["green2"]))

    plt.tight_layout(pad=0.5)
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# DIAGRAM 6 — Accuracy Improvement
# ══════════════════════════════════════════════════════════════════════════════
def diagram6():
    fig, ax = plt.subplots(figsize=(18, 11))
    setup_ax(fig, ax, "DIAGRAM 6 — Accuracy: v1 vs v2 Comparison")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    dimensions = [
        "Table Coverage\n(no fabrications)",
        "Column\nAccuracy",
        "Procedure\nCoverage",
        "Trigger\nCoverage",
        "Business\nRules",
        "Security\nFindings",
        "OVERALL",
    ]
    v1_scores = [72, 48, 78, 50, 85, 100, 70]
    v2_scores = [99, 98, 99, 95, 92, 100, 98]

    n = len(dimensions)
    bar_h = 0.055
    gap = 0.028
    block = bar_h * 2 + gap
    start_y = 0.88

    for i, (dim, s1, s2) in enumerate(zip(dimensions, v1_scores, v2_scores)):
        cy = start_y - i * (block + 0.022)

        # Dimension label
        ax.text(0.16, cy + bar_h/2 + gap/2, dim, ha='right', va='center',
                fontsize=8, color=C["white"], fontfamily='monospace')

        # v1 bar
        w1 = s1 / 100 * 0.72
        color1 = C["red2"] if s1 < 60 else (C["amber2"] if s1 < 80 else C["green2"])
        ax.add_patch(FancyBboxPatch((0.17, cy + gap/2), w1, bar_h,
                      boxstyle="round,pad=0,rounding_size=0.004",
                      facecolor=color1, edgecolor=color1, alpha=0.9, zorder=3))
        ax.text(0.17 + w1 + 0.008, cy + gap/2 + bar_h/2, f"v1: {s1}%",
                va='center', fontsize=7.5, color=color1, fontfamily='monospace',
                fontweight='bold')

        # v2 bar
        w2 = s2 / 100 * 0.72
        color2 = C["green2"] if s2 >= 90 else C["amber2"]
        ax.add_patch(FancyBboxPatch((0.17, cy - bar_h - gap/2), w2, bar_h,
                      boxstyle="round,pad=0,rounding_size=0.004",
                      facecolor=color2, edgecolor=color2, alpha=0.9, zorder=3))
        ax.text(0.17 + w2 + 0.008, cy - gap/2 - bar_h/2, f"v2: {s2}%",
                va='center', fontsize=7.5, color=color2, fontfamily='monospace',
                fontweight='bold')

        # Gain
        gain = s2 - s1
        if gain > 0:
            ax.text(0.93, cy + gap/2 + bar_h/2 - bar_h/2 - gap/4,
                    f"+{gain}%", ha='center', va='center',
                    fontsize=8.5, color=C["yellow"], fontweight='bold',
                    fontfamily='monospace')

        # Separator line
        if i < n-1:
            ax.axhline(cy - bar_h - gap, xmin=0.17, xmax=0.97,
                       color=C["border"], lw=0.5, linestyle=':')

    # 100% line
    ax.axvline(0.17 + 0.72, ymin=0.05, ymax=0.97,
               color=C["border"], lw=1, linestyle='--')
    ax.text(0.17 + 0.72 + 0.005, 0.965, "100%", ha='left', fontsize=7,
            color=C["gray"], fontfamily='monospace')

    # Gain legend
    legend_item(ax, 0.20, 0.042, C["red2"],   "v1 score (< 60%)")
    legend_item(ax, 0.36, 0.042, C["amber2"],  "v1 score (60-80%)")
    legend_item(ax, 0.52, 0.042, C["green2"],  "v2 score (≥ 90%)")
    legend_item(ax, 0.68, 0.042, C["yellow"],  "accuracy gain")

    # Root causes box
    ax.add_patch(FancyBboxPatch((0.02, 0.005), 0.96, 0.028,
                  boxstyle="round,pad=0,rounding_size=0.004",
                  facecolor=C["bg3"], edgecolor=C["teal2"], linewidth=1, zorder=3))
    ax.text(0.50, 0.019,
            "v1 losses: DA stdout stub (1.7KB) → Foundation had no DDL  |  "
            "Call 1 truncated  |  No validation  |  annotated_sources never read",
            ha='center', va='center', fontsize=7.5, color=C["gray2"],
            fontfamily='monospace', zorder=4)

    plt.tight_layout(pad=0.5)
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# MAIN — Save all diagrams
# ══════════════════════════════════════════════════════════════════════════════
diagrams = [
    ("01_system_overview",           diagram1),
    ("02_mcp_server_tools",          diagram2),
    ("03_execution_phases",          diagram3),
    ("04_task_list_communication",   diagram4),
    ("05_gap_hunter_comparison",     diagram5),
    ("06_accuracy_improvement",      diagram6),
]

paths = []
for name, fn in diagrams:
    fig = fn()
    path = os.path.join(OUT_DIR, f"ARCH_{name}.png")
    fig.savefig(path, dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    paths.append(path)
    print(f"Saved: {path}")

# Combined PDF
from matplotlib.backends.backend_pdf import PdfPages
pdf_path = os.path.join(OUT_DIR, "PIPELINE_ARCHITECTURE_DIAGRAMS.pdf")
with PdfPages(pdf_path) as pdf:
    for name, fn in diagrams:
        fig = fn()
        pdf.savefig(fig, bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close(fig)

print(f"\nAll diagrams saved.")
print(f"PDF: {pdf_path}")
print(f"PNGs: {OUT_DIR}\\ARCH_*.png")
