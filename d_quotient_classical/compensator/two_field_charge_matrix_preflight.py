#!/usr/bin/env python3
"""Exact two-compensator charge-lattice and health preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "COMPENSATOR_TWO_FIELD_CHARGE_MATRIX_PREFLIGHT_V1.json"
)
IMPORTS = {
    "one_field_preflight": {
        "path": (
            ROOT
            / "d_quotient_classical/compensator/"
            "COMPENSATOR_COMPLEX_SCALE_U1_CONNECTION_PREFLIGHT_V1.json"
        ),
        "sha256": "3b7b1f86392f0d5daeec4b1adac99a0e16e472ff37b44253908a20c53aad1404",
        "source_commit": "6cc041fadaaf6259142aa8f30a2f75879cf92dd3",
        "result_id": "COMPENSATOR_COMPLEX_SCALE_U1_CONNECTION_PREFLIGHT_V1",
        "result_state": "SCOPED_SEPARATED_SCALE_U1_MINIMAL_GOOD_LOCUS_EMPTY",
    },
    "conditional_full_gate": {
        "path": (
            ROOT
            / "d_quotient_classical/compensator/"
            "COMPENSATOR_COMPLEX_SCALE_U1_FULL_BV_CAUSAL_GATE_V1.json"
        ),
        "sha256": "66c09d849caa5ced489c0e9324a51f49d58e267f4bdffc5747eba025740d90ef",
        "source_commit": "edbb6cb724f7e6922c7567eaec358cfef86ff8af",
        "result_id": "COMPENSATOR_COMPLEX_SCALE_U1_FULL_BV_CAUSAL_GATE_V1",
        "result_state": "NOT_ACTIVATED_EMPTY_PREDECESSOR_LOCUS",
    },
    "positive_Berger_clock": {
        "path": (
            ROOT
            / "d_quotient_classical/certificates/"
            "POSITIVE_BERGER_CLOCK_BACKGROUND.json"
        ),
        "sha256": "35e1bb8a56b0591b3dd00aa8f22c328ad826ecd341c290564cfd1a68fcc3e687",
        "source_commit": "bb5738d6e3e30a68adcc9a70c35dac089079e3db",
        "result_id": "POSITIVE_BERGER_CLOCK_BACKGROUND",
        "claim_status": "CERTIFIED_EXACT_BACKGROUND",
    },
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _q(value: sp.Expr) -> str:
    return str(sp.factor(value))


def _matrix(value: sp.Matrix) -> dict[str, Any]:
    core = {
        "row_count": value.rows,
        "column_count": value.cols,
        "entries": [
            {"row": i, "column": j, "coefficient": _q(value[i, j])}
            for i in range(value.rows)
            for j in range(value.cols)
            if value[i, j] != 0
        ],
    }
    return {**core, "sha256": _digest(core)}


def _load_imports() -> dict[str, Any]:
    records: dict[str, Any] = {}
    payloads: dict[str, dict[str, Any]] = {}
    for key, spec in IMPORTS.items():
        actual = _sha(spec["path"])
        payload = json.loads(spec["path"].read_text())
        if actual != spec["sha256"] or payload["result_id"] != spec["result_id"]:
            raise AssertionError(f"{key} import drifted")
        for state_key in ("result_state", "claim_status"):
            if state_key in spec and payload.get(state_key) != spec[state_key]:
                raise AssertionError(f"{key} {state_key} drifted")
        records[key] = {
            "path": str(spec["path"].relative_to(ROOT)),
            "sha256": actual,
            "source_commit": spec["source_commit"],
            "result_id": spec["result_id"],
            **{
                k: spec[k]
                for k in ("result_state", "claim_status")
                if k in spec
            },
        }
        payloads[key] = payload
    if (
        payloads["one_field_preflight"]["terminal_verdict"]["healthy_locus"]
        != "EMPTY"
        or payloads["conditional_full_gate"]["activation_condition_satisfied"]
    ):
        raise AssertionError("two-field activation semantics drifted")
    return records


def _snf_diagonal(matrix: sp.Matrix) -> list[int]:
    diagonal = smith_normal_form(matrix, domain=ZZ)
    return [
        abs(int(diagonal[i, i]))
        for i in range(min(diagonal.rows, diagonal.cols))
        if diagonal[i, i] != 0
    ]


def _charge_lattice() -> dict[str, Any]:
    cases = {
        "rank_zero": sp.zeros(2, 0),
        "rank_one_primitive": sp.Matrix([[1], [0]]),
        "rank_one_nonprimitive_fixture": sp.Matrix([[2], [0]]),
        "rank_two_unimodular": sp.eye(2),
        "rank_two_finite_kernel_fixture": sp.diag(2, 4),
    }
    expected = {
        "rank_zero": [],
        "rank_one_primitive": [1],
        "rank_one_nonprimitive_fixture": [2],
        "rank_two_unimodular": [1, 1],
        "rank_two_finite_kernel_fixture": [2, 4],
    }
    computed = {name: _snf_diagonal(value) for name, value in cases.items()}
    if computed != expected:
        raise AssertionError("Smith classification fixtures drifted")
    return {
        "representation_cases": {
            "two_complex": (
                "phase lattice Z^2; primitive compact rank one leaves one "
                "continuous relative phase and is the only potentially viable "
                "minimal case"
            ),
            "real_plus_complex": (
                "phase lattice Z; compact rank one gauges its only phase, "
                "while rank zero is the unchanged global-phase theory; hence "
                "no compact-gauged relational phase survives"
            ),
            "real_plus_complex_scale_result": (
                "the two radial kinetic matrix obeys the same diagonal Ward/"
                "positivity lemma, so the extra real modulus does not create "
                "an independent healthy dressed-trace scale column"
            ),
        },
        "equivalence": (
            "Q~UQV with U in GL(2,Z) acting on phase-torus coordinates and "
            "V in GL(r,Z) acting on compact gauge generators, together with "
            "field permutation and sign reversal"
        ),
        "general_invariants": {
            "rank_one": (
                "SNF diag(d,0), d=gcd(all charges); faithful iff d=1"
            ),
            "rank_two_2x2": (
                "SNF diag(d1,d2), d1=gcd(entries), d1*d2=abs(det Q), "
                "d1 divides d2; faithful iff d1=d2=1"
            ),
        },
        "canonical_cases": [
            {
                "case": "rank_zero",
                "representative": "2x0 zero matrix",
                "snf": computed["rank_zero"],
                "faithful": False,
                "physical_phase_dimension": 2,
                "disposition": "NO_COMPACT_GAUGE_CHANGE",
            },
            {
                "case": "rank_one_primitive",
                "representative": "[[1],[0]]",
                "snf": computed["rank_one_primitive"],
                "faithful": True,
                "physical_phase_dimension": 1,
                "disposition": "ONLY_MINIMAL_CASE_WITH_A_RELATIVE_PHASE_CLOCK",
            },
            {
                "case": "rank_one_nonprimitive",
                "representative": "[[d],[0]], d>1",
                "snf_fixture_d=2": computed["rank_one_nonprimitive_fixture"],
                "faithful": False,
                "finite_kernel": "Z/d",
                "physical_phase_dimension": 1,
                "disposition": "NOT_MINIMAL_FAITHFUL",
            },
            {
                "case": "rank_two_unimodular",
                "representative": "I_2",
                "snf": computed["rank_two_unimodular"],
                "faithful": True,
                "physical_phase_dimension": 0,
                "disposition": "NO_RELATIONAL_PHASE",
            },
            {
                "case": "rank_two_nonunimodular",
                "representative": "diag(d1,d2)",
                "snf_fixture_(2,4)": computed[
                    "rank_two_finite_kernel_fixture"
                ],
                "faithful": False,
                "physical_phase_dimension": 0,
                "disposition": "FINITE_KERNEL_AND_NO_RELATIONAL_PHASE",
            },
        ],
        "selected_preflight_case": {
            "representation": "two_complex",
            "Q": [["1"], ["0"]],
            "charged_phase": "theta_1",
            "relative_physical_phase": "psi=theta_2",
            "gauge_phase": "theta_1",
            "reason": (
                "It is the unique minimal faithful compact rank that leaves "
                "one continuous phase after quotient."
            ),
        },
        "independent_rails": [
            "SymPy exact ZZ smith_normal_form in the producer and verifier",
            "Forge GMP-backed math/snf fixture in two_field_charge_matrix_snf_check.forge",
        ],
    }


def _action_and_ward() -> tuple[dict[str, Any], dict[str, Any]]:
    action = {
        "fields": [
            "g_ab",
            "Phi_i=rho_i exp(i theta_i), i=1,2, rho_i>0",
            "one real Weyl-scale connection W_a",
            "r compact U(1) connections A_a^alpha, r=0,1,2",
        ],
        "gauge_data": {
            "metric_scale_weights_(omega,eta)": ["1", "a"],
            "radial_weights_field_1": ["-1", "-b1"],
            "radial_weights_field_2": ["-1", "-b2"],
            "integer_compact_charge_matrix": "Q in Mat_(2xr)(Z)",
            "candidate_phase_shift_vector": "s in R^2",
        },
        "minimal_density": (
            "sqrt(-g){alpha_C C^2/8+alpha_R R_W^2"
            "-1/2 K^r_ij D rho_i.D rho_j"
            "-1/12 K^R_ij rho_i rho_j R_W"
            "-1/2 K^theta_ij rho_i rho_j B_i.B_j"
            "-V4(rho_1,rho_2)"
            "-1/4 Z_alpha_beta H^alpha.H^beta"
            "-1/2 chi_alpha F_W.H^alpha-zeta_W F_W^2/4}"
        ),
        "covariant_phase_one_forms": (
            "B_i=d theta_i+Q_(i alpha) A^alpha; for the selected primitive "
            "case B_1=dtheta_1+A and B_2=dtheta_2"
        ),
        "potential": (
            "V4=lambda40 rho1^4/4+lambda22 rho1^2 rho2^2/2"
            "+lambda04 rho2^4/4"
        ),
        "completeness": (
            "This is the complete declared formal-polar parity-even "
            "two-derivative scalar bilinear and regular U(1)-invariant "
            "quartic potential, plus the Abelian curvature kinetic matrix. "
            "Higher derivatives and fitted nonpolynomial potentials are absent."
        ),
    }

    a, b1, b2 = sp.symbols("a b1 b2", real=True)
    weights = sp.Matrix(
        [
            [2 * (a - b1), 2 * a - b1 - b2],
            [2 * a - b1 - b2, 2 * (a - b2)],
        ]
    )
    if weights[0, 1] != weights[1, 0]:
        raise AssertionError("bilinear Ward matrix drifted")
    ward = {
        "bilinear_weight_matrix": _matrix(weights),
        "bilinear_Ward_equations": [
            "(a-b1) K_11=0",
            "(2a-b1-b2) K_12=0",
            "(a-b2) K_22=0",
        ],
        "applies_to": ["K^r", "K^R", "K^theta"],
        "quartic_weight_rule": (
            "(4a-b_i-b_j-b_k-b_l) lambda_ijkl=0"
        ),
        "constant_parameter_exhaustiveness": (
            "A constant eta already imposes these weights; derivatives and "
            "integration by parts cannot cancel them."
        ),
    }
    return action, ward


def _positivity_and_gauge_rank() -> dict[str, Any]:
    a, b1, b2, s1, s2 = sp.symbols("a b1 b2 s1 s2", real=True)
    # Canonical primitive compact charge Q=(1,0)^T.
    # Rows: log g,rho1,rho2,theta1,theta2,W_L,A_L.
    # Columns: omega,eta,gamma.
    gauge = sp.Matrix(
        [
            [1, a, 0],
            [-1, -b1, 0],
            [-1, -b2, 0],
            [0, s1, 1],
            [0, s2, 0],
            [-1, -a, 0],
            [0, -s1, -1],
        ]
    )
    scale_minor_1 = sp.factor(gauge.extract([0, 1], [0, 1]).det())
    scale_minor_2 = sp.factor(gauge.extract([0, 2], [0, 1]).det())
    phase_minor = sp.factor(gauge.extract([0, 3, 4], [0, 1, 2]).det())
    if (
        scale_minor_1 != a - b1
        or scale_minor_2 != a - b2
        or phase_minor != -s2
    ):
        raise AssertionError("two-field gauge minors drifted")
    reducible = gauge.subs({b1: a, b2: a, s2: 0})
    relation = sp.Matrix([-a, 1, -s1])
    if reducible.rank() != 2 or reducible * relation != sp.zeros(7, 1):
        raise AssertionError("two-field reducibility drifted")

    k11, k12, k22 = sp.symbols("k11 k12 k22", real=True)
    kinetic = sp.Matrix([[k11, k12], [k12, k22]])
    determinant = sp.factor(kinetic.det())
    if determinant != k11 * k22 - k12**2:
        raise AssertionError("kinetic determinant drifted")

    return {
        "canonical_primitive_gauge_symbol": _matrix(gauge),
        "row_order": [
            "log g",
            "log rho1",
            "log rho2",
            "theta1",
            "theta2",
            "W_L",
            "A_L",
        ],
        "column_order": ["omega", "eta", "gamma"],
        "independence_minors": {
            "metric_rho1": "a-b1",
            "metric_rho2": "a-b2",
            "physical_relative_phase": "-s2",
        },
        "positive_kinetic_lemma": {
            "generic_matrix": _matrix(kinetic),
            "principal_conditions": [
                "k11>0",
                "k22>0",
                "k11*k22-k12^2>0",
            ],
            "Ward_consequence": (
                "positive diagonal entries and the two diagonal Ward rows "
                "force b1=a and b2=a"
            ),
            "semidefinite_boundary": (
                "if K_ii=0 in a positive-semidefinite matrix, "
                "det K>=0 forces K_12=0; every weight-mismatched field is a "
                "null row/column rather than a healthy active mode"
            ),
        },
        "complete_healthy_strata": {
            "some_b_i_not_a": (
                "candidate scale can be independent on radial/metric rows, "
                "but the corresponding scalar kinetic row is null; positive "
                "two-field inertia fails"
            ),
            "b1=b2=a_and_s2_nonzero": (
                "gauge rank is three only because eta shifts the surviving "
                "relative phase theta2; the relational clock is gauge"
            ),
            "b1=b2=a_and_s2_zero": {
                "rank": 2,
                "reducibility_vector_(omega,eta,gamma)": ["-a", "1", "-s1"],
                "identity": "G(-a,1,-s1)^T=0",
                "dressed_metrics": (
                    "g_hat_i=(rho_i/f_i)^2 g are eta invariant"
                ),
                "disposition": (
                    "relative clock survives, but no new dressed-trace gauge "
                    "direction exists"
                ),
            },
        },
        "first_incompatible_trichotomy": [
            "independent by scale weights => null/indefinite scalar kinetic",
            "independent by relative-phase shift => physical clock gauged",
            "healthy scalar kinetic plus physical clock => candidate reducible",
        ],
    }


def _stationarity_and_charges() -> dict[str, Any]:
    # Aggregate coefficient order:
    # alpha_B, alpha_R, K=f^T K^R f, C=beta^T Z(f) beta,
    # U=4 V4(f).
    cylinder_metric = sp.Matrix(
        [
            [0, 36, -sp.Rational(1, 2), -sp.Rational(1, 2), -sp.Rational(1, 4)],
            [0, 12, sp.Rational(1, 6), -sp.Rational(1, 2), sp.Rational(1, 4)],
        ]
    )
    berger_metric = sp.Matrix(
        [
            [
                sp.Rational(961, 9600),
                sp.Rational(22801, 6400),
                -sp.Rational(151, 960),
                -sp.Rational(1, 2),
                -sp.Rational(1, 4),
            ],
            [
                sp.Rational(403, 9600),
                sp.Rational(20083, 6400),
                sp.Rational(3, 320),
                -sp.Rational(1, 2),
                sp.Rational(1, 4),
            ],
            [
                sp.Rational(31, 1920),
                -sp.Rational(3473, 1280),
                sp.Rational(133, 960),
                -sp.Rational(1, 2),
                sp.Rational(1, 4),
            ],
        ]
    )
    positive = sp.Matrix(
        [5, 0, 1, sp.Rational(9, 16), sp.Rational(119, 480)]
    )
    if berger_metric * positive != sp.zeros(3, 1):
        raise AssertionError("neutral relative-clock Berger regression drifted")

    return {
        "aggregate_order": [
            "alpha_B",
            "alpha_R",
            "K=f^T K^R f",
            "C=beta^T Z(f) beta",
            "U=4 V4(f)",
        ],
        "Euler_formulas": {
            "metric": (
                "alpha_B B_ab+alpha_R(4R Ric_ab-R^2 g_ab)"
                "-K G_ab/6-T_ab=0"
            ),
            "radial_vector": (
                "(R/6)K^R f-grad_f[beta^T Z(f) beta/2]+grad_f V4=0"
            ),
            "compact_Gauss": "Q^T Z(f) beta=0 on a homogeneous closed-S3 slice",
            "phase": "nabla_a[Z(f)_ij B_j^a]=0",
        },
        "unit_cylinder_metric_rows": {
            "background": "R=6, beta=0",
            "row_order": ["E_00", "E_horizontal"],
            "matrix": _matrix(cylinder_metric),
            "radial_rows": (
                "K^R f+grad_f V4=0; two exact polynomial rows"
            ),
            "clock": "ABSENT_ON_THE_CONSTANT_PHASE_FIXTURE",
        },
        "frozen_Berger_metric_rows": {
            "background": "a=1,q=9/40,R=151/80",
            "row_order": ["E_00", "E_horizontal", "E_vertical"],
            "matrix": _matrix(berger_metric),
            "radial_rows": (
                "(151/480)K^R f-grad_f[beta^T Z(f) beta/2]"
                "+grad_f V4=0"
            ),
            "compact_Gauss": "Q^T Z(f) beta=0",
            "positive_neutral_clock_regression": {
                "aggregate_vector": ["5", "0", "1", "9/16", "119/480"],
                "metric_rows": "ZERO_EXACTLY",
                "canonical_primitive_charge": "Q=(1,0)^T",
                "velocity": ["beta1=0", "beta2=3/4"],
                "Gauss_row": "ZERO_EXACTLY",
                "relative_charge": "p2 nonzero when Z_22>0",
                "interpretation": (
                    "The primitive rank-one lattice genuinely permits the "
                    "old positive Berger clock in the neutral relative phase. "
                    "The terminal failure is the scale/trace trichotomy, not "
                    "stationarity or compact Gauss."
                ),
            },
        },
        "charge_split": {
            "canonical_momenta": "p=Z(f) beta",
            "gauge_constraint": "Q^T p=0",
            "relative_charge": (
                "for Q=(1,0)^T, p1=0 while Q_rel=p2 may be nonzero"
            ),
            "raw_D_phase_term": "beta2 delta p2 on the neutral clock branch",
            "scale_charge": (
                "constraint on closed S3; it cannot be left physical to "
                "supply the missing dressed-trace contraction"
            ),
        },
        "stationarity_disposition": (
            "A nonzero relative-clock stationary sector exists, so neither "
            "background stationarity nor compact Gauss is the no-go. It does "
            "not intersect a healthy independent dressed-trace scale gauge."
        ),
    }


def _terminal_verdict() -> dict[str, Any]:
    return {
        "result": "SCOPED_TWO_FIELD_MINIMAL_CHARGE_MATRIX_GOOD_LOCUS_EMPTY",
        "selected_action": False,
        "healthy_locus": "EMPTY",
        "compact_charge_lattice_result": (
            "primitive rank one leaves one legitimate relative phase and "
            "passes the compact-Gauss clock separator"
        ),
        "first_obstruction": (
            "positive two-field scalar kinetic forces b1=b2=a; the candidate "
            "scale is then reducible if the relative clock survives, while "
            "making it independent by s2!=0 gauges that clock"
        ),
        "full_BV_or_causal_completion_activated": False,
        "nonlinear_or_quantum_promotion": False,
        "next_gate": (
            "No automatic minimal successor. A new item must change the "
            "kinetic representation (for example non-Riemannian target "
            "constraints), add a distinct scale modulus/generator pair, or "
            "relax the dressed-trace/relative-clock requirements explicitly."
        ),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    if (
        payload["result_state"]
        != "SCOPED_TWO_FIELD_MINIMAL_CHARGE_MATRIX_GOOD_LOCUS_EMPTY"
        or payload["terminal_verdict"]["healthy_locus"] != "EMPTY"
        or payload["terminal_verdict"]["selected_action"]
        or payload["terminal_verdict"][
            "full_BV_or_causal_completion_activated"
        ]
        or any(payload["claim_flags"].values())
    ):
        raise AssertionError("terminal promotion detected")
    selected = payload["charge_lattice"]["selected_preflight_case"]
    if selected["Q"] != [["1"], ["0"]]:
        raise AssertionError("noncanonical charge lattice selected")
    strata = payload["positivity_and_gauge_rank"]["complete_healthy_strata"]
    if (
        strata["b1=b2=a_and_s2_zero"][
            "reducibility_vector_(omega,eta,gamma)"
        ]
        != ["-a", "1", "-s1"]
        or "relational clock is gauge"
        not in strata["b1=b2=a_and_s2_nonzero"]
    ):
        raise AssertionError("scale/clock trichotomy drifted")


def build() -> dict[str, Any]:
    imports = _load_imports()
    charge = _charge_lattice()
    action, ward = _action_and_ward()
    positivity = _positivity_and_gauge_rank()
    stationary = _stationarity_and_charges()
    verdict = _terminal_verdict()
    claim_boundary = (
        "This exact preflight classifies two formal-polar complex "
        "compensators, at most two compact U(1) generators with integer "
        "charge lattice up to GL(Z), two real scale columns, the complete "
        "declared minimal parity-even two-derivative scalar bilinears and "
        "regular quartic potential, and the certified cylinder/Berger "
        "homogeneous fixtures. Primitive compact rank one genuinely leaves a "
        "relative clock and evades the one-field Gauss obstruction. The good "
        "locus is nevertheless empty because positive active scalar kinetic, "
        "an independent dressed-trace scale direction and an ungauged "
        "relative clock cannot coexist in the declared representation. This "
        "does not exclude more fields, non-Riemannian or constrained target "
        "kinetics, higher derivatives, other potentials, boundaries, "
        "backgrounds or gauge representations. No selected action, full BV "
        "carrier, causal parent, nonlinear q2, Hadamard, anomaly/QME, "
        "particle, scattering, positivity or unitarity theorem follows."
    )
    payload = {
        "schema": "pure-weyl-compensator-two-field-charge-matrix-preflight-v1",
        "result_id": "COMPENSATOR_TWO_FIELD_CHARGE_MATRIX_PREFLIGHT_V1",
        "result_state": "SCOPED_TWO_FIELD_MINIMAL_CHARGE_MATRIX_GOOD_LOCUS_EMPTY",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "charge_lattice": charge,
        "action_basis": action,
        "constant_scale_Ward_system": ward,
        "positivity_and_gauge_rank": positivity,
        "stationarity_and_charges": stationary,
        "terminal_verdict": verdict,
        "claim_flags": {
            "SELECTED_ACTION": False,
            "FULL_BV_OR_CAUSAL_PARENT": False,
            "NONLINEAR_Q2": False,
            "HADAMARD_OR_QUANTUM": False,
            "GENERAL_MULTIFIELD_THEORY_EXCLUDED": False,
        },
        "claim_boundary": claim_boundary,
    }
    payload["content_hashes"] = {
        "imports_sha256": _digest(imports),
        "charge_lattice_sha256": _digest(charge),
        "action_sha256": _digest(action),
        "ward_sha256": _digest(ward),
        "positivity_rank_sha256": _digest(positivity),
        "stationarity_charge_sha256": _digest(stationary),
        "verdict_sha256": _digest(verdict),
        "claim_boundary_sha256": _digest(claim_boundary),
    }
    validate_payload(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            raise SystemExit("generated two-field charge-matrix result drifted")
        print(f"{payload['result_id']}: PASS")
        return
    OUTPUT.write_text(rendered)
    print(OUTPUT)


if __name__ == "__main__":
    main()
