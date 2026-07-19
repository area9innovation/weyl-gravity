"""Independent verifier for the symbolic-ell axial q-minus obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_axial_qminus_obstruction.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verify_one_physical_fibre(slice_path: Path) -> None:
    """Replay the stored PBW slice at ell=2 without producer imports."""

    payload = json.loads(slice_path.read_text(encoding="utf-8"))
    assert payload["result_id"] == "EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_AXIAL_QMINUS_PBW_SLICE"
    assert payload["extraction"]["maximum_total_derivative_order"] == 4
    assert payload["extraction"]["highest_weight_isolates_L_2ell"]
    ell, momentum, frequency, root = sp.symbols("ell k omega r", positive=True, real=True)
    locals_ = {"ell": ell, "k": momentum, "omega": frequency, "r": root, "I": sp.I}
    rows = payload["highest_weight_rows"]
    output = {
        20: sp.sympify(rows["E00"], locals=locals_),
        21: sp.sympify(rows["E01"], locals=locals_),
        24: sp.sympify(rows["E11"], locals=locals_),
        32: sp.sympify(rows["Maxwell_theta"], locals=locals_),
        33: sp.sympify(rows["Maxwell_phi"], locals=locals_),
    }
    substitutions = {
        ell: 2,
        root: 2 * sp.sqrt(3),
        momentum**2: 2 * sp.sqrt(3) - sp.Rational(7, 6),
        frequency**2: sp.Rational(29, 6),
    }
    output = {row: sp.factor(sp.sqrtdenest(value.subs(substitutions))) for row, value in output.items()}

    expected = {
        20: -sp.Rational(80, 9) * (163 + 261 * sp.sqrt(3)),
        21: 0,
        24: sp.Rational(8, 27) * (-21293 + 9450 * sp.sqrt(3)),
        32: sp.Rational(32, 3) * sp.I * (-137 + 55 * sp.sqrt(3)),
        33: 0,
    }
    for row, value in expected.items():
        assert sp.factor(output[row] - value) == 0, (row, output[row], value)


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
    assert provenance["parent_row_layout_sha256"] == slice_payload["parent"]["row_layout_sha256"]
    assert provenance["parent_action_sha256"] == slice_payload["parent"]["action_sha256"]
    for item in provenance["inputs"].values():
        path = ROOT / item["path"]
        assert item["sha256"] == _sha256(path)

    _verify_one_physical_fibre(slice_path)

    ell, root = sp.symbols("ell r", positive=True)
    section = payload["symbolic_adjoint_pairing"]
    polynomial_a = sp.sympify(section["A_ell"], locals={"ell": ell})
    polynomial_b = sp.sympify(section["B_ell"], locals={"ell": ell})
    norm = sp.factor(polynomial_a**2 - 2 * ell * (ell + 1) * polynomial_b**2)
    expected_norm = 2 * (ell - 1) ** 3 * (ell + 2) * (
        81 * ell**4 + 54 * ell**3 + 42 * ell - 1
    )
    assert sp.factor(norm - expected_norm) == 0
    assert sp.factor(sp.sympify(payload["nonvanishing_proof"]["norm_factorization"], locals={"ell": ell}) - expected_norm) == 0

    gaunt = sp.binomial(2 * ell, ell) ** 2 / sp.binomial(4 * ell, 2 * ell)
    expected_pairing = sp.factor(
        -8
        * gaunt
        * ell**2
        * (ell + 1)
        * (2 * ell + 1)
        * (root * polynomial_b - polynomial_a)
        / (3 * (6 * ell**2 + 3 * ell - 1))
    )
    stored_pairing = sp.sympify(
        section["axisymmetric_pairing"],
        locals={"ell": ell, "r": root},
    )
    assert sp.factor(stored_pairing - expected_pairing) == 0
    for value in (2, 3, 4, 5, 6):
        sample = sp.factor(expected_pairing.subs({ell: value, root: sp.sqrt(2 * value * (value + 1))}))
        assert sp.factor(sample - sp.sympify(section["direct_exact_samples"][str(value)])) == 0

    classification = payload["classification"]
    assert classification["symbolic_axial_dynamical_adjoint_coefficient_computed"]
    assert classification["coefficient_strictly_positive_every_integer_ell_ge_2"]
    assert classification["all_ell_tuned_axial_common_zero_tangent_bounded_obstructed"]
    assert not classification["polar_or_mixed_input_coefficient_computed"]
    assert not classification["fixed_circumference_or_multiple_abs_momentum_classified"]
    assert not classification["causal_or_quantum_claim"]
    assert payload["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] == "OBSTRUCTED"
    assert payload["correction_classes"]["SMOOTH_EXPONENTIAL_POLYNOMIAL"]["status"] == "CERTIFIED"
    assert payload["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_AXIAL_QMINUS_BOUNDED_OBSTRUCTION verifier: PASS")


if __name__ == "__main__":
    verify()
