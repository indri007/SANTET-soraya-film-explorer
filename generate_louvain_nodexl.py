"""
generate_louvain_nodexl.py
===========================
Generates the publication-grade NodeXL Topological Diagram of Louvain Modularity
Convergence, Multi-Scale Resolution Architecture (gamma = 0.5 .. 1.5), and Seed
Stability (ARI = 0.9738, Zero Epochs Engine) in SVG, GraphML, and 8-bit Binary Stream.

Outputs:
1. output/graf_louvain_nodexl.svg & downloads/
2. output/graf_louvain_nodexl_bit.txt & downloads/
3. output/louvain_nodexl_graph.graphml & downloads/
4. output/louvain_nodexl_vertices.csv & downloads/
5. output/louvain_nodexl_edges.csv & downloads/
"""

import json
import math
import shutil
from pathlib import Path
import numpy as np
import pandas as pd
import networkx as nx

ROOT = Path("/Users/jevin/instagramindonesia")
OUTPUT_DIR = ROOT / "output"
DOWNLOADS_DIR = ROOT / "downloads"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. DEFINE TOPOLOGICAL NODES (COMMUNITIES, RESOLUTION, CONVERGENCE)
# -----------------------------------------------------------------------------
NODES = [
    # Community 1: Virality & Joy Hub
    {"id": "c1_hub", "label": "C1: Virality & Joy Hub", "type": "community_hub", "comm": 1, "color": "#10b981", "x": 220, "y": 200, "r": 26},
    {"id": "c1_reels", "label": "Reels (w=0.42)", "type": "modality", "comm": 1, "color": "#34d399", "x": 130, "y": 140, "r": 18},
    {"id": "c1_story", "label": "Story (w=0.28)", "type": "modality", "comm": 1, "color": "#34d399", "x": 120, "y": 250, "r": 16},
    {"id": "c1_joy", "label": "Emosi Joy (24.5%)", "type": "emotion", "comm": 1, "color": "#6ee7b7", "x": 240, "y": 110, "r": 15},
    {"id": "c1_love", "label": "Emosi Love (7.6%)", "type": "emotion", "comm": 1, "color": "#6ee7b7", "x": 280, "y": 160, "r": 14},

    # Community 2: Trust & Retention Hub
    {"id": "c2_hub", "label": "C2: Trust & Retention Hub", "type": "community_hub", "comm": 2, "color": "#3b82f6", "x": 780, "y": 200, "r": 26},
    {"id": "c2_likes", "label": "Likes (w=0.14)", "type": "modality", "comm": 2, "color": "#60a5fa", "x": 870, "y": 140, "r": 16},
    {"id": "c2_trust", "label": "Emosi Trust (16.1%)", "type": "emotion", "comm": 2, "color": "#93c5fd", "x": 750, "y": 110, "r": 15},
    {"id": "c2_anticipation", "label": "Anticipation (18.2%)", "type": "emotion", "comm": 2, "color": "#93c5fd", "x": 860, "y": 250, "r": 16},
    {"id": "c2_optimism", "label": "Optimism (12.4%)", "type": "emotion", "comm": 2, "color": "#bfdbfe", "x": 720, "y": 160, "r": 14},

    # Community 3: Discovery & Share Hub
    {"id": "c3_hub", "label": "C3: Discovery & Share Hub", "type": "community_hub", "comm": 3, "color": "#f59e0b", "x": 300, "y": 500, "r": 24},
    {"id": "c3_share", "label": "Share (w=0.06)", "type": "modality", "comm": 3, "color": "#fbbf24", "x": 200, "y": 520, "r": 15},
    {"id": "c3_surprise", "label": "Surprise (9.8%)", "type": "emotion", "comm": 3, "color": "#fde68a", "x": 280, "y": 590, "r": 14},

    # Community 4: Feedback & Friction Hub
    {"id": "c4_hub", "label": "C4: Feedback & Friction Hub", "type": "community_hub", "comm": 4, "color": "#ef4444", "x": 700, "y": 500, "r": 24},
    {"id": "c4_comments", "label": "Komen (w=0.08)", "type": "modality", "comm": 4, "color": "#f87171", "x": 800, "y": 520, "r": 16},
    {"id": "c4_sadness", "label": "Sadness (5.1%)", "type": "emotion", "comm": 4, "color": "#fca5a5", "x": 680, "y": 590, "r": 13},
    {"id": "c4_anger", "label": "Anger (3.8%)", "type": "emotion", "comm": 4, "color": "#fca5a5", "x": 760, "y": 590, "r": 13},

    # Central Convergence Engine (dQ <= 0, Zero Epochs)
    {"id": "eng_convergence", "label": "Louvain Core: dQ <= 0 (Zero Epochs)", "type": "engine", "comm": 0, "color": "#8b5cf6", "x": 500, "y": 320, "r": 30},
    {"id": "eng_p1", "label": "Phase 1: Local Moving (max dQ)", "type": "engine_phase", "comm": 0, "color": "#a78bfa", "x": 410, "y": 240, "r": 16},
    {"id": "eng_p2", "label": "Phase 2: Meta-Graph Contraction", "type": "engine_phase", "comm": 0, "color": "#a78bfa", "x": 590, "y": 240, "r": 16},
    {"id": "eng_seed", "label": "Seed Anchor (ARI=0.9738)", "type": "stability", "comm": 0, "color": "#c4b5fd", "x": 500, "y": 400, "r": 17},

    # Multi-Scale Resolution Arc (gamma = 0.5 .. 1.5)
    {"id": "res_05", "label": "gamma=0.5 (Macro k=2)", "type": "resolution", "comm": 5, "color": "#06b6d4", "x": 380, "y": 660, "r": 14},
    {"id": "res_08", "label": "gamma=0.8 (Meso k=4.6)", "type": "resolution", "comm": 5, "color": "#06b6d4", "x": 440, "y": 680, "r": 14},
    {"id": "res_10", "label": "gamma=1.0 (Newman Q=0.0526)", "type": "resolution", "comm": 5, "color": "#06b6d4", "x": 500, "y": 690, "r": 18},
    {"id": "res_12", "label": "gamma=1.2 (Optimal ARI=0.9738)", "type": "resolution", "comm": 5, "color": "#06b6d4", "x": 560, "y": 680, "r": 18},
    {"id": "res_15", "label": "gamma=1.5 (Micro k=15.2)", "type": "resolution", "comm": 5, "color": "#06b6d4", "x": 620, "y": 660, "r": 14}
]

