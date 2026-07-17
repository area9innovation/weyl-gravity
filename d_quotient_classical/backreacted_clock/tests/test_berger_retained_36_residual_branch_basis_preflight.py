from __future__ import annotations

import json

from d_quotient_classical.backreacted_clock import berger_retained_36_residual_branch_basis_preflight as preflight
from d_quotient_classical.backreacted_clock import verify_berger_retained_36_residual_branch_basis_preflight as verifier


def test_normalized_even_odd_basis_is_outside_declared_field() -> None:
    value = preflight.build()
    assert value["field_obstruction"]["sqrt2_is_member_of_declared_field"] is False
    assert value["flags"]["CURRENT_INPUT_SCHEMA_FIELD_CONSISTENT_WITH_NORMALIZED_EO_BASIS"] is False


def test_two_exact_contract_repairs_are_recorded() -> None:
    repairs = preflight.build()["minimal_contract_repairs"]
    assert [row["repair_id"] for row in repairs] == ["EXTEND_DEFORMATION_FIELD", "USE_UNNORMALIZED_PARITY_BASIS"]
    assert repairs[0]["deformation_coefficient_field"] == "Q(sqrt(2),sqrt(10))"
    assert repairs[1]["normalization"].endswith("later scalar extension explicitly")


def test_missing_projector_is_not_overstated() -> None:
    value = preflight.build()
    assert value["separate_missing_carrier"]["status"] == "NOT_EXPORTED_NOT_A_NONEXISTENCE_THEOREM"
    assert value["flags"]["DYNAMICAL_BRANCH_PROJECTOR_AVAILABLE"] is False
    assert value["flags"]["ELL3_BRANCH_PROJECTION_AUTHORIZED"] is False


def test_v2_requires_typed_pairing_sector_and_reality_data() -> None:
    value = preflight.build()
    requirements = "\n".join(value["v2_contract_requirements"])
    assert "chiral deformation pairing" in requirements
    assert "mode or support sector" in requirements
    assert "antilinear real structure" in requirements
    assert value["even_odd_matrix_receipt"]["input_chiral_gram_assumption"].endswith(
        "NOT_IMPORTED_AS_A_BERGER_BRANCH_ARTIFACT"
    )


def test_persisted_and_independent_replay() -> None:
    assert json.loads(preflight.OUTPUT.read_text()) == preflight.build()
    assert verifier.main() == 0
