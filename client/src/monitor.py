"""Server data fetching with background thread and history buffering."""

import logging
import threading
import time
from collections import deque

import requests

log = logging.getLogger("monitor")


class ServerStatus:
    """Snapshot of one server's current status."""

    def __init__(self, server_id, name, host):
        self.server_id = server_id
        self.name = name
        self.host = host
        self.online = False
        self.error = None
        self.data = {}
        self.last_update = 0.0
        self.latency_ms = None


class ServerMonitor:
    """Poll servers periodically, keep short history for charts."""

    def __init__(self, config, on_update=None):
        self._config = config
        self._on_update = on_update
        self._lock = threading.Lock()
        self._statuses = {}
        self._history = {}  # server_id -> deque of (timestamp, cpu%, mem%, rx, tx)
        self._history_len = 120  # ~6 minutes at 3s interval
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _loop(self):
        log.info("Monitor thread started")
        while not self._stop.is_set():
            servers = self._config.servers
            # refresh server list statuses
            for i, s in enumerate(servers):
                sid = i
                if sid not in self._statuses:
                    self._statuses[sid] = ServerStatus(sid, s.get("name", s.get("host")), s.get("host"))
                else:
                    self._statuses[sid].name = s.get("name", s.get("host"))
                    self._statuses[sid].host = s.get("host")
            # remove stale
            for sid in list(self._statuses.keys()):
                if sid >= len(servers):
                    del self._statuses[sid]

            for i, s in enumerate(servers):
                self._fetch_one(i, s)

            if self._on_update:
                try:
                    self._on_update(self.snapshot())
                except Exception:
                    pass
            self._stop.wait(self._config.refresh_interval)

    def _fetch_one(self, sid, s):
        host = s.get("host", "")
        port = s.get("port", 8899)
        token = s.get("token", "")
        url = f"http://{host}:{port}/api/stats"
        headers = {"X-Auth-Token": token} if token else {}
        start = time.monotonic()
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            latency = (time.monotonic() - start) * 1000
            if resp.status_code == 200:
                data = resp.json()
                with self._lock:
                    st = self._statuses[sid]
                    st.online = True
                    st.error = None
                    st.data = data
                    st.last_update = time.time()
                    st.latency_ms = round(latency, 1)
                    self._append_history(sid, data)
            else:
                with self._lock:
                    st = self._statuses[sid]
                    st.online = False
                    st.error = f"HTTP {resp.status_code}"
                    st.latency_ms = round(latency, 1)
                log.warning("fetch %s -> HTTP %s", url, resp.status_code)
        except requests.RequestException as e:
            with self._lock:
                st = self._statuses[sid]
                st.online = False
                st.error = str(e.__class__.__name__)
                st.latency_ms = None
            log.warning("fetch %s failed: %s", url, e)

    def _append_history(self, sid, data):
        cpu = data.get("cpu", {}).get("percent", 0)
        mem = data.get("memory", {}).get("percent", 0)
        net = data.get("network", {})
        rx = net.get("rx_rate", 0)
        tx = net.get("tx_rate", 0)
        if sid not in self._history:
            self._history[sid] = deque(maxlen=self._history_len)
        self._history[sid].append((time.time(), cpu, mem, rx, tx))

    def snapshot(self):
        with self._lock:
            result = {}
            for sid, st in self._statuses.items():
                result[sid] = {
                    "name": st.name,
                    "host": st.host,
                    "online": st.online,
                    "error": st.error,
                    "data": st.data,
                    "last_update": st.last_update,
                    "latency_ms": st.latency_ms,
                    "history": list(self._history.get(sid, [])),
                }
            return result

    def get_status(self, sid):
        with self._lock:
            st = self._statuses.get(sid)
            if st is None:
                return None
            return {
                "name": st.name,
                "host": st.host,
                "online": st.online,
                "error": st.error,
                "data": st.data,
                "last_update": st.last_update,
                "latency_ms": st.latency_ms,
                "history": list(self._history.get(sid, [])),
            }
