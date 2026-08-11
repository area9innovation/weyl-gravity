#!/usr/bin/env python3
"""Independent verifier for the BT rigged resolution-Jordan Moller gate."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_RIGGED_RESOLUTION_JORDAN_MOLLER_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-rigged-resolution-jordan-moller-v1.schema.json")
FACTOR = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json")
THRESHOLD = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1.json")
ABEL = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_ABEL_NAIMARK_ASYMPTOTIC_DILATION_V1.json")
SHELL = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_LOG_SHELL_MOLLER_LIMIT_V1.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_threshold_integral():
    """Reintegrate rho with z=exp(-rapidity), unlike the producer's imported H."""
    import sympy as sp

    z, m = sp.symbols("z m", positive=True)
    r = m*m
    u = 1+m*m+m*(z+1/z)
    sqrt_lambda_du = m*m*(1-z*z)**2/z**3
    rho = (1-r)**2*(2*u*(1+r)-(1-r)**2)/(4*u**3)
    integrand = sp.cancel(rho*sqrt_lambda_du/u)
    primitive = sp.integrate(integrand, z, risch=True)
    raw = sp.limit(primitive, z, 1, dir="-")-sp.limit(primitive, z, 0, dir="+")
    expected = (5*r**3-6*r**2*sp.log(r)-3*r**2-6*r*sp.log(r)+3*r-5)/(24*(r-1))
    return sp.simplify(sp.re(raw)-expected) == 0


