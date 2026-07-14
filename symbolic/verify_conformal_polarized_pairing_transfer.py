#!/usr/bin/env python3
"""Repository entry point for the selected field pairing transfer."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from field_bv_identification.polarized_state.verify_pairing_transfer import main


if __name__ == "__main__":
    main()
