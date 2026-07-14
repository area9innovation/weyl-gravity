#!/usr/bin/env python3
"""Entry point for the canonical pure-Weyl dual-endpoint certificate."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from field_bv_identification.zero_modes.verify_dual_cokernel import main


if __name__ == "__main__":
    main()
