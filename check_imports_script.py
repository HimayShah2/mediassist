import os
import sys
import importlib.util

def check_imports():
    root = 'c:\\mediassist'
    ignore_dirs = {'.venv', '.pytest_cache', '__pycache__', 'build', 'dist', 'assets', 'logs', 'database'}
    errors = []
    
    for dirpath, _, filenames in os.walk(root):
        if any(ignored in dirpath for ignored in ignore_dirs):
            continue
            
        for file in filenames:
            if file.endswith('.py'):
                path = os.path.join(dirpath, file)
                module_name = os.path.relpath(path, root).replace('.py', '').replace(os.sep, '.')
                if module_name.endswith('.__init__'):
                    module_name = module_name[:-9]
                
                # Try to import
                try:
                    spec = importlib.util.spec_from_file_location(module_name, path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)
                except Exception as e:
                    errors.append(f"Failed to import {path}: {e}")
                    
    for err in errors:
        print(err)

if __name__ == '__main__':
    check_imports()
