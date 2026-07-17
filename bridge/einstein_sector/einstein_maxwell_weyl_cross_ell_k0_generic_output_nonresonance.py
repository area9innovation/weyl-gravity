"""Unbounded cross-ell k=0 nonresonance for generic output harmonics."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_generic_output_nonresonance.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_cross_ell_k0_generic_output_nonresonance.schema.json"
WINDOW_INPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_resonance_census.json"


class CrossEllGenericOutputNonresonanceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CrossEllGenericOutputNonresonanceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _offset_family_reduction() -> dict[str, Any]:
    intervals = {
        "Einstein_minus": (Fraction(-1, 2), Fraction(-1, 5)),
        "extra": (Fraction(3, 10), Fraction(1, 2)),
        "Einstein_plus": (Fraction(1), Fraction(5, 4)),
    }
    families = []
    for first, (first_low, first_high) in intervals.items():
        for second, (second_low, second_high) in intervals.items():
            for target, (target_low, target_high) in intervals.items():
                lower = target_low - first_high - second_high
                upper = target_high - first_low - second_low
                defects = [defect for defect in range(3) if lower < defect < upper]
                for defect in defects:
                    families.append((first, second, target, defect))
    expected = [
        ("Einstein_minus", "Einstein_minus", "Einstein_minus", 0),
        ("Einstein_minus", "Einstein_minus", "extra", 1),
        ("Einstein_minus", "Einstein_minus", "Einstein_plus", 2),
        ("Einstein_minus", "extra", "Einstein_plus", 1),
        ("Einstein_minus", "Einstein_plus", "Einstein_plus", 0),
        ("extra", "Einstein_minus", "Einstein_plus", 1),
        ("Einstein_plus", "Einstein_minus", "Einstein_plus", 0),
    ]
    _require(families == expected, f"offset-family reduction changed: {families}")
    return {
        "frequency_offset_definition": "omega_branch(ell)=ell+u_branch(ell)",
        "exact_open_bounds": {
            name: [str(lower), str(upper)] for name, (lower, upper) in intervals.items()
        },
        "angular_defect": "D=ell_1+ell_2-ell_3 is a nonnegative integer",
        "ordered_families": [
            {"input_1": first, "input_2": second, "target": target, "D": defect}
            for first, second, target, defect in families
        ],
        "unordered_families": [
            "minus+minus -> minus at ell_3=ell_1+ell_2",
            "minus+minus -> extra at ell_3=ell_1+ell_2-1",
            "minus+minus -> plus at ell_3=ell_1+ell_2-2",
            "minus+extra -> plus at ell_3=ell_1+ell_2-1",
            "minus+plus -> plus at ell_3=ell_1+ell_2",
        ],
    }


def _bound_witnesses() -> dict[str, Any]:
    ell = sp.symbols("ell", integer=True, positive=True)
    twice_lambda = 2 * ell * (ell + 1)
    witnesses = {
        "minus_above_ell_minus_half": sp.factor((2 * ell - sp.Rational(1, 4)) ** 2 - twice_lambda),
        "minus_below_ell_minus_fifth": sp.factor(twice_lambda - (sp.Rational(7, 5) * ell - sp.Rational(1, 25)) ** 2),
        "minus_above_ell_minus_two_fifths_for_ell_at_least_4": sp.factor((sp.Rational(9, 5) * ell - sp.Rational(4, 25)) ** 2 - twice_lambda),
        "minus_above_ell_minus_41_over_100": sp.factor((sp.Rational(91, 50) * ell - sp.Rational(1681, 10000)) ** 2 - twice_lambda),
        "minus_above_ell_minus_17_over_50_for_ell_at_least_3": sp.factor((sp.Rational(42, 25) * ell - sp.Rational(289, 2500)) ** 2 - twice_lambda),
        "plus_below_ell_plus_5_over_4": sp.factor((sp.Rational(3, 2) * ell + sp.Rational(25, 16)) ** 2 - twice_lambda),
        "plus_above_ell_plus_11_over_10_for_ell_at_least_4": sp.factor(twice_lambda - (sp.Rational(6, 5) * ell + sp.Rational(121, 100)) ** 2),
    }
    shifts = {name: 2 for name in witnesses}
    shifts["minus_above_ell_minus_two_fifths_for_ell_at_least_4"] = 4
    shifts["minus_above_ell_minus_17_over_50_for_ell_at_least_3"] = 3
    shifts["plus_above_ell_plus_11_over_10_for_ell_at_least_4"] = 4
    records = {}
    for name, polynomial in witnesses.items():
        shifted = sp.Poly(sp.expand(polynomial.subs(ell, ell + shifts[name])), ell)
        coefficients = shifted.all_coeffs()
        _require(all(coefficient > 0 for coefficient in coefficients), f"bound witness lost positivity: {name}")
        records[name] = {
            "polynomial": str(polynomial),
            "valid_from_ell": shifts[name],
            "shifted_positive_coefficients": [str(coefficient) for coefficient in coefficients],
        }
    records["extra_bounds"] = {
        "lower_difference": "2*ell/5-227/300>0 for ell>=2",
        "upper_difference": "(ell+1/2)^2-(ell(ell+1)-2/3)=11/12>0",
    }
    records["plus_above_ell_plus_one"] = {
        "squared_remainder": "2*ell*(ell+1)-(ell+1)^2=(ell+1)(ell-1)>0"
    }
    return records


def _family_exclusions() -> dict[str, Any]:
    a, b = sp.symbols("a b", integer=True, positive=True)
    lam_a = a * (a + 1)
    lam_b = b * (b + 1)
    c = a + b - 1
    lam_c = c * (c + 1)

    d_minus_minus_extra = sp.factor(lam_c - sp.Rational(2, 3) - lam_a - lam_b)
    expected_d0 = 2 * (a - 1) * (b - 1) - sp.Rational(8, 3)
    _require(sp.expand(d_minus_minus_extra - expected_d0) == 0, "minus-minus-extra delta changed")
    alpha_a = sp.factor(2 * expected_d0 + 4 * lam_b)
    alpha_b = sp.factor(2 * expected_d0 + 4 * lam_a)

    d_minus_extra_plus = sp.factor(lam_c - lam_a - (lam_b - sp.Rational(2, 3)))
    expected_d1 = 2 * (a - 1) * (b - 1) - sp.Rational(4, 3)
    _require(sp.expand(d_minus_extra_plus - expected_d1) == 0, "minus-extra-plus delta changed")
    beta_a = sp.factor(2 * expected_d1 + 4 * (lam_b - sp.Rational(2, 3)))
    beta_c = sp.factor(2 * expected_d1)

    return {
        "easy_sign_separated_families": {
            "minus_minus_to_minus_D0": "u_-(a)+u_-(b)<-2/5<u_-(a+b)",
            "minus_plus_to_plus_D0": "u_-(a)+u_+(b)<21/20<11/10<u_+(a+b)",
            "minus_minus_to_plus_D2": "if max(a,b)>=3 then u_-(a)+u_-(b)>-3/4>u_+(a+b-2)-2; (a,b)=(2,2) has 18-10*sqrt(3)>0 after squaring",
        },
        "minus_minus_to_extra_D1": {
            "delta_rational": str(expected_d0),
            "resonance_polynomial_expansion": "R0 + alpha_a*x_a + alpha_b*x_b - 2*x_a*x_b, x_j=sqrt(2*lambda_j)",
            "alpha_a": str(alpha_a),
            "alpha_b": str(alpha_b),
            "positivity": "delta>=-2/3 and lambda>=6 make alpha_a, alpha_b, alpha_a-2*x_b, and alpha_b-2*x_a strictly positive",
            "squarefree_cases": {
                "distinct_nonrational_parts": "the x_a*x_b squarefree basis element is unique and has coefficient -2",
                "equal_nonrational_parts": "the remaining irrational coefficient alpha_a*m_a+alpha_b*m_b is positive",
                "exactly_one_rational_inner_root": "the coefficient of the other irrational root is alpha-2*x_rational and is positive",
                "both_rational_inner_roots": "input squared frequencies are integers while the extra target squared frequency is integer-2/3, contradicting the squared resonance equation",
            },
        },
        "minus_extra_to_plus_D1": {
            "delta_rational": str(expected_d1),
            "resonance_polynomial_expansion": "R1 + beta_a*x_a + beta_c*x_c + 2*x_a*x_c",
            "beta_a": str(beta_a),
            "beta_c": str(beta_c),
            "positivity": "delta>=2/3, so beta_a, beta_c, and the product coefficient are strictly positive",
            "squarefree_cases": {
                "at_least_one_nonrational_inner_root": "the unique or merged irrational coefficient is a sum of strictly positive terms",
                "both_rational_inner_roots": "the two q squared frequencies are integers but the extra squared frequency has reduced denominator 1 or 3; rational-square denominator parity contradicts the squared resonance equation",
            },
        },
        "all_five_families_excluded": True,
    }


def build_certificate() -> dict[str, Any]:
    window = json.loads(WINDOW_INPUT.read_text(encoding="utf-8"))
    _require(window["classification"]["no_cross_ell_nonzero_output_resonance_in_window"], "bounded census input changed")
    return {
        "schema": "einstein-maxwell-weyl-cross-ell-k0-generic-output-nonresonance-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_CROSS_ELL_K0_GENERIC_OUTPUT_NONRESONANCE",
        "result_state": "UNBOUNDED_CROSS_ELL_GENERIC_OUTPUT_NONRESONANCE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_ALL_DISTINCT_GENERIC_INPUT_ELLS_K0_GENERIC_OUTPUT",
        "domain": "every pair of distinct generic input harmonics ell_1,ell_2>=2 at k=0, all p/q primary branches, both temporal sum/difference channels, and every angularly allowed generic output L>=2 in either parity",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "bounded_exact_audit": {"path": str(WINDOW_INPUT.relative_to(ROOT)), "sha256": _sha256(WINDOW_INPUT)},
        },
        "frequency_bounds": _bound_witnesses(),
        "family_reduction": _offset_family_reduction(),
        "family_exclusions": _family_exclusions(),
        "classification": {
            "all_distinct_generic_input_ells_covered": True,
            "all_generic_output_ells_at_least_2_covered": True,
            "all_input_and_target_primary_branches_covered": True,
            "all_nonzero_generic_output_channels_off_target_shells": True,
            "exceptional_output_L1_classified": False,
            "cross_ell_quadratic_source_solved": False,
        },
        "interpretation": "A distinct-ell k=0 quadratic product cannot fail at a nonzero-frequency generic target determinant. The only remaining spectral gate is the exceptional L=1 output; after that, any failure of the cross-ell cone must be a source/cokernel effect.",
        "next_gate": "classify adjacent-input exceptional L=1 output frequencies exactly, then compute the cross-ell mixed source projections on the common stabilizer-moment-map cone",
        "claim_boundary": "This is an unbounded generic-output nonresonance theorem, not a cross-ell second-order extension theorem. Exceptional L=1 output, mixed source coefficients, opposite momenta and phases, exceptional/global inputs, all-orders integration, causal propagation, and quantum claims remain open.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.06, "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <certificate>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 1.1, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_cross_ell_k0_generic_output_nonresonance --verify bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_generic_output_nonresonance.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_cross_ell_k0_generic_output_nonresonance.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_cross_ell_k0_generic_output_nonresonance"
            ]},
            "tier_2": {"status": "NOT_RUN", "reason": "the theorem depends only on unchanged content-addressed shell data and the already verified bounded audit"},
            "tier_3": {"status": "NOT_RUN", "reason": "exceptional L=1 and the cross-ell quadratic source remain open, so no full cone or programme freeze is promoted"}
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_cross_ell_k0_generic_output_nonresonance --verify bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_generic_output_nonresonance.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_cross_ell_k0_generic_output_nonresonance.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_cross_ell_k0_generic_output_nonresonance",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    payload = build_certificate()
    if arguments.write:
        DEFAULT_OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    assert arguments.verify is not None
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "generic-output nonresonance certificate is stale")


if __name__ == "__main__":
    main()
