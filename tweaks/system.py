from utils import registry as reg, system as sys
from config import REG_APP

def miti_off():
    return reg.exists(REG_APP, "MitigationsOff")

def toggle_miti():
    if miti_off():
        reg.rm(REG_APP, "MitigationsOff")
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity", "Enabled", 1, "REG_DWORD")
        reg.rm(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\kernel", "DisableExceptionChainValidation")
        reg.rm(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "FeatureSettings")
        reg.rm(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "FeatureSettingsOverride")
        reg.rm(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "FeatureSettingsOverrideMask")
        reg.rm(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "EnableCfg")
        reg.rm(r"HKLM\System\CurrentControlSet\Control\Session Manager", "ProtectionMode")
    else:
        reg.add(REG_APP, "MitigationsOff", 1, "REG_DWORD")
        # core isolation off
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity", "Enabled", 0, "REG_DWORD")
        # sehop
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\kernel", "DisableExceptionChainValidation", 1, "REG_DWORD")
        # spectre/meltdown
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "FeatureSettings", 1, "REG_DWORD")
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "FeatureSettingsOverride", 3, "REG_DWORD")
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "FeatureSettingsOverrideMask", 3, "REG_DWORD")
        # cfg
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "EnableCfg", 0, "REG_DWORD")
        reg.add(r"HKLM\System\CurrentControlSet\Control\Session Manager", "ProtectionMode", 0, "REG_DWORD")
    return True

def bcd_on():
    return reg.exists(REG_APP, "BcdeditOn")

def toggle_bcd():
    if bcd_on():
        reg.rm(REG_APP, "BcdeditOn")
        sys.bcdedit("/deletevalue tscsyncpolicy")
        sys.bcdedit("/deletevalue bootux")
        sys.bcdedit("/set bootmenupolicy standard")
        sys.bcdedit("/set hypervisorlaunchtype Auto")
        sys.bcdedit("/deletevalue quietboot")
        sys.bcdedit("/set nx optin")
        sys.bcdedit("/set allowedinmemorysettings 0x17000077")
        sys.bcdedit("/deletevalue vsmlaunchtype")
        sys.bcdedit("/deletevalue vm")
        sys.bcdedit("/deletevalue x2apicpolicy")
        sys.bcdedit("/deletevalue configaccesspolicy")
        reg.rm(r"HKLM\Software\Policies\Microsoft\FVE", "DisableExternalDMAUnderLock")
        reg.rm(r"HKLM\Software\Policies\Microsoft\Windows\DeviceGuard", "EnableVirtualizationBasedSecurity")
    else:
        reg.add(REG_APP, "BcdeditOn", 1, "REG_DWORD")
        sys.bcdedit("/set tscsyncpolicy enhanced")
        sys.bcdedit("/set bootux disabled")
        sys.bcdedit("/set bootmenupolicy standard")
        sys.bcdedit("/set quietboot yes")
        
        cpu = sys.cpu_info()
        if cpu["is_intel"]:
            sys.bcdedit("/set nx optout")
        else:
            sys.bcdedit("/set nx alwaysoff")
        
        sys.bcdedit("/set allowedinmemorysettings 0x0")
        sys.bcdedit("/set vsmlaunchtype Off")
        sys.bcdedit("/set vm No")
        reg.add(r"HKLM\Software\Policies\Microsoft\FVE", "DisableExternalDMAUnderLock", 0, "REG_DWORD")
        reg.add(r"HKLM\Software\Policies\Microsoft\Windows\DeviceGuard", "EnableVirtualizationBasedSecurity", 0, "REG_DWORD")
        sys.bcdedit("/set x2apicpolicy Enable")
        sys.bcdedit("/set uselegacyapicmode No")
        sys.bcdedit("/set configaccesspolicy Default")
    return True

def usb_off():
    return reg.exists(REG_APP, "UsbPowerOff")

def toggle_usb():
    if usb_off():
        reg.rm(REG_APP, "UsbPowerOff")
    else:
        reg.add(REG_APP, "UsbPowerOff", 1, "REG_DWORD")
        code, out, _ = sys.cmd('wmic PATH Win32_PnPEntity GET DeviceID')
        if code == 0:
            for line in out.split('\n'):
                line = line.strip()
                if line.startswith("USB\\VID_"):
                    p = rf"HKLM\System\CurrentControlSet\Enum\{line}\Device Parameters"
                    reg.add(p, "EnhancedPowerManagementEnabled", 0, "REG_DWORD")
                    reg.add(p, "AllowIdleIrpInD3", 0, "REG_DWORD")
                    reg.add(p, "EnableSelectiveSuspend", 0, "REG_DWORD")
                    reg.add(p, "DeviceSelectiveSuspended", 0, "REG_DWORD")
                    reg.add(p, "D3ColdSupported", 0, "REG_DWORD")
    return True

