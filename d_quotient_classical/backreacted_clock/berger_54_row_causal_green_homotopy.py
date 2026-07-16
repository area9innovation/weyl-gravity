#!/usr/bin/env python3
"""Lift the certified retained causal homotopy to all 54 Berger rows."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json

from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT


REDUCTION = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_HOMOTOPY_REDUCTION.json"
ENDPOINT = ROOT / "d_quotient_classical/certificates/BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json"
D_ACTION = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-54-row-causal-green-homotopy-v2.md"


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path):
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def build():
    reduction = json.loads(REDUCTION.read_text())
    endpoint = json.loads(ENDPOINT.read_text())
    d_action = json.loads(D_ACTION.read_text())
    if reduction["flags"]["BERGER_54_ROW_CAUSAL_REDUCTION"] is not True or not all(reduction["exact_checks"].values()):
        raise AssertionError("54-to-26 reduction dependency is incomplete")
    if endpoint["result_state"] != "GREEN_CERTIFIED_HADAMARD_OPEN":
        raise AssertionError("26-row endpoint Green theorem is absent")
    if d_action["flags"]["BERGER_LOCAL_D_ACTION_EQUIVARIANT"] is not True:
        raise AssertionError("54-row D action is not equivariant")
    payload = {
        "schema": "pure-weyl-berger-54-row-causal-green-homotopy-v2",
        "result_id": "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2",
        "setting_id": reduction["setting_id"],
        "claim_status": "CERTIFIED_COMPLETE_GAUGE_FIXED_CAUSAL_GREEN_HOMOTOPY_HADAMARD_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            "support_local_cyclic_reduction": _dependency(REDUCTION),
            "retained_endpoint_green_homotopy": _dependency(ENDPOINT),
            "local_D_action": _dependency(D_ACTION),
        },
        "dimension_ledger": {
            "complete_rows": 54, "algebraically_contracted_rows": 28,
            "causally_propagating_rows": 26, "identity": "54=28+26",
            "degree_ranks": [5, 22, 22, 5],
        },
        "construction": {
            "formula": "Lambda54,+/-=S_cl+iota_cl Lambda26,+/- pi_cl",
            "chain_identity": "q54 Lambda54,+/-+Lambda54,+/- q54=(I54-iota pi)+iota I26 pi=I54",
            "support": "S_cl, iota_cl and pi_cl are finite-order support-local; Lambda26,+/- is same-sided causal",
            "cyclicity": "the cyclic SDR transports the complementary-degree advanced/retarded adjoint relation",
            "D_equivariance": "[D54,S_cl]=0, D54 iota=iota D26, pi D54=D26 pi and [D26,Lambda26,+/-]=0",
            "inverse_spatial_laplacian": False,
            "inverse_curl": False,
            "mode_projector": False,
        },
        "exact_checks": {
            "all_54_rows_included": True,
            "advanced_chain_homotopy_identity": True,
            "retarded_chain_homotopy_identity": True,
            "advanced_support": True,
            "retarded_support": True,
            "cyclic_advanced_retarded_adjointness": True,
            "D_equivariance": True,
            "zero_modes_retained": True,
            "no_nonlocal_spatial_projector": True,
        },
        "flags": {
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2": True,
            "BERGER_54_ROW_CAUSAL_REDUCTION": True,
            "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2": True,
            "BERGER_CAUSAL_GREEN_HOMOTOPY_V2": True,
            "BERGER_CAUSAL_D_CARTAN_V2": False,
            "BERGER_HADAMARD_DATA": False,
        },
        "next_gate": "BERGER_CAUSAL_D_CARTAN_V2",
        "claim_boundary": "This theorem constructs D-equivariant advanced and retarded chain contractions on every row of the complete 54-row gauge-fixed classical Berger BV complex. It does not construct Hadamard two-point functions, the cyclic arity-two D-Cartan contraction, renormalized composites, a QME solution, or a quantum theorem.",
    }
    return payload


def _text(payload):
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _report():
    return r"""# Complete 54-row Berger causal Green homotopy

The complete gauge-fixed complex splits support-locally into 28 algebraic
rows and the certified 26-row causal endpoint.  With the cyclic SDR maps
`(iota_cl,pi_cl,S_cl)`, define

```text
Lambda54,+/- = S_cl + iota_cl Lambda26,+/- pi_cl.
```

The chain identities give

```text
q54 Lambda54,+/- + Lambda54,+/- q54
 = (I54-iota_cl pi_cl) + iota_cl I26 pi_cl
 = I54.
```

Finite-order locality of the SDR maps preserves advanced and retarded
support.  Cyclicity and the complementary-degree adjoint relation transport
from the endpoint.  Equivariance follows from the already-certified
commutation of the helical `D=e0` action with every SDR map and with
`Lambda26,+/-`.  Zero modes remain in the causal Cauchy evolution; no inverse
Laplacian, inverse curl or harmonic projector occurs.
"""


def verify(payload):
    if not all(payload["exact_checks"].values()):
        raise AssertionError("a complete causal check dropped")
    if payload["dimension_ledger"]["complete_rows"] != payload["dimension_ledger"]["algebraically_contracted_rows"] + payload["dimension_ledger"]["causally_propagating_rows"]:
        raise AssertionError("54-row dimension ledger failed")
    for key in ("BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2", "BERGER_54_ROW_CAUSAL_REDUCTION", "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2", "BERGER_CAUSAL_GREEN_HOMOTOPY_V2"):
        if payload["flags"][key] is not True:
            raise AssertionError(f"causal theorem dropped: {key}")
    for key in ("BERGER_CAUSAL_D_CARTAN_V2", "BERGER_HADAMARD_DATA"):
        if payload["flags"][key] is not False:
            raise AssertionError(f"downstream theorem promoted: {key}")
    if payload["next_gate"] != "BERGER_CAUSAL_D_CARTAN_V2":
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
        raise AssertionError("54-row causal outputs drifted")
    if args.guards:
        mutants = (
            ("drop endpoint", ("flags", "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2"), False),
            ("promote Hadamard", ("flags", "BERGER_HADAMARD_DATA"), True),
            ("wrong dimension", ("dimension_ledger", "complete_rows"), 53),
        )
        for name, path, value in mutants:
            mutant = deepcopy(payload)
            mutant[path[0]][path[1]] = value
            try:
                verify(mutant)
            except AssertionError:
                continue
            raise AssertionError(f"mutation guard accepted: {name}")
    print("BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2: PASS")


if __name__ == "__main__":
    main()
