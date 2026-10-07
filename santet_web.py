#!/usr/bin/env python3
"""
santet_web.py — mesin perintah `./bit web` untuk landing GitHub + Streamlit Cloud.
Dipanggil lewat bit (jangan dijalankan langsung kecuali untuk debug):

    ./bit web check        cek repo siap deploy (sintaks, path, ukuran, git-ignore, dependensi)
    ./bit web validate     validasi skema data/ dan results/sna_*     (pintas: ./bit validate)
    ./bit web stats        angka ringkas untuk README & kartu statistik
    ./bit web run          jalankan app lokal (streamlit run streamlit_app.py)
    ./bit web hero         buat ulang video hero lilin gelap (butuh ffmpeg)   (pintas: ./bit hero)
    ./bit web deploy       check + validate + cek git; --push untuk push ke main (pintas: ./bit deploy)

Kode keluar: 0 = lulus, 1 = ada error. Warning tidak menggagalkan.
Hanya butuh: Python 3.9+, pandas (streamlit untuk `run`).
"""
from __future__ import annotations

import argparse
import ast
import py_compile
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_ENTRY = ROOT / "streamlit_app.py"
APP_DIR = ROOT / "streamlit_app"
HERO = APP_DIR / "assets" / "hero.mp4"
REQUIRED = [
    "streamlit_app.py",
    "streamlit_app/app.py",
    "streamlit_app/pages/01_📖_Cerita.py",
    "santet_hero.py",
    "santet_m3.py",
    "santet_web.py",
    "santet_schema.py",
    "bit",
    "requirements.txt",
    "data/films_clean.csv",
]
APP_CODE = ["streamlit_app.py", "santet_hero.py", "santet_m3.py", "santet_schema.py", "streamlit_app/**/*.py"]
DISCLAIMER = "tidak berafiliasi"
MB = 1024 * 1024
LIMIT_WARN, LIMIT_FAIL = 50 * MB, 100 * MB      # batas GitHub: 100 MB per file
HERO_MAX = 8 * MB
# nama import → nama paket pip, untuk yang beda
PIP_NAME = {"sklearn": "scikit-learn", "yaml": "pyyaml", "PIL": "pillow", "cv2": "opencv-python"}
LOCAL_MODULES = {"santet_hero", "santet_m3", "santet_schema", "streamlit_app"}


# ── util tampilan ───────────────────────────────────────────────────────────
class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warns: list[str] = []

    def ok(self, msg: str) -> None:
        print(f"  ✅ {msg}")

    def warn(self, msg: str) -> None:
        self.warns.append(msg)
        print(f"  ⚠️  {msg}")

    def err(self, msg: str) -> None:
        self.errors.append(msg)
        print(f"  ❌ {msg}")

    def section(self, title: str) -> None:
        print(f"\n▸ {title}")

    def finish(self, name: str) -> int:
        print(f"\n{name}: {len(self.errors)} error, {len(self.warns)} warning")
        return 1 if self.errors else 0


def stdlib_names() -> set:
    """Nama modul standar Python. sys.stdlib_module_names baru ada di 3.10+;
    Python 3.9 bawaan macOS memakai daftar dari folder stdlib."""
    names = getattr(sys, "stdlib_module_names", None)
    if names:
        return set(names)
    import pkgutil
    import sysconfig
    std = sysconfig.get_paths()["stdlib"]
    out = set(sys.builtin_module_names)
    out |= {m.name for m in pkgutil.iter_modules([std, str(Path(std) / "lib-dynload")])}
    return out | {"__future__"}


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                              text=True, check=False).stdout.strip()
    except FileNotFoundError:
        return ""


def app_files() -> list[Path]:
    out: list[Path] = []
    for pat in APP_CODE:
        out += [p for p in ROOT.glob(pat) if p.is_file()]
    return sorted(set(out))


