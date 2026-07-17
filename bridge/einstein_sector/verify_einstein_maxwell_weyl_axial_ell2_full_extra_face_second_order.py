"""Independent verifier for the axial ell=2 full-extra face."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_full_extra_face_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_ell2_full_extra_face_second_order.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    for record in payload["provenance"]["inputs"].values():
        assert _sha256(ROOT / record["path"]) == record["sha256"]
    rank = payload["zero_frequency_source_rank"]
    tau = {name: sp.sympify(value, locals={"sqrt": sp.sqrt}) for name, value in rank["Taub_source_coefficients"].items()}
    assert tau["minus"] > 0
    assert tau["plus"] < 0 and tau["extra_e1"] < 0 and tau["extra_e2"] < 0
    assert rank["extra_interference_source"] == ["0", "0", "0", "0"]
    assert rank["spacetime_row_rank"] == 1
    assert rank["source_matrix_proportional_to_extra_Lee_Wald_Gram"] is True
    assert payload["nonzero_homogeneous_channels"]["image_equals_Noether_kernel"] is True
    classification = payload["classification"]
    assert classification["three_parameter_positive_cone_second_order_extendible"] is True
    assert classification["all_m_promoted"] is False
    assert classification["polar_input_parity_classified"] is False


if __name__ == "__main__":
    verify_certificate()
