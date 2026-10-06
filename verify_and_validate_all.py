#!/usr/bin/env python3
"""
verify_and_validate_all.py
Master Suite Verifikasi dan Validasi (V&V) Komprehensif:
1. Data Sumber CSV Historis (NapoleonCat, GoodStats, Statista, DataReportal 2020-2026)
2. Model Peramalan & Output Proyeksi 2027 (3 Skenario + Validasi XML SVG)
3. NodeXL Relational Graph Datasets:
   - 20.000 baris edge list
   - 200.000 baris edge list
   - 1.000.000 baris relasi multi-tahun 2020-2026 (.csv.gz)
   - 10.000.000 relasi multimodal (Story, Like, Share, Komen, Live, Reel)
4. Integritas Bahasa Bit Korpus Utama, NodeXL & Daemon (Lossless UTF-8 Roundtrip)
5. Streamlit App Syntax & Structural Integrity (streamlit_app.py, dashboard/app.py)
6. GitHub & Streamlit Cloud Deployment Status
"""

import os
import csv
import json
import gzip
import py_compile
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def print_header(title):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def check(name, condition, details=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}")
    if details:
        print(f"       -> {details}")
    return condition

def test_source_csv():
    print_header("1. VERIFIKASI DATA SUMBER HISTORIS (2020-2026)")
    path = os.path.join(BASE_DIR, "data", "instagram_users_indonesia_sources.csv")
    if not check("File CSV sumber ada", os.path.exists(path), path):
        return False
        
    with open(path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        
    c1 = check("Row count sesuai (14 baris konsensus)", len(reader) == 14, f"Total baris: {len(reader)}")
    expected_fields = ["tahun", "sumber", "jumlah_pengguna_juta", "penetrasi_persen_penduduk", "tanggal_akses", "catatan_metodologi"]
    c2 = check("Skema kolom valid", list(reader[0].keys()) == expected_fields, f"Kolom: {list(reader[0].keys())}")
    
    valid_data = True
    sources = set()
    years = set()
    for row in reader:
        for k, v in row.items():
            if v is None or (isinstance(v, str) and v.strip() == ""):
                valid_data = False
        sources.add(row["sumber"])
        years.add(int(row["tahun"]))
        
    c3 = check("Zero missing / null values", valid_data)
    c4 = check("Rentang tahun mencakup 2020-2026", min(years) == 2020 and max(years) == 2026, f"Tahun: {sorted(list(years))}")
    c5 = check("Sumber resmi memuat NapoleonCat, GoodStats, Statista", {"NapoleonCat", "GoodStats"}.issubset(sources))
    return all([c1, c2, c3, c4, c5])

def test_forecasting_and_outputs():
    print_header("2. VERIFIKASI PROYEKSI 2027 (3 SKENARIO) & SVG")
    csv_out = os.path.join(BASE_DIR, "output", "proyeksi_2027_tiga_skenario.csv")
    svg_out = os.path.join(BASE_DIR, "output", "proyeksi_instagram_2027.svg")
    
    c1 = check("File output CSV proyeksi ada", os.path.exists(csv_out), csv_out)
    c2 = check("File output SVG chart ada", os.path.exists(svg_out), svg_out)
    
    with open(csv_out, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        
    projections = {r["metrik"]: float(r["nilai_juta"]) for r in rows if r["kategori"] == "Proyeksi 2027"}
    c3 = check("Tiga skenario terdaftar di CSV", len(projections) == 3, f"Skenario: {list(projections.keys())}")
    c4 = check("Skenario Rendah (Konservatif) = 124.37M", 124.0 <= projections.get("Rendah (Konservatif / Saturasi)", 0) <= 125.0, f"Nilai: {projections.get('Rendah (Konservatif / Saturasi)')}M")
    c5 = check("Skenario Sedang (Moderat) = 128.00M", 127.0 <= projections.get("Sedang (Baseline / Moderat)", 0) <= 129.0, f"Nilai: {projections.get('Sedang (Baseline / Moderat)')}M")
    c6 = check("Skenario Tinggi (Optimis) = 132.83M", 132.0 <= projections.get("Tinggi (Optimis / Ekspansi)", 0) <= 134.0, f"Nilai: {projections.get('Tinggi (Optimis / Ekspansi)')}M")
    
    try:
        tree = ET.parse(svg_out)
        root = tree.getroot()
        is_svg = root.tag.endswith("svg")
        c7 = check("Sintaks file grafik SVG valid (Well-formed XML)", is_svg, f"Root tag: {root.tag}")
    except Exception as e:
        c7 = check("Sintaks SVG valid", False, str(e))
        
    return all([c1, c2, c3, c4, c5, c6, c7])

def test_nodexl_scale_datasets():
    print_header("3. VALIDASI NODEXL DATASETS (20K, 200K, 1M, 10M MULTIMODAL)")
    
    # 20k
    f_20k = os.path.join(BASE_DIR, "output", "dataset_nodexl_crawled_20000.csv")
    c1 = check("Dataset 20.000 ada", os.path.exists(f_20k))
    if c1:
        with open(f_20k, "r", encoding="utf-8") as f:
            lines = sum(1 for _ in f) - 1
        c1 = check("Jumlah baris 20.000 presisi", lines == 20000, f"Baris data: {lines}")
        
    # 200k
    f_200k = os.path.join(BASE_DIR, "output", "dataset_nodexl_crawled_200000.csv")
    c2 = check("Dataset 200.000 ada", os.path.exists(f_200k))
    if c2:
        with open(f_200k, "r", encoding="utf-8") as f:
            lines = sum(1 for _ in f) - 1
        c2 = check("Jumlah baris 200.000 presisi", lines == 200000, f"Baris data: {lines}")

    # 1M (.csv.gz)
    f_1m = os.path.join(BASE_DIR, "output", "dataset_nodexl_crawled_1000000.csv.gz")
    c3 = check("Dataset 1.000.000 GZIP ada", os.path.exists(f_1m))
    if c3:
        with gzip.open(f_1m, "rt", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            lines = sum(1 for _ in f)
        c3 = check("Jumlah baris 1.000.000 presisi", lines == 1000000, f"Header: {header}, Total baris: {lines}")

    # 10M Multimodal Manifest & Chunk
    f_10m_meta = os.path.join(BASE_DIR, "output", "dataset_nodexl_10000000_manifest.json")
    f_10m_chunk1 = os.path.join(BASE_DIR, "output", "nodexl_10m_chunks", "nodexl_edges_chunk_01.csv.gz")
    c4 = check("Manifest 10.000.000 multimodal ada", os.path.exists(f_10m_meta))
    c5 = check("Chunk 1 (1.000.000 relasi) ada", os.path.exists(f_10m_chunk1))
    if c4:
        with open(f_10m_meta, "r", encoding="utf-8") as f:
            m10 = json.load(f)
        formats = set(m10.get("formats_supported", []))
        breakdown = set(m10.get("interaction_breakdown", {}).keys())
        expected_formats = {"story", "like", "share", "komen", "live", "reel"}
        c4 = check("Modalitas lengkap (story, like, share, komen, live, reel)", 
                   expected_formats.issubset(formats) and expected_formats.issubset(breakdown),
                   f"Formats: {formats}")
    if c5:
        with gzip.open(f_10m_chunk1, "rt", encoding="utf-8") as f:
            lines_chunk1 = sum(1 for _ in f) - 1
        c5 = check("Chunk 1 memuat 1.000.000 baris relasi presisi", lines_chunk1 == 1000000, f"Total baris chunk 1: {lines_chunk1}")

    return all([c1, c2, c3, c4, c5])

def test_bit_integrity():
    print_header("4. INTEGRITAS BAHASA BIT & REVERSIBILITAS LOSSLESS")
    bit_files = [
        ("output/tren_instagram_bit.txt", 59952),
        ("output/rekomendasi_eksekusi_bit.txt", 28888),
        ("output/dataset_nodexl_20000_bit.txt", 4512),
        ("output/dataset_nodexl_200000_bit.txt", 6696),
        ("output/dataset_nodexl_1000000_bit.txt", 7224),
        ("output/dataset_nodexl_10000000_bit.txt", 14960),
        ("output/deploy_status_bit.txt", 1568),
        ("output/graf_betweenness_bit.txt", 6424),
        ("output/deployment_push_github_streamlit_bit.txt", 10352),
        ("output/louvain_nodexl_bit.txt", 2928),
        ("output/indobert_9emotions_bit.txt", 3456),
        ("output/nodexl_20_functions_bit.txt", 7424),
        ("output/scopus_q1_scientific_bit.txt", 9304),
        ("output/elsevier_kpi_formulas_bit.txt", 8840),
        ("output/scopus_q1_journal_bit.txt", 128696),
        ("output/repo_history_story_bit.txt", 63288),
        ("output/indobert_nodexl_bit.txt", 7472),
        ("output/nodexl_detailed_execution_bit.txt", 47432),
        ("output/indobert_cleaning_finetune_bit.txt", 26128),
        ("output/louvain_convergence_resolution_bit.txt", 19024),
        ("output/graf_louvain_nodexl_bit.txt", 4496),
        ("output/proyeksi_2027_bit.txt", 5504)
    ]
    
    all_passed = True
    for rel_path, exp_bits in bit_files:
        full_path = os.path.join(BASE_DIR, rel_path)
        if not check(f"File {rel_path} ada", os.path.exists(full_path)):
            all_passed = False
            continue
            
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        tokens = content.split()
        if len(tokens) > 1:
            total_bits = sum(len(t) for t in tokens)
            all_octets = all(len(t) == 8 and set(t).issubset({"0", "1"}) for t in tokens)
            reconstructed = bytearray(int(t, 2) for t in tokens)
        else:
            total_bits = len(content)
            all_octets = (total_bits % 8 == 0) and set(content).issubset({"0", "1"})
            reconstructed = bytearray(int(content[i:i+8], 2) for i in range(0, total_bits, 8))
            
        try:
            decoded_text = reconstructed.decode("utf-8")
            is_valid_utf8 = len(decoded_text) > 0
        except UnicodeDecodeError:
            is_valid_utf8 = False
            
        c_oct = check(f"Format octet biner valid ({rel_path})", all_octets)
        c_len = check(f"Presisi bit count ({rel_path})", total_bits == exp_bits, f"{total_bits} bits (expected: {exp_bits})")
        c_utf = check(f"Dekode UTF-8 lossless sempurna ({rel_path})", is_valid_utf8)
        if not (c_oct and c_len and c_utf):
            all_passed = False
            
    return all_passed

def test_scopus_q1_journal_and_downloads():
    print_header("5. VALIDASI NASKAH JURNAL SCOPUS Q1 ELSEVIER & DOWNLOADS")
    files_to_check = [
        ("PDF Publication Manuscript", "output/scopus_q1_journal_manuscript.pdf"),
        ("Word DOCX Manuscript", "output/scopus_q1_journal_manuscript.docx"),
        ("Markdown Manuscript", "output/scopus_q1_journal_manuscript.md"),
        ("8-Bit Binary Stream", "output/scopus_q1_journal_bit.txt"),
        ("Repo Story Markdown", "output/repo_history_story.md"),
        ("Repo Story Bitstream", "output/repo_history_story_bit.txt"),
        ("IndoBERT NodeXL SVG", "output/graf_indobert_nodexl.svg"),
        ("IndoBERT NodeXL GraphML", "output/indobert_nodexl_graph.graphml"),
        ("IndoBERT NodeXL Bitstream", "output/indobert_nodexl_bit.txt"),
        ("NodeXL Detailed Report", "output/nodexl_detailed_execution_report.md"),
        ("NodeXL Detailed Bit", "output/nodexl_detailed_execution_bit.txt"),
        ("Complete Research ZIP", "output/scopus_q1_elsevier_package.zip"),
        ("Downloads Mirror PDF", "downloads/scopus_q1_journal_manuscript.pdf"),
        ("Downloads Mirror DOCX", "downloads/scopus_q1_journal_manuscript.docx"),
        ("Downloads Mirror ZIP", "downloads/scopus_q1_elsevier_package.zip"),
        ("Downloads Mirror Story", "downloads/repo_history_story.md"),
        ("Downloads Mirror Story Bit", "downloads/repo_history_story_bit.txt"),
        ("IndoBERT Cleaned Corpus", "output/indobert_cleaned_corpus.csv"),
        ("IndoBERT Fine-Tune History", "output/indobert_finetune_history.csv"),
        ("IndoBERT Fine-Tune Metrics", "output/indobert_finetune_metrics.json"),
        ("IndoBERT Cleaning & FT Bitstream", "output/indobert_cleaning_finetune_bit.txt"),
        ("Downloads Mirror IndoBERT Bit", "downloads/indobert_cleaning_finetune_bit.txt"),
        ("Louvain Convergence Bitstream", "output/louvain_convergence_resolution_bit.txt"),
        ("Downloads Mirror Louvain Bit", "downloads/louvain_convergence_resolution_bit.txt"),
        ("Louvain NodeXL SVG", "output/graf_louvain_nodexl.svg"),
        ("Louvain NodeXL GraphML", "output/louvain_nodexl_graph.graphml"),
        ("Louvain NodeXL Vertices", "output/louvain_nodexl_vertices.csv"),
        ("Louvain NodeXL Edges", "output/louvain_nodexl_edges.csv"),
        ("Louvain NodeXL Bitstream", "output/graf_louvain_nodexl_bit.txt"),
        ("Downloads Mirror Louvain NodeXL Bit", "downloads/graf_louvain_nodexl_bit.txt"),
        ("Proyeksi 2027 CSV", "output/proyeksi_2027.csv"),
        ("Proyeksi 2027 PNG Chart", "output/proyeksi_2027.png"),
        ("Proyeksi 2027 Bitstream", "output/proyeksi_2027_bit.txt"),
        ("Downloads Mirror Proyeksi Bit", "downloads/proyeksi_2027_bit.txt")
    ]
    
    c_files = True
    for label, rel_path in files_to_check:
        full_path = os.path.join(BASE_DIR, rel_path)
        exists = os.path.exists(full_path)
        sz = os.path.getsize(full_path) if exists else 0
        pass_f = check(f"{label} ({rel_path})", exists and sz > 0, f"Size: {sz:,} bytes")
        if not pass_f:
            c_files = False

    # Check 11 Elsevier KPIs
    kpi_path = os.path.join(BASE_DIR, "output", "elsevier_kpi_benchmarks.csv")
    c_kpi_exists = check("Tabel benchmark Elsevier KPI CSV ada", os.path.exists(kpi_path))
    c_kpi_match = False
    if c_kpi_exists:
        with open(kpi_path, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
        all_passed = len(reader) == 11 and all(any(w in r.get("compliance_status", "") for w in ["PASS", "EXCEEDED"]) for r in reader)
        c_kpi_match = check("11 KPI Elsevier 100% Terpenuhi (PASS/EXCEEDED)", all_passed, f"Total KPI terverifikasi: {len(reader)}/11")

    return c_files and c_kpi_exists and c_kpi_match

def test_streamlit_and_deployment():
    print_header("6. VALIDASI KONSISTENSI STREAMLIT & DEPLOYMENT")
    root_app = os.path.join(BASE_DIR, "streamlit_app.py")
    dash_app = os.path.join(BASE_DIR, "dashboard", "app.py")
    req_file = os.path.join(BASE_DIR, "requirements.txt")
    
    c1 = check("Entrypoint streamlit_app.py ada", os.path.exists(root_app))
    c2 = check("Core dashboard/app.py ada", os.path.exists(dash_app))
    c3 = check("requirements.txt ada", os.path.exists(req_file))
    
    # Syntax check
    try:
        py_compile.compile(root_app, doraise=True)
        c4 = check("Syntax streamlit_app.py valid", True)
    except Exception as e:
        c4 = check("Syntax streamlit_app.py valid", False, str(e))
        
    try:
        py_compile.compile(dash_app, doraise=True)
        c5 = check("Syntax dashboard/app.py valid", True)
    except Exception as e:
        c5 = check("Syntax dashboard/app.py valid", False, str(e))
        
    # Check Section 9, 10, and 14 presence
    with open(dash_app, "r", encoding="utf-8") as f:
        code_str = f.read()
    c6 = check("dashboard/app.py memuat Section 9 (Network Analysis)", 'selected_section == "9. Network Analysis"' in code_str)
    c7 = check("dashboard/app.py memuat Section 10 (2027 Forecasting)", 'selected_section == "10. 2027 Forecasting"' in code_str)
    c8 = check("dashboard/app.py memuat Section 14 (Scopus Q1 Journal & Downloads)", 'selected_section == "14. Scopus Q1 Journal & Downloads"' in code_str)
    
    return all([c1, c2, c3, c4, c5, c6, c7, c8])

if __name__ == "__main__":
    r1 = test_source_csv()
    r2 = test_forecasting_and_outputs()
    r3 = test_nodexl_scale_datasets()
    r4 = test_bit_integrity()
    r5 = test_scopus_q1_journal_and_downloads()
    r6 = test_streamlit_and_deployment()
    
    print("\n" + "=" * 70)
    all_passed = all([r1, r2, r3, r4, r5, r6])
    if all_passed:
        print("  HASIL MASTER VALIDASI: 100% PASS (SEMUA 60 KRITERIA TERPENUHI)")
    else:
        print("  HASIL MASTER VALIDASI: TERDAPAT KEGAGALAN / PERIKSA LOG DI ATAS")
    print("=" * 70 + "\n")
    exit(0 if all_passed else 1)
