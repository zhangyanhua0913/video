#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
VOICE_TEXTS_DIR = RUNTIME_DIR / "voice_texts"
VOICE_CACHE_FILE = RUNTIME_DIR / "voice_cache" / "voices_cache.json"
SETTINGS_FILE = RUNTIME_DIR / "settings.json"
WEB_DIST_DIR = ROOT / "web" / "dist"
DEFAULT_ACCESS_TOKEN = "nAblyxkQTcVaeBu4M0rKaphRuwkdlbOV"
DEFAULT_TTS_VOICE = "BV700_V2_streaming"
FALLBACK_VOICES = [
    {"name": "湾湾小何（女声）", "code": "zh_female_wanwanxiaohe_moon_bigtts", "value": "zh_female_wanwanxiaohe_moon_bigtts", "label": "湾湾小何（女声）"},
    {"name": "少年子辛（男声）", "code": "zh_male_shaonianzixin_mars_bigtts", "value": "zh_male_shaonianzixin_mars_bigtts", "label": "少年子辛（男声）"},
]

for folder in (UPLOADS_DIR, OUTPUTS_DIR, VOICE_TEXTS_DIR):
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
    token: str = DEFAULT_ACCESS_TOKEN
    voiceType: str = ""
    speaker: str = ""
    rate: int = 0
    volume: int = 100
    mixLevel: float = 1.0
    originalAudioMixLevel: float = 0.0
    subtitlesEnabled: bool = True
    subtitleFontsize: int = 40
    subtitleFontcolor: str = "white"
    subtitleTemplate: str = "subtitle"
    subtitleEffect: str = "pop"
    popupTemplate: str = "auto"
    matchVideoDuration: bool = True
    popupLeadTime: float = 0.18
    popupMinDuration: float = 0.55
    popupMergeGap: float = 0.10
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
    bgmTracks: List[str] = Field(default_factory=list)
    bgmVolume: float = 0.35
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


@app.post("/api/upload-bgm")
async def upload_bgm(files: List[UploadFile] = File(...)) -> Dict[str, Any]:
    session_dir = UPLOADS_DIR / f"bgm_{int(time.time())}"
    session_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: List[str] = []

    valid_suffixes = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}
    for item in files:
        suffix = Path(item.filename or "").suffix.lower()
        if suffix not in valid_suffixes:
            continue
        safe_name = Path(item.filename or f"bgm_{len(saved_paths) + 1}.mp3").name
        target = session_dir / safe_name
        with target.open("wb") as handle:
            shutil.copyfileobj(item.file, handle)
        saved_paths.append(str(target))

    if not saved_paths:
        return {"success": False, "message": "No valid audio files uploaded."}
    return {"success": True, "message": f"Uploaded {len(saved_paths)} bgm files.", "tracks": saved_paths}


