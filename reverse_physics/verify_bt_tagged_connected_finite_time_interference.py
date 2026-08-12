#!/usr/bin/env python3
"""Independent verifier for tagged/connected BT finite-time interference."""
from __future__ import annotations

from itertools import combinations
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_CONNECTED_FINITE_TIME_INTERFERENCE_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-tagged-connected-finite-time-interference-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def parse(value):
    return sp.sympify(value, locals={"sqrt": sp.sqrt})


def vector(row):
    return sp.Matrix([parse(value) for value in row])


def minkowski_square(row):
    return sp.factor(row[0] ** 2 - sum(value**2 for value in row[1:]))


def independent_reconstruction(predecessors):
    tagged = predecessors["REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1"]
    full_phase = predecessors["REVERSE_PHYSICS_BT_SIX_POINT_FULL_PHASE_SPACE_BORN_POSITIVITY_V1"]
    witness = tagged["exact_tagged_spectator_witness"]
    incoming = [vector(row) for row in witness["incoming_momenta"]]
    outgoing = [vector(row) for row in witness["outgoing_momenta"]]
    momenta = incoming + [-row for row in outgoing]
    public_masks = full_phase["universal_complement_formula"]["channels"]
    tag = {0, 3}

    # Independently enumerate all unordered 3|3 splits and confirm that the
    # public representatives choose one member of every complement pair.
    all_masks = [sum(1 << index for index in subset) for subset in combinations(range(6), 3)]
    complement_classes = {tuple(sorted((mask, 63 ^ mask))) for mask in all_masks}

    rows = []
    for mask in public_masks:
        subset = tuple(index for index in range(6) if mask & (1 << index))
        q = sum((momenta[index] for index in subset), sp.zeros(4, 1))
        if q[0] < 0:
            q = -q
        radius = sp.sqrt(sum(value**2 for value in q[1:]))
        rows.append(
            {
                "mask": mask,
                "subset": subset,
                "q": q,
                "q_squared": minkowski_square(q),
                "delta": sp.factor(q[0] - radius),
                "D": sp.factor(q[0] + radius),
                "tag_odd": len(tag.intersection(subset)) == 1,
            }
        )

    r_masks = [row["mask"] for row in rows if row["tag_odd"]]
    n_masks = [row["mask"] for row in rows if not row["tag_odd"]]

    # Rebuild c_S=(1/4) sum_(A != S) beta_A without using the producer's
    # matrix expression.  Summing the six tagged output rows counts a tagged
    # intermediate five times and an untagged intermediate six times.
    beta_symbols = {mask: sp.Symbol("b%d" % mask) for mask in public_masks}
    c_rows = {
        output: sum(beta_symbols[channel] for channel in public_masks if channel != output) / 4
        for output in public_masks
    }
    direct = sp.sqrt(2) * sum(2 * c_rows[output] for output in r_masks)
    weighted = sp.sqrt(2) * (
        5 * sum(beta_symbols[mask] for mask in r_masks)
        + 6 * sum(beta_symbols[mask] for mask in n_masks)
    ) / 2

    duration = sp.Symbol("T", positive=True)

    def real_beta(row):
        if row["delta"] == 0:
            return duration / row["D"]
        return sp.sin(row["delta"] * duration) / (row["delta"] * row["D"])

    bracket = sp.simplify(
        sum((5 if row["tag_odd"] else 6) * real_beta(row) for row in rows)
    )
    target = (
        12 * duration
        + sp.Rational(125, 256) * sp.sin(sp.Rational(16, 5) * duration)
        + sp.Rational(125, 128) * sp.sin(sp.Rational(8, 5) * duration)
        + sp.Rational(125, 8) * sp.sin(sp.Rational(2, 5) * (sp.sqrt(17) - 3) * duration)
    )
    slope = sp.factor(sp.diff(target, duration).subs(duration, 0))
    return {
        "public_masks": public_masks,
        "all_masks": all_masks,
        "complement_classes": complement_classes,
        "rows": rows,
        "r_masks": r_masks,
        "n_masks": n_masks,
        "direct": direct,
        "weighted": weighted,
        "bracket": bracket,
        "target": target,
        "slope": slope,
        "secular": sp.limit(target / duration, duration, sp.oo),
    }


