import time
import ctypes
import subprocess

_results = {}

def measure_latency():
    try:
        k32 = ctypes.windll.kernel32
        freq = ctypes.c_longlong()
        k32.QueryPerformanceFrequency(ctypes.byref(freq))
        
        start = ctypes.c_longlong()
        end = ctypes.c_longlong()
        
        samples = []
        for _ in range(100):
            k32.QueryPerformanceCounter(ctypes.byref(start))
            time.sleep(0.001)
            k32.QueryPerformanceCounter(ctypes.byref(end))
            delta = (end.value - start.value) / freq.value * 1000
            samples.append(delta - 1.0)
        
        return sum(samples) / len(samples)
    except:
        return -1

def measure_memory():
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
        
        return {
            "total_mb": s.total // (1024 * 1024),
            "avail_mb": s.avail // (1024 * 1024),
            "used_pct": s.load
        }
    except:
        return {"total_mb": 0, "avail_mb": 0, "used_pct": 0}

def measure_dpc():
    try:
        r = subprocess.run(
            ["powershell", "-Command", "(Get-Counter '\\Processor(_Total)\\% DPC Time').CounterSamples.CookedValue"],
            capture_output=True, text=True, timeout=10
        )
        if r.returncode == 0:
            return float(r.stdout.strip())
    except:
        pass
    return -1

def run_benchmark():
    return {
        "latency_ms": round(measure_latency(), 3),
        "memory": measure_memory(),
        "dpc_pct": round(measure_dpc(), 2),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

def save_before():
    global _results
    _results["before"] = run_benchmark()
    return _results["before"]

def save_after():
    global _results
    _results["after"] = run_benchmark()
    return _results["after"]

def get_comparison():
    global _results
    if "before" not in _results or "after" not in _results:
        return None
    
    b = _results["before"]
    a = _results["after"]
    
    lat_diff = b["latency_ms"] - a["latency_ms"]
    mem_diff = a["memory"]["avail_mb"] - b["memory"]["avail_mb"]
    dpc_diff = b["dpc_pct"] - a["dpc_pct"]
    
    return {
        "latency": {"before": b["latency_ms"], "after": a["latency_ms"], "diff": round(lat_diff, 3)},
        "memory_free": {"before": b["memory"]["avail_mb"], "after": a["memory"]["avail_mb"], "diff": mem_diff},
        "dpc": {"before": b["dpc_pct"], "after": a["dpc_pct"], "diff": round(dpc_diff, 2)}
    }

def clear():
    global _results
    _results = {}
