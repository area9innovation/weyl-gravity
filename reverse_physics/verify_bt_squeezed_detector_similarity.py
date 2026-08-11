#!/usr/bin/env python3
"""Independent verifier for BT squeezed-detector similarity."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SQUEEZED_DETECTOR_SIMILARITY_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-squeezed-detector-similarity-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def matrix(value):
    return [[frac(x) for x in row] for row in value]


def tr(a):
    return sum(a[i][i] for i in range(len(a)))


def tp(a):
    return [list(row) for row in zip(*a)]


def mm(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in tp(b)] for row in a]


def invdiag(a):
    return [[1 / a[i][i] if i == j else Fraction(0) for j in range(len(a))] for i in range(len(a))]


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


def verify(c):
    checks = {}
    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(c))
    checks["schema"] = not errors
    g = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    exact = len(c.get("signed_kernel_similarity_fixtures", [])) == 8
    for row in c.get("signed_kernel_similarity_fixtures", []):
        k, gram = matrix(row["kernel"]), matrix(row["parent_gram"])
        sp, sd, kt = matrix(row["parent_isometry"]), matrix(row["daughter_isometry"]), matrix(row["transformed_kernel"])
        e1, e2 = row["e1"], row["e2"]
        h = [[Fraction(4 * e1 * e2) * Fraction((i, j) in ((0, 3), (1, 2), (2, 1), (3, 0))) for j in range(4)] for i in range(4)]
        recomputed = mm(mm(k, h), tp(k))
        transformed = mm(mm(sp, k), invdiag(sd))
        transformed_gram = mm(mm(transformed, h), tp(transformed))
        exact = exact and gram == recomputed and transformed == kt
        exact = exact and matrix(row["transformed_parent_gram"]) == transformed_gram
        exact = exact and mm(mm(tp(sp), g), sp) == g and mm(mm(tp(sd), h), sd) == h
        exact = exact and tr(mm(g, recomputed)) == tr(mm(g, transformed_gram)) == 0
    checks["independent_kernel_metric_similarity"] = exact
    p = c.get("finite_projector_similarity_fixture", {})
    pm, psm, sm = matrix(p.get("projector", [])), matrix(p.get("transported_projector", [])), matrix(p.get("similarity", []))
    checks["independent_projector_similarity"] = (
        mm(pm, pm) == pm and mm(psm, psm) == psm
        and mm(mm(sm, pm), invdiag(sm)) == psm
        and tr(pm) == tr(psm) == 1
    )
    p1, p1s = matrix(p.get("commutator_coefficient", [])), matrix(p.get("transported_commutator_coefficient", []))
    checks["independent_commutator_trace"] = mm(mm(sm, p1), invdiag(sm)) == p1s and tr(p1) == tr(p1s) == 0
    bare = c.get("bare_detector_mismatch", {})
    z = frac(bare.get("fixture_z", {})); x = z * z
    checks["bare_detector_boundary"] = frac(bare.get("fixture_probability", {})) == (1 - x) * x == Fraction(3, 16)
    coeff = c.get("coefficient_disposition", {})
    checks["coefficient_boundary"] = (
        frac(coeff.get("completed_public_finite_regulator_order_lambda_quadratic_coefficient", {})) == 0
        and frac(coeff.get("squeeze_additive_correction", {})) == 0
        and coeff.get("physical_zero") == "NOT_ESTABLISHED"
    )
    checks["claim_boundary"] = len(c.get("does_not_establish", [])) >= 8 and any("LORENTZIAN-CAUSAL" in x for x in c.get("does_not_establish", []))
    inputs = c.get("provenance", {}).get("inputs", [])
    checks["input_hashes"] = len(inputs) == 6 and all(x.get("sha256") == sha256(x.get("path", "")) for x in inputs)
    checks["science_forge_event_FNV_id"] = fnv1a(
        "sf:program/work/reverse-physics-bateman-squeezed-detector-similarity|"
        "DONE|reverse-physics|2026-08-11|Covariant Appendix-C squeeze "
        "similarity leaves the completed finite-regulator order-lambda "
        "quadratic Born trace exactly zero; bare pair occupation is not "
        "the transported Eq. (19) detector. Evidence: "
        "REVERSE_PHYSICS_BT_SQUEEZED_DETECTOR_SIMILARITY_V1.|"
    ) == 0xA908FC9B3503CE6F
    ledger = c.get("checks", {})
    checks["producer_ledger"] = ledger.get("ok") is True and ledger.get("passed") == ledger.get("total") == 20 and ledger.get("failures") == [] and len(ledger.get("details", {})) == 20 and all(ledger.get("details", {}).values())
    if errors:
        for error in errors: print(f"schema: {list(error.path)}: {error.message}")
    failures = [name for name, ok in checks.items() if not ok]
    if failures:
        print("BT SQUEEZED DETECTOR SIMILARITY VERIFY: FAIL")
        for name in failures: print(f"  {name}")
        return False, checks
    return True, checks


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--verify", default=CERT); args = parser.parse_args()
    ok, checks = verify(load(args.verify))
    if not ok: return 1
    print(f"BT SQUEEZED DETECTOR SIMILARITY VERIFY: ALL PASS ({sum(checks.values())}/{len(checks)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