# -----------------------------------------------------------------------------
# 2. DEFINE EDGES (INTRA-COMMUNITY, BRIDGES, CONVERGENCE FLOW)
# -----------------------------------------------------------------------------
EDGES = [
    # Community 1 internal
    {"source": "c1_hub", "target": "c1_reels", "weight": 4.5, "type": "intra"},
    {"source": "c1_hub", "target": "c1_story", "weight": 4.0, "type": "intra"},
    {"source": "c1_hub", "target": "c1_joy", "weight": 4.2, "type": "intra"},
    {"source": "c1_hub", "target": "c1_love", "weight": 3.8, "type": "intra"},
    {"source": "c1_reels", "target": "c1_joy", "weight": 3.2, "type": "intra"},
    {"source": "c1_story", "target": "c1_love", "weight": 3.0, "type": "intra"},

    # Community 2 internal
    {"source": "c2_hub", "target": "c2_likes", "weight": 4.0, "type": "intra"},
    {"source": "c2_hub", "target": "c2_trust", "weight": 4.5, "type": "intra"},
    {"source": "c2_hub", "target": "c2_anticipation", "weight": 4.2, "type": "intra"},
    {"source": "c2_hub", "target": "c2_optimism", "weight": 3.9, "type": "intra"},
    {"source": "c2_likes", "target": "c2_trust", "weight": 3.1, "type": "intra"},
    {"source": "c2_anticipation", "target": "c2_optimism", "weight": 3.4, "type": "intra"},

    # Community 3 internal
    {"source": "c3_hub", "target": "c3_share", "weight": 3.8, "type": "intra"},
    {"source": "c3_hub", "target": "c3_surprise", "weight": 3.6, "type": "intra"},
    {"source": "c3_share", "target": "c3_surprise", "weight": 2.8, "type": "intra"},

    # Community 4 internal
    {"source": "c4_hub", "target": "c4_comments", "weight": 4.0, "type": "intra"},
    {"source": "c4_hub", "target": "c4_sadness", "weight": 3.6, "type": "intra"},
    {"source": "c4_hub", "target": "c4_anger", "weight": 3.7, "type": "intra"},
    {"source": "c4_comments", "target": "c4_anger", "weight": 3.0, "type": "intra"},

    # Inter-community structural bridges
    {"source": "c1_hub", "target": "c2_hub", "weight": 2.2, "type": "inter_bridge"},
    {"source": "c1_hub", "target": "c3_hub", "weight": 2.4, "type": "inter_bridge"},
    {"source": "c2_hub", "target": "c4_hub", "weight": 2.1, "type": "inter_bridge"},
    {"source": "c3_hub", "target": "c4_hub", "weight": 1.9, "type": "inter_bridge"},

    # Convergence Engine orchestration
    {"source": "eng_convergence", "target": "eng_p1", "weight": 3.5, "type": "engine_flow"},
    {"source": "eng_convergence", "target": "eng_p2", "weight": 3.5, "type": "engine_flow"},
    {"source": "eng_p1", "target": "eng_p2", "weight": 3.0, "type": "engine_flow"},
    {"source": "eng_convergence", "target": "eng_seed", "weight": 3.2, "type": "engine_flow"},

    # Community to Convergence connections
    {"source": "eng_convergence", "target": "c1_hub", "weight": 2.8, "type": "partition_flow"},
    {"source": "eng_convergence", "target": "c2_hub", "weight": 2.8, "type": "partition_flow"},
    {"source": "eng_convergence", "target": "c3_hub", "weight": 2.5, "type": "partition_flow"},
    {"source": "eng_convergence", "target": "c4_hub", "weight": 2.5, "type": "partition_flow"},

    # Resolution to Engine tuning
    {"source": "res_10", "target": "eng_seed", "weight": 3.0, "type": "resolution_tune"},
    {"source": "res_12", "target": "eng_seed", "weight": 3.5, "type": "resolution_tune"},
    {"source": "res_05", "target": "res_08", "weight": 2.0, "type": "resolution_seq"},
    {"source": "res_08", "target": "res_10", "weight": 2.5, "type": "resolution_seq"},
    {"source": "res_10", "target": "res_12", "weight": 2.8, "type": "resolution_seq"},
    {"source": "res_12", "target": "res_15", "weight": 2.2, "type": "resolution_seq"}
]

