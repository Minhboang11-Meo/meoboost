"""
Memory tweaks
"""

from utils import registry, system
from config import REG_APP


# === Memory Optimization ===

def is_memory_on():
    """Kiểm tra memory optimization đã bật chưa"""
    return registry.value_exists(REG_APP, "MemoryOn")


def toggle_memory():
    """Bật/tắt memory optimization"""
    if is_memory_on():
        # Tắt
        registry.reg_delete(REG_APP, "MemoryOn")
        
        registry.reg_delete(r"HKLM\Software\Microsoft\FTH", "Enabled")
        registry.reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Search", "BackgroundAppGlobalToggle", 1, "REG_DWORD")
        registry.reg_delete(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "DisablePagingExecutive")
        registry.reg_delete(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "LargeSystemCache")
        
        # Enable Prefetch
        registry.reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters", "EnablePrefetcher", 3, "REG_DWORD")
        registry.reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters", "EnableSuperfetch", 3, "REG_DWORD")
        
        # Default timeouts
        registry.reg_add(r"HKCU\Control Panel\Desktop", "WaitToKillAppTimeout", "20000", "REG_SZ")
        registry.reg_add(r"HKLM\System\CurrentControlSet\Control", "WaitToKillServiceTimeout", "20000", "REG_SZ")
        registry.reg_add(r"HKCU\Control Panel\Desktop", "HungAppTimeout", "5000", "REG_SZ")
        
        # Reset fsutil
        system.run_cmd("fsutil behavior set memoryusage 1")
        system.run_cmd("fsutil behavior set mftzone 1")
        system.run_cmd("fsutil behavior set disablelastaccess 2")
        system.run_cmd("fsutil behavior set disablecompression 0")
    else:
        # Bật
        registry.reg_add(REG_APP, "MemoryOn", 1, "REG_DWORD")
        
        # Disable FTH
        registry.reg_add(r"HKLM\Software\Microsoft\FTH", "Enabled", 0, "REG_DWORD")
        
        # Disable Background apps
        registry.reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications", "GlobalUserDisabled", 1, "REG_DWORD")
        registry.reg_add(r"HKLM\Software\Policies\Microsoft\Windows\AppPrivacy", "LetAppsRunInBackground", 2, "REG_DWORD")
        registry.reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Search", "BackgroundAppGlobalToggle", 0, "REG_DWORD")
        
        # Disable paging for drivers
        registry.reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "DisablePagingExecutive", 1, "REG_DWORD")
        
        # Disable Page Combining
        system.run_powershell("Disable-MMAgent -PageCombining -mc")
        registry.reg_add(r"HKLM\System\CurrentControlSet\Control\Session Manager\Memory Management", "DisablePageCombining", 1, "REG_DWORD")
        
        # Large System Cache
        registry.reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "LargeSystemCache", 1, "REG_DWORD")
        
        # Free unused ram
        registry.reg_add(r"HKLM\System\CurrentControlSet\Control\Session Manager", "HeapDeCommitFreeBlockThreshold", 262144, "REG_DWORD")
        
        # Disable Prefetch/Superfetch
        registry.reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters", "EnablePrefetcher", 0, "REG_DWORD")
        registry.reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters", "EnableSuperfetch", 0, "REG_DWORD")
        
        # Disable Hibernation
        registry.reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power", "HiberbootEnabled", 0, "REG_DWORD")
        registry.reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Power", "HibernateEnabled", 0, "REG_DWORD")
        
        # Fast timeouts
        registry.reg_add(r"HKCU\Control Panel\Desktop", "WaitToKillAppTimeout", "1000", "REG_SZ")
        registry.reg_add(r"HKLM\System\CurrentControlSet\Control", "WaitToKillServiceTimeout", "1000", "REG_SZ")
        registry.reg_add(r"HKCU\Control Panel\Desktop", "HungAppTimeout", "1000", "REG_SZ")
        
        # fsutil settings
        system.run_cmd("fsutil behavior set memoryusage 2")
        system.run_cmd("fsutil behavior set mftzone 2")
        system.run_cmd("fsutil behavior set disablelastaccess 1")
        system.run_cmd("fsutil behavior set disable8dot3 1")
        system.run_cmd("fsutil behavior set disablecompression 1")
        system.run_cmd("fsutil behavior set disabledeletenotify 0")
    
    return True


# === CSRSS Priority ===

def is_csrss_high():
    """Kiểm tra CSRSS có high priority không"""
    val = registry.read_value(
        r"HKLM\Software\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\csrss.exe\PerfOptions",
        "CpuPriorityClass"
    )
    return val == 4


def toggle_csrss():
    """Bật/tắt CSRSS high priority"""
    path = r"HKLM\Software\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\csrss.exe\PerfOptions"
    mm_path = r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
    
    if is_csrss_high():
        registry.reg_delete(path, "CpuPriorityClass")
        registry.reg_delete(path, "IoPriority")
        registry.reg_delete(mm_path, "NoLazyMode")
        registry.reg_delete(mm_path, "AlwaysOn")
        registry.reg_delete(mm_path, "NetworkThrottlingIndex")
        registry.reg_delete(mm_path, "SystemResponsiveness")
    else:
        registry.reg_add(path, "CpuPriorityClass", 4, "REG_DWORD")
        registry.reg_add(path, "IoPriority", 3, "REG_DWORD")
        registry.reg_add(mm_path, "NoLazyMode", 1, "REG_DWORD")
        registry.reg_add(mm_path, "AlwaysOn", 1, "REG_DWORD")
        registry.reg_add(mm_path, "NetworkThrottlingIndex", 10, "REG_DWORD")
        registry.reg_add(mm_path, "SystemResponsiveness", 0, "REG_DWORD")
    
    return True
