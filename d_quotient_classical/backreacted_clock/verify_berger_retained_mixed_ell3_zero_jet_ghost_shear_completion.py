#!/usr/bin/env python3
"""Independent fast verifier for the zero-jet ghost-shear completion."""

import json

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_zero_jet_ghost_shear_completion as result,
)


def verify() -> None:
    value = json.loads(result.OUTPUT.read_text())
    result.fast_validate(value)
    if value["extended_matrix_audit"]["rank"] != value["extended_matrix_audit"]["augmented_rank"]:
        raise ValueError("compatible rank ledger drifted")
    if value["claim_flags"]["FULL_JET_BOUNDED_CYCLIC_DEFORMATION_CLASS_DECIDED"]:
        raise ValueError("zero-page primitive was overpromoted")


if __name__ == "__main__":
    verify()
    print("BERGER_RETAINED_MIXED_ELL3_ZERO_JET_GHOST_SHEAR_COMPLETION_V1 independent replay: PASS")
