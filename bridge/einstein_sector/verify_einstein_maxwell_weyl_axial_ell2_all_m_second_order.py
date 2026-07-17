"""Independent verifier for the all-m axial ell=2 cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_all_m_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_ell2_all_m_second_order.schema.json"


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
    ledger = payload["nonzero_frequency_resonance_ledger"]
    assert len(ledger["nine_nonzero_frequency_types"]) == 9
    for channel in ledger["nine_nonzero_frequency_types"].values():
        assert all(witness["certified_nonzero"] for witness in channel["axial_L1"].values())
        assert channel["axial_L3"]["p"]["certified_nonzero"]
        assert channel["axial_L3"]["q"]["certified_nonzero"]
    c = payload["classification"]
    assert c["all_m_axial_ell2_common_zero_cone_second_order_extendible"] is True
    assert c["polar_input_parity_classified"] is False


if __name__ == "__main__":
    verify_certificate()
