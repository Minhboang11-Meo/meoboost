"""
Common GPU tweaks (tất cả GPU)
"""

from utils import registry, system
from config import REG_APP


def is_gpu_tweaks_on():
    """Kiểm tra GPU tweaks đã bật chưa"""
    return registry.value_exists(REG_APP, "GpuTweaks")


def toggle_gpu_tweaks():
    """Bật/tắt các tweaks chung cho GPU"""
    if is_gpu_tweaks_on():
        # Tắt
        registry.reg_delete(REG_APP, "GpuTweaks")
        
        # Hardware scheduling về default
        hw = registry.read_value(r"HKLM\System\CurrentControlSet\Control\GraphicsDrivers", "HwSchMode")
        if hw is not None:
            registry.reg_add(r"HKLM\System\CurrentControlSet\Control\GraphicsDrivers", "HwSchMode", 1, "REG_DWORD")
        
        # FSO về default
        registry.reg_delete(r"HKCU\System\GameConfigStore", "GameDVR_Enabled")
        registry.reg_delete(r"HKCU\System\GameConfigStore", "GameDVR_FSEBehaviorMode")
        registry.reg_delete(r"HKCU\System\GameConfigStore", "GameDVR_FSEBehavior")
        registry.reg_delete(r"HKCU\System\GameConfigStore", "GameDVR_HonorUserFSEBehaviorMode")
        registry.reg_delete(r"HKCU\System\GameConfigStore", "GameDVR_DXGIHonorFSEWindowsCompatible")
        
        # GpuEnergyDrv enable
        registry.reg_add(r"HKLM\SYSTEM\CurrentControlSet\Services\GpuEnergyDrv", "Start", 2, "REG_DWORD")
        
        # Preemption enable
        registry.reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Scheduler", "EnablePreemption", 1, "REG_DWORD")
    else:
        # Bật
        registry.reg_add(REG_APP, "GpuTweaks", 1, "REG_DWORD")
        
        # Hardware Accelerated Scheduling
        hw = registry.read_value(r"HKLM\System\CurrentControlSet\Control\GraphicsDrivers", "HwSchMode")
        if hw is not None:
            registry.reg_add(r"HKLM\System\CurrentControlSet\Control\GraphicsDrivers", "HwSchMode", 2, "REG_DWORD")
        
        # GameMode
        registry.reg_add(r"HKCU\Software\Microsoft\GameBar", "AllowAutoGameMode", 1, "REG_DWORD")
        registry.reg_add(r"HKCU\Software\Microsoft\GameBar", "AutoGameModeEnabled", 1, "REG_DWORD")
        
        # Disable FSO
        registry.reg_add(r"HKCU\System\GameConfigStore", "GameDVR_Enabled", 0, "REG_DWORD")
        registry.reg_add(r"HKCU\System\GameConfigStore", "GameDVR_FSEBehaviorMode", 2, "REG_DWORD")
        registry.reg_add(r"HKCU\System\GameConfigStore", "GameDVR_FSEBehavior", 2, "REG_DWORD")
        registry.reg_add(r"HKCU\System\GameConfigStore", "GameDVR_HonorUserFSEBehaviorMode", 1, "REG_DWORD")
        registry.reg_add(r"HKCU\System\GameConfigStore", "GameDVR_DXGIHonorFSEWindowsCompatible", 1, "REG_DWORD")
        registry.reg_add(r"HKCU\System\GameConfigStore", "GameDVR_EFSEFeatureFlags", 0, "REG_DWORD")
        registry.reg_add(r"HKCU\System\GameConfigStore", "GameDVR_DSEBehavior", 2, "REG_DWORD")
        
        # Disable GpuEnergyDrv
        registry.reg_add(r"HKLM\SYSTEM\CurrentControlSet\Services\GpuEnergyDrv", "Start", 4, "REG_DWORD")
        
        # Disable Preemption
        registry.reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Scheduler", "EnablePreemption", 0, "REG_DWORD")
    
    return True
