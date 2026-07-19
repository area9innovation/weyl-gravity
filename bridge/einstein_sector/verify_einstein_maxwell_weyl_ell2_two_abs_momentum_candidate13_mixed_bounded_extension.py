"""Independent logical verifier for the candidate-13 mixed bounded extension."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_bounded_extension.json"


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
    witness = records["mixed_witness"]
    assert witness["classification"]["all_five_stabilizer_moment_maps_zero"]
    assert witness["classification"]["candidate_13_cross_fibre_resonance_functionals_zero"]
    same = records["same_fibre_census"]
    assert same["channel_count"] == 18 and same["nonzero_defect_count"] == 144
    assert same["classification"]["candidate_13_all_nonzero_same_fibre_channels_off_shell"]
    generic = records["finite_generic_cone"]
    assert generic["classification"]["complete_reduced_adjoint_cokernel_decomposition_certified"]
    assert not generic["classification"]["bounded_resonance_zero_locus_solved"]
    assert "smooth-class" in payload["complete_blockwise_disposition"]["audit_result"]
    assert set(payload["complete_blockwise_disposition"]["zero_frequency_pairings"].values()) == {"0"}
    assert records["pressure_obstruction"]["classification"]["candidate13_bounded_pressure_functional_nonzero"]
    assert records["isolated_cross_fibre_candidates"]["classification"]["twenty_one_distinct_admissible_candidates"]
    flags = payload["classification"]
    assert not flags["candidate_13_mixed_witness_bounded_second_order_extendible"]
    assert flags["candidate_13_mixed_witness_bounded_second_order_obstructed"]
    assert flags["candidate_13_mixed_witness_smooth_second_order_extendible"]
    assert flags["candidate_13_bounded_pressure_functional_nonzero"]
    assert not flags["complete_finite_block_bounded_source_in_image"]
    assert not flags["full_candidate_13_mixed_tangent_cone_classified"]
    assert not flags["all_orders_integrability"]
    assert not flags["causal_residual_observational_or_quantum_claim"]
    assert payload["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] == "OBSTRUCTED"
    assert payload["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_MIXED_BOUNDED_EXTENSION verifier: PASS")


if __name__ == "__main__":
    verify()
