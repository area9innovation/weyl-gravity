#!/usr/bin/env python3
"""Authoritative 26-component retained Berger minimal-BV row layout.

The minimal clock SDR removes the temporal-diffeomorphism and Weyl clock
doublets.  This module freezes the remaining coordinates, pairings, allowed
q1 blocks, differential orders, and adjoint conventions before any retained
operator coefficients are constructed.

It is a typed layout theorem, not a retained-operator theorem.  In
particular, the coefficientwise K_spatial, H_retained, and adjoint rows remain
open, as do every nonminimal row and all causal/stability claims.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_PATH = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "BERGER_RETAINED_MINIMAL_LAYOUT.json"
)
REPORT_PATH = (
    ROOT
    / "d_quotient_classical"
    / "reports"
    / "berger-retained-minimal-layout.md"
)
SCHEMA_PATH = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "berger-retained-minimal-layout-v1.schema.json"
)


METRIC_COMPONENTS = (
    "00", "01", "02", "03", "11", "12", "13", "22", "23", "33"
)
SPATIAL_COMPONENTS = ("1", "2", "3")


def _payload_digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _row(
    index: int,
    row_id: str,
    degree: int,
    parity: str,
    bundle_id: str,
    component: str,
    dual_row_id: str,
) -> dict[str, Any]:
    return {
        "index": index,
        "row_id": row_id,
        "degree": degree,
        "parity": parity,
        "bundle_id": bundle_id,
        "component": component,
        "dual_row_id": dual_row_id,
    }


def _rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for component in SPATIAL_COMPONENTS:
        rows.append(
            _row(
                len(rows),
                f"c_spatial_{component}",
                -1,
                "odd",
                "spatial_diff_ghost",
                component,
                f"c_spatial_star_{component}",
            )
        )
    for component in METRIC_COMPONENTS:
        rows.append(
            _row(
                len(rows),
                f"h_hat_{component}",
                0,
                "even",
                "dressed_metric",
                component,
                f"h_hat_star_{component}",
            )
        )
    for component in METRIC_COMPONENTS:
        rows.append(
            _row(
                len(rows),
                f"h_hat_star_{component}",
                1,
                "odd",
                "dressed_metric_antifield",
                component,
                f"h_hat_{component}",
            )
        )
    for component in SPATIAL_COMPONENTS:
        rows.append(
            _row(
                len(rows),
                f"c_spatial_star_{component}",
                2,
                "even",
                "spatial_diff_ghost_antifield",
                component,
                f"c_spatial_{component}",
            )
        )
    return rows


@dataclass(frozen=True)
class BergerRetainedMinimalLayout:
    payload: dict[str, Any]

    @classmethod
    def build(cls) -> "BergerRetainedMinimalLayout":
        rows = _rows()
        payload: dict[str, Any] = {
            "schema": "pure-weyl-berger-retained-minimal-layout-v1",
            "result_id": "BERGER_RETAINED_MINIMAL_LAYOUT",
            "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
            "phase_space_id": "positive_berger_fixed_coupling_linearized_solutions",
            "claim_status": "CERTIFIED_TYPED_LAYOUT",
            "dependency_tags": ["LOCAL-ALGEBRAIC"],
            "coordinate_conventions": {
                "frame": "oriented orthonormal Berger frame (0,1,2,3) with 0 future timelike",
                "metric_signature": "(-,+,+,+)",
                "metric_component_order": list(METRIC_COMPONENTS),
                "spatial_component_order": list(SPATIAL_COMPONENTS),
                "complex_degree_order": [-1, 0, 1, 2],
                "operator_direction": "q1 raises displayed complex degree by one",
                "integration_measure": "Berger-cylinder metric volume density",
                "dual_component_basis": "antifield component labels denote the basis dual to the displayed independent field components, so no hidden off-diagonal factor is present",
            },
            "bundle_rows": [
                {
                    "bundle_id": "spatial_diff_ghost",
                    "degree": -1,
                    "rank": 3,
                    "bundle_type": "spatial tangent gauge-parameter bundle",
                    "parity": "odd",
                },
                {
                    "bundle_id": "dressed_metric",
                    "degree": 0,
                    "rank": 10,
                    "bundle_type": "Sym^2(T^*M)",
                    "parity": "even",
                },
                {
                    "bundle_id": "dressed_metric_antifield",
                    "degree": 1,
                    "rank": 10,
                    "bundle_type": "density-dual of Sym^2(T^*M)",
                    "parity": "odd",
                },
                {
                    "bundle_id": "spatial_diff_ghost_antifield",
                    "degree": 2,
                    "rank": 3,
                    "bundle_type": "density-dual spatial vector identity bundle",
                    "parity": "even",
                },
            ],
            "component_rows": rows,
            "pairing_conventions": {
                "total_degree": 1,
                "field_antifield": "canonical density evaluation h_hat_star(h_hat)",
                "ghost_identity": "canonical density evaluation c_spatial_star(c_spatial)",
                "antisymmetric_coordinate_sign": "Omega(source,dual)=+1 and Omega(dual,source)=-1 in displayed order",
                "dual_involution_exact": True,
                "formal_adjoint_symbol": "sharp",
            },
            "q1_block_contract": [
                {
                    "block_id": "K_spatial",
                    "source_bundle": "spatial_diff_ghost",
                    "target_bundle": "dressed_metric",
                    "source_degree": -1,
                    "target_degree": 0,
                    "maximum_differential_order": 1,
                    "coefficient_status": "OPEN",
                    "meaning": "spatial diffeomorphism gauge generator in dressed coordinates",
                },
                {
                    "block_id": "H_retained",
                    "source_bundle": "dressed_metric",
                    "target_bundle": "dressed_metric_antifield",
                    "source_degree": 0,
                    "target_degree": 1,
                    "maximum_differential_order": 4,
                    "coefficient_status": "OPEN",
                    "meaning": "actual action-derived retained dressed-metric Hessian",
                },
                {
                    "block_id": "minus_K_spatial_sharp",
                    "source_bundle": "dressed_metric_antifield",
                    "target_bundle": "spatial_diff_ghost_antifield",
                    "source_degree": 1,
                    "target_degree": 2,
                    "maximum_differential_order": 1,
                    "coefficient_status": "OPEN",
                    "meaning": "cyclic BV-dual Noether-identity row",
                },
            ],
            "required_operator_identities": [
                "H_retained K_spatial=0",
                "K_spatial^sharp H_retained=0",
                "H_retained^sharp=H_retained",
                "q1_retained^2=0",
                "q1_retained^sharp Omega+Omega q1_retained=0",
                "C_34 is support-locally cyclic-SDR equivalent to C_26 direct_sum A_8",
            ],
            "support_and_order_contract": {
                "coefficient_class": "smooth parallel/invariant Berger background tensors",
                "allowed_maps": "finite-order differential operators and pointwise bundle maps only",
                "support_preserving": True,
                "forbidden": [
                    "inverse Laplacian",
                    "inverse curl",
                    "spectral or helicity projector",
                    "retarded or advanced Green operator in the SDR data",
                ],
            },
            "gate_split": {
                "immediate_gate": "BERGER_RETAINED_MINIMAL_OPERATOR",
                "subsequent_gate": "BERGER_NONMINIMAL_COMPLETION",
                "later_gates": [
                    "BERGER_RETAINED_OPERATOR_STABILITY",
                    "BERGER_CAUSAL_GREEN_HOMOTOPY",
                ],
            },
            "nonlinear_export_compatibility": {
                "stable_row_ids_reusable": True,
                "q1_layout_reusable": True,
                "q1_coefficients_complete": False,
                "q2_complete": False,
                "satisfies_CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT": False,
            },
            "flags": {
                "retained_row_inventory_complete": True,
                "dual_row_involution_complete": True,
                "pairing_conventions_frozen": True,
                "q1_block_types_frozen": True,
                "retained_q1_coefficients_complete": False,
                "nonminimal_rows_complete": False,
                "stability_proved": False,
                "causal_green_homotopy_constructed": False,
            },
            "claim_boundary": "This certificate freezes the 26 retained minimal component rows, degrees, bundle types, pairings, allowed q1 blocks, support rules, and differential-order ceilings. It does not construct any retained q1 coefficient, any nonminimal row, stability, Green homotopy, or q2 operation.",
        }
        result = cls(payload)
        result.verify()
        return result

    @property
    def digest(self) -> str:
        return _payload_digest(self.payload)

    def verify(self) -> None:
        p = self.payload
        rows = p["component_rows"]
        if len(rows) != 26:
            raise AssertionError("retained component count drifted")
        if [row["index"] for row in rows] != list(range(26)):
            raise AssertionError("retained component indices are not canonical")
        ids = [row["row_id"] for row in rows]
        if len(ids) != len(set(ids)):
            raise AssertionError("retained row IDs are not unique")
        by_id = {row["row_id"]: row for row in rows}
        for row in rows:
            dual = by_id.get(row["dual_row_id"])
            if dual is None or dual["dual_row_id"] != row["row_id"]:
                raise AssertionError(f"dual involution failed at {row['row_id']}")
            if row["degree"] + dual["degree"] != 1:
                raise AssertionError(f"pairing degree failed at {row['row_id']}")
        degree_counts = {
            degree: sum(row["degree"] == degree for row in rows)
            for degree in (-1, 0, 1, 2)
        }
        if degree_counts != {-1: 3, 0: 10, 1: 10, 2: 3}:
            raise AssertionError("retained degree ranks drifted")
        bundles = {row["bundle_id"] for row in rows}
        declared_bundles = {row["bundle_id"] for row in p["bundle_rows"]}
        if bundles != declared_bundles:
            raise AssertionError("component and bundle inventories disagree")
        for block in p["q1_block_contract"]:
            if block["target_degree"] != block["source_degree"] + 1:
                raise AssertionError(f"q1 degree drifted in {block['block_id']}")
            if block["coefficient_status"] != "OPEN":
                raise AssertionError("retained coefficients promoted by layout")
        if p["gate_split"] != {
            "immediate_gate": "BERGER_RETAINED_MINIMAL_OPERATOR",
            "subsequent_gate": "BERGER_NONMINIMAL_COMPLETION",
            "later_gates": [
                "BERGER_RETAINED_OPERATOR_STABILITY",
                "BERGER_CAUSAL_GREEN_HOMOTOPY",
            ],
        }:
            raise AssertionError("retained/nonminimal gate split drifted")
        flags = p["flags"]
        for key in (
            "retained_row_inventory_complete",
            "dual_row_involution_complete",
            "pairing_conventions_frozen",
            "q1_block_types_frozen",
        ):
            if flags[key] is not True:
                raise AssertionError(f"layout theorem flag dropped: {key}")
        for key in (
            "retained_q1_coefficients_complete",
            "nonminimal_rows_complete",
            "stability_proved",
            "causal_green_homotopy_constructed",
        ):
            if flags[key] is not False:
                raise AssertionError(f"open operator flag promoted: {key}")
        nonlinear = p["nonlinear_export_compatibility"]
        if nonlinear["q1_coefficients_complete"] is not False:
            raise AssertionError("layout promoted retained q1 coefficients")
        if nonlinear["q2_complete"] is not False:
            raise AssertionError("layout promoted q2")
        if nonlinear["satisfies_CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT"] is not False:
            raise AssertionError("layout promoted the nonlinear export")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Authoritative retained Berger minimal-BV layout

The minimal clock SDR leaves exactly four bundle rows:

| degree | bundle | rank |
|---:|---|---:|
| -1 | spatial diffeomorphism ghost | 3 |
| 0 | dressed symmetric metric | 10 |
| 1 | dressed metric antifield | 10 |
| 2 | spatial ghost antifield / identity row | 3 |

The certificate fixes all 26 component IDs, their orthonormal-frame ordering,
dual involution, complex degrees, parity, and canonical cyclic pairing.  The
only allowed nonzero retained $q_1$ blocks are

\[
K_{\rm spatial},\qquad H_{\rm retained},\qquad -K_{\rm spatial}^{\sharp},
\]

of maximum differential orders $1,4,1$, respectively.  Their coefficients
are deliberately not supplied by this layout theorem.

The next two gates are separate:

```text
BERGER_RETAINED_MINIMAL_OPERATOR
BERGER_NONMINIMAL_COMPLETION
```

The first must derive the complete retained coefficients from the actual
coupled action and verify the Noether, adjoint, nilpotency, cyclicity, and
34-to-26-plus-8 decomposition identities.  Only after it passes may the
second gate add antighost, multiplier, and gauge-fixing rows.

The stable IDs and $q_1$ layout may be reused by the nonlinear classical
export, but this certificate contains neither $q_1$ coefficients nor
$q_2$, so it does not satisfy `CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT`.
"""


