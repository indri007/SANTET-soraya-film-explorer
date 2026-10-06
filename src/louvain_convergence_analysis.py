#!/usr/bin/env python3
"""
src/louvain_convergence_analysis.py
===================================
Analisis Konvergensi Modularity & Stabilitas Resolusi Louvain Tanpa Epoch
dengan Representasi Bahasa Biner (8-bit UTF-8 Binary Stream).

Karakteristik Teori:
- Algoritma: Blondel et al. (2008) Greedy Modularity Optimization
- Kriteria Berhenti: Konvergensi Stasioner dQ <= 0 (Tidak Memerlukan Epoch)
- Parameter Kunci:
  1. Resolution (gamma): Mengontrol skala komunitas (0.5 s/d 1.5)
  2. Random Seed: Menguji stabilitas partisi stokastik menggunakan Adjusted Rand Index (ARI)

Output:
- output/louvain_convergence_resolution_report.md
- output/louvain_convergence_resolution_bit.txt
- output/louvain_convergence_manifest.json
- downloads/louvain_convergence_resolution_bit.txt
- downloads/louvain_convergence_resolution_report.md
"""

import json
from pathlib import Path
import networkx as nx
import community as community_louvain
import numpy as np

REPO_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_DIR / "output"
DOWNLOADS_DIR = REPO_DIR / "downloads"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

def adjusted_rand_index(labels_true, labels_pred):
    """Menghitung Adjusted Rand Index (ARI) murni tanpa ketergantungan sklearn."""
    from collections import Counter
    n = len(labels_true)
    if n <= 1:
        return 1.0
    
    classes_true = {}
    classes_pred = {}
    for idx, (lt, lp) in enumerate(zip(labels_true, labels_pred)):
        classes_true.setdefault(lt, []).append(idx)
        classes_pred.setdefault(lp, []).append(idx)
        
    contingency = Counter()
    for lt, lp in zip(labels_true, labels_pred):
        contingency[(lt, lp)] += 1
        
    def comb2(val):
        return val * (val - 1) // 2
        
    sum_comb_c = sum(comb2(cnt) for cnt in contingency.values())
    sum_comb_a = sum(comb2(len(members)) for members in classes_true.values())
    sum_comb_b = sum(comb2(len(members)) for members in classes_pred.values())
    
    expected_index = (sum_comb_a * sum_comb_b) / comb2(n)
    max_index = (sum_comb_a + sum_comb_b) / 2.0
    
    if max_index == expected_index:
        return 1.0
    return (sum_comb_c - expected_index) / (max_index - expected_index)

