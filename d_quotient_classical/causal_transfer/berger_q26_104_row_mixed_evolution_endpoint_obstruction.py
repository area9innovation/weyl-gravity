#!/usr/bin/env python3
"""Obstruct the rational fully-mixed correction ansatz at the left endpoint.

The ansatz keeps the frozen old-old blocks while making evolution commute:

    A_ext = N tensor A,
    q_ext = N tensor q + (I-N) tensor s,
    N = [[1,-1],[1,-1]], N^2 = 0.

Evolution equivariance reduces to A_0 s = s A_-1.  The required total
left-endpoint rank is 23.  Over Q an intertwiner s has rank 12, at most 10,
or rank 11.  In the rank-11 case its one-dimensional kernel is the unique
rational A_-1-invariant line, ker(A_-1), and the frozen q kills that line.
Consequently the doubled block has rank 22.  Rank 12 gives rank 24 and rank
at most 10 gives rank at most 22.  Thus rank 23 is absent in this declared
ansatz.  This is not a no-go theorem for general 104-row completions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
from typing import Any

from flint import fmpq, fmpq_mat
from jsonschema import Draft202012Validator
import sympy as sp
from sympy.polys.domains import QQ
from sympy.polys.matrices import DomainMatrix
from sympy.polys.matrices.sdm import SDM

from d_quotient_classical.causal_transfer import (
    berger_q26_104_row_canonical_cone_lift_obstruction as cone,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
RESULT_ID = (
    "BERGER_Q26_104_ROW_MIXED_EVOLUTION_CORRECTION_ENDPOINT_"
    "OBSTRUCTION_V1"
)
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
PAYLOAD = (
    ROOT
    / "d_quotient_classical/generated/"
    "berger_q26_104_row_mixed_evolution_endpoint_obstruction_v1/"
    "rational_endpoint_witness.json"
)
REPORT = (
    ROOT
    / "d_quotient_classical/reports/"
    "berger-q26-104-row-mixed-evolution-endpoint-obstruction-v1.md"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "berger-q26-104-row-mixed-evolution-endpoint-obstruction-v1.schema.json"
)
VERIFIER = (
    HERE
    / "verify_berger_q26_104_row_mixed_evolution_endpoint_obstruction.py"
)
TESTS = (
    HERE
    / "tests/test_berger_q26_104_row_mixed_evolution_endpoint_obstruction.py"
)
LOWER_BOUND = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_Q26_FINITE_ROW_MODULE_CLOSURE_LOWER_BOUND_V1.json"
)
PRIOR_CONE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_Q26_104_ROW_CANONICAL_CONE_LIFT_OBSTRUCTION_V1.json"
)
FORGE_PARTIAL = Path("/home/alstrup/area9/tango/forge/lib/math/sdrsolve.forge")

DEGREES_104 = tuple([-1] * 6 + [0] * 20 + [1] * 20 + [2] * 6) * 2
SEED = 20260721


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


def _qq(value: object):
    value = sp.Rational(value)
    return QQ(int(value.p), int(value.q))


def _spq(value: object) -> sp.Rational:
    return sp.Rational(int(value.numerator), int(value.denominator))


def _domain_matrix(matrix: sp.Matrix) -> DomainMatrix:
    record: dict[int, dict[int, object]] = {}
    for (row, column), value in sp.SparseMatrix(matrix).todok().items():
        record.setdefault(row, {})[column] = _qq(value)
    return DomainMatrix.from_rep(SDM(record, matrix.shape, QQ))


def _nullspace_rows(matrix: sp.Matrix) -> list[list[sp.Rational]]:
    nullspace = _domain_matrix(matrix).nullspace()
    return [
        [
            _spq(nullspace.rep.get(row, {}).get(column, QQ.zero))
            for column in range(matrix.cols)
        ]
        for row in range(nullspace.shape[0])
    ]


def _flint(matrix: sp.Matrix) -> fmpq_mat:
    return fmpq_mat(
        [
            [
                fmpq(
                    int(sp.Rational(matrix[row, column]).p),
                    int(sp.Rational(matrix[row, column]).q),
                )
                for column in range(matrix.cols)
            ]
            for row in range(matrix.rows)
        ]
    )


def _sympy(matrix: fmpq_mat) -> sp.Matrix:
    return sp.Matrix(
        matrix.nrows(),
        matrix.ncols(),
        lambda row, column: sp.Rational(
            int(matrix[row, column].numerator),
            int(matrix[row, column].denominator),
        ),
    )


def _intertwiner_system(target: sp.Matrix, source: sp.Matrix) -> sp.Matrix:
    return sp.kronecker_product(sp.eye(source.rows), target) - sp.kronecker_product(
        source.T, sp.eye(target.rows)
    )


def _vector_matrix(vector: list[sp.Rational], rows: int, columns: int) -> sp.Matrix:
    return sp.Matrix(
        rows,
        columns,
        lambda row, column: vector[column * rows + row],
    )


def _witness_from_basis(
    basis: list[list[sp.Rational]],
    rows: int,
    columns: int,
    target_rank: int,
) -> sp.Matrix:
    generator = random.Random(SEED + target_rank)
    flint_basis = [_flint(_vector_matrix(vector, rows, columns)) for vector in basis]
    for _ in range(10_000):
        candidate = fmpq_mat(rows, columns)
        for basis_matrix in flint_basis:
            coefficient = generator.randint(-3, 3)
            if coefficient:
                candidate += coefficient * basis_matrix
        if candidate.rank() == target_rank:
            return _sympy(candidate)
    raise AssertionError(f"failed to find deterministic rank-{target_rank} witness")


def _full_left_block(old_q: sp.Matrix, correction: sp.Matrix) -> sp.Matrix:
    return sp.Matrix.vstack(
        sp.Matrix.hstack(old_q, -old_q + correction),
        sp.Matrix.hstack(old_q - correction, -old_q + 2 * correction),
    )


def _record(matrix: sp.Matrix) -> dict[str, Any]:
    entries = [
        [
            row,
            column,
            int(sp.Rational(value).p),
            int(sp.Rational(value).q),
        ]
        for (row, column), value in sorted(sp.SparseMatrix(matrix).todok().items())
    ]
    body = {"shape": list(matrix.shape), "entries": entries}
    return {**body, "sha256": _digest(body)}


def _sparse_vector(vector: sp.Matrix) -> list[list[int | str]]:
    return [
        [row, str(vector[row, 0])]
        for row in range(vector.rows)
        if vector[row, 0]
    ]


def exact_witness() -> dict[str, Any]:
    q104 = cone._load_constant_matrix(cone.Q_PATH)
    a104 = cone._load_constant_matrix(cone.A_PATH)
    indices = {
        degree: [index for index, value in enumerate(DEGREES_104) if value == degree]
        for degree in (-1, 0)
    }
    old_q = q104.extract(indices[0], indices[-1])
    source = a104.extract(indices[-1], indices[-1])
    target = a104.extract(indices[0], indices[0])
    system = _intertwiner_system(target, source)
    hom_basis = _nullspace_rows(system)
    if len(hom_basis) != 20:
        raise AssertionError(f"intertwiner dimension drifted: {len(hom_basis)}")

    rank12 = _witness_from_basis(hom_basis, 40, 12, 12)
    source_kernel = source.nullspace()
    if len(source_kernel) != 1:
        raise AssertionError("source rational zero eigenspace drifted")
    invariant_line = source_kernel[0]
    kill_line = sp.kronecker_product(invariant_line.T, sp.eye(40))
    constrained_basis = _nullspace_rows(system.col_join(kill_line))
    rank11 = _witness_from_basis(constrained_basis, 40, 12, 11)

    rank12_full = _flint(_full_left_block(old_q, rank12)).rank()
    rank11_full = _flint(_full_left_block(old_q, rank11)).rank()
    if rank12_full != 24 or rank11_full != 22:
        raise AssertionError(
            f"endpoint ranks drifted: rank12->{rank12_full}, rank11->{rank11_full}"
        )
    if old_q * invariant_line != sp.zeros(40, 1):
        raise AssertionError("frozen q no longer kills the rational invariant line")
    if source * invariant_line != sp.zeros(12, 1):
        raise AssertionError("invariant line is not the zero eigenspace")
    if target * rank11 != rank11 * source:
        raise AssertionError("rank-11 witness lost equivariance")

    charpoly = sp.factor(source.charpoly().as_expr())
    expected = (
        sp.Symbol("lambda") ** 2
        * (sp.Symbol("lambda") ** 2 + 4) ** 2
        * (2 * sp.Symbol("lambda") ** 2 + 1)
        * (2 * sp.Symbol("lambda") ** 2 + 13) ** 2
        / 8
    )
    if sp.expand(charpoly - expected) != 0:
        raise AssertionError(f"source characteristic polynomial drifted: {charpoly}")

    body = {
        "schema": "pure-weyl-berger-q26-104-row-mixed-evolution-endpoint-witness-v1",
        "result_id": (
            "BERGER_Q26_104_ROW_MIXED_EVOLUTION_RATIONAL_ENDPOINT_WITNESS_V1"
        ),
        "coefficient_field": "QQ",
        "specialization": {"alpha_B": 2, "u": 1, "v": 3, "e0": 0, "e1": 0, "e2": 0, "e3": 0},
        "ansatz": {
            "N": [[1, -1], [1, -1]],
            "K": [[0, 1], [-1, 2]],
            "A_ext": "N tensor A",
            "q_ext": "N tensor q + K tensor s",
        },
        "intertwiner_dimension": len(hom_basis),
        "rank_11_constrained_intertwiner_dimension": len(constrained_basis),
        "source_characteristic_polynomial": str(charpoly),
        "unique_rational_invariant_line": _sparse_vector(invariant_line),
        "q_on_invariant_line": _sparse_vector(old_q * invariant_line),
        "rank_12_witness": _record(rank12),
        "rank_11_witness": _record(rank11),
        "endpoint_ranks": {"rank_12_correction": rank12_full, "rank_11_correction": rank11_full},
        "checks": {
            "hom_A_dimension_20": True,
            "unique_rational_eigenvalue_is_zero": True,
            "unique_rational_invariant_line_dimension_1": True,
            "frozen_q_kills_invariant_line": True,
            "rank_12_total_endpoint_rank_24": True,
            "rank_11_total_endpoint_rank_22": True,
            "rank_at_most_10_total_endpoint_rank_at_most_22": True,
            "required_rank_23_absent": True,
        },
    }
    return {**body, "sha256": _digest(body)}


def _artifact(path: Path, artifact_id: str) -> dict[str, str]:
    return {
        "artifact_id": artifact_id,
        "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "sha256": _sha(path),
    }


def build() -> dict[str, Any]:
    lower = _load(LOWER_BOUND)
    prior = _load(PRIOR_CONE)
    if lower.get("result_id") != "BERGER_Q26_FINITE_ROW_MODULE_CLOSURE_LOWER_BOUND_V1":
        raise AssertionError("lower-bound input drifted")
    if prior.get("result_id") != "BERGER_Q26_104_ROW_CANONICAL_CONE_LIFT_OBSTRUCTION_V1":
        raise AssertionError("prior cone input drifted")
    witness = exact_witness()
    witness_text = json.dumps(witness, indent=2, sort_keys=True) + "\n"
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-berger-q26-104-row-mixed-evolution-endpoint-obstruction-v1",
        "result_id": RESULT_ID,
        "result_state": "RATIONAL_FULLY_MIXED_CORRECTION_ANSATZ_MISSES_REQUIRED_LEFT_ENDPOINT_RANK",
        "lifecycle_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "scope": {
            "theory": "retained minimal pure-Weyl Berger BV complex",
            "background": "fixed rational positive Berger clock",
            "boundaries": "R_t x compact Berger S3; no spatial boundary",
            "carrier": "104 old rows plus one same-profile 104-row copy in the fully-mixed correction ansatz",
            "charge_sector": "unquotiented retained-26 formal Cauchy carrier",
            "degree": "left endpoint -1 to 0",
            "parity": "BV grading only; cyclic pairing not reached",
            "ell": "not harmonic-reduced",
            "m": "not harmonic-reduced",
            "k": "derivative generators specialized to zero",
            "omega": "stationary A104 rational compression",
        },
        "pinned_inputs": {
            "module_lower_bound": _artifact(LOWER_BOUND, lower["result_id"]),
            "prior_cone_obstruction": _artifact(PRIOR_CONE, prior["result_id"]),
            "q_Cauchy": _artifact(cone.Q_PATH, "rejected_candidate_q_Cauchy_104"),
            "A104": _artifact(cone.A_PATH, "global_A104"),
            "forge_partial_solver": _artifact(FORGE_PARTIAL, "FORGE_M9C_ONE_FREE_DIFFERENTIAL_SOLVER"),
        },
        "exact_obstruction": {
            "artifact_id": witness["result_id"],
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": hashlib.sha256(witness_text.encode()).hexdigest(),
            "required_left_endpoint_rank": 23,
            "attainable_neighbor_ranks": [22, 24],
            "proof": (
                "Every one-dimensional rational kernel of an A-equivariant correction is an A-invariant rational line. "
                "The source characteristic polynomial has no rational root except zero and ker(A_-1) is one-dimensional, "
                "so every rank-11 correction kills that unique line. The frozen old q also kills it, hence the induced "
                "off-diagonal map on ker(s) is zero and rank(q_ext)=2 rank(s)=22. Rank-12 corrections give rank 24; "
                "rank at most 10 gives rank at most 2r+(12-r)<=22. Therefore rank 23 is absent."
            ),
        },
        "classification": {
            "declared_mixed_correction_ansatz_closes": False,
            "all_rational_104_row_completions_obstructed": False,
            "global_104_row_lower_bound_raised": False,
            "PBW_operator_completion_constructed": False,
            "cyclic_pairing_constructed": False,
            "real_involution_constructed": False,
            "retained_SDR_constructed": False,
            "Hadamard_or_quantum_claim": False,
        },
        "partial_solver_disposition": {
            "forge_commit": "814484bc9",
            "usable_slice": "one free differential with adjacent differential and evolution frozen",
            "result": "the structured rational slice is exactly obstructed before the free middle differential is solved",
            "remaining_capability": "two-free-differential bilinear completion with rank strata, cyclicity and full SDR side conditions",
        },
        "next_gate": "GENERAL_NONCONE_SIMULTANEOUS_TWO_FREE_DIFFERENTIAL_COMPLETION_OR_CHARACTERISTIC_ZERO_SEPARATOR",
        "claim_boundary": (
            "This exact characteristic-zero theorem closes only the fully-mixed correction ansatz A_ext=N tensor A, "
            "q_ext=N tensor q+(I-N) tensor s at the left endpoint. It does not obstruct every 104-row non-cone "
            "completion, raise the global lower bound, or establish a cyclic pairing, real structure, retained SDR, "
            "Hadamard state, positivity, QME, particle, scattering or unitarity result."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.causal_transfer.berger_q26_104_row_mixed_evolution_endpoint_obstruction --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.causal_transfer.verify_berger_q26_104_row_mixed_evolution_endpoint_obstruction",
                "PYTHONPATH=. python3 -m unittest d_quotient_classical.causal_transfer.tests.test_berger_q26_104_row_mixed_evolution_endpoint_obstruction",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-q26-104-row-mixed-evolution-endpoint-obstruction-v1.schema.json -d d_quotient_classical/certificates/BERGER_Q26_104_ROW_MIXED_EVOLUTION_CORRECTION_ENDPOINT_OBSTRUCTION_V1.json",
            ],
        },
    }


def report_text() -> str:
    return r"""# Berger q26: mixed-evolution correction endpoint obstruction

