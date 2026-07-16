#!/usr/bin/env python3
"""Authoritative 34-row Berger curved-witness candidate export.

The export is deliberately separated from the Green theorem.  It freezes the
complete minimal cyclic data ``(W34, P34, pairing34)`` with

    P34 = q34 W34 + W34 q34

in the invariant-frame PBW algebra.  The witness combines the exact curved
Diff x Weyl companion with the pointwise clock contraction.  Failure of this
candidate in a downstream analytic test is scoped to this candidate; it is
not a nonexistence theorem for all possible witnesses.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import sympy as sp

from d_quotient_classical.backreacted_clock.berger_gauge_fixed_nonminimal_completion import (
    CERTIFICATE_PATH as GAUGE_CERTIFICATE,
    _adjoint_matrix,
    _exact_data as _gauge_fixed_data,
    _is_zero,
    _matrix_add,
    _negative,
    _sparse_multiply,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
    ROOT,
    _matrix_record,
)
from d_quotient_classical.backreacted_clock.berger_minimal_34_portable_contraction import (
    CERTIFICATE_PATH as MINIMAL_CERTIFICATE,
    _embed_block,
    _exact_matrices as _minimal_data,
    _one,
    _zero,
)
from d_quotient_classical.backreacted_clock.berger_nonminimal_algebraic_completion import (
    CERTIFICATE_PATH as NONMINIMAL_CERTIFICATE,
)


RETAINED_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_CURVED_CLOCK_REATTACHED_WITNESS.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-curved-clock-reattached-witness.md"
GENERATED_DIR = ROOT / "d_quotient_classical/generated/berger_curved_clock_reattached_witness"
W34_PATH = GENERATED_DIR / "W34.json"
P34_PATH = GENERATED_DIR / "P34.json"
PAIRING34_PATH = GENERATED_DIR / "pairing34.json"


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_hash(value: object) -> str:
    return _sha256_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    )


def _record_bytes(record: dict[str, object]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()


def _consumer_canonical_record(record: dict[str, object]) -> dict[str, object]:
    """Match the independent consumer's order/word canonicalization."""

    entries = []
    for row, column, terms in record["entries"]:
        ordered = sorted(
            terms,
            key=lambda term: (
                sum(term[0]),
                tuple(axis for axis, count in enumerate(term[0]) for _ in range(count)),
            ),
        )
        entries.append([row, column, ordered])
    body = {"shape": record["shape"], "entries": entries}
    return {**body, "sha256": _canonical_hash(body)}


def _current_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def _pairing34():
    pairing = _zero(34, 34)
    for index in range(5):
        pairing[index][29 + index] = _one()
        pairing[29 + index][index] = _one(-1)
    for index in range(12):
        pairing[5 + index][17 + index] = _one()
        pairing[17 + index][5 + index] = _one(-1)
    return pairing


def _clock_contraction_block():
    """The M-to-G clock part of the certified minimal homotopy."""

    block = _zero(5, 12)
    block[3][11] = _one()      # s Theta = tau
    block[4][10] = _one(-1)   # s R = -sigma
    return block


def _middle_identification():
    middle = _zero(12, 12)
    # This is the polynomial normalization already frozen by the retained
    # causal-witness certificate.  The action-normalized raised-index map is
    # a distinct convention and would introduce 1/alpha_B into this contract.
    for index in range(10):
        middle[index][index] = _one()
    return middle


def _assemble_candidate() -> dict[str, object]:
    minimal = _minimal_data()
    gauge = _gauge_fixed_data()
    q34 = minimal["q_full"]

    # The transported curved companion supplies the differential gauge part;
    # the already-certified clock homotopy supplies the algebraic complement.
    m_to_g = _matrix_add(gauge["gauge_condition"], _clock_contraction_block())
    e_to_m = _middle_identification()
    i_to_e = _negative(_adjoint_matrix(m_to_g))

    w34 = _zero(34, 34)
    _embed_block(w34, m_to_g, 0, 5)
    _embed_block(w34, e_to_m, 5, 17)
    _embed_block(w34, i_to_e, 17, 29)

    # Assemble qW+Wq by degree blocks.  This avoids two monolithic 34x34 PBW
    # products and keeps peak memory proportional to one physical block.
    k = [row[0:5] for row in q34[5:17]]
    h = [row[5:17] for row in q34[17:29]]
    identity_row = [row[17:29] for row in q34[29:34]]
    p34 = _zero(34, 34)
    _embed_block(p34, _sparse_multiply(m_to_g, k), 0, 0)
    _embed_block(
        p34,
        _matrix_add(_sparse_multiply(k, m_to_g), _sparse_multiply(e_to_m, h)),
        5,
        5,
    )
    _embed_block(
        p34,
        _matrix_add(_sparse_multiply(h, e_to_m), _sparse_multiply(i_to_e, identity_row)),
        17,
        17,
    )
    _embed_block(p34, _sparse_multiply(identity_row, i_to_e), 29, 29)

    pairing = _pairing34()
    q_cyclic = _matrix_add(
        _sparse_multiply(_adjoint_matrix(q34), pairing),
        _sparse_multiply(pairing, q34),
    )
    w_cyclic = _matrix_add(
        _sparse_multiply(_adjoint_matrix(w34), pairing),
        _sparse_multiply(pairing, w34),
    )
    if not _is_zero(q_cyclic):
        raise AssertionError("q34 is not cyclic for pairing34")
    if not _is_zero(w_cyclic):
        raise AssertionError("W34 is not cyclic for pairing34")

    return {
        "minimal_certificate": json.loads(MINIMAL_CERTIFICATE.read_text()),
        "nonminimal_certificate": json.loads(NONMINIMAL_CERTIFICATE.read_text()),
        "gauge_certificate": json.loads(GAUGE_CERTIFICATE.read_text()),
        "q34": q34,
        "W34": w34,
        "P34": p34,
        "pairing34": pairing,
    }


