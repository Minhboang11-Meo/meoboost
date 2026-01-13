"""
WinUtil-inspired Windows tweaks
Based on ChrisTitusTech's WinUtil
"""

from utils import registry as reg, system as sys


# === Disable Microsoft Copilot ===

def is_copilot_off():
    val = reg.read_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot", "TurnOffWindowsCopilot")
    return val == 1


def toggle_copilot():
    if is_copilot_off():
        # Enable Copilot
        reg.reg_delete(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot", "TurnOffWindowsCopilot")
        reg.reg_delete(r"HKCU\Software\Policies\Microsoft\Windows\WindowsCopilot", "TurnOffWindowsCopilot")
        reg.reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowCopilotButton", 1, "REG_DWORD")
    else:
        # Disable Copilot
        reg.reg_add(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot", "TurnOffWindowsCopilot", 1, "REG_DWORD")
        reg.reg_add(r"HKCU\Software\Policies\Microsoft\Windows\WindowsCopilot", "TurnOffWindowsCopilot", 1, "REG_DWORD")
        reg.reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowCopilotButton", 0, "REG_DWORD")
        reg.reg_add(r"HKLM\SOFTWARE\Microsoft\Windows\Shell\Copilot", "IsCopilotAvailable", 0, "REG_DWORD")
    return True


# === Disable Background Apps ===

def is_bg_apps_off():
    val = reg.read_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications", "GlobalUserDisabled")
    return val == 1


def toggle_bg_apps():
    if is_bg_apps_off():
        reg.reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications", "GlobalUserDisabled", 0, "REG_DWORD")
    else:
        reg.reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications", "GlobalUserDisabled", 1, "REG_DWORD")
    return True


# === Enable End Task with Right-Click ===

def is_end_task_on():
    val = reg.read_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\TaskbarDeveloperSettings", "TaskbarEndTask")
    return val == 1


def toggle_end_task():
    if is_end_task_on():
        reg.reg_delete(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\TaskbarDeveloperSettings", "TaskbarEndTask")
    else:
        reg.reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\TaskbarDeveloperSettings", "TaskbarEndTask", 1, "REG_DWORD")
    return True


# === Classic Right-Click Menu (Windows 11) ===

def is_classic_menu_on():
    val = reg.read_value(r"HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32", "")
    return val == ""


def toggle_classic_menu():
    if is_classic_menu_on():
        # Restore new menu
        sys.run_cmd('reg delete "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" /f')
    else:
        # Enable classic menu
        sys.run_cmd('reg add "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32" /f /ve')
    return True


# === Dark Mode Toggle ===

def is_dark_mode_on():
    val = reg.read_value(r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize", "AppsUseLightTheme")
    return val == 0


def toggle_dark_mode():
    if is_dark_mode_on():
        # Light mode
        reg.reg_add(r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize", "AppsUseLightTheme", 1, "REG_DWORD")
        reg.reg_add(r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize", "SystemUsesLightTheme", 1, "REG_DWORD")
    else:
        # Dark mode
        reg.reg_add(r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize", "AppsUseLightTheme", 0, "REG_DWORD")
        reg.reg_add(r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize", "SystemUsesLightTheme", 0, "REG_DWORD")
    return True


# === Show File Extensions ===

def is_file_ext_on():
    val = reg.read_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "HideFileExt")
    return val == 0


def toggle_file_ext():
    if is_file_ext_on():
        reg.reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "HideFileExt", 1, "REG_DWORD")
    else:
        reg.reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "HideFileExt", 0, "REG_DWORD")
    return True


# === Show Hidden Files ===

def is_hidden_files_on():
    val = reg.read_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "Hidden")
    return val == 1


def toggle_hidden_files():
    if is_hidden_files_on():
        reg.reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "Hidden", 2, "REG_DWORD")
    else:
        reg.reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "Hidden", 1, "REG_DWORD")
    return True


# === Disable Bing Search in Start Menu ===

def is_bing_search_off():
    val = reg.read_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Search", "BingSearchEnabled")
    return val == 0


def toggle_bing_search():
    if is_bing_search_off():
        reg.reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Search", "BingSearchEnabled", 1, "REG_DWORD")
    else:
        reg.reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Search", "BingSearchEnabled", 0, "REG_DWORD")
    return True


# === Disable Wi-Fi Sense ===

def is_wifi_sense_off():
    val = reg.read_value(r"HKLM\SOFTWARE\Microsoft\WcmSvc\wifinetworkmanager\config", "AutoConnectAllowedOEM")
    return val == 0


def toggle_wifi_sense():
    if is_wifi_sense_off():
        reg.reg_delete(r"HKLM\SOFTWARE\Microsoft\WcmSvc\wifinetworkmanager\config", "AutoConnectAllowedOEM")
    else:
        reg.reg_add(r"HKLM\SOFTWARE\Microsoft\WcmSvc\wifinetworkmanager\config", "AutoConnectAllowedOEM", 0, "REG_DWORD")
    return True


# === Disable Storage Sense ===

def is_storage_sense_off():
    val = reg.read_value(r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy", "01")
    return val == 0


def toggle_storage_sense():
    if is_storage_sense_off():
        reg.reg_add(r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy", "01", 1, "REG_DWORD")
    else:
        reg.reg_add(r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy", "01", 0, "REG_DWORD")
    return True


# === Apply All WinUtil Tweaks ===

def apply_all():
    toggle_copilot() if not is_copilot_off() else None
    toggle_bg_apps() if not is_bg_apps_off() else None
    toggle_end_task() if not is_end_task_on() else None
    toggle_bing_search() if not is_bing_search_off() else None
    toggle_storage_sense() if not is_storage_sense_off() else None
    toggle_file_ext() if not is_file_ext_on() else None
    toggle_hidden_files() if not is_hidden_files_on() else None
    return True


# Compat aliases
is_copilot_disabled = is_copilot_off
is_background_apps_disabled = is_bg_apps_off
is_end_task_enabled = is_end_task_on
is_classic_context_menu = is_classic_menu_on
is_dark_mode_enabled = is_dark_mode_on
is_file_extensions_visible = is_file_ext_on
is_hidden_files_visible = is_hidden_files_on
is_bing_search_disabled = is_bing_search_off
is_wifi_sense_disabled = is_wifi_sense_off
is_storage_sense_disabled = is_storage_sense_off
apply_all_winutil = apply_all
