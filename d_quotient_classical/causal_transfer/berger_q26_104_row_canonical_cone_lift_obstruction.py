#!/usr/bin/env python3
"""Obstruct the canonical rank-saturating 104-row doubled-cone lift.

The sharp module bound permits one free copy of the frozen 104-row carrier.
The first normal form to test is the doubled cone

    Q_J = [[q,-q],[q,-q]].

It is support-local, degree +1, has the required old-old block, and squares
to zero identically.  Keeping the old-old evolution block equal to A while
using the corresponding upper-triangular cone evolution reduces exact
equivariance to D q = q A.  This module proves that the lift equation has no
solution already in the one-dimensional rational Berger representation.

The result is deliberately scoped: it obstructs the canonical cone normal
form and its free-adjoint orientation, not every 104-row off-diagonal
factorization.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
RESULT_ID = "BERGER_Q26_104_ROW_CANONICAL_CONE_LIFT_OBSTRUCTION_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
PAYLOAD = (
    ROOT
    / "d_quotient_classical/generated/"
    "berger_q26_104_row_canonical_cone_lift_obstruction_v1/"
    "rational_trivial_representation_witness.json"
)
REPORT = (
    ROOT
    / "d_quotient_classical/reports/"
    "berger-q26-104-row-canonical-cone-lift-obstruction-v1.md"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "berger-q26-104-row-canonical-cone-lift-obstruction-v1.schema.json"
)
VERIFIER = (
    HERE / "verify_berger_q26_104_row_canonical_cone_lift_obstruction.py"
)
TESTS = (
    HERE
    / "tests/test_berger_q26_104_row_canonical_cone_lift_obstruction.py"
)
LOWER_BOUND = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_Q26_FINITE_ROW_MODULE_CLOSURE_LOWER_BOUND_V1.json"
)
LOWER_PAYLOAD = (
    ROOT
    / "d_quotient_classical/generated/"
    "berger_q26_finite_row_module_closure_v1/spin4_closure_witness.json"
)
Q_PATH = (
    ROOT
    / "quantum-weyl/lorentzian/generated/"
    "berger_canonical_graph_q_cauchy_obstruction/"
    "rejected_candidate_q_Cauchy_104.json"
)
A_PATH = (
    ROOT
    / "quantum-weyl/lorentzian/generated/"
    "berger_a104_endpoint_completion/global_A104.json"
)
SPECIALIZATION = {"alpha_B": 2, "u": 1, "v": 3}
EXPECTED = {
    "rank_q": 34,
    "rank_row_stack_q_qA": 35,
    "rank_column_stack_q_Aq": 35,
}
RIGHT_VECTOR = {6: -33, 10: -111, 15: 144, 16: -57, 20: 57}
RIGHT_OUTPUT = {92: -1022, 95: -1022, 97: -1022}
LEFT_VECTOR = {92: -27, 97: 27}
LEFT_OUTPUT = {
    6: 108,
    10: -4,
    13: -4,
    15: 28,
    20: -16,
    23: -16,
    25: -16,
}


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


def _load_constant_matrix(path: Path) -> sp.Matrix:
    record = _load(path)
    body = {"shape": record.get("shape"), "entries": record.get("entries")}
    if record.get("sha256") != _digest(body):
        raise AssertionError(f"internal operator hash drifted: {path}")
    if record.get("shape") != [104, 104]:
        raise AssertionError(f"operator shape drifted: {path}")
    alpha_B, u, v = sp.symbols("alpha_B u v")
    substitutions = {
        alpha_B: sp.Rational(SPECIALIZATION["alpha_B"]),
        u: sp.Rational(SPECIALIZATION["u"]),
        v: sp.Rational(SPECIALIZATION["v"]),
    }
    result = sp.zeros(104)
    for row, column, terms in record["entries"]:
        for exponents, coefficient_text in terms:
            if sum(exponents):
                continue
            coefficient = sp.sympify(
                coefficient_text,
                locals={"alpha_B": alpha_B, "u": u, "v": v},
            )
            result[row, column] += coefficient.subs(substitutions)
    return result


def _column(entries: dict[int, int]) -> sp.Matrix:
    value = sp.zeros(104, 1)
    for row, coefficient in entries.items():
        value[row, 0] = coefficient
    return value


def _sparse_vector(value: sp.Matrix) -> list[list[int | str]]:
    if value.cols != 1:
        raise ValueError("expected column vector")
    return [
        [row, str(value[row, 0])]
        for row in range(value.rows)
        if value[row, 0]
    ]


def _sparse_row(value: sp.Matrix) -> list[list[int | str]]:
    if value.rows != 1:
        raise ValueError("expected row vector")
    return [
        [column, str(value[0, column])]
        for column in range(value.cols)
        if value[0, column]
    ]


@lru_cache(maxsize=1)
def exact_audit() -> dict[str, Any]:
    q = _load_constant_matrix(Q_PATH)
    evolution = _load_constant_matrix(A_PATH)
    z = _column(RIGHT_VECTOR)
    right_output = q * evolution * z
    ell = _column(LEFT_VECTOR)
    left_output = ell.T * evolution * q
    checks = {
        "right_witness_in_kernel_q": q * z == sp.zeros(104, 1),
        "right_witness_qA_nonzero": right_output != sp.zeros(104, 1),
        "right_witness_output_matches": right_output
        == _column(RIGHT_OUTPUT),
        "left_witness_annihilates_q": ell.T * q == sp.zeros(1, 104),
        "left_witness_Aq_nonzero": left_output != sp.zeros(1, 104),
        "left_witness_output_matches": left_output
        == _column(LEFT_OUTPUT).T,
    }
    ranks = {
        "rank_q": int(q.rank()),
        "rank_row_stack_q_qA": int(q.col_join(q * evolution).rank()),
        "rank_column_stack_q_Aq": int(
            q.row_join(evolution * q).rank()
        ),
    }
    if ranks != EXPECTED or not all(checks.values()):
        raise AssertionError(
            f"canonical cone lift audit drifted: {ranks}, {checks}"
        )
    return {
        "schema": (
            "pure-weyl-berger-q26-canonical-cone-rational-witness-v1"
        ),
        "result_id": (
            "BERGER_Q26_CANONICAL_CONE_RATIONAL_TRIVIAL_"
            "REPRESENTATION_WITNESS_V1"
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
            "relation_check": (
                "all Berger commutators and their right-hand sides map to 0"
            ),
        },
        "ranks": ranks,
        "right_lift_Dq_equals_qA": {
            "status": "INCONSISTENT",
            "criterion": "ker(q) subset ker(q*A)",
            "witness_z": _sparse_vector(z),
            "q_z": [],
            "q_A_z": _sparse_vector(right_output),
            "cokernel_rank": ranks["rank_row_stack_q_qA"]
            - ranks["rank_q"],
        },
        "left_adjoint_lift_Aq_equals_qD": {
            "status": "INCONSISTENT",
            "criterion": "col(A*q) subset col(q)",
            "witness_ell": _sparse_vector(ell),
            "ell_transpose_q": [],
            "ell_transpose_A_q": _sparse_row(left_output),
            "cokernel_rank": ranks["rank_column_stack_q_Aq"]
            - ranks["rank_q"],
        },
        "checks": checks,
    }


def _artifact(path: Path, artifact_id: str) -> dict[str, str]:
    return {
        "artifact_id": artifact_id,
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def build() -> dict[str, Any]:
    lower = _load(LOWER_BOUND)
    if (
        lower.get("result_id")
        != "BERGER_Q26_FINITE_ROW_MODULE_CLOSURE_LOWER_BOUND_V1"
        or lower["classification"]["minimum_added_free_rows_at_least"]
        != 104
        or lower["classification"]["one_hundred_four_row_extension_sufficient"]
    ):
        raise AssertionError("104-row lower-bound input drifted")
    audit = exact_audit()
    payload_text = json.dumps(audit, indent=2, sort_keys=True) + "\n"
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": (
            "pure-weyl-berger-q26-104-row-canonical-cone-"
            "lift-obstruction-v1"
        ),
        "result_id": RESULT_ID,
        "result_state": (
            "CANONICAL_104_ROW_DOUBLED_CONE_EVOLUTION_LIFT_"
            "AND_FREE_ADJOINT_ORIENTATION_EMPTY"
        ),
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "scope": {
            "theory": "retained minimal pure-Weyl Berger BV complex",
            "background": "fixed rational positive Berger clock",
            "boundaries": "R_t x compact Berger S3; no spatial boundary",
            "charge_sector": (
                "unquotiented retained-26 formal companion/Cauchy carrier"
            ),
            "carrier": (
                "frozen 104 rows plus its one-copy 104-row free cone"
            ),
            "degree": (
                "old and new profiles both (-1:12,0:40,1:40,2:12)"
            ),
            "parity": "inherited BV parity; free-adjoint orientation included",
            "ell": "not harmonic-reduced",
            "m": "not harmonic-reduced",
            "k": "all finite-order Berger PBW derivatives",
            "omega": "stationary A104 formal evolution; no spectral split",
        },
        "pinned_inputs": {
            "module_lower_bound": _artifact(
                LOWER_BOUND,
                "BERGER_Q26_FINITE_ROW_MODULE_CLOSURE_LOWER_BOUND_V1",
            ),
            "module_closure_witness": _artifact(
                LOWER_PAYLOAD,
                "BERGER_Q26_SPIN4_MODULE_CLOSURE_WITNESS_V1",
            ),
            "q_Cauchy": _artifact(
                Q_PATH, "rejected_candidate_q_Cauchy_104"
            ),
            "A104": _artifact(A_PATH, "global_A104"),
        },
        "declared_completion_architecture": {
            "name": "RANK_SATURATING_CANONICAL_DOUBLED_CONE",
            "row_origin": (
                "one free copy of the full defect/free-dual module forced "
                "by the 104-row lower bound"
            ),
            "q_ext": "Q_J=[[q,-q],[q,-q]]",
            "q_ext_old_old": "q",
            "q_ext_squared_zero": True,
            "evolution_ansatz": (
                "A_D=[[A,D-A],[0,D]], with D degree zero and support-local"
            ),
            "commutator_formula": (
                "[A_D,Q_J]=[[Dq-qA,-Dq+qA],"
                "[Dq-qA,-Dq+qA]]"
            ),
            "equivariance_condition": "Dq=qA",
            "free_adjoint_condition": (
                "the dual orientation additionally requires Aq=qD^vee"
            ),
            "differential_order": (
                "D is allowed arbitrary finite PBW order; evaluation of any "
                "such D would still solve the specialized matrix equation"
            ),
            "real_involution": (
                "standard rational conjugation; not reached because the "
                "evolution lift equation is inconsistent"
            ),
            "retained_solution_map_incidence": (
                "old-old q and A blocks are fixed exactly; no projection or "
                "quotient removes their entries"
            ),
        },
        "rational_obstruction": {
            "payload": {
                "artifact_id": audit["result_id"],
                "path": str(PAYLOAD.relative_to(ROOT)),
                "sha256": hashlib.sha256(payload_text.encode()).hexdigest(),
            },
            "right_lift": audit["right_lift_Dq_equals_qA"],
            "left_adjoint_lift": audit["left_adjoint_lift_Aq_equals_qD"],
            "proof": (
                "A rational PBW solution evaluates under every multiplicative "
                "rational representation. In the trivial derivative "
                "representation, z lies in ker(q) but q*A*z is nonzero, so "
                "D*q=q*A is impossible. Independently ell^T*q=0 while "
                "ell^T*A*q is nonzero, obstructing the free-adjoint "
                "orientation."
            ),
        },
        "decoupled_mutation": {
            "new_blocks": "ZERO",
            "old_q_nonzero_entries": 1018,
            "old_A_nonzero_entries": 470,
            "q_square_defects": 157,
            "A_q_commutator_defects": 207,
            "status": "REPRODUCES_FROZEN_REJECTED_CONTROL",
        },
        "classification": {
            "canonical_doubled_cone_q_nilpotent": True,
            "canonical_doubled_cone_evolution_lift_exists": False,
            "free_adjoint_cone_orientation_exists": False,
            "all_104_row_completions_obstructed": False,
            "minimum_208_row_physical_carrier_constructed": False,
            "physical_Cauchy_pairing_constructed": False,
            "real_involution_on_accepted_carrier_constructed": False,
            "Hadamard_or_quantum_claim": False,
        },
        "next_gate": (
            "SOLVE_NON_CONE_104_ROW_OFF_DIAGONAL_FACTORIZATIONS_OR_"
            "EXPORT_THEIR_NEXT_DEFECT_ORBIT"
        ),
        "claim_boundary": (
            "This exact rational theorem obstructs the rank-saturating "
            "canonical doubled-cone strictification and its free-adjoint "
            "orientation while keeping the old q_Cauchy and A104 blocks. "
            "It is not a theorem about every 104-row off-diagonal "
            "factorization and does not raise the global 104-row lower bound. "
            "It constructs no accepted Cauchy/Krein pairing, retained "
            "contraction, Hadamard state, positivity, QME, particle, "
            "scattering or unitarity result."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                (
                    "PYTHONPATH=. python3 -m d_quotient_classical."
                    "causal_transfer."
                    "berger_q26_104_row_canonical_cone_lift_obstruction "
                    "--check --guards"
                ),
                (
                    "PYTHONPATH=. python3 -m d_quotient_classical."
                    "causal_transfer."
                    "verify_berger_q26_104_row_canonical_cone_lift_obstruction"
                ),
                (
                    "PYTHONPATH=. python3 -m unittest "
                    "d_quotient_classical.causal_transfer.tests."
                    "test_berger_q26_104_row_canonical_cone_lift_obstruction"
                ),
                (
                    "npx --yes ajv-cli@5 validate --spec=draft2020 "
                    "--strict=true -s d_quotient_classical/schema/"
                    "berger-q26-104-row-canonical-cone-lift-obstruction-"
                    "v1.schema.json -d d_quotient_classical/certificates/"
                    f"{RESULT_ID}.json"
                ),
            ],
        },
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Berger q26 canonical 104-row cone-lift obstruction

The sharp lower bound permits one free 104-row copy of the frozen carrier.
The canonical rank-saturating strictification is

\[
Q_J=\begin{pmatrix}q&-q\\q&-q\end{pmatrix},
\qquad Q_J^2=0.
\]

It keeps the old-old \(q\) block and uses exactly the forced degree profile.
Keeping the old-old evolution block equal to \(A_{104}\) gives the complete
upper-cone evolution ansatz

\[
A_D=\begin{pmatrix}A&D-A\\0&D\end{pmatrix}.
\]

Exact multiplication reduces equivariance to

\[
Dq=qA.
\]

This equation is already inconsistent in the rational one-dimensional Berger
representation \(e_0=e_1=e_2=e_3=0\) at
\((\alpha_B,u,v)=(2,1,3)\).  The specialized ranks are

\[
\operatorname{rank}q=34,\qquad
\operatorname{rank}\binom q{qA}=35.
\]

The payload stores an explicit \(z\) with \(qz=0\) but \(qAz\ne0\).
The adjoint orientation fails independently:

\[
\operatorname{rank}(q\;\;Aq)=35,
\]

with an explicit left-null witness for \(q\) that does not annihilate \(Aq\).
A rational PBW solution would specialize to solutions of both matrix
equations, so these are exact operator obstructions for this architecture.

The result does not obstruct general non-cone 104-row off-diagonal
factorizations.  Those are the next gate.  No accepted physical pairing,
retained contraction, Hadamard or quantum object is constructed.
"""


def _guards(value: dict[str, Any]) -> None:
    mutations = [
        ("classification", "canonical_doubled_cone_evolution_lift_exists", True),
        ("classification", "all_104_row_completions_obstructed", True),
        ("classification", "Hadamard_or_quantum_claim", True),
    ]
    for section, field, replacement in mutations:
        mutant = deepcopy(value)
        mutant[section][field] = replacement
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation survived: {section}.{field}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = exact_audit()
    value = build()
    validate(value)
    if args.write:
        PAYLOAD.parent.mkdir(parents=True, exist_ok=True)
        PAYLOAD.write_text(_render(payload))
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check:
        if PAYLOAD.read_text() != _render(payload):
            raise AssertionError("canonical cone witness payload drifted")
        if OUTPUT.read_text() != _render(value):
            raise AssertionError("canonical cone certificate drifted")
        if REPORT.read_text() != _report():
            raise AssertionError("canonical cone report drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
