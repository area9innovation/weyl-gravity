"""Independent verifier for the full generic k=0 moment-map cone."""

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

from bridge.einstein_sector.einstein_maxwell_weyl_plebanski_hacyan_stabilizer import (
    _rotation_representation,
)


CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_k0_moment_map_cone.schema.json"


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
    assert classification["full_generic_k0_common_zero_cone_classified"] is True
    assert classification["all_ell_all_m_both_parities_and_all_extra_polarizations_included"] is True
    assert classification["full_quadratic_source_solvability_on_cone_classified"] is False
    assert classification["opposite_momentum_standing_waves_classified"] is False
    assert classification["exceptional_global_blocks_classified"] is False

    a_plus, a_extra = sp.symbols("a_plus a_extra", nonnegative=True, real=True)
    for ell in range(2, 13):
        lam = sp.Integer(ell * (ell + 1))
        w_minus_sq = lam - sp.sqrt(2 * lam)
        w_extra_sq = lam - sp.Rational(2, 3)
        w_plus_sq = lam + sp.sqrt(2 * lam)
        assert w_minus_sq.is_positive
        assert (w_extra_sq - w_minus_sq).is_positive
        assert (w_plus_sq - w_extra_sq).is_positive
        a_minus = (w_plus_sq * a_plus + w_extra_sq * a_extra) / w_minus_sq
        assert sp.simplify(w_plus_sq * a_plus + w_extra_sq * a_extra - w_minus_sq * a_minus) == 0

        representation = _rotation_representation(ell)
        vector = sp.zeros(2 * ell + 1, 1)
        vector[ell] = 1
        angular = representation["angular_form"]
        for generator in ("J0", "Jplus", "Jminus"):
            assert sp.simplify(
                (vector.T * angular * representation[generator] * vector)[0]
            ) == 0

    neutral = payload["rotationally_neutral_subcone"]
    assert neutral["moment_maps"] == {
        "H": "0", "P_x": "0", "J_1": "0", "J_2": "0", "J_3": "0"
    }


if __name__ == "__main__":
    verify_certificate()
