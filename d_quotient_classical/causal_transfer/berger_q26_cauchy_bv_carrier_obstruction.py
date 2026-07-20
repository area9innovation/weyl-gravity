#!/usr/bin/env python3
"""Exact obstruction for the frozen Berger q26 Cauchy-graph lift.

The theorem proved here is deliberately scoped.  It considers the complete
class of finite-order support-local operators on the frozen 104-row formal
Cauchy graph which agree with the already normalized retained-26 companion
solution map.  Agreement on every formal Cauchy datum fixes the operator
uniquely.  The unique member is the previously serialized canonical graph
candidate, whose square and evolution commutator are recomputed here.

The extension lower bound uses an honest representation of the noncommuting
Berger derivative algebra.  A scalar principal-symbol substitution would not
preserve products and therefore cannot certify a factorization-rank bound.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
QUANTUM = ROOT / "quantum-weyl"
if str(QUANTUM) not in sys.path:
    sys.path.insert(0, str(QUANTUM))

from lorentzian import berger_canonical_graph_q_cauchy_obstruction as GRAPH  # noqa: E402


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/generated/berger_q26_cauchy_bv_carrier_obstruction_v1/adjoint_representation_witness.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-q26-cauchy-bv-carrier-obstruction-v1.md"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-q26-cauchy-bv-carrier-obstruction-v1.schema.json"
VERIFIER = HERE / "verify_berger_q26_cauchy_bv_carrier_obstruction.py"
TESTS = HERE / "tests/test_berger_q26_cauchy_bv_carrier_obstruction.py"

DEPENDENCIES = {
    "quantum_request": ROOT / "planning/events/quantum-berger-c26-normalized-hadamard-representative-REQUEST-d5d21252e177b056.json",
    "request_acceptance": ROOT / "planning/events/quantum-berger-c26-normalized-hadamard-representative-to-classical-d5d21252e177b056-RANSWER-ACCEPT-fc432630dfbc7cea.json",
    "retained_q26": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json",
    "retained_layout": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_LAYOUT.json",
    "full_A104_certificate": ROOT / "quantum-weyl/lorentzian/certificates/BERGER_A104_ENDPOINT_COMPLETION.json",
    "full_A104_operator": ROOT / "quantum-weyl/lorentzian/generated/berger_a104_endpoint_completion/global_A104.json",
    "canonical_graph_disposition": ROOT / "quantum-weyl/lorentzian/certificates/BERGER_CANONICAL_GRAPH_Q_CAUCHY_OBSTRUCTION.json",
    "rejected_q_Cauchy_104": ROOT / "quantum-weyl/lorentzian/generated/berger_canonical_graph_q_cauchy_obstruction/rejected_candidate_q_Cauchy_104.json",
}

DEGREES = GRAPH.DEGREES_104
SPECIALIZATION = {"alpha_B": 2, "u": 1, "v": 3}
REPRESENTATION_DIMENSION = 3


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _ref(path: Path, artifact_id: str) -> dict[str, str]:
    return {
        "artifact_id": artifact_id,
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _representation() -> tuple[sp.Matrix, ...]:
    """Adjoint representation of the u=1, v=3 Berger derivative algebra."""
    u = SPECIALIZATION["u"]
    v = SPECIALIZATION["v"]
    identity = sp.eye(REPRESENTATION_DIMENSION)
    d1 = sp.Matrix([[0, 0, 0], [0, 0, -v], [0, u, 0]])
    d2 = sp.Matrix([[0, 0, v], [0, 0, 0], [-u, 0, 0]])
    d3 = sp.Matrix([[0, -v, 0], [v, 0, 0], [0, 0, 0]])
    if d1 * d2 - d2 * d1 != u * d3:
        raise AssertionError("adjoint representation lost [D1,D2]=uD3")
    if d2 * d3 - d3 * d2 != v * d1:
        raise AssertionError("adjoint representation lost [D2,D3]=vD1")
    if d3 * d1 - d1 * d3 != v * d2:
        raise AssertionError("adjoint representation lost [D3,D1]=vD2")
    return identity, d1, d2, d3


def _integer_matrix(matrix: sp.Matrix) -> list[list[int]]:
    return [[int(value) for value in row] for row in matrix.tolist()]


def _evaluate_operator(
    operator: GRAPH.Operator, representation: tuple[sp.Matrix, ...]
) -> sp.Matrix:
    result = sp.zeros(REPRESENTATION_DIMENSION)
    alpha = SPECIALIZATION["alpha_B"]
    u = SPECIALIZATION["u"]
    v = SPECIALIZATION["v"]
    for word, polynomial in operator.items():
        coefficient = sum(
            sp.Rational(value.numerator, value.denominator)
            * alpha ** monomial[0]
            * u ** monomial[1]
            * v ** monomial[2]
            for monomial, value in polynomial.items()
        )
        represented_word = sp.eye(REPRESENTATION_DIMENSION)
        for axis in word:
            represented_word *= representation[axis]
        result += coefficient * represented_word
    return result


def _represented_block(
    matrix: GRAPH.Matrix,
    source_degree: int,
    degree_shift: int,
    representation: tuple[sp.Matrix, ...],
) -> tuple[sp.Matrix, list[int], list[int]]:
    target_rows = [
        index for index, degree in enumerate(DEGREES)
        if degree == source_degree + degree_shift
    ]
    source_columns = [
        index for index, degree in enumerate(DEGREES)
        if degree == source_degree
    ]
    block = sp.zeros(
        REPRESENTATION_DIMENSION * len(target_rows),
        REPRESENTATION_DIMENSION * len(source_columns),
    )
    for local_row, global_row in enumerate(target_rows):
        for local_column, global_column in enumerate(source_columns):
            value = _evaluate_operator(
                matrix[global_row][global_column], representation
            )
            block[
                REPRESENTATION_DIMENSION * local_row:
                REPRESENTATION_DIMENSION * (local_row + 1),
                REPRESENTATION_DIMENSION * local_column:
                REPRESENTATION_DIMENSION * (local_column + 1),
            ] = value
    return block, target_rows, source_columns


def _pivot_minor(matrix: sp.Matrix) -> dict[str, Any]:
    rank = matrix.rank()
    if rank == 0:
        return {
            "rank": 0,
            "pivot_rows": [],
            "pivot_columns": [],
            "determinant": "1",
        }
    _, pivot_columns = matrix.rref()
    selected_columns = list(pivot_columns[:rank])
    column_basis = matrix[:, selected_columns]
    _, pivot_rows = column_basis.T.rref()
    selected_rows = list(pivot_rows[:rank])
    minor = matrix.extract(selected_rows, selected_columns)
    determinant = sp.factor(minor.det())
    if determinant == 0:
        raise AssertionError("pivot-minor extraction failed")
    return {
        "rank": rank,
        "pivot_rows": selected_rows,
        "pivot_columns": selected_columns,
        "determinant": str(determinant),
    }


def _block_witness(
    matrix: GRAPH.Matrix,
    source_degree: int,
    shift: int,
    representation: tuple[sp.Matrix, ...],
) -> dict[str, Any]:
    block, target_rows, source_columns = _represented_block(
        matrix, source_degree, shift, representation
    )
    witness = _pivot_minor(block)
    witness.update(
        {
            "source_degree": source_degree,
            "target_degree": source_degree + shift,
            "represented_shape": list(block.shape),
            "carrier_target_rows": target_rows,
            "carrier_source_columns": source_columns,
        }
    )
    return witness


def _count_nonzero(matrix: GRAPH.Matrix) -> int:
    return sum(bool(operator) for row in matrix for operator in row)


def _maximum_order(matrix: GRAPH.Matrix) -> int:
    return max(
        (len(word) for row in matrix for operator in row for word in operator),
        default=0,
    )


@lru_cache(maxsize=1)
def _calculation() -> dict[str, Any]:
    a104_record = _load(DEPENDENCIES["full_A104_operator"])
    q_record = _load(DEPENDENCIES["rejected_q_Cauchy_104"])
    A104 = GRAPH._canonical_symbols(
        GRAPH._load_hashed_operator(DEPENDENCIES["full_A104_operator"], (104, 104))
    )
    q_cauchy = GRAPH._load_record(q_record, (104, 104))
    square = GRAPH._sparse_multiply(q_cauchy, q_cauchy)
    commutator = GRAPH._subtract(
        GRAPH._sparse_multiply(A104, q_cauchy),
        GRAPH._sparse_multiply(q_cauchy, A104),
    )
    square_count = _count_nonzero(square)
    commutator_count = _count_nonzero(commutator)
    if square_count != 157 or commutator_count != 207:
        raise AssertionError("rejected-candidate defect control drifted")

    representation = _representation()
    square_blocks = {
        "degree_minus1_to_plus1": _block_witness(
            square, -1, 2, representation
        ),
        "degree_0_to_plus2": _block_witness(square, 0, 2, representation),
    }
    commutator_blocks = {
        "degree_minus1_to_0": _block_witness(
            commutator, -1, 1, representation
        ),
        "degree_0_to_plus1": _block_witness(
            commutator, 0, 1, representation
        ),
        "degree_plus1_to_plus2": _block_witness(
            commutator, 1, 1, representation
        ),
    }
    if [row["rank"] for row in square_blocks.values()] != [13, 3]:
        raise AssertionError("represented square ranks drifted")
    if [row["rank"] for row in commutator_blocks.values()] != [13, 15, 5]:
        raise AssertionError("represented commutator ranks drifted")

    extension_by_degree = {
        "degree_0": math.ceil(
            square_blocks["degree_minus1_to_plus1"]["rank"]
            / REPRESENTATION_DIMENSION
        ),
        "degree_plus1": math.ceil(
            square_blocks["degree_0_to_plus2"]["rank"]
            / REPRESENTATION_DIMENSION
        ),
    }
    return {
        "a104_internal_sha256": a104_record["sha256"],
        "q_cauchy_internal_sha256": q_record["sha256"],
        "candidate_nonzero_sparse_entries": len(q_record["entries"]),
        "candidate_maximum_spatial_differential_order": _maximum_order(q_cauchy),
        "square_nonzero_sparse_entries": square_count,
        "commutator_nonzero_sparse_entries": commutator_count,
        "representation": {
            "name": "three_dimensional_adjoint",
            "dimension": REPRESENTATION_DIMENSION,
            "specialization": SPECIALIZATION,
            "D0": _integer_matrix(representation[0]),
            "D1": _integer_matrix(representation[1]),
            "D2": _integer_matrix(representation[2]),
            "D3": _integer_matrix(representation[3]),
            "relations": [
                "[D1,D2]=u D3",
                "[D2,D3]=v D1",
                "[D3,D1]=v D2",
                "[D0,Di]=0",
            ],
        },
        "square_blocks": square_blocks,
        "commutator_blocks": commutator_blocks,
        "extension_lower_bound": {
            "degree_0_added_rows_at_least": extension_by_degree["degree_0"],
            "degree_plus1_added_rows_at_least": extension_by_degree["degree_plus1"],
            "total_added_rows_at_least": sum(extension_by_degree.values()),
            "status": "NECESSARY_NOT_SUFFICIENT",
            "proof": (
                "For an enlarged degree-plus-one differential "
                "[q B; C E], nilpotence on the old carrier gives q^2=-BC. "
                "After the multiplicative 3-dimensional representation, "
                "rank(rho(B)rho(C)) is at most three times the number of "
                "new intermediate carrier rows in the relevant degree."
            ),
        },
    }


def build_payload() -> dict[str, Any]:
    calculation = _calculation()
    return {
        "schema": "pure-weyl-berger-q26-cauchy-bv-carrier-adjoint-witness-v1",
        "result_id": "BERGER_Q26_CAUCHY_BV_CARRIER_ADJOINT_WITNESS_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        **calculation,
    }


def build() -> dict[str, Any]:
    imported = {name: _load(path) for name, path in DEPENDENCIES.items()}
    request = imported["quantum_request"]["body"]["payload"]
    acceptance = imported["request_acceptance"]["body"]["payload"]
    if request["request_id"] != acceptance["request_id"]:
        raise ValueError("request acceptance does not match request")
    if acceptance["action"] != "ACCEPT":
        raise ValueError("quantum request is not accepted")
    if imported["retained_q26"]["flags"]["BERGER_RETAINED_MINIMAL_OPERATOR"] is not True:
        raise ValueError("retained q26 is not certified")
    if imported["full_A104_certificate"]["claim_flags"]["BERGER_FULL_A104_CAUCHY_OPERATOR"] is not True:
        raise ValueError("full A104 is not certified")
    disposition = imported["canonical_graph_disposition"]
    if (
        disposition["defects"]["candidate_q_Cauchy_square"]["nonzero_sparse_entries"]
        != 157
        or disposition["defects"]["A104_candidate_q_Cauchy_commutator"]["nonzero_sparse_entries"]
        != 207
    ):
        raise ValueError("imported rejected-candidate controls drifted")

    calculation = _calculation()
    payload = build_payload()
    payload_sha = hashlib.sha256(
        (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    ).hexdigest()
    dependencies = {
        name: _ref(
            path,
            (
                imported[name].get("result_id")
                or imported[name].get("id")
                or imported[name].get("schema")
                or name
            ),
        )
        for name, path in DEPENDENCIES.items()
    }
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-berger-q26-cauchy-bv-carrier-obstruction-v1",
        "result_id": "BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1",
        "result_state": "FROZEN_104_ROW_FORMAL_CAUCHY_GRAPH_LIFT_CLASS_EMPTY",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "request_id": request["request_id"],
        "dependency_refs": dependencies,
        "complete_declared_lift_class": {
            "carrier": "frozen 104-row formal stationary Cauchy graph of A104",
            "row_degrees": {
                "minus1": DEGREES.count(-1),
                "zero": DEGREES.count(0),
                "plus1": DEGREES.count(1),
                "plus2": DEGREES.count(2),
            },
            "coefficient_algebra": "finite-order PBW differential operators over QQ[alpha_B,u,v]",
            "support_policy": "finite-order support-local",
            "grading": "degree plus one",
            "compatibility_identity": (
                "q_C = ev_0 o q52_normalized o Sol_A104 on every formal "
                "104-row Cauchy datum"
            ),
            "pairing_real_adjoint_policy": (
                "cyclic pairing, real involution and graded-adjoint identities "
                "are additional constraints; the class is already empty before imposing them"
            ),
            "completeness_argument": (
                "Formal Cauchy evaluation ev_0 is the identity on the frozen "
                "104-row datum. Therefore the compatibility identity fixes "
                "q_C pointwise on every datum and admits at most one operator, "
                "independently of any finite differential-order bound."
            ),
            "unique_member": "imported rejected_candidate_q_Cauchy_104",
        },
        "exact_replay": {
            "q_Cauchy_nonzero_sparse_entries": calculation[
                "candidate_nonzero_sparse_entries"
            ],
            "q_Cauchy_maximum_spatial_differential_order": calculation[
                "candidate_maximum_spatial_differential_order"
            ],
            "q_Cauchy_square_nonzero_sparse_entries": calculation[
                "square_nonzero_sparse_entries"
            ],
            "A104_q_Cauchy_commutator_nonzero_sparse_entries": calculation[
                "commutator_nonzero_sparse_entries"
            ],
            "q_Cauchy_squared_zero": False,
            "A104_commutes_with_q_Cauchy": False,
        },
        "obstruction": {
            "same_104_row_lift": "DOES_NOT_EXIST_IN_COMPLETE_DECLARED_CLASS",
            "reason": (
                "the unique compatible operator has nonzero square and nonzero "
                "evolution commutator"
            ),
            "all_finite_orders": True,
            "pairing_real_adjoint_subclass": "EMPTY_A_FORTIORI",
        },
        "extension_lower_bound": calculation["extension_lower_bound"],
        "exact_witness_payload": {
            "artifact_id": payload["result_id"],
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": payload_sha,
        },
        "repair_alternatives": [
            {
                "kind": "CHANGE_NORMALIZED_COMPANION_OR_A104",
                "status": "OPEN",
                "note": "at least one frozen companion/evolution coefficient or compatibility convention must change",
            },
            {
                "kind": "ENLARGE_CAUCHY_CARRIER",
                "status": "OPEN",
                "note": "nilpotence alone requires at least six added rows: five in degree 0 and one in degree +1; sufficiency and evolution compatibility are not proved",
            },
        ],
        "claim_flags": {
            "BERGER_FROZEN_104_ROW_Q26_CAUCHY_GRAPH_LIFT_OBSTRUCTED": True,
            "BERGER_CANONICAL_157_207_DEFECTS_REPRODUCED": True,
            "BERGER_CARRIER_EXTENSION_AT_LEAST_6_ROWS": True,
            "BERGER_6_ROW_EXTENSION_SUFFICIENT": False,
            "BERGER_ALTERNATIVE_COMPANION_NO_GO": False,
            "BERGER_CAUCHY_KREIN_FORM": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": (
            "CHANGE_THE_NORMALIZED_COMPANION_OR_A104_OR_CONSTRUCT_AN_EXTENSION "
            "WITH_AT_LEAST_5_DEGREE_0_AND_1_DEGREE_PLUS1_ROWS"
        ),
        "claim_boundary": (
            "This exact obstruction is complete only for finite-order support-local "
            "degree-plus-one lifts on the frozen 104-row formal Cauchy graph satisfying "
            "the normalized q52 solution-map identity. It strengthens rejection of one "
            "candidate to nonexistence in that declared class because compatibility "
            "makes the candidate unique. The six-row extension bound is necessary, "
            "not sufficient. The result does not obstruct changed companions, changed "
            "A104 data or larger carriers; it supplies no Krein form, real structure, "
            "Hadamard state, positivity, QME, particle or scattering theorem."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=quantum-weyl:. python3 d_quotient_classical/causal_transfer/berger_q26_cauchy_bv_carrier_obstruction.py --check --guards",
                "PYTHONPATH=quantum-weyl:. python3 d_quotient_classical/causal_transfer/verify_berger_q26_cauchy_bv_carrier_obstruction.py",
                "PYTHONPATH=quantum-weyl:. python3 -m unittest d_quotient_classical.causal_transfer.tests.test_berger_q26_cauchy_bv_carrier_obstruction",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-q26-cauchy-bv-carrier-obstruction-v1.schema.json -d d_quotient_classical/certificates/BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1.json",
            ],
        },
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    replay = value["exact_replay"]
    if replay["q_Cauchy_square_nonzero_sparse_entries"] != 157:
        raise ValueError("square control drifted")
    if replay["A104_q_Cauchy_commutator_nonzero_sparse_entries"] != 207:
        raise ValueError("commutator control drifted")
    if replay["q_Cauchy_squared_zero"] or replay["A104_commutes_with_q_Cauchy"]:
        raise ValueError("rejected compatible lift was promoted")
    bound = value["extension_lower_bound"]
    if (
        bound["degree_0_added_rows_at_least"],
        bound["degree_plus1_added_rows_at_least"],
        bound["total_added_rows_at_least"],
        bound["status"],
    ) != (5, 1, 6, "NECESSARY_NOT_SUFFICIENT"):
        raise ValueError("extension lower bound drifted")
    for forbidden in (
        "BERGER_6_ROW_EXTENSION_SUFFICIENT",
        "BERGER_ALTERNATIVE_COMPANION_NO_GO",
        "BERGER_CAUCHY_KREIN_FORM",
        "BERGER_HADAMARD_DATA",
        "QUANTUM_CLAIM",
    ):
        if value["claim_flags"][forbidden]:
            raise ValueError(f"forbidden promotion: {forbidden}")


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Berger retained-26 Cauchy BV carrier obstruction

The normalized retained-26 companion solution map does **not** descend to a
BRST differential on the frozen 104-row stationary Cauchy carrier.

## Complete declared class

The class consists of finite-order support-local degree-\(+1\) PBW
differential operators on the frozen 104 rows satisfying

\[
q_C=\operatorname{ev}_0\,q_{52}^{\rm normalized}\,
       \operatorname{Sol}_{A_{104}}
\]

on every formal Cauchy datum.  Since evaluation at the initial slice is the
identity on those data, this compatibility identity fixes \(q_C\) uniquely.
It therefore closes the search over this declared class at every finite
differential order; it is not merely a bounded ansatz search.

The unique operator is the already serialized canonical graph candidate.
An independent classical consumer reproduces exactly

\[
\#\operatorname{supp}(q_C^2)=157,\qquad
\#\operatorname{supp}([A_{104},q_C])=207.
\]

Both required identities fail.  Adding cyclic-pairing, real-involution or
graded-adjoint requirements cannot repair an already empty class.

## Rigorous enlargement bound

The Berger derivative algebra is noncommutative, so a scalar symbol
substitution is not multiplicative and cannot justify a factorization-rank
claim.  The certificate instead uses its exact three-dimensional adjoint
representation at

\[
\alpha_B=2,\qquad u=1,\qquad v=3.
\]

The represented square has ranks \(13\) in degree \(-1\to+1\) and \(3\) in
degree \(0\to+2\).  If an enlarged degree-\(+1\) differential cancels the old
square through new rows, the old block factors through the new intermediate
degree.  Hence it needs at least five new degree-zero rows and one new
degree-\(+1\) row: at least six rows in total.

This bound is necessary, not sufficient.  No six-row construction or
evolution-compatible extension is claimed.

## Consequence for the Quantum request

The frozen 104-row normalized graph cannot be the requested BRST-compatible
Cauchy/Krein carrier.  The next construction must either change the
normalized companion/\(A_{104}\) data or enlarge the carrier subject to the
certified degreewise lower bound.  This result does not construct a Krein
form, real structure, Hadamard state, positivity, a QME or a quantum theory.

CLOSE-OUT: OBSTRUCTED — the exact no-go in the complete declared frozen-graph lift class is certified; alternative companions and larger carriers remain open.
EVIDENCE: d_quotient_classical/certificates/BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1.json
"""


