from utils import registry as reg, system as sys
from config import REG_APP

def vfx_off():
    v = reg.read(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting")
    return v == 2

def toggle_vfx():
    if vfx_off():
        reg.add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", 0, "REG_DWORD")
    else:
        reg.add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", 2, "REG_DWORD")
        reg.add(r"HKCU\Control Panel\Desktop", "MenuShowDelay", "0", "REG_SZ")
        reg.add(r"HKCU\Control Panel\Desktop\WindowMetrics", "MinAnimate", "0", "REG_SZ")
        reg.add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarAnimations", 0, "REG_DWORD")
        reg.add(r"HKCU\Software\Microsoft\Windows\DWM", "EnableAeroPeek", 0, "REG_DWORD")
        reg.add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "EnableTransparency", 0, "REG_DWORD")
    return True

def gb_off():
    v = reg.read(r"HKCU\System\GameConfigStore", "GameDVR_Enabled")
    return v == 0

def toggle_gb():
    if gb_off():
        reg.add(r"HKCU\System\GameConfigStore", "GameDVR_Enabled", 1, "REG_DWORD")
        reg.rm(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR", "AllowGameDVR")
    else:
        reg.add(r"HKCU\System\GameConfigStore", "GameDVR_Enabled", 0, "REG_DWORD")
        reg.add(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR", "AllowGameDVR", 0, "REG_DWORD")
        reg.add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\GameDVR", "AppCaptureEnabled", 0, "REG_DWORD")
        reg.add(r"HKCU\Software\Microsoft\GameBar", "UseNexusForGameBarEnabled", 0, "REG_DWORD")
        reg.add(r"HKCU\Software\Microsoft\GameBar", "ShowStartupPanel", 0, "REG_DWORD")
        reg.add(r"HKCU\Software\Microsoft\GameBar", "GamePanelStartupTipIndex", 3, "REG_DWORD")
    return True

def def_reduced():
    return reg.exists(REG_APP, "DefenderReduced")

def toggle_def():
    if def_reduced():
        reg.rm(REG_APP, "DefenderReduced")
        reg.rm(r"HKLM\SOFTWARE\Microsoft\Windows Defender\Real-Time Protection", "DisableScanOnRealtimeEnable")
    else:
        reg.add(REG_APP, "DefenderReduced", 1, "REG_DWORD")
        reg.add(r"HKLM\SOFTWARE\Microsoft\Windows Defender\Real-Time Protection", "DisableScanOnRealtimeEnable", 1, "REG_DWORD")
        reg.add(r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Scan", "AvgCPULoadFactor", 10, "REG_DWORD")
        # add common game folders to exclusions
        sys.ps("Add-MpPreference -ExclusionPath 'C:\\Program Files\\Steam' -ErrorAction SilentlyContinue")
        sys.ps("Add-MpPreference -ExclusionPath 'C:\\Program Files (x86)\\Steam' -ErrorAction SilentlyContinue")
        sys.ps("Add-MpPreference -ExclusionPath 'C:\\Games' -ErrorAction SilentlyContinue")
    return True

def ntfs_on():
    return reg.exists(REG_APP, "NtfsTweaked")

def toggle_ntfs():
    if ntfs_on():
        reg.rm(REG_APP, "NtfsTweaked")
        sys.cmd("fsutil behavior set disablelastaccess 2")
    else:
        reg.add(REG_APP, "NtfsTweaked", 1, "REG_DWORD")
        sys.cmd("fsutil behavior set disablelastaccess 1")
        sys.cmd("fsutil behavior set disable8dot3 1")
        sys.cmd("fsutil behavior set encryptpagingfile 0")
        sys.cmd("fsutil behavior set memoryusage 2")
    return True

def svc_on():
    return reg.exists(REG_APP, "ServicesOptimized")

def toggle_svc():
    auto = ["SysMain", "WSearch"]
    demand = ["TabletInputService", "PhoneSvc", "MapsBroker", "lfsvc", "wisvc", "RetailDemo", "MessagingService", "PcaSvc", "DiagTrack", "WMPNetworkSvc", "XblAuthManager", "XblGameSave", "XboxGipSvc", "XboxNetApiSvc"]
    
    if svc_on():
        reg.rm(REG_APP, "ServicesOptimized")
        for s in auto:
            sys.svc_startup(s, "auto")
        for s in demand:
            sys.svc_startup(s, "demand")
    else:
        reg.add(REG_APP, "ServicesOptimized", 1, "REG_DWORD")
        for s in auto + demand:
            sys.svc_startup(s, "disabled")
            sys.svc_stop(s)
    return True

def dx_on():
    return reg.exists(REG_APP, "DxOptimized")

def toggle_dx():
    if dx_on():
        reg.rm(REG_APP, "DxOptimized")
        reg.rm(r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "TdrLevel")
    else:
        reg.add(REG_APP, "DxOptimized", 1, "REG_DWORD")
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "TdrLevel", 0, "REG_DWORD")
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "TdrDelay", 60, "REG_DWORD")
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "DpiMapIommuContiguous", 1, "REG_DWORD")
    return True

