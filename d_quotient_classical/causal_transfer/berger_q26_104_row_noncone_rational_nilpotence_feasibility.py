#!/usr/bin/env python3
"""Construct an exact rational non-cone nilpotence feasibility witness.

This is a multiplicative trivial-Berger specialization, not a PBW operator
completion.  It keeps every old-old q_Cauchy degree block, adds the forced
(12,40,40,12) rows, and constructs a square-zero differential with ranks
(23,56,23), hence cohomology dimensions (1,1,1,1).  Its role is to prove
that nilpotency and cohomology rank alone cannot obstruct all 104-row
non-cone completions.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import random
from typing import Any

from jsonschema import Draft202012Validator
import numpy as np
import sympy as sp

from d_quotient_classical.causal_transfer import (
    berger_q26_104_row_canonical_cone_lift_obstruction as cone,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
RESULT_ID = (
    "BERGER_Q26_104_ROW_NONCONE_RATIONAL_NILPOTENCE_FEASIBILITY_V1"
)
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
PAYLOAD = (
    ROOT
    / "d_quotient_classical/generated/"
    "berger_q26_104_row_noncone_rational_nilpotence_feasibility_v1/"
    "rational_noncone_differential.json"
)
REPORT = (
    ROOT
    / "d_quotient_classical/reports/"
    "berger-q26-104-row-noncone-rational-nilpotence-feasibility-v1.md"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "berger-q26-104-row-noncone-rational-nilpotence-feasibility-v1."
    "schema.json"
)
VERIFIER = (
    HERE
    / "verify_berger_q26_104_row_noncone_rational_nilpotence_feasibility.py"
)
TESTS = (
    HERE
    / "tests/"
    "test_berger_q26_104_row_noncone_rational_nilpotence_feasibility.py"
)
MIXED_CONE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_Q26_104_ROW_FULLY_MIXED_CONE_SDR_OBSTRUCTION_V1.json"
)

DEGREES_104 = tuple(
    [-1] * 6 + [0] * 20 + [1] * 20 + [2] * 6
) * 2
SPECIALIZATION = {"alpha_B": 2, "u": 1, "v": 3}
PRIME = 1009
SEED = 26072031


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _complete_basis(columns: sp.Matrix, dimension: int) -> sp.Matrix:
    result = columns
    rank = int(result.rank())
    for index in range(dimension):
        candidate = result.row_join(sp.eye(dimension)[:, index])
        if candidate.rank() > rank:
            result = candidate
            rank += 1
        if rank == dimension:
            return result
    raise AssertionError("failed to complete rational basis")


def _zero_parameters(matrix: sp.Matrix) -> sp.Matrix:
    parameters = sorted(
        set().union(*(value.free_symbols for value in matrix)),
        key=str,
    )
    return matrix.subs({parameter: 0 for parameter in parameters})


def _modular_rank(matrix: sp.Matrix, prime: int) -> int:
    value = np.asarray(
        [
            [
                int(sp.Rational(entry).p)
                * pow(int(sp.Rational(entry).q), -1, prime)
                % prime
                for entry in row
            ]
            for row in matrix.tolist()
        ],
        dtype=np.int64,
    )
    pivot = 0
    for column in range(value.shape[1]):
        candidates = np.flatnonzero(value[pivot:, column])
        if not len(candidates):
            continue
        selected = pivot + int(candidates[0])
        value[[pivot, selected]] = value[[selected, pivot]]
        value[pivot] = (
            value[pivot]
            * pow(int(value[pivot, column]), -1, prime)
        ) % prime
        for row in range(pivot + 1, value.shape[0]):
            if value[row, column]:
                value[row] = (
                    value[row] - value[row, column] * value[pivot]
                ) % prime
        pivot += 1
        if pivot == value.shape[0]:
            break
    return pivot


def _record(matrix: sp.Matrix) -> dict[str, Any]:
    entries = [
        [
            row,
            column,
            int(sp.Rational(value).p),
            int(sp.Rational(value).q),
        ]
        for (row, column), value in sorted(
            sp.SparseMatrix(matrix).todok().items()
        )
    ]
    body = {"shape": list(matrix.shape), "entries": entries}
    return {**body, "sha256": _digest(body)}


@lru_cache(maxsize=1)
def exact_witness() -> dict[str, Any]:
    q = cone._load_constant_matrix(cone.Q_PATH)
    indices = {
        degree: [
            index
            for index, value in enumerate(DEGREES_104)
            if value == degree
        ]
        for degree in (-1, 0, 1, 2)
    }
    old = [
        q.extract(indices[0], indices[-1]),
        q.extract(indices[1], indices[0]),
        q.extract(indices[2], indices[1]),
    ]
    p, r, t = old

    # Left endpoint: graph of [p P], enlarged deterministically to rank 23.
    auxiliary = sp.zeros(40, 12)
    middle = p.row_join(auxiliary)
    rank = int(middle.rank())
    added = 0
    for index in range(40):
        if rank == 23:
            break
        basis_column = sp.eye(40)[:, index]
        candidate = middle.row_join(basis_column)
        if candidate.rank() > rank:
            auxiliary[:, added] = basis_column
            added += 1
            middle = p.row_join(auxiliary)
            rank += 1
    if rank != 23:
        raise AssertionError("left endpoint rank completion failed")
    d_minus1 = sp.eye(40).col_join(-r) * middle

    # Right endpoint: a rank-23 graph with frozen old-old t.
    new_output = sp.zeros(24, 40)
    for index in range(23):
        new_output[index, index] = 1
    graph = sp.zeros(40)
    graph[:12, :] = t
    d_plus1 = (new_output * graph).row_join(new_output)

    # Middle map: factor through ker(d_plus1) and the quotient by
    # im(d_minus1), then choose one-dimensional kernel in that 57-space.
    kernel = sp.Matrix.hstack(*d_plus1.nullspace())
    quotient = sp.Matrix.vstack(
        *[vector.T for vector in d_minus1.T.nullspace()]
    )
    kernel_old = kernel[:40, :]
    quotient_old = quotient[:, :40]
    right_inverse = _zero_parameters(
        kernel_old.gauss_jordan_solve(sp.eye(40))[0]
    )
    kernel_basis = right_inverse.row_join(
        sp.Matrix.hstack(*kernel_old.nullspace())
    )
    image_columns = list(quotient_old.rref()[1])
    quotient_basis = _complete_basis(
        quotient_old[:, image_columns], 57
    )
    quotient_basis_inverse = quotient_basis.inv()
    reduced_old = (quotient_basis_inverse * quotient_old)[:25, :]
    constrained = _zero_parameters(
        reduced_old.T.gauss_jordan_solve(r.T)[0]
    ).T
    free_middle = sp.zeros(57)
    free_middle[:40, :25] = constrained
    generator = random.Random(SEED)
    for row in range(40):
        for column in range(25, 57):
            free_middle[row, column] = generator.randint(-3, 3)
    for row in range(40, 56):
        for column in range(57):
            free_middle[row, column] = generator.randint(-3, 3)
    if _modular_rank(free_middle, PRIME) != 56:
        raise AssertionError("deterministic middle rank witness drifted")
    d_zero = (
        kernel
        * (kernel_basis * free_middle * quotient_basis_inverse)
        * quotient
    )

    checks = {
        "old_minus1_block_fixed": d_minus1[:40, :12] == p,
        "old_zero_block_fixed": d_zero[:40, :40] == r,
        "old_plus1_block_fixed": d_plus1[:12, :40] == t,
        "left_composition_zero": (
            d_zero * d_minus1 == sp.zeros(80, 24)
        ),
        "right_composition_zero": (
            d_plus1 * d_zero == sp.zeros(24, 80)
        ),
    }
    ranks = [
        _modular_rank(d_minus1, PRIME),
        _modular_rank(d_zero, PRIME),
        _modular_rank(d_plus1, PRIME),
    ]
    homology = [
        24 - ranks[0],
        80 - ranks[0] - ranks[1],
        80 - ranks[1] - ranks[2],
        24 - ranks[2],
    ]
    if not all(checks.values()) or ranks != [23, 56, 23]:
        raise AssertionError(
            f"rational non-cone witness drifted: {checks}, {ranks}"
        )
    if homology != [1, 1, 1, 1]:
        raise AssertionError("rational non-cone cohomology drifted")
    body = {
        "schema": (
            "pure-weyl-berger-q26-104-row-noncone-rational-"
            "differential-v1"
        ),
        "result_id": (
            "BERGER_Q26_104_ROW_NONCONE_RATIONAL_DIFFERENTIAL_WITNESS_V1"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "representation": {
            "coefficient_field": "QQ",
            "specialization": SPECIALIZATION,
            "derivative_generators": {
                "e0": 0,
                "e1": 0,
                "e2": 0,
                "e3": 0,
            },
            "multiplicative": True,
        },
        "seed": SEED,
        "rank_prime": PRIME,
        "degree_dimensions": [24, 80, 80, 24],
        "differential_ranks": ranks,
        "cohomology_dimensions": homology,
        "matrices": {
            "degree_minus1_to_0": _record(d_minus1),
            "degree_0_to_plus1": _record(d_zero),
            "degree_plus1_to_plus2": _record(d_plus1),
        },
        "checks": checks,
    }
    return {**body, "sha256": _digest(body)}


def _artifact(path: Path, artifact_id: str) -> dict[str, str]:
    return {
        "artifact_id": artifact_id,
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def build() -> dict[str, Any]:
    mixed = _load(MIXED_CONE)
    if (
        mixed.get("result_id")
        != "BERGER_Q26_104_ROW_FULLY_MIXED_CONE_SDR_OBSTRUCTION_V1"
    ):
        raise AssertionError("mixed cone input drifted")
    witness = exact_witness()
    witness_text = json.dumps(witness, indent=2, sort_keys=True) + "\n"
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": (
            "pure-weyl-berger-q26-104-row-noncone-rational-"
            "nilpotence-feasibility-v1"
        ),
        "result_id": RESULT_ID,
        "result_state": (
            "RATIONAL_TRIVIAL_REPRESENTATION_NONCONE_NILPOTENCE_AND_"
            "RETAINED_COHOMOLOGY_FEASIBLE"
        ),
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "scope": {
            "theory": "retained minimal pure-Weyl Berger BV complex",
            "background": "fixed rational positive Berger clock",
            "boundaries": "R_t x compact Berger S3; no spatial boundary",
            "carrier": (
                "rational trivial-representation specialization of a "
                "general non-cone 208-row differential"
            ),
            "charge_sector": "unquotiented retained-26 formal Cauchy carrier",
            "degree": "-1,0,1,2",
            "parity": "BV grading only; cyclic pairing not constructed",
            "ell": "not harmonic-reduced",
            "m": "not harmonic-reduced",
            "k": "derivative generators specialized to zero",
            "omega": "evolution lift not constructed",
        },
        "pinned_inputs": {
            "mixed_cone_SDR_obstruction": _artifact(
                MIXED_CONE,
                "BERGER_Q26_104_ROW_FULLY_MIXED_CONE_SDR_OBSTRUCTION_V1",
            ),
            "q_Cauchy": _artifact(
                cone.Q_PATH, "rejected_candidate_q_Cauchy_104"
            ),
        },
        "exact_witness": {
            "artifact_id": witness["result_id"],
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": hashlib.sha256(witness_text.encode()).hexdigest(),
            "coefficient_field": "QQ",
            "multiplicative_specialization": True,
            "added_degree_profile": [12, 40, 40, 12],
            "differential_ranks": [23, 56, 23],
            "cohomology_dimensions": [1, 1, 1, 1],
            "old_old_q_blocks_fixed": True,
            "q_ext_squared_zero": True,
        },
        "classification": {
            "nilpotence_rank_only_global_104_row_obstruction": False,
            "retained_cohomology_rank_only_global_104_row_obstruction": False,
            "rational_PBW_operator_completion_constructed": False,
            "A104_evolution_lift_constructed": False,
            "cyclic_pairing_constructed": False,
            "real_involution_constructed": False,
            "retained_SDR_constructed": False,
            "Hadamard_or_quantum_claim": False,
        },
        "next_gate": (
            "SOLVE_OR_OBSTRUCT_EVOLUTION_EQUIVARIANCE_AND_CYCLICITY_"
            "FOR_A_PBW_NONCONE_104_ROW_COMPLETION"
        ),
        "claim_boundary": (
            "This exact rational multiplicative-specialization witness proves "
            "that the frozen old-old q blocks admit a non-cone square-zero "
            "208-row completion with the retained degreewise cohomology "
            "dimensions. It is a feasibility control, not a rational PBW "
            "operator completion. It does not construct or prove existence "
            "of an A104-equivariant extension, cyclic pairing, real "
            "involution, retained SDR, Cauchy/Krein form, Hadamard state or "
            "quantum theory."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                (
                    "PYTHONPATH=. python3 -m d_quotient_classical."
                    "causal_transfer."
                    "berger_q26_104_row_noncone_rational_nilpotence_"
                    "feasibility --check --guards"
                ),
                (
                    "PYTHONPATH=. python3 -m d_quotient_classical."
                    "causal_transfer."
                    "verify_berger_q26_104_row_noncone_rational_"
                    "nilpotence_feasibility"
                ),
                (
                    "PYTHONPATH=. python3 -m unittest "
                    "d_quotient_classical.causal_transfer.tests."
                    "test_berger_q26_104_row_noncone_rational_"
                    "nilpotence_feasibility"
                ),
                (
                    "npx --yes ajv-cli@5 validate --spec=draft2020 "
                    "--strict=true -s d_quotient_classical/schema/"
                    "berger-q26-104-row-noncone-rational-nilpotence-"
                    "feasibility-v1.schema.json -d "
                    f"d_quotient_classical/certificates/{RESULT_ID}.json"
                ),
            ],
        },
    }


def report_text() -> str:
    return r"""# Berger q26 non-cone 104-row rational nilpotence feasibility

