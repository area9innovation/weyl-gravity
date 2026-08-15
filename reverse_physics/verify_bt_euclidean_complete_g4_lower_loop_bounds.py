#!/usr/bin/env python3
"""Independent verifier for the BT complete-g4 lower-loop theorem."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_LOWER_LOOP_BOUNDS_V1.json")
SCHEMA_PATH = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-euclidean-complete-g4-lower-loop-bounds-v1.schema.json")
ATLAS_PATH = os.path.join(ROOT, "reverse_physics/data/bt_euclidean_complete_g4_lower_loop_atlas_v1.json")
DATA_PATH = os.path.join(ROOT, "reverse_physics/data/bt_euclidean_complete_g4_lower_loop_bounds_v1.json")
UPSTREAM_PATH = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_TWO_PAIR_NONCANCELLATION_V1.json")
Poly = dict[int, Fraction]


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def fraction(value: dict) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def clean(poly: Poly) -> Poly:
    return {power: value for power, value in poly.items() if value}


def add_poly(left: Poly, right: Poly) -> Poly:
    result = dict(left)
    for power, value in right.items():
        result[power] = result.get(power, Fraction()) + value
    return clean(result)


def mul_poly(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for a, x in left.items():
        for b, y in right.items():
            result[a + b] = result.get(a + b, Fraction()) + x * y
    return clean(result)


def scale_poly(poly: Poly, scalar: Fraction | int) -> Poly:
    return clean({power: value * scalar for power, value in poly.items()})


def power_poly(poly: Poly, exponent: int) -> Poly:
    result = {0: Fraction(1)}
    for _ in range(exponent):
        result = mul_poly(result, poly)
    return result


def difference(power: int) -> Poly:
    if power == 0:
        return {}
    return {power: Fraction(1), 0: Fraction(-1)}


def b_symbol(multiples: list[int]) -> Poly:
    forward = {0: Fraction(1)}
    backward = {0: Fraction(1)}
    for multiple in multiples:
        forward = mul_poly(forward, difference(multiple))
        backward = mul_poly(backward, difference(-multiple))
    return add_poly(forward, backward)


def direct_kernel(degree: int, arguments: list[list[int]]) -> Poly:
    momenta = [form[2] for form in arguments]
    numerator: Poly = {}
    for singled in range(degree):
        rest = [momenta[index] for index in range(degree) if index != singled]
        numerator = add_poly(
            numerator, mul_poly(b_symbol([momenta[singled]]), b_symbol(rest))
        )
    partitions = []
    if degree == 4:
        partitions = [(0, 1), (0, 2), (0, 3)]
    elif degree == 5:
        partitions = list(itertools.combinations(range(5), 2))
    for left in partitions:
        selected = set(left)
        numerator = add_poly(
            numerator,
            mul_poly(
                b_symbol([momenta[index] for index in left]),
                b_symbol(
                    [
                        momenta[index]
                        for index in range(degree)
                        if index not in selected
                    ]
                ),
            ),
        )
    return scale_poly(numerator, Fraction(1, math.factorial(degree)))


def direct_omega(multiple: int) -> Poly:
    require(multiple != 0, "zero dispersion entered rational verifier")
    return {0: Fraction(2), multiple: Fraction(-1), -multiple: Fraction(-1)}


def add_rational(left, right):
    ln, ld = left
    rn, rd = right
    return add_poly(mul_poly(ln, rd), mul_poly(rn, ld)), mul_poly(ld, rd)


def verify_zero_loop(rows: list[dict]) -> None:
    total = ({}, {0: Fraction(1)})
    for row in rows:
        numerator = {0: fraction(row["coefficient"])}
        for vertex in row["kernels"]:
            numerator = mul_poly(
                numerator, direct_kernel(vertex["degree"], vertex["arguments"])
            )
        denominator = power_poly(
            direct_omega(1), 2 * row["omega_p_inverse_square_power"]
        )
        for form in row["propagators"]:
            denominator = mul_poly(
                denominator, power_poly(direct_omega(form[2]), 2)
            )
        total = add_rational(total, (numerator, denominator))

    w = direct_omega(1)
    target_numerator: Poly = {}
    for exponent, coefficient in enumerate(
        (63936, -57456, 16128, -840, -780, 561, -170, 17)
    ):
        target_numerator = add_poly(
            target_numerator, scale_poly(power_poly(w, exponent), coefficient)
        )
    target_denominator = scale_poly(
        mul_poly(
            power_poly(w, 2),
            mul_poly(
                add_poly({0: Fraction(4)}, scale_poly(w, -1)),
                power_poly(add_poly({0: Fraction(3)}, scale_poly(w, -1)), 2),
            ),
        ),
        32,
    )
    require(
        mul_poly(total[0], target_denominator)
        == mul_poly(target_numerator, total[1]),
        "ten-row zero-loop rational identity failed",
    )
    require(Fraction(63936, 32 * 4 * 9) == Fraction(111, 2), "soft residue failed")
    require(63936 - 57456 - 840 - 780 - 170 == 4690 > 0, "positivity ledger failed")


def kind(form: list[int]) -> tuple[str, int]:
    q, r, p = form
    require(r == 0, "unexpected second loop form")
    return ("Q", p * q) if q else ("W", abs(p))


def ledger_add(ledger, key, amount) -> None:
    ledger[key] = ledger.get(key, Fraction()) + amount


def collinear(vertex: dict) -> bool:
    return vertex["degree"] == 3 and all(
        form[0] == form[1] == 0 for form in vertex["arguments"]
    )


def verify_collinear_identity() -> None:
    arguments = [[0, 0, -2], [0, 0, 1], [0, 0, 1]]
    cubic = direct_kernel(3, arguments)
    # 6*t^4*K3=(t-1)^6*(t+1)^2 and
    # omega(p)^3=-(t-1)^6/t^3.
    left = scale_poly(mul_poly({4: Fraction(1)}, cubic), 6)
    right = mul_poly(power_poly(difference(1), 6), power_poly(add_poly({1: Fraction(1)}, {0: Fraction(1)}), 2))
    require(left == right, "collinear cubic Laurent identity failed")


def row_ledger(row: dict, record: dict) -> dict:
    ledger = {}
    ledger_add(ledger, ("W", 1), Fraction(-2 * row["omega_p_inverse_square_power"]))
    for form in row["propagators"]:
        ledger_add(ledger, kind(form), Fraction(-2))
    choices = [tuple(pair) for pair in record["generic_cubic_selected_argument_pairs"]]
    choice_index = 0
    for vertex in row["kernels"]:
        if collinear(vertex):
            ledger_add(ledger, ("W", 1), Fraction(3))
        elif vertex["degree"] == 3:
            require(choice_index < len(choices), "missing cubic selection")
            pair = choices[choice_index]
            choice_index += 1
            require(len(pair) == 2 and all(index in (0, 1, 2) for index in pair), "bad cubic selection")
            for index in pair:
                ledger_add(ledger, kind(vertex["arguments"][index]), Fraction(1))
        else:
            require(vertex["degree"] in (4, 5), "bad vertex degree")
            for form in vertex["arguments"]:
                ledger_add(ledger, kind(form), Fraction(1, 2))
    require(choice_index == len(choices), "extra cubic selection")
    return {key: value for key, value in ledger.items() if value}


def four_power(exponent: Fraction) -> Fraction:
    require(exponent >= 0 and exponent.denominator in (1, 2), "bad half power")
    return Fraction(2 ** (2 * exponent).numerator)


def verify_one_loop(rows: list[dict], records: list[dict], summary: dict) -> None:
    require(len(rows) == len(records) == 27, "one-loop row count failed")
    total = Fraction()
    beta_counts = {1: 0, 2: 0, 3: 0}
    for index, (row, record) in enumerate(zip(rows, records)):
        require(record["atlas_row_zero_based"] == index, "record order failed")
        ledger = row_ledger(row, record)
        encoded = [
            (entry["kind"], entry["shift"], fraction(entry["exponent"]))
            for entry in record["combined_exponent_ledger"]
        ]
        require(encoded == [(a, b, c) for (a, b), c in sorted(ledger.items())], "stored exponent ledger failed")
        external = sum(value for (name, _), value in ledger.items() if name == "W")
        beta = sum(-value for (name, _), value in ledger.items() if name == "Q" and value < 0)
        net = external + min(Fraction(), Fraction(2) - beta)
        require(fraction(record["external_omega_power"]) == external, "external exponent failed")
        require(fraction(record["negative_shifted_weight_sum"]) == beta, "weight sum failed")
        require(fraction(record["net_shell_power"]) == net >= 0, "shell power failed")
        require(beta in beta_counts, "unexpected weight sum")
        beta_counts[int(beta)] += 1

        constant = abs(fraction(row["coefficient"]))
        for vertex in row["kernels"]:
            constant *= {3: Fraction(2, 3), 4: Fraction(56, 3), 5: Fraction(8)}[vertex["degree"]]
        for (name, shift), exponent in ledger.items():
            if name == "W" and shift == 2 and exponent > 0:
                constant *= four_power(exponent)
            elif name == "Q" and exponent > 0:
                constant *= 8**exponent.numerator if exponent.denominator == 1 else 3 ** (2 * exponent).numerator
        if beta == 3:
            require(external >= 1, "weight-three compensation failed")
            constant *= Fraction(1215, 2048) * four_power(external - 1)
            require(record["bound_multiplier_uses_pi_squared"], "missing pi^2 marker")
        elif beta == 2:
            constant *= Fraction(405, 256) * four_power(external)
        else:
            constant *= Fraction(405, 64) * four_power(external)
        require(fraction(record["bound_multiplier"]) == constant, "row constant failed")
        total += constant

    require(beta_counts == {1: 4, 2: 15, 3: 8}, "weight-count split failed")
    require(summary["weight_sum_counts"] == {str(k): v for k, v in beta_counts.items()}, "stored weight counts failed")
    require(total == Fraction(900315, 4), "common multiplier failed")
    require(fraction(summary["common_bound_multiplier"]) == total, "stored multiplier failed")

    for m in range(1, 65):
        shell = (2 * m + 1) ** 4 - (2 * m - 1) ** 4
        require(shell == 64 * m**3 + 16 * m <= 80 * m**3, "four-dimensional shell failed")
    require(5 * 81 == 405, "five-center first shell failed")
    require(Fraction(405, 16 * 4) == Fraction(405, 64), "weight-one constant failed")
    require(Fraction(405, 16**2) == Fraction(405, 256), "weight-two constant failed")
    require(Fraction(405 * 3, 2 * 16**3) == Fraction(1215, 8192), "weight-three constant failed")


def verify(path: str = CERT_PATH) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
        errors = list(Draft202012Validator(schema).iter_errors(certificate))
        require(not errors, errors[0].message if errors else "schema failure")
        with open(ATLAS_PATH, encoding="utf-8") as handle:
            atlas = json.load(handle)
        with open(DATA_PATH, encoding="utf-8") as handle:
            data = json.load(handle)
        with open(UPSTREAM_PATH, encoding="utf-8") as handle:
            upstream = json.load(handle)

        require(all(atlas["checks"].values()), "atlas check failed")
        require(atlas["volume_scope"]["lengths"] == "every integer L>=7", "atlas volume scope failed")
        require(atlas["statistics"]["0"]["maximum_component_source_absolute_value"] == 6, "rank-zero source maximum failed")
        require(atlas["statistics"]["1"]["maximum_component_source_absolute_value"] == 5, "rank-one source maximum failed")
        zero_rows = [row for row in atlas["surviving_integrands"] if row["loop_rank"] == 0]
        one_rows = [row for row in atlas["surviving_integrands"] if row["loop_rank"] == 1]
        require(len(zero_rows) == 10 and len(one_rows) == 27, "atlas split failed")
        verify_zero_loop(zero_rows)
        verify_collinear_identity()
        verify_one_loop(one_rows, data["one_loop_rows"], data["one_loop_summary"])

        require(upstream["comparison"]["combined"] == "c_4+c_7<0", "two-loop sign failed")
        require(data["complete_leading_power"]["status"] == "COMPLETE_M4_LEADING_POWER_COEFFICIENT_STRICTLY_NEGATIVE", "complete leading-power status failed")
        require(certificate["zero_loop"] == data["zero_loop"], "zero-loop projection failed")
        require(certificate["collinear_cubic_identity"] == data["collinear_cubic_identity"], "collinear projection failed")
        require(certificate["one_loop_shell_lemma"] == data["one_loop_shell_lemma"], "shell-lemma projection failed")
        require(certificate["one_loop_summary"] == data["one_loop_summary"], "one-loop projection failed")
        require(certificate["complete_leading_power"] == data["complete_leading_power"], "certificate projection failed")
        require(certificate["data_sha256"] == file_hash(certificate["data"]), "data hash failed")
        require(certificate["atlas_sha256"] == file_hash(certificate["atlas"]), "atlas hash failed")
        require(certificate["producer_sha256"] == file_hash(certificate["producer"]), "producer hash failed")
        for item in certificate["provenance"]["inputs"]:
            require(item["sha256"] == file_hash(item["path"]), f"input hash failed: {item['path']}")
        require(all(certificate["checks"].values()), "certificate check failed")
        require("LORENTZIAN-CAUSAL" not in certificate["dependency_tags"], "Lorentzian promotion failed")
        return True
    except (OSError, ValueError, KeyError, TypeError, VerificationError, json.JSONDecodeError) as error:
        print(f"verification failed: {error}", file=sys.stderr)
        return False


def main() -> int:
    return 0 if verify() else 1


if __name__ == "__main__":
    raise SystemExit(main())
