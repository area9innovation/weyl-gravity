"""Independent consumer for the relative residual-action descent."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_RESIDUAL_ACTION_DESCENT_V1.json"
OVERLAY = ROOT / "residual_atlas/einstein-weyl-relative-residual-action-overlay-v1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-relative-residual-action-descent-v1.schema.json"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check_reference(reference: dict[str, str]) -> dict[str, Any]:
    path = ROOT / reference["path"]
    assert path.is_file()
    assert _sha256(path) == reference["sha256"]
    payload = _load(path)
    assert reference["result_id"] in {payload.get("result_id"), payload.get("schema")}
    return payload


def _symplectic_defect(action: list[list[str]], form: list[list[str]]) -> sp.Matrix:
    matrix = sp.Matrix(action)
    omega = sp.Matrix(form)
    return sp.simplify(matrix.T * omega * matrix - omega)


def verify_certificate() -> None:
    cert = _load(CERTIFICATE)
    overlay = _load(OVERLAY)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(cert)

    for reference in cert["provenance"]["inputs"].values():
        _check_reference(reference)
    assert _sha256(ROOT / cert["provenance"]["producer_path"]) == cert["provenance"]["producer_sha256"]
    assert _sha256(ROOT / cert["provenance"]["schema_path"]) == cert["provenance"]["schema_sha256"]

    triangle = _check_reference(cert["provenance"]["inputs"]["triangle"])
    components = _check_reference(cert["provenance"]["inputs"]["components"])
    dictionary = _check_reference(cert["provenance"]["inputs"]["dictionary"])
    manifest = _check_reference(cert["provenance"]["inputs"]["manifest"])
    assert triangle["acceptance_flags"]["H_PRODUCT_EQUIVARIANT"] is True
    assert components["global_endpoints"]["map_matrix"] == sp.eye(6).tolist()
    assert components["global_endpoints"]["dual_map_matrix"] == sp.eye(6).tolist()
    assert components["global_endpoints"]["cone_cohomology_dimension"] == 0
    assert components["global_endpoints"]["large_u1_map"] == "identity Z -> Z"
    assert triangle["pairing_disposition"] == {
        "standard_pairing_cyclic_map_exists": False,
        "three_forms_kept_distinct": True,
        "triangle_kind": "NONCYCLIC_THREE_FORM",
    }

    dictionary_ids = {row["id"] for row in dictionary["branch_rows"]}
    manifest_ids = {row["id"] for row in manifest["branches"]}
    rows = cert["branches"]
    assert len(rows) == 7
    assert len({row["branch_id"] for row in rows}) == 7
    assert {row["branch_id"] for row in rows if row["branch_id"] != "ph.global.electric_wilson.relative"} <= dictionary_ids
    for row in rows:
        assert set(row["manifest_branch_ids"]) <= manifest_ids
        assert row["global_orbit_quotient"]["status"] == "NO_CERTIFIED_MAP"
        assert row["support_local_physical_projection"]["status"] == "NO_CERTIFIED_MAP"
        assert row["causal_green_descent"]["status"] == "NO_CERTIFIED_MAP"
        assert row["relative_mapping_cone_cohomology"]["endpoint_degree"]["module"] == "0"

    by_id = {row["branch_id"]: row for row in rows}
    for branch_id in ("ph.generic.axial.relative", "ph.generic.polar.relative"):
        row = by_id[branch_id]
        assert row["relative_mapping_cone_cohomology"]["solution_degree"]["module"] == "(K_(ell,n)[omega]/(p))^2 tensor V_ell"
        assert row["pairing_blocks"]["relative_cofiber"]["radical_dimension"] == 0
        assert row["pairing_blocks"]["relative_cofiber"]["inertia"] == [2, 0]
        assert row["pairing_blocks"]["mixed_einstein_extra"]["matrix"] == "0"
    for branch_id in (
        "ph.global.homogeneous.relative",
        "ph.global.twist.relative",
        "ph.global.electric_wilson.relative",
    ):
        assert by_id[branch_id]["relative_mapping_cone_cohomology"]["solution_degree"]["module"] == "0"
        assert by_id[branch_id]["pairing_blocks"]["relative_cofiber"]["status"] == "NOT_APPLICABLE"

    tau = sp.symbols("tau", real=True)
    homogeneous_action = [
        ["1", "tau", "0", "0", "0", "0"],
        ["0", "1", "0", "0", "0", "0"],
        ["tau**2", "tau**3/3", "1", "tau", "0", "0"],
        ["2*tau", "tau**2", "0", "1", "0", "0"],
        ["0", "0", "0", "0", "1", "0"],
        ["0", "0", "0", "0", "tau", "1"],
    ]
    homogeneous_form = _check_reference(cert["provenance"]["inputs"]["homogeneous_form"])["theorem"][
        "cauchy_forms_after_common_factor_2piL"
    ]
    assert _symplectic_defect(homogeneous_action, homogeneous_form["einstein_maxwell"]) == sp.zeros(6)
    assert _symplectic_defect(homogeneous_action, homogeneous_form["weyl_maxwell"]) == sp.zeros(6)
    twist_action = [["1", "tau"], ["0", "1"]]
    twist_form = _check_reference(cert["provenance"]["inputs"]["twist_form"])["theorem"][
        "cauchy_forms_after_common_factor_L_N_1m"
    ]
    assert _symplectic_defect(twist_action, twist_form["einstein_maxwell"]) == sp.zeros(2)
    assert _symplectic_defect(twist_action, twist_form["weyl_maxwell"]) == sp.zeros(2)

    assert overlay["generated_claims_ledger"] is True
    assert _check_reference(overlay["base_manifest"]) == manifest
    cert_hash = _sha256(CERTIFICATE)
    assert len(overlay["rows"]) == sum(len(row["manifest_branch_ids"]) for row in rows)
    for row in overlay["rows"]:
        assert row["manifest_branch_id"] in manifest_ids
        assert row["relative_branch_id"] in {value["branch_id"] for value in rows}
        assert row["cells"]["residual_action"]["source"]["sha256"] == cert_hash
        assert row["cells"]["global_orbit_quotient"]["status"] == "NO_CERTIFIED_MAP"

    classification = cert["classification"]
    assert classification["chain_equivariance"] == "CERTIFIED"
    assert classification["endpoint_relative_cohomology"] == "CERTIFIED_ZERO"
    assert classification["three_action_derived_forms_distinct"] is True
    assert classification["standard_pairing_cyclic_map_exists"] is False
    assert classification["global_orbit_or_symplectic_quotient"] == "NO_CERTIFIED_MAP"
    assert classification["particle_observer_nonlinear_quantum_claim"] is False
    boundary = cert["claim_boundary"].lower()
    for excluded in ("orbit", "causal", "particle", "observable", "nonlinear", "quantum"):
        assert excluded in boundary


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_WEYL_RELATIVE_RESIDUAL_ACTION_DESCENT_V1 independent verification: PASS")