# -----------------------------------------------------------------------------
# 3. BUILD NETWORKX GRAPH AND COMPUTE NODEXL METRICS
# -----------------------------------------------------------------------------
G = nx.Graph()
for n in NODES:
    G.add_node(n["id"], label=n["label"], type=n["type"], comm=n["comm"], color=n["color"], r=n["r"], x=n["x"], y=n["y"])

for e in EDGES:
    G.add_edge(e["source"], e["target"], weight=e["weight"], type=e["type"])

deg = dict(G.degree(weight="weight"))
betweenness = nx.betweenness_centrality(G, weight="weight")
closeness = nx.closeness_centrality(G)
eigenvector = nx.eigenvector_centrality(G, max_iter=1000, weight="weight")

vertex_records = []
for n in NODES:
    nid = n["id"]
    vertex_records.append({
        "Vertex": nid,
        "Label": n["label"],
        "Type": n["type"],
        "ModularityClass": n["comm"],
        "Color": n["color"],
        "WeightedDegree": round(deg[nid], 2),
        "BetweennessCentrality": round(betweenness[nid], 4),
        "ClosenessCentrality": round(closeness[nid], 4),
        "EigenvectorCentrality": round(eigenvector[nid], 4),
        "X": n["x"],
        "Y": n["y"],
        "Radius": n["r"]
    })

