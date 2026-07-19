"""Produce the exact candidate-13 mixed moment/resonance-null witness."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_moment_resonance_null_witness.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_moment_resonance_null_witness.schema.json"
AMPLITUDE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.json"
ISOLATED = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json"
TAUB = ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json"
AXIAL_CURRENT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_data() -> dict[str, sp.Expr]:
    rho = (-sp.Integer(250) + 461 * sp.sqrt(10)) / 2132
    a = 6 - 2 * sp.sqrt(3)
    b = sp.Rational(16, 3)
    q1 = sp.sqrt(rho + a)
    q2 = sp.sqrt(4 * rho + a)
    p1 = sp.sqrt(rho + b)
    denominator = 2 * q1 + q2
    y1 = sp.cancel(p1 * (2 * p1 + q2) / (q1 * denominator))
    y2 = sp.cancel(p1 * (p1 - q1) / (q2 * denominator))
    return {"rho": rho, "a": a, "b": b, "q1": q1, "q2": q2, "p1": p1, "y1": y1, "y2": y2}


def s(expr: sp.Expr) -> str:
    return sp.sstr(expr)


def build() -> dict[str, object]:
    amplitude = json.loads(AMPLITUDE.read_text())
    isolated = json.loads(ISOLATED.read_text())
    taub = json.loads(TAUB.read_text())
    axial = json.loads(AXIAL_CURRENT.read_text())
    fibre = next(row for row in amplitude["physical_fibres"] if row["candidate_index"] == 13)
    ledger_row = isolated["candidate_ledger"]["rows"][12]
    if not (
        fibre["rho"] == "(-250 + 461*sqrt(10))/2132"
        and fibre["first_branch"] == fibre["second_branch"] == "p_extra"
        and fibre["target_branch"] == "q_plus"
        and fibre["signed_momenta"] == [1, -2]
        and amplitude["classification"]["mandatory_second_fibre_zero_plane_certified"]
        and isolated["classification"]["twenty_one_distinct_admissible_candidates"]
        and ledger_row["rho"] == fibre["rho"]
    ):
        raise AssertionError("candidate-13 cross-fibre inputs changed")
    if not (
        taub["classification"]["generic_covariant_moment_map_Taub_equality_certified"]
        and taub["generic_moment_maps"]["complete_target_H_Taub"]["axial_inertia_before_the_minus_sign"] == [3, 1]
        and axial["full_solution_pairing"]["Einstein_branch_signature_for_lambda_ge_6"] == [1, 1]
    ):
        raise AssertionError("moment-map/current inputs changed")

    d = exact_data()
    # Verify the rational identities over an abstract positive-frequency
    # field.  Substitution of the algebraic fixture then preserves them and
    # avoids asking a CAS to rediscover a very large nested-radical minpoly.
    Q1, Q2, P1 = sp.symbols("Q1 Q2 P1", nonzero=True)
    Y1 = P1 * (2 * P1 + Q2) / (Q1 * (2 * Q1 + Q2))
    Y2 = P1 * (P1 - Q1) / (Q2 * (2 * Q1 + Q2))
    h_identity = sp.cancel(Q1**2 * Y1 + Q2**2 * Y2 - P1**2)
    px_identity = sp.cancel(Q1 * Y1 - 2 * Q2 * Y2 - P1)
    if h_identity != 0 or px_identity != 0:
        raise AssertionError("mixed occupation identities failed")
    lam = sp.Symbol("lam")
    minus_norm = sp.sympify(
        axial["full_solution_pairing"]["Einstein_minus_branch_norm"].replace("lambda", "lam"),
        locals={"lam": lam},
    ).subs(lam, 6)
    minus_norm = sp.factor(minus_norm)
    rho_lower_exact = 461**2 * 10 > 1316**2
    rho_upper_exact = 2305**2 * 10 < 7646**2
    minus_sign_exact = (6**2 > (2**2) * 3) and (1**2 < (3**2) * 3)
    occupation_sign_exact = (2**2) * 3 > (sp.Rational(2, 3)) ** 2
    if not (rho_lower_exact and rho_upper_exact and minus_sign_exact):
        raise AssertionError("exact current or circumference signs changed")
    if not occupation_sign_exact:
        raise AssertionError("occupation positivity failed")

    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-candidate13-mixed-moment-resonance-null-witness-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_MIXED_MOMENT_RESONANCE_NULL_WITNESS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "generality_level": "G1",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "candidate-13 tuned compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "one normalized axial p-primary mode at n=1 plus normalized axial q-minus modes at n=1 and n=-2; the p-primary n=-2 occupation is zero",
            "degree": 2,
            "parity": "axial",
            "ell": "input ell=2; candidate-13 cross-fibre output L=4",
            "m": 0,
            "k": "signed momentum integers n=1 and n=-2 with k_n=n*sqrt(rho)",
            "omega": "p-primary at n=1 and q-minus at n=1,-2; positive-frequency carrier with conjugates understood",
        },
        "exact_fixture": {
            "rho": s(d["rho"]),
            "rho_exact_interval": ["1/2", "3/5"],
            "q_minus_offset_a": s(d["a"]),
            "p_primary_offset_b": s(d["b"]),
            "frequencies": {"q1": s(d["q1"]), "q2": s(d["q2"]), "p1": s(d["p1"])},
            "normalized_current_signs": {"p_primary": 1, "q_minus": -1},
            "axial_q_minus_unnormalized_current_at_lambda_6": s(minus_norm),
        },
        "occupation_witness": {
            "p_primary_n1": "1",
            "p_primary_n_minus2": "0",
            "q_minus_n1": s(d["y1"]),
            "q_minus_n_minus2": s(d["y2"]),
            "positivity_certificate": "y1>0 and y2>0; p1>q1 because p1^2-q1^2=b-a=2*sqrt(3)-2/3>0",
            "moment_equations": {
                "H": "q1^2*y1+q2^2*y2-p1^2=0",
                "P_x": "q1*y1-2*q2*y2-p1=0",
                "J_1": "0",
                "J_2": "0",
                "J_3": "0",
            },
            "rotation_reason": "A coefficient supported only at m=0 has zero T3 expectation, while T1 and T2 connect m=0 only to absent m=+/-1 coefficients; distinct momentum/shell blocks are orthogonal.",
        },
        "resonance_restriction": {
            "candidate_13_cross_fibre_equations": "zero because every bilinear candidate-13 p(n=1)*p(n=-2) term vanishes on the certified second-fibre-zero plane",
            "candidate_13_rho_isolated": "the exact isolated-candidate certificate proves that all 21 admissible circumference values are pairwise distinct",
            "same_fibre_functionals": "OPEN",
            "other_cross_fibre_functionals_at_this_rho": "absent from the certified 21-fibre ledger by pairwise distinctness",
        },
        "classification": {
            "nonzero_real_mixed_witness_certified": True,
            "all_five_stabilizer_moment_maps_zero": True,
            "candidate_13_cross_fibre_resonance_functionals_zero": True,
            "candidate_13_mixed_Taub_resonance_common_zero_nontrivial": True,
            "same_fibre_resonance_functionals_classified": False,
            "complete_mixed_two_fibre_tangent_cone_classified": False,
            "bounded_or_smooth_second_order_extension_certified": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "second_order_verdict": {
            "bounded_or_finite_quasiperiodic": "OPEN",
            "smooth_secular": "OPEN",
            "causal_retarded": "NO_CERTIFIED_MAP",
        },
        "interpretation": "The pure-extra Taub no-go is not stable under adjoining the negative-current Einstein-minus branch: an exact nonzero mixed tangent cancels all five moment maps while remaining on the candidate-13 cross-fibre resonance zero set. This activates, but does not solve, the same-fibre source gate.",
        "provenance": {
            "inputs": {
                str(AMPLITUDE.relative_to(ROOT)): sha(AMPLITUDE),
                str(ISOLATED.relative_to(ROOT)): sha(ISOLATED),
                str(TAUB.relative_to(ROOT)): sha(TAUB),
                str(AXIAL_CURRENT.relative_to(ROOT)): sha(AXIAL_CURRENT),
            }
        },
        "next_gate": "compute and restrict every same-fibre quadratic adjoint-cokernel functional to this exact mixed three-occupation witness, then decide bounded and smooth-secular extension separately",
        "claim_boundary": "This is an independence and activation witness, not a second-order extension. It certifies only the declared axial m=0 mixed carrier on the candidate-13 background. Same-fibre sources, the complete mixed cone, causal corrections, residual observables and quantum states remain fail-closed.",
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
        raise AssertionError("candidate-13 mixed moment/resonance witness is stale")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_MIXED_MOMENT_RESONANCE_NULL_WITNESS: PASS")


if __name__ == "__main__":
    main()
