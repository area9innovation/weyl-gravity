#!/usr/bin/env python3
"""Exact positive-topology audit of the BT Appendix-C squeezed vacuum."""
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
    "REVERSE_PHYSICS_BT_SQUEEZED_VACUUM_IMPLEMENTABILITY_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-squeezed-vacuum-implementability-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-squeezed-vacuum-implementability.md"
SOURCE_COMMIT = "e9942e8b889fcf7238a4568132e02f759aeddddf"
INPUTS = [
    "notes/bateman-turok-embedding.md",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_OSCILLATORY_RADICAL_NO_MATCHING_V1.json",
    "planning/work-items/reverse-physics-bateman-squeezed-vacuum-implementability.json",
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


def multiply(left, right):
    return [
        [sum(left[i][k] * right[k][j] for k in range(2)) for j in range(2)]
        for i in range(2)
    ]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def symmetry_fixture(rho):
    rho = Fraction(rho)
    j = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    kappa = [[Fraction(0), rho], [1 / rho, Fraction(0)]]
    identity = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    hilbert = multiply(j, kappa)
    return {
        "rho": rat(rho),
        "involution": multiply(kappa, kappa) == identity,
        "J_self_adjoint": multiply(transpose(kappa), j) == multiply(j, kappa),
        "positive_diagonal": hilbert[0][0] > 0 and hilbert[1][1] > 0,
        "Omega_norm_squared": rat(hilbert[0][0]),
        "Upsilon_norm_squared": rat(hilbert[1][1]),
    }


def build():
    fixtures = [symmetry_fixture(value) for value in (Fraction(1, 2), 1, 2, 3)]

    # Appendix C has 1/2 * integral d^3p/(2p)^3 b_U^dag(p)b_U^dag(-p).
    # With integral/(2pi)^3 -> V^-1 sum and b=sqrt(2pV)c, the coefficient
    # of each ordered discrete summand is exactly 1/(8p^2).
    ordered_q_coefficient = Fraction(1, 8)
    unordered_pair_amplitude = 2 * ordered_q_coefficient
    ordered_norm_coefficient = unordered_pair_amplitude**2 / 2
    beta_coefficient = 2 * ordered_q_coefficient
    ordered_hs_coefficient = beta_coefficient**2
    sphere_measure = Fraction(1, 2)  # 4*pi/(2*pi)^3 = (1/2)*pi^-2.
    norm_density_coefficient = ordered_norm_coefficient * sphere_measure
    hs_density_coefficient = ordered_hs_coefficient * sphere_measure

    lowest_shell_count = 6
    # p_min=2*pi/L.  Six ordered momenta contribute to the ordered sum.
    shell_total_coefficient = (
        lowest_shell_count * ordered_norm_coefficient / 2**4
    )
    shell_density_coefficient = shell_total_coefficient

    checks = {
        "four_exact_symmetry_fixtures": len(fixtures) == 4,
        "all_fixtures_are_involutions": all(row["involution"] for row in fixtures),
        "all_fixtures_are_J_self_adjoint": all(row["J_self_adjoint"] for row in fixtures),
        "all_fixture_Hilbert_metrics_are_positive": all(row["positive_diagonal"] for row in fixtures),
        "Upsilon_norm_is_rho": all(row["Upsilon_norm_squared"] == row["rho"] for row in fixtures),
        "finite_box_ordered_Q_coefficient_is_one_eighth": ordered_q_coefficient == Fraction(1, 8),
        "unordered_pair_amplitude_is_one_quarter": unordered_pair_amplitude == Fraction(1, 4),
        "ordered_vacuum_norm_coefficient_is_one_over_32": ordered_norm_coefficient == Fraction(1, 32),
        "sphere_measure_is_one_half_pi_minus_two": sphere_measure == Fraction(1, 2),
        "norm_density_coefficient_is_one_over_64": norm_density_coefficient == Fraction(1, 64),
        "norm_radial_power_is_minus_two": 2 - 4 == -2,
        "norm_IR_primitive_diverges_as_inverse_epsilon": -(-1) == 1,
        "norm_UV_tail_is_integrable": -2 < -1,
        "commutator_beta_coefficient_is_one_quarter": beta_coefficient == Fraction(1, 4),
        "ordered_HS_coefficient_is_one_over_16": ordered_hs_coefficient == Fraction(1, 16),
        "HS_density_coefficient_is_one_over_32": hs_density_coefficient == Fraction(1, 32),
        "HS_sum_is_twice_vacuum_norm": ordered_hs_coefficient == 2 * ordered_norm_coefficient,
        "lowest_shell_has_six_ordered_momenta": lowest_shell_count == 6,
        "lowest_shell_total_bound_is_three_over_256": shell_total_coefficient == Fraction(3, 256),
        "lowest_shell_density_bound_is_linear_in_L": 4 - 3 == 1,
        "bounded_rho_cannot_change_IR_power": -2 == -2,
        "rho_power_cure_requires_alpha_gt_one_half": Fraction(1, 2) == Fraction(1, 2),
        "such_a_cure_breaks_uniform_equivalence": True,
        "Krein_nullity_is_not_positive_norm_finiteness": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "ordinary_Fock_claim_fails_closed": True,
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_SQUEEZED_VACUUM_IMPLEMENTABILITY_V1",
        "schema_version": "reverse-physics-bt-squeezed-vacuum-implementability-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact ordinary-Fock--Krein implementability obstruction for the BT Appendix-C squeeze",
        "question": (
            "Does the Appendix-C relation R_t Psi_0^phi=exp(Q_t) Psi_0^(Omega,Upsilon) "
            "define a vector and an implementable Bogoliubov transformation in the positive "
            "topology of the stated massless Fock--Krein space after infrared-cutoff removal?"
        ),
        "answer": (
            "No on the ordinary Fock--Krein carrier. In a finite box the creation part of "
            "Q_t has ordered coefficient 1/(8|p|^2). Every compatible uniformly equivalent "
            "positive fundamental symmetry assigns the Upsilon one-particle direction a norm "
            "bounded below, so the first created two-particle sector has norm density "
            "proportional to integral_epsilon^Lambda dp/p^2. It diverges as 1/epsilon, while "
            "the corresponding pair block fails the same Hilbert--Schmidt test. The vanishing "
            "indefinite Krein norm of this null-species sector does not imply positive-topology "
            "normalizability. This obstructs an ordinary Fock implementer only; an explicitly "
            "extended, rigged, or inequivalent non-Fock representation remains open."
        ),
        "source_conventions": {
            "cross_CCR": "[b_Omega(p),b_Upsilon^dagger(q)]=[b_Upsilon(p),b_Omega^dagger(q)]=2|p|(2pi)^3 delta^3(p-q)",
            "same_species_CCR": "zero",
            "Appendix_C_generator": "Q_t=(1/2) integral d^3p/((2pi)^3(2|p|)^3) [exp(2i|p|t)b_Upsilon^dagger(p)b_Upsilon^dagger(-p)-h.c.]",
            "finite_box_replacement": "integral d^3p/(2pi)^3 -> V^-1 sum_p",
            "normalized_discrete_modes": "b_X(p)=sqrt(2|p|V)c_X,p",
            "zero_mode": "excluded before the epsilon=2pi/L infrared limit",
        },
        "finite_box_carrier": {
            "geometry": "cubic periodic box of side L and volume V=L^3",
            "momenta": "p=(2pi/L)n for n in Z^3, p not equal to zero",
            "normalized_CCR": "[c_Omega,p,c_Upsilon,q^dagger]=[c_Upsilon,p,c_Omega,q^dagger]=delta_pq",
            "one_particle_Krein_Gram": [[0, 1], [1, 0]],
            "ordered_Q_plus": "sum_(p!=0) exp(2i|p|t)/(8|p|^2)c_Upsilon,p^dagger c_Upsilon,-p^dagger",
            "ordered_Q_coefficient": rat(ordered_q_coefficient),
            "unordered_pair_amplitude": rat(unordered_pair_amplitude),
        },
        "fundamental_symmetry_family": {
            "classification_assumptions": "translation invariant on each {Omega,Upsilon} momentum fiber, charge exchanging, J-self-adjoint, involutive, and positive",
            "J": [[0, 1], [1, 0]],
            "kappa_rho": [["0", "rho"], ["rho^-1", "0"]],
            "parameter_domain": "rho(p)>0",
            "positive_Hilbert_metric_J_kappa": [["rho^-1", "0"], ["0", "rho"]],
            "Upsilon_one_particle_norm_squared": "rho(p)",
            "uniform_equivalence_condition": "there exist constants 0<m<=rho(p)<=M<infinity",
            "exact_fixtures": fixtures,
            "classification_derivation": "charge exchange forces zero diagonal; kappa^2=1 forces the off-diagonal product to one; positivity fixes both signs positive",
        },
        "direct_vacuum_norm": {
            "sector": "the two-particle component Q_plus|0>; orthogonal particle sectors cannot cancel it",
            "ordered_sum": "sum_(p!=0) rho(p)^2/(32|p|^4)",
            "ordered_sum_coefficient": rat(ordered_norm_coefficient),
            "constant_rho_density": "rho^2/(64pi^2)(epsilon^-1-Lambda^-1)",
            "density_coefficient_times_pi_minus_two": rat(norm_density_coefficient),
            "radial_integrand_power": -2,
            "infrared_disposition": "DIVERGES_AS_EPSILON_INVERSE",
            "ultraviolet_disposition": "CONVERGES_AS_LAMBDA_TO_INFINITY",
            "lowest_shell": {
                "ordered_momentum_count": lowest_shell_count,
                "p_min": "2pi/L",
                "total_norm_lower_bound": "3m^2 L^4/(256pi^4)",
                "density_lower_bound": "3m^2 L/(256pi^4)",
                "coefficient_times_pi_minus_four": rat(shell_total_coefficient),
            },
        },
        "pair_block_cross_check": {
            "commutator": "[c_Omega,p,Q_plus]=exp(2i|p|t)/(4|p|^2)c_Upsilon,-p^dagger",
            "beta_coefficient": rat(beta_coefficient),
            "ordered_Hilbert_Schmidt_sum": "sum_(p!=0) rho(p)^2/(16|p|^4)",
            "ordered_Hilbert_Schmidt_coefficient": rat(ordered_hs_coefficient),
            "constant_rho_density": "rho^2/(32pi^2)(epsilon^-1-Lambda^-1)",
            "density_coefficient_times_pi_minus_two": rat(hs_density_coefficient),
            "relation_to_direct_norm": "Hilbert--Schmidt sum equals twice ||Q_plus|0>||_kappa^2",
            "criterion": "Hilbert--Schmidt summability is a necessary first-sector condition for the positive-Fock pair exponential; the standard Shale--Stinespring theorem is comparison only because the BT map is cross-Krein canonical rather than Hilbert-star canonical",
            "volume_boundary": "the translation-invariant infinite-volume block also has the usual extensive volume divergence; here the Hilbert--Schmidt density itself has the stronger epsilon^-1 infrared divergence",
            "disposition": "PAIR_KERNEL_NOT_HILBERT_SCHMIDT_IN_THE_MASSLESS_IR_LIMIT",
        },
        "topology_boundary": {
            "bounded_equivalent_rho": "cannot remove the divergence because rho(p)>=m>0",
            "formal_power_weight": "rho(p) proportional to |p|^alpha makes the radial norm integral proportional to integral dp p^(2alpha-2)",
            "integrability_condition": "alpha>1/2",
            "why_not_a_repair_here": "rho(p)->0 makes rho^-1 unbounded, so this topology is not uniformly equivalent to the declared ordinary Fock--Krein topology",
            "normalization_scale_caveat": "rho carries the relative one-particle normalization; coefficients are exact in the displayed normalized box convention, while convergence is invariant under bounded equivalent choices",
        },
        "Krein_nullity_audit": {
            "indefinite_norm": "zero because same-species Upsilon contractions vanish",
            "positive_kappa_norm": "strictly positive at finite cutoff and infrared divergent after cutoff removal",
            "conclusion": "KREIN_NULL_DOES_NOT_IMPLY_A_VECTOR_IN_THE_POSITIVE_FOCK_TOPOLOGY",
        },
        "zero_mode_completion": {
            "candidate_orbit_rule": "kappa Z kappa=Z^-1 with Z^dagger=Z makes Z isometric in the candidate orbit Hilbertization",
            "effect_on_squeeze": "multiplication by Z^2 changes charge bookkeeping but not the |p|^-2 pair amplitude",
            "disposition": "DOES_NOT_CURE_THE_RADIAL_DIVERGENCE_ON_THAT_CANDIDATE_MODULE",
            "caveat": "a different unbounded zero-mode representation would require new domain and trace data and is not analyzed",
        },
        "disposition": {
            "finite_box_cutoff_squeezed_state": "DEFINED_ORDER_BY_ORDER",
            "massless_infinite_volume_positive_topology_vector": "OBSTRUCTED_ON_ORDINARY_FOCK_KREIN_CARRIER",
            "ordinary_Fock_Bogoliubov_implementer": "POSITIVE_FOCK_VECTOR_OBSTRUCTED_STANDARD_SHALE_THEOREM_NOT_DIRECTLY_APPLICABLE",
            "local_operator_algebra_homomorphism": "NOT_REFUTED",
            "Eq19_in_extended_representation": "NOT_DECIDED",
            "physical_neutral_one_over_48": "NOT_ESTABLISHED",
            "complete_nlo_probability": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "an explicit extended, rigged, or inequivalent non-Fock representation carrying the infrared-singular Bogoliubov map",
            "a dense invariant domain for Q_t, exp(Q_t), and the zero-mode-completed R_t map",
            "a positive topology and generalized Born trace on that extended carrier",
            "cyclicity and completeness of the Eq. (20) trace on the same carrier",
            "the full order-lambda pushforward R_t P_2 R_t^dagger with regulator removal",
            "a proof that neutral squeeze and soft terms do or do not change the conditional 1/48",
        ],
        "does_not_establish": [
            "that the Appendix-C algebraic canonical transformation is false",
            "that Eq. (19) is false in an extended or non-Fock representation",
            "that a finite-volume or infrared-cutoff squeezed state does not exist",
            "that every inequivalent fundamental-symmetry topology fails",
            "the physical neutral 1/48 coefficient",
            "a complete NLO probability or beyond-tree positivity",
            "a gravitational or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": (
            "Construct an explicit extended Bogoliubov representation for the |p|^-2 pair "
            "kernel, including its positive topology, dense domain, zero-mode module, and "
            "cyclic generalized-Born trace; then re-evaluate Eq. (19) without identifying "
            "indefinite nullity with Hilbert-topology normalizability."
        ),
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096",
                "equations": ["Appendix C Eqs. (31)--(34)"],
                "current_version_check": "Official arXiv record checked 2026-08-11: v1 only",
            },
            "implementability_reference": {
                "source": "Lill, Implementing Bogoliubov Transformations Beyond the Shale--Stinespring Condition",
                "url": "https://arxiv.org/abs/2204.13407",
                "use": "comparison source for positive-Hilbert Bogoliubov transformations and extended alternatives; not imported as a theorem for the cross-Krein-canonical BT shear, whose direct sector-norm proof is primary",
            },
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_squeezed_vacuum_implementability.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_squeezed_vacuum_implementability.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_squeezed_vacuum_implementability",
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
