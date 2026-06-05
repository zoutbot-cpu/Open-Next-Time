# Packet Format Notes

Known report format:

```text
04 <checksum-lo> <checksum-hi> <command> <length> <offset-lo> <offset-hi> 00 <payload...>
```

Report size:

```text
64 bytes
```

Checksum:

```text
checksum = sum(report[3:64]) & 0xffff
```

Known commands:

```text
0x01 = start/open transaction
0x02 = commit/end transaction
0x06 = settings / lighting config
0x09 = keymap/config blob write
0x0b = custom per-key RGB blob write
```

Known target interface in wired mode:

```text
VID:PID = 320F:5055
Interface/collection = MI_01 & Col04
usage_page = 65308
usage = 146
```
