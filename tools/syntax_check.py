#!/usr/bin/env python3
from __future__ import annotations

import compileall
import sys

ok = compileall.compile_dir(".", quiet=1)
raise SystemExit(0 if ok else 1)
