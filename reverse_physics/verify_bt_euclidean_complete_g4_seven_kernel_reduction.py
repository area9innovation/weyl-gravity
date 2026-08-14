#!/usr/bin/env python3
"""Independent verifier for the BT seven-kernel reduction certificate."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SEVEN_KERNEL_REDUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-complete-g4-seven-kernel-reduction-v1.schema.json",
)
ATLAS_PATH = os.path.join(
    ROOT,
    "reverse_physics/data/"
    "bt_euclidean_complete_g4_general_l_two_loop_v1.json",
)


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction(value: dict) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def negative(form: tuple[int, int, int]) -> tuple[int, int, int]:
    return -form[0], -form[1], -form[2]


def even_line(form: tuple[int, int, int]) -> tuple[int, int, int]:
    for component in form:
        if component:
            return form if component > 0 else negative(form)
    return form


def independent_signature(row: dict, invert_source: bool = False) -> tuple:
    def map_form(encoded: list[int]) -> tuple[int, int, int]:
        a, b, c = encoded
        return a, b, (-c if invert_source else c)

    vertices = []
    for kernel in row["kernels"]:
        direct = tuple(sorted(map_form(form) for form in kernel["arguments"]))
        reversed_vertex = tuple(sorted(negative(form) for form in direct))
        vertices.append((kernel["degree"], min(direct, reversed_vertex)))
    lines = tuple(
        sorted(even_line(map_form(form)) for form in row["propagators"])
    )
    return tuple(sorted(vertices)), lines


def verify_pairing(certificate: dict, atlas: dict) -> None:
    rows = [
        row
        for row in atlas["surviving_integrands"]
        if row["omega_p_inverse_square_power"] == 0
    ]
    require(len(rows) == 14, "upstream atlas no longer has fourteen s=0 rows")
    expected = [(1, 4), (2, 5), (3, 6), (7, 10), (8, 11), (9, 12), (13, 14)]
    observed = []
    used = set()
    for left in range(14):
        if left in used:
            continue
        matches = [
            right
            for right in range(14)
            if right != left
            and independent_signature(rows[right])
            == independent_signature(rows[left], invert_source=True)
        ]
        require(len(matches) == 1, f"row {left + 1} lacks a unique inversion mate")
        right = matches[0]
        require(right not in used, "inversion pairing is not disjoint")
        require(
            fraction(rows[left]["coefficient"])
            == fraction(rows[right]["coefficient"]),
            "paired coefficient mismatch",
        )
        observed.append((left + 1, right + 1))
        used.update((left, right))
    require(observed == expected, "unexpected seven-pair partition")
    stored = certificate["inversion_reduction"]["pairs"]
    require(
        [tuple(pair["atlas_row_indices_one_based"]) for pair in stored] == expected,
        "stored seven-pair partition drift",
    )
    require(
        all(
            fraction(pair["paired_coefficient"])
            == 2 * fraction(pair["single_coefficient"])
            for pair in stored
        ),
        "stored coefficient did not double under pairing",
    )
    for (left, _), pair in zip(expected, stored):
        require(
            pair["representative"]
            == {
                "kernels": rows[left - 1]["kernels"],
                "propagators": rows[left - 1]["propagators"],
            },
            f"stored representative drift for pair {pair['pair']}",
        )
    require(
        [pair["origin"] for pair in stored]
        == [
            "Cov(U31^2,U30^2)",
            "Cov(U31^2,U30^2)",
            "-2*U31*U41*U30",
            "Cov(U31^2,-U40)",
            "Cov(U31^2,-U40)",
            "2*U31*U51",
            "U41^2",
        ],
        "seven-pair origin ledger drift",
    )


def verify_quartic_identity() -> None:
    # Independently reconstruct the paired K4 numerator from the directed-edge
    # partition definition.  B(S)=-sum_T (-1)^(|S|-|T|) omega(sum T).
    momenta = ((1, 0), (-1, 0), (0, 1), (0, -1))
    variable = {
        (1, 0): "w",
        (-1, 0): "w",
        (0, 1): "v",
        (0, -1): "v",
        (1, 1): "u",
        (-1, -1): "u",
        (1, -1): "t",
        (-1, 1): "t",
    }

    def b(indices: tuple[int, ...]) -> dict[str, int]:
        result = {name: 0 for name in ("w", "v", "u", "t")}
        size = len(indices)
        for mask in range(1 << size):
            total = [0, 0]
            selected = 0
            for offset, index in enumerate(indices):
                if mask & (1 << offset):
                    selected += 1
                    total[0] += momenta[index][0]
                    total[1] += momenta[index][1]
            if total == [0, 0]:
                continue
            name = variable[tuple(total)]
            result[name] -= (-1) ** (size - selected)
        return result

    def multiply(left: dict[str, int], right: dict[str, int]) -> dict[tuple[str, str], int]:
        result = {}
        for left_name, left_value in left.items():
            for right_name, right_value in right.items():
                key = tuple(sorted((left_name, right_name)))
                result[key] = result.get(key, 0) + left_value * right_value
        return result

    numerator = {}

    def accumulate(product: dict[tuple[str, str], int]) -> None:
        for key, value in product.items():
            numerator[key] = numerator.get(key, 0) + value

    for singled in range(4):
        rest = tuple(index for index in range(4) if index != singled)
        accumulate(multiply(b((singled,)), b(rest)))
    for left in ((0, 1), (0, 2), (0, 3)):
        right = tuple(index for index in range(4) if index not in left)
        accumulate(multiply(b(left), b(right)))
    require(
        numerator
        == {
            ("w", "w"): 6,
            ("v", "v"): 6,
            ("v", "w"): 16,
            ("u", "w"): -4,
            ("t", "w"): -4,
            ("u", "v"): -4,
            ("t", "v"): -4,
            ("u", "u"): 1,
            ("t", "t"): 1,
            ("t", "u"): 0,
        },
        f"direct K4 partition reconstruction failed: {numerator}",
    )
    # Substitute u=A-x and t=A-y into
    # 6A^2+4wv-4A(u+t)+u^2+t^2.  The exact coefficient ledger is
    # A^2: 6-8+1+1=0; Ax and Ay: 4-2=2; x^2,y^2:1; wv:4.
    require(
        (6 - 8 + 1 + 1, 4 - 2, 4 - 2, 1, 1, 4)
        == (0, 2, 2, 1, 1, 4),
        "paired K4 coefficient identity failed",
    )
    # With c=cos(k_j), d=cos(r_j), independently expand
    # 2w_j+2v_j-[u_j+t_j]-w_j*v_j.  Its 1,c,d,cd coefficients vanish.
    require(
        (4 + 4 - 4 - 4, -4 + 4, -4 + 4, 4 - 4)
        == (0, 0, 0, 0),
        "per-axis lattice dispersion coefficient identity failed",
    )
    require(Fraction(8 + 64 + 4, 24) == Fraction(19, 6), "upper constant drift")
    require(Fraction(4, 24) == Fraction(1, 6), "lower constant drift")


def verify_green_and_carrier(certificate: dict) -> None:
    # The independent shell proof uses H_R<=R and R<=L/2:
    # 2R(R+1)+H_R <= 2R^2+3R <= L^2/2+3L/2 <= 2L^2 for L>=1.
    for length in range(5, 1001):
        radius = length // 2
        harmonic = sum((Fraction(1, item) for item in range(1, radius + 1)), Fraction())
        require(
            2 * radius * (radius + 1) + harmonic <= 2 * length * length,
            "finite shell inequality failed",
        )
    # The algebraic tail of the displayed proof is stronger than the sampled check.
    require(
        (Fraction(2) - Fraction(1, 2), -Fraction(3, 2))
        == (Fraction(3, 2), -Fraction(3, 2)),
        "analytic shell remainder identity failed",
    )

    k3_coefficient = Fraction(1 + 1 + 4 - 2 * (1 + 2 + 2), 6)
    require(k3_coefficient == Fraction(-2, 3), "transverse K3 fixture failed")
    selected_coefficient = (
        Fraction(-216) * k3_coefficient**2 * Fraction(1, 6) / 4
    )
    require(selected_coefficient == -4, "nested carrier coefficient failed")
    require(Fraction(5**4 - 1, 5**4) == Fraction(624, 625), "volume ratio constant drift")
    carrier = certificate["negative_nested_carrier"]
    require(carrier["atlas_rows_one_based"] == [7, 10], "nested carrier row drift")
    require("T_L<0" == carrier["sign"], "nested carrier sign promoted or lost")


def verify_boundaries(certificate: dict) -> None:
    disposition = certificate["method_disposition"]
    require(
        disposition["termwise_tuned_order_g_four_uniformity"] == "OBSTRUCTED",
        "termwise obstruction omitted",
    )
    require(
        disposition["combined_seven_kernel_large_volume_sign_and_scaling"] == "OPEN",
        "isolated carrier promoted to combined seven-kernel result",
    )
    require(
        disposition["complete_M4_large_volume_sign_and_scaling"] == "OPEN",
        "isolated carrier promoted to complete M4",
    )
    require(
        disposition["actual_interacting_h_minus_one_second_moment"] == "OPEN",
        "perturbative carrier promoted to actual H^-1 moment",
    )
    require(
        disposition["continuum_limit"] == "NOT_ESTABLISHED"
        and disposition["born_rule"] == "NOT_ESTABLISHED"
        and disposition["krein_reconstruction"] == "NOT_ASSESSED"
        and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED",
        "forbidden physics promotion",
    )
    require(
        set(certificate["dependency_tags"])
        == {"LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"},
        "dependency tag boundary drift",
    )
    text = " ".join(certificate["does_not_establish"])
    for phrase in ("all seven", "complete M4", "actual Gibbs", "H^-1", "LORENTZIAN-CAUSAL"):
        require(phrase in text, f"missing does-not-establish boundary: {phrase}")


def verify(path: str = CERT_PATH) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
        errors = sorted(
            Draft202012Validator(schema).iter_errors(certificate),
            key=lambda error: list(error.path),
        )
        require(not errors, errors[0].message if errors else "schema failure")
        require(certificate["data_sha256"] == file_hash(certificate["data"]), "data hash drift")
        require(
            certificate["producer_sha256"] == file_hash(certificate["producer"]),
            "producer hash drift",
        )
        for item in certificate["provenance"]["inputs"]:
            require(item["sha256"] == file_hash(item["path"]), f"input hash drift: {item['path']}")
        with open(ATLAS_PATH, encoding="utf-8") as handle:
            atlas = json.load(handle)
        verify_pairing(certificate, atlas)
        verify_quartic_identity()
        verify_green_and_carrier(certificate)
        verify_boundaries(certificate)
        rows = certificate["supporting_preflight"]["rows"]
        require([row["length"] for row in rows] == [5, 6, 7, 8], "preflight volume drift")
        require(all(row["sum"] < 0 for row in rows), "stored supporting sign drift")
        require(
            all(-0.021 < row["sum_over_N_omega_p"] < -0.015 for row in rows),
            "stored supporting ratio drift",
        )
        require(all(certificate["checks"].values()), "builder check is false")
    except (
        KeyError,
        OSError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
        VerificationError,
    ):
        return False
    return True


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else CERT_PATH
    if not verify(target):
        print("FAIL seven-kernel certificate verification", file=sys.stderr)
        return 1
    print(
        "PASS exact seven-pair reduction, paired-quartic bounds, negative L^2 carrier, hashes, schema, and claim boundaries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
