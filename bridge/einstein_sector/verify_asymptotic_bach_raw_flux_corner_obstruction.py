"""Independent leading-order verifier for the null-infinity raw-flux obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/asymptotic_bach_raw_flux_corner_obstruction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/asymptotic_bach_raw_flux_corner_obstruction.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    for record in payload["provenance"]["inputs"].values():
        assert _sha256(ROOT / record["path"]) == record["sha256"]

    # Independent asymptotic derivation.  For p=0,
    # chi=-2 r^-1 f'+O(r^-2); for p=1, chi=O(r^-3).
    f, fu, fuu, g, gu, guu, r = sp.symbols("f fu fuu g gu guu r")
    p0_p0 = sp.expand(2 * r * (f * guu - g * fuu))
    p0_p1 = sp.expand(2 * (fu * gu - g * fuu))
    corner = 2 * (f * gu - g * fu)
    corner_derivative = sp.diff(corner, f) * fu + sp.diff(corner, fu) * fuu + sp.diff(corner, g) * gu + sp.diff(corner, gu) * guu
    assert sp.expand(corner_derivative - p0_p0 / r) == 0

    algebra = payload["raw_flux_algebra"]
    producer_00 = sp.sympify(
        algebra["p0_p0"]["coefficient"]
        .replace("f_0(u)", "f")
        .replace("g_0(u)", "g")
        .replace("Derivative(f, (u, 2))", "fuu")
        .replace("Derivative(g, (u, 2))", "guu"),
        locals={"f": f, "g": g, "fuu": fuu, "guu": guu},
    )
    assert sp.expand(producer_00 - p0_p0 / r) == 0
    assert algebra["p1_p1"]["powers_r1_r0_rminus1"] == ["0", "0", "0"]
    assert algebra["p0_p1"]["verdict"] == "FINITE_CROSS_TERM_NOT_A_P1_P1_RADIATIVE_FORM"

    flags = payload["classification"]
    assert flags["p0_generic_cut_flux_divergence_certified"] is True
    assert flags["fixed_boundary_p1_raw_flux_radical"] is True
    assert flags["nondegenerate_finite_raw_phase_space_constructed"] is False
    assert flags["full_tensor_BV_BFV_phase_space_constructed"] is False
    assert flags["causal_particle_stability_or_quantum_claim"] is False
    charges = payload["generator_charge_disposition"]
    assert charges["P0"]["final_status"] == "OPEN"
    assert charges["D_M"]["final_status"] == "OPEN"
    assert charges["H_ESU"]["final_status"] == "OBSTRUCTED"
    assert charges["D_rad"]["final_status"] == "NO_CERTIFIED_MAP"


if __name__ == "__main__":
    verify()