def _artifact(path: Path, body: bytes) -> dict[str, str]:
    return {
        "format": "JSON_EXACT_SPARSE_OPERATOR",
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256_bytes(body),
    }


def build() -> tuple[dict[str, object], dict[Path, bytes]]:
    data = _assemble_candidate()
    records = {
        W34_PATH: _matrix_record(data["W34"]),
        P34_PATH: _matrix_record(data["P34"]),
        PAIRING34_PATH: _matrix_record(data["pairing34"]),
    }
    bodies = {path: _record_bytes(record) for path, record in records.items()}
    minimal = data["minimal_certificate"]
    nonminimal = data["nonminimal_certificate"]
    gauge = data["gauge_certificate"]
    q_record = _consumer_canonical_record(_matrix_record(data["q34"]))
    payload: dict[str, object] = {
        "schema": "quantum-weyl-berger-curved-witness-export-v1",
        "result_id": "BERGER_CURVED_CLOCK_REATTACHED_WITNESS",
        "result_state": "CURVED_WITNESS_CANDIDATE",
        "classical_commit": _current_commit(),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "setting_id": minimal["setting_id"],
        "row_layout": {"degree_ranks": [5, 12, 12, 5], "total_rows": 34},
        "operators": {
            "W34": _artifact(W34_PATH, bodies[W34_PATH]),
            "P34": _artifact(P34_PATH, bodies[P34_PATH]),
            "pairing34": _artifact(PAIRING34_PATH, bodies[PAIRING34_PATH]),
        },
        "coordinate_transport": {
            "curved_companion_sha256": nonminimal["gauge_fermion_template"]["curved_companion"]["sha256"],
            "raw_metric_from_dressed_sha256": gauge["gauge_fermion"]["raw_metric_from_dressed"]["sha256"],
            "transported_gauge_condition_sha256": gauge["gauge_fermion"]["gauge_condition_A"]["sha256"],
            "row_layout_sha256": _canonical_hash(minimal["row_layout"]),
            "q34_sha256": q_record["sha256"],
        },
        "claim_boundary": (
            "This authoritative classical export freezes one geometrically derived "
            "34-row curved witness candidate, its exact target P34=q34 W34+W34 q34, "
            "and the nondegenerate cyclic pairing34. It does not prove that P34 has "
            "advanced or retarded inverses. Failure of this submitted candidate does "
            "not establish global nonexistence of curved witnesses."
        ),
    }
    return payload, bodies


def _report(payload: dict[str, object]) -> str:
    return r"""# Authoritative 34-row Berger curved-witness candidate

The classical producer now exports the complete minimal operators

\[
W_{34},\qquad P_{34}=q_{34}W_{34}+W_{34}q_{34},\qquad \omega_{34}.
\]

The witness combines the exact transported curved Diff--Weyl companion, the
pointwise temporal/Weyl clock contraction, and the polynomial middle-block
normalization frozen by the retained causal witness. The canonical pairing is nondegenerate, and both
\(q_{34}\) and \(W_{34}\) are cyclic coefficientwise.

This is an authoritative candidate export, not yet a Green theorem.  A
downstream defect rejects this candidate only; it is not a theorem that no
other local curved witness exists.  Advanced/retarded inversion and the
retained 26-row causal homotopy remain separate fail-closed gates.
"""


def write() -> dict[str, object]:
    payload, bodies = build()
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    for path, body in bodies.items():
        path.write_bytes(body)
    CERTIFICATE_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    REPORT_PATH.write_text(_report(payload))
    return payload


def check() -> None:
    payload, bodies = build()
    expected = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if CERTIFICATE_PATH.read_text() != expected:
        raise SystemExit(f"stale certificate: {CERTIFICATE_PATH}")
    if REPORT_PATH.read_text() != _report(payload):
        raise SystemExit(f"stale report: {REPORT_PATH}")
    for path, body in bodies.items():
        if path.read_bytes() != body:
            raise SystemExit(f"stale operator artifact: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
    else:
        payload = write()
        print(json.dumps({
            "result_id": payload["result_id"],
            "result_state": payload["result_state"],
            "operators": payload["operators"],
        }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
