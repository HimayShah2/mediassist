import zipfile
import httpx
import os
from pathlib import Path

def download_nsis():
    # SourceForge direct download link
    url = "https://managedway.dl.sourceforge.net/project/nsis/NSIS%203/3.08/nsis-3.08.zip"
    nsis_dir = Path("scripts/nsis_portable")
    zip_path = Path("scripts/nsis.zip")
    
    if not (nsis_dir / "makensis.exe").exists():
        print(f"Downloading portable NSIS from SourceForge...")
        try:
            with httpx.Client(follow_redirects=True, timeout=120) as client:
                response = client.get(url)
                response.raise_for_status()
                with open(zip_path, "wb") as f:
                    f.write(response.content)
            
            print("Extracting NSIS...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # NSIS zips usually have a top-level folder like 'nsis-3.08'
                top_folder = zip_ref.namelist()[0].split('/')[0]
                zip_ref.extractall("scripts")
                if os.path.exists(f"scripts/{top_folder}"):
                    if os.path.exists(str(nsis_dir)):
                        import shutil
                        shutil.rmtree(str(nsis_dir))
                    os.rename(f"scripts/{top_folder}", str(nsis_dir))
            
            os.remove(zip_path)
            print("NSIS Portable ready.")
        except Exception as e:
            print(f"Failed to prepare NSIS: {e}")
            return None
    
    return str(nsis_dir / "makensis.exe")

if __name__ == "__main__":
    makensis = download_nsis()
    if makensis:
        import subprocess
        print(f"Compiling installer using {makensis}...")
        result = subprocess.run([makensis, "scripts/installer_script.nsi"], capture_output=True, text=True)
        print(result.stdout)
        if result.return_code != 0:
            print(result.stderr)
        else:
            print("Build Complete! Setup file is in the 'dist' folder.")
