#!/usr/bin/env python3
"""Independent verifier for the slice-valid BT weighted-current V2 gate."""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator, ValidationError


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_WEIGHTED_CURRENT_GATE_V2.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-euclidean-full-phase-weighted-current-gate-v2.schema.json")


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def frac(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def digest(relative: str) -> str:
    value = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            value.update(block)
    return value.hexdigest()


def pow_two(exponent: int) -> Fraction:
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2 ** (-exponent))


def reconstruct(matrix: list[list[int]]) -> dict:
    length = 4
    points = list(itertools.product(range(length), repeat=4))
    omega = {point: pow_two(matrix[point[0]][point[1]]) for point in points}

    def shift(point: tuple[int, ...], axis: int, step: int) -> tuple[int, ...]:
        changed = list(point)
        changed[axis] = (changed[axis] + step) % length
        return tuple(changed)

    residual = {}
    for point in points:
        residual[point] = sum(
            (omega[shift(point, axis, step)] / omega[point] for axis in range(4) for step in (-1, 1)),
            Fraction(-8),
        )
    potential = {point: residual[point] / omega[point] ** 2 for point in points}
    currents = {axis: {} for axis in range(4)}
    correctors = {axis: {} for axis in range(4)}
    identity_ok = True
    energy = Fraction(0)
    for point in points:
        for axis in range(4):
            other = shift(point, axis, 1)
            current = residual[point] * omega[other] / omega[point] - residual[other] * omega[point] / omega[other]
            conductance = omega[point] * omega[other]
            currents[axis][point] = current
            correctors[axis][point] = current - (potential[point] - potential[other])
            identity_ok &= current == conductance * (potential[point] - potential[other])
            energy += conductance * (potential[point] - potential[other]) ** 2
    exponent_sum = sum(matrix[point[0]][point[1]] for point in points)
    cosine_projection = sum(matrix[point[0]][point[1]] * (1, 0, -1, 0)[point[0]] for point in points)
    sine_projection = sum(matrix[point[0]][point[1]] * (0, 1, 0, -1)[point[0]] for point in points)
    return {
        "exponent_sum": exponent_sum,
        "cosine_projection": cosine_projection,
        "sine_projection": sine_projection,
        "residual_matrix": [[residual[(time, space, 0, 0)] for space in range(4)] for time in range(4)],
        "current_matrix": [[currents[0][(time, space, 0, 0)] for space in range(4)] for time in range(4)],
        "time_current_zero_mode": sum(currents[0].values(), Fraction(0)),
        "time_corrector_zero_mode": sum(correctors[0].values(), Fraction(0)),
        "action": sum((value * value for value in residual.values()), Fraction(0)) / 2,
        "identity_ok": identity_ok,
        "weighted_mean": sum(omega[point] ** 3 * potential[point] for point in points),
        "energy": energy,
    }


def verify(path: str = DEFAULT_CERT) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA, encoding="utf-8") as handle:
            Draft202012Validator(json.load(handle)).validate(cert)
        for item in cert["provenance"]["inputs"]:
            require(digest(item["path"]) == item["sha256"], "input hash drift")
        old_path = cert["provenance"]["inputs"][0]["path"]
        with open(os.path.join(ROOT, old_path), encoding="utf-8") as handle:
            predecessor = json.load(handle)
        old_row = [frac(value) for value in predecessor["exact_current_fixture"]["positive_field_time_row"]]
        require(old_row == [1, 1, 2, 4], "V1 fixture drift")
        old_exponents = [0, 0, 1, 2]
        require(sum(old_exponents[t] * (1, 0, -1, 0)[t] for t in range(4)) == -1, "V1 cosine projection unexpectedly vanished")
        require(sum(old_exponents[t] * (0, 1, 0, -1)[t] for t in range(4)) == -2, "V1 sine projection unexpectedly vanished")
        fixture = cert["slice_valid_fixture"]
        values = reconstruct(fixture["exponent_matrix_time_by_space"])
        require(values["exponent_sum"] == values["cosine_projection"] == values["sine_projection"] == 0, "fixture is not in E_p perpendicular")
        require([[frac(value) for value in row] for row in fixture["active_residual_matrix"]] == values["residual_matrix"], "residual matrix drift")
        require([[frac(value) for value in row] for row in fixture["active_forward_time_current_matrix"]] == values["current_matrix"], "current matrix drift")
        require(frac(fixture["full_time_current_zero_mode"]) == values["time_current_zero_mode"] == -24, "slice current zero mode drift")
        require(frac(fixture["full_action"]) == values["action"] == Fraction(837, 2), "slice action drift")
        require(frac(fixture["weighted_dirichlet_energy"]) == values["energy"] == Fraction(290295, 16), "Dirichlet energy drift")
        require(frac(fixture["weighted_potential_mean"]) == values["weighted_mean"] == 0, "weighted mean drift")
        require(values["identity_ok"], "weighted current identity failed")
        normal = cert["weighted_current_normal_form"]
        require(normal["identity"] == "J_xy=c_xy*(u_x-u_y)", "weighted identity text drift")
        require(normal["weighted_zero_mean"] == "sum_x Omega_x^3*u_x=sum_x (Delta Omega)_x=0", "weighted zero-mean text drift")
        split = cert["plain_gradient_corrector_split"]
        require(split["decomposition"] == "J_(x,i)=(grad_i u)_x+K_(x,i)", "corrector decomposition drift")
        require(split["axial_fourier_identity"] == "Jhat_1(p)=(1-exp(-i*p_1))*uhat(p)+Khat_1(p)", "corrector Fourier identity drift")
        require(frac(split["fixture_corrector_time_zero_mode"]) == values["time_corrector_zero_mode"] == -24, "corrector zero mode drift")
        disposition = cert["method_disposition"]
        require(disposition["v1_fixture_as_full_phase_slice_witness"] == "WITHDRAWN_SCOPE_ERROR", "V1 scope error not recorded")
        require(disposition["slice_valid_unweighted_periodic_gradient_identity"] == "OBSTRUCTED", "slice obstruction weakened")
        require(disposition["weighted_random_conductance_gradient_identity"] == "PROVED", "weighted identity omitted")
        require(disposition["plain_gradient_corrector_split"] == "PROVED", "corrector split omitted")
        require(disposition["weighted_potential_mass_structure_factor_bound"] == "OPEN", "weighted-potential mass bound promoted")
        require(disposition["conductance_corrector_hyperuniformity_bound"] == "OPEN", "corrector hyperuniformity promoted")
        require(disposition["translation_invariant_flux_corrector_bound"] == "OPEN", "flux corrector promoted")
        require(disposition["translation_invariant_current_susceptibility_bound"] == "OPEN", "susceptibility promoted")
        require(disposition["actual_interacting_H_minus_one_second_moment"] == "OPEN", "H-minus-one promoted")
        require(cert["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "dependency boundary drift")
        require(all(cert["checks"].values()), "producer check false")
        return True
    except (OSError, KeyError, TypeError, ValueError, VerificationError, ValidationError):
        return False


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CERT
    ok = verify(path)
    print("BT full-phase weighted-current V2 gate: PASS" if ok else "BT full-phase weighted-current V2 gate: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
