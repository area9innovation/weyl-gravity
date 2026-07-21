#!/usr/bin/env python3
"""Certify the first high-mode trace-majorant obstruction on scalar-flat Berger."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = (
    HERE
    / "certificates/SCALAR_FLAT_BERGER_VECTOR_SCHUR_HIGH_MODE_TRACE_MAJORANT_OBSTRUCTION_V1.json"
)
SCHEMA = HERE / "schema/scalar-flat-berger-vector-schur-high-mode-trace-majorant-obstruction-v1.schema.json"
DEPENDENCIES = {
    "low_blocks": HERE / "certificates/SCALAR_FLAT_BERGER_VECTOR_SCHUR_LOW_BLOCKS.json",
    "low_oracle": HERE / "generated/scalar_flat_berger_vector_schur_low_blocks_v1/blocks.json",
    "variation": HERE / "certificates/NORMALIZED_SCHUR_PSEUDODIFFERENTIAL_VARIATION.json",
    "variation_manifest": HERE / "generated/normalized_schur_pseudodifferential_variation_v1/operator_words.json",
}
PINNED = {
    "low_blocks": "58d8646e3aedc1a897a8e6d05d6128f0e0eb4f885225443b9133f1c1968914f0",
    "low_oracle": "2c81c166ae2c16ed4c97244b26bd134e24381779f2a6e7921a2daca4f29021b3",
    "variation": "5e437f7feed2044fd4ab7254388556536e41bf74a874398ece47f1d8b88f4a95",
    "variation_manifest": "837da72d4d358109cdcd5ecfeddbcc974ca6aa9ad04796cc6ef629870b8388d6",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(name: str) -> dict[str, str]:
    path = DEPENDENCIES[name]
    actual = _sha256(path)
    if actual != PINNED[name]:
        raise ValueError(f"{name} hash drifted: {actual}")
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": value["result_id"],
        "sha256": actual,
    }


def _weights(twice_j: int) -> list[sp.Rational]:
    return [sp.Rational(twice_j - 2 * row, 2) for row in range(twice_j + 1)]


def scalar_eigenvalue(n: int, j: sp.Rational, m: sp.Rational) -> sp.Rational:
    return sp.factor(n * n + j * (j + 1) - sp.Rational(3, 4) * m * m)


def insertion_numerator(j: sp.Rational, m: sp.Rational) -> sp.Rational:
    return sp.factor(2 * j * (j + 1) - 3 * m * m)


def first_insertion(n: int, j: sp.Rational, m: sp.Rational) -> sp.Rational:
    q = scalar_eigenvalue(n, j, m)
    if q == 0:
        raise ValueError("the scalar constant is primed and has no insertion eigenvalue")
    return sp.factor(-insertion_numerator(j, m) / (3 * q * q))


def _central_weights(twice_j: int) -> list[sp.Rational]:
    j = sp.Rational(twice_j, 2)
    return [m for m in _weights(twice_j) if abs(m) <= j / 2]


def _shell_witness(twice_j: int) -> dict[str, Any]:
    j = sp.Rational(twice_j, 2)
    central = _central_weights(twice_j)
    contribution = sp.factor(
        (twice_j + 1) * sum(abs(first_insertion(0, j, m)) for m in central)
    )
    return {
        "twice_j": twice_j,
        "j": str(j),
        "central_weight_count": len(central),
        "central_weights": [str(m) for m in central],
        "absolute_shell_contribution": str(contribution),
        "minus_uniform_lower_bound": str(sp.factor(contribution - sp.Rational(5, 48))),
    }


def build() -> dict[str, Any]:
    low = json.loads(DEPENDENCIES["low_blocks"].read_text())
    variation = json.loads(DEPENDENCIES["variation"].read_text())
    if low["claim_flags"]["LOW_VECTOR_SCHUR_BLOCKS_COMPUTED"] is not True:
        raise ValueError("terminal low-block theorem is not active")
    if variation["results"]["variation_orders"] != [-2, -4, -6]:
        raise ValueError("normalized Schur insertion orders drifted")

    certificate = {
        "$schema": "../schema/scalar-flat-berger-vector-schur-high-mode-trace-majorant-obstruction-v1.schema.json",
        "schema": "quantum-weyl-scalar-flat-berger-vector-schur-high-mode-trace-majorant-obstruction-v1",
        "result_id": "SCALAR_FLAT_BERGER_VECTOR_SCHUR_HIGH_MODE_TRACE_MAJORANT_OBSTRUCTION_V1",
        "result_state": "FIRST_INSERTION_ABSOLUTE_TRACE_MAJORANT_OBSTRUCTED",
        "lifecycle_state": "EXACT_TAIL_OBSTRUCTION_COMPLETE_COERCIVITY_PREFLIGHT_NOT_ACTIVATED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "input_commit": "0200fc87b",
        "dependencies": {name: _reference(name) for name in DEPENDENCIES},
        "import_gate": {
            "unique_pencil": "A(t)=F+tW with F=nabla^*nabla+Ric and W=-2 Ric",
            "normalization": "orthonormal coframe (dtheta,sigma1,sigma2,2sigma3), normalized product Haar measure, delta=d^dagger",
            "status": "PASS",
        },
        "first_insertion": {
            "operator": "B1=-(1/3) Delta0^-1 delta W d Delta0^-1",
            "mode_family": "n=0; j in (1/2)Z with j>=1; m=-j,-j+1,...,j",
            "scalar_laplacian_eigenvalue": "q_jm=j*(j+1)-(3/4)*m^2",
            "delta_W_d_eigenvalue": "p_jm=2*j*(j+1)-3*m^2",
            "first_insertion_eigenvalue": "b1_jm=-p_jm/(3*q_jm^2)",
            "left_multiplicity": "2*j+1",
            "central_band": "abs(m)<=j/2",
        },
        "exact_lower_bound_proof": {
            "range": "j>=1 and abs(m)<=j/2",
            "scalar_positivity": "q_jm>=j^2/4+j>0",
            "numerator_decomposition": "p_jm-(5/4)j^2=2j+3*(j^2/4-m^2)>=0",
            "denominator_decomposition": "2j^2-q_jm=j*(j-1)+(3/4)m^2>=0",
            "per_weight_bound": "abs(b1_jm)>=5/(48*j^2)",
            "central_weight_count_bound": "#{m:abs(m)<=j/2}>=j/2",
            "central_weight_count_formula": "for N=2j: floor(3N/4)-ceil(N/4)+1>=N/4, checked by N mod 4",
            "left_multiplicity_bound": "2*j+1>=2*j",
            "uniform_shell_lower_bound": "(2*j+1)*sum_central abs(b1_jm)>=5/48",
            "series_conclusion": "sum_{j>=1}(2*j+1)*sum_m abs(b1_jm) diverges by comparison with sum_{j>=1} 5/48",
        },
        "exact_shell_witnesses": [_shell_witness(twice_j) for twice_j in range(2, 17)],
        "trace_ideal_disposition": {
            "first_insertion_order": -2,
            "first_insertion_absolute_trace_majorant": "DOES_NOT_EXIST",
            "second_insertion_order": -4,
            "second_insertion_absolute_trace_majorant": "NOT_DECIDED_HERE",
            "third_insertion_order": -6,
            "third_insertion_absolute_trace_majorant": "NOT_DECIDED_HERE",
            "requested_three_summable_majorants": "OBSTRUCTED_AT_FIRST_INSERTION",
            "required_repair": "retain a declared regulator/subtraction for B1 and the finite part of B2; only the trace-class tail may use an ordinary absolute trace",
        },
        "claim_flags": {
            "LOW_BLOCK_PENCIL_AND_NORMALIZATION_IMPORTED": True,
            "FIRST_INSERTION_EXACT_MODE_FORMULA_VERIFIED": True,
            "FIRST_INSERTION_SUMMABLE_MAJORANT_OBSTRUCTED": True,
            "COMPLETE_HIGH_MODE_COERCIVITY_PREFLIGHT_COMPUTED": False,
            "FINITE_EXCEPTIONAL_BLOCK_SET_CLASSIFIED": False,
            "GLOBAL_DETERMINANT_OR_FINITE_TRACE_COMPUTED": False,
            "ANOMALY_COEFFICIENT_OR_QME_COMPUTED": False,
            "LORENTZIAN_OR_HADAMARD_PROMOTED": False,
        },
        "next_gate": "RESTATE_THE_GLOBAL_TAIL_GATE_AS_REGULATED_B1_PLUS_FINITE_PART_B2_PLUS_TRACE_CLASS_B3_TAIL_BEFORE_REQUESTING_A_COMPLETE_COERCIVITY_PREFLIGHT",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL certificate imports the unique normalized scalar-flat Berger vector Schur pencil and proves an exact high-mode obstruction to the requested ordinary summable majorant for the first metric insertion. The n=0 central-weight family alone has a uniform positive absolute shell contribution, so B1 is not trace class and cannot be assigned an ordinary absolutely convergent trace. This is the first exact failure of the requested three-majorant preflight. It does not disprove high-mode invertibility of A(t), classify the finite exceptional blocks, compute a regulated B1 value or finite B2 part, construct a global determinant, determine an anomaly coefficient or QME, or establish Lorentzian, Hadamard, state, particle, positivity, scattering or unitarity claims."
        ),
    }
    validate(certificate)
    return certificate


def validate(certificate: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    flags = certificate["claim_flags"]
    true_flags = {
        "LOW_BLOCK_PENCIL_AND_NORMALIZATION_IMPORTED",
        "FIRST_INSERTION_EXACT_MODE_FORMULA_VERIFIED",
        "FIRST_INSERTION_SUMMABLE_MAJORANT_OBSTRUCTED",
    }
    for name, value in flags.items():
        if value is not (name in true_flags):
            raise ValueError(f"claim-boundary drift at {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate = build()
    rendered = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale high-mode obstruction certificate: {OUTPUT}")
    print("SCALAR-FLAT BERGER VECTOR SCHUR HIGH-MODE TRACE MAJORANT: OBSTRUCTED AT B1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
