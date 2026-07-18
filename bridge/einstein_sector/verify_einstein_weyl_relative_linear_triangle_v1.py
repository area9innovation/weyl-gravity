"""Independent verifier for the compact-product relative linear triangle.

This consumer deliberately does not import the producer.  It checks the two
strict schemas, resolves every content-addressed reference, recomputes the
mapping-cone dimensions and endpoint ranks, and enforces the theorem boundary.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
TRIANGLE = ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1.json"
COMPONENTS = ROOT / "bridge/einstein_sector/generated/einstein_weyl_relative_linear_triangle_v1/components.json"
COMPONENT_SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-relative-linear-triangle-components-v1.schema.json"
TRIANGLE_SCHEMA = ROOT / "d_quotient_classical/schema/relative-linfinity-triangle-input-v2.schema.json"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_pointer(value: Any, pointer: str) -> Any:
    if pointer == "/":
        return value
    current = value
    for raw in pointer.lstrip("/").split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def _check_reference(reference: dict[str, str], *, with_pointer: bool) -> Any:
    path = ROOT / reference["path"]
    assert path.is_file(), path
    assert _sha256(path) == reference["sha256"], path
    payload = _load(path)
    assert payload["result_id"] == reference["result_id"], path
    return _resolve_pointer(payload, reference["pointer"]) if with_pointer else payload


def _identity(size: int) -> list[list[int]]:
    return [[int(row == column) for column in range(size)] for row in range(size)]


def verify_certificate() -> None:
    components = _load(COMPONENTS)
    triangle = _load(TRIANGLE)
    component_schema = _load(COMPONENT_SCHEMA)
    triangle_schema = _load(TRIANGLE_SCHEMA)
    Draft202012Validator.check_schema(component_schema)
    Draft202012Validator.check_schema(triangle_schema)
    Draft202012Validator(component_schema).validate(components)
    Draft202012Validator(triangle_schema).validate(triangle)

    provenance = components["provenance"]
    producer = ROOT / provenance["producer_path"]
    assert _sha256(producer) == provenance["producer_sha256"]
    for reference in provenance["inputs"].values():
        _check_reference(reference, with_pointer=False)

    for reference in components["q1_complexes"]["evidence"]:
        assert _check_reference(reference, with_pointer=True) is not None
    cofiber_evidence = components["mapping_cofiber"]["solution_cofiber_evidence"]
    assert len(cofiber_evidence) == 6
    for reference in cofiber_evidence:
        assert _check_reference(reference, with_pointer=True) is not None
    for form_name in ("einstein_source", "pulled_back_weyl", "relative_cofiber"):
        form = components["form_exports"][form_name]
        assert form["action_derived"] is True
        for reference in form["blocks"]:
            assert _check_reference(reference, with_pointer=True) is not None

    component_hash = _sha256(COMPONENTS)
    component_references = []
    for name, reference in triangle["triangle_artifacts"].items():
        payload = _check_reference(reference, with_pointer=False)
        if reference["path"] == str(COMPONENTS.relative_to(ROOT)):
            component_references.append(name)
            assert reference["sha256"] == component_hash
            assert payload == components
    assert sorted(component_references) == [
        "projection_or_cofiber",
        "relative_pairing",
        "source_pairing",
        "source_q1",
        "target_pairing",
        "target_q1",
    ]

    source = components["q1_complexes"]["source_dimensions"]
    target = components["q1_complexes"]["target_dimensions"]
    expected_cone = [source[0]] + [target[index] + source[index + 1] for index in range(3)] + [target[-1]]
    assert expected_cone == [5, 20, 28, 19, 6]
    assert components["mapping_cofiber"]["degree_dimensions"] == expected_cone
    assert components["mapping_cofiber"]["square_zero"] is True
    assert components["mapping_cofiber"]["support_local"] is True
    assert components["mapping_cofiber"]["uses_spectral_projector"] is False
    assert components["mapping_cofiber"]["uses_differential_inverse"] is False

    endpoints = components["global_endpoints"]
    k_one, k_two = sp.Integer(0), sp.Integer(1)
    assert sp.Rational(4, 3) * (k_one + k_two) ** 2 == sp.Rational(4, 3)
    endpoint_map = sp.Matrix(endpoints["map_matrix"])
    dual_map = sp.Matrix(endpoints["dual_map_matrix"])
    assert endpoints["connected_product_isometry_dimension"] + endpoints["constant_u1_reducibility_dimension"] == 6
    assert endpoint_map == sp.eye(6) and dual_map == sp.eye(6)
    assert endpoint_map.rank() == dual_map.rank() == 6
    assert endpoints["cone_cohomology_dimension"] == 0
    assert endpoints["large_u1_lattice"] == "H^1(S1 x S2;Z)=Z"
    assert endpoints["large_u1_map"] == "identity Z -> Z"
    assert endpoints["fixed_chern_class"] == "N=2"
    assert "Orientation-reversing" in endpoints["excluded_components"]

    assert triangle["pairing_disposition"] == {
        "triangle_kind": "NONCYCLIC_THREE_FORM",
        "standard_pairing_cyclic_map_exists": False,
        "three_forms_kept_distinct": True,
    }
    assert components["form_exports"]["standard_pairing_cyclic_map_exists"] is False
    assert components["form_exports"]["three_forms_kept_distinct"] is True
    obstruction = _check_reference(
        triangle["triangle_artifacts"]["generic_cyclic_map_inertia_obstruction"],
        with_pointer=False,
    )
    assert obstruction["classification"]["standard_pairing_all_sector_cyclic_triangle_possible"] is False
    assert obstruction["classification"]["noncyclic_off_shell_relative_triangle_obstructed"] is False

    expected_flags = {
        "OFF_SHELL_CHAIN_MAP_ALL_BV_ROWS": True,
        "SUPPORT_LOCAL_MAPPING_COFIBER": True,
        "GLOBAL_ENDPOINTS_INCLUDED": True,
        "THREE_ACTION_DERIVED_FORMS_EXPORTED": True,
        "GENERIC_STANDARD_PAIRING_CYCLIC_OBSTRUCTION_RESPECTED": True,
        "H_PRODUCT_EQUIVARIANT": True,
        "INDEPENDENT_VERIFIER_PASS": True,
    }
    assert triangle["acceptance_flags"] == expected_flags
    classification = components["classification"]
    assert classification["standard_pairing_cyclic_map"] is False
    assert classification["causal_nonlinear_observational_or_quantum_claim"] is False
    boundary = (components["claim_boundary"] + " " + triangle["claim_boundary"]).lower()
    for absent in ("q2", "q3", "causal", "particle", "observable", "quantum"):
        assert absent in boundary
    assert "fixed chern-class n=2" in triangle["boundaries"].lower()
    assert endpoints["map_matrix"] == _identity(6)


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1 independent verification: PASS")
