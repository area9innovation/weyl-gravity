"""Independent verifier for the complete combined ell=2 cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_combined_cone_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_combined_cone_second_order.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    for record in payload["provenance"]["inputs"].values():
        assert _sha256(ROOT / record["path"]) == record["sha256"]
    classification = payload["classification"]
    assert classification["complete_combined_ell2_k0_common_zero_cone_second_order_extendible"] is True
    assert classification["all_m_both_parities_and_both_extra_polarizations_included"] is True
    assert classification["cancellations_between_axial_and_polar_moment_maps_included"] is True
    assert classification["general_ell_classified"] is False
    assert "zero by" in payload["obstruction_descent"]["moment_map_cross_terms"]


if __name__ == "__main__":
    verify_certificate()
