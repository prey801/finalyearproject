import nbformat as nbf
import glob

def add_celery_to_notebook(path):
    with open(path, "r") as f:
        nb = nbf.read(f, as_version=4)
        
    modified = False
    for cell in nb.cells:
        if cell.cell_type == "code":
            # Start Celery worker alongside backend
            uvicorn_line = '"backend_process = subprocess.Popen([\\"uvicorn\\", \\"backend.main:app\\", \\"--host\\", \\"0.0.0.0\\", \\"--port\\", \\"8000\\"])\\n",'
            if uvicorn_line in cell.source and 'celery' not in cell.source:
                celery_code = '\n    "print(\\"Starting Celery worker...\\")\\n",\n    "celery_process = subprocess.Popen([\\"celery\\", \\"-A\\", \\"backend.worker\\", \\"worker\\", \\"--loglevel=info\\"])\\n",'
                cell.source = cell.source.replace(uvicorn_line, uvicorn_line + celery_code)
                modified = True
                
            # Terminate Celery worker on shutdown
            terminate_line = '"    backend_process.terminate()\\n",'
            if terminate_line in cell.source and 'celery_process.terminate()' not in cell.source:
                celery_terminate = '\n    "    celery_process.terminate()\\n",'
                cell.source = cell.source.replace(terminate_line, terminate_line + celery_terminate)
                modified = True

    if modified:
        with open(path, "w") as f:
            nbf.write(nb, f)
        print(f"Updated {path}")

if __name__ == "__main__":
    notebooks = [
        "notebooks/MedScope_AI_Colab_Unified.ipynb",
        "notebooks/MedScope_AI_Colab_FullSystem.ipynb"
    ]
    for nb in notebooks:
        try:
            add_celery_to_notebook(nb)
        except Exception as e:
            print(f"Failed to update {nb}: {e}")
