#!/usr/bin/env python3
"""Finalize the verified staged Berger ``q3`` as portable exact row chunks.

The expensive geometry, canonical transport, and identity replay live in the
content-addressed Tier-2 cache.  This finalizer refuses to run without the
matching verification receipt.  It serializes one output row at a time as a
deterministic gzip-compressed strict-JSON document, avoiding both the former
17 GB monolithic producer and a repository-hostile half-gigabyte JSON file.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import pickle
import sys

if os.environ.get("BERGER_TAYLOR_ORDER") != "3":
    raise RuntimeError("launch the q3 finalizer with BERGER_TAYLOR_ORDER=3")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.backreacted_clock import berger_support_local_q3_cache as cache
from d_quotient_classical.backreacted_clock.berger_support_local_q2 import (
    GAUGE_FIXED_PARITIES,
)
from d_quotient_classical.backreacted_clock.berger_support_local_q2_export import (
    _digest,
    _multiindex,
    _quadratic_coefficient,
)


CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q3.json"
PAYLOAD_PATH = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q3_PAYLOAD.json"
CHUNK_DIR = ROOT / "d_quotient_classical/generated/berger_support_local_q3"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-support-local-q3.md"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def _encoded_row(output: int, operator) -> dict[str, object]:
    terms = [
        [
            first,
            _multiindex(first_word),
            second,
            _multiindex(second_word),
            third,
            _multiindex(third_word),
            _quadratic_coefficient(coefficient),
        ]
        for first, first_word, second, second_word, third, third_word, coefficient
        in operator.terms
    ]
    # Internal words are lexicographically canonical as axis tuples.  The
    # portable representation stores PBW multi-indices, whose lexicographic
    # order is different (for example ``(0,1)`` versus ``(0,0,2)``).  Sort in
    # the declared portable key and assert uniqueness after conversion.
    terms.sort(
        key=lambda term: (
            term[0], tuple(term[1]), term[2], tuple(term[3]), term[4], tuple(term[5])
        )
    )
    keys = [
        (term[0], tuple(term[1]), term[2], tuple(term[3]), term[4], tuple(term[5]))
        for term in terms
    ]
    if len(keys) != len(set(keys)):
        raise AssertionError(f"row {output} has duplicate portable PBW keys")
    return {
        "schema": "pure-weyl-berger-support-local-q3-row-v1",
        "output": output,
        "terms": terms,
    }


def _write_deterministic_gzip(path: Path, value: object) -> tuple[str, str]:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(gzip.compress(canonical + b"\n", compresslevel=9, mtime=0))
    temporary.replace(path)
    return hashlib.sha256(canonical).hexdigest(), _sha256(path)


def _verified_inputs() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    raw = _load_json(cache.RAW_RECEIPT)
    transport = _load_json(cache.TRANSPORT_RECEIPT)
    verify = _load_json(cache.VERIFY_RECEIPT)
    if not all(receipt["cache_key"] == cache.CACHE_KEY for receipt in (raw, transport, verify)):
        raise AssertionError("q3 cache-key mismatch")
    if transport["raw_artifact_sha256"] != raw["artifact_sha256"]:
        raise AssertionError("q3 raw-to-transport receipt chain is broken")
    if verify["raw_artifact_sha256"] != raw["artifact_sha256"]:
        raise AssertionError("q3 raw verification hash mismatch")
    if verify["transported_artifact_sha256"] != transport["artifact_sha256"]:
        raise AssertionError("q3 transported verification hash mismatch")
    if not all(verify["checks"].values()):
        raise AssertionError("q3 exact verification receipt contains a false check")
    if _sha256(cache.TRANSPORTED_PATH) != transport["artifact_sha256"]:
        raise AssertionError("q3 transported cache artifact drifted")
    return raw, transport, verify


def build() -> tuple[dict[str, object], dict[str, object]]:
    raw_receipt, transport_receipt, verify_receipt = _verified_inputs()
    q1 = _load_json(cache.Q1_CERTIFICATE)
    q2 = _load_json(cache.Q2_CERTIFICATE)
    d_action = _load_json(cache.D_CERTIFICATE)
    with cache.TRANSPORTED_PATH.open("rb") as handle:
        operators = pickle.load(handle)
    if len(operators) != 54:
        raise AssertionError("transported q3 does not have 54 rows")

    CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    chunks = []
    total_terms = 0
    nonzero_rows = 0
    maximum_order = 0
    for output, operator in enumerate(operators):
        row = _encoded_row(output, operator)
        path = CHUNK_DIR / f"row_{output:02d}.json.gz"
        canonical_hash, file_hash = _write_deterministic_gzip(path, row)
        row_maximum = max(
            (sum(term[1]) + sum(term[3]) + sum(term[5]) for term in row["terms"]),
            default=0,
        )
        chunks.append(
            {
                "output": output,
                "path": str(path.relative_to(ROOT)),
                "file_sha256": file_hash,
                "canonical_sha256": canonical_hash,
                "term_count": len(row["terms"]),
                "maximum_total_jet_order": row_maximum,
            }
        )
        total_terms += len(row["terms"])
        nonzero_rows += bool(row["terms"])
        maximum_order = max(maximum_order, row_maximum)

    payload: dict[str, object] = {
        "schema": "pure-weyl-berger-support-local-q3-payload-v1",
        "coefficient_field": "Q(sqrt(10))",
        "pbw_basis": "left-invariant Berger frame; words e0^n0 e1^n1 e2^n2 e3^n3",
        "shape": [54, 54, 54, 54],
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "storage": "deterministic-gzip-strict-json-row-chunks",
        "chunks": chunks,
    }
    summary = {
        "payload_path": str(PAYLOAD_PATH.relative_to(ROOT)),
        "payload_file_sha256": None,
        "total_rows": 54,
        "nonzero_rows": nonzero_rows,
        "term_count": total_terms,
        "maximum_total_jet_order": maximum_order,
        "payload_canonical_sha256": _digest(payload),
        "payload_format": "strict-json-manifest-plus-deterministic-gzip-strict-json-row-chunks",
        "chunk_count": 54,
        "support_local": True,
        "Taylor_convention": "suspended-graded-symmetric-factorial-v1",
    }
    if total_terms != transport_receipt["term_count"]:
        raise AssertionError("portable q3 term count disagrees with transport receipt")
    if nonzero_rows != transport_receipt["nonzero_rows"]:
        raise AssertionError("portable q3 row count disagrees with transport receipt")
    if maximum_order != transport_receipt["maximum_total_jet_order"]:
        raise AssertionError("portable q3 jet order disagrees with transport receipt")

    certificate: dict[str, object] = {
        "schema": "pure-weyl-berger-support-local-q3-v1",
        "result_id": "BERGER_SUPPORT_LOCAL_Q3",
        "setting_id": q1["setting_id"],
        "claim_status": "CERTIFIED_COMPLETE_SUPPORT_LOCAL_CLASSICAL_Q3",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "gauge_fixed_classical_unary_q1": {"result_id": q1["result_id"], "sha256": _sha256(cache.Q1_CERTIFICATE)},
            "support_local_classical_q2": {"result_id": q2["result_id"], "sha256": _sha256(cache.Q2_CERTIFICATE)},
            "local_D_action": {"result_id": d_action["result_id"], "sha256": _sha256(cache.D_CERTIFICATE)},
        },
        "derivation": {
            "source": "covariant Weyl-plus-positive-clock action and nonlinear Diff semidirect Weyl BV master action",
            "method": "mixed third variation on three arbitrary four-dimensional jets",
            "not_fitted_to_residual_data": True,
            "background_fixture": "q=9/40, alpha_B=5, rho_bar=1, omega=3/4, lambda=119/480",
            "coefficient_field": "Q(sqrt(10))",
            "raw_minimal_rows": 34,
            "gauge_fixed_rows": 54,
            "raw_support_theorem": "only the twelve Euler-density rows have q3 because the nonlinear gauge action is field-linear and the ghost bracket is field-independent",
        },
        "row_layout": {
            "total_rows": 54,
            "component_rows": q1["row_layout"]["component_rows"],
            "parities": list(GAUGE_FIXED_PARITIES),
            "all_rows_ledgered": True,
        },
        "classical_ternary_q3": summary,
        "local_D_arity_three": {
            "L_D3": "ZERO",
            "reason": "the helical generator acts linearly as the central invariant derivative e0 on dressed component coefficients",
            "D_q3_derivation": True,
        },
        "exact_checks": {
            "q3_koszul_symmetry_raw_34_rows": True,
            "q1_q3_plus_q2_q2_arity_three_nilpotency_raw_coefficientwise": True,
            "quartic_action_cyclicity_raw_coefficientwise": True,
            "canonical_clock_transport_preserves_arity_three_identity": True,
            "canonical_gauge_fermion_transport_preserves_arity_three_identity": True,
            "q3_koszul_symmetry_gauge_fixed_54_rows": True,
            "D_q3_derivation_termwise": True,
            "L_D3_explicitly_zero_generator_action_is_linear": True,
            "all_54_output_rows_ledgered": True,
        },
        "tier_receipts": {
            "cache_key": cache.CACHE_KEY,
            "raw_receipt_sha256": _sha256(cache.RAW_RECEIPT),
            "transport_receipt_sha256": _sha256(cache.TRANSPORT_RECEIPT),
            "verify_receipt_sha256": _sha256(cache.VERIFY_RECEIPT),
            "publication_receipt_path": "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q3_TIER2_RECEIPT.json",
            "publication_receipt_sha256": "194673b3bef5b6c4a4125ac5e8e8ad44b12d3279c125aba565f52189cff06a1d",
            "raw_elapsed_seconds": raw_receipt["elapsed_seconds"],
            "transport_elapsed_seconds": transport_receipt["elapsed_seconds"],
            "verify_elapsed_seconds": verify_receipt["elapsed_seconds"],
            "test_tier": 2,
            "tier_3_not_run": "not a freeze, release, or paper-theorem promotion",
        },
        "flags": {
            "CLASSICAL_SUPPORT_LOCAL_Q3": True,
            "BERGER_LOCAL_D_ACTION_EQUIVARIANT_AT_ARITY_THREE": True,
            "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_Q3_EXPORT": True,
            "BERGER_ARITY_THREE_D_CARTAN_FULL_4D": False,
            "GENERAL_LOCAL_ANTIFIELD_KOSZUL_TATE_EXPORT": False,
        },
        "next_gates": ["BERGER_ARITY_THREE_D_CARTAN_FULL_4D", "GENERAL_LOCAL_ANTIFIELD_KOSZUL_TATE_EXPORT"],
        "claim_boundary": "This theorem exports the complete arbitrary-input four-dimensional classical q3 and explicit L_D3=0 declaration on the frozen 54-row gauge-fixed Berger BV complex. It proves the arity-three L-infinity identity, graded symmetry, action cyclicity, and local D derivation exactly. It does not by itself solve the arity-three D-Cartan recurrence, provide a background-independent antifield package, or establish a quantum or Hadamard theorem.",
    }
    return certificate, payload


def _report(certificate: dict[str, object]) -> str:
    q3 = certificate["classical_ternary_q3"]
    receipts = certificate["tier_receipts"]
    return f"""# Complete support-local Berger classical q3

