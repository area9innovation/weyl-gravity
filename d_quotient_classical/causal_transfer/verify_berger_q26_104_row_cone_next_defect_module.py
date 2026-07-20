#!/usr/bin/env python3
"""Independent quotient-model replay of the cone next-defect closure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import numpy as np

from d_quotient_classical.causal_transfer import (
    verify_berger_q26_finite_row_module_closure as quotient,
)


ROOT = Path(__file__).resolve().parents[2]
CERT = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_Q26_104_ROW_CONE_NEXT_DEFECT_MODULE_V1.json"
)
PAYLOAD = (
    ROOT
    / "d_quotient_classical/generated/"
    "berger_q26_104_row_cone_next_defect_module_v1/"
    "spin4_next_defect_closure_witness.json"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "berger-q26-104-row-cone-next-defect-module-v1.schema.json"
)
PRIME = 1009
SEED = 26072144


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def _rank(value: np.ndarray) -> int:
    return len(quotient._rref(value)[1])


def replay() -> dict[str, Any]:
    q_record = _load(quotient.Q104)
    q_value = quotient.GRAPH._load_record(q_record, (104, 104))
    evolution = quotient.GRAPH._canonical_symbols(
        quotient.GRAPH._load_hashed_operator(quotient.A104, (104, 104))
    )
    representation = quotient._spin_four_quotient()
    q = quotient._evaluate_matrix(q_value, representation)
    A = quotient._evaluate_matrix(evolution, representation)
    kernel = quotient._nullspace(q)
    left_kernel = quotient._nullspace(q.T)
    right = q @ A % PRIME @ kernel % PRIME
    left = (left_kernel.T @ A % PRIME @ q % PRIME).T
    raw = {
        "q": _rank(q),
        "kernel_q": kernel.shape[1],
        "right_lift_cokernel_image": _rank(right),
        "left_adjoint_cokernel_image": _rank(left),
        "combined_next_defect": _rank(
            np.concatenate([right, left], axis=1)
        ),
    }
    generator = np.random.default_rng(SEED)
    closure = quotient._compress([right, left], generator, 97)
    levels = []
    determinant = 0
    for _ in range(8):
        levels.append(_rank(closure))
        if levels[-1] == 936:
            determinant = quotient._determinant(closure)
            break
        closure = quotient._compress(
            [
                closure,
                q @ closure % PRIME,
                A @ closure % PRIME,
                q.T @ closure % PRIME,
                A.T @ closure % PRIME,
            ],
            generator,
            150,
        )
    return {"raw_ranks": raw, "levels": levels, "determinant": determinant}


def verify() -> dict[str, Any]:
    certificate = _load(CERT)
    payload = _load(PAYLOAD)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    if certificate["exact_payload"]["sha256"] != _sha(PAYLOAD):
        raise AssertionError("next-defect payload hash drifted")
    result = replay()
    if result != {
        "raw_ranks": {
            "q": 351,
            "kernel_q": 585,
            "right_lift_cokernel_image": 27,
            "left_adjoint_cokernel_image": 70,
            "combined_next_defect": 97,
        },
        "levels": [97, 344, 856, 936],
        "determinant": 472,
    }:
        raise AssertionError(f"independent next-defect replay drifted: {result}")
    if payload["closure_levels"][-1][
        "certified_independent_columns"
    ] != 936:
        raise AssertionError("producer next-defect closure is not full")
    flags = certificate["classification"]
    if (
        flags["all_non_cone_104_row_completions_obstructed"]
        or flags["global_minimum_added_rows_raised_above_104"]
        or flags["Hadamard_or_quantum_claim"]
    ):
        raise AssertionError("next-defect result was overpromoted")
    return result


if __name__ == "__main__":
    result = verify()
    print(
        "BERGER_Q26_104_ROW_CONE_NEXT_DEFECT_MODULE_V1: "
        f"VERIFIED (quotient determinant={result['determinant']} mod 1009)"
    )
