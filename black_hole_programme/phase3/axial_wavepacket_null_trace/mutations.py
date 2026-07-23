"""Mutation rails for the wave-packet null-trace audit."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from .verify import verify_document


HERE = Path(__file__).resolve().parent


def rejected(document: dict) -> bool:
    try:
        verify_document(document, deep=False)
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
    swapped["matching_direction_wavepacket_trace"]["Iplus"]["basis"] = ["XI0", "XI1", "EI0"]
    mutations.append(("swap-Iplus-Iminus", swapped))

    dropped_remainder = copy.deepcopy(base)
    dropped_remainder["claim_flags"]["wavepacket_trace_constructed"] = False
    mutations.append(("drop-remainder-bound", dropped_remainder))

    false_flux = copy.deepcopy(base)
    false_flux["claim_flags"]["endpoint_flux_Gram_certified"] = True
    mutations.append(("invent-endpoint-flux-Gram", false_flux))

    degraded_decay = copy.deepcopy(base)
    degraded_decay["exact_remainder_derivative_audit"]["repaired_decay_p_ij"][4][5] = 4
    mutations.append(("degrade-EI-cross-rate-decay", degraded_decay))

    weakened_q = copy.deepcopy(base)
    weakened_q["differentiated_volterra_envelope"]["q_derivative_strict_upper_bounds"][3] = "1/2"
    mutations.append(("weaken-third-derivative-contraction", weakened_q))

    for name, mutation in mutations:
        if not rejected(mutation):
            raise SystemExit("FAIL: mutation survived: " + name)
        print("PASS mutation rejected:", name)


if __name__ == "__main__":
    main()
