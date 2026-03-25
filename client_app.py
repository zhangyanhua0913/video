#!/usr/bin/env python3
"""Simple desktop client for the video-mixer skill."""

from __future__ import annotations

import queue
import random
import threading
import os
from pathlib import Path
from typing import Dict, List

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from client_bridge import SkillClientBridge


TRANSITIONS = ["fade", "wipeleft", "wiperight", "zoomin", "circleopen", "pixelize"]
RESOLUTIONS = {
    "1920x1080 (Landscape)": [1920, 1080],
    "1080x1920 (Portrait)": [1080, 1920],
    "1280x720 (720p)": [1280, 720],
}


class VideoMixerClientApp:
    BG_COLOR = "#f3f6fb"
    CARD_COLOR = "#ffffff"
    PRIMARY = "#1677ff"
    PRIMARY_ACTIVE = "#0f63d6"
    TEXT_MAIN = "#1f2a44"
    TEXT_SUB = "#5f6b85"
    BORDER = "#d9e2f2"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Video Mixer Studio")
        self.root.geometry("1080x760")
        self.root.minsize(960, 640)
        self.root.configure(bg=self.BG_COLOR)

        self.bridge = SkillClientBridge(workdir=Path(__file__).resolve().parent)
        self.result_queue: "queue.Queue[tuple[str, object]]" = queue.Queue()

        self.clip_paths: List[str] = []
        self.transition_var = tk.StringVar(value=TRANSITIONS[0])
        self.resolution_var = tk.StringVar(value=list(RESOLUTIONS.keys())[0])
        self.output_var = tk.StringVar(value=str(Path.cwd() / "mixed_output.mp4"))
        self.audio_fade_in_var = tk.StringVar(value="0")
        self.audio_fade_out_var = tk.StringVar(value="0")
        self.randomize_order_var = tk.BooleanVar(value=True)
        self.voiceover_enabled_var = tk.BooleanVar(value=False)
        self.voice_api_token_var = tk.StringVar(value=os.environ.get("VOLC_TTS_TOKEN", "").strip())
        self.selected_voice_label_var = tk.StringVar(value="Default (System)")
        self.voice_refresh_var = tk.BooleanVar(value=True)
        self.text_overlay_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value=self._build_backend_status("Waiting to start"))
        self.voice_options: List[Dict[str, str]] = [{"label": "Default (System)", "value": ""}]

        self._configure_styles()
        self._build_ui()
        self._refresh_backend_hint()
        self.root.after(150, self._poll_queue)

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("App.TFrame", background=self.BG_COLOR)
        style.configure(
            "HeaderTitle.TLabel",
            background=self.BG_COLOR,
            foreground=self.TEXT_MAIN,
            font=("Segoe UI", 20, "bold"),
        )
        style.configure(
            "HeaderSub.TLabel",
            background=self.BG_COLOR,
            foreground=self.TEXT_SUB,
            font=("Segoe UI", 10),
        )
        style.configure("App.TLabel", background=self.BG_COLOR, foreground=self.TEXT_MAIN, font=("Segoe UI", 10))
        style.configure("Card.TLabelframe", background=self.CARD_COLOR, bordercolor=self.BORDER, relief="solid")
        style.configure(
            "Card.TLabelframe.Label",
            background=self.CARD_COLOR,
            foreground=self.TEXT_MAIN,
            font=("Segoe UI", 10, "bold"),
        )
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(10, 8))
        style.map("Primary.TButton", background=[("!disabled", self.PRIMARY), ("active", self.PRIMARY_ACTIVE)])
        style.map("Primary.TButton", foreground=[("!disabled", "white"), ("active", "white")])
        style.configure("Ghost.TButton", font=("Segoe UI", 10), padding=(10, 8))
        style.configure("TEntry", padding=6)
        style.configure("TCombobox", padding=4)
        style.configure("TCheckbutton", background=self.CARD_COLOR, foreground=self.TEXT_MAIN, font=("Segoe UI", 10))

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=18, style="App.TFrame")
        container.pack(fill=tk.BOTH, expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        header = ttk.Frame(container, style="App.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Video Mixer Studio", style="HeaderTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(header, textvariable=self.status_var, style="HeaderSub.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 0))

        body = ttk.Frame(container, style="App.TFrame")
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        left = ttk.LabelFrame(body, text="Media Library", padding=14, style="Card.TLabelframe")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        button_bar = ttk.Frame(left, style="App.TFrame")
        button_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Button(button_bar, text="Add", command=self.add_clips, style="Ghost.TButton").pack(side=tk.LEFT)
        ttk.Button(button_bar, text="Add Folder", command=self.add_clip_folder, style="Ghost.TButton").pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(button_bar, text="Remove", command=self.remove_selected, style="Ghost.TButton").pack(side=tk.LEFT, padx=8)
        ttk.Button(button_bar, text="Up", command=lambda: self.move_clip(-1), style="Ghost.TButton").pack(side=tk.LEFT)
        ttk.Button(button_bar, text="Down", command=lambda: self.move_clip(1), style="Ghost.TButton").pack(side=tk.LEFT, padx=(8, 0))

        self.clip_list = tk.Listbox(left, selectmode=tk.EXTENDED)
        self.clip_list.configure(
            bg="#f9fbff",
            fg=self.TEXT_MAIN,
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground=self.BORDER,
            selectbackground="#dbeafe",
            selectforeground=self.TEXT_MAIN,
            font=("Segoe UI", 10),
        )
        self.clip_list.grid(row=1, column=0, sticky="nsew")

        right = ttk.LabelFrame(body, text="Output And Settings", padding=14, style="Card.TLabelframe")
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(1, weight=1)

        ttk.Label(right, text="Output", style="App.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(right, textvariable=self.output_var).grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ttk.Button(right, text="Browse", command=self.choose_output, style="Ghost.TButton").grid(row=0, column=2, padx=(8, 0))

        ttk.Label(right, text="Client Requirement", style="App.TLabel").grid(row=1, column=0, sticky="nw", pady=(10, 0))
        self.requirement_text = tk.Text(right, height=4, wrap="word")
        self.requirement_text.configure(
            bg="#f9fbff",
            fg=self.TEXT_MAIN,
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground=self.BORDER,
            font=("Segoe UI", 10),
            insertbackground=self.TEXT_MAIN,
        )
        self.requirement_text.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=(10, 0))

        generate_row = ttk.Frame(right)
        generate_row.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        generate_row.columnconfigure(0, weight=1)
        ttk.Button(generate_row, text="Generate Voice-over Script", command=self.generate_voiceover_script, style="Ghost.TButton").grid(
            row=0, column=0, sticky="ew"
        )

        ttk.Label(right, text="Resolution", style="App.TLabel").grid(row=3, column=0, sticky="w", pady=(10, 0))
        ttk.Combobox(
            right,
            textvariable=self.resolution_var,
            values=list(RESOLUTIONS.keys()),
            state="readonly",
        ).grid(row=3, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=(10, 0))

        ttk.Label(right, text="Transition", style="App.TLabel").grid(row=4, column=0, sticky="w", pady=(10, 0))
        ttk.Combobox(
            right,
            textvariable=self.transition_var,
            values=TRANSITIONS,
            state="readonly",
        ).grid(row=4, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=(10, 0))

        ttk.Label(right, text="Fade In", style="App.TLabel").grid(row=5, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(right, textvariable=self.audio_fade_in_var).grid(
            row=5, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=(10, 0)
        )

        ttk.Label(right, text="Fade Out", style="App.TLabel").grid(row=6, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(right, textvariable=self.audio_fade_out_var).grid(
            row=6, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=(10, 0)
        )

        ttk.Label(right, text="Overlay Text", style="App.TLabel").grid(row=7, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(right, textvariable=self.text_overlay_var).grid(
            row=7, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=(10, 0)
        )

        ttk.Checkbutton(
            right,
            text="Randomize Clip Order",
            variable=self.randomize_order_var,
        ).grid(row=8, column=0, columnspan=3, sticky="w", pady=(12, 0))

        ttk.Checkbutton(
            right,
            text="Add Voice-over",
            variable=self.voiceover_enabled_var,
        ).grid(row=9, column=0, columnspan=3, sticky="w", pady=(8, 0))

        ttk.Label(right, text="Voice API Token", style="App.TLabel").grid(row=10, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(right, textvariable=self.voice_api_token_var, show="*").grid(
            row=10, column=1, sticky="ew", padx=(8, 0), pady=(10, 0)
        )
        ttk.Checkbutton(
            right,
            text="Force Refresh",
            variable=self.voice_refresh_var,
        ).grid(row=10, column=2, sticky="e", pady=(10, 0))

        ttk.Label(right, text="Voice Tone", style="App.TLabel").grid(row=11, column=0, sticky="w", pady=(10, 0))
        self.voice_combobox = ttk.Combobox(
            right,
            textvariable=self.selected_voice_label_var,
            values=[item["label"] for item in self.voice_options],
            state="readonly",
        )
        self.voice_combobox.grid(row=11, column=1, sticky="ew", padx=(8, 0), pady=(10, 0))
        ttk.Button(right, text="Refresh Voices", command=self.refresh_voice_list, style="Ghost.TButton").grid(
            row=11, column=2, padx=(8, 0), pady=(10, 0)
        )

        ttk.Label(right, text="Voice-over Script", style="App.TLabel").grid(row=12, column=0, sticky="nw", pady=(10, 0))
        self.voiceover_text = tk.Text(right, height=6, wrap="word")
        self.voiceover_text.configure(
            bg="#f9fbff",
            fg=self.TEXT_MAIN,
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground=self.BORDER,
            font=("Segoe UI", 10),
            insertbackground=self.TEXT_MAIN,
        )
        self.voiceover_text.grid(row=12, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=(10, 0))

        button_row = ttk.Frame(right)
        button_row.grid(row=13, column=0, columnspan=3, sticky="ew", pady=(16, 0))
        button_row.columnconfigure(0, weight=1)
        button_row.columnconfigure(1, weight=1)

        self.run_button = ttk.Button(button_row, text="Start Mix", command=self.run_mix, style="Primary.TButton")
        self.run_button.grid(row=0, column=0, sticky="ew")
        ttk.Button(button_row, text="Run Preflight", command=self.run_preflight, style="Ghost.TButton").grid(
            row=0, column=1, sticky="ew", padx=(8, 0)
        )

        self.progress = ttk.Progressbar(right, mode="indeterminate")
        self.progress.grid(row=14, column=0, columnspan=3, sticky="ew", pady=(10, 0))

        log_frame = ttk.LabelFrame(container, text="Runtime Log", padding=14, style="Card.TLabelframe")
        log_frame.grid(row=2, column=0, sticky="nsew", pady=(12, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, height=12, wrap="word")
        self.log_text.configure(
            bg="#0f172a",
            fg="#dbe7ff",
            bd=0,
            relief="flat",
            font=("Consolas", 10),
            insertbackground="#dbe7ff",
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")
        self.log_text.configure(state="disabled")

    def add_clips(self) -> None:
        file_paths = filedialog.askopenfilenames(
            title="Choose Video Files",
            filetypes=[("Video Files", "*.mp4 *.mov *.mkv *.avi *.flv"), ("All Files", "*.*")],
        )
        for path in file_paths:
            if path not in self.clip_paths:
                self.clip_paths.append(path)
                self.clip_list.insert(tk.END, path)
        self._log(f"Added {len(file_paths)} file(s).")

    def add_clip_folder(self) -> None:
        folder_path = filedialog.askdirectory(title="Choose A Video Library Folder")
        if not folder_path:
            return

        extensions = {".mp4", ".mov", ".mkv", ".avi", ".flv"}
        added = 0
        for path in sorted(Path(folder_path).iterdir()):
            if path.is_file() and path.suffix.lower() in extensions and str(path) not in self.clip_paths:
                self.clip_paths.append(str(path))
                self.clip_list.insert(tk.END, str(path))
                added += 1

        self._log(f"Added {added} file(s) from folder: {folder_path}")

    def remove_selected(self) -> None:
        selected = list(self.clip_list.curselection())
        for index in reversed(selected):
            self.clip_list.delete(index)
            del self.clip_paths[index]

    def move_clip(self, offset: int) -> None:
        selected = self.clip_list.curselection()
        if len(selected) != 1:
            return

        index = selected[0]
        target = index + offset
        if target < 0 or target >= len(self.clip_paths):
            return

        self.clip_paths[index], self.clip_paths[target] = self.clip_paths[target], self.clip_paths[index]
        self._refresh_clip_list()
        self.clip_list.selection_set(target)

    def choose_output(self) -> None:
        file_path = filedialog.asksaveasfilename(
            title="Choose Output Video",
            defaultextension=".mp4",
            filetypes=[("MP4 Video", "*.mp4"), ("All Files", "*.*")],
        )
        if file_path:
            self.output_var.set(file_path)

    def generate_voiceover_script(self) -> None:
        requirement = self.requirement_text.get("1.0", tk.END).strip()
        if not requirement:
            messagebox.showwarning("Notice", "Please enter the client requirement first.")
            return

        self._log("Generating voice-over script locally.")
        threading.Thread(target=self._generate_voiceover_worker, args=(requirement,), daemon=True).start()

    def run_mix(self) -> None:
        if not self.clip_paths:
            messagebox.showwarning("Notice", "Please add at least one video file first.")
            return

        output_path = self.output_var.get().strip()
        if not output_path:
            messagebox.showwarning("Notice", "Please choose an output file.")
            return

        try:
            fade_in = float(self.audio_fade_in_var.get().strip() or "0")
            fade_out = float(self.audio_fade_out_var.get().strip() or "0")
        except ValueError:
            messagebox.showerror("Invalid Input", "Fade values must be numeric.")
            return

        voiceover_enabled = self.voiceover_enabled_var.get()
        voiceover_text = self.voiceover_text.get("1.0", tk.END).strip()
        if voiceover_enabled and not voiceover_text:
            messagebox.showwarning("Notice", "Please enter the voice-over text or turn off voice-over.")
            return

        selected_voice_name = self._selected_voice_name()
        token_value = self.voice_api_token_var.get().strip()

        payload = {
            "output": output_path,
            "resolution": RESOLUTIONS[self.resolution_var.get()],
            "clips": [
                {
                    "path": clip,
                    "transition": self.transition_var.get(),
                    "transitionDuration": 1.0,
                }
                for clip in self.clip_paths
            ],
            "audioFadeIn": fade_in,
            "audioFadeOut": fade_out,
            "randomizeOrder": self.randomize_order_var.get(),
            "randomSeed": random.randint(1, 999999999),
        }

        overlay_text = self.text_overlay_var.get().strip()
        if overlay_text:
            payload["textOverlays"] = [
                {
                    "text": overlay_text,
                    "startTime": 0,
                    "duration": 3,
                    "fontsize": 42,
                    "fontcolor": "white",
                    "x": "center",
                    "y": "top",
                }
            ]

        if voiceover_enabled:
            payload["voiceover"] = {
                "enabled": True,
                "text": voiceover_text,
                "rate": 0,
                "volume": 100,
                "voiceName": selected_voice_name,
                "mixLevel": 1.0,
                "originalAudioMixLevel": 0.45,
                "subtitlesEnabled": True,
                "subtitleFontsize": 40,
                "subtitleFontcolor": "white",
            }
            if token_value and selected_voice_name:
                payload["_remoteTts"] = {
                    "token": token_value,
                    "speaker": selected_voice_name,
                    "format": "mp3",
                    "sampleRate": 24000,
                    "speechRate": 0,
                    "preview": False,
                }

        self.run_button.configure(state="disabled")
        self.progress.start(10)
        self._log(
            f"Starting mix for {len(self.clip_paths)} file(s). "
            f"Random order: {self.randomize_order_var.get()}. Voice-over: {voiceover_enabled}."
        )

        threading.Thread(target=self._run_mix_worker, args=(payload,), daemon=True).start()

    def _generate_voiceover_worker(self, requirement: str) -> None:
        try:
            result = self.bridge.generate_voiceover_script(requirement, seconds=40)
            self.result_queue.put(("voiceover", result))
        except Exception as exc:
            self.result_queue.put(("error", exc))

    def refresh_voice_list(self) -> None:
        token = self.voice_api_token_var.get().strip()
        if not token:
            messagebox.showwarning("Notice", "Please enter the Voice API token first.")
            return
        self._log("Fetching voice list from remote API.")
        self.progress.start(10)
        threading.Thread(
            target=self._fetch_voice_list_worker,
            args=(token, bool(self.voice_refresh_var.get())),
            daemon=True,
        ).start()

    def _fetch_voice_list_worker(self, token: str, refresh: bool) -> None:
        try:
            result = self.bridge.fetch_volc_tts_voices(token=token, refresh=refresh)
            self.result_queue.put(("voices", result))
        except Exception as exc:
            self.result_queue.put(("error", exc))

    def run_preflight(self) -> None:
        self._log("Running packaging preflight check.")
        result = self.bridge.run_preflight()
        if result.success:
            self.status_var.set(self._build_backend_status("Preflight passed"))
            self._log(result.message)
            self._log(str(result.output))
            messagebox.showinfo("Preflight", result.message)
        else:
            self.status_var.set(self._build_backend_status("Preflight failed"))
            self._log(result.message)
            self._log(str(result.output))
            messagebox.showerror("Preflight", f"{result.message}\n\nMissing: {result.error}")

    def _run_mix_worker(self, payload: dict) -> None:
        try:
            remote_tts = payload.pop("_remoteTts", None)
            voiceover_cfg = payload.get("voiceover") if isinstance(payload.get("voiceover"), dict) else None
            if remote_tts and voiceover_cfg and voiceover_cfg.get("enabled"):
                self.result_queue.put(("log", "Generating voice-over audio from remote TTS API."))
                tts_result = self.bridge.synthesize_volc_tts_stream(
                    token=str(remote_tts.get("token", "")).strip(),
                    text=str(voiceover_cfg.get("text", "")).strip(),
                    speaker=str(remote_tts.get("speaker", "")).strip(),
                    audio_format=str(remote_tts.get("format", "mp3")),
                    sample_rate=int(remote_tts.get("sampleRate", 24000)),
                    speech_rate=int(remote_tts.get("speechRate", 0)),
                    preview=bool(remote_tts.get("preview", False)),
                )
                if not tts_result.success:
                    self.result_queue.put(
                        (
                            "mix",
                            tts_result,
                        )
                    )
                    return
                generated_audio = tts_result.output.get("audioPath") if isinstance(tts_result.output, dict) else None
                if generated_audio:
                    voiceover_cfg["audioPath"] = generated_audio
                    self.result_queue.put(("log", f"Remote TTS audio ready: {generated_audio}"))
            result = self.bridge.call("mix", payload)
            self.result_queue.put(("mix", result))
        except Exception as exc:
            self.result_queue.put(("error", exc))

    def _poll_queue(self) -> None:
        while not self.result_queue.empty():
            event, data = self.result_queue.get()
            self.progress.stop()
            self.run_button.configure(state="normal")

            if event == "mix":
                result = data
                self._log(f"Backend: {result.backend}")
                if result.raw_output:
                    self._log(result.raw_output)

                if result.success:
                    output_path = result.output.get("path") if isinstance(result.output, dict) else result.output
                    self.status_var.set(self._build_backend_status(f"Completed: {output_path}"))
                    self._log(result.message)
                    if isinstance(result.output, dict):
                        self._log(f"Clip order: {result.output.get('clipOrder')}")
                    messagebox.showinfo("Completed", f"Output file: {output_path}\nBackend: {result.backend}")
                else:
                    self.status_var.set(self._build_backend_status("Failed"))
                    detail = result.error or result.message
                    self._log(f"Failed: {detail}")
                    messagebox.showerror("Failed", f"{result.message}\n\nDetails: {detail}")

            elif event == "voiceover":
                result = data
                self._log(f"Voice-over backend: {result.backend}")
                if result.raw_output:
                    self._log(result.raw_output)

                if result.success:
                    script = result.output.get("script") if isinstance(result.output, dict) else str(result.output)
                    self.voiceover_text.delete("1.0", tk.END)
                    self.voiceover_text.insert("1.0", script)
                    self.voiceover_enabled_var.set(True)
                    self.status_var.set(self._build_backend_status("Voice-over script ready for confirmation"))
                    self._log(result.message)
                    messagebox.showinfo("Voice-over Ready", "The voice-over script is ready. Please review it before mixing.")
                else:
                    self._log(f"Voice-over generation failed: {result.message}")
                    messagebox.showerror("Voice-over Failed", f"{result.message}\n\nDetails: {result.error or ''}")

            elif event == "voices":
                result = data
                self._log(f"Voice API backend: {result.backend}")
                if result.success:
                    voices = result.output.get("voices") if isinstance(result.output, dict) else []
                    self._set_voice_options(voices if isinstance(voices, list) else [])
                    self._log(result.message)
                    messagebox.showinfo("Voices Ready", result.message)
                else:
                    self._log(f"Voice list fetch failed: {result.message}")
                    messagebox.showerror("Voice List Failed", f"{result.message}\n\nDetails: {result.error or ''}")

            elif event == "error":
                self.status_var.set(self._build_backend_status("Failed"))
                self._log(f"Error: {data}")
                messagebox.showerror("Error", str(data))
            elif event == "log":
                self._log(str(data))

        self.root.after(150, self._poll_queue)

    def _refresh_backend_hint(self) -> None:
        runtime_status = self.bridge.get_runtime_status()
        self._log(f"Runtime status: {runtime_status}")
        self.status_var.set(self._build_backend_status("Using the local Python skill runtime."))

    def _set_voice_options(self, options: List[Dict[str, str]]) -> None:
        normalized = [{"label": "Default (System)", "value": ""}]
        for item in options:
            label = str(item.get("label", "")).strip()
            value = str(item.get("value", "")).strip()
            if label and value:
                normalized.append({"label": label, "value": value})
        self.voice_options = normalized
        self.voice_combobox.configure(values=[item["label"] for item in self.voice_options])
        current_label = self.selected_voice_label_var.get().strip()
        all_labels = {item["label"] for item in self.voice_options}
        if current_label not in all_labels:
            self.selected_voice_label_var.set("Default (System)")

    def _selected_voice_name(self) -> str:
        selected = self.selected_voice_label_var.get().strip()
        for item in self.voice_options:
            if item["label"] == selected:
                return item["value"]
        return ""

    def _refresh_clip_list(self) -> None:
        self.clip_list.delete(0, tk.END)
        for path in self.clip_paths:
            self.clip_list.insert(tk.END, path)

    def _log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    @staticmethod
    def _build_backend_status(message: str) -> str:
        return f"Status: {message}"


def main() -> None:
    root = tk.Tk()
    VideoMixerClientApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
