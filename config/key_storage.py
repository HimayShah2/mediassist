import os
import json
from loguru import logger

try:
    import keyring
    HAS_KEYRING = True
except ImportError:
    HAS_KEYRING = False

SERVICE_NAME = "MediAssistPro"
ACCOUNT_NAME = "NIM_API_KEYS"

appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
storage_dir = os.path.join(appdata, "MediAssistPro")
os.makedirs(storage_dir, exist_ok=True)
FALLBACK_FILE = os.path.join(storage_dir, "keys.json")

def load_keys() -> list[str]:
    """Loads a dynamic list of API keys from keyring or fallback json."""
    keys_json = None
    if HAS_KEYRING:
        try:
            keys_json = keyring.get_password(SERVICE_NAME, ACCOUNT_NAME)
        except Exception as e:
            logger.warning(f"Keyring read failed: {e}")
            
    if not keys_json and os.path.exists(FALLBACK_FILE):
        try:
            with open(FALLBACK_FILE, "r") as f:
                keys_json = f.read()
        except Exception as e:
            logger.warning(f"Fallback file read failed: {e}")
            
    if keys_json:
        try:
            return json.loads(keys_json)
        except json.JSONDecodeError:
            return []
    return []

def save_keys(keys: list[str]) -> bool:
    """Saves a dynamic list of API keys."""
    keys_json = json.dumps(keys)
    success = False
    
    if HAS_KEYRING:
        try:
            keyring.set_password(SERVICE_NAME, ACCOUNT_NAME, keys_json)
            success = True
        except Exception as e:
            logger.warning(f"Keyring write failed: {e}")
            
    if not success:
        try:
            with open(FALLBACK_FILE, "w") as f:
                f.write(keys_json)
            success = True
        except Exception as e:
            logger.warning(f"Fallback file write failed: {e}")
            
    return success
