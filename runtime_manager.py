#!/usr/bin/env python3
"""
Runtime discovery helpers for bundled tools.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class RuntimeStatus:
    name: str
    available: bool
    detail: str
    path: Optional[str] = None


class RuntimeManager:
    def __init__(self, app_root: Optional[Path] = None):
        self.app_root = Path(app_root or Path(__file__).resolve().parent)
        self.runtime_root = self.app_root / "runtime"
        self.tools_root = self.app_root / "tools"
        self.skills_root = self.app_root / "skills"

    def build_env(self) -> Dict[str, str]:
        env = os.environ.copy()
        path_entries: List[str] = []

        ffmpeg_dir = self.get_ffmpeg_dir()
        if ffmpeg_dir is not None:
            path_entries.append(str(ffmpeg_dir))

        node_dir = self.get_node_dir()
        if node_dir is not None:
            path_entries.append(str(node_dir))

        if path_entries:
            env["PATH"] = os.pathsep.join(path_entries + [env.get("PATH", "")])

        return env

    def get_ffmpeg_dir(self) -> Optional[Path]:
        bundled = self._first_existing(
            self.tools_root / "ffmpeg" / "bin" / "ffmpeg.exe",
            self.tools_root / "ffmpeg" / "ffmpeg.exe",
            self.runtime_root / "ffmpeg" / "bin" / "ffmpeg.exe",
        )
        if bundled is not None:
            return bundled.parent

        system_path = shutil.which("ffmpeg")
        if system_path:
            return Path(system_path).parent

        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            winget_root = Path(local_appdata) / "Microsoft" / "WinGet" / "Packages"
            for package_dir in winget_root.glob("Gyan.FFmpeg*"):
                ffmpeg_exe = self._first_existing(
                    package_dir / "ffmpeg.exe",
                    package_dir / "ffmpeg-8.1-full_build" / "bin" / "ffmpeg.exe",
                )
                if ffmpeg_exe is not None:
                    return ffmpeg_exe.parent

        return None

    def get_ffmpeg_executable(self) -> Optional[Path]:
        ffmpeg_dir = self.get_ffmpeg_dir()
        if ffmpeg_dir is None:
            return None
        ffmpeg_exe = ffmpeg_dir / "ffmpeg.exe"
        return ffmpeg_exe if ffmpeg_exe.exists() else None

    def get_ffprobe_executable(self) -> Optional[Path]:
        ffmpeg_dir = self.get_ffmpeg_dir()
        if ffmpeg_dir is None:
            return None
        ffprobe_exe = ffmpeg_dir / "ffprobe.exe"
        return ffprobe_exe if ffprobe_exe.exists() else None

    def get_node_executable(self) -> Optional[Path]:
        bundled = self._first_existing(
            self.runtime_root / "node" / "node.exe",
            self.runtime_root / "nodejs" / "node.exe",
            self.tools_root / "node" / "node.exe",
        )
        if bundled is not None:
            return bundled

        system_path = shutil.which("node")
        return Path(system_path) if system_path else None

    def get_node_dir(self) -> Optional[Path]:
        node = self.get_node_executable()
        return node.parent if node else None

    def get_skill_path(self, skill_name: str = "video-mixer") -> Path:
        bundled_skill = self.skills_root / skill_name
        return bundled_skill if bundled_skill.exists() else self.app_root

    def get_status(self) -> Dict[str, RuntimeStatus]:
        ffmpeg_dir = self.get_ffmpeg_dir()
        ffprobe_exe = self.get_ffprobe_executable()
        node_exec = self.get_node_executable()
        local_skill = self.get_skill_path("video-mixer").joinpath("SKILL.md")

        return {
            "ffmpeg": RuntimeStatus("ffmpeg", ffmpeg_dir is not None, "ready" if ffmpeg_dir else "missing", str(ffmpeg_dir) if ffmpeg_dir else None),
            "ffprobe": RuntimeStatus("ffprobe", ffprobe_exe is not None, "ready" if ffprobe_exe else "missing", str(ffprobe_exe) if ffprobe_exe else None),
            "node": RuntimeStatus("node", node_exec is not None, "ready" if node_exec else "missing", str(node_exec) if node_exec else None),
            "local_skill": RuntimeStatus("local_skill", local_skill.exists(), "ready" if local_skill.exists() else "missing", str(local_skill) if local_skill.exists() else None),
        }

    def run_command(self, command: List[str], timeout_ms: int = 20000) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            cwd=str(self.app_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=self.build_env(),
            timeout=timeout_ms / 1000,
        )

    @staticmethod
    def _first_existing(*paths: Path) -> Optional[Path]:
        for path in paths:
            if path.exists():
                return path
        return None
