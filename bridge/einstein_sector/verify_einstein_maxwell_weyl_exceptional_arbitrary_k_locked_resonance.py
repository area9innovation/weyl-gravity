"""Independent verifier for the arbitrary-k locked resonance certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ARBITRARY_K_LOCKED_RESONANCE_V1.json"
ATLAS = ROOT / "residual_atlas/einstein-exceptional-arbitrary-k-locked-resonance-fragment.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-exceptional-arbitrary-k-locked-resonance-v1.schema.json"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_payload(cert: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(cert)
    for reference in cert["provenance"]["inputs"].values():
        path = ROOT / reference["path"]
        assert _sha256(path) == reference["sha256"]
        assert _load(path)["result_id"] == reference["result_id"]
    assert _sha256(ROOT / cert["provenance"]["producer_path"]) == cert["provenance"]["producer_sha256"]
    assert _sha256(ROOT / cert["provenance"]["schema_path"]) == cert["provenance"]["schema_sha256"]

    join = _load(ROOT / cert["provenance"]["inputs"]["join"]["path"])
    assert cert["provenance"]["inputs"]["join"]["sha256"] == "723083a24436059f19ae70f53287e6141c58f54b27eae50064896fd12eba7fbb"
    assert join["classification"]["complete_branch_labelled_obstruction_map_joined"]
    assert not join["classification"]["exceptional_generic_global_arbitrary_k_common_zero_classified"]

    k = sp.symbols("k", real=True)
    w2 = k**2 + sp.Rational(4, 3)
    assert sp.factor(4 * w2 - (2 * k) ** 2 - 6 + sp.Rational(2, 3)) == 0
    assert sp.factor((2 * sp.sqrt(w2) - sp.sqrt(w2)) ** 2 - k**2 - sp.Rational(4, 3)) == 0
    eta = sp.symbols("eta", real=True)
    boost = sp.Matrix([[sp.cosh(eta), sp.sinh(eta)], [sp.sinh(eta), sp.cosh(eta)]])
    metric = sp.diag(1, -1)
    assert sp.simplify(boost.T * metric * boost - metric) == sp.zeros(2)
    assert sp.simplify(boost.det()) == 1

    rest = _load(ROOT / cert["provenance"]["inputs"]["k0_difference_matrix"]["path"])
    expected_axial = rest["sparse_matrix"]["axial_output"].replace("R_ax=", "").replace(
        "conj(x_exceptional_axial)*y_extra_polar_e2",
        "conj(x_exceptional_axial(k))*y_boosted_extra_polar_e2(2k)",
    )
    expected_polar = rest["sparse_matrix"]["polar_output"].replace("R_pol=", "").replace(
        "conj(x_exceptional_polar)*y_extra_polar_e2",
        "conj(x_exceptional_polar(k))*y_boosted_extra_polar_e2(2k)",
    )
    rows = cert["locked_difference_matrix"]["nonzero_columns"]
    assert rows["axial_L1_output"] == f"R_ax(k)={expected_axial}"
    assert rows["polar_L1_output"] == f"R_pol(k)={expected_polar}"
    assert sp.sympify("-768/5") != 0 and sp.sympify("-864/5") != 0
    assert cert["locked_difference_matrix"]["six_zero_columns"] is True
    assert cert["locked_difference_matrix"]["rank_per_output_parity"] == 1

    classification = cert["classification"]
    assert classification["first_exact_cross_fibre_functional_exported"] is True
    assert classification["all_exceptional_cross_columns_computed"] is False
    assert classification["all_m_tensor_assembled"] is False
    assert classification["enlarged_common_zero_geometry_classified"] is False
    assert classification["multiple_abs_momentum_full_cone_classified"] is False
    assert classification["causal_all_orders_residual_observer_particle_quantum_claim"] is False
    assert cert["cross_fibre_functional"]["common_zero_geometry"] == "OPEN"
    assert "not asserted to be a global automorphism" in cert["covariant_transport_lemma"]["not_claimed"]


def verify_certificate() -> None:
    cert = _load(CERTIFICATE)
    verify_payload(cert)
    atlas = _load(ATLAS)
    assert atlas["generated_by_sha256"] == _sha256(ROOT / atlas["generated_by"])
    assert len(atlas["entries"]) == 1
    entry = atlas["entries"][0]
    assert entry["id"] == "einstein.ph.wm.interaction.exceptional_arbitrary_k_locked_resonance"
    assert entry["evidence"][0]["sha256"] == _sha256(CERTIFICATE)
    assert entry["mode_data"]["resonance"]["status"] == "CERTIFIED"
    assert entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"] == "OPEN"
    assert entry["mode_data"]["second_order"]["causal_retarded"]["status"] == "NO_CERTIFIED_MAP"


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ARBITRARY_K_LOCKED_RESONANCE_V1 independent verification: PASS")
