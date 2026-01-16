from __future__ import annotations

import threading
import time
import tkinter as tk
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
        self.root.geometry("700x420")

        tk.Label(self.root, text="Portal URL").pack(anchor="w", padx=12, pady=(12, 4))
        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(self.root, textvariable=self.url_var, width=90)
        self.url_entry.pack(anchor="w", padx=12)

        self.test_button = tk.Button(self.root, text="Test URL", command=self.on_test)
        self.test_button.pack(anchor="w", padx=12, pady=10)

        self.status_text = tk.Text(self.root, height=16, width=90, state="disabled")
        self.status_text.pack(anchor="w", padx=12, pady=(4, 12))

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


def main() -> None:
    app = PortalTesterApp()
    app.run()


if __name__ == "__main__":
    main()
