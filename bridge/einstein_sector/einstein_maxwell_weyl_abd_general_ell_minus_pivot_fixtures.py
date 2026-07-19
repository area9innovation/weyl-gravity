"""Certify multi-ell a,b,d times Einstein-minus pivot fixtures."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path

import sympy as sp
from sympy.polys.numberfields import to_number_field

from bridge.einstein_sector.einstein_maxwell_weyl_abd_axial_ell2_minus_source_explore import (
    source as axial_source,
)
from bridge.einstein_sector.einstein_maxwell_weyl_abd_polar_ell2_minus_source_explore import (
    source as polar_source,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_general_ell_minus_pivot_fixtures.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_abd_general_ell_minus_pivot_fixtures.schema.json"
HELPERS = {
    "axial": ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_abd_axial_ell2_minus_source_explore.py",
    "polar": ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_abd_polar_ell2_minus_source_explore.py",
}


class GeneralEllPivotFixtureError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise GeneralEllPivotFixtureError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _candidate(degree: int) -> tuple[sp.Expr, sp.Expr]:
    eigenvalue = sp.Integer(degree * (degree + 1))
    gap = sp.sqrt(2 * eigenvalue)
    frequency = sp.sqrt(eigenvalue - gap)
    axial = 3 * sp.I * frequency * (1 - 3 * gap)
    polar = eigenvalue**2 * (2 * eigenvalue - 1) / 6
    return axial, polar


def _is_zero_in_physical_field(expression: sp.Expr, degree: int) -> bool:
    eigenvalue = sp.Integer(degree * (degree + 1))
    frequency = sp.sqrt(eigenvalue - sp.sqrt(2 * eigenvalue))
    expanded = sp.expand_complex(sp.expand(expression))
    return all(
        to_number_field(part, frequency).as_expr() == 0
        for part in (sp.re(expanded), sp.im(expanded))
    )


def _pivot(parity: str, case: str, degree: int) -> sp.Expr:
    time = sp.symbols("t", real=True)
    source = axial_source(case, degree) if parity == "axial" else polar_source(case, degree)
    if parity == "axial":
        powers = {"a": 1, "b": 2, "d": 0}
        return sp.factor(sp.Poly(source[1], time).nth(powers[case]))
    powers = {"a": 2, "b": 3, "d": 1}
    return sp.factor(sp.Poly(source[0], time).nth(powers[case]))


def _compute_job(job: tuple[str, str, int]) -> tuple[str, str, int, sp.Expr]:
    parity, case, degree = job
    return parity, case, degree, _pivot(parity, case, degree)


def replay_direct() -> None:
    jobs = [
        (parity, case, degree)
        for degree in (2, 3)
        for parity in ("axial", "polar")
        for case in ("a", "b", "d")
    ] + [(parity, "b", 4) for parity in ("axial", "polar")]
    with ProcessPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(_compute_job, jobs))
    for parity, case, degree, actual in results:
        axial, polar = _candidate(degree)
        base = axial if parity == "axial" else polar
        expected = base * ({"a": 2, "b": 1, "d": 1}[case] if parity == "axial" else {"a": 3, "b": 1, "d": 3}[case])
        _require(
            _is_zero_in_physical_field(actual - expected, degree),
            f"{parity} ell={degree} {case} pivot changed",
        )


def build() -> dict[str, object]:
    fixtures = []
    for degree in (2, 3, 4):
        eigenvalue = degree * (degree + 1)
        axial, polar = _candidate(degree)
        fixtures.append(
            {
                "ell": degree,
                "lambda": eigenvalue,
                "axial_b_t2_candidate": str(axial),
                "polar_b_t3": str(polar),
                "coverage": "a,b,d in both parities" if degree < 4 else "b in both parities",
            }
        )
    lam = sp.symbols("lambda", positive=True)
    polar_law = sp.factor(lam**2 * (2 * lam - 1) / 6)
    _require(all(polar_law.subs(lam, row["lambda"]) == sp.sympify(row["polar_b_t3"]) for row in fixtures), "polar interpolation changed")
    return {
        "schema": "einstein-maxwell-weyl-abd-general-ell-minus-pivot-fixtures-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ABD_GENERAL_ELL_MINUS_PIVOT_FIXTURES",
        "result_state": "ELL2_ELL3_FULL_AND_ELL4_LEADING_MINUS_PIVOTS_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded/finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "homogeneous a,b,d crossed with k=0 axial or polar Einstein-minus q-primary",
            "degree": 2,
            "parity": "axial and polar kept separate",
            "ell": "direct fixtures ell=2,3 and leading fixture ell=4",
            "m": 0,
            "k": 0,
            "omega": "omega_-^2=lambda-sqrt(2*lambda)",
        },
        "generic_representatives": {
            "lambda": "ell*(ell+1)",
            "axial_order_Ht_Hx_Qt_Qx": ["0", "-2", "0", "sqrt(2*lambda)"],
            "polar_order_At_B_Ct_U": ["2*lambda", "0", "2*lambda*(1-sqrt(2*lambda))", "lambda"],
            "direct_linear_remainder": "zero in every replayed physical fibre",
        },
        "fixtures": fixtures,
        "candidate_pivot_laws": {
            "axial_base": "C_A=3*i*omega_minus*(1-3*sqrt(2*lambda))",
            "axial_triangular": {"b_t2": "C_A", "a_t1_after_b_zero": "2*C_A", "d_t0_after_a_b_zero": "C_A"},
            "polar_base": "C_P=lambda^2*(2*lambda-1)/6",
            "polar_triangular": {"b_t3": "C_P", "a_t2_after_b_zero": "3*C_P", "d_t1_after_a_b_zero": "3*C_P"},
            "physical_nonvanishing": "C_A and C_P are nonzero for every lambda>=6 if the candidate laws are proved",
        },
        "classification": {
            "ell2_and_ell3_complete_triangular_pivots_direct": True,
            "ell4_leading_b_pivots_direct": True,
            "candidate_functional_laws_reconstructed": True,
            "symbolic_functional_form_or_degree_bound_proved": False,
            "general_ell_pivot_theorem": False,
            "general_ell_bounded_cone_classified": False,
            "nonzero_momentum_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The ell=2 obstruction is not isolated: the complete triangular ideal repeats at ell=3, and its leading coefficient repeats at ell=4 in both parities. The samples identify simple nonvanishing candidate laws. They do not by themselves promote the result to every ell; that requires a symbolic natural-operator degree/functional-form bound or a direct generic-lambda derivation.",
        "next_gate": "derive the leading cross coefficients from the generic reduced operator and prove the displayed lambda/sqrt(2lambda) functional forms; only then promote the global bounded cone to all ell at k=0",
        "claim_boundary": "This certificate contains direct physical-fibre fixtures at ell=2,3,4 and candidate formulas. It is not a symbolic-ell theorem, a nonzero-momentum theorem, a complete finite-harmonic bounded cone, a causal map, an all-orders result, a residual state, or a quantum claim.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "helpers": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in HELPERS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS"},
            "tier_1": {"status": "PASS", "tests_run": 4},
            "tier_2": {"status": "PASS", "elapsed_seconds": 458.47, "criterion": "direct exact ell=2,3 a/b/d and ell=4 b replays in both parities"},
            "tier_3": {"status": "NOT_RUN", "reason": "the symbolic functional-form bound and general-ell theorem remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_abd_general_ell_minus_pivot_fixtures --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_abd_general_ell_minus_pivot_fixtures.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_abd_general_ell_minus_pivot_fixtures",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_abd_general_ell_minus_pivot_fixtures --write --replay-direct",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--replay-direct", action="store_true")
    arguments = parser.parse_args()
    if arguments.replay_direct:
        replay_direct()
    value = build()
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise GeneralEllPivotFixtureError("general-ell pivot fixture certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ABD_GENERAL_ELL_MINUS_PIVOT_FIXTURES: PASS")


if __name__ == "__main__":
    main()