def _write(result: BergerRetainedMinimalLayout) -> None:
    CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: BergerRetainedMinimalLayout) -> None:
    result.verify()
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError("retained minimal layout certificate drifted")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError("retained minimal layout report drifted")


def _guards(result: BergerRetainedMinimalLayout) -> None:
    mutations = [
        ("duplicate row ID", ("component_rows", 1, "row_id"), "c_spatial_1"),
        ("break dual", ("component_rows", 0, "dual_row_id"), "h_hat_00"),
        ("promote retained coefficients", ("flags", "retained_q1_coefficients_complete"), True),
        ("promote nonminimal", ("flags", "nonminimal_rows_complete"), True),
        ("merge gates", ("gate_split", "immediate_gate"), "BERGER_RETAINED_Q1_AND_NONMINIMAL_COMPLETION"),
        ("claim q2 export", ("nonlinear_export_compatibility", "q2_complete"), True),
    ]
    for name, path, value in mutations:
        payload = deepcopy(result.payload)
        target: Any = payload
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            BergerRetainedMinimalLayout(payload).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard failed: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = BergerRetainedMinimalLayout.build()
    if args.check:
        _check(result)
    else:
        _write(result)
    if args.guards:
        _guards(result)
    print("BERGER_RETAINED_MINIMAL_LAYOUT: PASS")
    print("retained rows: 3 + 10 + 10 + 3 = 26")
    print("retained coefficients/nonminimal/stability/Green/q2: OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
