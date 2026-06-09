#!/usr/bin/env python3
"""
Open Next Time - PyQt6 GUI
A safer open keyboard configurator for VS11K09A / X-98-GMKB boards.
Visual prototype - no HID writes are performed in this build.
"""

from __future__ import annotations
import sys
import json
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QListWidget, QTextEdit,
    QTabWidget, QSlider, QCheckBox, QFrame, QSizePolicy,
    QMessageBox, QColorDialog, QLineEdit, QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QRadialGradient, QPixmap, QIcon, QBrush

APP_NAME = "Open Next Time"
DEVICE_WIRED = "320F:5055"
DEVICE_DONGLE = "320F:5088"

# Maps target combo text fragments -> layout JSON filename in app/layouts/
TARGET_LAYOUTS = {
    "5055": "vs11k09a.json",   # wired VS11K09A (both auto-detect and explicit)
    "5088": "vs11k09a.json",   # dongle uses same physical layout
    "NT75": "nt75.json",       # future
    "Custom": None,            # no layout file
}

def _target_to_layout(text: str) -> str | None:
    """Return the layout filename for a target combo selection, or None."""
    for key, fname in TARGET_LAYOUTS.items():
        if key in text:
            return fname
    return "vs11k09a.json"    # fallback

C_BG_DEEP    = "rgba(8,12,20,204)"
C_BG_MID     = "rgba(15,22,36,204)"
C_BG_PANEL   = "rgba(19,29,46,204)"
C_BG_SECTION = "rgba(25,35,56,204)"
C_BORDER     = "#2a3f60"
C_ACCENT     = "#4a7fc1"
C_ACCENT2    = "#7c5cbf"
C_GREEN      = "#3a9e7e"
C_TEXT       = "#dce8f8"
C_TEXT_DIM   = "#7a9ac0"
C_SELECTED   = "#60d66d"
C_HOVER      = "#8bd0ff"

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: transparent;
    color: {C_TEXT};
}}
QTabWidget::pane {{
    border: 1px solid {C_BORDER};
    background: {C_BG_PANEL};
    border-radius: 4px;
}}
QTabBar::tab {{
    background: {C_BG_MID};
    color: {C_TEXT_DIM};
    padding: 10px 22px;
    border: 1px solid {C_BORDER};
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    font-weight: bold;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background: {C_ACCENT2};
    color: white;
    border-color: {C_ACCENT2};
}}
QTabBar::tab:hover:!selected {{
    background: {C_BG_SECTION};
    color: {C_TEXT};
}}
QPushButton {{
    background: {C_BG_SECTION};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 4px;
    padding: 7px 16px;
    font-weight: 500;
}}
QPushButton:hover {{
    background: {C_ACCENT};
    border-color: {C_ACCENT};
    color: white;
}}
QPushButton:pressed {{
    background: #3a6499;
}}
QPushButton#btnApply {{
    background: {C_ACCENT2};
    border-color: {C_ACCENT2};
    color: white;
}}
QPushButton#btnApply:hover {{ background: #9470d4; }}
QPushButton#btnAdd {{
    background: {C_GREEN};
    border-color: {C_GREEN};
    color: white;
}}
QPushButton#btnAdd:hover {{ background: #48b892; }}
QComboBox {{
    background: {C_BG_SECTION};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 4px;
    padding: 5px 10px;
    min-height: 28px;
}}
QComboBox::drop-down {{
    border-left: 1px solid {C_BORDER};
    width: 22px;
    subcontrol-origin: padding;
    subcontrol-position: top right;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}}
QComboBox::down-arrow {{
    image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMCIgaGVpZ2h0PSI2IiB2aWV3Qm94PSIwIDAgMTAgNiI+PHBvbHlnb24gcG9pbnRzPSIwLDAgMTAsMCA1LDYiIGZpbGw9IiNkY2U4ZjgiLz48L3N2Zz4=");
    width: 10px;
    height: 6px;
}}
QComboBox QAbstractItemView {{
    background: {C_BG_SECTION};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    selection-background-color: {C_ACCENT};
}}
QListWidget {{
    background: {C_BG_DEEP};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 4px;
    padding: 4px;
}}
QListWidget::item:selected {{ background: {C_ACCENT}; color: white; }}
QListWidget::item:hover {{ background: {C_BG_SECTION}; }}
QTextEdit {{
    background: {C_BG_DEEP};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 4px;
    padding: 6px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}}
QSlider::groove:horizontal {{
    height: 6px;
    background: {C_BG_SECTION};
    border-radius: 3px;
    border: 1px solid {C_BORDER};
}}
QSlider::handle:horizontal {{
    background: {C_ACCENT};
    width: 16px; height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}}
