
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
