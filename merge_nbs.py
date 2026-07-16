import nbformat as nbf
import json
import subprocess

# Get old training notebook
old_nb_str = subprocess.check_output(['git', 'show', 'HEAD^:notebooks/MedScope_AI_Colab_Training.ipynb']).decode('utf-8')
train_nb = nbf.reads(old_nb_str, as_version=4)

# Get system run notebook
with open("notebooks/MedScope_AI_Colab_System_Run.ipynb", "r") as f:
    run_nb = nbf.read(f, as_version=4)

# We want to keep all the training cells from train_nb
# Then add the running cells from run_nb
# The training notebook already mounts drive, clones repo, installs dependencies (for training).
# We will append the infrastructure and frontend cells.

# Let's just create a new unified notebook carefully.
new_nb = nbf.v4.new_notebook()

# Markdown title
new_nb.cells.append(nbf.v4.new_markdown_cell("# MedScope AI — Unified Training & Inference\n\nThis notebook trains the YOLO and Swin models, saves them, and then boots up the full system (Backend + Frontend) and exposes it via localtunnel."))

# From train_nb, take cells 1 to 9 (which do setup, data download, YOLO train, Swin train, and save to Drive)
new_nb.cells.extend(train_nb.cells[1:10])

# Add a markdown transition
new_nb.cells.append(nbf.v4.new_markdown_cell("## Run the Full System\n\nNow that training is complete and weights are saved, let's boot the system."))

# Add localtunnel install
new_nb.cells.append(nbf.v4.new_code_cell("#@title Install localtunnel\n!npm install -g localtunnel"))

# Add SAM2 download
new_nb.cells.append(nbf.v4.new_code_cell("#@title Download SAM2 Weights\n%cd $PROJECT_DIR\n!wget -q -O sam2_hiera_small.pt https://dl.fbaipublicfiles.com/segment_anything_2/072824/sam2_hiera_small.pt\nprint(\"SAM2 weights downloaded!\")"))

# Add backend dependencies (Redis, Postgres, Qdrant, pip)
new_nb.cells.append(nbf.v4.new_code_cell("#@title Install Backend Dependencies\n!apt-get update -qq\n!apt-get install -y -qq redis-server postgresql libgl1\n!python -m pip install -q -U pip setuptools wheel\n!python -m pip install -q -r backend/requirements.txt\n!python -m pip install -q -r models/requirements.txt\n!python -m pip install -q pytest qdrant-client nest_asyncio pyngrok"))

# Add Infrastructure start
new_nb.cells.append(nbf.v4.new_code_cell("#@title Start Infrastructure (Redis, Postgres, Qdrant)\n!service redis-server start\n!service postgresql start\n\n# Set up PostgreSQL\n!sudo -u postgres psql -c \"CREATE USER medscope WITH PASSWORD 'password';\" || true\n!sudo -u postgres psql -c \"CREATE DATABASE medscope_db OWNER medscope;\" || true\n\n# Set up Qdrant\nimport subprocess, time\nfrom pathlib import Path\n%cd $PROJECT_DIR\nif not Path(\"qdrant\").exists():\n    !wget -q https://github.com/qdrant/qdrant/releases/download/v1.7.0/qdrant-x86_64-unknown-linux-gnu.tar.gz\n    !tar -xzf qdrant-x86_64-unknown-linux-gnu.tar.gz\n\nsubprocess.Popen([\"./qdrant\"])\ntime.sleep(3)\nprint(\"Infrastructure services started.\")"))

# Add Frontend dependencies
new_nb.cells.append(nbf.v4.new_code_cell("#@title Install Frontend Dependencies\n%cd $PROJECT_DIR/frontend\n!npm install"))

# Add System run (Backend + Frontend)
new_nb.cells.append(nbf.v4.new_code_cell("#@title Run the Entire System\n%cd $PROJECT_DIR\nimport os, subprocess, time\nfrom pathlib import Path\n\n# Set environment variables for backend (using the newly trained weights!)\nos.environ['YOLO_WEIGHTS_PATH'] = str(Path(PROJECT_DIR) / \"models/weights/yolov11_malaria_best.pt\")\nos.environ['SWIN_WEIGHTS_PATH'] = str(Path(PROJECT_DIR) / \"models/weights/swin_malaria_best.pth\")\nos.environ['SAM2_WEIGHTS_PATH'] = str(Path(PROJECT_DIR) / \"sam2_hiera_small.pt\")\nos.environ['ALLOWED_ORIGINS'] = \"*\"\n\n# 1. Start Backend\nprint(\"Starting backend...\")\nbackend_process = subprocess.Popen([\"uvicorn\", \"backend.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"])\ntime.sleep(5) # Wait for startup\n\n# Expose backend\nbackend_lt = subprocess.Popen([\"lt\", \"--port\", \"8000\"], stdout=subprocess.PIPE, text=True)\nbackend_url_line = backend_lt.stdout.readline().strip()\nbackend_url = backend_url_line.split(\" \")[-1] if backend_url_line else \"http://localhost:8000\"\nprint(f\"Backend exposed at: {backend_url}\")\n\n# 2. Configure Frontend with Backend URL\nwith open(f\"{PROJECT_DIR}/frontend/.env.local\", \"w\") as f:\n    f.write(f\"NEXT_PUBLIC_API_URL={backend_url}\\n\")\n\n# 3. Start Frontend\nprint(\"Starting frontend...\")\nfrontend_process = subprocess.Popen([\"npm\", \"run\", \"dev\"], cwd=f\"{PROJECT_DIR}/frontend\")\ntime.sleep(5) # Wait for compilation\n\n# Expose frontend\nfrontend_lt = subprocess.Popen([\"lt\", \"--port\", \"3000\"], stdout=subprocess.PIPE, text=True)\nfrontend_url_line = frontend_lt.stdout.readline().strip()\nfrontend_url = frontend_url_line.split(\" \")[-1] if frontend_url_line else \"http://localhost:3000\"\n\nprint(\"\\n\" + \"=\"*60)\nprint(f\"🚀 SYSTEM IS RUNNING!\")\nprint(f\"🌍 Access the Frontend Web App here: {frontend_url}\")\nprint(f\"⚙️ Backend API is at: {backend_url}\")\nprint(\"=\"*60 + \"\\n\")\n\n# Keep the cell running so the servers stay alive\ntry:\n    frontend_process.wait()\nexcept KeyboardInterrupt:\n    print(\"\\nShutting down...\")\n    backend_process.terminate()\n    frontend_process.terminate()\n    backend_lt.terminate()\n    frontend_lt.terminate()"))

nbf.write(new_nb, "notebooks/MedScope_AI_Colab_Unified.ipynb")
