import os, sys, ctypes, subprocess, platform

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def elevate():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()

def cmd(command, shell=True, timeout=60):
    try:
        r = subprocess.run(command, shell=shell, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)

def ps(script):
    # powershell one-liner
    return cmd(f'powershell -NoProfile -ExecutionPolicy Bypass -Command "{script}"')

def cpu_info():
    cores = os.cpu_count() or 1
    proc = os.environ.get("PROCESSOR_IDENTIFIER", "")
    return {
        "name": proc,
        "cores": cores,
        "is_intel": "Intel" in proc,
        "is_amd": "AMD" in proc,
    }

def gpu_type():
    code, out, _ = cmd('wmic path win32_videocontroller get name')
    out = out.upper()
    
    if any(x in out for x in ["NVIDIA", "GEFORCE", "RTX", "GTX"]):
        return "nvidia"
    elif any(x in out for x in ["AMD", "RADEON"]):
        return "amd"
    elif any(x in out for x in ["INTEL", "UHD", "IRIS"]):
        return "intel"
    return "unknown"

def ram_kb():
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
    except:
        return 8 * 1024 * 1024  # 8gb fallback

def is_laptop():
    code, out, _ = cmd('wmic path win32_battery get status')
    return "OK" in out or (code == 0 and len(out.strip()) > 10)

def screen_res():
    try:
        u32 = ctypes.windll.user32
        return u32.GetSystemMetrics(0), u32.GetSystemMetrics(1)
    except:
        return 1920, 1080

def win_build():
    try:
        v = platform.version()
        return int(v.split(".")[-1])
    except:
        return 19041

def svc_exists(name):
    code, out, _ = cmd(f'sc query "{name}"')
    return "does not exist" not in out.lower() and code == 0

def svc_running(name):
    _, out, _ = cmd(f'sc query "{name}"')
    return "RUNNING" in out

def svc_start(name):
    code, _, _ = cmd(f'net start "{name}"')
    return code == 0

def svc_stop(name):
    code, _, _ = cmd(f'net stop "{name}"')
    return code == 0

def svc_startup(name, typ="auto"):
    code, _, _ = cmd(f'sc config "{name}" start= {typ}')
    return code == 0

def kill(name):
    code, _, _ = cmd(f'taskkill /f /im "{name}"')
    return code == 0

def power_plan():
    code, out, _ = cmd("powercfg /getactivescheme")
    if code == 0 and "(" in out:
        return out.split("(")[-1].split(")")[0].strip()
    return None

def set_power(guid):
    code, _, _ = cmd(f'powercfg /setactive "{guid}"')
    return code == 0

def netsh(args):
    code, _, _ = cmd(f"netsh {args}")
    return code == 0

def bcdedit(args):
    code, _, _ = cmd(f"bcdedit {args}")
    return code == 0

def mkdir(path):
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except:
        return False

# backwards compat
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
