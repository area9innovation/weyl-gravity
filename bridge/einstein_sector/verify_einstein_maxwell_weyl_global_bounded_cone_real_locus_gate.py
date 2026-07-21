"""Independent checks for the candidate-18 real-locus gate."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_GLOBAL_BOUNDED_CONE_REAL_LOCUS_GATE_V1.json"
ATLAS = ROOT / "residual_atlas/einstein-global-bounded-cone-real-locus-gate-fragment-v1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-global-bounded-cone-real-locus-gate-v1.schema.json"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_payload(payload: dict[str, Any]) -> None:
    Draft202012Validator(_load(SCHEMA)).validate(payload)
    for record in payload["provenance"]["inputs"].values():
        path = ROOT / record["path"]
        assert _sha256(path) == record["sha256"]
        assert _load(path)["result_id"] == record["result_id"]

    complex_input = _load(
        ROOT / payload["provenance"]["inputs"]["candidate18_complex"]["path"]
    )
    fibre_product = _load(
        ROOT / payload["provenance"]["inputs"]["fibre_product"]["path"]
    )
    rows = [row for row in fibre_product["candidate_rows"] if row["candidate_index"] == 18]
    assert len(rows) == 1
    row = rows[0]
    assert row["resonance_geometry"]["ambient_dimension_over_C"] == 30
    assert row["resonance_geometry"]["component_dimensions_over_C"] == [22]
    assert row["resonance_geometry"]["irreducible_components_over_C"] == 1

    assert len(list(itertools.combinations(range(5), 2))) == 10
    assert complex_input["one_factor"]["complex_dimension"] == 6
    assert complex_input["one_factor"]["equation_count"] == 10
    assert complex_input["complete_carrier"]["complex_dimension"] == 22
    assert 10 + 2 * 6 == 22
    assert 2 * (10 + 2 * 10) == 60

    gate = payload["selected_invariant_gate"]
    assert gate["ambient_real_dimension"] == 60
    assert gate["real_minor_equations_total"] == 40
    assert len(gate["rank_one_minor_labels_plus"]) == 10
    assert len(gate["rank_one_minor_labels_minus"]) == 10
    assert gate["rotation_equations"] == ["mu_J1=0", "mu_J2=0", "mu_J3=0"]
    assert gate["residual_group_at_this_gate"] == "U(1)_plus x U(1)_minus x lifted SO(3)"

    separation = _load(
        ROOT / payload["provenance"]["inputs"]["candidate18_separation"]["path"]
    )
    bridge = _load(
        ROOT / payload["provenance"]["inputs"]["candidate18_bridge"]["path"]
    )
    assert separation["classification"]["candidate18_singular_rotation_zero_quotient_at_least_two_components"]
    assert bridge["classification"]["candidate18_singular_components_joined_in_full_rotation_zero_fibre"]
    assert not bridge["classification"]["all_singular_points_connected_to_bridge"]
    assert not bridge["classification"]["full_rotation_zero_fibre_connected"]

    census = payload["closed_block_census"]
    candidate16 = _load(
        ROOT / payload["provenance"]["inputs"]["candidate16_gluing"]["path"]
    )
    candidate17_20 = _load(
        ROOT / payload["provenance"]["inputs"]["candidate17_20_contraction"]["path"]
    )
    candidate19_21 = _load(
        ROOT / payload["provenance"]["inputs"]["candidate19_21_links"]["path"]
    )
    assert candidate16["classification"]["candidate16_occupation_projection_proper_surjective"]
    assert candidate17_20["classification"]["candidate17_complete_singular_rotation_zero_fibre_connected"]
    assert candidate17_20["classification"]["candidate20_complete_singular_rotation_zero_fibre_connected"]
    assert candidate19_21["classification"]["candidate19_four_active_linear_sheets_classified"]
    assert candidate19_21["classification"]["candidate21_two_active_linear_sheets_classified"]
    assert "candidate18" in census

    classification = payload["classification"]
    assert classification["complete_finite_harmonic_bounded_ledger_frozen"]
    assert classification["candidate18_complex_carrier_classified"]
    assert not classification["candidate18_complete_real_fixed_occupation_fibre_classified"]
    assert not classification["candidate18_real_orbit_quotient_classified"]
    assert not classification["complex_variety_substituted_for_real_locus"]
    assert not classification["unrestricted_global_real_common_zero_classified"]
    assert payload["remaining_real_gate"]["real_radical_of_complete_fixed_occupation_ideal"] == "OPEN"


def verify_certificate() -> None:
    payload = _load(CERTIFICATE)
    verify_payload(payload)
    atlas = _load(ATLAS)
    entry = atlas["entries"][0]
    assert entry["evidence"][0]["sha256"] == _sha256(CERTIFICATE)
    assert entry["descriptions"]["nonlinear"] == "OPEN"
    assert entry["mode_data"]["resonance"]["status"] == "CERTIFIED"
    assert entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"] == "OPEN"
    assert entry["mode_data"]["second_order"]["causal_retarded"]["status"] == "NO_CERTIFIED_MAP"


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_GLOBAL_BOUNDED_CONE_REAL_LOCUS_GATE_V1 independent verification: PASS")
