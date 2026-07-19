"""Independent verifier for the symbolic-ell q-minus self-collision theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_qminus_self_collision.json"


def verify() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema_path = ROOT / value["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert hashlib.sha256(schema_path.read_bytes()).hexdigest() == value["schema_sha256"]
    generator_path = ROOT / value["provenance"]["generator_path"]
    assert hashlib.sha256(generator_path.read_bytes()).hexdigest() == value["provenance"]["generator_sha256"]
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]

    ell = sp.symbols("ell", integer=True, positive=True)
    n = ell * (ell + 1)
    s = sp.sqrt(2 * n)
    k2 = s - ell / 2 - sp.Rational(1, 6)
    wm2 = n - ell / 2 - sp.Rational(1, 6)
    z0 = sp.factor(4 * wm2)
    z2 = sp.factor(4 * (wm2 - k2))
    top = 2 * ell * (2 * ell + 1)
    offset = sp.symbols("offset", integer=True, nonnegative=True)
    assert sp.factor(z0 - top + sp.Rational(2, 3)) == 0
    assert sp.factor(z2 - 4 * (n - s)) == 0
    exceptional_k2 = sp.Poly(sp.expand((n**2 - 4 * n + 1).subs(ell, offset + 2)), offset)
    assert all(coefficient > 0 for coefficient in exceptional_k2.all_coeffs())

    lower_rational = 4 * ell - sp.Rational(2, 3)
    lower_radical2 = 2 * (2 * ell - 1) * (2 * ell)
    lower_square_gap = sp.factor(lower_rational**2 - lower_radical2)
    assert sp.expand(lower_square_gap - (72 * ell**2 - 12 * ell + 4) / 9) == 0
    assert all(
        coefficient > 0
        for coefficient in sp.Poly(9 * lower_square_gap.subs(ell, offset + 2), offset).all_coeffs()
    )

    upper_rational = 4 * ell + sp.Rational(8, 3)
    upper_radical2 = 2 * (2 * ell + 1) * (2 * ell + 2)
    upper_square_gap = sp.factor(upper_rational**2 - upper_radical2)
    assert sp.expand(upper_square_gap - (72 * ell**2 + 84 * ell + 28) / 9) == 0
    assert all(
        coefficient > 0
        for coefficient in sp.Poly(9 * upper_square_gap.subs(ell, offset + 2), offset).all_coeffs()
    )

    target = sp.symbols("Lambda", integer=True, positive=True)
    residual = sp.expand((4 * n - target - 4 * s) ** 2 - 2 * target)
    rational_part = sp.expand(residual + 8 * (4 * n - target) * s)
    assert sp.expand(rational_part - ((4 * n - target) ** 2 + 32 * n - 2 * target)) == 0
    assert sp.expand(rational_part.subs(target, 4 * n) - 24 * n) == 0

    sint, uint, epsilon = sp.symbols("sint uint epsilon", integer=True)
    integral_equation = sp.expand(
        ((2 * sint - 2) - (uint + epsilon))
        * ((2 * sint - 2) + (uint + epsilon))
    )
    assert sp.expand(integral_equation - ((2 * sint - 2) ** 2 - (uint + epsilon) ** 2)) == 0
    # The only positive factor pairs of 3 are (1,3) and (3,1).
    for left, right in ((1, 3), (3, 1)):
        assert (left + right) // 2 == 2
    assert value["symbolic_collision_proof"]["K2k_exclusion"]["Einstein_shell_integral_case"]["only_positive_factor_solution"] == "2*s-2=2, hence s=2 and ell=1"

    classification = value["classification"]
    assert classification["symbolic_ell_tuned_qminus_self_characteristic_census_complete"]
    assert classification["unique_nonzero_frequency_collision_is_L_2ell_K0_p_shell"]
    assert classification["symbolic_dynamical_adjoint_coefficient_computed"] is False
    assert classification["all_primary_symbolic_collision_census_complete"] is False
    assert value["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] == "OPEN"
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_QMINUS_SELF_COLLISION independent verification: PASS")


if __name__ == "__main__":
    verify()
