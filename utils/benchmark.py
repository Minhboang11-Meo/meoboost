"""
MeoBoost Benchmark - Native CPU/Memory Stress Test
Uses only built-in Python with no external tools
"""

import time
import os
import math
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor


def _cpu_stress_worker(duration_sec):
    """Single-threaded CPU stress using mathematical operations."""
    end_time = time.time() + duration_sec
    operations = 0
    
    while time.time() < end_time:
        # CPU-intensive calculations
        x = 0.0
        for i in range(1000):
            x += math.sin(i) * math.cos(i) * math.tan(i % 89 + 1)
            x += math.sqrt(abs(x) + 1)
            x += math.log(abs(x) + 1)
        operations += 1000
    
    return operations


def _memory_stress_worker(duration_sec, size_mb=100):
    """Memory stress test by allocating and manipulating data."""
    end_time = time.time() + duration_sec
    operations = 0
    
    # Allocate memory block
    block_size = size_mb * 1024 * 1024  # MB to bytes
    
    while time.time() < end_time:
        try:
            # Allocate and fill memory
            data = bytearray(block_size)
            
            # Write pattern
            for i in range(0, len(data), 4096):
                data[i] = (i % 256)
            
            # Read and verify
            checksum = 0
            for i in range(0, len(data), 4096):
                checksum += data[i]
            
            operations += 1
            del data
        except MemoryError:
            break
    
    return operations


def run_stress_test(duration_sec=30, test="cpu"):
    """
    Run CPU or memory stress test.
    
    Args:
        duration_sec: Test duration in seconds
        test: "cpu" or "memory"
    
    Returns:
        dict with score and metrics
    """
    start_time = time.time()
    
    try:
        if test == "cpu":
            # Use all CPU cores
            num_cores = multiprocessing.cpu_count()
            results = []
            
            with ThreadPoolExecutor(max_workers=num_cores) as executor:
                futures = [executor.submit(_cpu_stress_worker, duration_sec) 
                          for _ in range(num_cores)]
                results = [f.result() for f in futures]
            
            total_ops = sum(results)
            ops_per_sec = total_ops / duration_sec
            
            # Calculate score (normalized to ~10000 for a typical CPU)
            score = int(ops_per_sec / 100)
            
            return {
                "test": "cpu",
                "duration": duration_sec,
                "score": score,
                "cores_used": num_cores,
                "total_operations": total_ops,
                "ops_per_second": int(ops_per_sec),
                "completed": True
            }
            
        elif test == "memory":
            # Memory bandwidth test
            size_mb = 50  # Use 50MB blocks
            result = _memory_stress_worker(duration_sec, size_mb)
            
            # Calculate score based on operations
            score = result * 100
            
            return {
                "test": "memory",
                "duration": duration_sec,
                "score": score,
                "block_size_mb": size_mb,
                "iterations": result,
                "completed": True
            }
        else:
            return {"error": f"Unknown test: {test}", "score": 0}
            
    except Exception as e:
        return {"error": str(e), "score": 0}
    finally:
        elapsed = time.time() - start_time


def run_quick_benchmark():
    """Run a quick 10-second CPU benchmark and return score."""
    result = run_stress_test(duration_sec=10, test="cpu")
    return result.get("score", 0)


def get_system_info():
    """Get basic system information for benchmark context."""
    return {
        "cpu_count": multiprocessing.cpu_count(),
        "platform": os.name,
    }


def get_last_scores(count=5):
    """Return empty list - no external score storage."""
    return []
