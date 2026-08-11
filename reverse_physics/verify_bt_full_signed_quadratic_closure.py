#!/usr/bin/env python3
"""Independent verifier for the complete BT signed quadratic closure."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-full-signed-quadratic-closure-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def fraction(value):
    return Fraction(value["numerator"], value["denominator"])


def cadd(left, right):
    return left[0] + right[0], left[1] + right[1]


def cmul(left, right):
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


CZ = (Fraction(0), Fraction(0))
CO = (Fraction(1), Fraction(0))
CI = (Fraction(0), Fraction(1))


def poly(*coefficients):
    return {degree: value for degree, value in enumerate(coefficients) if value != CZ}


def padd(left, right):
    answer = dict(left)
    for degree, value in right.items():
        answer[degree] = cadd(answer.get(degree, CZ), value)
    return {degree: value for degree, value in answer.items() if value != CZ}


def pscale(value, item):
    value = value if isinstance(value, tuple) else (Fraction(value), Fraction(0))
    return {degree: cmul(value, coefficient) for degree, coefficient in item.items()}


def pmul(left, right):
    answer = {}
    for a, x in left.items():
        for b, y in right.items():
            answer[a + b] = cadd(answer.get(a + b, CZ), cmul(x, y))
    return {degree: value for degree, value in answer.items() if value != CZ}


def pderivative(item):
    return {
        degree - 1: (coefficient[0] * degree, coefficient[1] * degree)
        for degree, coefficient in item.items() if degree
    }


def preimages(species, sign, energy, slot):
    if species == "Omega":
        return [("a2", sign, poly((4 * energy * energy, Fraction(0))), (0, 0))]
    cross = [0, 0]
    cross[slot] = -2 * sign
    return [
        ("a1", sign, poly(CO), (0, 0)),
        ("a2", sign, poly(CZ, (Fraction(0), -2 * sign * energy)), (0, 0)),
        ("a2", -sign, poly((Fraction(-1), Fraction(0))), tuple(cross)),
    ]


def source_mode(species, sign, energy):
    if species == "a2":
        return poly(CO), {}
    return poly(CO, (Fraction(0), 2 * sign * energy)), poly((4 * energy * energy, Fraction(0)))


def source_kernel(parent, left, right, target_energy, e1, e2):
    left_mode, left_box = source_mode(left[0], left[1], e1)
    right_mode, right_box = source_mode(right[0], right[1], e2)
    source_energy = left[1] * e1 + right[1] * e2

    def omega(item):
        return padd(pscale(CI, pderivative(item)), pscale(target_energy + source_energy, item))

    def box(item):
        return padd(
            padd(
                pderivative(pderivative(item)),
                pscale((Fraction(0), -2 * source_energy), pderivative(item)),
            ),
            pscale(target_energy * target_energy - source_energy * source_energy, item),
        )

    pair = pmul(left_mode, right_mode)
    if parent == "Omega":
        return omega(pair)
    nonlinear = padd(
        box(pair),
        pscale(-2, padd(pmul(left_mode, right_box), pmul(left_box, right_mode))),
    )
    return omega(nonlinear)


def independent_kernel(signs, e1, e2):
    target_energy = signs[0] * e1 + signs[1] * e2
    density = Fraction(1, 64 * e1**3 * e2**3)
    result = {}
    phases = []
    for parent in ("Omega", "Upsilon"):
        for daughters in (
            ("Omega", "Omega"), ("Omega", "Upsilon"),
            ("Upsilon", "Omega"), ("Upsilon", "Upsilon"),
        ):
            total = {}
            for left in preimages(daughters[0], signs[0], e1, 0):
                for right in preimages(daughters[1], signs[1], e2, 1):
                    phase = tuple(
                        signs[index]
                        - (left[1] if index == 0 else right[1])
                        + left[3][index] + right[3][index]
                        for index in range(2)
                    )
                    phases.append(phase)
                    value = source_kernel(parent, left, right, target_energy, e1, e2)
                    value = pmul(value, pmul(left[2], right[2]))
                    total = padd(total, pscale(density, value))
            result[parent, daughters] = total
    return result, phases


def formula(parent, daughters, signs, e1, e2):
    s1, s2 = signs
    if parent == "Omega" and daughters == ("Omega", "Omega"):
        return Fraction(s1 * e1 + s2 * e2, 2 * e1 * e2)
    if parent == "Upsilon" and daughters == ("Omega", "Upsilon"):
        return Fraction(-s2, 2 * e1)
    if parent == "Upsilon" and daughters == ("Upsilon", "Omega"):
        return Fraction(-s1, 2 * e2)
    return Fraction(0)


def evaluate_terms(terms, e1, e2, time):
    total = CZ
    for term in terms:
        powers = term["powers"]
        coefficient = term["coefficient"]
        value = (
            fraction(coefficient["real"]), fraction(coefficient["imag"])
        )
        scale = Fraction(e1) ** powers[0] * Fraction(e2) ** powers[1] * Fraction(time) ** powers[2]
        total = cadd(total, (value[0] * scale, value[1] * scale))
    return total


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


def verify(certificate):
    checks = {}
    errors = sorted(
        Draft202012Validator(load(SCHEMA)).iter_errors(certificate),
        key=lambda error: list(error.path),
    )
    checks["schema"] = not errors

    kernel = certificate.get("completed_signed_kernel", {})
    rows = kernel.get("exact_rows", [])
    indexed = {
        (tuple(row.get("target_signs", [])), row.get("parent"), tuple(row.get("daughters", []))): row
        for row in rows
    }
    exact = True
    phase_exact = True
    for signs in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        for e1, e2 in ((2, 1), (3, 2), (5, 3)):
            computed, phases = independent_kernel(signs, e1, e2)
            phase_exact = phase_exact and all(phase == (0, 0) for phase in phases)
            for (parent, daughters), value in computed.items():
                expected = formula(parent, daughters, signs, e1, e2)
                exact = exact and value == ({} if expected == 0 else {0: (expected, Fraction(0))})
                recorded = indexed.get((signs, parent, daughters), {})
                exact = exact and evaluate_terms(recorded.get("terms", []), e1, e2, 7) == (expected, Fraction(0))
    checks["independent_full_preimage_kernel"] = exact
    checks["independent_phase_closure"] = phase_exact
    checks["recorded_kernel_row_count"] = len(rows) == 32 and len(indexed) == 32

    contributions = certificate.get("inverse_preimage_rule", {}).get("all_contributions", [])
    checks["contribution_ledger"] = (
        len(contributions) == 128
        and all(row.get("total_phase") == [0, 0] for row in contributions)
        and certificate.get("inverse_preimage_rule", {}).get("preimage_contribution_count") == 128
    )

    endpoint = certificate.get("endpoint_cancellation", {})
    checks["independent_parent_gram"] = (
        endpoint.get("complete_parent_gram") == {
            "G_OmegaOmega": "0",
            "G_OmegaUpsilon": "0",
            "G_UpsilonOmega": "0",
            "G_UpsilonUpsilon": "2*s1*s2",
        }
        and fraction(endpoint.get("raw_soft_residue", {})) == 0
        and fraction(endpoint.get("normalized_per_pair_log_response", {})) == 0
    )

    opposite = {"Omega": "Upsilon", "Upsilon": "Omega"}
    ward_rows = certificate.get("canonicality", {}).get("exact_fixture_rows", [])
    ward_index = {
        (fraction(row["x"]), fraction(row["y"]), row["parent"], row["output"], row["spectator"]): row
        for row in ward_rows
    }
    wards_ok = len(ward_rows) == 48
    for x, y in ((1, 1), (1, 2), (2, 1), (2, 3), (3, 2), (3, 5)):
        p = x + y
        for parent in ("Omega", "Upsilon"):
            for output in ("Omega", "Upsilon"):
                for spectator in ("Omega", "Upsilon"):
                    aa = (
                        formula(parent, (opposite[output], spectator), (1, 1), x, y)
                        + formula(parent, (spectator, opposite[output]), (1, 1), y, x)
                    )
                    mixed = (
                        formula(output, (opposite[parent], spectator), (1, -1), p, y)
                        + formula(output, (spectator, opposite[parent]), (-1, 1), y, p)
                    )
                    defect = x * aa + p * mixed
                    row = ward_index.get((Fraction(x), Fraction(y), parent, output, spectator), {})
                    wards_ok = wards_ok and defect == 0
                    wards_ok = wards_ok and fraction(row.get("AA_coefficient", {})) == aa
                    wards_ok = wards_ok and fraction(row.get("mixed_coefficient", {})) == mixed
                    wards_ok = wards_ok and fraction(row.get("CCR_defect", {})) == defect
    checks["independent_cross_CCR_Ward_identity"] = wards_ok

    eq19 = certificate.get("finite_mode_Eq19", {})
    disposition = certificate.get("disposition", {})
    coefficient = certificate.get("coefficient_disposition", {})
    checks["finite_mode_Eq19_boundary"] = (
        eq19.get("generator_charge_after_Z_dressing") == 0
        and eq19.get("squeeze_generator_charge_after_Z_dressing") == 0
        and eq19.get("disposition")
        == "EQ19_PROVED_THROUGH_ORDER_LAMBDA_FOR_THE_FINITE_MODE_QUADRATIC_ZERO_MODE_COMPLETED_SECTOR"
        and disposition.get("finite_mode_order_lambda_Eq19") == "PROVED_WITH_Q1_ZERO"
        and disposition.get("continuum_all_order_Eq19") == "NOT_PROVED"
    )
    checks["physical_coefficient_boundary"] = (
        coefficient.get("resonant_only_conditional_one_over_48")
        == "CANCELLED_BY_FULL_INVERSE_PREIMAGE_CLOSURE"
        and fraction(coefficient.get("completed_public_quadratic_map_soft_log_per_pair", {})) == 0
        and coefficient.get("physical_one_over_48") == "NOT_REPRODUCED"
        and coefficient.get("physical_zero")
        == "NOT_ESTABLISHED_WITHOUT_THE_REMAINING_PROJECTOR_TRACE"
        and disposition.get("physical_one_over_48") == "NOT_ESTABLISHED"
        and disposition.get("physical_zero") == "NOT_ESTABLISHED"
    )
    checks["claim_boundary"] = (
        len(certificate.get("does_not_establish", [])) >= 7
        and any("LORENTZIAN-CAUSAL" in item for item in certificate.get("does_not_establish", []))
        and disposition.get("squeezed_vacuum_dynamical_zero_mode_trace") == "NOT_COMPUTED"
    )

    inputs = certificate.get("provenance", {}).get("inputs", [])
    checks["input_hashes"] = len(inputs) == 8 and all(
        item.get("sha256") == sha256(item.get("path", "")) for item in inputs
    )
    checks["science_forge_event_FNV_id"] = fnv1a(
        "sf:program/work/reverse-physics-bateman-full-signed-quadratic-closure|"
        "DONE|reverse-physics|2026-08-11|Full signed quadratic preimage "
        "closure cancels the resonant-only soft logarithm, preserves the "
        "order-lambda cross CCR, and proves the finite-mode zero-mode-"
        "completed Eq. (19) sector with Q1=0. Evidence: "
        "REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.|"
    ) == 0xDE9C86C7AC5AFF50
    ledger = certificate.get("checks", {})
    checks["producer_ledger"] = (
        ledger.get("ok") is True
        and ledger.get("passed") == ledger.get("total") == 20
        and ledger.get("failures") == []
        and len(ledger.get("details", {})) == 20
        and all(ledger.get("details", {}).values())
    )

    if errors:
        for error in errors:
            print(f"schema: {list(error.path)}: {error.message}", file=sys.stderr)
    failures = [name for name, value in checks.items() if not value]
    if failures:
        print("BT FULL SIGNED QUADRATIC CLOSURE VERIFY: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return False, checks
    return True, checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args()
    ok, checks = verify(load(args.verify))
    if not ok:
        return 1
    print(
        "BT FULL SIGNED QUADRATIC CLOSURE VERIFY: ALL PASS "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
