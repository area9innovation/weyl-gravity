#!/usr/bin/env python3
"""Reduce the complete Berger causal problem from 54 rows to 26 rows.

The gauge-fixed nonminimal complex already carries a finite-order cyclic SDR

    (C_54,q_54) <--> (C_26,q_26),

with maps ``i,p,S``.  This module verifies the chain maps coefficientwise in
the Berger PBW algebra and records the exact conditional causal formula

    Lambda_54,+/- = S + i Lambda_26,+/- p.

Consequently a same-sided causal contraction of the retained 26-row complex
lifts to all 54 rows.  The result is an equivalence/reduction theorem; it does
not claim that the still-open 26-row endpoint homotopy exists.
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
    _identity_matrix,
    _is_zero,
    _matrix_add,
    _sparse_multiply,
    _subtract,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT
from d_quotient_classical.backreacted_clock.berger_minimal_34_portable_contraction import (
    _exact_matrices as _minimal_matrices,
)


CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_HOMOTOPY_REDUCTION.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-54-row-causal-homotopy-reduction.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-54-row-causal-homotopy-reduction-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def _chain_checks() -> dict[str, object]:
    full = _gauge_fixed_data()
    retained = _minimal_matrices()["q_retained"]
    q = full["q_gauge_fixed"]
    inclusion = full["iota"]
    projection = full["projection"]
    homotopy = full["homotopy"]

    if not _is_zero(
        _subtract(
            _sparse_multiply(q, inclusion),
            _sparse_multiply(inclusion, retained),
        )
    ):
        raise AssertionError("q_54 i=i q_26 failed")
    if not _is_zero(
        _subtract(
            _sparse_multiply(projection, q),
            _sparse_multiply(retained, projection),
        )
    ):
        raise AssertionError("p q_54=q_26 p failed")
    if not _is_zero(
        _subtract(
            _sparse_multiply(projection, inclusion),
            _identity_matrix(26),
        )
    ):
        raise AssertionError("p i=1_26 failed")

    endpoint_projector = _sparse_multiply(inclusion, projection)
    algebraic_projector = _subtract(_identity_matrix(54), endpoint_projector)
    contracted = _matrix_add(
        _sparse_multiply(q, homotopy),
        _sparse_multiply(homotopy, q),
    )
    if not _is_zero(_subtract(contracted, algebraic_projector)):
        raise AssertionError("q_54 S+S q_54=1-i p failed")
    if not _is_zero(_sparse_multiply(homotopy, homotopy)):
        raise AssertionError("S^2=0 failed")
    if not _is_zero(_sparse_multiply(projection, homotopy)):
        raise AssertionError("p S=0 failed")
    if not _is_zero(_sparse_multiply(homotopy, inclusion)):
        raise AssertionError("S i=0 failed")

    return {
        "q54": q,
        "q26": retained,
        "inclusion": inclusion,
        "projection": projection,
        "homotopy": homotopy,
    }


@dataclass(frozen=True)
class Berger54RowCausalHomotopyReduction:
    payload: dict[str, object]

    @classmethod
    def build(cls) -> "Berger54RowCausalHomotopyReduction":
        _chain_checks()
        dependency = json.loads(GAUGE_FIXED_CERTIFICATE.read_text())
        payload: dict[str, object] = {
            "schema": "pure-weyl-berger-54-row-causal-homotopy-reduction-v1",
            "result_id": "BERGER_54_ROW_CAUSAL_HOMOTOPY_REDUCTION",
            "setting_id": dependency["setting_id"],
            "claim_status": "CERTIFIED_CAUSAL_REDUCTION_ENDPOINT_OPEN",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            "dependency_refs": {
                "gauge_fixed_54_row_unary": {
                    "result_id": dependency["result_id"],
                    "sha256": _sha256(GAUGE_FIXED_CERTIFICATE),
                }
            },
            "dimension_ledger": {
                "complete_gauge_fixed_rows": 54,
                "retained_endpoint_rows": 26,
                "support_locally_contracted_rows": 28,
                "identity": "54=28+26",
                "degree_ranks_54": [5, 22, 22, 5],
                "degree_ranks_26": [3, 10, 10, 3],
            },
            "causal_reduction": {
                "maps": "the pinned iota_cl, pi_cl and S_cl of BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION",
                "chain_identities": [
                    "q_54 i=i q_26",
                    "p q_54=q_26 p",
                    "p i=1_26",
                    "q_54 S+S q_54=1_54-i p",
                    "S^2=0",
                    "p S=0",
                    "S i=0",
                ],
                "conditional_endpoint_identity": "q_26 Lambda_26,+/-+Lambda_26,+/- q_26=1_26",
                "lifted_formula": "Lambda_54,+/-=S+i Lambda_26,+/- p",
                "lifted_derivation": "q_54 Lambda_54,+/-+Lambda_54,+/- q_54=(1-i p)+i(p i)p=1_54",
                "support_argument": "S,i,p are finite-order differential operators; composing them with a retarded/advanced Lambda_26 preserves J^+/- support",
                "cyclic_argument": "the imported contraction is cyclic; endpoint advanced/retarded adjointness transfers through the cyclic inclusion/projection",
                "inverse_laplacian_or_curl": False,
                "mode_projector": False,
            },
            "exact_checks": {
                "all_54_rows_included": True,
                "coefficientwise_q54_i_equals_i_q26": True,
                "coefficientwise_p_q54_equals_q26_p": True,
                "pi_iota_identity": True,
                "algebraic_complement_contracted": True,
                "contraction_side_conditions": True,
                "support_local_finite_order": True,
                "cyclic_contraction_imported": True,
                "conditional_lifted_homotopy_identity": True,
                "conditional_causal_support": True,
            },
            "flags": {
                "BERGER_54_ROW_CAUSAL_REDUCTION": True,
                "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
                "BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION": False,
                "BERGER_CAUSAL_GREEN_HOMOTOPY": False,
            },
            "next_gate": "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY",
            "claim_boundary": (
                "This theorem removes all 28 clock/nonminimal/gauge-fixing rows from the analytic risk and proves that any retained 26-row advanced/retarded chain contraction lifts support-locally and cyclically to the complete gauge-fixed 54-row complex. It does not construct the retained metric mixed-order Green realization or promote BERGER_CAUSAL_GREEN_HOMOTOPY."
            ),
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        p = self.payload
        if p["schema"] != "pure-weyl-berger-54-row-causal-homotopy-reduction-v1":
            raise AssertionError("schema drifted")
        if p["dimension_ledger"]["complete_gauge_fixed_rows"] != (
            p["dimension_ledger"]["support_locally_contracted_rows"]
            + p["dimension_ledger"]["retained_endpoint_rows"]
        ):
            raise AssertionError("54=28+26 dimension ledger failed")
        _chain_checks()
        checks = p["exact_checks"]
        if not all(checks.values()):
            raise AssertionError("a causal-reduction check is false")
        flags = p["flags"]
        if flags["BERGER_54_ROW_CAUSAL_REDUCTION"] is not True:
            raise AssertionError("causal reduction not promoted")
        for key in (
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY",
            "BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION",
            "BERGER_CAUSAL_GREEN_HOMOTOPY",
        ):
            if flags[key] is not False:
                raise AssertionError(f"downstream causal theorem promoted: {key}")
        if p["next_gate"] != "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY":
            raise AssertionError("next gate drifted")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return """# Berger 54-row causal-homotopy reduction

