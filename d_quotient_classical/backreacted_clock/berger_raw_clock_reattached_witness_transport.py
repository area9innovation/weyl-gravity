#!/usr/bin/env python3
"""Coherent raw-coordinate transport of the 34-row Berger witness.

The first curved ``W34`` candidate used the dressed clock coordinates but an
untransported identity middle block.  This module instead starts from the
certified BV-canonical clock dressing, constructs the witness in raw metric
coordinates with the action-normalized fibre identification, and transports
the whole package coherently.  It proves the exact algebraic identities and
the scalar-biwave principal blocks in raw coordinates.  It deliberately does
not infer advanced/retarded inverses from principal-symbol agreement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from d_quotient_classical.backreacted_clock.berger_curved_witness_export import (
    _adjoint_matrix,
    _clock_contraction_block,
    _matrix_add,
    _negative,
    _one,
    _pairing34,
    _record_bytes,
    _sparse_multiply,
    _zero,
)
from d_quotient_classical.backreacted_clock.berger_curved_witness_principal_compatibility import (
    _temporal_order_four,
)
from d_quotient_classical.backreacted_clock.berger_gauge_fixed_nonminimal_completion import (
    _exact_data as _gauge_fixed_data,
    _is_zero,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
    ROOT,
    _matrix_record,
)
from d_quotient_classical.backreacted_clock.berger_minimal_34_portable_contraction import (
    _embed_block,
    _exact_matrices as _minimal_data,
)


OLD_WITNESS_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_CURVED_CLOCK_REATTACHED_WITNESS.json"
COMPATIBILITY_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_CURVED_WITNESS_PRINCIPAL_COMPATIBILITY.json"
PRINCIPAL_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_CLOCK_REATTACHED_PRINCIPAL_WITNESS.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-raw-clock-reattached-witness-transport.md"
GENERATED_DIR = ROOT / "d_quotient_classical/generated/berger_raw_clock_reattached_witness"
ARTIFACT_PATHS = {
    name: GENERATED_DIR / f"{name}.json"
    for name in ("raw_to_dressed_F12", "dressed_to_raw_C12", "q34_raw", "W34_raw", "P34_raw", "pairing34_raw")
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def _identity(rank: int):
    result = _zero(rank, rank)
    for index in range(rank):
        result[index][index] = _one()
    return result


def _subtract(left, right):
    return [[left[row][column] + right[row][column].scale(-1)
             for column in range(len(left[0]))] for row in range(len(left))]


def _coordinate_maps(raw_metric_from_dressed):
    """Return F: raw -> dressed and C=F^{-1}: dressed -> raw."""

    c12 = _identity(12)
    for row in range(10):
        for column in range(12):
            c12[row][column] = raw_metric_from_dressed[row][column]
    identity = _identity(12)
    # C=I+N and N^2=0 for the clock shear, hence F=I-N=2I-C.
    f12 = [[identity[row][column] + identity[row][column]
            + c12[row][column].scale(-1) for column in range(12)]
           for row in range(12)]
    if not _is_zero(_subtract(_sparse_multiply(f12, c12), identity)):
        raise AssertionError("F C != I")
    if not _is_zero(_subtract(_sparse_multiply(c12, f12), identity)):
        raise AssertionError("C F != I")
    return f12, c12


def _raw_fibre_identification():
    alpha = sp.Symbol("alpha_B", nonzero=True)
    eta = (-1, 1, 1, 1)
    pairs = ((0, 0), (0, 1), (0, 2), (0, 3), (1, 1),
             (1, 2), (1, 3), (2, 2), (2, 3), (3, 3))
    result = _zero(12, 12)
    for index, (first, second) in enumerate(pairs):
        density_factor = 1 if first == second else 2
        result[index][index] = _one(
            sp.Rational(4, 1)
            / (alpha * density_factor * eta[first] * eta[second])
        )
    return result


def _assemble_full(q_blocks, w_blocks):
    q34 = _zero(34, 34)
    w34 = _zero(34, 34)
    _embed_block(q34, q_blocks[0], 5, 0)
    _embed_block(q34, q_blocks[1], 17, 5)
    _embed_block(q34, q_blocks[2], 29, 17)
    _embed_block(w34, w_blocks[0], 0, 5)
    _embed_block(w34, w_blocks[1], 5, 17)
    _embed_block(w34, w_blocks[2], 17, 29)
    return q34, w34


def _p_blocks(q_blocks, w_blocks):
    k, h, ell = q_blocks
    c, j, c_dual = w_blocks
    return (
        _sparse_multiply(c, k),
        _matrix_add(_sparse_multiply(k, c), _sparse_multiply(j, h)),
        _matrix_add(_sparse_multiply(h, j), _sparse_multiply(c_dual, ell)),
        _sparse_multiply(ell, c_dual),
    )


def _full_from_diagonal(blocks):
    result = _zero(34, 34)
    for block, offset in zip(blocks, (0, 5, 17, 29), strict=True):
        _embed_block(result, block, offset, offset)
    return result


def _exact_data() -> dict[str, object]:
    minimal = _minimal_data()
    gauge = _gauge_fixed_data()
    f12, c12 = _coordinate_maps(gauge["raw_map"])

    q_new = minimal["q_full"]
    k_new = [row[0:5] for row in q_new[5:17]]
    h_new = [row[5:17] for row in q_new[17:29]]
    ell_new = [row[17:29] for row in q_new[29:34]]

    # y_new=U y_raw with U_field=F and U_antifield=F^{-sharp}.
    k_raw = _sparse_multiply(c12, k_new)
    h_raw = _sparse_multiply(
        _sparse_multiply(_adjoint_matrix(f12), h_new), f12
    )
    ell_raw = _sparse_multiply(ell_new, _adjoint_matrix(c12))
    q_blocks = (k_raw, h_raw, ell_raw)

    companion_new = _matrix_add(
        gauge["gauge_condition"], _clock_contraction_block()
    )
    companion_raw = _sparse_multiply(companion_new, f12)
    fibre_raw = _raw_fibre_identification()
    companion_dual_raw = _negative(_adjoint_matrix(companion_raw))
    w_blocks = (companion_raw, fibre_raw, companion_dual_raw)
    p_blocks = _p_blocks(q_blocks, w_blocks)
    q_raw, w_raw = _assemble_full(q_blocks, w_blocks)
    p_raw = _full_from_diagonal(p_blocks)
    pairing = _pairing34()

    # Exact differential and cyclic checks in raw coordinates.
    if not _is_zero(_sparse_multiply(h_raw, k_raw)):
        raise AssertionError("raw H K identity failed")
    if not _is_zero(_sparse_multiply(ell_raw, h_raw)):
        raise AssertionError("raw L H identity failed")
    q_cyclic = _matrix_add(
        _sparse_multiply(_adjoint_matrix(q_raw), pairing),
        _sparse_multiply(pairing, q_raw),
    )
    w_cyclic = _matrix_add(
        _sparse_multiply(_adjoint_matrix(w_raw), pairing),
        _sparse_multiply(pairing, w_raw),
    )
    if not _is_zero(q_cyclic) or not _is_zero(w_cyclic):
        raise AssertionError("raw transported package is not cyclic")

    # Coherent transport back reproduces the dressed q and gives the corrected
    # dressed middle block F J F^sharp rather than the rejected identity block.
    if not _is_zero(_subtract(_sparse_multiply(f12, k_raw), k_new)):
        raise AssertionError("K transport failed")
    h_new_replayed = _sparse_multiply(
        _sparse_multiply(_adjoint_matrix(c12), h_raw), c12
    )
    if not _is_zero(_subtract(h_new_replayed, h_new)):
        raise AssertionError("H transport failed")
    if not _is_zero(_subtract(_sparse_multiply(ell_raw, _adjoint_matrix(f12)), ell_new)):
        raise AssertionError("identity-row transport failed")
    companion_new_replayed = _sparse_multiply(companion_raw, c12)
    if not _is_zero(_subtract(companion_new_replayed, companion_new)):
        raise AssertionError("companion transport failed")
    fibre_new = _sparse_multiply(
        _sparse_multiply(f12, fibre_raw), _adjoint_matrix(f12)
    )

    # The raw coordinate system is the coordinate system of the independently
    # certified full-gauge principal theorem.
    temporal = tuple(
        _temporal_order_four(_matrix_record(block), 0, rank)
        for block, rank in zip(p_blocks, (5, 12, 12, 5), strict=True)
    )
    ghost4, field4, antifield4, identity4 = temporal
    if ghost4 != sp.eye(5) or identity4 != sp.eye(5):
        raise AssertionError("raw endpoint scalar-biwave principal failed")
    if field4[:10, :10] != sp.eye(10):
        raise AssertionError("raw metric scalar-biwave principal failed")
    if antifield4[:10, :10] != sp.eye(10):
        raise AssertionError("raw metric-antifield scalar-biwave principal failed")
    if field4[10:12, 10:12] != sp.zeros(2, 2):
        raise AssertionError("contractible clock diagonal acquired order four")

    return {
        "F12": f12,
        "C12": c12,
        "q34_raw": q_raw,
        "W34_raw": w_raw,
        "P34_raw": p_raw,
        "pairing34_raw": pairing,
        "fibre_new": fibre_new,
        "temporal": temporal,
    }


def _artifact(path: Path, body: bytes) -> dict[str, str]:
    return {
        "format": "JSON_EXACT_SPARSE_OPERATOR",
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(body).hexdigest(),
    }


def build() -> tuple[dict[str, object], dict[Path, bytes]]:
    data = _exact_data()
    matrices = {
        "raw_to_dressed_F12": data["F12"],
        "dressed_to_raw_C12": data["C12"],
        "q34_raw": data["q34_raw"],
        "W34_raw": data["W34_raw"],
        "P34_raw": data["P34_raw"],
        "pairing34_raw": data["pairing34_raw"],
    }
    bodies = {
        ARTIFACT_PATHS[name]: _record_bytes(_matrix_record(matrix))
        for name, matrix in matrices.items()
    }
    ghost4, field4, antifield4, identity4 = data["temporal"]
    payload: dict[str, object] = {
        "schema": "pure-weyl-berger-raw-clock-reattached-witness-transport-v1",
        "result_id": "BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT",
        "setting_id": json.loads(PRINCIPAL_CERTIFICATE.read_text())["setting_id"],
        "claim_status": "CERTIFIED_RAW_BV_TRANSPORT_PRINCIPAL_COMPATIBLE_GREEN_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            "submitted_curved_candidate": _dependency(OLD_WITNESS_CERTIFICATE),
            "candidate_compatibility_audit": _dependency(COMPATIBILITY_CERTIFICATE),
            "clock_reattached_principal": _dependency(PRINCIPAL_CERTIFICATE),
        },
        "coordinate_transport": {
            "direction": "F12 maps raw fields to dressed fields; C12=F12^{-1}",
            "maximum_order": 1,
            "support_local": True,
            "BV_canonical": True,
            "F12_C12_identity": True,
            "C12_F12_identity": True,
            "artifacts": {
                name: _artifact(ARTIFACT_PATHS[name], bodies[ARTIFACT_PATHS[name]])
                for name in ("raw_to_dressed_F12", "dressed_to_raw_C12")
            },
        },
        "operators": {
            name: _artifact(ARTIFACT_PATHS[name], bodies[ARTIFACT_PATHS[name]])
            for name in ("q34_raw", "W34_raw", "P34_raw", "pairing34_raw")
        },
        "raw_principal_audit": {
            "comparison_covector": [1, 0, 0, 0],
            "ghost_block_equals_I5": ghost4 == sp.eye(5),
            "metric_block_equals_I10": field4[:10, :10] == sp.eye(10),
            "metric_antifield_block_equals_I10": antifield4[:10, :10] == sp.eye(10),
            "identity_block_equals_I5": identity4 == sp.eye(5),
            "clock_diagonal_order_four_rank": field4[10:12, 10:12].rank(),
            "metric_to_clock_order_four_rank": field4[10:12, :10].rank(),
            "interpretation": "the rank-eight dressed metric subblock is a differential-coordinate presentation effect; raw coordinates expose a triangular metric-to-clock extension",
        },
        "exact_checks": {
            "raw_q_squared_zero": True,
            "raw_q_cyclic": True,
            "raw_W_cyclic": True,
            "raw_P_equals_qW_plus_Wq": True,
            "field_transport_exact": True,
            "antifield_transport_exact": True,
            "companion_transport_exact": True,
            "raw_scalar_biwave_principal_exact": True,
            "clock_diagonal_remains_nonpropagating_at_order_four": True,
        },
        "flags": {
            "BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT": True,
            "BERGER_RAW_CLOCK_REATTACHED_PRINCIPAL_COMPATIBILITY": True,
            "BERGER_RAW_CLOCK_REATTACHED_GREEN_INVERSION": False,
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
        },
        "next_gate": "BERGER_RAW_ENDPOINT_GREEN_FACTOR_OR_EXTENSION",
        "claim_boundary": (
            "This certificate repairs the coordinate mismatch in the submitted W34 candidate. "
            "It proves a coherent support-local BV-canonical raw/dressed transport, exact cyclic "
            "witness identities, and the independently required raw scalar-biwave principal blocks. "
            "It does not prove Green hyperbolicity of the complete lower-order curved operator, "
            "construct advanced/retarded inverses, or promote the retained 26-row causal homotopy."
        ),
    }
    return payload, bodies


def _report() -> str:
    return r"""# Raw clock-reattached Berger witness transport

