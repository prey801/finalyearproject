import nbformat as nbf

CELL_1_SOURCE = """\
#@title 1. Runtime and configuration
import os, sys
REPO_URL = "https://github.com/prey801/finalyearproject.git"
BRANCH = "main"
PROJECT_DIR = "/content/finalyearproject"
DRIVE_WEIGHTS_DIR = "/content/drive/MyDrive/medscope-ai/weights"

SUPABASE_URL = "" #@param {type:"string"}
SUPABASE_ANON_KEY = "" #@param {type:"string"}
GITHUB_TOKEN = "" #@param {type:"string"}
NGROK_AUTH_TOKEN = "" #@param {type:"string"}
"""

CELL_8_SOURCE = """\
#@title 8. Run the Entire System
%cd $PROJECT_DIR
import os, subprocess, time, urllib.request
from pathlib import Path

# --- Set environment variables ---
if "GITHUB_TOKEN" in globals() and GITHUB_TOKEN:
    os.environ['GITHUB_TOKEN'] = GITHUB_TOKEN
    print("✅ GITHUB_TOKEN set for GPT-4o")

os.environ['YOLO_WEIGHTS_PATH'] = str(Path(PROJECT_DIR) / "models/weights/yolov11_malaria_best.pt")
os.environ['SWIN_WEIGHTS_PATH'] = str(Path(PROJECT_DIR) / "models/weights/swin_malaria_best.pth")
os.environ['SAM2_WEIGHTS_PATH'] = str(Path(PROJECT_DIR) / "sam2_hiera_small.pt")
os.environ['ALLOWED_ORIGINS'] = "*"

# Install pyngrok
import subprocess as _sp
_sp.run(["pip", "install", "-q", "pyngrok"], check=True)

from pyngrok import ngrok

if "NGROK_AUTH_TOKEN" in globals() and NGROK_AUTH_TOKEN:
    ngrok.set_auth_token(NGROK_AUTH_TOKEN)
    print("✅ ngrok auth token set")
else:
    print("⚠️  No NGROK_AUTH_TOKEN — tunnels may be rate-limited. Get a free token at https://dashboard.ngrok.com")

# --- STEP 1: Start Backend (0.0.0.0 to ensure IPv4 binding) ---
print("\\n[1/5] Starting FastAPI backend...")
backend_process = subprocess.Popen(
    ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd=PROJECT_DIR
)

# Wait until backend is ACTUALLY ready (model loading takes 2-5 min)
print("   Waiting for backend to be ready (models loading, this can take several minutes)...")
for i in range(150):
    try:
        urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2)
        print(f"   ✅ Backend ready! ({i*2}s)")
        break
    except Exception:
        time.sleep(2)
        if i > 0 and i % 15 == 0:
            print(f"   ⏳ Still loading models... ({i*2}s elapsed)")
else:
    print("   ⚠️  Backend health check timed out — proceeding anyway")

# --- STEP 2: Start Celery Worker ---
print("[2/5] Starting Celery worker...")
celery_process = subprocess.Popen(
    ["celery", "-A", "backend.worker", "worker", "--loglevel=info"],
    cwd=PROJECT_DIR
)
time.sleep(3)

# --- STEP 3: Expose Backend via ngrok (use 127.0.0.1 NOT localhost to avoid IPv6) ---
print("[3/5] Opening ngrok tunnel for backend...")
backend_tunnel = ngrok.connect(addr="http://127.0.0.1:8000", bind_tls=True)
backend_url = backend_tunnel.public_url
print(f"   ⚙️  Backend: {backend_url}")

# --- STEP 4: Write frontend .env.local with backend URL ---
print("[4/5] Writing frontend config (.env.local)...")
with open(f"{PROJECT_DIR}/frontend/.env.local", "w") as f:
    f.write(f"NEXT_PUBLIC_API_URL={backend_url}\\n")
    if "SUPABASE_URL" in globals() and SUPABASE_URL:
        f.write(f"NEXT_PUBLIC_SUPABASE_URL={SUPABASE_URL}\\n")
        f.write(f"NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY={SUPABASE_ANON_KEY}\\n")
        f.write(f"NEXT_PUBLIC_SUPABASE_ANON_KEY={SUPABASE_ANON_KEY}\\n")

# --- STEP 5: Build Next.js frontend ---
print("[5/5] Building Next.js frontend (~2 mins)...")
build_process = subprocess.Popen(["npm", "run", "build"], cwd=f"{PROJECT_DIR}/frontend")
build_process.wait()
print("   ✅ Build complete. Starting frontend server on 0.0.0.0...")

# Start Next.js explicitly on 0.0.0.0 (IPv4) to avoid ERR_NGROK_8012
frontend_process = subprocess.Popen(
    ["npx", "next", "start", "-H", "0.0.0.0", "-p", "3000"],
    cwd=f"{PROJECT_DIR}/frontend"
)

# Wait until frontend is ACTUALLY ready before opening ngrok tunnel
print("   Waiting for Next.js to be ready on port 3000...")
for i in range(60):
    try:
        urllib.request.urlopen("http://127.0.0.1:3000", timeout=2)
        print(f"   ✅ Frontend ready! ({i*2}s)")
        break
    except Exception:
        time.sleep(2)
        if i > 0 and i % 10 == 0:
            print(f"   ⏳ Still starting... ({i*2}s)")
else:
    print("   ⚠️  Frontend health check timed out — proceeding anyway")

# Open ngrok tunnel — use 127.0.0.1 NOT localhost (avoids IPv6 [::1] which causes ERR_NGROK_8012)
frontend_tunnel = ngrok.connect(
    addr="http://127.0.0.1:3000",
    bind_tls=True,
    host_header="rewrite"
)
frontend_url = frontend_tunnel.public_url

print("\\n" + "="*60)
print(f"🚀 SYSTEM IS RUNNING!")
print(f"🌍 Frontend: {frontend_url}")
print(f"⚙️  Backend:  {backend_url}")
print("="*60 + "\\n")

try:
    frontend_process.wait()
except KeyboardInterrupt:
    print("\\nShutting down...")
    ngrok.disconnect(frontend_tunnel.public_url)
    ngrok.disconnect(backend_tunnel.public_url)
    ngrok.kill()
    backend_process.terminate()
    celery_process.terminate()
    frontend_process.terminate()
"""


def rewrite_notebook(path):
    with open(path, "r") as f:
        nb = nbf.read(f, as_version=4)

    for cell in nb.cells:
        if cell.cell_type != "code":
            continue

        if "#@title 1. Runtime and configuration" in cell.source:
            cell.source = CELL_1_SOURCE
            print(f"  ✅ Rewrote Cell 1 (config) in {path}")

        if "#@title 8. Run the Entire System" in cell.source:
            cell.source = CELL_8_SOURCE
            print(f"  ✅ Rewrote Cell 8 (startup) in {path}")

    with open(path, "w") as f:
        nbf.write(nb, f)


if __name__ == "__main__":
    notebooks = [
        "notebooks/MedScope_AI_Colab_FullSystem.ipynb",
        "notebooks/MedScope_AI_Colab_Unified.ipynb",
    ]
    for nb_path in notebooks:
        print(f"Updating {nb_path}...")
        try:
            rewrite_notebook(nb_path)
        except Exception as e:
            print(f"  ❌ Failed: {e}")
    print("\nDone.")
