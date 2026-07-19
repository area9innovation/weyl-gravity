"""Independent verifier for exceptional L2 difference-frequency nonresonance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_difference_frequency_nonresonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ell1_difference_frequency_nonresonance.schema.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = value["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()
    n, u, v = sp.symbols("n u v")
    generic = value["generic_generic_elimination"]["records"]
    assert len(generic) == 27
    assert {(row["offset"], row["left_branch"], row["right_branch"]) for row in generic} == {
        (offset, left, right)
        for offset in range(3)
        for left in ("minus", "extra", "plus")
        for right in ("minus", "extra", "plus")
    }
    by_generic_key = {(row["offset"], row["left_branch"], row["right_branch"]): row for row in generic}
    signs = {"minus": -1, "plus": 1}
    for offset in range(3):
        left_lambda = n * (n + 1)
        right_lambda = (n + offset) * (n + offset + 1)
        for left_branch in ("minus", "extra", "plus"):
            for right_branch in ("minus", "extra", "plus"):
                left = left_lambda - sp.Rational(2, 3) if left_branch == "extra" else left_lambda + signs[left_branch] * u
                right = right_lambda - sp.Rational(2, 3) if right_branch == "extra" else right_lambda + signs[right_branch] * v
                equation = sp.numer(sp.together((left + right - sp.Rational(16, 3)) ** 2 - 4 * left * right))
                if left_branch == "extra":
                    equation = equation.subs(u, 0)
                else:
                    equation = sp.resultant(equation, u**2 - 2 * left_lambda, u)
                if right_branch == "extra":
                    equation = equation.subs(v, 0)
                else:
                    equation = sp.resultant(equation, v**2 - 2 * right_lambda, v)
                polynomial = sp.Poly(equation, n).sqf_part().primitive()[1]
                row = by_generic_key[(offset, left_branch, right_branch)]
                assert [str(coefficient) for coefficient in polynomial.all_coeffs()] == row["polynomial_coefficients_descending"]
                roots = sp.polys.polytools.ground_roots(polynomial)
                assert not [root for root in roots if root.is_Integer and root >= 2]
                assert row["integer_roots_at_least_2"] == []
    dipole = value["dipole_generic_elimination"]["records"]
    assert len(dipole) == 12
    assert {(row["dipole"], row["generic_ell"], row["generic_branch"]) for row in dipole} == {
        (kind, ell, branch)
        for kind in ("physical_ell1", "exceptional_ell1")
        for ell in (2, 3)
        for branch in ("minus", "extra", "plus")
    }
    by_dipole_key = {(row["dipole"], row["generic_ell"], row["generic_branch"]): row for row in dipole}
    x = sp.symbols("x")
    bases = {"physical_ell1": sp.Integer(2), "exceptional_ell1": 2 / sp.sqrt(3)}
    for kind, base in bases.items():
        for ell in (2, 3):
            eigenvalue = sp.Integer(ell * (ell + 1))
            for branch in ("minus", "extra", "plus"):
                square = eigenvalue - sp.Rational(2, 3) if branch == "extra" else eigenvalue + signs[branch] * sp.sqrt(2 * eigenvalue)
                residual = sp.expand((sp.sqrt(square) - base) ** 2 - sp.Rational(16, 3))
                minimal = sp.Poly(sp.minpoly(residual, x), x).primitive()[1]
                row = by_dipole_key[(kind, ell, branch)]
                assert [str(coefficient) for coefficient in minimal.all_coeffs()] == row["minimal_polynomial_coefficients_descending"]
                assert minimal.eval(0) == sp.Integer(row["minimal_polynomial_constant"])
                assert minimal.eval(0) != 0
    classification = value["classification"]
    assert classification["no_k0_difference_frequency_collision"] is True
    assert classification["complete_k0_frequency_census_closed"] is True
    assert classification["positive_sum_live_global_times_ell2_extra_source_classified"] is False
    assert classification["opposite_nonzero_momenta_classified"] is False


if __name__ == "__main__":
    main()
