"""Independent low-cost verifier for the periodic l=2 graviton certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_periodic_graviton_second_order.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate(path: Path = CERTIFICATE) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["result_id"] == "EINSTEIN_MAXWELL_PERIODIC_GRAVITON_SECOND_ORDER"
    assert payload["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    assert _sha256(ROOT / payload["schema_path"]) == payload["schema_sha256"]
    assert _sha256(ROOT / payload["provenance"]["tensor_helper_path"]) == payload["provenance"]["tensor_helper_sha256"]
    for relative, digest in payload["provenance"]["inputs"].items():
        assert _sha256(ROOT / relative) == digest

    root = sp.sqrt(3)
    coupling = sp.Matrix(payload["first_order_mode"]["frequency_squared_matrix"])
    assert (coupling * sp.Matrix([1, root]) - (6 + 2 * root) * sp.Matrix([1, root])).applyfunc(sp.simplify) == sp.zeros(2, 1)
    assert (coupling * sp.Matrix([1, -root]) - (6 - 2 * root) * sp.Matrix([1, -root])).applyfunc(sp.simplify) == sp.zeros(2, 1)
    assert payload["first_order_mode"]["electric_charge_variation"].endswith("=0")
    assert payload["first_order_mode"]["magnetic_charge_variation"].endswith("=0")

    theta = sp.symbols("theta", real=True)
    source = sp.sympify(
        payload["quadratic_weyl_maxwell_source_time_zero"]["tt_projection"],
        locals={"theta": theta},
    )
    source_average = sp.integrate(source * sp.sin(theta), (theta, 0, sp.pi)) / 2
    assert sp.simplify(source_average + sp.Rational(12, 5) * (6 + 5 * root)) == 0
    chevreton_tt = -sp.Rational(9, 2) * (
        (33 + 18 * root) * sp.sin(theta) ** 4
        - (48 + 24 * root) * sp.sin(theta) ** 2
        + 16 + 8 * root
    )
    chevreton_average = sp.integrate(chevreton_tt * sp.sin(theta), (theta, 0, sp.pi)) / 2
    assert sp.simplify(chevreton_average + sp.Rational(36, 5) * (1 + root)) == 0
    assert payload["classification"]["adjoint_cokernel_obstruction_certified"] is True
    assert payload["classification"]["both_normal_branches_classified_at_second_order"] is False
    assert payload["classification"]["all_helicity_two_harmonics_obstructed"] is False


if __name__ == "__main__":
    verify_certificate()
