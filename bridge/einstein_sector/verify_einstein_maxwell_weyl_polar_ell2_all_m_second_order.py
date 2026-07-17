"""Independent verifier for the all-m polar ell=2 cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell2_all_m_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_polar_ell2_all_m_second_order.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    for record in payload["provenance"]["inputs"].values():
        assert _sha256(ROOT / record["path"]) == record["sha256"]
    blocks = payload["angular_selection"]["output_blocks"]
    assert [blocks[str(L)]["target_parity"] for L in range(5)] == ["polar", "axial", "polar", "axial", "polar"]
    scalar = payload["zero_frequency_descent"]["polar_L0"]
    assert scalar["spacetime_row_rank"] == 1
    assert scalar["extra_e1_e2_interference"] == ["0", "0", "0", "0"]
    ledger = payload["nonzero_frequency_resonance_ledger"]
    assert len(ledger["nine_nonzero_frequency_types"]) == 9
    classification = payload["classification"]
    assert classification["all_m_polar_ell2_common_zero_cone_second_order_extendible"] is True
    assert classification["axial_polar_mixed_cross_terms_classified"] is False


if __name__ == "__main__":
    verify_certificate()