The bounded fully-mixed correction ansatz

\[
A_{\rm ext}=N\otimes A,\qquad
q_{\rm ext}=N\otimes q+(I-N)\otimes s,
\qquad
N=\begin{pmatrix}1&-1\\1&-1\end{pmatrix}
\]

preserves the frozen old-old blocks and makes evolution equivariance linear:

\[
A_0s=sA_{-1}.
\]

It cannot attain the required left-endpoint rank (23) over \(\mathbb Q\).
The exact intertwiner space has dimension (20).  A rank-(11)
intertwiner has a one-dimensional rational invariant kernel.  The source
characteristic polynomial has no rational root except zero, and
\(\ker A_{-1}\) is one-dimensional, so this kernel is forced to be the
unique zero-eigenline.  The frozen old differential kills the same line.
Therefore the off-diagonal contribution on \(\ker s\) vanishes and

\[
\operatorname{rank}q_{\rm ext}=2\operatorname{rank}s=22.
\]

Rank-(12) corrections give total rank (24), while rank at most (10)
cannot exceed (22).  The missing value (23) is therefore an exact
characteristic-zero obstruction, not a failed numerical search.

This closes one structured rational branch only.  General non-cone
104-row completions still require the two-free-differential/rank-stratum
solver that the partial M9c delivery explicitly does not provide.
"""


def write_outputs() -> dict[str, Any]:
    witness = exact_witness()
    PAYLOAD.parent.mkdir(parents=True, exist_ok=True)
    PAYLOAD.write_text(json.dumps(witness, indent=2, sort_keys=True) + "\n")
    result = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report_text())
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    arguments = parser.parse_args()
    if arguments.check:
        expected = build()
        actual = _load(OUTPUT)
        if actual != expected:
            raise SystemExit("certificate drifted; rerun producer")
        payload = _load(PAYLOAD)
        if payload != exact_witness():
            raise SystemExit("payload drifted; rerun producer")
        Draft202012Validator.check_schema(_load(SCHEMA))
        Draft202012Validator(_load(SCHEMA)).validate(actual)
        if arguments.guards:
            if actual["classification"]["all_rational_104_row_completions_obstructed"]:
                raise SystemExit("claim-boundary guard failed")
            if actual["classification"]["Hadamard_or_quantum_claim"]:
                raise SystemExit("quantum-promotion guard failed")
        print(f"{RESULT_ID}: PASS")
        return 0
    write_outputs()
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    print(f"wrote {PAYLOAD.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
