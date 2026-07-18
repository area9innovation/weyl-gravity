#!/usr/bin/env python3
"""Reduce the generic Diff x Weyl ghost determinant to an Endo base.

The positive Euclidean operator ``H=-M_eff`` is not itself in the exactly
solvable nonminimal vector family because its Ricci endomorphism has the
opposite sign.  It nevertheless has the exact split

    H = H0 + W,
    H0 = F - (1/2) grad div,
    F = -Box I + Ric,
    W = -2 Ric.

``H0`` is the nondegenerate Endo vector operator with alpha=-1/2.  Its heat
kernel is a finite-proper-time transform of the minimal vector and scalar heat
kernels.  The remaining perturbation is a local curvature-order-one
endomorphism, so through third curvature order the determinant requires at
most three Duhamel insertions.  This is an exact reduction, not yet the
evaluation of those insertion traces.
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
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_GHOST_ENDO_DUHAMEL_REDUCTION.json"
SCHEMA = HERE / "schema/generic-background-ghost-endo-duhamel-reduction-v1.schema.json"
DEPENDENCIES = {
    "ghost_CPT_obstruction": HERE / "certificates/GENERIC_BACKGROUND_DIFF_WEYL_GHOST_CPT_OBSTRUCTION.json",
    "universal_CPT_kernels": ROOT / "quantum-weyl/transfer/certificates/CPT_UNIVERSAL_THIRD_CURVATURE_KERNELS.json",
}

SOURCE_ARCHIVE_SHA256 = "485ad72c51304f25e289d3f6c72705a956c547c134e2f183bef3750e63e6757c"
SOURCE_TEX_SHA256 = "4b5cdb2dbf08cc1a34dc268e1961c54f0a1eee096d2df63214a73e91d0d71fc2"


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


def _validate_dependencies(values: dict[str, dict[str, Any]]) -> None:
    obstruction = values["ghost_CPT_obstruction"]
    kernels = values["universal_CPT_kernels"]
    if (
        obstruction.get("CPT_applicability_decision", {}).get("verdict")
        != "DIRECT_MINIMAL_CPT_SUBSTITUTION_FOR_THE_GENERIC_GHOST_SECTOR_IS_OBSTRUCTED"
        or obstruction.get("algebraic_Weyl_ghost_elimination", {}).get(
            "effective_vector_operator"
        )
        != "M_eff xi_mu=Box xi_mu+Ric_mu_nu xi^nu+(1/2)nabla_mu div(xi)"
        or kernels.get("claim_flags", {}).get("FIVE_UNIVERSAL_CPT_KERNELS_IMPORTED")
        is not True
    ):
        raise ValueError("Endo-Duhamel dependencies drifted")


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    _validate_dependencies(values)

    alpha = Fraction(-1, 2)
    longitudinal_eigenvalue = 1 - alpha
    inverse_longitudinal = 1 / longitudinal_eigenvalue

    # Coefficient triples are (rough -Box, Ric endomorphism, grad div).
    h = (Fraction(1), Fraction(-1), Fraction(-1, 2))
    f = (Fraction(1), Fraction(1), Fraction(0))
    h0 = (f[0], f[1], alpha)
    w = tuple(left - right for left, right in zip(h, h0, strict=True))
    if w != (Fraction(0), Fraction(-2), Fraction(0)):
        raise AssertionError("the Endo split did not isolate W=-2 Ric")

    insertion_table = []
    for insertion_count in range(4):
        insertion_table.append(
            {
                "Ricci_insertion_count": insertion_count,
                "maximum_background_order_from_Endo_kernels": 3 - insertion_count,
                "total_curvature_order": 3,
                "Duhamel_sign": -1 if insertion_count % 2 else 1,
                "simplex_dimension": insertion_count,
            }
        )

    result = {
        "schema": "quantum-weyl-generic-background-ghost-endo-duhamel-reduction-v1",
        "result_id": "GENERIC_BACKGROUND_GHOST_ENDO_DUHAMEL_REDUCTION",
        "result_state": "NONMINIMAL_GHOST_EXACTLY_REDUCED_TO_ENDO_BASE_PLUS_LOCAL_RICCI_DUHAMEL_SERIES",
        "lifecycle_state": "EXACT_REDUCTION_CERTIFIED_INSERTION_TRACES_NOT_EVALUATED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": values["ghost_CPT_obstruction"]["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "background": "generic local oriented metric; compact without boundary for determinant factorization",
            "operator_domain": "nonzero ghost modes; global zero-mode volume and boundary conditions remain separately primed",
            "curvature_order": "exact operator split; determinant work table truncated through O(curvature^3)",
        },
        "repository_operator_convention": {
            "Schur_operator": "M_eff=Box I+Ric+(1/2) grad div",
            "positive_Euclidean_operator": "H=-M_eff=-Box I-Ric-(1/2) grad div",
            "coefficient_basis": ["-Box I", "Ric", "grad div"],
            "H_coefficients": [_q(value) for value in h],
        },
        "exact_Endo_split": {
            "minimal_vector_operator": "F=-Box I+Ric",
            "Endo_base": "H0=F+alpha grad div",
            "alpha": _q(alpha),
            "local_perturbation": "W=-2 Ric",
            "F_coefficients": [_q(value) for value in f],
            "H0_coefficients": [_q(value) for value in h0],
            "W_coefficients": [_q(value) for value in w],
            "identity": "H=H0+W",
            "Ward_identities": [
                "div F=Delta_0 div",
                "F grad=grad Delta_0",
            ],
            "gradient_action": "H0 grad=(3/2) grad Delta_0; H grad=(3/2) grad Delta_0-2 Ric grad",
        },
        "principal_projectors": {
            "transverse_eigenvalue": _q(1),
            "longitudinal_eigenvalue": _q(longitudinal_eigenvalue),
            "flat_inverse": "H0^{-1}=Delta_0^{-1}(Pi_T+(2/3)Pi_L)",
            "inverse_longitudinal_coefficient": _q(inverse_longitudinal),
            "nondegenerate": True,
        },
        "exact_Endo_heat_kernel": {
            "formula": "K_H0(t)=K_F(t)-grad grad_prime integral_t^(3t/2) ds K_Delta0(s)",
            "proper_time_lower_multiplier": _q(1),
            "proper_time_upper_multiplier": _q(longitudinal_eigenvalue),
            "flat_projector_check": "K_H0_flat=Pi_T exp(-t p^2)+Pi_L exp(-(3/2)t p^2)",
            "finite_proper_time_interval": True,
            "IR_infinite_range_introduced": False,
        },
        "nonzero_mode_determinant_identity": {
            "formula": "det_prime(H0)=det_prime(F)*det_prime((3/2)Delta_0)/det_prime(Delta_0)",
            "zeta_scaled_formula": "log det_prime(H0)=log det_prime(F)+zeta_Delta0(0) log(3/2)",
            "nonlocal_form_factor_consequence": "the Endo-base difference from F is local; nonlocal corrections enter through W=-2 Ric insertions",
            "zero_modes_excluded": True,
        },
        "Duhamel_expansion": {
            "heat_kernel_formula": "exp(-t(H0+W))=sum_n>=0 (-1)^n integral_ordered_simplex exp(-(t-s1)H0) W ... W exp(-sn H0)",
            "log_determinant_formula": "Tr log H=Tr log H0+sum_n>=1 (-1)^(n+1) Tr((H0^{-1}W)^n)/n",
            "curvature_degree_of_W": 1,
            "cubic_work_table": insertion_table,
            "maximum_W_insertions_through_cubic_order": 3,
            "finite_at_declared_order": True,
        },
        "source_provenance": {
            "title": "Schwinger--DeWitt expansion for the heat kernel of nonminimal operators in causal theories",
            "authors": ["A. O. Barvinsky", "A. E. Kalugin", "W. Wachowski"],
            "arxiv": "2508.06439v2",
            "url": "https://arxiv.org/abs/2508.06439v2",
            "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
            "source_tex_file": "nonmin1rev.tex",
            "source_tex_sha256": SOURCE_TEX_SHA256,
            "formula_locations": [
                "equations labelled minimal_vector and Ward",
                "equations labelled nonminimal-vector, K11, fullKforvec",
            ],
            "convention_specialization": "source H=-Box I+alpha grad div+Ric with alpha=-1/2 is H0; repository H differs by W=-2 Ric",
        },
        "claim_flags": {
            "GENERIC_GHOST_ENDO_BASE_IDENTIFIED": True,
            "ENDO_HEAT_KERNEL_FORMULA_SPECIALIZED": True,
            "NONZERO_MODE_ENDO_DETERMINANT_REDUCED": True,
            "CUBIC_DUHAMEL_INSERTION_BOUND_CERTIFIED": True,
            "GENERIC_NONMINIMAL_GHOST_CPT_REDUCTION_SUPPLIED": True,
            "GENERIC_NONMINIMAL_GHOST_INSERTION_TRACES_EVALUATED": False,
            "GENERIC_NONMINIMAL_GHOST_CPT_DETERMINANT_COMPUTED": False,
            "PHYSICAL_FOURTH_ORDER_HESSIAN_KERNEL_COMPUTED": False,
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED": False,
            "REPOSITORY_CUBIC_COEFFICIENTS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "EVALUATE_GHOST_RICCI_INSERTION_TRACES_N1_N2_N3_AND_SUPPLY_PHYSICAL_FOURTH_ORDER_HESSIAN_KERNEL",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL result exactly rewrites the positive generic Diff-Weyl ghost operator as the nondegenerate Endo vector base H0=F-(1/2)grad div plus the local endomorphism W=-2 Ric. The Endo base has an exact finite-proper-time heat-kernel formula and a nonzero-mode determinant reduction to one minimal vector and one scalar scaling term. Since W is curvature order one, the generic ghost determinant through third curvature order requires no more than three ordered Ricci insertions. The insertion traces and their carrier coefficients have not been evaluated, the generic physical fourth-order Hessian kernel is absent, and no repository cubic function or coefficient, complete Gamma1/Q1, residual transfer, Lorentzian, Hadamard, particle, positivity or unitarity theorem is claimed."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    flags = value["claim_flags"]
    true_flags = {
        "GENERIC_GHOST_ENDO_BASE_IDENTIFIED",
        "ENDO_HEAT_KERNEL_FORMULA_SPECIALIZED",
        "NONZERO_MODE_ENDO_DETERMINANT_REDUCED",
        "CUBIC_DUHAMEL_INSERTION_BOUND_CERTIFIED",
        "GENERIC_NONMINIMAL_GHOST_CPT_REDUCTION_SUPPLIED",
    }
    if any(flags[name] is not True for name in true_flags) or any(
        value is not False for name, value in flags.items() if name not in true_flags
    ):
        raise ValueError("Endo-Duhamel reduction crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale Endo-Duhamel certificate: {OUTPUT}")
    print("GENERIC GHOST ENDO-DUHAMEL REDUCTION: EXACT; INSERTION TRACES OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
