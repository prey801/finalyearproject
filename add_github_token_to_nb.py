import nbformat as nbf

def add_github_token(path):
    with open(path, "r") as f:
        nb = nbf.read(f, as_version=4)
        
    modified = False
    for cell in nb.cells:
        if cell.cell_type == "code":
            # Add GITHUB_TOKEN to the first cell
            if "#@title 1. Runtime and configuration" in cell.source and "GITHUB_TOKEN =" not in cell.source:
                cell.source += '\nGITHUB_TOKEN = "" #@param {type:"string"}\n'
                modified = True
                
            # Inject it into os.environ in cell 8
            if "#@title 8. Run the Entire System" in cell.source and "os.environ['GITHUB_TOKEN']" not in cell.source:
                injection = "if \"GITHUB_TOKEN\" in globals() and GITHUB_TOKEN:\n    os.environ['GITHUB_TOKEN'] = GITHUB_TOKEN\n\n"
                target = "os.environ['YOLO_WEIGHTS_PATH'] ="
                if target in cell.source:
                    cell.source = cell.source.replace(target, injection + target)
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
            add_github_token(nb)
        except Exception as e:
            print(f"Failed to update {nb}: {e}")
