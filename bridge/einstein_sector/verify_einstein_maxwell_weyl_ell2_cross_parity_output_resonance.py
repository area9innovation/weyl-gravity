"""Independent verifier for axial-polar ell=2 cross-output solvability."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_cross_parity_output_resonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_cross_parity_output_resonance.schema.json"


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
    assert [blocks[str(ell)]["target_parity"] for ell in range(5)] == ["absent_axial_L0", "polar", "axial", "polar", "axial"]
    assert payload["zero_frequency_blocks"]["physical_adjoint_cokernel"] == "none"
    assert payload["generic_isospectral_transfer"]["p"] == "-(3*k**2 + 3*lambda - 3*omega**2 - 2)/3"
    assert len(payload["nonzero_frequency_ledger"]) == 9
    for channel in payload["nonzero_frequency_ledger"].values():
        assert channel["all_present_blocks_invertible"] is True
        assert all(witness["certified_nonzero"] for witness in channel["polar_L1"].values())
        assert all(witness["certified_nonzero"] for witness in channel["polar_L3"].values())
        for block in ("axial_L2", "axial_L4"):
            assert channel[block]["p"]["certified_nonzero"]
            assert channel[block]["q"]["certified_nonzero"]


if __name__ == "__main__":
    verify_certificate()
