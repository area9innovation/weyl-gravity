"""Memory-bounded launcher for the exact Volterra-envelope proof groups."""
from __future__ import annotations

import os
import sys
from pathlib import Path


PRODUCER = Path(__file__).resolve().parent / "infinity_volterra_envelope.py"


if __name__ == "__main__":
    os.execv(sys.executable, [sys.executable, str(PRODUCER),
                              "--verify-sequence-index", "0"])
