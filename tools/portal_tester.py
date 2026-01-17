from __future__ import annotations

import os
import threading
import time
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox
from urllib.parse import urlparse

import requests


def _is_valid_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


class PortalTesterApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("InfinityAlamo Portal Tester")
        self.root.geometry("820x520")
        self.root.configure(bg="#0f172a")

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
            text="InfinityAlamo Portal Tester",
            fg=self._colors["text"],
            bg=self._colors["bg"],
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Paste a portal URL and run a quick reachability check.",
            fg=self._colors["muted"],
            bg=self._colors["bg"],
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 0))

        card = tk.Frame(self.root, bg=self._colors["card"], highlightthickness=1, highlightbackground="#1f2a44")
        card.pack(fill="x", padx=16, pady=(0, 12))

        tk.Label(card, text="Portal URL", fg=self._colors["text"], bg=self._colors["card"]).pack(
            anchor="w", padx=12, pady=(12, 4)
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

        action_row = tk.Frame(card, bg=self._colors["card"])
        action_row.pack(fill="x", padx=12, pady=(0, 12))

        self.test_button = tk.Button(
            action_row,
            text="Test URL",
            command=self.on_test,
            bg=self._colors["accent"],
            fg="#0b1120",
            relief="flat",
            padx=12,
            pady=6,
        )
        self.test_button.pack(side="left")

        self.open_button = tk.Button(
            action_row,
            text="Open URL",
            command=self.open_current_url,
            bg=self._colors["card_light"],
            fg=self._colors["text"],
            relief="flat",
            padx=12,
            pady=6,
        )
        self.open_button.pack(side="left", padx=(8, 0))

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

        self._link_targets: list[str] = []

        self.url_entry.focus_set()

    def log(self, message: str) -> None:
        self.status_text.configure(state="normal")
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.configure(state="disabled")
        self.status_text.see(tk.END)

    def on_test(self) -> None:
        url = self.url_var.get().strip()
        if not _is_valid_url(url):
            messagebox.showwarning("Invalid URL", "Enter a valid http(s) URL.")
            return

        self._clear_links()
        self.test_button.configure(state="disabled")
        self.log(f"Testing: {url}")
        thread = threading.Thread(target=self._run_test, args=(url,), daemon=True)
        thread.start()

    def _run_test(self, url: str) -> None:
        start = time.time()
        try:
            response = requests.get(url, timeout=15, allow_redirects=True)
            elapsed = time.time() - start
            self._finish_test(
                url=url,
                status=response.status_code,
                final_url=response.url,
                content_type=response.headers.get("Content-Type", "unknown"),
                elapsed=elapsed,
            )
        except Exception as exc:
            self._finish_error(url, exc)

    def _finish_test(
        self, url: str, status: int, final_url: str, content_type: str, elapsed: float
    ) -> None:
        self.root.after(
            0,
            lambda: self._ui_finish_test(url, status, final_url, content_type, elapsed),
        )

    def _ui_finish_test(
        self, url: str, status: int, final_url: str, content_type: str, elapsed: float
    ) -> None:
        self.log(f"Status: {status}")
        self.log(f"Final URL: {final_url}")
        self.log(f"Content-Type: {content_type}")
        self.log(f"Elapsed: {elapsed:.2f}s")
        self._register_link("Open final URL", final_url)
        self._register_path_link("Open output folder", Path.cwd() / "output")
        self._register_path_link("Open logs folder", Path.cwd() / "output" / "logs")
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

    def open_current_url(self) -> None:
        url = self.url_var.get().strip()
        if _is_valid_url(url):
            webbrowser.open(url)
        else:
            messagebox.showwarning("Invalid URL", "Enter a valid http(s) URL.")

    def open_output_folder(self) -> None:
        output_path = Path.cwd() / "output"
        if output_path.exists():
            os.startfile(output_path)  # type: ignore[attr-defined]
        else:
            messagebox.showinfo("Output folder", f"No output folder at {output_path}")

    def _register_link(self, label: str, target: str) -> None:
        self._link_targets.append(target)
        self.link_list.insert(tk.END, f"{label} — {target}")

    def _register_path_link(self, label: str, path: Path) -> None:
        if path.exists():
            self._register_link(label, str(path))

    def on_open_link(self, _event: tk.Event) -> None:
        selection = self.link_list.curselection()
        if not selection:
            return
        target = self._link_targets[selection[0]]
        if target.startswith("http"):
            webbrowser.open(target)
        else:
            os.startfile(target)  # type: ignore[attr-defined]

    def _clear_links(self) -> None:
        self._link_targets = []
        self.link_list.delete(0, tk.END)


def main() -> None:
    app = PortalTesterApp()
    app.run()


if __name__ == "__main__":
    main()
