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

def run_fps_benchmark(duration=10):
    try:
        import ctypes
        from ctypes import wintypes
        
        gdi32 = ctypes.windll.gdi32
        user32 = ctypes.windll.user32
        
        hdc = user32.GetDC(0)
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        
        frames = 0
        start = time.time()
        
        while time.time() - start < duration:
            for i in range(10):
                x = (frames * 7) % width
                y = (frames * 11) % height
                color = (frames * 13) % 0xFFFFFF
                
                gdi32.SetPixel(hdc, x, y, color)
                gdi32.Rectangle(hdc, x, y, x + 50, y + 50)
            
            frames += 1
        
        user32.ReleaseDC(0, hdc)
        
        elapsed = time.time() - start
        fps = frames / elapsed
        
        return {
            "fps": round(fps, 1),
            "frames": frames,
            "duration": round(elapsed, 2),
            "score": int(fps * 10)
        }
    except Exception as e:
        return {"fps": 0, "frames": 0, "duration": 0, "score": 0, "error": str(e)}

def run_stress_test(duration=30):
    try:
        import threading
        import math
        
        results = {"cpu_ops": 0, "completed": False}
        stop_flag = [False]
        
        def cpu_work():
            ops = 0
            while not stop_flag[0]:
                for i in range(1000):
                    _ = math.sqrt(i * 3.14159) * math.sin(i)
                ops += 1000
            results["cpu_ops"] = ops
        
        threads = []
        import os
        cores = os.cpu_count() or 4
        
        for _ in range(cores):
            t = threading.Thread(target=cpu_work)
            t.start()
            threads.append(t)
        
        time.sleep(duration)
        stop_flag[0] = True
        
        for t in threads:
            t.join()
        
        results["completed"] = True
        results["score"] = results["cpu_ops"] // 1000
        return results
    except Exception as e:
        return {"cpu_ops": 0, "completed": False, "error": str(e)}

def clear():
    global _results
    _results = {}
