#!/usr/bin/env python3
"""Compatibility entry point for the serial, bounded seven-target UCI check."""

import sys

from check_module_codegen import main

if __name__ == "__main__":
    sys.argv[1:1] = ["--module", "defense_uci"]
    sys.exit(main())
