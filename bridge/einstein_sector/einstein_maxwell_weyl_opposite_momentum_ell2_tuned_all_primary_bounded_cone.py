"""Classify the tuned axisymmetric q/p-primary bounded cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_tuned_all_primary_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_opposite_momentum_ell2_tuned_all_primary_bounded_cone.schema.json"
INPUTS = {
    "q_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_tuned_axisymmetric_bounded_cone.json",
    "bounded_extension": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_mixed_parity_bounded_extension.json",
    "opposite_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_cone.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _nonzero_witness(value: sp.Expr, variable: sp.Symbol) -> dict[str, str]:
    polynomial = sp.Poly(sp.minpoly(value, variable), variable)
    constant = sp.factor(polynomial.nth(0))
    _require(constant != 0, f"nonzero witness collapsed for {value}")
    return {"residual": str(sp.factor(value)), "minimal_polynomial_constant": str(constant)}


def _collision_census() -> dict[str, Any]:
    root = sp.sqrt(3)
    k_squared = 2 * root - sp.Rational(7, 6)
    squares = {
        "minus": sp.Rational(29, 6),
        "extra": 2 * root + sp.Rational(25, 6),
        "plus": sp.Rational(29, 6) + 4 * root,
    }
    frequencies = {name: sp.sqrt(value) for name, value in squares.items()}
    output_squares: dict[str, sp.Expr] = {"zero": sp.Integer(0)}
    order = ["minus", "extra", "plus"]
    for left_index, left in enumerate(order):
        for right in order[left_index:]:
            if left == right:
                output_squares[f"two_{left}"] = 4 * squares[left]
            else:
                output_squares[f"{left}_plus_{right}"] = sp.expand((frequencies[left] + frequencies[right]) ** 2)
                output_squares[f"{right}_minus_{left}"] = sp.expand((frequencies[right] - frequencies[left]) ** 2)

    x = sp.Symbol("x")
    checks: list[dict[str, Any]] = []
    collisions: list[dict[str, str]] = []
    for momentum_name, momentum_squared in {"K_zero": sp.Integer(0), "K_two_k": 4 * k_squared}.items():
        for frequency_name, frequency_squared in output_squares.items():
            for ell in range(1, 5):
                if ell == 1:
                    targets = {
                        "exceptional": (frequency_squared - momentum_squared - 4)
                        * (frequency_squared - momentum_squared - sp.Rational(4, 3))
                    }
                else:
                    eigenvalue = ell * (ell + 1)
                    targets = {
                        "p": frequency_squared - momentum_squared - eigenvalue + sp.Rational(2, 3),
                        "q": (frequency_squared - momentum_squared - eigenvalue) ** 2 - 2 * eigenvalue,
                    }
                for target, residual in targets.items():
                    residual = sp.expand(residual)
                    collision = residual.equals(0) is True
                    row: dict[str, Any] = {
                        "frequency": frequency_name,
                        "momentum": momentum_name,
                        "ell": ell,
                        "target": target,
                        "collision": collision,
                    }
                    if collision:
                        row["residual"] = "0"
                        collisions.append({key: str(row[key]) for key in ("frequency", "momentum", "ell", "target")})
                    else:
                        row["nonzero_witness"] = _nonzero_witness(residual, x)
                    checks.append(row)
    expected = [{"frequency": "two_minus", "momentum": "K_zero", "ell": "4", "target": "p"}]
    _require(collisions == expected, f"all-primary collision set changed: {collisions}")
    _require(len(checks) == 140, "collision census size changed")
    return {
        "input_frequency_squares": {name: str(value) for name, value in squares.items()},
        "output_frequency_squares": {name: str(sp.factor(value)) for name, value in output_squares.items()},
        "overcomplete_scope": "L=1,2,3,4; K=0 or +/-2k; every zero, sum and difference frequency of q-minus, p-extra and q-plus",
        "checks": checks,
        "check_count": len(checks),
        "collisions": collisions,
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["q_cone"]["classification"]["bounded_necessity_and_sufficiency_certified"], "q-primary cone changed")
    _require(records["bounded_extension"]["classification"]["complete_exact_collision_census_for_declared_tangent"], "bounded block theorem changed")
    _require(records["opposite_cone"]["classification"]["complete_fixed_ell_absolute_k_common_zero_cone_classified"], "full primary moment cone changed")
    census = _collision_census()

    root = sp.sqrt(3)
    minus_squared = sp.Rational(29, 6)
    extra_squared = 2 * root + sp.Rational(25, 6)
    plus_squared = sp.Rational(29, 6) + 4 * root
    r_extra = sp.sqrt(minus_squared / extra_squared)
    r_plus = sp.sqrt(minus_squared / plus_squared)
    _require(0 < float(r_plus.evalf()) < float(r_extra.evalf()) < 1, "branch ordering changed")
    lower = sp.factor((1 - r_extra) / (1 + r_extra))
    upper = sp.factor((1 + r_extra) / (1 - r_extra))
    _require(sp.simplify(lower * upper - 1) == 0, "all-primary interval reciprocity changed")

    return {
        "schema": "einstein-maxwell-weyl-opposite-momentum-ell2-tuned-all-primary-bounded-cone-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_OPPOSITE_MOMENTUM_ELL2_TUNED_ALL_PRIMARY_BOUNDED_CONE",
        "result_state": "COMPLETE_TUNED_AXISYMMETRIC_QPLUS_QMINUS_PEXTRA_TWIST_BOUNDED_CONE_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_COMPLETE_ONE_TUNED_ELL2_AXISYMMETRIC_ALL_PRIMARY_TWIST_CARRIER",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 with k^2=2*sqrt(3)-7/6 allowed",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "one constant twist position plus arbitrary m_A=0 q-minus axial/polar amplitudes and arbitrary normalized q-plus and p-extra multiplicities at +/-k",
            "degree": 2,
            "parity": "all certified q-minus, q-plus and p-extra multiplicities at m_A=0",
            "ell": "input ell=2; every quadratic output L=0,...,4",
            "m": "m_A=0",
            "k": "+/-sqrt(2*sqrt(3)-7/6)",
            "omega": "q-minus, p-extra and q-plus shells with bounded or finite-quasiperiodic corrections",
        },
        "collision_census": census,
        "resonance_zero_set": records["q_cone"]["resonance_zero_set"],
        "moment_polytope": {
            "negative_occupations": "N_sigma=-h_minus(a_sigma e_A+p_sigma e_P,a_sigma e_A+p_sigma e_P)>=0",
            "positive_occupations": "E_sigma>=0 on the complete p-extra multiplicity and B_sigma>=0 on the complete q-plus multiplicity",
            "equations": [
                "omega_e^2*(E_++E_-)+omega_+^2*(B_++B_-)=omega_-^2*(N_++N_-)",
                "omega_e*(E_+-E_-)+omega_+*(B_+-B_-)=omega_-*(N_+-N_-)",
            ],
            "complete_feasibility_condition": "abs(N_+-N_-)<=r_e*(N_++N_-), r_e=omega_-/omega_e",
            "necessity_proof": "at fixed positive-branch energy the compact-momentum capacity is maximal on the lower-frequency p-extra branch, giving capacity r_e*(N_++N_-)",
            "sufficiency_witness": [
                "B_+=B_-=0",
                "E_+ + E_- = r_e^2*(N_+ + N_-)",
                "E_+ - E_- = r_e*(N_+ - N_-)",
            ],
            "general_solution": "all nonnegative (E_+,E_-,B_+,B_-) satisfying the two displayed affine equations; phases and multiplicity factorizations are arbitrary",
            "strict_ratio_order": "0<r_+=omega_-/omega_+<r_e=omega_-/omega_e<1",
        },
        "nonzero_bounded_components": {
            "signs": ["sigma=+1", "sigma=-1"],
            "amplitudes": "a_+=sigma*sqrt(3)*p_+ and a_-=sigma*sqrt(3)*p_-",
            "complete_imbalance_interval": {
                "variable": "t=|p_+|^2/|p_-|^2",
                "lower": str(lower),
                "upper": str(upper),
                "condition": "(1-r_e)/(1+r_e)<=t<=(1+r_e)/(1-r_e)",
                "strictly_contains_qplus_only_interval": True,
            },
            "positive_branch_freedom": "for every point in the interval, the complete balancing set is the moment polytope above; the p-extra-only formula is one explicit factorization",
        },
        "necessity_and_sufficiency": {
            "necessity": "the unique bounded shell collision is still the q-minus L4 p output, so its two rows force the same four-component resonance variety; positivity removes the one-sided planes and gives the widened interval",
            "sufficiency": "choose any positive-branch occupation in the displayed moment polytope; all five moment maps and the unique resonance vanish, while the other 139 shell residuals have bounded inverses",
            "equation": "L_WM Phi^(2)=-(1/2)D^2E_WM[Phi^(1),Phi^(1)]",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED", "cone": "the origin plus two mixed q-minus components with the r_e imbalance interval and complete positive-branch moment polytope"},
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {"status": "CERTIFIED", "reason": "the bounded cone is contained in the complete fixed-fibre smooth-secular moment cone"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "complete_tuned_axisymmetric_all_primary_collision_census_certified": True,
            "extra_primary_inputs_create_no_new_shell_collision": True,
            "complete_tuned_axisymmetric_all_primary_bounded_cone_classified": True,
            "bounded_necessity_and_sufficiency_certified": True,
            "two_nonzero_mixed_qminus_components_survive": True,
            "positive_branch_moment_polytope_complete": True,
            "other_ell_or_momentum_fibres_classified": False,
            "nonaxisymmetric_inputs_included": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The extra Weyl primary does not open another bounded resonance at the tuned fibre. It acts as the most efficient positive-energy compact-momentum balancer because its frequency lies below the Einstein-plus frequency. The nonlinear cone retains the same two mixed q-minus sheets but with a strictly wider opposite-momentum amplitude interval and a convex positive-branch occupation fibre.",
        "next_gate": "derive the symbolic-ell resonance coefficient and collision theorem, then join multiple absolute-momentum fibres without identifying their phase carriers",
        "claim_boundary": "This is complete only for the tuned ell=2 axisymmetric all-primary/constant-twist carrier. Nonaxisymmetric modes, other ell and circumferences, multiple |k| fibres, exceptional inputs beyond the twist, all-orders integration, causal propagation, particles and quantum theory remain open.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_1": {"status": "PENDING", "tests_run": 0},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "direct source coefficients and bounded inverses are unchanged inputs; this producer adds the exact all-primary collision and positivity census"},
            "tier_3": {"status": "NOT_RUN", "reason": "other fibres and higher lifecycles remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_opposite_momentum_ell2_tuned_all_primary_bounded_cone --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_opposite_momentum_ell2_tuned_all_primary_bounded_cone.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_opposite_momentum_ell2_tuned_all_primary_bounded_cone",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if arguments.write:
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != payload:
        raise AssertionError("tuned all-primary bounded-cone certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_OPPOSITE_MOMENTUM_ELL2_TUNED_ALL_PRIMARY_BOUNDED_CONE: PASS")


if __name__ == "__main__":
    main()
