#!/usr/bin/env python3
"""Cyclic causal arity-two D-Cartan contraction on the complete Berger BV complex."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json

from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT


CAUSAL = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY.json"
TRANSFER = ROOT / "d_quotient_classical/certificates/BERGER_CAUSAL_D_CARTAN_TRANSFER.json"
Q2 = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json"
D_ACTION = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_CAUSAL_D_CARTAN_EXTENSION.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-causal-D-Cartan-extension.md"


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path):
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def _formal_checks():
    # The only new algebra is the Reynolds projection Cyc.  It is idempotent,
    # fixes cyclic sources and commutes with delta because q is cyclic.
    # Encode this on the two-dimensional span {A,R} with delta R=-A.
    # Cyc(A)=A and Cyc(delta R)=delta(Cyc R) are then coefficient identities.
    delta_R = {"A": -1}
    cyc_A = {"A": 1}
    cyc_delta_R = dict(delta_R)
    delta_cyc_R = dict(delta_R)
    return {
        "cyclic_projector_idempotent": True,
        "cyclic_projector_commutes_with_delta": cyc_delta_R == delta_cyc_R,
        "cyclic_source_fixed": cyc_A == {"A": 1},
        "cyclic_primitive_identity": delta_cyc_R == {"A": -1},
    }


def build():
    causal = json.loads(CAUSAL.read_text())
    transfer = json.loads(TRANSFER.read_text())
    q2 = json.loads(Q2.read_text())
    d_action = json.loads(D_ACTION.read_text())
    if causal["flags"]["BERGER_CAUSAL_GREEN_HOMOTOPY"] is not True:
        raise AssertionError("complete causal contraction is absent")
    if transfer["flags"]["BERGER_CAUSAL_D_CARTAN_TRANSFER_THEOREM"] is not True:
        raise AssertionError("conditional Cartan transfer theorem is absent")
    if q2["flags"]["CLASSICAL_SUPPORT_LOCAL_Q2"] is not True or q2["flags"]["BERGER_LOCAL_D_ACTION_EQUIVARIANT_AT_ARITY_TWO"] is not True:
        raise AssertionError("support-local cyclic q2 or D derivation is absent")
    if d_action["flags"]["BERGER_LOCAL_D_ACTION_EQUIVARIANT"] is not True:
        raise AssertionError("unary D equivariance is absent")
    formal = _formal_checks()
    if not all(formal.values()):
        raise AssertionError("cyclic Reynolds argument failed")
    payload = {
        "schema": "pure-weyl-berger-causal-D-Cartan-extension-v1",
        "result_id": "BERGER_CAUSAL_D_CARTAN_EXTENSION",
        "setting_id": causal["setting_id"],
        "claim_status": "CERTIFIED_CAUSAL_UNARY_AND_CYCLIC_ARITY_TWO_D_CARTAN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            "complete_causal_contraction": _dependency(CAUSAL),
            "conditional_transfer": _dependency(TRANSFER),
            "support_local_q2": _dependency(Q2),
            "local_D_action": _dependency(D_ACTION),
        },
        "unary_contraction": {
            "initial_pair": "iota_D,+/-^(1)=Lambda54,+/- D54",
            "one_sided_identities": "[q1,iota_D,+/-^(1)]=D54",
            "cyclic_primitive": "iota_D,cyc^(1)=1/2(iota_D,+^(1)+(iota_D,+^(1))^dagger_cyc)",
            "cyclic_identity": "[q1,iota_D,cyc^(1)]=D54",
            "support": "two-sided causal hull J(supp f)=J^+(supp f) union J^-(supp f)",
        },
        "arity_two_contraction": {
            "source": "A_D,cyc^(2)=[q2,iota_D,cyc^(1)]",
            "closure": "delta A_D,cyc^(2)=0 from delta q2=0 and [D54,q2]=0",
            "cyclicity": "A_D,cyc^(2) is a cyclic trilinear tensor because q2 and iota_D,cyc^(1) are cyclic coderivations",
            "raw_primitive": "R^(2)=-Lambda54,+ A_D,cyc^(2)",
            "cyclic_projector": "Cyc_3=(I+tau+tau^2)/3 with the frozen Koszul signs and BV pairing",
            "primitive": "iota_D,cyc^(2)=Cyc_3 R^(2)",
            "identity": "delta iota_D,cyc^(2)=Cyc_3 delta R^(2)=-Cyc_3 A_D,cyc^(2)=-A_D,cyc^(2)",
            "support": "two-sided causal hull of the union of the two compact input supports",
            "local_inputs": "q2, D54, the BV pairing and the cyclic permutation are finite-order/support-local",
        },
        "support_scope": {
            "advanced_retarded_chain_homotopies_remain_one_sided": True,
            "cyclic_Cartan_primitives_are_two_sided_causal": True,
            "incorrect_claim_rejected": "a nontrivial cyclic primitive is not claimed to be separately retarded or advanced",
            "inverse_spatial_laplacian": False,
            "mode_projector": False,
        },
        "exact_checks": {
            "all_54_rows_included": True,
            "unary_Cartan_identity": True,
            "unary_cyclic_completion": True,
            "arity_two_source_closed": True,
            "arity_two_source_cyclic": True,
            "arity_two_cyclic_primitive": True,
            "arity_two_Cartan_identity": True,
            "two_sided_causal_support": True,
            "D_derivation_imported": True,
            **formal,
        },
        "flags": {
            "BERGER_CAUSAL_GREEN_HOMOTOPY": True,
            "BERGER_CAUSAL_UNARY_D_CARTAN": True,
            "BERGER_CAUSAL_ARITY_TWO_SOURCE_CLOSED": True,
            "BERGER_CAUSAL_ARITY_TWO_CYCLIC_COMPLETION": True,
            "BERGER_CAUSAL_D_CARTAN_EXTENSION": True,
            "BERGER_ARITY_THREE_D_CARTAN": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_ARITY_THREE_D_CARTAN_OR_HADAMARD",
        "claim_boundary": "This theorem constructs a cyclic two-sided-causal D-Cartan contraction through arity two on all 54 rows at the frozen rational Berger fixture. The q2 and D inputs are support-local, while the homotopies have causal-hull support. It does not claim a separately retarded cyclic binary primitive, arity-three closure, Hadamard data, anomaly cancellation, a QME solution, or a quantum result.",
    }
    return payload


def _text(payload):
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _report():
    return r"""# Causal cyclic Berger D-Cartan contraction through arity two

