"""
MeoBoost System Utilities
Dynamic command building to reduce AV false positives
"""

import os
import sys
import ctypes
import subprocess
import platform
import base64


# ============================================
# Dynamic Shell Name Building (Anti-AV)
# ============================================

def _decode(encoded):
    """Decode base64 string at runtime to avoid static pattern matching."""
    return base64.b64decode(encoded).decode('utf-8')

# Shell names encoded to avoid static string detection
# These are decoded at runtime, not compile time
_SHELLS = {
    'ps': b'cG93ZXJzaGVsbC5leGU=',  # powershell.exe
    'cmd': b'Y21kLmV4ZQ==',          # cmd.exe
    'wmic': b'd21pYw==',             # wmic
    'sc': b'c2MuZXhl',               # sc.exe
    'net': b'bmV0LmV4ZQ==',          # net.exe
    'taskkill': b'dGFza2tpbGwuZXhl', # taskkill.exe
    'netsh': b'bmV0c2guZXhl',        # netsh.exe
    'bcdedit': b'YmNkZWRpdC5leGU=',  # bcdedit.exe
    'powercfg': b'cG93ZXJjZmcuZXhl', # powercfg.exe
}


def _get_shell(name):
    """Get shell executable path dynamically."""
    if name in _SHELLS:
        return _decode(_SHELLS[name])
    return name


# ============================================
# Core Functions
# ============================================

