"""
MeoBoost Benchmark - Uses GpuTest CLI
"""

import subprocess
import os
import time
import re

GPUTEST_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Files", "GpuTest", "GpuTest.exe")

def run_stress_test(duration_sec=60, test="fur"):
    if not os.path.exists(GPUTEST_PATH):
        return {"error": "GpuTest.exe not found", "score": 0}
    
    duration_ms = duration_sec * 1000
    
    try:
        cmd = [
            GPUTEST_PATH,
            f"/test={test}",
            "/width=800",
            "/height=600",
            "/benchmark",
            f"/benchmark_duration_ms={duration_ms}",
            "/no_scorebox"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=duration_sec + 30,
            cwd=os.path.dirname(GPUTEST_PATH)
        )
        
        score = parse_score()
        
        return {
            "test": test,
            "duration": duration_sec,
            "score": score,
            "completed": True
        }
    except subprocess.TimeoutExpired:
        return {"error": "Timeout", "score": 0}
    except Exception as e:
        return {"error": str(e), "score": 0}

def parse_score():
    csv_path = os.path.join(os.path.dirname(GPUTEST_PATH), "_geeks3d_gputest_scores.csv")
    try:
        if os.path.exists(csv_path):
            with open(csv_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    last = lines[-1].strip()
                    parts = last.split(',')
                    if len(parts) >= 4:
                        return int(parts[3])
    except:
        pass
    return 0

def get_last_scores(count=5):
    csv_path = os.path.join(os.path.dirname(GPUTEST_PATH), "_geeks3d_gputest_scores.csv")
    scores = []
    try:
        if os.path.exists(csv_path):
            with open(csv_path, 'r') as f:
                lines = f.readlines()
                for line in lines[-count:]:
                    parts = line.strip().split(',')
                    if len(parts) >= 4:
                        scores.append({
                            "date": parts[0] if parts else "",
                            "test": parts[1] if len(parts) > 1 else "",
                            "resolution": parts[2] if len(parts) > 2 else "",
                            "score": int(parts[3]) if len(parts) > 3 else 0
                        })
    except:
        pass
    return scores
