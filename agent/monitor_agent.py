#!/usr/bin/env python3
"""Lightweight server monitoring agent.

Exposes system metrics over HTTP/JSON. No third-party dependencies,
reads directly from /proc on Linux. Run with Python 3.6+.

Usage:
    python3 monitor_agent.py [--host 0.0.0.0] [--port 8899] [--token SECRET]
"""

import argparse
import json
import os
import platform
import signal
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    import psutil  # optional, falls back to /proc if unavailable
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def read_proc(path, default=None):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except Exception:
        return default


def read_proc_lines(path):
    try:
        with open(path, "r") as f:
            return f.readlines()
    except Exception:
        return []


def cpu_percent_since(sample):
    """Return CPU usage percent relative to a previous /proc/stat sample."""
    lines = read_proc_lines("/proc/stat")
    if not lines:
        return 0.0
    parts = lines[0].split()
    if not parts or parts[0] != "cpu":
        return 0.0
    fields = [int(x) for x in parts[1:9]]
    idle = fields[3] + (fields[4] if len(fields) > 4 else 0)
    total = sum(fields)
    delta_total = total - sample["total"]
    delta_idle = idle - sample["idle"]
    if delta_total <= 0:
        return 0.0
    return round(100.0 * (delta_total - delta_idle) / delta_total, 1)


def cpu_sample():
    lines = read_proc_lines("/proc/stat")
    if not lines:
        return {"idle": 0, "total": 0}
    parts = lines[0].split()
    fields = [int(x) for x in parts[1:9]]
    idle = fields[3] + (fields[4] if len(fields) > 4 else 0)
    return {"idle": idle, "total": sum(fields)}


def get_mem_info():
    if HAS_PSUTIL:
        vm = psutil.virtual_memory()
        return {
            "total": vm.total,
            "used": vm.used,
            "free": vm.available,
            "percent": round(vm.percent, 1),
        }
    mem_total = 0
    mem_available = 0
    for line in read_proc_lines("/proc/meminfo"):
        if line.startswith("MemTotal:"):
            mem_total = int(line.split()[1]) * 1024
        elif line.startswith("MemAvailable:"):
            mem_available = int(line.split()[1]) * 1024
    used = mem_total - mem_available
    percent = round(100.0 * used / mem_total, 1) if mem_total else 0
    return {"total": mem_total, "used": used, "free": mem_available, "percent": percent}


def get_disk_info():
    if HAS_PSUTIL:
        result = []
        for p in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(p.mountpoint)
                result.append(
                    {
                        "mount": p.mountpoint,
                        "device": p.device,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": round(usage.percent, 1),
                    }
                )
            except Exception:
                continue
        return result
    result = []
    for line in read_proc_lines("/proc/mounts"):
        parts = line.split()
        if len(parts) < 3:
            continue
        dev, mnt, fstype = parts[0], parts[1], parts[2]
        if fstype in ("proc", "sysfs", "devtmpfs", "devpts", "tmpfs", "cgroup", "overlay", "cgroup2"):
            continue
        if not dev.startswith("/dev/"):
            continue
        try:
            st = os.statvfs(mnt)
            total = st.f_blocks * st.f_frsize
            free = st.f_bavail * st.f_frsize
            used = (st.f_blocks - st.f_bfree) * st.f_frsize
            percent = round(100.0 * used / total, 1) if total else 0
            result.append(
                {"mount": mnt, "device": dev, "total": total, "used": used, "free": free, "percent": percent}
            )
        except Exception:
            continue
    return result


def get_net_info():
    if HAS_PSUTIL:
        counters = psutil.net_io_counters()
        return {
            "bytes_sent": counters.bytes_sent,
            "bytes_recv": counters.bytes_recv,
            "packets_sent": counters.packets_sent,
            "packets_recv": counters.packets_recv,
        }
    sent = recv = 0
    for line in read_proc_lines("/proc/net/dev"):
        if ":" not in line:
            continue
        iface, rest = line.split(":", 1)
        if iface.strip() == "lo":
            continue
        fields = rest.split()
        if len(fields) >= 9:
            try:
                recv += int(fields[0])
                sent += int(fields[8])
            except ValueError:
                pass
    return {"bytes_sent": sent, "bytes_recv": recv, "packets_sent": 0, "packets_recv": 0}


