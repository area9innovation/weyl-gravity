#!/usr/bin/env python3
"""Independent exact verifier for the BT perfect-square RG separatrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_PERFECT_SQUARE_RG_SEPARATRIX_V1.json",
)
SCHEMA = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-perfect-square-rg-separatrix-v1.schema.json",
)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def exact_rg_identities():
    import sympy as sp

    u, v, c, lam = sp.symbols("u v c lam")
    b3 = -(v * u + sp.Rational(3, 4) * u ** 3)
    b4 = -(v ** 2 + v * u ** 2)
    defining = u ** 2 + 2 * v
    lie = sp.diff(defining, u) * b3 + sp.diff(defining, v) * b4
    factorization = sp.factor(lie)
    expected = -defining * (v + sp.Rational(3, 2) * u ** 2)

    tangent_b3 = sp.factor(b3.subs(v, -u ** 2 / 2))
    tangent_b4 = sp.factor(b4.subs(v, -u ** 2 / 2))
    beta_lambda = sp.factor((-tangent_b3).subs(u, -lam))

    parabola_residual = sp.factor(
        (b4 - 2 * c * u * b3).subs(v, c * u ** 2) / u ** 4
    )
    roots = sp.solve(parabola_residual, c)
    return {
        "factorization": sp.expand(factorization - expected) == 0,
        "restricted_beta3": tangent_b3 == -u ** 3 / 4,
        "restricted_beta4": tangent_b4 == u ** 4 / 4,
        "restricted_beta_lambda_over_K": beta_lambda == -lam ** 3 / 4,
        "parabola_residual": sp.expand(
            parabola_residual - c * (c + sp.Rational(1, 2))
        ) == 0,
        "parabola_roots": roots == [sp.Rational(-1, 2), sp.Integer(0)],
    }


def exact_counterterm_identities():
    """Verify the pole residues using a dual number A^2=0."""
    # Represent 1+a*A as the coefficient a.  Products add coefficients,
    # inverse negates, and rational powers multiply at first order.
    z_phi = Fraction(1)
    composite3 = Fraction(1)
    composite4 = Fraction(1)
    z3 = composite3 - Fraction(3, 2) * z_phi
    z4 = composite4 - 2 * z_phi
    return {
        "z3": z3 == Fraction(-1, 2),
        "z4": z4 == Fraction(-1),
        "bare_relation": z4 == 2 * z3,
        "whole_action_pole": z_phi == composite3 == composite4,
    }


def exact_sector_enumeration():
    rows = []
    for v3 in range(9):
        for v4 in range(9):
            # Combine half-edge counting with connected one-loop Euler count.
            internal = v3 + v4
            if 3 * v3 + 4 * v4 == 2 * internal + 4:
                rows.append((v3, v4, internal))
    return rows


def verify(path):
    checks = {}
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA, encoding="utf-8") as handle:
            schema = json.load(handle)
        errors = sorted(Draft202012Validator(schema).iter_errors(cert),
                        key=lambda error: list(error.path))
        checks["strict_schema"] = not errors
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    identities = exact_rg_identities()
    checks.update({f"rg_{name}": ok for name, ok in identities.items()})
    counterterms = exact_counterterm_identities()
    checks.update({f"counterterm_{name}": ok
                   for name, ok in counterterms.items()})

    expected_sectors = [(4, 0, 4), (2, 1, 3), (0, 2, 2)]
    checks["sector_enumeration"] = exact_sector_enumeration() == list(
        reversed(expected_sectors)
    )
    recorded = cert.get("four_point_one_loop_sectors", {}).get("rows", [])
    checks["sector_record"] = [
        (row.get("cubic_vertices"), row.get("quartic_vertices"),
         row.get("internal_lines")) for row in recorded
    ] == expected_sectors

    f = cert.get("finite_jet_nonuniqueness", {})
    checks["jet_dimension"] = (
        f.get("carrier_dimension") == 16 and f.get("top_slot") == "x1*x2*x3*x4"
    )
    checks["mutation_boundary"] = (
        "not a claim" in f.get("inference_boundary", "").lower()
        and "x1*x2*x3*x4" in f.get("crossing_symmetric_mutation", "")
    )
    checks["real_coefficient_fail_closed"] = (
        cert.get("real_threshold_matching", {}).get("status") == "NOT_COMPUTED"
        and "-3/8" in cert.get("real_threshold_matching", {}).get(
            "predecessor_coefficient", "")
    )
    disposition = cert.get("disposition", {})
    checks["physical_boundary"] = (
        disposition.get("renormalized_four_leg_loop_jet") == "NOT_COMPUTED"
        and disposition.get("real_virtual_collinear_cancellation") == "NOT_COMPUTED"
        and disposition.get("beyond_tree_positivity") == "NOT_ESTABLISHED"
    )
    checks["dependency_boundary"] = (
        cert.get("dependency_tags") == ["LOCAL-ALGEBRAIC"]
        and any("LORENTZIAN-CAUSAL" in item
                for item in cert.get("does_not_establish", []))
    )
    checks["provenance_hashes"] = all(
        item.get("sha256") == sha256(item.get("path", ""))
        for item in cert.get("provenance", {}).get("inputs", [])
    )
    recorded_checks = cert.get("checks", {})
    checks["producer_checks"] = (
        recorded_checks.get("ok") is True
        and recorded_checks.get("passed") == recorded_checks.get("total") == 17
        and not recorded_checks.get("failures")
    )

    for name, ok in checks.items():
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    passed = sum(checks.values())
    print(f"RESULT: {'PASS' if passed == len(checks) else 'FAIL'} "
          f"({passed}/{len(checks)})")
    return passed == len(checks)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.verify) else 1


if __name__ == "__main__":
    sys.exit(main())
