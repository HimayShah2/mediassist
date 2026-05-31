import time
import os
from pathlib import Path
from PySide6.QtCore import QThread, Signal

class DocumentProcessor(QThread):
    """
    QThread that processes documents from a queue in the background.
    """
    progress_updated = Signal(str, int)
    processing_finished = Signal(str, bool, str)

    def __init__(self, file_queue, parent=None):
        super().__init__(parent)
        self.file_queue = file_queue
        self._is_running = True

    def run(self):
        while self._is_running:
            if not self.file_queue.empty():
                file_path = self.file_queue.get()
                self._process_file(file_path)
            else:
                time.sleep(0.1)  # Sleep briefly to avoid high CPU usage

    def _process_file(self, file_path):
        filename = os.path.basename(file_path)
        try:
            # Simulate a multi-step ingestion process (e.g. OCR, parsing, database storage)
            for i in range(1, 101, 10):
                if not self._is_running:
                    break
                self.progress_updated.emit(filename, i)
                time.sleep(0.3)  # Simulated delay
            
            if self._is_running:
                self.progress_updated.emit(filename, 100)
                self.processing_finished.emit(filename, True, "Successfully ingested")
        except Exception as e:
            self.processing_finished.emit(filename, False, str(e))

    def stop(self):
        self._is_running = False
        self.wait()


class AutoIngestDaemon(QThread):
    """
    QThread that monitors a directory for new PDFs and emits a signal when one is found.
    """
    new_file_detected = Signal(str)

    def __init__(self, watch_dir, parent=None):
        super().__init__(parent)
        self.watch_dir = Path(watch_dir)
        self._is_running = True
        self._processed_files = set()

    def run(self):
        if not self.watch_dir.exists():
            try:
                self.watch_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass

        while self._is_running:
            if self.watch_dir.exists():
                for filepath in self.watch_dir.glob("*.pdf"):
                    filepath_str = str(filepath)
                    if filepath_str not in self._processed_files:
                        self._processed_files.add(filepath_str)
                        self.new_file_detected.emit(filepath_str)
            time.sleep(2)  # Poll every 2 seconds

    def stop(self):
        self._is_running = False
        self.wait()