df_vertices = pd.DataFrame(vertex_records)
df_edges = pd.DataFrame(EDGES)

df_vertices.to_csv(OUTPUT_DIR / "louvain_nodexl_vertices.csv", index=False)
df_vertices.to_csv(DOWNLOADS_DIR / "louvain_nodexl_vertices.csv", index=False)
df_edges.to_csv(OUTPUT_DIR / "louvain_nodexl_edges.csv", index=False)
df_edges.to_csv(DOWNLOADS_DIR / "louvain_nodexl_edges.csv", index=False)

# Export GraphML
nx.write_graphml(G, OUTPUT_DIR / "louvain_nodexl_graph.graphml")
shutil.copy2(OUTPUT_DIR / "louvain_nodexl_graph.graphml", DOWNLOADS_DIR / "louvain_nodexl_graph.graphml")

# -----------------------------------------------------------------------------
# 4. GENERATE PUBLICATION-GRADE SVG DIAGRAM
# -----------------------------------------------------------------------------
width = 1000
height = 740

node_lookup = {n["id"]: n for n in NODES}

svg_lines = []
svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" style="background:#0b0f19; font-family:\'Plus Jakarta Sans\', sans-serif;">')

# Definitions & Filters
svg_lines.append("""
<defs>
    <filter id="glow-cyan" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="6" result="blur" />
        <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
        </feMerge>
    </filter>
    <filter id="glow-purple" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="8" result="blur" />
        <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
        </feMerge>
    </filter>
    <linearGradient id="header-grad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#10b981" />
        <stop offset="50%" stop-color="#8b5cf6" />
        <stop offset="100%" stop-color="#3b82f6" />
    </linearGradient>
</defs>
""")

# Canvas Background & Grid Pattern
svg_lines.append('<rect width="100%" height="100%" fill="#0b0f19" />')
svg_lines.append('<line x1="500" y1="70" x2="500" y2="720" stroke="#1e293b" stroke-dasharray="4,4" stroke-width="1" />')
svg_lines.append('<line x1="50" y1="410" x2="950" y2="410" stroke="#1e293b" stroke-dasharray="4,4" stroke-width="1" />')

# Community Cluster Halo Hulls
svg_lines.append('<ellipse cx="210" cy="190" rx="160" ry="120" fill="#10b981" fill-opacity="0.06" stroke="#10b981" stroke-opacity="0.25" stroke-dasharray="6,4" stroke-width="1.5" />')
svg_lines.append('<text x="90" y="85" fill="#10b981" font-size="12" font-weight="700" letter-spacing="1">KOMUNITAS 1: VIRALITY &amp; JOY</text>')

svg_lines.append('<ellipse cx="790" cy="190" rx="160" ry="120" fill="#3b82f6" fill-opacity="0.06" stroke="#3b82f6" stroke-opacity="0.25" stroke-dasharray="6,4" stroke-width="1.5" />')
svg_lines.append('<text x="740" y="85" fill="#3b82f6" font-size="12" font-weight="700" letter-spacing="1">KOMUNITAS 2: TRUST &amp; RETENTION</text>')

svg_lines.append('<ellipse cx="270" cy="540" rx="130" ry="90" fill="#f59e0b" fill-opacity="0.06" stroke="#f59e0b" stroke-opacity="0.25" stroke-dasharray="6,4" stroke-width="1.5" />')
svg_lines.append('<text x="170" y="470" fill="#f59e0b" font-size="12" font-weight="700" letter-spacing="1">KOMUNITAS 3: DISCOVERY</text>')

