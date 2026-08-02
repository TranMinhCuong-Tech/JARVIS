"""
System Monitor - theo doi CPU / RAM / Disk / GPU, KHONG CAN API KEY.
Dung thu vien psutil (va GPUtil neu co GPU NVIDIA).
"""
import psutil

try:
    import GPUtil
except ImportError:
    GPUtil = None


def get_system_stats() -> str:
    """Tra ve mot cau tom tat tinh trang CPU/RAM/Disk (va GPU neu co)."""
    cpu_percent = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    parts = [
        f"CPU usage is at {cpu_percent} percent",
        f"memory usage is at {mem.percent} percent",
        f"disk usage is at {disk.percent} percent",
    ]

    if GPUtil:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                parts.append(
                    f"GPU '{gpu.name}' is at {gpu.load * 100:.0f} percent load "
                    f"and {gpu.temperature}\u00b0C"
                )
        except Exception:
            pass

    return "Sir, " + ", ".join(parts) + "."


def check_high_usage(cpu_threshold: float = 90.0, mem_threshold: float = 90.0):
    """Kiem tra nhanh xem CPU/RAM co dang qua tai khong.
    Tra ve chuoi canh bao neu vuot nguong, hoac None neu binh thuong.
    Ham nay danh cho vong lap giam sat nen (background monitoring)."""
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent

    if cpu >= cpu_threshold:
        return f"Warning sir, CPU usage is critically high at {cpu} percent."
    if mem >= mem_threshold:
        return f"Warning sir, memory usage is critically high at {mem} percent."
    return None
