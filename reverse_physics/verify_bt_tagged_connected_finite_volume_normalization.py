#!/usr/bin/env python3
"""Independent verifier for finite-volume tagged/connected normalization."""
from __future__ import annotations

import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_CONNECTED_FINITE_VOLUME_NORMALIZATION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-tagged-connected-finite-volume-normalization-v1.schema.json",
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


def reconstruct(predecessors):
    interference = predecessors["REVERSE_PHYSICS_BT_TAGGED_CONNECTED_FINITE_TIME_INTERFERENCE_V1"]
    tagged = predecessors["REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1"]
    rows = interference["tagged_fixture_and_channels"]["channels"]
    t, kappa, volume, area = sp.symbols("T kappa V Area", positive=True)
    coupling, acceptance = sp.symbols("lambda DeltaOmega", positive=True)

    def real_channel(row):
        delta = parse(row["delta"])
        denominator = parse(row["D"])
        if delta == 0:
            return t / denominator
        return sp.sin(delta * t) / (delta * denominator)

    w = sp.simplify(
        sum((5 if row["carrier"] == "R_TAG_ODD" else 6) * real_channel(row) for row in rows)
    )
    W = w.subs(t, kappa * t) / kappa**2

    energy = sp.Rational(6, 5) * kappa
    raw_norm = 2 * energy * volume
    gram = sp.Matrix([[0, raw_norm], [raw_norm, 0]])
    positive_vector = sp.Matrix([1, 1]) / sp.sqrt(2)
    positive_norm = sp.factor((positive_vector.T * gram * positive_vector)[0])
    external_normalizer = 1 / sp.sqrt(positive_norm)
    disconnected = sp.factor(external_normalizer * raw_norm * external_normalizer)
    connected = sp.factor(external_normalizer * external_normalizer)

    external_tagged = 24 * coupling**4
    external_cross = 16 * sp.sqrt(2) * coupling**6 * W * connected
    relative = sp.factor(external_cross / external_tagged)
    q4 = (
        sp.Rational(75, 2048)
        * coupling**4
        * acceptance
        / (sp.pi**2 * kappa**2 * area)
    )
    q6 = sp.factor(q4 * relative)
    W_rate = 12 / kappa
    relative_rate = sp.factor((relative / W) * W_rate)
    q6_rate = sp.factor((q6 / W) * W_rate)
    tau = sp.symbols("tau", positive=True)
    double_relative = sp.factor(relative_rate * tau * kappa**2 * volume)
    return {
        "interference": interference,
        "tagged": tagged,
        "w": w,
        "W": W,
        "energy": energy,
        "raw_norm": raw_norm,
        "gram": gram,
        "positive_vector": positive_vector,
        "positive_norm": positive_norm,
        "disconnected": disconnected,
        "connected": connected,
        "relative": relative,
        "q4": q4,
        "q6": q6,
        "W_rate": W_rate,
        "relative_rate": relative_rate,
        "q6_rate": q6_rate,
        "double_relative": double_relative,
        "symbols": {"T": t, "kappa": kappa, "V": volume, "Area": area, "lambda": coupling, "DeltaOmega": acceptance, "tau": tau},
    }


