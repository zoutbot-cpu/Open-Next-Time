# Roadmap

## Phase 1: Make the GUI project clean

- Keep app runnable with `py -m app.main`
- Move layout data into `app/layouts/vs11k09a.py`
- Keep assets in `app/assets`
- Keep behavior visual-only
- Add syntax check script
- Add basic smoke test

## Phase 2: Dry-run backend

- Convert pending GUI mappings into CLI-style mapping plans
- Validate mapping names
- Show generated packets or command preview
- Do not write to HID yet

## Phase 3: Safe normal-key writing

- Add optional HID backend
- Only support normal key remaps at first
- Require confirmation dialog
- Refuse modifier remaps until decoded

## Phase 4: Protocol tools

- Extract report ID 0x04 packets from pcapng
- Validate checksums
- Diff keymap blobs
- Create capture manifest summaries

## Phase 5: Future targets

- Add target abstraction
- Add VS11K09A target
- Add NT75 placeholder
- Add custom VID:PID placeholder

## Explicitly blocked for now

- Modifier remapping
- Mouse key writing
- Multimedia key writing
- Office key writing
- RGB writing
- Writing configuration over 2.4GHz dongle mode
