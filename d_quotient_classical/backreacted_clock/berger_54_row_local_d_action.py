#!/usr/bin/env python3
"""Complete support-local helical D action on the 54-row Berger complex.

The clock-dressed invariant frame is stationary under the helical generator.
Thus its infinitesimal action on every component row is the central invariant
time derivative ``e_0``.  This module proves coefficientwise that the action
commutes with the complete gauge-fixed classical unary differential and with
all maps of the 54-to-26 support-local contraction.  It also verifies the
formal skew-adjoint/cyclic relation.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from pathlib import Path

from d_quotient_classical.backreacted_clock.berger_gauge_fixed_nonminimal_completion import (
    CERTIFICATE_PATH as GAUGE_FIXED_CERTIFICATE,
    _exact_data as _gauge_fixed_data,
    _is_zero,
    _matrix_add,
    _negative,
    _sparse_multiply,
    _subtract,
    _zero,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
    ROOT,
    LinearOperator,
    _adjoint_matrix,
    _matrix_record,
)


CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-54-row-local-D-action.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-54-row-local-D-action-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _d_matrix(rank: int) -> list[list[LinearOperator]]:
    result = _zero(rank, rank)
    derivative = LinearOperator.from_terms(((0, (0,), 1),))
    for index in range(rank):
        result[index][index] = derivative
    return result


@lru_cache(maxsize=1)
def _exact_checks() -> dict[str, object]:
    data = _gauge_fixed_data()
    d54 = _d_matrix(54)
    d26 = _d_matrix(26)
    q = data["q_gauge_fixed"]
    inclusion = data["iota"]
    projection = data["projection"]
    homotopy = data["homotopy"]
    omega = data["omega"]

    if not _is_zero(_subtract(_sparse_multiply(q, d54), _sparse_multiply(d54, q))):
        raise AssertionError("[q_1,D] is nonzero")
    if not _is_zero(_subtract(_sparse_multiply(d54, inclusion), _sparse_multiply(inclusion, d26))):
        raise AssertionError("D_54 i=i D_26 failed")
    if not _is_zero(_subtract(_sparse_multiply(projection, d54), _sparse_multiply(d26, projection))):
        raise AssertionError("p D_54=D_26 p failed")
    if not _is_zero(_subtract(_sparse_multiply(d54, homotopy), _sparse_multiply(homotopy, d54))):
        raise AssertionError("[D,S] is nonzero")
    if not _is_zero(_matrix_add(_adjoint_matrix(d54), d54)):
        raise AssertionError("D is not formally skew adjoint")
    cyclic_defect = _matrix_add(
        _sparse_multiply(_adjoint_matrix(d54), omega),
        _sparse_multiply(omega, d54),
    )
    if not _is_zero(cyclic_defect):
        raise AssertionError("D does not preserve the cyclic pairing")
    return {"D54": d54, "D26": d26}


@dataclass(frozen=True)
class Berger54RowLocalDAction:
    payload: dict[str, object]

    @classmethod
    def build(cls) -> "Berger54RowLocalDAction":
        matrices = _exact_checks()
        dependency = json.loads(GAUGE_FIXED_CERTIFICATE.read_text())
        rows = dependency["row_layout"]["component_rows"]
        payload: dict[str, object] = {
            "schema": "pure-weyl-berger-54-row-local-D-action-v1",
            "result_id": "BERGER_54_ROW_LOCAL_D_ACTION",
            "setting_id": dependency["setting_id"],
            "claim_status": "CERTIFIED_COMPLETE_LOCAL_D_ACTION_UNARY_EQUIVARIANCE",
            "dependency_tags": ["LOCAL-ALGEBRAIC"],
            "dependency_refs": {
                "gauge_fixed_54_row_unary": {
                    "result_id": dependency["result_id"],
                    "sha256": _sha256(GAUGE_FIXED_CERTIFICATE),
                }
            },
            "geometric_definition": {
                "generator": "D_helical=partial_t plus the compensating internal clock rotation",
                "dressed_frame_action": "D=e_0 on every dressed component coefficient",
                "background_stationary": True,
                "invariant_frame_commutators": "[e_0,e_i]=0",
                "maximum_differential_order": 1,
                "support_local": True,
            },
            "row_layout": {
                "total_rows": 54,
                "degree_ranks": [5, 22, 22, 5],
                "row_ids": [row["row_id"] for row in rows],
                "all_rows_have_D_action": True,
            },
            "D_action": {
                "matrix": _matrix_record(matrices["D54"]),
                "shape": [54, 54],
                "coordinate_rule": "D(row_A)=e_0 row_A for A=0,...,53",
                "formal_adjoint": "D^sharp=-D",
            },
            "retained_D_action": {
                "matrix": _matrix_record(matrices["D26"]),
                "shape": [26, 26],
            },
            "exact_checks": {
                "all_54_rows_included": True,
                "D_support_local_order_one": True,
                "q1_D_commutator_zero_coefficientwise": True,
                "D_iota_equivariant": True,
                "D_projection_equivariant": True,
                "D_homotopy_equivariant": True,
                "D_formally_skew_adjoint": True,
                "D_preserves_cyclic_pairing": True,
            },
            "flags": {
                "BERGER_LOCAL_D_ACTION_COMPLETE_54_ROWS": True,
                "BERGER_LOCAL_D_ACTION_EQUIVARIANT": True,
                "CLASSICAL_SUPPORT_LOCAL_Q2": False,
                "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT": False,
                "BERGER_ARITY_TWO_D_CARTAN_FULL_4D": False,
            },
            "next_gate": "CLASSICAL_SUPPORT_LOCAL_Q2",
            "claim_boundary": (
                "This certificate supplies the complete support-local helical D action on all 54 gauge-fixed classical rows and proves unary equivariance, contraction equivariance, and cyclicity coefficientwise. It does not supply the full four-dimensional q2, prove the D derivation identity at arity two, or promote the full arity-two Cartan contraction."
            ),
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        p = self.payload
        if p["schema"] != "pure-weyl-berger-54-row-local-D-action-v1":
            raise AssertionError("schema drifted")
        _exact_checks()
        if p["row_layout"]["total_rows"] != 54 or len(p["row_layout"]["row_ids"]) != 54:
            raise AssertionError("row ledger incomplete")
        if not all(p["exact_checks"].values()):
            raise AssertionError("a D-action exact check is false")
        flags = p["flags"]
        if flags["BERGER_LOCAL_D_ACTION_COMPLETE_54_ROWS"] is not True:
            raise AssertionError("complete D action not promoted")
        if flags["BERGER_LOCAL_D_ACTION_EQUIVARIANT"] is not True:
            raise AssertionError("D equivariance not promoted")
        for key in (
            "CLASSICAL_SUPPORT_LOCAL_Q2",
            "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT",
            "BERGER_ARITY_TWO_D_CARTAN_FULL_4D",
        ):
            if flags[key] is not False:
                raise AssertionError(f"downstream arity-two claim promoted: {key}")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return """# Complete 54-row Berger local D action

