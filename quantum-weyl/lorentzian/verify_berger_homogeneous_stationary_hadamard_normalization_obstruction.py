#!/usr/bin/env python3
"""Independent replay of the homogeneous stationary obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import sympy as sp

try:
    from local_bv.schema_validation import validate_instance
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from local_bv.schema_validation import validate_instance


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = (
    HERE
    / "certificates/"
    "BERGER_HOMOGENEOUS_STATIONARY_HADAMARD_NORMALIZATION_OBSTRUCTION.json"
)
SCHEMA = (
    HERE
    / "schema/"
    "berger-homogeneous-stationary-hadamard-normalization-obstruction-v1.schema.json"
)
A104 = HERE / "generated/berger_a104_endpoint_completion/global_A104.json"
SOURCES = (
    "berger_homogeneous_stationary_hadamard_normalization_obstruction.py",
    "berger_homogeneous_stationary_hadamard_normalization_obstruction_certificate.py",
    "verify_berger_homogeneous_stationary_hadamard_normalization_obstruction.py",
    "schema/berger-homogeneous-stationary-hadamard-normalization-obstruction-v1.schema.json",
    "tests/test_berger_homogeneous_stationary_hadamard_normalization_obstruction.py",
    "../reports/berger-homogeneous-stationary-hadamard-normalization-obstruction.md",
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def _homogeneous_matrix() -> sp.Matrix:
    record = _load(A104)
    body = {key: value for key, value in record.items() if key != "sha256"}
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if digest != record["sha256"]:
        raise ValueError("independent A104 internal hash failed")
    alpha, u, v = sp.symbols("alpha_B u v")
    matrix = sp.zeros(104)
    for row, column, terms in record["entries"]:
        for exponents, coefficient in terms:
            if sum(exponents[1:]) == 0:
                matrix[row, column] += sp.sympify(
                    coefficient,
                    locals={"alpha_B": alpha, "u": u, "v": v},
                ).subs({alpha: 1, u: 1, v: 5})
    return matrix


def verify() -> dict:
    value = _load(OUTPUT)
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"homogeneous obstruction schema failed: {errors}")

    matrix = _homogeneous_matrix()
    metric_indices = tuple(range(6, 26)) + tuple(range(58, 78))
    antifield_indices = tuple(range(26, 46)) + tuple(range(78, 98))
    lam, x = sp.symbols("lambda x")
    metric_cp = sp.factor(
        matrix.extract(metric_indices, metric_indices).charpoly(lam).as_expr()
    )
    antifield_cp = sp.factor(
        matrix.extract(antifield_indices, antifield_indices)
        .charpoly(lam)
        .as_expr()
    )
    p = (
        9 * x**6
        + 39 * x**5
        - 116 * x**4
        + 900 * x**3
        - 3160 * x**2
        - 300 * x
        + 4800
    )
    quotient, remainder = sp.div(
        sp.Poly(metric_cp, lam), sp.Poly(p.subs(x, lam**2), lam)
    )
    if (
        metric_cp != antifield_cp
        or remainder.as_expr() != 0
        or quotient.as_expr() == 0
        or sp.gcd(sp.Poly(p, x), sp.Poly(sp.diff(p, x), x)).degree() != 0
        or sp.gcd(
            quotient,
            sp.Poly(p.subs(x, lam**2), lam),
        ).degree()
        != 0
        or not (p.subs(x, sp.Rational(3, 2)) > 0 > p.subs(x, 2))
        or not (p.subs(x, sp.Rational(5, 2)) < 0 < p.subs(x, 3))
    ):
        raise ValueError("independent exact spectral replay failed")

    flags = value["claim_flags"]
    if (
        not flags["HOMOGENEOUS_REAL_GROWTH_EIGENLINES_CERTIFIED"]
        or flags["STATIONARY_FULL_CARRIER_COMPLEX_STRUCTURE_EXISTS"]
        or flags["NONSTATIONARY_HADAMARD_REPRESENTATIVE_RULED_OUT"]
        or flags["KREIN_COVARIANCE_WITHOUT_COMPLEX_STRUCTURE_RULED_OUT"]
        or flags["PHYSICAL_BRST_QUOTIENT_INSTABILITY_CERTIFIED"]
        or flags["RETAINED_BRST_HADAMARD_CERTIFIED"]
        or flags["LORENTZIAN_QME_CERTIFIED"]
    ):
        raise ValueError("independent claim-boundary replay failed")

    for name, ref in value["dependency_refs"].items():
        path = ROOT / ref["path"]
        source = _load(path)
        if (
            hashlib.sha256(path.read_bytes()).hexdigest() != ref["sha256"]
            or ref["result_id"]
            != source.get("result_id", "A104_EXACT_SPARSE_PAYLOAD")
        ):
            raise ValueError(f"dependency drift: {name}")
    manifest = {
        path: hashlib.sha256((HERE / path).read_bytes()).hexdigest()
        for path in SOURCES
    }
    if value["provenance"]["source_manifest"] != manifest:
        raise ValueError("source manifest drifted")
    return value


if __name__ == "__main__":
    verify()
    print("BERGER homogeneous stationary independent replay: PASS")