# ── perintah: check ─────────────────────────────────────────────────────────
def cmd_check(_: argparse.Namespace, r: Report | None = None) -> int:
    r = r or Report()
    in_git = bool(git("rev-parse", "--is-inside-work-tree"))

    r.section("File wajib")
    for rel in REQUIRED:
        p = ROOT / rel
        if not p.exists():
            r.err(f"tidak ada: {rel}")
        elif in_git and git("check-ignore", rel):
            r.err(f"di-ignore git, tidak akan ikut ke cloud: {rel}  →  git add -f '{rel}'")
        else:
            r.ok(rel)
    if HERO.exists():
        size = HERO.stat().st_size
        if in_git and git("check-ignore", str(HERO.relative_to(ROOT))):
            r.err("hero.mp4 di-ignore git  →  git add -f streamlit_app/assets/hero.mp4")
        elif size > HERO_MAX:
            r.warn(f"hero.mp4 {size / MB:.1f} MB, sebaiknya < {HERO_MAX // MB} MB (./bit hero)")
        else:
            r.ok(f"hero.mp4 {size / 1024:.0f} KB")
    else:
        r.warn("hero.mp4 tidak ada, halaman Cerita tampil tanpa video (./bit hero)")

    r.section("Sintaks & kode app")
    imports: set[str] = set()
    for p in app_files():
        rel = p.relative_to(ROOT)
        text = p.read_text(encoding="utf-8")
        try:
            py_compile.compile(str(p), doraise=True)
        except py_compile.PyCompileError as e:
            r.err(f"{rel}: {e.msg.strip().splitlines()[-1]}")
            continue
        if re.search(r"^(<<<<<<<|=======|>>>>>>>)", text, re.M):
            r.err(f"{rel}: masih ada penanda konflik git")
        if m := re.search(r"['\"](/Users/|/home/|C:\\\\)[^'\"]*", text):
            r.err(f"{rel}: path absolut {m.group(0)[:60]!r} (akan error di cloud)")
        for node in ast.walk(ast.parse(text)):
            if isinstance(node, ast.Import):
                imports |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                imports.add(node.module.split(".")[0])
    r.ok(f"{len(app_files())} file Python app lolos kompilasi")

    pages = list((APP_DIR / "pages").glob("*.py")) + [APP_DIR / "app.py"]
    hero_txt = (ROOT / "santet_hero.py").read_text(encoding="utf-8").lower() if (ROOT / "santet_hero.py").exists() else ""
    missing = [p.name for p in pages if p.exists() and DISCLAIMER not in p.read_text(encoding="utf-8").lower()
               and DISCLAIMER not in hero_txt]
    if missing:
        r.warn(f"disclaimer '{DISCLAIMER}' tidak ditemukan di: {', '.join(missing)}")
    else:
        r.ok("disclaimer tidak berafiliasi ada")

    r.section("Dependensi (requirements.txt)")
    req = (ROOT / "requirements.txt").read_text(encoding="utf-8") if (ROOT / "requirements.txt").exists() else ""
    declared = {re.split(r"[<>=!~\[ ;]", ln.strip(), maxsplit=1)[0].lower()
                for ln in req.splitlines() if ln.strip() and not ln.startswith("#")}
    std = stdlib_names()
    third = sorted(i for i in imports - LOCAL_MODULES if i not in std)
    for mod in third:
        pkg = PIP_NAME.get(mod, mod).lower()
        (r.ok if pkg in declared else r.err)(
            f"{mod} {'tercantum' if pkg in declared else 'BELUM ada di requirements.txt → tambah: ' + pkg}")

    r.section("Ukuran file (batas GitHub 100 MB)")
    tracked = git("ls-files").splitlines() if in_git else [str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file()]
    big = 0
    for rel in tracked:
        p = ROOT / rel
        if p.is_file() and (s := p.stat().st_size) > LIMIT_WARN:
            big += 1
            (r.err if s > LIMIT_FAIL else r.warn)(f"{rel}: {s / MB:.0f} MB")
    if not big:
        r.ok("tidak ada file > 50 MB")

    r.section("Rahasia")
    if (ROOT / ".streamlit/secrets.toml").exists() and in_git and not git("check-ignore", ".streamlit/secrets.toml"):
        r.err(".streamlit/secrets.toml TIDAK di-ignore — jangan sampai ter-commit")
    leaked = [f for f in tracked if re.search(r"(^|/)\.env$|secrets\.toml$", f)]
    (r.err if leaked else r.ok)(f"file rahasia ter-track: {leaked}" if leaked else "tidak ada .env / secrets ter-track")
    return r.finish("check")


# ── perintah: validate ──────────────────────────────────────────────────────
def cmd_validate(_: argparse.Namespace, r: Report | None = None) -> int:
    sys.path.insert(0, str(ROOT))
    import santet_schema as S

    r = r or Report()
    for t in S.TABLES:
        paths = sorted(ROOT.glob(t.path_glob))
        r.section(f"Tabel {t.name}  ({t.path_glob})")
        if not paths:
            r.warn("tidak ada file")
        for p in paths:
            errs = S.validate_table(t, p)
            rel = p.relative_to(ROOT)
            if errs:
                for e in errs:
                    r.err(f"{rel}: {e}")
            else:
                r.ok(f"{rel}")
    for folder in sorted(ROOT.glob("results/sna_*")):
        r.section(f"Folder SNA {folder.name}")
        errs, warns = S.validate_sna_folder(folder)
        for e in errs:
            r.err(e)
        for w in warns:
            r.warn(w)
        pngs = len(list(folder.glob("[0-2][0-9]_*.png")))
        r.ok(f"{pngs} PNG, {len(list(folder.glob('[0-2][0-9]_*.csv')))} CSV, 20 analisis terdaftar")
    return r.finish("validate")


