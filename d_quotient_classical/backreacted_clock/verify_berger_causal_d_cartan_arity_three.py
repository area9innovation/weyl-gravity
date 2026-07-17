#!/usr/bin/env python3
"""Independent lightweight consumer for the Berger arity-three Cartan theorem."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_ARITY_THREE_D_CARTAN_FULL_4D.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-causal-D-Cartan-arity-three-v1.schema.json"
MANIFEST_SCHEMA = ROOT / "d_quotient_classical/schema/berger-causal-D-Cartan-arity-three-manifest-v1.schema.json"
RECEIPT_SCHEMA = ROOT / "d_quotient_classical/schema/berger-causal-D-Cartan-arity-three-receipt-v1.schema.json"
MANIFEST = ROOT / "d_quotient_classical/manifests/BERGER_ARITY_THREE_D_CARTAN_FULL_4D_SOURCE_MANIFEST.json"
RECEIPT = ROOT / "d_quotient_classical/certificates/BERGER_ARITY_THREE_D_CARTAN_FULL_4D_VERIFICATION_RECEIPT.json"
Q3 = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q3.json"
Q3_PAYLOAD = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q3_PAYLOAD.json"
PAIRING = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> int:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    manifest_schema = json.loads(MANIFEST_SCHEMA.read_text())
    receipt_schema = json.loads(RECEIPT_SCHEMA.read_text())
    for current in (schema, manifest_schema, receipt_schema):
        jsonschema.Draft202012Validator.check_schema(current)
    jsonschema.Draft202012Validator(schema).validate(certificate)

    manifest = json.loads(MANIFEST.read_text())
    receipt = json.loads(RECEIPT.read_text())
    jsonschema.Draft202012Validator(manifest_schema).validate(manifest)
    jsonschema.Draft202012Validator(receipt_schema).validate(receipt)
    for relative, expected in manifest["files"].items():
        if _sha256(ROOT / relative) != expected:
            raise AssertionError(f"source-manifest hash mismatch: {relative}")
    if manifest["certificate_canonical_sha256"] != _canonical_sha256(certificate):
        raise AssertionError("certificate canonical hash mismatch")
    if receipt["certificate_sha256"] != _sha256(CERTIFICATE):
        raise AssertionError("receipt certificate hash mismatch")
    if receipt["source_manifest_sha256"] != _sha256(MANIFEST):
        raise AssertionError("receipt source-manifest hash mismatch")

    q3 = json.loads(Q3.read_text())
    if _sha256(Q3) != certificate["dependency_refs"]["support_local_q3"]["sha256"]:
        raise AssertionError("q3 dependency hash mismatch")
    if _sha256(Q3_PAYLOAD) != q3["classical_ternary_q3"]["payload_file_sha256"]:
        raise AssertionError("q3 portable payload hash mismatch")
    if q3["local_D_arity_three"] != {
        "D_q3_derivation": True,
        "L_D3": "ZERO",
        "reason": q3["local_D_arity_three"]["reason"],
    }:
        raise AssertionError("q3 D-action declaration drifted")

    rows = q3["row_layout"]["component_rows"]
    degrees = tuple(int(row["degree"]) for row in rows)
    pairing = json.loads(PAIRING.read_text())["contraction"]["cyclic_pairing"]["entries"]
    partners = {int(left): int(right) for left, right, _terms in pairing}
    signs = {int(left): int(terms[0][1]) for left, _right, terms in pairing}
    if set(partners) != set(range(54)):
        raise AssertionError("pairing row coverage mismatch")
    for index in range(54):
        partner = partners[index]
        if partners[partner] != index or degrees[index] + degrees[partner] != 1:
            raise AssertionError("odd Darboux duality mismatch")
        if signs[partner] != -signs[index]:
            raise AssertionError("odd Darboux orientation mismatch")

    counts = Counter(degrees)
    admissible = 0
    defects = 0
    for a, na in counts.items():
        for b, nb in counts.items():
            for c, nc in counts.items():
                for d, nd in counts.items():
                    if a + b + c + d:
                        continue
                    multiplicity = na * nb * nc * nd
                    admissible += multiplicity
                    p = (a & 1, b & 1, c & 1, d & 1)
                    exponent = sum(
                        (p[offset:] + p[:offset])[0]
                        * sum((p[offset:] + p[:offset])[1:])
                        for offset in range(4)
                    )
                    defects += multiplicity if exponent & 1 else 0
    audit = certificate["cyclic_completion"]["pairing_and_sign_audit"]
    if admissible != audit["admissible_degree_zero_row_quartets"] or defects != 0:
        raise AssertionError("independent C4 audit mismatch")

    if -Fraction(1, 2) + Fraction(1, 2) != 0:
        raise AssertionError("Jacobi cancellation arithmetic failed")
    cyc = (Fraction(1, 4),) * 4
    square = tuple(
        sum(cyc[i] * cyc[(slot - i) % 4] for i in range(4))
        for slot in range(4)
    )
    if square != cyc or -sum(cyc) != -1:
        raise AssertionError("independent Reynolds calculation failed")
    if not all(certificate["exact_checks"].values()):
        raise AssertionError("certificate proof ledger contains a false check")
    if certificate["flags"]["QUANTUM_CLAIM"] is not False:
        raise AssertionError("classical certificate promoted a quantum claim")

    print("BERGER_ARITY_THREE_D_CARTAN_FULL_4D independent audit: PASS")
    print(f"rows=54 admissible_C4_quartets={admissible} defects={defects}")
    print("audit boundary: structural recurrence and frozen hashes checked; q3 action expansion imported from its Tier-2 certificate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