The canonical doubled cone has the wrong retained cohomology.  That mismatch
does not extend to all non-cone completions.  In the exact multiplicative
rational specialization

\[
e_0=e_1=e_2=e_3=0,\qquad(\alpha_B,u,v)=(2,1,3),
\]

the frozen old-old \(q_{\rm Cauchy}\) blocks admit a non-cone differential on
the \(208\)-row degree profile

\[
(24,80,80,24).
\]

The three differential ranks are

\[
(23,56,23),
\]

both adjacent compositions vanish exactly, and the degreewise cohomology is

\[
(1,1,1,1),
\]

matching the specialized retained 26-row complex.  The payload contains every
rational matrix entry and internal content hashes.  An independent verifier
replays the products and certifies the ranks at a different good prime.

This is a feasibility control only.  It is not a PBW operator completion, and
it supplies no evolution lift, cyclic pairing, real involution or retained
SDR.  It proves that the next obstruction must use evolution, cyclicity,
locality/PBW lifting or nontrivial Berger representations rather than
nilpotency and cohomology ranks alone.
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    witness = exact_witness()
    certificate = build()
    witness_text = json.dumps(witness, indent=2, sort_keys=True) + "\n"
    certificate_text = json.dumps(
        certificate, indent=2, sort_keys=True
    ) + "\n"
    if args.check:
        if PAYLOAD.read_text() != witness_text:
            raise AssertionError("witness payload drifted")
        if OUTPUT.read_text() != certificate_text:
            raise AssertionError("certificate drifted")
        if REPORT.read_text() != report_text():
            raise AssertionError("report drifted")
    else:
        _write(PAYLOAD, witness_text)
        _write(OUTPUT, certificate_text)
        _write(REPORT, report_text())
    Draft202012Validator(_load(SCHEMA)).validate(certificate)
    if args.guards:
        mutated = json.loads(certificate_text)
        mutated["classification"][
            "rational_PBW_operator_completion_constructed"
        ] = True
        try:
            Draft202012Validator(_load(SCHEMA)).validate(mutated)
        except Exception:
            pass
        else:
            raise AssertionError("schema accepted PBW promotion")
    print(
        f"{RESULT_ID}: PASS ranks=[23,56,23] "
        "cohomology=[1,1,1,1]"
    )


if __name__ == "__main__":
    main()