The clock dressing is a first-order BV-canonical differential coordinate
change.  Consequently the scalar-biwave theorem must be compared in raw
metric coordinates, not against the isolated ten-row dressed subblock.

The coherent transport uses

\[
J_{\rm raw}=\frac4{\alpha_B}R_{\rm raise},\qquad
J_{\rm dressed}=FJ_{\rm raw}F^\sharp,
\]

and transports the gauge companion, the unary differential, antifields and
pairing at the same time.  Coefficientwise PBW checks prove

\[
q_{34,\rm raw}^2=0,
\qquad
P_{34,\rm raw}=q_{34,\rm raw}W_{34,\rm raw}
 +W_{34,\rm raw}q_{34,\rm raw},
\]

with exact cyclicity.  At the normalized noncharacteristic covector, the raw
ghost, metric, metric-antifield and identity principal blocks are
\(I_5,I_{10},I_{10},I_5\).  The two clock rows have no clock-to-clock
order-four diagonal.  They occur only as a triangular metric-to-clock
extension and remain the already certified local contractible sector.

This resolves the apparent rank-eight mismatch: it was a differential
coordinate-presentation effect.  The causal flag remains false.  The next
gate is to factor, filter, or otherwise construct Green operators for the
complete lower-order raw endpoint operator; principal agreement alone is not
a Green theorem.
"""


def write() -> dict[str, object]:
    payload, bodies = build()
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    for path, body in bodies.items():
        path.write_bytes(body)
    CERTIFICATE_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    REPORT_PATH.write_text(_report())
    return payload


def check() -> None:
    payload, bodies = build()
    expected = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if CERTIFICATE_PATH.read_text() != expected:
        raise AssertionError("raw witness transport certificate drifted")
    if REPORT_PATH.read_text() != _report():
        raise AssertionError("raw witness transport report drifted")
    for path, body in bodies.items():
        if path.read_bytes() != body:
            raise AssertionError(f"raw witness artifact drifted: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
        payload = json.loads(CERTIFICATE_PATH.read_text())
    else:
        payload = write()
    print(payload["result_id"] + ": PASS")
    print("raw scalar-biwave principal: exact")
    print("causal Green homotopy: OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
