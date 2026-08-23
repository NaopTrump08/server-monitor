"""Formatting helpers for metrics display."""

import time


def format_bytes(n):
    """Format byte count into human-readable string."""
    try:
        n = float(n)
    except (TypeError, ValueError):
        return "-"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(n)} {unit}"
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def format_rate(n):
    """Format bytes/sec rate."""
    try:
        n = float(n)
    except (TypeError, ValueError):
        return "-"
    for unit in ("B/s", "KB/s", "MB/s", "GB/s"):
        if n < 1024 or unit == "GB/s":
            if unit == "B/s":
                return f"{int(n)} {unit}"
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} GB/s"


def format_uptime(seconds):
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return "-"
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    if days:
        return f"{days}d {hours}h {mins}m"
    if hours:
        return f"{hours}h {mins}m {secs}s"
    if mins:
        return f"{mins}m {secs}s"
    return f"{secs}s"


def format_time(ts):
    if not ts:
        return "-"
    return time.strftime("%H:%M:%S", time.localtime(ts))
