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
    assert claims["target_pullback_nondegenerate_on_complete_standard_image"] is True
    assert claims["identity_inclusion_symplectic"] is False
    assert claims["regular_radiative_relative_signature_per_real_spatial_harmonic"] == [2, 2]
    assert claims["generic_axial_extra_signature"] == [2, 0]
    assert claims["complete_generic_axial_target_signature"] == [3, 1]

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
        r"\begin{theorem}[Complete standard harmonic inclusion]",
        r"\begin{theorem}[Generic axial target classification]",
        r"\operatorname{sig}\cT_{\rm WM}^{\rm ax}=(3,1)",
        "before the final residual quotient",
        "not, by itself, a quantum ghost or unitarity theorem",
        "The polar extra branch and the final residual descent remain open",
    ]
    for marker in required:
        assert marker in normalized, marker

    forbidden = [
        "LORENTZIAN_CERTIFIED",
        "THEOREM_FROZEN",
        "the polar extra branch is complete",
        "proves asymptotically flat scattering",
    ]
    for marker in forbidden:
        assert marker not in text, marker

    print("COMPACT_EINSTEIN_MAXWELL_WEYL_LINEAR_PAPER_A_CLAIM_MAP: PASS")


if __name__ == "__main__":
    main()
