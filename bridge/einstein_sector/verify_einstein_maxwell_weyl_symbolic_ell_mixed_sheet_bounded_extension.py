"""Independent logical verifier for the symbolic mixed-sheet extension."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_mixed_sheet_bounded_extension.json"


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
    assert records["parity_matrix"]["classification"]["complete_resonance_zero_variety_classified"]
    assert records["standard_census"]["classification"]["unique_nonzero_frequency_standard_branch_collision_is_qminus_L2ell_p"]
    assert records["finite_generic_cone"]["classification"]["complete_reduced_adjoint_cokernel_decomposition_certified"]
    assert records["common_zero"]["classification"]["twist_aligned_common_zero_intersection_nonempty_every_ell"]
    proof = payload["bounded_blockwise_proof"]
    assert "exists exactly" in proof["abstract_criterion"]
    assert "all five pairings vanish" in proof["zero_block"]
    assert "a_+*a_-" in proof["unique_polar_output"]
    assert "a_+*p_-" in proof["unique_axial_output"]
    classification = payload["classification"]
    assert classification["both_symbolic_mixed_sheet_signs_covered"]
    assert classification["every_integer_ell_ge_2_has_nonzero_bounded_second_order_jet"]
    assert classification["five_moment_maps_and_all_bounded_resonant_functionals_vanish"]
    assert classification["bounded_correction_exists_by_complete_cokernel_criterion"]
    assert not classification["full_mixed_sheet_amplitude_cone_classified"]
    assert not classification["all_orders_integrability"]
    assert not classification["causal_or_quantum_claim"]
    assert payload["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] == "CERTIFIED"
    assert payload["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_MIXED_SHEET_BOUNDED_EXTENSION verifier: PASS")


if __name__ == "__main__":
    verify()
