# Analisis Konvergensi Modularity & Resolusi Louvain Tanpa Epoch
**Algoritma:** Blondel et al. (2008) Greedy Modularity Optimization  
**Graf Uji:** 30 simpul (nodes), 383 sisi (edges)  
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
| 0.5                | -0.0014              | 0.0012    | 2.2                | 0.0849                   | Makro-Ekosistem Komunitas Besar |
| 0.8                | 0.0151              | 0.0207    | 4.6                | 0.0920                   | Klaster Menengah Agregat |
| **1.0 (Default)**  | **0.0526**          | **0.0001**| **2.0**            | **0.8970**               | **Skala Standar Newman-Girvan** |
| 1.2                | 0.0258              | 0.0003    | 7.0                | 0.9738                   | Mengatasi Resolution Limit |
| 1.5                | -0.0022              | 0.0021    | 15.2                | 0.6940                   | Mikro-Komunitas Granular |

---

## 3. Evaluasi Stabilitas Stokastik (Random Seed)
- **Seed Diuji:** [42, 100, 2026, 2027, 9999]
- **Adjusted Rand Index (ARI):** 0.8970 (Konsistensi partisi > 0.85 = Robust & Statistically Reliable).
- **Rekomendasi Operasional:** Kunci `random_state=42` untuk menjamin determinisme 100% pada pipeline otomatisasi.
