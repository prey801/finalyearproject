import nbformat as nbf
import glob

def fix_nb(path):
    with open(path, "r") as f:
        nb = nbf.read(f, as_version=4)
        
    for cell in nb.cells:
        if cell.cell_type == "code" and "#@title 1. Runtime and configuration" in cell.source:
            if "SUPABASE_URL" not in cell.source:
                cell.source += "\nSUPABASE_URL = \"\" #@param {type:\"string\"}\n"
                cell.source += "SUPABASE_ANON_KEY = \"\" #@param {type:\"string\"}\n"
                
        if cell.cell_type == "code" and "with open(f\"{PROJECT_DIR}/frontend/.env.local\", \"w\") as f:" in cell.source:
            # We replace "w" with "a" but wait, .env.local doesn't exist after git clone. 
            # We need to write everything.
            old_code = "with open(f\"{PROJECT_DIR}/frontend/.env.local\", \"w\") as f:\n    f.write(f\"NEXT_PUBLIC_API_URL={backend_url}\\n\")"
            new_code = """with open(f"{PROJECT_DIR}/frontend/.env.local", "w") as f:
    f.write(f"NEXT_PUBLIC_API_URL={backend_url}\\n")
    if "SUPABASE_URL" in globals() and SUPABASE_URL:
        f.write(f"NEXT_PUBLIC_SUPABASE_URL={SUPABASE_URL}\\n")
        f.write(f"NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY={SUPABASE_ANON_KEY}\\n")
        f.write(f"NEXT_PUBLIC_SUPABASE_ANON_KEY={SUPABASE_ANON_KEY}\\n")"""
            if old_code in cell.source:
                cell.source = cell.source.replace(old_code, new_code)
                
    with open(path, "w") as f:
        nbf.write(nb, f)

fix_nb("notebooks/MedScope_AI_Colab_FullSystem.ipynb")

if __name__ == "__main__":
    try:
        fix_nb("notebooks/MedScope_AI_Colab_Unified.ipynb")
    except:
        pass
