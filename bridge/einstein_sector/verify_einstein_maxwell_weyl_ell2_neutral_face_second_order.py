"""Independent lightweight verifier for the ell=2 neutral-face theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_neutral_face_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_neutral_face_second_order.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    for record in payload["provenance"]["inputs"].values():
        assert _sha256(ROOT / record["path"]) == record["sha256"]
    balance = payload["raw_amplitude_balance"]
    vectors = {name: sp.Matrix([sp.sympify(v, locals={"sqrt": sp.sqrt}) for v in row]) for name, row in balance["zero_source_vectors_E00_E11_E22_Maxwell1"].items()}
    tau = {name: sp.sympify(v, locals={"sqrt": sp.sqrt}) for name, v in balance["Taub_coefficients"].items()}
    for name, vector in vectors.items():
        assert sp.simplify(vector - tau[name] * sp.Matrix([1, 0, sp.Rational(1, 2), 0])) == sp.zeros(4, 1)
    assert len(payload["nonzero_frequency_channel_ledger"]) == 9
    for channel in payload["nonzero_frequency_channel_ledger"].values():
        assert channel["homogeneous_remainder"] == ["0", "0", "0", "0"]
        for output in channel["generic_polar_outputs"].values():
            assert output["p_shell_witness"]["certified_nonzero"] is True
            assert output["q_shell_witness"]["certified_nonzero"] is True
    assert payload["classification"]["two_parameter_positive_quadrant_face_second_order_extendible"] is True
    assert payload["classification"]["complete_k0_density_cone_second_order_classified"] is False


if __name__ == "__main__":
    verify_certificate()
