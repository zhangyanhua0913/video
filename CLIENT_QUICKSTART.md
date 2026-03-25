# Video Mixer Client Quick Start

## Run locally

```bash
python client_app.py
```

## What it does

- Lets the user pick video files in a desktop window
- Builds the `mix` payload for the existing skill
- Prefers `openclaw skill call video-mixer mix ...` when OpenClaw is installed
- Falls back to local `skill_handler.py` when OpenClaw is unavailable

## Packaging as an exe

Install PyInstaller:

```bash
pip install pyinstaller
```

Build:

```bash
pyinstaller --noconsole --onefile client_app.py
```

The packaged executable will be created under `dist/`.

## Notes

- `ffmpeg` and `ffprobe` still need to be available on the target machine.
- If you want the packaged client to use OpenClaw, `openclaw` must also be installed and available in `PATH`.
- If OpenClaw is not installed, the app still works through the local fallback path.

## Remote TTS (Volc)

1. In the client, enable `Add Voice-over`.
2. Fill `Voice API Token` with your Bearer token value (`sk-xxxx`).
3. Click `Refresh Voices` to fetch the latest voice list.
4. Choose a `Voice Tone`.
5. Start mixing.

When token + voice tone are both present, the client calls:

- `GET /api/api-market/invoke/volc-tts-voices` (voice list)
- `POST /api/api-market/invoke/volc-tts-stream` (generate speech audio)

Then the generated audio is injected into the mixing pipeline as the voice-over track.
