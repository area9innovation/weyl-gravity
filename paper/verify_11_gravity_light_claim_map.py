#!/usr/bin/env python3
"""Fail-closed verification of the Paper 11 working-draft claim map."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAIM_MAP = ROOT / "paper/11-gravity-light-cyclic-causal-ell3-claim-map.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    payload = json.loads(CLAIM_MAP.read_text(encoding="utf-8"))
    assert payload["schema"] == "paper-11-gravity-light-cyclic-causal-ell3-claim-map-v1"
    assert payload["result_id"] == "PAPER_11_GRAVITY_LIGHT_CYCLIC_CAUSAL_ELL3_DRAFT"
    assert (
        payload["result_state"]
        == "WRITING_STARTED_ALGEBRAIC_THEOREM_CERTIFIED_RESIDUAL_MIXING_INPUT_BLOCKED"
    )
    assert payload["lifecycle_state"] == "WRITING_STARTED"
    assert payload["dependency_tags"] == ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
    assert payload["paper_scope"]["operator_coefficient_field"] == "Q(sqrt(10))"
    assert (
        payload["paper_scope"]["deformation_coefficient_field"]
        == "Q(sqrt(2),sqrt(10))"
    )

    claims = payload["certified_claims"]
    required_true = {
        "typed_cyclic_64_to_36_contraction",
        "retained_mixed_ell2_nonzero",
        "retained_mixed_ell3_nonzero",
        "retained_exchange_zero_after_exact_projection",
        "retained_arity_three_identity_all_36_rows",
        "physical_quartic_cyclicity_independently_replayed",
        "pairing_weight_mutation_rejected",
        "full_retained_BV_ell3_cyclicity_independently_replayed",
        "degree_two_polarization_mutation_rejected",
        "coupled_K_Berger_cyclic_causal_Cartan_through_arity_three",
    }
    assert all(claims[name] is True for name in required_true)
    assert claims["retained_mixed_ell2_coefficient_count"] == 1_474
    assert claims["retained_mixed_ell3_coefficient_count"] == 25_950
    assert claims["physical_quartic_coefficient_count"] == 25_662
    assert claims["physical_quartic_cyclicity_defect_count"] == 0
    assert claims["pairing_weight_mutation_defect_count"] == 17_108
    assert claims["ghost_antifield_completion_coefficient_count"] == 288
    assert claims["ghost_antifield_positive_transpose_sign_count"] == 120
    assert claims["ghost_antifield_negative_transpose_sign_count"] == 168
    assert claims["full_BV_cyclicity_defect_count"] == 0
    assert claims["degree_two_polarization_mutation_defect_count"] == 132
    assert claims["gravity_output_two_Maxwell_input_count"] == 7_614
    assert claims["Maxwell_output_one_Maxwell_input_count"] == 18_336

    nonclaims = payload["explicit_nonclaims"]
    assert nonclaims
    assert all(value is False for value in nonclaims.values())
    assert payload["next_gate"]["status"] == "INPUT_BLOCKED"
    assert (
        payload["next_gate"]["required_input"]
        == "BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V2"
    )

    for relative, expected in payload["inputs"].items():
        path = ROOT / relative
        assert path.is_file(), relative
        assert _sha256(path) == expected, relative

    full_BV = json.loads(
        (
            ROOT
            / "quantum-weyl/transfer/certificates/BERGER_RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY.json"
        ).read_text(encoding="utf-8")
    )
    full_diagnostics = full_BV["exact_replay"]["diagnostics"]
    assert full_BV["claim_flags"][
        "FULL_RETAINED_BV_ELL3_CYCLICITY_INDEPENDENTLY_REPLAYED"
    ] is True
    assert full_diagnostics["ghost_antifield_completion_coefficient_count"] == 288
    assert full_diagnostics["full_BV_cyclicity_defect_count"] == 0
    assert (
        full_diagnostics[
            "omitted_degree_two_polarization_mutation_defect_count"
        ]
        == 132
    )

    manuscript = ROOT / payload["manuscript"]
    assert _sha256(manuscript) == payload["manuscript_sha256"]
    text = manuscript.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required_markers = [
        r"\boxed{\text{The gravity--light interaction survives cyclic causal reduction through }\ell_3.}",
        r"\begin{theorem}[Gravity--light survival through $\ell_3$]",
        r"\begin{proposition}[Independent physical quartic cyclicity]",
        r"\begin{proposition}[Independent full-BV quartic cyclicity]",
        r"\begin{theorem}[Cyclic causal Cartan compatibility]",
        r"25{,}950",
        r"25{,}662",
        r"17{,}108",
        r"The odd topological direction can be central or inert as a deformation class",
        r"the authoritative branch-basis manifest has not been supplied",
        r"1/\sqrt2\notin\Q(\sqrt{10})",
        r"not yet a photon or graviton scattering amplitude",
    ]
    for marker in required_markers:
        assert marker in normalized, marker

    forbidden_markers = [
        "the residual mixing table is complete",
        "the topological particle branch",
        "a Lorentzian quantum master equation is restored",
        "a positive-Hilbert-space theorem is proved",
        "arity four is certified",
    ]
    for marker in forbidden_markers:
        assert marker not in text, marker

    print("PAPER_11_GRAVITY_LIGHT_CYCLIC_CAUSAL_ELL3_DRAFT_CLAIM_MAP: PASS")


if __name__ == "__main__":
    main()
