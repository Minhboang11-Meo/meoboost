"""
Intel iGPU tweaks
"""

from utils import registry, system


def has_intel_gpu():
    """Kiểm tra có Intel GPU không"""
    return system.get_gpu_type() == "intel"


def is_vram_increased():
    """Kiểm tra VRAM đã tăng chưa"""
    val = registry.read_value(r"HKLM\SOFTWARE\Intel\GMM", "DedicatedSegmentSize")
    return val == 1024


def toggle_vram():
    """Tăng/reset VRAM cho Intel iGPU"""
    if is_vram_increased():
        registry.reg_delete(r"HKLM\SOFTWARE\Intel\GMM", "DedicatedSegmentSize")
    else:
        registry.reg_add(r"HKLM\SOFTWARE\Intel\GMM", "DedicatedSegmentSize", 1024, "REG_DWORD")
    return True
