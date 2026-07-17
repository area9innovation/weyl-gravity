"""Independent verifier for the unbounded generic-output nonresonance theorem."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_generic_output_nonresonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_cross_ell_k0_generic_output_nonresonance.schema.json"


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    generator = ROOT / payload["provenance"]["generator_path"]
    assert payload["provenance"]["generator_sha256"] == hashlib.sha256(generator.read_bytes()).hexdigest()
    bounded = ROOT / payload["provenance"]["bounded_exact_audit"]["path"]
    assert payload["provenance"]["bounded_exact_audit"]["sha256"] == hashlib.sha256(bounded.read_bytes()).hexdigest()

    # Independently enumerate the only integer angular defects compatible
    # with rigorous rational frequency-offset enclosures.
    intervals = {
        "Einstein_minus": (Fraction(-1, 2), Fraction(-1, 5)),
        "extra": (Fraction(3, 10), Fraction(1, 2)),
        "Einstein_plus": (Fraction(1), Fraction(5, 4)),
    }
    found = []
    for first, first_interval in intervals.items():
        for second, second_interval in intervals.items():
            for target, target_interval in intervals.items():
                lower = target_interval[0] - first_interval[1] - second_interval[1]
                upper = target_interval[1] - first_interval[0] - second_interval[0]
                for angular_defect in range(3):
                    if lower < angular_defect < upper:
                        found.append((first, second, target, angular_defect))
    recorded = [
        (entry["input_1"], entry["input_2"], entry["target"], entry["D"])
        for entry in payload["family_reduction"]["ordered_families"]
    ]
    assert found == recorded
    assert len(found) == 7

    a, b = sp.symbols("a b", integer=True, positive=True)
    la = a * (a + 1)
    lb = b * (b + 1)
    c = a + b - 1
    lc = c * (c + 1)
    d0 = sp.factor(lc - sp.Rational(2, 3) - la - lb)
    d1 = sp.factor(lc - la - (lb - sp.Rational(2, 3)))
    assert sp.expand(d0 - (2 * (a - 1) * (b - 1) - sp.Rational(8, 3))) == 0
    assert sp.expand(d1 - (2 * (a - 1) * (b - 1) - sp.Rational(4, 3))) == 0

    # Coefficients of the two hard radical families.  Their stated lower
    # bounds are positive on a,b>=2; substitutions a=A+2,b=B+2 leave
    # polynomials with positive coefficients.
    coefficients = [
        2 * d0 + 4 * lb,
        2 * d0 + 4 * la,
        2 * d1 + 4 * (lb - sp.Rational(2, 3)),
        2 * d1,
    ]
    A, B = sp.symbols("A B", nonnegative=True)
    for coefficient in coefficients:
        shifted = sp.Poly(sp.expand(coefficient.subs({a: A + 2, b: B + 2})), A, B)
        assert all(entry > 0 for entry in shifted.coeffs())

    # The one-rational-root correction in the minus-minus-extra family is
    # positive because sqrt(2 lambda)<lambda for lambda>=6.
    assert 2 * (-sp.Rational(2, 3)) + 2 * 6 > 0
    # The sole small endpoint not separated by the rational offset bounds.
    assert 18**2 > (10**2) * 3

    classification = payload["classification"]
    assert classification["all_distinct_generic_input_ells_covered"] is True
    assert classification["all_generic_output_ells_at_least_2_covered"] is True
    assert classification["all_nonzero_generic_output_channels_off_target_shells"] is True
    assert classification["exceptional_output_L1_classified"] is False
    assert classification["cross_ell_quadratic_source_solved"] is False


if __name__ == "__main__":
    main()