def startup_on():
    return reg.exists(REG_APP, "StartupOptimized")

def toggle_startup():
    if startup_on():
        reg.rm(REG_APP, "StartupOptimized")
    else:
        reg.add(REG_APP, "StartupOptimized", 1, "REG_DWORD")
        reg.add(r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", "DelayedDesktopSwitchTimeout", 0, "REG_DWORD")
        reg.add(r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Serialize", "StartupDelayInMSec", 0, "REG_DWORD")
        reg.add(r"HKCU\Control Panel\Desktop", "AutoEndTasks", "1", "REG_SZ")
        reg.add(r"HKCU\Control Panel\Desktop", "WaitToKillAppTimeout", "2000", "REG_SZ")
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Control", "WaitToKillServiceTimeout", "2000", "REG_SZ")
    return True

def prio_on():
    return reg.exists(REG_APP, "PriorityOptimized")

def toggle_prio():
    p = r"HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl"
    if prio_on():
        reg.rm(REG_APP, "PriorityOptimized")
        reg.add(p, "Win32PrioritySeparation", 2, "REG_DWORD")
    else:
        reg.add(REG_APP, "PriorityOptimized", 1, "REG_DWORD")
        reg.add(p, "Win32PrioritySeparation", 38, "REG_DWORD")  # 26 hex
    return True

def irq_on():
    return reg.exists(REG_APP, "IrqOptimized")

def toggle_irq():
    if irq_on():
        reg.rm(REG_APP, "IrqOptimized")
    else:
        reg.add(REG_APP, "IrqOptimized", 1, "REG_DWORD")
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\kernel", "InterruptTimeBias", 1, "REG_DWORD")
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\kernel", "InterruptSteeringDisabled", 0, "REG_DWORD")
    return True

def dpc_on():
    return reg.exists(REG_APP, "DpcOptimized")

def toggle_dpc():
    if dpc_on():
        reg.rm(REG_APP, "DpcOptimized")
        reg.rm(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\kernel", "DpcWatchdogProfileOffset")
    else:
        reg.add(REG_APP, "DpcOptimized", 1, "REG_DWORD")
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\kernel", "DpcWatchdogProfileOffset", 0, "REG_DWORD")
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\kernel", "DpcTimeout", 0, "REG_DWORD")
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\kernel", "IdealDpcRate", 1, "REG_DWORD")
    return True

def mmcss_on():
    return reg.exists(REG_APP, "MmcssOptimized")

def toggle_mmcss():
    p = r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
    if mmcss_on():
        reg.rm(REG_APP, "MmcssOptimized")
        reg.add(p, "SystemResponsiveness", 20, "REG_DWORD")
    else:
        reg.add(REG_APP, "MmcssOptimized", 1, "REG_DWORD")
        reg.add(p, "SystemResponsiveness", 0, "REG_DWORD")
        reg.add(p, "NetworkThrottlingIndex", 0xFFFFFFFF, "REG_DWORD")
        reg.add(p + r"\Tasks\Games", "Scheduling Category", "High", "REG_SZ")
        reg.add(p + r"\Tasks\Games", "SFIO Priority", "High", "REG_SZ")
        reg.add(p + r"\Tasks\Games", "GPU Priority", 8, "REG_DWORD")
        reg.add(p + r"\Tasks\Games", "Priority", 6, "REG_DWORD")
    return True

def wer_off():
    return reg.exists(REG_APP, "WerOff")

def toggle_wer():
    if wer_off():
        reg.rm(REG_APP, "WerOff")
        sys.svc_startup("WerSvc", "demand")
    else:
        reg.add(REG_APP, "WerOff", 1, "REG_DWORD")
        sys.svc_stop("WerSvc")
        sys.svc_startup("WerSvc", "disabled")
        reg.add(r"HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting", "Disabled", 1, "REG_DWORD")
    return True

def nagle_off():
    return reg.exists(REG_APP, "NagleOff")

def toggle_nagle():
    if nagle_off():
        reg.rm(REG_APP, "NagleOff")
    else:
        reg.add(REG_APP, "NagleOff", 1, "REG_DWORD")
        code, out, _ = sys.cmd(r'reg query "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces" /s /v "DefaultGateway"')
        if code == 0:
            cur = ""
            for ln in out.split('\n'):
                if 'HKEY' in ln:
                    cur = ln.strip().replace("HKEY_LOCAL_MACHINE", "HKLM")
                elif 'DefaultGateway' in ln and cur:
                    reg.add(cur, "TcpAckFrequency", 1, "REG_DWORD")
                    reg.add(cur, "TCPNoDelay", 1, "REG_DWORD")
    return True

def throt_off():
    return reg.exists(REG_APP, "ThrottleOff")

def toggle_throt():
    p = r"HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling"
    if throt_off():
        reg.rm(REG_APP, "ThrottleOff")
        reg.rm(p, "PowerThrottlingOff")
    else:
        reg.add(REG_APP, "ThrottleOff", 1, "REG_DWORD")
        reg.add(p, "PowerThrottlingOff", 1, "REG_DWORD")
    return True

def park_off():
    return reg.exists(REG_APP, "ParkingOff")

def toggle_park():
    if park_off():
        reg.rm(REG_APP, "ParkingOff")
    else:
        reg.add(REG_APP, "ParkingOff", 1, "REG_DWORD")
        sys.cmd("powercfg -setacvalueindex scheme_current sub_processor CPMINCORES 100")
        sys.cmd("powercfg -setactive scheme_current")
    return True

def apply_all():
    toggle_vfx()
    toggle_gb()
    toggle_ntfs()
    toggle_svc()
    toggle_dx()
    toggle_startup()
    toggle_prio()
    toggle_irq()
    toggle_dpc()
    toggle_mmcss()
    toggle_wer()
    toggle_nagle()
    toggle_throt()
    toggle_park()
    return True

# compat
is_visual_fx_off = vfx_off
toggle_visual_fx = toggle_vfx
is_gamebar_off = gb_off
toggle_gamebar = toggle_gb
is_defender_reduced = def_reduced
toggle_defender = toggle_def
is_ntfs_tweaked = ntfs_on
is_services_optimized = svc_on
toggle_services = toggle_svc
is_dx_optimized = dx_on
is_startup_optimized = startup_on
is_priority_optimized = prio_on
toggle_priority = toggle_prio
is_irq_optimized = irq_on
is_dpc_optimized = dpc_on
is_mmcss_optimized = mmcss_on
is_wer_off = wer_off
is_nagle_off = nagle_off
is_throttle_off = throt_off
toggle_throttle = toggle_throt
is_parking_off = park_off
toggle_parking = toggle_park
apply_all_fps = apply_all
