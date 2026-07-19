"""Independent structural verifier for the completed Berger A104."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERTIFICATE = HERE / "certificates/BERGER_A104_ENDPOINT_COMPLETION.json"
PARTIAL = HERE / "generated/berger_a104_global_partial_assembly/global_A104_partial.json"
EXPORT = ROOT / "d_quotient_classical/certificates/BERGER_ENDPOINT_A24_CAUCHY_EXPORT.json"
FULL = HERE / "generated/berger_a104_endpoint_completion/global_A104.json"
SOURCE_PATHS = (
    "quantum-weyl/lorentzian/berger_a104_endpoint_completion.py",
    "quantum-weyl/lorentzian/berger_a104_endpoint_completion_certificate.py",
    "quantum-weyl/lorentzian/verify_berger_a104_endpoint_completion.py",
    "quantum-weyl/lorentzian/schema/berger-a104-endpoint-completion-v1.schema.json",
    "quantum-weyl/lorentzian/tests/test_berger_a104_endpoint_completion.py",
)


def _digest(body: object) -> str:
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _entry_map(record: dict) -> dict[tuple[int, int], object]:
    return {(row, column): terms for row, column, terms in record["entries"]}


def verify() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    partial = json.loads(PARTIAL.read_text())
    export = json.loads(EXPORT.read_text())
    full = json.loads(FULL.read_text())

    full_body = {"shape": full["shape"], "entries": full["entries"]}
    if full.get("sha256") != _digest(full_body):
        raise AssertionError("full A104 internal hash mismatch")
    if hashlib.sha256((json.dumps(full, indent=2, sort_keys=True) + "\n").encode()).hexdigest() != certificate["full_operator"]["sha256"]:
        raise AssertionError("full A104 file hash mismatch")

    full_entries = _entry_map(full)
    partial_entries = _entry_map(partial)
    for coordinate, terms in partial_entries.items():
        if full_entries.get(coordinate) != terms:
            raise AssertionError("previously certified A104 coordinate changed")

    expected = dict(partial_entries)
    for insertion in certificate["endpoint_insertion_ledger"]:
        block = export["derived_A12_blocks"][insertion["block_id"]]
        local = _entry_map(block)
        for (row, column), terms in local.items():
            coordinate = (
                insertion["global_row_indices"][row],
                insertion["global_column_indices"][column],
            )
            if coordinate in expected:
                raise AssertionError("endpoint block overlaps a prior nonzero entry")
            expected[coordinate] = terms
    if expected != full_entries:
        raise AssertionError("full A104 has missing or extra sparse entries")

    if certificate["coverage"] != {
        "closed_blocks": ["ghost_A12", "identity_A12"],
        "known_coordinates": 10816,
        "known_nonzero_sparse_entries": len(full_entries),
        "total_coordinates": 10816,
        "unknown_coordinates": 0,
    }:
        raise AssertionError("full A104 coverage mismatch")
    if certificate["claim_flags"]["BERGER_Q_CAUCHY_104"] is not False:
        raise AssertionError("q_Cauchy was over-promoted")
    if certificate["claim_flags"]["BERGER_HADAMARD_DATA"] is not False:
        raise AssertionError("Hadamard data were over-promoted")

    manifest = certificate["provenance"]["source_manifest"]
    expected_manifest = {
        path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        for path in SOURCE_PATHS
    }
    if manifest != expected_manifest:
        raise AssertionError("source manifest mismatch")
    if certificate["provenance"]["source_manifest_sha256"] != _digest(manifest):
        raise AssertionError("source manifest aggregate hash mismatch")


def main() -> int:
    verify()
    print("BERGER A104 ENDPOINT COMPLETION independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
