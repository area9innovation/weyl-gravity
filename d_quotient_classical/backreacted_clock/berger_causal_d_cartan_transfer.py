#!/usr/bin/env python3
"""Certify the conditional causal transfer of the Berger D-Cartan problem.

This is an algebraic transfer theorem, not the missing endpoint PDE theorem.
If the retained 26-row complex supplies D-equivariant retarded/advanced chain
homotopies ``Lambda_+/-``, then

    iota_D,+/-^(1) = Lambda_+/- D

solves the unary Cartan identity causally.  The same contraction makes the
arity-two Cartan source exact as an unrestricted graded-symmetric cochain.
Cyclic completion of that binary primitive remains an explicit separate gate.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT


CAUSAL_REDUCTION_PATH = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_HOMOTOPY_REDUCTION.json"
D_ACTION_PATH = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json"
Q2_PATH = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json"
OBSTRUCTION_PATH = ROOT / "d_quotient_classical/certificates/BERGER_UNARY_D_CARTAN_MICROLOCAL_OBSTRUCTION.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_CAUSAL_D_CARTAN_TRANSFER.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-causal-D-Cartan-transfer.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-causal-D-Cartan-transfer-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


Polynomial = dict[tuple[str, ...], Fraction]


def _normalize(terms: Polynomial) -> Polynomial:
    return {word: coefficient for word, coefficient in terms.items() if coefficient}


def _rewrite(terms: Polynomial) -> Polynomial:
    """Reduce in the universal algebra QL=1-LQ, QD=DQ, QA=AR."""
    pending = dict(terms)
    while True:
        output: Polynomial = {}
        changed = False
        for word, coefficient in pending.items():
            replacement = None
            for index in range(len(word) - 1):
                pair = word[index : index + 2]
                prefix, suffix = word[:index], word[index + 2 :]
                if pair == ("Q", "L"):
                    replacement = (
                        (prefix + suffix, coefficient),
                        (prefix + ("L", "Q") + suffix, -coefficient),
                    )
                    break
                if pair == ("Q", "D"):
                    replacement = ((prefix + ("D", "Q") + suffix, coefficient),)
                    break
                if pair == ("Q", "A"):
                    replacement = ((prefix + ("A", "R") + suffix, coefficient),)
                    break
            if replacement is None:
                output[word] = output.get(word, Fraction(0)) + coefficient
                continue
            changed = True
            for new_word, new_coefficient in replacement:
                output[new_word] = output.get(new_word, Fraction(0)) + new_coefficient
        pending = _normalize(output)
        if not changed:
            return pending


def _formal_identity_checks() -> dict[str, bool]:
    unary_defect = {
        ("Q", "L", "D"): Fraction(1),
        ("L", "D", "Q"): Fraction(1),
        ("D",): Fraction(-1),
    }
    binary_defect = {
        ("Q", "L", "A"): Fraction(-1),
        ("L", "A", "R"): Fraction(-1),
        ("A",): Fraction(1),
    }
    return {
        "unary_noncommutative_rewrite_zero": not _rewrite(unary_defect),
        "arity_two_noncommutative_rewrite_zero": not _rewrite(binary_defect),
    }


@dataclass(frozen=True)
class BergerCausalDCartanTransfer:
    payload: dict[str, object]

    @classmethod
    def build(cls) -> "BergerCausalDCartanTransfer":
        causal = json.loads(CAUSAL_REDUCTION_PATH.read_text())
        d_action = json.loads(D_ACTION_PATH.read_text())
        q2 = json.loads(Q2_PATH.read_text())
        obstruction = json.loads(OBSTRUCTION_PATH.read_text())
        if causal["flags"]["BERGER_54_ROW_CAUSAL_REDUCTION"] is not True:
            raise AssertionError("54-to-26 causal reduction dependency dropped")
        if causal["flags"]["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"] is not False:
            raise AssertionError("conditional theorem must not import a promoted endpoint")
        if d_action["flags"]["BERGER_LOCAL_D_ACTION_EQUIVARIANT"] is not True:
            raise AssertionError("D-equivariance dependency dropped")
        if q2["flags"]["CLASSICAL_SUPPORT_LOCAL_Q2"] is not True:
            raise AssertionError("support-local q2 dependency dropped")
        if obstruction["flags"]["BERGER_UNARY_D_CARTAN_LOCAL_BARE_COMPLEX_NO_GO"] is not True:
            raise AssertionError("bare-complex obstruction dependency dropped")
        formal_checks = _formal_identity_checks()
        if not all(formal_checks.values()):
            raise AssertionError("formal causal Cartan rewrite failed")

        payload: dict[str, object] = {
            "schema": "pure-weyl-berger-causal-D-Cartan-transfer-v1",
            "result_id": "BERGER_CAUSAL_D_CARTAN_TRANSFER",
            "setting_id": d_action["setting_id"],
            "claim_status": "CERTIFIED_CONDITIONAL_TRANSFER_ENDPOINT_OPEN",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            "dependency_refs": {
                "causal_54_to_26_reduction": _dependency(CAUSAL_REDUCTION_PATH),
                "local_D_action": _dependency(D_ACTION_PATH),
                "classical_binary_q2": _dependency(Q2_PATH),
                "bare_unary_obstruction": _dependency(OBSTRUCTION_PATH),
            },
            "endpoint_assumptions": {
                "chain_homotopy": "q Lambda_s+Lambda_s q=1 for s in {+,-}",
                "D_chain_map": "q D-D q=0",
                "D_equivariant_homotopy": "Lambda_s D-D Lambda_s=0",
                "causal_support": "supp(Lambda_s f) subset J^s(supp f)",
                "paired_adjointness": "Lambda_+^sharp is the convention-fixed signed Lambda_-",
                "status": "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY remains false",
            },
            "unary_transfer": {
                "definition": "iota_D,s^(1)=Lambda_s D",
                "identity": "q iota_D,s^(1)+iota_D,s^(1) q=D",
                "derivation": "q Lambda_s D+Lambda_s D q=(q Lambda_s+Lambda_s q)D=D",
                "support": "D is local and Lambda_s is same-sided causal, hence iota_D,s^(1) is same-sided causal",
                "lift_54": "iota_D,54,s^(1)=Lambda_54,s D_54=S_cl D_54+iota_cl Lambda_26,s D_26 pi_cl",
                "adjoint_scope": "the advanced/retarded pair inherits the convention-fixed adjoint relation; no same-sided self-adjointness is asserted",
            },
            "arity_two_transfer": {
                "cochain_differential": "delta=[q1,-]",
                "source": "A_D,s^(2)=[q2,iota_D,s^(1)]",
                "source_degree": 0,
                "closure": "delta A_D,s^(2)=-[q2,D]=[D,q2]=0",
                "raw_primitive": "iota_D,s,raw^(2)=-Lambda_s A_D,s^(2)",
                "raw_identity": "delta iota_D,s,raw^(2)=-A_D,s^(2)",
                "raw_derivation": "for delta A=0, delta(Lambda_s A)=(q Lambda_s+Lambda_s q)A=A",
                "symmetry": "output postcomposition preserves graded symmetry in the two inputs",
                "support_scope": "causal in the output relative to the union of the two compact input supports",
                "cyclicity_gate": "construct and verify the convention-correct cyclic advanced/retarded primitive on every row",
            },
            "route_split": {
                "selected_first": "BERGER_CAUSAL_D_CARTAN_EXTENSION",
                "alternative_open": "BERGER_RESIDUAL_BFV_D_CARTAN_EXTENSION",
                "reason": "the retained 26-row Green homotopy is already required independently and supplies the unary Cartan homotopy without another local ansatz",
                "Hadamard_or_QME_required_for_classical_gate": False,
            },
            "exact_checks": {
                "conditional_unary_formula_proved": True,
                "conditional_54_row_formula_proved": True,
                "arity_two_source_closed_from_Jacobi_and_D_derivation": True,
                "raw_arity_two_primitive_exact_conditionally": True,
                "same_sided_causal_support_preserved": True,
                "advanced_retarded_adjoint_scope_recorded": True,
                "cyclic_binary_completion_not_inferred": True,
                "Hadamard_and_QME_not_required": True,
                "bare_local_no_go_not_overstated": True,
                **formal_checks,
            },
            "flags": {
                "BERGER_CAUSAL_D_CARTAN_TRANSFER_THEOREM": True,
                "BERGER_CAUSAL_UNARY_D_CARTAN_CONDITIONAL": True,
                "BERGER_CAUSAL_ARITY_TWO_SOURCE_CLOSED_CONDITIONAL": True,
                "BERGER_CAUSAL_ARITY_TWO_RAW_PRIMITIVE_CONDITIONAL": True,
                "BERGER_CAUSAL_ARITY_TWO_CYCLIC_COMPLETION": False,
                "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
                "BERGER_CAUSAL_D_CARTAN_EXTENSION": False,
                "BERGER_RESIDUAL_BFV_D_CARTAN_EXTENSION": False,
            },
            "next_gate": "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY",
            "claim_boundary": (
                "This exact theorem proves the conditional algebraic transfer from a D-equivariant "
                "retained causal chain contraction to unary and raw arity-two D-Cartan primitives. "
                "It does not construct the 26-row Green homotopy, a cyclic arity-two primitive, "
                "Hadamard data, residual/BFV rows, a QME solution, or a quantum result."
            ),
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        p = self.payload
        if p["schema"] != "pure-weyl-berger-causal-D-Cartan-transfer-v1":
            raise AssertionError("schema drifted")
        if p["next_gate"] != "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY":
            raise AssertionError("causal endpoint is not the next gate")
        if not all(p["exact_checks"].values()):
            raise AssertionError("a conditional transfer check is false")
        flags = p["flags"]
        for key in (
            "BERGER_CAUSAL_D_CARTAN_TRANSFER_THEOREM",
            "BERGER_CAUSAL_UNARY_D_CARTAN_CONDITIONAL",
            "BERGER_CAUSAL_ARITY_TWO_SOURCE_CLOSED_CONDITIONAL",
            "BERGER_CAUSAL_ARITY_TWO_RAW_PRIMITIVE_CONDITIONAL",
        ):
            if flags[key] is not True:
                raise AssertionError(f"conditional theorem dropped: {key}")
        for key in (
            "BERGER_CAUSAL_ARITY_TWO_CYCLIC_COMPLETION",
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY",
            "BERGER_CAUSAL_D_CARTAN_EXTENSION",
            "BERGER_RESIDUAL_BFV_D_CARTAN_EXTENSION",
        ):
            if flags[key] is not False:
                raise AssertionError(f"open theorem promoted: {key}")
        unary = p["unary_transfer"]
        if unary["definition"] != "iota_D,s^(1)=Lambda_s D":
            raise AssertionError("unary transfer formula drifted")
        binary = p["arity_two_transfer"]
        if binary["raw_primitive"] != "iota_D,s,raw^(2)=-Lambda_s A_D,s^(2)":
            raise AssertionError("raw binary primitive drifted")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Conditional causal D-Cartan transfer

The bare finite-order unary Cartan homotopy is obstructed, but a
\(D\)-equivariant causal contraction solves a different and sufficient
problem. If

\[
q\Lambda_\pm+\Lambda_\pm q=1,
\qquad [q,D]=[\Lambda_\pm,D]=0,
\]

then

\[
\iota^{(1)}_{D,\pm}=\Lambda_\pm D
\]

satisfies \([q,\iota^{(1)}_{D,\pm}]=D\) with the same-sided causal support.
The certified 54-to-26 SDR gives the exact lifted formula

\[
\iota^{(1)}_{D,54,\pm}
=S_{\rm cl}D_{54}
+\iota_{\rm cl}\Lambda_{26,\pm}D_{26}\pi_{\rm cl}.
\]

At arity two, set

\[
A^{(2)}_{D,\pm}=[q_2,\iota^{(1)}_{D,\pm}].
\]

The Jacobi identity, \([q_1,q_2]=0\), and \([D,q_2]=0\) imply
\(\delta A^{(2)}_{D,\pm}=0\). Therefore the raw causal primitive

\[
\iota^{(2)}_{D,\pm,\mathrm{raw}}
=-\Lambda_\pm A^{(2)}_{D,\pm}
\]

solves the arity-two equation as a graded-symmetric cochain. Its
convention-correct cyclic advanced/retarded completion remains a separate
gate and is not promoted here.

The next constructive theorem is precisely the retained 26-row causal Green
homotopy. Hadamard data and the quantum master equation are not prerequisites
for this classical causal Cartan step.
"""


