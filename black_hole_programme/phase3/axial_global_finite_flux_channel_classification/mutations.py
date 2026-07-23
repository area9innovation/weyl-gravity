"""Mutation tests for the fail-closed classifier boundary."""

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

    dropped_extra = copy.deepcopy(base)
    dropped_extra["basis_contract"]["additional_origin_columns"] = [0]
    mutations.append(("delete-additional-coordinate", dropped_extra))

    wrong_selector = copy.deepcopy(base)
    wrong_selector["basis_contract"]["raw_future_regular_selector"] = [0, 1, 4]
    mutations.append(("apply-public-selector-to-raw", wrong_selector))

    swapped = copy.deepcopy(base)
    swapped["classifier_contract"]["conservation"] = "GHplus+gminus-gplus=0"
    mutations.append(("swap-Iminus-Iplus-orientation", swapped))

    identify_currents = copy.deepcopy(base)
    identify_currents["forbidden_promotions"][
        "radial_current_identified_with_null_flux"
    ] = True
    mutations.append(("identify-radial-and-null-current", identify_currents))

    flatten = copy.deepcopy(base)
    flatten["forbidden_promotions"]["exceptional_wall_flattened"] = True
    mutations.append(("flatten-exceptional-wall", flatten))

    positive = copy.deepcopy(base)
    positive["forbidden_promotions"]["positive_metric_inferred_from_inertia"] = True
    mutations.append(("infer-positive-metric-from-inertia", positive))

    global_mode = copy.deepcopy(base)
    global_mode["claim_flags"]["global_connection_imported"] = True
    mutations.append(("invent-global-connection", global_mode))

    full_scattering = copy.deepcopy(base)
    full_scattering["forbidden_promotions"][
        "partial_relation_called_full_scattering"
    ] = True
    mutations.append(("call-partial-relation-full-scattering", full_scattering))

    formal_global = copy.deepcopy(base)
    formal_global["forbidden_promotions"][
        "formal_infinity_vector_called_global"
    ] = True
    mutations.append(("call-formal-vector-global", formal_global))

    for name, mutation in mutations:
        if not rejected(mutation):
            raise SystemExit("FAIL: mutation survived: " + name)
        print("PASS mutation rejected:", name)


if __name__ == "__main__":
    main()
