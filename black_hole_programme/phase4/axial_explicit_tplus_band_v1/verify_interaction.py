#!/usr/bin/env python3
"""Independent exact/metadata verifier for the interaction-picture result."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

Matrix = list[list[Fraction]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(value: list[list[str]]) -> Matrix:
    return [[Fraction(entry) for entry in row] for row in value]


def zeros(rows: int, cols: int) -> Matrix:
    return [[Fraction(0) for _ in range(cols)] for _ in range(rows)]


def identity(n: int) -> Matrix:
    result = zeros(n, n)
    for index in range(n):
        result[index][index] = Fraction(1)
    return result


def add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[i][j] + right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def sub(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[i][j] - right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def mul(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            sum(
                (left[i][k] * right[k][j] for k in range(len(right))),
                Fraction(0),
            )
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def neg(value: Matrix) -> Matrix:
    return [[-entry for entry in row] for row in value]


def inv2(value: Matrix) -> Matrix:
    determinant = value[0][0] * value[1][1] - value[0][1] * value[1][0]
    if determinant == 0:
        raise AssertionError("singular exact fixture pivot")
    return [
        [value[1][1] / determinant, -value[0][1] / determinant],
        [-value[1][0] / determinant, value[0][0] / determinant],
    ]


def hstack(*blocks: Matrix) -> Matrix:
    return [sum((block[row] for block in blocks), []) for row in range(len(blocks[0]))]


def vstack(*blocks: Matrix) -> Matrix:
    return sum(blocks, [])


def block_diag3(first: Matrix, second: Matrix, third: Matrix) -> Matrix:
    z = zeros(2, 2)
    return vstack(hstack(first, z, z), hstack(z, second, z), hstack(z, z, third))


def is_zero(value: Matrix) -> bool:
    return all(entry == 0 for row in value for entry in row)


def independent_exact_check(data: dict) -> None:
    fixture = data["exact_interaction_picture"]
    matrices = {
        name: decode(value) for name, value in fixture["inputs"].items()
    }
    A, E, D, C, Ax = (
        matrices["A"],
        matrices["E"],
        matrices["D"],
        matrices["C"],
        matrices["Ax"],
    )
    P, R, Q = matrices["P"], matrices["R"], matrices["Q"]
    dotP, dotQ = matrices["dotP"], matrices["dotQ"]
    Pinv = inv2(P)
    Pp, Rp = mul(A, P), mul(Ax, R)
    dotPp = add(mul(E, P), mul(A, dotP))
    Qp = add(mul(A, Q), mul(D, R))
    dotQp = add(add(mul(E, Q), mul(A, dotQ)), mul(C, R))
    Pinvp = neg(mul(mul(Pinv, Pp), Pinv))

    J = mul(Pinv, dotP)
    K = mul(Pinv, Q)
    dotK = sub(mul(Pinv, dotQ), mul(J, K))
    Jp = add(mul(Pinv, dotPp), mul(Pinvp, dotP))
    Kp = add(mul(Pinv, Qp), mul(Pinvp, Q))
    dotKp = sub(
        add(mul(Pinvp, dotQ), mul(Pinv, dotQp)),
        add(mul(Jp, K), mul(J, Kp)),
    )

    if J != decode(fixture["derived"]["J"]):
        raise AssertionError("J fixture drift")
    if K != decode(fixture["derived"]["K"]):
        raise AssertionError("K fixture drift")
    if dotK != decode(fixture["derived"]["dotK"]):
        raise AssertionError("dotK fixture drift")
    if Jp != mul(mul(Pinv, E), P):
        raise AssertionError("J differential identity failed")
    drive = mul(mul(Pinv, D), R)
    if Kp != drive:
        raise AssertionError("K differential identity failed")
    if dotKp != sub(mul(mul(Pinv, C), R), mul(J, drive)):
        raise AssertionError("dotK differential identity failed")

    z, eye = zeros(2, 2), identity(2)
    unit = vstack(
        hstack(eye, J, add(mul(J, K), dotK)),
        hstack(z, eye, K),
        hstack(z, z, eye),
    )
    factorized = mul(block_diag3(P, P, R), unit)
    expected = vstack(
        hstack(P, dotP, dotQ),
        hstack(z, P, Q),
        hstack(z, z, R),
    )
    if factorized != expected:
        raise AssertionError("six-state reconstruction failed")
    if factorized != decode(fixture["derived"]["F6"]):
        raise AssertionError("stored six-state witness drift")

    chart = {key: Fraction(value) for key, value in fixture["chart_fixture"].items()}
    q, qt, z1, zt = chart["q"], chart["q_tau"], chart["z"], chart["z_tau"]
    p, pt, z2, z2t = chart["p"], chart["p_tau"], chart["z2"], chart["z2_tau"]
    if p != 1 / q or pt != -qt / q**2:
        raise AssertionError("reciprocal chart law failed")
    if [z1, z1 * q] != [z2 * p, z2]:
        raise AssertionError("chart base reconstruction failed")
    if [zt, zt * q + z1 * qt] != [z2t * p + z2 * pt, z2t]:
        raise AssertionError("chart tangent reconstruction failed")
    if not fixture["all_zero"]:
        raise AssertionError("producer exact gate is false")
    if not all(is_zero(decode(value)) for value in fixture["residuals"].values()):
        raise AssertionError("stored exact residual is nonzero")


def verify(path: Path) -> None:
    data = json.loads(path.read_text())
    if data.get("status") != "INTERACTION_PICTURE_EXACT_AND_MICRO_SUCCESSOR_PASS_R4_OPEN":
        raise AssertionError("interaction result is not certified")
    independent_exact_check(data)

    for imported in data["imports"].values():
        imported_path = ROOT / imported["path"]
        if sha256(imported_path) != imported["sha256"]:
            raise AssertionError(f"import hash drift: {imported['path']}")
    predecessor = json.loads(
        (ROOT / data["imports"]["predecessor"]["path"]).read_text()
    )
    if predecessor["payload_sha256"] != data["imports"]["predecessor"]["payload_sha256"]:
        raise AssertionError("predecessor payload drift")

    successor = data["validated_micro_successor"]
    checkpoint_path = ROOT / successor["checkpoint"]
    manifest_path = ROOT / successor["manifest"]
    if sha256(checkpoint_path) != successor["checkpoint_sha256"]:
        raise AssertionError("successor checkpoint hash drift")
    if sha256(manifest_path) != successor["manifest_sha256"]:
        raise AssertionError("successor manifest hash drift")
    checkpoint = json.loads(checkpoint_path.read_text())
    manifest = json.loads(manifest_path.read_text())
    if successor["radial_start"] != "487/16" or successor["radial_end"] != "3895/128":
        raise AssertionError("declared micro-successor radial interval drift")
    if checkpoint["payload_sha256"] != successor["payload_sha256"]:
        raise AssertionError("successor payload identity drift")
    if checkpoint["payload"]["radius"] != "3895/128":
        raise AssertionError("micro-successor radial endpoint drift")
    if checkpoint["payload"]["generator"] != 7315:
        raise AssertionError("frequency generator drift")
    summary = manifest["run"]["summary"]
    if not summary["coefficients"] or not summary["containment"]:
        raise AssertionError("direct/jet Forge gate failed")
    if float(summary["tail"]) >= 0.5 or float(summary["width"]) >= 10.0:
        raise AssertionError("Forge tail or width gate failed")

    point = data["physical_center_fixture"]
    if point["status"] != "POINT_FIXTURE_PASS":
        raise AssertionError("physical point fixture refused")
    if max(point["residuals"].values()) >= point["threshold"]:
        raise AssertionError("physical point residual gate failed")
    if point["forced_chart_switch"]["spin2_abs_q"] <= 0:
        raise AssertionError("spin-two chart switch was not admissible")
    if point["forced_chart_switch"]["spin1_abs_q"] <= 0:
        raise AssertionError("spin-one chart switch was not admissible")

    flags = data["claim_flags"]
    for key in (
        "interaction_picture_identity_exact",
        "reciprocal_chart_transition_exact",
        "wronskian_fixture_pass",
        "physical_point_interaction_direct_agreement",
        "validated_correlated_successor_beyond_487_over_16",
    ):
        if flags.get(key) is not True:
            raise AssertionError(f"missing positive gate: {key}")
    for key in (
        "validated_projective_interval_transport_to_r4",
        "complete_outgoing_frame_at_r4",
        "explicit_Tplus_certified",
        "reflection_or_stokes_certified",
    ):
        if flags.get(key) is not False:
            raise AssertionError(f"overclaim: {key}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--certificate", type=Path, default=HERE / "interaction_certificate.json"
    )
    args = parser.parse_args()
    verify(args.certificate)
    print("PASS: exact interaction picture and validated micro-successor")


if __name__ == "__main__":
    main()
