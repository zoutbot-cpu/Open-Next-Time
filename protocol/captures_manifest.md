# Captures Manifest

Raw captures are not included in this repo ZIP by default.

Reason:

```text
- pcapng files may contain local device paths
- captures may contain usernames/timestamps/host details
- raw captures should stay private unless intentionally published
```

Useful captures taken during research:

```text
USBReportRate_1000.pcapng
USBReportRate_500.pcapng
NKey.pcapng
ExchangeKeys.pcapng
WindowsLock.pcapng
Fullreset-includesrgb.pcapng
SetKey_J-Officekey-Copy.pcapng
SetKey_K-Multimedia-WWW Home.pcapng
SetKey_L-Win+D.pcapng
SetKey_L-Alt+F4.pcapng
SetKey_P-MouseLB.pcapng
```

Analysis summary:

```text
Report rate, N-Key, Exchange Key, Windows Lock, and Reset use command 0x06.
Special key assignments use command 0x09 but are not simple single-key substitutions.
```
