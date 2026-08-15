#!/usr/bin/env python3
"""Independent verifier for the BT flux-corrector pointwise-energy no-go."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator, ValidationError


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FLUX_CORRECTOR_POINTWISE_ENERGY_NO_GO_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-euclidean-flux-corrector-pointwise-energy-no-go-v1.schema.json")
MATRIX = (
    (0, 0, 0, 0),
    (0, 0, 1, -1),
    (0, 1, 0, -1),
    (0, 0, 0, 0),
)


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


def omega_at(length: int, time: int, space: int) -> Fraction:
    exponent = MATRIX[time][space % 4] if time < 4 else 0
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2 ** (-exponent))


def enumerate_slab(length: int) -> dict[str, object]:
    """Independently enumerate the two active coordinates and multiply inert sites."""
    omega = {(t, s): omega_at(length, t, s) for t in range(length) for s in range(length)}

    def at(t: int, s: int) -> Fraction:
        return omega[(t % length, s % length)]

    residual = {}
    for t in range(length):
        for s in range(length):
            here = at(t, s)
            residual[(t, s)] = Fraction(-4) + at(t - 1, s) / here + at(t + 1, s) / here + at(t, s - 1) / here + at(t, s + 1) / here
    potential = {site: residual[site] / omega[site] ** 2 for site in residual}
    action_two_dimensional = sum((value * value for value in residual.values()), Fraction(0)) / 2
    energy_two_dimensional = Fraction(0)
    current_rows = []
    potential_rows = []
    for t in range(length):
        row_current = Fraction(0)
        row_potential = Fraction(0)
        for s in range(length):
            here = (t, s)
            ahead = ((t + 1) % length, s)
            conductance = omega[here] * omega[ahead]
            row_current += conductance * (potential[here] - potential[ahead])
            row_potential += potential[here]
            for other in (ahead, (t, (s + 1) % length)):
                edge_conductance = omega[here] * omega[other]
                difference = potential[here] - potential[other]
                energy_two_dimensional += edge_conductance * difference * difference
        current_rows.append(row_current)
        potential_rows.append(row_potential)
    inert = length * length
    return {
        "action": action_two_dimensional * inert,
        "energy": energy_two_dimensional * inert,
        "current_rows": current_rows,
        "potential_rows": potential_rows,
        "time_slice_exponent_sums": [sum((MATRIX[t][s % 4] if t < 4 else 0 for s in range(length))) for t in range(length)],
    }


def verify(path: str = DEFAULT_CERT) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA, encoding="utf-8") as handle:
            Draft202012Validator(json.load(handle)).validate(cert)
        require(cert["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "dependency boundary drift")
        inputs = cert["provenance"]["inputs"]
        require(len(inputs) == 1 and digest(inputs[0]["path"]) == inputs[0]["sha256"], "input hash drift")
        family = cert["localized_slab_family"]
        require(family["exponent_matrix_time_by_space"] == [list(row) for row in MATRIX], "slab matrix drift")
        scaling = cert["cell_and_scaling_data"]
        expected_current = [Fraction(-69, 8), Fraction(15, 8), Fraction(21, 4), Fraction(1, 2), Fraction(-1, 2)]
        expected_potential = [Fraction(1, 2), Fraction(335, 16), Fraction(27, 2), Fraction(1, 2)]
        require([frac(value) for value in scaling["forward_time_current_row_sums_at_t_0_1_2_3_L_minus_1"]] == expected_current, "current row data drift")
        require([frac(value) for value in scaling["weighted_potential_row_sums"]] == expected_potential, "potential row data drift")
        for length in (8, 12):
            values = enumerate_slab(length)
            multiplier = length // 4
            require(values["time_slice_exponent_sums"] == [0] * length, f"E_p orthogonality failed at L={length}")
            require(values["action"] == Fraction(837, 128) * length**3, f"action scaling failed at L={length}")
            require(values["energy"] == Fraction(290423, 1024) * length**3, f"energy scaling failed at L={length}")
            require(values["current_rows"][:4] == [multiplier * value for value in expected_current[:4]], f"current replication failed at L={length}")
            require(values["current_rows"][-1] == multiplier * expected_current[-1], f"periodic boundary current failed at L={length}")
            require(values["potential_rows"][:4] == [multiplier * value for value in expected_potential], f"potential replication failed at L={length}")
            require(values["current_rows"][4:-1] == [0] * (length - 5), f"unexpected current outside boundary rows at L={length}")
            require(values["potential_rows"][4:] == [0] * (length - 4), f"potential leaked outside slab at L={length}")
        ratios = cert["diverging_ratios"]
        omega_upper = Fraction(1936, 49)
        lower_square = Fraction(9, 256)
        require(frac(ratios["action_ratio_linear_coefficient"]) == lower_square / (omega_upper * Fraction(837, 128)) == Fraction(49, 360096), "action ratio drift")
        require(frac(ratios["dirichlet_ratio_linear_coefficient"]) == lower_square / (omega_upper * Fraction(290423, 1024)) == Fraction(9, 2868668), "Dirichlet ratio drift")
        require(frac(ratios["combined_ratio_linear_coefficient"]) == lower_square / (omega_upper * Fraction(297119, 1024)) == Fraction(441, 143805596), "combined ratio drift")
        quotient = [Fraction(4), 0, -4, 0, 5, -4, 1]
        numerator = [Fraction(0)] * 9
        for degree, coefficient in enumerate(quotient):
            numerator[degree] += coefficient
            numerator[degree + 2] += coefficient
        numerator[0] -= 4
        require(numerator == [Fraction(0), 0, 0, 0, 1, -4, 6, -4, 1], "Dalzell polynomial identity failed")
        require(sum((Fraction(coefficient, degree + 1) for degree, coefficient in enumerate(quotient)), Fraction(0)) == Fraction(22, 7), "Dalzell quotient integral failed")
        require(Fraction(3, 8) - Fraction(891, 16 * 300) >= Fraction(3, 16), "large-L corrector lower bound failed")
        disposition = cert["method_disposition"]
        require(disposition["pointwise_corrector_bound_by_N_omega_action"] == "OBSTRUCTED", "action no-go weakened")
        require(disposition["pointwise_corrector_bound_by_N_omega_weighted_dirichlet_energy"] == "OBSTRUCTED", "energy no-go weakened")
        require(disposition["Gibbs_corrector_hyperuniformity_bound"] == "OPEN", "Gibbs corrector promoted")
        require(disposition["translation_invariant_current_susceptibility_bound"] == "OPEN", "susceptibility promoted")
        require(disposition["actual_interacting_H_minus_one_second_moment"] == "OPEN", "H-minus-one promoted")
        require(disposition["continuum_limit"] == "NOT_ESTABLISHED", "continuum promoted")
        require(disposition["born_rule"] == "NOT_ESTABLISHED", "Born rule promoted")
        require(disposition["krein_reconstruction"] == "NOT_ASSESSED", "Krein promoted")
        require(disposition["lorentzian_transfer"] == "NOT_ESTABLISHED", "Lorentzian transfer promoted")
        require(all(cert["checks"].values()), "producer check false")
        return True
    except (OSError, KeyError, TypeError, ValueError, VerificationError, ValidationError):
        return False


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CERT
    ok = verify(path)
    print("BT flux-corrector pointwise-energy no-go: PASS" if ok else "BT flux-corrector pointwise-energy no-go: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
