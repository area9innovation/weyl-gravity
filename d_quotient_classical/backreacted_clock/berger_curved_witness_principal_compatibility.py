#!/usr/bin/env python3
"""Audit the curved W34 candidate against the clock-reattached principal theorem.

The existing W34 export is an exact cyclic primitive for its declared P34.
That does not imply that the declared P34 realizes the independently certified
scalar metric biwave principal block.  This module compares the two exact
artifacts and emits a scoped incompatibility certificate for the submitted
candidate only.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import sympy as sp

from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT


WITNESS_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_CURVED_CLOCK_REATTACHED_WITNESS.json"
PRINCIPAL_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_CLOCK_REATTACHED_PRINCIPAL_WITNESS.json"
RETAINED_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
LAYOUT_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_34_PORTABLE_CONTRACTION.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_CURVED_WITNESS_PRINCIPAL_COMPATIBILITY.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-curved-witness-principal-compatibility.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-curved-witness-principal-compatibility-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def _artifact_path(record: dict[str, object]) -> Path:
    path = ROOT / str(record["path"])
    if _sha256(path) != record["sha256"]:
        raise AssertionError("P34 artifact hash mismatch")
    return path


def _temporal_order_four(record: dict[str, object], start: int, rank: int) -> sp.Matrix:
    matrix = sp.zeros(rank)
    symbols = {"u": sp.Symbol("u"), "v": sp.Symbol("v"), "alpha_B": sp.Symbol("alpha_B", nonzero=True)}
    for row, column, terms in record["entries"]:
        if not (start <= row < start + rank and start <= column < start + rank):
            continue
        for exponents, coefficient in terms:
            if exponents == [4, 0, 0, 0]:
                matrix[row - start, column - start] += sp.sympify(coefficient, locals=symbols)
    return matrix


def _retained_hessian_temporal(record: dict[str, object]) -> sp.Matrix:
    matrix = sp.zeros(10)
    alpha = sp.Symbol("alpha_B", nonzero=True)
    symbols = {"u": sp.Symbol("u"), "v": sp.Symbol("v"), "alpha_B": alpha}
    for row, column, terms in record["q1_blocks"]["H_retained"]["entries"]:
        for exponents, coefficient in terms:
            if exponents == [4, 0, 0, 0]:
                matrix[row, column] += sp.sympify(coefficient, locals=symbols)
    return matrix


def _minor_witness(matrix: sp.Matrix, rank: int) -> dict[str, object]:
    columns = list(matrix.rref()[1])
    if len(columns) != rank:
        raise AssertionError("column rank witness drifted")
    rows = list(matrix[:, columns].T.rref()[1])
    if len(rows) != rank:
        raise AssertionError("row rank witness drifted")
    determinant = sp.factor(matrix.extract(rows, columns).det())
    if determinant == 0:
        raise AssertionError("rank witness minor vanished")
    return {"rows": rows, "columns": columns, "determinant": str(determinant)}


def _exact_audit() -> dict[str, object]:
    witness = json.loads(WITNESS_CERTIFICATE.read_text())
    principal = json.loads(PRINCIPAL_CERTIFICATE.read_text())
    retained = json.loads(RETAINED_CERTIFICATE.read_text())
    layout = json.loads(LAYOUT_CERTIFICATE.read_text())
    if witness["result_state"] != "CURVED_WITNESS_CANDIDATE":
        raise AssertionError("curved witness lifecycle drifted")
    if principal["flags"]["BERGER_FULL_METRIC_BIWAVE_PRINCIPAL"] is not True:
        raise AssertionError("principal metric theorem dropped")
    if layout["row_layout"]["degree_ranks"] != [5, 12, 12, 5]:
        raise AssertionError("34-row layout drifted")

    p34 = json.loads(_artifact_path(witness["operators"]["P34"]).read_text())
    ghost = _temporal_order_four(p34, 0, 5)
    field = _temporal_order_four(p34, 5, 12)
    antifield = _temporal_order_four(p34, 17, 12)
    identity = _temporal_order_four(p34, 29, 5)
    metric = field[:10, :10]
    metric_antifield = antifield[:10, :10]
    expected5 = sp.eye(5)
    expected10 = sp.eye(10)
    if ghost != expected5 or identity != expected5:
        raise AssertionError("ghost/identity scalar biwave principal regressed")
    if metric.rank() != 8 or metric_antifield.rank() != 8:
        raise AssertionError("submitted metric principal rank changed")
    if field.rank() != 10 or antifield.rank() != 10:
        raise AssertionError("submitted full field principal rank changed")
    if metric == expected10:
        raise AssertionError("expected submitted-candidate incompatibility disappeared")

    alpha = sp.Symbol("alpha_B", nonzero=True)
    eta = (-1, 1, 1, 1)
    pairs = ((0, 0), (0, 1), (0, 2), (0, 3), (1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3))
    fibre = sp.diag(*[
        sp.Rational(4, 1) / (alpha * (1 if first == second else 2) * eta[first] * eta[second])
        for first, second in pairs
    ])
    hessian = _retained_hessian_temporal(retained)
    j_only_metric = sp.simplify(metric + (fibre - sp.eye(10)) * hessian)
    if j_only_metric.rank() != 8 or j_only_metric == expected10:
        raise AssertionError("J-only repair boundary changed")

    row_ids = [row["row_id"] for row in layout["row_layout"]["component_rows"]]
    return {
        "witness": witness,
        "principal": principal,
        "retained": retained,
        "layout": layout,
        "p34": p34,
        "ghost": ghost,
        "field": field,
        "antifield": antifield,
        "identity": identity,
        "metric": metric,
        "metric_antifield": metric_antifield,
        "j_only_metric": j_only_metric,
        "row_ids": row_ids,
    }


@dataclass(frozen=True)
class BergerCurvedWitnessPrincipalCompatibility:
    payload: dict[str, object]

    @classmethod
    def build(cls) -> "BergerCurvedWitnessPrincipalCompatibility":
        data = _exact_audit()
        metric = data["metric"]
        field = data["field"]
        payload: dict[str, object] = {
            "schema": "pure-weyl-berger-curved-witness-principal-compatibility-v1",
            "result_id": "BERGER_CURVED_WITNESS_PRINCIPAL_COMPATIBILITY",
            "setting_id": data["witness"]["setting_id"],
            "claim_status": "SUBMITTED_W34_PRINCIPAL_INCOMPATIBLE_REPAIR_REQUIRED",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            "dependency_refs": {
                "curved_W34_candidate": _dependency(WITNESS_CERTIFICATE),
                "clock_reattached_principal": _dependency(PRINCIPAL_CERTIFICATE),
                "retained_q1": _dependency(RETAINED_CERTIFICATE),
                "minimal_34_layout": _dependency(LAYOUT_CERTIFICATE),
            },
            "comparison_covector": {
                "frame_covector": [1, 0, 0, 0],
                "wave_symbol_squared": "1",
                "reason": "a single exact noncharacteristic covector suffices to reject equality of polynomial principal symbols",
            },
            "degree_block_audit": {
                "ghost_rank": data["ghost"].rank(),
                "ghost_equals_scalar_biwave_I5": data["ghost"] == sp.eye(5),
                "dressed_metric_rank": metric.rank(),
                "required_metric_rank": 10,
                "full_field_rank_with_two_clock_rows": field.rank(),
                "full_field_size": 12,
                "metric_antifield_rank": data["metric_antifield"].rank(),
                "identity_rank": data["identity"].rank(),
                "identity_equals_scalar_biwave_I5": data["identity"] == sp.eye(5),
            },
            "rank_witnesses": {
                "dressed_metric_rank8_minor": _minor_witness(metric, 8),
                "full_field_rank10_minor": _minor_witness(field, 10),
            },
            "normalized_obstruction": {
                "block": "degree_zero_dressed_metric",
                "output_row": data["row_ids"][5],
                "input_row": data["row_ids"][5],
                "derivative_exponents": [4, 0, 0, 0],
                "submitted_coefficient": str(metric[0, 0]),
                "required_coefficient": "1",
                "defect": str(metric[0, 0] - 1),
                "normalized_dual_functional": "minus coefficient extraction at (h_hat_00,h_hat_00,e0^4)",
                "dual_pairing_on_defect": "1",
            },
            "normalization_test": {
                "candidate_middle_map": "identity on the first ten middle rows",
                "principal_theorem_middle_map": "J=(4/alpha_B) R_raise",
                "J_only_corrected_metric_rank": data["j_only_metric"].rank(),
                "J_only_equals_scalar_biwave_I10": data["j_only_metric"] == sp.eye(10),
                "conclusion": "changing the middle fibre map alone does not repair the dressed incidence; the raw/dressed BV-canonical transport must be applied coherently to q, W, P and the pairing",
            },
            "exact_checks": {
                "submitted_qW_plus_Wq_identity_imported": True,
                "principal_metric_target_imported": True,
                "ghost_principal_compatible": True,
                "identity_principal_compatible": True,
                "dressed_metric_principal_rank_is_8_not_10": True,
                "clock_rows_raise_full_field_rank_only_to_10_of_12": True,
                "normalized_coefficient_obstruction_nonzero": True,
                "J_only_repair_fails": True,
                "candidate_scope_not_global_nonexistence": True,
            },
            "flags": {
                "BERGER_CURVED_WITNESS_ALGEBRAIC_IDENTITY": True,
                "BERGER_CURVED_WITNESS_PRINCIPAL_COMPATIBILITY": False,
                "BERGER_CURVED_WITNESS_GREEN_EXECUTION": False,
                "BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT": False,
                "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
            },
            "next_gate": "BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT",
            "claim_boundary": (
                "This exact comparison rejects the submitted W34/P34 candidate as a realization "
                "of the separately certified scalar metric principal block. It does not reject "
                "the algebraic identity P34=q34 W34+W34 q34, and it is not a no-go theorem for "
                "other witnesses, raw-coordinate BV-canonical transports, auxiliary-field "
                "realizations, or the retained 26-row Green homotopy."
            ),
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        p = self.payload
        if p["next_gate"] != "BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT":
            raise AssertionError("repair gate drifted")
        if not all(p["exact_checks"].values()):
            raise AssertionError("principal compatibility check dropped")
        flags = p["flags"]
        if flags["BERGER_CURVED_WITNESS_ALGEBRAIC_IDENTITY"] is not True:
            raise AssertionError("algebraic witness identity dropped")
        for key in (
            "BERGER_CURVED_WITNESS_PRINCIPAL_COMPATIBILITY",
            "BERGER_CURVED_WITNESS_GREEN_EXECUTION",
            "BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT",
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY",
        ):
            if flags[key] is not False:
                raise AssertionError(f"open or failed flag promoted: {key}")
        audit = p["degree_block_audit"]
        if audit["dressed_metric_rank"] != 8 or audit["required_metric_rank"] != 10:
            raise AssertionError("metric rank obstruction drifted")
        if p["normalized_obstruction"]["defect"] != "-1":
            raise AssertionError("normalized obstruction drifted")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Curved-witness/principal compatibility audit

The submitted (W_{34}) remains an exact cyclic primitive for its declared
operator:

\[
P_{34}=q_{34}W_{34}+W_{34}q_{34}.
\]

It does not, however, realize the separately certified clock-reattached
scalar metric principal block. At the exact noncharacteristic covector
(\zeta=(1,0,0,0)), the ghost and identity blocks equal the required
biwave identity, but the ten-row dressed metric block has rank eight rather
than ten. The two clock rows raise the full twelve-row field block only to
rank ten.

The normalized defect is already visible in the (e_0^4) coefficient from
(h_{\hat 0 0}) to its equation: the submitted coefficient is zero and the
required scalar-biwave coefficient is one. Replacing the identity middle map
by (J=(4/\alpha_B)R_{\rm raise}) alone leaves the metric rank equal to eight.
Thus this is not merely a normalization adjustment; the raw/dressed
BV-canonical coordinate transport must be applied coherently to (q,W,P)
and the pairing.

This rejects only the submitted curved witness as the desired principal
realization. It is not a no-go theorem for a corrected transported witness,
an auxiliary realization, or the retained Green homotopy itself.
"""


