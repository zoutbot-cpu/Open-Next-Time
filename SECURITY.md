# Security and Safety

This project talks to USB HID devices, so safety matters.

## Current GUI state

The GUI prototype does not write to keyboards.

## Rules for future HID writing

- Dry-run first by default
- Require explicit confirmation before writing
- Prefer wired USB mode
- Refuse unknown targets
- Do not write to dongle mode unless tested
- Do not implement modifier remapping until decoded
- Keep recovery instructions visible in the app

## Do not commit

- Vendor EXE files
- Vendor DLL files
- Private logs with usernames
- Raw captures containing sensitive host/device paths unless the repo is private