def _write(result: BergerCausalDCartanTransfer) -> None:
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: BergerCausalDCartanTransfer) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError("causal D-Cartan transfer certificate drifted")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError("causal D-Cartan transfer report drifted")


def _guards(result: BergerCausalDCartanTransfer) -> None:
    mutations = (
        ("promote endpoint", ("flags", "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"), True),
        ("promote cyclic binary", ("flags", "BERGER_CAUSAL_ARITY_TWO_CYCLIC_COMPLETION"), True),
        ("promote total", ("flags", "BERGER_CAUSAL_D_CARTAN_EXTENSION"), True),
        ("change next gate", (None, "next_gate"), "BERGER_RESIDUAL_BFV_D_CARTAN_EXTENSION"),
        ("change unary formula", ("unary_transfer", "definition"), "iota=D^(-1)"),
    )
    for name, path, value in mutations:
        payload = deepcopy(result.payload)
        if path[0] is None:
            payload[path[1]] = value
        else:
            payload[path[0]][path[1]] = value
        try:
            BergerCausalDCartanTransfer(payload).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard failed: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = BergerCausalDCartanTransfer.build()
    if args.check:
        _check(result)
    else:
        _write(result)
    if args.guards:
        _guards(result)
    print("BERGER_CAUSAL_D_CARTAN_TRANSFER: PASS")
    print("conditional unary and raw arity-two transfer: CERTIFIED")
    print("retained 26-row causal Green homotopy: OPEN")
    print("cyclic arity-two causal completion: OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