def run_louvain_analysis():
    graph_path = OUTPUT_DIR / "nodexl_complete_graph.graphml"
    if not graph_path.exists():
        graph_path = OUTPUT_DIR / "indobert_nodexl_graph.graphml"
        
    print(f"[1/4] Memuat graf dari: {graph_path.name}")
    G = nx.read_graphml(graph_path)
    G = nx.Graph(G)  # convert to undirected
    
    resolutions = [0.5, 0.8, 1.0, 1.2, 1.5]
    seeds = [42, 100, 2026, 2027, 9999]
    
    print("[2/4] Menjalankan uji konvergensi tanpa epoch lintas resolution & seed...")
    results = {}
    
    for gamma in resolutions:
        partitions_for_gamma = []
        modularities = []
        num_communities_list = []
        
        for s in seeds:
            part = community_louvain.best_partition(G, resolution=gamma, random_state=s)
            mod = community_louvain.modularity(part, G)
            n_comm = len(set(part.values()))
            
            partitions_for_gamma.append(part)
            modularities.append(mod)
            num_communities_list.append(n_comm)
            
        # Hitung stabilitas antar-seed (Pairwise Adjusted Rand Index)
        nodes = list(G.nodes())
        ari_scores = []
        for i in range(len(seeds)):
            for j in range(i + 1, len(seeds)):
                labels_i = [partitions_for_gamma[i][n] for n in nodes]
                labels_j = [partitions_for_gamma[j][n] for n in nodes]
                ari = adjusted_rand_index(labels_i, labels_j)
                ari_scores.append(ari)
                
        results[gamma] = {
            "mean_modularity": float(np.mean(modularities)),
            "std_modularity": float(np.std(modularities)),
            "mean_communities": float(np.mean(num_communities_list)),
            "stability_ari": float(np.mean(ari_scores)) if ari_scores else 1.0,
            "modularity_samples": [float(m) for m in modularities]
        }
        print(f"      -> Resolution gamma={gamma:3.1f}: Q={results[gamma]['mean_modularity']:.4f} +/- {results[gamma]['std_modularity']:.4f} | Komunitas={results[gamma]['mean_communities']:.1f} | ARI Stabilitas={results[gamma]['stability_ari']:.4f}")

    # Susun Laporan Ilmiah
    report_md = f"""# Analisis Konvergensi Modularity & Resolusi Louvain Tanpa Epoch
**Algoritma:** Blondel et al. (2008) Greedy Modularity Optimization  
**Graf Uji:** {len(G.nodes()):,} simpul (nodes), {len(G.edges()):,} sisi (edges)  
**Kriteria Konvergensi:** Titik Stasioner Delta Q <= 0 (Tanpa Memerlukan Konsep Epoch)

---

## 1. Pembuktian Matematis: Mengapa Louvain Tidak Memerlukan Epoch?
- **Fase 1 (Optimasi Modularitas Lokal):** Setiap node ditugaskan ke komunitas tetangga yang memaksimalkan gain modularitas:
  Delta Q = [(Sigma_in + 2k_i,in)/(2m) - ((Sigma_tot + k_i)/(2m))^2] - [Sigma_in/(2m) - (Sigma_tot/(2m))^2 - (k_i/(2m))^2]
  Iterasi lokal berlangsung hingga Delta Q <= 0 untuk seluruh simpul.
- **Fase 2 (Agregasi Graf Super-Node):** Komunitas dikontraksikan menjadi meta-node.
- **Konvergensi Global:** Siklus berhenti total saat struktur partisi tidak dapat ditingkatkan lagi secara modular. Menambahkan epoch redundan karena nilai modularity telah mencapai konvergensi optimal.

---

## 2. Pengaruh Parameter Resolution (gamma)
Formulasi Reichardt-Bornholdt Modularity:
Q_gamma = (1/2m) * SUM [ A_ij - gamma * (k_i * k_j)/(2m) ] * delta(c_i, c_j)

| Resolution (gamma) | Mean Modularity (Q) | Std Dev Q | Rata-rata Komunitas | Stabilitas Partisi (ARI) | Interpretasi Skala |
|:------------------:|:-------------------:|:---------:|:-------------------:|:------------------------:|:-------------------|
| 0.5                | {results[0.5]['mean_modularity']:.4f}              | {results[0.5]['std_modularity']:.4f}    | {results[0.5]['mean_communities']:.1f}                | {results[0.5]['stability_ari']:.4f}                   | Makro-Ekosistem Komunitas Besar |
| 0.8                | {results[0.8]['mean_modularity']:.4f}              | {results[0.8]['std_modularity']:.4f}    | {results[0.8]['mean_communities']:.1f}                | {results[0.8]['stability_ari']:.4f}                   | Klaster Menengah Agregat |
| **1.0 (Default)**  | **{results[1.0]['mean_modularity']:.4f}**          | **{results[1.0]['std_modularity']:.4f}**| **{results[1.0]['mean_communities']:.1f}**            | **{results[1.0]['stability_ari']:.4f}**               | **Skala Standar Newman-Girvan** |
| 1.2                | {results[1.2]['mean_modularity']:.4f}              | {results[1.2]['std_modularity']:.4f}    | {results[1.2]['mean_communities']:.1f}                | {results[1.2]['stability_ari']:.4f}                   | Mengatasi Resolution Limit |
| 1.5                | {results[1.5]['mean_modularity']:.4f}              | {results[1.5]['std_modularity']:.4f}    | {results[1.5]['mean_communities']:.1f}                | {results[1.5]['stability_ari']:.4f}                   | Mikro-Komunitas Granular |

---

## 3. Evaluasi Stabilitas Stokastik (Random Seed)
- **Seed Diuji:** [42, 100, 2026, 2027, 9999]
- **Adjusted Rand Index (ARI):** {results[1.0]['stability_ari']:.4f} (Konsistensi partisi > 0.85 = Robust & Statistically Reliable).
- **Rekomendasi Operasional:** Kunci `random_state=42` untuk menjamin determinisme 100% pada pipeline otomatisasi.
"""

    rep_path = OUTPUT_DIR / "louvain_convergence_resolution_report.md"
    rep_dl = DOWNLOADS_DIR / "louvain_convergence_resolution_report.md"
    with open(rep_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    with open(rep_dl, "w", encoding="utf-8") as f:
        f.write(report_md)

    print("[3/4] Mengonversi laporan ke representasi Bahasa Biner (8-bit UTF-8 stream)...")
    utf8_bytes = report_md.encode("utf-8")
    binary_octets = [f"{b:08b}" for b in utf8_bytes]
    bitstream_str = " ".join(binary_octets)
    total_bits = len(binary_octets) * 8
    
    bit_path = OUTPUT_DIR / "louvain_convergence_resolution_bit.txt"
    bit_dl = DOWNLOADS_DIR / "louvain_convergence_resolution_bit.txt"
    with open(bit_path, "w", encoding="utf-8") as f:
        f.write(bitstream_str)
    with open(bit_dl, "w", encoding="utf-8") as f:
        f.write(bitstream_str)

    # Verifikasi Lossless Roundtrip
    reconstructed_bytes = bytearray(int(b, 2) for b in binary_octets)
    decoded_text = reconstructed_bytes.decode("utf-8")
    assert decoded_text == report_md, "ERROR: Lossless roundtrip verification failed!"
    print(f"[4/4] Verifikasi Lossless: 100% SUKSES! ({total_bits:,} bits | {len(binary_octets):,} octets)")

    manifest = {
        "title": "Louvain Convergence & Resolution Stability 8-Bit Binary Manifest",
        "algorithm": "Blondel et al. (2008) Greedy Modularity Optimization",
        "total_nodes": len(G.nodes()),
        "total_edges": len(G.edges()),
        "total_bits": total_bits,
        "total_octets": len(binary_octets),
        "resolution_benchmark": results,
        "lossless_verified": True
    }
    with open(OUTPUT_DIR / "louvain_convergence_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return total_bits, results

if __name__ == "__main__":
    total_bits, res = run_louvain_analysis()
    print(f"\nEksekusi tuntas: {total_bits} bits tersimpan.")
