import sys
import threading
import PyInstaller.__main__

def run_pyinstaller():
    # Inside the new thread, we have a 64MB C-stack!
    # Now we can safely increase the Python recursion limit without segfaulting Windows.
    sys.setrecursionlimit(10000)
    try:
        PyInstaller.__main__.run(['--noconfirm', 'mediassist.spec'])
        print("PyInstaller finished successfully!")
    except Exception as e:
        print("PyInstaller failed:", e)

# Set the C-Stack size for new threads to 64MB (default is 1MB on Windows)
threading.stack_size(67108864)

# Create and start the thread
thread = threading.Thread(target=run_pyinstaller)
thread.start()
thread.join()
