import sys
sys.setrecursionlimit(5000)
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {
    "packages": ["os", "PySide6", "langchain", "chromadb", "onnxruntime", "loguru", "dotenv", "pydantic"],
    "excludes": ["tkinter", "PyQt5", "PyQt6", "PySide2"],
    "include_files": ["assets/", "models_local/"]
}

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="MediAssist Pro",
    version="2.0.0",
    description="MediAssist Pro embedded LLM",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, target_name="MediAssist.exe")]
)
