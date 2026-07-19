"""Independent verifier for the product-background full-BV join boundary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/PRODUCT_S2_S2_FULL_BV_JOIN_BOUNDARY.json"


def verify() -> None:
    data = json.loads(CERTIFICATE.read_text())
    for dependency in data["dependencies"].values():
        path = ROOT / dependency["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != dependency["sha256"]:
            raise AssertionError("dependency digest mismatch")
        source = json.loads(path.read_text())
        if source["result_id"] != dependency["result_id"]:
            raise AssertionError("dependency identity mismatch")

    source_manifest = data["provenance"]["source_manifest"]
    for relative_path, expected in source_manifest.items():
        if hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest() != expected:
            raise AssertionError("source manifest mismatch")
    manifest_digest = hashlib.sha256(
        json.dumps(source_manifest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if manifest_digest != data["provenance"]["source_manifest_sha256"]:
        raise AssertionError("source-manifest digest mismatch")

    product = json.loads(
        (HERE / "certificates/PRODUCT_S2_S2_GHOST_MINIMAL_VECTOR_DETERMINANT_PRECERTIFICATE.json").read_text()
    )
    full_bv = json.loads(
        (HERE / "certificates/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json").read_text()
    )
    if product["scope"]["background"] != "S2(1) x S2(2)":
        raise AssertionError("product background mismatch")
    if "round_S4" not in full_bv["integration_slice"]["gauge"]:
        raise AssertionError("full-BV background mismatch")
    if data["scope_comparison"]["same_background"] is not False:
        raise AssertionError("background mismatch was erased")
    if data["join_decision"]["round_full_BV_rows_can_be_reused_on_product"] is not False:
        raise AssertionError("round-S4 rows were reused on product")
    if data["claim_flags"]["PRODUCT_FULL_BV_DETERMINANT_COMPUTED"] is not False:
        raise AssertionError("product full-BV determinant over-promoted")
    if data["minimal_missing_carrier"]["primary"] != "PRODUCT_S2_S2_GAUGE_FIXED_METRIC_HESSIAN_SPECTRAL_CARRIER":
        raise AssertionError("minimal physical carrier drifted")


def main() -> int:
    verify()
    print("PRODUCT S2xS2 FULL-BV JOIN BOUNDARY independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
