#!/usr/bin/env python3
"""Memory-bounded exact finite-field preflight for three BT rotation angles.

This is deliberately not a characteristic-zero theorem.  It checks the full
three-variable rational-function identities over one declared prime field,
using isolated external-mass-mask workers so that no process needs the full
42-slot degree-at-most-three jet.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))

from bt_six_point_generic_external_mass_kernel import generic_external_mass_kernel
from bt_sparse_rational import SparseRationalField


PRIME = 1_000_003
PAIRS = [
    (7, 56),
    (11, 52),
    (13, 50),
    (14, 49),
    (19, 44),
    (21, 42),
    (22, 41),
    (25, 38),
    (26, 37),
    (28, 35),
]
WORKER_MASKS = [mask for pair in PAIRS for mask in pair]


def polynomial_hash(polynomial):
    digest = hashlib.sha256()
    for exponents, coefficient in sorted(polynomial.to_dict().items()):
        digest.update((",".join(map(str, exponents)) + ":").encode())
        digest.update(str(int(coefficient)).encode())
        digest.update(b";")
    return digest.hexdigest()


def normalized_rational_hash(value):
    leading = value.denominator.leading_coefficient()
    numerator = value.numerator / leading
    denominator = value.denominator / leading
    digest = hashlib.sha256()
    digest.update(polynomial_hash(numerator).encode())
    digest.update(b"/")
    digest.update(polynomial_hash(denominator).encode())
    return digest.hexdigest()


def exact_family(active_mass_mask):
    field = SparseRationalField(["t", "u", "v"], modulus=PRIME)
    t, u, v = field.gens

    def cosine_sine(parameter):
        return (
            (1 - parameter * parameter) / (1 + parameter * parameter),
            2 * parameter / (1 + parameter * parameter),
        )

    cosine_t, sine_t = cosine_sine(t)
    cosine_u, sine_u = cosine_sine(u)
    cosine_v, sine_v = cosine_sine(v)

    def vector(*entries):
        return tuple(field.coerce(entry) for entry in entries)

    incoming = [
        vector(Fraction(6, 5), Fraction(6, 5), 0, 0),
        vector(1, Fraction(-3, 5), Fraction(4, 5), 0),
        vector(1, Fraction(-3, 5), Fraction(-4, 5), 0),
    ]

    def rotate(momentum):
        x_value = cosine_t * momentum[1] - sine_t * momentum[2]
        y_value = sine_t * momentum[1] + cosine_t * momentum[2]
        z_value = momentum[3]
        y_value, z_value = (
            cosine_u * y_value - sine_u * z_value,
            sine_u * y_value + cosine_u * z_value,
        )
        x_value, y_value = (
            cosine_v * x_value - sine_v * y_value,
            sine_v * x_value + cosine_v * y_value,
        )
        return momentum[0], x_value, y_value, z_value

    momenta = incoming + [
        tuple(-entry for entry in rotate(momentum)) for momentum in incoming
    ]

    def add(*vectors):
        return tuple(
            sum((value[index] for value in vectors), field.zero)
            for index in range(4)
        )

    def square(momentum):
        return momentum[0] ** 2 - sum(
            (entry * entry for entry in momentum[1:]), field.zero
        )

    adjacent = [
        square(add(momenta[index], momenta[(index + 1) % 6]))
        for index in range(6)
    ]
    triples = [
        square(
            add(
                momenta[index],
                momenta[(index + 1) % 6],
                momenta[(index + 2) % 6],
            )
        )
        for index in range(3)
    ]
    result = generic_external_mass_kernel(
        adjacent,
        triples,
        scalar_coerce=field.coerce,
        max_degree=3,
        active_mass_mask=active_mass_mask,
    )
    coefficients = result["degree_three"]
    return {
        str(mask): {
            "hash": normalized_rational_hash(coefficients[mask]),
            "numerator_total_degree": int(
                coefficients[mask].numerator.total_degree()
            ),
            "denominator_total_degree": int(
                coefficients[mask].denominator.total_degree()
            ),
            "numerator_variable_degrees": list(
                map(int, coefficients[mask].numerator.degrees())
            ),
            "denominator_variable_degrees": list(
                map(int, coefficients[mask].denominator.degrees())
            ),
            "numerator_terms": len(coefficients[mask].numerator),
            "denominator_terms": len(coefficients[mask].denominator),
        }
        for mask in [active_mass_mask]
    }


def run_workers():
    rows = {}
    for active_mask in WORKER_MASKS:
        print(f"worker {active_mask} start", flush=True)
        command = [
            sys.executable,
            os.path.abspath(__file__),
            "--worker",
            str(active_mask),
        ]
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        rows.update(payload)
        print(
            f"worker {active_mask} complete: {','.join(sorted(payload))}",
            flush=True,
        )
        complement = 63 ^ active_mask
        if str(complement) in rows:
            print(
                f"pair {min(active_mask, complement)}/"
                f"{max(active_mask, complement)} equal: "
                f"{rows[str(active_mask)]['hash'] == rows[str(complement)]['hash']}",
                flush=True,
            )
    comparisons = []
    for mask in sorted(map(int, rows)):
        complement = 63 ^ mask
        if mask >= complement:
            continue
        comparisons.append(
            {
                "mask": mask,
                "complement_mask": complement,
                "equal": rows[str(mask)]["hash"]
                == rows[str(complement)]["hash"],
                "coefficient": rows[str(mask)],
                "complement": rows[str(complement)],
            }
        )
    return {
        "field": f"GF({PRIME})(t,u,v)",
        "prime": PRIME,
        "rotation": "R_z(v) R_x(u) R_z(t)",
        "worker_active_masks": WORKER_MASKS,
        "coefficient_count": len(rows),
        "comparisons": comparisons,
        "all_ten_equal": len(comparisons) == 10
        and all(row["equal"] for row in comparisons),
        "characteristic_zero_identity": "NOT_ESTABLISHED",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", type=int, choices=WORKER_MASKS)
    args = parser.parse_args(argv)
    if args.worker is not None:
        print(json.dumps(exact_family(args.worker), sort_keys=True))
        return 0
    result = run_workers()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("RESULT:", "PASS" if result["all_ten_equal"] else "FAIL")
    return 0 if result["all_ten_equal"] else 1


if __name__ == "__main__":
    sys.exit(main())
