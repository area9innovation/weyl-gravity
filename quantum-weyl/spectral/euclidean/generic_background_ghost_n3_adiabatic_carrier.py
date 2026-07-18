#!/usr/bin/env python3
"""Compute the exact adiabatic angular carrier of the three-Ricci ghost trace.

At cubic curvature order, the three-insertion term in ``Tr log(H0+W)`` uses
only the flat Endo inverse

    G0(p) = p^-2 (I - (1/3) n n^T),  n=p/|p|,

and ``W=-2 Ric``.  At zero external momentum the tensor numerator therefore
reduces to an isotropic angular average.  This module computes that average
exactly over Q.  The remaining radial integral is scaleless/IR singular in
this adiabatic limit, so this is a carrier moment rather than the full
momentum-dependent triangle form factor.
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
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_ADIABATIC_CARRIER.json"
SCHEMA = HERE / "schema/generic-background-ghost-n3-adiabatic-carrier-v1.schema.json"
DEPENDENCY = HERE / "certificates/GENERIC_BACKGROUND_GHOST_ENDO_DUHAMEL_REDUCTION.json"


def _q(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, Any]:
    parent = json.loads(DEPENDENCY.read_text())
    if (
        parent.get("exact_Endo_split", {}).get("local_perturbation") != "W=-2 Ric"
        or parent.get("principal_projectors", {}).get("inverse_longitudinal_coefficient")
        != _q(Fraction(2, 3))
        or parent.get("Duhamel_expansion", {}).get(
            "maximum_W_insertions_through_cubic_order"
        )
        != 3
    ):
        raise ValueError("three-insertion dependency drifted")

    dimension = 4
    longitudinal_subtraction = Fraction(1, 3)
    d = Fraction(dimension)
    c = longitudinal_subtraction

    # <tr(P R P R P R)> with P=I-c nn^T.  The invariant basis is
    # (tr R^3, tr R tr R^2, (tr R)^3).
    projector_coefficients = {
        "tr_R3": 1 - 3 * c / d + 6 * c**2 / (d * (d + 2))
        - 8 * c**3 / (d * (d + 2) * (d + 4)),
        "tr_R_tr_R2": 3 * c**2 / (d * (d + 2))
        - 6 * c**3 / (d * (d + 2) * (d + 4)),
        "tr_R_cubed": -c**3 / (d * (d + 2) * (d + 4)),
    }
    expected = {
        "tr_R3": Fraction(503, 648),
        "tr_R_tr_R2": Fraction(11, 864),
        "tr_R_cubed": Fraction(-1, 5184),
    }
    if projector_coefficients != expected:
        raise AssertionError("isotropic Endo projector average drifted")

    # The n=3 logarithm coefficient is +1/3 and W^3=(-2)^3 R^3.
    log_multiplier = Fraction(1, 3) * Fraction(-2) ** 3
    log_coefficients = {
        key: log_multiplier * value for key, value in projector_coefficients.items()
    }
    expected_log = {
        "tr_R3": Fraction(-503, 243),
        "tr_R_tr_R2": Fraction(-11, 324),
        "tr_R_cubed": Fraction(1, 1944),
    }
    if log_coefficients != expected_log:
        raise AssertionError("three-insertion logarithm coefficients drifted")

    result = {
        "schema": "quantum-weyl-generic-background-ghost-n3-adiabatic-carrier-v1",
        "result_id": "GENERIC_BACKGROUND_GHOST_N3_ADIABATIC_CARRIER",
        "result_state": "N3_ZERO_EXTERNAL_MOMENTUM_ANGULAR_NUMERATOR_EXACT_RADIAL_TRIANGLE_OPEN",
        "lifecycle_state": "COEFFICIENT_BEARING_CARRIER_MOMENT_COMPUTED_FULL_FORM_FACTOR_NOT_COMPUTED",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": parent["classical_commit"],
        "scope": {
            "dimension": dimension,
            "signature": "Euclidean",
            "background_carrier": "one-point algebraic symmetric Ricci endomorphism with zero external momentum",
            "curvature_order": 3,
            "insertion_count": 3,
            "mode_scope": "flat Endo principal kernel on nonzero loop momentum",
        },
        "flat_Endo_inverse": {
            "formula": "G0(p)=p^-2(Pi_T+(2/3)Pi_L)=p^-2(I-(1/3)n n^T)",
            "unit_direction": "n=p/|p|",
            "longitudinal_subtraction": _q(c),
            "projector_symbol": "P=I-c n n^T",
        },
        "cyclic_tensor_numerator": {
            "formula": "tr(P R P R P R)=tr(R^3)-3c(n R^3 n)+3c^2(n R n)(n R^2 n)-c^3(n R n)^3",
            "ordered_invariant_basis": ["tr_R3", "tr_R_tr_R2", "tr_R_cubed"],
        },
        "isotropic_moments": {
            "n_R3_n": "tr(R^3)/d",
            "n_R_n_times_n_R2_n": "(tr(R)tr(R^2)+2tr(R^3))/(d(d+2))",
            "n_R_n_cubed": "((tr R)^3+6tr(R)tr(R^2)+8tr(R^3))/(d(d+2)(d+4))",
            "sphere_dimension": dimension - 1,
        },
        "angular_average": {
            "formula": "<tr(P R P R P R)>_S3=sum_i coefficient_i invariant_i",
            "coefficients": {key: _q(value) for key, value in projector_coefficients.items()},
            "scalar_flat_specialization": "(503/648) tr(R^3)",
        },
        "polarized_S3_carrier": {
            "ordered_basis": [
                "sym_tr_R1_R2_R3",
                "sum_tr_R1_tr_R2_R3",
                "tr_R1_tr_R2_tr_R3",
            ],
            "basis_definitions": {
                "sym_tr_R1_R2_R3": "(tr(R1 R2 R3)+tr(R1 R3 R2))/2",
                "sum_tr_R1_tr_R2_R3": "sum_cyclic tr(R1)tr(R2 R3)/3",
                "tr_R1_tr_R2_tr_R3": "tr(R1)tr(R2)tr(R3)",
            },
            "angular_coefficients": {
                "sym_tr_R1_R2_R3": _q(Fraction(503, 648)),
                "sum_tr_R1_tr_R2_R3": _q(Fraction(11, 864)),
                "tr_R1_tr_R2_tr_R3": _q(Fraction(-1, 5184)),
            },
            "Tr_log_coefficients": {
                "sym_tr_R1_R2_R3": _q(Fraction(-503, 243)),
                "sum_tr_R1_tr_R2_R3": _q(Fraction(-11, 324)),
                "tr_R1_tr_R2_tr_R3": _q(Fraction(1, 1944)),
            },
            "stabilizer": "S3",
            "diagonal_restriction": "R1=R2=R3=R reproduces the stored cubic invariant coefficients",
        },
        "three_insertion_log_term": {
            "parent_series_coefficient": _q(Fraction(1, 3)),
            "W_cubic_multiplier": _q(Fraction(-8)),
            "combined_multiplier": _q(log_multiplier),
            "formula": "(1/3)Tr((G0 W)^3)=J3 sum_i coefficient_i invariant_i",
            "coefficients": {key: _q(value) for key, value in log_coefficients.items()},
            "scalar_flat_specialization": "J3*(-503/243) tr(R^3)",
        },
        "radial_and_momentum_status": {
            "adiabatic_radial_kernel": "J3=int d^4p/(2pi)^4 (p^2)^-3",
            "adiabatic_integral_status": "SCALARLESS_AND_IR_SINGULAR_IN_DIMENSIONAL_REGULARIZATION",
            "full_nonzero_external_momentum_triangle": "NOT_COMPUTED",
            "local_counterterm_coefficient": "NOT_INFERRED",
            "reason": "the exact angular numerator does not specify the nonlocal three-point form factor or an IR prescription",
        },
        "carrier_crosswalk": {
            "scalar_flat_algebraic_lineage": "tr(R^3)",
            "candidate_source_carrier": "I10",
            "repository_I10_normalization_map": "NO_CERTIFIED_MAP",
            "reason": "the repository K_munu carrier and the Ricci endomorphism have not yet been related with frozen normalization at nonzero external momentum",
        },
        "claim_flags": {
            "GENERIC_GHOST_N3_ADIABATIC_ANGULAR_CARRIER_COMPUTED": True,
            "GENERIC_GHOST_N3_SCALAR_FLAT_RICCI_CUBIC_COEFFICIENT_COMPUTED": True,
            "GENERIC_GHOST_N3_FULL_MOMENTUM_KERNEL_COMPUTED": False,
            "GENERIC_GHOST_N2_INSERTION_TRACE_COMPUTED": False,
            "GENERIC_GHOST_N1_INSERTION_TRACE_COMPUTED": False,
            "REPOSITORY_I10_NORMALIZATION_MAP_CERTIFIED": False,
            "GENERIC_NONMINIMAL_GHOST_CPT_DETERMINANT_COMPUTED": False,
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependency": {
            "path": str(DEPENDENCY.relative_to(ROOT)),
            "result_id": parent["result_id"],
            "sha256": _sha256(DEPENDENCY),
        },
        "next_gate": "COMPUTE_N3_NONZERO_MOMENTUM_TRIANGLE_AND_N1_N2_CURVED_ENDO_INSERTION_TRACES",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL result evaluates the exact isotropic tensor numerator of the three-Ricci insertion in the flat Endo kernel at zero external momentum. It fixes the rational coefficients 503/648, 11/864 and -1/5184 before W and logarithm factors, and -503/243, -11/324 and 1/1944 in the n=3 Tr-log row. The adiabatic radial integral is scaleless and IR singular in four dimensions, so no nonlocal triangle form factor, local counterterm coefficient, repository I10 normalization, complete ghost determinant, Gamma1/Q1, residual, Lorentzian, Hadamard, particle, positivity or unitarity result is inferred."
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
        "GENERIC_GHOST_N3_ADIABATIC_ANGULAR_CARRIER_COMPUTED",
        "GENERIC_GHOST_N3_SCALAR_FLAT_RICCI_CUBIC_COEFFICIENT_COMPUTED",
    }
    if any(flags[key] is not True for key in true_flags) or any(
        flag is not False for key, flag in flags.items() if key not in true_flags
    ):
        raise ValueError("three-insertion carrier crossed its claim boundary")
    angular = value["angular_average"]["coefficients"]
    logarithm = value["three_insertion_log_term"]["coefficients"]
    if angular != {
        "tr_R3": _q(Fraction(503, 648)),
        "tr_R_tr_R2": _q(Fraction(11, 864)),
        "tr_R_cubed": _q(Fraction(-1, 5184)),
    } or logarithm != {
        "tr_R3": _q(Fraction(-503, 243)),
        "tr_R_tr_R2": _q(Fraction(-11, 324)),
        "tr_R_cubed": _q(Fraction(1, 1944)),
    }:
        raise ValueError("three-insertion rational coefficients drifted")
    polarized = value["polarized_S3_carrier"]
    if polarized["angular_coefficients"] != {
        "sym_tr_R1_R2_R3": _q(Fraction(503, 648)),
        "sum_tr_R1_tr_R2_R3": _q(Fraction(11, 864)),
        "tr_R1_tr_R2_tr_R3": _q(Fraction(-1, 5184)),
    } or polarized["Tr_log_coefficients"] != {
        "sym_tr_R1_R2_R3": _q(Fraction(-503, 243)),
        "sum_tr_R1_tr_R2_R3": _q(Fraction(-11, 324)),
        "tr_R1_tr_R2_tr_R3": _q(Fraction(1, 1944)),
    }:
        raise ValueError("three-insertion polarized carrier drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale three-insertion carrier certificate: {OUTPUT}")
    print("GENERIC GHOST N3 ADIABATIC CARRIER: EXACT; FULL TRIANGLE OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
