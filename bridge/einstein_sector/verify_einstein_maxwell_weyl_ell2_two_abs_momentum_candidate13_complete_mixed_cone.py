"""Independent logical verifier for the complete candidate-13 mixed cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_complete_mixed_cone.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == sha(schema_path)
    records = {}
    for name, item in payload["provenance"]["inputs"].items():
        path = ROOT / item["path"]
        assert item["sha256"] == sha(path)
        records[name] = json.loads(path.read_text(encoding="utf-8"))
    assert records["candidate13_incidence"]["prime_zero_variety_theorem"]["equation_count"] == 18
    assert records["candidate13_incidence"]["classification"]["candidate_13_ideal_prime"]
    assert records["same_fibre_census"]["nonzero_defect_count"] == 144
    assert records["finite_generic_cone"]["classification"]["complete_reduced_adjoint_cokernel_decomposition_certified"]
    assert records["isolated_cross_fibre_candidates"]["classification"]["twenty_one_distinct_admissible_candidates"]
    assert records["pure_extra_taub_join"]["classification"]["candidate_13_resonance_Taub_common_zero_is_origin"]
    assert records["mixed_bounded_witness"]["classification"]["candidate_13_mixed_witness_bounded_second_order_obstructed"]
    assert records["pressure_obstruction"]["classification"]["candidate13_bounded_pressure_functional_nonzero"]
    assert records["bounded_zero_block"]["classification"]["five_stabilizers_plus_circle_pressure_complete_on_finite_generic_zero_block"]
    assert records["bounded_zero_block"]["classification"]["bounded_zero_frequency_necessity_and_sufficiency_certified"]
    assert records["candidate13_zero_block"]["classification"]["complete_candidate13_bounded_zero_frequency_receiver_certified"]
    assert records["scalar_separation"]["classification"]["candidate13_complete_bounded_cone_is_origin"]
    assert payload["coefficientwise_functionals"]["stabilizer"] == ["mu_H", "mu_Px", "mu_J1", "mu_J2", "mu_J3"]
    assert payload["coefficientwise_functionals"]["candidate13_cross_fibre"]["count_over_C"] == 18
    assert "R_c=0" in payload["tangent_cones"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["formula"]
    assert "R_13,18=0" in payload["tangent_cones"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["formula"]
    assert "mu_J3=0" in payload["tangent_cones"]["SMOOTH_EXPONENTIAL_POLYNOMIAL"]["formula"]
    flags = payload["classification"]
    assert flags["complete_candidate13_bounded_tangent_cone_formula_certified"]
    assert flags["candidate13_known_bounded_functional_ledger_certified"]
    assert flags["complete_candidate13_bounded_functional_ledger_certified"]
    assert flags["complete_candidate13_smooth_tangent_cone_formula_certified"]
    assert flags["five_stabilizer_pressure_and_eighteen_resonance_functionals_necessary_bounded"]
    assert flags["five_stabilizer_pressure_and_eighteen_resonance_functionals_sufficient_bounded"]
    assert flags["candidate13_complete_bounded_cone_is_origin"]
    assert not flags["nonzero_mixed_bounded_point_exists"]
    assert flags["nonzero_mixed_bounded_point_nonexistence_certified"]
    assert flags["nonzero_mixed_smooth_point_certified"]
    assert flags["real_algebraic_component_decomposition_classified"]
    assert not flags["all_orders_integrability"]
    assert not flags["causal_residual_observational_or_quantum_claim"]
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_COMPLETE_MIXED_CONE verifier: PASS")


if __name__ == "__main__":
    verify()
