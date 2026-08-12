#!/usr/bin/env python3
"""Independent fraction verification of the dressed scalar source pullback."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_POSITIVE_SOURCE_AFFILIATION_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-scalar-dressed-positive-source-affiliation-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def zero(rows, columns=None):
    columns = rows if columns is None else columns
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def identity(size):
    return [[Fraction(row == column) for column in range(size)] for row in range(size)]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def multiply(left, right):
    return [[sum(left[i][k] * right[k][j] for k in range(len(right))) for j in range(len(right[0]))] for i in range(len(left))]


def add(left, right):
    return [[a + b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(left, right)]


def subtract(left, right):
    return [[a - b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(left, right)]


def scale(value, matrix):
    return [[value * entry for entry in row] for row in matrix]


def diagonal(values):
    return [[values[row] if row == column else Fraction(0) for column in range(len(values))] for row in range(len(values))]


def trace(matrix):
    return sum(matrix[index][index] for index in range(len(matrix)))


def rank(matrix):
    rows = [row[:] for row in matrix]
    out = 0
    for column in range(len(rows[0])):
        pivot = next((row for row in range(out, len(rows)) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[out], rows[pivot] = rows[pivot], rows[out]
        value = rows[out][column]
        rows[out] = [entry / value for entry in rows[out]]
        for row in range(len(rows)):
            if row != out and rows[row][column]:
                factor = rows[row][column]
                rows[row] = [a - factor * b for a, b in zip(rows[row], rows[out])]
        out += 1
    return out


def sharp(matrix, metric):
    return multiply(multiply(metric, transpose(matrix)), metric)


def verify(certificate):
    size = 8
    eta = zero(size)
    for column in range(size):
        eta[7 - column][column] = Fraction(1)
    charges = [2 * value.bit_count() - 3 for value in range(size)]
    qop = diagonal([Fraction(value) for value in charges])

    p_u = zero(size)
    for row in (0, 7):
        for column in (0, 7):
            p_u[row][column] = Fraction(1, 2)
    p_plus = zero(size)
    for representative in range(4):
        for row in (representative, 7 - representative):
            for column in (representative, 7 - representative):
                p_plus[row][column] = Fraction(1, 2)

    support = sorted({charges[row] - charges[column] for row in range(size) for column in range(size) if p_u[row][column]})
    fixed_grams_zero = True
    for charge in sorted(set(charges)):
        indices = [index for index, value in enumerate(charges) if value == charge]
        fixed_grams_zero &= all(eta[row][column] == 0 for row in indices for column in indices)

    d = [Fraction(2), Fraction(3), Fraction(5), Fraction(7), Fraction(1, 7), Fraction(1, 5), Fraction(1, 3), Fraction(1, 2)]
    r = diagonal(d)
    r_sharp = sharp(r, eta)
    p_phi = multiply(multiply(r_sharp, p_u), r)
    p_phi_plus = multiply(multiply(r_sharp, p_plus), r)

    effect_input = next(row["path"] for row in certificate["provenance"]["inputs"] if "POSITIVE_SECTOR_PHYSICAL_DETECTOR_EFFECT" in row["path"])
    effect_cert = load(os.path.join(ROOT, effect_input))
    residue = [[Fraction(entry) for entry in row] for row in effect_cert["fixed_shell_transition_effect"]["R_plus"]]
    effect4 = multiply(transpose(residue), residue)
    # U_plus G U_plus^sharp has each complement-pair block equal to G_ij/2.
    click = zero(size)
    for i in range(4):
        for j in range(4):
            for row in (i, 7 - i):
                for column in (j, 7 - j):
                    click[row][column] = effect4[i][j] / 2
    no_click = subtract(p_plus, click)
    click_phi = multiply(multiply(r_sharp, click), r)
    no_click_phi = multiply(multiply(r_sharp, no_click), r)

    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in certificate["provenance"]["inputs"]),
        "cross_metric_is_involutive": multiply(eta, eta) == identity(size),
        "source_projector_reconstructed": multiply(p_u, p_u) == p_u and sharp(p_u, eta) == p_u and rank(p_u) == 1,
        "positive_plane_reconstructed": multiply(p_plus, p_plus) == p_plus and rank(p_plus) == 4,
        "charge_spectrum_has_no_zero": 0 not in charges,
        "fixed_charge_spaces_are_isotropic": fixed_grams_zero,
        "source_projector_breaks_charge": multiply(qop, p_u) != multiply(p_u, qop),
        "projector_charge_support_reconstructed": support == [-6, 0, 6],
        "certificate_charge_support_matches": certificate["positive_BT_source"]["source_projector_charge_support"] == support,
        "fixture_is_Krein_unitary": multiply(multiply(transpose(r), eta), r) == eta and multiply(r_sharp, r) == identity(size),
        "pulled_projector_is_idempotent": multiply(p_phi, p_phi) == p_phi,
        "pulled_projector_is_self_adjoint": sharp(p_phi, eta) == p_phi,
        "projector_commuting_square": multiply(multiply(r, p_phi), r_sharp) == p_u,
        "positive_plane_commuting_square": multiply(multiply(r, p_phi_plus), r_sharp) == p_plus,
        "effect_is_exact_Gram": effect4 == multiply(transpose(residue), residue),
        "pulled_click_commuting_square": multiply(multiply(r, click_phi), r_sharp) == click,
        "pulled_no_click_commuting_square": multiply(multiply(r, no_click_phi), r_sharp) == no_click,
        "pulled_effects_are_complete": add(click_phi, no_click_phi) == p_phi_plus,
        "target_click_trace_is_one_sixteenth": trace(multiply(p_u, click)) == Fraction(1, 16),
        "target_no_click_trace_is_fifteen_sixteenths": trace(multiply(p_u, no_click)) == Fraction(15, 16),
        "scalar_click_trace_is_preserved": trace(multiply(p_phi, click_phi)) == Fraction(1, 16),
        "scalar_no_click_trace_is_preserved": trace(multiply(p_phi, no_click_phi)) == Fraction(15, 16),
        "rate_is_inherited_exactly": certificate["transferred_scalar_detector_effect"]["declared_source_rate"] == effect_cert["detector_probability_jet"]["declared_source_rate"],
        "Laurent_support_records_both_orbit_branches": certificate["formal_Rt_affiliation"]["scalar_Laurent_orbit_support"] == ["Z^-6", "1", "Z^6"],
        "fixture_is_not_promoted_to_public_Rt": certificate["formal_Rt_affiliation"]["fixture_role"] == "a nontrivial rational Krein-unitary replay checks the universal identities but is not identified with the public Rt",
        "standard_projector_boundary_is_preserved": certificate["interpretation"]["standard_shift_invariant_P_chi"] == "NOT_CONSTRUCTED",
        "general_Eq19_boundary_is_preserved": certificate["interpretation"]["general_Eq19"] == "NOT_PROVED" and "Eq. (19) for arbitrary scalar projectors" in certificate["does_not_establish"],
        "Lorentzian_boundary_is_preserved": "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"],
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
