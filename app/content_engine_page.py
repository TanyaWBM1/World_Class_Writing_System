from __future__ import annotations

import json
import os
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.content_engine.batch_runner import (
    build_content_plan,
    export_approved_bundle,
    load_batch_queue,
    run_batch,
    update_approval_state,
)
from runtime.generation.llm_backend import inspect_api_key_status


RUNS_DIR = ROOT / "runs"
PLATFORMS = ("linkedin", "twitter", "instagram", "facebook", "youtube", "reddit")


class ContentEnginePage:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("World Class Content Engine")
        self.root.geometry("1360x920")

        self.mode_var = tk.StringVar(value="narrative")
        self.grit_var = tk.StringVar(value="medium")
        self.voice_var = tk.StringVar(value="tanya_lawson_v1")
        self.output_count_var = tk.StringVar(value="1")
        self.model_var = tk.StringVar(value="gpt-5")
        self.temperature_var = tk.StringVar(value="0.7")
        self.max_tokens_var = tk.StringVar(value="900")
        self.batch_status_var = tk.StringVar(value="idle")
        self.batch_dir_var = tk.StringVar(value=str(RUNS_DIR))
        self.api_status_var = tk.StringVar(value="")
        self.platform_vars = {platform: tk.BooleanVar(value=platform in {"linkedin", "twitter"}) for platform in PLATFORMS}

        self.current_batch_dir: Path | None = None
        self.queue_items: list[dict] = []

        self._build_ui()
        self._refresh_api_status()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        shell = ttk.Frame(self.root, padding=16)
        shell.grid(sticky="nsew")
        shell.columnconfigure(0, weight=0)
        shell.columnconfigure(1, weight=1)
        shell.rowconfigure(1, weight=1)

        ttk.Label(shell, text="Content Engine", font=("Georgia", 18, "bold")).grid(row=0, column=0, sticky="w")
        self.api_label = ttk.Label(shell, textvariable=self.api_status_var, foreground="#9c2f00")
        self.api_label.grid(row=0, column=1, sticky="e")

        controls = ttk.LabelFrame(shell, text="Batch Setup", padding=12)
        controls.grid(row=1, column=0, sticky="nsw", padx=(0, 12))

        ttk.Label(controls, text="Topics (one per line)").grid(row=0, column=0, sticky="w")
        self.topics_widget = tk.Text(controls, width=42, height=10, wrap="word")
        self.topics_widget.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 10))

        self._add_combo(controls, "Mode", self.mode_var, ("creative_writing", "acf_lite", "narrative", "authority", "utility", "hybrid"), 2)
        self._add_combo(controls, "Grit", self.grit_var, ("low", "medium", "high", "extreme"), 4)
        self._add_combo(controls, "Voice Profile", self.voice_var, ("tanya_lawson_v1",), 6)
        self._add_combo(controls, "Model", self.model_var, ("gpt-5", "gpt-5-mini", "gpt-4.1"), 8)

        ttk.Label(controls, text="Output Count Per Topic").grid(row=10, column=0, sticky="w")
        ttk.Entry(controls, textvariable=self.output_count_var, width=16).grid(row=11, column=0, sticky="ew", pady=(4, 10))
        ttk.Label(controls, text="Temperature").grid(row=10, column=1, sticky="w")
        ttk.Entry(controls, textvariable=self.temperature_var, width=16).grid(row=11, column=1, sticky="ew", pady=(4, 10))
        ttk.Label(controls, text="Max Tokens").grid(row=12, column=0, sticky="w")
        ttk.Entry(controls, textvariable=self.max_tokens_var, width=16).grid(row=13, column=0, sticky="ew", pady=(4, 10))

        platform_box = ttk.LabelFrame(controls, text="Platforms", padding=10)
        platform_box.grid(row=14, column=0, columnspan=2, sticky="ew", pady=(6, 10))
        for idx, platform in enumerate(PLATFORMS):
            ttk.Checkbutton(platform_box, text=platform, variable=self.platform_vars[platform]).grid(row=idx // 2, column=idx % 2, sticky="w")

        button_bar = ttk.Frame(controls)
        button_bar.grid(row=15, column=0, columnspan=2, sticky="ew")
        button_bar.columnconfigure(0, weight=1)
        button_bar.columnconfigure(1, weight=1)
        ttk.Button(button_bar, text="Run Batch", command=self.run_batch_click).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(button_bar, text="Export Approved Bundle", command=self.export_bundle_click).grid(row=0, column=1, sticky="ew")

        right = ttk.Frame(shell)
        right.grid(row=1, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        right.rowconfigure(2, weight=1)

        status_box = ttk.LabelFrame(right, text="Batch Status", padding=12)
        status_box.grid(row=0, column=0, sticky="ew")
        for idx in range(2):
            status_box.columnconfigure(idx, weight=1)
        self._status_field(status_box, "Batch status", self.batch_status_var, 0)
        self._status_field(status_box, "Batch folder", self.batch_dir_var, 1, width=58)

        review_box = ttk.LabelFrame(right, text="Review Queue", padding=12)
        review_box.grid(row=1, column=0, sticky="nsew", pady=(12, 12))
        review_box.columnconfigure(0, weight=0)
        review_box.columnconfigure(1, weight=1)
        review_box.rowconfigure(0, weight=1)

        left_review = ttk.Frame(review_box)
        left_review.grid(row=0, column=0, sticky="nsw", padx=(0, 12))
        left_review.rowconfigure(1, weight=1)

        ttk.Label(left_review, text="Generated Items").grid(row=0, column=0, sticky="w")
        self.queue_list = tk.Listbox(left_review, width=42, height=20)
        self.queue_list.grid(row=1, column=0, sticky="nsw", pady=(4, 8))
        self.queue_list.bind("<<ListboxSelect>>", self.on_item_selected)

        action_bar = ttk.Frame(left_review)
        action_bar.grid(row=2, column=0, sticky="ew")
        action_bar.columnconfigure(0, weight=1)
        action_bar.columnconfigure(1, weight=1)
        ttk.Button(action_bar, text="Approve", command=lambda: self.change_state("approved")).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(action_bar, text="Reject", command=lambda: self.change_state("rejected")).grid(row=0, column=1, sticky="ew")
        ttk.Button(action_bar, text="Needs Review", command=lambda: self.change_state("needs_review")).grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(6, 0))
        ttk.Button(action_bar, text="Open Output", command=self.open_selected_output).grid(row=1, column=1, sticky="ew", pady=(6, 0))

        detail_tabs = ttk.Notebook(review_box)
        detail_tabs.grid(row=0, column=1, sticky="nsew")

        self.summary_text = self._add_text_tab(detail_tabs, "Summary")
        self.governed_text = self._add_text_tab(detail_tabs, "Governed")
        self.raw_text = self._add_text_tab(detail_tabs, "Raw")

        rank_box = ttk.LabelFrame(right, text="Ranking Snapshot", padding=12)
        rank_box.grid(row=2, column=0, sticky="nsew")
        rank_box.columnconfigure(0, weight=1)
        rank_box.rowconfigure(0, weight=1)
        self.ranking_text = tk.Text(rank_box, wrap="word", height=12)
        self.ranking_text.grid(row=0, column=0, sticky="nsew")
        ranking_scroll = ttk.Scrollbar(rank_box, command=self.ranking_text.yview)
        ranking_scroll.grid(row=0, column=1, sticky="ns")
        self.ranking_text.configure(yscrollcommand=ranking_scroll.set)

    def _add_text_tab(self, notebook: ttk.Notebook, label: str) -> tk.Text:
        frame = ttk.Frame(notebook, padding=8)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        widget = tk.Text(frame, wrap="word")
        widget.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(frame, command=widget.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        widget.configure(yscrollcommand=scroll.set)
        notebook.add(frame, text=label)
        return widget

    def _add_combo(self, parent: ttk.Widget, label: str, variable: tk.StringVar, values: tuple[str, ...], row: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w")
        ttk.Combobox(parent, textvariable=variable, values=values, state="readonly", width=34).grid(
            row=row + 1,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(4, 10),
        )

    def _status_field(self, parent: ttk.Widget, label: str, variable: tk.StringVar, column: int, width: int = 20) -> None:
        frame = ttk.Frame(parent)
        frame.grid(row=0, column=column, sticky="ew", padx=(0, 10))
        ttk.Label(frame, text=label).grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=variable, state="readonly", width=width).grid(row=1, column=0, sticky="ew", pady=(4, 0))

    def _refresh_api_status(self) -> None:
        status = inspect_api_key_status()
        self.api_status_var.set(status["message"])
        self.api_label.configure(foreground="#1f5f2c" if status["status"] == "ready" else "#9c2f00")

    def _set_busy(self, busy: bool) -> None:
        self.root.config(cursor="watch" if busy else "")

    def _selected_platforms(self) -> list[str]:
        return [platform for platform, enabled in self.platform_vars.items() if enabled.get()]

    def _build_plan(self) -> dict:
        topics = [line.strip() for line in self.topics_widget.get("1.0", "end").splitlines() if line.strip()]
        if not topics:
            raise ValueError("Enter at least one topic.")
        platforms = self._selected_platforms()
        if not platforms:
            raise ValueError("Select at least one platform.")
        try:
            output_count = int(self.output_count_var.get().strip())
            temperature = float(self.temperature_var.get().strip())
            max_tokens = int(self.max_tokens_var.get().strip())
        except ValueError as exc:
            raise ValueError("Output count, temperature, and max tokens must be numeric.") from exc
        if output_count <= 0:
            raise ValueError("Output count per topic must be greater than 0.")
        return build_content_plan(
            topics=topics,
            mode=self.mode_var.get(),
            grit=self.grit_var.get(),
            voice_profile=self.voice_var.get(),
            platforms=platforms,
            output_count_per_topic=output_count,
            model=self.model_var.get(),
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def run_batch_click(self) -> None:
        self._refresh_api_status()
        try:
            plan = self._build_plan()
        except ValueError as exc:
            messagebox.showerror("Invalid batch input", str(exc))
            return

        self.batch_status_var.set("running")
        self._set_busy(True)
        thread = threading.Thread(target=self._run_batch_worker, args=(plan,), daemon=True)
        thread.start()

    def _run_batch_worker(self, plan: dict) -> None:
        result = run_batch(plan)
        self.root.after(0, lambda: self._after_batch_run(result))

    def _after_batch_run(self, result: dict) -> None:
        self._set_busy(False)
        self.current_batch_dir = Path(result["batch_dir"])
        self.batch_status_var.set("completed")
        self.batch_dir_var.set(result["batch_dir"])
        self.load_queue()

    def load_queue(self) -> None:
        if not self.current_batch_dir:
            return
        queue = load_batch_queue(self.current_batch_dir)
        self.queue_items = queue["items"]
        self.queue_list.delete(0, "end")
        for item in self.queue_items:
            label = f"{item['approval_state']} | {item['topic'][:32]} | {item['platform']} | {item['ranking']['weighted_score']}"
            self.queue_list.insert("end", label)
        self.ranking_text.delete("1.0", "end")
        ranked = sorted(self.queue_items, key=lambda item: item["ranking"]["weighted_score"], reverse=True)
        lines = []
        for item in ranked[:20]:
            lines.append(
                f"{item['item_id']} | {item['topic']} | {item['platform']} | score={item['ranking']['weighted_score']} | state={item['approval_state']}"
            )
        self.ranking_text.insert("1.0", "\n".join(lines))

    def _selected_item(self) -> dict | None:
        selection = self.queue_list.curselection()
        if not selection:
            return None
        return self.queue_items[selection[0]]

    def on_item_selected(self, _event=None) -> None:
        item = self._selected_item()
        if not item:
            return
        self.summary_text.delete("1.0", "end")
        self.governed_text.delete("1.0", "end")
        self.raw_text.delete("1.0", "end")

        summary_path = Path(item["run_summary_path"])
        governed_path = Path(item["governed_output_path"])
        raw_path = Path(item["raw_output_path"])
        eval_path = Path(item["evaluation_report_path"])

        summary_blob = []
        summary_blob.append(f"item_id: {item['item_id']}")
        summary_blob.append(f"topic: {item['topic']}")
        summary_blob.append(f"platform: {item['platform']}")
        summary_blob.append(f"approval_state: {item['approval_state']}")
        summary_blob.append(f"final_status: {item['final_status']}")
        summary_blob.append(f"ranking_score: {item['ranking']['weighted_score']}")
        if eval_path.exists():
            report = json.loads(eval_path.read_text(encoding="utf-8"))
            summary_blob.append("")
            summary_blob.append("ranking_breakdown:")
            for key, value in item["ranking"]["score_breakdown"].items():
                summary_blob.append(f"- {key}: {value}")
            summary_blob.append("")
            summary_blob.append("warning_reasons:")
            for value in report.get("warnings", []) or ["none"]:
                summary_blob.append(f"- {value}")
            summary_blob.append("")
            summary_blob.append("blocking_failures:")
            for value in report.get("blocking_failures", []) or ["none"]:
                summary_blob.append(f"- {value}")
        elif summary_path.exists():
            summary_blob.append("")
            summary_blob.append(summary_path.read_text(encoding="utf-8"))
        self.summary_text.insert("1.0", "\n".join(summary_blob))
        if governed_path.exists():
            self.governed_text.insert("1.0", governed_path.read_text(encoding="utf-8"))
        if raw_path.exists():
            self.raw_text.insert("1.0", raw_path.read_text(encoding="utf-8"))

    def change_state(self, new_state: str) -> None:
        item = self._selected_item()
        if not item or not self.current_batch_dir:
            return
        update_approval_state(self.current_batch_dir, item["item_id"], new_state)
        self.load_queue()

    def export_bundle_click(self) -> None:
        if not self.current_batch_dir:
            messagebox.showinfo("No batch", "Run a batch first.")
            return
        bundle = export_approved_bundle(self.current_batch_dir)
        self.batch_status_var.set(f"exported {bundle['approved_item_count']} approved items")
        self.batch_dir_var.set(bundle["export_dir"])
        messagebox.showinfo("Export complete", f"Approved bundle created at:\n{bundle['export_dir']}")

    def open_selected_output(self) -> None:
        item = self._selected_item()
        if not item:
            return
        path = Path(item["governed_output_path"])
        if path.exists():
            os.startfile(path)


def main() -> None:
    root = tk.Tk()
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    ContentEnginePage(root)
    root.mainloop()


if __name__ == "__main__":
    main()
