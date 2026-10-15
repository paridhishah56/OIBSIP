"""Tkinter interface for the Random Password Generator."""

import tkinter as tk
from tkinter import ttk

from password_generator import (
    MAX_LENGTH,
    MIN_LENGTH,
    PasswordOptions,
    SessionHistory,
    estimate_strength,
    generate_password,
)


class PasswordGeneratorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("560x700")
        self.root.minsize(500, 650)

        self.password = tk.StringVar()
        self.length = tk.IntVar(value=16)
        self.uppercase = tk.BooleanVar(value=True)
        self.lowercase = tk.BooleanVar(value=True)
        self.digits = tk.BooleanVar(value=True)
        self.special_characters = tk.BooleanVar(value=True)
        self.exclude_ambiguous = tk.BooleanVar(value=False)
        self.show_password = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="Choose your options and generate a password.")
        self.strength_text = tk.StringVar(value="Strength: —")
        self.history = SessionHistory(limit=5)

        self._build_interface()

    def _build_interface(self) -> None:
        container = ttk.Frame(self.root, padding=(24, 20))
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)

        ttk.Label(container, text="Random Password Generator", font=("Segoe UI", 18, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(container, text="Create a strong password with secure randomness.").grid(
            row=1, column=0, sticky="w", pady=(4, 18)
        )

        settings = ttk.LabelFrame(container, text="Password options", padding=14)
        settings.grid(row=2, column=0, sticky="ew")
        settings.columnconfigure(1, weight=1)
        ttk.Label(settings, text="Length").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(
            settings,
            from_=MIN_LENGTH,
            to=MAX_LENGTH,
            textvariable=self.length,
            width=8,
            wrap=False,
        ).grid(row=0, column=1, sticky="w", padx=(16, 0))

        category_frame = ttk.Frame(settings)
        category_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 4))
        for column, (label, variable) in enumerate(
            (
                ("Uppercase", self.uppercase),
                ("Lowercase", self.lowercase),
                ("Digits", self.digits),
                ("Special characters", self.special_characters),
            )
        ):
            ttk.Checkbutton(category_frame, text=label, variable=variable).grid(
                row=column // 2, column=column % 2, sticky="w", padx=(0, 18), pady=3
            )
        ttk.Checkbutton(
            settings,
            text="Exclude ambiguous characters (0, O, o, 1, l, I)",
            variable=self.exclude_ambiguous,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

        output = ttk.LabelFrame(container, text="Generated password", padding=14)
        output.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        output.columnconfigure(0, weight=1)
        self.password_entry = ttk.Entry(output, textvariable=self.password, show="•", font=("Consolas", 12))
        self.password_entry.grid(row=0, column=0, sticky="ew")
        ttk.Checkbutton(output, text="Show", variable=self.show_password, command=self._toggle_visibility).grid(
            row=0, column=1, padx=(10, 0)
        )
        button_row = ttk.Frame(output)
        button_row.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Button(button_row, text="Generate Password", command=self._generate).pack(side="left")
        ttk.Button(button_row, text="Copy to Clipboard", command=self._copy).pack(side="left", padx=(8, 0))

        strength_row = ttk.Frame(container)
        strength_row.grid(row=4, column=0, sticky="ew", pady=(14, 0))
        strength_row.columnconfigure(0, weight=1)
        ttk.Label(strength_row, textvariable=self.strength_text).grid(row=0, column=0, sticky="w")
        self.strength_bar = ttk.Progressbar(strength_row, maximum=100, mode="determinate", length=180)
        self.strength_bar.grid(row=0, column=1, sticky="e")

        ttk.Label(container, textvariable=self.status, wraplength=500).grid(
            row=5, column=0, sticky="w", pady=(8, 0)
        )

        history_frame = ttk.LabelFrame(container, text="Session history", padding=14)
        history_frame.grid(row=6, column=0, sticky="nsew", pady=(18, 0))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(1, weight=1)
        ttk.Label(
            history_frame,
            text="Sensitive: the last five passwords stay in memory until this window closes.",
            wraplength=480,
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.history_list = tk.Listbox(history_frame, height=5, font=("Consolas", 10), activestyle="none")
        self.history_list.grid(row=1, column=0, sticky="nsew")
        history_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_list.yview)
        history_scrollbar.grid(row=1, column=1, sticky="ns")
        self.history_list.configure(yscrollcommand=history_scrollbar.set)
        ttk.Button(history_frame, text="Clear History", command=self._clear_history).grid(
            row=2, column=0, sticky="e", pady=(10, 0)
        )

    def _options(self) -> PasswordOptions:
        return PasswordOptions(
            length=self.length.get(),
            uppercase=self.uppercase.get(),
            lowercase=self.lowercase.get(),
            digits=self.digits.get(),
            special_characters=self.special_characters.get(),
            exclude_ambiguous=self.exclude_ambiguous.get(),
        )

    def _generate(self) -> None:
        try:
            generated = generate_password(self._options())
        except (ValueError, tk.TclError) as error:
            self.status.set(str(error))
            return

        self.password.set(generated)
        strength, score = estimate_strength(generated)
        self.strength_text.set(f"Strength: {strength}")
        self.strength_bar.configure(value=score)
        self.history.add(generated)
        self._refresh_history()
        try:
            self._copy_to_clipboard(generated)
        except Exception:
            self.status.set("Password generated, but clipboard access failed. Use Copy to Clipboard to retry.")
        else:
            self.status.set("Password generated and copied to the clipboard.")

    @staticmethod
    def _copy_to_clipboard(password: str) -> None:
        try:
            import pyperclip
        except ImportError as error:
            raise RuntimeError("Clipboard support requires pyperclip.") from error
        pyperclip.copy(password)

    def _copy(self) -> None:
        current_password = self.password.get()
        if not current_password:
            self.status.set("Generate a password before copying.")
            return
        try:
            self._copy_to_clipboard(current_password)
        except Exception:
            self.status.set("Clipboard access failed. Check clipboard support and try again.")
        else:
            self.status.set("Password copied to the clipboard.")

    def _toggle_visibility(self) -> None:
        self.password_entry.configure(show="" if self.show_password.get() else "•")

    def _refresh_history(self) -> None:
        self.history_list.delete(0, tk.END)
        for password in self.history.passwords:
            self.history_list.insert(tk.END, password)

    def _clear_history(self) -> None:
        self.history.clear()
        self._refresh_history()
        self.status.set("Session history cleared.")


def main() -> None:
    root = tk.Tk()
    PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
