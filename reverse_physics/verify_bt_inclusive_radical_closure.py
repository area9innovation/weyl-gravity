#!/usr/bin/env python3
"""Independent verifier for the BT inclusive radical-closure certificate.

The producer is not imported.  Kernel tensor powers are recomputed by an
aggregated dynamic program on charge pairs rather than by expanding the
producer's term list.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import defaultdict
from fractions import Fraction

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_INCLUSIVE_RADICAL_CLOSURE_V1.json",
)
SCHEMA = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-inclusive-radical-closure-v1.schema.json",
)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction(payload):
    return Fraction(payload["numerator"], payload["denominator"])


def series(rows):
    return {int(row["charge"]): fraction(row["coefficient"])
            for row in rows if fraction(row["coefficient"])}


def multiply(left, right, reverse_left=False):
    out = defaultdict(Fraction)
    for q_left, c_left in left.items():
        effective_left = -q_left if reverse_left else q_left
        for q_right, c_right in right.items():
            out[effective_left + q_right] += c_left * c_right
    return {q: c for q, c in out.items() if c}


def add(left, right):
    out = defaultdict(Fraction)
    for source in (left, right):
        for charge, coefficient in source.items():
            out[charge] += coefficient
    return {q: c for q, c in out.items() if c}


def aggregate_kernel(base, power):
    """Return {(left charge, right charge): coefficient} without term expansion."""
    aggregate = {(0, 0): Fraction(1)}
    for _ in range(power):
        next_aggregate = defaultdict(Fraction)
        for (old_left, old_right), old_coefficient in aggregate.items():
            for left, right, coefficient in base:
                next_aggregate[(old_left + left, old_right + right)] += (
                    old_coefficient * coefficient
                )
        aggregate = dict(next_aggregate)
    return aggregate


def apply_aggregate(value, aggregate):
    out = defaultdict(Fraction)
    for (left, right), kernel_coefficient in aggregate.items():
        shift = left + right
        for charge, coefficient in value.items():
            out[charge + shift] += kernel_coefficient * coefficient
    return {q: c for q, c in out.items() if c}


def verify(certificate):
    checks = {}
    try:
        with open(SCHEMA, encoding="utf-8") as handle:
            schema_payload = json.load(handle)
        Draft202012Validator.check_schema(schema_payload)
        Draft202012Validator(schema_payload).validate(certificate)
        checks["strict_schema"] = True
    except Exception:
        checks["strict_schema"] = False

    checks["identity_and_boundary"] = (
        certificate.get("certificate")
        == "REVERSE_PHYSICS_BT_INCLUSIVE_RADICAL_CLOSURE_V1"
        and certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC"]
        and certificate.get("lifecycle_state") == "CLASSIFIED"
        and certificate.get("disposition", {}).get("physical_inclusive_map")
        == "NOT_CONSTRUCTED"
        and any("LORENTZIAN-CAUSAL" in item
                for item in certificate.get("does_not_establish", []))
    )

    try:
        inputs = certificate["provenance"]["inputs"]
        checks["input_hashes"] = len(inputs) == 4 and all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        )
    except (KeyError, OSError):
        checks["input_hashes"] = False

    carrier = certificate.get("carrier", {})
    b = series(carrier.get("populated_B_fixture", []))
    c = series(carrier.get("populated_C_fixture", []))
    a = add(b, c)
    bt_product = multiply(a, a, reverse_left=False)
    hilbert_product = multiply(a, a, reverse_left=True)
    recorded_born = certificate.get("born_trace_identity", {})
    checks["independent_Born_trace"] = (
        b and set(b) == {0}
        and c and all(q < 0 for q in c)
        and bt_product.get(0, 0) == fraction(recorded_born["BT_trace"])
        and b[0] ** 2 == fraction(recorded_born["B_dagger_B_trace"])
        and bt_product.get(0, 0) == b[0] ** 2
        and hilbert_product.get(0, 0)
        == fraction(recorded_born["Hilbert_mutation_trace"])
        and hilbert_product.get(0, 0) != bt_product.get(0, 0)
    )
    checks["negative_sector_not_global_radical"] = (
        multiply({-1: Fraction(1)}, {+1: Fraction(1)}).get(0, 0) == 1
        and "not a radical of the full Laurent algebra"
        in carrier.get("negative_radical", "")
    )

    kernel = certificate.get("eq20_completeness_kernel", {})
    recorded_terms = kernel.get("nonzero_terms", [])
    base = [
        (row["left_charge"], row["right_charge"],
         fraction(row["coefficient"]))
        for row in recorded_terms
    ]
    checks["Eq20_kernel_exact"] = sorted(base) == [
        (-1, +1, Fraction(1)), (+1, -1, Fraction(1))
    ] and all(left + right == 0 for left, right, _ in base)

    rows_by_n = {
        row["unresolved_multiplicity"]: row
        for row in kernel.get("tensor_power_rows", [])
    }
    tensor_ok = set(rows_by_n) == set(range(6))
    for power in range(6):
        aggregate = aggregate_kernel(base, power)
        image = apply_aggregate(c, aggregate)
        expected = {q: coefficient * 2**power
                    for q, coefficient in c.items()}
        row = rows_by_n.get(power, {})
        tensor_ok = tensor_ok and (
            image == expected
            and sum(1 for _ in range(2**power))
            == row.get("expanded_kernel_terms")
            and row.get("total_shifts") == [0]
            and row.get("image_support") == sorted(c)
            and row.get("image_scale") == 2**power
            and row.get("closure") is True
        )
    checks["independent_tensor_powers"] = tensor_ok

    weights = [fraction(row) for row in kernel.get("finite_weight_fixture", [])]
    scale = sum(weight * 2**power for power, weight in enumerate(weights))
    recorded_scale = fraction(kernel.get("finite_weight_scale", {}))
    recorded_image = series(kernel.get("finite_weight_image", []))
    checks["independent_weighted_sum"] = (
        len(weights) == 6 and scale != 0 and scale == recorded_scale
        and recorded_image == {q: scale * coefficient
                               for q, coefficient in c.items()}
        and all(q < 0 for q in recorded_image)
    )

    recorded_criterion = certificate.get("criterion_exhaustion", {})
    rows = recorded_criterion.get("rows", [])
    row_map = {(row["left_charge"], row["right_charge"]): row for row in rows}
    criterion_ok = len(rows) == 49 and len(row_map) == 49
    for left in range(-3, 4):
        for right in range(-3, 4):
            shift = left + right
            closes = shift <= 0
            witness_charge = -shift if shift > 0 else None
            witness_trace = Fraction(1) if shift > 0 else Fraction(0)
            row = row_map.get((left, right), {})
            criterion_ok = criterion_ok and (
                row.get("total_shift") == shift
                and row.get("closes_negative_carrier") is closes
                and row.get("counterexample_input_charge") == witness_charge
                and fraction(row.get("counterexample_trace", {}))
                == witness_trace
            )
    checks["independent_shift_criterion"] = criterion_ok

    classification = {
        row["entry"]: row for row in kernel.get("classification", [])
    }
    checks["diagonal_mutations_are_distinguished"] = (
        classification.get("W^{Omega Omega}", {}).get("total_shift") == 2
        and classification.get("W^{Omega Omega}", {}).get("radical_closure")
        is False
        and classification.get("W^{Upsilon Upsilon}", {}).get("total_shift")
        == -2
        and classification.get("W^{Upsilon Upsilon}", {}).get(
            "radical_closure") is True
    )

    checks["missing_objects_fail_closed"] = (
        len(certificate.get("missing_object_ledger", [])) >= 5
        and certificate.get("disposition", {}).get("real_virtual_cancellation")
        == "NOT_COMPUTED"
        and certificate.get("disposition", {}).get("beyond_tree_positivity")
        == "NOT_ESTABLISHED"
    )
    checks["producer_checks_recorded"] = (
        certificate.get("checks", {}).get("ok") is True
        and certificate.get("checks", {}).get("passed")
        == certificate.get("checks", {}).get("total")
        and not certificate.get("checks", {}).get("failures")
    )
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="independent BT inclusive radical-closure verifier")
    parser.add_argument("--verify", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    with open(args.verify, encoding="utf-8") as handle:
        certificate = json.load(handle)
    checks = verify(certificate)
    for name, passed in checks.items():
        print(("[OK ] " if passed else "[FAIL] ") + name)
    failures = [name for name, passed in checks.items() if not passed]
    print("checks %d/%d" % (len(checks) - len(failures), len(checks)))
    print("RESULT: %s" % ("PASS" if not failures else "FAIL"))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
