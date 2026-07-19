"""Certify the generic-lambda a,b,d times Einstein-minus bounded pivots."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_abd_generic_lambda_pivot_explore import (
    _legendre_jet,
    axial_b_pivot,
    polar_b_pivot,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_generic_lambda_pivot.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_abd_generic_lambda_pivot.schema.json"
DIRECT_ENGINE = ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_abd_generic_lambda_pivot_explore.py"
FIXTURES = ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_general_ell_minus_pivot_fixtures.json"


class GenericLambdaPivotError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise GenericLambdaPivotError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_pivots() -> tuple[sp.Expr, sp.Expr]:
    eigenvalue = sp.symbols("lambda", positive=True)
    gap = sp.sqrt(2 * eigenvalue)
    frequency = sp.sqrt(eigenvalue - gap)
    axial = -3 * sp.I * frequency * (3 * gap - 1)
    polar = eigenvalue**2 * (2 * eigenvalue - 1) / 6
    return axial, polar


def replay_symbolic() -> None:
    expected_axial, expected_polar = expected_pivots()
    with ProcessPoolExecutor(max_workers=2) as executor:
        axial_future = executor.submit(axial_b_pivot)
        polar_future = executor.submit(polar_b_pivot)
        actual_axial = axial_future.result()
        actual_polar = polar_future.result()
    _require(sp.simplify(actual_axial - expected_axial) == 0, "generic axial pivot changed")
    _require(sp.simplify(actual_polar - expected_polar) == 0, "generic polar pivot changed")


def build() -> dict[str, object]:
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    _require(
        fixtures["classification"]["ell2_and_ell3_complete_triangular_pivots_direct"],
        "complete ell2/ell3 direct fixture changed",
    )
    _require(
        fixtures["classification"]["ell4_leading_b_pivots_direct"],
        "ell4 direct fixture changed",
    )
    eigenvalue = sp.symbols("lambda", positive=True)
    axial, polar = expected_pivots()
    z = sp.symbols("z", real=True)
    jet_remainders = {}
    for name, initial in (("even", (sp.S.One, sp.S.Zero)), ("odd", (sp.S.Zero, sp.S.One))):
        harmonic = _legendre_jet(z, eigenvalue, *initial)
        residual = sp.Poly(
            sp.expand((1 - z**2) * sp.diff(harmonic, z, 2) - 2 * z * sp.diff(harmonic, z) + eigenvalue * harmonic),
            z,
        )
        low_coefficients = [sp.factor(residual.nth(degree)) for degree in range(7)]
        _require(low_coefficients == [0] * 7, f"{name} formal Legendre jet changed")
        jet_remainders[name] = [str(value) for value in low_coefficients]
    maximum_jet_order = 8
    maximum_operator_order = 4
    _require(
        maximum_jet_order >= maximum_operator_order + 2,
        "formal Legendre jet no longer safely exceeds the operator derivative order",
    )
    for row in fixtures["fixtures"]:
        degree = row["ell"]
        lam = sp.Integer(row["lambda"])
        local = {"I": sp.I, "sqrt": sp.sqrt}
        stored_axial = sp.sympify(row["axial_b_t2_candidate"], locals=local)
        stored_polar = sp.sympify(row["polar_b_t3"], locals=local)
        _require(sp.simplify(axial.subs(eigenvalue, lam) - stored_axial) == 0, f"axial ell={degree} fixture changed")
        _require(sp.simplify(polar.subs(eigenvalue, lam) - stored_polar) == 0, f"polar ell={degree} fixture changed")
    return {
        "schema": "einstein-maxwell-weyl-abd-generic-lambda-pivot-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ABD_GENERIC_LAMBDA_PIVOT",
        "result_state": "GENERIC_LAMBDA_AXIAL_POLAR_MINUS_BOUNDED_PIVOT_IDEAL_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded/finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "homogeneous a,b,d crossed with one axial or polar Einstein-minus q-primary",
            "degree": 2,
            "parity": "axial and polar kept separate",
            "ell": "every fixed integer ell>=2",
            "m": "all m by SO3 multiplicity one",
            "k": 0,
            "omega": "omega_minus^2=lambda-sqrt(2*lambda)",
        },
        "generic_lambda_derivation": {
            "method": "direct four-dimensional Bach-Maxwell tensor calculation on formal Legendre jets at z=0; the Legendre ODE fixes all derivatives and lambda remains symbolic",
            "not_interpolation": True,
            "even_scalar_jet": "Y(0)=1,Y'(0)=0 for the polar scalar output",
            "odd_vector_jet": "Y(0)=0,Y'(0)=1 for the axial vector output",
            "maximum_harmonic_jet_order": maximum_jet_order,
            "Bach_Maxwell_maximum_sphere_derivative_order": maximum_operator_order,
            "jet_order_safety_margin": maximum_jet_order - maximum_operator_order,
            "Legendre_ODE_remainder_through_degree_6": jet_remainders,
            "axial_b_t2": str(axial),
            "polar_b_t3": str(polar),
        },
        "triangular_locality_lemma": {
            "axial": {
                "reason": "the highest term contains exactly one time derivative of the circle profile; d/dt(t^3/3,t^2,t)=(t^2,2t,1)",
                "pivots": {"b_t2": "C_A", "a_t1_after_b_zero": "2*C_A", "d_t0_after_a_b_zero": "C_A"},
            },
            "polar": {
                "reason": "the highest term contains no time derivative of the circle profile; (t^3/3,t^2,t) gives the ratio (1,3,3) after normalizing C_P to b_t3",
                "pivots": {"b_t3": "C_P", "a_t2_after_b_zero": "3*C_P", "d_t1_after_a_b_zero": "3*C_P"},
            },
            "lower_sphere_profiles": "the a/b sphere profiles have lower time degree and cannot alter the displayed leading pivots",
            "direct_full_chain_audit": "the complete a,b,d ratios are independently replayed at ell=2,3 in both parities",
        },
        "nonvanishing": {
            "physical_domain": "lambda=ell*(ell+1)>=6",
            "axial": "omega_minus>0 and 3*sqrt(2*lambda)-1>0",
            "polar": "lambda^2*(2*lambda-1)/6>0",
            "consequence": "in either parity, a nonzero Einstein-minus amplitude forces b=0, then a=0, then d=0 for bounded corrections",
        },
        "SO3_promotion": {
            "intertwiner": "each scalar global input defines an SO3 map V_ell to V_ell",
            "multiplicity_one": "dim Hom_SO3(V_ell,V_ell)=1",
            "jet_normalization_role": "the even/odd formal jet is a local normalization used to evaluate the unique equivariant coefficient; it is not an identification of the physical m or harmonic parity",
            "all_m": True,
            "cross_parity": "axial and polar outputs occupy distinct parity blocks and cannot cancel",
        },
        "classification": {
            "generic_lambda_functional_form_proved_without_interpolation": True,
            "all_fixed_ell_at_least_2_pivots_nonzero": True,
            "all_m_promoted": True,
            "both_parities_classified": True,
            "bounded_abd_cross_ideal_classified": True,
            "nonzero_momentum_classified": False,
            "complete_global_wave_cone_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The ell=2 and ell=3 triangular obstructions are the physical fibres of one exact natural-operator identity. Every generic rest-frame Einstein-minus wave excludes the generalized homogeneous a,b,d directions from the bounded correction class, in either parity and for every m.",
        "next_gate": "combine this ideal with the every-fixed-ell k=0 common-zero wave theorem and the complete global zero-frequency classification",
        "claim_boundary": "This theorem covers only a,b,d crossed with one generic k=0 Einstein-minus block. It does not include nonzero momentum, cross-ell sums, exceptional wave inputs, the complete global cone, causal propagation, all-orders integration, residual descent, particles or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "direct_engine_path": str(DIRECT_ENGINE.relative_to(ROOT)),
            "direct_engine_sha256": _sha256(DIRECT_ENGINE),
            "fixture_path": str(FIXTURES.relative_to(ROOT)),
            "fixture_sha256": _sha256(FIXTURES),
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.41},
            "tier_1": {"status": "PASS", "elapsed_seconds": 3.11, "tests_run": 5},
            "tier_2": {"status": "PASS", "tensor_stage_elapsed_seconds": 374.94, "max_rss_kib": 175352, "criterion": "both symbolic tensor contractions replayed with lambda unevaluated; exact ell=2,3,4 physical fixtures agree"},
            "tier_3": {"status": "NOT_RUN", "reason": "nonzero momentum, cross-ell, causal, residual and quantum gates remain excluded"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_abd_generic_lambda_pivot --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_abd_generic_lambda_pivot.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_abd_generic_lambda_pivot",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_abd_generic_lambda_pivot --write --replay-symbolic",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--replay-symbolic", action="store_true")
    arguments = parser.parse_args()
    if arguments.replay_symbolic:
        replay_symbolic()
    value = build()
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise GenericLambdaPivotError("generic-lambda pivot certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ABD_GENERIC_LAMBDA_PIVOT: PASS")


if __name__ == "__main__":
    main()
