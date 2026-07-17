"""Verify the theorem-to-certificate map for Paper 91."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


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

    polar_module = _load(
        "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json"
    )
    polar_module_classification = polar_module["classification"]
    assert polar_module_classification["canonical_extra_polar_quotient_two_p_summands"]
    assert polar_module_classification["Einstein_image_equals_complete_q_primary_summand"]
    assert polar_module_classification[
        "all_physical_lambda_and_compact_momenta_including_zero_certified"
    ]

    polar_current = _load(
        "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json"
    )
    polar_current_classification = polar_current["classification"]
    assert polar_current_classification["direct_four_dimensional_Lee_Wald_match"]
    assert polar_current_classification["Einstein_extra_orthogonality"]
    assert polar_current_classification["extra_block_positive_frequency_inertia_2_0"]

    sqrt3 = sp.sqrt(3)
    omega_minus = sp.sqrt(6 - 2 * sqrt3)
    omega_extra = 4 / sqrt3
    frequencies = (
        sp.Integer(0),
        2 * omega_minus,
        2 * omega_extra,
        omega_extra + omega_minus,
        omega_extra - omega_minus,
    )
    expected_signs = {
        6: ((-1, 1), (1, 1), (1, 1), (1, 1), (-1, 1)),
        20: ((-1, 1), (-1, 1), (1, -1), (-1, -1), (-1, 1)),
    }
    for lam, signs in expected_signs.items():
        for omega, (p_sign, q_sign) in zip(frequencies, signs, strict=True):
            p_value = sp.simplify(omega**2 - lam + sp.Rational(2, 3))
            q_value = sp.simplify(omega**4 - 2 * lam * omega**2 + lam * (lam - 2))
            assert p_value.equals(0) is False
            assert q_value.equals(0) is False
            assert (p_value.is_positive and p_sign == 1) or (
                p_value.is_negative and p_sign == -1
            )
            assert (q_value.is_positive and q_sign == 1) or (
                q_value.is_negative and q_sign == -1
            )

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
        "Theorem 3.1 (generic polar linear input)",
        "Proposition 4.1 (Taub pairing equals the stabilizer moment map)",
        "pure extra generic mode: obstructed",
        "balanced Einstein--extra mode: extendible to second order",
        "Theorem 5.1 (pure-extra fixed-bundle no-go)",
        "Theorem 8.1 (balanced Einstein--extra second-order extension)",
        "finite quasiperiodic in time",
        "generic_polar_channels.",
        "4.cross_difference",
        "Phi^{(2)}_{2,2\\omega_e}",
        "Phi^{(2)}_{4,2\\omega_e}",
        "Why the full nonlinear cone is the next theorem",
    ):
        assert required_text in manuscript, required_text
    assert "admits a real, periodic" not in manuscript
    assert "$\\Phi^{(2)}$ is real and periodic" not in manuscript

    claims = claim_map["certified_claims"]
    assert all(value is True for value in claims.values())
    repairs = claim_map["specialist_review_repairs"]
    assert all(value is True for value in repairs.values())
    nonclaims = claim_map["explicit_nonclaims"]
    assert all(value is False for value in nonclaims.values())
    receipt = claim_map["verification_receipt"]
    assert receipt["tier_0"]["status"] == "PASSED"
    assert receipt["tiers_1_and_2"]["status"] == "PASSED"
    assert receipt["tier_3_full_repository"]["status"] == "NOT_RUN"


if __name__ == "__main__":
    verify()
