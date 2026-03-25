#!/usr/bin/env python3
"""Backend API for the web frontend."""

from __future__ import annotations

import random
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

from client_bridge import SkillClientBridge


ROOT = Path(__file__).resolve().parent
RUNTIME_DIR = ROOT / "runtime"
UPLOADS_DIR = RUNTIME_DIR / "uploads"
OUTPUTS_DIR = RUNTIME_DIR / "outputs"
VOICE_CACHE_FILE = RUNTIME_DIR / "voice_cache" / "voices_cache.json"
SETTINGS_FILE = RUNTIME_DIR / "settings.json"
WEB_DIST_DIR = ROOT / "web" / "dist"
FALLBACK_VOICES = [
    {"name": "湾湾小何（女声）", "code": "zh_female_wanwanxiaohe_moon_bigtts", "value": "zh_female_wanwanxiaohe_moon_bigtts", "label": "湾湾小何（女声）"},
    {"name": "少年子辛（男声）", "code": "zh_male_shaonianzixin_mars_bigtts", "value": "zh_male_shaonianzixin_mars_bigtts", "label": "少年子辛（男声）"},
]

for folder in (UPLOADS_DIR, OUTPUTS_DIR):
    folder.mkdir(parents=True, exist_ok=True)


class VoiceListRequest(BaseModel):
    token: str
    refresh: bool = True


class ScriptRequest(BaseModel):
    requirement: str
    seconds: int = 40


class VoiceoverPayload(BaseModel):
    enabled: bool = False
    text: str = ""
    token: str = ""
    speaker: str = ""
    rate: int = 0
    volume: int = 100
    mixLevel: float = 1.0
    originalAudioMixLevel: float = 0.45
    subtitlesEnabled: bool = True
    subtitleFontsize: int = 40
    subtitleFontcolor: str = "white"
    matchVideoDuration: bool = True
    ssml: str = ""
    resourceId: str = "volcano_tts"
    emotion: str = ""
    emotionScale: Optional[int] = None
    loudnessRate: int = 0
    enableTimestamp: bool = False
    pitch: int = 0
    mixSpeaker: Optional[Dict[str, Any]] = None


class MixRequest(BaseModel):
    clips: List[str] = Field(default_factory=list)
    outputName: str = "mixed_output.mp4"
    resolution: List[int] = Field(default_factory=lambda: [1920, 1080])
    transition: str = "fade"
    transitionDuration: float = 1.0
    audioFadeIn: float = 0.0
    audioFadeOut: float = 0.0
    randomizeOrder: bool = True
    randomSeed: Optional[int] = None
    targetDuration: Optional[float] = None
    overlayText: str = ""
    voiceover: VoiceoverPayload = Field(default_factory=VoiceoverPayload)


class SettingsPayload(BaseModel):
    voiceToken: str = ""


app = FastAPI(title="GoEditVideo Web Backend", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

bridge = SkillClientBridge(workdir=ROOT)


@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "status": bridge.get_runtime_status()}


@app.get("/api/settings")
def get_settings() -> Dict[str, Any]:
    if not SETTINGS_FILE.exists():
        return {"success": True, "settings": {"voiceToken": ""}}
    try:
        data = json_load(SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    return {"success": True, "settings": {"voiceToken": str(data.get("voiceToken", ""))}}


@app.post("/api/settings")
def save_settings(payload: SettingsPayload) -> Dict[str, Any]:
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json_dump({"voiceToken": payload.voiceToken.strip()}), encoding="utf-8")
    return {"success": True, "message": "Settings saved."}


@app.post("/api/voices")
def get_voices(payload: VoiceListRequest) -> Dict[str, Any]:
    result = bridge.fetch_volc_tts_voices(token=payload.token, refresh=payload.refresh)
    if result.success:
        voices = result.output.get("voices", [])
        try:
            VOICE_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            VOICE_CACHE_FILE.write_text(json_dump({"voices": voices}), encoding="utf-8")
        except Exception:
            pass
        return {"success": True, "message": result.message, "voices": voices}

    if VOICE_CACHE_FILE.exists():
        try:
            cached = json_load(VOICE_CACHE_FILE.read_text(encoding="utf-8"))
            voices = cached.get("voices", [])
            if isinstance(voices, list) and voices:
                return {
                    "success": True,
                    "message": "Voice API is temporarily unavailable. Using local cached voice list.",
                    "voices": voices,
                    "warning": result.error,
                }
        except Exception:
            pass

    return {
        "success": True,
        "message": "Voice API is unavailable. Using built-in fallback voices.",
        "voices": FALLBACK_VOICES,
        "warning": result.error,
    }


def json_dump(data: Dict[str, Any]) -> str:
    import json

    return json.dumps(data, ensure_ascii=False, indent=2)


def json_load(text: str) -> Dict[str, Any]:
    import json

    return json.loads(text)


@app.post("/api/script")
def generate_script(payload: ScriptRequest) -> Dict[str, Any]:
    result = bridge.generate_voiceover_script(payload.requirement, payload.seconds)
    if not result.success:
        return {"success": False, "message": result.message, "error": result.error}
    return {"success": True, "message": result.message, "script": result.output.get("script", "")}


