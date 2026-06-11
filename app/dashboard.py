from __future__ import annotations

import os
import sys
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.generation.llm_backend import inspect_api_key_status, run_llm_generation
from run_writer import build_input_bundle, build_reports, build_run_config, load_json, resolve_libraries, write_json
from runtime.generation.llm_backend import build_governed_generation_result
from runtime.mode_system.mode_router import apply_mode_to_profile, ui_visibility
from runtime.voice_system.voice_runtime import analyze_voice_text

RUNS_DIR = ROOT / "runs"


class WriterDashboard:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("World Class Writing System")
        self.root.geometry("1500x980")
        self.root.minsize(1320, 860)

        self.mode_var = tk.StringVar(value="creative_writing")
        self.input_mode_var = tk.StringVar(value="Generate from idea")
        self.grit_var = tk.StringVar(value="medium")
        self.platform_var = tk.StringVar(value="none")
        self.length_var = tk.StringVar(value="long")
        self.voice_var = tk.StringVar(value="tanya_lawson_v1")
        self.model_var = tk.StringVar(value="gpt-5")
        self.temperature_var = tk.StringVar(value="0.8")
        self.max_tokens_var = tk.StringVar(value="1200")
        self.show_raw_var = tk.BooleanVar(value=False)
        self.preserve_structure_var = tk.BooleanVar(value=True)
        self.creative_pattern_var = tk.StringVar(value="memory_scene")
        self.human_texture_var = tk.BooleanVar(value=True)
        self.claim_var = tk.StringVar(value="")
        self.defined_window_var = tk.StringVar(value="")
        self.external_collider_var = tk.StringVar(value="")
        self.uncertainty_sentence_var = tk.StringVar(value="")
        self.outcome_window_var = tk.StringVar(value="")

        self.selected_mode_var = tk.StringVar(value="creative_writing")
        self.selected_voice_var = tk.StringVar(value="tanya_lawson_v1")
        self.selected_grit_var = tk.StringVar(value="medium")
        self.selected_platform_var = tk.StringVar(value="none")
        self.final_status_var = tk.StringVar(value="idle")
        self.output_folder_var = tk.StringVar(value=str(RUNS_DIR))
        self.api_key_status_var = tk.StringVar(value="")

        self.last_run_dir: Path | None = None
        self.field_blocks: dict[str, ttk.Frame] = {}
        self.field_row = 0

        self._build_ui()
        self._refresh_api_key_status()
        self._toggle_raw_visibility()
        self.input_mode_var.trace_add("write", lambda *_: self._update_input_mode_visibility())
        self.mode_var.trace_add("write", lambda *_: self._update_mode_visibility())
        self._update_input_mode_visibility()
        self._update_mode_visibility()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        shell = ttk.Frame(self.root, padding=16)
        shell.grid(sticky="nsew")
        shell.columnconfigure(0, weight=1)
        shell.columnconfigure(1, weight=1)
        shell.rowconfigure(2, weight=1)
        shell.rowconfigure(3, weight=2)

        ttk.Label(shell, text="World Class Writing System Dashboard", font=("Georgia", 18, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        self.api_warning_label = ttk.Label(shell, textvariable=self.api_key_status_var, foreground="#9c2f00")
        self.api_warning_label.grid(row=0, column=1, sticky="e")
        ttk.Label(
            shell,
            text="Start with an idea or paste something you already wrote. Then click Run + Validate.",
            foreground="#4f4f4f",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 12))

        left_panel = ttk.LabelFrame(shell, text="Writing Setup", padding=12)
        left_panel.grid(row=2, column=0, sticky="nsew", padx=(0, 12))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(0, weight=1)

        form_canvas = tk.Canvas(left_panel, highlightthickness=0)
        form_canvas.grid(row=0, column=0, sticky="nsew")
        form_scroll = ttk.Scrollbar(left_panel, orient="vertical", command=form_canvas.yview)
        form_scroll.grid(row=0, column=1, sticky="ns")
        form_canvas.configure(yscrollcommand=form_scroll.set)

        controls = ttk.Frame(form_canvas, padding=(0, 0, 4, 0))
        controls.columnconfigure(0, weight=1)
        form_window = form_canvas.create_window((0, 0), window=controls, anchor="nw")

        def _sync_form_width(event) -> None:
            form_canvas.itemconfigure(form_window, width=event.width)

        def _sync_scroll_region(_event) -> None:
            form_canvas.configure(scrollregion=form_canvas.bbox("all"))

        form_canvas.bind("<Configure>", _sync_form_width)
        controls.bind("<Configure>", _sync_scroll_region)

        ttk.Label(
            controls,
            text="Set up the run here. If the form is longer than the window, scroll inside this panel.",
            foreground="#5a5a5a",
            wraplength=520,
        ).grid(row=self.field_row, column=0, sticky="w", pady=(0, 12))
        self.field_row += 1

        self._add_combo_block(
            controls,
            "input_mode",
            "How are you starting this piece?",
            "Choose whether you're starting fresh or refining something you already wrote.",
            self.input_mode_var,
            ("Generate from idea", "Refine something I already wrote"),
        )
        self._add_combo_block(
            controls,
            "mode",
            "Which system mode do you want?",
            "Creative Writing is imagination-first. ACF Lite is reality-first and requires claim discipline.",
            self.mode_var,
            ("creative_writing", "acf_lite"),
        )
        self._add_info_block(
            controls,
            "mode_explainer",
            "Creative Writing = imagination-first, reflective, experience-driven\nACF Lite = reality-first, structured, claim-based writing",
        )
        self._add_topic_block(
            controls,
            "topic",
            "What are you writing about?",
            "Describe the idea, experience, or angle you want to explore. Don't overthink it, write it how you would say it.",
        )
        self._add_existing_text_block(
            controls,
            "existing_text",
            "Paste your writing here",
            "Only used in refine mode. Paste your draft and the system will strengthen it without changing your voice.",
        )
        self._add_check_block(
            controls,
            "preserve_structure",
            "Preserve original structure",
            "Refine mode only. Keeps the original paragraph layout as much as possible.",
            self.preserve_structure_var,
        )
        self._add_combo_block(
            controls,
            "voice_profile",
            "Who should sound like they are speaking?",
            "Choose the voice profile for the final writing.",
            self.voice_var,
            ("tanya_lawson_v1",),
        )
        self._add_combo_block(
            controls,
            "grit",
            "How sharp should the tone be?",
            "Low is gentle. Medium is balanced. High is direct. Extreme is very sharp and should be used carefully.",
            self.grit_var,
            ("low", "medium", "high", "extreme"),
        )
        self._add_combo_block(
            controls,
            "platform",
            "Where will this be published?",
            "This adapts the output for the destination platform.",
            self.platform_var,
            ("none", "linkedin", "twitter", "instagram", "facebook", "youtube", "reddit"),
        )
        self._add_combo_block(
            controls,
            "length",
            "How long should it be?",
            "Choose the target size for the output.",
            self.length_var,
            ("short", "medium", "long"),
        )
        self._add_combo_block(
            controls,
            "creative_pattern_controls",
            "What creative pattern should guide the draft?",
            "Creative Writing only. This changes the imaginative framing style.",
            self.creative_pattern_var,
            ("memory_scene", "symbolic_reflection", "character_pressure"),
        )
        self._add_check_block(
            controls,
            "human_texture_controls",
            "Keep human texture turned on",
            "Creative Writing only. This keeps lived detail and human roughness in the writing.",
            self.human_texture_var,
        )
        self._add_entry_block(
            controls,
            "topic_or_claim",
            "What claim or topic are you testing?",
            "ACF Lite only. Enter the claim or disciplined topic you want examined.",
            self.claim_var,
        )
        self._add_entry_block(
            controls,
            "defined_window",
            "What is the defined window?",
            "ACF Lite only. This is the time period or scope where the claim should be tested.",
            self.defined_window_var,
        )
        self._add_entry_block(
            controls,
            "external_collider",
            "What outside reality check could prove or disprove this?",
            "ACF Lite only. Use something concrete such as client feedback, actual sales calls, or a court outcome.",
            self.external_collider_var,
        )
        self._add_entry_block(
            controls,
            "uncertainty_sentence",
            "What uncertainty should be stated clearly?",
            "ACF Lite only. Add a sentence that admits what is still unknown.",
            self.uncertainty_sentence_var,
        )
        self._add_entry_block(
            controls,
            "outcome_window",
            "When should results become visible?",
            "ACF Lite only. Define when you expect observable evidence or a meaningful check-in.",
            self.outcome_window_var,
        )

        draft_box = ttk.LabelFrame(controls, text="Draft Settings", padding=10)
        draft_box.grid(row=self.field_row, column=0, sticky="ew", pady=(10, 0))
        draft_box.columnconfigure(0, weight=1)
        draft_box.columnconfigure(1, weight=1)
        self.field_row += 1

        ttk.Label(draft_box, text="Which OpenAI model should draft first?").grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(
            draft_box,
            text="The model creates the raw draft. The repo still governs and validates the final result.",
            foreground="#5a5a5a",
            wraplength=340,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 6))
        ttk.Combobox(
            draft_box, textvariable=self.model_var, values=("gpt-5", "gpt-5-mini", "gpt-4.1"), state="readonly"
        ).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        ttk.Label(draft_box, text="How much variation should the draft have?").grid(row=3, column=0, sticky="w")
        ttk.Label(draft_box, text="Lower is tighter. Higher is looser.", foreground="#5a5a5a").grid(
            row=4, column=0, sticky="w", pady=(2, 4)
        )
        ttk.Entry(draft_box, textvariable=self.temperature_var).grid(row=5, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(draft_box, text="How much draft length can the model use?").grid(row=3, column=1, sticky="w")
        ttk.Label(draft_box, text="This caps the raw LLM response size.", foreground="#5a5a5a").grid(
            row=4, column=1, sticky="w", pady=(2, 4)
        )
        ttk.Entry(draft_box, textvariable=self.max_tokens_var).grid(row=5, column=1, sticky="ew", pady=(0, 10))

        ttk.Checkbutton(draft_box, text="Show raw LLM output", variable=self.show_raw_var, command=self._toggle_raw_visibility).grid(
            row=6, column=0, sticky="w", pady=(4, 4)
        )
        ttk.Label(
            draft_box,
            text="Turn this on if you want to inspect the ungoverned first draft in the dashboard.",
            foreground="#5a5a5a",
            wraplength=280,
        ).grid(row=7, column=0, sticky="w")
        ttk.Label(draft_box, text="Use Run for draft generation only.", foreground="#5a5a5a", wraplength=280).grid(
            row=6, column=1, sticky="w", pady=(4, 4)
        )
        ttk.Label(
            draft_box,
            text="Use Run + Validate for the full governed execution path.",
            foreground="#5a5a5a",
            wraplength=280,
        ).grid(row=7, column=1, sticky="w")

        actions_box = ttk.LabelFrame(left_panel, text="Actions", padding=12)
        actions_box.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        actions_box.columnconfigure(0, weight=1)

        ttk.Label(
            actions_box,
            text="Run your draft",
            font=("Georgia", 14, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        button_bar = ttk.Frame(actions_box)
        button_bar.grid(row=1, column=0, sticky="ew")
        for idx in range(3):
            button_bar.columnconfigure(idx, weight=1)
        ttk.Button(button_bar, text="Run", style="SecondaryAction.TButton", command=self.generate_only).grid(
            row=0, column=0, sticky="ew", padx=(0, 8)
        )
        ttk.Button(button_bar, text="Run + Validate", style="PrimaryAction.TButton", command=self.generate_and_validate).grid(
            row=0, column=1, sticky="ew", padx=(0, 8)
        )
        ttk.Button(button_bar, text="Reset", style="MinimalAction.TButton", command=self.reset_dashboard).grid(
            row=0, column=2, sticky="ew"
        )

        action_help = ttk.Label(
            actions_box,
            text=(
                "Run = generate or refine only.  "
                "Run + Validate = full governed execution.  "
                "Reset = clear current form inputs."
            ),
            foreground="#5a5a5a",
            wraplength=520,
        )
        action_help.grid(row=2, column=0, sticky="w", pady=(8, 0))

        open_bar = ttk.Frame(actions_box)
        open_bar.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        for idx in range(3):
            open_bar.columnconfigure(idx, weight=1)
        ttk.Button(open_bar, text="Open raw draft", style="Secondary.TButton", command=self.open_latest_raw).grid(
            row=0, column=0, sticky="ew", padx=(0, 8)
        )
        ttk.Button(open_bar, text="Open governed output", style="Secondary.TButton", command=self.open_latest_output).grid(
            row=0, column=1, sticky="ew", padx=(0, 8)
        )
        ttk.Button(open_bar, text="Open evaluation report", style="Secondary.TButton", command=self.open_latest_evaluation).grid(
            row=0, column=2, sticky="ew"
        )

        right = ttk.Frame(shell)
        right.grid(row=2, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        status_box = ttk.LabelFrame(right, text="Last Run Summary", padding=12)
        status_box.grid(row=0, column=0, sticky="ew")
        for idx in range(3):
            status_box.columnconfigure(idx, weight=1)
        self._status_field(status_box, "Selected mode", self.selected_mode_var, 0, 0)
        self._status_field(status_box, "Selected voice", self.selected_voice_var, 0, 1)
        self._status_field(status_box, "Selected grit", self.selected_grit_var, 0, 2)
        self._status_field(status_box, "Selected platform", self.selected_platform_var, 1, 0)
        self._status_field(status_box, "Final status", self.final_status_var, 1, 1)
        self._status_field(status_box, "Output folder", self.output_folder_var, 1, 2, 42)

        field_help_box = ttk.LabelFrame(right, text="What each field does", padding=12)
        field_help_box.grid(row=1, column=0, sticky="nsew", pady=(12, 12))
        field_help_box.columnconfigure(0, weight=1)
        field_help_box.rowconfigure(0, weight=1)
        self.field_help_text = tk.Text(field_help_box, wrap="word", height=12)
        self.field_help_text.grid(row=0, column=0, sticky="nsew")
        field_help_scroll = ttk.Scrollbar(field_help_box, command=self.field_help_text.yview)
        field_help_scroll.grid(row=0, column=1, sticky="ns")
        self.field_help_text.configure(yscrollcommand=field_help_scroll.set)
        self.field_help_text.insert("1.0", self._field_guide_text())
        self.field_help_text.configure(state="disabled")

        usage_box = ttk.LabelFrame(right, text="How to use this dashboard", padding=12)
        usage_box.grid(row=2, column=0, sticky="nsew")
        usage_box.columnconfigure(0, weight=1)
        usage_box.rowconfigure(0, weight=1)
        self.help_text = tk.Text(usage_box, wrap="word", height=10)
        self.help_text.grid(row=0, column=0, sticky="nsew")
        help_scroll = ttk.Scrollbar(usage_box, command=self.help_text.yview)
        help_scroll.grid(row=0, column=1, sticky="ns")
        self.help_text.configure(yscrollcommand=help_scroll.set)
        self.help_text.insert("1.0", self._dashboard_guide())
        self.help_text.configure(state="disabled")

        lower = ttk.Frame(shell)
        lower.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(14, 0))
        lower.columnconfigure(0, weight=3)
        lower.columnconfigure(1, weight=2)
        lower.columnconfigure(2, weight=2)
        lower.rowconfigure(0, weight=1)

        governed_box = ttk.LabelFrame(lower, text="Governed Output", padding=12)
        governed_box.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        governed_box.columnconfigure(0, weight=1)
        governed_box.rowconfigure(0, weight=1)
        self.governed_text = tk.Text(governed_box, wrap="word")
        self.governed_text.grid(row=0, column=0, sticky="nsew")
        self.governed_text.insert("1.0", "Your final writing will appear here after you run the system.")
        governed_scroll = ttk.Scrollbar(governed_box, command=self.governed_text.yview)
        governed_scroll.grid(row=0, column=1, sticky="ns")
        self.governed_text.configure(yscrollcommand=governed_scroll.set)

        self.raw_box = ttk.LabelFrame(lower, text="Raw LLM Output", padding=12)
        self.raw_box.grid(row=0, column=1, sticky="nsew", padx=(0, 8))
        self.raw_box.columnconfigure(0, weight=1)
        self.raw_box.rowconfigure(0, weight=1)
        self.raw_text = tk.Text(self.raw_box, wrap="word")
        self.raw_text.grid(row=0, column=0, sticky="nsew")
        raw_scroll = ttk.Scrollbar(self.raw_box, command=self.raw_text.yview)
        raw_scroll.grid(row=0, column=1, sticky="ns")
        self.raw_text.configure(yscrollcommand=raw_scroll.set)

        summary_box = ttk.LabelFrame(lower, text="Evaluation Summary", padding=12)
        summary_box.grid(row=0, column=2, sticky="nsew")
        summary_box.columnconfigure(0, weight=1)
        summary_box.rowconfigure(0, weight=1)
        self.summary_text = tk.Text(summary_box, wrap="word")
        self.summary_text.grid(row=0, column=0, sticky="nsew")
        summary_scroll = ttk.Scrollbar(summary_box, command=self.summary_text.yview)
        summary_scroll.grid(row=0, column=1, sticky="ns")
        self.summary_text.configure(yscrollcommand=summary_scroll.set)

    def _add_block(self, parent: ttk.Widget, key: str, title: str, helper: str) -> ttk.Frame:
        frame = ttk.Frame(parent)
        frame.grid(row=self.field_row, column=0, sticky="ew", pady=(0, 14))
        frame.columnconfigure(0, weight=1)
        ttk.Label(frame, text=title).grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text=helper, foreground="#5a5a5a", wraplength=500).grid(row=1, column=0, sticky="w", pady=(4, 6))
        self.field_blocks[key] = frame
        self.field_row += 1
        return frame

    def _add_info_block(self, parent: ttk.Widget, key: str, text: str) -> None:
        frame = ttk.Frame(parent)
        frame.grid(row=self.field_row, column=0, sticky="ew", pady=(0, 14))
        frame.columnconfigure(0, weight=1)
        ttk.Label(frame, text=text, foreground="#4a4a4a", wraplength=500, justify="left").grid(row=0, column=0, sticky="w")
        self.field_blocks[key] = frame
        self.field_row += 1

    def _add_combo_block(
        self, parent: ttk.Widget, key: str, title: str, helper: str, variable: tk.StringVar, values: tuple[str, ...]
    ) -> None:
        ttk.Combobox(self._add_block(parent, key, title, helper), textvariable=variable, values=values, state="readonly").grid(
            row=2, column=0, sticky="ew"
        )

    def _add_entry_block(self, parent: ttk.Widget, key: str, title: str, helper: str, variable: tk.StringVar) -> None:
        ttk.Entry(self._add_block(parent, key, title, helper), textvariable=variable).grid(row=2, column=0, sticky="ew")

    def _add_check_block(self, parent: ttk.Widget, key: str, title: str, helper: str, variable: tk.BooleanVar) -> None:
        ttk.Checkbutton(self._add_block(parent, key, title, helper), text=title, variable=variable).grid(
            row=2, column=0, sticky="w"
        )

    def _add_topic_block(self, parent: ttk.Widget, key: str, title: str, helper: str) -> None:
        frame = self._add_block(parent, key, title, helper)
        self.topic_widget = tk.Text(frame, width=42, height=6, wrap="word")
        self.topic_widget.grid(row=2, column=0, sticky="ew")

    def _add_existing_text_block(self, parent: ttk.Widget, key: str, title: str, helper: str) -> None:
        frame = self._add_block(parent, key, title, helper)
        self.existing_text_widget = tk.Text(frame, width=42, height=14, wrap="word")
        self.existing_text_widget.grid(row=2, column=0, sticky="ew")

    def _status_field(
        self, parent: ttk.Widget, label: str, variable: tk.StringVar, row: int, column: int, width: int = 22
    ) -> None:
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=column, sticky="ew", padx=(0, 10), pady=(0, 8))
        ttk.Label(frame, text=label).grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=variable, state="readonly", width=width).grid(row=1, column=0, sticky="ew", pady=(4, 0))

    def _refresh_api_key_status(self) -> None:
        status = inspect_api_key_status()
        self.api_key_status_var.set(status["message"])
        self.api_warning_label.configure(foreground="#1f5f2c" if status["status"] == "ready" else "#9c2f00")

    def _toggle_raw_visibility(self) -> None:
        if self.show_raw_var.get():
            self.raw_box.grid()
        else:
            self.raw_box.grid_remove()

    def _update_mode_visibility(self) -> None:
        mode = self.mode_var.get()
        show_fields = set(ui_visibility(mode)["show_fields"])
        creative_fields = {"topic", "voice_profile", "grit", "creative_pattern_controls", "human_texture_controls"}
        acf_fields = {"topic_or_claim", "defined_window", "external_collider", "uncertainty_sentence", "outcome_window"}
        for key, block in self.field_blocks.items():
            if key in {"input_mode", "mode", "mode_explainer", "platform", "length"}:
                block.grid()
            elif key in creative_fields:
                if mode == "creative_writing":
                    block.grid()
                else:
                    block.grid_remove()
            elif key in acf_fields:
                if key in show_fields:
                    block.grid()
                else:
                    block.grid_remove()
        self._update_input_mode_visibility()

    def _update_input_mode_visibility(self) -> None:
        is_refine = self.input_mode_var.get() == "Refine something I already wrote"
        for key in {"existing_text", "preserve_structure"}:
            block = self.field_blocks.get(key)
            if block:
                if is_refine:
                    block.grid()
                else:
                    block.grid_remove()
        topic_block = self.field_blocks.get("topic")
        if topic_block:
            if is_refine and self.mode_var.get() == "acf_lite":
                topic_block.grid_remove()
            elif is_refine:
                topic_block.grid_remove()
            else:
                topic_block.grid()

    def _current_settings(self) -> dict:
        topic = self.topic_widget.get("1.0", "end").strip()
        existing_text = self.existing_text_widget.get("1.0", "end").strip()
        mode = self.mode_var.get()
        input_mode = "refine" if self.input_mode_var.get() == "Refine something I already wrote" else "generate"
        active_topic = self.claim_var.get().strip() if mode == "acf_lite" and self.claim_var.get().strip() else topic
        if input_mode == "refine":
            if not existing_text:
                raise ValueError("Paste the writing you want to refine before you run the system.")
            if not active_topic:
                active_topic = existing_text.splitlines()[0][:120] or "refined_existing_text"
        elif not active_topic:
            raise ValueError("Enter a topic or claim before you run the system.")
        try:
            temperature = float(self.temperature_var.get().strip())
            max_tokens = int(self.max_tokens_var.get().strip())
        except ValueError as exc:
            raise ValueError("Temperature must be a number and max tokens must be an integer.") from exc
        if not 0.0 <= temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0.")
        if max_tokens <= 0:
            raise ValueError("Max tokens must be greater than 0.")
        return {
            "run_id": f"dashboard_llm_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "input_mode": input_mode,
            "topic": active_topic,
            "existing_text": existing_text,
            "mode": mode,
            "grit": self.grit_var.get(),
            "platform": self.platform_var.get(),
            "length": self.length_var.get(),
            "voice_profile": self.voice_var.get(),
            "creative_pattern_controls": self.creative_pattern_var.get(),
            "human_texture_controls": self.human_texture_var.get(),
            "claim": self.claim_var.get().strip(),
            "defined_window": self.defined_window_var.get().strip(),
            "external_collider": self.external_collider_var.get().strip(),
            "uncertainty_sentence": self.uncertainty_sentence_var.get().strip(),
            "outcome_window": self.outcome_window_var.get().strip(),
            "model": self.model_var.get(),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "preserve_original_structure": self.preserve_structure_var.get(),
        }

    def _set_busy_state(self, busy: bool) -> None:
        self.root.config(cursor="watch" if busy else "")

    def _run_async(self, force_validation: bool) -> None:
        if self.input_mode_var.get() == "Generate from idea":
            self._refresh_api_key_status()
        else:
            self.api_key_status_var.set("Refine mode uses the local governance stack and skips OpenAI draft generation.")
            self.api_warning_label.configure(foreground="#1f5f2c")
        try:
            settings = self._current_settings()
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc))
            return
        output_dir = RUNS_DIR / settings["run_id"]
        self.selected_mode_var.set(settings["mode"])
        self.selected_voice_var.set(settings["voice_profile"])
        self.selected_grit_var.set(settings["grit"])
        self.selected_platform_var.set(settings["platform"])
        self.output_folder_var.set(str(output_dir))
        self.final_status_var.set("Generating your draft...")
        self._set_busy_state(True)
        threading.Thread(
            target=self._execute_run, args=(settings, output_dir, force_validation), daemon=True
        ).start()

    def generate_only(self) -> None:
        self._run_async(False)

    def generate_and_validate(self) -> None:
        self._run_async(True)

    def reset_dashboard(self) -> None:
        self.input_mode_var.set("Generate from idea")
        self.mode_var.set("creative_writing")
        self.grit_var.set("medium")
        self.platform_var.set("none")
        self.length_var.set("long")
        self.voice_var.set("tanya_lawson_v1")
        self.model_var.set("gpt-5")
        self.temperature_var.set("0.8")
        self.max_tokens_var.set("1200")
        self.show_raw_var.set(False)
        self.creative_pattern_var.set("memory_scene")
        self.human_texture_var.set(True)
        self.claim_var.set("")
        self.defined_window_var.set("")
        self.external_collider_var.set("")
        self.uncertainty_sentence_var.set("")
        self.outcome_window_var.set("")
        self.topic_widget.delete("1.0", "end")
        self.existing_text_widget.delete("1.0", "end")
        self.raw_text.delete("1.0", "end")
        self.governed_text.delete("1.0", "end")
        self.summary_text.delete("1.0", "end")
        self.selected_mode_var.set("creative_writing")
        self.selected_voice_var.set("tanya_lawson_v1")
        self.selected_grit_var.set("medium")
        self.selected_platform_var.set("none")
        self.final_status_var.set("idle")
        self.output_folder_var.set(str(RUNS_DIR))
        self.governed_text.insert("1.0", "Your final writing will appear here after you run the system.")
        self._toggle_raw_visibility()
        self._update_input_mode_visibility()
        self._update_mode_visibility()

    def _execute_run(self, settings: dict, output_dir: Path, run_full_validation: bool) -> None:
        if settings["input_mode"] == "refine":
            result = self._run_refinement(settings, output_dir, run_full_validation)
        else:
            result = run_llm_generation(settings, output_dir, run_full_validation=run_full_validation)
        self.last_run_dir = output_dir
        self.root.after(0, lambda: self._render_result(result))

    def _render_result(self, result: dict) -> None:
        self._set_busy_state(False)
        self.output_folder_var.set(str(result["output_dir"]))
        self.final_status_var.set("Complete" if result["ok"] else (result.get("final_status") or result.get("run_summary", {}).get("final_status", "failed")))
        self.raw_text.delete("1.0", "end")
        self.governed_text.delete("1.0", "end")
        self.summary_text.delete("1.0", "end")
        if result.get("raw_text"):
            self.raw_text.insert("1.0", result["raw_text"])
        if result.get("final_text"):
            self.governed_text.insert("1.0", result["final_text"])
        summary = result.get("run_summary", {})
        self.summary_text.insert("1.0", self._summary_string(summary, Path(result["output_dir"]), result.get("error")))
        if not result["ok"]:
            messagebox.showwarning("LLM backend", result.get("error", "The LLM backend run failed."))

    def _run_refinement(self, settings: dict, output_dir: Path, run_full_validation: bool) -> dict:
        output_dir.mkdir(parents=True, exist_ok=True)
        original_text = settings["existing_text"]
        original_path = output_dir / "original_input.txt"
        refined_path = output_dir / "refined_output.txt"
        original_path.write_text(original_text, encoding="utf-8")

        class Args:
            pass

        args = Args()
        args.topic = settings["topic"]
        args.mode = settings["mode"]
        args.grit = settings["grit"]
        args.platform = settings["platform"]
        args.length = settings["length"]
        args.voice_profile = settings["voice_profile"]
        args.output_dir = output_dir
        args.dry_run = False
        args.claim = settings.get("claim", "")
        args.defined_window = settings.get("defined_window", "")
        args.external_collider = settings.get("external_collider", "")
        args.uncertainty_sentence = settings.get("uncertainty_sentence", "")
        args.outcome_window = settings.get("outcome_window", "")

        run_config = build_run_config(args)
        run_config["run_id"] = settings["run_id"]
        run_config["generator_profile"].update(
            {
                "claim": settings.get("claim", ""),
                "defined_window": settings.get("defined_window", ""),
                "external_collider": settings.get("external_collider", ""),
                "uncertainty_sentence": settings.get("uncertainty_sentence", ""),
                "outcome_window": settings.get("outcome_window", ""),
                "preserve_original_structure": settings.get("preserve_original_structure", True),
            }
        )
        run_config["generator_profile"] = apply_mode_to_profile(run_config["generator_profile"])

        input_bundle = build_input_bundle(run_config)
        input_bundle["execution_metadata"]["entrypoint"] = "app/dashboard.py"
        input_bundle["execution_metadata"]["generation_backend"] = "refine_existing_text"
        input_bundle["refinement"] = {
            "refinement_applied": True,
            "preserve_original_structure": settings.get("preserve_original_structure", True),
        }
        write_json(output_dir / "input_bundle.json", input_bundle)

        original_analysis = analyze_voice_text(original_text, build_governed_generation_result(original_text, run_config["generator_profile"])["mode_selection"]["mode_id"])
        generation_result = build_governed_generation_result(original_text, run_config["generator_profile"])
        refined_text = generation_result["selected_output"]
        if settings.get("preserve_original_structure", True):
            refined_text = self._apply_original_structure(original_text, refined_text)
            generation_result["selected_output"] = refined_text
        refined_path.write_text(refined_text, encoding="utf-8")

        ownership_map = load_json(ROOT / "libraries" / "updated_library_crosswalk.json")
        validator_registry = load_json(ROOT / "runtime" / "validation" / "validator_registry.json")
        resolved_libraries = resolve_libraries(input_bundle, ownership_map, validator_registry)
        write_json(output_dir / "resolved_libraries.json", resolved_libraries)

        evaluation_report, enforcement_report, run_summary = build_reports(run_config, generation_result, resolved_libraries)
        refined_analysis = analyze_voice_text(refined_text, generation_result["mode_selection"]["mode_id"])
        cadence_adjustments = [
            flag for flag in refined_analysis.get("compression_flags", [])
            if flag not in original_analysis.get("compression_flags", [])
        ]
        roughness_adjustments = [
            flag for flag in refined_analysis.get("over_polish_flags", [])
            if flag not in original_analysis.get("over_polish_flags", [])
        ]
        major_changes_detected = original_text.strip() != refined_text.strip()

        evaluation_report.update(
            {
                "refinement_applied": True,
                "major_changes_detected": major_changes_detected,
                "cadence_adjustments": cadence_adjustments,
                "roughness_adjustments": roughness_adjustments,
            }
        )
        enforcement_report.update(
            {
                "refinement_applied": True,
                "major_changes_detected": major_changes_detected,
                "cadence_adjustments": cadence_adjustments,
                "roughness_adjustments": roughness_adjustments,
            }
        )
        run_summary.update(
            {
                "generation_backend": "refine_existing_text",
                "refinement_applied": True,
                "major_changes_detected": major_changes_detected,
                "cadence_adjustments": cadence_adjustments,
                "roughness_adjustments": roughness_adjustments,
                "raw_output_artifact": "original_input.txt",
                "governed_output_artifact": "refined_output.txt",
                "validation_requested": run_full_validation,
            }
        )

        write_json(output_dir / "evaluation_report.json", evaluation_report)
        write_json(output_dir / "enforcement_report.json", enforcement_report)
        write_json(output_dir / "run_summary.json", run_summary)

        return {
            "ok": True,
            "run_id": run_config["run_id"],
            "raw_text": original_text,
            "final_text": refined_text,
            "evaluation_report": evaluation_report,
            "enforcement_report": enforcement_report,
            "run_summary": run_summary,
            "output_dir": str(output_dir),
        }

    def _apply_original_structure(self, original_text: str, refined_text: str) -> str:
        original_paragraphs = [part.strip() for part in original_text.split("\n\n") if part.strip()]
        refined_sentences = [part.strip() for part in refined_text.replace("\n", " ").split(". ") if part.strip()]
        if len(original_paragraphs) <= 1 or not refined_sentences:
            return refined_text
        rebuilt = []
        cursor = 0
        remaining = len(refined_sentences)
        for index, paragraph in enumerate(original_paragraphs):
            original_sentence_count = max(1, len([part for part in paragraph.split(".") if part.strip()]))
            remaining_slots = max(1, len(original_paragraphs) - index)
            take = min(max(1, original_sentence_count), max(1, remaining // remaining_slots))
            selected = refined_sentences[cursor : cursor + take]
            cursor += take
            if selected:
                chunk = ". ".join(selected).strip()
                if not chunk.endswith((".", "!", "?")):
                    chunk += "."
                rebuilt.append(chunk)
        if cursor < len(refined_sentences):
            tail = ". ".join(refined_sentences[cursor:]).strip()
            if tail:
                if rebuilt and not rebuilt[-1].endswith(("!", "?", ".")):
                    rebuilt[-1] += "."
                rebuilt.append(tail if tail.endswith((".", "!", "?")) else f"{tail}.")
        return "\n\n".join(rebuilt)

    def _summary_string(self, summary: dict, output_dir: Path, error: str | None) -> str:
        lines = [
            f"Selected mode: {self.selected_mode_var.get()}",
            f"Selected voice: {self.selected_voice_var.get()}",
            f"Selected grit: {self.selected_grit_var.get()}",
            f"Selected platform: {self.selected_platform_var.get()}",
            f"Final status: {summary.get('final_status', self.final_status_var.get())}",
            f"Output folder: {output_dir}",
        ]
        if summary.get("generation_backend"):
            lines.append(f"Draft backend: {summary['generation_backend']}")
        if error:
            lines.extend(["", f"Error: {error}"])
        for label, items in (("Warnings", summary.get("warning_reasons")), ("Blocking reasons", summary.get("blocking_reasons"))):
            if items is not None:
                lines.extend(["", f"{label}:"])
                for item in items or ["none"]:
                    lines.append(f"- {item}")
        if summary.get("notes"):
            lines.extend(["", "Notes:"])
            for item in summary["notes"]:
                lines.append(f"- {item}")
        return "\n".join(lines)

    def _field_guide_text(self) -> str:
        return (
            "Input Mode\nChoose whether you're starting fresh or refining something you already wrote.\n\n"
            "Topic\nThis is what your piece is about. It can be rough. The system will help shape it.\n\n"
            "Paste your writing\nOnly used in refine mode. Paste your draft here and the system will strengthen it without flattening your voice.\n\n"
            "Preserve original structure\nLeave this on if you want the system to keep your paragraph flow as much as possible.\n\n"
            "Writing System Mode\nCreative Writing is imagination-first. ACF Lite is reality-first and more claim-disciplined.\n\n"
            "Voice Profile\nChoose who the final writing should sound like.\n\n"
            "Grit\nThis controls how soft or sharp the delivery feels.\n\n"
            "Platform\nUse this to shape the piece for where it will be read.\n\n"
            "Length\nChoose how much room the piece should have.\n\n"
            "Defined Window\nACF Lite only. This is the period or scope you want the claim tested inside.\n\n"
            "External Collider\nACF Lite only. This is the outside reality check that could challenge the claim.\n\n"
            "Uncertainty Sentence\nACF Lite only. This is where you name what is still not fully known.\n\n"
            "Outcome Window\nACF Lite only. This is when you expect visible results or a real check-in point."
        )

    def _dashboard_guide(self) -> str:
        return (
            "If you're starting from scratch, choose Generate from idea, write the topic in your own words, and click Run + Validate.\n\n"
            "If you already have a draft, choose Refine something I already wrote, paste it in, and let the system tighten it without stripping out your voice.\n\n"
            "Creative Writing is the imagination-first path. ACF Lite is the reality-first path when you need tighter claim discipline.\n\n"
            "Run gives you the governed writing pass. Run + Validate gives you the full governed execution plus the reporting layer. Reset clears the form so you can start clean.\n\n"
            "When the run finishes, the final writing appears in Governed Output. The summary and evaluation panel show what happened and where the files were saved."
        )

    def _latest_run_dir(self) -> Path | None:
        if self.last_run_dir and self.last_run_dir.exists():
            return self.last_run_dir
        if not RUNS_DIR.exists():
            return None
        candidates = [path for path in RUNS_DIR.iterdir() if path.is_dir()]
        return max(candidates, key=lambda path: path.stat().st_mtime) if candidates else None

    def open_latest_raw(self) -> None:
        self._open_latest_file(("raw_llm_output.txt", "original_input.txt"), "No output")

    def open_latest_output(self) -> None:
        self._open_latest_file(("refined_output.txt", "final_governed_output.txt"), "No output")

    def open_latest_evaluation(self) -> None:
        self._open_latest_file("evaluation_report.json", "No report")

    def _open_latest_file(self, filename: str | tuple[str, ...], title: str) -> None:
        run_dir = self._latest_run_dir()
        if not run_dir:
            messagebox.showinfo(title, "No run folder exists yet.")
            return
        filenames = (filename,) if isinstance(filename, str) else filename
        for item in filenames:
            path = run_dir / item
            if path.exists():
                os.startfile(path)
                return
        messagebox.showinfo(title, f"The latest run does not have {' or '.join(filenames)}.")


def main() -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    root = tk.Tk()
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    style.configure("Action.TButton", padding=(12, 10), font=("Segoe UI", 11, "bold"))
    style.configure("SecondaryAction.TButton", padding=(16, 14), font=("Segoe UI", 12, "bold"))
    style.configure(
        "PrimaryAction.TButton",
        padding=(22, 18),
        font=("Segoe UI", 13, "bold"),
        foreground="#111111",
        background="#2e7d32",
    )
    style.configure("MinimalAction.TButton", padding=(10, 10), font=("Segoe UI", 10))
    style.configure("Secondary.TButton", padding=(10, 8), font=("Segoe UI", 10))
    style.map(
        "PrimaryAction.TButton",
        background=[
            ("disabled", "#9fb89f"),
            ("pressed", "#1b5e20"),
            ("active", "#256b29"),
            ("!disabled", "#2e7d32"),
        ],
        foreground=[
            ("disabled", "#222222"),
            ("pressed", "#111111"),
            ("active", "#111111"),
            ("!disabled", "#111111"),
        ],
    )
    style.map("SecondaryAction.TButton", background=[("!disabled", "#d9e6f2")])
    WriterDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
