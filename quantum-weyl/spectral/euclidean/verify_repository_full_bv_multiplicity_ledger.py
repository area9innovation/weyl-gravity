#!/usr/bin/env python3
"""Independent replay of the physical round-S4 full-BV multiplicity ledger."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

try:
    from .multiplicity_export_receiver import (
        ROOT,
        validate_repository_multiplicity_export,
    )
    from .tt_hessian_dictionary_receiver import validate_tt_hessian_dictionary
except ImportError:
    from multiplicity_export_receiver import ROOT, validate_repository_multiplicity_export
    from tt_hessian_dictionary_receiver import validate_tt_hessian_dictionary


HERE = Path(__file__).resolve().parent
LEDGER = HERE / "certificates/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json"
TT_DICTIONARY = HERE / "certificates/REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1.json"

EXPECTED_FACTORS = (
    ("repository_physical_upper", "Delta_2_perp(4)", "BOSONIC", 5, -1, 2),
    ("repository_scalar_ghost", "Delta_0(-4)", "FERMIONIC", 1, 1, 2),
    ("repository_physical_lower", "Delta_2_perp(2)", "BOSONIC", 5, -1, 2),
    ("repository_vector_ghost", "Delta_1_perp(-3)", "FERMIONIC", 3, 1, 2),
)


def verify() -> dict[str, object]:
    ledger = json.loads(LEDGER.read_text())
    tt = json.loads(TT_DICTIONARY.read_text())
    commit = tt["classical_commit"]
    validate_tt_hessian_dictionary(
        tt, repository_root=ROOT, expected_classical_commit=commit
    )
    generic = validate_repository_multiplicity_export(
        ledger,
        repository_root=ROOT,
        expected_classical_commit=commit,
        expected_analytic_route="EUCLIDEAN_ELLIPTIC",
    )

    observed = tuple(
        (
            row["factor_id"],
            row["operator"],
            row["statistics"],
            row["component_rank"],
            row["determinant_exponent"]["numerator"],
            row["determinant_exponent"]["denominator"],
        )
        for row in ledger["repository_factors"]
    )
    if observed != EXPECTED_FACTORS:
        raise ValueError("physical full-BV factor ledger drifted")
    rows = {row["generator_id"]: row for row in ledger["integration_slice"]["rows"]}
    if set(rows) != {"h_TT", "xi_T", "xi_L", "omega"}:
        raise ValueError("physical full-BV integration-row coverage drifted")
    if not (
        rows["h_TT"]["component_rank"] == 5
        and rows["xi_T"]["component_rank"] == 3
        and rows["xi_L"]["component_rank"] == 1
        and rows["omega"]["component_rank"] == 1
        and "delete_10_killing_vectors" in rows["xi_T"]["zero_mode_policy_id"]
        and "delete_5_conformal_modes" in rows["omega"]["zero_mode_policy_id"]
    ):
        raise ValueError("physical row rank or priming policy drifted")

    weighted_rank = sum(
        Fraction(numerator, denominator) * rank
        for _, _, _, rank, numerator, denominator in observed
    )
    if weighted_rank != Fraction(-3):
        raise ValueError("physical determinant weighted rank drifted")
    if not (
        generic["row_coverage_complete"] is True
        and generic["factor_coverage_complete"] is True
        and generic["target_signed_rank"] == 6
        and generic["scalar_ghost_input_rank"] == 2
        and generic["scalar_ghost_output_rank"] == 1
    ):
        raise ValueError("generic full-BV receiver replay drifted")
    return {
        "result_id": ledger["result_id"],
        "classical_commit": commit,
        "operators": [row[1] for row in observed],
        "integration_row_count": len(rows),
        "repository_factor_count": len(observed),
        "target_signed_rank": generic["target_signed_rank"],
        "Z_exponent_weighted_rank": str(weighted_rank),
        "zero_mode_dimensions": {"TT": 0, "Killing": 10, "proper_conformal": 5},
        "status": "PHYSICAL_FULL_BV_LEDGER_INDEPENDENTLY_ACCEPTED",
    }


def main() -> int:
    print(json.dumps(verify(), indent=2, sort_keys=True))
    print("repository full-BV multiplicity ledger independent replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