@app.post("/api/upload-clips")
async def upload_clips(files: List[UploadFile] = File(...)) -> Dict[str, Any]:
    session_dir = UPLOADS_DIR / f"upload_{int(time.time())}"
    session_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: List[str] = []

    for item in files:
        suffix = Path(item.filename or "").suffix.lower()
        if suffix not in {".mp4", ".mov", ".mkv", ".avi", ".flv"}:
            continue
        safe_name = Path(item.filename or f"clip_{len(saved_paths) + 1}.mp4").name
        target = session_dir / safe_name
        with target.open("wb") as handle:
            shutil.copyfileobj(item.file, handle)
        saved_paths.append(str(target))

    if not saved_paths:
        return {"success": False, "message": "No valid video files uploaded."}
    return {"success": True, "message": f"Uploaded {len(saved_paths)} clips.", "clips": saved_paths}


@app.post("/api/mix")
def mix_video(payload: MixRequest) -> Dict[str, Any]:
    if not payload.clips:
        return {"success": False, "message": "Please upload clips first."}

    output_name = Path(payload.outputName).name
    output_path = OUTPUTS_DIR / output_name

    use_voiceover = bool(payload.voiceover.enabled and payload.voiceover.text.strip())
    per_clip_duration: Optional[float] = None
    if (not use_voiceover) and payload.targetDuration and payload.targetDuration > 0:
        per_clip_duration = max(0.5, float(payload.targetDuration) / max(1, len(payload.clips)))

    command_payload: Dict[str, Any] = {
        "output": str(output_path),
        "resolution": payload.resolution,
        "clips": [
            {
                "path": clip_path,
                "transition": payload.transition,
                "transitionDuration": payload.transitionDuration,
                **({"duration": per_clip_duration} if per_clip_duration else {}),
            }
            for clip_path in payload.clips
        ],
        "audioFadeIn": payload.audioFadeIn,
        "audioFadeOut": payload.audioFadeOut,
        "randomizeOrder": payload.randomizeOrder,
        "randomSeed": payload.randomSeed if payload.randomSeed is not None else random.randint(1, 999_999_999),
    }

    if payload.overlayText.strip():
        command_payload["textOverlays"] = [
            {
                "text": payload.overlayText.strip(),
                "startTime": 0,
                "duration": 3,
                "fontsize": 42,
                "fontcolor": "white",
                "x": "center",
                "y": "top",
            }
        ]

    local_tts_fallback = False
    local_tts_reason = ""

    if use_voiceover:
        voice_data: Dict[str, Any] = {
            "enabled": True,
            "text": payload.voiceover.text.strip(),
            "rate": payload.voiceover.rate,
            "volume": payload.voiceover.volume,
            "voiceName": payload.voiceover.speaker.strip(),
            "mixLevel": payload.voiceover.mixLevel,
            "originalAudioMixLevel": payload.voiceover.originalAudioMixLevel,
            "subtitlesEnabled": payload.voiceover.subtitlesEnabled,
            "subtitleFontsize": payload.voiceover.subtitleFontsize,
            "subtitleFontcolor": payload.voiceover.subtitleFontcolor,
            "matchVideoDuration": payload.voiceover.matchVideoDuration,
        }

        if payload.voiceover.token.strip() and payload.voiceover.speaker.strip():
            tts_result = bridge.synthesize_volc_tts_stream(
                token=payload.voiceover.token.strip(),
                text=payload.voiceover.text.strip(),
                speaker=payload.voiceover.speaker.strip(),
                audio_format="mp3",
                sample_rate=24000,
                speech_rate=payload.voiceover.rate,
                preview=False,
                ssml=payload.voiceover.ssml.strip(),
                resource_id=payload.voiceover.resourceId.strip() or "volcano_tts",
                emotion=payload.voiceover.emotion.strip(),
                emotion_scale=payload.voiceover.emotionScale,
                loudness_rate=payload.voiceover.loudnessRate,
                enable_timestamp=payload.voiceover.enableTimestamp,
                pitch=payload.voiceover.pitch,
                mix_speaker=payload.voiceover.mixSpeaker,
            )
            if tts_result.success:
                audio_path = tts_result.output.get("audioPath") if isinstance(tts_result.output, dict) else None
                if audio_path:
                    voice_data["audioPath"] = audio_path
                else:
                    local_tts_fallback = True
                    local_tts_reason = "Remote TTS returned no audio path."
            else:
                local_tts_fallback = True
                local_tts_reason = tts_result.message or "Remote TTS failed."

        command_payload["voiceover"] = voice_data

    result = bridge.call("mix", command_payload)
    if not result.success:
        return {"success": False, "message": result.message, "error": result.error}

    response: Dict[str, Any] = {
        "success": True,
        "message": result.message,
        "outputPath": str(output_path),
        "downloadUrl": f"/api/download/{output_name}",
        "details": result.output,
    }
    if local_tts_fallback:
        response["warning"] = "Remote TTS failed; used local system voice fallback."
        response["warningDetail"] = local_tts_reason
    return response


@app.get("/api/download/{filename}")
def download_file(filename: str):
    target = OUTPUTS_DIR / Path(filename).name
    if not target.exists():
        return JSONResponse({"success": False, "message": "File not found."}, status_code=404)
    return FileResponse(path=target, filename=target.name, media_type="video/mp4")


if WEB_DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=WEB_DIST_DIR, html=True), name="web")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
