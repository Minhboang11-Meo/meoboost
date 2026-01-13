import os, sys

APP_NAME = "MeoBoost"
VERSION = "1.0.0"
GITHUB_URL = "github.com/Minhboang11-Meo/meoboost"

# pyinstaller puts stuff in _MEIPASS
if getattr(sys, 'frozen', False):
    SCRIPT_DIR = sys._MEIPASS
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Check for compressed files first, fallback to original Files/
FILES_COMPRESSED_DIR = os.path.join(SCRIPT_DIR, "FilesCompressed")
FILES_DIR = os.path.join(SCRIPT_DIR, "Files")

# If running from EXE with compressed files
if os.path.exists(FILES_COMPRESSED_DIR):
    FILES_COMPRESSED = True
else:
    FILES_COMPRESSED = False

SYSTEM_DRIVE = os.environ.get("SYSTEMDRIVE", "C:")
DATA_DIR = os.path.join(SYSTEM_DRIVE, os.sep, "MeoBoost")
BACKUP_DIR = os.path.join(DATA_DIR, "Backups")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

REG_APP = r"HKCU\Software\MeoBoost"
REG_NVIDIA = r"HKLM\SYSTEM\CurrentControlSet\Services\nvlddmkm"
REG_TCPIP = r"HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
