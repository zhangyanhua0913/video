---
name: video-mixer
description: Use this skill when the user wants to auto-mix local video clips, generate a thumbnail, inspect available transitions, or save/load mix configs for the Go Edit Video workspace. It wraps the existing Python video mixer so the agent can work through a recognized local OpenClaw skill directory while keeping execution inside this repository.
---

# Video Mixer

## Overview

This skill wraps the local Python video editing tool in this workspace.
Use it for tasks like:

- Mix multiple local video clips into one output file
- Generate a thumbnail from a source video
- List supported transition names before building a mix
- Save or load JSON config files used by the mixer

The actual implementation lives in the repository root:

- `skill_handler.py`
- `video_mixer.py`

## Workflow

1. Confirm the input and output paths are local Windows paths.
2. If the user only needs transition names, run:
   `python skills/video-mixer/scripts/run_video_mixer.py listTransitions`
3. If the user wants a mix or thumbnail, create a JSON payload that matches the command schema in `references/commands.md`.
4. Invoke the wrapper script:
   `python skills/video-mixer/scripts/run_video_mixer.py <command> --json-file <payload.json>`
5. Parse the JSON result and report success, output path, and any error details.

## Command Guide

- `mix`: combine clips into one output video
- `thumbnail`: generate a thumbnail image from one video
- `saveConfig`: write a config JSON file
- `loadConfig`: read a config JSON file
- `listTransitions`: return supported transition names

Read `references/commands.md` when you need the exact payload shape.

## Notes

- This skill is a local AgentSkill wrapper around the existing Python runtime. It is recognized by OpenClaw/Codex as a skill directory because it follows the `skills/<name>/SKILL.md` layout.
- Do not call the old `openclaw skill register` or `openclaw skill call` commands for this project. Those commands do not match the current OpenClaw skills model.
- FFmpeg and FFprobe must be available for `mix` and `thumbnail`.
