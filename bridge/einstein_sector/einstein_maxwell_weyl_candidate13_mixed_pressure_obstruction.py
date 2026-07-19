"""Certify the candidate-13 bounded pressure obstruction and smooth extension."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_mixed_pressure_obstruction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_candidate13_mixed_pressure_obstruction.schema.json"
WITNESS = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_moment_resonance_null_witness.json"
SAME_FIBRE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_same_fibre_resonance_census.json"
FIXED_ELL = ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order.json"
SMOOTH = ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_fixture() -> dict[str, sp.Expr]:
    rho = (-sp.Integer(250) + 461 * sp.sqrt(10)) / 2132
    q1 = sp.sqrt(rho + 6 - 2 * sp.sqrt(3))
    q2 = sp.sqrt(4 * rho + 6 - 2 * sp.sqrt(3))
    p1 = sp.sqrt(rho + sp.Rational(16, 3))
    y1 = p1 * (2 * p1 + q2) / (q1 * (2 * q1 + q2))
    y2 = p1 * (p1 - q1) / (q2 * (2 * q1 + q2))
    pressure = sp.factor(rho * (1 - y1 - 4 * y2) / 2)
    return {"rho": rho, "q1": q1, "q2": q2, "p1": p1, "y1": y1, "y2": y2, "pressure": pressure}


def s(value: sp.Expr) -> str:
    return sp.sstr(value)


def build() -> dict[str, object]:
    witness = json.loads(WITNESS.read_text())
    same = json.loads(SAME_FIBRE.read_text())
    fixed = json.loads(FIXED_ELL.read_text())
    smooth = json.loads(SMOOTH.read_text())
    if not (
        witness["classification"]["all_five_stabilizer_moment_maps_zero"]
        and witness["classification"]["candidate_13_cross_fibre_resonance_functionals_zero"]
        and same["classification"]["candidate_13_all_nonzero_same_fibre_channels_off_shell"]
        and smooth["classification"]["complete_finite_harmonic_smooth_tangent_cone_classified"]
        and smooth["classification"]["complete_smooth_adjoint_cokernel_equals_five_stabilizers"]
    ):
        raise AssertionError("candidate-13 pressure inputs changed")
    circle = fixed["primary_action_and_scalar_source_theorem"]["circle_pressure"]
    if "proportional to k^2" not in circle["feynman_hellmann_reason"]:
        raise AssertionError("circle-pressure input changed")

    d = exact_fixture()
    Q1, Q2, P1 = sp.symbols("Q1 Q2 P1", positive=True)
    Y1 = P1 * (2 * P1 + Q2) / (Q1 * (2 * Q1 + Q2))
    Y2 = P1 * (P1 - Q1) / (Q2 * (2 * Q1 + Q2))
    if sp.cancel(Q1**2 * Y1 + Q2**2 * Y2 - P1**2) != 0:
        raise AssertionError("H identity changed")
    if sp.cancel(Q1 * Y1 - 2 * Q2 * Y2 - P1) != 0:
        raise AssertionError("P_x identity changed")
    if not (461**2 * 10 > 250**2 and 2**2 * 3 > sp.Rational(2, 3) ** 2):
        raise AssertionError("elementary sign witnesses changed")
    # Exact sign chain: rho>0; p1>q1; hence y1>1 and y2>0, so pressure<0.

    return {
        "schema": "einstein-maxwell-weyl-candidate13-mixed-pressure-obstruction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_CANDIDATE13_MIXED_PRESSURE_OBSTRUCTION",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "generality_level": "G1",
        "scope": witness["scope"],
        "primary_action_identity": {
            "kernel": "A=sqrt(1+c)*G(c)*P(omega^2-k^2/(1+c))",
            "on_shell_circle_derivative": "dA/dc|_(c=0,P=0)=G(0)*P'(s)*k^2",
            "normalized_current": "h=2*G(0)*P'(s)",
            "pressure_functional": "R_c(u)=(1/2) sum k_j^2 h_j",
            "universality": "the formula holds for every simple p- or q-primary and is independent of the regular primary normalization G",
        },
        "exact_witness": {
            "rho": s(d["rho"]),
            "signed_current_occupations": {"p_n1": "1", "qminus_n1": f"-({s(d['y1'])})", "qminus_n_minus2": f"-({s(d['y2'])})"},
            "moment_identities": {"H": "q1^2*y1+q2^2*y2-p1^2=0", "P_x": "q1*y1-2*q2*y2-p1=0", "rotations": "J_1=J_2=J_3=0"},
            "pressure": s(d["pressure"]),
            "pressure_reduced_factor": s(1 - d["y1"] - 4 * d["y2"]),
            "exact_nonzero_sign_proof": "rho>0 and p1>q1. Therefore y1=(p1/q1)*(2*p1+q2)/(2*q1+q2)>1 and y2>0, so 1-y1-4*y2<0 and R_c(u)<0.",
        },
        "independence_theorem": {
            "five_moment_maps": "zero",
            "candidate_13_cross_fibre_functionals": "zero",
            "all_nonzero_frequency_same_fibre_functionals": "not applicable because every channel is off shell",
            "bounded_circle_pressure_functional": "strictly negative",
            "conclusion": "mu_X(u)=0 for every compact stabilizer X, but R_c^bounded(u)!=0",
        },
        "zero_frequency_source": {
            "typed_pairing": "R_c(u)=<dcircle,(1/2)D^2E_WM[u,u]> in the constant circumference/radius direction",
            "value": s(d["pressure"]),
            "bounded_cokernel_reason": "a nonzero constant circle-pressure coefficient cannot be produced by a bounded or finite-quasiperiodic correction in the homogeneous zero-frequency block",
            "calibration_boundary": "only the action-derived pairing and its nonzero sign are asserted here; no componentwise E11 source convention is imported",
        },
        "correction_classes": {
            "bounded_or_finite_quasiperiodic": {
                "status": "OBSTRUCTED",
                "reason": "at Omega=0 the homogeneous operator has no bounded image in the E11 pressure row, while R_c(u)<0",
            },
            "smooth_exponential_polynomial": {
                "status": "CERTIFIED",
                "abstract_sufficiency": "the complete finite-support smooth theorem says the five stabilizer moment maps exhaust the persistent cokernel",
                "pressure_correction": "a finite secular primitive exists by the complete smooth theorem; its componentwise normalization is not asserted by this pressure-pairing certificate",
            },
            "causal_retarded": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "candidate13_mixed_moment_resonance_independence_witness_certified": True,
            "candidate13_bounded_pressure_functional_nonzero": True,
            "candidate13_bounded_or_finite_quasiperiodic_extension_obstructed": True,
            "candidate13_smooth_exponential_polynomial_extension_certified": True,
            "complete_candidate13_mixed_cone_classified": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "provenance": {
            "inputs": {
                str(WITNESS.relative_to(ROOT)): sha(WITNESS),
                str(SAME_FIBRE.relative_to(ROOT)): sha(SAME_FIBRE),
                str(FIXED_ELL.relative_to(ROOT)): sha(FIXED_ELL),
                str(SMOOTH.relative_to(ROOT)): sha(SMOOTH),
            }
        },
        "next_gate": "classify the bounded pressure/resonance functionals on the full candidate-13 mixed moment-map cone rather than this single exact axial witness",
        "claim_boundary": "This theorem classifies one declared candidate-13 axial m=0 mixed tangent: bounded/finitely quasiperiodic correction is OBSTRUCTED, while a smooth exponential-polynomial second-order correction is CERTIFIED. It does not classify the full mixed cone, all-orders integration, causal corrections, residual observables or quantum states.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
    elif not OUTPUT.exists() or OUTPUT.read_text() != rendered:
        raise AssertionError("candidate-13 mixed pressure certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_CANDIDATE13_MIXED_PRESSURE_OBSTRUCTION: PASS")


if __name__ == "__main__":
    main()
