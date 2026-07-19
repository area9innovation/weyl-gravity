#!/usr/bin/env python3
"""Independent verifier for the nine odd-L highest-weight zero subspaces."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_odd_L_highest_weight_zero_subspaces.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_odd_L_highest_weight_zero_subspaces.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == sha(SCHEMA)
    parent_path = ROOT / value["provenance"]["parent"]
    assert value["provenance"]["parent_sha256"] == sha(parent_path)
    parent = json.loads(parent_path.read_text())
    parent_odd = [item for item in parent["physical_fibres"] if item["output_ell"] in (1, 3)]
    witnesses = value["witnesses"]
    assert [item["candidate_index"] for item in witnesses] == [1, 2, 6, 10, 14, 16, 17, 18, 20]
    assert len(parent_odd) == len(witnesses) == 9

    scalar_count = 0
    subspace_dimension = 0
    for source, witness in zip(parent_odd, witnesses, strict=True):
        assert source["fibre_id"] == witness["fibre_id"]
        output_ell = int(source["output_ell"])
        assert output_ell < 4
        assert clebsch_gordan(2, 2, output_ell, 2, 2, 4) == 0
        expected_dimension = 2 * (
            int(source["first_branch_multiplicity_per_parity"])
            + int(source["second_branch_multiplicity_per_parity"])
        )
        assert witness["highest_weight_subspace_dimension_over_C"] == expected_dimension
        assert witness["target_scalar_equations_vanishing"] == source["scalar_magnetic_equations"]
        assert witness["temporal_signs"] == source["temporal_signs"]
        if output_ell == 1:
            assert source["temporal_channel"] == "DIFFERENCE"
            assert source["temporal_signs"] == [1, -1]
            assert "positive-frequency reality partner has m=-2" in witness["real_tangent_completion"]
        else:
            assert source["temporal_channel"] == "SUM"
            assert source["temporal_signs"] == [1, 1]
        scalar_count += int(source["scalar_magnetic_equations"])
        subspace_dimension += expected_dimension

    summary = value["summary"]
    assert (
        summary["classified_physical_fibres"],
        summary["L1_difference_fibres"],
        summary["L3_sum_fibres"],
        summary["target_scalar_equations_vanishing"],
        summary["sum_of_highest_weight_subspace_dimensions_over_C"],
        summary["remaining_cross_fibre_physical_fibres_without_full_decomposition"],
    ) == (9, 3, 6, scalar_count, subspace_dimension, 16)
    classification = value["classification"]
    assert classification["all_nine_odd_L_highest_weight_zero_subspaces_certified"]
    assert classification["mixed_nonzero_points_certified_on_every_odd_L_fibre"]
    assert not classification["complete_odd_L_zero_varieties_classified"]
    assert not classification["same_fibre_quadratic_sources_classified"]
    assert not classification["taub_common_zero_intersection_classified"]
    assert not classification["complete_two_fibre_tangent_cone_classified"]
    assert not classification["causal_or_quantum_claim"]


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_ODD_L_HIGHEST_WEIGHT_ZERO_SUBSPACES independent verification: PASS")
