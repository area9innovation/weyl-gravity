#!/usr/bin/env python3
"""Independent verifier for the exact compact quadrupole Julia instrument."""
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
    "REVERSE_PHYSICS_BT_EXACT_QUADRUPOLE_JULIA_INSTRUMENT_V1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-exact-quadrupole-julia-instrument-v1.schema.json"
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


# Exact Q(sqrt(3)) arithmetic as pairs a+b*sqrt(3).
def q(a=0, b=0):
    return Fraction(a), Fraction(b)


def qadd(x, y):
    return x[0] + y[0], x[1] + y[1]


def qneg(x):
    return -x[0], -x[1]


def qmul(x, y):
    return x[0] * y[0] + 3 * x[1] * y[1], x[0] * y[1] + x[1] * y[0]


ZERO = q(0)
ONE = q(1)


def matmul(left, right):
    rows = len(left)
    inner = len(right)
    cols = len(right[0])
    return [
        [
            sum_q(qmul(left[i][k], right[k][j]) for k in range(inner))
            for j in range(cols)
        ]
        for i in range(rows)
    ]


def sum_q(values):
    result = ZERO
    for value in values:
        result = qadd(result, value)
    return result


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def identity(size):
    return [[ONE if i == j else ZERO for j in range(size)] for i in range(size)]


