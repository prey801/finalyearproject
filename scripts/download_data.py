import os
import subprocess
import logging
from pathlib import Path
from dotenv import load_dotenv

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from data.config import DataPaths

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()  # Load environment variables (e.g., ROBOFLOW_API_KEY)

def download_nih_malaria():
    """
    Downloads the NIH Malaria dataset from Kaggle.
    Requires kaggle.json to be configured in ~/.kaggle/kaggle.json
    """
    dataset_name = "iarunava/cell-images-for-detecting-malaria"
    target_dir = DataPaths.NIH_MALARIA_RAW
    
    if list(target_dir.glob("*.png")) or (target_dir / "cell_images").exists():
        logging.info("NIH Malaria dataset already seems to exist. Skipping download.")
        return

    logging.info(f"Downloading NIH Malaria dataset to {target_dir}...")
    try:
        # Run kaggle cli command
        subprocess.run([
            "kaggle", "datasets", "download", "-d", dataset_name, 
            "-p", str(target_dir), "--unzip"
        ], check=True)
        logging.info("NIH Malaria dataset downloaded successfully.")
    except FileNotFoundError:
        logging.error("Kaggle CLI not found. Please install kaggle via 'pip install kaggle'")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to download NIH dataset. Ensure kaggle.json is set up. Error: {e}")

def download_roboflow_dataset(workspace, project_name, target_dir):
    """
    Downloads a generic dataset from Roboflow Universe.
    """
    api_key = os.environ.get("ROBOFLOW_API_KEY")
    
    if not api_key:
        logging.error("ROBOFLOW_API_KEY environment variable not set. Skipping Roboflow download.")
        return

    try:
        from roboflow import Roboflow
    except ImportError:
        logging.error("Roboflow library not found. Please install via 'pip install roboflow'")
        return

    if (target_dir / "data.yaml").exists():
        logging.info(f"Dataset {project_name} already exists at {target_dir}. Skipping download.")
        return

    logging.info(f"Downloading {project_name} to {target_dir}...")
    try:
        rf = Roboflow(api_key=api_key)
        project = rf.workspace(workspace).project(project_name)
        version = project.version(1)
        dataset = version.download("yolov11", location=str(target_dir))
        logging.info(f"{project_name} downloaded successfully.")
    except Exception as e:
        logging.error(f"Failed to download {project_name}: {e}")

if __name__ == "__main__":
    download_nih_malaria()
    download_roboflow_dataset("brian-musyoki-s-workspace", "iml-malaria-td7v9", DataPaths.ROBOFLOW_MALARIA_RAW)
    download_roboflow_dataset("joseph-nelson", "bccd", DataPaths.ROBOFLOW_BCCD_RAW)
    download_roboflow_dataset("leukemia", "leukemia-2.0", DataPaths.ROBOFLOW_LEUKEMIA_RAW)