QSlider::sub-page:horizontal {{ background: {C_ACCENT}; border-radius: 3px; }}
QCheckBox {{ color: {C_TEXT}; spacing: 8px; padding: 4px 0; }}
QCheckBox::indicator {{
    width: 16px; height: 16px;
    border: 1px solid {C_BORDER};
    border-radius: 3px;
    background: {C_BG_SECTION};
}}
QCheckBox::indicator:checked {{ background: {C_ACCENT}; border-color: {C_ACCENT}; }}
QScrollBar:vertical {{
    background: {C_BG_MID}; width: 8px; border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {C_BORDER}; border-radius: 4px; min-height: 24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QFrame#sectionFrame {{
    background: {C_BG_SECTION};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
}}
QLabel#sectionTitle {{
    color: {C_TEXT};
    font-size: 13px;
    font-weight: bold;
    padding: 2px 0 6px 0;
}}
QLabel#dimLabel {{ color: {C_TEXT_DIM}; font-size: 12px; }}
QLabel#valueLabel {{ color: white; font-size: 18px; font-weight: bold; }}
"""


class CosmicBackground(QWidget):
    _pixmap = None  # class-level cache so it loads once

    def __init__(self, parent=None):
        super().__init__(parent)
        if CosmicBackground._pixmap is None:
            img_path = Path(__file__).parent / "assets" / "background.png"
            CosmicBackground._pixmap = QPixmap(str(img_path))

    def paintEvent(self, event):
        p = QPainter(self)
        if CosmicBackground._pixmap and not CosmicBackground._pixmap.isNull():
            scaled = CosmicBackground._pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            # centre-crop
            x = (scaled.width()  - self.width())  // 2
            y = (scaled.height() - self.height()) // 2
            p.drawPixmap(0, 0, scaled, x, y, self.width(), self.height())
        else:
            # fallback gradient if image missing
            grad = QLinearGradient(0, 0, self.width(), self.height())
            grad.setColorAt(0.0, QColor("#070b12"))
            grad.setColorAt(1.0, QColor("#0a0f1c"))
            p.fillRect(self.rect(), grad)
        p.end()


class KeyButton(QPushButton):
    def __init__(self, label: str, cli_name: str, parent=None):
        super().__init__(label, parent)
        self.cli_name = cli_name
        self.setMinimumHeight(32)
        self._set_style(False)

    def _set_style(self, selected: bool):
        if selected:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {C_SELECTED}; color: #0a1a0a;
                    border: 2px solid {C_SELECTED}; border-radius: 3px;
                    font-size: 10px; font-weight: bold; padding: 1px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: #1a2840; color: {C_TEXT};
                    border: 1px solid #2a3f60; border-radius: 3px;
                    font-size: 10px; padding: 1px;
                }}
                QPushButton:hover {{
                    background: #223555; border-color: {C_HOVER}; color: {C_HOVER};
                }}
            """)

    def setSelected(self, val: bool):
        self._set_style(val)


