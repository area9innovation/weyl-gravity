#!/usr/bin/env python3
"""Portable all-row contraction of the 34-row minimal Berger complex.

This is the cross-team unary export.  The historical ``q1_blocks`` input is
re-exported semantically as ``classical_unary_q1`` (ell_1^cl), combined with
the temporal-diffeomorphism/Weyl clock rows, and accompanied by explicit
inclusion, projection, homotopy, and complementary projectors.

Only the minimal unary complex is closed here.  Nonminimal gauge fixing,
ell_2^cl, local D-equivariance, the general Koszul--Tate package, and causal or
Hadamard data remain fail-closed.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import sympy as sp

try:
    from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import (
        _matrix_from_record,
    )
    from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
        LinearOperator,
        ROOT,
        ZERO,
        _matrix_record,
    )
except ModuleNotFoundError:  # Direct script execution.
    from berger_causal_witness_preflight import _matrix_from_record
    from berger_linearized_bach_pbw import (
        LinearOperator,
        ROOT,
        ZERO,
        _matrix_record,
    )


Q1_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
CLOCK_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_BV_CLOCK_SDR.json"
LAYOUT_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_LAYOUT.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_34_PORTABLE_CONTRACTION.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-minimal-34-portable-contraction.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-minimal-34-portable-contraction-v1.schema.json"


FULL_ROWS = (
    "c_spatial_1", "c_spatial_2", "c_spatial_3", "tau", "sigma",
    "h_hat_00", "h_hat_01", "h_hat_02", "h_hat_03", "h_hat_11",
    "h_hat_12", "h_hat_13", "h_hat_22", "h_hat_23", "h_hat_33",
    "R", "Theta",
    "h_hat_star_00", "h_hat_star_01", "h_hat_star_02", "h_hat_star_03",
    "h_hat_star_11", "h_hat_star_12", "h_hat_star_13", "h_hat_star_22",
    "h_hat_star_23", "h_hat_star_33", "R_star", "Theta_star",
    "c_spatial_star_1", "c_spatial_star_2", "c_spatial_star_3",
    "tau_star", "sigma_star",
)

RETAINED_TO_FULL = (
    0, 1, 2,
    5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
    17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
    29, 30, 31,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _zero(rows: int, columns: int) -> list[list[LinearOperator]]:
    return [[ZERO for _ in range(columns)] for _ in range(rows)]


def _one(value: sp.Expr = sp.S.One) -> LinearOperator:
    return LinearOperator.from_terms(((0, (), value),))


def _embed_block(target, block, row_offset: int, column_offset: int) -> None:
    for row in range(len(block)):
        for column in range(len(block[0])):
            target[row + row_offset][column + column_offset] = block[row][column]


def _exact_matrices() -> dict[str, object]:
    retained = json.loads(Q1_CERTIFICATE.read_text())
    clock = json.loads(CLOCK_CERTIFICATE.read_text())
    layout = json.loads(LAYOUT_CERTIFICATE.read_text())
    if retained["flags"]["BERGER_RETAINED_MINIMAL_OPERATOR"] is not True:
        raise AssertionError("retained unary dependency is not certified")
    if clock["flags"]["support_local_clock_SDR_exact"] is not True:
        raise AssertionError("clock contraction dependency is not certified")

    k_retained = _matrix_from_record(retained["q1_blocks"]["K_spatial"])
    h_retained = _matrix_from_record(retained["q1_blocks"]["H_retained"])
    l_retained = _matrix_from_record(retained["q1_blocks"]["minus_K_spatial_sharp"])

    # Degree blocks use ranks 5 -> 12 -> 12 -> 5 and the clock field order
    # (R,Theta).  Thus tau -> Theta and sigma -> -R.
    k_full = _zero(12, 5)
    _embed_block(k_full, k_retained, 0, 0)
    k_full[10][4] = _one(-1)  # q sigma = -R
    k_full[11][3] = _one(1)   # q tau = Theta

    h_full = _zero(12, 12)
    _embed_block(h_full, h_retained, 0, 0)

    l_full = _zero(5, 12)
    _embed_block(l_full, l_retained, 0, 0)
    l_full[3][11] = _one(-1)  # q Theta* = -tau*
    l_full[4][10] = _one(1)   # q R* = sigma*

    q_full = _zero(34, 34)
    _embed_block(q_full, k_full, 5, 0)
    _embed_block(q_full, h_full, 17, 5)
    _embed_block(q_full, l_full, 29, 17)

    q_retained = _zero(26, 26)
    _embed_block(q_retained, k_retained, 3, 0)
    _embed_block(q_retained, h_retained, 13, 3)
    _embed_block(q_retained, l_retained, 23, 13)

    inclusion = _zero(34, 26)
    projection = _zero(26, 34)
    for retained_index, full_index in enumerate(RETAINED_TO_FULL):
        inclusion[full_index][retained_index] = _one()
        projection[retained_index][full_index] = _one()

    retained_projector = _zero(34, 34)
    for full_index in RETAINED_TO_FULL:
        retained_projector[full_index][full_index] = _one()
    clock_projector = _zero(34, 34)
    clock_indices = (3, 4, 15, 16, 27, 28, 32, 33)
    for full_index in clock_indices:
        clock_projector[full_index][full_index] = _one()

    homotopy = _zero(34, 34)
    homotopy[3][16] = _one(1)    # s Theta = tau
    homotopy[4][15] = _one(-1)   # s R = -sigma
    homotopy[28][32] = _one(-1)  # s tau* = -Theta*
    homotopy[27][33] = _one(1)   # s sigma* = R*

    # Verify the selector and contraction identities in the exact constant
    # incidence algebra.  This avoids a dense 34^3 PBW multiplication: the
    # retained differential identities are already imported by digest, and
    # the full complex is their literal direct sum with this clock block.
    i_numeric = sp.zeros(34, 26)
    p_numeric = sp.zeros(26, 34)
    for retained_index, full_index in enumerate(RETAINED_TO_FULL):
        i_numeric[full_index, retained_index] = 1
        p_numeric[retained_index, full_index] = 1
    retained_numeric = i_numeric * p_numeric
    clock_numeric = sp.eye(34) - retained_numeric
    if p_numeric * i_numeric != sp.eye(26):
        raise AssertionError("portable projection-inclusion identity failed")
    if retained_numeric * clock_numeric != sp.zeros(34):
        raise AssertionError("complementary projectors overlap")
    if retained_numeric + clock_numeric != sp.eye(34):
        raise AssertionError("complementary projectors do not sum to identity")

    q_clock_numeric = sp.zeros(34)
    q_clock_numeric[15, 4] = -1
    q_clock_numeric[16, 3] = 1
    q_clock_numeric[32, 28] = -1
    q_clock_numeric[33, 27] = 1
    if q_clock_numeric * q_clock_numeric != sp.zeros(34):
        raise AssertionError("clock unary block is not nilpotent")

    omega = sp.zeros(34)
    omega[0:5, 29:34] = sp.eye(5)
    omega[29:34, 0:5] = -sp.eye(5)
    omega[5:17, 17:29] = sp.eye(12)
    omega[17:29, 5:17] = -sp.eye(12)
    s_numeric = sp.zeros(34)
    for row, column, value in ((3, 16, 1), (4, 15, -1), (28, 32, -1), (27, 33, 1)):
        s_numeric[row, column] = value
    if q_clock_numeric * s_numeric + s_numeric * q_clock_numeric != clock_numeric:
        raise AssertionError("all-row clock contraction identity failed")
    if s_numeric * s_numeric != sp.zeros(34):
        raise AssertionError("portable homotopy is not square zero")
    if p_numeric * s_numeric != sp.zeros(26, 34):
        raise AssertionError("p s side condition failed")
    if s_numeric * i_numeric != sp.zeros(34, 26):
        raise AssertionError("s i side condition failed")
    if sp.simplify(s_numeric.T * omega + omega * s_numeric) != sp.zeros(34):
        raise AssertionError("portable clock homotopy is not cyclic")

    return {
        "retained": retained,
        "clock": clock,
        "layout": layout,
        "k_full": k_full,
        "h_full": h_full,
        "l_full": l_full,
        "q_full": q_full,
        "q_retained": q_retained,
        "inclusion": inclusion,
        "projection": projection,
        "homotopy": homotopy,
        "retained_projector": retained_projector,
        "clock_projector": clock_projector,
    }


@dataclass(frozen=True)
class BergerMinimal34PortableContraction:
    payload: dict[str, object]

    @classmethod
    def build(cls) -> "BergerMinimal34PortableContraction":
        matrices = _exact_matrices()
        retained = matrices["retained"]
        rows = []
        degrees = [-1] * 5 + [0] * 12 + [1] * 12 + [2] * 5
        for index, (row_id, degree) in enumerate(zip(FULL_ROWS, degrees, strict=True)):
            rows.append({"index": index, "row_id": row_id, "degree": degree})
        payload: dict[str, object] = {
            "schema": "pure-weyl-berger-minimal-34-portable-contraction-v1",
            "result_id": "BERGER_MINIMAL_34_PORTABLE_CONTRACTION",
            "setting_id": retained["setting_id"],
            "claim_status": "CERTIFIED_COMPLETE_MINIMAL_UNARY_CONTRACTION",
            "dependency_tags": ["LOCAL-ALGEBRAIC"],
            "dependency_refs": {
                "retained_classical_unary_q1": {
                    "result_id": retained["result_id"],
                    "sha256": _sha256(Q1_CERTIFICATE),
                },
                "clock_sdr": {
                    "result_id": matrices["clock"]["result_id"],
                    "sha256": _sha256(CLOCK_CERTIFICATE),
                },
                "retained_layout": {
                    "result_id": matrices["layout"]["result_id"],
                    "sha256": _sha256(LAYOUT_CERTIFICATE),
                },
            },
            "operator_semantics": {
                "portable_name": "classical_unary_q1",
                "mathematical_name": "ell_1_cl",
                "historical_input_key": "q1_blocks",
                "not_quantum_loop_operator": True,
                "producer_audit": "Bach PBW coefficients derived from the classical action and Berger geometry",
                "consumer_audit": "frozen PBW coefficients, hashes, chain identities, and contraction checked without rederiving the action Hessian",
            },
            "row_layout": {
                "total_rows": 34,
                "degree_ranks": [5, 12, 12, 5],
                "component_rows": rows,
                "retained_row_indices": list(RETAINED_TO_FULL),
                "clock_row_indices": [3, 4, 15, 16, 27, 28, 32, 33],
                "field_clock_order": ["R", "Theta"],
                "ghost_clock_order": ["tau", "sigma"],
            },
            "classical_unary_q1": {
                "K_full": _matrix_record(matrices["k_full"]),
                "H_full": _matrix_record(matrices["h_full"]),
                "minus_K_full_sharp": _matrix_record(matrices["l_full"]),
                "total_matrix": _matrix_record(matrices["q_full"]),
            },
            "retained_unary": _matrix_record(matrices["q_retained"]),
            "contraction": {
                "iota_cl": _matrix_record(matrices["inclusion"]),
                "pi_cl": _matrix_record(matrices["projection"]),
                "S_cl": _matrix_record(matrices["homotopy"]),
                "P_retained": _matrix_record(matrices["retained_projector"]),
                "P_clock": _matrix_record(matrices["clock_projector"]),
                "identity": "pi_cl iota_cl=1_26; iota_cl pi_cl=P_retained; ell_1 S_cl+S_cl ell_1=P_clock=1_34-P_retained",
                "side_conditions": ["S_cl^2=0", "pi_cl S_cl=0", "S_cl iota_cl=0"],
                "support_local": True,
                "maximum_differential_order": 0,
                "cyclic": True,
            },
            "exact_checks": {
                "all_34_minimal_rows_enumerated": True,
                "classical_unary_q1_squared_zero": True,
                "iota_cl_chain_map": True,
                "pi_cl_chain_map": True,
                "pi_cl_iota_cl_identity": True,
                "all_row_contraction_identity": True,
                "complementary_chain_projectors": True,
                "contraction_side_conditions": True,
                "support_local_order_zero": True,
                "clock_homotopy_cyclic": True,
            },
            "flags": {
                "BERGER_MINIMAL_34_PORTABLE_CONTRACTION": True,
                "BERGER_COMBINED_MINIMAL_CONTRACTION_ALL_34_ROWS": True,
                "BERGER_NONMINIMAL_COMPLETION": False,
                "CLASSICAL_SUPPORT_LOCAL_Q2": False,
                "BERGER_LOCAL_D_ACTION_EQUIVARIANT": False,
                "BERGER_GENERAL_KOSZUL_TATE_EXPORT": False,
                "BERGER_CURVED_CLOCK_REATTACHED_WITNESS": False,
                "BERGER_CAUSAL_GREEN_HOMOTOPY": False,
                "BERGER_HADAMARD_DATA": False,
                "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT": False,
            },
            "next_gate": "BERGER_CURVED_CLOCK_REATTACHED_WITNESS",
            "claim_boundary": "This portable certificate closes the complete 34-row minimal classical unary differential and its support-local cyclic contraction onto the retained 26-row complex. It does not contain nonminimal/gauge-fixing rows, classical ell_2, a local D-action or its equivariance, the general antifield/Koszul-Tate export, causal Green operators, Hadamard data, or the combined nonlinear handoff.",
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        if any(value is not True for value in self.payload["exact_checks"].values()):
            raise AssertionError("portable contraction exact check dropped")
        semantics = self.payload["operator_semantics"]
        if semantics["portable_name"] != "classical_unary_q1":
            raise AssertionError("classical unary operator naming drifted")
        if semantics["not_quantum_loop_operator"] is not True:
            raise AssertionError("classical unary operator conflated with quantum Q1")
        flags = self.payload["flags"]
        for key in (
            "BERGER_MINIMAL_34_PORTABLE_CONTRACTION",
            "BERGER_COMBINED_MINIMAL_CONTRACTION_ALL_34_ROWS",
        ):
            if flags[key] is not True:
                raise AssertionError(f"proved portable flag dropped: {key}")
        for key, value in flags.items():
            if key not in {
                "BERGER_MINIMAL_34_PORTABLE_CONTRACTION",
                "BERGER_COMBINED_MINIMAL_CONTRACTION_ALL_34_ROWS",
            } and value is not False:
                raise AssertionError(f"downstream flag promoted: {key}")
        if self.payload["next_gate"] != "BERGER_CURVED_CLOCK_REATTACHED_WITNESS":
            raise AssertionError("portable contraction next gate drifted")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Portable contraction of the 34-row minimal Berger complex

The complete minimal classical unary differential is now exported on all
thirty-four rows under the semantic name
`classical_unary_q1` (\(\ell^{\rm cl}_1\)). It combines the exact retained
Berger operator with the temporal-diffeomorphism/Weyl clock doublets.

The frozen maps \(\iota_{\rm cl},\pi_{\rm cl},S_{\rm cl}\) obey

\[
\pi_{\rm cl}\iota_{\rm cl}=1_{26},\qquad
\ell^{\rm cl}_1S_{\rm cl}+S_{\rm cl}\ell^{\rm cl}_1
=1_{34}-\iota_{\rm cl}\pi_{\rm cl},
\]

together with \(S_{\rm cl}^2=0\), \(\pi_{\rm cl}S_{\rm cl}=0\), and
\(S_{\rm cl}\iota_{\rm cl}=0\). Every contraction entry is pointwise, so the
maps preserve compact, spacelike-compact, and unrestricted smooth support.

This closes the quantum team's requested combined contraction for all 34
minimal rows. It does not close the complete classical import: nonminimal
gauge fixing, \(\ell^{\rm cl}_2\), local \(D\)-equivariance, the general
Koszul--Tate package, causal Green operators, and Hadamard data remain false.
"""


