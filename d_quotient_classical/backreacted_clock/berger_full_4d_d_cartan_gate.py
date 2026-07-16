#!/usr/bin/env python3
"""Fail-closed dependency gate for the full four-dimensional D-Cartan solve."""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT


Q1_PATH = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
D_PATH = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json"
Q2_PATH = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_FULL_4D_D_CARTAN_GATE.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-full-4d-D-Cartan-gate.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-full-4d-D-Cartan-gate-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


@dataclass(frozen=True)
class BergerFull4DDCartanGate:
    payload: dict[str, object]

    @classmethod
    def build(cls) -> "BergerFull4DDCartanGate":
        q1 = json.loads(Q1_PATH.read_text())
        d_action = json.loads(D_PATH.read_text())
        q2 = json.loads(Q2_PATH.read_text())
        if q1["flags"]["BERGER_NONMINIMAL_COMPLETION"] is not True:
            raise AssertionError("complete 54-row q1 prerequisite dropped")
        if d_action["flags"]["BERGER_LOCAL_D_ACTION_EQUIVARIANT"] is not True:
            raise AssertionError("local D prerequisite dropped")
        if q2["flags"]["CLASSICAL_SUPPORT_LOCAL_Q2"] is not True:
            raise AssertionError("support-local q2 prerequisite dropped")
        payload: dict[str, object] = {
            "schema": "pure-weyl-berger-full-4d-D-Cartan-gate-v1",
            "result_id": "BERGER_FULL_4D_D_CARTAN_GATE",
            "setting_id": q1["setting_id"],
            "claim_status": "INPUTS_COMPLETE_UNARY_EXISTENCE_OPEN",
            "dependency_tags": ["LOCAL-ALGEBRAIC"],
            "dependency_refs": {
                "classical_unary_q1": _dependency(Q1_PATH),
                "local_D_action": _dependency(D_PATH),
                "classical_binary_q2": _dependency(Q2_PATH),
            },
            "gate_order": [
                {
                    "gate": "BERGER_UNARY_D_CARTAN_EXISTENCE_FULL_4D",
                    "identity": "q1 iota_D^(1)+iota_D^(1) q1=D",
                    "required_properties": [
                        "degree_minus_one",
                        "finite_order_support_local",
                        "graded_cyclic",
                        "all_54_rows",
                    ],
                    "retained_reduction": "iota_D,54^(1)=S_cl D_54+iota_cl iota_D,26^(1) pi_cl",
                    "failure_output": "normalized retained-core obstruction; scoped to the declared finite-order local class",
                },
                {
                    "gate": "BERGER_ARITY_TWO_D_CARTAN_SOURCE_FULL_4D",
                    "identity": "A_D^(2)=[q2,iota_D^(1)]",
                    "required_properties": [
                        "q1_closed",
                        "graded_cyclic",
                        "D_equivariant",
                        "all_54_rows",
                    ],
                },
                {
                    "gate": "BERGER_ARITY_TWO_D_CARTAN_FULL_4D",
                    "identity": "[q1,iota_D^(2)]=-[q2,iota_D^(1)]",
                    "required_properties": [
                        "degree_minus_one_bilinear",
                        "finite_order_support_local",
                        "graded_symmetric",
                        "graded_cyclic",
                        "all_54_rows",
                    ],
                },
            ],
            "forbidden_shortcuts": [
                "D_inverse",
                "Fourier_or_harmonic_projector",
                "inverse_Laplacian_or_inverse_curl",
                "promotion_from_the_reduced_mode_fixture",
                "global_nonexistence_claim_from_one_failed_candidate",
            ],
            "exact_checks": {
                "complete_54_row_q1_input": True,
                "complete_54_row_D_input": True,
                "complete_54_row_q2_input": True,
                "unary_gate_precedes_source_gate": True,
                "source_gate_precedes_arity_two_gate": True,
                "arity_two_promotion_requires_unary_promotion": True,
                "failed_candidate_scope_is_not_global_nonexistence": True,
            },
            "flags": {
                "BERGER_FULL_4D_D_CARTAN_INPUTS_COMPLETE": True,
                "BERGER_UNARY_D_CARTAN_EXISTENCE_FULL_4D": False,
                "BERGER_ARITY_TWO_D_CARTAN_SOURCE_FULL_4D": False,
                "BERGER_ARITY_TWO_D_CARTAN_FULL_4D": False,
            },
            "next_gate": "BERGER_UNARY_D_CARTAN_EXISTENCE_FULL_4D",
            "claim_boundary": (
                "This dependency certificate proves only that q1, D, and q2 inputs are complete "
                "and enforces the unary-before-binary Cartan order. It does not construct "
                "iota_D^(1) or iota_D^(2). Failure in a declared candidate class is not global "
                "nonexistence of every Cartan homotopy."
            ),
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        p = self.payload
        if p["next_gate"] != "BERGER_UNARY_D_CARTAN_EXISTENCE_FULL_4D":
            raise AssertionError("unary Cartan gate was bypassed")
        if not all(p["exact_checks"].values()):
            raise AssertionError("Cartan dependency check dropped")
        flags = p["flags"]
        if flags["BERGER_FULL_4D_D_CARTAN_INPUTS_COMPLETE"] is not True:
            raise AssertionError("complete Cartan inputs not recorded")
        if flags["BERGER_ARITY_TWO_D_CARTAN_SOURCE_FULL_4D"] and not flags[
            "BERGER_UNARY_D_CARTAN_EXISTENCE_FULL_4D"
        ]:
            raise AssertionError("Cartan source promoted before unary existence")
        if flags["BERGER_ARITY_TWO_D_CARTAN_FULL_4D"] and not (
            flags["BERGER_UNARY_D_CARTAN_EXISTENCE_FULL_4D"]
            and flags["BERGER_ARITY_TWO_D_CARTAN_SOURCE_FULL_4D"]
        ):
            raise AssertionError("arity-two Cartan promoted before prerequisites")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Full four-dimensional Berger D-Cartan dependency gate

The complete 54-row (q_1), local (D)-action, and support-local (q_2) are
available.  They do not by themselves supply a Cartan homotopy.  The first
required theorem is the unary identity

\[
q_1\iota_D^{(1)}+\iota_D^{(1)}q_1=D.
\]

Using the certified 54-to-26 contraction, the efficient lift is

\[
\iota_{D,54}^{(1)}
=S_{\rm cl}D_{54}
+\iota_{\rm cl}\iota_{D,26}^{(1)}\pi_{\rm cl}.
\]

Only after that gate passes may the binary source

\[
A_D^{(2)}=[q_2,\iota_D^{(1)}]
\]

be formed and tested for (q_1)-closure, cyclicity and (D)-equivariance.
The final solve is

\[
[q_1,\iota_D^{(2)}]=-[q_2,\iota_D^{(1)}].
\]

All three downstream flags remain false. A failure in one finite-order local
ansatz is scoped to that ansatz and is not a global nonexistence theorem.
"""


def _write(result: BergerFull4DDCartanGate) -> None:
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: BergerFull4DDCartanGate) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise SystemExit(f"stale certificate: {CERTIFICATE_PATH}")
    if REPORT_PATH.read_text() != result.report_text():
        raise SystemExit(f"stale report: {REPORT_PATH}")


def _guards(result: BergerFull4DDCartanGate) -> None:
    for name, mutate in (
        (
            "source before unary",
            lambda p: p["flags"].update(
                {"BERGER_ARITY_TWO_D_CARTAN_SOURCE_FULL_4D": True}
            ),
        ),
        (
            "arity two before prerequisites",
            lambda p: p["flags"].update(
                {"BERGER_ARITY_TWO_D_CARTAN_FULL_4D": True}
            ),
        ),
        (
            "skip unary next gate",
            lambda p: p.update({"next_gate": "BERGER_ARITY_TWO_D_CARTAN_FULL_4D"}),
        ),
    ):
        mutant = deepcopy(result.payload)
        mutate(mutant)
        try:
            BergerFull4DDCartanGate(mutant).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard failed: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = BergerFull4DDCartanGate.build()
    if args.check:
        _check(result)
    else:
        _write(result)
    if args.guards:
        _guards(result)
    print("full 4D D-Cartan inputs: COMPLETE")
    print("unary D-Cartan existence: OPEN")
    print("arity-two D-Cartan: BLOCKED BY UNARY GATE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
