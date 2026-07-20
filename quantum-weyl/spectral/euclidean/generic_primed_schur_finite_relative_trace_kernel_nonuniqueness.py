#!/usr/bin/env python3
"""Exact nonuniqueness theorem for the generic finite Schur trace kernel."""

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
OUTPUT = (
    HERE
    / "certificates/"
    "GENERIC_PRIMED_SCHUR_FINITE_RELATIVE_TRACE_KERNEL_NONUNIQUENESS.json"
)
SCHEMA = (
    HERE
    / "schema/"
    "generic-primed-schur-finite-relative-trace-kernel-nonuniqueness-v1.schema.json"
)
ASSEMBLY = (
    HERE
    / "certificates/PARITY_EVEN_THIRD_CURVATURE_FIVE_FORM_FACTOR_ASSEMBLY.json"
)
ASSEMBLY_HASH = "c474dedff8923233d94998e04e044c5931f03df69fcbf973c650d665f7246f06"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _reference(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": payload["result_id"],
        "sha256": _sha256(path),
    }


def build() -> dict[str, Any]:
    if _sha256(ASSEMBLY) != ASSEMBLY_HASH:
        raise ValueError("five-form-factor assembly hash drifted")
    assembly = json.loads(ASSEMBLY.read_text())
    if (
        assembly["claim_flags"]["MAXIMAL_PARTIAL_BV_QUOTIENT_COMPUTED"] is not True
        or assembly["claim_flags"][
            "GENERIC_SCHUR_REFERENCE_FINITE_ROWS_COMPUTED"
        ]
        is not False
        or assembly["first_missing_analytic_datum"]["datum_id"]
        != "GENERIC_PRIMED_SCHUR_FINITE_RELATIVE_TRACE_KERNEL"
    ):
        raise ValueError("Schur receiver activation gate drifted")

    k = Fraction(1, 2)
    t = Fraction(7, 11)
    finite_rk_shift = t
    finite_rk2_shift = 2 * k * t + t * t
    det3_rational_shift = -t + k * t + t * t / 2
    if (
        finite_rk_shift != Fraction(7, 11)
        or finite_rk2_shift != Fraction(126, 121)
        or det3_rational_shift != Fraction(-14, 121)
    ):
        raise ValueError("finite smoothing witness arithmetic failed")

    cubic_amplitude = Fraction(3, 2)
    cubic_rk = cubic_amplitude
    cubic_rk2 = 2 * k * cubic_amplitude
    cubic_det3 = (Fraction(1, 1) / (1 + k) - 1 + k) * cubic_amplitude
    cubic_full = cubic_rk - cubic_rk2 / 2 + cubic_det3
    if (
        cubic_rk != Fraction(3, 2)
        or cubic_rk2 != Fraction(3, 2)
        or cubic_det3 != Fraction(1, 4)
        or cubic_full != 1
    ):
        raise ValueError("cubic finite-row witness arithmetic failed")

    return {
        "schema": (
            "quantum-weyl-generic-primed-schur-finite-relative-"
            "trace-kernel-nonuniqueness-v1"
        ),
        "result_id": (
            "GENERIC_PRIMED_SCHUR_FINITE_RELATIVE_TRACE_KERNEL_NONUNIQUENESS"
        ),
        "result_state": (
            "BACKGROUND_UNIVERSAL_FINITE_KERNEL_NONUNIQUE_"
            "MINIMAL_GLOBAL_SPECTRAL_INPUT_IDENTIFIED"
        ),
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": assembly["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "background_class": (
                "closed scalar-flat metrics with a declared compact global "
                "completion and primed scalar/vector domains"
            ),
            "operator_class": (
                "self-adjoint classical order-zero S=I+K with K of order -2, "
                "fixed complete polyhomogeneous symbol modulo smoothing"
            ),
            "subtraction": assembly["scope"]["subtraction"],
        },
        "declared_complete_kernel_class": {
            "fixed_data": [
                "complete local polyhomogeneous symbol of S_L(W)",
                "all Wodzicki residues and their local scale density",
                "primed zero-mode projector Pi_0",
                "positive elliptic weight Q_mu=(Delta_0+Pi_0)/mu^2",
                "common Mellin/proper-time subtraction prescription",
            ],
            "allowed_completion_difference": (
                "self-adjoint smoothing family supported entirely on the "
                "primed complement and small enough to preserve invertibility"
            ),
            "equivalence_question": (
                "whether the fixed local and subtraction data determine the "
                "reference finite trace rows modulo that completion class"
            ),
        },
        "rank_one_finite_value_witness": {
            "primed_unit_vector": "e with Pi_0 e=0 and Qe=q e, q>0",
            "base_action": "K e=(1/2)e",
            "smoothing_perturbation": "T=(7/11)|e><e|",
            "zero_mode_action": "T vanishes on ker(Delta_0)",
            "invertibility": {
                "base_S_eigenvalue": _q(1 + k),
                "perturbed_S_eigenvalue": _q(1 + k + t),
                "status": "POSITIVE",
            },
            "finite_trace_shifts": {
                "Delta_R_mu0_K": _q(finite_rk_shift),
                "Delta_FP_R_mu0_K2": _q(finite_rk2_shift),
                "Delta_log_det3": "log(47/33)-14/121",
                "Delta_log_Det_3_R": "log(47/33)",
            },
            "nonzero_proof": (
                "47/33>1, hence log(47/33)>0; moreover "
                "log(47/33)>14/47>14/121, so both determinant shifts are nonzero"
            ),
        },
        "third_curvature_row_witness": {
            "family": "T(u1,u2,u3)=(3/2)u1*u2*u3 |e><e|",
            "properties": [
                "T and its first and second derivatives vanish at u=0",
                "the complete symbol and every residue agree for all u",
                "T acts only on the fixed primed complement",
                "S+T remains invertible in a neighborhood of u=0",
            ],
            "mixed_third_variation_shifts": {
                "Delta_d123_R_mu0_K": _q(cubic_rk),
                "Delta_d123_FP_R_mu0_K2": _q(cubic_rk2),
                "Delta_d123_log_det3": _q(cubic_det3),
                "Delta_d123_log_Det_3_R": _q(cubic_full),
            },
            "carrier_consequence": (
                "multiplying the smoothing amplitude by any selected nonzero "
                "linear functional on the certified ten-dimensional labelled "
                "carrier quotient changes that finite third-curvature row "
                "without changing the imported local symbol, scale derivative, "
                "zero modes or subtraction data"
            ),
        },
        "invariance_ledger": {
            "complete_symbol": "UNCHANGED_SMOOTHING_HAS_SYMBOL_ZERO",
            "Wodzicki_residues": "UNCHANGED_RESIDUE_VANISHES_ON_SMOOTHING",
            "scale_derivative": "UNCHANGED",
            "zero_mode_projector": "UNCHANGED_P_T_EQUALS_ZERO",
            "subtraction_scheme": "UNCHANGED",
            "reference_finite_rows": "CHANGED",
            "third_curvature_finite_row": "CHANGED",
        },
        "special_background_holdouts": {
            "round_S4": "PINNED_BUT_NOT_INTERPOLATED",
            "product_S2_S2": "PINNED_BUT_NOT_INTERPOLATED",
            "consequence": (
                "two isolated spectra do not select a generic smoothing "
                "completion or a background-universal finite kernel"
            ),
        },
        "minimal_additional_global_input": {
            "status": "REQUIRED",
            "data": [
                "content-addressed compact global scalar-flat metric and orientation",
                "complete scalar and vector bundle domains and boundary conditions",
                "primed zero-mode projectors with normalization",
                "the global primed resolvent kernel of F+W and scalar weight Q",
                "or an equivalent complete spectral measure with eigenprojectors",
                "the reference scale mu_0 and common determinant phase/contour policy",
            ],
            "sufficiency": (
                "these data select the unique global Green/resolvent and make "
                "R_mu0(K), FP R_mu0(K^2), det_3(I+K) and their metric "
                "variations well-defined for that background"
            ),
            "not_supplied_by": [
                "local jets or complete symbols",
                "Wodzicki residues or scale response",
                "round-S4 and S2xS2 special-background values",
                "the full-BV multiplicity ledger alone",
            ],
        },
        "decision": {
            "background_universal_finite_kernel_from_declared_local_data": (
                "NONUNIQUE"
            ),
            "generic_reference_finite_rows": "PARAMETERIZED_BY_GLOBAL_SPECTRAL_DATA",
            "complete_generic_BV_five_form_factors": "NOT_COMPUTED",
            "predecessor_maximal_partial_BV_quotient": "UNCHANGED",
        },
        "dependency": _reference(ASSEMBLY, assembly),
        "claim_flags": {
            "EXACT_FINITE_KERNEL_NONUNIQUENESS_PROVED": True,
            "EXACT_THIRD_CURVATURE_ROW_NONUNIQUENESS_PROVED": True,
            "SYMBOL_RESIDUE_ZERO_MODE_AND_SUBTRACTION_PRESERVED": True,
            "MINIMAL_GLOBAL_SPECTRAL_INPUT_IDENTIFIED": True,
            "SPECIAL_BACKGROUND_INTERPOLATION_USED": False,
            "BACKGROUND_UNIVERSAL_FINITE_KERNEL_CONSTRUCTED": False,
            "COMPLETE_GENERIC_BV_FIVE_FORM_FACTORS_COMPUTED": False,
            "QME_OR_LORENTZIAN_PROMOTED": False,
        },
        "next_gate": (
            "choose one content-addressed global scalar-flat background and "
            "supply its primed resolvent or complete spectral measure before "
            "computing background-specific finite Schur variations"
        ),
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL theorem proves that the "
            "declared local Schur operator data, all residues, priming and "
            "subtraction scheme do not determine a background-universal finite "
            "relative-trace kernel. Exact rank-one smoothing witnesses change "
            "both the finite determinant and a selected cubic carrier row while "
            "preserving every declared local datum. The result identifies the "
            "minimal missing global spectral input. It does not compute a "
            "background-specific generic kernel, complete the full-BV five "
            "functions, supply Gamma1/Q1, decide a QME, or establish any "
            "Lorentzian, Hadamard, state, particle, scattering or unitarity claim."
        ),
    }


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale Schur nonuniqueness certificate: {OUTPUT}")
    print("GENERIC PRIMED SCHUR FINITE KERNEL NONUNIQUENESS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