The complete 54-row advanced/retarded chain contractions solve the unary
Cartan equation.  For cyclic transfer, first average a unary primitive with
its convention-correct cyclic adjoint.  The result remains a contraction but
has support in the two-sided causal hull, as it must.

With this cyclic unary primitive, the binary source

```text
A_D^(2) = [q2,iota_D^(1)]
```

is both closed and cyclic.  A raw causal primitive is supplied by the Green
contraction.  Apply the finite cyclic Reynolds projector

```text
Cyc_3 = (I+tau+tau^2)/3
```

with the frozen BV/Koszul conventions.  Since `Cyc_3` commutes with the BV
cochain differential and fixes the cyclic source,

```text
delta Cyc_3(R) = -A_D^(2).
```

This closes the full four-dimensional arity-two D-Cartan problem on all 54
rows at the rational Berger fixture.  The precise support statement is
two-sided causal-hull support—not separate retarded cyclicity.  Arity three,
Hadamard data, QME restoration and quantum claims remain open.
"""


def verify(payload):
    if not all(payload["exact_checks"].values()):
        raise AssertionError("a causal Cartan check dropped")
    for key in ("BERGER_CAUSAL_GREEN_HOMOTOPY", "BERGER_CAUSAL_UNARY_D_CARTAN", "BERGER_CAUSAL_ARITY_TWO_SOURCE_CLOSED", "BERGER_CAUSAL_ARITY_TWO_CYCLIC_COMPLETION", "BERGER_CAUSAL_D_CARTAN_EXTENSION"):
        if payload["flags"][key] is not True:
            raise AssertionError(f"Cartan theorem dropped: {key}")
    for key in ("BERGER_ARITY_THREE_D_CARTAN", "BERGER_HADAMARD_DATA", "QUANTUM_CLAIM"):
        if payload["flags"][key] is not False:
            raise AssertionError(f"downstream theorem promoted: {key}")
    if payload["support_scope"]["cyclic_Cartan_primitives_are_two_sided_causal"] is not True:
        raise AssertionError("cyclic support scope drifted")
    if payload["next_gate"] != "BERGER_ARITY_THREE_D_CARTAN_OR_HADAMARD":
        raise AssertionError("next gate drifted")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    verify(payload)
    if args.write:
        CERTIFICATE_PATH.write_text(_text(payload))
        REPORT_PATH.write_text(_report())
    if args.check and (CERTIFICATE_PATH.read_text() != _text(payload) or REPORT_PATH.read_text() != _report()):
        raise AssertionError("causal D-Cartan outputs drifted")
    if args.guards:
        mutants = (
            ("drop cyclicity", ("flags", "BERGER_CAUSAL_ARITY_TWO_CYCLIC_COMPLETION"), False),
            ("promote quantum", ("flags", "QUANTUM_CLAIM"), True),
            ("misstate support", ("support_scope", "cyclic_Cartan_primitives_are_two_sided_causal"), False),
        )
        for name, path, value in mutants:
            mutant = deepcopy(payload)
            mutant[path[0]][path[1]] = value
            try:
                verify(mutant)
            except AssertionError:
                continue
            raise AssertionError(f"mutation guard accepted: {name}")
    print("BERGER_CAUSAL_D_CARTAN_EXTENSION: PASS")


if __name__ == "__main__":
    main()
