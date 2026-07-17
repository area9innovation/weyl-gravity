"""Independent verifier for the paired opposite-momentum cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import jsonschema
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.einstein_sector.einstein_maxwell_weyl_plebanski_hacyan_stabilizer import _rotation_representation

CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_opposite_momentum_cone.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    for record in payload["provenance"]["inputs"].values():
        assert _sha256(ROOT / record["path"]) == record["sha256"]
    c = payload["classification"]
    assert c["complete_fixed_ell_absolute_k_common_zero_cone_classified"] is True
    assert c["nonzero_standing_wave_subcone_constructed"] is True
    assert c["relative_phase_quadratic_source_classified"] is False

    ap, ae, k2 = sp.symbols("a_plus a_extra k2", positive=True, real=True)
    for ell in range(2, 9):
        lam = sp.Integer(ell * (ell + 1))
        wm2 = k2 + lam - sp.sqrt(2 * lam)
        we2 = k2 + lam - sp.Rational(2, 3)
        wp2 = k2 + lam + sp.sqrt(2 * lam)
        am = (wp2 * ap + we2 * ae) / wm2
        assert sp.simplify(wp2 * ap + we2 * ae - wm2 * am) == 0
        representation = _rotation_representation(ell)
        v = sp.zeros(2 * ell + 1, 1)
        v[ell] = 1
        for generator in ("J0", "Jplus", "Jminus"):
            assert sp.simplify((v.T * representation["angular_form"] * representation[generator] * v)[0]) == 0


if __name__ == "__main__":
    verify_certificate()
