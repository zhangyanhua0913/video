#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command handler for the local video-mixer skill runtime.
"""

from __future__ import annotations

import json
import os
import random
import sys
from dataclasses import dataclass
from typing import Any, Dict

try:
    from video_mixer import VideoMixer
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from video_mixer import VideoMixer


@dataclass
class SkillResponse:
    success: bool = True
    message: str = ""
    output: Any = None
    error: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "output": self.output,
            "error": self.error,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class VideoMixerSkillHandler:
    """High-level command router for the local video mixer."""

    TRANSITIONS = {
        "fade": "Fade in/out",
        "wipeleft": "Wipe from left to right",
        "wiperight": "Wipe from right to left",
        "zoomin": "Zoom in",
        "circleopen": "Circle open",
        "pixelize": "Pixelize",
    }

    def __init__(self) -> None:
        self.mixer: VideoMixer | None = None

    def handle_mix(self, params: Dict[str, Any]) -> SkillResponse:
        if "output" not in params:
            return SkillResponse(False, "Missing required parameter: output", error="Missing parameter: output")
        if "clips" not in params or not params["clips"]:
            return SkillResponse(False, "Missing required parameter: clips", error="Missing parameter: clips")

        try:
            output_path = params["output"]
            clips = list(params["clips"])
            resolution = tuple(params.get("resolution", [1920, 1080]))

            if params.get("randomizeOrder"):
                rng = random.Random(params.get("randomSeed"))
                rng.shuffle(clips)

            self.mixer = VideoMixer(output_path=output_path, resolution=resolution)

            for clip in clips:
                if "path" not in clip:
                    return SkillResponse(False, "Each clip must include a path.", error="Missing clip path")

                self.mixer.add_clip(
                    clip["path"],
                    duration=clip.get("duration"),
                    transition=clip.get("transition", "fade"),
                    transition_duration=clip.get("transitionDuration", 1.0),
                )

            target_duration = params.get("targetDuration")
            if target_duration is not None:
                self.mixer.set_target_duration(target_duration)

            background_music = params.get("backgroundMusic")
            if isinstance(background_music, dict):
                self.mixer.set_background_music(
                    tracks=background_music.get("tracks"),
                    volume=background_music.get("volume", 0.35),
                )

            for overlay in params.get("textOverlays", []) or []:
                self.mixer.add_text_overlay(
                    overlay.get("text", ""),
                    start_time=overlay.get("startTime", 0),
                    duration=overlay.get("duration", 5),
                    x=overlay.get("x", "center"),
                    y=overlay.get("y", "center"),
                    fontsize=overlay.get("fontsize", 24),
                    fontcolor=overlay.get("fontcolor", "white"),
                    font_path=overlay.get("fontPath"),
                    template=overlay.get("template", "default"),
                )

            audio_fade_in = params.get("audioFadeIn", 0)
            audio_fade_out = params.get("audioFadeOut", 0)
            if audio_fade_in > 0 or audio_fade_out > 0:
                self.mixer.set_audio_fade(fade_in=audio_fade_in, fade_out=audio_fade_out)

            color_correction = params.get("colorCorrection")
            if color_correction and color_correction.get("enabled"):
                self.mixer.enable_color_correction(
                    brightness=color_correction.get("brightness", 0),
                    contrast=color_correction.get("contrast", 1),
                    saturation=color_correction.get("saturation", 1),
                    gamma=color_correction.get("gamma", 1),
                )

            voiceover = params.get("voiceover")
            if voiceover and voiceover.get("enabled"):
                voiceover_text = voiceover.get("text", "").strip()
                if not voiceover_text:
                    return SkillResponse(False, "Voice-over is enabled but no text was provided.", error="Missing voice-over text")

                self.mixer.set_voiceover(
                    text=voiceover_text,
                    enabled=True,
                    rate=voiceover.get("rate", 0),
                    volume=voiceover.get("volume", 100),
                    voice_name=voiceover.get("voiceName"),
                    mix_level=voiceover.get("mixLevel", 1.0),
                    original_audio_mix_level=voiceover.get("originalAudioMixLevel", 0.5),
                    subtitles_enabled=voiceover.get("subtitlesEnabled", True),
                    subtitle_fontsize=voiceover.get("subtitleFontsize", 40),
                    subtitle_fontcolor=voiceover.get("subtitleFontcolor", "white"),
                    subtitle_font_path=voiceover.get("subtitleFontPath"),
                    subtitle_template=voiceover.get("subtitleTemplate", "subtitle"),
                    subtitle_effect=voiceover.get("subtitleEffect", "pop"),
                    popup_template=voiceover.get("popupTemplate", "auto"),
                    match_video_duration=voiceover.get("matchVideoDuration", True),
                    matched_phrases=voiceover.get("matchedKeyPhrases"),
                    word_timestamps=voiceover.get("timestampWords"),
                    popup_lead_time=voiceover.get("popupLeadTime", 0.18),
                    popup_min_duration=voiceover.get("popupMinDuration", 0.55),
                    popup_merge_gap=voiceover.get("popupMergeGap", 0.10),
                )
                self.mixer.set_external_voiceover_audio(voiceover.get("audioPath"))

            success = self.mixer.generate(
                transition_enabled=params.get("transitionEnabled", True),
                audio_enabled=params.get("audioEnabled", True),
            )

            if success:
                return SkillResponse(
                    True,
                    f"Video mix completed: {output_path}",
                    output={
                        "path": output_path,
                        "clipOrder": [clip["path"] for clip in clips],
                        "randomizedOrder": bool(params.get("randomizeOrder")),
                        "voiceoverEnabled": bool(voiceover and voiceover.get("enabled")),
                        "backgroundMusic": getattr(self.mixer, "selected_background_music_path", None),
                    },
                )

            detail_error = getattr(self.mixer, "last_error", None) or "Failed to generate video"
            return SkillResponse(False, f"Failed to generate the mixed video: {detail_error}", error=detail_error)
        except Exception as exc:
            return SkillResponse(False, f"Processing failed: {exc}", error=str(exc))

    def handle_thumbnail(self, params: Dict[str, Any]) -> SkillResponse:
        if "videoPath" not in params:
            return SkillResponse(False, "Missing parameter: videoPath", error="Missing parameter: videoPath")
        if "output" not in params:
            return SkillResponse(False, "Missing parameter: output", error="Missing parameter: output")

        try:
            video_path = params["videoPath"]
            output_path = params["output"]
            timestamp = params.get("timestamp")
            width = params.get("width", 320)

            mixer = VideoMixer(output_path=output_path)
            mixer.add_clip(video_path)
            success = mixer.generate_thumbnail(
                output_path=output_path,
                timestamp=timestamp,
                width=width,
            )

            if success:
                return SkillResponse(True, f"Thumbnail generated: {output_path}", output=output_path)

            return SkillResponse(False, "Failed to generate the thumbnail.", error="Failed to generate thumbnail")
        except Exception as exc:
            return SkillResponse(False, f"Processing failed: {exc}", error=str(exc))

    def handle_save_config(self, params: Dict[str, Any]) -> SkillResponse:
        if "config" not in params:
            return SkillResponse(False, "Missing parameter: config", error="Missing parameter: config")
        if "output" not in params:
            return SkillResponse(False, "Missing parameter: output", error="Missing parameter: output")

        try:
            with open(params["output"], "w", encoding="utf-8") as handle:
                json.dump(params["config"], handle, ensure_ascii=False, indent=2)
            return SkillResponse(True, f"Config saved: {params['output']}", output=params["output"])
        except Exception as exc:
            return SkillResponse(False, f"Processing failed: {exc}", error=str(exc))

    def handle_load_config(self, params: Dict[str, Any]) -> SkillResponse:
        if "configPath" not in params:
            return SkillResponse(False, "Missing parameter: configPath", error="Missing parameter: configPath")

        config_path = params["configPath"]
        if not os.path.exists(config_path):
            return SkillResponse(False, f"Config file not found: {config_path}", error="Config file not found")

        try:
            with open(config_path, "r", encoding="utf-8") as handle:
                config = json.load(handle)
            return SkillResponse(True, "Config loaded successfully.", output=config)
        except Exception as exc:
            return SkillResponse(False, f"Processing failed: {exc}", error=str(exc))

    def handle_list_transitions(self, params: Dict[str, Any]) -> SkillResponse:
        del params
        transitions = [{"name": name, "description": description} for name, description in self.TRANSITIONS.items()]
        return SkillResponse(True, "Transition list loaded successfully.", output=transitions)

    def process(self, command: str, params: Dict[str, Any]) -> SkillResponse:
        command_lower = command.lower()
        if command_lower == "mix":
            return self.handle_mix(params)
        if command_lower == "thumbnail":
            return self.handle_thumbnail(params)
        if command_lower == "saveconfig":
            return self.handle_save_config(params)
        if command_lower == "loadconfig":
            return self.handle_load_config(params)
        if command_lower == "listtransitions":
            return self.handle_list_transitions(params)
        return SkillResponse(False, f"Unknown command: {command}", error=f"Unknown command: {command}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Video Mixer Skill Handler")
        print("")
        print("Available commands:")
        print("  - mix")
        print("  - thumbnail")
        print("  - saveConfig")
        print("  - loadConfig")
        print("  - listTransitions")
        print("")
        print("Example:")
        print('  python skill_handler.py mix "{\\"output\\": \\"video.mp4\\", \\"clips\\": [...]}"')
        return

    command = sys.argv[1]

    if len(sys.argv) > 2:
        try:
            params = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            print(
                json.dumps(
                    {
                        "success": False,
                        "message": "The payload must be valid JSON.",
                        "output": None,
                        "error": "Invalid JSON payload",
                    },
                    ensure_ascii=False,
                )
            )
            raise SystemExit(1)
    else:
        params = {}

    response = VideoMixerSkillHandler().process(command, params)
    print(response.to_json())
    raise SystemExit(0 if response.success else 1)


if __name__ == "__main__":
    main()
