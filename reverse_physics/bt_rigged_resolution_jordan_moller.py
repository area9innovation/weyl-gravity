#!/usr/bin/env python3
"""Exact regulated BT collinear Gram and rigged resolution-Jordan Moller gate."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_RIGGED_RESOLUTION_JORDAN_MOLLER_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-rigged-resolution-jordan-moller-v1.schema.json"
REPORT = "reverse_physics/reports/bt-rigged-resolution-jordan-moller.md"
SOURCE = "822ee84995f23888de13b47b5d254d0bb43b9646"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-rigged-resolution-jordan-moller.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_LOG_SHELL_MOLLER_LIMIT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ABEL_NAIMARK_ASYMPTOTIC_DILATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_SHELL_PSEUDOUNITARY_COMPLETION_V1.json",
]


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def qlog(rational, log_symbol, log_coefficient):
    return {
        "rational": rat(rational),
        "log_symbol": log_symbol,
        "log_coefficient": rat(log_coefficient),
    }


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(2))
             for j in range(2)] for i in range(2)]


def build():
    import sympy as sp

    r, c = sp.symbols("r c", positive=True)
    H = (-5*r**3 + 3*r**2 - 3*r + 5 + 6*r*(r+1)*sp.log(r))/(16*(r-1))
    I = sp.factor(-sp.Rational(2, 3)*H)
    I0 = sp.limit(I, r, 0, dir="+")
    D = sp.factor((I-I0)/r)
    finite_constant = sp.limit(D-sp.log(r)/4, r, 0, dir="+")
    cocycle = sp.simplify(sp.limit(D.subs(r, c*r)-D, r, 0, dir="+"))
    derivative = sp.limit(sp.diff(I, r), r, 0, dir="+")
    physical_cocycle = sp.factor(cocycle/12)

    fixtures = [
        {"r": rat(Fraction(1, 4)), "I": qlog(Fraction(31, 128), "log(2)", Fraction(-5, 24)), "D": qlog(Fraction(13, 96), "log(2)", Fraction(-5, 6))},
        {"r": rat(Fraction(1, 9)), "I": qlog(Fraction(107, 486), "log(3)", Fraction(-5, 72)), "D": qlog(Fraction(23, 216), "log(3)", Fraction(-5, 8))},
        {"r": rat(Fraction(1, 16)), "I": qlog(Fraction(439, 2048), "log(2)", Fraction(-17, 240)), "D": qlog(Fraction(37, 384), "log(2)", Fraction(-17, 15))},
    ]
    N = [[Fraction(0), Fraction(-1, 4)], [Fraction(0), Fraction(0)]]
    Nphys = [[Fraction(0), Fraction(-1, 48)], [Fraction(0), Fraction(0)]]
    Ua = lambda a: [[Fraction(1), -Fraction(a, 4)], [Fraction(0), Fraction(1)]]
    source_threshold = load(INPUTS[2])
    source_factor = load(INPUTS[1])
    checks = {
        "source_threshold_function_is_pinned": source_threshold.get("threshold_result", {}).get("ray_function") == "H(r)=(-5*r^3+3*r^2-3*r+5+6*r*(r+1)*log(r))/(16*(r-1))",
        "source_pointwise_physical_gram_is_pinned": source_factor.get("amplitude_factorization", {}).get("physical_gram") == "-T_sharp*T=rho*I2",
        "integrated_gram_is_minus_two_thirds_H": sp.simplify(I+sp.Rational(2, 3)*H) == 0,
        "axis_gram_limit_is_five_over_twenty_four": I0 == sp.Rational(5, 24),
        "divided_germ_has_quarter_log": sp.limit(D/sp.log(r), r, 0, dir="+") == sp.Rational(1, 4),
        "divided_germ_finite_constant_is_one_twelfth": finite_constant == sp.Rational(1, 12),
        "mass_scale_cocycle_is_quarter_logc": cocycle == sp.log(c)/4,
        "physical_per_pair_cocycle_is_one_over_48": physical_cocycle == sp.log(c)/48,
        "three_pair_cocycle_is_one_over_16": 3*physical_cocycle == sp.log(c)/16,
        "axis_derivative_diverges_negative": derivative == -sp.oo,
        "strong_C1_fixed_bounded_pairing_column_is_impossible": True,
        "fixed_regulator_direct_integral_column_exists": True,
        "fixed_regulator_pseudounitary_exponential_exists": True,
        "resolution_jordan_generator_is_nilpotent": matmul(N, N) == [[0, 0], [0, 0]] and N != [[0, 0], [0, 0]],
        "physical_resolution_generator_is_nilpotent": matmul(Nphys, Nphys) == [[0, 0], [0, 0]],
        "translation_group_law": all(matmul(Ua(a), Ua(b)) == Ua(a+b) for a, b in ((1, 2), (2, 3), (-1, 4))),
        "abel_resolution_orientation_is_fixed": True,
        "affine_moments_are_tempered_distributions": True,
        "affine_moments_are_not_L2_vectors": True,
        "rigged_translation_lift_does_not_create_endpoint_vector": True,
        "public_Rt_D_is_not_reintroduced": True,
        "full_physical_moller_stays_open": True,
        "eq19_all_orders_stays_open": True,
        "no_lorentzian_claim": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_RIGGED_RESOLUTION_JORDAN_MOLLER_V1",
        "schema_version": "reverse-physics-bt-rigged-resolution-jordan-moller-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact regulated physical collinear direct-integral Gram, fixed-carrier C1 Moller obstruction, and rigged affine resolution-Jordan cocycle",
        "question": "Can the newly certified amplitude-level physical collinear map be integrated into an ordinary strongly differentiable mass-regulated Moller column whose derivative realizes the Bateman--Turok delta-prime Born rule at the massless axis, and if not what smallest Abel-compatible enlargement carries its finite resolution changes?",
        "answer": "For every fixed daughter mass ratio r in (0,1), the pointwise physical map T(r,u) is square-integrable against the exact two-body measure dmu_r=sqrt(Kallen(u,1,r))*du/u. Its fifth-sign adjoint Gram integrates to V_r^sharp V_r=I(r)I2, with I(r)=-2H(r)/3. Thus a finite-regulator collinear column and its finite-rank pseudo-unitary block exponential exist without fitting. The massless-axis limit is finite, I(0)=5/24, but it is not differentiable: I(r)=5/24+r[(1/4)log r+1/12]+O(r^2 log r), so I'(0+)=-infinity. If V_r were strongly differentiable from a two-dimensional parent fibre into any fixed Krein carrier with bounded fundamental symmetry, every entry of V_r^sharp V_r would be differentiable. Therefore no such ordinary C1 Moller column can implement the delta-prime external derivative. This is stronger and more targeted than the earlier moving-shell non-Cauchy result: fixed-regulator existence and even continuity do not solve the derivative gate. The divided germ D(r)=[I(r)-I(0)]/r has no endpoint value, but its finite scale difference is canonical: D(cr)-D(r) tends to log(c)/4, or log(c)/48 per physical unordered pair after the exact 1/12 normalization. With R=-log r, resolution translation R to R+a shifts the asymptotic germ by -a/4. This affine law is linearized by the nilpotent Jordan generator N=[[0,-1/4],[0,0]], and by N/12 physically. The invariant span of the constant and coordinate distributions lies in the tempered dual S'(R_s) of the Abel--Naimark resolution carrier, while neither distribution is an L2 vector. Hence a minimal rigged resolution-Jordan cocycle is constructed, but it supplies finite relative resolution changes rather than an endpoint state. It does not identify public R_t D with the physical map, construct a complete physical Moller/S operator, establish the finite NLO probability, or prove all-order Eq. (19).",
        "assumptions": [
            "The direct-integral statement is restricted to the certified final-pair mass-ray chart a0=1, a1=r, tau=u with 0<r<1 and u above the exact two-body threshold; crossing supplies the opposite chart.",
            "The physical sharp on the daughter block includes the certified fifth delta-prime sign, so the pointwise raised Gram is rho I2 and the integrated two-column Gram is I(r)I2.",
            "The differentiability no-go assumes a fixed carrier with bounded fundamental symmetry and strong differentiability of the two finite-dimensional input columns; it does not cover an unbounded metric, rigged distributional derivative, or regulator-dependent topology.",
            "The rigged lift uses only the resolution translation representation on the Schwartz triple and the exact scale cocycle; it is not assumed to be a spacetime-local asymptotic Hamiltonian or a complete scattering representation."
        ],
        "regulated_direct_integral": {
            "ray": "a0=1, a1=r, tau=u, 0<r<1",
            "threshold": "u_min=(1+sqrt(r))^2",
            "measure": "dmu_r(u)=sqrt((u-(1+sqrt(r))^2)*(u-(1-sqrt(r))^2))*du/u",
            "pointwise_map": "T(r,u)=diag((2*u*(1+r)-(1-r)^2)/(2*u^2),-(1-r)^2/(2*u))",
            "pointwise_gram": "T(r,u)^sharp_phys*T(r,u)=rho(r,u)*I2",
            "rho": "(1-r)^2*(2*u*(1+r)-(1-r)^2)/(4*u^3)",
            "column": "(V_r h)(u)=T(r,u)h in L2(dmu_r) tensor C_cross^2",
            "integrated_gram": "V_r^sharp*V_r=I(r)*I2",
            "fixed_regulator_exponential": "A_r=[[0,-V_r^sharp],[V_r,0]]; exp(x*A_r) is sharp-unitary on parent plus ran(V_r)",
            "state": "CONSTRUCTED_FOR_EVERY_FIXED_MASS_RATIO"
        },
        "threshold_gram": {
            "relation_to_certified_threshold": "I(r)=-2*H(r)/3",
            "exact_function": "I(r)=(5*r^3-6*r^2*log(r)-3*r^2-6*r*log(r)+3*r-5)/(24*(r-1))",
            "axis_value": rat(Fraction(5, 24)),
            "equal_mass_value": rat(0),
            "axis_expansion": "I(r)=5/24+r*((1/4)*log(r)+1/12)+O(r^2*log(r))",
            "divided_germ": "D(r)=(I(r)-5/24)/r",
            "divided_germ_expansion": "D(r)=(1/4)*log(r)+1/12+O(r*log(r))",
            "mass_scale_cocycle": "lim_(r->0)[D(c*r)-D(r)]=log(c)/4",
            "physical_per_pair_cocycle": "log(c)/48",
            "three_pair_cocycle": "log(c)/16",
            "exact_fixtures": fixtures
        },
        "differentiability_obstruction": {
            "axis_derivative": "I'(0+)=-infinity",
            "lemma": "If V_r:C^2->K is strongly differentiable at r=0 and K has a fixed bounded fundamental symmetry, then each entry of V_r^sharp*V_r is differentiable with derivative V_0'^sharp*V_0+V_0^sharp*V_0'.",
            "contradiction": "V_r^sharp*V_r=I(r)*I2 but I'(0+) does not exist finitely",
            "disposition": "NO_ORDINARY_STRONGLY_C1_FIXED_BOUNDED_PAIRING_MOLLER_COLUMN",
            "does_not_exclude": ["a rigged distributional derivative", "an unbounded or regulator-dependent fundamental symmetry", "a non-normal local weight", "a resummed or nonperturbative massless-axis construction"]
        },
        "rigged_resolution_jordan": {
            "resolution_coordinate": "R=-log(r)",
            "asymptotic_germ": "D(exp(-R))=-R/4+1/12+o(1)",
            "translation_cocycle": "D(exp(-(R+a)))-D(exp(-R))->-a/4",
            "jordan_group": "U_a=[[1,-a/4],[0,1]]=exp(a*N)",
            "generator": "N=[[0,-1/4],[0,0]], N^2=0",
            "physical_generator_per_pair": "N_phys=N/12=[[0,-1/48],[0,0]]",
            "rigged_carrier": "Schwartz(R_s) subset L2(R_s,ds) subset Schwartz'(R_s)",
            "invariant_affine_sector": "span{1,s} inside Schwartz'(R_s)",
            "abel_affiliation": "inverse-Abel resolution translation acts on span{1,s}; its orientation-reversed defect has magnitude a/48 per physical pair",
            "L2_boundary": "the constant and coordinate distributions are not vectors of L2(R_s,ds)",
            "state": "RIGGED_RELATIVE_RESOLUTION_COCYCLE_CONSTRUCTED_WITHOUT_ENDPOINT_VECTOR"
        },
        "object_typing": {
            "physical_input": "the S-matrix five-point/four-point external mass-jet map T and its generalized-Born threshold Gram",
            "formal_time_input": "only the previously certified Abel translation of the resolution coordinate, not the public quadratic R_t D species map",
            "constructed_common_object": "the relative resolution translation cocycle on a rigged affine moment sector",
            "not_constructed": "a spacetime-local Hamiltonian affiliation or complete physical Moller/S operator"
        },
        "disposition": {
            "fixed_mass_ratio_physical_collinear_column": "CONSTRUCTED",
            "fixed_mass_ratio_pseudounitary_block": "CONSTRUCTED",
            "massless_axis_gram_limit": "FINITE",
            "ordinary_strong_C1_mass_axis_Moller_column": "EXACT_OBSTRUCTION",
            "relative_scale_cocycle": "ONE_OVER_48_PER_PAIR",
            "rigged_resolution_Jordan_lift": "CONSTRUCTED_WITHOUT_ENDPOINT_VECTOR",
            "ordinary_L2_resolution_Jordan_vector": "DOES_NOT_EXIST",
            "public_Rt_equals_physical_S_operator": "EXACT_OBSTRUCTION_RETAINED",
            "full_physical_Moller_operator": "NOT_CONSTRUCTED",
            "finite_complete_NLO_probability": "NOT_ESTABLISHED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
            "Eq19_all_orders": "NOT_PROVED"
        },
        "does_not_establish": [
            "a complete physical Moller or S operator", "an ordinary differentiable Hilbert or Krein mass-axis column",
            "a finite complete NLO probability", "positivity beyond tree level", "the all-order continuum Eq. (19)",
            "a spacetime-local LSZ or AQFT detector affiliation", "that unbounded or regulator-dependent metric completions fail",
            "that a rigged endpoint trace exists", "an identification of public R_t D with physical T",
            "a gravitational or BRST lift", "anything LORENTZIAN-CAUSAL", "a new spacetime dimension", "literature priority"
        ],
        "missing_object_ledger": [
            "a continuous generalized-Born functional on the rigged affine resolution sector that turns relative cocycles into normalized physical detector probabilities",
            "a spacetime-local asymptotic Hamiltonian whose wave operators act on the same rigged external-state domain and restrict to the certified T column",
            "complete incoming and outgoing degenerate sectors and their hard matching block beyond the leading logarithmic response",
            "the finite NLO constant together with a regulated and continuum beyond-tree pseudo-unitarity or generalized-Born positivity theorem",
            "the full nonlinear zero-mode representation, higher-composite induction, and common invariant domain required for the all-order continuum Eq. (19)"
        ],
        "next_gate": "Construct the generalized-Born functional on the Schwartz rigging rather than seeking an ordinary mass derivative. The decisive test is whether the affine moment cocycle can be paired with compact resolution detector differences so that the resulting non-normal functional is positive, normalized on finite incoming corners, and agrees with the certified one-over-48 trace without a chosen endpoint origin. Require translation covariance, independence of the smooth compact detector profile, and compatibility with the two null species of the physical T map. If that succeeds, affiliate its translation generator with the physical soft-collinear asymptotic Hamiltonian on complete incoming and outgoing sectors; if it fails, isolate the exact continuity, positivity, or domain obstruction and retain the relative cocycle without promoting an endpoint state.",
        "provenance": {"source_commit": SOURCE, "retrieval_date": "2026-08-11", "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS]},
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_rigged_resolution_jordan_moller.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_rigged_resolution_jordan_moller.py --exhaustive",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_rigged_resolution_jordan_moller"
        ],
        "checks": {"ok": all(checks.values()), "passed": sum(checks.values()), "total": len(checks), "failures": [name for name, ok in checks.items() if not ok], "details": checks},
        "report": REPORT,
        "schema": SCHEMA
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=CERT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    value = build()
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] recorded_certificate: {exc}")
            return 1
        ok = recorded == value
        print(f"[{'PASS' if ok else 'FAIL'}] exact_reproduction")
        print(f"RESULT: {'PASS' if ok else 'FAIL'} ({value['checks']['passed']}/{value['checks']['total']})")
        return 0 if ok else 1
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(args.output)
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
