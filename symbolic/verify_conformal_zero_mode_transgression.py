#!/usr/bin/env python3
"""Repository entry point for the algebraic zero-mode suspension."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from field_bv_identification.polarized_state.verify_zero_mode_transgression import main


if __name__ == "__main__":
    main()
