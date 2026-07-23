"""Mutation rails for the axial null-endpoint flux-Gram certificate."""
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

    dropped_reconstruction = copy.deepcopy(base)
    dropped_reconstruction["current_representative"]["chart_pullback"]["metric"] = (
        "h0_t=h0_v; h1_t=h1_EF"
    )
    mutations.append(("drop-differentiated-reconstruction", dropped_reconstruction))

    swapped = copy.deepcopy(base)
    swapped["endpoint_grams"]["orientation"]["Iminus"] = (
        "the increasing-r coordinate Gram"
    )
    mutations.append(("swap-past-endpoint-orientation", swapped))

    counterterm = copy.deepcopy(base)
    counterterm["current_representative"][
        "counterterm_or_radial_improvement_added"
    ] = True
    mutations.append(("invent-current-counterterm", counterterm))

    rescaled = copy.deepcopy(base)
    rescaled["endpoint_grams"]["normalization"] = (
        "G_endpoint = Stokes-oriented i*F^r"
    )
    mutations.append(("omit-pi-alpha-rescaling", rescaled))

    false_rank = copy.deepcopy(base)
    false_rank["endpoint_grams"]["Iplus"]["classification"]["rank"] = 2
    mutations.append(("false-rank-across-pilot", false_rank))

    weakened_tail = copy.deepcopy(base)
    weakened_tail["trace_limit_theorem"]["exact_remainder_input"][
        "minimum_cross_rate_decay_p"
    ] = 4
    mutations.append(("weaken-remainder-decay", weakened_tail))

    scattering = copy.deepcopy(base)
    scattering["claim_flags"]["scattering_channels_classified"] = True
    mutations.append(("invent-scattering-promotion", scattering))

    for name, mutation in mutations:
        if not rejected(mutation):
            raise SystemExit("FAIL: mutation survived: " + name)
        print("PASS mutation rejected:", name)


if __name__ == "__main__":
    main()
