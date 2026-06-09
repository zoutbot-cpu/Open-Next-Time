# Open Next Time

Open Next Time is a Python/PyQt6 prototype for a safer open keyboard configurator.

Current target:

```text
Next Time NT980 / VS11K09A / X-98-GMKB
Wired USB VID:PID: 320F:5055
2.4GHz dongle VID:PID: 320F:5088
```

The GUI is currently visual-first and intentionally conservative. It does **not** perform real HID writes yet.

## Run

From the repo root:

```powershell
py -m app.main
```

or:

```powershell
py open_next_time_gui.py
```

No external packages are required for the GUI prototype.

## Current status

Working / present:

```text
- Cosmic background
- Vendor-style keyboard preview
- Keyboard preview scaled 20% smaller
- Clickable keyboard hitboxes
- Pending remap plan UI
- Target keyboard selector
- Placeholder support for future NT75 target
- Settings and protocol notes tabs
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
- Modifier remapping
- Mouse key assignments
- Multimedia key assignments
- Office key assignments
- RGB writing
- Dongle-mode configuration writes
```

## Safety rule

Default behavior must stay dry-run / preview-first.

Do not write to HID devices unless the user explicitly confirms an apply action.

Modifier remapping is currently unsafe and should not be implemented from the failed v4/v5 experiments.

## Project structure

```text
app/
  main.py
  assets/
    background.png
    vendor_keyboard_preview.png
  layouts/
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

## Suggested first Codex task

Refactor without changing behavior:

```text
Move GUI layout data out of app/main.py into app/layouts/vs11k09a.py.
Keep the app runnable with: py -m app.main.
Do not add HID writing yet.
```

Generated: 2026-06-05
