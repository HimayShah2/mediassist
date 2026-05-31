import PyInstaller.__main__
import os
import shutil

def main():
    print("Starting MediAssist Pro Build Process...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    entry_point = os.path.join(project_root, "app_controller.py")
    dist_dir = os.path.join(project_root, "dist")
    build_dir = os.path.join(project_root, "build")
    
    # Clean previous build directories if they exist
    if os.path.exists(dist_dir):
        print(f"Cleaning previous dist directory: {dist_dir}")
        shutil.rmtree(dist_dir)
    if os.path.exists(build_dir):
        print(f"Cleaning previous build directory: {build_dir}")
        shutil.rmtree(build_dir)
        
    print("Running PyInstaller...")
    
    PyInstaller.__main__.run([
        entry_point,
        "--name=MediAssistPro",
        "--onefile",        # Bundle into a single standalone .exe
        "--console",       # Show console to debug startup issues
        "--exclude-module=numpy.array_api", # FIX: Prevents infinite loop in PyInstaller
        "--exclude-module=torch",
        "--exclude-module=transformers",
        "--exclude-module=scipy",
        "--exclude-module=pandas",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        # Bundle required data directories
        f"--add-data={os.path.join(project_root, 'config')}{os.pathsep}config",
        f"--add-data={os.path.join(project_root, 'assets')}{os.pathsep}assets",
        f"--add-data={os.path.join(project_root, 'knowledge_base', 'seed_documents')}{os.pathsep}knowledge_base/seed_documents",
        f"--add-data={os.path.join(project_root, 'models_local')}{os.pathsep}models_local",
        # Hidden imports for PySide6 and ChromaDB
        "--hidden-import=PySide6",
        "--hidden-import=chromadb",
        "--hidden-import=chromadb.telemetry.product.posthog",
        "--hidden-import=chromadb.api.segment",
        "--hidden-import=hnswlib",
        "--hidden-import=pydantic",
        "--hidden-import=uvicorn",
        "--hidden-import=fastapi",
        "--hidden-import=pysqlcipher3",
        "--hidden-import=onnxruntime",
        "--collect-all=chromadb", 
        "--collect-data=chromadb",
        "--collect-binaries=onnxruntime"
    ])
    
    print(f"Build completed successfully. Executable is located in {dist_dir}")

if __name__ == "__main__":
    main()