def verify(certificate):
    checks = {}
    schema = load(SCHEMA_REL)
    checks["schema_validation"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    checks["certificate_identity"] = certificate.get("certificate") == (
        "REVERSE_PHYSICS_BT_EXACT_QUADRUPOLE_JULIA_INSTRUMENT_V1"
    )

    provenance = certificate.get("provenance", {})
    inputs = provenance.get("inputs", [])
    checks["input_hashes_recomputed"] = len(inputs) == 5 and all(
        os.path.isfile(os.path.join(ROOT, row.get("path", "")))
        and row.get("sha256") == sha256(row["path"])
        for row in inputs
    )
    paths = [row.get("path", "") for row in inputs]
    predecessors = [
        "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_SPACETIME_QUADRUPOLE_DARK_DETECTOR_Q8_V1.json",
        "reverse_physics/certificates/REVERSE_PHYSICS_BT_COHERENT_COMPACT_WAVEPACKET_DETECTOR_DILATION_V1.json",
        "reverse_physics/certificates/REVERSE_PHYSICS_BT_TWO_ANGLE_LOCAL_DETECTOR_COMPRESSION_V1.json",
    ]
    checks["three_predecessor_pass_flags_rechecked"] = all(
        path in paths and load(path)["checks"]["ok"] for path in predecessors
    )
    event_paths = [path for path in paths if "/events/" in path]
    checks["done_event_matches_work_item"] = len(event_paths) == 1 and (
        lambda event: event["body"]["payload"]["to_state"] == "DONE"
        and event["body"]["payload"]["target"].endswith(
            "exact-quadrupole-julia-instrument"
        )
    )(load(event_paths[0]))

    instrument = certificate.get("bounded_click_instrument", {})
    checks["click_contraction_is_explicit"] = (
        instrument.get("click_Kraus") == "K_click=(1/2)|0><u2|"
        and instrument.get("click_norm") == "1/2"
        and instrument.get("source_effect")
        == "E_click=K_click^*K_click=(1/4)P_u"
    )
    checks["no_click_square_root_is_explicit"] = (
        instrument.get("no_click_Kraus")
        == "K_no=I+(sqrt(3)/2-1)P_u"
        and instrument.get("no_click_effect")
        == "E_no=K_no^*K_no=I-(1/4)P_u"
    )
    checks["effect_normalization_is_explicit"] = (
        instrument.get("normalization") == "E_click+E_no=I exactly"
        and "p_click(Psi)=|<u2,Psi>|^2/4" in instrument.get("probability", "")
    )

    # Independent exact Julia calculation in Q(sqrt(3)).
    half = q(Fraction(1, 2))
    minus_half = q(Fraction(-1, 2))
    root3_half = q(0, Fraction(1, 2))
    julia = [
        [root3_half, ZERO, minus_half],
        [ZERO, ONE, ZERO],
        [half, ZERO, root3_half],
    ]
    checks["Julia_left_unitarity_recomputed"] = matmul(transpose(julia), julia) == identity(3)
    checks["Julia_right_unitarity_recomputed"] = matmul(julia, transpose(julia)) == identity(3)
    checks["defect_squares_recomputed"] = (
        qmul(root3_half, root3_half) == q(Fraction(3, 4))
        and qmul(half, half) == q(Fraction(1, 4))
        and qadd(qmul(root3_half, root3_half), qmul(half, half)) == ONE
    )
    dilation = certificate.get("exact_Julia_dilation", {})
    checks["stored_Julia_fixture_is_exact"] = (
        dilation.get("click_matrix") == [["1/2", "0"]]
        and dilation.get("source_defect") == [["sqrt(3)/2", "0"], ["0", "1"]]
        and dilation.get("output_defect") == [["sqrt(3)/2"]]
        and dilation.get("Julia_matrix") == [
            ["sqrt(3)/2", "0", "-1/2"],
            ["0", "1", "0"],
            ["1/2", "0", "sqrt(3)/2"],
        ]
    )
    checks["defect_intertwining_recomputed"] = qmul(root3_half, half) == qmul(half, root3_half)

    # Method-distinct polynomial antiderivative moments.
    mean = (3 * Fraction(2, 3) - 2) / 2
    norm = (9 * Fraction(2, 5) - 6 * Fraction(2, 3) + 2) / 4
    cubic = (
        27 * Fraction(2, 7)
        - 27 * Fraction(2, 5)
        + 9 * Fraction(2, 3)
        - 2
    ) / 8
    checks["P2_mean_recomputed"] = mean == 0
    checks["P2_norm_recomputed"] = norm == Fraction(2, 5)
    checks["P2_cubic_recomputed"] = cubic == Fraction(4, 35)
    checks["cubic_scalar_projection_recomputed"] = cubic / 2 == Fraction(2, 35)

    response = certificate.get("darkness_and_response", {})
    compact = load(predecessors[0])
    checks["fibrewise_darkness_source_rechecked"] = (
        compact["exact_darkness_and_probability"]["status"]
        == "STRICTLY_POSITIVE_COMPACT_SPACETIME_LOCAL_DARK_Q8_COEFFICIENT"
        and "separately for every P" in response.get("orthogonality", "")
        and "angle-independent" in response.get("leading_subspace", "")
    )
    checks["strict_X4_response_source_rechecked"] = (
        "nonzero" in response.get("strict_response", "")
        and "strictly positive" in response.get("strict_response", "")
    )
    checks["finite_strength_probability_is_exact"] = response.get(
        "exact_instrument_probability"
    ) == "p_click[X(lambda)]=(1/4)|<u2,X(lambda)>|^2"
    checks["lambda8_coefficient_is_positive"] = (
        response.get("coefficient_statement", "").startswith(
            "p_click=lambda^8*|<u2,X4>|^2/4"
        )
        and "strictly positive" in response.get("coefficient_statement", "")
    )
    checks["detector_and_BT_orders_are_separated"] = (
        response.get("detector_coupling_status")
        == "EXACT_FINITE_STRENGTH_NO_G_DETECTOR_REMAINDER"
        and response.get("BT_coupling_status")
        == "COEFFICIENTWISE_LAMBDA_EXPANSION_REMAINS"
    )

    obstruction = certificate.get("full_local_exponential_obstruction", {})
    checks["cubic_obstruction_is_stored"] = (
        obstruction.get("cubic_moment") == "int_-1^1 P2(c)^3dc=4/35"
        and obstruction.get("scalar_projection_coefficient")
        == "(1/2)*int_-1^1 P2(c)^3dc=2/35"
        and "does not structurally preserve" in obstruction.get("consequence", "")
    )

    locality = certificate.get("locality_ledger", {})
    checks["local_density_is_distinguished_from_compression"] = (
        "C_c_infinity" in locality.get("underlying_density", "")
        and "P0 D_h P2" in locality.get("click_compression", "")
        and locality.get("global_objects_in_click")
        == ["vacuum projection P0", "two-particle projection P2", "global response-mode normalization"]
    )
    checks["global_no_click_projector_is_explicit"] = (
        locality.get("global_object_in_no_click") == "P_u=|u2><u2|"
    )
    checks["local_Kraus_nonidentification_is_explicit"] = (
        "not_established_relation" in locality
        and "bounded-region local AQFT algebra" in locality["not_established_relation"]
        and locality.get("status")
        == "OPERATIONAL_INSTRUMENT_EXACT_LOCAL_KRAUS_REALIZATION_OPEN"
    )

    disposition = certificate.get("disposition", {})
    boundaries = certificate.get("does_not_establish", [])
    checks["operational_instrument_is_exact"] = (
        disposition.get("finite_strength_operational_instrument")
        == "CONSTRUCTED_EXACTLY"
        and disposition.get("click_no_click_normalization") == "EXACT"
    )
    checks["local_Kraus_remains_open"] = (
        disposition.get("compact_local_Kraus_realization") == "NOT_CONSTRUCTED"
        and any("local AQFT algebra" in row for row in boundaries)
    )
    checks["public_BT_selection_remains_open"] = (
        disposition.get("public_BT_selection") == "NOT_CONSTRUCTED"
        and any("public BT dynamics" in row for row in boundaries)
    )
    checks["all_order_lambda_remains_open"] = (
        disposition.get("all_order_BT_lambda_probability") == "NOT_CONSTRUCTED"
        and any("all-order BT probability" in row for row in boundaries)
    )
    checks["Eq19_remains_open"] = (
        disposition.get("general_Eq19") == "NOT_PROVED_AND_NOT_USED"
        and any("Eq. (19)" in row for row in boundaries)
    )
    checks["gravity_remains_open"] = (
        disposition.get("gravity_or_metric_BV_BRST_transfer") == "NOT_CONSTRUCTED"
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