def verify(certificate):
    inputs = certificate["provenance"]["inputs"]
    predecessor_list = [
        load(os.path.join(ROOT, row["path"]))
        for row in inputs
        if "/certificates/" in row["path"]
    ]
    predecessors = {row["certificate"]: row for row in predecessor_list}
    result = reconstruct(predecessors)
    common = certificate["common_finite_volume_spectator"]
    scaled = certificate["scaled_finite_time_kernel"]
    probability = certificate["dimensionless_tree_cross_probability"]
    limits = certificate["limit_classification"]
    interpretation = certificate["interpretation"]
    boundaries = certificate["does_not_establish"]
    symbols = result["symbols"]
    t, kappa, volume = symbols["T"], symbols["kappa"], symbols["V"]
    coupling, acceptance, area = symbols["lambda"], symbols["DeltaOmega"], symbols["Area"]

    expected_w = (
        12 * t
        + sp.Rational(125, 256) * sp.sin(sp.Rational(16, 5) * t)
        + sp.Rational(125, 128) * sp.sin(sp.Rational(8, 5) * t)
        + sp.Rational(125, 8) * sp.sin(sp.Rational(2, 5) * (sp.sqrt(17) - 3) * t)
    )
    expected_q6 = (
        125 * sp.sqrt(2) * coupling**6 * result["W"] * acceptance
        / (12288 * sp.pi**2 * kappa**3 * area * volume)
    )
    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in inputs),
        "four_certificate_predecessors_pass": len(predecessor_list) == 4 and all(row["checks"]["ok"] for row in predecessor_list),
        "dependency_boundary_is_exact": certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_is_coefficient_computed": certificate["lifecycle_state"] == "COEFFICIENT_COMPUTED",
        "ten_channel_W_is_independently_rebuilt": sp.simplify(sp.expand_trig(result["w"] - expected_w)) == 0,
        "scale_covariance_is_rebuilt": sp.simplify(result["W"] - expected_w.subs(t, kappa * t) / kappa**2) == 0 and scaled["scale_covariance"] == "W_kappa(T)=w(kappa*T)/kappa^2",
        "spectator_energy_is_rebuilt": result["energy"] == sp.Rational(6, 5) * kappa and common["fixture_energy"] == "E_s=6*kappa/5",
        "cross_gram_is_independently_rebuilt": result["gram"] == sp.Matrix([[0, result["raw_norm"]], [result["raw_norm"], 0]]),
        "ghost_even_mode_norm_is_rebuilt": result["positive_norm"] == result["raw_norm"] == sp.Rational(12, 5) * kappa * volume,
        "recorded_box_norm_is_exact": common["fixture_norm"] == "N_s=12*kappa*V/5" and common["raw_mode_norm"].endswith("=2*E_s*V"),
        "identity_normalization_is_rebuilt": result["disconnected"] == 1 and common["disconnected_identity_factor"].endswith("=1"),
        "connected_inverse_norm_is_rebuilt": result["connected"] == 5 / (12 * kappa * volume) and common["connected_factor"].endswith("=1/N_s"),
        "leading_external_norm_is_rebuilt": result["tagged"]["four_point_positive_jet_factorization"]["jet_norm"] == "r4^sharp*r4=24" and probability["leading_tagged_external_jet_norm"] == "24*lambda^4",
        "relative_cross_is_rebuilt": sp.simplify(result["relative"] - 2 * sp.sqrt(2) * coupling**2 * result["W"] / (3 * result["raw_norm"])) == 0,
        "leading_tagged_probability_is_rebuilt": result["q4"] == 75 * coupling**4 * acceptance / (2048 * sp.pi**2 * kappa**2 * area),
        "dimensionless_cross_probability_is_rebuilt": sp.simplify(result["q6"] - expected_q6) == 0 and probability["tree_cross_contribution"].startswith("q_cross^(6)=125*sqrt(2)"),
        "active_factors_cancel_only_in_the_ratio": sp.simplify(result["q6"] / result["q4"] - result["relative"]) == 0,
        "fixed_time_volume_limit_is_rebuilt": sp.limit(result["q6"], volume, sp.oo) == 0 and limits["fixed_finite_T_V_to_infinity"] == "q_cross^(6)->0 as 1/V",
        "large_time_W_rate_is_rebuilt_from_linear_part": result["W_rate"] == 12 / kappa and scaled["large_time_rate"].endswith("=12/kappa"),
        "large_time_q6_rate_is_rebuilt": result["q6_rate"] == 125 * sp.sqrt(2) * coupling**6 * acceptance / (1024 * sp.pi**2 * kappa**4 * area * volume),
        "large_time_relative_rate_is_rebuilt": result["relative_rate"] == 10 * sp.sqrt(2) * coupling**2 / (3 * kappa**2 * volume),
        "double_scaled_relative_limit_is_rebuilt": result["double_relative"] == 10 * sp.sqrt(2) * coupling**2 * symbols["tau"] / 3,
        "order_of_limits_is_typed_honestly": interpretation["fixed_time_thermodynamic_limit"] == "ZERO" and interpretation["fixed_volume_long_time_behavior"] == "SECULAR" and interpretation["universal_joint_large_time_large_volume_limit"] == "DOES_NOT_EXIST_WITHOUT_SCALING_CHOICE",
        "compact_packet_is_not_promoted": interpretation["compact_packet_replacement"] == "NOT_CONSTRUCTED" and "a box-independent compact-packet value for q_cross" in boundaries,
        "complete_lambda6_is_not_promoted": interpretation["complete_order_lambda6_probability"] == "NOT_COMPUTED" and "the complete order-lambda6 tagged probability" in boundaries,
        "loop_source_survival_remain_open": interpretation["loop_source_and_survival_completion"] == "NOT_CONSTRUCTED" and any("one-loop" in row for row in boundaries) and any("dressed-source" in row for row in boundaries) and any("survival" in row for row in boundaries),
        "all_time_decoupling_is_rejected": "all-time decoupling from the fixed-time V-to-infinity limit" in boundaries,
        "Eq19_gravity_and_Lorentzian_boundaries_remain_open": interpretation["general_Eq19"] == "NOT_PROVED" and interpretation["gravity_or_BV_BRST_transfer"] == "NOT_CONSTRUCTED" and interpretation["Lorentzian_causal_claim"] == "NOT_ESTABLISHED",
        "next_gate_is_packet_and_inclusive_completion": "normalized compact packet f0" in certificate["next_gate"] and "Only the assembled packet result may promote the complete lambda6 probability" in certificate["next_gate"],
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