def make_section(title: str):
    frame = QFrame()
    frame.setObjectName("sectionFrame")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 10, 14, 14)
    layout.setSpacing(8)
    lbl = QLabel(title)
    lbl.setObjectName("sectionTitle")
    layout.addWidget(lbl)
    return frame, layout


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} — Keyboard Configurator")
        icon_path = Path(__file__).parent / "assets" / "favicon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self.resize(1260, 820)
        self.setMinimumSize(1100, 700)
        # Place on primary screen, vertically centred but shifted down 50 px
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            screen.x() + (screen.width()  - 1260) // 2,
            screen.y() + (screen.height() -  820) // 2 + 50,
        )

        self._selected_key: str | None = None
        self._selected_btn: KeyButton | None = None
        self._key_buttons: dict[str, KeyButton] = {}
        # Load keyboard layout from JSON
        self._current_layout_file = "vs11k09a.json"
        layout_file = Path(__file__).parent / "layouts" / self._current_layout_file
        with open(layout_file, "r", encoding="utf-8") as f:
            self._kb_layout = json.load(f)

        root = CosmicBackground()
        root.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(20, 16, 20, 16)
        root_layout.setSpacing(12)
        root_layout.addWidget(self._build_header())

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBar().setStyleSheet("QTabBar::tab { margin-right: 6px; }")
        root_layout.addWidget(self.tabs, 1)

        self._build_keymap_tab()
        self._build_lighting_tab()
        self._build_settings_tab()
        self._build_notes_tab()

        self._log("Open Next Time started.")
        self._log("Visual shell only — HID writes are disabled.")

    def _build_header(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        title = QLabel(APP_NAME)
        title.setStyleSheet("color: #e8f0ff; font-size: 22px; font-weight: bold; background: transparent;")
        sub = QLabel("A safer open keyboard configurator for VS11K09A / X-98-GMKB boards")
        sub.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 11px; background: transparent;")
        col = QVBoxLayout()
        col.setSpacing(2)
        col.addWidget(title)
        col.addWidget(sub)
        h.addLayout(col)
        h.addStretch()
        scan_btn = QPushButton("Scan Device")
        scan_btn.clicked.connect(self.scan_device)
        export_btn = QPushButton("Export Plan")
        export_btn.clicked.connect(self.export_plan)
        reload_btn = QPushButton("⟳ Reload Layout")
        reload_btn.setToolTip("Reload keyboard layout from JSON without restarting")
        reload_btn.clicked.connect(self.reload_layout)
        h.addWidget(reload_btn)
        h.addWidget(scan_btn)
        h.addWidget(export_btn)
        return w

    def _build_keymap_tab(self):
        w = QWidget()
        outer = QVBoxLayout(w)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(12)

        kb_frame, kb_layout = make_section("Keyboard layout")
        hint = QLabel("Click a key to select it, then choose an output and click Add to plan.")
        hint.setObjectName("dimLabel")
        kb_layout.addWidget(hint)
        self._kb_section_layout = kb_layout   # stored for live reload
        self._build_key_grid(kb_layout)
        outer.addWidget(kb_frame)

        bottom = QHBoxLayout()
        bottom.setSpacing(12)

        # ── Mapping panel ─────────────────────────────────────────────────────
        map_frame, map_layout = make_section("Selected mapping")
        map_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        LABEL_W = 100  # shared width for both row labels

        # Physical key display — read-only box, aligned with Button type
        phys_row = QHBoxLayout()
        lp = QLabel("Physical key"); lp.setObjectName("dimLabel"); lp.setFixedWidth(LABEL_W)
        self.selected_key_label = QLineEdit("None")
        self.selected_key_label.setReadOnly(True)
        self.selected_key_label.setStyleSheet(
            f"background: rgba(25,35,56,192); color: white; font-size: 13px; font-weight: bold;"
            f"border: 1px solid {C_BORDER}; border-radius: 4px; padding: 4px 8px;"
        )
        phys_row.addWidget(lp)
        phys_row.addWidget(self.selected_key_label, 1)
        map_layout.addLayout(phys_row)

        # Button type selector
        type_row = QHBoxLayout()
        type_lbl = QLabel("Button type"); type_lbl.setObjectName("dimLabel"); type_lbl.setFixedWidth(LABEL_W)
        self.btn_type_combo = QComboBox()
        self.btn_type_combo.addItems([
            "Standard Key",
            "Function Key",
            "Mouse Key",
            "Multimedia Key",
            "Combination Key",
        ])
        type_row.addWidget(type_lbl)
        type_row.addWidget(self.btn_type_combo, 1)
        map_layout.addLayout(type_row)

        # Output key selector — stacked pages per button type
        out_lbl = QLabel("Output key"); out_lbl.setObjectName("dimLabel")
        map_layout.addWidget(out_lbl)

        self._output_stack = QStackedWidget()

        # Page 0 — Standard Key
        p0 = QWidget()
        p0l = QHBoxLayout(p0); p0l.setContentsMargins(0,0,0,0)
        self.std_combo = QComboBox()
        self.std_combo.addItems([
            "a","b","c","d","e","f","g","h","i","j","k","l","m",
            "n","o","p","q","r","s","t","u","v","w","x","y","z",
            "0","1","2","3","4","5","6","7","8","9",
            "minus","equals","leftbracket","rightbracket","backslash",
            "semicolon","quote","grave","comma","dot","slash",
            "backspace","tab","space",
        ])
        p0l.addWidget(self.std_combo)
        self._output_stack.addWidget(p0)

        # Page 1 — Function Key
        p1 = QWidget()
        p1l = QHBoxLayout(p1); p1l.setContentsMargins(0,0,0,0)
        self.fn_combo = QComboBox()
        self.fn_combo.addItems([
            "esc","enter","shift (left)","shift (right)",
            "ctrl (left)","ctrl (right)","alt (left)","alt (right)",
            "capslock","numlock","scrolllock","pause","insert","delete",
            "home","end","pageup","pagedown",
            "left","right","up","down",
            "f1","f2","f3","f4","f5","f6",
            "f7","f8","f9","f10","f11","f12",
            "leftgui","rightgui","application","fn",
        ])
        p1l.addWidget(self.fn_combo)
        self._output_stack.addWidget(p1)

        # Page 2 — Mouse Key
        p2 = QWidget()
        p2l = QHBoxLayout(p2); p2l.setContentsMargins(0,0,0,0)
        self.mouse_combo = QComboBox()
        self.mouse_combo.addItems([
            "Left Mouse Button",
            "Right Mouse Button",
            "Middle Mouse Button",
            "Mouse Button 4 (Back)",
            "Mouse Button 5 (Forward)",
            "Scroll Up",
            "Scroll Down",
        ])
        p2l.addWidget(self.mouse_combo)
        self._output_stack.addWidget(p2)

        # Page 3 — Multimedia Key
        p3 = QWidget()
        p3l = QHBoxLayout(p3); p3l.setContentsMargins(0,0,0,0)
        self.media_combo = QComboBox()
        self.media_combo.addItems([
            "Play / Pause",
            "Next Track",
            "Previous Track",
            "Stop",
            "Volume Up",
            "Volume Down",
            "Mute",
            "Open Media Player",
            "Open Browser",
            "Open Calculator",
            "Open File Manager",
            "Email",
            "Search",
            "Sleep",
        ])
        p3l.addWidget(self.media_combo)
        self._output_stack.addWidget(p3)

        # Page 4 — Combination Key  (modifier + key)
        p4 = QWidget()
        p4l = QHBoxLayout(p4); p4l.setContentsMargins(0,0,0,0); p4l.setSpacing(6)
        self.combo_mod_combo = QComboBox()
        self.combo_mod_combo.addItems([
            "Ctrl","Shift","Alt","Win",
            "Ctrl + Shift","Ctrl + Alt","Ctrl + Win",
            "Shift + Alt","Alt + Win",
            "Ctrl + Shift + Alt",
        ])
        plus_lbl = QLabel("+")
        plus_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        plus_lbl.setFixedWidth(16)
        self.combo_key_combo = QComboBox()
        self.combo_key_combo.addItems([
            "a","b","c","d","e","f","g","h","i","j","k","l","m",
            "n","o","p","q","r","s","t","u","v","w","x","y","z",
            "0","1","2","3","4","5","6","7","8","9",
            "f1","f2","f3","f4","f5","f6","f7","f8","f9","f10","f11","f12",
            "tab","space","enter","backspace","delete","insert",
            "home","end","pageup","pagedown","left","right","up","down",
            "minus","equals","leftbracket","rightbracket","backslash",
            "semicolon","quote","grave","comma","dot","slash",
        ])
        p4l.addWidget(self.combo_mod_combo, 1)
        p4l.addWidget(plus_lbl)
        p4l.addWidget(self.combo_key_combo, 1)
        self._output_stack.addWidget(p4)

        map_layout.addWidget(self._output_stack)
        self.btn_type_combo.currentIndexChanged.connect(self._output_stack.setCurrentIndex)

        # Action buttons
        btn_row = QHBoxLayout(); btn_row.setSpacing(8)
        add_btn = QPushButton("Add to plan"); add_btn.setObjectName("btnAdd"); add_btn.clicked.connect(self.add_mapping)
        dry_btn = QPushButton("Dry Run"); dry_btn.clicked.connect(self.dry_run)
        apply_btn = QPushButton("Apply to Keyboard"); apply_btn.setObjectName("btnApply"); apply_btn.clicked.connect(self.apply_plan)
        restore_btn = QPushButton("Restore Defaults"); restore_btn.clicked.connect(self.restore_defaults)
        clear_btn = QPushButton("Clear Plan"); clear_btn.clicked.connect(self.clear_plan)
        for b in [add_btn, dry_btn, apply_btn, restore_btn, clear_btn]:
            btn_row.addWidget(b)
        btn_row.addStretch()
        map_layout.addLayout(btn_row)
        bottom.addWidget(map_frame, 3)

        # Plan panel
        plan_frame, plan_layout = make_section("Pending plan")
        plan_frame.setFixedWidth(220)
        self.plan_list = QListWidget()
        plan_layout.addWidget(self.plan_list)
        bottom.addWidget(plan_frame)

        # Log panel
        log_frame, log_layout = make_section("Log")
        log_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.log_text = QTextEdit(); self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        bottom.addWidget(log_frame, 2)

        outer.addLayout(bottom, 1)
        self.tabs.addTab(w, "Keymap")

    def _build_key_grid(self, parent_layout: QVBoxLayout):
        """
        Builds the keyboard grid from the loaded JSON layout.

        JSON uses relative units:
          width/height  in u  (1.0 = 1u, default 1.0)
          gap_left      in u  extra space left of this key (default 0)
          gap_top       in u  extra space above this key (default 0)

        Grid resolution: U cols per 1u wide, R rows per 1u tall, G gap cols.
        Column for each key is computed by walking left-to-right per row.

        Tall keys (height > 1.0) span into the next row. Their column
        position is recorded so the next row can skip past them correctly.
        """
        U = 8    # grid cols per 1u
        R = 4    # grid rows per 1u
        G = 1    # gap between adjacent keys in grid cols
        ROW_H = self._kb_layout.get("grid", {}).get("row_height_px", 9)

        def C(u): return int(u * U)   # units -> grid cols (truncate, no drift)
        def RR(u): return int(u * R)  # units -> grid rows

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        grid = QGridLayout(container)
        grid.setSpacing(0)
        grid.setContentsMargins(0, 4, 0, 4)

        max_grid_row = 0

        # tall_keys: maps row_id -> list of (gc_start, gc_end) occupied by
        # a tall key from the previous row, so we can skip past them.
        tall_keys: dict[int, list[tuple[int,int]]] = {}

        for row_def in self._kb_layout["rows"]:
            row_id   = row_def["row_id"]
            grid_row = row_id * R
            gc = 0

            # Skip past any tall keys from the row above that occupy this col
            blocked_cols = tall_keys.get(row_id, [])
            def next_free(col, blocked=blocked_cols):
                for start, end in blocked:
                    if start <= col < end:
                        col = end + G
                return col

            for k in row_def["keys"]:
                w  = k.get("width",    1.0)
                h  = k.get("height",   1.0)
                gl = k.get("gap_left", 0.0)
                gt = k.get("gap_top",  0.0)

                cspan   = C(w)
                gt_rows = RR(gt)
                gr      = grid_row + gt_rows

                gc += C(gl)
                gc  = next_free(gc)

                if h > 1.0:
                    # Split tall key into one half-button per logical row it covers.
                    # Each half triggers the same cli, styled identically.
                    # Top half: fills this row from gr to end of logical row.
                    # Bottom halves: fill subsequent logical rows fully.
                    rows_spanned = round(h)
                    top_rspan  = R - gt_rows   # remaining rows in this logical row
                    bot_rspan  = R             # full logical row height

                    for span_idx in range(rows_spanned):
                        rspan  = top_rspan if span_idx == 0 else bot_rspan
                        btn_gr = gr if span_idx == 0 else (row_id + span_idx) * R

                        # hide top border on bottom halves, bottom border on top half
                        is_top = (span_idx == 0)
                        is_bot = (span_idx == rows_spanned - 1)
                        border_top    = "1px solid #2a3f60" if is_top  else "none"
                        border_bottom = "1px solid #2a3f60" if is_bot  else "none"
                        label  = k["label"] if is_top else ""

                        btn = KeyButton(label, k["cli"])
                        btn.setStyleSheet(f"""
                            QPushButton {{
                                background: #1a2840; color: {C_TEXT};
                                border-left:   1px solid #2a3f60;
                                border-right:  1px solid #2a3f60;
                                border-top:    {border_top};
                                border-bottom: {border_bottom};
                                border-radius: 0px;
                                font-size: 10px; padding: 1px;
                            }}
                            QPushButton:hover {{
                                background: #223555;
                                border-color: {C_HOVER};
                                color: {C_HOVER};
                            }}
                        """)
                        btn.clicked.connect(lambda checked, b=btn: self._on_key_clicked(b))
                        self._key_buttons.setdefault(k["cli"], []).append(btn)
                        grid.addWidget(btn, btn_gr, gc, rspan, cspan)
                        max_grid_row = max(max_grid_row, btn_gr + rspan)

                        # register this col range as blocked for the next row
                        next_row = row_id + span_idx + 1
                        tall_keys.setdefault(next_row, []).append((gc, gc + cspan))

                else:
                    rspan = R - gt_rows
                    btn = KeyButton(k["label"], k["cli"])
                    btn.clicked.connect(lambda checked, b=btn: self._on_key_clicked(b))
                    self._key_buttons.setdefault(k["cli"], []).append(btn)
                    grid.addWidget(btn, gr, gc, rspan, cspan)
                    max_grid_row = max(max_grid_row, gr + rspan)

                gc += cspan + G

        for i in range(max_grid_row):
            grid.setRowMinimumHeight(i, ROW_H)

        parent_layout.addWidget(container)

    def _on_key_clicked(self, btn: KeyButton):
        # Deselect all halves of the previously selected key
        if self._selected_key and self._selected_key in self._key_buttons:
            for b in self._key_buttons[self._selected_key]:
                b.setSelected(False)
        # Select all halves of the newly clicked key
        self._selected_key = btn.cli_name
        for b in self._key_buttons.get(btn.cli_name, [btn]):
            b.setSelected(True)
        # Use the label from whichever half has text
        label = next((b.text() for b in self._key_buttons.get(btn.cli_name, [btn]) if b.text()), btn.cli_name)
        self.selected_key_label.setText(label)
        self.selected_key_label.setCursorPosition(0)  # show start of text
        self._log(f"Selected: {label} ({btn.cli_name})")

    # ── Colour helper ─────────────────────────────────────────────────────────
    def _apply_rainbow_color(self):
        """Show RAINBOW indicator in the colour fields."""
        self._lighting_color = QColor(255, 0, 128)  # internal placeholder
        self._color_preview.setStyleSheet("""
            QPushButton {
                border: 1px solid #2a3f60; border-radius: 4px;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #FF0000, stop:0.17 #FF8800,
                    stop:0.33 #FFFF00, stop:0.50 #00FF00,
                    stop:0.67 #00FFFF, stop:0.83 #0000FF,
                    stop:1.0 #FF00FF);
            }
        """)
        self._r_edit.setText("#")
        self._g_edit.setText("#")
        self._b_edit.setText("#")
        self._hex_edit.setText("RAINBOW")

    def _apply_lighting_color(self, color: QColor):
        """Push a chosen colour into the preview swatch and RGB/hex fields."""
        self._lighting_color = color
        r, g, b = color.red(), color.green(), color.blue()
        hex_str = f"{r:02X}{g:02X}{b:02X}"
        self._color_preview.setStyleSheet(
            f"background-color: rgb({r},{g},{b}); border: 1px solid #2a3f60; border-radius: 4px;"
        )
        self._r_edit.setText(str(r))
        self._g_edit.setText(str(g))
        self._b_edit.setText(str(b))
        self._hex_edit.setText(hex_str)

    def _open_color_picker(self):
        color = QColorDialog.getColor(self._lighting_color, self, "Pick colour")
        if color.isValid():
            self._apply_lighting_color(color)

    def _on_rgb_edited(self):
        try:
            r = max(0, min(255, int(self._r_edit.text())))
            g = max(0, min(255, int(self._g_edit.text())))
            b = max(0, min(255, int(self._b_edit.text())))
            self._apply_lighting_color(QColor(r, g, b))
        except ValueError:
            pass

    def _on_hex_edited(self):
        txt = self._hex_edit.text().lstrip("#")
        if len(txt) == 6:
            try:
                self._apply_lighting_color(QColor(f"#{txt}"))
            except Exception:
                pass

    def _build_lighting_tab(self):
        self._lighting_color = QColor(255, 255, 255)

        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12); layout.setSpacing(12)

        # ── Keyboard preview ──────────────────────────────────────────────────
        kb_frame, kb_layout = make_section("Keyboard layout")
        hint = QLabel("Click a key to set its colour. Per-key RGB not yet implemented.")
        hint.setObjectName("dimLabel")
        kb_layout.addWidget(hint)
        self._build_key_grid(kb_layout)
        layout.addWidget(kb_frame)

        # ── Bottom row: RGB Mode (left) + Colour picker (right) ───────────────
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)

        # ── LEFT: RGB Mode panel ──────────────────────────────────────────────
        mode_frame, fl = make_section("RGB Mode")
        note = QLabel("RGB writing is not yet implemented. This shows the planned controls.")
        note.setObjectName("dimLabel"); note.setWordWrap(True)
        note.setStyleSheet("color: rgba(122,154,192,255); padding-left: 8px;")
        fl.addWidget(note)

        MODE_OPTIONS = ["Normal","Breath","Spectrum","Wave","Rain","Reaction","Ripples","Stars","Custom","Off"]

        for lbl_text, attr, lo, hi, default in [
            ("Mode",       None,               None, None, None),
            ("Brightness", "brightness_slider", 0,   255,  128),
            ("Speed",      "speed_slider",      0,   10,   5),
        ]:
            row = QHBoxLayout()
            lbl = QLabel(lbl_text)
            lbl.setStyleSheet("padding-left: 8px;")
            lbl.setFixedWidth(98)
            row.addWidget(lbl)
            if attr is None:
                combo = QComboBox()
                combo.addItems(MODE_OPTIONS)
                fm = combo.fontMetrics()
                max_w = max(fm.horizontalAdvance(m) for m in MODE_OPTIONS)
                combo.setFixedWidth(max_w + 48)
                row.addWidget(combo)
                row.addStretch()
            else:
                slider = QSlider(Qt.Orientation.Horizontal)
                slider.setRange(lo, hi); slider.setValue(default)
                val_lbl = QLabel(str(default)); val_lbl.setFixedWidth(36)
                slider.valueChanged.connect(lambda v, vl=val_lbl: vl.setText(str(v)))
                setattr(self, attr, slider)
                row.addWidget(slider, 1); row.addWidget(val_lbl)
            fl.addLayout(row)

        btn_row = QHBoxLayout(); btn_row.setSpacing(8)
        al = QPushButton("All Light"); al.setObjectName("btnAdd")
        al.clicked.connect(lambda: self._log("All Light clicked (not implemented)"))
        off = QPushButton("Lights Off")
        off.clicked.connect(lambda: self._log("Lights Off clicked (not implemented)"))
        btn_row.addWidget(al); btn_row.addWidget(off); btn_row.addStretch()
        fl.addLayout(btn_row)
        mode_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        bottom_row.addWidget(mode_frame, 1)

        # ── RIGHT: Colour picker panel ────────────────────────────────────────
        cp_frame, cp_layout = make_section("Colour")
        cp_layout.setSpacing(10)

        # 10 swatches: 9 basic colours + 1 rainbow
        SWATCHES = [
            "#FF0000", "#FF8800", "#FFFF00", "#00FF00",
            "#00FFFF", "#0000FF", "#FF00FF", "#FFFFFF",
            "#888888", "rainbow",
        ]
        swatch_row = QHBoxLayout()
        swatch_row.setSpacing(5)
        swatch_row.setContentsMargins(8, 0, 8, 0)

        SWATCH_SIZE = 28

        for sw in SWATCHES:
            btn = QPushButton()
            btn.setFixedSize(SWATCH_SIZE, SWATCH_SIZE)
            btn.setToolTip(sw if sw != "rainbow" else "Rainbow")
            if sw == "rainbow":
                btn.setStyleSheet("""
                    QPushButton {
                        border: 1px solid #2a3f60;
                        border-radius: 4px;
                        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                            stop:0 #FF0000, stop:0.17 #FF8800,
                            stop:0.33 #FFFF00, stop:0.50 #00FF00,
                            stop:0.67 #00FFFF, stop:0.83 #0000FF,
                            stop:1.0 #FF00FF);
                    }
                    QPushButton:hover { border-color: #8bd0ff; }
                """)
                btn.clicked.connect(lambda: self._apply_rainbow_color())
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {sw};
                        border: 1px solid #2a3f60;
                        border-radius: 4px;
                    }}
                    QPushButton:hover {{ border-color: #8bd0ff; }}
                """)
                c = QColor(sw)
                btn.clicked.connect(lambda checked, col=c: self._apply_lighting_color(col))
            swatch_row.addWidget(btn)

        cp_layout.addLayout(swatch_row)

        # Preview square + RGB/hex inputs
        picker_row = QHBoxLayout()
        picker_row.setContentsMargins(8, 0, 8, 0)
        picker_row.setSpacing(10)

        # Colour preview square (clickable → opens QColorDialog)
        self._color_preview = QPushButton()
        self._color_preview.setFixedSize(56, 56)
        self._color_preview.setToolTip("Click to open colour picker")
        self._color_preview.setStyleSheet(
            "background-color: rgb(255,255,255); border: 1px solid #2a3f60; border-radius: 4px;"
        )
        self._color_preview.clicked.connect(self._open_color_picker)
        picker_row.addWidget(self._color_preview)

        # RGB + Hex fields
        fields_grid = QGridLayout()
        fields_grid.setSpacing(5)
        field_style = (
            f"background: rgba(25,35,56,192); color: {C_TEXT}; "
            "border: 1px solid #2a3f60; border-radius: 4px; padding: 3px 6px;"
        )

        for col_idx, lbl_txt in enumerate(["R", "G", "B"]):
            lbl = QLabel(lbl_txt)
            lbl.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 11px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fields_grid.addWidget(lbl, 0, col_idx)

        self._r_edit = QLineEdit("255"); self._r_edit.setFixedWidth(46)
        self._g_edit = QLineEdit("255"); self._g_edit.setFixedWidth(46)
        self._b_edit = QLineEdit("255"); self._b_edit.setFixedWidth(46)
        for i, ed in enumerate([self._r_edit, self._g_edit, self._b_edit]):
            ed.setStyleSheet(field_style)
            ed.editingFinished.connect(self._on_rgb_edited)
            fields_grid.addWidget(ed, 1, i)

        hex_lbl = QLabel("#")
        hex_lbl.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 11px;")
        hex_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fields_grid.addWidget(hex_lbl, 2, 0)

        self._hex_edit = QLineEdit("FFFFFF")
        self._hex_edit.setFixedWidth(86)
        self._hex_edit.setStyleSheet(field_style)
        self._hex_edit.editingFinished.connect(self._on_hex_edited)
        fields_grid.addWidget(self._hex_edit, 2, 1, 1, 2)

        picker_row.addLayout(fields_grid)
        picker_row.addStretch()
        cp_layout.addLayout(picker_row)

        cp_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        bottom_row.addWidget(cp_frame, 1)
        layout.addLayout(bottom_row)
        layout.addStretch()
        self.tabs.addTab(w, "Lighting")

    def _build_settings_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12); layout.setSpacing(12)

        dev_frame, dev_layout = make_section("Device status")
        row = QHBoxLayout()
        col_l = QVBoxLayout()
        l1 = QLabel("Detected device"); l1.setObjectName("dimLabel")
        self.device_status_label = QLabel(f"Wired target: {DEVICE_WIRED}")
        self.device_status_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        col_l.addWidget(l1); col_l.addWidget(self.device_status_label)
        col_r = QVBoxLayout()
        l2 = QLabel("Mode hint"); l2.setObjectName("dimLabel")
        self.mode_hint_label = QLabel("Use wired mode for configuration")
        col_r.addWidget(l2); col_r.addWidget(self.mode_hint_label)
        row.addLayout(col_l, 1); row.addLayout(col_r, 1)
        dev_layout.addLayout(row)
        layout.addWidget(dev_frame)

        tgt_frame, tgt_layout = make_section("Target keyboard")
        note = QLabel("Select the device family. Placeholder for future multi-keyboard support.")
        note.setObjectName("dimLabel"); note.setWordWrap(True)
        tgt_layout.addWidget(note)
        self.target_combo = QComboBox()
        self.target_combo.addItems([
            "Auto-detect wired VS11K09A (320F:5055)",
            "VS11K09A / X-98-GMKB wired USB (320F:5055)",
            "VS11K09A / X-98-GMKB 2.4GHz dongle (320F:5088) — input only",
            "NT75 (future target)",
            "Custom VID:PID (future)",
        ])
        self.target_combo.currentTextChanged.connect(self._target_changed)
        tgt_layout.addWidget(self.target_combo)
        layout.addWidget(tgt_frame)

        tog_frame, tog_layout = make_section("Known vendor settings")
        for text in ["Windows Lock", "Exchange Key / WASD", "N-Key rollover", "1000 Hz report rate"]:
            tog_layout.addWidget(QCheckBox(text))
        layout.addWidget(tog_frame)

        rec_frame, rec_layout = make_section("Recovery")
        rec_text = QTextEdit(); rec_text.setReadOnly(True); rec_text.setFixedHeight(160)
        rec_text.setText(
            "If wired mode stops working:\n"
            "1. Unplug USB-C and remove dongle.\n"
            "2. Turn battery switch OFF.\n"
            "3. Wait about 20 seconds.\n"
            "4. Turn battery switch ON.\n"
            "5. Plug USB-C back in.\n"
            "6. Press Fn + 5 if needed.\n\n"
            "Known modes:\n"
            "  Fn + 1 / 2 / 3 = Bluetooth profiles\n"
            "  Fn + 4 = 2.4GHz receiver mode\n"
            "  Fn + 5 = wired / main mode"
        )
        rec_layout.addWidget(rec_text)
        layout.addWidget(rec_frame); layout.addStretch()
        self.tabs.addTab(w, "Settings")

    def _build_notes_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12); layout.setSpacing(12)
        frame, fl = make_section("Current confirmed protocol")
        txt = QTextEdit(); txt.setReadOnly(True)
        txt.setText(
            "Confirmed:\n"
            "  Wired USB mode:   320F:5055\n"
            "  Dongle mode:      320F:5088  (vendor app does not detect it)\n"
            "  Config interface: MI_01 & Col04\n"
            "  Report size:      64 bytes, report ID 0x04\n\n"
            "Known commands:\n"
            "  0x01  start transaction\n"
            "  0x02  commit / end transaction\n"
            "  0x09  keymap blob write\n"
            "  0x06  settings / lighting config\n"
            "  0x0b  custom RGB blob write\n\n"
            "Safe today:\n"
            "  Normal key remaps (e.g. CapsLock -> Esc, PageUp -> Home)\n\n"
            "Not solved yet:\n"
            "  Modifier bottom-row behavior\n"
            "  Windows/Mac or Win/Alt swap mode\n"
            "  Mouse / multimedia / office / special key encodings\n"
            "  RGB write protocol\n"
            "  Dongle-mode config writes\n"
        )
        fl.addWidget(txt)
        layout.addWidget(frame)
        self.tabs.addTab(w, "Protocol Notes")

    # Actions
    def add_mapping(self):
        if not self._selected_key:
            QMessageBox.information(self, "No key selected", "Click a key on the layout first.")
            return
        page = self._output_stack.currentIndex()
        if page == 0:
            output = self.std_combo.currentText()
        elif page == 1:
            output = self.fn_combo.currentText()
        elif page == 2:
            output = self.mouse_combo.currentText()
        elif page == 3:
            output = self.media_combo.currentText()
        elif page == 4:
            output = f"{self.combo_mod_combo.currentText()} + {self.combo_key_combo.currentText()}"
        else:
            output = "unknown"
        mapping = f"{self._selected_key} -> {output}"
        self.plan_list.addItem(mapping)
        self._log(f"Added mapping: {mapping}")

    def clear_plan(self):
        self.plan_list.clear()
        self._log("Cleared pending plan.")

    def dry_run(self):
        items = [self.plan_list.item(i).text() for i in range(self.plan_list.count())]
        if not items:
            self._log("Dry-run: no mappings pending."); return
        self._log("Dry-run plan:")
        for m in items:
            self._log(f"  --map {m}")

    def apply_plan(self):
        items = [self.plan_list.item(i).text() for i in range(self.plan_list.count())]
        if not items:
            self._log("Apply: no mappings pending."); return
        self._log("Apply clicked — HID writing is disabled in this prototype.")
        self._log("Would run: py vs11k09a_keymapper.py " + " ".join(f"--map {m}" for m in items) + " --apply")

    def restore_defaults(self):
        self._log("Restore defaults clicked.")
        self._log("Would run: py vs11k09a_keymapper.py --restore-defaults --apply")

    def export_plan(self):
        items = [self.plan_list.item(i).text() for i in range(self.plan_list.count())]
        if not items:
            self._log("No pending mappings to export."); return
        self._log("Exported plan:")
        for m in items: self._log(f"  {m}")

    def scan_device(self):
        self._log("Scan clicked — prototype does not enumerate HID yet.")

    def _target_changed(self, text: str):
        self._log(f"Target selected: {text}")
        if "NT75" in text:
            self.mode_hint_label.setText("Future target — not yet supported")
        elif "5088" in text:
            self.mode_hint_label.setText("Dongle mode is input-only for now")
        else:
            self.mode_hint_label.setText("Use wired mode for configuration")
        # Reload keyboard layout for the selected target
        fname = _target_to_layout(text)
        if fname:
            self.reload_layout(fname)
        else:
            self._log("No layout defined for this target.")

    def reload_layout(self, filename=None):
        """Re-read a JSON layout file and rebuild the keyboard grid in place.
        If filename is None or not a string, reloads the current layout file."""
        if not isinstance(filename, str) or not filename:
            filename = getattr(self, "_current_layout_file", None) or "vs11k09a.json"
        layout_file = Path(__file__).parent / "layouts" / filename
        if not layout_file.exists():
            self._log(f"No layout file found for this target: {filename}")
            return
        try:
            with open(layout_file, "r", encoding="utf-8") as f:
                self._kb_layout = json.load(f)
            self._current_layout_file = filename
        except Exception as e:
            self._log(f"Reload failed: {e}")
            return

        # Remove old keyboard grid widget (last item added after the hint label)
        layout = self._kb_section_layout
        # The grid container is always the last widget in the section layout
        item = layout.itemAt(layout.count() - 1)
        if item and item.widget():
            item.widget().deleteLater()
            layout.removeItem(item)

        self._key_buttons.clear()
        self._selected_btn = None   # kept for compat but unused now
        self._selected_key = None
        self.selected_key_label.setText("None")

        self._build_key_grid(layout)
        self._log("Layout reloaded from JSON.")

    def _log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{ts}] {msg}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    from PyQt6.QtGui import QFont
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(STYLESHEET)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())