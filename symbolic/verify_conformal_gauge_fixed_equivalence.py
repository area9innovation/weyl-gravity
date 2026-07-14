#!/usr/bin/env python3
"""Entry point for the field-theoretic gauge-fixed equivalence certificate."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from field_bv_identification.gauge_fixed_equivalence.verify_gauge_fixed_equivalence import (
    main,
)


if __name__ == "__main__":
    main()
