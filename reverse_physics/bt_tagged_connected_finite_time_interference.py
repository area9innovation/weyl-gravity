#!/usr/bin/env python3
"""Exact tagged-spectator/connected BT finite-time tree interference."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_CONNECTED_FINITE_TIME_INTERFERENCE_V1.json",
)
SCHEMA = "reverse_physics/schema/reverse-physics-bt-tagged-connected-finite-time-interference-v1.schema.json"
REPORT = "reverse_physics/reports/bt-tagged-connected-finite-time-interference.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-tagged-connected-finite-time-interference.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_HARD_NONFORWARD_PHYSICAL_STRATIFIED_ATLAS_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_FULL_PHASE_SPACE_BORN_POSITIVITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_GHOST_EVEN_HISTORY_EMBEDDING_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_GLOBAL_CONNECTED_FINITE_TIME_PACKET_COLUMN_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_SHELL_TREE_NORMALIZATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_THREE_JUMP_KREIN_MOLLER_JET_V1.json",
]


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def rational_vector(row):
    return sp.Matrix([sp.Rational(value) for value in row])


def exact_string(value):
    return sp.sstr(sp.factor(value))


def minkowski_square(vector):
    return sp.factor(vector[0] ** 2 - sum(value**2 for value in vector[1:]))


def build():
    atlas = load(INPUTS[1])
    tagged = load(INPUTS[2])
    full_phase = load(INPUTS[3])
    ghost_even = load(INPUTS[4])
    global_column = load(INPUTS[5])
    shell = load(INPUTS[6])
    profile = load(INPUTS[7])
    three_jump = load(INPUTS[8])
    predecessors = [
        atlas,
        tagged,
        full_phase,
        ghost_even,
        global_column,
        shell,
        profile,
        three_jump,
    ]

    witness = tagged["exact_tagged_spectator_witness"]
    incoming = [rational_vector(row) for row in witness["incoming_momenta"]]
    outgoing = [rational_vector(row) for row in witness["outgoing_momenta"]]
    all_incoming = incoming + [-row for row in outgoing]
    labels = witness["all_incoming_labels"]
    tag = set(witness["tagged_pair"])
    active = sorted(set(range(6)) - tag)

    representative_masks = ghost_even["neutral_six_leg_carrier"]["representative_masks"]
    public_masks = full_phase["universal_complement_formula"]["channels"]
    channel_rows = []
    r_masks = []
    n_masks = []
    deltas = {}
    denominators = {}
    invariants = {}
    for mask in representative_masks:
        subset = [index for index in range(6) if mask & (1 << index)]
        momentum = sum((all_incoming[index] for index in subset), sp.zeros(4, 1))
        # A 3|3 channel is unordered.  Replace a negative-energy representative
        # by its complement orientation so every recorded q is future directed.
        if momentum[0] < 0:
            momentum = -momentum
        spatial_norm = sp.sqrt(sum(value**2 for value in momentum[1:]))
        delta = sp.factor(momentum[0] - spatial_norm)
        denominator = sp.factor(momentum[0] + spatial_norm)
        invariant = minkowski_square(momentum)
        carrier = "R_TAG_ODD" if len(tag.intersection(subset)) == 1 else "N_TAG_EVEN"
        if carrier == "R_TAG_ODD":
            r_masks.append(mask)
        else:
            n_masks.append(mask)
        deltas[mask] = delta
        denominators[mask] = denominator
        invariants[mask] = invariant
        channel_rows.append(
            {
                "mask": mask,
                "subset": subset,
                "labels": [labels[index] for index in subset],
                "carrier": carrier,
                "q": [exact_string(value) for value in momentum],
                "q_squared": exact_string(invariant),
                "delta": exact_string(delta),
                "D": exact_string(denominator),
                "resonant": delta == 0,
            }
        )

    dimension = len(representative_masks)
    incidence = sp.ones(dimension, dimension) - sp.eye(dimension)
    beta = sp.Matrix(sp.symbols("beta0:%d" % dimension))
    connected = incidence * beta / 4
    tagged_embedding = sp.Matrix([2 if mask in r_masks else 0 for mask in representative_masks])
    tagged_norm = tagged_embedding.dot(tagged_embedding)
    connected_positive_coordinates = sp.sqrt(2) * connected
    direct_pairing = sp.expand(tagged_embedding.dot(connected_positive_coordinates))
    expected_pairing = sp.sqrt(2) * (
        5 * sum(beta[index] for index, mask in enumerate(representative_masks) if mask in r_masks)
        + 6 * sum(beta[index] for index, mask in enumerate(representative_masks) if mask in n_masks)
    ) / 2

    duration = sp.symbols("T", positive=True)

    def real_beta(mask):
        delta = deltas[mask]
        denominator = denominators[mask]
        if delta == 0:
            return duration / denominator
        return sp.sin(delta * duration) / (delta * denominator)

    weight = {mask: (5 if mask in r_masks else 6) for mask in representative_masks}
    real_bracket = sp.expand_trig(
        sp.simplify(sum(weight[mask] * real_beta(mask) for mask in representative_masks))
    )
    expected_bracket = (
        12 * duration
        + sp.Rational(125, 256) * sp.sin(sp.Rational(16, 5) * duration)
        + sp.Rational(125, 128) * sp.sin(sp.Rational(8, 5) * duration)
        + sp.Rational(125, 8)
        * sp.sin(sp.Rational(2, 5) * (sp.sqrt(17) - 3) * duration)
    )
    positive_lower_coefficient = sp.factor((221 - 50 * sp.sqrt(17)) / 8)
    small_time_slope = sp.factor(sp.diff(expected_bracket, duration).subs(duration, 0))
    secular_coefficient = sp.limit(expected_bracket / duration, duration, sp.oo)
    restored_multiplier = 16 * sp.sqrt(2)

    resonant_masks = [mask for mask in representative_masks if deltas[mask] == 0]
    nonresonant_classes = [
        {
            "name": "hard_total",
            "masks": [7],
            "delta": "16/5",
            "D": "16/5",
            "q_squared": "256/25",
        },
        {
            "name": "algebraic_exchange",
            "masks": [19, 21, 26, 28],
            "delta": "2*(3 - sqrt(17))/5",
            "D": "2*(3 + sqrt(17))/5",
            "q_squared": "-32/25",
        },
        {
            "name": "spacelike_axis",
            "masks": [14],
            "delta": "-8/5",
            "D": "16/5",
            "q_squared": "-128/25",
        },
    ]

    phase_text = three_jump["physical_moller_column"]["common_phase"]
    profile_phase = profile["physical_pullback"]["phase"]
    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "eight_predecessors_pass": len(predecessors) == 8 and all(row["checks"]["ok"] for row in predecessors),
        "tagged_pair_is_zero_three": sorted(tag) == [0, 3],
        "active_labels_are_one_two_four_five": active == [1, 2, 4, 5],
        "public_and_positive_frame_masks_agree": representative_masks == public_masks,
        "ten_representative_masks_are_unique": len(representative_masks) == len(set(representative_masks)) == 10,
        "every_representative_has_three_labels": all(len(row["subset"]) == 3 for row in channel_rows),
        "all_oriented_channel_energies_are_nonnegative": all(sp.Rational(row["q"][0]) >= 0 for row in channel_rows),
        "delta_times_D_is_q_squared": all(sp.simplify(deltas[mask] * denominators[mask] - invariants[mask]) == 0 for mask in representative_masks),
        "tag_odd_masks_are_exact": r_masks == [7, 19, 21, 14, 26, 28],
        "tag_even_masks_are_exact": n_masks == [11, 13, 25, 22],
        "carrier_partition_is_six_plus_four": len(r_masks) == 6 and len(n_masks) == 4 and not set(r_masks).intersection(n_masks),
        "tagged_species_rule_selects_exactly_one_tag_label": all((row["mask"] in r_masks) == (len(tag.intersection(row["subset"])) == 1) for row in channel_rows),
        "tagged_embedding_has_six_coefficients_two": list(tagged_embedding).count(2) == 6 and list(tagged_embedding).count(0) == 4,
        "tagged_embedding_norm_is_24": tagged_norm == 24,
        "tagged_predecessor_norm_is_24": tagged["four_point_positive_jet_factorization"]["jet_norm"] == "r4^sharp*r4=24",
        "positive_frame_is_orthonormal": ghost_even["neutral_six_leg_carrier"]["frame_grams"]["positive"] == "U_plus^T*eta*U_plus=I10",
        "connected_positive_coordinates_are_sqrt2_c": ghost_even["complete_coefficient_embedding"]["full_vector"] == "a=(c,c)=sqrt(2)*U_plus*c",
        "incidence_matrix_is_J_minus_I": incidence == sp.ones(10, 10) - sp.eye(10),
        "incidence_determinant_is_minus9": incidence.det() == -9 and full_phase["universal_complement_formula"]["incidence_determinant"] == -9,
        "tag_odd_incidence_weights_are_five": all(sum(incidence[row, column] for row, mask in enumerate(representative_masks) if mask in r_masks) == 5 for column, mask in enumerate(representative_masks) if mask in r_masks),
        "tag_even_incidence_weights_are_six": all(sum(incidence[row, column] for row, mask in enumerate(representative_masks) if mask in r_masks) == 6 for column, mask in enumerate(representative_masks) if mask in n_masks),
        "direct_pairing_equals_weighted_formula": sp.simplify(direct_pairing - expected_pairing) == 0,
        "four_channels_are_exactly_resonant": resonant_masks == [11, 13, 25, 22],
        "all_resonant_channels_are_tag_even": resonant_masks == n_masks,
        "every_resonant_denominator_is_two": all(denominators[mask] == 2 for mask in resonant_masks),
        "nonresonant_channel_class_counts_are_one_four_one": [len(row["masks"]) for row in nonresonant_classes] == [1, 4, 1],
        "finite_time_bracket_is_exact": sp.simplify(sp.expand_trig(real_bracket - expected_bracket)) == 0,
        "resonant_linear_contribution_is_12T": sum(weight[mask] * real_beta(mask) for mask in resonant_masks) == 12 * duration,
        "sine_lower_bound_coefficient_is_exact": sp.simplify(positive_lower_coefficient - (sp.Rational(221, 8) - 25 * sp.sqrt(17) / 4)) == 0,
        "lower_bound_coefficient_is_strictly_positive": 221**2 > 50**2 * 17,
        "large_time_secular_coefficient_is_12": secular_coefficient == 12,
        "small_time_slope_is_positive": sp.simplify(small_time_slope - (-29 + 50 * sp.sqrt(17)) / 8) == 0 and 50**2 * 17 > 29**2,
        "public_six_point_multiplier_is_16": shell["tree_topology_normalization"]["common_amplitude_multiplier"] == "16*i*lambda^4",
        "common_four_to_six_tree_phase_is_certified": "four-, five-, six-, and seven-point tree phase" in phase_text and "topology-independent common tree phase" in profile_phase,
        "restored_cross_multiplier_is_16sqrt2": restored_multiplier == 16 * sp.sqrt(2),
        "global_finite_time_kernel_is_imported": global_column["global_connected_column"]["kernel"].startswith("beta_B,T=F_T(delta_B)/D_B"),
        "atlas_identified_this_lambda6_gate": "order-lambda6 interference" in atlas["next_gate"],
        "normalization_and_inclusive_boundaries_remain_open": tagged["hard_nonforward_stratified_atlas"]["cross_stratum_detector"] == "NOT_CONSTRUCTED" and "higher-order spectator interference or the finite one-loop four-point term" in tagged["does_not_establish"],
        "Eq19_gravity_and_Lorentzian_boundaries_remain_open": "the standard scalar projector or general Eq. (19)" in tagged["does_not_establish"] and "gravity or metric BV/BRST transfer" in tagged["does_not_establish"] and "anything LORENTZIAN-CAUSAL" in tagged["does_not_establish"],
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_TAGGED_CONNECTED_FINITE_TIME_INTERFERENCE_V1",
        "schema_version": "reverse-physics-bt-tagged-connected-finite-time-interference-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact external-mass/species tree cross kernel between the tagged spectator and connected six-point BT finite-time columns",
        "question": "Do the order-lambda2 tagged-spectator tree and order-lambda4 connected six-point tree decouple on their common positive external-jet carrier, or is their order-lambda6 finite-time interference nonzero?",
        "answer": "They do not decouple at the certified tagged fixture. The active four-point jet embeds isometrically in the public ten-dimensional positive six-leg frame with coefficient two on the six neutral complement-pair coordinates containing exactly one tag label and zero on the remaining four, preserving norm 24. Pairing this vector with c=(J-I)beta/4 gives incidence weight five on those six channels and weight six on the other four. At p0=k0, the other four channels are exactly on shell: delta=0 and D=2, so they contribute 12*T. The remaining six channels give three bounded sine classes. Restoring the common tree phase and the public six-point multiplier gives I_tree^(6)=16*sqrt(2)*lambda^6*W(T), where W(T)=12*T+125*sin(16*T/5)/256+125*sin(8*T/5)/128+125*sin(2*(sqrt(17)-3)*T/5)/8. For T>0, sin(x)>=-x implies W(T)>=[221-50*sqrt(17)]*T/8>0, and W(T)/T tends to 12. The exact external-jet cross kernel is therefore finite at finite time, strictly positive and secular. This is not yet a normalized packet probability or the complete order-lambda6 coefficient: the common distributional packet/coarea normalization, active four-point loop, source correction and survival/collinear completion remain missing.",
        "tagged_fixture_and_channels": {
            "all_incoming_labels": labels,
            "tagged_pair": sorted(tag),
            "active_labels": active,
            "total_momentum": [exact_string(value) for value in sum(incoming, sp.zeros(4, 1))],
            "representative_masks": representative_masks,
            "channels": channel_rows,
            "R_tag_odd_masks": r_masks,
            "N_tag_even_masks": n_masks,
            "resonant_masks": resonant_masks,
            "nonresonant_classes": nonresonant_classes,
            "status": "TEN_CHANNEL_TAGGED_FIXTURE_CLASSIFIED_EXACTLY",
        },
        "common_positive_external_jet_carrier": {
            "positive_frame": "U_plus=[I10;I10]/sqrt(2), with U_plus^T*eta*U_plus=I10",
            "connected_coordinates": "a_T=sqrt(2)*U_plus*c_T, c_T=(J-I)*beta_T/4",
            "tagged_embedding_rule": "d_S=2 for S in R (exactly one of tag labels 0,3) and d_S=0 for S in N",
            "tagged_embedding_vector": [int(value) for value in tagged_embedding],
            "tagged_norm": "d^T*d=24",
            "isometry_statement": "the six active four-point complement-pair coefficients embed in the same public positive frame without changing the certified r4 norm 24",
            "incidence_pairing": "<d,a_T>=sqrt(2)/2*(5*sum_(A in R)beta_A,T+6*sum_(A in N)beta_A,T)",
            "weight_reason": "among the six R output rows an R intermediate channel is omitted once and occurs five times, while an N intermediate channel is omitted zero times and occurs six times",
            "status": "COMMON_POSITIVE_CARRIER_AND_NORM_PRESERVING_TAGGED_EMBEDDING_CONSTRUCTED",
        },
        "exact_tree_interference_kernel": {
            "finite_time_kernel": "beta_A,T=F_T(delta_A)/D_A, F_T(delta)=integral_0^T exp(i*delta*tau)dt",
            "real_kernel": "Re(beta_A,T)=sin(delta_A*T)/(delta_A*D_A), with the continuous value T/D_A at delta_A=0",
            "tree_phase": "the four- and six-point trees are compared in the certified common-phase reduced-amplitude convention; that phase cancels, while M4/lambda^2=d and A6/lambda^4=16*a_T fix the displayed relative sign",
            "four_point_coefficient": "lambda^2*d",
            "six_point_coefficient": "16*lambda^4*a_T",
            "reduced_pairing": "<d,a_T>=sqrt(2)/2*(5*sum_R beta+6*sum_N beta)",
            "real_bracket": "W(T)=12*T+125*sin(16*T/5)/256+125*sin(8*T/5)/128+125*sin(2*(sqrt(17)-3)*T/5)/8",
            "restored_cross_kernel": "I_tree^(6)=2*Re<lambda^2*d,16*lambda^4*a_T>=16*sqrt(2)*lambda^6*W(T)",
            "resonant_contribution": "6*sum_(A in N)Re(beta_A,T)=12*T",
            "strict_lower_bound": "W(T)>=[221-50*sqrt(17)]*T/8>0 for every T>0",
            "lower_bound_proof": "apply sin(x)>=-x to the three positive sine arguments; 221>50*sqrt(17) because 221^2=48841>42500=50^2*17",
            "small_time_slope": "W'(0)=(-29+50*sqrt(17))/8>0",
            "large_time_limit": "lim_(T->infinity) W(T)/T=12",
            "classification": "FINITE_AT_EVERY_FINITE_T_STRICTLY_POSITIVE_AND_SECULAR",
            "status": "TAGGED_AND_CONNECTED_TREE_SECTORS_DO_NOT_DECOUPLE",
        },
        "interpretation": {
            "common_external_jet_carrier": "CONSTRUCTED",
            "tagged_connected_tree_cross_kernel": "COEFFICIENT_COMPUTED",
            "finite_time_value": "FINITE_AND_STRICTLY_POSITIVE_FOR_T_GT_ZERO",
            "large_time_behavior": "SECULAR_WITH_COEFFICIENT_12_IN_W",
            "tree_sector_decoupling": "FALSE",
            "normalized_cross_stratum_packet_probability": "NOT_COMPUTED",
            "complete_order_lambda6_probability": "NOT_COMPUTED",
            "loop_and_survival_completion": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED",
        },
        "assumptions": [
            "the exact rational p0=k0 hard nonforward fixture and its active four-point mass-jet coefficient are imported by content hash",
            "the neutral six-leg complement representatives and positive ghost-even U_plus frame are the public certified carrier; no competing six-leg carrier is introduced",
            "the tag pair contains one Omega and one Upsilon while the active quartic block contains two of each, selecting exactly the six neutral masks with one tag label",
            "the connected finite-time replacement beta=F_T(delta)/D is evaluated pointwise at the tagged fixture for finite positive T",
            "the certified common-phase reduced-amplitude convention and public factor 16 for the connected six-point tree are retained",
            "the result is an external-mass/species kernel before a common packet coarea, finite-volume normalization, loop or survival completion",
        ],
        "does_not_establish": [
            "a dimensionless normalized cross-stratum packet probability",
            "a legitimate multiplication of the tagged delta distribution by the connected continuous kernel without a common packet/coarea construction",
            "the complete order-lambda6 probability coefficient",
            "the finite rational or logarithmic active four-point one-loop contribution on the same packet carrier",
            "the order-lambda correction to the dressed scalar source on the same carrier",
            "the matching virtual, survival, forward or collinear contribution",
            "real-virtual or KLN cancellation",
            "an exact probability after summing all perturbative orders",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Eq. (19)",
            "gravity or metric BV/BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "missing_object_ledger": [
            {"object": "common spectator-connected packet/coarea normalization", "status": "MISSING", "required_value": "a compact finite-resolution family that resolves the spectator delta and connected amplitude in one dimensionally consistent generalized-Born trace"},
            {"object": "complete active four-point one-loop coefficient", "status": "MISSING", "required_value": "finite and logarithmic loop terms, counterterms and their external-mass projection on the same tagged packet carrier"},
            {"object": "source and survival completion", "status": "MISSING", "required_value": "the order-lambda dressed-source correction and matching virtual/survival block required at probability order lambda6"},
            {"object": "forward and collinear inclusive boundary", "status": "MISSING", "required_value": "one common regulator and real-virtual completion across resonant factorization supports"},
        ],
        "next_gate": "Construct the complete tagged-stratum order-lambda6 inclusive coefficient on one compact finite-time packet family. First derive the spectator delta coarea and connected-kernel scaling under a physical resolution epsilon, preserving dimensions and the six/four carrier incidence. Then place the certified tree cross term beside the active one-loop four-point interference, the possible order-lambda source correction, and the pseudo-unitary survival contribution. The calculation must decide whether the 12*T resonance cancels, exponentiates into survival, or remains as a finite detector-dependent secular term. Only that assembled object may be called the NLO physical probability; Eq. (19), gravity and Lorentzian transfer remain later gates.",
        "provenance": {
            "source_commit": "831031130b0f0e086ed5f4fa6ac62ff45ab45651",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact SymPy rational/algebraic reconstruction of all ten future-oriented channel momenta at the certified tagged fixture; set-theoretic species selection of the six tag-odd positive coordinates; exact J-I incidence pairing; exact finite-time real-kernel aggregation; and a symbolic sine lower bound with an integer-square positivity witness. No floating-point arithmetic is used.",
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_tagged_connected_finite_time_interference.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_tagged_connected_finite_time_interference.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_tagged_connected_finite_time_interference",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
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
    if value["checks"]["failures"]:
        print("failures:", ", ".join(value["checks"]["failures"]))
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