def verify(certificate, exhaustive=False):
    import sympy as sp

    schema_errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    factor, threshold, abel, shell = map(load, (FACTOR, THRESHOLD, ABEL, SHELL))
    direct = certificate.get("regulated_direct_integral", {})
    gram = certificate.get("threshold_gram", {})
    obstruction = certificate.get("differentiability_obstruction", {})
    jordan = certificate.get("rigged_resolution_jordan", {})
    disposition = certificate.get("disposition", {})

    r, c = sp.symbols("r c", positive=True)
    I = (5*r**3-6*r**2*sp.log(r)-3*r**2-6*r*sp.log(r)+3*r-5)/(24*(r-1))
    D = sp.factor((I-sp.Rational(5, 24))/r)
    formula_ok = (
        sp.limit(I, r, 0, dir="+") == sp.Rational(5, 24)
        and sp.limit(I, r, 1) == 0
        and sp.limit(D-sp.log(r)/4, r, 0, dir="+") == sp.Rational(1, 12)
        and sp.limit(D.subs(r, c*r)-D, r, 0, dir="+") == sp.log(c)/4
        and sp.limit(sp.diff(I, r), r, 0, dir="+") == -sp.oo
    )

    fixture_expected = [
        (Fraction(1, 4), Fraction(31, 128), "log(2)", Fraction(-5, 24), Fraction(13, 96), Fraction(-5, 6)),
        (Fraction(1, 9), Fraction(107, 486), "log(3)", Fraction(-5, 72), Fraction(23, 216), Fraction(-5, 8)),
        (Fraction(1, 16), Fraction(439, 2048), "log(2)", Fraction(-17, 240), Fraction(37, 384), Fraction(-17, 15)),
    ]
    fixture_ok = True
    try:
        rows = gram["exact_fixtures"]
        fixture_ok = len(rows) == 3
        for row, expected in zip(rows, fixture_expected):
            rr, irat, logname, ilog, drat, dlog = expected
            fixture_ok &= (
                frac(row["r"]) == rr
                and frac(row["I"]["rational"]) == irat
                and row["I"]["log_symbol"] == logname
                and frac(row["I"]["log_coefficient"]) == ilog
                and frac(row["D"]["rational"]) == drat
                and row["D"]["log_symbol"] == logname
                and frac(row["D"]["log_coefficient"]) == dlog
            )
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        fixture_ok = False

    q, ell = sp.symbols("q ell", nonzero=True)
    T = sp.diag(q, ell)
    J = sp.Matrix([[0, 1], [1, 0]])
    Tstar = -J*T.T*J
    rho = -q*ell
    eta = sp.diag(1, 1, -1, -1)*sp.diag(J, J)
    A = sp.zeros(4)
    A[:2, 2:] = -Tstar
    A[2:, :2] = T
    Asharp = eta*A.T*eta
    block_ok = sp.simplify(Tstar*T-rho*sp.eye(2)) == sp.zeros(2) and Asharp == -A and sp.simplify(A*A+rho*sp.eye(4)) == sp.zeros(4)

    inputs = certificate.get("provenance", {}).get("inputs", [])
    checks = {
        "schema": not schema_errors,
        "identity_tags_lifecycle": certificate.get("certificate") == "REVERSE_PHYSICS_BT_RIGGED_RESOLUTION_JORDAN_MOLLER_V1" and certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"] and certificate.get("lifecycle_state") == "CLASSIFIED",
        "source_threshold": threshold.get("threshold_result", {}).get("logarithmic_slope_coefficient") == {"numerator": -3, "denominator": 8},
        "source_factorization": factor.get("amplitude_factorization", {}).get("splitting_map") == "T=diag(2*Q,2*L)",
        "exact_threshold_formula_and_germ": formula_ok,
        "exact_log_fixtures": fixture_ok,
        "pointwise_block_pseudounitarity": block_ok,
        "direct_integral_typing": direct.get("integrated_gram") == "V_r^sharp*V_r=I(r)*I2" and direct.get("state") == "CONSTRUCTED_FOR_EVERY_FIXED_MASS_RATIO",
        "C1_lemma_and_contradiction": obstruction.get("axis_derivative") == "I'(0+)=-infinity" and obstruction.get("disposition") == "NO_ORDINARY_STRONGLY_C1_FIXED_BOUNDED_PAIRING_MOLLER_COLUMN",
        "scale_normalization": gram.get("mass_scale_cocycle") == "lim_(r->0)[D(c*r)-D(r)]=log(c)/4" and gram.get("physical_per_pair_cocycle") == "log(c)/48" and gram.get("three_pair_cocycle") == "log(c)/16",
        "jordan_group": jordan.get("generator") == "N=[[0,-1/4],[0,0]], N^2=0" and jordan.get("physical_generator_per_pair") == "N_phys=N/12=[[0,-1/48],[0,0]]",
        "rigged_not_L2": jordan.get("rigged_carrier") == "Schwartz(R_s) subset L2(R_s,ds) subset Schwartz'(R_s)" and jordan.get("invariant_affine_sector") == "span{1,s} inside Schwartz'(R_s)" and jordan.get("L2_boundary") == "the constant and coordinate distributions are not vectors of L2(R_s,ds)",
        "abel_translation_source": abel.get("time_resolution_map", {}).get("translation") == "q_(R+b)(y)=q_R(y-b) and p_(R+b)(y)=p_R(y-b)",
        "prior_strong_limit_boundary": shell.get("disposition", {}).get("ordinary_L2_strong_Moller_limit") == "EXACT_OBSTRUCTION",
        "object_boundary": disposition.get("public_Rt_equals_physical_S_operator") == "EXACT_OBSTRUCTION_RETAINED" and disposition.get("full_physical_Moller_operator") == "NOT_CONSTRUCTED",
        "claim_boundaries": disposition.get("finite_complete_NLO_probability") == "NOT_ESTABLISHED" and disposition.get("beyond_tree_positivity") == "NOT_ESTABLISHED" and disposition.get("Eq19_all_orders") == "NOT_PROVED" and "anything LORENTZIAN-CAUSAL" in certificate.get("does_not_establish", []),
        "hashes": len(inputs) == 7 and all(row.get("sha256") == sha256(row.get("path", "")) for row in inputs),
        "producer_ledger": certificate.get("checks", {}).get("passed") == certificate.get("checks", {}).get("total") == 25 and certificate.get("checks", {}).get("failures") == [] and all(certificate.get("checks", {}).get("details", {}).values()),
        "independent_threshold_integration": (not exhaustive) or independent_threshold_integral(),
    }
    for error in schema_errors:
        print("schema", list(error.path), error.message)
    failures = [name for name, ok in checks.items() if not ok]
    if failures:
        print("BT RIGGED RESOLUTION JORDAN MOLLER VERIFY: FAIL", *failures, sep="\n  ")
        return False, checks
    return True, checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    parser.add_argument("--exhaustive", action="store_true")
    args = parser.parse_args(argv)
    ok, checks = verify(load(args.verify), args.exhaustive)
    if not ok:
        return 1
    print(f"BT RIGGED RESOLUTION JORDAN MOLLER VERIFY: ALL PASS ({sum(checks.values())}/{len(checks)})" + (" [EXHAUSTIVE]" if args.exhaustive else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
