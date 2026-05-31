import os
import zipfile
import shutil
from pathlib import Path

def create_payload():
    dist_dir = Path("dist/MediAssistPro")
    payload_zip = Path("scripts/payload.zip")
    
    print(f"Zipping application payload from {dist_dir}...")
    if payload_zip.exists():
        os.remove(payload_zip)
        
    with zipfile.ZipFile(payload_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(dist_dir)
                zipf.write(file_path, arcname)
    
    print(f"Payload created: {payload_zip} ({payload_zip.stat().st_size / 1024 / 1024:.2f} MB)")

def create_stub():
    stub_code = """
import os
import zipfile
import sys
import shutil
from pathlib import Path
import winshell
from win32com.client import Dispatch

def install():
    app_name = "MediAssistPro"
    install_dir = Path(os.environ["LOCALAPPDATA"]) / app_name
    
    print(f"Installing {app_name} to {install_dir}...")
    
    if install_dir.exists():
        shutil.rmtree(install_dir)
    os.makedirs(install_dir, exist_ok=True)
    
    # Get zip path (it will be bundled by PyInstaller)
    if hasattr(sys, '_MEIPASS'):
        zip_path = Path(sys._MEIPASS) / "payload.zip"
    else:
        zip_path = Path("payload.zip")
        
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(install_dir)
        
    # Create Shortcut
    desktop = Path(winshell.desktop())
    path = desktop / f"{app_name}.lnk"
    target = str(install_dir / "MediAssistPro.exe")
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(str(path))
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = str(install_dir)
    shortcut.IconLocation = target
    shortcut.save()
    
    print("Installation Complete!")
    os.system(f'start "" "{target}"')

if __name__ == "__main__":
    try:
        install()
    except Exception as e:
        print(f"Installation failed: {e}")
        input("Press Enter to exit...")
"""
    with open("scripts/installer_stub.py", "w") as f:
        f.write(stub_code)

if __name__ == "__main__":
    create_payload()
    create_stub()
    
    import subprocess
    print("Compiling Setup Executable...")
    # Using --onefile to create a single setup exe
    # Including payload.zip as a data file
    subprocess.run([
        ".venv/Scripts/python.exe", "-m", "PyInstaller",
        "--name=MediAssistPro_Setup",
        "--onefile",
        "--console",
        "--add-data", "scripts/payload.zip;.",
        "scripts/installer_stub.py"
    ])
    print("Build Finished! Find 'MediAssistPro_Setup.exe' in 'dist' folder.")
