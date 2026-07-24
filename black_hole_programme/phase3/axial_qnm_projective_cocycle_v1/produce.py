#!/usr/bin/env python3
"""Produce the exact scalar projective-cocycle certificate."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
INPUTS = {
    "triangular_factorization": (
        ROOT / "black_hole_programme/phase3/"
        "axial_rw_lx_triangular_preflight/certificate.json"
    ),
    "complete_reconstruction": (
        ROOT / "black_hole_programme/phase3/"
        "axial_complete_reconstruction_repair/certificate.json"
    ),
}
R, W = sp.symbols("r omega")
I = sp.I


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str | int) -> sp.Expr:
    return sp.sympify(value, locals={"r": R, "omega": W, "I": I})


def matrix(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[parse(value) for value in row] for row in rows])


def exact(value: sp.Expr) -> sp.Expr:
    return sp.cancel(sp.together(value))


def encode(value: sp.Expr) -> str:
    return sp.sstr(sp.factor(exact(value)))


def maximal_minor_gcd(value: sp.Matrix) -> sp.Expr:
    minors = [
        sp.factor(value[list(rows), :].det())
        for rows in itertools.combinations(range(value.rows), value.cols)
    ]
    nonzero = [minor for minor in minors if minor != 0]
    result = nonzero[0]
    for minor in nonzero[1:]:
        result = sp.gcd(result, minor)
    return sp.factor(result)


def produce() -> dict:
    triangular = json.loads(INPUTS["triangular_factorization"].read_text())
    complete = json.loads(INPUTS["complete_reconstruction"].read_text())
    flow6 = matrix(complete["complete_reconstruction"]["flow6"])
    source = flow6[4:, :4]
    embedding = matrix(
        triangular["carrier_exact_sequence"]["RW_embedding_J"]
    )
    master = matrix(
        triangular["Einstein_kernel_RW_equivalence"][
            "U_H1F_to_PsiPsiPrime"
        ]
    )
    extension = (master * source * embedding).applyfunc(exact)

    rw = triangular["operators"]["L_RW"]
    a_rw, b_rw = parse(rw["a"]), parse(rw["b"])
    e00, e01, e10, e11 = (
        extension[0, 0], extension[0, 1],
        extension[1, 0], extension[1, 1],
    )
    # The first extension row changes the relation between the companion's
    # second coordinate and the derivative of the metric scalar.
    s1_r = exact(e11 + e00 + sp.diff(e01, R))
    s0_r = exact(
        a_rw * e00 + e10 + sp.diff(e00, R) - b_rw * e01
    )
    f = (R - 2) / R
    dstar = lambda value: exact(f * sp.diff(value, R))
    potential = 6 * (R - 2) * (R - 1) / R**4
    u = exact(W**2 - potential)
    s1 = exact(f * s1_r)
    s0 = exact(f**2 * s0_r - I * W * f * s1_r)
    cocycle = exact(s0 - sp.Rational(1, 2) * dstar(s1))
    projective = lambda value: exact(
        dstar(dstar(dstar(value)))
        + 4 * u * dstar(value)
        + 2 * dstar(u) * value
    )

    gauge_a = sp.Function("gauge_a")(R)
    gauge_b = sp.Function("gauge_b")(R)
    delta_s1 = dstar(dstar(gauge_a)) + 2 * dstar(gauge_b)
    delta_s0 = (
        dstar(dstar(gauge_b))
        - gauge_a * dstar(u)
        - 2 * dstar(gauge_a) * u
    )
    gauge_identity = exact(
        delta_s0
        - sp.Rational(1, 2) * dstar(delta_s1)
        + sp.Rational(1, 2) * projective(gauge_a)
    )
    if gauge_identity != 0:
        raise RuntimeError("projective gauge identity failed")

    rho_gauge = -I / (W**2 * (R * W - 2 * I))
    residual = exact(
        cocycle + sp.Rational(1, 2) * projective(rho_gauge)
    )
    c_m2, c_m1, c_0 = sp.symbols("c_m2 c_m1 c_0")
    completion = c_m2 / R**2 + c_m1 / R + c_0
    exactness_expr = sp.together(
        projective(completion) + 2 * residual
    )
    exact_poly = sp.Poly(exactness_expr.as_numer_denom()[0], R)
    exact_matrix, exact_rhs = sp.linear_eq_to_matrix(
        exact_poly.all_coeffs(), [c_m2, c_m1, c_0]
    )
    exact_left_witness = sp.Matrix([
        (104 * W**4 - 75 * W**2 + 126) / (9 * W**4),
        26 * (2 * W**2 + 3) / (9 * W**2),
        2 * (13 * W**2 + 6) / (9 * W**2),
        1, 0, 0,
    ])
    exact_obstruction = exact(
        (exact_left_witness.T * exact_rhs)[0]
    )
    if any(exact(value) != 0 for value in (
        exact_left_witness.T * exact_matrix
    )):
        raise RuntimeError("exactness left-null witness drift")

    reduced_coefficients = {
        c_m2: -3 * I / (20 * W),
        c_m1: -I / (5 * W),
        c_0: (-13 * I * W - 30) / (60 * W**2),
    }
    reducing_gauge = exact(rho_gauge + completion.subs(reduced_coefficients))
    reduced = exact(
        cocycle + sp.Rational(1, 2) * projective(reducing_gauge)
    )

    q = sp.Symbol("q")
    angular = exact(-f / R**2)
    angular_expr = sp.together(
        projective(completion) + 2 * residual - 2 * q * angular
    )
    angular_poly = sp.Poly(angular_expr.as_numer_denom()[0], R)
    angular_matrix, angular_rhs = sp.linear_eq_to_matrix(
        angular_poly.all_coeffs(), [c_m2, c_m1, c_0, q]
    )
    angular_left_witness = sp.Matrix([
        40 * (21 * W**2 - 41) / (3 * (11 * W**2 - 6)),
        20 * (21 * W**2 - 41) / (3 * (11 * W**2 - 6)),
        10 * (21 * W**2 - 26) / (3 * (11 * W**2 - 6)),
        (31 * W**2 - 26) / (11 * W**2 - 6),
        1, 0,
    ])
    angular_obstruction = exact(
        (angular_left_witness.T * angular_rhs)[0]
    )
    if any(exact(value) != 0 for value in (
        angular_left_witness.T * angular_matrix
    )):
        raise RuntimeError("angular left-null witness drift")
    exact_minor_gcd = maximal_minor_gcd(exact_matrix)
    angular_minor_gcd = maximal_minor_gcd(angular_matrix)

    document = {
        "schema": "phase3-axial-qnm-projective-cocycle-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": "EXACT_RATIONAL_COCYCLE_NONTRIVIAL_QNM_UNEVALUATED",
        "scope": {
            "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Schwarzschild exterior M=1",
            "sector": "axial ell=2 repeated spin-two filtered block",
            "field": "C(I,omega)(r), generic omega",
            "derivative": "D=D_rstar=((r-2)/r)*D_r",
            "frequency_exclusions": [
                "omega=0 threshold",
                "special divisor collisions such as omega=I are not classified",
            ],
        },
        "imports": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
            }
            for name, path in INPUTS.items()
        },
        "scalarization": {
            "f": encode(f),
            "field_redefinition": "psi=exp(I*omega*rstar)*P",
            "operator": "L=D**2+U",
            "U": encode(u),
            "source_convention": "L*x=(s1*D+s0)*y",
            "s1_r": encode(s1_r),
            "s0_r": encode(s0_r),
            "s1": encode(s1),
            "s0": encode(s0),
            "first_extension_row_included": True,
        },
        "projective_cocycle": {
            "definition": "calI=s0-(D*s1)/2",
            "calI": encode(cocycle),
            "numerator_factor": encode(
                sp.together(cocycle).as_numer_denom()[0]
            ),
            "denominator_factor": encode(
                sp.together(cocycle).as_numer_denom()[1]
            ),
            "projective_operator": "K_U=D**3+4*U*D+2*(D*U)",
            "gauge_change": "x -> x+(a*D+b)*y",
            "gauge_law": "delta_calI=-(K_U*a)/2",
            "gauge_identity_verified": True,
        },
        "local_pole_audit": {
            "singularities": {
                "r=0": "calI has pole order 3",
                "r=2": "calI has a zero; generic rational gauge has no pole",
                "r=2*I/omega": "calI has pole order 4; gauge has at most a simple pole",
                "r=infinity": "calI=O(r**-2); polynomial gauge part is constant",
            },
            "r0_indicial_factor": "-8*(m-6)*(m-2)*(m+2)",
            "horizon_indicial_factor": "m*(m**2+16*omega**2)/8",
            "infinity_leading_factor": "4*m*omega**2*r**(m-1)",
            "apparent_pole_leading_calI": "-3*(omega-I)**3/omega**3",
            "apparent_pole_leading_K_simple": "6*I*(omega-I)**3/omega",
            "forced_apparent_gauge": encode(rho_gauge),
            "exhaustive_generic_ansatz": (
                "-I/(omega**2*(r*omega-2*I))"
                "+c_m2/r**2+c_m1/r+c_0"
            ),
        },
        "rational_nonexactness": {
            "equation": "K_U*a+2*calI=0",
            "coefficient_matrix": [
                [encode(value) for value in row]
                for row in exact_matrix.tolist()
            ],
            "rhs": [encode(value) for value in exact_rhs],
            "matrix_rank": int(exact_matrix.rank()),
            "augmented_rank": int(exact_matrix.row_join(exact_rhs).rank()),
            "left_null_witness": [
                encode(value) for value in exact_left_witness
            ],
            "left_null_obstruction": encode(exact_obstruction),
            "solution": "EMPTY",
            "conclusion": "[calI] != 0 over the declared generic rational field",
        },
        "reduced_representative": {
            "equivalence_convention": "calI_reduced=calI+(K_U*a_reducing)/2",
            "a_reducing": encode(reducing_gauge),
            "calI_reduced": encode(reduced),
            "reduction_rule": (
                "match the apparent pole and cancel the three highest "
                "remaining r=0 pole coefficients"
            ),
            "canonical_under_all_analytic_gauges": False,
        },
        "angular_class_test": {
            "classification": "algebraic angular spectral deformation, not a physical background tangent",
            "angular_derivative": encode(angular),
            "equation": "calI+(K_U*a)/2=q*(-f/r**2)",
            "coefficient_matrix": [
                [encode(value) for value in row]
                for row in angular_matrix.tolist()
            ],
            "rhs": [encode(value) for value in angular_rhs],
            "matrix_rank": int(angular_matrix.rank()),
            "augmented_rank": int(
                angular_matrix.row_join(angular_rhs).rank()
            ),
            "left_null_witness": [
                encode(value) for value in angular_left_witness
            ],
            "left_null_obstruction": encode(angular_obstruction),
            "solution": "EMPTY",
            "conclusion": (
                "[calI] is not proportional to [-f/r**2] over the "
                "declared generic rational field"
            ),
        },
        "finite_specialization_corollary": {
            "rational_nonexactness_witness": encode(exact_obstruction),
            "rational_nonexactness_certified_when": (
                "omega!=0, omega!=I, and omega**2!=3"
            ),
            "angular_nonproportionality_witness": encode(
                angular_obstruction
            ),
            "angular_nonproportionality_certified_when": (
                "omega!=0, omega!=I, and omega**2!=-4"
            ),
            "rank_change_locus_exactness_matrix": ["omega=0"],
            "rank_change_locus_angular_matrix": ["omega=0"],
            "maximal_minor_gcd_exactness": encode(exact_minor_gcd),
            "maximal_minor_gcd_angular": encode(angular_minor_gcd),
            "reduction_denominator_exclusions": [
                "omega=0: threshold and reducing-gauge denominators",
                "omega=I: r*omega-2*I collides with the horizon r=2",
            ],
            "witness_zero_loci_not_classified": [
                "omega**2=3 for the rational-nonexactness witness",
                "omega**2=-4 for the angular witness",
            ],
            "safe_reading": (
                "Splitting is excluded wherever the applicable witness is "
                "defined and nonzero. No splitting or nonsplitting statement "
                "is inferred at an excluded or witness-zero specialization."
            ),
        },
        "claim_flags": {
            "exact_scalarization_rederived": True,
            "projective_gauge_law_exact": True,
            "generic_rational_ansatz_exhaustive": True,
            "generic_rational_cocycle_nontrivial": True,
            "declared_reduced_representative_exact": True,
            "generic_angular_class_nonproportional": True,
            "beta_n_evaluated": False,
            "physical_QNM_fredholm_realization_constructed": False,
            "simple_QNM_smith_case_selected": False,
            "QNM_double_pole_established": False,
        },
        "does_not_establish": [
            "a value or nonzero theorem for any QNM period beta_n",
            "a Smith case at any physical Regge-Wheeler QNM",
            "a second-order inverse-connection or Green-resolvent pole",
            "a generalized ringdown term",
            "special-frequency rational cohomology at omega=0 or divisor collisions",
            "a LORENTZIAN-CAUSAL quantum theorem",
        ],
    }
    OUTPUT.write_text(json.dumps(document, indent=2) + "\n")
    return document


if __name__ == "__main__":
    result = produce()
    print(result["status"])
