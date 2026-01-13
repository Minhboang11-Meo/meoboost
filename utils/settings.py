import os, json
from config import DATA_DIR

SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
_cache = None

def _ensure_dir():
    if not os.path.exists(DATA_DIR):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
        except Exception:
            pass  # might fail on some weird setups

def load():
    global _cache
    if _cache is not None:
        return _cache
    
    _ensure_dir()
    
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                _cache = json.load(f)
        except Exception:
            _cache = {}  # corrupted file, just reset
    else:
        _cache = {}
    
    return _cache

def save(data=None):
    global _cache
    _ensure_dir()
    
    if data is not None:
        _cache = data
    if _cache is None:
        _cache = {}
    
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(_cache, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False  # TODO: handle permission issues

def get(key, default=None):
    return load().get(key, default)

def set(key, val):
    data = load()
    data[key] = val
    return save(data)

def get_lang():
    return get("language")

def set_lang(lang):
    return set("language", lang)

def get_tweaks():
    return get("tweaks", {})

def set_tweak(id, on):
    tweaks = get_tweaks()
    tweaks[id] = on
    return set("tweaks", tweaks)

def first_run():
    return not get("initialized", False)

def mark_init():
    return set("initialized", True)

def clear():
    global _cache
    _cache = None

def export_to_file(filepath):
    data = load()
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def import_from_file(filepath):
    global _cache
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        _cache = data
        save(_cache)
        return True
    except Exception:
        return False

def get_all():
    return load().copy()