def _write(result: BergerCurvedWitnessPrincipalCompatibility) -> None:
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: BergerCurvedWitnessPrincipalCompatibility) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError("principal compatibility certificate drifted")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError("principal compatibility report drifted")


def _guards(result: BergerCurvedWitnessPrincipalCompatibility) -> None:
    mutations = (
        ("promote compatibility", ("flags", "BERGER_CURVED_WITNESS_PRINCIPAL_COMPATIBILITY"), True),
        ("promote Green", ("flags", "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"), True),
        ("erase defect", ("normalized_obstruction", "defect"), "0"),
        ("skip repair", (None, "next_gate"), "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"),
    )
    for name, path, value in mutations:
        payload = deepcopy(result.payload)
        if path[0] is None:
            payload[path[1]] = value
        else:
            payload[path[0]][path[1]] = value
        try:
            BergerCurvedWitnessPrincipalCompatibility(payload).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard failed: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = BergerCurvedWitnessPrincipalCompatibility.build()
    if args.check:
        _check(result)
    else:
        _write(result)
    if args.guards:
        _guards(result)
    print("BERGER_CURVED_WITNESS_PRINCIPAL_COMPATIBILITY: FAIL (scoped candidate)")
    print("exact algebraic W34 identity: PRESERVED")
    print("next gate: coherent raw-clock BV witness transport")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