@app.post("/api/mix")
def mix_video(payload: MixRequest) -> Dict[str, Any]:
    if not payload.clips:
        return {"success": False, "message": "Please upload clips first."}

    output_name = Path(payload.outputName).name
    output_path = OUTPUTS_DIR / output_name

    use_voiceover = bool(payload.voiceover.enabled and payload.voiceover.text.strip())
    selected_voice = payload.voiceover.voiceType.strip() or payload.voiceover.speaker.strip()
    if (not use_voiceover) and not (payload.targetDuration and payload.targetDuration > 0):
        return {"success": False, "message": "targetDuration is required when voice-over is disabled."}

    command_payload: Dict[str, Any] = {
        "output": str(output_path),
        "resolution": payload.resolution,
        "clips": [
            {
                "path": clip_path,
                "transition": payload.transition,
                "transitionDuration": payload.transitionDuration,
            }
            for clip_path in payload.clips
        ],
        "audioFadeIn": payload.audioFadeIn,
        "audioFadeOut": payload.audioFadeOut,
        "randomizeOrder": payload.randomizeOrder,
        "randomSeed": payload.randomSeed if payload.randomSeed is not None else random.randint(1, 999_999_999),
    }
    if (not use_voiceover) and payload.targetDuration:
        command_payload["targetDuration"] = float(payload.targetDuration)
    if payload.bgmTracks:
        command_payload["backgroundMusic"] = {
            "tracks": payload.bgmTracks,
            "volume": payload.bgmVolume,
        }

    if payload.overlayText.strip():
        command_payload["textOverlays"] = [
            {
                "text": payload.overlayText.strip(),
                "startTime": 0,
                "duration": 3,
                "fontsize": 42,
                "fontcolor": "white",
                "template": "sticker",
                "x": "center",
                "y": "top",
            }
        ]

    local_tts_fallback = False
    local_tts_reason = ""
    tts_mode = "disabled"

    def _format_tts_error(result_obj: Any) -> str:
        if not result_obj:
            return "Remote TTS failed."
        parts: List[str] = []
        msg = str(getattr(result_obj, "message", "") or "").strip()
        err = str(getattr(result_obj, "error", "") or "").strip()
        raw = str(getattr(result_obj, "raw_output", "") or "").strip()
        if msg:
            parts.append(msg)
        if err and err not in parts:
            parts.append(err)
        if raw and raw not in parts:
            parts.append(raw[:1200])
        if not parts:
            return "Remote TTS failed."
        return " | ".join(parts)

    if use_voiceover:
        print(f"[TTS] Voice-over enabled. selected_voice={selected_voice!r} text_len={len(payload.voiceover.text.strip())}")
        voice_text_path = ""
        try:
            safe_output_stem = Path(output_name).stem or "voiceover"
            voice_text_file = VOICE_TEXTS_DIR / f"{safe_output_stem}_{int(time.time())}.txt"
            voice_text_file.write_text(payload.voiceover.text.strip(), encoding="utf-8")
            voice_text_path = str(voice_text_file)
        except Exception as exc:
            print(f"[TTS] Failed to save voice text: {exc}")
        voice_data: Dict[str, Any] = {
            "enabled": True,
            "text": payload.voiceover.text.strip(),
            "rate": payload.voiceover.rate,
            "volume": payload.voiceover.volume,
            "voiceName": selected_voice,
            "mixLevel": payload.voiceover.mixLevel,
            "originalAudioMixLevel": payload.voiceover.originalAudioMixLevel,
            "subtitlesEnabled": payload.voiceover.subtitlesEnabled,
            "subtitleFontsize": payload.voiceover.subtitleFontsize,
            "subtitleFontcolor": payload.voiceover.subtitleFontcolor,
            "subtitleTemplate": payload.voiceover.subtitleTemplate,
            "subtitleEffect": payload.voiceover.subtitleEffect,
            "popupTemplate": payload.voiceover.popupTemplate,
            "matchVideoDuration": payload.voiceover.matchVideoDuration,
            "popupLeadTime": payload.voiceover.popupLeadTime,
            "popupMinDuration": payload.voiceover.popupMinDuration,
            "popupMergeGap": payload.voiceover.popupMergeGap,
        }
        if voice_text_path:
            voice_data["textPath"] = voice_text_path

        token_value = payload.voiceover.token.strip() or DEFAULT_ACCESS_TOKEN
        if token_value and selected_voice:
            tts_mode = "remote_attempt"
            print("[TTS] Trying remote TTS via /api/v1/tts ...")
            tts_result = bridge.synthesize_tts_http_demo(
                access_token=token_value,
                text=payload.voiceover.text.strip(),
                speaker=selected_voice,
                emotion=payload.voiceover.emotion.strip(),
                appid="9847999155",
                cluster=payload.voiceover.resourceId.strip() or "volcano_tts",
            )
            if not tts_result.success:
                # Keep a single stable path: retry /api/v1/tts with a known-good voice.
                # This avoids 403 from stream resource authorization mismatch.
                fallback_voice = DEFAULT_TTS_VOICE
                if selected_voice != fallback_voice:
                    print(
                        f"[TTS] /api/v1/tts failed with selected voice ({selected_voice}). "
                        f"Retrying with fallback voice ({fallback_voice}) ..."
                    )
                    tts_result = bridge.synthesize_tts_http_demo(
                        access_token=token_value,
                        text=payload.voiceover.text.strip(),
                        speaker=fallback_voice,
                        emotion=payload.voiceover.emotion.strip(),
                        appid="9847999155",
                        cluster=payload.voiceover.resourceId.strip() or "volcano_tts",
                    )
            if tts_result.success:
                audio_path = tts_result.output.get("audioPath") if isinstance(tts_result.output, dict) else None
                if audio_path:
                    tts_mode = "remote_success"
                    print(f"[TTS] Remote TTS success. audioPath={audio_path}")
                    voice_data["audioPath"] = audio_path
                    actual_speaker = tts_result.output.get("speaker") if isinstance(tts_result.output, dict) else None
                    if isinstance(actual_speaker, str) and actual_speaker.strip():
                        voice_data["voiceName"] = actual_speaker.strip()
                    ts_path = tts_result.output.get("timestampPath")
                    if isinstance(ts_path, str) and ts_path:
                        voice_data["timestampPath"] = ts_path
                        try:
                            ts_obj = json_load(Path(ts_path).read_text(encoding="utf-8"))
                            words = ts_obj.get("words", []) if isinstance(ts_obj, dict) else []
                            if isinstance(words, list) and words:
                                voice_data["timestampWords"] = words
                            timeline_lines: List[str] = []
                            for item in words if isinstance(words, list) else []:
                                if not isinstance(item, dict):
                                    continue
                                word = str(item.get("word", "")).strip()
                                start = item.get("start_time")
                                end = item.get("end_time")
                                if not word:
                                    continue
                                if isinstance(start, (int, float)) and isinstance(end, (int, float)):
                                    timeline_lines.append(f"{float(start):.3f} --> {float(end):.3f}  {word}")
                                else:
                                    timeline_lines.append(word)
                            if timeline_lines:
                                safe_output_stem = Path(output_name).stem or "voiceover"
                                timeline_file = VOICE_TEXTS_DIR / f"{safe_output_stem}_{int(time.time())}_timeline.txt"
                                timeline_file.write_text("\n".join(timeline_lines), encoding="utf-8")
                                voice_data["timelineTextPath"] = str(timeline_file)
                        except Exception as exc:
                            print(f"[TTS] Failed to save timeline text: {exc}")
                    matched_phrases = tts_result.output.get("matchedKeyPhrases") if isinstance(tts_result.output, dict) else None
                    if isinstance(matched_phrases, list):
                        voice_data["matchedKeyPhrases"] = matched_phrases
                    matched_path = tts_result.output.get("matchedKeyPhrasesPath") if isinstance(tts_result.output, dict) else None
                    if isinstance(matched_path, str) and matched_path:
                        voice_data["matchedKeyPhrasesPath"] = matched_path
                else:
                    tts_mode = "local_fallback"
                    local_tts_fallback = True
                    local_tts_reason = "Remote TTS returned no audio path."
                    print(f"[TTS] Fallback to local system voice: {local_tts_reason}")
            else:
                tts_mode = "local_fallback"
                local_tts_fallback = True
                local_tts_reason = _format_tts_error(tts_result)
                print(f"[TTS] Fallback to local system voice: {local_tts_reason}")
        else:
            tts_mode = "local_no_token"
            local_tts_reason = "Missing token or voice type."
            print(f"[TTS] Skip remote TTS: {local_tts_reason} token_present={bool(token_value)} voice_present={bool(selected_voice)}")

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
        "ttsMode": tts_mode,
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
