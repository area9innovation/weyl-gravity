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

    false_bound = copy.deepcopy(base)
    false_bound["endpoint_grams"]["Iplus"]["uniform_auxiliary_L2_control"][
        "spectral_operator_norm_upper_bound"
    ] = "640"
    mutations.append(("understate-uniform-operator-bound", false_bound))

    dropped_inverse = copy.deepcopy(base)
    dropped_inverse["endpoint_grams"]["Iminus"]["uniform_auxiliary_L2_control"][
        "inverse_frobenius_squared"
    ]["certified_maximum"] = "0"
    mutations.append(("erase-inverse-norm-bound", dropped_inverse))

    wrong_conservation = copy.deepcopy(base)
    wrong_conservation["endpoint_grams"]["orientation"][
        "scattering_convention"
    ] = "T^dagger*J_out*T=-J_in"
    mutations.append(("flip-incoming-conservation-sign", wrong_conservation))

    unrestricted = copy.deepcopy(base)
    unrestricted["claim_flags"][
        "unrestricted_improvement_invariance_certified"
    ] = True
    mutations.append(("invent-unrestricted-improvement-invariance", unrestricted))

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
