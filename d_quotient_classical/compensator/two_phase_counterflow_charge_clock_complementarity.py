#!/usr/bin/env python3
"""Exact charge-clock complementarity and unrestricted-clock health theorem."""

from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path
from typing import Any
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name("TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1.json")
PAYLOAD = Path(__file__).with_name("TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_PAYLOAD_V1.json")
IMPORTS = {
    "causal_parent": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1.json", "7d969e7e630f793dfe12fe07b0e98a67b2543f9aa85fa03277e491fb00296db7"),
    "fixed_charge": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_V1.json", "812f6a3c2308eaeef09bee25ec8c79c8f7c86de7a51383141f8cae46c2f9cae5"),
    "background": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_V1.json", "9fa277c57a28aa831d56cec4a49774f716cb000616afde74013d9320dc0a1763"),
    "charge_seed": ("d_quotient_classical/certificates/BERGER_CLOCK_REDUCED_CHARGE_SEED.json", "573381287998b6645b37fcbad0273c23c0e5cff58450cbcf7a2dc1152a8dfcd9"),
}


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def canon(value: Any) -> str: return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def pin_imports() -> dict[str, Any]:
    rows = {}
    for name, (relative, expected) in IMPORTS.items():
        path = ROOT / relative; actual = sha(path)
        if actual != expected: raise AssertionError(f"import drift {name}: {actual}")
        data = json.loads(path.read_text())
        rows[name] = {"path": relative, "result_id": data["result_id"], "sha256": actual, "oracle_fields_consumed": []}
    return rows


def finite_rank_fixture(C: sp.Matrix, v: sp.Matrix) -> dict[str, Any]:
    if C.cols != v.rows or v.cols != 1: raise ValueError("shape mismatch")
    rank_c = C.rank(); augmented = C.col_join(v.T).rank()
    d_null = augmented == rank_c
    quotient_clock_dimension = C.cols - rank_c
    d_clock_survives = not d_null
    return {"n": C.cols, "constraint_rank": rank_c, "quotient_clock_dimension": quotient_clock_dimension,
            "D_null_on_constraint_tangent": d_null, "D_clock_class_survives_quotient": d_clock_survives,
            "rank_C": rank_c, "rank_C_stacked_vT": augmented}


