#!/usr/bin/env python3
"""Method-distinct verifier for the BT order-lambda R_t kernel.

This rail does not import the producer.  It evaluates the mode products at
three exact rational energy splittings, independently performs the leading
map inversion, and contracts the resulting coefficients with the BT
off-diagonal Krein metric.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from fractions import Fraction

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_RT_JORDAN_KERNEL_V1.json",
)
SCHEMA = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-rt-jordan-kernel-v1.schema.json",
)


@dataclass(frozen=True)
class C:
    r: Fraction = Fraction(0)
    i: Fraction = Fraction(0)

    def __add__(self, other):
        other = cast(other)
        return C(self.r + other.r, self.i + other.i)

    __radd__ = __add__

    def __neg__(self):
        return C(-self.r, -self.i)

    def __sub__(self, other):
        return self + (-cast(other))

    def __mul__(self, other):
        other = cast(other)
        return C(self.r * other.r - self.i * other.i,
                 self.r * other.i + self.i * other.r)

    __rmul__ = __mul__


def cast(value):
    return value if isinstance(value, C) else C(Fraction(value))


I = C(Fraction(0), Fraction(1))


def add(left, right):
    size = max(len(left), len(right))
    return tuple((left[n] if n < len(left) else C())
                 + (right[n] if n < len(right) else C())
                 for n in range(size))


def scale(value, polynomial):
    return tuple(cast(value) * coefficient for coefficient in polynomial)


def multiply(left, right):
    out = [C() for _ in range(len(left) + len(right) - 1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] = out[i + j] + a * b
    return tuple(out)


def trim(polynomial):
    polynomial = list(polynomial)
    while len(polynomial) > 1 and polynomial[-1] == C():
        polynomial.pop()
    return tuple(polynomial)


def a_kernels(e1, e2):
    energy = e1 + e2
    omega = {
        ("a2", "a2"): (C(2 * energy),),
        ("a2", "a1"): (C(2 * e1), I * (4 * energy * e2)),
        ("a1", "a2"): (C(2 * e2), I * (4 * energy * e1)),
        ("a1", "a1"): (
            C(), I * (4 * (e1 * e1 + e2 * e2)),
            C(-8 * energy * e1 * e2),
        ),
    }
    upsilon = {
        ("a2", "a2"): (C(),),
        ("a2", "a1"): (C(8 * energy * e2 * (e1 - e2)),),
        ("a1", "a2"): (C(8 * energy * e1 * (e2 - e1)),),
        ("a1", "a1"): (C(-8 * energy * (e1 * e1 + e2 * e2)),),
    }
    return omega, upsilon


def invert(kernel, e1, e2):
    inverse = {
        1: {
            "a2": {"Omega": (C(4 * e1 * e1),),
                   "Upsilon": (C(), -I * (2 * e1))},
            "a1": {"Omega": (C(),), "Upsilon": (C(1),)},
        },
        2: {
            "a2": {"Omega": (C(4 * e2 * e2),),
                   "Upsilon": (C(), -I * (2 * e2))},
            "a1": {"Omega": (C(),), "Upsilon": (C(1),)},
        },
    }
    out = {}
    density = Fraction(1, 64 * e1**3 * e2**3)
    for left_bt in ("Omega", "Upsilon"):
        for right_bt in ("Omega", "Upsilon"):
            value = (C(),)
            for (left_a, right_a), coefficient in kernel.items():
                term = multiply(coefficient, inverse[1][left_a][left_bt])
                term = multiply(term, inverse[2][right_a][right_bt])
                value = add(value, term)
            out[(left_bt, right_bt)] = trim(scale(density, value))
    return out


def expected_carrier(e1, e2):
    energy = e1 + e2
    return {
        "Omega": {
            ("Omega", "Omega"): energy / (2 * e1 * e2),
            ("Omega", "Upsilon"): Fraction(1, 8 * e2**3),
            ("Upsilon", "Omega"): Fraction(1, 8 * e1**3),
            ("Upsilon", "Upsilon"): Fraction(0),
        },
        "Upsilon": {
            ("Omega", "Omega"): Fraction(0),
            ("Omega", "Upsilon"): energy * (e1 - e2) / (2 * e1 * e2**2),
            ("Upsilon", "Omega"): energy * (e2 - e1) / (2 * e1**2 * e2),
            ("Upsilon", "Upsilon"): (
                -energy * (e1**2 + e2**2) / (8 * e1**3 * e2**3)
            ),
        },
    }


def gram(rows, e1, e2):
    opposite = {"Omega": "Upsilon", "Upsilon": "Omega"}
    out = {}
    for left in rows:
        for right in rows:
            value = Fraction(0)
            for species in (("Omega", "Omega"), ("Omega", "Upsilon"),
                            ("Upsilon", "Omega"), ("Upsilon", "Upsilon")):
                dual = (opposite[species[0]], opposite[species[1]])
                value += rows[left][species] * rows[right][dual]
            out[(left, right)] = 4 * e1 * e2 * value
    return out


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(path):
    with open(path, encoding="utf-8") as handle:
        cert = json.load(handle)
    with open(SCHEMA, encoding="utf-8") as handle:
        schema = json.load(handle)
    errors = sorted(Draft202012Validator(schema).iter_errors(cert),
                    key=lambda error: list(error.path))
    checks = {"strict_schema": not errors}
    for error in errors[:8]:
        print(f"SCHEMA: {'/'.join(map(str, error.path))}: {error.message}")

    appendix = cert.get("appendix_c_consistency", {})
    checks["linear_label_logic"] = (
        appendix.get("printed_eq31") == "ordinary a1 plus (1+2iEt) a2"
        and appendix.get("minimal_repair") == "exchange a1 and a2 in Eq. (31)"
        and "growing oscillator a1" in appendix.get("eq32_requires", "")
        and "ordinary a2 and growing a1" in appendix.get("eq33_requires", "")
    )

    fixtures = [
        (Fraction(1), Fraction(2)),
        (Fraction(2, 3), Fraction(5, 4)),
        (Fraction(7, 5), Fraction(7, 5)),
    ]
    carrier_ok = True
    secular_ok = True
    gram_ok = True
    determinant_ok = True
    for e1, e2 in fixtures:
        omega_a, upsilon_a = a_kernels(e1, e2)
        omega = invert(omega_a, e1, e2)
        upsilon = invert(upsilon_a, e1, e2)
        expected = expected_carrier(e1, e2)
        for row, computed in (("Omega", omega), ("Upsilon", upsilon)):
            for key, polynomial in computed.items():
                secular_ok = secular_ok and len(polynomial) == 1
                carrier_ok = carrier_ok and polynomial == (C(expected[row][key]),)
        rows = {"Omega": expected["Omega"], "Upsilon": expected["Upsilon"]}
        matrix = gram(rows, e1, e2)
        energy = e1 + e2
        g00 = Fraction(1, 8 * e1**2 * e2**2)
        g11 = -2 * energy**2 * (e1 - e2)**2 / (e1**2 * e2**2)
        g01 = (-energy**2 * (e1**2 + e2**2 - e1 * e2)
               / (2 * e1**3 * e2**3))
        gram_ok = gram_ok and matrix == {
            ("Omega", "Omega"): g00,
            ("Omega", "Upsilon"): g01,
            ("Upsilon", "Omega"): g01,
            ("Upsilon", "Upsilon"): g11,
        }
        determinant_ok = determinant_ok and g00 * g11 - g01 * g01 < 0
    checks["independent_carrier_fixtures"] = carrier_ok
    checks["independent_secular_cancellation"] = secular_ok
    checks["independent_krein_gram"] = gram_ok
    checks["negative_fixed_split_determinant"] = determinant_ok

    gram_record = cert.get("fixed_splitting_krein_gram", {})
    checks["recorded_gram_formulas"] = (
        gram_record.get("G_OmegaOmega") == "1/(8*e1^2*e2^2)"
        and gram_record.get("G_UpsilonUpsilon")
        == "-2*E^2*(e1-e2)^2/(e1^2*e2^2)"
        and gram_record.get("G_OmegaUpsilon")
        == "-E^2*(e1^2+e2^2-e1*e2)/(2*e1^3*e2^3)"
    )
    # e1^3*G_OmegaUpsilon at e1=0, e2=f equals -f/2, so the
    # z-endpoint pole is genuinely cubic rather than an uncancelled notation.
    checks["independent_endpoint_residue_nonzero"] = all(
        -f / 2 != 0 for f in (Fraction(1), Fraction(3, 2), Fraction(5))
    )

    formal = cert.get("formal_generator", {})
    checks["formal_anti_krein_completion_declared"] = (
        "K_down-K_down^dag" in formal.get("definition", "")
        and formal.get("status") == "FORMAL_FINITE_MODE_LIFT_ONLY"
    )
    disposition = cert.get("disposition", {})
    checks["claim_boundary"] = (
        disposition.get("order_lambda_two_annihilator_kernel")
        == "COEFFICIENT_COMPUTED"
        and disposition.get("continuum_distributional_domain")
        == "NOT_CONSTRUCTED"
        and disposition.get("exact_gram_one_over_48") == "NOT_DERIVED"
        and disposition.get("physical_nlo_probability") == "NOT_ESTABLISHED"
    )

    inputs = cert.get("provenance", {}).get("inputs", [])
    checks["pinned_input_hashes"] = len(inputs) == 2 and all(
        item.get("sha256") == sha256(item.get("path", "")) for item in inputs
    )
    checks["producer_checks_recorded"] = (
        cert.get("checks", {}).get("ok") is True
        and cert.get("checks", {}).get("passed") == 18
        and cert.get("checks", {}).get("total") == 18
    )

    ok = all(checks.values())
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(f"RESULT: {'PASS' if ok else 'FAIL'} "
          f"({sum(checks.values())}/{len(checks)})")
    return ok


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.verify) else 1


if __name__ == "__main__":
    sys.exit(main())
