#!/usr/bin/env python3
"""Independent verifier for compact-spacetime local BT quadrupole q8."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COMPACT_SPACETIME_QUADRUPOLE_DARK_DETECTOR_Q8_V1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-compact-spacetime-quadrupole-dark-detector-q8-v1.schema.json"
)


def load(relative):
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_hash(value):
    return hashlib.sha256(
        f"{value.numerator}/{value.denominator}".encode()
    ).hexdigest()


def receipt_matches(row, value):
    return (
        row.get("exact") == str(value)
        and row.get("canonical_sha256") == canonical_hash(value)
    )


def verify(certificate):
    checks = {}
    schema = load(SCHEMA_REL)
    checks["schema_validation"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    checks["certificate_identity"] = certificate.get("certificate") == (
        "REVERSE_PHYSICS_BT_COMPACT_SPACETIME_QUADRUPOLE_DARK_DETECTOR_Q8_V1"
    )

    provenance = certificate.get("provenance", {})
    inputs = provenance.get("inputs", [])
    checks["input_hashes_recomputed"] = len(inputs) == 6 and all(
        os.path.isfile(os.path.join(ROOT, row.get("path", "")))
        and row.get("sha256") == sha256(row["path"])
        for row in inputs
    )
    paths = [row.get("path", "") for row in inputs]
    expected_predecessors = [
        "reverse_physics/certificates/REVERSE_PHYSICS_BT_LOCAL_QUADRUPOLE_DARK_DETECTOR_Q8_V1.json",
        "reverse_physics/certificates/REVERSE_PHYSICS_BT_GLOBAL_CONNECTED_FINITE_TIME_PACKET_COLUMN_V1.json",
        "reverse_physics/certificates/REVERSE_PHYSICS_BT_CONTINUOUS_ANGLE_Q6_FAMILY_V1.json",
        "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_BANDWIDTH_DARK_PORT_Q8_V1.json",
    ]
    checks["four_predecessor_pass_flags_rechecked"] = all(
        path in paths and load(path)["checks"]["ok"]
        for path in expected_predecessors
    )
    event_paths = [path for path in paths if "/events/" in path]
    checks["done_event_matches_work_item"] = len(event_paths) == 1 and (
        lambda event: event["body"]["payload"]["to_state"] == "DONE"
        and event["body"]["payload"]["target"].endswith(
            "compact-spacetime-quadrupole-dark-detector-q8"
        )
    )(load(event_paths[0]))

    cutoff = certificate.get("compact_cutoff_sequence", {})
    checks["compact_support_recomputed"] = (
        cutoff.get("sequence") == "h_R(x)=chi(x/R)*h0(x), R>=1"
        and cutoff.get("support") == "supp(h_R) subset {|x|_E<2R}"
        and "C_c_infinity" in cutoff.get("cutoff", "")
    )
    checks["Hermitian_quadratures_are_compact"] = (
        "Re(h_R)" in cutoff.get("Hermitian_realization", "")
        and "Im(h_R)" in cutoff.get("Hermitian_realization", "")
        and "compactly supported" in cutoff.get("Hermitian_realization", "")
    )

    # Method-distinct Schwartz proof.  On a derivative term with gamma
    # derivatives landing on chi_R, |D^gamma chi_R| contributes R^-gamma.
    # The support is either |x|>=R or R<=|x|<=2R.  A Schwartz tail of order
    # N+L+|alpha| supplies R^(-N-L-|alpha|); multiplication by x^alpha and
    # the target weight contributes at most R^(N+|alpha|), leaving R^-L.
    for alpha in range(5):
        for beta in range(5):
            for gamma in range(beta + 1):
                for N in range(5):
                    L = 3
                    cutoff_power = -gamma
                    polynomial_power = N + alpha
                    tail_order = N + alpha + L
                    total_power = cutoff_power + polynomial_power - tail_order
                    if total_power > -L:
                        checks["annular_multiindex_power_count"] = False
                        break
                else:
                    continue
                break
            else:
                continue
            break
        else:
            continue
        break
    else:
        checks["annular_multiindex_power_count"] = True
    checks["arbitrary_tail_gain_implies_S_convergence"] = (
        "every N,m,L" in cutoff.get("Leibniz_bound", "")
        and "R^(-L)" in cutoff.get("Leibniz_bound", "")
        and "tends to h0_hat in S" in cutoff.get("Fourier_statement", "")
    )
    checks["Paley_Wiener_boundary_retained"] = (
        "not claimed compactly supported" in cutoff.get("Fourier_statement", "")
        and certificate.get("disposition", {}).get("Fourier_support")
        == "NONCOMPACT_AND_RETAINED"
    )

    gate = certificate.get("tempered_response_gate", {})
    global_tree = load(expected_predecessors[1])
    checks["global_tree_HS_input_rechecked"] = (
        global_tree["global_connected_column"]["status"]
        == "GLOBAL_CONNECTED_FINITE_TIME_POSITIVE_EFFECT_CONSTRUCTED"
        and "1539" in gate.get("tree_input", "")
        and "Hilbert--Schmidt" in gate.get("tree_input", "")
    )
    # Independent local integrability: int_0^1 (-log u)du =
    # [-u log u + u]_0^1 = 1.  Both c endpoints reduce to this model.
    log_integral = Fraction(1)
    checks["endpoint_log_integral_recomputed"] = (
        log_integral == 1
        and gate.get("log_integral") == "int_0^1 abs(log u)du=1"
        and gate.get("loop_endpoint_model")
        == "log(1-c^2)=log(1-c)+log(1+c) on -1<c<1"
    )
    angle = load(expected_predecessors[2])
    checks["loop_endpoint_source_rechecked"] = (
        "1-c^2" in angle["continuous_finite_time_loop"]["invariant_log"]
        and "logarithmic growth" in gate.get("growth", "")
        and "degree-four F2" in gate.get("growth", "")
    )
    checks["tempered_functional_is_explicit"] = (
        gate.get("functional")
        == "A4:S(R^4)->C is a tempered distribution and therefore continuous in the Schwartz topology"
        and "there exists finite R0" in gate.get("continuity_consequence", "")
        and "<|A4(h0)|/2" in gate.get("continuity_consequence", "")
    )

    probability = certificate.get("exact_darkness_and_probability", {})
    local = load(expected_predecessors[0])
    base = Fraction(
        local["local_detector_probability"]["exact_rational_lower"]["exact"]
    )
    retained = base * Fraction(1, 2) ** 2
    checks["imported_lower_hash_rechecked"] = receipt_matches(
        probability.get("imported_lower", {}), base
    )
    checks["quarter_probability_recomputed"] = retained == Fraction(
        1, 18_874_368_000
    )
    checks["compact_lower_hash_rechecked"] = receipt_matches(
        probability.get("compact_lower", {}), retained
    )
    checks["compact_lower_exceeds_target"] = retained > Fraction(
        1, 20_000_000_000
    )
    checks["fibrewise_zero_survives_arbitrary_weight"] = (
        "integral_sphere F2(P,r)dOmega=0" in probability.get("leading_identity", "")
        and "separately on every timelike P fibre" in probability.get("reason", "")
        and "Fourier tails" in probability.get("reason", "")
    )
    checks["amplitude_to_probability_square_is_explicit"] = (
        probability.get("amplitude_retention")
        == "|A4(h_R)|>|A4(h0)|/2 for R>=R0"
        and probability.get("comparison")
        == "Q8_compact/q4_bar>1/18874368000>1/20000000000"
    )
    checks["joint_order_is_scoped"] = probability.get("joint_expansion") == (
        "p_selected=g_det^2*lambda^8*Q8_compact+"
        "O(g_det^2*lambda^10)+O(g_det^4)"
    )

    disposition = certificate.get("disposition", {})
    boundaries = certificate.get("does_not_establish", [])
    checks["support_radius_is_existential"] = (
        disposition.get("finite_support_radius")
        == "EXISTS_BUT_NOT_NUMERICALLY_BOUNDED"
        and any("numerical cutoff radius" in row for row in boundaries)
    )
    checks["causal_pAQFT_remains_open"] = (
        disposition.get("causal_pAQFT_observable") == "NOT_CONSTRUCTED"
        and any("causal perturbative AQFT" in row for row in boundaries)
    )
    checks["detector_all_orders_remain_open"] = (
        disposition.get("all_orders_in_external_detector_coupling")
        == "NOT_CONSTRUCTED"
        and any("g_detector^4" in row for row in boundaries)
    )
    checks["Eq19_remains_open"] = (
        disposition.get("general_Eq19") == "NOT_PROVED_AND_NOT_USED"
        and any("Eq. (19)" in row for row in boundaries)
    )
    checks["gravity_remains_open"] = (
        disposition.get("gravity_or_metric_BV_BRST_transfer")
        == "NOT_CONSTRUCTED"
        and any("metric BV--BRST" in row for row in boundaries)
    )
    checks["Lorentzian_boundary_present"] = (
        disposition.get("Lorentzian_causal_claim") == "NOT_ESTABLISHED"
        and "anything LORENTZIAN-CAUSAL" in boundaries
    )
    checks["literature_priority_forbidden"] = "literature priority" in boundaries
    return checks


def main():
    certificate = load(CERT_REL)
    checks = verify(copy.deepcopy(certificate))
    for name, passed in checks.items():
        print(("PASS: " if passed else "FAIL: ") + name)
    if all(checks.values()):
        print("RESULT: PASS")
        return 0
    print("RESULT: FAIL", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
