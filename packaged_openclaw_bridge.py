#!/usr/bin/env python3
"""
Helpers for packaged OpenClaw execution.
"""

from __future__ import annotations

import subprocess
from typing import Any, Dict

from runtime_manager import RuntimeManager


class PackagedOpenClawBridge:
    def __init__(self, runtime: RuntimeManager, skill_name: str = "video-mixer"):
        self.runtime = runtime
        self.skill_name = skill_name

    def is_available(self) -> bool:
        return (
            self.runtime.get_openclaw_executable() is not None
            and self.runtime.get_skill_path(self.skill_name).joinpath("SKILL.md").exists()
        )

    def ensure_skill_registered(self) -> subprocess.CompletedProcess[str]:
        skill_dir = self.runtime.get_skill_path(self.skill_name)
        if not skill_dir.joinpath("SKILL.md").exists():
            raise RuntimeError(f"Local OpenClaw skill directory not found: {skill_dir}")

        return subprocess.CompletedProcess(
            args=["local-skill-check", str(skill_dir)],
            returncode=0,
            stdout=f"Local AgentSkill ready at {skill_dir}",
            stderr="",
        )

    def call(self, command_name: str, params: Dict[str, Any]) -> subprocess.CompletedProcess[str]:
        raise RuntimeError(
            "OpenClaw recognizes the local AgentSkill directory, but direct command-style "
            "invocation is not supported by the current OpenClaw CLI. Falling back to the "
            "local Python skill runtime."
        )

    def generate_voiceover_script(self, user_requirement: str, seconds: int = 40) -> subprocess.CompletedProcess[str]:
        prompt = (
            "You are writing a short Chinese voice-over script for an auto-edited video. "
            f"Target about {seconds} seconds of spoken duration. "
            "Output only the final narration script in Chinese, with no markdown, no title, no bullet points. "
            "Keep it natural, promotional, and easy to read aloud. "
            f"User requirement: {user_requirement}"
        )
        command = self._base_command() + [
            "agent",
            "--local",
            "--agent",
            "main",
            "--json",
            "--thinking",
            "low",
            "--timeout",
            "120",
            "--message",
            prompt,
        ]
        return self._run(command)

    def get_current_model(self) -> subprocess.CompletedProcess[str]:
        command = self._base_command() + ["config", "get", "agents.defaults.model.primary"]
        return self._run(command)

    def set_current_model(self, model_name: str) -> subprocess.CompletedProcess[str]:
        command = self._base_command() + ["models", "set", model_name]
        return self._run(command)

    def _run(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            cwd=str(self.runtime.app_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=self.runtime.build_env(),
        )

    def _base_command(self) -> list[str]:
        executable = self.runtime.get_openclaw_executable()
        if executable is None:
            raise RuntimeError("OpenClaw runtime is not available.")
        return executable