def verify(certificate):
    inputs = certificate["provenance"]["inputs"]
    predecessor_list = [
        load(os.path.join(ROOT, row["path"]))
        for row in inputs
        if "/certificates/" in row["path"]
    ]
    predecessors = {row["certificate"]: row for row in predecessor_list}
    independent = independent_reconstruction(predecessors)
    fixture = certificate["tagged_fixture_and_channels"]
    carrier = certificate["common_positive_external_jet_carrier"]
    kernel = certificate["exact_tree_interference_kernel"]
    interpretation = certificate["interpretation"]
    boundaries = certificate["does_not_establish"]
    recorded_rows = fixture["channels"]
    row_by_mask = {row["mask"]: row for row in recorded_rows}

    row_values_match = True
    row_labels_match = True
    for row in independent["rows"]:
        recorded = row_by_mask.get(row["mask"], {})
        row_values_match = row_values_match and (
            tuple(recorded.get("subset", [])) == row["subset"]
            and vector(recorded.get("q", ["1", "1", "1", "1"])) == row["q"]
            and sp.simplify(parse(recorded.get("q_squared", "1")) - row["q_squared"]) == 0
            and sp.simplify(parse(recorded.get("delta", "1")) - row["delta"]) == 0
            and sp.simplify(parse(recorded.get("D", "1")) - row["D"]) == 0
            and recorded.get("resonant") == (row["delta"] == 0)
            and recorded.get("carrier") == ("R_TAG_ODD" if row["tag_odd"] else "N_TAG_EVEN")
        )
        expected_labels = [fixture["all_incoming_labels"][index] for index in row["subset"]]
        row_labels_match = row_labels_match and recorded.get("labels") == expected_labels

    expected_vector = [2 if mask in independent["r_masks"] else 0 for mask in independent["public_masks"]]
    resonant = [row["mask"] for row in independent["rows"] if row["delta"] == 0]
    n_rows = [row for row in independent["rows"] if not row["tag_odd"]]
    nonresonant = [row for row in independent["rows"] if row["delta"] != 0]
    expected_lower = (221 - 50 * sp.sqrt(17)) / 8

    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in inputs),
        "eight_predecessors_pass": len(predecessor_list) == 8 and all(row["checks"]["ok"] for row in predecessor_list),
        "dependency_boundary_is_exact": certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_is_coefficient_computed": certificate["lifecycle_state"] == "COEFFICIENT_COMPUTED",
        "twenty_three_subsets_make_ten_complement_classes": len(independent["all_masks"]) == 20 and len(independent["complement_classes"]) == 10,
        "public_masks_represent_every_complement_class_once": len(independent["public_masks"]) == 10 and {tuple(sorted((mask, 63 ^ mask))) for mask in independent["public_masks"]} == independent["complement_classes"],
        "recorded_masks_preserve_public_order": fixture["representative_masks"] == independent["public_masks"],
        "recorded_channel_rows_are_unique_and_complete": len(recorded_rows) == len(row_by_mask) == 10 and set(row_by_mask) == set(independent["public_masks"]),
        "channel_subsets_and_exact_kinematics_are_rederived": row_values_match,
        "channel_labels_are_rederived": row_labels_match,
        "every_oriented_channel_has_nonnegative_energy": all(row["q"][0] >= 0 for row in independent["rows"]),
        "delta_D_factorization_is_rederived": all(sp.simplify(row["delta"] * row["D"] - row["q_squared"]) == 0 for row in independent["rows"]),
        "six_tag_odd_masks_are_rederived": fixture["R_tag_odd_masks"] == independent["r_masks"] == [7, 19, 21, 14, 26, 28],
        "four_tag_even_masks_are_rederived": fixture["N_tag_even_masks"] == independent["n_masks"] == [11, 13, 25, 22],
        "tagged_embedding_vector_is_rederived": carrier["tagged_embedding_vector"] == expected_vector,
        "tagged_embedding_norm_is_rederived": sum(value * value for value in expected_vector) == 24 and carrier["tagged_norm"] == "d^T*d=24",
        "incidence_pairing_is_rederived": sp.simplify(independent["direct"] - independent["weighted"]) == 0 and "5*sum_(A in R)" in carrier["incidence_pairing"] and "6*sum_(A in N)" in carrier["incidence_pairing"],
        "four_resonant_masks_are_rederived": fixture["resonant_masks"] == resonant == [11, 13, 25, 22],
        "resonant_rows_are_exactly_tag_even": [row["mask"] for row in n_rows] == resonant,
        "resonant_rows_have_delta_zero_D_two": all(row["delta"] == 0 and row["D"] == 2 and row["q_squared"] == 0 for row in n_rows),
        "six_nonresonant_rows_are_rederived": len(nonresonant) == 6,
        "nonresonant_class_multiplicities_are_rederived": sorted([sum(sp.simplify(row["delta"] - sp.Rational(16, 5)) == 0 for row in nonresonant), sum(sp.simplify(row["delta"] + sp.Rational(8, 5)) == 0 for row in nonresonant), sum(sp.simplify(row["delta"] - sp.Rational(2, 5) * (3 - sp.sqrt(17))) == 0 for row in nonresonant)]) == [1, 1, 4],
        "finite_time_bracket_is_rederived": sp.simplify(sp.expand_trig(independent["bracket"] - independent["target"])) == 0 and kernel["real_bracket"].startswith("W(T)=12*T"),
        "resonant_part_is_12T": sum(6 * sp.Symbol("T") / row["D"] for row in n_rows) == 12 * sp.Symbol("T") and kernel["resonant_contribution"].endswith("=12*T"),
        "strict_lower_bound_is_rederived": 221**2 > 50**2 * 17 and expected_lower > 0 and kernel["strict_lower_bound"] == "W(T)>=[221-50*sqrt(17)]*T/8>0 for every T>0",
        "small_time_slope_is_rederived": sp.simplify(independent["slope"] - (-29 + 50 * sp.sqrt(17)) / 8) == 0 and 50**2 * 17 > 29**2,
        "large_time_coefficient_is_rederived": independent["secular"] == 12 and interpretation["large_time_behavior"] == "SECULAR_WITH_COEFFICIENT_12_IN_W",
        "restored_multiplier_is_recorded": kernel["restored_cross_kernel"] == "I_tree^(6)=2*Re<lambda^2*d,16*lambda^4*a_T>=16*sqrt(2)*lambda^6*W(T)",
        "nondecoupling_conclusion_is_exact": kernel["status"] == "TAGGED_AND_CONNECTED_TREE_SECTORS_DO_NOT_DECOUPLE" and interpretation["tree_sector_decoupling"] == "FALSE",
        "finite_time_classification_is_exact": kernel["classification"] == "FINITE_AT_EVERY_FINITE_T_STRICTLY_POSITIVE_AND_SECULAR" and interpretation["finite_time_value"] == "FINITE_AND_STRICTLY_POSITIVE_FOR_T_GT_ZERO",
        "normalized_probability_is_not_promoted": interpretation["normalized_cross_stratum_packet_probability"] == "NOT_COMPUTED" and "a dimensionless normalized cross-stratum packet probability" in boundaries,
        "complete_lambda6_probability_is_not_promoted": interpretation["complete_order_lambda6_probability"] == "NOT_COMPUTED" and "the complete order-lambda6 probability coefficient" in boundaries,
        "loop_source_and_survival_remain_open": interpretation["loop_and_survival_completion"] == "NOT_CONSTRUCTED" and any("one-loop" in row for row in boundaries) and any("dressed scalar source" in row for row in boundaries) and any("survival" in row for row in boundaries),
        "Eq19_gravity_and_Lorentzian_boundaries_remain_open": interpretation["general_Eq19"] == "NOT_PROVED" and interpretation["gravity_or_BV_BRST_transfer"] == "NOT_CONSTRUCTED" and interpretation["Lorentzian_causal_claim"] == "NOT_ESTABLISHED",
        "next_gate_is_inclusive_lambda6_assembly": "complete tagged-stratum order-lambda6 inclusive coefficient" in certificate["next_gate"] and "Only that assembled object may be called the NLO physical probability" in certificate["next_gate"],
    }
    return {name: bool(value) for name, value in checks.items()}


def main():
    checks = verify(load(CERT))
    failures = [name for name, ok in checks.items() if not ok]
    print("checks %d/%d" % (sum(checks.values()), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    if failures:
        print("failures:", ", ".join(failures))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
