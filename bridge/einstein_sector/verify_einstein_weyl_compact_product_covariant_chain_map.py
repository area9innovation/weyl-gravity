"""Independent consumer for the compact-product covariant chain-map export."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1.json"
RECEIPT = ROOT / "bridge/einstein_sector/receipts/einstein-weyl-compact-product-covariant-chain-map-v1.json"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(path: Path = CERTIFICATE) -> None:
    value = _load(path)
    schema_path = ROOT / value["schema_path"]
    schema = _load(schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == _sha256(schema_path)
    assert value["result_id"] == "EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1"
    assert value["dependency_tags"] == ["LOCAL-ALGEBRAIC"]

    provenance = value["provenance"]
    producer = ROOT / provenance["producer_path"]
    assert provenance["producer_sha256"] == _sha256(producer)
    proof_path = ROOT / provenance["heavy_proof"]["path"]
    assert provenance["heavy_proof"]["sha256"] == _sha256(proof_path)
    for record in provenance["inputs"].values():
        assert record["sha256"] == _sha256(ROOT / record["path"])

    proof = _load(proof_path)
    assert proof["result_id"] == "EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_PROOF_V1"
    assert proof["producer"]["path"] == provenance["producer_path"]
    assert proof["producer"]["sha256"] == provenance["producer_sha256"]
    assert proof["invariant_ansatz"]["candidate_count"] == 41
    assert proof["invariant_ansatz"]["combined_rank"] == 26
    assert proof["invariant_ansatz"]["combined_augmented_rank"] == 26
    assert proof["invariant_ansatz"]["coefficient_vector"] == [
        "3", "3/2", "-1", "0", "0", "0", "-5/2", "0", "0", "0", "0",
        "-1/2", "0", "0", "0", "0", "5/2", "0", "0", "0", "0", "0",
        "0", "0", "3", "0", "0", "0", "3", "0", "0", "0", "0", "-3",
        "-3", "0", "0", "0", "0", "0", "0"
    ]
    assert proof["identity_fit"] == {
        "candidate_count": 9,
        "rank": 9,
        "augmented_rank": 9,
        "coefficient_vector": ["3/2", "1", "-1/2", "0", "0", "0", "0", "0", "-3/2"],
        "unique": True,
    }
    assert set(proof["symbolic_action_replays"]) == {
        "axial_ell2", "axial_ell3", "axial_ell4",
        "polar_ell2", "polar_ell3", "polar_ell4",
    }
    for replay in proof["symbolic_action_replays"].values():
        assert replay["all_ten_symmetric_tensor_components"] == "0"
        assert replay["off_shell_frequency_momentum_retained"] is True

    chain_map = value["chain_map"]
    assert chain_map["support_local"] is True
    assert chain_map["uses_inverse_laplacian_curl_frequency_or_momentum"] is False
    assert chain_map["operator_orders"] == {
        "metric_from_E": 2,
        "metric_from_M": 1,
        "maxwell": 0,
        "diff_identity": 2,
    }
    formula = chain_map["metric_equation_map"]
    assert "3 P(E)" in formula
    assert "+3 B(I,J_S;nabla M)-3 B(J_S,I;nabla M)" in formula
    assert value["classification"]["single_covariant_support_local_map_reconstructed"] is True
    assert value["classification"]["noncyclic_three_form_triangle_completed"] is False
    assert value["classification"]["finite_large_gauge_and_residual_endpoints_included"] is False

    receipt = _load(RECEIPT)
    assert receipt["result_id"] == "EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1_VERIFICATION_RECEIPT"
    assert receipt["dependency_tags"] == ["LOCAL-ALGEBRAIC"]
    for record in receipt["artifacts"].values():
        assert record["sha256"] == _sha256(ROOT / record["path"])
    assert receipt["tiers"]["tier_0"]["status"] == "PASS"
    assert receipt["tiers"]["tier_1"]["status"] == "PASS"
    assert receipt["tiers"]["tier_2"]["status"] == "PASS"
    assert receipt["tiers"]["tier_3"]["status"] == "NOT_RUN"


if __name__ == "__main__":
    verify()
    print("compact-product covariant chain-map consumer: PASS")
