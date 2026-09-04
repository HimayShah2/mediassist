"""
Model resolution + first-run download so a non-technical user never has to
think about model files.

Resolution order:
  1. $MEDIASSIST_MODEL if it points at a real .gguf
  2. the first *.gguf found in ./models_local/
  3. download the default small model into ./models_local/
"""
import os
import glob
from loguru import logger

# ~0.9 GB, strong instruction-following + JSON for its size.
DEFAULT_REPO = os.getenv("MEDIASSIST_MODEL_REPO", "bartowski/Qwen2.5-1.5B-Instruct-GGUF")
DEFAULT_FILE = os.getenv("MEDIASSIST_MODEL_FILE", "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf")


def _models_dir() -> str:
    d = os.path.join(os.getcwd(), "models_local")
    os.makedirs(d, exist_ok=True)
    return d


def find_local_model() -> str | None:
    env = os.getenv("MEDIASSIST_MODEL")
    if env and os.path.isfile(env):
        return env
    hits = sorted(glob.glob(os.path.join(_models_dir(), "*.gguf")))
    return hits[0] if hits else None


def download_default_model(progress=None) -> str:
    """progress(fraction_0_to_1, human_status) — optional UI callback."""
    from huggingface_hub import hf_hub_download

    target_dir = _models_dir()
    if progress:
        progress(0.0, f"Downloading AI model ({DEFAULT_FILE}, ~0.9 GB). This is a one-time step...")

    # huggingface_hub streams with its own bar; we only get start/end signals here.
    path = hf_hub_download(repo_id=DEFAULT_REPO, filename=DEFAULT_FILE,
                           local_dir=target_dir, local_dir_use_symlinks=False)
    if progress:
        progress(1.0, "AI model ready.")
    logger.info(f"Downloaded default model to {path}")
    return path


def resolve_model_path(progress=None) -> str:
    p = find_local_model()
    if p:
        logger.info(f"Using local model: {p}")
        return p
    logger.warning("No local model found - downloading the default small model.")
    return download_default_model(progress=progress)