def com_off():
    return reg.exists(REG_APP, "ComPortsOff")

def toggle_com():
    if com_off():
        reg.rm(REG_APP, "ComPortsOff")
        sys.cmd('pnputil /enable-device "ACPI\\PNP0501\\1"')
        sys.cmd('pnputil /enable-device "ACPI\\PNP0501\\2"')
    else:
        reg.add(REG_APP, "ComPortsOff", 1, "REG_DWORD")
        sys.cmd('pnputil /disable-device "ACPI\\PNP0501\\1"')
        sys.cmd('pnputil /disable-device "ACPI\\PNP0501\\2"')
    return True

def eisa_off():
    return reg.exists(REG_APP, "EisaPicOff")

def toggle_eisa():
    if eisa_off():
        reg.rm(REG_APP, "EisaPicOff")
        sys.cmd('pnputil /enable-device "ACPI\\PNP0000\\4&d215348&0"')
    else:
        reg.add(REG_APP, "EisaPicOff", 1, "REG_DWORD")
        sys.cmd('pnputil /disable-device "ACPI\\PNP0000\\4&d215348&0"')
    return True

def hpet_off():
    return reg.exists(REG_APP, "HpetOff")

def toggle_hpet():
    if hpet_off():
        reg.rm(REG_APP, "HpetOff")
        sys.bcdedit("/set useplatformclock true")
        sys.cmd('pnputil /enable-device "ACPI\\PNP0103\\0"')
    else:
        reg.add(REG_APP, "HpetOff", 1, "REG_DWORD")
        sys.bcdedit("/set useplatformclock false")
        sys.bcdedit("/deletevalue useplatformtick")
        sys.cmd('pnputil /disable-device "ACPI\\PNP0103\\0"')
    return True

def wav_off():
    return reg.exists(REG_APP, "GsWavetableOff")

def toggle_wav():
    if wav_off():
        reg.rm(REG_APP, "GsWavetableOff")
        reg.add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Drivers32", "midi", "wdmaud.drv", "REG_SZ")
    else:
        reg.add(REG_APP, "GsWavetableOff", 1, "REG_DWORD")
        reg.rm(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Drivers32", "midi")
        reg.add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Drivers32", "midi", "", "REG_SZ")
    return True

def hv_off():
    return reg.exists(REG_APP, "HypervDriverOff")

def toggle_hv():
    if hv_off():
        reg.rm(REG_APP, "HypervDriverOff")
        sys.cmd('sc config hvservice start= auto')
        for s in ["vmickvpexchange", "vmicguestinterface", "vmicshutdown", "vmicheartbeat", "vmicvmsession", "vmictimesync", "vmicvss"]:
            sys.cmd(f'sc config {s} start= demand')
    else:
        reg.add(REG_APP, "HypervDriverOff", 1, "REG_DWORD")
        svcs = ["hvservice", "vmickvpexchange", "vmicguestinterface", "vmicshutdown", "vmicheartbeat", "vmicvmsession", "vmictimesync", "vmicvss"]
        for s in svcs:
            sys.cmd(f'sc stop {s}')
            sys.cmd(f'sc config {s} start= disabled')
    return True

def rdp_off():
    return reg.exists(REG_APP, "RdpRedirectorOff")

def toggle_rdp():
    if rdp_off():
        reg.rm(REG_APP, "RdpRedirectorOff")
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Services\rdpdr", "Start", 3, "REG_DWORD")
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Services\tsusbhub", "Start", 3, "REG_DWORD")
    else:
        reg.add(REG_APP, "RdpRedirectorOff", 1, "REG_DWORD")
        sys.cmd('sc stop rdpdr')
        sys.cmd('sc stop tsusbhub')
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Services\rdpdr", "Start", 4, "REG_DWORD")
        reg.add(r"HKLM\SYSTEM\CurrentControlSet\Services\tsusbhub", "Start", 4, "REG_DWORD")
    return True

# compat
is_mitigations_off = miti_off
toggle_mitigations = toggle_miti
is_bcdedit_on = bcd_on
toggle_bcdedit = toggle_bcd
is_usb_power_off = usb_off
toggle_usb_power = toggle_usb
is_com_ports_off = com_off
toggle_com_ports = toggle_com
is_eisa_pic_off = eisa_off
toggle_eisa_pic = toggle_eisa
is_hpet_off = hpet_off
is_gs_wavetable_off = wav_off
toggle_gs_wavetable = toggle_wav
is_hyperv_driver_off = hv_off
toggle_hyperv_driver = toggle_hv
is_rdp_redirector_off = rdp_off
toggle_rdp_redirector = toggle_rdp
