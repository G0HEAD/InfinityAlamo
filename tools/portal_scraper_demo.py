from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk
import webbrowser
from datetime import date, datetime, timedelta
from pathlib import Path
from tkinter import messagebox
from urllib.parse import urlparse

from probate.config import load_config
from probate.pipeline import run_pipeline



def _is_valid_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


class PortalTesterApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Infinity Alamo Demo")
        self.root.geometry("820x520")
        self.root.configure(bg="#0f172a")

        self.repo_root = Path(__file__).resolve().parents[1]
        self.output_dir = self.repo_root / "output"
        self.logs_dir = self.output_dir / "logs"

        self._colors = {

            "bg": "#0f172a",
            "card": "#111827",
            "card_light": "#1f2937",
            "text": "#e5e7eb",
            "muted": "#9ca3af",
            "accent": "#38bdf8",
            "accent_dark": "#0ea5e9",
        }

        header = tk.Frame(self.root, bg=self._colors["bg"])
        header.pack(fill="x", padx=16, pady=(16, 8))
        tk.Label(
            header,
            text="Infinity Alamo Demo",
            fg=self._colors["text"],
            bg=self._colors["bg"],
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Run the probate pipeline and view extracted results.",
            fg=self._colors["muted"],
            bg=self._colors["bg"],
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 0))

        card = tk.Frame(self.root, bg=self._colors["card"], highlightthickness=1, highlightbackground="#1f2a44")
        card.pack(fill="x", padx=16, pady=(0, 12))

        tk.Label(card, text="County:", fg=self._colors["text"], bg=self._colors["card"]).pack(
            anchor="w", padx=12, pady=(12, 2)
        )
        tk.Label(
            card,
            text="example (e.g., Texas)",
            fg=self._colors["muted"],
            bg=self._colors["card"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=12, pady=(0, 6))
        self.county_var = tk.StringVar(value="DemoCounty")
        self.county_entry = tk.Entry(
            card,
            textvariable=self.county_var,
            width=30,
            relief="flat",
            bg=self._colors["card_light"],
            fg=self._colors["text"],
            insertbackground=self._colors["text"],
        )
        self.county_entry.pack(anchor="w", padx=12, pady=(0, 8))

        tk.Label(card, text="Portal URL (optional)", fg=self._colors["text"], bg=self._colors["card"]).pack(
            anchor="w", padx=12, pady=(4, 4)
        )
        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(
            card,
            textvariable=self.url_var,
            width=92,
            relief="flat",
            bg=self._colors["card_light"],
            fg=self._colors["text"],
            insertbackground=self._colors["text"],
        )
        self.url_entry.pack(anchor="w", padx=12, pady=(0, 12))

        date_row = tk.Frame(card, bg=self._colors["card"])
        date_row.pack(fill="x", padx=12, pady=(0, 12))
        tk.Label(date_row, text="Run Date", fg=self._colors["text"], bg=self._colors["card"]).pack(
            side="left"
        )
        self.date_var = tk.StringVar(value=date.today().isoformat())
        recent_dates = [
            (date.today() - timedelta(days=offset)).isoformat() for offset in range(0, 14)
        ]
        self.date_picker = ttk.Combobox(
            date_row,
            textvariable=self.date_var,
            values=recent_dates,
            width=14,
            state="normal",
        )
        self.date_picker.pack(side="left", padx=(8, 0))
        self.today_button = tk.Button(
            date_row,
            text="Today",
            command=lambda: self.date_var.set(date.today().isoformat()),
            bg=self._colors["card_light"],
            fg=self._colors["text"],
            relief="flat",
            padx=10,
            pady=4,
        )
        self.today_button.pack(side="left", padx=(8, 0))

        action_row = tk.Frame(card, bg=self._colors["card"])
        action_row.pack(fill="x", padx=12, pady=(0, 12))

        self.test_button = tk.Button(
            action_row,
            text="Run Pipeline",
            command=self.on_test,
            bg=self._colors["accent"],
            fg="#0b1120",
            relief="flat",
            padx=12,
            pady=6,
        )
        self.test_button.pack(side="left")

        self.open_output_button = tk.Button(
            action_row,
            text="Open Output Folder",
            command=self.open_output_folder,
            bg=self._colors["card_light"],
            fg=self._colors["text"],
            relief="flat",
            padx=12,
            pady=6,
        )
        self.open_output_button.pack(side="left", padx=(8, 0))

        results_card = tk.Frame(self.root, bg=self._colors["card"], highlightthickness=1, highlightbackground="#1f2a44")
        results_card.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        tk.Label(
            results_card,
            text="Captured Details",
            fg=self._colors["text"],
            bg=self._colors["card"],
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=12, pady=(12, 4))

        self.status_text = tk.Text(
            results_card,
            height=9,
            width=100,
            state="disabled",
            bg=self._colors["card_light"],
            fg=self._colors["text"],
            insertbackground=self._colors["text"],
            relief="flat",
        )
        self.status_text.pack(fill="both", expand=False, padx=12, pady=(0, 8))

        tk.Label(
            results_card,
            text="Captured Links (double-click to open)",
            fg=self._colors["muted"],
            bg=self._colors["card"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=12, pady=(0, 4))

        self.link_list = tk.Listbox(
            results_card,
            height=5,
            bg=self._colors["card_light"],
            fg=self._colors["text"],
            selectbackground=self._colors["accent_dark"],
            relief="flat",
        )
        self.link_list.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.link_list.bind("<Double-Button-1>", self.on_open_link)

        tk.Label(
            results_card,
            text="Run Checklist",
            fg=self._colors["muted"],
            bg=self._colors["card"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=12, pady=(0, 4))

        self.checklist = tk.Listbox(
            results_card,
            height=4,
            bg=self._colors["card_light"],
            fg=self._colors["text"],
            relief="flat",
        )
        self.checklist.pack(fill="x", padx=12, pady=(0, 12))

        self._link_targets: list[str] = []

        self.url_entry.focus_set()

    def log(self, message: str) -> None:
        self.status_text.configure(state="normal")
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.configure(state="disabled")
        self.status_text.see(tk.END)

    def on_test(self) -> None:
        url = self.url_var.get().strip()
        if url and not _is_valid_url(url):
            messagebox.showwarning("Invalid URL", "Enter a valid http(s) URL.")
            return

        try:
            run_date = date.fromisoformat(self.date_var.get().strip())
        except Exception:
            messagebox.showwarning("Invalid Date", "Use YYYY-MM-DD format.")
            return

        self._clear_links()
        self._clear_checklist()
        self.test_button.configure(state="disabled")
        self.log(f"Running pipeline for {run_date.isoformat()}...")
        thread = threading.Thread(
            target=self._run_pipeline,
            args=(run_date, self.county_var.get().strip(), url),
            daemon=True,
        )
        thread.start()

    def _run_pipeline(self, run_date: date, county_name: str, portal_url: str) -> None:
        start = time.time()
        try:
            config = load_config("config/counties.yaml")
            for county in config.counties:
                if county.name != county_name:
                    county.enabled = False
                if portal_url:
                    county.portal_url = portal_url

            results = run_pipeline(config, run_date)
            elapsed = time.time() - start
            self._finish_pipeline(run_date, results, elapsed)
        except Exception as exc:
            self._finish_error(str(run_date), exc)

    def _finish_pipeline(
        self, run_date: date, results: list, elapsed: float
    ) -> None:
        self.root.after(
            0,
            lambda: self._ui_finish_pipeline(run_date, results, elapsed),
        )

    def _ui_finish_pipeline(
        self, run_date: date, results: list, elapsed: float
    ) -> None:
        self.log(f"Elapsed: {elapsed:.2f}s")
        self.log(f"Cases captured: {len(results)}")
        for result in results:
            fields = result.extracted_fields
            self.log(
                f"- {fields.case_number or result.case_ref.case_number} | "
                f"{fields.deceased_name} | {fields.filer_name} | "
                f"{fields.property_address}"
            )

        report_path = (
            self.output_dir / "reports" / f"Daily_Probate_Leads_{run_date.isoformat()}.xlsx"
        )
        log_path = self.logs_dir / f"{run_date.isoformat()}.log"

        self._checklist_item("Config loaded", True)
        self._checklist_item("Pipeline executed", True)
        self._checklist_item("Cases found", len(results) > 0)
        self._checklist_item("Report generated", report_path.exists())
        self._checklist_item("Logs written", log_path.exists())

        if report_path.exists():
            self._register_path_link("Open report", report_path)
        if self.output_dir.exists():
            self._register_path_link("Open output folder", self.output_dir)
        if self.logs_dir.exists():
            self._register_path_link("Open logs folder", self.logs_dir)

        for result in results:
            for pdf_path in result.pdf_paths:
                self._register_path_link("Open PDF", Path(pdf_path))
        self.log("-" * 60)
        self.test_button.configure(state="normal")


    def _finish_error(self, url: str, exc: Exception) -> None:
        self.root.after(0, lambda: self._ui_finish_error(url, exc))

    def _ui_finish_error(self, url: str, exc: Exception) -> None:
        self.log(f"Error: {exc}")
        self.log("-" * 60)
        self.test_button.configure(state="normal")

    def run(self) -> None:
        self.root.mainloop()

    def open_output_folder(self) -> None:
        output_path = self.output_dir
        if output_path.exists():
            self._open_path(output_path)
        else:
            output_path.mkdir(parents=True, exist_ok=True)
            self._open_path(output_path)

    def _open_path(self, path: Path) -> None:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)

    def _register_link(self, label: str, target: str) -> None:
        self._link_targets.append(target)
        self.link_list.insert(tk.END, f"{label} — {target}")


    def _register_path_link(self, label: str, path: Path) -> None:
        if path.exists():
            self._register_link(label, str(path))
        else:
            self._register_link(f"{label} (missing)", str(path))


    def on_open_link(self, _event: tk.Event) -> None:
        selection = self.link_list.curselection()
        if not selection:
            return
        target = self._link_targets[selection[0]]
        if target.startswith("http"):
            webbrowser.open(target)
        else:
            self._open_path(Path(target))


    def _clear_links(self) -> None:
        self._link_targets = []
        self.link_list.delete(0, tk.END)

    def _clear_checklist(self) -> None:
        self.checklist.delete(0, tk.END)

    def _checklist_item(self, label: str, ok: bool) -> None:
        status = "✅" if ok else "⚠️"
        self.checklist.insert(tk.END, f"{status} {label}")


def main() -> None:
    app = PortalTesterApp()
    app.run()


if __name__ == "__main__":
    main()
