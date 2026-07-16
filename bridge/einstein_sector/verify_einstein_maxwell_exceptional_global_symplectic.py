"""Independent verifier for exceptional global symplectic completion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_exceptional_global_symplectic.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate(path: Path = CERTIFICATE) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["result_id"] == "COMPACT_EM_EXCEPTIONAL_GLOBAL_SYMPLECTIC"
    assert payload["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    assert _sha256(ROOT / payload["schema_path"]) == payload["schema_sha256"]
    assert (
        _sha256(ROOT / payload["provenance"]["generator_path"])
        == payload["provenance"]["generator_sha256"]
    )
    for relative, digest in payload["provenance"]["inputs"].items():
        assert _sha256(ROOT / relative) == digest

    ell0 = payload["ell0_global_theorem"]
    matrix = sp.Matrix(
        [[sp.Integer(value) for value in row] for row in ell0["dimensionless_matrix_after_factor_2piL"]]
    )
    expected = sp.Matrix(
        [
            [0, -1, 0, -1, 0, 0],
            [1, 0, 1, 0, 0, 0],
            [0, -1, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, -2],
            [0, 0, 0, 0, 2, 0],
        ]
    )
    assert matrix == expected
    assert matrix.rank() == ell0["matrix_rank"] == 6
    assert matrix.det() == ell0["matrix_determinant"] == 4
    assert "beta=b+d" in ell0["Darboux_reorganization"]
    assert "flat S1 connection" in ell0["new_potential_level_mode"]
    assert "not c1(P_N)" in ell0["fixed_bundle_scope"]

    twist = payload["axial_ell1_twist_theorem"]
    assert twist["rank_per_real_harmonic"] == 2
    assert "8*pi*L/3" in twist["Cauchy_form"]
    assert "not periodic" in twist["periodic_gauge_audit"]
    assert "three identical" in twist["SO3_statement"]

    fixture = payload["direct_lee_wald_fixture"]
    assert fixture["remainders"] == {"ell0": "0", "twist": "0"}
    assert fixture["ell0_time_dependence_after_equations"] == "0"
    assert fixture["twist_time_dependence_after_equations"] == "0"
    completions = payload["completes"]
    assert [row["json_pointer"] for row in completions] == [
        "/ell0_complex/global_moduli",
        "/ell1_quotient/global_zero_mode",
    ]
    assert all("completion" in row["scope"] for row in completions)

    classification = payload["classification"]
    assert classification["ell0_metric_global_form_nondegenerate"] is True
    assert classification["electric_charge_holonomy_pair_complete"] is True
    assert classification["axial_ell1_twist_generalized_pair_complete"] is True
    assert classification["fixed_bundle_standard_harmonic_symplectic_completion"] is True
    assert classification["bounded_in_time_subspace_theorem"] is False
    assert classification["one_particle_complex_structure_constructed"] is False
    assert classification["Weyl_Maxwell_pullback_matching"] is False
    assert classification["Lorentzian_causal_or_scattering_theorem"] is False


if __name__ == "__main__":
    verify_certificate()
