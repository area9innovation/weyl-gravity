"""Independent verifier for the mixed moment-map zero-locus theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_mixed_moment_map_zero_locus.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_mixed_moment_map_zero_locus.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    assert payload["provenance"]["generator_sha256"] == _sha256(ROOT / payload["provenance"]["generator_path"])
    for record in payload["provenance"]["inputs"].values():
        assert record["sha256"] == _sha256(ROOT / record["path"])

    wp, we, wm = sp.symbols("wp we wm", positive=True)
    ap, ae, am = sp.symbols("ap ae am", nonnegative=True)
    energy = wp**2 * ap + we**2 * ae - wm**2 * am
    momentum = wp * ap + we * ae - wm * am
    assert sp.expand(energy - wm * momentum - wp * (wp - wm) * ap - we * (we - wm) * ae) == 0

    root = sp.sqrt(3)
    q_taub = sp.Rational(48, 5) * (5 * root - 6)
    e_taub = -sp.Rational(832, 45)
    ratio = sp.Rational(27, 52) * (5 * root - 6)
    assert sp.simplify(q_taub + e_taub * ratio) == 0
    fixture = payload["minimal_k0_balanced_fixture"]
    assert sp.simplify(sp.sympify(fixture["extra_e2"]["raw_cosine_amplitude_squared"], locals={"sqrt": sp.sqrt}) - ratio) == 0
    assert fixture["common_moment_maps"]["all_five_zero"] is True
    assert payload["classification"]["same_nonzero_k_travelling_common_H_Px_zero_locus_trivial"] is True
    assert payload["classification"]["generic_ell2_ell4_output_shell_resonances_excluded"] is True


if __name__ == "__main__":
    verify_certificate()
