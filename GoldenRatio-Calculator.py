#!/usr/bin/env python3
"""
golden_ratio_app.py
Modern macOS-friendly Golden Ratio utility using CustomTkinter.
Scrollable main window when the window is too small.
"""

from __future__ import annotations

import platform
import customtkinter as ctk
from tkinter import messagebox

PHI = (1 + 5 ** 0.5) / 2  # ~1.618033988749895


def _parse_float(text: str) -> float:
    t = (text or "").strip().replace(",", ".")
    if not t:
        raise ValueError("Empty")
    return float(t)


def _fmt(x: float) -> str:
    s = f"{x:.10f}".rstrip("0").rstrip(".")
    return s if s else "0"


class GoldenRatioApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.title("Golden Ratio")

        # Resizable window + reasonable defaults
        self.geometry("520x520")
        self.minsize(420, 420)
        self.resizable(True, True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.live_var = ctk.BooleanVar(value=True)
        self.mode_var = ctk.StringVar(value="single")

        # ✅ Scrollable root container (vertical scrollbar appears automatically)
        self.container = ctk.CTkScrollableFrame(self, corner_radius=18)
        self.container.grid(row=0, column=0, padx=18, pady=18, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)

        # Header
        title = ctk.CTkLabel(
            self.container,
            text="Golden Ratio",
            font=self._font(24, "bold"),
        )
        title.grid(row=0, column=0, padx=18, pady=(18, 2), sticky="w")

        subtitle = ctk.CTkLabel(
            self.container,
            text=f"φ = {_fmt(PHI)}",
            font=self._font(13, "normal"),
            text_color=("gray35", "gray70"),
        )
        subtitle.grid(row=1, column=0, padx=18, pady=(0, 12), sticky="w")

        # Tabs
        self.tabs = ctk.CTkSegmentedButton(
            self.container,
            values=["From one number", "From two numbers"],
            command=self._on_tab_change,
            corner_radius=12,
        )
        self.tabs.set("From one number")
        self.tabs.grid(row=2, column=0, padx=18, pady=(0, 14), sticky="ew")

        # Content area
        self.content = ctk.CTkFrame(self.container, corner_radius=16)
        self.content.grid(row=3, column=0, padx=18, pady=(0, 12), sticky="ew")
        self.content.grid_columnconfigure(0, weight=1)

        self._build_single_view()
        self._build_pair_view()
        self._show_mode("single")

        # Footer
        footer = ctk.CTkFrame(self.container, fg_color="transparent")
        footer.grid(row=4, column=0, padx=18, pady=(0, 18), sticky="ew")
        footer.grid_columnconfigure(0, weight=1)

        self.hint = ctk.CTkLabel(
            footer,
            text="Tip: Press Enter to calculate. Copy buttons on the right.",
            font=self._font(12, "normal"),
            text_color=("gray35", "gray70"),
            justify="left",
            wraplength=360,
        )
        self.hint.grid(row=0, column=0, sticky="w")

        live_switch = ctk.CTkSwitch(
            footer,
            text="Live",
            variable=self.live_var,
            command=self._maybe_recalc,
        )
        live_switch.grid(row=0, column=1, sticky="e")

        # Keyboard shortcuts
        self.bind("<Return>", lambda _e: self._calculate())
        if platform.system() == "Darwin":
            self.bind("<Command-l>", lambda _e: self._focus_primary())
        else:
            self.bind("<Control-l>", lambda _e: self._focus_primary())

        # ✅ Mouse wheel scrolling (trackpad/wheel)
        self._bind_mousewheel(self.container)

        # Initial focus
        self.after(120, self._focus_primary)

    # -------------------- Helpers --------------------

    def _font(self, size: int, weight: str = "normal"):
        if platform.system() == "Darwin":
            return ("SF Pro Display", size, weight)
        return ("Segoe UI", size, weight)

    def _bind_mousewheel(self, widget):
        """
        Make mouse wheel / trackpad scroll the CTkScrollableFrame.
        Works on macOS, Windows, Linux.
        """
        # Windows/macOS
        widget.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        # Linux
        widget.bind_all("<Button-4>", self._on_mousewheel_linux_up, add="+")
        widget.bind_all("<Button-5>", self._on_mousewheel_linux_down, add="+")

    def _on_mousewheel(self, event):
        # On Windows: event.delta is multiples of 120
        # On macOS: smaller deltas, but sign is correct
        self.container._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux_up(self, _event):
        self.container._parent_canvas.yview_scroll(-1, "units")

    def _on_mousewheel_linux_down(self, _event):
        self.container._parent_canvas.yview_scroll(1, "units")

    # -------------------- UI builders --------------------

    def _build_single_view(self) -> None:
        self.single = ctk.CTkFrame(self.content, corner_radius=16, fg_color="transparent")
        self.single.grid(row=0, column=0, sticky="ew")
        self.single.grid_columnconfigure(0, weight=1)

        self.single_entry = ctk.CTkEntry(
            self.single,
            placeholder_text="Enter a number (e.g., 10)",
            font=self._font(14),
            justify="center",
            height=40,
        )
        self.single_entry.grid(row=0, column=0, padx=18, pady=(18, 10), sticky="ew")
        self.single_entry.bind("<KeyRelease>", lambda _e: self._maybe_recalc())

        btn_row = ctk.CTkFrame(self.single, fg_color="transparent")
        btn_row.grid(row=1, column=0, padx=18, pady=(0, 12), sticky="ew")
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)

        self.calc_btn = ctk.CTkButton(btn_row, text="Calculate", command=self._calculate, corner_radius=12, height=40)
        self.calc_btn.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.clear_btn = ctk.CTkButton(
            btn_row,
            text="Clear",
            command=self._clear,
            corner_radius=12,
            height=40,
            fg_color=("gray80", "gray25"),
            text_color=("black", "white"),
            hover_color=("gray75", "gray30"),
        )
        self.clear_btn.grid(row=0, column=1, padx=(8, 0), sticky="ew")

        results = ctk.CTkFrame(self.single, corner_radius=16)
        results.grid(row=2, column=0, padx=18, pady=(0, 18), sticky="ew")
        results.grid_columnconfigure(0, weight=1)

        self.small_value = ctk.StringVar(value="—")
        self.large_value = ctk.StringVar(value="—")

        self._result_row(results, 0, "Smaller (x / φ)", self.small_value, lambda: self._copy(self.small_value.get()))
        self._result_row(results, 1, "Larger (x × φ)", self.large_value, lambda: self._copy(self.large_value.get()))

    def _build_pair_view(self) -> None:
        self.pair = ctk.CTkFrame(self.content, corner_radius=16, fg_color="transparent")
        self.pair.grid(row=0, column=0, sticky="ew")
        self.pair.grid_columnconfigure(0, weight=1)

        grid = ctk.CTkFrame(self.pair, fg_color="transparent")
        grid.grid(row=0, column=0, padx=18, pady=(18, 10), sticky="ew")
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        self.small_entry = ctk.CTkEntry(grid, placeholder_text="Smaller", font=self._font(14), justify="center", height=40)
        self.small_entry.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        self.small_entry.bind("<KeyRelease>", lambda _e: self._maybe_recalc())

        self.large_entry = ctk.CTkEntry(grid, placeholder_text="Larger", font=self._font(14), justify="center", height=40)
        self.large_entry.grid(row=0, column=1, padx=(8, 0), sticky="ew")
        self.large_entry.bind("<KeyRelease>", lambda _e: self._maybe_recalc())

        btn_row = ctk.CTkFrame(self.pair, fg_color="transparent")
        btn_row.grid(row=1, column=0, padx=18, pady=(0, 12), sticky="ew")
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)

        self.calc_btn2 = ctk.CTkButton(btn_row, text="Check / Solve", command=self._calculate, corner_radius=12, height=40)
        self.calc_btn2.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.clear_btn2 = ctk.CTkButton(
            btn_row,
            text="Clear",
            command=self._clear,
            corner_radius=12,
            height=40,
            fg_color=("gray80", "gray25"),
            text_color=("black", "white"),
            hover_color=("gray75", "gray30"),
        )
        self.clear_btn2.grid(row=0, column=1, padx=(8, 0), sticky="ew")

        results = ctk.CTkFrame(self.pair, corner_radius=16)
        results.grid(row=2, column=0, padx=18, pady=(0, 18), sticky="ew")
        results.grid_columnconfigure(0, weight=1)

        self.ratio_value = ctk.StringVar(value="—")
        self.missing_value = ctk.StringVar(value="—")

        self._result_row(results, 0, "Larger / Smaller", self.ratio_value, lambda: self._copy(self.ratio_value.get()))
        self._result_row(results, 1, "Missing value (if one empty)", self.missing_value, lambda: self._copy(self.missing_value.get()))

    def _result_row(self, parent, row: int, label: str, var: ctk.StringVar, copy_cmd) -> None:
        wrapper = ctk.CTkFrame(parent, fg_color="transparent")
        wrapper.grid(row=row, column=0, padx=14, pady=(12 if row == 0 else 6, 10), sticky="ew")
        wrapper.grid_columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(wrapper, text=label, font=self._font(12), text_color=("gray35", "gray70"))
        lbl.grid(row=0, column=0, sticky="w")

        line = ctk.CTkFrame(wrapper, fg_color="transparent")
        line.grid(row=1, column=0, sticky="ew")
        line.grid_columnconfigure(0, weight=1)

        val = ctk.CTkLabel(line, textvariable=var, font=self._font(16, "bold"))
        val.grid(row=0, column=0, sticky="w")

        copy_btn = ctk.CTkButton(
            line,
            text="Copy",
            command=copy_cmd,
            width=72,
            height=28,
            corner_radius=10,
            fg_color=("gray85", "gray25"),
            text_color=("black", "white"),
            hover_color=("gray80", "gray30"),
        )
        copy_btn.grid(row=0, column=1, sticky="e")

    # -------------------- Mode & actions --------------------

    def _on_tab_change(self, value: str) -> None:
        self._show_mode("single" if value == "From one number" else "pair")
        self._clear()

    def _show_mode(self, mode: str) -> None:
        self.mode_var.set(mode)
        if mode == "single":
            self.pair.grid_remove()
            self.single.grid()
        else:
            self.single.grid_remove()
            self.pair.grid()
        self._focus_primary()

    def _focus_primary(self) -> None:
        if self.mode_var.get() == "single":
            self.single_entry.focus_set()
            self.single_entry.select_range(0, "end")
        else:
            self.small_entry.focus_set()
            self.small_entry.select_range(0, "end")

    def _clear(self) -> None:
        if self.mode_var.get() == "single":
            self.single_entry.delete(0, "end")
            self.small_value.set("—")
            self.large_value.set("—")
        else:
            self.small_entry.delete(0, "end")
            self.large_entry.delete(0, "end")
            self.ratio_value.set("—")
            self.missing_value.set("—")
        self.hint.configure(text="Tip: Press Enter to calculate. Copy buttons on the right.")

    def _copy(self, text: str) -> None:
        if not text or text == "—":
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self.hint.configure(text="Copied to clipboard.")

    def _maybe_recalc(self) -> None:
        if self.live_var.get():
            self._calculate(silent=True)

    def _calculate(self, silent: bool = False) -> None:
        try:
            if self.mode_var.get() == "single":
                x = _parse_float(self.single_entry.get())
                self.small_value.set(_fmt(x / PHI))
                self.large_value.set(_fmt(x * PHI))
                self.hint.configure(text="Done. Use Copy to paste results.")
            else:
                s_txt = self.small_entry.get().strip()
                l_txt = self.large_entry.get().strip()
                s = _parse_float(s_txt) if s_txt else None
                l = _parse_float(l_txt) if l_txt else None

                if s is not None and l is not None:
                    if s == 0:
                        raise ValueError("Smaller cannot be zero.")
                    ratio = l / s
                    diff = abs(ratio - PHI)
                    self.ratio_value.set(_fmt(ratio))
                    self.missing_value.set(f"Δ to φ: {_fmt(diff)}")
                    self.hint.configure(text="Ratio computed. Δ shows how close you are to φ.")
                    return

                if s is None and l is None:
                    raise ValueError("Enter at least one value.")
                if s is None:
                    self.missing_value.set(_fmt(l / PHI))
                    self.ratio_value.set("—")
                    self.hint.configure(text="Solved the missing smaller value (l / φ).")
                else:
                    self.missing_value.set(_fmt(s * PHI))
                    self.ratio_value.set("—")
                    self.hint.configure(text="Solved the missing larger value (s × φ).")

        except ValueError as e:
            msg = str(e) if str(e) else "Please enter valid numbers."
            if silent:
                self.hint.configure(text=msg)
            else:
                messagebox.showerror("Invalid Input", msg)


if __name__ == "__main__":
    GoldenRatioApp().mainloop()