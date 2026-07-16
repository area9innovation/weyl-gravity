"""Independent verifier for the compact harmonic-domain/Taub certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/compact_harmonic_domain_taub_descent.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate(path: Path = CERTIFICATE) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["result_id"] == "COMPACT_HARMONIC_DOMAIN_AND_TAUB_DESCENT"
    assert payload["generality_level"] == "G1_DOMAIN_AND_DESCENT_FREEZE"
    assert _sha256(ROOT / payload["schema_path"]) == payload["schema_sha256"]
    for relative, digest in payload["provenance"]["inputs"].items():
        assert _sha256(ROOT / relative) == digest

    epsilon, lift = sp.symbols("epsilon p", real=True)
    fixture = payload["topology_and_charge_fibres"]["exact_flux_check"]["fixture"]
    chern = sp.sympify(fixture["chern_family"], locals={"epsilon": epsilon, "p": lift})
    flux = sp.sympify(fixture["flux_family"], locals={"epsilon": epsilon, "p": lift, "pi": sp.pi})
    assert sp.expand(chern - (2 + 2 * epsilon**2 * lift)) == 0
    assert sp.expand(flux - 4 * sp.pi * (1 + epsilon**2 * lift)) == 0
    assert fixture["fixed_bundle_consequence"] == "p=0"

    fibres = payload["topology_and_charge_fibres"]
    assert fibres["fixed_compact_u1_bundle"]["allowed_magnetic_lift"] is False
    assert fibres["enlarged_continuous_flux_theory"]["allowed_magnetic_lift"] is True
    assert fibres["enlarged_continuous_flux_theory"]["not_the_same_phase_space"] is True
    assert fibres["electric_only_variation_on_fixed_bundle"]["allowed"] is True

    rules = payload["harmonic_conventions_and_selection"]
    assert rules["constant_lapse_spatial_rules"][:3] == [
        "n_1+n_2=0",
        "ell_1=ell_2",
        "m_1+m_2=0",
    ]
    assert payload["slice_conservation"]["exact_symbolic_contraction"] == "0"
    assert payload["noether_gauge_descent"]["status"] == "FORMAL_ACTION_NOETHER_DESCENT_CERTIFIED"
    assert payload["classification"]["cauchy_slice_independence"] is True
    assert payload["classification"]["complete_adjoint_cokernel_computed"] is False
    assert payload["classification"]["lorentzian_causal_theorem"] is False


if __name__ == "__main__":
    verify_certificate()
