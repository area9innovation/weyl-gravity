"""Memory-bounded independent launcher for the four exact residual audits."""
from __future__ import annotations

import os
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRODUCER = HERE / "infinity_metric_heads.py"


def main() -> None:
    # Replace the process between branches.  This returns all SymPy memory to
    # the OS without retaining a supervisory Python heap.
    os.execv(
        sys.executable,
        [sys.executable, str(PRODUCER), "--verify-sequence-index", "0"],
    )


if __name__ == "__main__":
    main()
