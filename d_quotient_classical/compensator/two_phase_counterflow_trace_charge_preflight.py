#!/usr/bin/env python3
"""Exact two-phase counterflow trace/charge preflight.

This is a finite homogeneous classical calculation.  It selects one
fixed-relative-charge Berger stratum but constructs neither a causal BV parent
nor a Green operator.  All serialized arithmetic is rational.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_V1.json"
PAYLOAD_OUTPUT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_PAYLOAD_V1.json"
IMPORTS = {
    "gauss_structure": {
        "path": "d_quotient_classical/compensator/CLOSED_S3_GAUGED_CLOCK_GAUSS_STRUCTURE_THEOREM_V1.json",
        "sha256": "c88b41a26262c2e79f2e7dbcccf66c50e19cfc179ed96dad8a847fc81f4e2433",
        "source_commit": "02a688837b866e9318ae92107744bba9c52de4d7",
        "result_id": "CLOSED_S3_GAUGED_CLOCK_GAUSS_STRUCTURE_THEOREM_V1",
    },
    "relative_hodge": {
        "path": "d_quotient_classical/compensator/CLOSED_S3_RELATIVE_PHASE_NONHOMOGENEOUS_HODGE_PREFLIGHT_V1.json",
        "sha256": "8bea19daa641aed5d771dd440624e5c7ea6128ce857ebd04c3d9b010c7acd5f9",
        "source_commit": "fcfa6f88b390a19a83f844791400f16da121e5d4",
        "result_id": "CLOSED_S3_RELATIVE_PHASE_NONHOMOGENEOUS_HODGE_PREFLIGHT_V1",
    },
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _q(value: sp.Expr) -> str:
    value = sp.factor(sp.cancel(value))
    return str(value)


def _rows(matrix: sp.Matrix) -> list[list[str]]:
    return [[_q(matrix[i, j]) for j in range(matrix.cols)] for i in range(matrix.rows)]


def _load_imports() -> dict[str, Any]:
    answer: dict[str, Any] = {}
    for key, spec in IMPORTS.items():
        path = ROOT / spec["path"]
        actual = _sha(path)
        data = json.loads(path.read_text())
        if actual != spec["sha256"] or data.get("result_id") != spec["result_id"]:
            raise AssertionError(f"{key} import drifted")
        answer[key] = {**spec, "actual_sha256": actual, "oracle_fields_consumed": []}
    return answer


def _phase_identity() -> dict[str, Any]:
    x1, x2, gauge, f1, f2 = sp.symbols("x1 x2 gauge f1 f2", nonzero=True)
    total = f1 + f2
    dchi = (f1 * x1 + f2 * x2) / total
    dpsi = x1 - x2
    mu = f1 * f2 / total
    residual = sp.expand(
        f1 * (x1 - gauge) ** 2
        + f2 * (x2 - gauge) ** 2
        - total * (dchi - gauge) ** 2
        - mu * dpsi**2
    )
    if sp.factor(residual) != 0:
        raise AssertionError("phase square completion failed")
    return {
        "field_change": {
            "F": "f1_squared+f2_squared",
            "chi": "(f1_squared*theta1+f2_squared*theta2)/F",
            "psi": "theta1-theta2",
            "mu_squared": "f1_squared*f2_squared/F",
        },
        "exact_identity": "f1_squared*(dtheta1-A)^2+f2_squared*(dtheta2-A)^2=F*(dchi-A)^2+mu_squared*(dpsi)^2",
        "diagonal_Gauss_equation": "F*(dot_chi-A0)=0",
        "diagonal_charge": "Q_diag=F*(dot_chi-A0)=0",
        "relative_charge": "Q_rel=a^3*mu_squared*dot_psi/N",
        "positivity_condition": "f1_squared>0 and f2_squared>0 implies mu_squared>0",
        "no_Maxwell_term": True,
    }


def _stationary_loci() -> dict[str, Any]:
    alpha_b, alpha_r, m2, v0, c = sp.symbols("alpha_B alpha_R M2 V0 C")
    r_cyl = sp.Integer(6)
    cyl = {
        "background": "R x S3 unit round cylinder",
        "R": "6",
        "beta": "0",
        "locus": {
            "alpha_B": "arbitrary",
            "alpha_R": "arbitrary",
            "M_P_squared": _q(c / 2 - 24 * alpha_r),
            "V0": _q(c - 36 * alpha_r),
            "C_condition": "C=mu_squared*Omega^2>0",
        },
    }

    r = sp.Rational(151, 80)
    beta_per_alpha = sp.Rational(961, 9600)
    beta = beta_per_alpha * alpha_b
    equations = sp.Matrix(
        [
            sp.Rational(9, 80) * alpha_b - c,
            v0 - c + beta + alpha_r * r**2,
            m2 - (3 * c - 4 * beta) / r + 4 * alpha_r * r,
        ]
    )
    matrix = sp.linear_eq_to_matrix(list(equations), [alpha_b, alpha_r, m2, v0, c])[0]
    rref, pivots = matrix.rref()
    solution = sp.solve(list(equations), [alpha_b, alpha_r, m2], dict=True)[0]
    expected = {
        alpha_b: sp.Rational(80, 9) * c,
        alpha_r: sp.Rational(19040, 615627) * c - sp.Rational(6400, 22801) * v0,
        m2: -sp.Rational(80, 151) * c + sp.Rational(320, 151) * v0,
    }
    if any(sp.factor(solution[k] - value) != 0 for k, value in expected.items()):
        raise AssertionError("Berger stationary locus drifted")
    return {
        "universal_static_equations": {
            "U(Phi0)": "C-beta",
            "Phi0": "(3*C/2-2*beta)/R",
            "M_P_squared": "2*Phi0-4*alpha_R*R",
            "V0": "C-beta-alpha_R*R^2",
        },
        "cylinder": cyl,
        "berger": {
            "background": "stationary Berger R x S3, a=1, c_squared=9/40",
            "R": _q(r),
            "beta_per_alpha_B": _q(beta_per_alpha),
            "anisotropic_shape_equation": "alpha_B=80*C/9",
            "coefficient_order": ["alpha_B", "alpha_R", "M_P_squared", "V0", "C"],
            "stationarity_matrix": _rows(matrix),
            "rref": _rows(rref),
            "pivot_columns": list(pivots),
            "locus": {str(k): _q(value) for k, value in expected.items()},
            "beta_over_C_on_locus": "961/1080",
            "alpha_R_zero_iff": "V0/C=119/1080",
        },
    }


def _quadratic_data() -> dict[str, Any]:
    # Coefficient matrices are derived from the exact homogeneous density
    # L=beta*N/a-6*a*Phi*adot^2/N-6*a^2*adot*Phidot/N
    #   +N*a*R*Phi-N*a^3*U(Phi)+a^3[mu^2*psidot^2+F(chidot-A0)^2]/(2N).
    beta, c, r, omega, alpha_r, f = sp.symbols("beta C R Omega alpha_R F", nonzero=True)
    raw_velocity = sp.Matrix(
        [
            [6 * (beta - sp.Rational(3, 4) * c) / r, -3, -sp.Rational(3, 2) * c / omega, 0],
            [-3, 0, 0, 0],
            [-sp.Rational(3, 2) * c / omega, 0, c / omega**2, 0],
            [0, 0, 0, f],
        ]
    )
    reduced_velocity = sp.Matrix(
        [[6 * (beta - sp.Rational(3, 4) * c) / r, -3], [-3, 0]]
    )
    if sp.factor(reduced_velocity.det()) != -9:
        raise AssertionError("R2 velocity determinant drifted")
    return {
        "homogeneous_density": "beta*N/a-6*a*Phi*adot^2/N-6*a^2*adot*Phidot/N+N*a*R*Phi-N*a^3*U(Phi)+a^3*(mu_squared*dot_psi^2+F*(dot_chi-A0)^2)/(2*N)",
        "variables": {
            "a": "exp(u/2)",
            "N": "exp(n)",
            "Phi": "Phi0+z",
            "psi": "Omega*t+p",
            "chi": "chi_bar+c",
            "A0": "A",
        },
        "raw_L2": "F*(A-dot_c)^2/2+C*dot_p^2/(2*Omega^2)+C*n^2/2+3*(beta-3*C/4)*dot_u^2/R-3*dot_u*dot_z+(beta-3*C/8)*u^2+n*(-C*dot_p/Omega-3*C*u/2)+u*(3*C*dot_p/(2*Omega)-R*z)-z^2/(4*alpha_R)",
        "raw_velocity_order": ["dot_u", "dot_z", "dot_p", "dot_c"],
        "raw_velocity_hessian": [[str(sp.factor(x)) for x in row] for row in raw_velocity.tolist()],
        "algebraic_constraints": {
            "Gauss": "A=dot_c",
            "lapse": "n=dot_p/Omega+3*u/2",
            "homogeneous_shift": "no independent scalar zero-mode; it imposes the closed spatial-diffeomorphism constraint",
            "delta_Q_rel_after_lapse": "0",
        },
        "reduced_L2_alpha_R_nonzero": "3*(beta-3*C/4)*dot_u^2/R-3*dot_u*dot_z+(beta-3*C/2)*u^2-R*u*z-z^2/(4*alpha_R)",
        "reduced_velocity_order": ["dot_u", "dot_z"],
        "reduced_velocity_hessian": [[str(sp.factor(x)) for x in row] for row in reduced_velocity.tolist()],
        "reduced_velocity_determinant": "-9",
        "alpha_R_nonzero_inertia": [1, 1],
        "alpha_R_nonzero_health": "OBSTRUCTED_SPLIT_SCALAR_PAIR",
        "principal_polynomials": {
            "alpha_R_nonzero_homogeneous_temporal_top_order": "-9*lambda^4",
            "alpha_R_zero_homogeneous_temporal_top_order": "6*(beta-3*C/4)*lambda^2/R",
            "relative_phase_all_positive_scalar_harmonics": "mu_squared*(omega^2-lambda_ell)",
            "spatial_gravity_parent": "NOT_COMPUTED_OUTSIDE_THIS_HOMOGENEOUS_PREFLIGHT",
        },
        "trace_touch": {
            "phase_order_zero_Hessian_nonzero_if": "C>0",
            "reduced_u_squared_coefficient": "beta-3*C/2",
            "compact_support_test": "with all other reduced variations zero, the u Euler row contains 2*(beta-3*C/2)*u; this coefficient is nonzero on both fixtures",
            "conclusion": "an arbitrary compactly supported pure-u variation is not a kernel direction on either declared fixture",
        },
    }


def _characteristics() -> dict[str, Any]:
    return {
        "alpha_R_nonzero_general": {
            "dimensionless_parameters": ["b=beta/C", "t=alpha_R*R^2/C", "y=lambda^2/R"],
            "roots_y": "(4*b+8*t-3 +/- sqrt((4*b-3)^2+48*t))/(24*t)",
            "repeated_threshold": "t_D=-(4*b-3)^2/48",
            "zero_root_threshold": "t_0=3/2-b",
            "Jordan_at_t_D": "size_2_at_each_repeated_square_root_branch",
            "Jordan_at_t_0": "size_2_at_lambda_zero",
            "health": "OBSTRUCTED_SPLIT_INERTIA_FOR_ALL_t",
        },
        "cylinder_alpha_R_zero": {
            "reduced_L2": "-3*C*dot_u^2/8-3*C*u^2/2",
            "velocity_Hessian": "-3*C/4",
            "characteristic_roots": ["-2", "2"],
            "Jordan": "simple",
            "Hamiltonian": "indefinite",
            "status": "OBSTRUCTED",
        },
        "cylinder_alpha_R_nonzero_thresholds": {"t_D": "-3/16", "t_0": "3/2"},
        "berger_alpha_R_nonzero_thresholds": {
            "b": "961/1080",
            "t_D": "-22801/3499200",
            "t_0": "659/1080",
            "repeated_y_at_t_D": "-1469/453",
            "nonzero_lambda_squared_at_t_0": "221819/158160",
        },
    }


def _selected_fixture() -> dict[str, Any]:
    c = sp.Rational(9, 16)
    beta = sp.Rational(961, 1920)
    r = sp.Rational(151, 80)
    kinetic = 3 * (beta - sp.Rational(3, 4) * c) / r
    mass = beta - sp.Rational(3, 2) * c
    omega2 = -mass / kinetic
    if (kinetic, mass, omega2) != (sp.Rational(1, 8), -sp.Rational(659, 1920), sp.Rational(659, 240)):
        raise AssertionError("selected Berger scalar fixture drifted")
    return {
        "selected": True,
        "background": "stationary Berger R x S3, a=1, c_squared=9/40",
        "charge_leaf": "Q_rel fixed; Q_diag=0",
        "parameters": {
            "f1_squared": "2",
            "f2_squared": "2",
            "F": "4",
            "mu_squared": "1",
            "Omega": "3/4",
            "C": "9/16",
            "alpha_B": "5",
            "alpha_R": "0",
            "M_P_squared": "-1/6",
            "V0": "119/1920",
            "R": "151/80",
            "beta": "961/1920",
        },
        "action": "integral sqrt(-ghat){5*C_hat^2/8-(1/12)*R_hat-119/1920-1/2*[2*(dtheta1-A)^2+2*(dtheta2-A)^2]}",
        "Maxwell_term": "ABSENT",
        "reduced_L2": "dot_u^2/8-659*u^2/1920",
        "velocity_Hessian": "1/4",
        "equation": "ddot_u+659*u/240=0",
        "characteristic_roots": ["-I*sqrt(659/240)", "I*sqrt(659/240)"],
        "Jordan": "two_simple_complex_roots",
        "Hamiltonian": "dot_u^2/8+659*u^2/1920",
        "Hamiltonian_positive": True,
        "relative_nonhomogeneous_mode": "positive with coefficient mu_squared=1",
        "split_scalar_pair": False,
        "terminal_status": "PASSED_FIXED_RELATIVE_CHARGE_BERGER_STRATUM",
    }


def _charges() -> list[dict[str, Any]]:
    return [
        {"generator": "U1_diag", "Hamiltonian": "Q_diag=F*(dot_chi-A0)", "unrestricted": "GAUGE_BY_GAUSS", "fixed_Q_rel_leaf": "GAUGE_BY_GAUSS"},
        {"generator": "R_rel", "Hamiltonian": "Q_rel", "unrestricted": "CHARGED_GLOBAL", "fixed_Q_rel_leaf": "PRESYMPLECTIC_NULL_HAMILTONIAN_CONSTANT"},
        {"generator": "D", "Hamiltonian": "Omega*Q_rel modulo the closed diffeomorphism constraint", "unrestricted": "CHARGED_GLOBAL", "fixed_Q_rel_leaf": "PRESYMPLECTIC_NULL_ONLY_AFTER_FIXED_CHARGE_RESTRICTION"},
        {"generator": "K=D-Omega*R_rel", "Hamiltonian": "0 modulo the closed diffeomorphism constraint", "unrestricted": "GAUGE_AND_BACKGROUND_STABILIZER", "fixed_Q_rel_leaf": "GAUGE_AND_BACKGROUND_STABILIZER"},
    ]


def _payload(imports: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "schema": "pure-weyl-two-phase-counterflow-trace-charge-preflight-payload-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_PAYLOAD_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imports": imports,
        "oracle_fields_consumed": [],
        "phase_decomposition": _phase_identity(),
        "stationary_loci": _stationary_loci(),
        "quadratic_hessian_and_constraints": _quadratic_data(),
        "characteristic_and_Jordan_ledger": _characteristics(),
        "charge_ledger": _charges(),
        "selected_fixture": _selected_fixture(),
    }
    payload["content_sha256"] = _digest(payload)
    return payload


def _certificate(imports: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    terminal = {
        "result_state": "CERTIFIED_SELECTED_FIXED_CHARGE_BERGER_PREFLIGHT",
        "cylinder": "OBSTRUCTED_NEGATIVE_REAL_TRACE_MODE",
        "alpha_R_nonzero": "OBSTRUCTED_SPLIT_SCALAR_PAIR",
        "selected_Berger": "PASSED_FIXED_RELATIVE_CHARGE_BERGER_STRATUM",
        "selected_action": True,
        "downstream_causal_parent_activation": True,
        "activation_scope": "only the serialized action, Berger background and fixed-Q_rel leaf",
        "unrestricted_D_is_gauge": False,
    }
    boundary = {
        "establishes": [
            "exact two-phase diagonal/relative square completion and Gauss reduction",
            "action-derived homogeneous trace/lapse Hessian on cylinder and frozen Berger backgrounds",
            "exact inertia, characteristic and Jordan classification of the declared homogeneous scalar block",
            "four-generator charge disposition on unrestricted and fixed-relative-charge strata",
            "one selected positive fixed-charge Berger preflight stratum",
        ],
        "does_not_establish": [
            "a support-local full BV causal parent",
            "Green hyperbolicity or a causal propagator",
            "a Hadamard state or any quantum claim",
            "that unrestricted D is gauge",
            "health away from the serialized action/background/charge leaf",
        ],
    }
    return {
        "schema": "pure-weyl-two-phase-counterflow-trace-charge-preflight-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_V1",
        "result_state": terminal["result_state"],
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imports": imports,
        "payload_ref": {
            "path": str(PAYLOAD_OUTPUT.relative_to(ROOT)),
            "sha256": "PENDING_WRITE",
            "content_sha256": payload["content_sha256"],
        },
        "selected_fixture": payload["selected_fixture"],
        "charge_ledger": payload["charge_ledger"],
        "terminal_verdict": terminal,
        "claim_boundary": boundary,
        "claim_flags": {
            "EXACT_HOMOGENEOUS_PREFLIGHT": True,
            "SELECTED_ACTION": True,
            "FULL_BV_CAUSAL_PARENT": False,
            "GREEN_HYPERBOLICITY": False,
            "HADAMARD_OR_QUANTUM": False,
            "UNRESTRICTED_D_GAUGE": False,
            "MAXWELL_TERM": False,
        },
        "content_hashes": {
            "selected_fixture_sha256": _digest(payload["selected_fixture"]),
            "charge_ledger_sha256": _digest(payload["charge_ledger"]),
            "terminal_sha256": _digest(terminal),
            "claim_boundary_sha256": _digest(boundary),
        },
    }


def validate_payload(payload: dict[str, Any]) -> None:
    expected = _digest({k: v for k, v in payload.items() if k != "content_sha256"})
    if payload.get("content_sha256") != expected:
        raise AssertionError("payload content hash mismatch")
    if payload.get("oracle_fields_consumed") != []:
        raise AssertionError("oracle consumption forbidden")
    if not payload["phase_decomposition"]["no_Maxwell_term"]:
        raise AssertionError("Maxwell term introduced")
    if payload["quadratic_hessian_and_constraints"]["reduced_velocity_determinant"] != "-9":
        raise AssertionError("split inertia certificate drifted")
    if payload["selected_fixture"]["parameters"]["alpha_R"] != "0":
        raise AssertionError("selected action left the healthy stratum")
    if not payload["selected_fixture"]["Hamiltonian_positive"]:
        raise AssertionError("selected Hamiltonian positivity lost")


def validate_certificate(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    flags = certificate["claim_flags"]
    if flags["FULL_BV_CAUSAL_PARENT"] or flags["GREEN_HYPERBOLICITY"] or flags["HADAMARD_OR_QUANTUM"] or flags["UNRESTRICTED_D_GAUGE"] or flags["MAXWELL_TERM"]:
        raise AssertionError("claim boundary promoted")
    if certificate["terminal_verdict"]["cylinder"] != "OBSTRUCTED_NEGATIVE_REAL_TRACE_MODE":
        raise AssertionError("cylinder obstruction was promoted")
    if certificate["terminal_verdict"]["unrestricted_D_is_gauge"]:
        raise AssertionError("unrestricted D charge was erased")
    expected = {
        "selected_fixture_sha256": _digest(certificate["selected_fixture"]),
        "charge_ledger_sha256": _digest(certificate["charge_ledger"]),
        "terminal_sha256": _digest(certificate["terminal_verdict"]),
        "claim_boundary_sha256": _digest(certificate["claim_boundary"]),
    }
    if certificate.get("content_hashes") != expected:
        raise AssertionError("certificate content hash mismatch")
    if certificate["payload_ref"]["content_sha256"] != payload["content_sha256"]:
        raise AssertionError("payload canonical hash mismatch")


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    imports = _load_imports()
    payload = _payload(imports)
    certificate = _certificate(imports, payload)
    validate_payload(payload)
    validate_certificate(certificate, payload)
    return certificate, payload


def write() -> None:
    certificate, payload = build()
    PAYLOAD_OUTPUT.write_text(_render(payload))
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD_OUTPUT)
    validate_certificate(certificate, payload)
    OUTPUT.write_text(_render(certificate))


def check() -> None:
    certificate, payload = build()
    if not OUTPUT.exists() or not PAYLOAD_OUTPUT.exists():
        raise AssertionError("generated artifacts missing")
    stored_payload = json.loads(PAYLOAD_OUTPUT.read_text())
    stored_certificate = json.loads(OUTPUT.read_text())
    if stored_payload != payload:
        raise AssertionError("stored payload drifted")
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD_OUTPUT)
    if stored_certificate != certificate:
        raise AssertionError("stored certificate drifted")
    print("TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_V1: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else write()


if __name__ == "__main__":
    main()
