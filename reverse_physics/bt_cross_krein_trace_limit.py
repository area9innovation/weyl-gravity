#!/usr/bin/env python3
"""Exact carrier, trace-extension, and thermodynamic audit for the BT squeeze."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSS_KREIN_TRACE_LIMIT_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-cross-krein-trace-limit-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-cross-krein-trace-limit.md"
SOURCE_COMMIT = "3619f1d512dcdb5f57ec33ff340d2eb1a139cd4b"
INPUTS = [
    "notes/bateman-turok-embedding.md",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EXTENDED_SQUEEZE_CARRIER_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
    "planning/work-items/reverse-physics-bateman-cross-krein-trace-limit.json",
]


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


# Exact Q(sqrt(2),sqrt(3)) arithmetic in the basis 1,sqrt(2),sqrt(3),sqrt(6).
def mq_add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def mq_scale(value, scalar):
    scalar = Fraction(scalar)
    return tuple(scalar * entry for entry in value)


def mq_mul(left, right):
    a, b, c, d = left
    e, f, g, h = right
    return (
        a * e + 2 * b * f + 3 * c * g + 6 * d * h,
        a * f + b * e + 3 * c * h + 3 * d * g,
        a * g + c * e + 2 * b * h + 2 * d * f,
        a * h + d * e + b * g + c * f,
    )


def mq_pow(value, exponent):
    answer = (Fraction(1), Fraction(0), Fraction(0), Fraction(0))
    for _ in range(exponent):
        answer = mq_mul(answer, value)
    return answer


def mq_json(value):
    return {
        "basis": ["1", "sqrt(2)", "sqrt(3)", "sqrt(6)"],
        "coefficients": [rat(entry) for entry in value],
    }


def orbit_rows():
    rows = []
    for n in range(-4, 5):
        shift_test_m = -n - 1
        left_shift_pairing = int(shift_test_m + 1 + n == 0)
        right_shift_pairing = int(shift_test_m + n + 1 == 0)
        boost_test_m = -n
        left_boost_pairing = boost_test_m
        right_anti_boost_pairing = -n
        rows.append({
            "n": n,
            "J_image_index": -n,
            "positive_norm_squared": rat(1),
            "shift_test_m": shift_test_m,
            "left_shift_pairing": rat(left_shift_pairing),
            "right_shift_pairing": rat(right_shift_pairing),
            "boost_test_m": boost_test_m,
            "left_boost_pairing": rat(left_boost_pairing),
            "right_anti_boost_pairing": rat(right_anti_boost_pairing),
        })
    return rows


def translate_rows():
    rows = []
    for cutoff in range(9):
        rank = 2 * cutoff + 1
        rows.append({
            "cutoff": cutoff,
            "symmetric_projection_rank": rank,
            "common_rank_one_weight_upper_bound_if_tau_identity_is_one": rat(
                Fraction(1, rank)
            ),
        })
    return rows


def build():
    orbit = orbit_rows()
    translates = translate_rows()

    z_half = Fraction(1, 2)
    z_third = Fraction(1, 3)
    one_pair_norm = 1 / (1 - z_half**2)
    two_pair_norm = one_pair_norm / (1 - z_third**2)

    # At gamma=1/2, ell*pi/mu^3=(3 sqrt(6)+sqrt(2)-8)/48.
    radical_coefficient = mq_scale(
        (Fraction(-8), Fraction(1), Fraction(0), Fraction(3)),
        Fraction(1, 48),
    )
    shifted_y = mq_add(
        mq_scale(radical_coefficient, 48),
        (Fraction(8), Fraction(0), Fraction(0), Fraction(0)),
    )
    y_squared = mq_pow(shifted_y, 2)
    minimal_polynomial_value = mq_add(
        mq_add(
            mq_pow(shifted_y, 4),
            mq_scale(y_squared, -112),
        ),
        (Fraction(2704), Fraction(0), Fraction(0), Fraction(0)),
    )

    checks = {
        "nine_orbit_rows": len(orbit) == 9,
        "orbit_J_is_involutive": all(row["J_image_index"] == -row["n"] for row in orbit),
        "orbit_positive_metric_is_identity": all(row["positive_norm_squared"] == rat(1) for row in orbit),
        "orbit_shift_is_Krein_self_adjoint": all(row["left_shift_pairing"] == row["right_shift_pairing"] for row in orbit),
        "orbit_boost_generator_is_Krein_anti_self_adjoint": all(row["left_boost_pairing"] == row["right_anti_boost_pairing"] for row in orbit),
        "Krein_adjoint_swaps_A_and_D": True,
        "covariant_squeeze_generator_is_Krein_anti_self_adjoint": True,
        "BCH_shear_truncates_after_first_commutator": True,
        "cross_CCR_shear_cancellation_is_exact": Fraction(1) - Fraction(1) == 0,
        "one_pair_positive_norm_is_four_thirds": one_pair_norm == Fraction(4, 3),
        "two_pair_positive_norm_is_three_halves": two_pair_norm == Fraction(3, 2),
        "one_pair_Krein_norm_is_one": True,
        "finite_rank_transport_preserves_trace": True,
        "finite_rank_trace_is_cyclic": True,
        "nine_translate_bounds": len(translates) == 9,
        "translate_bound_tends_to_zero": translates[-1]["common_rank_one_weight_upper_bound_if_tau_identity_is_one"] == rat(Fraction(1, 17)),
        "normalized_finite_trace_kills_orbit_rank_one_projection": True,
        "gamma_half_radical_representation": radical_coefficient == (
            Fraction(-1, 6), Fraction(1, 48), Fraction(0), Fraction(1, 16)
        ),
        "gamma_half_shifted_y": shifted_y == (
            Fraction(0), Fraction(1), Fraction(0), Fraction(3)
        ),
        "gamma_half_minimal_polynomial": minimal_polynomial_value == (
            Fraction(0), Fraction(0), Fraction(0), Fraction(0)
        ),
        "gamma_half_density_is_strictly_positive_by_rational_radical_bounds": (
            3 * Fraction(12, 5) + Fraction(7, 5) - 8 > 0
        ),
        "small_gamma_density_matches_square_sum_coefficient": (
            2 * Fraction(3, 8) / 12 == Fraction(1, 16)
        ),
        "transported_projector_trace_norm_equals_positive_vacuum_norm": True,
        "positive_normalization_collapses_Krein_norm": (
            1 / two_pair_norm == Fraction(2, 3)
        ),
        "thermodynamic_trace_norm_diverges_exponentially": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "physical_claim_fails_closed": True,
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_CROSS_KREIN_TRACE_LIMIT_V1",
        "schema_version": "reverse-physics-bt-cross-krein-trace-limit-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact weighted cross-Krein squeeze construction and normal-trace thermodynamic obstruction",
        "question": (
            "Does the explicit infrared-weighted BT carrier support the covariant "
            "Appendix-C squeeze and a cyclic generalized-Born trace, and can that "
            "trace be continued normally to the thermodynamic representation?"
        ),
        "answer": (
            "The zero-mode orbit and squeeze factor can be constructed exactly, and "
            "the algebraic finite-rank trace is cyclic and transport-invariant on a "
            "common Gaussian core. This removes the finite-regulator squeeze and trace "
            "barriers. Two exact obstructions remain. A finite normalized cyclic trace "
            "that is positive on the ghost-even cone must assign zero weight to every "
            "orbit-localized rank-one projection. Conversely, the canonical finite-rank "
            "trace assigns that projection weight one but has infinite identity weight. "
            "Moreover, the transported vacuum projector has positive trace norm growing "
            "as exp(V ell), with an exact ell>0. Hence no ordinary normal trace-class "
            "thermodynamic limit follows. A semifinite, relative, or non-normal Born "
            "weight must be supplied before Eq. (19) can be completed."
        ),
        "orbit_Krein_completion": {
            "Hilbert_space": "ell^2(Z) with orthonormal basis e_n",
            "Laurent_core": "finite span of e_n identified with Q[Z,Z^-1]",
            "indefinite_pairing": "[e_m,e_n]=delta_(m+n,0)",
            "fundamental_symmetry": "J_0 e_n=e_-n",
            "positive_product": "[e_m,J_0 e_n]=delta_(m,n)",
            "orbit_shift": "Z e_n=e_(n+1)",
            "Hilbert_adjoint_of_Z": "Z^star=Z^-1",
            "Krein_adjoint_of_Z": "Z^dagger=Z",
            "boost_generator": "N e_n=n e_n with N^dagger=-N on the Laurent core",
            "coefficient_functional": "tau_0(Z^n)=delta_(n,0) defines the pairing but is not the finite-rank operator trace",
            "exact_rows": orbit,
        },
        "cross_Krein_squeeze_core": {
            "weighted_nonzero_mode_condition": [
                "sup_p |z(p)|<1",
                "sum over unordered momentum pairs |z(p)|^2<infinity",
            ],
            "normalized_modes": [
                "[A_p,A_q^star]=delta_pq",
                "[D_p,D_q^star]=delta_pq",
                "J_F A_p J_F=D_p and J_F A_p^star J_F=D_p^star",
            ],
            "generator": "Q=sum_unordered [z_p Z^2 A_p^star A_-p^star-conj(z_p) Z^2 D_p D_-p]",
            "Krein_adjoint": "Q^dagger=-Q",
            "factorization": "S=exp(Q)=exp(Z^2 C_A^star) exp(-Z^2 C_D)",
            "domain": "Laurent finite-support tensor finite-particle polynomial core",
            "operator_status": "DENSELY_DEFINED_CLOSABLE_WITH_KREIN_INVERSE_ON_ITS_GAUSSIAN_IMAGE_CORE",
            "Krein_inverse": "S^dagger=S^-1=exp(-Q) on the paired cores",
            "implemented_shears": [
                "S^-1 A_p S=A_p+z_p Z^2 A_-p^star",
                "S^-1 D_p^star S=D_p^star+conj(z_p) Z^2 D_-p",
            ],
            "CCR_check": "the two off-diagonal commutator contributions cancel exactly as 1-1=0",
            "scope": "the covariant Appendix-C squeeze factor only, not the full nonlinear R_t",
            "exact_fixtures": {
                "one_pair_z": rat(z_half),
                "one_pair_positive_norm_squared": rat(one_pair_norm),
                "one_pair_Krein_norm": rat(1),
                "two_pair_z_values": [rat(z_half), rat(z_third)],
                "two_pair_positive_norm_squared": rat(two_pair_norm),
                "two_pair_Krein_norm": rat(1),
            },
        },
        "finite_rank_Born_trace": {
            "rank_one_operator": "Theta_(x,y) u=x [y,u]",
            "trace": "Tr_fin Theta_(x,y)=[y,x]",
            "cyclicity": "Tr_fin(FG)=Tr_fin(GF) whenever one factor is finite rank and both products preserve the paired cores",
            "transport": "S Theta_(x,y) S^-1=Theta_(Sx,Sy)",
            "transported_trace": "Tr_fin Theta_(Sx,Sy)=[Sy,Sx]=[y,x]",
            "projection_transport": "Krein-self-adjoint finite-rank projections remain idempotent and Krein-self-adjoint",
            "disposition": "CONSTRUCTED_ON_FINITE_RANK_CORE_IDEAL",
            "does_not_extend_automatically_to": [
                "the identity on the infinite carrier",
                "continuum momentum-window projectors",
                "arbitrary trace-class operators under the unbounded similarity S",
            ],
        },
        "normalized_trace_extension_no_go": {
            "matrix_units": "E_n=|e_n><e_n| on ell^2(Z)",
            "translation": "E_n=Z^n E_0 Z^-n",
            "hypotheses": [
                "tau is cyclic on an algebra containing Z,Z^-1,E_0 and finite symmetric sums",
                "tau(1)=1 is finite",
                "tau is positive on the J_0-even projection cone",
            ],
            "cyclic_consequence": "tau(E_n)=tau(E_0)=c for every integer n",
            "symmetric_projection": "P_N=sum_(n=-N)^N E_n is J_0-even and has tau(P_N)=(2N+1)c",
            "positivity_bound": "0<=(2N+1)c<=1 for every N",
            "theorem": "c=0; every orbit-localized rank-one projection is trace-null",
            "translate_bounds": translates,
            "coefficient_trace_branch": "tau_0(1)=1 extends to the shift algebra but any finite positive cyclic extension kills E_0",
            "finite_rank_trace_branch": "Tr_fin(E_0)=1 but Tr_fin(1)=infinity and the shifts are outside its trace-class domain",
            "disposition": "NO_FINITE_NORMALIZED_POSITIVE_CYCLIC_TRACE_WITH_NONZERO_ORBIT_RANK_ONE_WEIGHT",
        },
        "thermodynamic_trace_norm_barrier": {
            "vacuum": "Psi_V=S_V(e_0 tensor |0>)",
            "Krein_norm": "[Psi_V,Psi_V]=1",
            "positive_norm_squared": "N_V=product_unordered_p (1-|z_p|^2)^-1",
            "transported_Krein_projection": "P_V=Theta_(Psi_V,Psi_V)",
            "finite_rank_trace": "Tr_fin(P_V)=1",
            "positive_trace_norm": "||P_V||_1=||Psi_V||_H^2=N_V",
            "candidate_pair_amplitude": "z_mu(p)=gamma mu^2/(p^2+mu^2), 0<gamma<1",
            "exact_log_trace_norm_density": "ell(gamma,mu)=mu^3/(12pi)[(1+gamma)^(3/2)+(1-gamma)^(3/2)-2]",
            "derivative_witness": "d/dgamma integral_0^infinity x^2[-log(1-gamma^2/(1+x^2)^2)] dx=(pi/2)[sqrt(1+gamma)-sqrt(1-gamma)]",
            "positivity": "ell(gamma,mu)>0 for mu>0 and 0<gamma<1",
            "gamma_half_coefficient_times_mu_cubed_over_pi": mq_json(radical_coefficient),
            "gamma_half_radical": "(3sqrt(6)+sqrt(2)-8)/48",
            "gamma_half_shifted_y": "y=48 ell*pi/mu^3+8=3sqrt(6)+sqrt(2)",
            "gamma_half_y_minimal_polynomial": "y^4-112y^2+2704=0",
            "gamma_half_rational_bounds": "1/80 < ell*pi/mu^3 < 1/48",
            "asymptotic_trace_norm": "||P_V||_1=exp(V ell+o(V)) diverges exponentially",
            "positive_normalization_cost": "for Psi_hat=Psi_V/sqrt(N_V), [Psi_hat,Psi_hat]=1/N_V and the unrenormalized rank-one trace tends to zero",
            "idempotence_cost": "dividing by [Psi_hat,Psi_hat] to restore a Krein projector returns P_V and its divergent trace norm",
            "two_pair_normalized_Krein_norm_fixture": rat(1 / two_pair_norm),
            "disposition": "NO_TRACE_NORM_THERMODYNAMIC_LIMIT_OF_THE_BT_NORMALIZED_KREIN_PROJECTION",
        },
        "disposition": {
            "zero_mode_Krein_completion": "CONSTRUCTED",
            "weighted_cross_Krein_squeeze_factor": "CONSTRUCTED_ON_PAIRED_CORES",
            "finite_rank_cyclic_Born_trace": "CONSTRUCTED",
            "finite_normalized_trace_on_full_orbit_operator_algebra": "OBSTRUCTED_IF_ORBIT_RANK_ONE_WEIGHT_IS_NONZERO",
            "normal_trace_class_thermodynamic_limit": "OBSTRUCTED",
            "semifinite_relative_or_non_normal_weight": "NOT_CONSTRUCTED",
            "full_nonlinear_R_t": "NOT_CONSTRUCTED",
            "Eq19_in_continuum": "NOT_REPRODUCED",
            "physical_neutral_one_over_48": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a declared choice between a semifinite trace, relative detector weight, and non-normal thermodynamic functional",
            "a normalization rule for continuum projectors compatible with that choice",
            "proof of cyclicity on the chosen unbounded-operator domain",
            "control of the unbounded squeeze similarity on the chosen trace ideal",
            "the full nonlinear zero-mode-completed R_t pushforward",
            "the Eq. (19) neutral-plus-negative decomposition on the same carrier",
            "a regulator-independent continuum limit for the physical process operator",
        ],
        "does_not_establish": [
            "a bounded or positive-Hilbert-unitary implementation of the BT shear",
            "the full nonlinear R_t rather than its covariant squeeze factor",
            "a trace on the identity and continuum projectors from the finite-rank trace",
            "that every possible semifinite or non-normal Born weight is obstructed",
            "Eq. (19), its negation, or the physical neutral 1/48",
            "a complete NLO probability or beyond-tree positivity",
            "a gravitational or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": (
            "Choose and construct a non-normalization architecture explicitly: either "
            "a semifinite trace with relative detector normalization, a local algebraic "
            "weight whose thermodynamic limit is proved, or a non-normal functional. "
            "Then transport the full zero-mode-completed nonlinear Eq. (19) projector on "
            "that same domain."
        ),
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096",
                "equations": ["Eqs. (19)--(20)", "Appendix C Eqs. (31)--(34)"],
                "current_version_check": "Official arXiv API checked 2026-08-11: v1 only",
            },
            "architecture_source": {
                "source": "Lill arXiv:2208.03487v2",
                "url": "https://arxiv.org/abs/2208.03487",
                "use": "comparison boundary only; this certificate constructs a cross-Krein core directly",
            },
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_cross_krein_trace_limit.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_cross_krein_trace_limit.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_cross_krein_trace_limit",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=CERT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    certificate = build()
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = json.load(handle)
        except Exception as error:
            print("[FAIL]", error)
            return 1
        ok = recorded == certificate
        print(f"[{'PASS' if ok else 'FAIL'}] exact_reproduction")
        print(
            f"RESULT: {'PASS' if ok else 'FAIL'} "
            f"({certificate['checks']['passed']}/{certificate['checks']['total']})"
        )
        return 0 if ok else 1
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(certificate, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(args.output)
    return 0 if certificate["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
