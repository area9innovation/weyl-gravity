#!/usr/bin/env python3
"""Certify the generic-background Diff x Weyl ghost obstruction to minimal CPT.

The conformal-transverse vector gauge has an algebraic Weyl-ghost row, but
eliminating it does not make the diffeomorphism ghost Laplace type.  The
resulting nonminimal vector operator is independent of the trace coefficient
in the vector gauge.  On a non-Einstein background it also fails to preserve
the longitudinal Hodge sector.  Consequently the Einstein-background four-
factor determinant ledger cannot be substituted directly into the imported
minimal-Laplace CPT kernels.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_DIFF_WEYL_GHOST_CPT_OBSTRUCTION.json"
SCHEMA = HERE / "schema/generic-background-diff-weyl-ghost-cpt-obstruction-v1.schema.json"
DEPENDENCIES = {
    "classical_minimal_BV": ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json",
    "Einstein_scalar_ghost_reduction": HERE / "certificates/DIFF_WEYL_SCALAR_GHOST_REDUCTION.json",
    "full_BV_multiplicity_ledger": HERE / "certificates/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json",
    "universal_CPT_kernels": ROOT / "quantum-weyl/transfer/certificates/CPT_UNIVERSAL_THIRD_CURVATURE_KERNELS.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value.get("result_id") or value.get("schema")),
        "sha256": _sha256(path),
    }


def _q(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _diag(values: tuple[Fraction, ...]) -> list[list[dict[str, int]]]:
    return [
        [_q(value if row == column else 0) for column in range(len(values))]
        for row, value in enumerate(values)
    ]


def _schur_row(beta: Fraction) -> dict[str, Any]:
    vector_divergence = Fraction(1) - 2 * beta
    vector_from_weyl = 2 * (Fraction(1) - 4 * beta)
    trace_from_vector = Fraction(2)
    trace_from_weyl = Fraction(8)
    correction = vector_from_weyl * trace_from_vector / trace_from_weyl
    effective = vector_divergence - correction
    return {
        "beta": _q(beta),
        "vector_divergence_coefficient_before_elimination": _q(vector_divergence),
        "gradient_weyl_coefficient": _q(vector_from_weyl),
        "trace_divergence_coefficient": _q(trace_from_vector),
        "trace_weyl_coefficient": _q(trace_from_weyl),
        "Schur_correction": _q(correction),
        "effective_divergence_coefficient": _q(effective),
    }


def _validate_dependencies(values: dict[str, dict[str, Any]]) -> None:
    classical = values["classical_minimal_BV"]
    scalar = values["Einstein_scalar_ghost_reduction"]
    ledger = values["full_BV_multiplicity_ledger"]
    cpt = values["universal_CPT_kernels"]
    if (
        classical.get("claim_flags", {}).get("CLASSICAL_ANTIFIELD_EXPORT_IMPORTED")
        is not True
        or scalar.get("exact_variation", {}).get("vector_gauge_general_beta")
        != "delta F_mu=Box xi_mu+Ric_mu_nu xi^nu+(1-2 beta)nabla_mu div(xi)+2(1-4 beta)nabla_mu omega"
        or scalar.get("gauge_conventions", {}).get("trace_gauge") != "F_W=h"
        or ledger.get("result_state") != "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED"
        or cpt.get("claim_flags", {}).get("FIVE_UNIVERSAL_CPT_KERNELS_IMPORTED")
        is not True
        or cpt.get("claim_flags", {}).get(
            "REPOSITORY_GENERIC_BACKGROUND_TRACE_SUBSTITUTION_SUPPLIED"
        )
        is not False
    ):
        raise ValueError("generic-background ghost CPT dependencies drifted")


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    _validate_dependencies(values)

    beta_rows = [_schur_row(beta) for beta in (Fraction(0), Fraction(1, 4), Fraction(1, 2))]
    if any(row["effective_divergence_coefficient"] != _q(Fraction(1, 2)) for row in beta_rows):
        raise AssertionError("Diff-Weyl ghost Schur complement depends on beta")

    # At a unit covector e_0 the normalized principal symbol is
    # I+(1/2)e_0 e_0^T.  At e_1 it is the corresponding permuted diagonal.
    p0 = (Fraction(3, 2), Fraction(1), Fraction(1), Fraction(1))
    p1 = (Fraction(1), Fraction(3, 2), Fraction(1), Fraction(1))
    p0_inverse = tuple(Fraction(1, 1) / value for value in p0)
    relative_symbol = tuple(left * right for left, right in zip(p0_inverse, p1, strict=True))
    if len(set(p0)) != 2 or len(set(relative_symbol)) == 1:
        raise AssertionError("nonminimal principal-symbol witness collapsed")

    # A tracefree Ricci jet S_01=S_10=1 sends k=e_0 to e_1.  The curvature
    # term 2 S.k therefore has a nonzero transverse component, so gradients
    # are not preserved on a generic background.
    tracefree_ricci = (
        (0, 1, 0, 0),
        (1, 0, 0, 0),
        (0, 0, 0, 0),
        (0, 0, 0, 0),
    )
    gradient_covector = (1, 0, 0, 0)
    mixing = tuple(
        2 * sum(tracefree_ricci[row][column] * gradient_covector[column] for column in range(4))
        for row in range(4)
    )
    if mixing != (0, 2, 0, 0):
        raise AssertionError("tracefree-Ricci Hodge-mixing witness drifted")

    result = {
        "schema": "quantum-weyl-generic-background-diff-weyl-ghost-cpt-obstruction-v1",
        "result_id": "GENERIC_BACKGROUND_DIFF_WEYL_GHOST_CPT_OBSTRUCTION",
        "result_state": "GENERIC_GHOST_OPERATOR_NONMINIMAL_AND_HODGE_MIXED_MINIMAL_CPT_SUBSTITUTION_OBSTRUCTED",
        "lifecycle_state": "OBSTRUCTED_CURRENT_MINIMAL_CPT_ARCHITECTURE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": values["classical_minimal_BV"]["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "background": "generic local oriented metric; Einstein specialization recorded separately",
            "gauge": "F_mu=nabla^nu h_mu_nu-beta nabla_mu h and F_W=h",
            "domain": "compactly supported local ghost jets; zero modes and global boundary data excluded",
        },
        "exact_FP_rows": {
            "metric_BRST": "delta h_mu_nu=nabla_mu xi_nu+nabla_nu xi_mu+2 omega g_mu_nu",
            "vector_gauge_variation": "delta F_mu=Box xi_mu+Ric_mu_nu xi^nu+(1-2 beta)nabla_mu div(xi)+2(1-4 beta)nabla_mu omega",
            "trace_gauge_variation": "delta F_W=2 div(xi)+8 omega",
            "weyl_row_is_algebraically_invertible": True,
        },
        "algebraic_Weyl_ghost_elimination": {
            "method": "Schur complement of the algebraic 8 in the coupled (F_mu,F_W) by (xi,omega) FP operator",
            "beta_controls": beta_rows,
            "effective_vector_operator": "M_eff xi_mu=Box xi_mu+Ric_mu_nu xi^nu+(1/2)nabla_mu div(xi)",
            "beta_independent": True,
        },
        "nonminimal_principal_symbol": {
            "normalized_formula": "sigma_2(M_eff)(k)=|k|^2 I+(1/2) k tensor k",
            "unit_covector_e0": _diag(p0),
            "eigenvalues_e0": [_q(value) for value in p0],
            "transverse_multiplicity": 3,
            "longitudinal_multiplicity": 1,
            "elliptic": True,
            "Laplace_type": False,
            "characteristic_polynomial": "(lambda-1)^3(lambda-3/2)",
            "fixed_two_sided_scalarizer_no_go": {
                "principal_symbol_e0_inverse": _diag(p0_inverse),
                "principal_symbol_e1": _diag(p1),
                "relative_symbol_P0_inverse_P1_diagonal": [_q(value) for value in relative_symbol],
                "is_scalar": False,
                "reason": "if fixed invertible A,B made A P(k) B scalar for both unit covectors, P0^{-1}P1 would be scalar up to similarity; its exact diagonal is (2/3,3/2,1,1)",
            },
        },
        "generic_Hodge_mixing": {
            "identity_on_gradient": "M_eff(nabla c)=-(3/2)nabla Delta_0 c+2 Ric_mu_nu nabla^nu c",
            "Ricci_split": "Ric_mu_nu=(R/4)g_mu_nu+S_mu_nu",
            "tracefree_Ricci_fixture": [list(row) for row in tracefree_ricci],
            "gradient_covector_fixture": list(gradient_covector),
            "transverse_mixing_term_2S_dot_k": list(mixing),
            "longitudinal_subspace_preserved": False,
            "Einstein_specialization": "M_eff(nabla c)=-(3/2)nabla(Delta_0-R/3)c",
            "Einstein_scalar_factor_reproduced": "Delta_0-R/3",
        },
        "CPT_applicability_decision": {
            "imported_kernel_operator_class": "minimal second-order Laplace type F=-Box+P",
            "generic_repository_ghost_operator_class": "nonminimal vector operator with Hodge mixing",
            "current_four_factor_ledger_background": "Einstein/round-S4 reduction",
            "verdict": "DIRECT_MINIMAL_CPT_SUBSTITUTION_FOR_THE_GENERIC_GHOST_SECTOR_IS_OBSTRUCTED",
            "minimal_missing_calculation": "a covariant nonminimal-vector CPT determinant for M_eff in the matched Diff-Weyl gauge and measure, or a different generic-background gauge/local field extension with an exact determinant-and-Jacobian equivalence to minimal Laplace blocks",
        },
        "claim_flags": {
            "GENERIC_DIFF_WEYL_FP_ROWS_DERIVED": True,
            "ALGEBRAIC_WEYL_GHOST_ELIMINATED": True,
            "EFFECTIVE_VECTOR_OPERATOR_BETA_INDEPENDENT": True,
            "GENERIC_GHOST_PRINCIPAL_SYMBOL_NONMINIMAL": True,
            "GENERIC_GHOST_HODGE_SPLIT_OBSTRUCTED": True,
            "EINSTEIN_SCALAR_GHOST_FACTOR_REPRODUCED": True,
            "GENERIC_NONMINIMAL_GHOST_CPT_DETERMINANT_COMPUTED": False,
            "REPOSITORY_GENERIC_BACKGROUND_TRACE_SUBSTITUTION_SUPPLIED": False,
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED": False,
            "REPOSITORY_CUBIC_COEFFICIENTS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "NONMINIMAL_GENERIC_BACKGROUND_GHOST_CPT_DETERMINANT_AND_PHYSICAL_FOURTH_ORDER_HESSIAN_KERNEL",
        "claim_boundary": "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL theorem derives the generic coupled Diff-Weyl FP rows and their exact algebraic Weyl-ghost Schur complement. The resulting beta-independent vector operator is elliptic but non-Laplace type, has unequal transverse/longitudinal principal eigenvalues, and fails to preserve the Hodge split for a generic tracefree-Ricci jet. It reproduces the accepted scalar ghost factor only on Einstein backgrounds. Therefore the existing Einstein four-factor ledger cannot be substituted directly into the five imported minimal-Laplace CPT kernels. This does not compute the required nonminimal ghost determinant, the generic physical fourth-order Hessian kernel, any repository cubic function or coefficient, complete Gamma1 or Q1, residual transfer, or a Lorentzian, Hadamard, particle, positivity or unitarity theorem.",
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    flags = value["claim_flags"]
    required_true = (
        "GENERIC_DIFF_WEYL_FP_ROWS_DERIVED",
        "ALGEBRAIC_WEYL_GHOST_ELIMINATED",
        "EFFECTIVE_VECTOR_OPERATOR_BETA_INDEPENDENT",
        "GENERIC_GHOST_PRINCIPAL_SYMBOL_NONMINIMAL",
        "GENERIC_GHOST_HODGE_SPLIT_OBSTRUCTED",
        "EINSTEIN_SCALAR_GHOST_FACTOR_REPRODUCED",
    )
    required_false = tuple(name for name in flags if name not in required_true)
    if any(flags[name] is not True for name in required_true) or any(
        flags[name] is not False for name in required_false
    ):
        raise ValueError("generic-background ghost CPT result crossed its boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale generic-background ghost CPT certificate: {OUTPUT}")
    print("GENERIC DIFF-WEYL GHOST CPT: NONMINIMAL/HODGE-MIXED OBSTRUCTION CERTIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
