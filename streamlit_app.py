"""
streamlit_app.py
Root entrypoint for Streamlit Community Cloud deployment.
Bridging to dashboard/app.py with proper repo path resolution.
"""
import os
import sys
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

dashboard_path = ROOT / "dashboard" / "app.py"
runpy.run_path(str(dashboard_path), run_name="__main__")
