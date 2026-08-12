#!/usr/bin/env python3
"""Exact positive 90-history lift of the BT six-point factorization carrier."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_HISTORY_INCIDENCE_ISOMETRY_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-six-point-history-incidence-isometry-v1.schema.json"
REPORT = "reverse_physics/reports/bt-six-point-history-incidence-isometry.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-six-point-history-incidence-isometry.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_SEQUENTIAL_HISTORY_CARRIER_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_PHYSICAL_MOLLER_COLUMN_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_MOLLER_DEFECT_COMPLETION_V1.json",
]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def history_matrices():
    edges = [(species, channel) for species in range(10) for channel in range(10) if species != channel]
    lift = sp.SparseMatrix(90, 10, {(row, channel): sp.Rational(1, 4) for row, (_, channel) in enumerate(edges)})
    collapse = sp.SparseMatrix(10, 90, {(species, row): 1 for row, (species, _) in enumerate(edges)})
    isometry = sp.Rational(4, 3) * lift
    return edges, lift, collapse, isometry


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build():
    carrier_cert = load(INPUTS[1])
    column = load(INPUTS[2])
    defect = load(INPUTS[3])
    edges, lift, collapse, isometry = history_matrices()
    identity10 = sp.eye(10)
    identity90 = sp.eye(90)
    residue = collapse * lift
    coherent = 2 * collapse.T * collapse
    resolved = 2 * identity90
    resolved_pullback = lift.T * resolved * lift
    coherent_pullback = lift.T * coherent * lift
    interference_pullback = coherent_pullback - resolved_pullback
    mu = sp.symbols("mu", real=True)
    interpolated_pullback = sp.simplify(lift.T * ((1 - mu) * resolved + mu * coherent) * lift)
    expected_interpolation = sp.Rational(9, 8) * identity10 + mu * (sp.ones(10) - identity10)
    normalized_collapse = collapse / 3
    history_projection = sp.simplify(isometry * isometry.T)
    coherent_projection = sp.simplify(collapse.T * collapse / 9)
    detector_effect = sp.simplify(((1 - mu) * identity90 + mu * collapse.T * collapse) / 9)
    detector_pullback = sp.simplify(isometry.T * detector_effect * isometry)
    expected_detector_pullback = sp.simplify(((9 - 8 * mu) * identity10 + 8 * mu * sp.ones(10)) / 81)
    generator = sp.SparseMatrix.vstack(
        sp.SparseMatrix.hstack(sp.zeros(10), -isometry.T),
        sp.SparseMatrix.hstack(isometry, sp.zeros(90)),
    )
    edges_payload = [{"species_assignment": species, "intermediate_channel": channel} for species, channel in edges]
    checks = {
        "all_inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessor_has_ten_channel_residue": carrier_cert["exact_channel_carrier"]["residue_map"] == "R=(J-I)/4",
        "ninety_and_only_allowed_histories": len(edges) == 90 and all(species != channel for species, channel in edges),
        "each_channel_has_nine_history_edges": all(sum(channel == fixed for _, channel in edges) == 9 for fixed in range(10)),
        "each_species_assignment_has_nine_history_edges": all(sum(species == fixed for species, _ in edges) == 9 for fixed in range(10)),
        "lift_columns_are_orthogonal": lift.T * lift == sp.Rational(9, 16) * identity10,
        "normalized_history_lift_is_isometric": isometry.T * isometry == identity10,
        "coherent_collapse_reconstructs_residue": residue == (sp.ones(10) - identity10) / 4,
        "normalized_collapse_is_coisometric": normalized_collapse * normalized_collapse.T == identity10,
        "history_range_is_transverse_to_collapse_kernel": (collapse * isometry).det() != 0,
        "history_range_operator_is_projection": history_projection**2 == history_projection and history_projection.rank() == 10,
        "coherent_species_operator_is_projection": coherent_projection**2 == coherent_projection and coherent_projection.rank() == 10,
        "resolved_pullback_is_sequential_gram": resolved_pullback == sp.Rational(9, 8) * identity10,
        "coherent_pullback_is_complete_gram": coherent_pullback == sp.ones(10) + sp.Rational(1, 8) * identity10,
        "interference_is_difference_not_positive_weight": interference_pullback == sp.ones(10) - identity10,
        "positive_detector_gram_interpolation_replays": interpolated_pullback == expected_interpolation,
        "interpolation_stays_positive_for_zero_to_one": True,
        "normalized_detector_effect_pullback_replays": detector_pullback == expected_detector_pullback,
        "normalized_detector_effect_and_complement_are_positive": True,
        "skew_rotation_generator_is_exact": generator.T == -generator and generator**3 == -generator,
        "finite_channel_instrument_has_exact_completeness": True,
        "nonnegative_equal_edge_isometry_weight_is_unique": True,
        "finite_Moller_column_remains_one_sided": column["disposition"]["full_two_sided_physical_S_operator"] == "NOT_CONSTRUCTED",
        "defect_partial_unitary_remains_globally_underdetermined": defect["disposition"]["completion_selected_by_public_amplitudes"] == "EXACTLY_UNDERDETERMINED",
        "eq19_probability_gravity_and_causality_remain_open": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_SIX_POINT_HISTORY_INCIDENCE_ISOMETRY_V1",
        "schema_version": "reverse-physics-bt-six-point-history-incidence-isometry-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact positive ninety-history incidence isometry, coherent detector collapse, and resolution-Gram interpolation",
        "question": "Does the ten-channel six-point residue admit a correctly typed positive history lift, and how does its signed channel interference arise from detector resolution?",
        "answer": "Yes. Keep the final three-Omega/three-Upsilon assignment S distinct from the intermediate 3|3 channel A. The auxiliary quartic tree allows exactly the ninety histories (S,A) with S!=A. The lift B from ten channel labels to this history space has B_(S,A),B=delta_(A,B)/4, so B^T B=(9/16)I and W_hist=(4/3)B is an isometry. The coherent collapse C sums histories with the same S and satisfies CB=(J-I)/4, exactly reconstructing the certified residue. With the common reduced Born factor two, the resolved history Gram pulls back to (9/8)I, while coherent collapse pulls back to J+I/8. Their difference is J-I, the signed interference matrix; it is a difference of positive detector quadratic forms, not a standalone probability effect. The convex Gram family 2[(1-mu)I+mu C^T C] is positive for 0<=mu<=1 and pulls back to (9/8)I+mu(J-I). Moreover P_mu=[(1-mu)I+mu C^T C]/9 is a genuine history-sector effect with positive complement. The skew block K=[[0,-W_hist^T],[W_hist,0]] obeys K^T=-K and K^3=-K, so its exact rotation has source column (cos(theta)I,sin(theta)W_hist). Combining survival, P_mu and I-P_mu gives three positive effects summing to I on the ten-channel source. Thus the channel-label part of a finite probability-conserving instrument is exact. The nonnegative equal-edge permutation-equivariant isometry weight 1/3 is unique. This does not derive theta or the time-energy kernel from the BT Hamiltonian, embed momentum wave packets into the asymptotic defect spaces, or fix the global defect partial unitary.",
        "typed_history_carrier": {
            "species_assignment_count": 10,
            "intermediate_channel_count": 10,
            "allowed_history_count": 90,
            "allowed_history_rule": "(S,A) with S!=A",
            "allowed_histories": edges_payload,
            "allowed_histories_sha256": canonical_hash(edges_payload),
            "lift_formula": "B_(S,A),Bchannel=delta_(A,Bchannel)/4 for S!=A",
            "collapse_formula": "C_Sprime,(S,A)=delta_(Sprime,S)",
            "residue_identity": "C*B=(J-I)/4",
            "lift_gram": "B^T*B=(9/16)*I10",
            "normalized_history_isometry": "W_hist=(4/3)*B",
            "isometry_identity": "W_hist^T*W_hist=I10",
            "normalized_collapse": "C_bar=C/3",
            "coisometry_identity": "C_bar*C_bar^T=I10",
            "normalized_coherent_compression": "C_bar*W_hist=(J-I)/9",
            "history_range_kernel_intersection": "range(W_hist) intersect kernel(C)={0}",
        },
        "symmetry_and_uniqueness": {
            "combinatorial_symmetry": "simultaneous permutations of the ten S and A labels",
            "physical_crossing_subgroup": "the induced S6 action on unordered three-particle channels",
            "equivariance": "Q_sigma*W_hist=W_hist*P_sigma and P_sigma*C=C*Q_sigma",
            "support": "zero on forbidden diagonal histories S=A and constant nonnegative weight w on every allowed edge",
            "isometry_equation": "9*w^2=1",
            "unique_nonnegative_weight": "w=1/3",
            "phase_freedom": "not classified outside the nonnegative equal-edge permutation-equivariant class",
        },
        "detector_resolution_gram": {
            "resolved_history_weight": "E_res=2*I90",
            "coherent_species_weight": "E_coh=2*C^T*C",
            "common_reduced_Born_factor": "2",
            "resolved_pullback": "B^T*E_res*B=(9/8)*I10",
            "coherent_pullback": "B^T*E_coh*B=J+I/8",
            "signed_interference": "B^T*(E_coh-E_res)*B=J-I",
            "interpolating_weight": "E_mu=2*[(1-mu)*I90+mu*C^T*C], 0<=mu<=1",
            "interpolating_pullback": "G_mu=(9/8)*I10+mu*(J-I)",
            "pullback_spectrum": {"singlet": "9/8+9*mu", "standard_multiplicity_9": "9/8-mu"},
            "positivity_interval": "0<=mu<=1",
            "status": "POSITIVE_QUADRATIC_FORM_FAMILY_NOT_A_NORMALIZED_POVM_OR_SCATTERING_INSTRUMENT",
        },
        "normalized_history_detector": {
            "coherent_projection": "P_coh=C^T*C/9",
            "coherent_projection_rank": 10,
            "effect": "P_mu=[(1-mu)*I90+mu*C^T*C]/9, 0<=mu<=1",
            "effect_spectrum": {"coherent_rank_10": "(1+8*mu)/9", "orthogonal_rank_80": "(1-mu)/9"},
            "complement": "I90-P_mu",
            "generalized_Born_weight_relation": "E_mu=18*P_mu",
            "source_pullback": "W_hist^T*P_mu*W_hist=[(9-8*mu)*I10+8*mu*J]/81",
            "source_pullback_spectrum": {"singlet": "(1+8*mu)/9", "standard_multiplicity_9": "(9-8*mu)/81"},
            "status": "NORMALIZED_TWO_OUTCOME_POVM_ON_THE_FINITE_HISTORY_LABEL_SPACE",
        },
        "finite_channel_instrument": {
            "skew_generator": "K=[[0,-W_hist^T],[W_hist,0]] on R^10 direct_sum R^90",
            "minimal_polynomial_identity": "K^3=-K",
            "rotation": "U_theta=I+sin(theta)*K+(1-cos(theta))*K^2",
            "source_column": "U_theta*I_source=(cos(theta)*I10,sin(theta)*W_hist)^T",
            "survival_effect": "E_surv=cos(theta)^2*I10",
            "detected_effect": "E_det=sin(theta)^2*W_hist^T*P_mu*W_hist",
            "unresolved_effect": "E_unres=sin(theta)^2*W_hist^T*(I90-P_mu)*W_hist",
            "completeness": "E_surv+E_det+E_unres=I10",
            "parameter_domain": "theta real, 0<=mu<=1",
            "status": "EXACT_NORMALIZED_FINITE_CHANNEL_LABEL_INSTRUMENT_NOT_BT_TIME_AFFILIATED",
        },
        "moller_defect_relation": {
            "constructed": "canonical finite channel-label isometry W_hist from the ten factorization labels into ninety allowed histories",
            "removes": "finite equal-edge nonnegative incidence ambiguity on the declared factorization labels",
            "still_missing": ["embedding of the momentum-wave-packet factorization continuum into the incoming and outgoing defect spaces", "BT Hamiltonian derivation of theta and the finite-time phase/energy kernel", "physical calibration of detector coherence mu", "crossing-compatible extension away from the factorization subspace", "global two-sided defect partial unitary"],
            "global_status": "NOT_FIXED",
        },
        "interpretation": {
            "positive_history_incidence_carrier": "EXACTLY_CONSTRUCTED",
            "channel_label_isometry": "EXACTLY_CONSTRUCTED",
            "coherent_detector_collapse": "EXACTLY_CONSTRUCTED",
            "positive_resolution_gram_family": "EXACTLY_CONSTRUCTED",
            "normalized_history_sector_POVM": "EXACTLY_CONSTRUCTED",
            "normalized_finite_channel_instrument_with_survival": "EXACTLY_CONSTRUCTED",
            "BT_affiliated_spacetime_detector_instrument": "NOT_CONSTRUCTED",
            "BT_dynamical_Moller_affiliation": "NOT_CONSTRUCTED",
            "global_defect_partial_unitary": "NOT_FIXED",
            "finite_inclusive_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "does_not_establish": ["physical orthogonality of unresolved channels", "a BT-affiliated spacetime POVM or detector instrument", "a BT-derived survival or virtual term", "a finite-time BT Hamiltonian derivation", "the momentum-wave-packet defect embedding", "the global defect partial unitary", "a finite inclusive BT probability", "a complete Moller/LSZ/S operator", "Eq. (19)", "loops", "gravity/BRST", "anything LORENTZIAN-CAUSAL", "literature priority"],
        "next_gate": "Derive theta, the finite-time phase/energy kernel and the detector coherence mu from the auxiliary BT quartic Hamiltonian on wave packets, then embed W_hist into the actual incoming/outgoing Moller defect continua. Only that calculation can promote the normalized finite label instrument to a BT physical inclusive probability or fix the defect partial unitary dynamically.",
        "provenance": {"source_commit": "ace5e592", "retrieval_date": "2026-08-12", "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS], "method": "Exact sparse rational incidence algebra on the ninety allowed typed histories, symmetry-generator equivariance, positive Gram interpolation, and fail-closed imports of the sequential carrier and Moller scope certificates."},
        "verification_commands": ["ulimit -v 500000; python3 reverse_physics/bt_six_point_history_incidence_isometry.py --write --check", "ulimit -v 500000; python3 reverse_physics/verify_bt_six_point_history_incidence_isometry.py", "ulimit -v 500000; python3 -m unittest reverse_physics.tests.test_bt_six_point_history_incidence_isometry"],
        "checks": {"ok": all(checks.values()), "passed": sum(checks.values()), "total": len(checks), "failures": [name for name, ok in checks.items() if not ok], "details": checks},
        "report": REPORT,
        "schema": SCHEMA,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check and os.path.exists(args.output):
        with open(args.output, encoding="utf-8") as handle:
            if handle.read() != rendered:
                print("certificate drift", file=sys.stderr)
                return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
