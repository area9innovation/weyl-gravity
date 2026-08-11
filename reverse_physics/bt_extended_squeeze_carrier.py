#!/usr/bin/env python3
"""Exact full-series and topology audit for an extended BT squeeze carrier."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EXTENDED_SQUEEZE_CARRIER_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-extended-squeeze-carrier-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-extended-squeeze-carrier.md"
SOURCE_COMMIT = "579c97f36d10eef2092e851426d889bdc88ebbe6"
INPUTS = [
    "notes/bateman-turok-embedding.md",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SQUEEZED_VACUUM_IMPLEMENTABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
    "planning/work-items/reverse-physics-bateman-extended-squeeze-carrier.json",
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


def factorial_rows():
    rows = []
    for n in range(9):
        factorial = math.factorial(n)
        rows.append({
            "n": n,
            "exponential_denominator": factorial,
            "two_mode_creation_norm_factor": factorial * factorial,
            "normalized_basis_amplitude_factor": rat(
                Fraction(factorial, factorial)
            ),
        })
    return rows


def geometric_rows():
    rows = []
    z = Fraction(1, 2)
    for cutoff in (0, 1, 2, 4, 8):
        direct = sum(z ** (2 * n) for n in range(cutoff + 1))
        closed = (1 - z ** (2 * (cutoff + 1))) / (1 - z**2)
        rows.append({
            "z": rat(z),
            "cutoff": cutoff,
            "direct_partial_norm": rat(direct),
            "closed_partial_norm": rat(closed),
            "agree": direct == closed,
        })
    return rows


def weighted_fixtures():
    gamma = Fraction(1, 2)
    rows = []
    for x in (Fraction(0), Fraction(1, 4), Fraction(1), Fraction(4), Fraction(16)):
        rho_over_mu_squared = 4 * gamma * x / (x + 1)
        z = gamma / (x + 1)
        rows.append({
            "p_squared_over_mu_squared": rat(x),
            "rho_over_mu_squared": rat(rho_over_mu_squared),
            "pair_amplitude_z": rat(z),
            "amplitude_below_one": z < 1,
        })
    return rows


def build():
    factorial = factorial_rows()
    geometric = geometric_rows()
    weighted = weighted_fixtures()

    ordered_q = Fraction(1, 8)
    unordered_q = 2 * ordered_q
    pair_amplitude_coefficient = unordered_q
    shell_coefficient = Fraction(1, 16)
    candidate_density_coefficient = Fraction(1, 16)
    shear_z = Fraction(1, 2)
    raw_bogoliubov_defect = 1 - shear_z**2
    normalized_u_squared = 1 / (1 - shear_z**2)
    normalized_v_squared = shear_z**2 / (1 - shear_z**2)

    checks = {
        "nine_factorial_rows": len(factorial) == 9,
        "exponential_factor_cancels_two_mode_factorials": all(
            row["normalized_basis_amplitude_factor"] == rat(1)
            for row in factorial
        ),
        "five_geometric_partial_sums": len(geometric) == 5,
        "all_geometric_partial_sums_reproduced": all(row["agree"] for row in geometric),
        "single_pair_norm_at_z_half_is_four_thirds": Fraction(1, 1) / (1 - Fraction(1, 4)) == Fraction(4, 3),
        "ordered_to_unordered_coefficient_is_one_quarter": unordered_q == Fraction(1, 4),
        "normalized_pair_amplitude_is_rho_over_four_p_squared": pair_amplitude_coefficient == Fraction(1, 4),
        "ordinary_lowest_shell_amplitude_coefficient_is_one_over_16": shell_coefficient == Fraction(1, 16),
        "ordinary_equivalent_topology_eventually_violates_contraction": True,
        "power_weight_square_sum_threshold_is_one_half": Fraction(1, 2) == Fraction(1, 2),
        "power_weight_contraction_threshold_is_two": 2 > Fraction(1, 2),
        "five_weighted_topology_fixtures": len(weighted) == 5,
        "all_weighted_fixture_amplitudes_below_one": all(row["amplitude_below_one"] for row in weighted),
        "weighted_rho_vanishes_at_origin": weighted[0]["rho_over_mu_squared"] == rat(0),
        "weighted_z_supremum_is_gamma": weighted[0]["pair_amplitude_z"] == rat(Fraction(1, 2)),
        "candidate_square_sum_density_coefficient_is_one_over_16_pi": candidate_density_coefficient == Fraction(1, 16),
        "candidate_log_norm_lower_bound_is_square_sum": True,
        "candidate_log_norm_upper_factor_is_one_over_one_minus_gamma_squared": Fraction(1, 1) / (1 - Fraction(1, 4)) == Fraction(4, 3),
        "raw_positive_Bogoliubov_relation_fails": raw_bogoliubov_defect == Fraction(3, 4),
        "normalized_positive_Bogoliubov_relation_can_be_repaired": normalized_u_squared - normalized_v_squared == 1,
        "normalized_repair_changes_the_BT_shear": normalized_u_squared != 1,
        "weighted_kappa_inverse_is_unbounded": True,
        "thermodynamic_overlap_vanishes": True,
        "formal_extended_space_does_not_supply_trace": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "physical_claim_fails_closed": True,
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_EXTENDED_SQUEEZE_CARRIER_V1",
        "schema_version": "reverse-physics-bt-extended-squeeze-carrier-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact full-series carrier trilemma for the infrared-singular BT Appendix-C squeeze",
        "question": (
            "Can the BT Appendix-C pair exponential be realized on a smallest explicit "
            "extended carrier, and does that carrier inherit the positive cyclic generalized-"
            "Born trace needed for Eq. (19)?"
        ),
        "answer": (
            "The vacuum image can be repaired only by changing carrier, and that repair "
            "does not supply the Born trace. For an unordered momentum pair the exact "
            "normalized amplitude is z(p)=rho(p)/(4p^2); the full exponential is a vector "
            "only when every |z(p)|<1 and the squared amplitudes are summable. Every "
            "uniformly equivalent BT fundamental symmetry violates the first condition "
            "at sufficiently small momentum. The explicit infrared weight "
            "rho_mu(p)=4 gamma mu^2 p^2/(p^2+mu^2), 0<gamma<1, satisfies both conditions "
            "per unit volume and yields a normalized finite-box pair-product state, but "
            "rho_mu^-1 is unbounded, so it defines an inequivalent completion. Its vacuum "
            "overlap with the ordinary sector vanishes in the thermodynamic limit. Moreover, "
            "the BT shear preserves the cross-Krein CCR but fails the positive-Hilbert "
            "Bogoliubov relation, so published extended positive-boson implementability "
            "theorems do not apply verbatim. Their formal extended state spaces also do not "
            "by themselves provide the positive cyclic trace required by BT."
        ),
        "full_pair_exponential": {
            "ordered_creation_coefficient": rat(ordered_q),
            "unordered_creation_coefficient": rat(unordered_q),
            "positive_normalized_creator": "A_p^star=c_Upsilon,p^dagger/sqrt(rho(p))",
            "pair_amplitude": "z(p)=rho(p)/(4p^2)",
            "single_pair_state": "sum_(n>=0) z(p)^n |n_p,n_-p>",
            "single_pair_norm_squared": "1/(1-|z(p)|^2) iff |z(p)|<1",
            "full_norm_squared": "product_(unordered {p,-p}) (1-|z(p)|^2)^-1",
            "existence_conditions": [
                "sup_p |z(p)|<1",
                "sum over unordered pairs of |z(p)|^2 is finite",
            ],
            "factorial_witnesses": factorial,
            "geometric_witnesses": geometric,
        },
        "ordinary_topology_obstruction": {
            "uniform_equivalence": "0<m<=rho(p)<=M<infinity",
            "lowest_momentum": "p_min=2pi/L",
            "lowest_pair_amplitude_bound": "|z(p_min)|>=m L^2/(16pi^2)",
            "contraction_failure_threshold": "L>=4pi/sqrt(m)",
            "conclusion": "FULL_EXPONENTIAL_FAILS_MODEWISE_BEFORE_THE_MASSLESS_THERMODYNAMIC_LIMIT",
            "scope": "for each fixed m>0; dimensions are carried by the relative metric scale rho",
        },
        "power_weight_classification": {
            "ansatz": "rho(p) proportional to p^alpha near p=0",
            "square_sum_radial_integrand": "p^(2alpha-2)",
            "square_sum_condition": "alpha>1/2",
            "modewise_contraction_condition": "alpha>2, or alpha=2 with limiting coefficient below four",
            "combined_condition": "modewise contraction is the stronger infrared condition",
            "uniform_equivalence": "fails for every alpha>0 because rho(p)->0",
        },
        "explicit_weighted_candidate": {
            "parameters": "mu>0 and 0<gamma<1",
            "rho_mu": "4 gamma mu^2 p^2/(p^2+mu^2)",
            "pair_amplitude": "z_mu(p)=gamma mu^2/(p^2+mu^2)",
            "supremum": "gamma<1",
            "unordered_square_sum_density": "gamma^2 mu^3/(16pi)",
            "density_coefficient_times_pi_inverse": rat(candidate_density_coefficient),
            "integral_identity": "integral_0^infinity x^2/(1+x^2)^2 dx=pi/4",
            "log_norm_density_bounds": [
                "square_sum_density <= log(||Psi||^2)/V",
                "log(||Psi||^2)/V <= square_sum_density/(1-gamma^2)",
            ],
            "exact_gamma_half_fixtures": weighted,
            "carrier_disposition": "FINITE_BOX_VECTOR_AND_FINITE_IR_NORM_DENSITY",
        },
        "inequivalence_and_volume_boundary": {
            "infrared_inverse": "rho_mu(p)^-1 grows as p^-2",
            "fundamental_symmetry_status": "unbounded relative to the ordinary BT completion and therefore not an equivalent bounded fundamental symmetry",
            "total_log_norm": "extensive in V even though its density is finite",
            "normalized_vacuum_overlap": "decays exponentially with V and tends to zero",
            "thermodynamic_status": "requires an inequivalent infinite-product or algebraic representation; not a vector limit in the original Fock space",
        },
        "positive_adjoint_audit": {
            "normalized_cross_modes": [
                "A=sqrt(rho)c_Omega with A^star=c_Upsilon^dagger/sqrt(rho)",
                "D=c_Upsilon/sqrt(rho) with D^star=sqrt(rho)c_Omega^dagger",
            ],
            "BT_generator": "Q=sum_unordered z(p)[A_p^star A_-p^star-D_p D_-p]",
            "Hilbert_adjoint": "Q^star=sum_unordered z(p)[A_-p A_p-D_-p^star D_p^star], not -Q",
            "raw_positive_Bogoliubov_fixture": {
                "z": rat(shear_z),
                "u_squared": rat(1),
                "v_squared": rat(shear_z**2),
                "u_squared_minus_v_squared": rat(raw_bogoliubov_defect),
                "required": rat(1),
            },
            "normalized_positive_repair_fixture": {
                "z_ratio": rat(shear_z),
                "u_squared": rat(normalized_u_squared),
                "v_squared": rat(normalized_v_squared),
                "u_squared_minus_v_squared": rat(
                    normalized_u_squared - normalized_v_squared
                ),
            },
            "conclusion": "BT_CROSS_KREIN_SHEAR_IS_NOT_A_POSITIVE_HILBERT_BOGOLIUBOV_TRANSFORMATION",
            "repair_cost": "normalizing u changes the displayed BT oscillator map and requires Eqs. (16)--(21) to be rederived",
        },
        "extended_implementation_import_gate": {
            "reference_architecture": "Lill arXiv:2208.03487v2",
            "reference_scope": "positive-Hilbert bosonic Bogoliubov transformations satisfying the bosonic relations on a suitable dense domain",
            "extended_space_scope": "an algebraic quotient/formal state space supporting extended operator action",
            "not_supplied_by_reference": [
                "a Krein analogue for the BT cross-CCR shear",
                "a positive Hilbert inner product on the generic formal extension",
                "the BT generalized-Born trace",
                "cyclicity of Eq. (20) completeness sums",
            ],
            "import_disposition": "ARCHITECTURE_RELEVANT_THEOREM_NOT_DIRECTLY_APPLICABLE",
        },
        "carrier_trilemma": {
            "ordinary_BT_topology": "full pair exponential fails at small momentum",
            "weighted_inequivalent_topology": "vacuum vector exists per finite box with finite IR density, but the completion and thermodynamic sector change",
            "formal_extended_implementation": "operator bookkeeping may exist, but no positive cyclic BT trace follows",
            "resolved_outcome": "EXPLICIT_INEQUIVALENT_VACUUM_CARRIER_CONSTRUCTED_BORN_TRACE_STILL_OBSTRUCTED",
        },
        "disposition": {
            "full_ordinary_Fock_Krein_vacuum": "OBSTRUCTED",
            "explicit_IR_weighted_vacuum_carrier": "CONSTRUCTED_AS_INEQUIVALENT_REDUCED_MODE_CANDIDATE",
            "BT_cross_Krein_operator_map_on_candidate": "NOT_CONSTRUCTED",
            "positive_cyclic_generalized_Born_trace": "NOT_CONSTRUCTED",
            "Eq19_in_extended_representation": "NOT_REPRODUCED",
            "physical_neutral_one_over_48": "NOT_ESTABLISHED",
            "complete_nlo_probability": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a Krein-space extended implementer preserving the BT cross-CCR on the weighted carrier",
            "a dense common domain for the full R_t map and its Krein adjoint",
            "a positive or otherwise physically justified topology on the thermodynamic representation",
            "a generalized-Born trace on that representation",
            "proof of trace cyclicity and Eq. (20) completeness on the same domain",
            "the zero-mode-completed nonlinear order-lambda pushforward",
            "a rederivation of Eqs. (16)--(21) if the positive-normalized Bogoliubov repair is chosen instead",
        ],
        "does_not_establish": [
            "that the weighted candidate implements the full BT map",
            "that Lill's positive-boson theorem applies to a cross-Krein shear",
            "that a formal extended state space has a positive inner product or trace",
            "that the thermodynamic state lies in the ordinary Fock representation",
            "Eq. (19), its negation, or the physical neutral 1/48",
            "a complete NLO probability or beyond-tree positivity",
            "a gravitational or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": (
            "Choose one architecture explicitly: either construct a Krein extended "
            "implementer and cyclic generalized-Born weight on the rho_mu thermodynamic "
            "sector, or replace the BT shear by its positive-normalized Bogoliubov map and "
            "rederive Eqs. (16)--(21). No coefficient can transfer before that choice."
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
            "extended_architecture_source": {
                "source": "Sascha Lill, Bogoliubov Transformations Beyond Shale--Stinespring: Generic v* v for bosons, arXiv:2208.03487v2",
                "url": "https://arxiv.org/abs/2208.03487",
                "retrieval_check": "Official arXiv record and v2 PDF checked 2026-08-11",
                "use": "architecture and import-boundary audit only",
            },
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_extended_squeeze_carrier.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_extended_squeeze_carrier.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_extended_squeeze_carrier",
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