def get_load_avg():
    line = read_proc_lines("/proc/loadavg")
    if not line:
        return [0.0, 0.0, 0.0]
    parts = line[0].split()
    try:
        return [float(x) for x in parts[:3]]
    except ValueError:
        return [0.0, 0.0, 0.0]


def get_uptime():
    line = read_proc("/proc/uptime")
    if not line:
        return 0.0
    try:
        return float(line.split()[0])
    except (ValueError, IndexError):
        return 0.0


def get_tcp_connections():
    count = 0
    for line in read_proc_lines("/proc/net/tcp"):
        if line.startswith("sl"):
            continue
        count += 1
    return count


def get_process_count():
    try:
        return len(os.listdir("/proc"))
    except OSError:
        return 0


class Monitor:
    def __init__(self):
        self._lock = threading.Lock()
        self._prev_cpu = cpu_sample()
        self._prev_net = get_net_info()
        self._prev_net_time = time.monotonic()
        self.boot_time = self._get_boot_time()

    def _get_boot_time(self):
        if HAS_PSUTIL:
            try:
                return int(psutil.boot_time())
            except Exception:
                pass
        try:
            with open("/proc/stat") as f:
                for line in f:
                    if line.startswith("btime"):
                        return int(line.split()[1])
        except Exception:
            pass
        return int(time.time()) - int(get_uptime())

    def collect(self):
        with self._lock:
            now = time.monotonic()
            cpu = cpu_percent_since(self._prev_cpu)
            self._prev_cpu = cpu_sample()

            net = get_net_info()
            delta_time = now - self._prev_net_time
            if delta_time > 0:
                rx_rate = max(0, net["bytes_recv"] - self._prev_net["bytes_recv"]) / delta_time
                tx_rate = max(0, net["bytes_sent"] - self._prev_net["bytes_sent"]) / delta_time
            else:
                rx_rate = tx_rate = 0
            self._prev_net = net
            self._prev_net_time = now

        mem = get_mem_info()
        return {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "kernel": platform.release(),
            "arch": platform.machine(),
            "python": platform.python_version(),
            "cpu": {
                "cores": os.cpu_count() or 1,
                "percent": cpu,
                "load1": get_load_avg()[0],
                "load5": get_load_avg()[1],
                "load15": get_load_avg()[2],
            },
            "memory": mem,
            "disk": get_disk_info(),
            "network": {
                "bytes_sent": net["bytes_sent"],
                "bytes_recv": net["bytes_recv"],
                "rx_rate": round(rx_rate, 1),
                "tx_rate": round(tx_rate, 1),
            },
            "system": {
                "uptime": get_uptime(),
                "processes": get_process_count(),
                "tcp_connections": get_tcp_connections(),
            },
            "timestamp": time.time(),
            "boot_time": self.boot_time,
            "agent_version": "1.0.0",
        }


class Handler(BaseHTTPRequestHandler):
    monitor = None
    token = None

    def _auth_ok(self):
        if not self.token:
            return True
        return self.headers.get("X-Auth-Token") == self.token

    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.rstrip("/") == "/api/stats" or self.path.rstrip("/") == "/":
            if not self._auth_ok():
                self._send_json({"error": "Unauthorized"}, 401)
                return
            self._send_json(self.monitor.collect())
        elif self.path == "/health":
            self._send_json({"status": "ok"})
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Auth-Token")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))


def main():
    parser = argparse.ArgumentParser(description="Server monitor agent")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8899)
    parser.add_argument("--token", default="")
    args = parser.parse_args()

    Monitor_inst = Monitor()
    Handler.monitor = Monitor_inst
    Handler.token = args.token

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.daemon_threads = True

    def shutdown_handler(signum, frame):
        print("\nShutting down...")
        server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    print("Monitor agent listening on %s:%s" % (args.host, args.port))
    if args.token:
        print("Auth token enabled")
    print("CPU: %s cores | Python %s" % (os.cpu_count(), platform.python_version()))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
