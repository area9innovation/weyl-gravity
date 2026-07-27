#!/usr/bin/env python3
"""Standalone-history successor rail for the immutable V1 six-row certificate."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ci.standalone_provenance import resolve_attached_ref
from d_quotient_classical.causal_transfer import (
    verify_berger_q26_minimal_six_row_cyclic_obstruction as historical_verifier,
)


def main() -> None:
    ref = resolve_attached_ref(
        historical_verifier.PINNED_COMMIT,
        historical_verifier.PINNED_PATH,
    )
    historical_verifier.PINNED_COMMIT = ref.commit
    historical_verifier.PINNED_PATH = ref.path
    historical_verifier.verify()
    print("BERGER_Q26_MINIMAL_SIX_ROW_CYCLIC_OBSTRUCTION standalone replay: PASS")


if __name__ == "__main__":
    main()