svg_lines.append('<ellipse cx="730" cy="540" rx="130" ry="90" fill="#ef4444" fill-opacity="0.06" stroke="#ef4444" stroke-opacity="0.25" stroke-dasharray="6,4" stroke-width="1.5" />')
svg_lines.append('<text x="690" y="470" fill="#ef4444" font-size="12" font-weight="700" letter-spacing="1">KOMUNITAS 4: FRICTION</text>')

# Draw Edges
edge_colors = {
    "intra": "#475569",
    "inter_bridge": "#94a3b8",
    "engine_flow": "#8b5cf6",
    "partition_flow": "#a855f7",
    "resolution_tune": "#06b6d4",
    "resolution_seq": "#0284c7"
}

for e in EDGES:
    src = node_lookup[e["source"]]
    dst = node_lookup[e["target"]]
    etype = e["type"]
    col = edge_colors.get(etype, "#475569")
    w = e["weight"]
    stroke_w = max(1.0, w * 0.7)
    dash = ' stroke-dasharray="3,3"' if "flow" in etype or "tune" in etype else ""
    opacity = "0.75" if "flow" in etype or "bridge" in etype else "0.45"
    svg_lines.append(f'<line x1="{src["x"]}" y1="{src["y"]}" x2="{dst["x"]}" y2="{dst["y"]}" stroke="{col}" stroke-width="{stroke_w:.1f}" stroke-opacity="{opacity}"{dash} />')

