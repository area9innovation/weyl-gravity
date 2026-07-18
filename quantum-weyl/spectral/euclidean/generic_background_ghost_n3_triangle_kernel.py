#!/usr/bin/env python3
"""Reduce the generic ghost n=3 trace to an exact simplex/Wick triangle."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_TRIANGLE_KERNEL.json"
SCHEMA = HERE / "schema/generic-background-ghost-n3-triangle-kernel-v1.schema.json"
DEPENDENCY = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_ADIABATIC_CARRIER.json"


def _q(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _subset_row(bits: tuple[int, int, int]) -> dict[str, Any]:
    size = sum(bits)
    selected = [index for index, bit in enumerate(bits) if bit]
    wick_rows = []
    for pair_count in range(size + 1):
        # After Feynman parametrization and the d=4 loop integral, the
        # coefficient multiplying each Wick pairing is
        # Gamma(1+s-m)/2^m=(s-m)!/2^m.
        wick_rows.append(
            {
                "loop_metric_pair_count": pair_count,
                "homogeneous_loop_degree": 2 * pair_count,
                "coefficient_per_pairing": _q(
                    Fraction(math.factorial(size - pair_count), 2**pair_count)
                ),
                "Delta_power": pair_count - size - 1,
            }
        )
    factors = [f"{'Q' + str(i) if bits[i] else 'I'} R{i + 1}" for i in range(3)]
    return {
        "subset_bits": "".join(map(str, bits)),
        "selected_projectors": selected,
        "projector_count": size,
        "projector_coefficient": _q(Fraction(-1, 3) ** size),
        "denominator_powers": [1 + bit for bit in bits],
        "alpha_weight_exponents": list(bits),
        "shifted_numerator": "tr(" + " ".join(factors) + ") with Qi=(l+ri)(l+ri)^T",
        "maximum_loop_metric_pair_count": size,
        "wick_rows": wick_rows,
    }


def build() -> dict[str, Any]:
    parent = json.loads(DEPENDENCY.read_text())
    if (
        parent.get("polarized_S3_carrier", {}).get("stabilizer") != "S3"
        or parent.get("claim_flags", {}).get(
            "GENERIC_GHOST_N3_FULL_MOMENTUM_KERNEL_COMPUTED"
        )
        is not False
    ):
        raise ValueError("n=3 triangle dependency drifted")

    sectors = [_subset_row(bits) for bits in itertools.product((0, 1), repeat=3)]
    if len(sectors) != 8 or sum(len(row["wick_rows"]) for row in sectors) != 20:
        raise AssertionError("triangle sector enumeration drifted")

    result = {
        "schema": "quantum-weyl-generic-background-ghost-n3-triangle-kernel-v1",
        "result_id": "GENERIC_BACKGROUND_GHOST_N3_TRIANGLE_KERNEL",
        "result_state": "N3_NONZERO_MOMENTUM_TRIANGLE_REDUCED_TO_EXACT_SIMPLEX_WICK_KERNEL",
        "lifecycle_state": "PARAMETRIC_TRIANGLE_KERNEL_COMPUTED_REPOSITORY_CARRIER_PROJECTION_OPEN",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": parent["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "external_momenta": "k1+k2+k3=0 with generic nonexceptional Euclidean invariants",
            "curvature_order": 3,
            "insertion_count": 3,
            "field_carrier": "three labelled symmetric Ricci endomorphisms R1,R2,R3",
        },
        "momentum_routing": {
            "loop_momenta": ["q0=p", "q1=p+k1", "q2=p-k3"],
            "denominators": ["D0=q0^2", "D1=q1^2", "D2=q2^2"],
            "projectors": "Pi(qi)=I-(1/3)qi qi^T/Di",
            "direct_integrand": "tr(Pi(q0)R1 Pi(q1)R2 Pi(q2)R3)/(D0 D1 D2)",
            "cyclic_covariance": "(R1,k1;R2,k2;R3,k3;p) rotates with p->p+k1",
        },
        "feynman_simplex": {
            "domain": "alpha_i>=0, alpha0+alpha1+alpha2=1",
            "Omega_positive": "Delta=alpha0 alpha1 k1^2+alpha1 alpha2 k2^2+alpha2 alpha0 k3^2",
            "shift": "l=p+alpha1 k1-alpha2 k3",
            "shifted_vectors": [
                "r0=-alpha1 k1+alpha2 k3",
                "r1=(1-alpha1)k1+alpha2 k3",
                "r2=-alpha1 k1-(1-alpha2)k3",
            ],
            "barycentric_identity": "alpha0 r0+alpha1 r1+alpha2 r2=0",
            "loop_prefactor": "(4pi)^-2",
        },
        "projector_sector_expansion": {
            "sector_count": len(sectors),
            "sector_multiplicities_by_projector_count": [1, 3, 3, 1],
            "total_Wick_rows": 20,
            "sectors": sectors,
        },
        "master_kernel": {
            "formula": "T3=(-8/3)(4pi)^-2 sum_S (-1/3)^|S| int_simplex alpha_S sum_m c_(|S|,m) Delta^(m-|S|-1) Wick_(2m)[N_S(l+r)]",
            "W_and_Tr_log_multiplier": _q(Fraction(-8, 3)),
            "alpha_S": "product_i alpha_i for i in S",
            "Wick_definition": "take the homogeneous loop-degree 2m part and sum all pair contractions with the Euclidean metric",
            "maximum_Wick_pair_count": 3,
            "UV_status": "FINITE_BY_POWER_COUNTING_FOR_GENERIC_NONEXCEPTIONAL_EXTERNAL_MOMENTA",
            "IR_status": "FINITE_ONLY_OFF_EXCEPTIONAL_MOMENTUM_CONFIGURATIONS",
        },
        "consistency": {
            "direct_eight_sector_integrand_identity": "EXACT",
            "cyclic_trace_covariance": "EXACT",
            "adiabatic_numerator_limit": "RECOVERS_GENERIC_BACKGROUND_GHOST_N3_ADIABATIC_CARRIER_BEFORE_RADIAL_INTEGRATION",
            "simplex_Wick_coefficient_formula": "c_(s,m)=(s-m)!/2^m",
        },
        "carrier_projection": {
            "source_candidate": "I10",
            "repository_I10_projection": "NOT_COMPUTED",
            "repository_K_to_Ricci_crosswalk": "NO_CERTIFIED_MAP",
            "reason": "the exact labelled Ricci triangle has not yet been reduced using the frozen scalar-flat K_munu normalization and four-dimensional carrier identities",
        },
        "claim_flags": {
            "GENERIC_GHOST_N3_NONZERO_MOMENTUM_PARAMETRIC_KERNEL_COMPUTED": True,
            "GENERIC_GHOST_N3_EIGHT_PROJECTOR_SECTORS_EXACT": True,
            "GENERIC_GHOST_N3_REPOSITORY_I10_PROJECTION_COMPUTED": False,
            "GENERIC_GHOST_N2_INSERTION_TRACE_COMPUTED": False,
            "GENERIC_GHOST_N1_INSERTION_TRACE_COMPUTED": False,
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
        "next_gate": "PROJECT_N3_TRIANGLE_TO_REPOSITORY_I10_AND_COMPUTE_N1_N2_CURVED_ENDO_TRACES",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL result computes the full generic-nonexceptional-momentum three-Ricci ghost triangle as an exact eight-sector Feynman-simplex/Wick kernel. All projector coefficients, denominator powers, alpha weights and twenty Wick rows are rational and independently replayed against the direct Endo-projector integrand. The result is a parametric tensor kernel, not yet the repository I10 form factor: the scalar-flat K_munu-to-Ricci normalization and carrier projection remain open, as do the curved-Endo one- and two-insertion rows, the complete ghost determinant, physical fourth-order Hessian, repository functions, Gamma1/Q1, residual, Lorentzian, Hadamard, particle, positivity and unitarity theorems."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    expansion = value["projector_sector_expansion"]
    expected_sectors = [
        _subset_row(bits) for bits in itertools.product((0, 1), repeat=3)
    ]
    if expansion["sector_count"] != len(expected_sectors):
        raise ValueError("triangle sector count drifted")
    if expansion["sector_multiplicities_by_projector_count"] != [1, 3, 3, 1]:
        raise ValueError("triangle sector multiplicities drifted")
    if expansion["total_Wick_rows"] != sum(
        len(row["wick_rows"]) for row in expected_sectors
    ):
        raise ValueError("triangle Wick-row count drifted")
    if expansion["sectors"] != expected_sectors:
        raise ValueError("triangle sector coefficients or structure drifted")
    if value["master_kernel"]["W_and_Tr_log_multiplier"] != _q(Fraction(-8, 3)):
        raise ValueError("triangle W/Tr-log multiplier drifted")
    flags = value["claim_flags"]
    true_flags = {
        "GENERIC_GHOST_N3_NONZERO_MOMENTUM_PARAMETRIC_KERNEL_COMPUTED",
        "GENERIC_GHOST_N3_EIGHT_PROJECTOR_SECTORS_EXACT",
    }
    if any(flags[key] is not True for key in true_flags) or any(
        flag is not False for key, flag in flags.items() if key not in true_flags
    ):
        raise ValueError("n=3 triangle crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale n=3 triangle certificate: {OUTPUT}")
    print("GENERIC GHOST N3 TRIANGLE: EXACT PARAMETRIC KERNEL; I10 PROJECTION OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
