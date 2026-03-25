#!/usr/bin/env python3
"""Video mixing utilities backed by ffmpeg/ffprobe."""

from __future__ import annotations

import json
import os
import random
import re
import subprocess
import sys
import tempfile
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional


class VideoMixer:
    """High-level helper for mixing local video clips."""

    TRANSITIONS = {
        "fade": "Fade in/out",
        "wipeleft": "Wipe from left to right",
        "wiperight": "Wipe from right to left",
        "zoomin": "Zoom in",
        "circleopen": "Circle open",
        "pixelize": "Pixelize",
    }

    def __init__(self, output_path: str = "output.mp4", resolution: tuple = (1920, 1080)):
        self.clips: List[Dict[str, Any]] = []
        self.output_path = output_path
        self.resolution = resolution
        self.width, self.height = resolution
        self.text_overlays: List[Dict[str, Any]] = []
        self.audio_fade_in = 0.0
        self.audio_fade_out = 0.0
        self.color_correction_enabled = False
        self.brightness = 0.0
        self.contrast = 1.0
        self.saturation = 1.0
        self.gamma = 1.0
        self.voiceover_enabled = False
        self.voiceover_text = ""
        self.voiceover_rate = 0
        self.voiceover_volume = 100
        self.voiceover_voice_name: Optional[str] = None
        self.voiceover_mix_level = 1.0
        self.original_audio_mix_level = 0.5
        self.voiceover_subtitles_enabled = True
        self.voiceover_subtitle_fontsize = 40
        self.voiceover_subtitle_fontcolor = "white"
        self.voiceover_subtitle_font_path: Optional[str] = None
        self.match_video_to_voiceover = True
        self.external_voiceover_audio_path: Optional[str] = None

    def add_clip(
        self,
        file_path: str,
        duration: float | None = None,
        transition: str = "fade",
        transition_duration: float = 1.0,
    ) -> None:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"视频文件不存在: {file_path}")
        if transition and transition not in self.TRANSITIONS:
            raise ValueError(f"不支持的转场效果: {transition}")

        self.clips.append(
            {
                "path": os.path.abspath(file_path),
                "duration": duration,
                "transition": transition,
                "transition_duration": transition_duration,
            }
        )
        print(f"[OK] Added clip: {file_path}")

    def add_text_overlay(
        self,
        text: str,
        start_time: float = 0,
        duration: float = 5,
        x: str = "center",
        y: str = "center",
        fontsize: int = 24,
        fontcolor: str = "white",
        font_path: str | None = None,
    ) -> None:
        if x == "center":
            x = "(w-text_w)/2"
        elif x == "left":
            x = "10"
        elif x == "right":
            x = "w-text_w-10"

        if y == "center":
            y = "(h-text_h)/2"
        elif y == "top":
            y = "10"
        elif y == "bottom":
            y = "h-text_h-10"

        self.text_overlays.append(
            {
                "text": text,
                "start_time": float(start_time),
                "duration": float(duration),
                "x": x,
                "y": y,
                "fontsize": int(fontsize),
                "fontcolor": fontcolor,
                "font_path": font_path,
            }
        )

    def set_audio_fade(self, fade_in: float = 0, fade_out: float = 0) -> None:
        self.audio_fade_in = float(fade_in)
        self.audio_fade_out = float(fade_out)

    def shuffle_clips(self, seed: Optional[int] = None) -> None:
        rng = random.Random(seed)
        rng.shuffle(self.clips)

    def set_voiceover(
        self,
        text: str,
        enabled: bool = True,
        rate: int = 0,
        volume: int = 100,
        voice_name: Optional[str] = None,
        mix_level: float = 1.0,
        original_audio_mix_level: float = 0.5,
        subtitles_enabled: bool = True,
        subtitle_fontsize: int = 40,
        subtitle_fontcolor: str = "white",
        subtitle_font_path: Optional[str] = None,
        match_video_duration: bool = True,
    ) -> None:
        self.voiceover_enabled = enabled and bool(text.strip())
        self.voiceover_text = text.strip()
        self.voiceover_rate = max(-10, min(10, int(rate)))
        self.voiceover_volume = max(0, min(100, int(volume)))
        self.voiceover_voice_name = voice_name.strip() if voice_name else None
        self.voiceover_mix_level = max(0.1, float(mix_level))
        self.original_audio_mix_level = max(0.0, float(original_audio_mix_level))
        self.voiceover_subtitles_enabled = bool(subtitles_enabled)
        self.voiceover_subtitle_fontsize = max(18, int(subtitle_fontsize))
        self.voiceover_subtitle_fontcolor = subtitle_fontcolor or "white"
        self.voiceover_subtitle_font_path = subtitle_font_path
        self.match_video_to_voiceover = bool(match_video_duration)

    def set_external_voiceover_audio(self, audio_path: Optional[str]) -> None:
        path = (audio_path or "").strip()
        if not path:
            self.external_voiceover_audio_path = None
            return
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Voice-over audio file does not exist: {audio_path}")
        self.external_voiceover_audio_path = abs_path

    def enable_color_correction(
        self,
        brightness: float = 0,
        contrast: float = 1,
        saturation: float = 1,
        gamma: float = 1,
    ) -> None:
        self.color_correction_enabled = True
        self.brightness = brightness
        self.contrast = contrast
        self.saturation = saturation
        self.gamma = gamma

    @staticmethod
    def _escape_drawtext_text(text: str) -> str:
        return (
            text.replace("\\", "\\\\")
            .replace(":", r"\:")
            .replace("'", r"\'")
            .replace("%", r"\%")
            .replace(",", r"\,")
            .replace("[", r"\[")
            .replace("]", r"\]")
        )

    @staticmethod
    def _default_windows_fontfile() -> Optional[str]:
        windows_dir = os.environ.get("WINDIR", r"C:\Windows")
        candidates = [
            os.path.join(windows_dir, "Fonts", "msyh.ttc"),
            os.path.join(windows_dir, "Fonts", "msyhbd.ttc"),
            os.path.join(windows_dir, "Fonts", "simhei.ttf"),
            os.path.join(windows_dir, "Fonts", "simsun.ttc"),
            os.path.join(windows_dir, "Fonts", "arial.ttf"),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    @staticmethod
    def _split_text_segments(text: str) -> List[str]:
        normalized_text = (
            text.replace("\r", "\n")
            .replace("\u3002", "\n")
            .replace("\uff01", "\n")
            .replace("\uff1f", "\n")
            .replace("\uff1b", "\n")
            .replace("!", "\n")
            .replace("?", "\n")
            .replace(";", "\n")
        )
        segments = [part.strip() for part in re.split(r"\n+", normalized_text) if part.strip()]
        return segments if segments else [text.strip()]

    def _get_media_duration(self, file_path: str) -> float:
        cmd_format = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            file_path,
        ]
        result = subprocess.run(cmd_format, capture_output=True, text=True)
        raw = (result.stdout or "").strip()
        if result.returncode == 0:
            try:
                value = float(raw)
                if value > 0:
                    return value
            except (TypeError, ValueError):
                pass

        cmd_stream = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0,v:0",
            "-show_entries",
            "stream=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            file_path,
        ]
        stream_result = subprocess.run(cmd_stream, capture_output=True, text=True)
        if stream_result.returncode == 0:
            for line in (stream_result.stdout or "").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    value = float(line)
                    if value > 0:
                        return value
                except (TypeError, ValueError):
                    continue

        if file_path.lower().endswith(".wav"):
            try:
                with wave.open(file_path, "rb") as wav_file:
                    frame_rate = wav_file.getframerate()
                    frame_count = wav_file.getnframes()
                if frame_rate > 0 and frame_count > 0:
                    return frame_count / frame_rate
            except Exception:
                pass

        raise RuntimeError(f"Cannot get duration: {file_path} (ffprobe output: {raw or 'N/A'})")

    def _get_video_duration(self, file_path: str) -> float:
        return self._get_media_duration(file_path)

    def _get_clip_duration(self, clip: Dict[str, Any]) -> float:
        if clip.get("duration") is not None:
            return float(clip["duration"])
        return self._get_video_duration(clip["path"])

    def _estimate_duration_for_clips(self, clips: List[Dict[str, Any]]) -> float:
        total = 0.0
        for index, clip in enumerate(clips):
            total += self._get_clip_duration(clip)
            if index < len(clips) - 1:
                total -= float(clip.get("transition_duration", 1.0))
        return max(total, 0.0)

    def _fit_clips_to_target_duration(self, target_duration: float) -> None:
        if not self.clips or target_duration <= 0:
            return

        source_clips = [dict(clip) for clip in self.clips]
        fitted: List[Dict[str, Any]] = []
        current_duration = 0.0
        index = 0
        tolerance = 0.08
        max_iterations = max(20, len(source_clips) * 8)

        while current_duration < target_duration - tolerance and index < max_iterations:
            candidate = dict(source_clips[index % len(source_clips)])
            full_duration = self._get_clip_duration(candidate)
            if full_duration <= 0.25:
                index += 1
                continue

            if not fitted:
                max_clip_duration = target_duration - current_duration
            else:
                prev_transition = float(fitted[-1].get("transition_duration", 1.0))
                max_clip_duration = (target_duration - current_duration) + prev_transition

            chosen_duration = min(full_duration, max_clip_duration)
            if chosen_duration <= 0.25:
                break

            candidate["duration"] = round(chosen_duration, 3)
            fitted.append(candidate)
            current_duration = self._estimate_duration_for_clips(fitted)
            index += 1

        if fitted:
            overflow = current_duration - target_duration
            if overflow > tolerance:
                last = fitted[-1]
                last_duration = self._get_clip_duration(last)
                last["duration"] = round(max(0.25, last_duration - overflow), 3)
            self.clips = fitted

    def _build_voiceover_subtitle_overlays(self, total_duration: float) -> List[Dict[str, Any]]:
        if not self.voiceover_enabled or not self.voiceover_subtitles_enabled or not self.voiceover_text:
            return []

        segments = self._split_text_segments(self.voiceover_text)
        if not segments:
            return []

        overlays: List[Dict[str, Any]] = []
        total_chars = sum(len(part) for part in segments) or len(segments)
        cursor = 0.0

        for index, segment in enumerate(segments):
            remaining_duration = max(total_duration - cursor, 0.0)
            remaining_segments = len(segments) - index
            proportional_duration = total_duration * (len(segment) / total_chars) if total_duration > 0 else 0
            duration = max(1.8, proportional_duration)
            if remaining_segments == 1:
                duration = max(remaining_duration, 1.8)
            else:
                max_allowed = max(remaining_duration - 1.2 * (remaining_segments - 1), 1.8)
                duration = min(duration, max_allowed)

            overlays.append(
                {
                    "text": segment,
                    "start_time": round(cursor, 3),
                    "duration": round(duration, 3),
                    "x": "(w-text_w)/2",
                    "y": "h-text_h-80",
                    "fontsize": self.voiceover_subtitle_fontsize,
                    "fontcolor": self.voiceover_subtitle_fontcolor,
                    "font_path": self.voiceover_subtitle_font_path,
                }
            )
            cursor += duration
        return overlays

    def _build_text_filter(self, total_duration: float) -> str:
        overlays = list(self.text_overlays)
        overlays.extend(self._build_voiceover_subtitle_overlays(total_duration))
        if not overlays:
            return ""

        filters = []
        for overlay in overlays:
            text = self._escape_drawtext_text(overlay["text"])
            start = overlay["start_time"]
            end = start + overlay["duration"]
            font_path = overlay.get("font_path")
            if not font_path:
                font_path = self._default_windows_fontfile()
            if font_path:
                escaped_font_path = font_path.replace("\\", "/").replace(":", r"\:")
                font_expr = f"fontfile='{escaped_font_path}'"
            else:
                font_expr = ""
            filters.append(
                "drawtext="
                f"text='{text}':"
                f"{font_expr + ':' if font_expr else ''}"
                f"fontsize={overlay['fontsize']}:"
                f"fontcolor={overlay['fontcolor']}:"
                f"x={overlay['x']}:"
                f"y={overlay['y']}:"
                "box=1:"
                "boxcolor=black@0.45:"
                "boxborderw=12:"
                f"enable='between(t,{start},{end})'"
            )
        return ",".join(filters)

    def _build_color_correction_filter(self) -> str:
        if not self.color_correction_enabled:
            return ""
        filters = []
        if self.brightness != 0 or self.contrast != 1:
            filters.append(f"eq=brightness={self.brightness}:contrast={self.contrast}")
        if self.saturation != 1:
            filters.append(f"hue=s={self.saturation}")
        if self.gamma != 1:
            filters.append("curves=all='0/0 1/1':presets=none")
        return ",".join(filters)

    def generate_thumbnail(self, output_path: str = "thumbnail.jpg", timestamp: float | None = None, width: int = 320) -> bool:
        if not self.clips:
            return False
        try:
            first_clip = self.clips[0]["path"]
            if timestamp is None:
                timestamp = self._get_video_duration(first_clip) / 2
            cmd = ["ffmpeg", "-y", "-ss", str(timestamp), "-i", first_clip, "-vf", f"scale={width}:-1", "-vframes", "1", output_path]
            return subprocess.run(cmd, capture_output=True, text=True).returncode == 0
        except Exception:
            return False

    def _has_audio_stream(self, file_path: str) -> bool:
        cmd = ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0 and bool(result.stdout.strip())

    def _synthesize_voiceover(self, output_path: str) -> None:
        if not self.voiceover_enabled:
            raise RuntimeError("Voice-over is not enabled")
        if os.name != "nt":
            raise RuntimeError("Voice-over generation currently supports Windows only")
        synthesis_error: Optional[str] = None
        try:
            import win32com.client  # type: ignore

            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            if self.voiceover_voice_name:
                target = self.voiceover_voice_name.lower()
                for i in range(speaker.GetVoices().Count):
                    token = speaker.GetVoices().Item(i)
                    if target in token.GetDescription().lower():
                        speaker.Voice = token
                        break

            stream = win32com.client.Dispatch("SAPI.SpFileStream")
            SSFMCreateForWrite = 3
            stream.Open(str(output_path), SSFMCreateForWrite, False)
            speaker.AudioOutputStream = stream
            speaker.Rate = self.voiceover_rate
            speaker.Volume = self.voiceover_volume
            for segment in self._split_text_segments(self.voiceover_text):
                speaker.Speak(segment)
            stream.Close()
        except Exception as exc:
            synthesis_error = str(exc)
            escaped_output = output_path.replace("'", "''")
            escaped_text = self.voiceover_text.replace("'", "''")
            escaped_voice = (self.voiceover_voice_name or "").replace("'", "''")
            voice_select = f"$synth.SelectVoice('{escaped_voice}');" if self.voiceover_voice_name else ""
            script = (
                "Add-Type -AssemblyName System.Speech; "
                "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                f"{voice_select}"
                f"$synth.Rate = {self.voiceover_rate}; "
                f"$synth.Volume = {self.voiceover_volume}; "
                f"$synth.SetOutputToWaveFile('{escaped_output}'); "
                f"$synth.Speak('{escaped_text}'); "
                "$synth.Dispose();"
            )
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip() or "Failed to synthesize voice-over")

        if not os.path.exists(output_path) or os.path.getsize(output_path) <= 64:
            detail = f" ({synthesis_error})" if synthesis_error else ""
            raise RuntimeError(f"Failed to synthesize voice-over: output wav is empty{detail}")
        try:
            with wave.open(output_path, "rb") as wav_file:
                if wav_file.getnframes() <= 0:
                    raise RuntimeError("Failed to synthesize voice-over: wav has no audio frames")
        except wave.Error as exc:
            raise RuntimeError(f"Failed to synthesize voice-over: invalid wav ({exc})")

    def _apply_voiceover(self, source_video: str, output_path: str, voiceover_path: Optional[str] = None) -> bool:
        if voiceover_path is None:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_voiceover = os.path.join(temp_dir, "voiceover.wav")
                self._synthesize_voiceover(temp_voiceover)
                return self._apply_voiceover(source_video, output_path, temp_voiceover)

        cmd = ["ffmpeg", "-y", "-i", source_video, "-i", voiceover_path]
        if self._has_audio_stream(source_video):
            filter_complex = (
                f"[0:a]volume={self.original_audio_mix_level}[bg];"
                f"[1:a]volume={self.voiceover_mix_level}[vo];"
                "[bg][vo]amix=inputs=2:duration=first:dropout_transition=2[aout]"
            )
            cmd.extend(["-filter_complex", filter_complex, "-map", "0:v:0", "-map", "[aout]"])
        else:
            cmd.extend(["-map", "0:v:0", "-map", "1:a:0"])
        cmd.extend(["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", output_path])
        return subprocess.run(cmd, capture_output=False, text=True).returncode == 0

    def _build_filter_complex(self) -> str:
        if not self.clips:
            raise ValueError("No clips added")

        normalize_filters = []
        for index, clip in enumerate(self.clips):
            clip_duration = max(0.25, self._get_clip_duration(clip))
            normalize_filters.append(
                f"[{index}:v]trim=duration={clip_duration},setpts=PTS-STARTPTS,"
                f"scale={self.width}:{self.height},setsar=1,fps=30,format=yuv420p,settb=AVTB[v{index}]"
            )

        if len(self.clips) == 1:
            return f"{normalize_filters[0]};[v0]null[v]"

        filter_parts = list(normalize_filters)
        previous_label = "v0"
        accumulated_offset = 0.0
        for index in range(len(self.clips) - 1):
            current = self.clips[index]
            next_clip = self.clips[index + 1]
            clip_duration = self._get_clip_duration(current)
            next_duration = self._get_clip_duration(next_clip)
            transition = current.get("transition", "fade")
            transition_duration = float(current.get("transition_duration", 1.0))
            transition_duration = min(transition_duration, max(0.1, clip_duration - 0.05), max(0.1, next_duration - 0.05))
            next_label = f"v{index + 1}"
            output_label = "v" if index == len(self.clips) - 2 else f"vx{index}"

            if index == 0:
                accumulated_offset = max(0.0, clip_duration - transition_duration)
            else:
                accumulated_offset += max(0.0, clip_duration - transition_duration)

            filter_parts.append(
                f"[{previous_label}][{next_label}]xfade=transition={transition}:duration={transition_duration}:offset={accumulated_offset}[{output_label}]"
            )
            previous_label = output_label
        return "; ".join(filter_parts)

    def _build_concat_filter(self) -> str:
        filters = []
        for index, clip in enumerate(self.clips):
            clip_duration = max(0.25, self._get_clip_duration(clip))
            filters.append(
                f"[{index}:v]trim=duration={clip_duration},setpts=PTS-STARTPTS,"
                f"scale={self.width}:{self.height},setsar=1,fps=30,format=yuv420p,settb=AVTB[v{index}]"
            )
        video_inputs = "".join(f"[v{index}]" for index in range(len(self.clips)))
        filters.append(f"{video_inputs}concat=n={len(self.clips)}:v=1:a=0[v]")
        return "; ".join(filters)

    def _build_audio_filter(self) -> str:
        filters = []
        for index, clip in enumerate(self.clips):
            clip_duration = max(0.25, self._get_clip_duration(clip))
            filters.append(
                f"[{index}:a]atrim=duration={clip_duration},asetpts=PTS-STARTPTS,aresample=44100,"
                f"aformat=sample_fmts=fltp:channel_layouts=stereo[a{index}]"
            )

        audio_inputs = "".join(f"[a{index}]" for index in range(len(self.clips)))
        filters.append(f"{audio_inputs}concat=n={len(self.clips)}:v=0:a=1[a]")

        if self.audio_fade_in > 0 or self.audio_fade_out > 0:
            total_duration = self._get_output_duration_estimate()
            fade_parts = []
            if self.audio_fade_in > 0:
                fade_parts.append(f"afade=t=in:st=0:d={self.audio_fade_in}")
            if self.audio_fade_out > 0 and total_duration > self.audio_fade_out:
                fade_start = max(0, total_duration - self.audio_fade_out)
                fade_parts.append(f"afade=t=out:st={fade_start}:d={self.audio_fade_out}")
            if fade_parts:
                filters.append(f"[a]{','.join(fade_parts)}[afinal]")
            else:
                filters.append("[a]anull[afinal]")
        else:
            filters.append("[a]anull[afinal]")
        return "; ".join(filters)

    def _get_output_duration_estimate(self) -> float:
        return self._estimate_duration_for_clips(self.clips)

    def generate(self, transition_enabled: bool = True, audio_enabled: bool = True) -> bool:
        if not self.clips:
            print("No clips available")
            return False

        voiceover_dir: Optional[tempfile.TemporaryDirectory[str]] = None
        voiceover_path: Optional[str] = None
        try:
            final_output_path = self.output_path
            working_output_path = final_output_path

            if self.voiceover_enabled:
                base_name = Path(final_output_path)
                working_output_path = str(base_name.with_name(f"{base_name.stem}_base{base_name.suffix}"))
                if self.external_voiceover_audio_path:
                    voiceover_path = self.external_voiceover_audio_path
                else:
                    voiceover_dir = tempfile.TemporaryDirectory()
                    voiceover_path = os.path.join(voiceover_dir.name, "voiceover.wav")
                    self._synthesize_voiceover(voiceover_path)
                if self.match_video_to_voiceover:
                    self._fit_clips_to_target_duration(self._get_media_duration(voiceover_path))

            cmd = ["ffmpeg", "-y"]
            for clip in self.clips:
                cmd.extend(["-i", clip["path"]])

            if transition_enabled and len(self.clips) > 1:
                filter_complex = self._build_filter_complex()
            else:
                filter_complex = self._build_concat_filter()

            current_video_label = "v"
            text_filter = self._build_text_filter(self._get_output_duration_estimate())
            if text_filter:
                filter_complex += f";[{current_video_label}]{text_filter}[v_text]"
                current_video_label = "v_text"

            color_filter = self._build_color_correction_filter()
            if color_filter:
                filter_complex += f";[{current_video_label}]{color_filter}[v_color]"
                current_video_label = "v_color"

            if audio_enabled and len(self.clips) > 0:
                filter_complex = f"{filter_complex}; {self._build_audio_filter()}"

            cmd.extend(["-filter_complex", filter_complex, "-map", f"[{current_video_label}]"])
            if audio_enabled and len(self.clips) > 0:
                cmd.extend(["-map", "[afinal]", "-c:a", "aac", "-b:a", "128k"])
            else:
                cmd.extend(["-an"])
            cmd.extend(["-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", working_output_path])

            print(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=False, text=True)
            if result.returncode != 0:
                return False

            if self.voiceover_enabled:
                voiceover_ok = self._apply_voiceover(working_output_path, final_output_path, voiceover_path)
                try:
                    if os.path.exists(working_output_path):
                        os.remove(working_output_path)
                except OSError:
                    pass
                if not voiceover_ok:
                    return False
            return True
        except Exception as exc:
            print(f"[FAIL] {exc}")
            return False
        finally:
            if voiceover_dir is not None:
                voiceover_dir.cleanup()

    def save_config(self, config_path: str) -> None:
        config = {
            "resolution": self.resolution,
            "output_path": self.output_path,
            "clips": self.clips,
            "text_overlays": self.text_overlays,
            "audio_fade_in": self.audio_fade_in,
            "audio_fade_out": self.audio_fade_out,
            "voiceover": {
                "enabled": self.voiceover_enabled,
                "text": self.voiceover_text,
                "rate": self.voiceover_rate,
                "volume": self.voiceover_volume,
                "voice_name": self.voiceover_voice_name,
                "mix_level": self.voiceover_mix_level,
                "original_audio_mix_level": self.original_audio_mix_level,
                "subtitles_enabled": self.voiceover_subtitles_enabled,
                "subtitle_fontsize": self.voiceover_subtitle_fontsize,
                "subtitle_fontcolor": self.voiceover_subtitle_fontcolor,
                "subtitle_font_path": self.voiceover_subtitle_font_path,
                "match_video_duration": self.match_video_to_voiceover,
                "external_audio_path": self.external_voiceover_audio_path,
            },
            "color_correction": {
                "enabled": self.color_correction_enabled,
                "brightness": self.brightness,
                "contrast": self.contrast,
                "saturation": self.saturation,
                "gamma": self.gamma,
            },
        }
        with open(config_path, "w", encoding="utf-8") as handle:
            json.dump(config, handle, ensure_ascii=False, indent=2)

    @classmethod
    def load_config(cls, config_path: str) -> "VideoMixer":
        with open(config_path, "r", encoding="utf-8") as handle:
            config = json.load(handle)

        mixer = cls(config["output_path"], tuple(config["resolution"]))
        for clip in config["clips"]:
            mixer.add_clip(
                clip["path"],
                clip.get("duration"),
                clip.get("transition", "fade"),
                clip.get("transition_duration", 1.0),
            )

        for overlay in config.get("text_overlays", []):
            mixer.add_text_overlay(
                overlay["text"],
                overlay.get("start_time", 0),
                overlay.get("duration", 5),
                overlay.get("x", "center"),
                overlay.get("y", "center"),
                overlay.get("fontsize", 24),
                overlay.get("fontcolor", "white"),
                overlay.get("font_path"),
            )

        mixer.set_audio_fade(config.get("audio_fade_in", 0), config.get("audio_fade_out", 0))

        color = config.get("color_correction", {})
        if color.get("enabled"):
            mixer.enable_color_correction(
                color.get("brightness", 0),
                color.get("contrast", 1),
                color.get("saturation", 1),
                color.get("gamma", 1),
            )

        voiceover = config.get("voiceover", {})
        if voiceover.get("enabled"):
            mixer.set_voiceover(
                text=voiceover.get("text", ""),
                enabled=True,
                rate=voiceover.get("rate", 0),
                volume=voiceover.get("volume", 100),
                voice_name=voiceover.get("voice_name"),
                mix_level=voiceover.get("mix_level", 1.0),
                original_audio_mix_level=voiceover.get("original_audio_mix_level", 0.5),
                subtitles_enabled=voiceover.get("subtitles_enabled", True),
                subtitle_fontsize=voiceover.get("subtitle_fontsize", 40),
                subtitle_fontcolor=voiceover.get("subtitle_fontcolor", "white"),
                subtitle_font_path=voiceover.get("subtitle_font_path"),
                match_video_duration=voiceover.get("match_video_duration", True),
            )
            mixer.set_external_voiceover_audio(voiceover.get("external_audio_path"))

        return mixer


def print_help() -> None:
    print("Video Mixing Tool")
    print("Usage: python video_mixer.py help")
    print("Supported transitions:")
    for key, value in VideoMixer.TRANSITIONS.items():
        print(f"  - {key}: {value}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "help":
        print_help()
    else:
        print_help()
