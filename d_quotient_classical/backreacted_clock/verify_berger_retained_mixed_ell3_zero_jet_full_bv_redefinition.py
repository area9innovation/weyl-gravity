#!/usr/bin/env python3
"""Independent fast verifier for the zero-jet full-BV redefinition screen."""

from __future__ import annotations

import json

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_full_bv_coderivation_redefinition as result,
)


def verify() -> None:
    value = json.loads(result.OUTPUT.read_text())
    result.fast_validate(value)
    witness = value["normalized_dual_witness"]
    if witness["normalized_target_evaluation"] != "1":
        raise ValueError("dual witness is not normalized")
    if value["exact_matrix_audit"]["rank"] + 1 != value["exact_matrix_audit"]["augmented_rank"]:
        raise ValueError("rank obstruction ledger drifted")
    if value["PBW_augmentation_ideal"]["scalar_output_defects"]:
        raise ValueError("positive PBW words acquired a scalar component")
    flags = value["claim_flags"]
    if flags["FULL_JET_BOUNDED_CYCLIC_DEFORMATION_CLASS_DECIDED"] or flags["QUANTUM_CLAIM"]:
        raise ValueError("zero-jet screen was overpromoted")


if __name__ == "__main__":
    verify()
    print("BERGER_RETAINED_MIXED_ELL3_ZERO_JET_FULL_BV_REDEFINITION_V1 independent replay: PASS")