The covariant Weyl--clock BV master action has been differentiated on three
arbitrary four-dimensional jets and transported through the certified clock,
nonminimal, and gauge-fixing canonical maps.  The complete 54-row operation
contains **{q3['term_count']}** exact sparse PBW terms on
**{q3['nonzero_rows']}** nonzero output rows, with maximum total jet order
**{q3['maximum_total_jet_order']}**.

The content-addressed Tier-2 chain took {receipts['raw_elapsed_seconds']:.1f}s
for action derivation, {receipts['transport_elapsed_seconds']:.1f}s for
canonical transport, and {receipts['verify_elapsed_seconds']:.1f}s for the
row-bounded exact replay.  It proves the arity-three part of `Q^2=0`, graded
symmetry, quartic action cyclicity, and the local `D` derivation.  Portable
data are deterministic gzip-compressed strict-JSON row chunks referenced by
a strict-JSON manifest; this is a storage encoding, not a reduced-mode claim.
Exact commands, elapsed times, peak memory, and the Tier-3 skip rationale are
recorded in `BERGER_SUPPORT_LOCAL_Q3_TIER2_RECEIPT.json`.

This supplies the missing classical input for the ND3 Cartan engine.  It does
not pre-decide whether the arity-three Cartan source is exact or obstructed,
and it does not promote any quantum or Hadamard claim.
"""


def _write(certificate: dict[str, object], payload: dict[str, object]) -> None:
    PAYLOAD_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    certificate["classical_ternary_q3"]["payload_file_sha256"] = _sha256(PAYLOAD_PATH)
    CERTIFICATE_PATH.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    REPORT_PATH.write_text(_report(certificate))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate, payload = build()
    if args.check:
        expected = json.loads(CERTIFICATE_PATH.read_text())
        if json.loads(PAYLOAD_PATH.read_text()) != payload:
            raise AssertionError("q3 payload manifest drifted")
        certificate["classical_ternary_q3"]["payload_file_sha256"] = _sha256(PAYLOAD_PATH)
        if expected != certificate:
            raise AssertionError("q3 certificate drifted")
    else:
        _write(certificate, payload)
    print("BERGER_SUPPORT_LOCAL_Q3: PASS")
    print(json.dumps(certificate["classical_ternary_q3"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
