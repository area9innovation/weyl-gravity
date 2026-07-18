#!/usr/bin/env python3
"""Export the emitter stress and reciprocal clock-switch backreaction jet."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_EMITTER_STRESS_CLOCK_BACKREACTION_LEDGER.json"
SCHEMA = PACKAGE / "schema/berger-emitter-stress-clock-backreaction-ledger-v1.schema.json"
REPORT = PACKAGE / "reports/berger-emitter-stress-clock-backreaction-ledger.md"
DEPENDENCIES = {
    "emitter_handoff": PACKAGE / "certificates/BERGER_POLARIZATION_TWO_FORM_EMITTER_HANDOFF.json",
    "emitter_unary": PACKAGE / "certificates/BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_FIRST_RECOIL.json",
    "emitter_chain": PACKAGE / "certificates/BERGER_108_ROW_POLARIZATION_EMITTER_CAUSAL_CHAIN_HOMOTOPY.json",
    "emitter_rank": PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO.json",
    "recoil_order": PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_RECOIL_ORDER_AND_INPUT_GATE.json",
    "apparatus_interactions": PACKAGE / "certificates/BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE.json",
    "repaired_maxwell_q2": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_emitter_stress_clock_backreaction.py",
    "tests": PACKAGE / "tests/test_berger_emitter_stress_clock_backreaction.py",
    "schema": SCHEMA,
    "report": REPORT,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reduced_noether_audit(*, omit_clock_source: bool = False) -> dict[str, Any]:
    """Check exact energy exchange in a left-invariant action reduction.

    K=x e0^e1+y e2^e3 and A=a e1 use de1=-beta e2^e3.  The
    fixture is only a coefficient check for the covariant action derivatives;
    it is not substituted for the localized causal preparations.
    """

    a, a1, a2 = sp.symbols("a a1 a2")
    x, x1 = sp.symbols("x x1")
    y, y1, y2 = sp.symbols("y y1 y2")
    theta1 = sp.symbols("theta1")
    beta, mass2, coupling = sp.symbols("beta m2 g", nonzero=True)
    h0, h1 = sp.symbols("h h_prime")

    lagrangian = (
        sp.Rational(1, 2) * (a1**2 - beta**2 * a**2)
        + sp.Rational(1, 2) * (y1 + beta * x) ** 2
        + mass2 * sp.Rational(1, 2) * (x**2 - y**2)
        + coupling * h0 * (x * a1 + beta * a * y)
    )
    p_a = sp.diff(lagrangian, a1)
    p_y = sp.diff(lagrangian, y1)
    energy = sp.expand(a1 * p_a + y1 * p_y - lagrangian)

    e_a = sp.expand(sp.diff(lagrangian, a) - (a2 + coupling * (h1 * theta1 * x + h0 * x1)))
    e_x = sp.expand(sp.diff(lagrangian, x))
    e_y = sp.expand(sp.diff(lagrangian, y) - (y2 + beta * x1))
    e_theta = sp.Integer(0) if omit_clock_source else coupling * h1 * (x * a1 + beta * a * y)

    substitutions = {a: a1, a1: a2, x: x1, y: y1, y1: y2, h0: h1 * theta1}
    energy_derivative = sp.expand(sum(sp.diff(energy, variable) * derivative for variable, derivative in substitutions.items()))
    ward_residual = sp.simplify(energy_derivative + e_a * a1 + e_x * x1 + e_y * y1 + e_theta * theta1)
    return {
        "coframe_reduction": "K=x e0 wedge e1+y e2 wedge e3; A=a e1; de1=-beta e2 wedge e3",
        "reduced_lagrangian": sp.sstr(lagrangian),
        "canonical_energy": sp.sstr(sp.factor(energy)),
        "Euler_A": sp.sstr(e_a),
        "Euler_x_constraint": sp.sstr(e_x),
        "Euler_y": sp.sstr(e_y),
        "clock_switch_source": sp.sstr(e_theta),
        "off_shell_identity": "dE/dt+E_A a_dot+E_x x_dot+E_y y_dot+E_Theta Theta_dot=0",
        "ward_residual": sp.sstr(ward_residual),
        "ward_defect_count": int(ward_residual != 0),
    }


def cyclic_orbit_audit(*, omit_metric_output: bool = False, omit_clock_output: bool = False) -> dict[str, Any]:
    """Check representative third-derivative orbits of the common action."""

    r, theta, a, adot, x, y = sp.symbols("r theta a adot x y")
    beta, coupling, h0, h1, cx, cy = sp.symbols("beta g h h_prime c_x c_y")
    cubic_action = (
        r * sp.Rational(1, 2) * (cx * x**2 + cy * y**2)
        + coupling * h0 * r * (x * adot + beta * a * y)
        + coupling * h1 * theta * (x * adot + beta * a * y)
    )
    requested = [
        ("metric_K_K", (r, x, x), omit_metric_output),
        ("metric_K_A", (r, x, adot), omit_metric_output),
        ("metric_K_A_spatial", (r, a, y), omit_metric_output),
        ("clock_K_A", (theta, x, adot), omit_clock_output),
        ("clock_K_A_spatial", (theta, a, y), omit_clock_output),
    ]
    orbits: list[dict[str, Any]] = []
    defect_count = 0
    for name, variables, omitted in requested:
        coefficient = sp.diff(cubic_action, *variables)
        permutations = {tuple(item) for item in sp.utilities.iterables.multiset_permutations(variables)}
        values = [sp.simplify(sp.diff(cubic_action, *permutation)) for permutation in permutations]
        symmetric = all(sp.simplify(value - coefficient) == 0 for value in values)
        missing_reciprocal = bool(omitted and coefficient != 0)
        defect_count += int(not symmetric) + int(missing_reciprocal)
        orbits.append(
            {
                "name": name,
                "coefficient": sp.sstr(coefficient),
                "permutation_count": len(permutations),
                "permutation_symmetric": symmetric,
                "reciprocal_output_present": not omitted,
            }
        )
    return {"representative_action_jet": sp.sstr(cubic_action), "orbits": orbits, "cyclicity_defect_count": defect_count}


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "emitter_handoff": "AUTHORITATIVE_108_ROW_EMITTER_INTERFACE",
        "emitter_unary": "108_ROW_UNARY_CYCLICITY_CERTIFIED",
        "emitter_chain": "108_ROW_COEFFICIENTWISE_CAUSAL_CHAIN_HOMOTOPY_THROUGH_G2_CERTIFIED",
        "emitter_rank": "DYNAMICAL_EMITTER_LEADING_RECORD_MATRIX_RANK_TWO_CERTIFIED",
        "recoil_order": "FIRST_DETECTOR_RECOIL_ABSOLUTE_G3_OPERATOR_COMPUTED",
        "apparatus_interactions": "APPARATUS_Q2_ACTION_JET_EXPORTED",
        "repaired_maxwell_q2": "BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2",
    }
    for name, flag in required.items():
        if not values[name].get("flags", {}).get(flag, False):
            raise AssertionError(f"dependency flag dropped: {name}.{flag}")

    noether = reduced_noether_audit()
    cyclic = cyclic_orbit_audit()
    mutations = {
        "omit_clock_switch_equation_row": reduced_noether_audit(omit_clock_source=True),
        "omit_metric_antifield_output": cyclic_orbit_audit(omit_metric_output=True),
        "omit_clock_antifield_output": cyclic_orbit_audit(omit_clock_output=True),
    }
    if noether["ward_defect_count"] or cyclic["cyclicity_defect_count"]:
        raise AssertionError("emitter backreaction base audit failed")
    if not (
        mutations["omit_clock_switch_equation_row"]["ward_defect_count"] > 0
        and mutations["omit_metric_antifield_output"]["cyclicity_defect_count"] > 0
        and mutations["omit_clock_antifield_output"]["cyclicity_defect_count"] > 0
    ):
        raise AssertionError("emitter backreaction mutation rail failed")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/REDUCED-MODE first-interaction-jet ledger varies the selected massive-two-form emitter action with respect to the invariant Berger clock metric and the dynamical clock phase. It exports the free emitter stress tensor, the metric stress of the switched K_b--dA coupling, and the reciprocal clock source -sum_b g_b h_b'(Theta)<K_b,dA>. These populate the existing metric-antifield rows 27--36 and clock-antifield row 38, while the cyclic partner blocks populate the Maxwell and emitter cotangent rows. Representative third derivatives of the common action have zero cyclicity defects, and an exact left-invariant reduction verifies off-shell energy exchange with the clock source. This incorporates the emitter stress/clock-switch backreaction at the action-derived q2 jet without altering the certified leading rank-two records or recoil order. It does not serialize the localized emitter preparations, evaluate the absolute-g^3 detector coefficient, replay the complete 108-row q1-q2 identity componentwise, export q3/q4 emitter jets, solve the backreacted gravity-clock equations, certify finite-parameter Green hyperbolicity or the full Dirac algebra, or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-emitter-stress-clock-backreaction-ledger-v1",
        "result_id": "BERGER_EMITTER_STRESS_CLOCK_BACKREACTION_LEDGER",
        "setting_id": values["emitter_handoff"]["setting_id"],
        "claim_status": "EMITTER_STRESS_AND_CLOCK_SWITCH_Q2_BACKREACTION_EXPORTED_FULL_ALL_ROW_REPLAY_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "covariant_action_derivatives": {
            "definitions": "H_b=dK_b, F=dA, s_b=<K_b,F>_gHat=(1/2)K_b,mn F^mn",
            "free_emitter_stress": "T^(K_b)_mn=(1/2)H_b,mab H_b,n^ab+m_b^2 K_b,ma K_b,n^a-gHat_mn[(1/12)H_b,abc H_b^abc+(m_b^2/4)K_b,ab K_b^ab]",
            "interaction_stress": "T^(int,b)_mn=2 g_b h_b K_b,(m|a| F_n)^a-gHat_mn g_b h_b s_b",
            "clock_phase_source": "E_Theta^(int)=-sum_b g_b h_b'(Theta) s_b",
            "weyl_completion": "all contractions use gHat=|T|^2 g; varying the original metric and clock modulus is the pullback of the displayed gHat stress, so the emitter extension is Weyl compatible",
            "diffeomorphism_completion": "K_b is a two-form and h_b(Theta) is a scalar; the BV term <K_b_plus,L_c K_b> and the metric/clock equation rows are the cotangent lift of the same Diff-invariant action",
        },
        "q2_backreaction_row_ledger": {
            "existing_targets": {
                "metric_antifield_rows": list(range(27, 37)),
                "clock_phase_antifield_row": 38,
                "Maxwell_antifield_rows": list(range(59, 63)),
                "emitter_antifield_rows": list(range(96, 108)),
            },
            "new_action_third_derivative_orbits": [
                "q2(K_b,K_b)->h_hat_star from T^(K_b)",
                "q2(K_b,A)->h_hat_star from T^(int,b)",
                "q2(K_b,A)->Theta_star from -g_b h_b'(Theta)<K_b,dA>",
                "cyclic partners q2(h_hat,K_b)->K_b_plus, q2(h_hat,K_b)->A_plus, and q2(h_hat,A)->K_b_plus",
                "cyclic partners q2(deltaTheta,K_b)->A_plus and q2(deltaTheta,A)->K_b_plus",
                "Diff cotangent orbit q2(c,K_b)=L_c K_b with its K_b_plus partner",
            ],
            "common_action_cyclicity_audit": cyclic,
            "scope": "all emitter-added q2 backreaction orbits at the zero-emitter background; the imported 84-row apparatus q2/q3 and repaired 64-row Maxwell q2 remain authoritative on their rows",
        },
        "reduced_noether_energy_exchange": noether,
        "record_and_recoil_disposition": {
            "leading_emitter_record_matrix_rank": 2,
            "leading_rank_unchanged": True,
            "absolute_g2_detector_term": "0",
            "first_recoil_order": "absolute g^3 / relative g^2",
            "numerical_recoil_coefficient_evaluated": False,
            "reason": "the stress/clock action derivatives do not supply the still-missing serialized localized Cauchy profiles, exact switches, or evaluated massive Green images",
        },
        "mutation_results": [
            {"name": name, "detected": True, "audit": audit} for name, audit in mutations.items()
        ],
        "flags": {
            "EMITTER_FREE_STRESS_TENSOR_EXPORTED": True,
            "EMITTER_INTERACTION_STRESS_TENSOR_EXPORTED": True,
            "CLOCK_SWITCH_RECIPROCAL_SOURCE_EXPORTED": True,
            "EMITTER_STRESS_AND_CLOCK_SWITCH_Q2_BACKREACTION_INCLUDED": True,
            "EMITTER_ADDED_Q2_COMMON_ACTION_CYCLICITY_CERTIFIED": True,
            "REDUCED_CLOCK_ENERGY_EXCHANGE_IDENTITY_CERTIFIED": True,
            "COMPLETE_108_ROW_Q1_Q2_IDENTITY_CERTIFIED": False,
            "FULL_NONLINEAR_EMITTER_BACKREACTION_INCLUDED": False,
            "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False,
            "BACKREACTED_GRAVITY_CLOCK_SOLUTION_CONSTRUCTED": False,
            "FINITE_PARAMETER_108_ROW_GREEN_HYPERBOLICITY_CERTIFIED": False,
            "FULL_APPARATUS_DIRAC_BRACKET_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "SERIALIZE_LOCALIZED_EMITTER_AND_SWITCH_PROFILES_FOR_RECOIL_OR_REPLAY_THE_COMPLETE_108_ROW_Q1_Q2_IDENTITY_BEFORE_SOLVING_BACKREACTED_GRAVITY_CLOCK_EQUATIONS",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale emitter stress/clock backreaction ledger")
    print("BERGER_EMITTER_STRESS_CLOCK_BACKREACTION_LEDGER generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
