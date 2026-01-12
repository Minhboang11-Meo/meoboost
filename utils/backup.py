"""
Backup và restore utilities
"""

import os
from datetime import datetime

from utils import system
from utils import registry
from config import BACKUP_DIR, DATA_DIR


def create_restore_point(description="MeoBoost Backup"):
    """Tạo restore point Windows"""
    # Cho phép tạo restore point thường xuyên
    registry.reg_add(
        r"HKLM\Software\Microsoft\Windows NT\CurrentVersion\SystemRestore",
        "SystemRestorePointCreationFrequency", 0, "REG_DWORD"
    )
    
    # Enable restore trên các ổ đĩa
    system.run_powershell("Enable-ComputerRestore -Drive 'C:\\'")
    
    # Tạo restore point
    code, _, _ = system.run_cmd(
        f'wmic.exe /namespace:\\\\root\\default Path SystemRestore Call CreateRestorePoint "{description}", 100, 7'
    )
    return code == 0


def backup_registry():
    """Backup HKCU và HKLM registry"""
    date_str = datetime.now().strftime("%Y-%m-%d_%H%M")
    backup_path = os.path.join(BACKUP_DIR, date_str)
    
    system.make_dir(backup_path)
    
    hklm_file = os.path.join(backup_path, "HKLM.reg")
    hkcu_file = os.path.join(backup_path, "HKCU.reg")
    
    ok1 = registry.export_key("HKLM", hklm_file)
    ok2 = registry.export_key("HKCU", hkcu_file)
    
    return ok1 and ok2


def full_backup():
    """Tạo cả restore point và backup registry"""
    system.make_dir(DATA_DIR)
    system.make_dir(BACKUP_DIR)
    
    rp = create_restore_point()
    rb = backup_registry()
    
    return rp or rb


def is_first_run():
    """Kiểm tra lần chạy đầu tiên"""
    marker = os.path.join(DATA_DIR, ".initialized")
    return not os.path.exists(marker)


def mark_initialized():
    """Đánh dấu đã khởi tạo xong"""
    system.make_dir(DATA_DIR)
    marker = os.path.join(DATA_DIR, ".initialized")
    try:
        with open(marker, "w") as f:
            f.write(datetime.now().isoformat())
        return True
    except:
        return False


def get_backup_list():
    """Lấy danh sách các bản backup"""
    if not os.path.exists(BACKUP_DIR):
        return []
    
    backups = []
    for name in os.listdir(BACKUP_DIR):
        path = os.path.join(BACKUP_DIR, name)
        if os.path.isdir(path):
            backups.append(name)
    
    return sorted(backups, reverse=True)


def restore_backup(date_str):
    """Khôi phục từ bản backup"""
    backup_path = os.path.join(BACKUP_DIR, date_str)
    
    hklm_file = os.path.join(backup_path, "HKLM.reg")
    hkcu_file = os.path.join(backup_path, "HKCU.reg")
    
    ok = True
    if os.path.exists(hklm_file):
        ok = ok and registry.import_file(hklm_file)
    if os.path.exists(hkcu_file):
        ok = ok and registry.import_file(hkcu_file)
    
    return ok
