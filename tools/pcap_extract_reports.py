#!/usr/bin/env python3
"""Extract likely 64-byte keyboard reports from a pcapng/raw capture.

This is a lightweight byte-pattern tool, not a full pcap parser.
It looks for report ID 0x04 and validates the checksum format observed
for the VS11K09A keyboard.
"""

from __future__ import annotations

import argparse
from pathlib import Path


KNOWN_COMMANDS = {0x01, 0x02, 0x06, 0x09, 0x0B, 0x14, 0x25}


def valid_report(chunk: bytes) -> bool:
    if len(chunk) != 64:
        return False
    if chunk[0] != 0x04:
        return False
    if chunk[3] not in KNOWN_COMMANDS:
        return False
    checksum = chunk[1] | (chunk[2] << 8)
    return checksum == (sum(chunk[3:64]) & 0xFFFF)


def extract_reports(data: bytes) -> list[tuple[int, bytes]]:
    reports: list[tuple[int, bytes]] = []
    seen: set[bytes] = set()

    for offset in range(0, max(0, len(data) - 63)):
        chunk = data[offset:offset + 64]
        if valid_report(chunk) and chunk not in seen:
            reports.append((offset, chunk))
            seen.add(chunk)

    return reports


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("capture", type=Path)
    parser.add_argument("--show-payload", action="store_true")
    args = parser.parse_args()

    data = args.capture.read_bytes()
    reports = extract_reports(data)

    print(f"Found {len(reports)} unique reports")
    for offset, report in reports:
        cmd = report[3]
        length = report[4]
        blob_offset = report[5] | (report[6] << 8)
        checksum = report[1] | (report[2] << 8)
        print(
            f"file_off=0x{offset:08x} cmd=0x{cmd:02x} "
            f"len={length:02d} blob_off=0x{blob_offset:04x} checksum=0x{checksum:04x}"
        )
        if args.show_payload and length:
            print("  " + report[8:8 + length].hex(" "))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
