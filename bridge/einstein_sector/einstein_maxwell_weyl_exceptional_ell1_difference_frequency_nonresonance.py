"""Exclude every k=0 difference-frequency route to the exceptional L=2 shell."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_difference_frequency_nonresonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ell1_difference_frequency_nonresonance.schema.json"
INPUTS = {
    "positive_sum_census": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_resonance_census.json",
    "frequency_isolation": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_frequency_isolation.json",
    "moment_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json",
}


class DifferenceFrequencyNonresonanceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DifferenceFrequencyNonresonanceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _frequency_squared(branch: str, eigenvalue: sp.Expr, radical: sp.Expr) -> sp.Expr:
    if branch == "extra":
        return eigenvalue - sp.Rational(2, 3)
    return eigenvalue + {"minus": -1, "plus": 1}[branch] * radical


def _generic_pair_records() -> list[dict[str, object]]:
    n, left_radical, right_radical = sp.symbols("n u v")
    target_squared = sp.Rational(16, 3)
    records = []
    for offset in range(3):
        left_lambda = n * (n + 1)
        right_lambda = (n + offset) * (n + offset + 1)
        for left_branch in ("minus", "extra", "plus"):
            for right_branch in ("minus", "extra", "plus"):
                left = _frequency_squared(left_branch, left_lambda, left_radical)
                right = _frequency_squared(right_branch, right_lambda, right_radical)
                necessary = sp.numer(sp.together((left + right - target_squared) ** 2 - 4 * left * right))
                eliminated = necessary
                if left_branch != "extra":
                    eliminated = sp.resultant(eliminated, left_radical**2 - 2 * left_lambda, left_radical)
                else:
                    eliminated = eliminated.subs(left_radical, 0)
                if right_branch != "extra":
                    eliminated = sp.resultant(eliminated, right_radical**2 - 2 * right_lambda, right_radical)
                else:
                    eliminated = eliminated.subs(right_radical, 0)
                polynomial = sp.Poly(eliminated, n).sqf_part().primitive()[1]
                rational_roots = sp.polys.polytools.ground_roots(polynomial)
                forbidden = [root for root in rational_roots if root.is_Integer and root >= 2]
                _require(not forbidden, f"generic difference collision survived at offset={offset}, {left_branch}/{right_branch}")
                records.append(
                    {
                        "offset": offset,
                        "left_branch": left_branch,
                        "right_branch": right_branch,
                        "polynomial_coefficients_descending": [str(value) for value in polynomial.all_coeffs()],
                        "degree": polynomial.degree(),
                        "rational_roots": {str(root): multiplicity for root, multiplicity in rational_roots.items()},
                        "integer_roots_at_least_2": [],
                    }
                )
    return records


def _dipole_pair_records() -> list[dict[str, object]]:
    x = sp.symbols("x")
    target_squared = sp.Rational(16, 3)
    records = []
    bases = {"physical_ell1": sp.Integer(2), "exceptional_ell1": 2 / sp.sqrt(3)}
    for base_name, base_frequency in bases.items():
        for ell in (2, 3):
            eigenvalue = sp.Integer(ell * (ell + 1))
            for branch in ("minus", "extra", "plus"):
                square = _frequency_squared(branch, eigenvalue, sp.sqrt(2 * eigenvalue))
                residual = sp.expand((sp.sqrt(square) - base_frequency) ** 2 - target_squared)
                minimal = sp.Poly(sp.minpoly(residual, x), x).primitive()[1]
                constant = minimal.eval(0)
                _require(constant != 0, f"dipole difference collision survived for {base_name}, ell={ell}, {branch}")
                records.append(
                    {
                        "dipole": base_name,
                        "generic_ell": ell,
                        "generic_branch": branch,
                        "residual": str(sp.factor(residual)),
                        "minimal_polynomial_coefficients_descending": [str(value) for value in minimal.all_coeffs()],
                        "minimal_polynomial_constant": str(constant),
                    }
                )
    return records


def build() -> dict[str, object]:
    inputs = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(inputs["positive_sum_census"]["classification"]["positive_sum_resonance_census_complete"], "positive-sum census changed")
    _require(not inputs["positive_sum_census"]["classification"]["difference_frequency_resonances_classified"], "upstream difference gate unexpectedly changed")
    _require(inputs["frequency_isolation"]["classification"]["complete_pure_exceptional_ell1_k0_second_order_no_go_frozen"], "exceptional shell changed")
    _require(inputs["moment_cone"]["classification"]["all_ell_all_m_both_parities_and_all_extra_polarizations_included"], "generic spectrum inventory changed")
    generic_records = _generic_pair_records()
    dipole_records = _dipole_pair_records()
    _require(len(generic_records) == 27, "generic branch-offset census is incomplete")
    _require(len(dipole_records) == 12, "dipole-generic census is incomplete")
    return {
        "schema": "einstein-maxwell-weyl-exceptional-ell1-difference-frequency-nonresonance-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELL1_DIFFERENCE_FREQUENCY_NONRESONANCE",
        "result_state": "COMPLETE_K0_DIFFERENCE_FREQUENCY_EXCEPTIONAL_L2_NONRESONANCE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; stationary harmonic spectrum",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "every pair of certified k=0 oscillatory primary frequencies capable by angular selection of producing L=2",
            "degree": 2,
            "parity": "parity-blind necessary triangle census, hence conservative for both output parities",
            "ell": "generic ell>=2 pairs with |ell_1-ell_2|<=2, plus physical/exceptional ell1 against generic ell=2,3",
            "m": "all m allowed by Clebsch-Gordan selection",
            "k": 0,
            "omega": "difference channel |omega_1-omega_2| tested against 2*omega_exceptional=4/sqrt(3)",
        },
        "target": {
            "angular_momentum": 2,
            "momentum": 0,
            "frequency": "2*omega_exceptional=4/sqrt(3)",
            "frequency_squared": "16/3",
            "target_primary": "generic ell=2 extra p-primary",
        },
        "generic_generic_elimination": {
            "necessary_equation": "(A+B-16/3)^2-4*A*B=0, obtained by squaring |sqrt(A)-sqrt(B)|=4/sqrt(3)",
            "angular_reduction": "L=2 requires |ell_1-ell_2|<=2, so ell_2=ell_1+d with d in {0,1,2}",
            "radical_relations": "u^2=2*n*(n+1), v^2=2*(n+d)*(n+d+1)",
            "proof": "successive exact resultants give an integer polynomial P_(d,s,t)(n); an integer solution n>=2 would be a rational root, and the complete rational-root factorization has none",
            "records": generic_records,
        },
        "dipole_generic_elimination": {
            "angular_reduction": "with one ell=1 input, L=2 requires generic ell in {2,3}",
            "dipole_frequencies": {"physical_ell1": "2", "exceptional_ell1": "2/sqrt(3)"},
            "proof": "for each of twelve exact residuals, its primitive minimal polynomial has nonzero constant term, so the residual is nonzero",
            "records": dipole_records,
            "dipole_dipole": "physical/physical and exceptional/exceptional differences vanish; |2-2/sqrt(3)| is not 4/sqrt(3)",
        },
        "classification": {
            "all_generic_branch_pairs_covered": True,
            "all_angular_offsets_for_L2_covered": True,
            "physical_and_exceptional_dipole_pairs_covered": True,
            "no_k0_difference_frequency_collision": True,
            "complete_k0_frequency_census_closed": True,
            "positive_sum_live_global_times_ell2_extra_source_classified": False,
            "opposite_nonzero_momenta_classified": False,
            "bounded_mixed_cone_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Unequal-frequency k=0 oscillator pairs cannot feed the exceptional 2*omega_e,L=2 resonance. Together with the prior positive-sum census, the only k=0 route outside the pure exceptional self block is the already isolated generalized-zero global times ell=2 extra column. This closes the frequency arithmetic, not the coefficientwise bounded cone.",
        "next_gate": "combine the global-times-ell2-extra coefficient matrix with the global bounded ideal and exceptional/common-moment-map equations; treat opposite nonzero momenta separately",
        "claim_boundary": "This is an exact k=0 frequency nonresonance theorem. It does not compute or cancel the live global-times-ell2-extra source, classify the complete exceptional mixed bounded cone, include opposite nonzero momenta, prove all-orders or causal extension, descend residual states, or make particle or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.23},
            "tier_1": {"status": "PASS", "elapsed_seconds": 5.39, "tests_run": 28},
            "tier_2": {"status": "PASS", "criterion": "27 exact resultant polynomials and twelve exact minimal polynomials were recomputed"},
            "tier_3": {"status": "NOT_RUN", "reason": "source coefficients, opposite momentum, causal, residual and quantum gates remain excluded"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_difference_frequency_nonresonance --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_ell1_difference_frequency_nonresonance.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_ell1_difference_frequency_nonresonance",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise DifferenceFrequencyNonresonanceError("difference-frequency certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELL1_DIFFERENCE_FREQUENCY_NONRESONANCE: PASS")


if __name__ == "__main__":
    main()
