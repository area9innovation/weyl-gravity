#!/usr/bin/env python3
"""Independent verifier for the BT external-virtuality-jet obstruction.

The producer is not imported.  This verifier evaluates mixed derivatives by
subset convolution: the top coefficient of a product is the sum over every
subset and its complement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_OFFSHELL_JET_OBSTRUCTION_V1.json",
)
SCHEMA = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-offshell-jet-obstruction-v1.schema.json",
)


def fraction(payload):
    return Fraction(payload["numerator"], payload["denominator"])


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def top_of_product(left, right, n):
    """Top square-free coefficient, independently via complementary masks."""
    full = (1 << n) - 1
    total = Fraction(0)
    for mask, coefficient in left.items():
        complement = full ^ mask
        total += coefficient * right.get(complement, Fraction(0))
    return total


def verify_witness(row):
    n = row["external_legs"]
    a = fraction(row["parameter"])
    full = (1 << n) - 1
    base = {0: Fraction(1)}
    mutated = {0: Fraction(1), full: a}
    base_projected = top_of_product(base, base, n)
    mutated_projected = top_of_product(mutated, mutated, n)
    return (
        row["jet_dimension"] == 1 << n
        and fraction(row["base_on_shell"]) == base[0]
        and fraction(row["mutated_on_shell"]) == mutated[0]
        and fraction(row["base_projected_probability"]) == base_projected
        and fraction(row["mutated_projected_probability"]) == mutated_projected
        and fraction(row["probability_shift"])
        == mutated_projected - base_projected == 2 * a
        and fraction(row["expected_shift"]) == 2 * a
    )


def verify(certificate):
    checks = {}
    try:
        with open(SCHEMA, encoding="utf-8") as handle:
            schema = json.load(handle)
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(certificate)
        checks["strict_schema"] = True
    except Exception:
        checks["strict_schema"] = False

    checks["identity_and_claim_boundary"] = (
        certificate.get("certificate")
        == "REVERSE_PHYSICS_BT_OFFSHELL_JET_OBSTRUCTION_V1"
        and certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC"]
        and certificate.get("lifecycle_state") == "CLASSIFIED"
        and any("LORENTZIAN-CAUSAL" in item
                for item in certificate.get("does_not_establish", []))
    )

    try:
        inputs = certificate["provenance"]["inputs"]
        checks["input_hashes"] = len(inputs) == 3 and all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        )
    except (KeyError, OSError):
        checks["input_hashes"] = False

    algebra = certificate.get("jet_algebra", {})
    rows = algebra.get("dimension_rows", [])
    checks["independent_dimension_and_non_descent"] = (
        len(rows) == 7
        and [row["external_legs"] for row in rows] == list(range(1, 8))
        and all(verify_witness(row) for row in rows)
    )

    complement_checks = []
    for n, key in ((4, "four_leg_complement_rows"),
                   (5, "five_leg_complement_rows")):
        full = (1 << n) - 1
        recorded = algebra.get(key, [])
        ok = len(recorded) == 1 << n
        by_mask = {row["mask"]: row for row in recorded}
        ok = ok and len(by_mask) == 1 << n
        for mask in range(1 << n):
            complement = full ^ mask
            # The pair x_S+x_Sc has exactly two ordered top products.
            row = by_mask.get(mask, {})
            ok = ok and (
                row.get("complement_mask") == complement
                and row.get("union_mask") == full
                and row.get("overlap_mask") == 0
                and fraction(row.get("projector_of_pair_squared", {})) == 2
            )
        complement_checks.append(ok)
    checks["independent_complement_exhaustion"] = all(complement_checks)

    pair = certificate.get("first_nlo_pair", {})
    virtual = pair.get("virtual_channel", {}).get("fixture", {})
    real = pair.get("real_channel", {}).get("fixture", {})
    checks["independent_nlo_pair"] = (
        verify_witness(virtual)
        and verify_witness(real)
        and virtual.get("external_legs") == 4
        and real.get("external_legs") == 5
        and fraction(pair.get("combined_fixture_shift", {}))
        == Fraction(6, 7) + Fraction(10, 11) == Fraction(136, 77)
    )

    disposition = certificate.get("disposition", {})
    checks["fail_closed_disposition"] = (
        disposition.get("offshell_jet_necessity") == "PROVED"
        and disposition.get("descent_to_on_shell_amplitude_class")
        == "DISPROVED"
        and disposition.get(
            "published_on_shell_data_define_first_nlo_probability")
        == "NO"
        and disposition.get("physical_nlo_process_map") == "NOT_CONSTRUCTED"
        and disposition.get("underlying_theory_ambiguous")
        == "NOT_ESTABLISHED"
        and disposition.get("beyond_tree_positivity") == "NOT_ESTABLISHED"
    )

    audit = certificate.get("literature_audit", [])
    checks["public_source_boundary"] = (
        len(audit) == 4
        and sum(row.get("status_on_2026_08_09", "").startswith("TO_APPEAR")
                for row in audit) == 2
        and "Eq. (18)" in pair.get("inference_boundary", "")
    )

    checks["missing_objects_populated"] = (
        len(certificate.get("missing_object_ledger", [])) >= 6
        and "field-redefinition" in " ".join(
            certificate.get("missing_object_ledger", []))
        and "KLN" in " ".join(certificate.get("does_not_establish", []))
    )

    recorded = certificate.get("checks", {})
    checks["producer_checks_recorded"] = (
        recorded.get("ok") is True
        and recorded.get("passed") == recorded.get("total")
        and not recorded.get("failures")
    )
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="independent BT off-shell jet verifier")
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
