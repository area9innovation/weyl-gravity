"""Independent verifier for the all-ell q-minus parity resonance matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_qminus_parity_resonance_matrix.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(schema_path)

    provenance = payload["provenance"]
    slice_path = ROOT / provenance["pbw_slice"]["path"]
    assert provenance["pbw_slice"]["sha256"] == _sha256(slice_path)
    slice_payload = json.loads(slice_path.read_text(encoding="utf-8"))
    assert provenance["parent_q2_sha256"] == slice_payload["parent"]["q2_sha256"]
    assert provenance["parent_action_sha256"] == slice_payload["parent"]["action_sha256"]
    assert provenance["parent_row_layout_sha256"] == slice_payload["parent"]["row_layout_sha256"]
    for item in provenance["inputs"].values():
        path = ROOT / item["path"]
        assert item["sha256"] == _sha256(path)

    ell = sp.symbols("ell", integer=True, positive=True)
    root, momentum = sp.symbols("r k", positive=True, real=True)
    gaunt = sp.binomial(2 * ell, ell) ** 2 / sp.binomial(4 * ell, 2 * ell)
    local = {"ell": ell, "r": root, "k": momentum, "C_ell": gaunt}
    stored_slice = {
        key: sp.factor(sp.sympify(value, locals=local))
        for key, value in slice_payload["reduced_axisymmetric_pairings"].items()
    }
    matrix = payload["resonance_matrix"]
    axial = sp.sympify(matrix["R_axial_diagonal"], locals=local)
    polar = sp.sympify(matrix["R_polar_diagonal"], locals=local)
    cross = sp.sympify(matrix["X_axial_polar"], locals=local)
    assert sp.factor(axial - stored_slice["polar_output_from_axial_axial"]) == 0
    assert sp.factor(polar - stored_slice["polar_output_from_polar_polar"]) == 0
    assert sp.factor(cross - stored_slice["axial_output_from_axial_plus_polar_minus"]) == 0
    eigenvalue = ell * (ell + 1)
    assert sp.factor(polar + eigenvalue * axial / 2) == 0

    cross_a = 3 * ell**3 + 8 * ell**2 + 5 * ell
    cross_b = 2 * ell**2 + 5 * ell + 1
    expected_norm = ell * (ell - 1) ** 3 * (ell + 1) * (ell + 2)
    assert sp.factor(cross_a**2 - 2 * eigenvalue * cross_b**2 - expected_norm) == 0
    assert sp.factor(
        sp.sympify(payload["nonvanishing_proofs"]["cross_norm_factorization"], locals={"ell": ell})
        - expected_norm
    ) == 0

    a_plus, a_minus, p_plus, p_minus = sp.symbols("a_plus a_minus p_plus p_minus")
    diagonal = a_plus * a_minus - eigenvalue * p_plus * p_minus / 2
    wedge = a_plus * p_minus - a_minus * p_plus
    scale = sp.sqrt(eigenvalue / 2)
    for sign in (-1, 1):
        sheet = {a_plus: sign * scale * p_plus, a_minus: sign * scale * p_minus}
        assert sp.simplify(diagonal.subs(sheet)) == 0
        assert sp.simplify(wedge.subs(sheet)) == 0
    for plane in ({a_plus: 0, p_plus: 0}, {a_minus: 0, p_minus: 0}):
        assert diagonal.subs(plane) == 0
        assert wedge.subs(plane) == 0

    ell2_input = json.loads((ROOT / provenance["inputs"]["ell2_direct_matrix"]["path"]).read_text(encoding="utf-8"))
    ell2 = ell2_input["resonance_matrix"]
    substitutions = {
        ell: 2,
        root: 2 * sp.sqrt(3),
        momentum: sp.sqrt(2 * sp.sqrt(3) - sp.Rational(7, 6)),
    }
    assert sp.factor(sp.sqrtdenest(axial.subs(substitutions)) - sp.sympify(ell2["axial_diagonal_coefficient"])) == 0
    assert sp.factor(polar.subs(substitutions) / axial.subs(substitutions) - sp.sympify(ell2["polar_over_axial_diagonal_ratio"])) == 0
    assert sp.factor(sp.sqrtdenest(cross.subs(substitutions)) - sp.sympify(ell2["cross_coefficient"])) == 0

    classification = payload["classification"]
    assert classification["action_derived_two_parity_matrix_computed"]
    assert classification["all_three_coefficients_nonzero_every_integer_ell_ge_2"]
    assert classification["complete_resonance_zero_variety_classified"]
    assert classification["nonzero_two_momentum_null_sheets_exist_every_integer_ell_ge_2"]
    assert not classification["general_all_channel_bounded_extension_on_null_sheets"]
    assert not classification["fixed_circumference_or_multiple_abs_momentum_classified"]
    assert not classification["causal_or_quantum_claim"]
    corrections = payload["correction_classes"]
    assert corrections["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] == "OPEN"
    assert corrections["SMOOTH_EXPONENTIAL_POLYNOMIAL"]["status"] == "CERTIFIED"
    assert corrections["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_QMINUS_PARITY_RESONANCE_MATRIX verifier: PASS")


if __name__ == "__main__":
    verify()
