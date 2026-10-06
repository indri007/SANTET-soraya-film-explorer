from pathlib import Path

src = Path("instagram_pipeline_10steps.py")

print("=" * 70)
print("INSTAGRAM 2027 — PIPELINE FILE CHECK")
print("=" * 70)

if not src.exists():
    print("❌ instagram_pipeline_10steps.py tidak ditemukan")
    raise SystemExit(1)

text = src.read_text(encoding="utf-8")

print("File ditemukan.")
print("Ukuran:", len(text), "characters")
print("Baris :", len(text.splitlines()))

required = [
    "step1",
    "step2",
    "step3",
    "step4",
    "step5",
    "step6",
    "step7",
    "step8",
    "step9",
    "step10",
    "main",
]

print("\nPemeriksaan fungsi:")

for name in required:
    found = name in text
    print(
        f"{'✓' if found else '❌'} {name}"
    )

if "step8_machine_learning" in text:
    print("\n✓ STEP 08 ditemukan")
else:
    print("\n❌ STEP 08 tidak ditemukan")

print("\nKesimpulan:")

if all(name in text for name in required):
    print("✓ Struktur pipeline tampaknya lengkap.")
else:
    print("❌ Pipeline TIDAK lengkap.")
    print("❌ Jangan jalankan pipeline ini dulu.")
    print("❌ File perlu dipulihkan dari versi lengkap.")
