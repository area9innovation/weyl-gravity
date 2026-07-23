"""Mutation rails for the wave-packet null-trace audit."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from .verify import verify_document


HERE = Path(__file__).resolve().parent


def rejected(document: dict) -> bool:
    try:
        verify_document(document)
    except SystemExit:
        return True
    return False


def main() -> None:
    base = json.loads((HERE / "certificate.json").read_text())
    mutations = []

    missing_derivative = copy.deepcopy(base)
    missing_derivative["exact_remainder_derivative_audit"]["first_missing_derivative_order"] = 3
    mutations.append(("omit-one-omega-derivative", missing_derivative))

    swapped = copy.deepcopy(base)
    swapped["matching_direction_formal_trace"]["Iplus"]["basis"] = ["XI0", "XI1", "EI0"]
    mutations.append(("swap-Iplus-Iminus", swapped))

    dropped_remainder = copy.deepcopy(base)
    dropped_remainder["claim_flags"]["wavepacket_trace_constructed"] = True
    mutations.append(("drop-remainder-bound", dropped_remainder))

    for name, mutation in mutations:
        if not rejected(mutation):
            raise SystemExit("FAIL: mutation survived: " + name)
        print("PASS mutation rejected:", name)


if __name__ == "__main__":
    main()
