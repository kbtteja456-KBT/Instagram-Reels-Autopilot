"""System resource monitoring and safeguard to prevent crashes during FFmpeg rendering."""

import shutil
import psutil
from typing import Dict, Any, Tuple, List
from backend.app.core.logging import logger


class ResourceGuard:
    """Monitors system resources (CPU, RAM, Disk) to ensure safe rendering."""

    MIN_FREE_DISK_GB = 2.0
    MAX_CPU_PERCENT = 92.0
    MAX_RAM_PERCENT = 90.0

    @classmethod
    def get_system_metrics(cls) -> Dict[str, Any]:
        disk = shutil.disk_usage(".")
        free_disk_gb = disk.free / (1024 ** 3)
        total_disk_gb = disk.total / (1024 ** 3)
        ram = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)

        return {
            "cpu_percent": cpu,
            "ram_percent": ram.percent,
            "ram_free_gb": round(ram.available / (1024 ** 3), 2),
            "disk_free_gb": round(free_disk_gb, 2),
            "disk_total_gb": round(total_disk_gb, 2),
        }

    @classmethod
    def verify_safe_to_render(cls) -> Tuple[bool, List[str]]:
        metrics = cls.get_system_metrics()
        warnings = []

        if metrics["disk_free_gb"] < cls.MIN_FREE_DISK_GB:
            warnings.append(f"Low disk space: {metrics['disk_free_gb']} GB remaining (min {cls.MIN_FREE_DISK_GB} GB)")

        if metrics["ram_percent"] > cls.MAX_RAM_PERCENT:
            warnings.append(f"High RAM usage: {metrics['ram_percent']}% (max {cls.MAX_RAM_PERCENT}%)")

        if metrics["cpu_percent"] > cls.MAX_CPU_PERCENT:
            warnings.append(f"High CPU usage: {metrics['cpu_percent']}% (max {cls.MAX_CPU_PERCENT}%)")

        is_safe = len(warnings) == 0
        return is_safe, warnings


resource_guard = ResourceGuard()
