"""Independent verifier for the maximal parity-complete exact sequence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_WEYL_PARITY_COMPLETE_RESIDUAL_EXACT_SEQUENCE_MAXIMAL_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-parity-complete-residual-exact-sequence-maximal-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_payload(payload: dict[str, Any], *, verify_files: bool = True) -> None:
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).validate(payload)
    if verify_files:
        assert payload["schema_sha256"] == _sha256(SCHEMA)
        assert payload["provenance"]["generator_sha256"] == _sha256(ROOT / payload["provenance"]["generator_path"])
        for item in payload["provenance"]["inputs"].values():
            path = ROOT / item["path"]
            imported = json.loads(path.read_text())
            assert item["sha256"] == _sha256(path)
            assert item["result_id"] == imported["result_id"]
    ids = []
    for row in payload["authoritative_table"]:
        ids.append(row["id"])
        assert row["Einstein_dimension"] + row["extra_dimension"] == row["Weyl_dimension"]
        assert row["Einstein_pairing_rank"] + row["extra_pairing_rank"] == row["Weyl_pairing_rank"]
        assert row["radical_dimensions"] == [0, 0, 0]
    assert ids == ["generic.axial", "generic.polar", "exceptional.ell1.axial", "exceptional.ell1.polar", "polar.ell0.nonzero_fourier", "homogeneous.ell0.k0", "twist.ell1.k0"]
    assert payload["maximal_preresidual_statement"]["kernel_equals_image"] is True
    assert payload["maximal_preresidual_statement"]["cokernel_equals_declared_extra"] is True
    assert payload["maximal_preresidual_statement"]["splitting_claim"] is False
    assert payload["maximal_preresidual_statement"]["cyclic_claim"] is False
    assert payload["first_absent_maps"]["strict_complex_short_exact_inclusion"].startswith("OBSTRUCTED")
    assert payload["first_absent_maps"]["after_residual_quotient_functor"].startswith("NO_CERTIFIED_MAP")
    assert payload["current_compatibility"]["triangle_kind"] == "NONCYCLIC_THREE_FORM"
    assert payload["endpoint_disposition"]["large_U1"].endswith("no tangent deletion")
    assert payload["classification"]["degreewise_short_exact_complex_certified"] is False
    assert payload["classification"]["after_residual_exact_sequence_certified"] is False


def verify_certificate() -> None:
    verify_payload(json.loads(CERTIFICATE.read_text()))


if __name__ == "__main__":
    verify_certificate()
