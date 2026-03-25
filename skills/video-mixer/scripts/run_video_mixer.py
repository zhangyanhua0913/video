#!/usr/bin/env python3
"""
Wrapper entrypoint for the local Video Mixer AgentSkill.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_payload(inline_json: str | None, json_file: str | None) -> dict:
    if inline_json and json_file:
        raise ValueError("Use either --json or --json-file, not both.")

    if inline_json:
        data = json.loads(inline_json)
    elif json_file:
        data = json.loads(Path(json_file).read_text(encoding="utf-8"))
    else:
        data = {}

    if not isinstance(data, dict):
        raise ValueError("The payload must be a JSON object.")

    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local video mixer skill wrapper.")
    parser.add_argument("command", help="mix, thumbnail, saveConfig, loadConfig, or listTransitions")
    parser.add_argument("--json", dest="inline_json", help="Inline JSON payload")
    parser.add_argument("--json-file", dest="json_file", help="Path to a JSON payload file")
    args = parser.parse_args()

    repo_root = _repo_root()
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from skill_handler import VideoMixerSkillHandler

    try:
        payload = _load_payload(args.inline_json, args.json_file)
        response = VideoMixerSkillHandler().process(args.command, payload)
        print(response.to_json())
        return 0 if response.success else 1
    except Exception as exc:
        print(
            json.dumps(
                {
                    "success": False,
                    "message": f"Wrapper execution failed: {exc}",
                    "output": None,
                    "error": str(exc),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
