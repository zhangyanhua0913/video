# Packaged OpenClaw Plan

This project now includes a runtime-discovery layer so the desktop client can prefer bundled tools and validate a release bundle before packaging.

## Runtime layout

Place packaged dependencies in these folders:

```text
runtime/
  node/
    node.exe
    openclaw.cmd
    node_modules/
      openclaw/
      npm/
tools/
  ffmpeg/
    bin/
      ffmpeg.exe
      ffprobe.exe
skills/
  video-mixer/
    SKILL.md
    agents/
    references/
    scripts/
    skill.yml
    skill_handler.py
    video_mixer.py
```

If `skills/video-mixer/` is missing, the app falls back to the project root.

## What the app does

- `runtime_manager.py` detects bundled `ffmpeg`, `node`, and `openclaw`
- `packaged_openclaw_bridge.py` detects the local AgentSkill wrapper and falls back safely when OpenClaw CLI cannot execute command-style calls
- `client_bridge.py` prefers the bundled OpenClaw runtime and falls back to the local Python handler
- `packaging/prepare_runtime_bundle.py` copies private FFmpeg, Node, OpenClaw, and skill assets into the project bundle layout
- `packaging/preflight_check.py` verifies the bundle before you build an installer

## Recommended build flow

1. Run `python packaging/prepare_runtime_bundle.py`
2. Run `python packaging/preflight_check.py`
3. Build the Python GUI with `PyInstaller`
4. Create a Windows installer with Inno Setup

## PyInstaller example

```bash
pyinstaller --noconsole --onedir client_app.py
```

## Installer notes

- Keep logs and temp files under `%LOCALAPPDATA%`
- Do not rely on system `PATH`; ship private runtimes instead
- Let the client use local Python fallback when bundled OpenClaw is absent
- Run the app's "Run Preflight" button once on the packaged folder before shipping