def build_payload() -> dict[str, Any]:
    pins = pin_imports()
    causal = json.loads((ROOT / IMPORTS["causal_parent"][0]).read_text())
    fixed = json.loads((ROOT / IMPORTS["fixed_charge"][0]).read_text())
    if causal["complete_parent"]["complete_component_rank"] != 70 or not causal["complete_parent"]["zero_modes_retained"]:
        raise AssertionError("unrestricted carrier import failed")
    if fixed["claim_flags"]["POSITIVE_RELATIVE_CLOCK_SURVIVES"]:
        raise AssertionError("fixed branch was promoted")

    omega = sp.Rational(3, 4)
    inertia = sp.Rational(12, 5) * sp.pi**2 * sp.sqrt(10)
    charge = sp.simplify(inertia * omega)
    J = sp.Matrix([[0, 1], [-1, 0]])
    A = sp.Matrix([[0, 1 / inertia], [0, 0]])
    if A**2 != sp.zeros(2) or A.rank() != 1:
        raise AssertionError("global Jordan block failed")
    if sp.factor(charge - sp.Rational(9, 5) * sp.pi**2 * sp.sqrt(10)) != 0:
        raise AssertionError("integrated charge normalization failed")
    hessian = sp.Matrix([[0, 0], [0, 1 / inertia]])
    if sp.simplify(J * hessian - A) != sp.zeros(2):
        raise AssertionError("Hamiltonian evolution normalization failed")

    fixtures = {
        "single_fixed_charge": finite_rank_fixture(sp.Matrix([[1]]), sp.Matrix([omega])),
        "two_clocks_D_constrained": finite_rank_fixture(sp.Matrix([[1, 0]]), sp.Matrix([omega, 0])),
        "two_clocks_D_unconstrained": finite_rank_fixture(sp.Matrix([[1, 0]]), sp.Matrix([0, omega])),
    }
    if not fixtures["single_fixed_charge"]["D_null_on_constraint_tangent"] or fixtures["single_fixed_charge"]["D_clock_class_survives_quotient"]:
        raise AssertionError("rank-one complementarity failed")

    return {
        "schema": "pure-weyl-two-phase-counterflow-charge-clock-complementarity-payload-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_PAYLOAD_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "imports": pins,
        "general_theorem": {
            "phase_space": "T*R^n with Omega=sum_i dQ_i wedge dpsi_i",
            "D_velocity": "v in R^n with i_D Omega=v^T dQ and H_D=v^T Q",
            "regular_charge_constraint": "C Q=q0, rank(C)=r, followed by quotient by phase translations im(C^T)",
            "nullity_criterion": "D is null on ker(C dQ) iff v belongs to im(C^T), equivalently rank([C;v^T])=rank(C)",
            "surviving_clock_class": "[v] in R^n/im(C^T)",
            "complementarity": "D null implies [v]=0, so no D-evolving clock survives; [v]!=0 implies D remains charged and non-gauge",
            "intermediate_regular_reduction_retaining_D_clock_and_making_D_null": "IMPOSSIBLE",
            "fixtures": fixtures,
        },
        "branch_dichotomy": {
            "fixed_Q_rel": {"D": "null after derived restriction", "R_rel": "quotiented radical", "relative_clock_dimension": 0, "status": "OBSTRUCTED_CLOCK_REMOVED"},
            "unrestricted_Q_rel": {"symplectic_basis": ["delta_psi_0", "delta_Q_rel"], "symplectic_matrix": [[0, 1], [-1, 0]], "pairing_rank": 2, "R_rel": "charged global symmetry", "D": "physical Hamiltonian generator H_D=Omega_background Q_rel", "K": "D-Omega_background R_rel is the background stabilizer", "relative_clock_dimension": 2},
            "no_averaging": True,
        },
        "unrestricted_global_clock_health": {
            "background_Omega": "3/4", "integrated_inertia": "12*pi^2*sqrt(10)/5", "background_Q_rel": "9*pi^2*sqrt(10)/5",
            "quadratic_augmented_Hessian_basis_[psi,Q]": [["0", "0"], ["0", "sqrt(10)/(24*pi^2)"]],
            "quadratic_augmented_Hessian_inertia": [1, 0, 1],
            "linearized_evolution_matrix": [["0", "sqrt(10)/(24*pi^2)"], ["0", "0"]],
            "characteristic_polynomial": "lambda^2", "roots": [{"root": "0", "algebraic_multiplicity": 2, "geometric_multiplicity": 1, "largest_Jordan_block": 2}],
            "Jordan_chain": ["e_psi", "I*e_Q with A(I*e_Q)=e_psi"],
            "solution": "delta_Q_rel(t)=q1; delta_psi_0(t)=psi1+t*q1/I",
            "real_exponential_growing_roots": 0,
            "bounded_or_finite_quasiperiodic_stability": False,
            "first_failed_physical_sector": "homogeneous global relative-charge mode has a physical secular phase Jordan partner",
            "why_not_gauge": "R_rel is charged on the unrestricted carrier and raw D has Hamiltonian Omega_background Q_rel",
            "positive_fact": "the augmented charge Hessian 1/I is positive on the charge direction",
            "terminal_verdict": "UNRESTRICTED_CLOCK_POSITIVE_CHARGE_CURVATURE_BUT_SECULARLY_UNBOUNDED",
        },
        "remaining_sector_ledger": {
            "unrestricted_70_row_unary_causality": "CERTIFIED_IMPORTED",
            "all_Hodge_physical_cohomology_pairing_inertia": "NOT_REACHED_AFTER_FIRST_EXACT_FAILURE",
            "gradient_cone": "NOT_REACHED_AFTER_FIRST_EXACT_FAILURE",
            "other_real_growing_modes": "NOT_REACHED_AFTER_FIRST_EXACT_FAILURE",
        },
        "claim_boundary": {
            "establishes": ["finite-rank charge-clock complementarity theorem", "separate fixed and unrestricted branches", "physical charged raw-D global Darboux pair on the unrestricted branch", "positive charge curvature and exact size-two zero Jordan block", "first failure of bounded linear clock stability"],
            "does_not_establish": ["complete all-Hodge health or instability", "a negative-norm mode", "exponential instability", "fixed-charge clock survival", "observer, nonlinear, Hadamard, QME, particle, scattering or unitarity claims"],
        },
        "oracle_fields_consumed": [],
    }


def documents():
    payload = build_payload(); payload["content_sha256"] = canon(payload)
    cert = {"schema": "pure-weyl-two-phase-counterflow-charge-clock-complementarity-v1", "result_id": "TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1", "result_state": "UNRESTRICTED_CHARGED_CLOCK_HAS_EXACT_SECULAR_ZERO_JORDAN_OBSTRUCTION", "dependency_tags": payload["dependency_tags"], "imports": payload["imports"], "general_theorem_sha256": canon(payload["general_theorem"]), "branch_dichotomy_sha256": canon(payload["branch_dichotomy"]), "first_failed_physical_sector": payload["unrestricted_global_clock_health"]["first_failed_physical_sector"], "bounded_stability": False, "real_exponential_growing_roots": 0, "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "content_sha256": payload["content_sha256"]}, "claim_boundary": payload["claim_boundary"]}
    return cert, payload


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args=parser.parse_args(); cert,payload=documents()
    if args.check:
        if json.loads(OUT.read_text()) != cert or json.loads(PAYLOAD.read_text()) != payload: raise SystemExit("generated artifacts stale")
    else:
        OUT.write_text(json.dumps(cert,indent=2,sort_keys=True)+"\n"); PAYLOAD.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print("TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1: PASS")


if __name__ == "__main__": main()