def _guards(value: dict[str, Any]) -> None:
    mutations = []
    for path, replacement in (
        (("exact_replay", "q_Cauchy_square_nonzero_sparse_entries"), 156),
        (("exact_replay", "A104_q_Cauchy_commutator_nonzero_sparse_entries"), 206),
        (("extension_lower_bound", "total_added_rows_at_least"), 5),
        (("claim_flags", "BERGER_HADAMARD_DATA"), True),
    ):
        mutant = deepcopy(value)
        mutant[path[0]][path[1]] = replacement
        try:
            validate(mutant)
        except Exception:
            mutations.append(True)
        else:
            mutations.append(False)
    if not all(mutations):
        raise AssertionError("a mutation guard survived")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    payload = build_payload()
    value = build()
    validate(value)
    if args.guards:
        _guards(value)
    rendered_payload = _render(payload)
    rendered_value = _render(value)
    if args.check:
        if PAYLOAD.read_text() != rendered_payload:
            raise SystemExit(f"generated payload drifted: {PAYLOAD}")
        if OUTPUT.read_text() != rendered_value:
            raise SystemExit(f"certificate drifted: {OUTPUT}")
        if REPORT.read_text() != _report():
            raise SystemExit(f"report drifted: {REPORT}")
    else:
        PAYLOAD.parent.mkdir(parents=True, exist_ok=True)
        PAYLOAD.write_text(rendered_payload)
        OUTPUT.write_text(rendered_value)
        REPORT.write_text(_report())
    print("BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1: PASS")


if __name__ == "__main__":
    main()