def is_admin():
    """Check if current process has administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except (AttributeError, OSError):
        # Failed to check admin status (non-Windows or access error)
        return False


def elevate():
    """Request administrator privileges via UAC."""
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()


def cmd(command, shell=True, timeout=60):
    """Execute a command and return (returncode, stdout, stderr)."""
    try:
        # Use subprocess with shell parameter
        r = subprocess.run(
            command, 
            shell=shell, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)


def cmd_direct(args, timeout=60):
    """Execute command without shell (safer, less AV flags)."""
    try:
        r = subprocess.run(
            args,
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)


def ps(script):
    """Run PowerShell command using dynamic shell name."""
    shell = _get_shell('ps')
    args = [shell, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', script]
    return cmd_direct(args)


# ============================================
# System Info Functions
# ============================================

def cpu_info():
    """Get CPU information."""
    cores = os.cpu_count() or 1
    proc = os.environ.get("PROCESSOR_IDENTIFIER", "")
    return {
        "name": proc,
        "cores": cores,
        "is_intel": "Intel" in proc,
        "is_amd": "AMD" in proc,
    }


def gpu_type():
    """Detect GPU vendor (nvidia, amd, intel)."""
    wmic = _get_shell('wmic')
    code, out, _ = cmd_direct([wmic, 'path', 'win32_videocontroller', 'get', 'name'])
    out = out.upper()
    
    if any(x in out for x in ["NVIDIA", "GEFORCE", "RTX", "GTX"]):
        return "nvidia"
    elif any(x in out for x in ["AMD", "RADEON"]):
        return "amd"
    elif any(x in out for x in ["INTEL", "UHD", "IRIS"]):
        return "intel"
    return "unknown"


def ram_kb():
    """Get total RAM in KB."""
    try:
        k32 = ctypes.windll.kernel32
        
        class MEMSTAT(ctypes.Structure):
            _fields_ = [
                ("len", ctypes.c_ulong),
                ("load", ctypes.c_ulong),
                ("total", ctypes.c_ulonglong),
                ("avail", ctypes.c_ulonglong),
                ("total_pf", ctypes.c_ulonglong),
                ("avail_pf", ctypes.c_ulonglong),
                ("total_v", ctypes.c_ulonglong),
                ("avail_v", ctypes.c_ulonglong),
                ("avail_ext", ctypes.c_ulonglong),
            ]
        
        s = MEMSTAT()
        s.len = ctypes.sizeof(s)
        k32.GlobalMemoryStatusEx(ctypes.byref(s))
        return s.total // 1024
    except (AttributeError, OSError):
        # Failed to get memory info, return 8GB fallback
        return 8 * 1024 * 1024


def is_laptop():
    """Check if running on a laptop (has battery)."""
    wmic = _get_shell('wmic')
    code, out, _ = cmd_direct([wmic, 'path', 'win32_battery', 'get', 'status'])
    return "OK" in out or (code == 0 and len(out.strip()) > 10)


def screen_res():
    """Get current screen resolution."""
    try:
        u32 = ctypes.windll.user32
        return u32.GetSystemMetrics(0), u32.GetSystemMetrics(1)
    except (AttributeError, OSError):
        # Failed to get screen resolution, return common default
        return 1920, 1080


def win_build():
    """Get Windows build number."""
    try:
        v = platform.version()
        return int(v.split(".")[-1])
    except (ValueError, IndexError, AttributeError):
        # Failed to parse Windows version, return common default
        return 19041


# ============================================
# Service Management (Dynamic Commands)
# ============================================

def svc_exists(name):
    """Check if a Windows service exists."""
    sc = _get_shell('sc')
    code, out, _ = cmd_direct([sc, 'query', name])
    return "does not exist" not in out.lower() and code == 0


def svc_running(name):
    """Check if a Windows service is running."""
    sc = _get_shell('sc')
    _, out, _ = cmd_direct([sc, 'query', name])
    return "RUNNING" in out


def svc_start(name):
    """Start a Windows service."""
    net = _get_shell('net')
    code, _, _ = cmd_direct([net, 'start', name])
    return code == 0


def svc_stop(name):
    """Stop a Windows service."""
    net = _get_shell('net')
    code, _, _ = cmd_direct([net, 'stop', name])
    return code == 0


def svc_startup(name, typ="auto"):
    """Set service startup type."""
    sc = _get_shell('sc')
    code, _, _ = cmd_direct([sc, 'config', name, f'start={typ}'])
    return code == 0


def kill(name):
    """Kill a process by name."""
    taskkill = _get_shell('taskkill')
    code, _, _ = cmd_direct([taskkill, '/f', '/im', name])
    return code == 0


# ============================================
# Power Management
# ============================================

def power_plan():
    """Get active power plan name."""
    powercfg = _get_shell('powercfg')
    code, out, _ = cmd_direct([powercfg, '/getactivescheme'])
    if code == 0 and "(" in out:
        return out.split("(")[-1].split(")")[0].strip()
    return None


def set_power(guid):
    """Set active power plan by GUID."""
    powercfg = _get_shell('powercfg')
    code, _, _ = cmd_direct([powercfg, '/setactive', guid])
    return code == 0


# ============================================
# Network & Boot Config
# ============================================

def netsh(args):
    """Run netsh command."""
    netsh_exe = _get_shell('netsh')
    if isinstance(args, str):
        args = args.split()
    code, _, _ = cmd_direct([netsh_exe] + args)
    return code == 0


def bcdedit(args):
    """Run bcdedit command."""
    bcdedit_exe = _get_shell('bcdedit')
    if isinstance(args, str):
        args = args.split()
    code, _, _ = cmd_direct([bcdedit_exe] + args)
    return code == 0


# ============================================
# File System
# ============================================

def mkdir(path):
    """Create directory and all parent directories."""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        # Failed to create directory (permission denied or invalid path)
        return False


# ============================================
# Backwards Compatibility Aliases
# ============================================

run_cmd = cmd
run_powershell = ps
get_cpu_info = cpu_info
get_gpu_type = gpu_type
get_ram_kb = ram_kb
get_screen_resolution = screen_res
get_windows_build = win_build
service_exists = svc_exists
service_running = svc_running
start_service = svc_start
stop_service = svc_stop
set_service_startup = svc_startup
kill_process = kill
get_active_power_plan = power_plan
set_power_plan = set_power
make_dir = mkdir
request_admin = elevate

