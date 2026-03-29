#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Client bridge for invoking the local Python video-mixer skill."""

from __future__ import annotations

import base64
import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import error, parse, request

import requests

from runtime_manager import RuntimeManager
from skill_handler import VideoMixerSkillHandler

FIXED_TTS_ACCESS_TOKEN = "nAblyxkQTcVaeBu4M0rKaphRuwkdlbOV"


@dataclass
class ClientResult:
    success: bool
    message: str
    output: Any = None
    error: Optional[str] = None
    backend: str = "local"
    raw_output: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any], backend: str, raw_output: str = "") -> "ClientResult":
        return cls(
            success=bool(data.get("success")),
            message=str(data.get("message", "")),
            output=data.get("output"),
            error=data.get("error"),
            backend=backend,
            raw_output=raw_output,
        )


class SkillClientBridge:
    COZE_WORKFLOW_URL = "https://api.coze.cn/v1/workflow/run"
    COZE_WORKFLOW_ID = "7621492603993276454"
    COZE_API_TOKEN = "sat_1ioklBC8oH3qXf4EcZzqipjgwFRVuDXP2sAyUREK4rt27S7RyPd1PsDk2hmKSogJ"
    DEFAULT_COZE_INPUT = (
        "过年买好物，就来小琰商店！新春特惠火热开启，福利直接拉满！"
        "全场消费满九十九，立减三十！实实在在的优惠，不玩套路，只给实惠！"
        "不仅如此，进店还有超多好礼相送，惊喜不断，福利不停！"
        "新的一年，小琰商店陪你红红火火"
    )

    def __init__(self, skill_name: str = "video-mixer", workdir: Optional[Path] = None):
        self.skill_name = skill_name
        self.workdir = Path(workdir or Path.cwd())
        self.runtime = RuntimeManager(self.workdir)

    def get_runtime_status(self) -> Dict[str, str]:
        statuses = self.runtime.get_status()
        return {
            name: f"{status.detail}: {status.path}" if status.path else status.detail
            for name, status in statuses.items()
        }

    def run_preflight(self) -> ClientResult:
        statuses = self.runtime.get_status()
        failures = [name for name, status in statuses.items() if not status.available]
        if failures:
            return ClientResult(
                success=False,
                message="Preflight failed. One or more required runtimes are missing.",
                output={name: status.path or status.detail for name, status in statuses.items()},
                error=", ".join(failures),
                backend="preflight",
            )

        return ClientResult(
            success=True,
            message="Preflight passed. Required runtimes and local skill files are present.",
            output={name: status.path or status.detail for name, status in statuses.items()},
            backend="preflight",
        )

    def call(self, command: str, params: Dict[str, Any]) -> ClientResult:
        handler = VideoMixerSkillHandler()
        previous_path = os.environ.get("PATH", "")
        env = self.runtime.build_env()
        try:
            os.environ["PATH"] = env.get("PATH", previous_path)
            response = handler.process(command, params)
        finally:
            os.environ["PATH"] = previous_path
        return ClientResult.from_dict(response.to_dict(), backend="local")

    def generate_voiceover_script(self, user_requirement: str, seconds: int = 40) -> ClientResult:
        requirement = user_requirement.strip()
        if not requirement:
            return ClientResult(
                success=False,
                message="Please enter the customer's requirement first.",
                error="missing_requirement",
                backend="voiceover",
            )

        script = self._build_local_voiceover_script(requirement, seconds)
        return ClientResult(
            success=True,
            message="Voice-over script generated locally.",
            output={"script": script, "seconds": seconds},
            backend="local",
        )

    def fetch_volc_tts_voices(self, token: str, refresh: bool = True, timeout: int = 20) -> ClientResult:
        token_value = token.strip()
        if not token_value:
            return ClientResult(
                success=False,
                message="Please enter the API token first.",
                error="missing_token",
                backend="remote",
            )

        query = parse.urlencode({"refresh": 1 if refresh else 0})
        url = f"https://api8.92k.fun/api/api-market/invoke/volc-tts-voices?{query}"
        headers = {
            "Authorization": f"Bearer {token_value}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        req = request.Request(url=url, method="GET", headers=headers)
        status_code = 0
        raw_text = ""
        last_error = ""
        for attempt in range(3):
            try:
                with request.urlopen(req, timeout=timeout) as resp:
                    status_code = getattr(resp, "status", 200)
                    raw_text = resp.read().decode("utf-8", errors="replace")
                last_error = ""
                break
            except error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace") if hasattr(exc, "read") else str(exc)
                return ClientResult(
                    success=False,
                    message=f"Failed to fetch voices: HTTP {exc.code}",
                    error=detail,
                    backend="remote",
                    raw_output=detail,
                )
            except Exception as exc:
                last_error = str(exc)
                if attempt < 2:
                    time.sleep(0.35 * (attempt + 1))
                continue

        if last_error:
            return ClientResult(
                success=False,
                message="Failed to fetch voices.",
                error=last_error,
                backend="remote",
            )

        if status_code >= 400:
            return ClientResult(
                success=False,
                message=f"Failed to fetch voices: HTTP {status_code}",
                error=raw_text,
                backend="remote",
                raw_output=raw_text,
            )

        try:
            payload = json.loads(raw_text)
        except json.JSONDecodeError:
            return ClientResult(
                success=False,
                message="Voice list API returned non-JSON data.",
                error="invalid_json",
                backend="remote",
                raw_output=raw_text,
            )

        voices = self._extract_voice_options(payload)
        if not voices:
            return ClientResult(
                success=False,
                message="No voices found in API response.",
                error="empty_voice_list",
                backend="remote",
                raw_output=raw_text,
            )

        return ClientResult(
            success=True,
            message=f"Fetched {len(voices)} voices.",
            output={"voices": voices},
            backend="remote",
            raw_output=raw_text,
        )

    def synthesize_volc_tts_stream(
        self,
        token: str,
        text: str,
        speaker: str,
        audio_format: str = "mp3",
        sample_rate: int = 24000,
        speech_rate: int = 0,
        preview: bool = False,
        ssml: str = "",
        resource_id: str = "volcano_tts",
        emotion: str = "",
        emotion_scale: Optional[int] = None,
        loudness_rate: int = 0,
        enable_timestamp: bool = False,
        pitch: int = 0,
        mix_speaker: Optional[Dict[str, Any]] = None,
        timeout: int = 90,
    ) -> ClientResult:
        token_value = token.strip()
        if not token_value:
            return ClientResult(False, "Please enter the API token first.", error="missing_token", backend="remote")
        content = text.strip()
        if not content:
            return ClientResult(False, "Voice-over text is empty.", error="missing_text", backend="remote")
        speaker_value = speaker.strip()
        if not speaker_value:
            return ClientResult(False, "Please select a voice tone first.", error="missing_speaker", backend="remote")

        url = "https://api8.92k.fun/api/api-market/invoke/volc-tts-stream"
        payload: Dict[str, Any] = {
            "text": content,
            "speaker": speaker_value,
            "voice_type": speaker_value,
            "resource_id": resource_id,
            "preview": bool(preview),
            "audio_params.format": audio_format,
            "audio_params.sample_rate": sample_rate,
            "audio_params.speech_rate": speech_rate,
            "audio_params.loudness_rate": loudness_rate,
            "audio_params.enable_timestamp": bool(enable_timestamp),
            "additions.post_process.pitch": pitch,
        }
        if ssml.strip():
            payload["ssml"] = ssml.strip()
        if emotion.strip():
            payload["audio_params.emotion"] = emotion.strip()
        if emotion_scale is not None:
            payload["audio_params.emotion_scale"] = int(emotion_scale)
        if isinstance(mix_speaker, dict) and mix_speaker:
            payload["mix_speaker"] = mix_speaker
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {token_value}",
            "Content-Type": "application/json",
            "Accept": "*/*",
        }
        req = request.Request(url=url, method="POST", data=body, headers=headers)
        # Force direct connection and ignore system proxy env vars.
        opener = request.build_opener(request.ProxyHandler({}))

        try:
            with opener.open(req, timeout=timeout) as resp:
                status_code = getattr(resp, "status", 200)
                content_type = (resp.headers.get("Content-Type") or "").lower()
                data_bytes = resp.read()
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace") if hasattr(exc, "read") else str(exc)
            return ClientResult(
                False,
                f"TTS request failed: HTTP {exc.code}",
                error=detail,
                backend="remote",
                raw_output=detail,
            )
        except Exception as exc:
            return ClientResult(False, "TTS request failed.", error=str(exc), backend="remote")

        if status_code >= 400:
            return ClientResult(
                False,
                f"TTS request failed: HTTP {status_code}",
                error=data_bytes.decode("utf-8", errors="replace"),
                backend="remote",
            )

        file_bytes: bytes
        response_text = data_bytes.decode("utf-8", errors="replace")
        if "application/json" in content_type or response_text.strip().startswith("{"):
            try:
                response_json = json.loads(response_text)
            except json.JSONDecodeError:
                return ClientResult(False, "TTS response JSON is invalid.", error="invalid_json", backend="remote")

            err_code = self._pick_first(response_json, ["code", "error_code", "errCode"])
            if err_code not in (None, 0, "0", "200", 200):
                err_msg = self._pick_first(response_json, ["message", "msg", "error", "errMsg"]) or response_text
                return ClientResult(False, f"TTS generation failed: {err_msg}", error=str(err_code), backend="remote")

            file_bytes = self._extract_audio_bytes_from_json(response_json)
            if not file_bytes:
                audio_url = self._extract_audio_url_from_json(response_json)
                if audio_url:
                    download_result = self._download_binary(audio_url, timeout=timeout)
                    if not download_result.success:
                        return download_result
                    file_bytes = download_result.output["bytes"]
                else:
                    return ClientResult(
                        False,
                        "TTS generation failed: no audio data in response.",
                        error="missing_audio",
                        backend="remote",
                        raw_output=response_text[:1000],
                    )
        else:
            file_bytes = data_bytes

        if not file_bytes or len(file_bytes) < 256:
            return ClientResult(False, "TTS audio is empty.", error="empty_audio", backend="remote")

        cache_dir = self.workdir / "runtime" / "voice_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        ext = "mp3" if audio_format.lower() not in {"pcm", "wav"} else audio_format.lower()
        file_path = cache_dir / f"tts_{uuid.uuid4().hex[:12]}.{ext}"
        file_path.write_bytes(file_bytes)

        return ClientResult(
            True,
            "TTS audio generated.",
            output={"audioPath": str(file_path), "speaker": speaker_value, "format": ext},
            backend="remote",
        )

    def synthesize_tts_http_demo(
        self,
        access_token: str,
        text: str,
        speaker: str,
        emotion: str = "",
        appid: str = "9847999155",
        cluster: str = "volcano_tts",
        host: str = "openspeech.bytedance.com",
        timeout: int = 90,
    ) -> ClientResult:
        # Temporarily pin to a fixed token to avoid frontend/config mismatch.
        token_value = FIXED_TTS_ACCESS_TOKEN
        content = self._normalize_tts_text(text)
        if not content:
            return ClientResult(False, "Voice-over text is empty.", error="missing_text", backend="remote")
        voice_type = speaker.strip() or "BV700_V2_streaming"

        url = f"https://{host}/api/v1/tts"
        headers = {
            "Authorization": f"Bearer;{token_value}",
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
        }
        payload: Dict[str, Any] = {
            "app": {"appid": appid, "token": "access_token", "cluster": cluster},
            "user": {"uid": str(uuid.uuid4().hex[:15])},
            "audio": {
                "voice_type": voice_type,
                "encoding": "mp3",
                "speed_ratio": 1.0,
                "volume_ratio": 1.0,
                "pitch_ratio": 1.0,
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": content,
                "text_type": "plain",
                "operation": "query",
                "with_frontend": 1,
                "frontend_type": "unitTson",
            },
        }
        if emotion.strip():
            payload["audio"]["emotion"] = emotion.strip()

        def _post_once(req_text: str) -> ClientResult:
            local_payload = dict(payload)
            local_payload["request"] = dict(payload["request"])
            local_payload["request"]["text"] = req_text
            try:
                with requests.Session() as session:
                    # Force direct connection and ignore system proxy env vars.
                    session.trust_env = False
                    # Use `json=` to avoid latin-1 body encoding errors for non-ASCII text.
                    resp = session.post(url, json=local_payload, headers=headers, timeout=timeout)
                raw_text = resp.text
                response_json = resp.json()
            except Exception as exc:
                return ClientResult(False, "TTS demo request failed.", error=str(exc), backend="remote")

            code = response_json.get("code")
            if code not in (3000, "3000", 0, "0"):
                msg = str(response_json.get("message") or response_json.get("msg") or "TTS demo failed.")
                return ClientResult(False, f"TTS demo failed: {msg}", error=str(code), backend="remote", raw_output=raw_text[:2000])

            data_b64 = response_json.get("data")
            if not isinstance(data_b64, str) or not data_b64.strip():
                return ClientResult(False, "TTS demo response has no audio data.", error="missing_audio", backend="remote")

            try:
                file_bytes = base64.b64decode(data_b64)
            except Exception:
                return ClientResult(False, "TTS demo audio base64 decode failed.", error="invalid_audio_base64", backend="remote")

            if not file_bytes or len(file_bytes) < 256:
                return ClientResult(False, "TTS demo audio is empty.", error="empty_audio", backend="remote")

            cache_dir = self.workdir / "runtime" / "voice_cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            file_path = cache_dir / f"tts_demo_{uuid.uuid4().hex[:12]}.mp3"
            file_path.write_bytes(file_bytes)

            timestamp_path = ""
            matched_path = ""
            matched_items: List[Dict[str, Any]] = []
            addition = response_json.get("addition", {})
            frontend = addition.get("frontend") if isinstance(addition, dict) else None
            if isinstance(frontend, str) and frontend.strip():
                try:
                    frontend_obj = json.loads(frontend)
                    ts_path = file_path.with_suffix(".timestamps.json")
                    ts_path.write_text(json.dumps(frontend_obj, ensure_ascii=False, indent=2), encoding="utf-8")
                    timestamp_path = str(ts_path)

                    coze_input_text = content.strip() or self.DEFAULT_COZE_INPUT
                    key_phrases = self._fetch_key_phrases_from_coze(coze_input_text)
                    matched_items = self._match_key_phrases_from_frontend(frontend_obj, key_phrases)
                    if not matched_items:
                        matched_items = self._match_key_phrases_from_frontend(frontend_obj, None)
                    if matched_items:
                        matched_file = file_path.with_suffix(".matched_key_phrases.json")
                        matched_file.write_text(json.dumps(matched_items, ensure_ascii=False, indent=2), encoding="utf-8")
                        matched_path = str(matched_file)
                except Exception:
                    timestamp_path = ""
                    matched_path = ""
                    matched_items = []

            return ClientResult(
                True,
                "TTS demo audio generated.",
                output={
                    "audioPath": str(file_path),
                    "timestampPath": timestamp_path,
                    "matchedKeyPhrasesPath": matched_path,
                    "matchedKeyPhrases": matched_items,
                    "durationMs": addition.get("duration") if isinstance(addition, dict) else None,
                    "speaker": voice_type,
                    "format": "mp3",
                },
                backend="remote",
            )

        result = _post_once(content)
        if result.success:
            return result

        if str(result.error) == "3011":
            retry_text = self._simplify_tts_text(content)
            if retry_text and retry_text != content:
                retry_result = _post_once(retry_text)
                if retry_result.success:
                    return retry_result
        return result

    @classmethod
    def _extract_voice_options(cls, payload: Any) -> List[Dict[str, str]]:
        options: List[Dict[str, str]] = []
        seen = set()

        for item in cls._iter_voice_candidates(payload):
            value = cls._pick_first(item, ["voice", "voiceName", "voice_id", "voiceId", "speaker", "id", "code"])
            if not value:
                continue
            value = str(value).strip()
            if not value or value in seen:
                continue
            name = cls._pick_first(item, ["name", "displayName", "title", "alias", "speakerName"])
            name = str(name).strip() if name else ""
            short_name = name if name else value
            options.append(
                {
                    "name": short_name,
                    "code": value,
                    "value": value,
                    "label": short_name,
                }
            )
            seen.add(value)
        return options

    @classmethod
    def _iter_voice_candidates(cls, node: Any) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        if isinstance(node, dict):
            if cls._pick_first(node, ["voice", "voiceName", "voice_id", "voiceId", "speaker", "id", "code"]):
                results.append(node)
            for value in node.values():
                results.extend(cls._iter_voice_candidates(value))
            return results
        if isinstance(node, list):
            for item in node:
                if isinstance(item, str) and item.strip():
                    results.append({"voice": item.strip(), "name": item.strip()})
                else:
                    results.extend(cls._iter_voice_candidates(item))
        return results

    @staticmethod
    def _pick_first(data: Dict[str, Any], keys: List[str]) -> Optional[Any]:
        for key in keys:
            value = data.get(key)
            if value is not None and str(value).strip():
                return value
        return None

    @classmethod
    def _extract_audio_url_from_json(cls, payload: Any) -> Optional[str]:
        for node in cls._iter_dict_nodes(payload):
            url = cls._pick_first(node, ["audio_url", "audioUrl", "url", "download_url", "file_url"])
            if isinstance(url, str) and url.startswith(("http://", "https://")):
                return url
        return None

    @classmethod
    def _extract_audio_bytes_from_json(cls, payload: Any) -> bytes:
        for node in cls._iter_dict_nodes(payload):
            for key in ("audio_base64", "base64", "audio", "audioData"):
                value = node.get(key)
                if not isinstance(value, str):
                    continue
                raw = value.strip()
                if not raw:
                    continue
                if raw.startswith("data:") and "," in raw:
                    raw = raw.split(",", 1)[1]
                try:
                    return base64.b64decode(raw, validate=False)
                except Exception:
                    continue
        return b""

    @classmethod
    def _iter_dict_nodes(cls, node: Any) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        if isinstance(node, dict):
            results.append(node)
            for value in node.values():
                results.extend(cls._iter_dict_nodes(value))
            return results
        if isinstance(node, list):
            for item in node:
                results.extend(cls._iter_dict_nodes(item))
        return results

    @staticmethod
    def _normalize_tts_text(text: str) -> str:
        raw = str(text or "")
        cleaned = (
            raw.replace("\r\n", "\n")
            .replace("\r", "\n")
            .replace("\t", " ")
            .replace("“", "\"")
            .replace("”", "\"")
            .replace("‘", "'")
            .replace("’", "'")
        )
        lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
        return " ".join(lines).strip()

    def _fetch_key_phrases_from_coze(self, input_text: str) -> List[str]:
        token = os.environ.get("COZE_API_TOKEN", "").strip() or self.COZE_API_TOKEN
        workflow_id = os.environ.get("COZE_WORKFLOW_ID", "").strip() or self.COZE_WORKFLOW_ID
        text_value = (input_text or "").strip() or self.DEFAULT_COZE_INPUT
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {"workflow_id": workflow_id, "parameters": {"input": text_value}}

        try:
            with requests.Session() as session:
                session.trust_env = False
                resp = session.post(self.COZE_WORKFLOW_URL, headers=headers, json=payload, timeout=20)
            resp_obj = resp.json()
            if resp_obj.get("code") != 0:
                print(f"[Coze API] workflow error: {resp_obj.get('msg') or resp_obj.get('message')}")
                return []
            data_raw = resp_obj.get("data")
            if not isinstance(data_raw, str):
                print(f"[Coze API] workflow data type invalid: {type(data_raw)}")
                return []
            data_obj = json.loads(data_raw)
            arr = data_obj.get("arr", [])
            if not isinstance(arr, list):
                print(f"[Coze API] arr field is not a list: {type(arr)}")
                return []
            phrases: List[str] = []
            for item in arr:
                if isinstance(item, dict):
                    phrase = str(item.get("text", "")).strip()
                    if phrase and phrase not in phrases:
                        phrases.append(phrase)
                elif isinstance(item, str):
                    phrase = item.strip()
                    if phrase and phrase not in phrases:
                        phrases.append(phrase)
            return phrases
        except Exception as exc:
            print(f"[Coze API] workflow request failed: {exc}")
            return []

    @classmethod
    def _match_key_phrases_from_frontend(
        cls, frontend_obj: Dict[str, Any], key_phrases: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        words = frontend_obj.get("words", [])
        if not isinstance(words, list) or not words:
            return []

        char_positions: List[Dict[str, Any]] = []
        for item in words:
            if not isinstance(item, dict):
                continue
            word = str(item.get("word", ""))
            start = item.get("start_time")
            end = item.get("end_time")
            if not word:
                continue
            if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
                continue
            for char in word:
                char_positions.append({"char": char, "start": float(start), "end": float(end)})

        if not char_positions:
            return []

        full_text = "".join(item["char"] for item in char_positions)
        targets = [p for p in (key_phrases or []) if isinstance(p, str) and p.strip()]
        if not targets:
            targets = cls._derive_key_phrases_from_text(full_text)
        if not targets:
            return []

        results: List[Dict[str, Any]] = []
        for phrase in targets:
            search_from = 0
            while True:
                start_index = full_text.find(phrase, search_from)
                if start_index < 0:
                    break
                end_index = start_index + len(phrase) - 1
                if end_index >= len(char_positions):
                    break
                results.append(
                    {
                        "text": phrase,
                        "start": char_positions[start_index]["start"],
                        "end": char_positions[end_index]["end"],
                    }
                )
                search_from = start_index + len(phrase)
        return results

    @staticmethod
    def _derive_key_phrases_from_text(full_text: str) -> List[str]:
        import re

        if not full_text:
            return []
        chunks = re.split(r"[，。！？!?,、\s]+", full_text)
        phrases: List[str] = []
        for chunk in chunks:
            phrase = chunk.strip()
            if len(phrase) < 4:
                continue
            if phrase in phrases:
                continue
            phrases.append(phrase)
            if len(phrases) >= 5:
                break
        return phrases

    @staticmethod
    def _simplify_tts_text(text: str) -> str:
        import re

        normalized = SkillClientBridge._normalize_tts_text(text)
        # Keep common CJK/ASCII words and basic punctuation only.
        simplified = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff，。！？、,.!?\-\s]", "", normalized)
        return re.sub(r"\s+", " ", simplified).strip()

    @staticmethod
    def _download_binary(url: str, timeout: int = 90) -> ClientResult:
        try:
            req = request.Request(url=url, method="GET", headers={"Accept": "*/*"})
            with request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
        except Exception as exc:
            return ClientResult(False, "Failed to download TTS audio.", error=str(exc), backend="remote")
        return ClientResult(True, "Downloaded audio.", output={"bytes": data}, backend="remote")

    @staticmethod
    def _build_local_voiceover_script(requirement: str, seconds: int) -> str:
        sentence_count = 5 if seconds <= 40 else 6
        base_lines = [
            f"这一次，我们围绕“{requirement}”做一条更有节奏感的短视频口播。",
            "画面会从素材库里自动挑选重点镜头，用更紧凑的方式把核心信息快速讲清楚。",
            "你会看到内容、氛围和节奏被重新组织，让整条视频更适合展示、讲解和传播。",
            "如果你希望强调产品亮点、使用场景或者情绪表达，这套自动混剪流程也能一起带出来。",
            "确认这段口播之后，系统就会结合现有素材直接开始混剪，输出一条更完整的成片。",
            "如果需要，我们还可以继续微调口播语气、镜头顺序和整体节奏。",
        ]
        return "".join(base_lines[:sentence_count])
