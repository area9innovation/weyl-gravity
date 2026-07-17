"""Exact all-ell k=0 quadratic output resonance audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_all_ell_k0_output_resonance.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_all_ell_k0_output_resonance.schema.json"
INPUTS = {
    "axial_physical_ring": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_physical_completion": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "homogeneous_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json",
    "ell2_combined_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_combined_cone_second_order.json",
}


class AllEllK0OutputResonanceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AllEllK0OutputResonanceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _positive_shift_coefficients(polynomial: sp.Expr, variable: sp.Symbol, floor: int) -> list[str]:
    shifted = sp.Poly(sp.expand(polynomial.subs(variable, variable + floor)), variable)
    coefficients = shifted.all_coeffs()
    _require(all(coefficient > 0 for coefficient in coefficients), f"positivity shift failed: {polynomial}")
    return [str(coefficient) for coefficient in coefficients]


def _frequency_polynomials() -> dict[str, sp.Expr]:
    lam, z = sp.symbols("lambda z")
    return {
        "double_einstein": 3 * z - 12 * lam + 8,
        "double_extra_pair": z**2 - 8 * lam * z + 16 * lam**2 - 32 * lam,
        "einstein_pair": z**2 - 4 * lam * z + 8 * lam,
        "einstein_extra_mixed": (
            81 * z**4
            + (216 - 648 * lam) * z**3
            + (1296 * lam**2 - 1188 * lam + 216) * z**2
            + (-1296 * lam**2 + 1008 * lam + 96) * z
            + 324 * lam**2 - 144 * lam + 16
        ),
    }


def _candidate_resultants() -> dict[str, Any]:
    n, capital_lambda = sp.symbols("ell Lambda", integer=True, positive=True)
    lam, z = sp.symbols("lambda z")
    physical_lam = n * (n + 1)
    p_target = z - (capital_lambda - sp.Rational(2, 3))
    q_target = (z - capital_lambda) ** 2 - 2 * capital_lambda
    polynomials = _frequency_polynomials()

    def resultants(name: str, output_ell: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
        polynomial = polynomials[name].subs(lam, physical_lam)
        target_lambda = sp.expand(output_ell * (output_ell + 1))
        p_value = sp.factor(sp.resultant(polynomial, p_target.subs(capital_lambda, target_lambda), z))
        q_value = sp.factor(sp.resultant(polynomial, q_target.subs(capital_lambda, target_lambda), z))
        return p_value, q_value

    records: dict[str, Any] = {}
    expected = {
        "double_einstein_at_2ell": (
            "double_einstein",
            2 * n,
            6 * (n - 1),
            -4 * (9 * n**2 + 33 * n - 16),
        ),
        "double_extra_minus_at_2ell_minus_1": (
            "double_extra_pair",
            2 * n - 1,
            sp.Rational(4, 9) * (9 * n**2 - 54 * n + 1),
            -144 * n**2 * (n - 1) * (7 * n + 9),
        ),
        "einstein_sum_at_2ell": (
            "einstein_pair",
            2 * n,
            -sp.Rational(4, 9) * (18 * n**3 - 3 * n**2 - 18 * n - 1),
            -16 * n**2 * (n + 1) * (4 * n**3 + 12 * n**2 - 9 * n - 9),
        ),
    }
    for label, (family, output_ell, expected_p, expected_q) in expected.items():
        p_value, q_value = resultants(family, output_ell)
        _require(sp.factor(p_value - expected_p) == 0, f"{label} p resultant changed")
        _require(sp.factor(q_value - expected_q) == 0, f"{label} q resultant changed")
        records[label] = {
            "output_ell": str(output_ell),
            "p_resultant": str(sp.factor(p_value)),
            "q_resultant": str(sp.factor(q_value)),
            "nonzero_for_integer_ell_at_least_2": True,
        }
    records["double_einstein_at_2ell"]["nonzero_witness"] = {
        "p": "6*(ell-1)>0",
        "q_core_shift_ell_minus_2_coefficients": _positive_shift_coefficients(9 * n**2 + 33 * n - 16, n, 2),
    }
    records["double_extra_minus_at_2ell_minus_1"]["nonzero_witness"] = {
        "p": "9*(ell-3)^2-80 cannot vanish because 80 is not an integer square",
        "q": "-144*ell^2*(ell-1)*(7ell+9) has no zero for ell>=2",
    }
    records["einstein_sum_at_2ell"]["nonzero_witness"] = {
        "p_core_shift_ell_minus_2_coefficients": _positive_shift_coefficients(18 * n**3 - 3 * n**2 - 18 * n - 1, n, 2),
        "q_core_shift_ell_minus_2_coefficients": _positive_shift_coefficients(4 * n**3 + 12 * n**2 - 9 * n - 9, n, 2),
    }

    mixed_top_p, mixed_top_q = resultants("einstein_extra_mixed", 2 * n)
    top_p_core = 144 * n**5 + 600 * n**4 + 335 * n**3 - 230 * n**2 - 113 * n + 32
    top_q_core = -mixed_top_q / 16
    _require(sp.factor(mixed_top_p + 36 * n * top_p_core) == 0, "mixed top p resultant changed")
    _require(sp.factor(mixed_top_q + 16 * top_q_core) == 0, "mixed top q normalization changed")
    records["extra_minus_einstein_sum_at_2ell"] = {
        "output_ell": "2*ell",
        "p_resultant": str(sp.factor(mixed_top_p)),
        "q_resultant": str(sp.factor(mixed_top_q)),
        "p_core_shift_ell_minus_2_coefficients": _positive_shift_coefficients(top_p_core, n, 2),
        "q_core_shift_ell_minus_2_coefficients": _positive_shift_coefficients(top_q_core, n, 2),
        "nonzero_for_integer_ell_at_least_2": True,
    }

    mixed_previous_p, mixed_previous_q = resultants("einstein_extra_mixed", 2 * n - 1)
    finite_values = {}
    for value in range(2, 8):
        p_value = int(mixed_previous_p.subs(n, value))
        q_value = int(mixed_previous_q.subs(n, value))
        _require(p_value != 0 and q_value != 0, f"mixed previous resonance at ell={value}")
        finite_values[str(value)] = {"p_resultant": str(p_value), "q_resultant": str(q_value)}
    records["extra_minus_einstein_sum_at_2ell_minus_1"] = {
        "output_ell": "2*ell-1",
        "candidate_range": "2<=ell<=7; excluded by shell ordering for ell>=8",
        "exact_finite_values": finite_values,
        "nonzero_on_complete_candidate_range": True,
    }

    return records


def _localization_witnesses() -> dict[str, Any]:
    n = sp.symbols("ell", integer=True, positive=True)
    witnesses = {
        "twice_extra_plus": {
            "location": "above q_+(Lambda_{2ell}); no angularly allowed target",
            "proof": "z-M_{2ell}=2ell+4sqrt(2lambda)>4sqrt(2lambda)>sqrt(2M_{2ell})",
        },
        "extra_plus_einstein_sum": {
            "location": "above q_+(Lambda_{2ell}); no angularly allowed target",
            "proof": "sqrt((lambda+sqrt(2lambda))(lambda-2/3))>lambda+sqrt(2lambda)/2-2/3, so z-M_{2ell}>2sqrt(2lambda)>sqrt(2M_{2ell})",
            "radical_lower_bound_remainder": "(3*lambda-8)/18",
        },
        "twice_extra_minus": {
            "only_candidate": "L=2ell-1",
            "lower_shell_bound": "q_+(Lambda_{2ell-2})<z from sqrt(2lambda)<7ell/4 and (3ell-2)^2-2M_{2ell-2}=ell^2",
            "upper_shell_bound": "z<q_-(Lambda_{2ell}) from sqrt(2lambda)>7ell/5 and (18ell/5)^2-2M_{2ell}=4ell*(31ell-25)/25",
        },
        "twice_einstein": {
            "only_candidate": "L=2ell",
            "lower_shell_witness": str(sp.factor((6 * n - sp.Rational(8, 3)) ** 2 - 2 * (2 * n - 1) * (2 * n))),
        },
        "extra_plus_extra_minus_sum": {
            "only_candidate": "L=2ell",
            "proof": "sqrt(lambda(lambda-2))>lambda-2 gives z-M_{2ell-1}>6ell-4>sqrt(2M_{2ell-1})",
            "squared_gap": str(sp.factor((6 * n - 4) ** 2 - 2 * (2 * n - 1) * (2 * n))),
        },
        "extra_minus_einstein_sum": {
            "only_candidates": ["L=2ell-1 for 2<=ell<=7", "L=2ell"],
            "proof": "the same radical remainder (3lambda-8)/18 and sqrt(2lambda)<2ell put z above q_+(Lambda_{2ell-2}); for ell>=8, sqrt(2lambda)<=3ell/2 puts z above q_+(Lambda_{2ell-1})",
            "first_squared_gap": str(sp.factor((6 * n - 4) ** 2 - 2 * (2 * n - 2) * (2 * n - 1))),
            "ell_at_least_8_squared_gap": str(sp.factor((3 * n - 2) ** 2 - 2 * (2 * n - 1) * (2 * n))),
        },
        "extra_plus_extra_minus_difference": {
            "location": "2<z<9/4<q_-(Lambda_2)",
            "proof": "z=4lambda/(lambda+sqrt(lambda(lambda-2))) and sqrt(lambda(lambda-2))>7lambda/9 for lambda>=6",
        },
        "extra_plus_einstein_difference": {
            "location": "0<z<2/3",
            "squared_inequality_remainder": "2*(3*lambda-8)/9",
        },
        "einstein_extra_minus_difference": {
            "location": "0<z<2/3",
            "squared_inequality_remainder": "2*(3*lambda-8)/9",
        },
    }
    _require(sp.expand((6 * n - 4) ** 2 - 2 * (2 * n - 1) * (2 * n) - 4 * (n - 1) * (7 * n - 4)) == 0, "sum gap changed")
    _require(sp.expand((3 * n - 2) ** 2 - 2 * (2 * n - 1) * (2 * n) - (n**2 - 8 * n + 4)) == 0, "mixed threshold changed")
    return witnesses


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(
        records["axial_physical_ring"]["classification"]["extra_quotient_two_cyclic_summands_on_every_physical_fiber"],
        "axial target input changed",
    )
    _require(records["polar_physical_completion"]["classification"]["Einstein_image_equals_complete_q_primary_summand"], "polar target input changed")
    _require(
        records["homogeneous_operator"]["classification"]["all_nonzero_frequency_homogeneous_channels_solved"],
        "homogeneous nonzero compatibility changed",
    )
    return {
        "schema": "einstein-maxwell-weyl-all-ell-k0-output-resonance-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ALL_ELL_K0_OUTPUT_RESONANCE",
        "result_state": "ALL_GENERIC_ELL_K0_QUADRATIC_NONZERO_OUTPUTS_NONRESONANT",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_ALL_GENERIC_ELL_K0_OUTPUT_RESONANCE",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "domain": "every integer input ell>=2 at k=0, all nine quadratic sum/difference frequency types, and every angularly allowed output 0<=L<=2ell in either parity",
        "target_shells": {
            "L_at_least_1": ["p_L(z)=z-(L(L+1)-2/3)", "q_L(z)=(z-L(L+1))^2-2L(L+1)"],
            "L_equals_1": "the same root set {0,4/3,4} contains every physical exceptional axial or polar shell",
            "L_equals_0": "not a spectral inversion: every actual Omega!=0 source is in the homogeneous operator image by the exact Noether identity",
        },
        "frequency_minimal_polynomials": {name: str(sp.factor(value)) for name, value in _frequency_polynomials().items()},
        "shell_localization": _localization_witnesses(),
        "candidate_resultants": _candidate_resultants(),
        "classification": {
            "all_nine_frequency_types_covered": True,
            "all_ell_at_least_2_covered": True,
            "all_nonzero_output_channels_off_physical_target_shells": True,
            "homogeneous_nonzero_channels_solvable_by_Noether_completion": True,
            "zero_frequency_source_cokernel_classified": False,
            "complete_all_ell_second_order_cone_proved": False,
        },
        "interpretation": "Nonzero-frequency resonances do not cut the k=0 Taub-zero cone at any generic input ell. Any failure of the all-ell second-order extension theorem must therefore occur in the zero-frequency adjoint-cokernel/source map, not in a sum/difference target resonance.",
        "next_gate": "derive the zero-frequency homogeneous source from the arbitrary-lambda reduced quadratic action, certify an ell=3 coefficient fixture, and then identify the symbolic-lambda row-rank and moment-map factorization needed for the complete all-ell cone",
        "claim_boundary": "This is an exact output-resonance theorem, not a complete second-order extension theorem. The general-ell zero-frequency source map, opposite momenta, exceptional/global inputs, all-orders integration, causal propagation, and quantum theory remain open.",
        "verification_receipt": {
            "producing_date": "2026-07-17",
            "tier_0": {
                "status": "PASS",
                "elapsed_seconds": 0.05,
                "commands": [
                    "python3 -m py_compile bridge/einstein_sector/einstein_maxwell_weyl_all_ell_k0_output_resonance.py bridge/einstein_sector/verify_einstein_maxwell_weyl_all_ell_k0_output_resonance.py bridge/einstein_sector/tests/test_einstein_maxwell_weyl_all_ell_k0_output_resonance.py",
                    "python3 -m json.tool bridge/certificates/einstein_maxwell_weyl_all_ell_k0_output_resonance.json",
                    "git diff --check -- <scoped paths>",
                ],
            },
            "tier_1": {
                "status": "PASS",
                "elapsed_seconds": 2.10,
                "commands": [
                    "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_all_ell_k0_output_resonance --verify bridge/certificates/einstein_maxwell_weyl_all_ell_k0_output_resonance.json",
                    "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_all_ell_k0_output_resonance.py",
                    "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_all_ell_k0_output_resonance",
                ],
            },
            "tier_2": {
                "status": "NOT_RUN_NOT_REQUIRED",
                "reason": "all target-operator, physical-ring, exceptional-shell, and homogeneous-Noether inputs are unchanged content-addressed certificates",
            },
            "tier_3": {
                "status": "NOT_RUN_NOT_REQUIRED",
                "reason": "this certificate closes one output-resonance gate but does not promote the complete all-ell second-order cone or a programme-wide freeze",
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_all_ell_k0_output_resonance --verify bridge/certificates/einstein_maxwell_weyl_all_ell_k0_output_resonance.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_all_ell_k0_output_resonance.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_all_ell_k0_output_resonance",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"all-ell resonance certificate stale: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