In the clock-dressed helical frame the background and every PBW coefficient
are stationary.  The residual generator therefore acts as the invariant time
derivative `e_0` on every field, ghost, antifield and nonminimal row.

Exact PBW composition proves

```text
[q_1,D]=0,
D i=i D_ret,
p D=D_ret p,
[D,S]=0,
D^sharp=-D.
```

Thus the portable local D action and unary equivariance are complete on all
54 rows.  The remaining nonlinear input is the full four-dimensional q2;
the existing reduced-mode q2 and its all-weight Cartan contraction are not
silently promoted to that theorem.
"""


def _write(result: Berger54RowLocalDAction) -> None:
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: Berger54RowLocalDAction) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError("D-action certificate drifted")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError("D-action report drifted")


def _guards(result: Berger54RowLocalDAction) -> None:
    mutations = (
        ("drop row", ("row_layout", "total_rows"), 53),
        ("drop equivariance", ("flags", "BERGER_LOCAL_D_ACTION_EQUIVARIANT"), False),
        ("promote q2", ("flags", "CLASSICAL_SUPPORT_LOCAL_Q2"), True),
        ("promote Cartan", ("flags", "BERGER_ARITY_TWO_D_CARTAN_FULL_4D"), True),
    )
    for name, path, value in mutations:
        payload = deepcopy(result.payload)
        payload[path[0]][path[1]] = value
        try:
            Berger54RowLocalDAction(payload).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard failed: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = Berger54RowLocalDAction.build()
    if args.check:
        _check(result)
    else:
        _write(result)
    if args.guards:
        _guards(result)
    print("BERGER_54_ROW_LOCAL_D_ACTION: PASS")
    print("all-row local D action and unary equivariance: COMPLETE")
    print("full four-dimensional q2 and arity-two D-Cartan: OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