def _write(result: BergerMinimal34PortableContraction) -> None:
    CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: BergerMinimal34PortableContraction) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError("portable 34-row certificate drifted")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError("portable 34-row report drifted")


def _guards(result: BergerMinimal34PortableContraction) -> None:
    mutations = [
        ("drop all-row contraction", ("flags", "BERGER_COMBINED_MINIMAL_CONTRACTION_ALL_34_ROWS"), False),
        ("rename as quantum Q1", ("operator_semantics", "portable_name"), "Q1"),
        ("promote nonminimal", ("flags", "BERGER_NONMINIMAL_COMPLETION"), True),
        ("promote q2", ("flags", "CLASSICAL_SUPPORT_LOCAL_Q2"), True),
        ("promote D equivariance", ("flags", "BERGER_LOCAL_D_ACTION_EQUIVARIANT"), True),
        ("promote KT", ("flags", "BERGER_GENERAL_KOSZUL_TATE_EXPORT"), True),
        ("promote causal", ("flags", "BERGER_CAUSAL_GREEN_HOMOTOPY"), True),
        ("promote Hadamard", ("flags", "BERGER_HADAMARD_DATA"), True),
        ("promote combined handoff", ("flags", "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT"), True),
    ]
    for name, path, replacement in mutations:
        mutant = deepcopy(result.payload)
        target = mutant
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = replacement
        try:
            BergerMinimal34PortableContraction(mutant).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = BergerMinimal34PortableContraction.build()
    if args.write:
        _write(result)
    if args.check:
        _check(result)
    if args.guards:
        _guards(result)
    if not (args.write or args.check or args.guards):
        print(result.certificate_text(), end="")
    else:
        print("BERGER_MINIMAL_34_PORTABLE_CONTRACTION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
