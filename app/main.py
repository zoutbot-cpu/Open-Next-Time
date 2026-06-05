#!/usr/bin/env python3
"""
Open Next Time - Cosmic GUI Prototype

Visual prototype only.
Uses a starfield / nebula background and a faux translucent content pane.
No keyboard writes are performed in this build.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path


APP_NAME = "Open Next Time"
DEVICE_WIRED = "320F:5055"
DEVICE_DONGLE = "320F:5088"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} - Cosmic Prototype")
        self.geometry("1220x780")
        self.minsize(1100, 700)

        self.bg_image = tk.PhotoImage(file=str(Path(__file__).parent / "assets" / "background.png"))
        self.keyboard_preview_image = tk.PhotoImage(file=str(Path(__file__).parent / "assets" / "vendor_keyboard_preview.png"))
        self.selected_tab = "Keymap"

        self.selected_key_var = tk.StringVar(value="None")
        self.selected_cli_name = None
        self.output_key_var = tk.StringVar(value="home")
        self.device_status_var = tk.StringVar(value=f"Wired target: {DEVICE_WIRED}")
        self.mode_var = tk.StringVar(value="Use wired mode for configuration")
        self.target_device_var = tk.StringVar(value="Auto-detect wired VS11K09A (320F:5055)")

        self.tab_buttons = {}
        self.tab_frames = {}

        self._build_ui()
        self._show_tab("Keymap")
        self._log("Cosmic prototype started.")
        self._log("Visual shell only. HID writes are disabled.")

    def _build_ui(self):
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)

        self.canvas_bg = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)

        # Top title
        self.title_id = self.canvas.create_text(
            34, 28, anchor="nw",
            text=APP_NAME,
            fill="#f4f6ff",
            font=("Segoe UI", 22, "bold")
        )
        self.subtitle_id = self.canvas.create_text(
            34, 62, anchor="nw",
            text="A safer open keyboard configurator for VS11K09A / X-98-GMKB boards",
            fill="#c4cede",
            font=("Segoe UI", 10)
        )

        # Action buttons
        self.scan_btn = tk.Button(
            self, text="Scan Device", command=self.scan_device,
            bg="#223043", fg="#f5fbff", activebackground="#314866", activeforeground="#ffffff",
            relief="flat", padx=14, pady=7
        )
        self.export_btn = tk.Button(
            self, text="Export Plan", command=self.export_plan,
            bg="#223043", fg="#f5fbff", activebackground="#314866", activeforeground="#ffffff",
            relief="flat", padx=14, pady=7
        )
        self.scan_btn_win = self.canvas.create_window(980, 28, anchor="nw", window=self.scan_btn)
        self.export_btn_win = self.canvas.create_window(1090, 28, anchor="nw", window=self.export_btn)

        # Tab bar
        self.tab_bar_y = 104
        tab_names = ["Keymap", "Lighting", "Settings", "Protocol Notes"]
        x = 34
        for name in tab_names:
            btn = tk.Button(
                self, text=name, command=lambda n=name: self._show_tab(n),
                bg="#172233", fg="#dfe8f7", activebackground="#243651", activeforeground="#ffffff",
                relief="flat", padx=18, pady=9, font=("Segoe UI", 10, "bold")
            )
            self.tab_buttons[name] = btn
            self.canvas.create_window(x, self.tab_bar_y, anchor="nw", window=btn)
            x += 140 if name != "Protocol Notes" else 160

        # Main content pane
        self.pane_rect = self.canvas.create_rectangle(
            28, 150, 1192, 742,
            fill="#0d1018", outline="#89a9d8", width=1,
            stipple="gray50"
        )

        self.pane_host = tk.Frame(self, bg="#131926", bd=0, highlightthickness=0)
        self.pane_window = self.canvas.create_window(42, 164, anchor="nw", window=self.pane_host, width=1136, height=564)

        self._build_tabs()

    def _build_tabs(self):
        self._build_keymap_tab()
        self._build_lighting_tab()
        self._build_settings_tab()
        self._build_notes_tab()

    def _clear_pane(self):
        for child in self.pane_host.winfo_children():
            child.pack_forget()

    def _show_tab(self, name):
        self.selected_tab = name
        self._clear_pane()
        self.tab_frames[name].pack(fill="both", expand=True)
        self._style_tabs()

    def _style_tabs(self):
        for name, btn in self.tab_buttons.items():
            if name == self.selected_tab:
                btn.configure(bg="#6f5fa8", fg="#ffffff", activebackground="#7d6db9")
            else:
                btn.configure(bg="#172233", fg="#dfe8f7", activebackground="#243651")

    def _section(self, parent, title):
        outer = tk.Frame(parent, bg="#182032", bd=0, highlightthickness=1, highlightbackground="#31425f")
        tk.Label(
            outer, text=title, bg="#182032", fg="#f2f5fb",
            font=("Segoe UI", 11, "bold"), anchor="w"
        ).pack(fill="x", padx=12, pady=(10, 6))
        return outer

    def _build_keymap_tab(self):
        frame = tk.Frame(self.pane_host, bg="#131926")
        self.tab_frames["Keymap"] = frame

        keyboard_panel = self._section(frame, "Keyboard layout")
        keyboard_panel.pack(fill="x")

        tk.Label(
            keyboard_panel,
            text="Vendor-style preview from the cleaned app assets, scaled 20% smaller.",
            bg="#182032", fg="#a9b6ca", anchor="w"
        ).pack(fill="x", padx=12, pady=(0, 8))

        self.keyboard_canvas = tk.Canvas(
            keyboard_panel,
            width=self.keyboard_preview_image.width(),
            height=self.keyboard_preview_image.height(),
            bg="#182032",
            highlightthickness=0,
            bd=0
        )
        self.keyboard_canvas.pack(anchor="nw", padx=10, pady=(0, 12))

        self.key_items = {}
        self.selected_key_rect = None
        self.vendor_key_layout = [('Esc', 'esc', 19, 6, 32, 34), ('F1', 'f1', 97, 6, 32, 34), ('F2', 'f2', 136, 6, 32, 34), ('F3', 'f3', 174, 6, 32, 34), ('F4', 'f4', 212, 6, 32, 34), ('F5', 'f5', 271, 6, 32, 34), ('F6', 'f6', 311, 6, 32, 34), ('F7', 'f7', 349, 6, 32, 34), ('F8', 'f8', 388, 6, 32, 34), ('F9', 'f9', 445, 6, 34, 34), ('F10', 'f10', 484, 6, 34, 34), ('F11', 'f11', 523, 6, 34, 34), ('F12', 'f12', 562, 6, 34, 34), ('Delete', 'delete', 640, 6, 34, 35), ('Insert', 'insert', 678, 6, 34, 34), ('PageUp', 'pageup', 716, 6, 34, 35), ('PageDown', 'pagedown', 755, 6, 34, 35), ('`', 'grave', 19, 62, 32, 34), ('1', '1', 58, 62, 32, 34), ('2', '2', 97, 62, 32, 34), ('3', '3', 136, 62, 32, 34), ('4', '4', 174, 62, 32, 34), ('5', '5', 214, 62, 32, 34), ('6', '6', 252, 62, 32, 34), ('7', '7', 290, 62, 32, 34), ('8', '8', 330, 62, 32, 34), ('9', '9', 368, 62, 32, 34), ('0', '0', 407, 62, 32, 34), ('-', 'minus', 445, 62, 32, 34), ('+', 'equals', 485, 62, 32, 34), ('BackSpace', 'backspace', 523, 62, 72, 34), ('NumLock', 'numlock', 640, 62, 34, 34), ('Num /', 'kp_slash', 679, 62, 32, 34), ('Num *', 'kp_asterisk', 716, 62, 34, 34), ('Num -', 'kp_minus', 755, 62, 34, 34), ('Tab', 'tab', 19, 101, 42, 34), ('Q', 'q', 67, 101, 32, 34), ('W', 'w', 106, 101, 32, 34), ('E', 'e', 145, 101, 32, 34), ('R', 'r', 184, 101, 32, 34), ('T', 't', 222, 101, 32, 34), ('Y', 'y', 262, 101, 32, 34), ('U', 'u', 300, 101, 32, 34), ('I', 'i', 338, 101, 32, 34), ('O', 'o', 378, 101, 32, 34), ('P', 'p', 416, 101, 32, 34), ('[', 'leftbracket', 455, 101, 32, 34), (']', 'rightbracket', 494, 101, 32, 34), ('\\', 'backslash', 533, 101, 62, 34), ('Num 7', 'kp_7', 640, 101, 34, 34), ('Num 8', 'kp_8', 679, 101, 32, 34), ('Num 9', 'kp_9', 718, 101, 34, 34), ('Num +', 'kp_plus', 755, 101, 34, 74), ('CapsLock', 'capslock', 19, 140, 61, 35), ('A', 'a', 86, 140, 32, 35), ('S', 's', 125, 140, 32, 35), ('D', 'd', 164, 140, 32, 35), ('F', 'f', 203, 140, 32, 35), ('G', 'g', 242, 140, 32, 35), ('H', 'h', 281, 140, 32, 35), ('J', 'j', 319, 140, 32, 35), ('K', 'k', 358, 140, 32, 35), ('L', 'l', 397, 140, 32, 35), (';', 'semicolon', 434, 140, 34, 35), ("'", 'quote', 475, 140, 32, 35), ('Enter', 'enter', 512, 140, 83, 35), ('Num 4', 'kp_4', 640, 142, 34, 34), ('Num 5', 'kp_5', 679, 142, 32, 34), ('Num 6', 'kp_6', 716, 142, 34, 34), ('Shift', 'leftshift', 19, 180, 80, 35), ('Z', 'z', 106, 180, 32, 35), ('X', 'x', 144, 180, 32, 35), ('C', 'c', 184, 180, 32, 35), ('V', 'v', 222, 180, 32, 35), ('B', 'b', 262, 180, 32, 35), ('N', 'n', 300, 180, 32, 35), ('M', 'm', 338, 180, 32, 35), (',', 'comma', 377, 180, 32, 35), ('.', 'dot', 416, 180, 32, 35), ('/', 'slash', 455, 180, 32, 35), ('Rightshift', 'rightshift', 494, 180, 62, 35), ('Num 1', 'kp_1', 640, 180, 34, 35), ('Num 2', 'kp_2', 679, 180, 32, 35), ('Num 3', 'kp_3', 718, 180, 34, 35), ('Num Enter', 'kp_enter', 755, 180, 34, 74), ('Up', 'up', 582, 190, 34, 34), ('Ctrl', 'leftctrl', 19, 220, 42, 35), ('Win', 'leftgui', 67, 220, 42, 35), ('Alt', 'leftalt', 115, 220, 42, 35), ('Space', 'space', 163, 220, 238, 35), ('Right Alt', 'rightalt', 404, 220, 35, 35), ('Fn', 'fn', 444, 220, 36, 35), ('Right Ctrl', 'rightctrl', 484, 220, 43, 35), ('Num 0', 'kp_0', 678, 220, 34, 34), ('Num .', 'kp_dot', 718, 220, 32, 34), ('Left', 'left', 545, 228, 34, 34), ('Down', 'down', 582, 228, 34, 34), ('Right', 'right', 622, 228, 34, 34)]
        self._draw_keyboard_layout()

        bottom = tk.Frame(frame, bg="#131926")
        bottom.pack(fill="both", expand=True, pady=(14, 0))

        selected_panel = self._section(bottom, "Selected mapping")
        selected_panel.pack(side="left", fill="both", expand=True, padx=(0, 12))

        row = tk.Frame(selected_panel, bg="#182032")
        row.pack(fill="x", padx=12, pady=(2, 10))

        left = tk.Frame(row, bg="#182032")
        left.pack(side="left", fill="x", expand=True, padx=(0, 12))
        right = tk.Frame(row, bg="#182032")
        right.pack(side="left", fill="x", expand=True)

        tk.Label(left, text="Physical key", bg="#182032", fg="#9fb0c8", anchor="w").pack(fill="x")
        tk.Label(
            left, textvariable=self.selected_key_var, bg="#182032", fg="#ffffff", anchor="w",
            font=("Segoe UI", 14, "bold")
        ).pack(fill="x")

        tk.Label(right, text="Output key", bg="#182032", fg="#9fb0c8", anchor="w").pack(fill="x")
        output_combo = ttk.Combobox(
            right, textvariable=self.output_key_var, state="readonly",
            values=[
                "esc", "capslock", "home", "end", "pageup", "pagedown",
                "insert", "delete", "scrolllock", "pause",
                "left", "right", "up", "down",
                "numlock", "kp_slash", "kp_asterisk", "kp_minus", "kp_plus", "kp_enter",
                "kp_0", "kp_1", "kp_2", "kp_3", "kp_4", "kp_5", "kp_6", "kp_7", "kp_8", "kp_9", "kp_dot",
                "leftctrl", "leftgui", "leftalt", "rightalt", "rightgui", "application",
                "a", "b", "c", "d", "e", "f", "j", "k", "l",
            ]
        )
        output_combo.pack(fill="x", pady=(4, 0))

        btns = tk.Frame(selected_panel, bg="#182032")
        btns.pack(fill="x", padx=12, pady=(0, 12))

        tk.Button(
            btns, text="Add to pending plan", command=self.add_mapping,
            bg="#2a796f", fg="#ffffff", activebackground="#348f84", activeforeground="#ffffff",
            relief="flat", padx=10, pady=8
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            btns, text="Dry Run", command=self.dry_run,
            bg="#33425f", fg="#ffffff", activebackground="#405377", activeforeground="#ffffff",
            relief="flat", padx=10, pady=8
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            btns, text="Apply to Keyboard", command=self.apply_plan,
            bg="#6e4e8f", fg="#ffffff", activebackground="#8160a6", activeforeground="#ffffff",
            relief="flat", padx=10, pady=8
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            btns, text="Restore Defaults", command=self.restore_defaults,
            bg="#33425f", fg="#ffffff", activebackground="#405377", activeforeground="#ffffff",
            relief="flat", padx=10, pady=8
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            btns, text="Clear Plan", command=self.clear_plan,
            bg="#33425f", fg="#ffffff", activebackground="#405377", activeforeground="#ffffff",
            relief="flat", padx=10, pady=8
        ).pack(side="left")

        plan_panel = self._section(bottom, "Pending plan")
        plan_panel.pack(side="left", fill="both", expand=False, padx=(0, 12))
        self.plan_list = tk.Listbox(
            plan_panel, bg="#0d111a", fg="#eaf0ff", selectbackground="#51668f", relief="flat", width=28, height=9
        )
        self.plan_list.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        log_panel = self._section(bottom, "Log")
        log_panel.pack(side="left", fill="both", expand=True)

        self.log_text = tk.Text(
            log_panel,
            height=9, bg="#0d111a", fg="#dfe8f7",
            insertbackground="#ffffff", relief="flat", wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _draw_keyboard_layout(self):
        c = self.keyboard_canvas
        c.delete("all")
        self.key_items.clear()
        c.create_image(0, 0, anchor="nw", image=self.keyboard_preview_image)

        for display, cli_name, x, y, w, h in self.vendor_key_layout:
            self._draw_key_hitbox(display, cli_name, x, y, w, h)

    def _draw_key_hitbox(self, display, cli_name, x, y, w, h):
        c = self.keyboard_canvas
        rect = c.create_rectangle(
            x, y, x + w, y + h,
            fill="",
            outline="",
            width=1
        )
        c.tag_bind(rect, "<Button-1>", lambda _e, name=cli_name, label=display: self.select_key_from_canvas(name, label))
        c.tag_bind(rect, "<Enter>", lambda _e, r=rect: c.itemconfigure(r, outline="#8bd0ff", width=2))
        c.tag_bind(rect, "<Leave>", lambda _e, r=rect: self._key_leave(r))
        self.key_items[cli_name] = rect

    def _key_leave(self, rect):
        if rect != self.selected_key_rect:
            self.keyboard_canvas.itemconfigure(rect, outline="", width=1)

    def select_key_from_canvas(self, cli_name, display):
        if self.selected_key_rect is not None:
            self.keyboard_canvas.itemconfigure(self.selected_key_rect, outline="", width=1)
        self.selected_key_rect = self.key_items.get(cli_name)
        if self.selected_key_rect is not None:
            self.keyboard_canvas.itemconfigure(self.selected_key_rect, outline="#60d66d", width=3)
        self.selected_key_var.set(display.replace("\\n", " ") if display.strip() else "Space")
        self.selected_cli_name = cli_name
        self._log(f"Selected physical key: {self.selected_key_var.get()} ({cli_name})")

    def _build_lighting_tab(self):
        frame = tk.Frame(self.pane_host, bg="#131926")
        self.tab_frames["Lighting"] = frame

        top = self._section(frame, "Lighting")
        top.pack(fill="both", expand=True)

        tk.Label(top, text="RGB support is parked for now, but this shows the visual direction.",
                 bg="#182032", fg="#a9b6ca", anchor="w").pack(fill="x", padx=12, pady=(0, 14))

        tk.Label(top, text="Mode", bg="#182032", fg="#f1f5ff", anchor="w").pack(fill="x", padx=12)
        ttk.Combobox(
            top, state="readonly",
            values=["Normal", "Breath", "Spectrum", "Wave", "Rain", "Reaction", "Ripples", "Stars", "Custom", "Off"]
        ).pack(fill="x", padx=12, pady=(4, 14))

        tk.Label(top, text="Brightness", bg="#182032", fg="#f1f5ff", anchor="w").pack(fill="x", padx=12)
        scale = tk.Scale(top, from_=0, to=255, orient="horizontal", bg="#182032", fg="#dfe8f7",
                         highlightthickness=0, troughcolor="#273551")
        scale.pack(fill="x", padx=12)

        btn_row = tk.Frame(top, bg="#182032")
        btn_row.pack(fill="x", padx=12, pady=(14, 12))
        tk.Button(btn_row, text="All Light", bg="#2a796f", fg="#ffffff", relief="flat", padx=10, pady=8).pack(side="left", padx=(0, 8))
        tk.Button(btn_row, text="Complete Extinction", bg="#33425f", fg="#ffffff", relief="flat", padx=10, pady=8).pack(side="left")

    def _build_settings_tab(self):
        frame = tk.Frame(self.pane_host, bg="#131926")
        self.tab_frames["Settings"] = frame

        status = self._section(frame, "Device status")
        status.pack(fill="x")

        row = tk.Frame(status, bg="#182032")
        row.pack(fill="x", padx=12, pady=(0, 12))

        left = tk.Frame(row, bg="#182032")
        left.pack(side="left", fill="x", expand=True)
        right = tk.Frame(row, bg="#182032")
        right.pack(side="left", fill="x", expand=True)

        tk.Label(left, text="Detected device", bg="#182032", fg="#9fb0c8", anchor="w").pack(fill="x")
        tk.Label(left, textvariable=self.device_status_var, bg="#182032", fg="#ffffff",
                 font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x")

        tk.Label(right, text="Mode hint", bg="#182032", fg="#9fb0c8", anchor="w").pack(fill="x")
        tk.Label(right, textvariable=self.mode_var, bg="#182032", fg="#ffffff", anchor="w").pack(fill="x")

        target_panel = self._section(frame, "Target keyboard")
        target_panel.pack(fill="x", pady=(14, 0))

        tk.Label(
            target_panel,
            text="Select the device family/target. This is a UI placeholder for future multi-keyboard support.",
            bg="#182032", fg="#a9b6ca", anchor="w"
        ).pack(fill="x", padx=12, pady=(0, 6))

        self.target_combo = ttk.Combobox(
            target_panel,
            textvariable=self.target_device_var,
            state="readonly",
            values=[
                "Auto-detect wired VS11K09A (320F:5055)",
                "VS11K09A / X-98-GMKB wired USB (320F:5055)",
                "VS11K09A / X-98-GMKB 2.4GHz dongle (320F:5088) - input only for now",
                "NT75 (future target)",
                "Custom VID:PID (future)",
            ],
        )
        self.target_combo.pack(fill="x", padx=12, pady=(0, 12))
        self.target_combo.bind("<<ComboboxSelected>>", self._target_changed)

        toggles = self._section(frame, "Known vendor settings")
        toggles.pack(fill="x", pady=(14, 0))

        for text in ["Windows Lock", "Exchange Key / WASD", "N-Key", "1000 Hz report rate"]:
            var = tk.BooleanVar(value=False)
            tk.Checkbutton(
                toggles, text=text, variable=var,
                bg="#182032", fg="#eef3ff", selectcolor="#24304a",
                activebackground="#182032", activeforeground="#ffffff",
                anchor="w"
            ).pack(fill="x", padx=12, pady=2)

        recovery = self._section(frame, "Recovery")
        recovery.pack(fill="both", expand=True, pady=(14, 0))

        notes = (
            "If wired mode stops working:\n"
            "1. Unplug USB-C and remove dongle.\n"
            "2. Turn battery switch OFF.\n"
            "3. Wait about 20 seconds.\n"
            "4. Turn battery switch ON.\n"
            "5. Plug USB-C back in.\n"
            "6. Press Fn + 5 if needed.\n\n"
            "Known modes:\n"
            "Fn + 1 / 2 / 3 = Bluetooth profiles\n"
            "Fn + 4 = 2.4GHz receiver mode\n"
            "Fn + 5 = wired/main mode"
        )
        msg = tk.Text(recovery, bg="#0d111a", fg="#dfe8f7", relief="flat", height=11, wrap="word")
        msg.insert("1.0", notes)
        msg.config(state="disabled")
        msg.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _build_notes_tab(self):
        frame = tk.Frame(self.pane_host, bg="#131926")
        self.tab_frames["Protocol Notes"] = frame

        panel = self._section(frame, "Current confirmed protocol")
        panel.pack(fill="both", expand=True)

        notes = (
            "Confirmed:\n"
            "- Wired USB mode: 320F:5055\n"
            "- Dongle mode: 320F:5088, vendor app does not detect it\n"
            "- Config interface in wired mode: MI_01 & Col04\n"
            "- 64-byte reports, report ID 0x04\n"
            "- 0x01 start transaction\n"
            "- 0x02 commit/end transaction\n"
            "- 0x09 keymap blob write\n"
            "- 0x06 settings / lighting config\n"
            "- 0x0b custom RGB blob write\n\n"
            "Safe today:\n"
            "- Normal key remaps like CapsLock -> Esc, PageUp -> Home\n\n"
            "Not solved yet:\n"
            "- Modifier bottom row behavior\n"
            "- Windows/Mac or Win/Alt swap mode\n"
            "- Mouse/multimedia/office/special key encodings\n"
        )
        txt = tk.Text(panel, bg="#0d111a", fg="#dfe8f7", relief="flat", wrap="word")
        txt.insert("1.0", notes)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _display_to_cli_name(self, key):
        mapping = {
            "Esc": "esc", "Caps": "capslock", "LShift": "leftshift", "RShift": "rightshift",
            "LCtrl": "leftctrl", "LWin": "leftgui", "LAlt": "leftalt", "RAlt": "rightalt",
            "AltGr": "rightalt", "PgUp": "pageup", "PgDn": "pagedown", "Del": "delete",
            "Ins": "insert", "Backspace": "backspace", "Enter": "enter", "Space": "space",
            "Left": "left", "Right": "right", "Up": "up", "Down": "down", "`": "grave",
            "\\": "backslash", "[": "leftbracket", "]": "rightbracket", ";": "semicolon",
            "'": "quote", ",": "comma", ".": "dot", "/": "slash", "-": "minus", "=": "equals",
        }
        return mapping.get(key, key.lower())

    def select_key(self, key):
        self.selected_key_var.set(key)
        self._log(f"Selected physical key: {key}")

    def add_mapping(self):
        key = self.selected_key_var.get()
        output = self.output_key_var.get()
        if key == "None":
            messagebox.showinfo("No key selected", "Click a key on the layout first.")
            return
        physical = getattr(self, "selected_cli_name", self._display_to_cli_name(key))
        mapping = f"{physical}={output}"
        self.plan_list.insert("end", mapping)
        self._log(f"Added mapping: {mapping}")

    def clear_plan(self):
        self.plan_list.delete(0, "end")
        self._log("Cleared pending plan.")

    def dry_run(self):
        mappings = list(self.plan_list.get(0, "end"))
        if not mappings:
            self._log("Dry-run requested, but no mappings are pending.")
            return
        self._log("Dry-run plan:")
        for m in mappings:
            self._log(f"  --map {m}")

    def apply_plan(self):
        mappings = list(self.plan_list.get(0, "end"))
        if not mappings:
            self._log("Apply requested, but no mappings are pending.")
            return
        self._log("Apply clicked. HID writing is disabled in this visual prototype.")
        cmd = "py vs11k09a_keymapper.py " + " ".join(f"--map {m}" for m in mappings) + " --apply"
        self._log("Would run:")
        self._log("  " + cmd)

    def restore_defaults(self):
        self._log("Restore defaults clicked.")
        self._log("Would run:")
        self._log("  py vs11k09a_keymapper.py --restore-defaults --apply")

    def export_plan(self):
        mappings = list(self.plan_list.get(0, "end"))
        if not mappings:
            self._log("No pending mappings to export.")
            return
        self._log("Exported plan:")
        for m in mappings:
            self._log(f"  --map {m}")

    def _target_changed(self, _event=None):
        target = self.target_device_var.get()
        self._log(f"Target selected: {target}")
        if "NT75" in target:
            self.mode_var.set("Future target selected")
        elif "5088" in target:
            self.mode_var.set("Dongle mode is input-only for now")
        else:
            self.mode_var.set("Use wired mode for configuration")

    def scan_device(self):
        target = self.target_device_var.get()
        self.device_status_var.set(f"Selected target: {target}")
        self._log("Scan clicked. Prototype does not enumerate HID yet.")

    def _log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{ts}] {msg}\n")
        self.log_text.see("end")

    def _on_resize(self, event):
        w = max(event.width, self.bg_image.width())
        h = max(event.height, self.bg_image.height())
        self.canvas.coords(self.canvas_bg, 0, 0)

        # Stretch content bounds with window
        right = event.width - 28
        bottom = event.height - 28
        self.canvas.coords(self.pane_rect, 28, 150, right, bottom)
        self.canvas.coords(self.pane_window, 42, 164)
        self.canvas.itemconfigure(self.pane_window, width=max(900, event.width - 84), height=max(460, event.height - 206))

        # Right top buttons
        self.canvas.coords(self.scan_btn_win, event.width - 230, 28)
        self.canvas.coords(self.export_btn_win, event.width - 118, 28)


if __name__ == "__main__":
    app = App()
    app.mainloop()