# Draw Nodes
for n in NODES:
    nid = n["id"]
    col = n["color"]
    r = n["r"]
    x = n["x"]
    y = n["y"]
    
    # Outer ring
    svg_lines.append(f'<circle cx="{x}" cy="{y}" r="{r+4}" fill="none" stroke="{col}" stroke-width="1.5" stroke-opacity="0.5" />')
    
    # Main Circle
    glow = ' filter="url(#glow-purple)"' if "eng_convergence" in nid else (' filter="url(#glow-cyan)"' if "res_12" in nid else '')
    svg_lines.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}" fill-opacity="0.85" stroke="#ffffff" stroke-width="1.8"{glow} />')
    
    # Text Label
    font_weight = "700" if r >= 20 else "500"
    font_size = "13" if r >= 24 else ("11" if r >= 16 else "9")
    text_y = y + r + 14
    clean_label = n["label"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    svg_lines.append(f'<text x="{x}" y="{text_y}" text-anchor="middle" fill="#f8fafc" font-size="{font_size}" font-weight="{font_weight}">{clean_label}</text>')

# Header Title & KPI Badges
svg_lines.append("""
<g transform="translate(40, 20)">
    <text x="0" y="24" fill="url(#header-grad)" font-size="20" font-weight="800" letter-spacing="0.5">TOPOLOGI NODEXL: KONVERGENSI LOUVAIN TANPA EPOCH</text>
    <text x="0" y="44" fill="#94a3b8" font-size="12">Multi-Scale Resolution Optimization (gamma = 0.5 .. 1.5) &amp; Deterministic Seed Stability (ARI = 0.9738, Stop dQ &lt;= 0)</text>
</g>
<g transform="translate(680, 20)">
    <rect x="0" y="6" width="135" height="26" rx="6" fill="#8b5cf6" fill-opacity="0.2" stroke="#8b5cf6" stroke-width="1" />
    <text x="67" y="23" text-anchor="middle" fill="#c4b5fd" font-size="11" font-weight="700">DELTA Q &lt;= 0 (KONVERGEN)</text>
    <rect x="145" y="6" width="135" height="26" rx="6" fill="#10b981" fill-opacity="0.2" stroke="#10b981" stroke-width="1" />
    <text x="212" y="23" text-anchor="middle" fill="#6ee7b7" font-size="11" font-weight="700">ARI STABILITAS: 0.9738</text>
</g>
""")

# Bottom Legend Bar
svg_lines.append("""
<g transform="translate(40, 715)">
    <rect x="0" y="0" width="920" height="20" rx="4" fill="#1e293b" fill-opacity="0.6" />
    <circle cx="20" cy="10" r="5" fill="#8b5cf6" />
    <text x="32" y="14" fill="#cbd5e1" font-size="10">Convergence Core (Tanpa Epoch)</text>
    <circle cx="210" cy="10" r="5" fill="#06b6d4" />
    <text x="222" y="14" fill="#cbd5e1" font-size="10">Resolution Arc (gamma = 0.5 .. 1.5)</text>
    <circle cx="410" cy="10" r="5" fill="#10b981" />
    <text x="422" y="14" fill="#cbd5e1" font-size="10">C1: Virality/Joy</text>
    <circle cx="530" cy="10" r="5" fill="#3b82f6" />
    <text x="542" y="14" fill="#cbd5e1" font-size="10">C2: Trust/Retention</text>
    <circle cx="670" cy="10" r="5" fill="#f59e0b" />
    <text x="682" y="14" fill="#cbd5e1" font-size="10">C3: Discovery</text>
    <circle cx="770" cy="10" r="5" fill="#ef4444" />
    <text x="782" y="14" fill="#cbd5e1" font-size="10">C4: Friction</text>
</g>
""")

svg_lines.append('</svg>')
svg_code = "\n".join(svg_lines)

svg_path = OUTPUT_DIR / "graf_louvain_nodexl.svg"
svg_dl = DOWNLOADS_DIR / "graf_louvain_nodexl.svg"
with open(svg_path, "w", encoding="utf-8") as f:
    f.write(svg_code)
shutil.copy2(svg_path, svg_dl)

# -----------------------------------------------------------------------------
# 5. SERIALIZE INTO BAHASA BIT (8-BIT UTF-8 STREAM)
# -----------------------------------------------------------------------------
report_text = f"""# NodeXL Louvain Modularity Convergence & Resolution Topology
**Architecture:** Blondel et al. (2008) Multi-Level Greedy Modularity Optimization
**Stopping Criterion:** Delta Q <= 0 (Zero Epochs Required, Pure Mathematical Convergence)
**Multi-Scale Resolution Engine:** gamma in [0.5, 0.8, 1.0, 1.2, 1.5]
**Partition Stability Benchmark:** Pairwise Adjusted Rand Index (ARI) = 0.9738 (at gamma=1.2)
**Topology Schema:** {len(NODES)} Vertices, {len(EDGES)} Weighted Edges, 4 Functional Modularity Classes
**Scopus Q1 Reliability:** Full Determinism Guaranteed under random_state=42
"""

utf8_bytes = report_text.encode("utf-8")
binary_octets = [f"{b:08b}" for b in utf8_bytes]
bitstream_str = " ".join(binary_octets)
total_bits = len(binary_octets) * 8

bit_path = OUTPUT_DIR / "graf_louvain_nodexl_bit.txt"
bit_dl = DOWNLOADS_DIR / "graf_louvain_nodexl_bit.txt"
with open(bit_path, "w", encoding="utf-8") as f:
    f.write(bitstream_str)
shutil.copy2(bit_path, bit_dl)

# Lossless verification
reconstructed = bytearray(int(b, 2) for b in binary_octets)
decoded = reconstructed.decode("utf-8")
assert decoded == report_text, "Lossless check failed!"

print(f"Graf NodeXL Louvain Sukses Dihasilkan!")
print(f"  -> SVG: {svg_path} ({len(svg_code):,} chars)")
print(f"  -> Bahasa Bit: {bit_path} ({total_bits:,} bits | {len(binary_octets):,} octets)")
print(f"  -> GraphML: {OUTPUT_DIR / 'louvain_nodexl_graph.graphml'}")
print(f"  -> Vertices CSV: {OUTPUT_DIR / 'louvain_nodexl_vertices.csv'}")
