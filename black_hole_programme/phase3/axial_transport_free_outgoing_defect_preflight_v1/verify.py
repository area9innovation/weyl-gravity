#!/usr/bin/env python3
"""Independent verifier for the transport-free outgoing-defect preflight."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

from . import produce


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(document: dict) -> None:
    jsonschema.validate(
        document, json.loads((HERE / "schema.json").read_text())
    )
    for name, record in document["imports"].items():
        path = ROOT / record["path"]
        if path != produce.SOURCES[name] or sha256(path) != record["sha256"]:
            raise RuntimeError(f"source drift: {name}")

    expected = produce.produce()
    if document != expected:
        raise RuntimeError("independent recomputation mismatch")

    tier_a = document["tier_A_transport_free_determinant"]
    if (
        tier_a["det_O_nonzero_certified"]
        or tier_a["Tplus_rank_certified"]
        or tier_a["certified_full_typed_Tminus_matrix_available"]
        or tier_a["diagnostic_only"]["certified_nonzero"]
    ):
        raise RuntimeError("determinant/outgoing rank promoted without input")
    if (
        tier_a["diagnostic_only"]["classification"] != "OBSERVED"
        or tier_a["diagnostic_only"]["source_lifecycle"]
        != "UNVALIDATED-NUMERIC"
    ):
        raise RuntimeError("diagnostic lifecycle drift")
    missing = {
        item["object"]: item["status"]
        for item in document["missing_object_ledger"]
    }
    for name in (
        "certified_full_typed_Tminus_matrix",
        "certified_explicit_Tplus_matrix",
        "explicit_common_J_congruence_frames",
    ):
        if missing.get(name) != "MISSING":
            raise RuntimeError(f"missing-object ledger drift: {name}")

    tier_b = document["tier_B_abstract_pseudo_isometry"]
    if (
        not tier_b["abstract_Tplus_existence"]["certified"]
        or not tier_b["abstract_stokes_identity"]["certified"]
        or not tier_b["raw_embedding"]["certified"]
        or not tier_b["raw_embedding"]["injective"]
        or tier_b["normalized_embedding"]["explicit_normalizers_computed"]
    ):
        raise RuntimeError("abstract theorem boundary drift")

    flags = document["claim_flags"]
    for key in (
        "oriented_raw_basis_crosswalk_certified",
        "transport_free_det_equivalence_certified",
        "abstract_typed_Tplus_exists",
        "abstract_stokes_on_horizon_regular_columns",
        "raw_one_sided_pseudo_isometric_embedding_certified",
        "abstract_common_J_normalization_exists",
    ):
        if not flags[key]:
            raise RuntimeError(f"missing exact abstract claim: {key}")
    for key in (
        "full_typed_Tminus_entries_certified",
        "det_O_nonzero_certified",
        "Tplus_rank_or_outgoing_population_certified",
        "explicit_Tplus_matrix_certified",
        "physical_reflection_map_evaluated",
        "time_domain_or_quantum_claim",
    ):
        if flags[key]:
            raise RuntimeError(f"downstream claim promoted: {key}")


def main() -> None:
    verify(json.loads((HERE / "certificate.json").read_text()))
    print("PASS transport-free outgoing-defect preflight")


if __name__ == "__main__":
    main()
