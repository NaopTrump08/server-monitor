"""Alerts centre — threshold alerting engine and the alerts page.

The manager evaluates the monitor snapshot every tick: a metric crossing its
threshold raises an alert, dropping back below resolves it. Events (with
resolve time) are kept in memory and persisted as JSON in the config dir.
"""

import json
import os
import threading
import time
from collections import deque

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .glass import GlassFrame

RULES = {
    "cpu": ("CPU 使用率", 80),
    "mem": ("内存使用率", 85),
    "disk": ("磁盘使用率", 90),
}
RULE_LABEL = {
    "cpu": "CPU",
    "mem": "内存",
    "disk": "磁盘",
    "offline": "离线",
}


class AlertManager:
    def __init__(self, path=None):
        self._path = path
        self._lock = threading.Lock()
        self._events = deque(maxlen=300)
        self._active = {}
        self._load()

    # ------------------------------------------------------------- persistence
    def _load(self):
        try:
            if self._path and os.path.exists(self._path):
                with open(self._path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._events = deque(data.get("events", [])[-300:], maxlen=300)
                self._active = data.get("active", {})
        except (OSError, ValueError):
            pass

    def _save(self):
        if not self._path:
            return
        try:
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump({"events": list(self._events), "active": self._active},
                          f, ensure_ascii=False, indent=1)
        except OSError:
            pass

    # -------------------------------------------------------------- evaluation
    def evaluate(self, snapshot):
        now = time.time()
        changed = False
        with self._lock:
            for sid, s in snapshot.items():
                name = s.get("name") or s.get("host") or f"服务器 {sid + 1}"
                online = bool(s.get("online"))
                d = s.get("data") or {}

                values = {
                    "cpu": d.get("cpu", {}).get("percent", 0),
                    "mem": d.get("memory", {}).get("percent", 0),
                    "disk": max((x.get("percent", 0) for x in (d.get("disk") or [])), default=0),
                }
                for rule, (label, threshold) in RULES.items():
                    val = values[rule]
                    key = f"{sid}:{rule}"
                    if val >= threshold:
                        if key not in self._active:
                            ev = {
                                "time": now,
                                "server": name,
                                "rule": rule,
                                "value": round(val, 1),
                                "level": "error" if val >= threshold + 10 else "warning",
                                "status": "active",
                                "resolved": None,
                                "message": f"{label} {val:.0f}%（阈值 {threshold}%）",
                            }
                            self._active[key] = ev
                            self._events.appendleft(ev)
                            changed = True
                        else:
                            self._active[key]["value"] = round(val, 1)
                            changed = True
                    else:
                        ev = self._active.pop(key, None)
                        if ev is not None:
                            ev["status"] = "resolved"
                            ev["resolved"] = now
                            changed = True

                key = f"{sid}:offline"
                if not online:
                    if key not in self._active:
                        ev = {
                            "time": now,
                            "server": name,
                            "rule": "offline",
                            "value": None,
                            "level": "error",
                            "status": "active",
                            "resolved": None,
                            "message": "服务器离线（无法连接）",
                        }
                        self._active[key] = ev
                        self._events.appendleft(ev)
                        changed = True
                else:
                    ev = self._active.pop(key, None)
                    if ev is not None:
                        ev["status"] = "resolved"
                        ev["resolved"] = now
                        changed = True

            if changed:
                self._save()
            return list(self._events), len(self._active)

    def active_count(self):
        with self._lock:
            return len(self._active)


class AlertRow(GlassFrame):
    def __init__(self, ev, parent=None):
        super().__init__(parent, radius=18)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(12)

        # level badge
        level = ev.get("level")
        badge = QLabel("严重" if level == "error" else "警告")
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(
            "color: %s; background: rgba(%s, 0.24); border: 1px solid rgba(%s, 0.5);"
            " border-radius: 11px; padding: 3px 10px; font-size: 11px; font-weight: 600;"
            % (("#ff8a80", "255, 59, 48", "255, 59, 48") if level == "error"
               else ("#ffb74d", "255, 159, 10", "255, 159, 10"))
        )
        lay.addWidget(badge)

        # message + server
        col = QVBoxLayout()
        col.setSpacing(2)
        msg = QLabel(ev.get("message", ""))
        msg.setObjectName("cardTitle")
        col.addWidget(msg)
        server = QLabel(ev.get("server", ""))
        server.setObjectName("cardHost")
        col.addWidget(server)
        lay.addLayout(col)
        lay.addStretch(1)

        # time
        t = ev.get("resolved") or ev.get("time")
        time_lbl = QLabel(time.strftime("%m-%d %H:%M:%S", time.localtime(t)))
        time_lbl.setObjectName("cardHost")
        lay.addWidget(time_lbl)

        # status
        active = ev.get("status") == "active"
        status = QLabel("进行中" if active else "已恢复")
        status.setAlignment(Qt.AlignCenter)
        color = ("#ff8a80", "255, 59, 48", "255, 59, 48") if active else ("#7ce8a4", "52, 199, 89", "52, 199, 89")
        status.setStyleSheet(
            "color: %s; background: rgba(%s, 0.2); border: 1px solid rgba(%s, 0.45);"
            " border-radius: 11px; padding: 3px 10px; font-size: 11px; font-weight: 600;" % color
        )
        lay.addWidget(status)


class AlertsPage(GlassFrame):
    def __init__(self, parent=None):
        super().__init__(parent, radius=26)
        self._last_sig = None
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        # header
        head = QHBoxLayout()
        head.setSpacing(12)
        title = QLabel("告警中心")
        title.setObjectName("sectionTitle")
        head.addWidget(title)
        hint = QLabel("阈值：CPU 80% · 内存 85% · 磁盘 90% · 离线")
        hint.setObjectName("appSubtitle")
        head.addWidget(hint)
        head.addStretch(1)
        lay.addLayout(head)

        # summary tiles
        tiles = QHBoxLayout()
        tiles.setSpacing(14)
        self.tile_active = self._build_tile(tiles, "进行中", "#ff3b30")
        self.tile_resolved = self._build_tile(tiles, "今日已解决", "#34c759")
        self.tile_total = self._build_tile(tiles, "累计告警", "#ff9f0a")
        lay.addLayout(tiles)

        # event list
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.NoFrame)
        self._scroll.viewport().setAutoFillBackground(False)
        self._container = QWidget()
        self._container.setAutoFillBackground(False)
        self._list_lay = QVBoxLayout(self._container)
        self._list_lay.setContentsMargins(0, 0, 0, 0)
        self._list_lay.setSpacing(10)
        self._list_lay.addStretch(1)
        self._scroll.setWidget(self._container)
        lay.addWidget(self._scroll, 1)

        # empty state
        self._empty = GlassFrame(radius=22)
        el = QVBoxLayout(self._empty)
        el.setContentsMargins(24, 40, 24, 40)
        et = QLabel("暂无告警记录")
        et.setObjectName("appTitle")
        et.setAlignment(Qt.AlignCenter)
        eh = QLabel("一切正常 · 指标超过阈值或服务器离线时这里会出现记录")
        eh.setObjectName("appSubtitle")
        eh.setAlignment(Qt.AlignCenter)
        el.addStretch(1)
        el.addWidget(et)
        el.addWidget(eh)
        el.addStretch(1)
        self._list_lay.addWidget(self._empty)

    def _build_tile(self, layout, label, color):
        tile = GlassFrame(radius=22)
        tile.setFixedHeight(86)
        lay = QHBoxLayout(tile)
        lay.setContentsMargins(20, 14, 20, 14)
        v = QVBoxLayout()
        v.setSpacing(1)
        val = QLabel("0")
        val.setObjectName("tileNum")
        val.setStyleSheet(f"color: {color};")
        lbl = QLabel(label)
        lbl.setObjectName("tileLbl")
        v.addWidget(val)
        v.addWidget(lbl)
        lay.addLayout(v)
        lay.addStretch(1)
        layout.addWidget(tile, 1)
        return val

    def update_view(self, events, active):
        today = time.localtime().tm_yday
        resolved_today = sum(
            1 for e in events
            if e.get("status") == "resolved"
            and time.localtime(e.get("resolved") or 0).tm_yday == today
        )
        self.tile_active.setText(str(active))
        self.tile_resolved.setText(str(resolved_today))
        self.tile_total.setText(str(len(events)))

        sig = (
            active,
            tuple((round(e.get("value") or 0, 1), e.get("status")) for e in events[:60]),
        )
        if sig == self._last_sig:
            return
        self._last_sig = sig

        # rebuild rows
        while self._list_lay.count():
            item = self._list_lay.takeAt(0)
            w = item.widget()
            if w is not None and w is not self._empty:
                w.deleteLater()

        if not events:
            self._list_lay.addWidget(self._empty)
            self._empty.show()
            return
        self._empty.hide()

        for ev in events[:60]:
            row = AlertRow(ev)
            self._list_lay.insertWidget(self._list_lay.count() - 1, row)
