#!/usr/bin/env python3
"""Independently verify the BT torus Green-tail counterfamily certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from fractions import Fraction
from itertools import product

import jsonschema


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERTIFICATE = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_GREEN_TAIL_COUNTERFAMILY_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-green-tail-counterfamily-v1.schema.json",
)
SOURCE_COMMIT = "7b547b73f33b039220dd542db49fb7a14df36450"


def file_hash(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def eliminate(coefficients: list[list[Fraction]], values: list[Fraction]) -> list[Fraction]:
    rows = [row[:] + [value] for row, value in zip(coefficients, values)]
    dimension = len(rows)
    for column in range(dimension):
        pivot = None
        for candidate in range(column, dimension):
            if rows[candidate][column] != 0:
                pivot = candidate
                break
        if pivot is None:
            raise ArithmeticError("singular rational fixture system")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]
        for entry in range(column, dimension + 1):
            rows[column][entry] /= divisor
        for candidate in range(dimension):
            if candidate == column:
                continue
            multiplier = rows[candidate][column]
            if multiplier == 0:
                continue
            for entry in range(column, dimension + 1):
                rows[candidate][entry] -= multiplier * rows[column][entry]
    return [row[dimension] for row in rows]


def reconstruct_fixture() -> dict[str, object]:
    side = 4

    def canonical(point: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
        distances = [min(value % side, (-value) % side) for value in point]
        distances.sort()
        return tuple(distances)  # type: ignore[return-value]

    orbit_list = tuple(
        tuple(sorted(values))
        for values in product(range(3), repeat=4)
        if tuple(values) == tuple(sorted(values))
    )
    orbit_index = {orbit: number for number, orbit in enumerate(orbit_list)}
    multiplicity: list[int] = []
    adjacency: list[dict[int, int]] = []
    all_points = tuple(product(range(side), repeat=4))
    for orbit in orbit_list:
        multiplicity.append(sum(canonical(point) == orbit for point in all_points))
        counts: Counter[int] = Counter()
        for axis in range(4):
            for step in (-1, 1):
                point = list(orbit)
                point[axis] = (point[axis] + step) % side
                counts[orbit_index[canonical(tuple(point))]] += 1
        adjacency.append(dict(counts))

    lam = Fraction(2)
    epsilon = Fraction(1, 8)
    delta = Fraction(1, 2)
    source = [
        Fraction(8) * lam**3 / (lam**2 + sum(value**2 for value in orbit)) ** 3
        for orbit in orbit_list
    ]
    source_mean = (
        sum(
            (count * value for count, value in zip(multiplicity, source)),
            Fraction(),
        )
        / len(all_points)
    )
    dimension = len(orbit_list)
    coefficients: list[list[Fraction]] = []
    values: list[Fraction] = []
    for row in range(dimension - 1):
        equation = [Fraction() for _ in range(dimension)]
        equation[row] += 8
        for target, count in adjacency[row].items():
            equation[target] -= count
        coefficients.append(equation)
        values.append(source[row] - source_mean)
    coefficients.append([Fraction(value) for value in multiplicity])
    values.append(Fraction())
    potential = eliminate(coefficients, values)
    potential_minimum = min(potential)
    base = [value - potential_minimum + epsilon for value in potential]
    sine = (Fraction(), Fraction(1), Fraction(), Fraction(-1))
    field = [
        base[orbit_index[canonical(point)]]
        * (
            1
            + delta
            * sine[point[0]]
            * sine[point[1]]
            * sine[point[2]]
            * sine[point[3]]
        )
        for point in all_points
    ]

    def number(point: tuple[int, int, int, int]) -> int:
        return ((point[0] * side + point[1]) * side + point[2]) * side + point[3]

    neighbor_rows: list[list[int]] = [[] for _ in all_points]
    for row, point in enumerate(all_points):
        for axis in range(4):
            for step in (-1, 1):
                adjacent_point = list(point)
                adjacent_point[axis] = (adjacent_point[axis] + step) % side
                neighbor_rows[row].append(number(tuple(adjacent_point)))
    residual = [
        sum((field[target] / field[row] - 1 for target in targets), Fraction())
        for row, targets in enumerate(neighbor_rows)
    ]
    gradient = [
        sum(
            (
                residual[target] * field[row] / field[target]
                - residual[row] * field[target] / field[row]
                for target in targets
            ),
            Fraction(),
        )
        for row, targets in enumerate(neighbor_rows)
    ]
    residual_norm = sum((value * value for value in residual), Fraction())
    gradient_norm = sum((value * value for value in gradient), Fraction())
    mixed_minor = (
        field[number((1, 1, 1, 1))] * field[number((3, 3, 1, 1))]
        - field[number((3, 1, 1, 1))] * field[number((1, 3, 1, 1))]
    )
    return {
        "vertices": len(all_points),
        "orbit_count": dimension,
        "lambda": lam,
        "epsilon": epsilon,
        "delta": delta,
        "source_mean": source_mean,
        "potential_minimum": potential_minimum,
        "field_minimum": min(field),
        "field_maximum": max(field),
        "residual_norm_squared": residual_norm,
        "gradient_norm_squared": gradient_norm,
        "quotient": gradient_norm / residual_norm,
        "gradient_sum": sum(gradient, Fraction()),
        "mixed_product_minor": mixed_minor,
        "source_compatibility": sum(
            (
                count * (value - source_mean)
                for count, value in zip(multiplicity, source)
            ),
            Fraction(),
        ),
        "potential_weighted_sum": sum(
            (count * value for count, value in zip(multiplicity, potential)),
            Fraction(),
        ),
    }


def verify(certificate: dict[str, object]) -> list[tuple[str, bool]]:
    with open(SCHEMA, encoding="utf-8") as handle:
        schema = json.load(handle)
    try:
        jsonschema.Draft202012Validator(schema).validate(certificate)
        schema_ok = True
    except jsonschema.ValidationError:
        schema_ok = False

    provenance = certificate["provenance"]
    provenance_ok = (
        provenance["repository_base_commit"] == SOURCE_COMMIT
        and all(
            os.path.isfile(os.path.join(ROOT, row["path"]))
            and file_hash(os.path.join(ROOT, row["path"])) == row["sha256"]
            for row in provenance["inputs"]
        )
    )
    family = certificate["family"]
    family_ok = (
        family["side"] == "L_n=n^24"
        and family["bubble_scale"] == "lambda_n=n^16=L_n^(2/3)"
        and family["tail_scale"] == "R_n=n^21=L_n^(7/8)"
        and family["positive_lift"] == "epsilon_n=lambda_n/R_n^2=n^-26"
        and family["poisson_potential"]
        == "v_n is the unique mean-zero solution of -Delta v_n=f_n-mean(f_n)"
        and family["field"] == "u_n=u_n^0*(1+delta_n*p_n)>0"
    )
    lemma = certificate["discrete_green_annular_lemma"]
    lemma_ok = (
        lemma["action_bounds"]
        == "there are universal 0<c<C<infinity with c<=||Delta u/u||_2^2<=C"
        and lemma["base_gradient_bound"]
        == "||g(u^0)||_2^2<=C*[lambda^-8+lambda^4/R^8+R^4/L^8+lambda^4/(R^4*L^4)]"
        and lemma["proof_method"]
        == "Fourier representation of the mean-zero torus Green kernel, summation by parts for first through fourth differences, dyadic annular convolution estimates, and the exact weighted-current identity g=L_(u_x*u_y)[Delta u/u^3]"
    )
    perturbation = certificate["perturbation_theorem"]
    perturbation_ok = (
        perturbation["positivity"] == "|delta_n*p_n|<=1/n<=1/2"
        and perturbation["stability"]
        == "||r(u_n)-r(u_n^0)||_2=O(delta_n) and ||g(u_n)-g(u_n^0)||_2=O(delta_n/L_n^2)"
        and "atanh positivity" in perturbation["nonseparability_witness"]
    )
    power = certificate["power_balance"]
    exponents = power["scale_exponents_in_n"]
    side = exponents["side"]
    bubble = exponents["bubble_scale"]
    tail = exponents["tail_scale"]
    lift = exponents["positive_lift"]
    amplitude = exponents["four_way_amplitude"]
    derived_exponents = {
        "lattice_core": 4 * side - 8 * bubble,
        "background_transition": 4 * side + 4 * bubble - 8 * tail,
        "mean_source": 4 * tail - 4 * side,
        "periodic_image": 4 * bubble - 4 * tail,
        "four_way_perturbation": 2 * amplitude,
        "field_contrast": 2 * tail - 2 * bubble,
        "annular_separation": 3 * tail - bubble - 2 * side,
    }
    exponent_ok = (
        (side, bubble, tail, lift, amplitude) == (24, 16, 21, -26, -1)
        and 0 < bubble < tail < side
        and lift == bubble - 2 * tail
        and derived_exponents
        == {
            "lattice_core": -32,
            "background_transition": -8,
            "mean_source": -12,
            "periodic_image": -20,
            "four_way_perturbation": -2,
            "field_contrast": 10,
            "annular_separation": -1,
        }
        and max(
            derived_exponents[name]
            for name in (
                "lattice_core",
                "background_transition",
                "mean_source",
                "periodic_image",
                "four_way_perturbation",
            )
        )
        < 0
    )
    terms = power["base_terms_after_free_normalization"]
    power_ok = (
        terms
        == {
            "lattice_core": "L_n^4*lambda_n^-8=n^-32",
            "background_transition": "L_n^4*lambda_n^4/R_n^8=n^-8",
            "mean_source": "R_n^4/L_n^4=n^-12",
            "periodic_image": "lambda_n^4/R_n^4=n^-20",
        }
        and power["four_way_perturbation"] == "delta_n^2=n^-2"
        and power["normalized_upper_bound"]
        == "Q_n/omega_Ln^2<=C*(n^-32+n^-8+n^-12+n^-20+n^-2)=O(n^-2)"
        and power["limit"] == "lim_(n->infinity) Q_n/omega_Ln^2=0"
    )
    contrast = certificate["action_and_contrast"]
    contrast_ok = (
        contrast["positive_action"]
        == "0<c<=||r_n||_2^2<=C, hence 0<c/2<=A_n<=C/2"
        and contrast["field_contrast"]
        == "max(u_n)/min(u_n)<=C*R_n^2/lambda_n^2=C*n^10=C*L_n^(5/12)"
    )

    rebuilt = reconstruct_fixture()
    fixture = certificate["exact_fixture"]
    rational_keys = (
        "lambda",
        "epsilon",
        "delta",
        "source_mean",
        "potential_minimum",
        "field_minimum",
        "field_maximum",
        "residual_norm_squared",
        "gradient_norm_squared",
        "quotient",
        "gradient_sum",
        "mixed_product_minor",
    )
    fixture_ok = (
        fixture["vertices"] == rebuilt["vertices"] == 256
        and fixture["orbit_count"] == rebuilt["orbit_count"] == 15
        and all(dec(fixture[key]) == rebuilt[key] for key in rational_keys)
        and rebuilt["source_compatibility"] == 0
        and rebuilt["potential_weighted_sum"] == 0
        and rebuilt["field_minimum"] > 0
        and rebuilt["residual_norm_squared"] > 0
        and rebuilt["gradient_sum"] == 0
        and rebuilt["mixed_product_minor"] > 0
        and all(fixture["checks"].values())
    )
    disposition = certificate["research_disposition"]
    boundary_ok = (
        disposition["all_field_torus_scaled_PL"] == "REFUTED"
        and disposition["nonseparable_polynomial_contrast_counterfamily"]
        == "CONSTRUCTED"
        and disposition["complete_residual_gradient_free_scale_collapse"] == "PROVED"
        and disposition["witten_poincare_transfer"] == "OPEN"
        and disposition["interacting_h_minus_one"] == "OPEN"
        and disposition["continuum_measure"] == "OPEN"
        and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED"
    )
    checks = certificate["checks"]
    return [
        ("strict_schema", schema_ok),
        (
            "producer_not_imported",
            "bt_euclidean_torus_green_tail_counterfamily" not in sys.modules,
        ),
        ("predecessor_hash_and_source_commit", provenance_ok),
        ("family_definition", family_ok),
        ("discrete_green_annular_lemma", lemma_ok),
        ("four_way_perturbation", perturbation_ok),
        ("power_balance", power_ok),
        ("independent_power_exponents", exponent_ok),
        ("positive_action_and_polynomial_contrast", contrast_ok),
        ("independent_rational_fixture", fixture_ok),
        ("claim_boundaries", boundary_ok),
        (
            "dependency_tags",
            certificate["dependency_tags"]
            == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        ),
        (
            "self_checks",
            checks["ok"] is True
            and checks["passed"] == checks["total"] == 9
            and all(checks["details"].values()),
        ),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", default=DEFAULT_CERTIFICATE)
    args = parser.parse_args(argv)
    try:
        with open(args.certificate, encoding="utf-8") as handle:
            certificate = json.load(handle)
        checks = verify(certificate)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"[FAIL] verifier exception: {exc}")
        return 1
    for name, passed in checks:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    passed = sum(value for _, value in checks)
    print(
        "BT torus Green-tail counterfamily verifier: "
        f"{passed}/{len(checks)} checks passed"
    )
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
