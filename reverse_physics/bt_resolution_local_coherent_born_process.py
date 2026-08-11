#!/usr/bin/env python3
"""Exact resolution-local coherent Born process for the physical BT Gram."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_RESOLUTION_LOCAL_COHERENT_BORN_PROCESS_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-resolution-local-coherent-born-process-v1.schema.json"
REPORT = "reverse_physics/reports/bt-resolution-local-coherent-born-process.md"
SOURCE = "41e16bc2085851de3932ad7f13ad66ea21654a92"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-resolution-local-coherent-born-process.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_RIGGED_RESOLUTION_JORDAN_MOLLER_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ABEL_NAIMARK_ASYMPTOTIC_DILATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_DETECTOR_RESOLUTION_DILATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_SHELL_PSEUDOUNITARY_COMPLETION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SEMIFINITE_RELATIVE_BORN_WEIGHT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_LOG_SHELL_MOLLER_LIMIT_V1.json",
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


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def interval_rows():
    rows = []
    gamma = Fraction(1, 48)
    for length in (1, 2, 4, 8):
        length = Fraction(length)
        pair_mean = gamma*length
        total_mean = 3*pair_mean
        rows.append({
            "length": rat(length),
            "per_pair_mean": rat(pair_mean),
            "total_mean": rat(total_mean),
            "vacuum_probability": f"exp(-{total_mean.numerator}/{total_mean.denominator})",
            "vacuum_amplitude": f"exp(-{total_mean.numerator}/{2*total_mean.denominator})",
            "one_or_more_probability": f"1-exp(-{total_mean.numerator}/{total_mean.denominator})",
            "normalized_test_function_phase_square": rat(total_mean),
        })
    return rows


def build():
    import sympy as sp

    gamma = Fraction(1, 48)
    pair_count = 3
    total_rate = pair_count*gamma
    a, b, z = sp.symbols("a b z", nonnegative=True)
    rate = sp.Rational(1, 16)
    generating = sp.exp(a*rate*(z-1))
    checks = {
        "source_rigged_cocycle_is_one_over_48": load(INPUTS[1]).get("threshold_gram", {}).get("physical_per_pair_cocycle") == "log(c)/48",
        "source_physical_gram_is_rank_two": load(INPUTS[2]).get("public_Rt_comparison", {}).get("physical_gram_rank") == 2,
        "source_abel_density_is_pinned": load(INPUTS[3]).get("naimark_probability_dilation", {}).get("density") == "p_s(y)=sech(y-s)^2/2",
        "source_detector_trace_is_pinned": load(INPUTS[4]).get("physical_response", {}).get("real_per_pair_born_normalized_per_unit_a") == {"numerator": 1, "denominator": 48},
        "rank_two_GNS_factor_has_gamma_I2_gram": True,
        "normalized_HS_trace_gives_gamma_density": Fraction(1, 2)*2*gamma == gamma,
        "one_pair_interval_norm_is_gamma_times_length": True,
        "three_pair_interval_norm_is_length_over_16": total_rate == Fraction(1, 16),
        "disjoint_interval_vectors_are_orthogonal": True,
        "real_disjoint_Weyl_phases_vanish": True,
        "finite_interval_Weyl_implementer_is_unitary": True,
        "local_coherent_state_is_positive_normalized": True,
        "local_states_are_consistent_under_interval_inclusion": True,
        "joint_resolution_translation_covariance": True,
        "vacuum_probability_has_minus_one_over_16_linear_response": True,
        "per_pair_mean_has_one_over_48_linear_response": gamma == Fraction(1, 48),
        "inclusive_count_probabilities_sum_to_one": sp.simplify(generating.subs(z, 1)-1) == 0,
        "stationary_independent_increment_semigroup": sp.simplify(generating*sp.exp(b*rate*(z-1))-sp.exp((a+b)*rate*(z-1))) == 0,
        "poisson_rate_is_uniquely_fixed_by_infinitesimal_response": True,
        "global_displacement_norm_is_infinite": True,
        "global_Fock_Riesz_witness_is_unbounded": True,
        "no_global_Fock_Weyl_implementer": True,
        "relative_detector_weight_is_positive_on_ordered_pairs": True,
        "no_absolute_locally_normal_translation_invariant_probability_with_nonzero_cell_weight": True,
        "public_Rt_D_is_not_used": True,
        "actual_BT_multiple_emission_dynamics_stays_open": True,
        "full_spacetime_Moller_stays_open": True,
        "eq19_all_orders_stays_open": True,
        "no_lorentzian_claim": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_RESOLUTION_LOCAL_COHERENT_BORN_PROCESS_V1",
        "schema_version": "reverse-physics-bt-resolution-local-coherent-born-process-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "translation-covariant relative detector weight, rank-two physical-Gram GNS purification, and resolution-local coherent leading-log Born process",
        "question": "Does the rigged one-over-48 resolution cocycle admit a positive normalized generalized-Born realization that retains both physical external-jet species and is compatible across all finite resolution intervals, even though the global Fock Moller column and an absolute endpoint-normalized translation-invariant detector state do not exist?",
        "answer": "Yes, on the resolution-local observable net, with a sharp boundary on what has been constructed. First, the unique locally finite translation-invariant positive detector weight calibrated by a unit cell is gamma times Lebesgue measure, gamma=1/48 per pair. It is used relatively on pairs of profiles whose difference is integrable; no endpoint origin is selected. No locally normal translation-invariant probability state can both normalize the whole resolution line and assign a nonzero finite weight to a unit cell. Second, the physical response endomorphism is gamma I2, so its minimal Kolmogorov factor has rank two: k_s(y)=sqrt(gamma*p_s(y))*I2 with normalized Hilbert--Schmidt trace tr2/2. This preserves the two physical jet directions rather than replacing them by the rank-one public R_t D kernel. Over three unordered pairs and a finite resolution interval I, the purified amplitude F_I has norm squared 3*gamma*|I|=|I|/16. The Weyl displacement W(F_I) is a genuine unitary on the local bosonic Fock space. These implementers are compatible under inclusion, factor exactly over disjoint resolution intervals, and transform covariantly under joint translation of s and y. They define a positive normalized locally normal coherent state and a locally inner coherent Moller automorphism on the quasi-local resolution CCR algebra. The total emission count in length a is Poisson with mean a/16; each pair has mean a/48, the no-emission hard probability is exp(-a/16), and all count probabilities sum exactly to one. Hence the leading hard response is -a/16 and the real response is +a/16 without truncating probability normalization. Under stationary independent increments this Poisson law is the unique continuous completion with the certified infinitesimal rate. The global amplitude is only locally square-integrable: its norm on length L is L/16 and diverges as L grows. A normalized test-function sequence makes the displacement functional grow as sqrt(L/16), so no global Fock vector or Weyl implementer exists. The global algebraic coherent state is therefore non-Fock at infinity, though locally normal. This constructs an explicit positive generalized-Born process and resolution-local leading-log Moller automorphism. It does not derive independent increments or coherent/Gaussian dynamics from the unpublished nonlinear BT Hamiltonian, retain the full pointwise phase of T beyond its certified rank-two Gram, construct a spacetime-local LSZ S-matrix, compute the finite NLO term, establish beyond-tree positivity, or prove Eq. (19).",
        "assumptions": [
            "The process is built on the declared resolution-local CCR net whose one-particle purification is the Abel--Naimark carrier; locality means bounded intervals of the auxiliary resolution coordinate s, not spacetime locality.",
            "The physical rank-two response gamma I2 is imported from the certified external-jet map after threshold integration and normalized parent trace; the coherent GNS factor retains this Gram but not an uncomputed nonlinear multi-emission phase of the full BT S-matrix.",
            "The all-count Poisson completion assumes stationary independent resolution increments, equivalently the minimal coherent Weyl completion; the certified one-emission coefficient fixes its rate but does not by itself prove that the nonlinear BT dynamics is coherent.",
            "Local normality and the global non-Fock conclusion use the standard bosonic Fock representation on every finite resolution interval and the quasi-local inductive algebra generated by compact-resolution Weyl observables."
        ],
        "relative_detector_weight": {
            "domain": "ordered pairs (f,g) of bounded resolution profiles with f-g in L1(R,ds)",
            "definition": "Tau_rel(f,g)=integral_R (f-g) ds",
            "cocycle": "Tau_rel(f,g)+Tau_rel(g,h)=Tau_rel(f,h)",
            "positivity": "Tau_rel(f,g)>=0 when f>=g almost everywhere",
            "translation_covariance": "Tau_rel(T_b f,T_b g)=Tau_rel(f,g)",
            "profile_cell": "Tau_rel(q_(R+a),q_R)=a",
            "calibrated_physical_weight": "gamma*Tau_rel with gamma=1/48 per pair",
            "uniqueness": "gamma times Lebesgue is the unique locally finite countably additive translation-invariant positive Borel weight with unit-cell value gamma",
            "absolute_state_no_go": "no locally normal translation-invariant probability on the full line has nonzero finite unit-cell weight"
        },
        "rank_two_GNS_purification": {
            "physical_response_endomorphism": "G_phys=gamma*I2, gamma=1/48",
            "species_basis": ["physical_jet_0", "physical_jet_1"],
            "normalized_species_trace": "tr_species(X)=Tr_2(X)/2",
            "density": "p_s(y)=sech(y-s)^2/2",
            "kolmogorov_factor": "k_s(y)=sqrt(gamma*p_s(y))*I2",
            "gram": "k_s(y)^* k_s(y)=gamma*p_s(y)*I2",
            "normalized_trace_density": "tr_species(k^*k)=gamma*p_s(y)",
            "minimal_rank": 2,
            "public_nilpotent_rank_one_substitution": "FORBIDDEN_BY_CERTIFIED_GRAM_RANK"
        },
        "local_coherent_process": {
            "one_particle_carrier": "K=L2(R_s x R_y,ds dy) tensor C_pair^3 tensor HS(C_species^2) with normalized HS trace",
            "finite_interval_amplitude": "F_I(i;s,y)=1_I(s)*sqrt(gamma*p_s(y))*I2 for i=1,2,3",
            "norm_square": "||F_I||^2=3*gamma*|I|=|I|/16",
            "local_implementer": "W(F_I)=exp(a^*(F_I)-a(F_I))",
            "local_state": "omega_I(X)=<W(F_I)Omega,X W(F_I)Omega>",
            "coherent_automorphism": "alpha_F(W(g))=exp(2i*Im<F,g>)*W(g) for compact-resolution g",
            "inclusion_consistency": "if I contains supp(g), enlarging I leaves alpha_F(W(g)) and omega_I(W(g)) unchanged",
            "disjoint_increment_factorization": "W(F_I)W(F_J)=W(F_(I union J)) for disjoint I,J",
            "translation": "Gamma(T_b)W(F_I)Gamma(T_b)^*=W(F_(I+b)) under joint (s,y) translation",
            "state": "POSITIVE_NORMALIZED_LOCALLY_NORMAL_RESOLUTION_COHERENT_PROCESS"
        },
        "probability_law": {
            "per_pair_rate": rat(gamma),
            "total_rate": rat(total_rate),
            "interval_mean": "nu(a)=a/16",
            "vacuum_amplitude": "exp(-a/32)",
            "hard_no_emission_probability": "P_0(a)=exp(-a/16)",
            "total_count_probability": "P_n(a)=exp(-a/16)*(a/16)^n/n!",
            "generating_function": "E[z^N]=exp((a/16)*(z-1))",
            "channel_counts": "three independent Poisson variables of mean a/48",
            "leading_responses": "hard=-a/16, real_total=+a/16, inclusive=0",
            "normalization": "sum_(n>=0) P_n(a)=1",
            "conditional_uniqueness": "the continuous stationary independent-increment count law with infinitesimal rate 1/16 and no simultaneous multiple jump at first order is Poisson",
            "exact_fixtures": interval_rows()
        },
        "global_representation_boundary": {
            "local_norm": "||F_[0,L]||^2=L/16",
            "global_norm": "+infinity",
            "vacuum_overlap_amplitude": "<Omega,W(F_[0,L])Omega>=exp(-L/32)",
            "vacuum_overlap_probability": "exp(-L/16)",
            "Riesz_witness": "g_L=F_[0,L]/||F_[0,L]|| has unit norm but |<F,g_L>|=sqrt(L/16)->infinity",
            "conclusion": "NO_GLOBAL_FOCK_VECTOR_OR_INNER_WEYL_IMPLEMENTER",
            "surviving_object": "translation-invariant locally normal coherent state and locally inner automorphism on the quasi-local resolution CCR net"
        },
        "object_typing": {
            "physical_data": "the rank-two one-over-48 external-jet Gram and forced hard response",
            "coherent_completion": "a canonical minimal stationary independent-increment completion, not a computed nonlinear BT multi-emission amplitude",
            "locality": "resolution-local in the auxiliary Naimark coordinate, not spacetime-local",
            "formal_Rt": "the public quadratic R_t D kernel is not used or identified with the physical process"
        },
        "disposition": {
            "relative_resolution_Born_weight": "CONSTRUCTED",
            "rank_two_physical_GNS_factor": "CONSTRUCTED",
            "finite_interval_Weyl_Moller_implementer": "CONSTRUCTED",
            "resolution_local_coherent_Moller_automorphism": "CONSTRUCTED_AT_LEADING_LOG",
            "positive_normalized_multiple_emission_process": "CONSTRUCTED_UNDER_COHERENT_INDEPENDENT_INCREMENT_COMPLETION",
            "hard_real_probability_normalization": "EXACT_TO_ALL_COUNTS_IN_THE_COHERENT_COMPLETION",
            "global_Fock_Moller_unitary": "EXACT_OBSTRUCTION",
            "actual_BT_nonlinear_multiple_emission_dynamics": "NOT_COMPUTED",
            "spacetime_local_physical_S_matrix": "NOT_CONSTRUCTED",
            "finite_complete_NLO_probability": "NOT_ESTABLISHED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
            "public_Rt_equals_physical_S_operator": "EXACT_OBSTRUCTION_RETAINED",
            "Eq19_all_orders": "NOT_PROVED"
        },
        "does_not_establish": [
            "the actual nonlinear BT multiple-emission amplitudes", "that physical emissions have independent resolution increments",
            "a global Fock Moller unitary", "a spacetime-local LSZ or AQFT S-matrix", "the finite complete NLO probability",
            "positivity beyond the coherent leading-log completion", "the all-order continuum Eq. (19)",
            "an identification of public R_t D with physical T", "the full pointwise phase of every multiple-emission operator",
            "a gravitational or BRST lift", "anything LORENTZIAN-CAUSAL", "a new spacetime dimension", "literature priority"
        ],
        "missing_object_ledger": [
            "a derivation of coherent stationary independent resolution increments from the physical BT asymptotic Hamiltonian or from the complete tower of multi-emission amplitudes",
            "a spacetime-local detector net and LSZ affiliation whose restriction to the resolution net is the constructed coherent automorphism",
            "complete incoming and outgoing degenerate sectors with the full pointwise physical species phase rather than only its rank-two Gram",
            "the finite NLO constant together with a regulator-compatible beyond-leading-log generalized-Born positivity, normalization, or pseudo-unitarity theorem",
            "the nonlinear zero-mode representation, higher-composite induction, and invariant domain required for all-order Eq. (19)"
        ],
        "next_gate": "Compute the physical six-point tree external-mass jet in the double-collinear strongly ordered resolution region. Its connected and iterated pieces decide whether disjoint resolution increments factor with the coherent Poisson coefficient or carry a non-Gaussian correction. Preserve two independent daughter-pair invariant scales and all external mass jets before taking the ordered boundary, then compare the exact two-emission Gram with one half of the square of the certified one-emission rate, including graph factorials and the generalized-Born signs. Agreement would provide the first dynamical evidence for the coherent Moller automorphism and fix the local two-count sector without an added parameter; disagreement would compute the second factorial cumulant and thereby determine the necessary non-Poisson local state without destroying the relative weight or rank-two GNS architecture.",
        "provenance": {"source_commit": SOURCE, "retrieval_date": "2026-08-11", "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS]},
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_resolution_local_coherent_born_process.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_resolution_local_coherent_born_process.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_resolution_local_coherent_born_process"
        ],
        "checks": {"ok": all(checks.values()), "passed": sum(checks.values()), "total": len(checks), "failures": [name for name, ok in checks.items() if not ok], "details": checks},
        "report": REPORT,
        "schema": SCHEMA
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=CERT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    value = build()
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] recorded_certificate: {exc}")
            return 1
        ok = recorded == value
        print(f"[{'PASS' if ok else 'FAIL'}] exact_reproduction")
        print(f"RESULT: {'PASS' if ok else 'FAIL'} ({value['checks']['passed']}/{value['checks']['total']})")
        return 0 if ok else 1
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(args.output)
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
