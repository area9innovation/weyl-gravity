#!/usr/bin/env python3
"""Fail-closed verification of the scoped compact Einstein paper claim map."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLAIM_MAP = ROOT / "paper/10-compact-einstein-maxwell-weyl-phase-space-claim-map.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    payload = json.loads(CLAIM_MAP.read_text(encoding="utf-8"))
    assert payload["result_id"] == "COMPACT_EINSTEIN_MAXWELL_WEYL_LINEAR_PAPER_A"
    assert payload["lifecycle_state"] == "CLASSIFIED"
    assert payload["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]

    claims = payload["certified_claims"]
    assert claims["linear_solution_quotient_inclusion_injective"] is True
    assert claims["formal_linear_inclusion_covers_nonintegrable_jacobi_fields"] is True
    assert claims["target_pullback_nondegenerate_on_complete_standard_image"] is True
    assert claims["identity_inclusion_symplectic"] is False
    assert claims["regular_radiative_relative_inertia_per_real_spatial_harmonic"] == [2, 2]
    assert claims["all_compact_momenta_including_k_zero_certified"] is True
    assert claims["generic_axial_extra_positive_frequency_current_inertia"] == [2, 0]
    assert claims["complete_generic_axial_positive_frequency_current_inertia"] == [3, 1]

    nonclaims = payload["explicit_nonclaims"]
    assert nonclaims
    assert all(value is False for value in nonclaims.values())

    for relative, expected in payload["inputs"].items():
        path = ROOT / relative
        assert path.is_file(), relative
        assert _sha256(path) == expected, relative

    manuscript = ROOT / payload["manuscript"]
    text = manuscript.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        r"\begin{theorem}[Fixed-bundle tangent inclusion]",
        r"\begin{proposition}[Dual-number formal linearization]",
        r"\begin{theorem}[Relative phase-space endomorphism]",
        r"\begin{theorem}[Axial target decomposition and current inertia]",
        r"\operatorname{inertia}\bigl(h_+|_{\mathcal H^{\rm ax}_+}\bigr)=(3,1)",
        r"R_{\rm phys}=\mathbb Q[\lambda,k",
        r"n\in\mathbb Z$, including $n=0$",
        "The Einstein image therefore equals the complete $q$-primary summand",
        r"{-i\omega_eL N_{\ell m}}",
        "so $h_+$ is Hermitian on a common positive-frequency shell",
        "before the final residual quotient",
        "not, by itself, a quantum ghost or unitarity theorem",
        "The polar extra branch and the final residual descent remain open",
    ]
    for marker in required:
        assert marker in normalized, marker

    forbidden = [
        "LORENTZIAN_CERTIFIED",
        "THEOREM_FROZEN",
        r"\operatorname{sig}\cT_{\rm WM}^{\rm ax}",
        "every real compact momentum",
        r"{-i\omega_eN_{\ell m}}",
        "the polar extra branch is complete",
        "proves asymptotically flat scattering",
    ]
    for marker in forbidden:
        assert marker not in text, marker

    print("COMPACT_EINSTEIN_MAXWELL_WEYL_LINEAR_PAPER_A_CLAIM_MAP: PASS")


if __name__ == "__main__":
    main()
