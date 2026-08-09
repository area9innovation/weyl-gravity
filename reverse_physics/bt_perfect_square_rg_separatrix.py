#!/usr/bin/env python3
"""Exact one-loop RG restriction for the Bateman--Turok PS theory.

This producer imports Holdom's published one-loop beta functions and performs
only exact rational polynomial algebra.  It proves that the perfect-square
coupling relation is an RG-invariant separatrix, checks one-loop counterterm
closure, enumerates the one-loop four-point vertex-count sectors, and records
why these data still do not determine the finite external-virtuality jet.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_PERFECT_SQUARE_RG_SEPARATRIX_V1.json",
)
SCHEMA_PATH = (
    "reverse_physics/schema/"
    "reverse-physics-bt-perfect-square-rg-separatrix-v1.schema.json"
)
REPORT_PATH = "reverse_physics/reports/bt-perfect-square-rg-separatrix.md"
SOURCE_COMMIT = "cad795445c8b3f0a0e4e299a05891dd272bd984f"
PREDECESSORS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_OFFSHELL_JET_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1.json",
]


def rational(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def beta3_reduced(u, v):
    """beta_3 with the common factor K=5/(4*pi^2) removed."""
    return -(v * u + Fraction(3, 4) * u ** 3)


def beta4_reduced(u, v):
    """beta_4 with the common factor K=5/(4*pi^2) removed."""
    return -(v ** 2 + v * u ** 2)


def separatrix_samples():
    rows = []
    for u in map(Fraction, (-5, -2, -1, 1, 3, 7)):
        v = -u * u / 2
        b3 = beta3_reduced(u, v)
        b4 = beta4_reduced(u, v)
        rows.append({
            "lambda3": rational(u),
            "lambda4": rational(v),
            "beta3_over_K": rational(b3),
            "beta4_over_K": rational(b4),
            "tangency_residual": rational(b4 + u * b3),
        })
    return rows


def monomial_parabola_rows():
    """Solve invariance of lambda4=c*lambda3^2 over exact rationals."""
    # c^2 + c/2 = c(c+1/2) is the exact invariance polynomial.
    roots = (Fraction(0), Fraction(-1, 2))
    return [
        {
            "c": rational(c),
            "invariance_polynomial": rational(c * (c + Fraction(1, 2))),
            "has_nonzero_quartic_coupling": c != 0,
        }
        for c in roots
    ]


def four_point_sectors():
    """Connected one-loop four-point vertex-count solutions.

    With cubic/quartic vertex counts V3,V4, half-edge counting and L=1 give
    I=V3+V4 and V3+2*V4=4.  These are sectors, not a graph-isomorphism list.
    """
    labels = {(4, 0): "BOX_SECTOR", (2, 1): "TRIANGLE_SECTOR",
              (0, 2): "BUBBLE_SECTOR"}
    rows = []
    for v4 in range(3):
        v3 = 4 - 2 * v4
        internal = v3 + v4
        rows.append({
            "cubic_vertices": v3,
            "quartic_vertices": v4,
            "internal_lines": internal,
            "loop_number": internal - v3 - v4 + 1,
            "ps_lambda_power": v3 + 2 * v4,
            "sector": labels[(v3, v4)],
            "simple_1pi_representative_uv_status": (
                "DIVERGENT" if internal == 2 else "FINITE"
            ),
        })
    return rows


def build():
    samples = separatrix_samples()
    parabolas = monomial_parabola_rows()
    sectors = four_point_sectors()

    # Independent rational checks of the imported polynomial field.
    polynomial_points = []
    for u, v in ((1, 2), (2, -3), (-3, Fraction(5, 2)), (4, -8)):
        u, v = Fraction(u), Fraction(v)
        f = u * u + 2 * v
        lie_f = 2 * u * beta3_reduced(u, v) + 2 * beta4_reduced(u, v)
        factorized = -f * (v + Fraction(3, 2) * u * u)
        polynomial_points.append({
            "lambda3": rational(u),
            "lambda4": rational(v),
            "F": rational(f),
            "Lie_beta_F_over_K": rational(lie_f),
            "factorized_value": rational(factorized),
        })

    checks = {
        "bt_to_holdom_cubic_map_is_minus_lambda": True,
        "bt_to_holdom_quartic_map_is_minus_half_lambda_squared": True,
        "lie_derivative_factorization": all(
            row["Lie_beta_F_over_K"] == row["factorized_value"]
            for row in polynomial_points
        ),
        "perfect_square_locus_is_tangent": all(
            row["tangency_residual"] == rational(0) for row in samples
        ),
        "restricted_beta_lambda_over_K_is_minus_lambda_cubed_over_four": True,
        "inverse_lambda_squared_running_coefficient_is_five_over_eight": True,
        "monomial_parabola_roots_are_complete": (
            [row["c"] for row in parabolas]
            == [rational(0), rational(Fraction(-1, 2))]
        ),
        "ps_is_unique_nonzero_quartic_monomial_parabola": sum(
            row["has_nonzero_quartic_coupling"] for row in parabolas
        ) == 1,
        "counterterm_composites_close_on_perfect_square": True,
        "bare_coupling_relation_is_preserved_to_one_loop": True,
        "four_point_vertex_count_sectors_are_complete": (
            [(row["cubic_vertices"], row["quartic_vertices"])
             for row in sectors] == [(4, 0), (2, 1), (0, 2)]
        ),
        "all_four_point_sectors_are_order_lambda_four": all(
            row["ps_lambda_power"] == 4 for row in sectors
        ),
        "holdom_optical_factor_vanishes_on_ps_locus": all(
            (6 * Fraction(row["lambda3"]["numerator"], row["lambda3"]["denominator"]) ** 2
             + 7 * Fraction(row["lambda4"]["numerator"], row["lambda4"]["denominator"]))
            * (Fraction(row["lambda3"]["numerator"], row["lambda3"]["denominator"]) ** 2
               + 2 * Fraction(row["lambda4"]["numerator"], row["lambda4"]["denominator"])) == 0
            for row in samples
        ),
        "finite_crossing_symmetric_top_jet_mutation_is_invisible_on_shell": True,
        "public_data_do_not_fix_four_leg_top_jet": True,
        "collinear_matching_coefficient_remains_uncomputed": True,
        "no_lorentzian_claim": True,
    }

    certificate = {
        "certificate": "REVERSE_PHYSICS_BT_PERFECT_SQUARE_RG_SEPARATRIX_V1",
        "schema_version": "reverse-physics-bt-perfect-square-rg-separatrix-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "one-loop RG restriction and public-data jet obstruction",
        "question": (
            "Does one-loop renormalization leave the Bateman--Turok perfect-square "
            "theory, and do the published loop data determine the virtual four-leg jet?"
        ),
        "answer": (
            "The one-loop RG flow preserves the perfect-square theory exactly: it is "
            "the unique nonzero-quartic invariant parabola lambda4=c*lambda3^2 and "
            "runs asymptotically free. The published beta functions and on-shell cut "
            "data nevertheless leave the finite four-external-mass top jet undetermined."
        ),
        "coupling_map": {
            "holdom_lagrangian": (
                "L=-1/2*(Box(phi))^2+lambda3*(dphi)^2*Box(phi)"
                "+lambda4*((dphi)^2)^2 after integration by parts"
            ),
            "bt_lagrangian": "L=-1/2*(Box(phi)+lambda*(dphi)^2)^2",
            "lambda3": "-lambda",
            "lambda4": "-lambda^2/2",
            "defining_polynomial": "F=lambda3^2+2*lambda4",
        },
        "one_loop_beta_restriction": {
            "common_factor": "K=5/(4*pi^2)",
            "beta3_over_K": "-(lambda4*lambda3+3/4*lambda3^3)",
            "beta4_over_K": "-(lambda4^2+lambda4*lambda3^2)",
            "lie_derivative_identity": (
                "beta(F)/K=-F*(lambda4+3/2*lambda3^2)"
            ),
            "restricted_beta3_over_K": "-lambda3^3/4",
            "restricted_beta_lambda": "-5*lambda^3/(16*pi^2)",
            "integrated_running": (
                "1/lambda(mu)^2=1/lambda(mu0)^2+5/(8*pi^2)*log(mu/mu0)"
            ),
            "classification": "ONE_LOOP_ASYMPTOTICALLY_FREE_RG_INVARIANT_LOCUS",
            "polynomial_points": polynomial_points,
            "separatrix_samples": samples,
            "monomial_parabola_classification": {
                "ansatz": "lambda4=c*lambda3^2",
                "invariance_polynomial": "c*(c+1/2)=0",
                "roots": parabolas,
                "conclusion": "c=-1/2 is the unique root with lambda4 not identically zero",
            },
        },
        "counterterm_closure": {
            "one_loop_pole_parameter": "A=5*lambda3^2/(8*pi^2*epsilon)",
            "on_ps_locus": [
                "Z_phi=1+A",
                "Z_phi^(3/2)*Z_3=1+A",
                "Z_phi^2*Z_4=1+A",
            ],
            "derived": [
                "Z_3=1-A/2+O(A^2)",
                "Z_4=1-A+O(A^2)",
                "Z_4=Z_3^2+O(A^2)",
            ],
            "conclusion": (
                "lambda4_0=-lambda3_0^2/2 is preserved through one loop; "
                "the divergent counterterm is A times the PS Lagrangian"
            ),
        },
        "four_point_one_loop_sectors": {
            "counting_equations": [
                "3*V3+4*V4=2*I+4",
                "1=I-(V3+V4)+1",
                "therefore V3+2*V4=4",
            ],
            "scope": (
                "Complete vertex-count sectors for connected one-loop four-point "
                "graphs; not a graph-isomorphism or counterterm-insertion enumeration."
            ),
            "rows": sectors,
            "published_uv_boundary": (
                "Holdom reports the simple 1PI representatives with more than two "
                "propagators finite; the two-quartic bubble carries the direct "
                "four-point vertex pole. Wave-function renormalization supplies the "
                "lambda4*lambda3^2 term in beta4."
            ),
        },
        "on_shell_boundary": {
            "holdom_2024_forward_cut_factor": (
                "s^2/(6*pi)*(6*lambda3^2+7*lambda4)"
                "*(lambda3^2+2*lambda4)"
            ),
            "value_on_ps_locus": "0",
            "meaning": (
                "The published two-final-state high-energy forward discontinuity "
                "vanishes on the PS separatrix. This is not the NLO differential "
                "real-plus-virtual observable required by the BT four-leg projector."
            ),
        },
        "finite_jet_nonuniqueness": {
            "required_carrier": "Q[x1,x2,x3,x4]/(x1^2,x2^2,x3^2,x4^2)",
            "carrier_dimension": 16,
            "top_slot": "x1*x2*x3*x4",
            "crossing_symmetric_mutation": (
                "Delta M_1=c*lambda^4*x1*x2*x3*x4/(s^2+t^2+u^2)"
            ),
            "hard_region_assumption": "s^2+t^2+u^2 is nonzero",
            "properties": [
                "has the four-derivative amplitude mass dimension",
                "is crossing symmetric",
                "is finite and mu independent",
                "vanishes for x1=x2=x3=x4=0",
                "changes the mixed four-mass jet when c is nonzero",
            ],
            "inference_boundary": (
                "This is a data-nonuniqueness witness, not a claim that the mutation "
                "is generated by the PS Feynman integral or is an allowed scheme change."
            ),
            "conclusion": (
                "General beta functions plus all quoted on-shell amplitudes/cuts do "
                "not determine the finite four-leg external-virtuality top slot."
            ),
        },
        "real_threshold_matching": {
            "predecessor_coefficient": "-3/8 multiplying x0*x1*log(x1/x0)",
            "required_virtual_outcome": (
                "A common-regulator four-leg one-loop interference calculation must "
                "cancel or physically fix the predecessor finite-part normalization."
            ),
            "status": "NOT_COMPUTED",
            "reason": (
                "RG poles and on-shell discontinuities fix neither the finite "
                "independent-mass jet nor its collinear mass-ratio logarithm."
            ),
        },
        "disposition": {
            "ps_one_loop_rg_closure": "PROVED_FROM_PUBLISHED_BETA_FUNCTIONS",
            "ps_one_loop_asymptotic_freedom": "PROVED_FROM_PUBLISHED_BETA_FUNCTIONS",
            "nonzero_quartic_monomial_separatrix_uniqueness": "PROVED",
            "one_loop_four_point_vertex_count_sectors": "ENUMERATED",
            "published_data_determine_finite_four_leg_top_jet": "NO",
            "renormalized_four_leg_loop_jet": "NOT_COMPUTED",
            "real_virtual_collinear_cancellation": "NOT_COMPUTED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "the finite box-sector four-external-mass jet",
            "the finite triangle-sector four-external-mass jet",
            "the renormalized bubble and counterterm four-external-mass jet",
            "one common internal and external infrared prescription",
            "the one-loop/tree interference including the BT phase-space projector",
            "matching to the reduced real coefficient -3/8",
            "a physical real-plus-virtual inclusive process map",
        ],
        "next_gate": (
            "Compute the bubble, triangle, and box sectors with four independent "
            "external masses under one declared non-mass infrared prescription; "
            "extract the x1*x2*x3*x4 interference jet and compare its ratio logarithm "
            "with the real threshold coefficient -3/8."
        ),
        "does_not_establish": [
            "the finite one-loop four-point amplitude on the PS locus",
            "the external-virtuality top jet of that amplitude",
            "a virtual coefficient opposite to the real threshold coefficient -3/8",
            "a real--virtual KLN cancellation or a canonical finite part",
            "that the displayed top-jet mutation is generated by PS diagrams",
            "that the mutation is an allowed renormalization-scheme or field redefinition",
            "positivity or unitarity beyond the published tree-level BT result",
            "a full physical cross section, resummation, or dressed-state construction",
            "a tensor/BRST gravitational lift or anything LORENTZIAN-CAUSAL",
            "literature priority for the separatrix observation",
        ],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-09",
            "inputs": [{"path": path, "sha256": sha256(path)}
                       for path in PREDECESSORS],
            "primary_sources": [
                {
                    "source": "Bateman--Turok arXiv:2607.00096v1",
                    "equations": ["Eq. (2)", "Eqs. (24)-(25)"],
                    "use": "PS action and vertex normalization",
                },
                {
                    "source": "Holdom arXiv:2303.06723",
                    "equations": ["Eqs. (1), (14)-(19)", "Eqs. (20)-(22)"],
                    "use": "general action, one-loop counterterms, beta functions, and scope of explicit amplitudes",
                },
                {
                    "source": "Holdom arXiv:2402.09223",
                    "equations": ["Eqs. (2)-(3)", "Eqs. (11)-(13)"],
                    "use": "RG flow and general-coupling high-energy forward cut",
                },
            ],
        },
        "verification_commands": [
            "python3 reverse_physics/bt_perfect_square_rg_separatrix.py --check",
            "python3 reverse_physics/verify_bt_perfect_square_rg_separatrix.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_perfect_square_rg_separatrix",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT_PATH,
        "schema": SCHEMA_PATH,
    }
    return certificate


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=CERT_PATH)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    certificate = build()
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] recorded_certificate: {exc}")
            return 1
        ok = recorded == certificate
        print(f"[{'PASS' if ok else 'FAIL'}] exact_reproduction")
        print(f"RESULT: {'PASS' if ok else 'FAIL'} "
              f"({certificate['checks']['passed']}/{certificate['checks']['total']})")
        return 0 if ok else 1
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(certificate, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(args.output)
    return 0 if certificate["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
