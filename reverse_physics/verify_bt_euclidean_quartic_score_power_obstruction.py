#!/usr/bin/env python3
"""Independent verifier for the quartic-score power obstruction."""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_QUARTIC_SCORE_POWER_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-quartic-score-power-obstruction-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def decode_gaussian(value: dict) -> tuple[Fraction, Fraction]:
    return decode(value["real"]), decode(value["imaginary"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def load(relative: str) -> dict:
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


# Independent exact first-order Gaussian-integer algebra.  A polynomial is
# represented as (constant, epsilon coefficient), each entry a (real, imag)
# Fraction pair.
def cadd(a, b):
    return a[0] + b[0], a[1] + b[1]


def cneg(a):
    return -a[0], -a[1]


def csub(a, b):
    return cadd(a, cneg(b))


def cmul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def cscale(a, scalar):
    scalar = Fraction(scalar)
    return scalar * a[0], scalar * a[1]


CZ = (Fraction(0), Fraction(0))
CO = (Fraction(1), Fraction(0))
CI = (Fraction(0), Fraction(1))


def padd(a, b):
    return cadd(a[0], b[0]), cadd(a[1], b[1])


def psub(a, b):
    return csub(a[0], b[0]), csub(a[1], b[1])


def pmul(a, b):
    return cmul(a[0], b[0]), cadd(cmul(a[1], b[0]), cmul(a[0], b[1]))


def phase(component, sign):
    turns, slope = component
    roots = (CO, CI, cneg(CO), cneg(CI))
    value = roots[(sign * turns) % 4]
    return value, cscale(cmul(value, CI), sign * slope)


def bsym(momentums):
    total = (CZ, CZ)
    for axis in range(4):
        for sign in (-1, 1):
            product = (CO, CZ)
            for momentum in momentums:
                product = pmul(product, psub(phase(momentum[axis], sign), (CO, CZ)))
            total = padd(total, product)
    return total


def independent_fixture():
    p = ((0, 1), (0, 0), (0, 0), (0, 0))
    q = ((1, 0), (0, 0), (0, 0), (0, 0))
    r = ((0, 0), (1, 0), (0, 0), (0, 0))
    s = ((-1, -1), (-1, 0), (0, 0), (0, 0))
    momentums = (p, q, r, s)
    total = (CZ, CZ)
    for i in range(4):
        total = padd(
            total,
            pmul(
                bsym((momentums[i],)),
                bsym(tuple(momentums[j] for j in range(4) if j != i)),
            ),
        )
    for i, j, k, ell in ((0, 1, 2, 3), (0, 2, 1, 3), (0, 3, 1, 2)):
        total = padd(
            total,
            pmul(bsym((momentums[i], momentums[j])), bsym((momentums[k], momentums[ell]))),
        )
    return cscale(total[0], Fraction(1, 24)), cscale(total[1], Fraction(1, 24))


def close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=3.0e-14, abs_tol=3.0e-15)


def verify(path: str = CERT_PATH) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
        if list(Draft202012Validator(schema).iter_errors(data)):
            return False
        for source in data["provenance"]["inputs"]:
            if file_hash(source["path"]) != source["sha256"]:
                return False

        source = load(
            "reverse_physics/data/anderson_bateman_herzog_turok_quartic_soft_source_v1.json"
        )
        if source["source_archive_sha256"] != "e3f1a65d9dbc2d98cb428e57ac4f54ae8443421fdf1491423c8a3316b904595a":
            return False
        if source["equations_transcribed"]["quartic_vertex"] != "V4(p1,p2,p3,p4)=(p1 dot p2)*(p3 dot p4)+(p1 dot p3)*(p2 dot p4)+(p1 dot p4)*(p2 dot p3)":
            return False
        if "scales linearly" not in source["source_statements"][1]:
            return False

        fixture = data["exact_soft_fixture"]
        value, derivative = independent_fixture()
        if value != (Fraction(0), Fraction(0)):
            return False
        if derivative != (Fraction(-1, 3), Fraction(0)):
            return False
        if decode_gaussian(fixture["kernel_at_epsilon_zero"]) != value:
            return False
        if decode_gaussian(fixture["epsilon_derivative"]) != derivative:
            return False
        if fixture["status"] != "EXACT_NONZERO_LINEAR_SOFT_COEFFICIENT":
            return False

        expansion = data["exact_lattice_expansion"]
        if expansion["coefficients"] != "S_0=(1/2)*sum a^2, S_1=(1/2)*sum a*b, S_2=sum(a*c/6+b^2/8)":
            return False
        if expansion["status"] != "PROVED_BY_EXACT_TAYLOR_COEFFICIENT_EXTRACTION":
            return False
        kernel = data["fourier_kernel"]
        if "(1/24)" not in kernel["symmetric_kernel"] or kernel["status"] != "PROVED":
            return False

        lower = data["wiener_chaos_lower_bound"]
        required_lower = {
            "variance_bound": "E_0[Q_L^2]>=c_4*N*|p|^2>=c_5*N*omega_p",
            "normalized_bound": "E_0[Q_L^2]/(N*omega_p^2)>=c_6/omega_p",
            "volume_growth": "Since omega_p=4*sin(pi/L)^2<=4*pi^2/L^2, the normalized isolated square is at least c_7*L^2.",
            "status": "PROVED_POWER_NONUNIFORMITY_OF_ISOLATED_QUARTIC_SCORE_SQUARE",
        }
        if any(lower.get(key) != value for key, value in required_lower.items()):
            return False

        preflight = data["numerical_preflight"]
        observations = load(preflight["data"])
        if file_hash(preflight["data"]) != preflight["data_sha256"]:
            return False
        if file_hash(preflight["source"]) != preflight["source_sha256"]:
            return False
        if preflight["rows"] != observations["rows"]:
            return False
        rows = preflight["rows"]
        if [row["length"] for row in rows] != [4, 8, 16, 32]:
            return False
        for row in rows:
            length = row["length"]
            volume = length**4
            omega = 4.0 * math.sin(math.pi / length) ** 2
            normalized = row["variance"] / (volume * omega * omega)
            if row["volume"] != volume:
                return False
            if not close(row["variance_over_N_omega_squared"], normalized):
                return False
            if not close(row["variance_over_N_omega_squared_L_squared"], normalized / length**2):
                return False

        disposition = data["method_disposition"]
        required = {
            "exact_quartic_score_kernel": "PROVED",
            "quartic_external_soft_degree": "LINEAR_NONZERO",
            "isolated_quartic_score_square_uniform_in_L": "OBSTRUCTED",
            "fixed_order_positive_termwise_score_bound": "OBSTRUCTED_AS_FORMULATED",
            "cubic_rg_matching_suffices_for_whole_score": "OBSTRUCTED_AS_AN_INFERENCE",
            "complete_order_g_four_score_coefficient": "OPEN",
            "power_cancellation_in_renormalized_zero_fiber_composite": "OPEN",
            "nonperturbative_annealed_zero_fiber_score_bound": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        }
        if any(disposition.get(name) != value for name, value in required.items()):
            return False
        if data["cancellation_boundary"]["status"] != "WHOLE_ORDER_CANCELLATION_REQUIRED_NOT_PROVED":
            return False
        if not all(data["checks"].values()):
            return False
        return True
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else CERT_PATH
    raise SystemExit(0 if verify(target) else 1)
