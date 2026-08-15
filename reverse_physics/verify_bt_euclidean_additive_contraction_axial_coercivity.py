#!/usr/bin/env python3
"""Independent verifier for the BT contraction and axial theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_"
    "ADDITIVE_CONTRACTION_AXIAL_COERCIVITY_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-"
    "additive-contraction-axial-coercivity-v1.schema.json",
)

Gaussian = tuple[Fraction, Fraction]
Laurent = dict[int, Gaussian]
ZERO: Gaussian = (Fraction(0), Fraction(0))


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def gadd(left: Gaussian, right: Gaussian) -> Gaussian:
    return left[0] + right[0], left[1] + right[1]


def gmul(left: Gaussian, right: Gaussian) -> Gaussian:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def ladd(left: Laurent, right: Laurent) -> Laurent:
    result = dict(left)
    for power, coefficient in right.items():
        result[power] = gadd(result.get(power, ZERO), coefficient)
        if result[power] == ZERO:
            del result[power]
    return result


def lscale(value: Laurent, scalar: Fraction | int) -> Laurent:
    scalar = Fraction(scalar)
    return {
        power: (scalar * coefficient[0], scalar * coefficient[1])
        for power, coefficient in value.items()
    }


def lmul(left: Laurent, right: Laurent) -> Laurent:
    result: Laurent = {}
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            power = left_power + right_power
            result[power] = gadd(
                result.get(power, ZERO),
                gmul(left_coefficient, right_coefficient),
            )
    return {power: value for power, value in result.items() if value != ZERO}


def lderivative(value: Laurent) -> Laurent:
    result: Laurent = {}
    for power, (real, imaginary) in value.items():
        result[power] = (-power * imaginary, power * real)
    return {power: coefficient for power, coefficient in result.items() if coefficient != ZERO}


def exact_fourier_fixture() -> dict[str, Fraction]:
    sine: Laurent = {
        1: (Fraction(0), Fraction(-1, 2)),
        -1: (Fraction(0), Fraction(1, 2)),
    }
    derivative = lderivative(sine)
    residual = ladd(derivative, lmul(sine, sine))
    second = lderivative(derivative)
    current = ladd(second, lscale(lmul(lmul(sine, sine), sine), -2))
    gradient = lderivative(current)
    residual_square = lmul(residual, residual).get(0, ZERO)
    gradient_square = lmul(gradient, gradient).get(0, ZERO)
    return {
        "residual_norm": residual_square[0],
        "gradient_norm": gradient_square[0],
        "residual_imaginary": residual_square[1],
        "gradient_imaginary": gradient_square[1],
    }


def reconstruct_cycle_fixture(section: dict) -> dict[str, object]:
    omega = [decode(value) for value in section["omega"]]
    parameter = decode(section["s"])
    size = len(omega)

    def residual(field: list[Fraction]) -> list[Fraction]:
        edges = [(site, (site + 1) % size) for site in range(size)]
        laplacian = [Fraction(0) for _ in field]
        for left, right in edges:
            difference = field[right] - field[left]
            laplacian[left] += difference
            laplacian[right] -= difference
        return [laplacian[site] / field[site] for site in range(size)]

    initial = residual(omega)
    deformed = [(1 - parameter) * value + parameter for value in omega]
    later = residual(deformed)
    predicted = [
        initial[site]
        * (1 - parameter)
        * omega[site]
        / deformed[site]
        for site in range(size)
    ]
    initial_action = sum((value**2 for value in initial), Fraction(0)) / 2
    later_action = sum((value**2 for value in later), Fraction(0)) / 2
    derivative = -sum(
        (initial[site] ** 2 / omega[site] for site in range(size)),
        Fraction(0),
    )
    return {
        "initial": initial,
        "deformed": deformed,
        "later": later,
        "predicted": predicted,
        "initial_action": initial_action,
        "later_action": later_action,
        "derivative": derivative,
    }


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False
    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    recorded = {
        row["path"]: row["sha256"] for row in certificate["provenance"]["inputs"]
    }
    checks["provenance_hashes_current"] = len(recorded) == 3 and all(
        file_hash(relative) == digest for relative, digest in recorded.items()
    )
    contraction = certificate["additive_positive_field_contraction"]
    fixture = contraction["exact_fixture"]
    rebuilt = reconstruct_cycle_fixture(fixture)
    checks["cycle_residuals_reconstructed"] = (
        rebuilt["initial"] == [decode(value) for value in fixture["residual"]]
        and rebuilt["later"]
        == [decode(value) for value in fixture["deformed_residual"]]
        and rebuilt["later"] == rebuilt["predicted"]
    )
    checks["cycle_action_drop_reconstructed"] = (
        rebuilt["initial_action"] == decode(fixture["initial_action"])
        and rebuilt["later_action"] == decode(fixture["deformed_action"])
        and rebuilt["initial_action"] - rebuilt["later_action"]
        == decode(fixture["strict_action_drop"])
        and rebuilt["initial_action"] > rebuilt["later_action"]
    )
    checks["cycle_derivative_reconstructed"] = (
        rebuilt["derivative"] == decode(fixture["action_derivative_at_zero"])
        and rebuilt["derivative"] == -9
    )
    axial = certificate["continuum_axial_coercivity"]["exact_fixture"]
    fourier = exact_fourier_fixture()
    checks["independent_fourier_fixture"] = (
        fourier["residual_imaginary"] == 0
        and fourier["gradient_imaginary"] == 0
        and fourier["residual_norm"]
        == decode(axial["residual_norm_squared_average"])
        == Fraction(7, 8)
        and fourier["gradient_norm"]
        == decode(axial["gradient_norm_squared_average"])
        == Fraction(17, 4)
        and fourier["gradient_norm"] - fourier["residual_norm"]
        == decode(axial["strict_gap_above_sharp_constant_one"])
        == Fraction(27, 8)
    )
    ward = certificate["reciprocal_field_ward_identity"]
    checks["ward_chain_recorded"] = (
        ward["vector_field"] == "X(psi)=P_H*exp(-psi)=P_H*Omega^(-1)"
        and "-(1-1/N)" in ward["divergence"]
        and "-sum_x r_x^2/Omega_x" in ward["gradient_pairing"]
        and "lambda^2*(1-1/N)" in ward["identity"]
    )
    axial_theorem = certificate["continuum_axial_coercivity"]
    checks["axial_proof_chain_recorded"] = (
        axial_theorem["first_identity"]
        == "||R||_2^2=X+Y, X=||u'||_2^2, Y=||u||_4^4"
        and "X+2Y" in axial_theorem["pairing"]
        and "k_1^2*(X+Y)" in axial_theorem["first_poincare_step"]
        and axial_theorem["theorem"]
        == "||E||_2^2>=k_1^4*||R||_2^2, k_1=2*pi/ell"
    )
    hodge = certificate["multidimensional_hodge_gate"]
    checks["multidimensional_hodge_gate_recorded"] = (
        "E=delta A/delta psi=div j" in hodge["definitions"]
        and hodge["curl_identity"] == "d(j_flat)=-2*dR wedge dpsi"
        and "exact Hodge component" in hodge["higher_dimensional_failure_mode"]
        and hodge["status"] == "OPEN"
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
        "REDUCED-MODE",
    ]
    checks["method_boundary"] = (
        certificate["method_disposition"]["finite_volume_sublevel_topology"]
        == "CONTRACTIBLE"
        and certificate["method_disposition"][
            "continuum_one_dimensional_gradient_domination"
        ]
        == "PROVED"
        and certificate["method_disposition"][
            "multidimensional_transverse_current_control"
        ]
        == "OPEN"
        and certificate["method_disposition"]["volume_uniform_witten_coercivity"]
        == "OPEN"
        and certificate["method_disposition"]["interacting_h_minus_one_bound"]
        == "OPEN"
    )
    checks["certificate_checks_closed"] = (
        certificate["checks"]["ok"]
        and certificate["checks"]["passed"] == certificate["checks"]["total"]
        and not certificate["checks"]["failures"]
        and all(certificate["checks"]["details"].values())
    )
    checks["required_nonclaims"] = {
        "a full multidimensional volume-uniform gradient bound",
        "a Poincare inequality or Witten one-form coercivity",
        "an unweighted residual, field, or H^-1 moment estimate",
        "anything LORENTZIAN-CAUSAL",
    }.issubset(set(certificate["does_not_establish"]))
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return all(checks.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
