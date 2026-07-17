"""Verify the theorem-to-certificate map for Paper 91."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLAIM_MAP = ROOT / "paper/91-charge-fibre-taub-bridge-claim-map.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(relative_path: str) -> dict[str, object]:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def verify() -> None:
    claim_map = json.loads(CLAIM_MAP.read_text(encoding="utf-8"))
    assert claim_map["lifecycle_state"] == "THEOREM_FROZEN"
    assert set(claim_map["dependency_tags"]) == {"LOCAL-ALGEBRAIC", "REDUCED-MODE"}
    assert (ROOT / claim_map["manuscript"]).is_file()
    assert claim_map["authorship"] == {
        "author": "GPT-5.6.sol",
        "model_provider": "OpenAI",
        "commissioner_and_corresponding_human_contact": "Asger Alstrup Palm",
        "commissioner_claims_technical_contribution": False,
    }

    for relative_path, expected_hash in claim_map["inputs"].items():
        assert _sha256(ROOT / relative_path) == expected_hash, relative_path

    moment = _load("bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json")
    moment_classification = moment["classification"]
    assert moment_classification["generic_covariant_moment_map_Taub_equality_certified"] is True
    assert moment_classification["generic_extra_H_Taub_negative_definite"] is True
    assert moment_classification[
        "all_nonzero_generic_pure_extra_fixed_bundle_tangents_second_order_obstructed"
    ] is True

    mixed = _load("bridge/certificates/einstein_maxwell_weyl_mixed_moment_map_zero_locus.json")
    mixed_classification = mixed["classification"]
    assert mixed_classification["same_nonzero_k_travelling_common_H_Px_zero_locus_trivial"] is True
    assert mixed_classification["minimal_nonzero_all_five_moment_map_zero_fixture_constructed"] is True

    balanced = _load("bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json")
    balanced_classification = balanced["classification"]
    assert balanced_classification["complete_second_order_extension_constructed"] is True
    assert balanced_classification["all_dependent_polar_tensor_rows_Noether_completed"] is True
    assert balanced_classification["fixed_charge_and_reality_audit_passed"] is True
    assert (
        balanced["dependent_row_completion"]["Noether_completion"]
        ["selector_plus_Noether_determinant"]
        == "-4"
    )

    manuscript = (ROOT / claim_map["manuscript"]).read_text(encoding="utf-8")
    assert "GPT-5.6.sol (OpenAI model)" in manuscript
    assert "The AI system is not an author." not in manuscript
    for required_text in (
        "pure extra generic mode: obstructed",
        "balanced Einstein--extra mode: extendible to second order",
        "Theorem 5.1 (pure-extra fixed-bundle no-go)",
        "Theorem 8.1 (balanced Einstein--extra second-order extension)",
        "Why the full nonlinear cone is the next theorem",
    ):
        assert required_text in manuscript, required_text

    claims = claim_map["certified_claims"]
    assert all(value is True for value in claims.values())
    nonclaims = claim_map["explicit_nonclaims"]
    assert all(value is False for value in nonclaims.values())


if __name__ == "__main__":
    verify()
