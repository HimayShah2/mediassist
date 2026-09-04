"""PyInstaller runtime hook: make llama-cpp-python's native libraries load in a
frozen build. Runs before any app import."""
import os
import sys
import ctypes


def _setup():
    if not getattr(sys, "frozen", False):
        return
    base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    libdir = os.path.join(base, "llama_cpp", "lib")
    if not os.path.isdir(libdir):
        return

    os.environ["PATH"] = libdir + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("GGML_BACKEND_PATH", libdir)
    try:
        os.add_dll_directory(libdir)
    except Exception:
        pass

    # Preload in dependency order so llama.dll resolves its ggml symbols.
    for name in ("ggml-base.dll", "ggml-cpu.dll", "ggml.dll", "llama.dll", "mtmd.dll"):
        p = os.path.join(libdir, name)
        if os.path.exists(p):
            try:
                ctypes.CDLL(p)
            except Exception:
                pass


_setup()
