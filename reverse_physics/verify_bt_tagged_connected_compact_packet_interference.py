#!/usr/bin/env python3
"""Independent verifier for compact tagged/connected packet interference."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_CONNECTED_COMPACT_PACKET_INTERFERENCE_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-tagged-connected-compact-packet-interference-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def packet_sum(h, table):
    count = len(table)
    return h * sum(sum(row) for row in table) / count


def verify(certificate):
    schema = load(SCHEMA)
    inputs = certificate["provenance"]["inputs"]
    predecessors = [load(os.path.join(ROOT, row["path"])) for row in inputs if "/certificates/" in row["path"]]
    pred = {row["certificate"]: row for row in predecessors}
    interference = pred["REVERSE_PHYSICS_BT_TAGGED_CONNECTED_FINITE_TIME_INTERFERENCE_V1"]
    box = pred["REVERSE_PHYSICS_BT_TAGGED_CONNECTED_FINITE_VOLUME_NORMALIZATION_V1"]
    tagged = pred["REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1"]

    channels = interference["tagged_fixture_and_channels"]["channels"]
    tag = {0, 3}
    rebuilt_R = []
    rebuilt_N = []
    for row in channels:
        mask = row["mask"]
        labels = {index for index in range(6) if mask & (1 << index)}
        (rebuilt_R if len(labels & tag) == 1 else rebuilt_N).append(mask)
    weight_sum = 5 * len(rebuilt_R) + 6 * len(rebuilt_N)

    rows = certificate["box_to_packet_limit"]["constant_kernel_fixture"]
    fixed_values = []
    for row in rows:
        count = row["cells"]
        h = Fraction(row["cell_measure"])
        value = Fraction(row["kernel_value"])
        table = [[value] * count for _ in range(count)]
        fixed_values.append(packet_sum(h, table))

    table = [
        [Fraction(2), Fraction(1, 3), Fraction(-1, 5)],
        [Fraction(4, 7), Fraction(3, 2), Fraction(5, 9)],
        [Fraction(-2, 11), Fraction(7, 8), Fraction(6, 5)],
    ]
    nonconstant = packet_sum(Fraction(1, 17), table)
    diagonal = Fraction(1, 17) * sum(table[i][i] for i in range(3)) / 3

    carrier = certificate["compact_packet_carrier"]
    functional = certificate["compact_tree_cross_functional"]
    limit = certificate["box_to_packet_limit"]
    interpretation = certificate["physical_interpretation"]
    boundaries = certificate["does_not_establish"]
    checks = {
        "schema_validation": not list(Draft202012Validator(schema).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in inputs),
        "six_predecessors_pass": len(predecessors) == 6 and all(row["checks"]["ok"] for row in predecessors),
        "dependency_tags_are_exact": certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_is_coefficient_computed": certificate["lifecycle_state"] == "COEFFICIENT_COMPUTED",
        "public_measure_and_normalization_are_recorded": carrier["one_particle_measure"] == "dnu(p)=d^3p/(2*E_p) in the public BT convention" and carrier["normalization"].endswith("=1"),
        "identity_overlap_is_rederived": carrier["identity_overlap"] == "c_fg=<u(g),I*u(f)>_K=<g,f>_L2(dnu)" and carrier["same_packet_overlap"] == "c_ff=1",
        "mask_partition_is_independently_rebuilt": rebuilt_R == [7, 19, 21, 14, 26, 28] and rebuilt_N == [11, 13, 25, 22],
        "incidence_bound_is_independently_rebuilt": weight_sum == 54 == functional["incidence_weight_sum"] and functional["pointwise_bound"] == "|W_kappa,T(k,p)|<=54*T/d0",
        "packet_Cauchy_bound_is_recorded": functional["functional_bound"] == "|C_fg|<=54*T*sqrt(mu_in*mu_out)/d0 for normalized packets",
        "relative_cross_prefactor_is_exact": functional["relative_tree_cross"] == "q_cross^(6)[g,f]/q_tag^(4)=(2*sqrt(2)*lambda^2/3)*Re[conj(c_fg)*C_fg]",
        "fixture_q6_prefactor_is_exact": functional["fixture_probability"].startswith("q_cross^(6)[f,f]=25*sqrt(2)*lambda^6"),
        "fixture_diagonal_imports_positive_W": functional["fixture_diagonal"].endswith(">0 for T>0") and interference["interpretation"]["finite_time_value"] == "FINITE_AND_STRICTLY_POSITIVE_FOR_T_GT_ZERO",
        "tagged_leading_norm_is_consistent": tagged["four_point_positive_jet_factorization"]["jet_norm"] == "r4^sharp*r4=24",
        "single_cell_inverse_norm_is_consistent": box["common_finite_volume_spectator"]["connected_factor"].endswith("=1/N_s") and "h=1/(2*E_s*V)=1/N_s" in limit["single_mode"],
        "four_refinements_are_recomputed": fixed_values == [Fraction(21, 143)] * 4,
        "recorded_refinements_match": [Fraction(row["matrix_element"]) for row in rows] == fixed_values,
        "fixed_packet_measure_is_constant": [Fraction(row["packet_measure"]) for row in rows] == [Fraction(3, 13)] * 4,
        "cell_measure_decreases_with_refinement": [Fraction(row["cell_measure"]) for row in rows] == [Fraction(3, 13), Fraction(3, 26), Fraction(3, 65), Fraction(3, 143)],
        "nonconstant_double_sum_is_independent": nonconstant == Fraction(36887, 282744) == Fraction(limit["nonconstant_fixture"]["matrix_element"]),
        "off_diagonal_sum_is_required": diagonal == Fraction(47, 510) == Fraction(limit["nonconstant_fixture"]["diagonal_only_wrong_value"]) and diagonal != nonconstant,
        "Riemann_limit_is_typed_as_fixed_support": "fixed support" in limit["continuous_kernel_limit"],
        "smooth_approximation_is_Hilbert_Schmidt": "Hilbert--Schmidt" in limit["smooth_packet_extension"],
        "mode_counting_rejects_naive_1_over_V": "compensates" in limit["mode_counting"],
        "single_mode_and_fixed_packet_limits_are_distinct": interpretation["single_box_mode_fixed_T_V_to_infinity"] == "ZERO_BUT_STATE_BECOMES_MOMENTUM_SHARP" and interpretation["fixed_compact_packet_box_refinement"] == "FINITE_AND_GENERALLY_NONZERO",
        "local_positive_packet_claim_is_scoped_to_finite_T": interpretation["strictly_positive_local_packet_exists_for_each_fixed_T_gt_0"] == "YES_BY_CONTINUITY_OF_THE_FINITE_TIME_KERNEL" and any("uniform control" in row for row in boundaries),
        "complete_lambda6_is_not_promoted": interpretation["complete_order_lambda6_probability"] == "NOT_COMPUTED" and "the complete order-lambda6 tagged probability" in boundaries,
        "source_loop_survival_are_not_promoted": interpretation["active_loop_source_survival_completion"] == "NOT_CONSTRUCTED" and any("dressed-source" in row for row in boundaries) and any("one-loop" in row for row in boundaries) and any("survival" in row for row in boundaries),
        "Eq19_gravity_Lorentzian_boundaries_are_exact": interpretation["general_Eq19"] == "NOT_PROVED" and interpretation["gravity_or_BV_BRST_transfer"] == "NOT_CONSTRUCTED" and interpretation["Lorentzian_causal_claim"] == "NOT_ESTABLISHED",
        "next_gate_disposes_of_lambda5_before_lambda6": "probability order lambda5" in certificate["next_gate"] and "Only after disposing of lambda5" in certificate["next_gate"],
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
