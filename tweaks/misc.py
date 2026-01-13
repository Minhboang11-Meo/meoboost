"""
MeoBoost Miscellaneous Tools
"""

import os
import shutil
from utils import registry, system, files
from config import FILES_DIR


def clear_memory_native():
    """Clear memory using native PowerShell commands (no external tools)."""
    # Force garbage collection and working set trimming via PowerShell
    ps_script = """
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
    Get-Process | ForEach-Object {
        try { $_.MinWorkingSet = 1 } catch {}
    }
    """
    system.run_cmd(f'powershell -NoProfile -Command "{ps_script}"')


def run_cleaner():
    """Clean temporary files and free memory."""
    temp_dir = os.environ.get("TEMP", "")
    windir = os.environ.get("SYSTEMROOT", r"C:\Windows")
    
    # Clear recycle bin
    system.run_cmd("rd /s /q %SYSTEMDRIVE%\\$Recycle.bin", shell=True)
    
    # Clear user temp
    if temp_dir and os.path.exists(temp_dir):
        for item in os.listdir(temp_dir):
            try:
                path = os.path.join(temp_dir, item)
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
            except (OSError, PermissionError):
                # Skip files in use or permission denied
                pass
    
    # Clear Windows temp
    win_temp = os.path.join(windir, "Temp")
    if os.path.exists(win_temp):
        for item in os.listdir(win_temp):
            try:
                os.remove(os.path.join(win_temp, item))
            except (OSError, PermissionError):
                # Skip files in use or permission denied
                pass
    
    # Clear prefetch
    prefetch = os.path.join(windir, "Prefetch")
    if os.path.exists(prefetch):
        for item in os.listdir(prefetch):
            try:
                os.remove(os.path.join(prefetch, item))
            except (OSError, PermissionError):
                # Skip files in use or permission denied
                pass
    
    # Clear memory using native PowerShell (replaces EmptyStandbyList.exe)
    clear_memory_native()
    
    return True


def game_boost(exe_path):
    """Optimize Windows for a specific game executable."""
    if not os.path.exists(exe_path):
        return False
    
    exe_name = os.path.basename(exe_path)
    
    # Set GPU preference to high performance
    registry.reg_add(
        r"HKCU\Software\Microsoft\DirectX\UserGpuPreferences",
        exe_path, "GpuPreference=2;", "REG_SZ"
    )
    
    # Disable fullscreen optimizations
    registry.reg_add(
        r"HKCU\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers",
        exe_path, "~ DISABLEDXMAXIMIZEDWINDOWEDMODE", "REG_SZ"
    )
    
    # Set high CPU priority
    path = rf"HKLM\Software\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\{exe_name}\PerfOptions"
    registry.reg_add(path, "CpuPriorityClass", 3, "REG_DWORD")
    
    return True


def soft_restart():
    """Soft restart Windows components (explorer, network, memory)."""
    # Restart explorer
    system.kill_process("explorer.exe")
    windir = os.environ.get("SYSTEMROOT", r"C:\Windows")
    os.startfile(os.path.join(windir, "explorer.exe"))
    
    # Reset network
    system.run_cmd("netsh advfirewall reset")
    system.run_cmd("ipconfig /release")
    system.run_cmd("ipconfig /renew")
    system.run_cmd("nbtstat -R")
    system.run_cmd("nbtstat -RR")
    system.run_cmd("ipconfig /flushdns")
    system.run_cmd("ipconfig /registerdns")
    
    # Clear memory using native PowerShell
    clear_memory_native()
    
    return True


def is_audio_latency_on():
    """Check if MeoBoost audio latency task is enabled."""
    # Check if scheduled task exists and is enabled
    code, out, _ = system.run_cmd('schtasks /query /tn "MeoBoostAudioLatency" 2>nul')
    return code == 0 and "Ready" in out


def toggle_audio_latency():
    """Toggle audio latency optimization using Windows Scheduled Task."""
    real = files.get_file("REAL.exe")
    
    if not real:
        return False
    
    task_name = "MeoBoostAudioLatency"
    
    if is_audio_latency_on():
        # Disable: Delete scheduled task and stop process
        system.run_cmd(f'schtasks /delete /tn "{task_name}" /f')
        system.kill_process("REAL.exe")
    else:
        # Enable: Create scheduled task to run at logon with high priority
        # First, ensure any old task is removed
        system.run_cmd(f'schtasks /delete /tn "{task_name}" /f 2>nul')
        
        # Create new task that runs at logon
        create_cmd = (
            f'schtasks /create /tn "{task_name}" '
            f'/tr "{real}" '
            f'/sc onlogon '
            f'/rl highest '
            f'/f'
        )
        system.run_cmd(create_cmd)
        
        # Start it now
        system.run_cmd(f'schtasks /run /tn "{task_name}"')
    
    return True


def set_w32_priority(value):
    """Set Win32 priority separation value."""
    return registry.reg_add(
        r"HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl",
        "Win32PrioritySeparation", value, "REG_DWORD"
    )

