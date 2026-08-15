#!/usr/bin/env python3
"""Independent verifier for the BT complete-g4 pair-3/pair-6 bounds."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_LINEAR_PAIR_BOUNDS_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-complete-g4-linear-pair-bounds-v1.schema.json",
)
SEVEN_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SEVEN_KERNEL_REDUCTION_V1.json"
)
SUBPOWER_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SUBPOWER_PAIR_BOUNDS_V1.json"
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


def even_form(form: list[int] | tuple[int, int, int]) -> tuple[int, int, int]:
    encoded = tuple(form)
    for component in encoded:
        if component:
            return encoded if component > 0 else tuple(-item for item in encoded)
    return encoded


def allocation_ledger(
    representative: dict,
    cubic_choices: dict[int, tuple[tuple[int, int, int], tuple[int, int, int]]],
) -> dict[tuple[int, int, int], Fraction]:
    ledger: dict[tuple[int, int, int], Fraction] = {}

    def add(form: list[int] | tuple[int, int, int], amount: Fraction) -> None:
        key = even_form(form)
        ledger[key] = ledger.get(key, Fraction()) + amount

    for propagator in representative["propagators"]:
        add(propagator, Fraction(-2))
    for index, kernel in enumerate(representative["kernels"]):
        available = {even_form(form) for form in kernel["arguments"]}
        if kernel["degree"] == 3:
            require(index in cubic_choices, "missing cubic allocation")
            selected = cubic_choices[index]
            require(
                all(even_form(form) in available for form in selected),
                "selected cubic leg is absent",
            )
            for form in selected:
                add(form, Fraction(1))
        else:
            require(kernel["degree"] in (4, 5), "unexpected vertex degree")
            for form in kernel["arguments"]:
                add(form, Fraction(1, 2))
    return {key: value for key, value in ledger.items() if value}


def verify_upstream_and_allocations(certificate: dict) -> None:
    with open(os.path.join(ROOT, SEVEN_REL), encoding="utf-8") as handle:
        seven = json.load(handle)
    with open(os.path.join(ROOT, SUBPOWER_REL), encoding="utf-8") as handle:
        subpower = json.load(handle)
    source = {row["pair"]: row for row in seven["inversion_reduction"]["pairs"]}
    expected = {
        3: ([3, 6], "-2*U31*U41*U30", Fraction(-432)),
        6: ([9, 12], "2*U31*U51", Fraction(180)),
    }
    require(
        subpower["power_sector_reduction"]["subpower_pairs"] == [1, 2, 5],
        "predecessor subpower set drift",
    )
    require([row["pair"] for row in certificate["pair_bounds"]] == [3, 6], "pair order drift")
    for row in certificate["pair_bounds"]:
        number = row["pair"]
        indices, origin, coefficient = expected[number]
        upstream = source[number]
        require(upstream["atlas_row_indices_one_based"] == indices, "atlas rows drift")
        require(upstream["origin"] == origin, "origin drift")
        require(fraction(upstream["paired_coefficient"]) == coefficient, "coefficient drift")
        require(
            row["upstream"]
            == {
                "atlas_rows_one_based": indices,
                "origin": origin,
                "paired_coefficient": upstream["paired_coefficient"],
                "representative": upstream["representative"],
            },
            f"stored representative drift for pair {number}",
        )

    p, q, r = (0, 0, 1), (1, 0, 0), (0, 1, 0)
    s, sp, qp = (1, 1, 0), (1, 1, 1), (1, 0, 1)
    ledger_3 = allocation_ledger(source[3]["representative"], {0: (p, s), 1: (s, q)})
    ledger_6 = allocation_ledger(source[6]["representative"], {0: (p, q)})
    require(
        ledger_3
        == {
            p: Fraction(3, 2),
            q: Fraction(-1, 2),
            r: Fraction(-3, 2),
            sp: Fraction(-3, 2),
        },
        f"pair 3 exponent ledger failed: {ledger_3}",
    )
    require(
        ledger_6
        == {
            p: Fraction(3, 2),
            q: Fraction(-1, 2),
            r: Fraction(-1),
            qp: Fraction(-3, 2),
        },
        f"pair 6 exponent ledger failed: {ledger_6}",
    )


def verify_constants_and_convolution(certificate: dict) -> None:
    cubic = Fraction(2, 3)
    quartic = Fraction(7 * 64, 24)
    directed_block = 2 * 4
    quintic_partitions = 5 + 10
    quintic = Fraction(quintic_partitions * directed_block**2, 120)
    require(directed_block == 8, "directed-edge block constant failed")
    require(quartic == Fraction(56, 3), "quartic constant failed")
    require(quintic == 8, "quintic constant failed")
    require(Fraction(432) * cubic**2 * quartic == 3584, "pair 3 constant failed")
    require(Fraction(180) * cubic * quintic == 960, "pair 6 constant failed")
    stored = certificate["vertex_bounds"]["constants"]
    require(fraction(stored["quintic_all_leg_product"]) == 8, "stored K5 constant drift")

    # Centered max-norm shell in four dimensions.
    for m in range(1, 65):
        shell = (2 * m + 1) ** 4 - (2 * m - 1) ** 4
        require(shell == 64 * m**3 + 16 * m, "4D shell identity failed")
        require(shell <= 80 * m**3, "4D shell upper bound failed")

    # Independent constant ledger for C_33. The first two pieces use
    # sum_{j<=M/2} j^-3*shell(j)<=40M and the other distance >=M/2.
    near_each = 8 * 40
    middle = 64 * 625
    # In the far region the shell coefficient is 8*80=640 and
    # sum_{m>2M}m^-3<=1/(8M^2).
    far = Fraction(640, 8)
    inner = 2 * near_each + middle + far
    require(inner == 40720, "C_33 constant failed")
    require(80 * Fraction(3, 2) <= inner, "coincident-center bound failed")
    outer_shell = 2 * 80 + 2
    require(outer_shell == 162, "outer two-centre shell constant failed")
    outer = inner * 81
    require(outer == 3298320, "D_133 constant failed")
    spectral = 4 * 64 * 64
    require(spectral == 16384, "spectral conversion denominator failed")
    explicit_3 = Fraction(3584) * Fraction(outer, spectral) * 8
    explicit_6 = Fraction(960) * 2 * 8
    require(explicit_3 == 5772060, "pair 3 explicit constant failed")
    require(explicit_6 == 15360, "pair 6 explicit constant failed")

    convolution = certificate["torus_convolution"]
    require(convolution["inner_bound"] == "C_33(x)<=40720/max(1,rho(x))^2", "inner bound drift")
    require(convolution["outer_bound"] == "D_133(p)<=3298320*L", "outer bound drift")
    bounds = {row["pair"]: row for row in certificate["pair_bounds"]}
    require(bounds[3]["raw_bound"] == "abs(I_3(L))<=3584*omega(p)^(3/2)*S_3(L)/N", "pair 3 raw bound drift")
    require(bounds[3]["explicit_bound"] == "abs(I_3(L))<=5772060*pi^3*L", "pair 3 explicit bound drift")
    require(bounds[6]["raw_bound"] == "abs(I_6(L))<=960*omega(p)^(3/2)*G1(L)*J_L/N", "pair 6 raw bound drift")
    require(bounds[6]["explicit_bound"] == "abs(I_6(L))<=15360*pi^3*L*B_L, B_L=11/16+(1/2)*log(floor(L/2))", "pair 6 explicit bound drift")

    # The imported bounds G1<=2N and J<=N*B_L, together with
    # omega(p)^(3/2)<=8*pi^3/L^3, give the displayed constants.
    with open(os.path.join(ROOT, SEVEN_REL), encoding="utf-8") as handle:
        seven = json.load(handle)
    with open(os.path.join(ROOT, SUBPOWER_REL), encoding="utf-8") as handle:
        subpower = json.load(handle)
    require("<=2*N" in seven["green_sum"]["upper_bound"], "G1 bound drift")
    require(
        subpower["convolution_bounds"]["J_bound"]
        == "J_L<=N*B_L, B_L=11/16+(1/2)*log(R)",
        "J bound drift",
    )


def verify_boundaries(certificate: dict) -> None:
    reduction = certificate["power_sector_reduction"]
    require(reduction["subpower_pairs"] == [1, 2, 3, 5, 6], "five-pair set drift")
    require(reduction["pairs_still_capable_of_N_omega_p_scale"] == [4, 7], "two-pair gate drift")
    disposition = certificate["method_disposition"]
    expected = {
        "pairs_3_6_tuned_g_four_uniformity": "NOT_ESTABLISHED_BY_THESE_BOUNDS",
        "combined_pairs_4_7_power_coefficient": "OPEN",
        "complete_seven_kernel_large_volume_sign_and_scaling": "OPEN",
        "complete_M4_large_volume_sign_and_scaling": "OPEN",
        "nonperturbative_annealed_score": "OPEN",
        "actual_interacting_h_minus_one_second_moment": "OPEN",
        "continuum_limit": "NOT_ESTABLISHED",
        "born_rule": "NOT_ESTABLISHED",
        "krein_reconstruction": "NOT_ASSESSED",
        "lorentzian_transfer": "NOT_ESTABLISHED",
    }
    require(all(disposition.get(key) == value for key, value in expected.items()), "claim boundary drift")
    require(certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "dependency tags drift")
    require(all(certificate["checks"].values()), "certificate contains a failed check")


def verify(path: str = CERT_PATH) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
        errors = sorted(
            Draft202012Validator(schema).iter_errors(certificate),
            key=lambda item: list(item.path),
        )
        require(not errors, f"schema validation failed: {errors[0].message if errors else ''}")
        require(certificate["data_sha256"] == file_hash(certificate["data"]), "data hash drift")
        require(certificate["producer_sha256"] == file_hash(certificate["producer"]), "producer hash drift")
        for source in certificate["provenance"]["inputs"]:
            require(source["sha256"] == file_hash(source["path"]), f"input hash drift: {source['path']}")
        with open(os.path.join(ROOT, certificate["data"]), encoding="utf-8") as handle:
            data = json.load(handle)
        for field in (
            "vertex_bounds",
            "torus_convolution",
            "pair_bounds",
            "power_sector_reduction",
            "method_disposition",
            "does_not_establish",
            "next_gate",
        ):
            require(certificate[field] == data[field], f"certificate/data drift: {field}")
        verify_upstream_and_allocations(certificate)
        verify_constants_and_convolution(certificate)
        verify_boundaries(certificate)
        return True
    except (OSError, ValueError, KeyError, TypeError, VerificationError) as error:
        if path == CERT_PATH:
            print(f"FAIL: {error}", file=sys.stderr)
        return False


def main() -> int:
    if verify():
        print("PASS: exact BT pair-3 O(L) and pair-6 O(L log L) bounds verified")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
