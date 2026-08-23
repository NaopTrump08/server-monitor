"""Configuration management for server-monitor client.

Stores server list as JSON in the user config directory.
"""

import json
import os
import sys
import threading

APP_NAME = "ServerMonitor"
CONFIG_VERSION = 1


def config_dir():
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        base = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    return os.path.join(base, APP_NAME)


def default_servers():
    return []


class Config:
    def __init__(self, path=None):
        self._lock = threading.RLock()
        self._path = path or os.path.join(config_dir(), "servers.json")
        self._servers = []
        self._refresh_interval = 3
        self.load()

    def load(self):
        with self._lock:
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._servers = data.get("servers", [])
                self._refresh_interval = data.get("refresh_interval", 3)
            except (FileNotFoundError, json.JSONDecodeError):
                self._servers = default_servers()

    def save(self):
        with self._lock:
            try:
                os.makedirs(os.path.dirname(self._path), exist_ok=True)
                data = {
                    "version": CONFIG_VERSION,
                    "refresh_interval": self._refresh_interval,
                    "servers": self._servers,
                }
                with open(self._path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except OSError as e:
                print("Failed to save config:", e)

    @property
    def servers(self):
        with self._lock:
            return list(self._servers)

    @property
    def refresh_interval(self):
        with self._lock:
            return self._refresh_interval

    @refresh_interval.setter
    def refresh_interval(self, value):
        with self._lock:
            self._refresh_interval = max(1, min(60, int(value)))
            self.save()

    def get_server(self, index):
        with self._lock:
            if 0 <= index < len(self._servers):
                return dict(self._servers[index])
        return None

    def add_server(self, server):
        with self._lock:
            if not server.get("name"):
                server["name"] = server.get("host", "Unnamed")
            if not server.get("color"):
                server["color"] = "#2563eb"
            self._servers.append(server)
            self.save()

    def update_server(self, index, server):
        with self._lock:
            if 0 <= index < len(self._servers):
                self._servers[index] = server
                self.save()
                return True
        return False

    def remove_server(self, index):
        with self._lock:
            if 0 <= index < len(self._servers):
                self._servers.pop(index)
                self.save()
                return True
        return False
