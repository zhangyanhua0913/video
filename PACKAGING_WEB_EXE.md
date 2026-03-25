# Web Frontend + Python Backend 打包说明

## 1. 构建前端静态文件

```bash
cd web
npm install
npm run build
cd ..
```

构建完成后会生成 `web/dist`。

## 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

## 3. 本地启动（非打包）

```bash
python web_client_app.py
```

会自动打开浏览器访问 `http://127.0.0.1:8765`。

## 4. 打包为 exe

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --add-data "web/dist;web/dist" web_client_app.py
```

产物路径：`dist/web_client_app.exe`

## 5. 运行前提

- 目标机器需要安装 `ffmpeg` 和 `ffprobe` 并可在 PATH 访问。
- 若使用远程 TTS，需在界面填写有效 token 并能访问对应 API。
