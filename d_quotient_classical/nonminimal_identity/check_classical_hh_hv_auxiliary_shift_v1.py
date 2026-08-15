#!/usr/bin/env python3
"""Independent bivariate-jet replay of the classical hh/hv shift tables."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, NamedTuple


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_HH_HV_AUXILIARY_SHIFT_V1.json"
ACTION = ROOT / "covariant_completion/certificates/curved_auxiliary_action_definition.json"
SPLIT = ROOT / "covariant_completion/certificates/curved_auxiliary_canonical_split.json"
PREDECESSOR = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
DIM = 4
SIGNS = (-1, 1, 1, 1)
COORDS = tuple((i, j) for i in range(DIM) for j in range(i, DIM))
MULTI2 = tuple(sorted((x for x in itertools.product(range(3), repeat=DIM) if sum(x) <= 2), key=lambda x: (sum(x), x)))
MULTI1 = tuple(x for x in MULTI2 if sum(x) <= 1)


class P(NamedTuple):
    base: Fraction
    left: Fraction
    right: Fraction
    mixed: Fraction


Z = P(Fraction(0), Fraction(0), Fraction(0), Fraction(0))


def add(*values: P) -> P:
    return P(*(sum((value[index] for value in values), Fraction(0)) for index in range(4)))


def scale(factor: Fraction, value: P) -> P:
    return P(*(factor * entry for entry in value))


def mul(a: P, b: P) -> P:
    return P(
        a.base * b.base,
        a.left * b.base + a.base * b.left,
        a.right * b.base + a.base * b.right,
        a.mixed * b.base + a.left * b.right + a.right * b.left + a.base * b.mixed,
    )


def pmatmul(left: list[list[P]], right: list[list[P]]) -> list[list[P]]:
    return [[add(*(mul(left[i][k], right[k][j]) for k in range(DIM))) for j in range(DIM)] for i in range(DIM)]


def fmatmul(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[sum((left[i][k] * right[k][j] for k in range(DIM)), Fraction(0)) for j in range(DIM)] for i in range(DIM)]


ETA = [[Fraction(SIGNS[i] if i == j else 0) for j in range(DIM)] for i in range(DIM)]


def fscale(value: list[list[Fraction]], factor: Fraction) -> list[list[Fraction]]:
    return [[factor * entry for entry in row] for row in value]


def inverse_coefficients(metric: list[list[P]]) -> list[list[P]]:
    left = [[metric[i][j].left for j in range(DIM)] for i in range(DIM)]
    right = [[metric[i][j].right for j in range(DIM)] for i in range(DIM)]
    qleft = fscale(fmatmul(fmatmul(ETA, left), ETA), Fraction(-1))
    qright = fscale(fmatmul(fmatmul(ETA, right), ETA), Fraction(-1))
    mixed_source = [[sum((qleft[i][k] * right[k][j] + qright[i][k] * left[k][j] for k in range(DIM)), Fraction(0)) for j in range(DIM)] for i in range(DIM)]
    qmixed = fscale(fmatmul(mixed_source, ETA), Fraction(-1))
    return [[P(ETA[i][j], qleft[i][j], qright[i][j], qmixed[i][j]) for j in range(DIM)] for i in range(DIM)]


def background_second(axis: int, other: int, mu: int, nu: int) -> Fraction:
    return Fraction(-int(axis == other and axis > 0 and mu == nu and mu > 0))


def direction(coord_index: int, multiindex: tuple[int, ...]) -> tuple[list[list[Fraction]], list[list[list[Fraction]]], list[list[list[list[Fraction]]]]]:
    value = [[Fraction(0) for _ in range(DIM)] for _ in range(DIM)]
    first = [[[Fraction(0) for _ in range(DIM)] for _ in range(DIM)] for _ in range(DIM)]
    second = [[[[Fraction(0) for _ in range(DIM)] for _ in range(DIM)] for _ in range(DIM)] for _ in range(DIM)]
    i, j = COORDS[coord_index]
    order = sum(multiindex)
    targets: list[list[Fraction]]
    if order == 0:
        targets = [value]
    elif order == 1:
        targets = [first[multiindex.index(1)]]
    else:
        axes = [axis for axis, count in enumerate(multiindex) for _ in range(count)]
        targets = [second[axes[0]][axes[1]]]
        if axes[0] != axes[1]:
            targets.append(second[axes[1]][axes[0]])
    for target in targets:
        target[i][j] = target[j][i] = Fraction(1)
    return value, first, second


def zero_direction():
    return (
        [[Fraction(0) for _ in range(DIM)] for _ in range(DIM)],
        [[[Fraction(0) for _ in range(DIM)] for _ in range(DIM)] for _ in range(DIM)],
        [[[[Fraction(0) for _ in range(DIM)] for _ in range(DIM)] for _ in range(DIM)] for _ in range(DIM)],
    )


def geometry(left, right):
    left_value, left_first, left_second = left
    right_value, right_first, right_second = right
    metric = [[P(ETA[i][j], left_value[i][j], right_value[i][j], Fraction(0)) for j in range(DIM)] for i in range(DIM)]
    metric_first = [[[
        P(Fraction(0), left_first[axis][i][j], right_first[axis][i][j], Fraction(0))
        for j in range(DIM)
    ] for i in range(DIM)] for axis in range(DIM)]
    metric_second = [[[ [
        P(background_second(axis, other, i, j), left_second[axis][other][i][j], right_second[axis][other][i][j], Fraction(0))
        for j in range(DIM)
    ] for i in range(DIM)] for other in range(DIM)] for axis in range(DIM)]
    inverse = inverse_coefficients(metric)
    inverse_first = []
    for axis in range(DIM):
        derivative = pmatmul(pmatmul(inverse, metric_first[axis]), inverse)
        inverse_first.append([[scale(Fraction(-1), derivative[i][j]) for j in range(DIM)] for i in range(DIM)])
    gamma = [[[scale(Fraction(1, 2), add(*(
        mul(inverse[rho][sigma], add(metric_first[mu][sigma][nu], metric_first[nu][sigma][mu], scale(Fraction(-1), metric_first[sigma][mu][nu])))
        for sigma in range(DIM)
    ))) for nu in range(DIM)] for mu in range(DIM)] for rho in range(DIM)]
    dgamma = [[[[scale(Fraction(1, 2), add(*(
        add(
            mul(inverse_first[axis][rho][sigma], add(metric_first[mu][sigma][nu], metric_first[nu][sigma][mu], scale(Fraction(-1), metric_first[sigma][mu][nu]))),
            mul(inverse[rho][sigma], add(metric_second[axis][mu][sigma][nu], metric_second[axis][nu][sigma][mu], scale(Fraction(-1), metric_second[axis][sigma][mu][nu]))),
        ) for sigma in range(DIM)
    ))) for nu in range(DIM)] for mu in range(DIM)] for rho in range(DIM)] for axis in range(DIM)]
    ricci = [[add(
        *(add(dgamma[rho][rho][mu][nu], scale(Fraction(-1), dgamma[nu][rho][mu][rho])) for rho in range(DIM)),
        *(add(
            mul(gamma[rho][rho][lam], gamma[lam][mu][nu]),
            scale(Fraction(-1), mul(gamma[rho][nu][lam], gamma[lam][mu][rho])),
        ) for rho in range(DIM) for lam in range(DIM)),
    ) for nu in range(DIM)] for mu in range(DIM)]
    scalar = add(*(mul(inverse[i][j], ricci[i][j]) for i in range(DIM) for j in range(DIM)))
    shift = [[add(scale(Fraction(2), ricci[i][j]), scale(Fraction(-1, 3), mul(metric[i][j], scalar))) for j in range(DIM)] for i in range(DIM)]
    return gamma, shift


def hh_expected(*, exhaustive: bool) -> tuple[dict[tuple[Any, ...], tuple[str, str]], set[tuple[Any, ...]]]:
    basis = tuple((coord, multi, direction(coord, multi)) for coord in range(len(COORDS)) for multi in MULTI2)
    expected: dict[tuple[Any, ...], tuple[str, str]] = {}
    selected: set[tuple[Any, ...]] = set()
    eligible_index = 0
    for left_index, (left_coord, left_multi, left) in enumerate(basis):
        for right_index in range(left_index, len(basis)):
            right_coord, right_multi, right = basis[right_index]
            if sum(left_multi) + sum(right_multi) not in (0, 2):
                continue
            pair = (f"h_{COORDS[left_coord][0]}{COORDS[left_coord][1]}", left_multi, f"h_{COORDS[right_coord][0]}{COORDS[right_coord][1]}", right_multi)
            use = exhaustive or eligible_index % 31 == 0
            eligible_index += 1
            if not use:
                continue
            selected.add(pair)
            _, shift = geometry(left, right)
            for mu, nu in COORDS:
                coefficient = shift[mu][nu].mixed
                if coefficient:
                    key = (f"f_hat_{mu}{nu}", f"h_{COORDS[left_coord][0]}{COORDS[left_coord][1]}", left_multi, f"h_{COORDS[right_coord][0]}{COORDS[right_coord][1]}", right_multi)
                    expected[key] = (str(coefficient), str(coefficient / 2 if left_index == right_index else coefficient))
    return expected, selected


def hv_expected() -> dict[tuple[Any, ...], tuple[str, str]]:
    zero = zero_direction()
    expected: dict[tuple[Any, ...], tuple[str, str]] = {}
    for coord in range(len(COORDS)):
        for multi in MULTI1:
            gamma, _ = geometry(direction(coord, multi), zero)
            for vector in range(DIM):
                for mu, nu in COORDS:
                    coefficient = -2 * gamma[vector][mu][nu].left
                    if coefficient:
                        key = (f"f_hat_{mu}{nu}", f"h_{COORDS[coord][0]}{COORDS[coord][1]}", multi, f"v_{vector}", (0, 0, 0, 0))
                        expected[key] = (str(coefficient), str(coefficient))
    return expected


def load_table(entries: list[dict[str, object]], kind: str) -> dict[tuple[Any, ...], tuple[str, str]]:
    if kind == "hh":
        return {
            (entry["output_row"], entry["h_left_row"], tuple(entry["h_left_jet"]), entry["h_right_row"], tuple(entry["h_right_jet"])): (entry["second_Frechet_coefficient"], entry["homogeneous_polynomial_coefficient"])
            for entry in entries
        }
    return {
        (entry["output_row"], entry["h_row"], tuple(entry["h_jet"]), entry["v_row"], tuple(entry["v_jet"])): (entry["second_Frechet_coefficient"], entry["homogeneous_polynomial_coefficient"])
        for entry in entries
    }


def canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, object], *, exhaustive: bool = False) -> list[str]:
    tables = value.get("field_component_tables", {})
    hh_entries = tables.get("hh_second_Frechet", {}).get("entries", [])
    hv_entries = tables.get("hv_second_Frechet", {}).get("entries", [])
    hh = load_table(hh_entries, "hh")
    hv = load_table(hv_entries, "hv")
    expected_hh, selected_pairs = hh_expected(exhaustive=exhaustive)
    selected_hh = {key: item for key, item in hh.items() if (key[1], key[2], key[3], key[4]) in selected_pairs}
    expected_hv = hv_expected()
    inputs = value.get("provenance", {}).get("inputs", [])
    pins = {item.get("path"): item.get("sha256") for item in inputs}
    expected_pins = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (ACTION, SPLIT, PREDECESSOR)}
    flags = value.get("claim_flags", {})
    weyl = tables.get("nonlinear_Weyl_second_variation_regression", {})
    hashes = value.get("canonical_hashes", {})
    ok = (
        value.get("result_id") == "CLASSICAL_HH_HV_AUXILIARY_SHIFT_V1"
        and value.get("dependency_tags") == ["LOCAL-ALGEBRAIC"]
        and selected_hh == expected_hh
        and hv == expected_hv
        and len(hh) == len(hh_entries)
        and len(hv) == len(hv_entries)
        and all(sum(key[2]) + sum(key[4]) in (0, 2) and Fraction(item[0]) and Fraction(item[1]) for key, item in hh.items())
        and all(sum(key[2]) == 1 and sum(key[4]) == 0 and Fraction(item[0]) and Fraction(item[1]) for key, item in hv.items())
        and len(hh) == tables.get("hh_second_Frechet", {}).get("nonzero_output_component_coefficients")
        and len(hv) == tables.get("hv_second_Frechet", {}).get("nonzero_output_component_coefficients")
        and tables.get("cylinder_curvature_regression", {}).get("matches_unit_cylinder") is True
        and weyl.get("component_checks") == 1200
        and weyl.get("defects") == 0
        and hashes.get("field_component_tables_sha256") == canonical_digest(tables)
        and hashes.get("hh_entries_sha256") == canonical_digest(hh_entries)
        and hashes.get("hv_entries_sha256") == canonical_digest(hv_entries)
        and pins == expected_pins
        and flags.get("HH_SECOND_FRECHET_COMPONENT_JETS_SERIALIZED") is True
        and flags.get("HV_SECOND_FRECHET_COMPONENT_JETS_SERIALIZED") is True
        and flags.get("CURVED_CYLINDER_ZEROTH_ORDER_TERMS_INCLUDED") is True
        and flags.get("HH_HV_COTANGENT_PARTNERS_SERIALIZED") is False
        and flags.get("FULL_386_QUADRATIC_BV_COTANGENT_LIFT_SERIALIZED") is False
        and flags.get("CLASSICAL_IMPORT_GATE_PASSED") is False
        and flags.get("HADAMARD_STATE_CONSTRUCTED") is False
        and flags.get("QME_RESTORED") is False
    )
    return [] if ok else ["independent bivariate geometry replay, provenance, hash, or fail-closed boundary mismatch"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exhaustive", action="store_true", help="replay every eligible hh input pair (Tier 2, about 100 seconds)")
    args = parser.parse_args()
    value = json.loads(RESULT.read_text())
    errors = check(value, exhaustive=args.exhaustive)
    tables = value["field_component_tables"]
    mode = "EXHAUSTIVE" if args.exhaustive else "FAST_STRATIFIED"
    ok = not errors
    print(f"CLASSICAL_HH_HV_AUXILIARY_SHIFT_V1_INDEPENDENT_BIVARIATE_REPLAY_{mode}: " + ("PASS" if ok else "FAIL"))
    if ok:
        print(json.dumps({"hh_coefficients": len(tables["hh_second_Frechet"]["entries"]), "hh_pairs_replayed": 1875 if args.exhaustive else 61, "hv_coefficients": len(tables["hv_second_Frechet"]["entries"]), "weyl_component_checks": tables["nonlinear_Weyl_second_variation_regression"]["component_checks"]}, sort_keys=True))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
