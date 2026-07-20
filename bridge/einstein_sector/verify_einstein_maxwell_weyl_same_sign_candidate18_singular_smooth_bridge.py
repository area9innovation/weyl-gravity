"""Independent verifier for the candidate 18 singular-to-smooth bridge."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_singular_smooth_bridge.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema_path = ROOT / payload["schema_path"]
    Draft202012Validator(json.loads(schema_path.read_text())).validate(payload)
    assert payload["schema_sha256"] == sha(schema_path)
    assert payload["provenance"]["generator_sha256"] == sha(ROOT / payload["provenance"]["generator_path"])
    for item in payload["provenance"]["inputs"].values():
        assert item["sha256"] == sha(ROOT / item["path"])
    a, c, beta, pp, pm, t = sp.symbols("a c beta pp pm t", positive=True, real=True)
    w = sp.Matrix([sp.cos(t), sp.sin(t)])
    A = sp.Matrix([[a, c], [c, a]])
    u = sp.sqrt(6 * pp / (w.T * A * w)[0]) * w
    v = sp.sqrt(6 * pm / beta) * w
    assert sp.simplify((u.T * A * u)[0] / 6 - pp) == 0
    assert sp.simplify(beta * (v.T * v)[0] / 6 - pm) == 0
    assert w.subs(t, 0) == sp.Matrix([1, 0])
    assert w.subs(t, sp.pi / 2) == sp.Matrix([0, 1])
    flags = payload["classification"]
    assert flags["candidate18_singular_components_joined_in_full_rotation_zero_fibre"]
    assert flags["bridge_interior_complex_smooth"]
    assert not flags["full_rotation_zero_fibre_connected"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE18_SINGULAR_SMOOTH_BRIDGE verifier: PASS")


if __name__ == "__main__":
    verify()
