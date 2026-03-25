# Web 前端说明

本目录是视频混剪客户端的 Web 页面（React + Vite）。

## 开发模式

1. 安装依赖

```bash
npm install
```

2. 启动 Python 后端

```bash
cd ..
python web_backend.py
```

3. 启动前端

```bash
cd web
npm run dev
```

Vite 已配置 `/api` 代理到 `http://127.0.0.1:8765`。

## 生产构建

```bash
npm run build
```

构建产物在 `web/dist`，可由 `web_backend.py` 直接静态托管。
