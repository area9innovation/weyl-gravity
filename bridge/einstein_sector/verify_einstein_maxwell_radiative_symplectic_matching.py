"""Independent verifier for the radiative symplectic matching theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_radiative_symplectic_matching.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_matrix(rows: list[list[str]], eigenvalue: sp.Symbol, norm: sp.Symbol | None = None) -> sp.Matrix:
    locals_map: dict[str, sp.Expr] = {"lam": eigenvalue}
    if norm is not None:
        locals_map["N_lm"] = norm
    return sp.Matrix(
        [
            [sp.sympify(value.replace("lambda", "lam"), locals=locals_map) for value in row]
            for row in rows
        ]
    )


def verify_certificate(path: Path = CERTIFICATE) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["result_id"] == "COMPACT_EM_RADIATIVE_SYMPLECTIC_MATCHING"
    assert payload["generality_level"] == "G2_RADIATIVE_ALL_N_ELL_M_WITH_ELL1_QUOTIENT"
    assert payload["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    assert _sha256(ROOT / payload["schema_path"]) == payload["schema_sha256"]
    assert _sha256(ROOT / payload["provenance"]["generator_path"]) == payload["provenance"]["generator_sha256"]
    assert _sha256(ROOT / payload["provenance"]["exhaustive_action_check_path"]) == payload["provenance"]["exhaustive_action_check_sha256"]
    for relative, digest in payload["provenance"]["inputs"].items():
        assert _sha256(ROOT / relative) == digest

    eigenvalue, norm = sp.symbols("lambda N_lm", positive=True)
    matching = payload["master_matching"]
    axial_master = _parse_matrix(matching["axial_master_matrix"], eigenvalue)
    polar_master = _parse_matrix(matching["polar_master_matrix"], eigenvalue)
    axial_form = _parse_matrix(
        matching["action_normalized_matrices_without_N_over_2"]["axial"],
        eigenvalue,
    )
    polar_form = _parse_matrix(
        matching["action_normalized_matrices_without_N_over_2"]["polar"],
        eigenvalue,
    )
    assert axial_form * axial_master == axial_master.T * axial_form
    assert polar_form * polar_master == polar_master.T * polar_form
    assert sp.expand(
        axial_form.det() - 2 * eigenvalue**2 * (eigenvalue - 2)
    ) == 0
    assert sp.expand(polar_form.det() - 2 * (eigenvalue - 2)) == 0
    assert axial_form.subs(eigenvalue, 6).is_positive_definite
    assert polar_form.subs(eigenvalue, 6).is_positive_definite

    harmonic = payload["harmonic_reduction"]
    coefficient_axial = _parse_matrix(
        harmonic["axial_rest_frame_coefficient_hessian"], eigenvalue, norm
    )
    integrated_polar = _parse_matrix(
        harmonic["polar_integrated_hessian"], eigenvalue, norm
    )
    stored_coefficient_form = _parse_matrix(
        matching["axial_rest_frame_coefficient_matrix_without_N_over_2"],
        eigenvalue,
    )
    assert coefficient_axial == norm * stored_coefficient_form / 2
    assert axial_form == stored_coefficient_form * axial_master
    assert integrated_polar == norm * polar_form / 2

    ell1 = payload["ell1_quotient"]
    ell1_form = _parse_matrix(
        ell1["polar_presymplectic_matrix_without_N_over_2"], eigenvalue
    )
    polar_gauge = sp.Matrix([2, 1])
    polar_physical = sp.Matrix([0, 1])
    assert ell1_form * polar_gauge == sp.zeros(2, 1)
    assert ell1_form.rank() == 1
    assert (polar_physical.T * ell1_form * polar_physical)[0] == 4
    assert ell1["polar_quotient_weight_with_harmonic_normalization"] == "2*N_1m"
    axial_ell1 = _parse_matrix(
        ell1["axial_presymplectic_matrix_without_N_over_2"], eigenvalue
    )
    assert axial_ell1 * sp.Matrix([1, -1]) == sp.zeros(2, 1)
    assert axial_ell1.rank() == 1
    assert (sp.Matrix([[1, 1]]) * axial_ell1 * sp.Matrix([1, 1]))[0] == 16
    assert "provisional '2 for Psi'" in ell1["supersession"]

    classification = payload["classification"]
    assert classification["exact_arbitrary_harmonic_second_variation"] is True
    assert classification["covariant_Lee_Wald_integrated_matching"] is True
    assert classification["fixed_magnetic_bundle_overlap_safe"] is True
    assert classification["physical_radiative_norms_positive"] is True
    assert classification["homogeneous_ell0_global_pairing"] is False
    assert classification["axial_ell1_global_twist_pairing"] is False
    assert classification["Weyl_Maxwell_pullback_matching"] is False
    assert classification["Lorentzian_causal_or_scattering_theorem"] is False


if __name__ == "__main__":
    verify_certificate()
