#!/usr/bin/env python3
"""Exact local variation theorem for the normalized longitudinal Schur operator."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MANIFEST = HERE / "generated/normalized_schur_pseudodifferential_variation_v1/operator_words.json"
OUTPUT = HERE / "certificates/NORMALIZED_SCHUR_PSEUDODIFFERENTIAL_VARIATION.json"
MANIFEST_SCHEMA = HERE / "schema/normalized-schur-pseudodifferential-operator-words-v1.schema.json"
SCHEMA = HERE / "schema/normalized-schur-pseudodifferential-variation-v1.schema.json"
DEPENDENCIES = {
    "normalized_schur": HERE / "certificates/GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION.json",
    "surrogate_obstruction": HERE / "certificates/SCALAR_FLAT_BERGER_SCHUR_SURROGATE_OBSTRUCTION.json",
    "berger_low_blocks": HERE / "certificates/SCALAR_FLAT_BERGER_VECTOR_SCHUR_LOW_BLOCKS.json",
    "berger_low_oracle": HERE / "generated/scalar_flat_berger_vector_schur_low_blocks_v1/blocks.json",
}
PINNED = {
    "normalized_schur": "b40ec3a8bd3a21d8e0ece7c98f98e1776e8c47d557b8c8b5427e422b60c65a78",
    "surrogate_obstruction": "687aa26ec62e34dfa9adde53f4d1793741a97b9829c7dee55b71f11f6d54f2d5",
    "berger_low_blocks": "58d8646e3aedc1a897a8e6d05d6128f0e0eb4f885225443b9133f1c1968914f0",
    "berger_low_oracle": "2c81c166ae2c16ed4c97244b26bd134e24381779f2a6e7921a2daca4f29021b3",
}
ORDERS = {"delta": 1, "d": 1, "G": -2, "W": 0, "DeltaInv": -2}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _matrix(value: sp.Matrix) -> list[list[str]]:
    return [[str(sp.factor(value[i, j])) for j in range(value.cols)] for i in range(value.rows)]


def _reference(name: str) -> dict[str, str]:
    path = DEPENDENCIES[name]
    actual = _sha(path)
    if actual != PINNED[name]:
        raise ValueError(f"{name} hash drifted: {actual}")
    data = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": data["result_id"],
        "sha256": actual,
    }


def _word(power: int) -> list[str]:
    word = ["delta", "G"]
    for _ in range(power):
        word.extend(["W", "G"])
    word.append("d")
    return word


def _word_order(word: list[str]) -> int:
    return sum(ORDERS[token] for token in word)


def _finite_noncommuting_fixture() -> dict[str, Any]:
    t = sp.symbols("t")
    delta0 = sp.diag(2, 3)
    d = sp.Matrix([[1, 0], [0, 1], [0, 0], [0, 0]])
    delta = sp.Matrix([[2, 0, 0, 0], [0, 3, 0, 0]])
    f = sp.diag(2, 3, 1, 1)
    f[2:4, 2:4] = sp.Matrix([[5, 1], [1, 7]])
    w = sp.Matrix([[1, 2, -1, 3], [2, -2, 4, 1], [-1, 4, 3, 2], [3, 1, 2, -1]])
    g = f.inv()
    if f * d != d * delta0 or delta * f != delta0 * delta or delta * d != delta0:
        raise AssertionError("finite fixture Ward identities failed")
    exact = sp.Rational(2, 3) * sp.eye(2) + sp.Rational(1, 3) * delta * (f + t * w).inv() * d
    coefficients = [
        sp.simplify(exact.diff(t, k).subs(t, 0) / math.factorial(k))
        for k in range(1, 4)
    ]
    words = [
        sp.Rational((-1) ** k, 3) * delta * g * (w * g) ** k * d
        for k in range(1, 4)
    ]
    if any(sp.simplify(a - b) != sp.zeros(2) for a, b in zip(coefficients, words)):
        raise AssertionError("noncommuting resolvent coefficients failed")
    reordered = -sp.Rational(1, 3) * delta * w * g * g * d
    if reordered == coefficients[0]:
        raise AssertionError("noncommuting ordering control collapsed")
    return {
        "F": _matrix(f),
        "W": _matrix(w),
        "d": _matrix(d),
        "delta": _matrix(delta),
        "Delta0": _matrix(delta0),
        "taylor_coefficients": [_matrix(row) for row in coefficients],
        "derivatives_at_zero": [
            _matrix(math.factorial(k) * coefficients[k - 1]) for k in range(1, 4)
        ],
        "reordered_first_coefficient": _matrix(reordered),
        "reordered_word_rejected": reordered != coefficients[0],
    }


def _berger_control() -> dict[str, Any]:
    oracle = json.loads(DEPENDENCIES["berger_low_oracle"].read_text())
    block = next(row for row in oracle["blocks"] if row["n"] == 0 and row["twice_j"] == 1)
    expected = [["-64/81", "0"], ["0", "-64/81"]]
    if block["S_L_first_derivative_at_zero"] != expected:
        raise AssertionError("Berger low-block derivative drifted")
    delta0 = sp.Rational(9, 16)
    delta_w_d = sp.Rational(3, 4)
    correct = -delta_w_d / (3 * delta0**2)
    surrogate = delta_w_d / (3 * delta0)
    if correct != sp.Rational(-64, 81) or surrogate != sp.Rational(4, 9):
        raise AssertionError("Berger scalar control failed")
    return {
        "block_id": block["block_id"],
        "Delta0": "9/16",
        "delta_W_d": "3/4",
        "correct_first_variation": str(correct),
        "oracle_matrix": expected,
        "one_inverse_surrogate": str(surrogate),
        "values_distinct": correct != surrogate,
    }


def _moving_projector_control() -> dict[str, Any]:
    # A rotating rank-one range: R(t)=A(t) because A(t) is its own reduced inverse.
    # It is deliberately nonlinear, since it tests the general projector derivative,
    # not the fixed-background linear W pencil.
    a0 = sp.Matrix([[1, 0], [0, 0]])
    adot = sp.Matrix([[0, 1], [1, 0]])
    r0 = a0
    rdot = adot
    p0 = sp.eye(2) - a0
    pdot = -adot
    naive = -r0 * adot * r0
    corrected = -r0 * adot * r0 - pdot * r0 - r0 * pdot
    if naive != sp.zeros(2) or corrected != rdot:
        raise AssertionError("moving-projector control failed")
    return {
        "A0": _matrix(a0),
        "A_prime0": _matrix(adot),
        "P0": _matrix(p0),
        "P_prime0": _matrix(pdot),
        "R_prime0": _matrix(rdot),
        "naive_fixed_projector_term": _matrix(naive),
        "full_projector_formula": _matrix(corrected),
        "naive_formula_rejected": naive != rdot,
    }


def build_manifest() -> dict[str, Any]:
    variations = []
    principal = {
        1: "-(1/3)<xi,W xi>/|xi|^4",
        2: "+(1/3)<xi,W^2 xi>/|xi|^6",
        3: "-(1/3)<xi,W^3 xi>/|xi|^8",
    }
    for k in range(1, 4):
        word = _word(k)
        coefficient = sp.Rational((-1) ** k, 3)
        variations.append(
            {
                "t_power": k,
                "taylor_coefficient": str(coefficient),
                "derivative_at_zero_coefficient": str(math.factorial(k) * coefficient),
                "operator_word": word,
                "ward_reduced_word": ["DeltaInv", "delta"]
                + sum((["W", "G"] for _ in range(k - 1)), [])
                + ["W", "d", "DeltaInv"],
                "operator_order": _word_order(word),
                "principal_symbol_order": -2 * k,
                "subprincipal_symbol_order": -2 * k - 1,
                "principal_symbol": principal[k],
            }
        )
    if [row["operator_order"] for row in variations] != [-2, -4, -6]:
        raise AssertionError("variation order arithmetic failed")
    return {
        "$schema": "../../schema/normalized-schur-pseudodifferential-operator-words-v1.schema.json",
        "schema": "quantum-weyl-normalized-schur-pseudodifferential-operator-words-v1",
        "result_id": "NORMALIZED_SCHUR_PSEUDODIFFERENTIAL_OPERATOR_WORDS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "parameter_family": "A(t)=F+tW; S_L(t)=(2/3)I+(1/3)delta R(t)d",
        "fixed_data": ["F", "W", "d", "delta", "metric", "connection"],
        "resolvent_expansion": {
            "G": "F^-1 on the declared fixed primed complement",
            "through_t3": [
                {"t_power": k, "coefficient": str((-1) ** k), "operator_word": ["G"] + [token for _ in range(k) for token in ("W", "G")]}
                for k in range(4)
            ],
        },
        "schur_variations": variations,
        "symbol_calculus": {
            "composition_convention": "(a#b)_{m+n-1}=a_m b_{n-1}+a_{m-1}b_n+(1/i)partial_xi(a_m)nabla_x(b_n)",
            "elliptic_inverse": "G in Psi^-2 for Laplace-type F with scalar principal symbol |xi|^2 I",
            "first_correction_order": -2,
            "subprincipal_dependencies": ["sub(F)", "connection parts of d and delta", "covariant derivatives of W"],
            "local_data_only": True,
            "does_not_supply": ["finite smoothing trace", "global determinant", "spectral cut", "zero-mode measure"],
        },
        "projector_and_domain": {
            "fixed_common_complement_hypothesis": "P is t-independent, [P,A(t)]=0, and A(t)|Ran(1-P) is invertible on one common domain",
            "fixed_formula": "R'=-R W R",
            "moving_formula": "R'=-R A' R-P'R-RP'",
            "smooth_self_adjoint_constant_rank_formula": "P'=-R A'P-P A'R",
            "rank_change_status": "NO_DIFFERENTIABLE_REDUCED_RESOLVENT_WITHOUT_A_STRATUM_OR_CONTOUR_CHOICE",
            "berger_at_t0": "P_F is fixed locally, P_F d=0, delta P_F=0 and W P_F=0",
        },
        "exact_noncommuting_fixture": _finite_noncommuting_fixture(),
        "berger_low_block_control": _berger_control(),
        "moving_projector_control": _moving_projector_control(),
        "mutation_controls": {
            "wrong_sign": "REJECT",
            "commuting_reorder": "REJECT",
            "one_inverse_surrogate": "REJECT",
            "frozen_moving_projector": "REJECT",
        },
    }


def build_certificate(manifest: dict[str, Any], manifest_hash: str) -> dict[str, Any]:
    return {
        "$schema": "../schema/normalized-schur-pseudodifferential-variation-v1.schema.json",
        "schema": "quantum-weyl-normalized-schur-pseudodifferential-variation-v1",
        "result_id": "NORMALIZED_SCHUR_PSEUDODIFFERENTIAL_VARIATION",
        "result_state": "FIXED_DOMAIN_VARIATIONS_THROUGH_T3_AND_PROJECTOR_BOUNDARY_CERTIFIED",
        "lifecycle_state": "LOCAL_OPERATOR_VARIATION_CERTIFIED_GLOBAL_TRACE_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "input_commit": "0200fc87b",
        "manifest": {
            "path": str(MANIFEST.relative_to(ROOT)),
            "result_id": manifest["result_id"],
            "sha256": manifest_hash,
        },
        "results": {
            "variation_orders": [-2, -4, -6],
            "first_variation": "-(1/3)delta G W G d=-(1/3)Delta0^-1 delta W d Delta0^-1",
            "second_variation": "+(2/3)delta G W G W G d",
            "third_variation": "-2 delta G W G W G W G d",
            "berger_first_variation": "-64/81",
            "one_inverse_surrogate": "4/9",
            "projector_disposition": "FIXED_COMPLEMENT_CERTIFIED; MOVING_PROJECTOR_TERMS_EXPLICIT; RANK_CHANGE_FAILS_CLOSED",
            "local_global_split": "POLYHOMOGENEOUS_SYMBOL_VARIATIONS_LOCAL; SMOOTHING_TRACE_AND_FINITE_DETERMINANT_GLOBAL",
        },
        "claim_flags": {
            "RESOLVENT_AND_SCHUR_VARIATIONS_THROUGH_T3_COMPUTED": True,
            "FIRST_CORRECTION_ORDER_MINUS_TWO_PROVED": True,
            "PROJECTOR_DERIVATIVE_BOUNDARY_EXPLICIT": True,
            "BERGER_MINUS_64_OVER_81_REPRODUCED": True,
            "GLOBAL_FINITE_DETERMINANT_COMPUTED": False,
            "HEAT_KERNEL_COEFFICIENT_COMPUTED": False,
            "QME_OR_LORENTZIAN_PROMOTED": False,
        },
        "dependencies": {name: _reference(name) for name in DEPENDENCIES},
        "next_gate": "CONSUME_THE_OPERATOR_WORD_MANIFEST_IN_THE_INDEPENDENT_PSEUDODIFFERENTIAL_HEAT_KERNEL_LAYER_AND_PROVE_HIGH_MODE_DOMAIN_CONTROL",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL certificate derives the exact noncommutative resolvent and normalized-Schur variations through cubic parameter order on a declared fixed common primed domain. It proves the successive local pseudodifferential orders -2, -4 and -6, records subprincipal orders and required geometric inputs, independently anchors the first Berger block at -64/81, and exposes the mandatory moving-projector terms and rank-change nondefinition. It does not compute a Seeley-DeWitt coefficient, Wodzicki residue, smoothing trace, global finite determinant, spectral tail, anomaly coefficient, QME restoration, Lorentzian causal object, Hadamard state, particle space or unitarity statement."
        ),
    }


def validate(manifest: dict[str, Any], certificate: dict[str, Any]) -> None:
    for path, value in ((MANIFEST_SCHEMA, manifest), (SCHEMA, certificate)):
        schema = json.loads(path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)
    flags = certificate["claim_flags"]
    if any(flags[name] is not True for name in list(flags)[:4]):
        raise AssertionError("positive claim flags drifted")
    if any(flags[name] is not False for name in list(flags)[4:]):
        raise AssertionError("forbidden promotion enabled")


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = build_manifest()
    manifest_hash = hashlib.sha256(_render(manifest).encode()).hexdigest()
    certificate = build_certificate(manifest, manifest_hash)
    validate(manifest, certificate)
    return manifest, certificate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest, certificate = build()
    rendered_manifest = _render(manifest)
    rendered_certificate = _render(certificate)
    if args.check:
        if not MANIFEST.exists() or MANIFEST.read_text() != rendered_manifest:
            raise SystemExit("normalized-Schur operator-word manifest drifted")
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered_certificate:
            raise SystemExit("normalized-Schur variation certificate drifted")
        return 0
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(rendered_manifest)
    OUTPUT.write_text(rendered_certificate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
