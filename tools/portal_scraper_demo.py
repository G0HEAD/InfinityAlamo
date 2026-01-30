from __future__ import annotations

import json
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
from urllib.parse import urlparse, urlunparse

from probate.config import load_config
from probate.pipeline import run_pipeline



def _is_valid_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def _mask_url(value: str) -> str:
    try:
        parsed = urlparse(value)
        if not parsed.scheme or not parsed.netloc:
            return value
        # Strip query/fragment for safer display
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))
    except Exception:
        return value


class PortalTesterApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Infinity Alamo Demo")
        self.root.geometry("820x520")
        self.root.configure(bg="#0f172a")

        self.repo_root = self._get_repo_root()
        self.runtime_root = self._get_runtime_root()
        self.output_dir = self.runtime_root / "output"
        self.logs_dir = self.output_dir / "logs"
        self.settings_path = self.runtime_root / ".portal_demo_settings.json"
        self.settings = self._load_settings()

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
        county_options = self._load_county_options()
        default_county = county_options[0] if county_options else "DemoCounty"
        self.county_var = tk.StringVar(value=default_county)
        self.county_combo = ttk.Combobox(
            card,
            textvariable=self.county_var,
            values=county_options,
            width=28,
            state="normal",
        )
        self.county_combo.pack(anchor="w", padx=12, pady=(0, 8))

        tk.Label(card, text="Portal URL (optional)", fg=self._colors["text"], bg=self._colors["card"]).pack(
            anchor="w", padx=12, pady=(4, 4)
        )
        self.remember_url_var = tk.BooleanVar(
            value=bool(self.settings.get("remember_url", False))
        )
        self.url_var = tk.StringVar(
            value=self.settings.get("default_url", "") if self.remember_url_var.get() else ""
        )
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
        self.schedule_time_var = tk.StringVar(
            value=self.settings.get("schedule_time", "21:00")
        )
        self.schedule_frequency_var = tk.StringVar(
            value=self.settings.get("schedule_frequency", "DAILY")
        )
        self.schedule_day_var = tk.StringVar(
            value=self.settings.get("schedule_day", "MON")
        )
        self.notify_on_complete_var = tk.BooleanVar(
            value=bool(self.settings.get("notify_on_complete", False))
        )
        self.demo_data_var = tk.BooleanVar(
            value=bool(self.settings.get("enable_demo_data", True))
        )
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

        self.schedule_button = tk.Button(
            action_row,
            text="Schedule Help",
            command=self.show_schedule_help,
            bg=self._colors["card_light"],
            fg=self._colors["text"],
            relief="flat",
            padx=12,
            pady=6,
        )
        self.schedule_button.pack(side="left", padx=(8, 0))

        self.settings_button = tk.Button(
            action_row,
            text="Settings",
            command=self.show_settings,
            bg=self._colors["card_light"],
            fg=self._colors["text"],
            relief="flat",
            padx=12,
            pady=6,
        )
        self.settings_button.pack(side="left", padx=(8, 0))

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
        if url:
            self.log(f"Portal URL: {_mask_url(url)}")
            try:
                config = load_config(str(self.repo_root / "config" / "counties.yaml"))
                county_name = self.county_var.get().strip()
                names = {county.name.lower() for county in config.counties}
                if (
                    county_name
                    and county_name.lower() not in names
                    and not self.demo_data_var.get()
                ):
                    messagebox.showwarning(
                        "County filter not found",
                        "County not found in config. The run will proceed without "
                        "county filtering and will pull all available results.",
                    )
            except Exception:
                pass
        thread = threading.Thread(
            target=self._run_pipeline,
            args=(run_date, self.county_var.get().strip(), url),
            daemon=True,
        )
        thread.start()

    def _run_pipeline(self, run_date: date, county_name: str, portal_url: str) -> None:
        start = time.time()
        try:
            config = load_config(str(self.repo_root / "config" / "counties.yaml"))
            self._apply_output_paths(config)
            demo_enabled = self.demo_data_var.get()
            if not demo_enabled:
                for county in config.counties:
                    if self._is_demo_county(county):
                        county.enabled = False
            matched = False
            selected = None
            for county in config.counties:
                if county.name.lower() == county_name.lower():
                    selected = county
                    matched = True
                    break

            selection_allowed = (
                selected is not None
                and (demo_enabled or not self._is_demo_county(selected))
            )
            if selection_allowed:
                for county in config.counties:
                    county.enabled = county is selected
                if portal_url:
                    selected.portal_url = portal_url
                selected.county_filter = county_name
                self.county_warning = ""
            else:
                if selected is not None and not demo_enabled and self._is_demo_county(selected):
                    self.county_warning = (
                        "Demo data disabled; skipping demo county selection."
                    )
                if portal_url:
                    if not config.counties:
                        raise ValueError("No counties configured in config/counties.yaml.")
                    if demo_enabled:
                        selected = config.counties[0]
                        for county in config.counties:
                            county.enabled = county is selected
                        selected.portal_url = portal_url
                        selected.county_filter = county_name
                        self.county_warning = (
                            f"County '{county_name}' not found in config; "
                            f"using '{selected.name}' connector with filter hint."
                        )
                    else:
                        for county in config.counties:
                            if not self._is_demo_county(county):
                                county.enabled = True
                        enabled = [c for c in config.counties if c.enabled]
                        if not enabled:
                            raise ValueError(
                                "Demo data disabled and no non-demo counties are configured."
                            )
                        for county in enabled:
                            county.portal_url = portal_url
                            county.county_filter = county_name
                        self.county_warning = (
                            f"County '{county_name}' not found in config; "
                            "collecting all portal results without county filtering."
                        )
                else:
                    self.county_warning = (
                        f"County '{county_name}' not found in config; "
                        "running all enabled counties."
                    )

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
        if getattr(self, "county_warning", ""):
            self.log(f"Note: {self.county_warning}")
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

    def show_schedule_help(self) -> None:
        repo_path = str(self.repo_root)
        python_path = sys.executable
        windows_args = "-m probate --yesterday"
        cron_line = "0 21 * * * /path/to/python -m probate --yesterday"
        task_name = "InfinityAlamo Daily"
        schedule_time = self.schedule_time_var.get().strip() or "21:00"
        schedule_frequency = self.schedule_frequency_var.get().strip().upper() or "DAILY"
        schedule_day = self.schedule_day_var.get().strip().upper() or "MON"
        cron_line = f"0 {schedule_time.split(':')[0]} * * * /path/to/python -m probate --yesterday"
        notify_clause = ""
        if self.notify_on_complete_var.get():
            notify_clause = ' && msg * "InfinityAlamo scan completed"'
        task_run = (
            f'cmd /c "cd /d {repo_path} && \\"{python_path}\\" {windows_args}{notify_clause}"'
        )
        schedule_args = ["/SC", schedule_frequency, "/ST", schedule_time]
        if schedule_frequency == "WEEKLY":
            schedule_args.extend(["/D", schedule_day])
        schedule_args_str = " ".join(schedule_args)
        task_cmd_powershell = (
            f'schtasks /Create /F {schedule_args_str} /TN "{task_name}" '
            f'/TR \'cmd /c "cd /d {repo_path} && \\"{python_path}\\" {windows_args}{notify_clause}"\''
        )

        dialog = tk.Toplevel(self.root)
        dialog.title("Schedule Help")
        dialog.configure(bg=self._colors["card"])
        dialog.geometry("720x420")

        tk.Label(
            dialog,
            text="Schedule Help",
            fg=self._colors["text"],
            bg=self._colors["card"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=12, pady=(12, 4))

        help_text = (
            "Recommended: use your OS scheduler for daily runs.\n\n"
            "Windows Task Scheduler (manual):\n"
            f"1) Create Task → Trigger: {schedule_frequency.title()} {schedule_time}\n"
            "2) Action: Start a program\n"
            f"3) Program: {python_path}\n"
            f"4) Arguments: {windows_args}\n"
            f"5) Start in: {repo_path}\n\n"
            "Windows Task Scheduler (one-command):\n"
            f"{task_cmd_powershell}\n\n"
            "macOS/Linux (cron):\n"
            f"{cron_line}\n"
        )

        text = tk.Text(
            dialog,
            height=14,
            width=88,
            bg=self._colors["card_light"],
            fg=self._colors["text"],
            relief="flat",
            wrap="word",
        )
        text.insert("1.0", help_text)
        text.configure(state="disabled")
        text.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        button_row = tk.Frame(dialog, bg=self._colors["card"])
        button_row.pack(fill="x", padx=12, pady=(0, 12))

        copy_btn = tk.Button(
            button_row,
            text="Copy Task Scheduler Command",
            command=lambda: self._copy_command(task_cmd_powershell),
            bg=self._colors["accent"],
            fg="#0b1120",
            relief="flat",
            padx=12,
            pady=6,
        )
        copy_btn.pack(side="left")

        actions_menu = tk.Menu(dialog, tearoff=0)

        def _current_schedule_values() -> tuple[str, str, str]:
            time_value = self.schedule_time_var.get().strip() or "21:00"
            frequency_value = self.schedule_frequency_var.get().strip() or "DAILY"
            day_value = self.schedule_day_var.get().strip() or "MON"
            return time_value, frequency_value, day_value

        actions_menu.add_command(
            label="Create Task Now",
            command=lambda: self._create_scheduled_task(
                dialog, task_name, *_current_schedule_values(), task_run
            ),
        )
        actions_menu.add_command(
            label="Check Task Status",
            command=lambda: self._query_task(dialog, task_name),
        )
        actions_menu.add_command(
            label="Enable Task",
            command=lambda: self._toggle_task(dialog, task_name, enable=True),
        )
        actions_menu.add_command(
            label="Disable Task",
            command=lambda: self._toggle_task(dialog, task_name, enable=False),
        )
        actions_menu.add_command(
            label="Delete Task",
            command=lambda: self._delete_task(dialog, task_name),
        )

        self.task_actions_menu = actions_menu

        menu_btn = tk.Button(
            button_row,
            text="Task Actions ☰",
            command=lambda: self._show_task_actions(menu_btn),
            bg=self._colors["card_light"],
            fg=self._colors["text"],
            relief="flat",
            padx=12,
            pady=6,
        )
        menu_btn.pack(side="left", padx=(8, 0))

        close_btn = tk.Button(
            button_row,
            text="Close",
            command=dialog.destroy,
            bg=self._colors["card_light"],
            fg=self._colors["text"],
            relief="flat",
            padx=12,
            pady=6,
        )
        close_btn.pack(side="left", padx=(8, 0))

    def _copy_command(self, command: str) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(command)
        messagebox.showinfo("Copied", "Task Scheduler command copied to clipboard.")

    def _show_task_actions(self, widget: tk.Widget) -> None:
        try:
            self.task_actions_menu.tk_popup(
                widget.winfo_rootx(), widget.winfo_rooty() + widget.winfo_height()
            )
        finally:
            self.task_actions_menu.grab_release()

    def _create_scheduled_task(
        self,
        dialog: tk.Toplevel,
        task_name: str,
        schedule_time: str,
        schedule_frequency: str,
        schedule_day: str,
        task_run: str,
    ) -> None:
        if not _is_valid_time(schedule_time):
            messagebox.showwarning("Invalid time", "Use HH:MM (24h) format.")
            return
        schedule_frequency = schedule_frequency.upper()
        schedule_day = schedule_day.upper()
        args = [
            "schtasks",
            "/Create",
            "/F",
            "/SC",
            schedule_frequency,
            "/ST",
            schedule_time,
            "/TN",
            task_name,
            "/TR",
            task_run,
        ]
        if schedule_frequency == "WEEKLY":
            args.extend(["/D", schedule_day])
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            messagebox.showinfo("Task Created", "Daily task created successfully.")
            dialog.destroy()
        else:
            messagebox.showwarning(
                "Task Creation Failed",
                (result.stderr or result.stdout or "Unknown error").strip(),
            )
            dialog.destroy()

    def _query_task(self, dialog: tk.Toplevel, task_name: str) -> None:
        result = subprocess.run(
            ["schtasks", "/Query", "/TN", task_name, "/V", "/FO", "LIST"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            messagebox.showinfo("Task Status", result.stdout.strip())
            dialog.destroy()
        else:
            messagebox.showwarning("Task Status", (result.stderr or result.stdout).strip())
            dialog.destroy()

    def _toggle_task(self, dialog: tk.Toplevel, task_name: str, enable: bool) -> None:
        action = "/ENABLE" if enable else "/DISABLE"
        result = subprocess.run(
            ["schtasks", "/Change", "/TN", task_name, action],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            messagebox.showinfo("Task Updated", "Task updated successfully.")
            dialog.destroy()
        else:
            messagebox.showwarning("Task Update Failed", (result.stderr or result.stdout).strip())
            dialog.destroy()

    def _delete_task(self, dialog: tk.Toplevel, task_name: str) -> None:
        result = subprocess.run(
            ["schtasks", "/Delete", "/TN", task_name, "/F"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            messagebox.showinfo("Task Deleted", "Task deleted successfully.")
            dialog.destroy()
        else:
            messagebox.showwarning("Task Delete Failed", (result.stderr or result.stdout).strip())
            dialog.destroy()

    def show_settings(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Settings")
        dialog.configure(bg=self._colors["card"])
        dialog.geometry("560x340")

        tk.Label(
            dialog,
            text="Settings",
            fg=self._colors["text"],
            bg=self._colors["card"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=12, pady=(12, 4))

        tk.Label(
            dialog,
            text="Default Portal URL",
            fg=self._colors["text"],
            bg=self._colors["card"],
        ).pack(anchor="w", padx=12, pady=(8, 4))
        url_entry = tk.Entry(
            dialog,
            textvariable=self.url_var,
            width=70,
            relief="flat",
            bg=self._colors["card_light"],
            fg=self._colors["text"],
            insertbackground=self._colors["text"],
        )
        url_entry.pack(anchor="w", padx=12)

        remember_check = tk.Checkbutton(
            dialog,
            text="Remember URL on this device",
            variable=self.remember_url_var,
            bg=self._colors["card"],
            fg=self._colors["text"],
            selectcolor=self._colors["card_light"],
            activebackground=self._colors["card"],
            activeforeground=self._colors["text"],
        )
        remember_check.pack(anchor="w", padx=12, pady=(6, 0))

        demo_check = tk.Checkbutton(
            dialog,
            text="Enable demo data",
            variable=self.demo_data_var,
            bg=self._colors["card"],
            fg=self._colors["text"],
            selectcolor=self._colors["card_light"],
            activebackground=self._colors["card"],
            activeforeground=self._colors["text"],
        )
        demo_check.pack(anchor="w", padx=12, pady=(4, 0))

        tk.Label(
            dialog,
            text="Preferred Daily Scan Time (HH:MM, 24h)",
            fg=self._colors["text"],
            bg=self._colors["card"],
        ).pack(anchor="w", padx=12, pady=(12, 4))
        time_entry = tk.Entry(
            dialog,
            textvariable=self.schedule_time_var,
            width=10,
            relief="flat",
            bg=self._colors["card_light"],
            fg=self._colors["text"],
            insertbackground=self._colors["text"],
        )
        time_entry.pack(anchor="w", padx=12)

        tk.Label(
            dialog,
            text="Schedule Frequency",
            fg=self._colors["text"],
            bg=self._colors["card"],
        ).pack(anchor="w", padx=12, pady=(12, 4))
        freq_picker = ttk.Combobox(
            dialog,
            textvariable=self.schedule_frequency_var,
            values=["DAILY", "WEEKLY"],
            width=10,
            state="readonly",
        )
        freq_picker.pack(anchor="w", padx=12)

        tk.Label(
            dialog,
            text="Weekly Day (if WEEKLY)",
            fg=self._colors["text"],
            bg=self._colors["card"],
        ).pack(anchor="w", padx=12, pady=(12, 4))
        day_picker = ttk.Combobox(
            dialog,
            textvariable=self.schedule_day_var,
            values=["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"],
            width=6,
            state="readonly",
        )
        day_picker.pack(anchor="w", padx=12)

        notify_check = tk.Checkbutton(
            dialog,
            text="Notify on completion (Windows pop-up)",
            variable=self.notify_on_complete_var,
            bg=self._colors["card"],
            fg=self._colors["text"],
            selectcolor=self._colors["card_light"],
            activebackground=self._colors["card"],
            activeforeground=self._colors["text"],
        )
        notify_check.pack(anchor="w", padx=12, pady=(12, 4))

        privacy_note = tk.Label(
            dialog,
            text="Note: settings are stored locally in .portal_demo_settings.json",
            fg=self._colors["muted"],
            bg=self._colors["card"],
            font=("Segoe UI", 9),
        )
        privacy_note.pack(anchor="w", padx=12, pady=(4, 0))

        button_row = tk.Frame(dialog, bg=self._colors["card"])
        button_row.pack(fill="x", padx=12, pady=(16, 12))

        save_btn = tk.Button(
            button_row,
            text="Save",
            command=lambda: self._save_settings(dialog),
            bg=self._colors["accent"],
            fg="#0b1120",
            relief="flat",
            padx=12,
            pady=6,
        )
        save_btn.pack(side="left")

        close_btn = tk.Button(
            button_row,
            text="Close",
            command=dialog.destroy,
            bg=self._colors["card_light"],
            fg=self._colors["text"],
            relief="flat",
            padx=12,
            pady=6,
        )
        close_btn.pack(side="left", padx=(8, 0))

    def _load_settings(self) -> dict:
        if not self.settings_path.exists():
            return {}
        try:
            return json.loads(self.settings_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_settings(self, dialog: tk.Toplevel) -> None:
        time_value = self.schedule_time_var.get().strip()
        if time_value and not _is_valid_time(time_value):
            messagebox.showwarning("Invalid time", "Use HH:MM (24h) format.")
            return
        payload = {
            "default_url": self.url_var.get().strip() if self.remember_url_var.get() else "",
            "schedule_time": time_value or "21:00",
            "schedule_frequency": self.schedule_frequency_var.get().strip() or "DAILY",
            "schedule_day": self.schedule_day_var.get().strip() or "MON",
            "notify_on_complete": bool(self.notify_on_complete_var.get()),
            "remember_url": bool(self.remember_url_var.get()),
            "enable_demo_data": bool(self.demo_data_var.get()),
        }
        self.settings_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        dialog.destroy()
        messagebox.showinfo("Saved", "Settings saved.")

    def _apply_output_paths(self, config: "object") -> None:
        config.output.pdf_dir = str(self.runtime_root / "data" / "pdfs")
        config.output.report_dir = str(self.runtime_root / "output" / "reports")
        config.output.logs_dir = str(self.runtime_root / "output" / "logs")

    def _get_repo_root(self) -> Path:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS)
        return Path(__file__).resolve().parents[1]

    def _get_runtime_root(self) -> Path:
        if getattr(sys, "frozen", False):
            base = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
            return base / "InfinityAlamoDemo"
        return Path(__file__).resolve().parents[1]

    def _load_county_options(self) -> list[str]:
        try:
            config = load_config(str(self.repo_root / "config" / "counties.yaml"))
            names = [county.name for county in config.counties]
            return sorted(set(names)) if names else ["DemoCounty"]
        except Exception:
            return ["DemoCounty"]

    @staticmethod
    def _is_demo_county(county: "object") -> bool:
        name = getattr(county, "name", "")
        connector = getattr(county, "connector", "")
        return str(name).lower().startswith("demo") or str(connector).lower().startswith(
            "demo"
        )

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


def _is_valid_time(value: str) -> bool:
    try:
        datetime.strptime(value, "%H:%M")
        return True
    except Exception:
        return False


def main() -> None:
    app = PortalTesterApp()
    app.run()


if __name__ == "__main__":
    main()
