# Server Monitor

轻量级多服务器监控客户端，内置 VNC 远程桌面。Windows 桌面应用。

## 功能

- **多服务器监控**：卡片式展示每台服务器的 CPU、内存、磁盘、网络速率、负载与实时延迟
- **实时图表**：每台服务器绘制 CPU / 内存 / 网络吞吐量趋势曲线
- **VNC 远程桌面**：内嵌 VNC 客户端，支持鼠标与键盘输入转发，免装额外 VNC 软件
- **在线状态一目了然**：ONLINE / OFFLINE 状态点、延迟毫秒数、最后更新时间
- **易配置**：图形化添加/编辑服务器，每个服务器独立配置 Agent 端口、认证 Token、VNC 端口与密码
- **轻量 Agent**：服务器端只需运行单个 Python 脚本（`agent/monitor_agent.py`），HTTP 暴露 `/api/stats`

## 架构

```
┌──────────────┐   HTTP /api/stats    ┌─────────────────┐
│  Client exe  │ ───────────────────► │  monitor_agent  │ 每台被监控服务器
│  (PySide6)   │                      │  (:8899, token) │
│              │ ───────────────────► │  VNC server     │
│  + VNC 内嵌  │   RFB (5901)        │  (x11vnc/Tiger) │
└──────────────┘                      └─────────────────┘
```

## 快速开始

### 服务器端（被监控机器）

```bash
# 1. 启动监控 Agent（端口 8899，可选 token）
python3 agent/monitor_agent.py --port 8899 --token YOUR_TOKEN

# 2. 可选：启动 VNC 服务（如 x11vnc，端口 5901）
x11vnc -display :0 -forever -shared -rfbauth ~/.vnc/passwd -rfbport 5901
```

### 客户端（Windows）

1. 从 [Releases](https://github.com/NaopTrump08/server-monitor/releases) 下载 `ServerMonitor.zip`
2. 解压后双击 `ServerMonitor.exe`
3. 点击 "+ Add Server"，填写服务器 IP、Agent 端口（8899）、Token、VNC 端口（5901）与 VNC 密码
4. 卡片实时显示状态，点击卡片上的 VNC 按钮进入远程桌面

### 源码运行（开发）

```bash
cd client
pip install -r requirements.txt
python src/main.py
```

## 自行打包 exe

- Windows：双击 `client/scripts/build_exe.bat`
- 或推送 `v*` 标签，GitHub Actions 自动构建并发布 Release

## 安全提示

- 默认配置为占位符，请勿将真实服务器 IP 与凭据提交到公开仓库
- Agent 建议设置强 Token 并限制仅内网访问
- VNC 建议仅暴露给可信网络，或配合防火墙

## License

MIT
