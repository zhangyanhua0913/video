#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Video mixing utilities backed by ffmpeg/ffprobe."""

from __future__ import annotations

import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
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
    TEXT_STYLE_PRESETS: Dict[str, Dict[str, Any]] = {
        "default": {
            "box": 1,
            "boxcolor": "black@0.45",
            "boxborderw": 12,
            "borderw": 1,
            "bordercolor": "black@0.80",
            "shadowcolor": "black@0.45",
            "shadowx": 1,
            "shadowy": 1,
        },
        "subtitle": {
            "box": 1,
            "boxcolor": "black@0.72",
            "boxborderw": 14,
            "borderw": 2,
            "bordercolor": "black@0.92",
            "shadowcolor": "black@0.68",
            "shadowx": 2,
            "shadowy": 2,
            "fontcolor": "#FFE9A8",
        },
        "sticker": {
            "box": 1,
            "boxcolor": "white@0.22",
            "boxborderw": 22,
            "borderw": 2,
            "bordercolor": "white@0.90",
            "shadowcolor": "black@0.40",
            "shadowx": 1,
            "shadowy": 1,
        },
        "neon": {
            "box": 0,
            "borderw": 2,
            "bordercolor": "black@0.85",
            "shadowcolor": "cyan@0.45",
            "shadowx": 1,
            "shadowy": 1,
        },
        "karaoke": {
            "box": 1,
            "boxcolor": "black@0.68",
            "boxborderw": 18,
            "borderw": 1,
            "bordercolor": "black@0.85",
            "shadowcolor": "black@0.55",
            "shadowx": 1,
            "shadowy": 1,
        },
        "transparent_outline": {
            "box": 0,
            "borderw": 2,
            "bordercolor": "white@0.92",
            "shadowcolor": "black@0.32",
            "shadowx": 1,
            "shadowy": 1,
        },
        "transparent_neon": {
            "box": 0,
            "borderw": 1,
            "bordercolor": "black@0.78",
            "shadowcolor": "cyan@0.35",
            "shadowx": 1,
            "shadowy": 1,
        },
        "transparent_subtitle": {
            "box": 0,
            "borderw": 1,
            "bordercolor": "black@0.82",
            "shadowcolor": "black@0.40",
            "shadowx": 1,
            "shadowy": 1,
        },
        "promo_tag": {
            "box": 1,
            "boxcolor": "red@0.35",
            "boxborderw": 16,
            "borderw": 2,
            "bordercolor": "yellow@0.95",
            "shadowcolor": "black@0.40",
            "shadowx": 1,
            "shadowy": 1,
        },
        "brand_banner": {
            "box": 1,
            "boxcolor": "black@0.52",
            "boxborderw": 20,
            "borderw": 1,
            "bordercolor": "white@0.88",
            "shadowcolor": "black@0.45",
            "shadowx": 1,
            "shadowy": 1,
        },
        "news_flash": {
            "box": 1,
            "boxcolor": "blue@0.38",
            "boxborderw": 14,
            "borderw": 1,
            "bordercolor": "white@0.92",
            "shadowcolor": "black@0.36",
            "shadowx": 1,
            "shadowy": 1,
        },
        "luxury_minimal": {
            "box": 0,
            "borderw": 1,
            "bordercolor": "black@0.78",
            "shadowcolor": "black@0.28",
            "shadowx": 1,
            "shadowy": 1,
        },
        "yellow_black_bold": {
            "box": 0,
            "borderw": 8,
            "bordercolor": "black",
            "shadowx": 0,
            "shadowy": 0,
            "shadowcolor": "black@0.0",
            "fontcolor": "yellow",
        },
        "yellow_black_glow": {
            "box": 0,
            "borderw": 6,
            "bordercolor": "black",
            "shadowx": 1,
            "shadowy": 1,
            "shadowcolor": "orange@0.65",
            "fontcolor": "#FFD54A",
        },
        "yellow_orange_flash": {
            "box": 0,
            "borderw": 5,
            "bordercolor": "#2C1A00",
            "shadowx": 1,
            "shadowy": 1,
            "shadowcolor": "#FF8A00@0.55",
            "fontcolor": "#FFC61A",
        },
        "black_plate_yellow": {
            "box": 1,
            "boxcolor": "black@0.35",
            "boxborderw": 8,
            "borderw": 5,
            "bordercolor": "black",
            "shadowx": 0,
            "shadowy": 0,
            "shadowcolor": "black@0.0",
            "fontcolor": "#FFD54A",
        },
        "popup_zoom_gold": {
            "box": 0,
            "borderw": 7,
            "bordercolor": "#FFD54A",
            "shadowx": 2,
            "shadowy": 2,
            "shadowcolor": "#FF9F1C@0.72",
            "fontcolor": "#FFF8D9",
        },
        "popup_bounce_red": {
            "box": 0,
            "borderw": 7,
            "bordercolor": "#FFE066",
            "shadowx": 2,
            "shadowy": 2,
            "shadowcolor": "#FF5A1F@0.78",
            "fontcolor": "#FF3B30",
        },
        "popup_neon_flash": {
            "box": 0,
            "borderw": 6,
            "bordercolor": "#FF4FD8",
            "shadowx": 2,
            "shadowy": 2,
            "shadowcolor": "#22D3EE@0.85",
            "fontcolor": "#B8F6FF",
        },
        "popup_explosion": {
            "box": 0,
            "borderw": 8,
            "bordercolor": "#FF2D2D",
            "shadowx": 2,
            "shadowy": 2,
            "shadowcolor": "#FF7A00@0.88",
            "fontcolor": "#FFF7E8",
        },
        "popup_scale_purple": {
            "box": 0,
            "borderw": 6,
            "bordercolor": "#FDE2FF",
            "shadowx": 2,
            "shadowy": 2,
            "shadowcolor": "#F472B6@0.72",
            "fontcolor": "#9B5DE5",
        },
        "popup_shake_yellow": {
            "box": 0,
            "borderw": 7,
            "bordercolor": "black",
            "shadowx": 2,
            "shadowy": 2,
            "shadowcolor": "#FFB703@0.65",
            "fontcolor": "#FFD93D",
        },
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
        self.voiceover_subtitle_fontsize = 48
        self.voiceover_subtitle_fontcolor = "white"
        self.voiceover_subtitle_font_path: Optional[str] = None
        self.voiceover_subtitle_template = "subtitle"
        self.voiceover_subtitle_effect = "pop"
        self.voiceover_popup_template = "auto"
        self.voiceover_popup_enabled = True
        self.match_video_to_voiceover = True
        self.external_voiceover_audio_path: Optional[str] = None
        self.voiceover_matched_phrases: List[Dict[str, Any]] = []
        self.voiceover_word_timestamps: List[Dict[str, Any]] = []
        self.voiceover_popup_lead_time = 0.18
        self.voiceover_popup_min_duration = 0.55
        self.voiceover_popup_merge_gap = 0.10
        self.target_duration: Optional[float] = None
        self.background_music_tracks: List[str] = []
        self.background_music_volume: float = 0.45
        self.selected_background_music_path: Optional[str] = None
        self.last_error: Optional[str] = None

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
        template: str = "default",
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
                "template": (template or "default").strip().lower(),
            }
        )

    @classmethod
    def _resolve_text_style(cls, template: str | None) -> Dict[str, Any]:
        key = (template or "default").strip().lower()
        return dict(cls.TEXT_STYLE_PRESETS.get(key, cls.TEXT_STYLE_PRESETS["default"]))

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
        subtitle_fontsize: int = 48,
        subtitle_fontcolor: str = "white",
        subtitle_font_path: Optional[str] = None,
        subtitle_template: str = "subtitle",
        subtitle_effect: str = "pop",
        popup_template: str = "auto",
        popup_enabled: bool = True,
        match_video_duration: bool = True,
        matched_phrases: Optional[List[Dict[str, Any]]] = None,
        word_timestamps: Optional[List[Dict[str, Any]]] = None,
        popup_lead_time: float = 0.18,
        popup_min_duration: float = 0.55,
        popup_merge_gap: float = 0.10,
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
        self.voiceover_subtitle_template = (subtitle_template or "subtitle").strip().lower()
        self.voiceover_subtitle_effect = (subtitle_effect or "pop").strip().lower()
        self.voiceover_popup_template = (popup_template or "auto").strip().lower()
        self.voiceover_popup_enabled = bool(popup_enabled)
        self.match_video_to_voiceover = bool(match_video_duration)
        self.voiceover_matched_phrases = self._normalize_matched_phrases(matched_phrases)
        self.voiceover_word_timestamps = self._normalize_word_timestamps(word_timestamps)
        self.voiceover_popup_lead_time = max(0.0, float(popup_lead_time))
        self.voiceover_popup_min_duration = max(0.12, float(popup_min_duration))
        self.voiceover_popup_merge_gap = max(0.0, float(popup_merge_gap))

    @staticmethod
    def _normalize_matched_phrases(items: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        if not isinstance(items, list):
            return []
        normalized: List[Dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            text = str(item.get("text", "")).strip()
            start = item.get("start")
            end = item.get("end")
            if not text:
                continue
            if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
                continue
            speak_start = max(0.0, float(start))
            speak_end = max(speak_start, float(end))
            normalized.append(
                {
                    "text": text,
                    "speak_start": round(speak_start, 3),
                    "speak_end": round(speak_end, 3),
                }
            )
        normalized.sort(key=lambda x: (x["speak_start"], x["speak_end"], x["text"]))
        return normalized

    @staticmethod
    def _normalize_word_timestamps(items: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        if not isinstance(items, list):
            return []
        normalized: List[Dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            word = str(item.get("word", "")).strip()
            start = item.get("start_time")
            end = item.get("end_time")
            if not word:
                continue
            if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
                continue
            s = max(0.0, float(start))
            e = max(s, float(end))
            normalized.append({"word": word, "start_time": round(s, 3), "end_time": round(e, 3)})
        normalized.sort(key=lambda x: (x["start_time"], x["end_time"]))
        return normalized

    def _build_timed_subtitle_overlays_from_words(self) -> List[Dict[str, Any]]:
        words = self.voiceover_word_timestamps
        if not words:
            return []

        subtitle_y = "h*2/3-text_h/2+320"
        overlays: List[Dict[str, Any]] = []
        punct = {"，", "。", "！", "？", "；", "、", ",", ".", "!", "?", ";"}
        group_words: List[Dict[str, Any]] = []
        max_chars = 14
        max_span = 2.6

        def flush_group() -> None:
            nonlocal group_words, overlays
            if not group_words:
                return
            text = self._sanitize_subtitle_text("".join(str(w["word"]) for w in group_words))
            if not text:
                group_words = []
                return
            start = float(group_words[0]["start_time"])
            end = float(group_words[-1]["end_time"])
            duration = max(0.12, end - start)
            overlays.append(
                {
                    "text": text,
                    "start_time": round(start, 3),
                    "duration": round(duration, 3),
                    "x": "(w-text_w)/2",
                    "y": subtitle_y,
                    "fontsize": self.voiceover_subtitle_fontsize,
                    "fontcolor": self.voiceover_subtitle_fontcolor,
                    "font_path": self.voiceover_subtitle_font_path,
                    "template": self.voiceover_subtitle_template,
                    "effect": self.voiceover_subtitle_effect,
                }
            )
            group_words = []

        for item in words:
            group_words.append(item)
            text_now = "".join(str(w["word"]) for w in group_words)
            span = float(group_words[-1]["end_time"]) - float(group_words[0]["start_time"])
            is_break = str(item["word"]) in punct
            too_long = len(text_now) >= max_chars or span >= max_span
            if is_break or too_long:
                flush_group()
        flush_group()
        return overlays

    def _build_popup_phrase_timeline(self, total_duration: float) -> List[Dict[str, Any]]:
        if not self.voiceover_matched_phrases:
            return []
        lead_time = self.voiceover_popup_lead_time
        min_popup_duration = self.voiceover_popup_min_duration
        merge_gap = self.voiceover_popup_merge_gap
        max_end = max(total_duration, 0.0)

        base_items: List[Dict[str, Any]] = []
        for item in self.voiceover_matched_phrases:
            speak_start = float(item["speak_start"])
            speak_end = float(item["speak_end"])
            popup_start = max(0.0, speak_start - lead_time)
            popup_end = max(popup_start + min_popup_duration, speak_end)
            if max_end > 0:
                popup_start = min(popup_start, max_end)
                popup_end = min(max(popup_end, popup_start + 0.12), max_end)
            base_items.append(
                {
                    "text": item["text"],
                    "speak_start": round(speak_start, 3),
                    "speak_end": round(speak_end, 3),
                    "popup_start": round(popup_start, 3),
                    "popup_end": round(popup_end, 3),
                }
            )

        if not base_items:
            return []

        grouped: List[Dict[str, Any]] = []
        group_start = 0
        group_end = base_items[0]["popup_end"]
        group_id = 1
        for idx in range(1, len(base_items)):
            current = base_items[idx]
            if current["popup_start"] <= group_end + merge_gap:
                group_end = max(group_end, current["popup_end"])
            else:
                for fill_idx in range(group_start, idx):
                    filled = dict(base_items[fill_idx])
                    filled["popup_end"] = round(group_end, 3)
                    filled["group_id"] = group_id
                    grouped.append(filled)
                group_id += 1
                group_start = idx
                group_end = current["popup_end"]
        for fill_idx in range(group_start, len(base_items)):
            filled = dict(base_items[fill_idx])
            filled["popup_end"] = round(group_end, 3)
            filled["group_id"] = group_id
            grouped.append(filled)
        return grouped

    @staticmethod
    def _pick_popup_template(template_name: str) -> str:
        key = (template_name or "").strip().lower()
        return key if key.startswith("popup_") else "popup_bounce_red"

    @staticmethod
    def _pick_popup_effect(template_name: str) -> str:
        key = (template_name or "").strip().lower()
        mapping = {
            "popup_zoom_gold": "pop_bounce_y",
            "popup_bounce_red": "pop_bounce_y",
            "popup_neon_flash": "pop_float_y",
            "popup_explosion": "pop_bounce_y",
            "popup_scale_purple": "pop_float_y",
            "popup_shake_yellow": "pop_shake_x",
        }
        return mapping.get(key, "pop_bounce_y")

    def set_external_voiceover_audio(self, audio_path: Optional[str]) -> None:
        path = (audio_path or "").strip()
        if not path:
            self.external_voiceover_audio_path = None
            return
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Voice-over audio file does not exist: {audio_path}")
        self.external_voiceover_audio_path = abs_path

    def set_target_duration(self, target_duration: Optional[float]) -> None:
        if target_duration is None:
            self.target_duration = None
            return
        target = float(target_duration)
        self.target_duration = target if target > 0 else None

    def set_background_music(self, tracks: Optional[List[str]], volume: float = 0.45) -> None:
        normalized: List[str] = []
        for raw in tracks or []:
            path = str(raw or "").strip()
            if not path:
                continue
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                normalized.append(abs_path)
        self.background_music_tracks = normalized
        self.background_music_volume = max(0.0, min(float(volume), 2.0))
        self.selected_background_music_path = None

    def _pick_background_music(self) -> Optional[str]:
        if not self.background_music_tracks:
            return None
        available = [path for path in self.background_music_tracks if os.path.exists(path)]
        if not available:
            return None
        picked = random.choice(available)
        self.selected_background_music_path = picked
        return picked

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
            .replace("\n", r"\n")
            .replace(":", r"\:")
            .replace("'", r"\'")
            .replace("%", r"\%")
            .replace(",", r"\,")
            .replace("[", r"\[")
            .replace("]", r"\]")
        )

    @staticmethod
    def _char_width_units(text: str) -> int:
        units = 0
        for ch in text:
            if ch.isspace():
                units += 1
            elif ord(ch) > 127:
                units += 2
            else:
                units += 1
        return max(units, 1)

    def _wrap_line_by_units(self, text: str, max_units: int) -> List[str]:
        chunks: List[str] = []
        current = ""
        current_units = 0
        for ch in text:
            ch_units = 2 if ord(ch) > 127 else 1
            if current and current_units + ch_units > max_units:
                chunks.append(current)
                current = ch
                current_units = ch_units
            else:
                current += ch
                current_units += ch_units
        if current:
            chunks.append(current)
        return chunks if chunks else [text]

    def _split_overlay_if_too_long(self, overlay: Dict[str, Any], max_width_ratio: float = 0.86) -> List[Dict[str, Any]]:
        text = str(overlay.get("text", "") or "").strip()
        if not text:
            return [overlay]

        fontsize = max(10, int(overlay.get("fontsize", 24)))
        width_factor = 0.58
        max_width = max(120, int(self.width * max_width_ratio))
        max_units_per_pass = max(6, int(max_width / (fontsize * width_factor)))

        total_units = self._char_width_units(text)
        if total_units <= max_units_per_pass:
            return [overlay]

        # Keep the same font size. For long text, split into two sequential passes.
        target_units_first = max_units_per_pass
        units = 0
        cut_index = len(text)
        for idx, ch in enumerate(text):
            units += 2 if ord(ch) > 127 else 1
            if units >= target_units_first:
                cut_index = idx + 1
                break

        first_text = text[:cut_index].strip()
        second_text = text[cut_index:].strip()
        if not first_text or not second_text:
            return [overlay]

        start = float(overlay.get("start_time", 0))
        duration = max(0.2, float(overlay.get("duration", 5)))
        first_duration = duration * 0.5
        second_duration = duration - first_duration

        first = dict(overlay)
        first["text"] = first_text
        first["start_time"] = start
        first["duration"] = first_duration

        second = dict(overlay)
        second["text"] = second_text
        second["start_time"] = start + first_duration
        second["duration"] = second_duration
        return [first, second]

    @staticmethod
    def _expand_overlay_effect(overlay: Dict[str, Any]) -> List[Dict[str, Any]]:
        effect = str(overlay.get("effect", "") or "").strip().lower()
        if not effect.startswith("pop"):
            return [overlay]
        # Keep a fixed font size for the whole popup lifecycle.
        normalized = dict(overlay)
        if effect == "pop":
            normalized["effect"] = "none"
        elif effect.startswith("pop_"):
            normalized["effect"] = effect[len("pop_") :]
        return [normalized]

    @staticmethod
    def _resolve_binary(binary_name: str) -> str:
        exe_name = f"{binary_name}.exe" if os.name == "nt" else binary_name
        candidate_paths = [
            os.path.join(os.getcwd(), "tools", "ffmpeg", "bin", exe_name),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools", "ffmpeg", "bin", exe_name),
        ]
        for candidate in candidate_paths:
            if os.path.exists(candidate):
                return candidate

        found = shutil.which(binary_name) or shutil.which(exe_name)
        return found or binary_name

    @classmethod
    def _ffmpeg_binary(cls) -> str:
        return cls._resolve_binary("ffmpeg")

    @classmethod
    def _ffprobe_binary(cls) -> str:
        return cls._resolve_binary("ffprobe")

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
        if not text:
            return []

        normalized = str(text).replace("\r\n", "\n").replace("\r", "\n")
        parts = re.split(r"[，。！？；：,.!?;:\n]+", normalized)
        segments: List[str] = []
        for part in parts:
            cleaned = re.sub(r"\s+", " ", part).strip()
            if cleaned:
                segments.append(cleaned)
        return segments

    @staticmethod
    def _sanitize_subtitle_text(text: str) -> str:
        if not text:
            return ""
        replaced = re.sub(r"[，。！？；：、,.!?;:()\[\]{}\"'“”‘’]", " ", text)
        return re.sub(r"\s+", " ", replaced).strip()

    def _get_media_duration(self, file_path: str) -> float:
        cmd_format = [
            self._ffprobe_binary(),
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
            self._ffprobe_binary(),
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

        timed_overlays = self._build_timed_subtitle_overlays_from_words()
        overlays: List[Dict[str, Any]] = timed_overlays

        segments = self._split_text_segments(self.voiceover_text)
        if not segments and not overlays:
            return []

        # Fallback only when no API timestamp words are available.
        if not overlays and segments:
            subtitle_y = "h*2/3-text_h/2+320"
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
                        "text": self._sanitize_subtitle_text(segment),
                        "start_time": round(cursor, 3),
                        "duration": round(duration, 3),
                        "x": "(w-text_w)/2",
                        "y": subtitle_y,
                        "fontsize": self.voiceover_subtitle_fontsize,
                        "fontcolor": self.voiceover_subtitle_fontcolor,
                        "font_path": self.voiceover_subtitle_font_path,
                        "template": self.voiceover_subtitle_template,
                        "effect": self.voiceover_subtitle_effect,
                    }
                )
                cursor += duration

        # Keep the original subtitle burn-in, and add an extra popup layer on top.
        popup_timeline = self._build_popup_phrase_timeline(total_duration)
        if self.voiceover_popup_enabled and popup_timeline:
            configured_popup_template = (self.voiceover_popup_template or "auto").strip().lower()
            popup_template = (
                configured_popup_template
                if configured_popup_template.startswith("popup_")
                else self._pick_popup_template(self.voiceover_subtitle_template)
            )
            popup_effect = self._pick_popup_effect(popup_template)
            popup_fontsize = max(18, int(self.voiceover_subtitle_fontsize))
            for item in popup_timeline:
                popup_start = float(item["popup_start"])
                popup_end = float(item["popup_end"])
                duration = max(0.16, popup_end - popup_start)
                overlays.append(
                    {
                        "text": str(item["text"]),
                        "start_time": round(popup_start, 3),
                        "duration": round(duration, 3),
                        "x": "(w-text_w)/2",
                        "y": "h*0.12",
                        "fontsize": popup_fontsize,
                        "fontcolor": self.voiceover_subtitle_fontcolor,
                        "font_path": self.voiceover_subtitle_font_path,
                        "template": popup_template,
                        "effect": popup_effect,
                        # Stable, fixed timeline format for downstream debugging/export.
                        "timed_phrase": {
                            "text": str(item["text"]),
                            "speak_start": float(item["speak_start"]),
                            "speak_end": float(item["speak_end"]),
                            "popup_start": popup_start,
                            "popup_end": popup_end,
                            "group_id": int(item["group_id"]),
                        },
                    }
                )
        return overlays

    def _build_text_filter(self, total_duration: float) -> str:
        overlays = list(self.text_overlays)
        overlays.extend(self._build_voiceover_subtitle_overlays(total_duration))
        if not overlays:
            return ""

        effective_overlays: List[Dict[str, Any]] = []
        for overlay in overlays:
            split_items = self._split_overlay_if_too_long(overlay, max_width_ratio=0.86)
            for item in split_items:
                effective_overlays.extend(self._expand_overlay_effect(item))

        filters = []
        for overlay in effective_overlays:
            text = self._escape_drawtext_text(overlay["text"])
            start = overlay["start_time"]
            end = start + overlay["duration"]
            # Use [start, end) to prevent two overlays sharing the boundary frame.
            enable_expr = f"gte(t,{start})*lt(t,{end})"
            effect_name = str(overlay.get("effect", "") or "").strip().lower()
            base_x = str(overlay.get("x", "(w-text_w)/2"))
            base_y = str(overlay.get("y", "h-text_h-90"))
            x_expr = base_x
            y_expr = base_y
            if effect_name in {"bounce", "bounce_y"}:
                y_expr = f"({base_y})-abs(sin((t-{start})*9))*20"
            elif effect_name in {"float", "float_y"}:
                y_expr = f"({base_y})+sin((t-{start})*5)*10"
            elif effect_name in {"shake", "shake_x"}:
                x_expr = f"({base_x})+sin((t-{start})*36)*7"
            elif effect_name in {"bounce_shake", "shake_bounce"}:
                y_expr = f"({base_y})-abs(sin((t-{start})*8))*16"
                x_expr = f"({base_x})+sin((t-{start})*30)*5"
            font_path = overlay.get("font_path")
            if not font_path:
                font_path = self._default_windows_fontfile()
            if font_path:
                escaped_font_path = font_path.replace("\\", "/").replace(":", r"\:")
                font_expr = f"fontfile='{escaped_font_path}'"
            else:
                font_expr = ""
            style = self._resolve_text_style(overlay.get("template"))
            template_name = str(overlay.get("template") or "").strip().lower()
            resolved_fontcolor = str(style.get("fontcolor") or overlay["fontcolor"])
            box = 1 if style.get("box", 0) else 0
            borderw = int(style.get("borderw", 0))
            shadowx = int(style.get("shadowx", 0))
            shadowy = int(style.get("shadowy", 0))
            style_parts: List[str] = [f"box={box}"]
            if box:
                style_parts.append(f"boxcolor={style.get('boxcolor', 'black@0.45')}")
                style_parts.append(f"boxborderw={int(style.get('boxborderw', 12))}")
            if borderw > 0:
                style_parts.append(f"borderw={borderw}")
                style_parts.append(f"bordercolor={style.get('bordercolor', 'black@0.9')}")
            if shadowx or shadowy:
                style_parts.append(f"shadowx={shadowx}")
                style_parts.append(f"shadowy={shadowy}")
                style_parts.append(f"shadowcolor={style.get('shadowcolor', 'black@0.65')}")
            if template_name == "yellow_black_bold":
                filters.append(
                    "drawtext="
                    f"text='{text}':"
                    f"{font_expr + ':' if font_expr else ''}"
                    f"fontsize={overlay['fontsize']}:"
                    "fontcolor=yellow:"
                    f"x={x_expr}:"
                    f"y={y_expr}:"
                    "box=0:"
                    "borderw=6:"
                    "bordercolor=black:"
                    "shadowx=0:"
                    "shadowy=0:"
                    "fix_bounds=1:"
                    f"enable='{enable_expr}'"
                )
            else:
                filters.append(
                    "drawtext="
                    f"text='{text}':"
                    f"{font_expr + ':' if font_expr else ''}"
                    f"fontsize={overlay['fontsize']}:"
                    f"fontcolor={resolved_fontcolor}:"
                    f"x={x_expr}:"
                    f"y={y_expr}:"
                    f"{':'.join(style_parts)}:"
                    "fix_bounds=1:"
                    f"enable='{enable_expr}'"
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
            cmd = [self._ffmpeg_binary(), "-y", "-ss", str(timestamp), "-i", first_clip, "-vf", f"scale={width}:-1", "-vframes", "1", output_path]
            return subprocess.run(cmd, capture_output=True, text=True).returncode == 0
        except Exception:
            return False

    def _has_audio_stream(self, file_path: str) -> bool:
        cmd = [self._ffprobe_binary(), "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0 and bool(result.stdout.strip())

    def _synthesize_voiceover(self, output_path: str) -> None:
        if not self.voiceover_enabled:
            raise RuntimeError("Voice-over is not enabled")
        self._call_coze_before_voiceover(output_path)
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

    def _call_coze_before_voiceover(self, output_path: str) -> None:
        input_text = (self.voiceover_text or "").strip()
        if not input_text:
            print("[Coze API] Empty voice-over text, skipping Coze API request.")
            return

        coze_api_url = "https://api.coze.cn/v1/workflow/run"
        headers = {
            "Authorization": "Bearer sat_1ioklBC8oH3qXf4EcZzqipjgwFRVuDXP2sAyUREK4rt27S7RyPd1PsDk2hmKSogJ",
            "Content-Type": "application/json",
        }
        payload = {
            "workflow_id": "7621492603993276454",
            "parameters": {"input": input_text},
        }

        print("[Coze API] Starting Coze API request...")
        try:
            import requests

            print(f"[Coze API] Requesting with input: {input_text[:50]}...")
            response = requests.post(coze_api_url, headers=headers, json=payload, timeout=3)
            print(f"[Coze API] Response status: {response.status_code}")
            response_data = response.json()

            if response_data.get("code") != 0:
                print(f"[Coze API] API returned error: {response_data.get('msg', 'Unknown error')}")
                return

            data_content = response_data.get("data")
            if not isinstance(data_content, str):
                print(f"[Coze API] Invalid data format: {type(data_content)}")
                return

            data_json = json.loads(data_content)
            arr_data = data_json.get("arr", [])
            print(f"[Coze API] Extracted arr: {arr_data}")

            formatted_data: List[Dict[str, Any]] = []
            current_time = 0.0
            for item in arr_data:
                if isinstance(item, dict):
                    text = str(item.get("text", ""))
                    duration = float(item.get("duration", 0.3))
                    formatted_data.append(
                        {
                            "text": text,
                            "start": round(current_time, 1),
                            "end": round(current_time + duration, 1),
                        }
                    )
                    current_time += duration
                elif isinstance(item, str):
                    for char in item:
                        formatted_data.append(
                            {
                                "text": char,
                                "start": round(current_time, 1),
                                "end": round(current_time + 0.3, 1),
                            }
                        )
                        current_time += 0.3

            save_dir = os.path.join(os.path.dirname(output_path), "coze_data")
            os.makedirs(save_dir, exist_ok=True)
            timestamp = int(time.time())

            arr_save_path = os.path.join(save_dir, f"coze_arr_{timestamp}.json")
            with open(arr_save_path, "w", encoding="utf-8") as handle:
                json.dump(arr_data, handle, ensure_ascii=False, indent=2)
            print(f"[Coze API] arr saved to: {arr_save_path}")

            formatted_save_path = os.path.join(save_dir, f"coze_formatted_{timestamp}.json")
            with open(formatted_save_path, "w", encoding="utf-8") as handle:
                json.dump(formatted_data, handle, ensure_ascii=False, indent=2)
            print(f"[Coze API] Formatted data saved to: {formatted_save_path}")
        except Exception as exc:
            print(f"[Coze API] Request failed: {exc}")
            print("[Coze API] Skipping Coze API processing, continuing with audio generation")

    def _apply_voiceover(
        self,
        source_video: str,
        output_path: str,
        voiceover_path: Optional[str] = None,
        background_music_path: Optional[str] = None,
        background_music_volume: float = 0.45,
    ) -> bool:
        if voiceover_path is None:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_voiceover = os.path.join(temp_dir, "voiceover.wav")
                self._synthesize_voiceover(temp_voiceover)
                return self._apply_voiceover(source_video, output_path, temp_voiceover)

        cmd = [self._ffmpeg_binary(), "-y", "-i", source_video, "-i", voiceover_path]
        bgm_enabled = bool(background_music_path and os.path.exists(background_music_path))
        if bgm_enabled:
            cmd.extend(["-stream_loop", "-1", "-i", str(background_music_path)])

        voice_duration = max(0.1, self._get_media_duration(voiceover_path))
        safe_bgm_volume = max(0.0, min(float(background_music_volume), 2.0))
        # Keep BGM clearly under the voice-over loudness when narration exists.
        safe_bgm_volume = min(safe_bgm_volume, max(0.0, float(self.voiceover_mix_level)) * 0.80)
        if self._has_audio_stream(source_video):
            if bgm_enabled:
                filter_complex = (
                    f"[0:a]volume={self.original_audio_mix_level}[bg];"
                    f"[1:a]volume={self.voiceover_mix_level}[vo];"
                    f"[2:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,"
                    f"atrim=duration={voice_duration},asetpts=PTS-STARTPTS,volume={safe_bgm_volume}[bgm];"
                    "[bg][vo][bgm]amix=inputs=3:duration=first:dropout_transition=2[aout]"
                )
            else:
                filter_complex = (
                    f"[0:a]volume={self.original_audio_mix_level}[bg];"
                    f"[1:a]volume={self.voiceover_mix_level}[vo];"
                    "[bg][vo]amix=inputs=2:duration=first:dropout_transition=2[aout]"
                )
            cmd.extend(["-filter_complex", filter_complex, "-map", "0:v:0", "-map", "[aout]"])
        else:
            if bgm_enabled:
                filter_complex = (
                    f"[1:a]volume={self.voiceover_mix_level}[vo];"
                    f"[2:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,"
                    f"atrim=duration={voice_duration},asetpts=PTS-STARTPTS,volume={safe_bgm_volume}[bgm];"
                    "[vo][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
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
                f"scale={self.width}:{self.height}:force_original_aspect_ratio=decrease,"
                f"pad={self.width}:{self.height}:(ow-iw)/2:(oh-ih)/2:color=black,"
                f"setsar=1,fps=30,format=yuv420p,settb=AVTB[v{index}]"
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
                f"scale={self.width}:{self.height}:force_original_aspect_ratio=decrease,"
                f"pad={self.width}:{self.height}:(ow-iw)/2:(oh-ih)/2:color=black,"
                f"setsar=1,fps=30,format=yuv420p,settb=AVTB[v{index}]"
            )
        video_inputs = "".join(f"[v{index}]" for index in range(len(self.clips)))
        filters.append(f"{video_inputs}concat=n={len(self.clips)}:v=1:a=0[v]")
        return "; ".join(filters)

    def _build_audio_filter(self, bgm_input_index: Optional[int] = None, bgm_volume: float = 0.45) -> str:
        filters = []
        for index, clip in enumerate(self.clips):
            clip_duration = max(0.25, self._get_clip_duration(clip))
            filters.append(
                f"[{index}:a]atrim=duration={clip_duration},asetpts=PTS-STARTPTS,aresample=44100,"
                f"aformat=sample_fmts=fltp:channel_layouts=stereo[a{index}]"
            )

        audio_inputs = "".join(f"[a{index}]" for index in range(len(self.clips)))
        filters.append(f"{audio_inputs}concat=n={len(self.clips)}:v=0:a=1[a]")
        active_audio = "a"

        if bgm_input_index is not None:
            total_duration = max(0.1, self._get_output_duration_estimate())
            safe_bgm_volume = max(0.0, min(float(bgm_volume), 2.0))
            filters.append(
                f"[{bgm_input_index}:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,"
                f"atrim=duration={total_duration},asetpts=PTS-STARTPTS,volume={safe_bgm_volume}[bgm]"
            )
            filters.append("[a][bgm]amix=inputs=2:duration=first:dropout_transition=2[a_mix]")
            active_audio = "a_mix"

        if self.audio_fade_in > 0 or self.audio_fade_out > 0:
            total_duration = self._get_output_duration_estimate()
            fade_parts = []
            if self.audio_fade_in > 0:
                fade_parts.append(f"afade=t=in:st=0:d={self.audio_fade_in}")
            if self.audio_fade_out > 0 and total_duration > self.audio_fade_out:
                fade_start = max(0, total_duration - self.audio_fade_out)
                fade_parts.append(f"afade=t=out:st={fade_start}:d={self.audio_fade_out}")
            if fade_parts:
                filters.append(f"[{active_audio}]{','.join(fade_parts)}[afinal]")
            else:
                filters.append(f"[{active_audio}]anull[afinal]")
        else:
            filters.append(f"[{active_audio}]anull[afinal]")
        return "; ".join(filters)

    def _get_output_duration_estimate(self) -> float:
        return self._estimate_duration_for_clips(self.clips)

    def generate(self, transition_enabled: bool = True, audio_enabled: bool = True) -> bool:
        self.last_error = None
        if not self.clips:
            print("No clips available")
            self.last_error = "No clips available"
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
            elif self.target_duration:
                self._fit_clips_to_target_duration(self.target_duration)

            cmd = [self._ffmpeg_binary(), "-y"]
            for clip in self.clips:
                cmd.extend(["-i", clip["path"]])
            selected_bgm = self._pick_background_music()
            bgm_input_index: Optional[int] = None
            if selected_bgm and (not self.voiceover_enabled):
                cmd.extend(["-stream_loop", "-1", "-i", selected_bgm])
                bgm_input_index = len(self.clips)

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
                filter_complex = f"{filter_complex}; {self._build_audio_filter(bgm_input_index, self.background_music_volume)}"

            cmd.extend(["-filter_complex", filter_complex, "-map", f"[{current_video_label}]"])
            if audio_enabled and len(self.clips) > 0:
                cmd.extend(["-map", "[afinal]", "-c:a", "aac", "-b:a", "128k"])
            else:
                cmd.extend(["-an"])
            cmd.extend(["-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", working_output_path])

            print(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=False, text=True)
            if result.returncode != 0:
                self.last_error = f"ffmpeg failed with exit code {result.returncode}"
                return False

            if self.voiceover_enabled:
                voiceover_ok = self._apply_voiceover(
                    working_output_path,
                    final_output_path,
                    voiceover_path,
                    background_music_path=selected_bgm,
                    background_music_volume=self.background_music_volume,
                )
                try:
                    if os.path.exists(working_output_path):
                        os.remove(working_output_path)
                except OSError:
                    pass
                if not voiceover_ok:
                    self.last_error = self.last_error or "Failed to apply voice-over audio/subtitles"
                    return False
            return True
        except Exception as exc:
            print(f"[FAIL] {exc}")
            self.last_error = str(exc)
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
                "subtitle_template": self.voiceover_subtitle_template,
                "popup_enabled": self.voiceover_popup_enabled,
                "popup_template": self.voiceover_popup_template,
                "match_video_duration": self.match_video_to_voiceover,
                "external_audio_path": self.external_voiceover_audio_path,
                "matched_phrases": self.voiceover_matched_phrases,
                "word_timestamps": self.voiceover_word_timestamps,
                "popup_lead_time": self.voiceover_popup_lead_time,
                "popup_min_duration": self.voiceover_popup_min_duration,
                "popup_merge_gap": self.voiceover_popup_merge_gap,
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
                overlay.get("template", "default"),
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
                subtitle_fontsize=voiceover.get("subtitle_fontsize", 48),
                subtitle_fontcolor=voiceover.get("subtitle_fontcolor", "white"),
                subtitle_font_path=voiceover.get("subtitle_font_path"),
                subtitle_template=voiceover.get("subtitle_template", "subtitle"),
                popup_enabled=voiceover.get("popup_enabled", True),
                popup_template=voiceover.get("popup_template", "auto"),
                match_video_duration=voiceover.get("match_video_duration", True),
                matched_phrases=voiceover.get("matched_phrases"),
                word_timestamps=voiceover.get("word_timestamps"),
                popup_lead_time=voiceover.get("popup_lead_time", 0.18),
                popup_min_duration=voiceover.get("popup_min_duration", 0.55),
                popup_merge_gap=voiceover.get("popup_merge_gap", 0.10),
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


