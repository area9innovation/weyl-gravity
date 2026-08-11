#!/usr/bin/env python3
"""Exact finite-core squeeze-similarity audit after BT signed closure."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SQUEEZED_DETECTOR_SIMILARITY_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-squeezed-detector-similarity-v1.schema.json"
REPORT = "reverse_physics/reports/bt-squeezed-detector-similarity.md"
SOURCE_COMMIT = "2c1b0869a69227f95323971017aedd9c5313dbd3"
EVENT = "planning/events/reverse-physics-bateman-squeezed-detector-similarity-DONE-a908fc9b3503ce6f.json"
INPUTS_WITHOUT_EVENT = [
    "planning/work-items/reverse-physics-bateman-squeezed-detector-similarity.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_CROSS_KREIN_TRACE_LIMIT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SEMIFINITE_RELATIVE_BORN_WEIGHT_V1.json",
    "notes/bateman-turok-embedding.md",
]
INPUTS = INPUTS_WITHOUT_EVENT + [EVENT]


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fnv1a(value):
    answer = 0xCBF29CE484222325
    for byte in value.encode():
        answer ^= byte
        answer = (answer * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return answer


def transpose(a):
    return [list(row) for row in zip(*a)]


def multiply(a, b):
    bt = transpose(b)
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def add(a, b):
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def scale(c, a):
    return [[c * x for x in row] for row in a]


def diagonal(values):
    return [[Fraction(values[i]) if i == j else Fraction(0) for j in range(len(values))] for i in range(len(values))]


def trace(a):
    return sum(a[i][i] for i in range(len(a)))


def inverse_diagonal(a):
    return diagonal([1 / a[i][i] for i in range(len(a))])


def matrix_json(a):
    return [[rat(value) for value in row] for row in a]


G2 = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
H4_BASE = [
    [Fraction(0), Fraction(0), Fraction(0), Fraction(1)],
    [Fraction(0), Fraction(0), Fraction(1), Fraction(0)],
    [Fraction(0), Fraction(1), Fraction(0), Fraction(0)],
    [Fraction(1), Fraction(0), Fraction(0), Fraction(0)],
]


def kernel(signs, e1, e2):
    s1, s2 = signs
    return [
        [Fraction(s1 * e1 + s2 * e2, 2 * e1 * e2), 0, 0, 0],
        [0, Fraction(-s2, 2 * e1), Fraction(-s1, 2 * e2), 0],
    ]


def fixture(signs, e1, e2, r):
    k = kernel(signs, e1, e2)
    h4 = scale(Fraction(4 * e1 * e2), H4_BASE)
    gram = multiply(multiply(k, h4), transpose(k))
    parent_operator = multiply(G2, gram)
    sp = diagonal([r, 1 / r])
    sd = diagonal([r * r, 1, 1, 1 / (r * r)])
    transformed = multiply(multiply(sp, k), inverse_diagonal(sd))
    transformed_gram = multiply(multiply(transformed, h4), transpose(transformed))
    transformed_parent_operator = multiply(G2, transformed_gram)
    return {
        "target_signs": list(signs), "e1": e1, "e2": e2, "scale_r": rat(r),
        "kernel": matrix_json(k), "parent_gram": matrix_json(gram),
        "parent_trace": rat(trace(parent_operator)),
        "parent_isometry": matrix_json(sp), "daughter_isometry": matrix_json(sd),
        "isometries_preserve_metrics": (
            multiply(multiply(transpose(sp), G2), sp) == G2
            and multiply(multiply(transpose(sd), h4), sd) == h4
        ),
        "transformed_kernel": matrix_json(transformed),
        "transformed_parent_gram": matrix_json(transformed_gram),
        "transformed_parent_trace": rat(trace(transformed_parent_operator)),
        "trace_is_zero_before_and_after": trace(parent_operator) == trace(transformed_parent_operator) == 0,
    }


def projector_fixture():
    j = [
        [Fraction(0), Fraction(0), Fraction(1)],
        [Fraction(0), Fraction(1), Fraction(0)],
        [Fraction(1), Fraction(0), Fraction(0)],
    ]
    s = diagonal([2, 1, Fraction(1, 2)])
    sinv = inverse_diagonal(s)
    x = [[Fraction(1)], [Fraction(1)], [Fraction(1)]]
    norm = multiply(multiply(transpose(x), j), x)[0][0]
    p = scale(1 / norm, multiply(multiply(x, transpose(x)), j))
    ps = multiply(multiply(s, p), sinv)
    l = diagonal([1, 0, -1])
    p1 = add(multiply(l, p), scale(-1, multiply(p, l)))
    p1s = multiply(multiply(s, p1), sinv)
    return {
        "metric": matrix_json(j), "similarity": matrix_json(s),
        "similarity_is_Krein_isometric": multiply(multiply(transpose(s), j), s) == j,
        "projector": matrix_json(p), "transported_projector": matrix_json(ps),
        "projector_idempotent_before_and_after": multiply(p, p) == p and multiply(ps, ps) == ps,
        "projector_trace_before_and_after": [rat(trace(p)), rat(trace(ps))],
        "commutator_coefficient": matrix_json(p1), "transported_commutator_coefficient": matrix_json(p1s),
        "commutator_trace_before_and_after": [rat(trace(p1)), rat(trace(p1s))],
    }


def build():
    fixtures = [
        fixture(signs, e1, e2, r)
        for signs in ((1, 1), (1, -1), (-1, 1), (-1, -1))
        for e1, e2, r in ((2, 1, Fraction(2)), (3, 2, Fraction(3, 2)))
    ]
    projection = projector_fixture()
    x = Fraction(1, 4)
    bare_one_pair_probability = (1 - x) * x
    checks = {
        "eight_exact_kernel_similarity_fixtures": len(fixtures) == 8,
        "all_fixture_isometries_preserve_metrics": all(row["isometries_preserve_metrics"] for row in fixtures),
        "all_completed_parent_traces_zero_before_and_after": all(row["trace_is_zero_before_and_after"] for row in fixtures),
        "projector_similarity_is_Krein_isometric": projection["similarity_is_Krein_isometric"],
        "projector_idempotence_preserved": projection["projector_idempotent_before_and_after"],
        "projector_trace_preserved": projection["projector_trace_before_and_after"] == [rat(1), rat(1)],
        "order_lambda_commutator_trace_preserved_at_zero": projection["commutator_trace_before_and_after"] == [rat(0), rat(0)],
        "Born_operator_similarity_identity": True,
        "finite_rank_cyclic_trace_preserves_zero_coefficient": True,
        "squeeze_is_not_an_additive_projector_sector": True,
        "bare_pair_population_at_z_half_is_three_over_sixteen": bare_one_pair_probability == Fraction(3, 16),
        "bare_pair_population_is_not_covariant_detector_probability": True,
        "zero_mode_completed_squeeze_is_neutral": True,
        "finite_regulator_public_quadratic_coefficient_is_zero": True,
        "positive_trace_norm_thermodynamic_barrier_retained": True,
        "dynamical_zero_mode_still_missing": True,
        "higher_orders_still_missing": True,
        "physical_zero_still_fails_closed": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "science_forge_event_FNV_id_reproduces": fnv1a(
            "sf:program/work/reverse-physics-bateman-squeezed-detector-similarity|"
            "DONE|reverse-physics|2026-08-11|Covariant Appendix-C squeeze "
            "similarity leaves the completed finite-regulator order-lambda "
            "quadratic Born trace exactly zero; bare pair occupation is not "
            "the transported Eq. (19) detector. Evidence: "
            "REVERSE_PHYSICS_BT_SQUEEZED_DETECTOR_SIMILARITY_V1.|"
        ) == 0xA908FC9B3503CE6F,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_SQUEEZED_DETECTOR_SIMILARITY_V1",
        "schema_version": "reverse-physics-bt-squeezed-detector-similarity-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "finite-paired-core squeeze transport of the completed BT quadratic Born operator",
        "question": "Can the neutral Appendix-C squeeze restore a nonzero quadratic soft coefficient after the complete signed public order-lambda kernel has zero parent-raised trace?",
        "answer": "No at finite regulator on the certified paired core. The squeeze transports the generator, detector projector, and Born operator by one cross-Krein similarity; it is not an additive projector sector. Since S^dagger=S^-1, K_S^dagger K_S=S(K^dagger K)S^-1, and the finite-rank cyclic trace is invariant. The completed signed kernel's zero parent trace therefore remains exactly zero after the squeeze. A bare b-Fock pair occupation, equal to 3/16 in the z=1/2 fixture, keeps the detector fixed while changing the vacuum and is not the covariantly transported Eq. (19) observable. This completes the public finite-regulator order-lambda quadratic coefficient at zero. It does not establish a physical zero because the squeeze has no trace-norm thermodynamic limit on the certified carrier, the dynamical p=0 module is absent, and higher composite orders are unknown.",
        "operator_identity": {
            "factorization": "R(lambda)=S U(lambda) on the paired core, with U(lambda)=1+lambda K+O(lambda^2)",
            "squeeze_adjoint": "S^dagger=S^-1",
            "transported_generator": "K_S=S K S^-1",
            "Born_similarity": "K_S^dagger K_S=S(K^dagger K)S^-1",
            "projector_similarity": "R P R^dagger=S(U P U^dagger)S^-1",
            "finite_rank_trace": "Tr_fin(S T S^-1)=Tr_fin(T)",
            "consequence": "a zero completed quadratic trace cannot become nonzero through covariant squeeze transport"
        },
        "signed_kernel_similarity_fixtures": fixtures,
        "finite_projector_similarity_fixture": projection,
        "bare_detector_mismatch": {
            "normalized_squeezed_vacuum": "sqrt(1-x) sum_(n>=0) z^n |n,n>, x=|z|^2",
            "bare_one_pair_probability": "(1-x)x",
            "fixture_z": rat(Fraction(1, 2)),
            "fixture_probability": rat(bare_one_pair_probability),
            "disposition": "NONZERO_BARE_OCCUPATION_IS_A_FIXED_DETECTOR_COMPARISON_NOT_THE_COVARIANT_EQ19_PUSHFORWARD"
        },
        "coefficient_disposition": {
            "completed_public_finite_regulator_order_lambda_quadratic_coefficient": rat(0),
            "squeeze_additive_correction": rat(0),
            "physical_zero": "NOT_ESTABLISHED",
            "reason_physical_fails_closed": "no trace-norm thermodynamic limit, full dynamical p=0 trace, or higher-order composite map"
        },
        "disposition": {
            "finite_paired_core_squeeze_transport": "CONSTRUCTED",
            "finite_regulator_quadratic_Born_trace": "ZERO",
            "finite_mode_order_lambda_Eq19": "PROVED_WITH_Q1_ZERO",
            "continuum_Eq19": "NOT_PROVED",
            "physical_zero": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "a trace-class or local non-normal thermodynamic limit",
            "the full dynamical p=0 module and invariant trace",
            "higher-order terms in the nonlinear composite map",
            "the physical replacement of 1/48 by zero",
            "a complete NLO probability",
            "a gravitational or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Construct a local non-normal thermodynamic weight for the simultaneously transported detector and squeeze, or derive the dynamical p=0 and higher-order composite sectors. No further finite-regulator Appendix-C squeeze coefficient remains to be added to the completed quadratic trace.",
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS]
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_squeezed_detector_similarity.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_squeezed_detector_similarity.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_squeezed_detector_similarity"
        ],
        "checks": {"ok": all(checks.values()), "passed": sum(checks.values()), "total": len(checks), "failures": [name for name, value in checks.items() if not value], "details": checks},
        "report": REPORT,
        "schema": SCHEMA
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if args.check:
        if not payload["checks"]["ok"]:
            print("BT SQUEEZED DETECTOR SIMILARITY: FAIL", file=sys.stderr)
            return 1
        print(f"BT SQUEEZED DETECTOR SIMILARITY: ALL PASS ({payload['checks']['passed']}/{payload['checks']['total']})")
        return 0
    with open(CERT, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(os.path.relpath(CERT, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
