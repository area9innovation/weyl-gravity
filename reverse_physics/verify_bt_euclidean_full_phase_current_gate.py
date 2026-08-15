#!/usr/bin/env python3
"""Independent verifier for the BT full-phase current gate."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator, ValidationError


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_CURRENT_GATE_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-euclidean-full-phase-current-gate-v1.schema.json")


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


def reconstruct() -> dict:
    length = 4
    volume = length**4
    time_row = (Fraction(1), Fraction(1), Fraction(2), Fraction(4))
    omega = []
    coordinates = []
    for index in range(volume):
        coordinate = []
        value = index
        for _ in range(4):
            coordinate.append(value % length)
            value //= length
        coordinates.append(tuple(coordinate))
        omega.append(time_row[coordinate[0]])

    def index_of(coordinate: tuple[int, ...]) -> int:
        return sum((coordinate[axis] % length) * length**axis for axis in range(4))

    residual = []
    for coordinate, center in zip(coordinates, omega):
        row = Fraction(-8)
        for axis in range(4):
            for sign in (-1, 1):
                neighbor = list(coordinate)
                neighbor[axis] += sign
                row += omega[index_of(tuple(neighbor))] / center
        residual.append(row)
    current = []
    for index, coordinate in enumerate(coordinates):
        neighbor = list(coordinate)
        neighbor[0] += 1
        other = index_of(tuple(neighbor))
        current.append(
            residual[index] * omega[other] / omega[index]
            - residual[other] * omega[index] / omega[other]
        )
    direct_gradient = []
    current_divergence = []
    for index, coordinate in enumerate(coordinates):
        outgoing_weight = Fraction(0)
        incoming_term = Fraction(0)
        divergence = Fraction(0)
        for axis in range(4):
            forward_coordinate = list(coordinate)
            forward_coordinate[axis] += 1
            forward = index_of(tuple(forward_coordinate))
            backward_coordinate = list(coordinate)
            backward_coordinate[axis] -= 1
            backward = index_of(tuple(backward_coordinate))
            outgoing_weight += omega[forward] / omega[index]
            outgoing_weight += omega[backward] / omega[index]
            incoming_term += residual[forward] * omega[index] / omega[forward]
            incoming_term += residual[backward] * omega[index] / omega[backward]
            forward_current = (
                residual[index] * omega[forward] / omega[index]
                - residual[forward] * omega[index] / omega[forward]
            )
            backward_current = (
                residual[backward] * omega[index] / omega[backward]
                - residual[index] * omega[backward] / omega[index]
            )
            divergence -= forward_current - backward_current
        direct_gradient.append(-residual[index] * outgoing_weight + incoming_term)
        current_divergence.append(divergence)
    return {
        "residual_time_row": tuple(residual[t] for t in range(4)),
        "current_time_row": tuple(current[t] for t in range(4)),
        "full_current": sum(current, Fraction(0)),
        "full_action": sum((value * value for value in residual), Fraction(0)) / 2,
        "current_divergence_matches_direct_gradient": current_divergence == direct_gradient,
    }


def verify(path: str = DEFAULT_CERT) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA, encoding="utf-8") as handle:
            Draft202012Validator(json.load(handle)).validate(cert)
        for item in cert["provenance"]["inputs"]:
            require(digest(item["path"]) == item["sha256"], "input hash drift")
        values = reconstruct()
        fixture = cert["exact_current_fixture"]
        require(tuple(map(frac, fixture["residual_time_row"])) == values["residual_time_row"], "residual drift")
        require(tuple(map(frac, fixture["forward_current_time_row"])) == values["current_time_row"], "current row drift")
        require(frac(fixture["full_current_zero_mode"]) == values["full_current"] == -444, "full current drift")
        require(frac(fixture["full_action"]) == values["full_action"] == 378, "full action drift")
        require(frac(fixture["current_zero_mode_per_spatial_site"]) == Fraction(-111, 16), "current density drift")
        require(values["current_divergence_matches_direct_gradient"], "current-divergence identity fails on exact fixture")
        reduction = cert["full_phase_reduction"]
        require(reduction["status"] == "EXACT_TRANSLATION_INVARIANT_TWO_MODE_REDUCTION", "phase reduction drift")
        require("(36+81*C_s)" in reduction["resulting_pair_moment"], "pair constant drift")
        identity = cert["current_identity"]
        require(identity["canonical_oriented_current"] == "J_(x,i)=r_x*w_(x,x+e_i)-r_(x+e_i)*w_(x+e_i,x)", "current definition drift")
        require(identity["action_gradient"] == "G_x=partial A/partial psi_x=-sum_i[J_(x,i)-J_(x-e_i,i)]", "action-gradient identity drift")
        require(identity["fourier_divergence"] == "Ghat(p)=sum_i[exp(i*p_i)-1]*Jhat_i(p)", "Fourier-divergence identity drift")
        require("omega_p/g^2" in identity["axial_score_identity"], "score identity missing")
        require("g^2*N*omega_p" in identity["equivalent_current_gate"], "current gate missing")
        disposition = cert["method_disposition"]
        require(disposition["pointwise_second_factor_from_canonical_current_gradient"] == "OBSTRUCTED", "pointwise obstruction weakened")
        require(disposition["translation_invariant_current_susceptibility_bound"] == "OPEN", "current theorem promoted")
        require(disposition["actual_interacting_H_minus_one_second_moment"] == "OPEN", "H-minus-one promoted")
        require(cert["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "dependency boundary drift")
        require(all(cert["checks"].values()), "producer check false")
        return True
    except (OSError, KeyError, TypeError, ValueError, VerificationError, ValidationError):
        return False


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CERT
    ok = verify(path)
    print("BT full-phase current gate certificate: PASS" if ok else "BT full-phase current gate certificate: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