# ── perintah: stats ─────────────────────────────────────────────────────────
def cmd_stats(_: argparse.Namespace) -> int:
    import pandas as pd

    f = pd.read_csv(ROOT / "data/films_clean.csv")
    print(f"film               : {len(f)}  ({int(f['tahun'].min())}–{int(f['tahun'].max())})")
    print(f"rumah produksi     : {f['rumah_produksi'].nunique()}")
    print(f"komentar (total)   : {int(f['comments'].sum()):,}".replace(",", "."))
    print(f"komentator unik    : {int(f['unique_commenters'].sum()):,}".replace(",", "."))
    print(f"penonton (total)   : {int(f['penonton'].sum()):,}".replace(",", "."))
    print(f"angka penonton final: {int(f['is_final'].sum())} dari {len(f)} film")
    for folder in sorted(ROOT.glob("results/sna_*/nodexl")):
        v = pd.read_csv(folder / "vertices.csv", encoding="utf-8-sig")
        e = pd.read_csv(folder / "edges.csv", encoding="utf-8-sig")
        print(f"SNA {folder.parent.name}: {int((v['Jenis'] == 'user').sum()):,} akun · "
              f"{len(e):,} sisi · {v['Komunitas'].nunique()} komunitas".replace(",", "."))
    return 0


# ── perintah: run ───────────────────────────────────────────────────────────
def cmd_run(a: argparse.Namespace) -> int:
    if not shutil.which("streamlit"):
        print("streamlit belum terpasang → pip install -r requirements.txt")
        return 1
    return subprocess.call(["streamlit", "run", str(APP_ENTRY), "--server.port", str(a.port)], cwd=ROOT)


# ── perintah: hero ──────────────────────────────────────────────────────────
def cmd_hero(a: argparse.Namespace) -> int:
    if not shutil.which("ffmpeg"):
        print("ffmpeg belum terpasang → macOS: brew install ffmpeg")
        return 1
    HERO.parent.mkdir(parents=True, exist_ok=True)
    if a.source:
        args = ["-i", a.source, "-t", "12", "-vf", "scale=1280:-2", "-an"]
    else:   # latar gelap 'lilin berkedip', bebas hak cipta
        args = ["-f", "lavfi", "-i", "color=c=0x1a0a05:s=1280x720:d=12", "-vf",
                "noise=alls=22:allf=t+u,vignette=PI/4,eq=brightness='0.04*sin(2*PI*t*1.3)':eval=frame"]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *args, "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-crf", "30", "-movflags", "+faststart", str(HERO)]
    rc = subprocess.call(cmd)
    if rc == 0:
        print(f"✅ {HERO.relative_to(ROOT)}  {HERO.stat().st_size / 1024:.0f} KB")
        print("   jangan lupa: git add -f streamlit_app/assets/hero.mp4")
    return rc


# ── perintah: deploy ────────────────────────────────────────────────────────
def cmd_deploy(a: argparse.Namespace) -> int:
    r = Report()
    print("═══ 1/3 check ═══")
    cmd_check(a, r)
    print("\n═══ 2/3 validate ═══")
    cmd_validate(a, r)
    print("\n═══ 3/3 git ═══")
    branch = git("branch", "--show-current")
    (r.ok if branch == "main" else r.err)(f"branch: {branch or '?'} (Streamlit Cloud membaca main)")
    dirty = git("status", "--porcelain")
    (r.warn if dirty else r.ok)("ada perubahan belum di-commit:\n" + dirty if dirty else "working tree bersih")
    git("fetch", "--quiet")
    ahead = git("rev-list", "--count", "@{u}..HEAD") or "?"
    behind = git("rev-list", "--count", "HEAD..@{u}") or "?"
    if behind not in ("0", "?"):
        r.err(f"tertinggal {behind} commit dari origin → git pull --rebase dulu")
    r.ok(f"belum di-push: {ahead} commit")
    code = r.finish("deploy")
    if code == 0 and a.push and ahead not in ("0", "?"):
        print("\n→ git push")
        return subprocess.call(["git", "push"], cwd=ROOT)
    if code == 0:
        print("\nSiap. Streamlit Cloud redeploy otomatis 1–2 menit setelah push ke main.")
    return code


def main() -> int:
    p = argparse.ArgumentParser(prog="./bit web", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="cek repo siap deploy").set_defaults(fn=cmd_check)
    sub.add_parser("validate", help="validasi skema data").set_defaults(fn=cmd_validate)
    sub.add_parser("stats", help="angka ringkas").set_defaults(fn=cmd_stats)
    run = sub.add_parser("run", help="jalankan app lokal")
    run.add_argument("--port", type=int, default=8501)
    run.set_defaults(fn=cmd_run)
    hero = sub.add_parser("hero", help="buat video hero")
    hero.add_argument("--source", help="video sumber (default: latar lilin sintetis)")
    hero.set_defaults(fn=cmd_hero)
    dep = sub.add_parser("deploy", help="gerbang sebelum push")
    dep.add_argument("--push", action="store_true", help="push otomatis bila semua lulus")
    dep.set_defaults(fn=cmd_deploy)
    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
