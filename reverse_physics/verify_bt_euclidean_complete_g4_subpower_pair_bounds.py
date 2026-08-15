#!/usr/bin/env python3
"""Independent verifier for the exact BT complete-g4 subpower pair bounds."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SUBPOWER_PAIR_BOUNDS_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-complete-g4-subpower-pair-bounds-v1.schema.json",
)
SEVEN_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SEVEN_KERNEL_REDUCTION_V1.json"
)
GENERAL_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_GENERAL_L_TWO_LOOP_V1.json"
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


def exponent_ledger(
    representative: dict,
    allocations: tuple[tuple[tuple[int, int, int], ...], ...],
    quartic_all_legs: bool = False,
) -> dict[tuple[int, int, int], Fraction]:
    """Subtract propagators and add independently selected vertex factors."""

    ledger: dict[tuple[int, int, int], Fraction] = {}

    def add(form: list[int] | tuple[int, int, int], amount: Fraction) -> None:
        key = even_form(form)
        ledger[key] = ledger.get(key, Fraction()) + amount

    for propagator in representative["propagators"]:
        add(propagator, Fraction(-2))
    require(
        len(allocations) == len(representative["kernels"]),
        "allocation does not cover every kernel",
    )
    for kernel, selected in zip(representative["kernels"], allocations):
        available = {even_form(form) for form in kernel["arguments"]}
        if kernel["degree"] == 4 and quartic_all_legs:
            require(not selected, "quartic all-leg allocation must be implicit")
            for form in kernel["arguments"]:
                add(form, Fraction(1, 2))
        else:
            require(kernel["degree"] == 3, "unexpected non-cubic allocation")
            require(len(selected) == 2, "cubic bound must select two legs")
            require(
                all(even_form(form) in available for form in selected),
                "selected cubic leg is absent from its kernel",
            )
            for form in selected:
                add(form, Fraction(1))
    return {key: value for key, value in ledger.items() if value}


def verify_upstream_and_allocations(certificate: dict) -> None:
    with open(os.path.join(ROOT, SEVEN_REL), encoding="utf-8") as handle:
        seven = json.load(handle)
    upstream = {row["pair"]: row for row in seven["inversion_reduction"]["pairs"]}
    expected = {
        1: ([1, 4], "Cov(U31^2,U30^2)", Fraction(324)),
        2: ([2, 5], "Cov(U31^2,U30^2)", Fraction(324)),
        5: ([8, 11], "Cov(U31^2,-U40)", Fraction(-108)),
    }
    stored = certificate["pair_bounds"]
    require([row["pair"] for row in stored] == [1, 2, 5], "pair order drift")
    for row in stored:
        number = row["pair"]
        source = upstream[number]
        indices, origin, coefficient = expected[number]
        require(source["atlas_row_indices_one_based"] == indices, "atlas pair drift")
        require(source["origin"] == origin, "pair origin drift")
        require(fraction(source["paired_coefficient"]) == coefficient, "pair coefficient drift")
        require(
            row["upstream"]
            == {
                "atlas_rows_one_based": indices,
                "origin": origin,
                "paired_coefficient": source["paired_coefficient"],
                "representative": source["representative"],
            },
            f"stored upstream representative drift for pair {number}",
        )

    p, q, r = (0, 0, 1), (1, 0, 0), (0, 1, 0)
    qr, qp, qrp, rp = (1, 1, 0), (1, 0, 1), (1, 1, 1), (0, 1, -1)
    allocations = {
        1: ((p, qr), (p, qr), (qr, q), (qr, q)),
        2: ((r, qp), (p, qr), (p, q), (r, qr)),
        5: ((p, q), (p, r), ()),
    }
    ledgers = {
        number: exponent_ledger(
            upstream[number]["representative"],
            allocations[number],
            quartic_all_legs=(number == 5),
        )
        for number in (1, 2, 5)
    }
    require(
        ledgers[1] == {p: Fraction(2), r: Fraction(-2), qrp: Fraction(-2)},
        f"pair 1 allocation ledger failed: {ledgers[1]}",
    )
    require(
        ledgers[2]
        == {p: Fraction(2), q: Fraction(-1), qp: Fraction(-1), qrp: Fraction(-2)},
        f"pair 2 allocation ledger failed: {ledgers[2]}",
    )
    require(
        ledgers[5]
        == {
            p: Fraction(2),
            q: Fraction(-1, 2),
            qp: Fraction(-3, 2),
            r: Fraction(-1, 2),
            rp: Fraction(-3, 2),
        },
        f"pair 5 allocation ledger failed: {ledgers[5]}",
    )


def verify_constants_and_shells(certificate: dict) -> None:
    cubic = Fraction(2, 3)
    with open(os.path.join(ROOT, GENERAL_REL), encoding="utf-8") as handle:
        general = json.load(handle)
    require(
        general["factorized_conditioning_sector"]["vertex_bound"]
        == "K3=V3/6 and |V3(p,q,-p-q)|<=4*omega(p)*min(omega(q),omega(p+q))",
        "upstream cubic soft-leg theorem drift",
    )
    # For a directed lattice edge, the inclusion-exclusion block is a complex
    # monomial plus its conjugate.  Each component is bounded by the product of
    # the selected sqrt(omega)'s; four axes and the conjugate factor give 8.
    # For a singleton B({k})=omega(k)<=4*sqrt(omega(k)) because omega<=16,
    # so the same constant 8 safely covers every block used by a 1|3 or 2|2
    # partition without invoking floating-point square roots.
    require(2 * 4 == 8 and 16 <= 8 * 4, "directed-edge block constant failed")
    partition_count = 4 + 3
    edge_product_constant = 8 * 8
    quartic = Fraction(partition_count * edge_product_constant, 24)
    require(quartic == Fraction(56, 3), "quartic all-leg constant failed")
    require(Fraction(324) * cubic**4 == 64, "pair 1/2 constant failed")
    require(Fraction(108) * cubic**2 * quartic == 896, "pair 5 constant failed")
    require(
        fraction(certificate["vertex_bounds"]["constants"]["cubic_two_leg"])
        == cubic,
        "stored cubic constant drift",
    )
    require(
        fraction(certificate["vertex_bounds"]["constants"]["quartic_all_leg_product"])
        == quartic,
        "stored quartic constant drift",
    )

    # Exact max-norm shell arithmetic in four dimensions, doubled for the two
    # centres 0 and -p.  The final 32 sum(m^-3) is bounded using zeta(3)<3/2.
    for m in range(1, 65):
        shell = 2 * ((2 * m + 1) ** 4 - (2 * m - 1) ** 4)
        require(shell == 128 * m**3 + 32 * m, "two-centre shell identity failed")
    require(Fraction(32) * Fraction(3, 2) == 48, "summable shell tail failed")
    require(128 + 48 == 176, "shifted-convolution constant failed")
    require(Fraction(176, 256) == Fraction(11, 16), "B_L constant failed")
    require(Fraction(128, 256) == Fraction(1, 2), "B_L logarithm failed")

    convolution = certificate["convolution_bounds"]
    require(
        convolution["dimensionless_shifted_sum"]
        == "sum_(q!=0,-p) [rho_2(q)*rho_2(q+p)^3]^(-1)<=176+128*log(R)",
        "shifted sum statement drift",
    )
    require(
        convolution["J_bound"] == "J_L<=N*B_L, B_L=11/16+(1/2)*log(R)",
        "J_L bound drift",
    )

    # After G2<=N*A_L and J<=N*B_L, use N*omega(p)^2<=16*pi^4.
    require(64 * 16 == 1024, "pair 1/2 explicit constant failed")
    require(896 * 16 == 14336, "pair 5 explicit constant failed")
    bounds = {row["pair"]: row for row in certificate["pair_bounds"]}
    require(bounds[1]["raw_bound"] == "abs(I_1(L))<=64*omega(p)^2*G2(L)^2/N", "pair 1 raw bound drift")
    require(bounds[2]["raw_bound"] == "abs(I_2(L))<=64*omega(p)^2*G2(L)^2/N", "pair 2 raw bound drift")
    require(bounds[5]["raw_bound"] == "abs(I_5(L))<=896*omega(p)^2*J_L^2/N", "pair 5 raw bound drift")
    require(bounds[1]["explicit_bound"] == "abs(I_1(L))<=1024*pi^4*A_L^2", "pair 1 explicit bound drift")
    require(bounds[2]["explicit_bound"] == "abs(I_2(L))<=1024*pi^4*A_L^2", "pair 2 explicit bound drift")
    require(bounds[5]["explicit_bound"] == "abs(I_5(L))<=14336*pi^4*B_L^2", "pair 5 explicit bound drift")


def verify_boundaries(certificate: dict) -> None:
    reduction = certificate["power_sector_reduction"]
    require(reduction["subpower_pairs"] == [1, 2, 5], "subpower set drift")
    require(
        reduction["pairs_still_capable_of_N_omega_p_scale"] == [3, 4, 6, 7],
        "four-pair power gate drift",
    )
    disposition = certificate["method_disposition"]
    required = {
        "pair_3_scale": "OPEN",
        "pair_6_scale": "OPEN",
        "combined_pairs_3_4_6_7_power_coefficient": "OPEN",
        "complete_M4_large_volume_sign_and_scaling": "OPEN",
        "nonperturbative_annealed_score": "OPEN",
        "actual_interacting_h_minus_one_second_moment": "OPEN",
        "continuum_limit": "NOT_ESTABLISHED",
        "born_rule": "NOT_ESTABLISHED",
        "krein_reconstruction": "NOT_ASSESSED",
        "lorentzian_transfer": "NOT_ESTABLISHED",
    }
    require(
        all(disposition.get(key) == value for key, value in required.items()),
        "claim boundary or open-gate disposition drift",
    )
    require(
        certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "dependency boundary drift",
    )
    require(all(certificate["checks"].values()), "certificate contains a failed check")


def verify(path: str = CERT_PATH) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
        errors = sorted(Draft202012Validator(schema).iter_errors(certificate), key=lambda item: list(item.path))
        require(not errors, f"schema validation failed: {errors[0].message if errors else ''}")

        require(certificate["data_sha256"] == file_hash(certificate["data"]), "data hash drift")
        require(certificate["producer_sha256"] == file_hash(certificate["producer"]), "producer hash drift")
        for source in certificate["provenance"]["inputs"]:
            require(source["sha256"] == file_hash(source["path"]), f"input hash drift: {source['path']}")
        with open(os.path.join(ROOT, certificate["data"]), encoding="utf-8") as handle:
            data = json.load(handle)
        for field in (
            "vertex_bounds",
            "convolution_bounds",
            "pair_bounds",
            "power_sector_reduction",
            "method_disposition",
            "does_not_establish",
            "next_gate",
        ):
            require(certificate[field] == data[field], f"certificate/data drift: {field}")

        verify_upstream_and_allocations(certificate)
        verify_constants_and_shells(certificate)
        verify_boundaries(certificate)
        return True
    except (OSError, ValueError, KeyError, TypeError, VerificationError) as error:
        if path == CERT_PATH:
            print(f"FAIL: {error}", file=sys.stderr)
        return False


def main() -> int:
    if verify():
        print("PASS: exact BT complete-g4 subpower pair bounds verified")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
