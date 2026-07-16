"""Independent low-cost verifier for the periodic photon certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_periodic_photon_second_order.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate(path: Path = CERTIFICATE) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["result_id"] == "EINSTEIN_MAXWELL_PERIODIC_PHOTON_SECOND_ORDER"
    assert payload["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    assert payload["lifecycle_state"] == "CLASSIFIED"

    for relative, digest in payload["provenance"]["inputs"].items():
        assert _sha256(ROOT / relative) == digest
    assert _sha256(ROOT / payload["schema_path"]) == payload["schema_sha256"]

    coupling = sp.Matrix(payload["first_order_mode"]["frequency_squared_matrix"])
    mode = sp.Matrix(payload["first_order_mode"]["physical_eigenvector"])
    omega_squared = payload["first_order_mode"]["physical_frequency_squared"]
    assert coupling * mode == omega_squared * mode
    assert payload["first_order_mode"]["electric_charge_variation"].endswith("=0")
    assert payload["first_order_mode"]["magnetic_charge_variation"].endswith("=0")

    time, theta = sp.symbols("t theta", real=True)
    source = sp.sympify(
        payload["quadratic_weyl_maxwell_source"]["tt_projection"],
        locals={"t": time, "theta": theta},
    )
    source_average = sp.integrate(source * sp.sin(theta), (theta, 0, sp.pi)) / 2
    assert sp.simplify(source_average + sp.Rational(16, 3)) == 0

    chevreton_tt = (
        8 * (sp.sin(theta) ** 2 - 1)
        + (8 - 12 * sp.sin(theta) ** 2) * sp.sin(2 * time) ** 2
    )
    chevreton_average = sp.integrate(
        chevreton_tt * sp.sin(theta), (theta, 0, sp.pi)
    ) / 2
    assert sp.simplify(chevreton_average + sp.Rational(8, 3)) == 0
    assert payload["adjoint_cokernel_witness"]["fixed_charge_condition"].startswith("p=0")
    assert payload["adjoint_cokernel_witness"]["normalized_source_pairing"] == "-16/3"
    assert payload["classification"]["adjoint_cokernel_obstruction_certified"] is True
    assert payload["classification"]["general_photon_harmonic_no_go_certified"] is False
    assert payload["classification"]["periodic_helicity_two_result_certified"] is False


if __name__ == "__main__":
    verify_certificate()