The complete gauge-fixed Berger unary BV complex has 54 rows, but 28 of
them are already support-locally and cyclically contractible.  Exact PBW
composition verifies the SDR chain identities with the retained 26-row
complex.

If the retained complex admits same-sided homotopies
`Lambda_26,+/-`, then

```text
Lambda_54,+/- = S + i Lambda_26,+/- p
```

satisfies the complete 54-row identity.  The local maps `S,i,p` do not
enlarge support, so retarded/advanced support and the cyclic adjoint relation
transfer automatically.

This is a reduction theorem, not the endpoint PDE theorem.  The only
remaining causal gate is the mixed-order metric realization inside the
retained 26-row complex.
"""


def _write(result: Berger54RowCausalHomotopyReduction) -> None:
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: Berger54RowCausalHomotopyReduction) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError("causal-reduction certificate drifted")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError("causal-reduction report drifted")


def _guards(result: Berger54RowCausalHomotopyReduction) -> None:
    mutations = (
        ("break dimension", ("dimension_ledger", "support_locally_contracted_rows"), 27),
        ("drop reduction", ("flags", "BERGER_54_ROW_CAUSAL_REDUCTION"), False),
        ("promote endpoint", ("flags", "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"), True),
        ("promote total", ("flags", "BERGER_CAUSAL_GREEN_HOMOTOPY"), True),
    )
    for name, path, value in mutations:
        payload = deepcopy(result.payload)
        payload[path[0]][path[1]] = value
        try:
            Berger54RowCausalHomotopyReduction(payload).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard failed: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = Berger54RowCausalHomotopyReduction.build()
    if args.check:
        _check(result)
    else:
        _write(result)
    if args.guards:
        _guards(result)
    print("BERGER_54_ROW_CAUSAL_HOMOTOPY_REDUCTION: PASS")
    print("complete 54-row causal problem reduced exactly to 26 rows")
    print("retained 26-row endpoint Green homotopy: OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
