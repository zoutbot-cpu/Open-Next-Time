# Open Next Time

Open Next Time is a Python/PyQt6 keyboard configurator for Next Time keyboards.

Current target:

```text
Next Time NT980 / VS11K09A / X-98-GMKB
Wired USB VID:PID: 320F:5055
2.4GHz dongle VID:PID: 320F:5088
```

The GUI is intentionally conservative. It does **not** perform real HID writes yet.

## Requirements

```powershell
pip install PyQt6
```

## Run

From the repo root:

```powershell
py app\main.py
```

## Current status

Working / present:

```text
- PyQt6 GUI with cosmic nebula background image
- JSON-driven keyboard layout (app/layouts/vs11k09a.json)
  - Relative unit sizing (width, height, gap_left, gap_top)
  - Tall keys (Num+, Num Enter) rendered as stacked half-buttons
  - Live reload without restarting (⟳ Reload Layout button)
- Clickable keyboard grid on both Keymap and Lighting tabs
- Target keyboard selector linked to layout file
  - Placeholder support for future NT75 target
- Keymap tab:
  - Physical key read-only field
  - Button type selector: Standard / Function / Mouse / Multimedia / Combination
  - Pending remap plan with dry-run and export
- Lighting tab:
  - RGB mode, brightness and speed controls
  - 10-colour swatch panel (9 basic + rainbow)
  - Colour picker with RGB fields and hex code
- Settings tab with device status, recovery notes and vendor toggles
- Protocol Notes tab
```

Known-good protocol direction:

```text
- Normal key remapping has worked in live tests
- CapsLock -> Esc worked
- PageUp -> Home worked
```

Not safe / not implemented yet:

```text
- Real HID writes from the GUI
- Modifier remapping (unsafe, blocked from failed v4/v5 experiments)
- Mouse key assignments
- Multimedia key assignments
- Office key assignments
- RGB writing
- Dongle-mode configuration writes
```

## Safety rule

Default behavior must stay dry-run / preview-first.

Do not write to HID devices unless the user explicitly confirms an apply action.

Modifier remapping is currently unsafe and should not be implemented.

## Project structure

```text
app/
  main.py
  assets/
    background.png
    favicon.ico
  layouts/
    vs11k09a.json    ← keyboard layout, edit this to adjust key positions
    README.md

tools/
  pcap_extract_reports.py
  syntax_check.py

docs/
  vs11k09a_keyboard_notes.md
  fn_shortcuts.md
  recovery.md
  vendor_ui_map.md

protocol/
  packet_format.md
  captures_manifest.md

captures/
  README.md
```

## Adding a new keyboard layout

1. Create `app/layouts/<name>.json` following the same format as `vs11k09a.json`
2. Add an entry to `TARGET_LAYOUTS` in `app/main.py`
3. Add the target name to the combo box in `_build_settings_tab`

The layout JSON uses relative units:

```text
width / height   in u  (1.0 = standard key, 2.0 = double wide/tall)
gap_left         in u  extra space to the left of this key
gap_top          in u  extra space above this key (shifts key down within its row)
```

Generated: 2026-06-09
