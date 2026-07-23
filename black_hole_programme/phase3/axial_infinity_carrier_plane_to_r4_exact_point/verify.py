#!/usr/bin/env python3
"""Verify the staged exact-point infinity-plane transport chain."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from black_hole_programme.phase3.axial_global_connection_matrix_v5.chunks.point_carrier_plane_transport import (
    STAGE_BOUNDARIES,
    verify_stage_payload,
)
from black_hole_programme.phase3.axial_global_connection_matrix_v5.chunks.verify_handoff import (
    _require,
    canonical_sha256,
)


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificate.json"
STAGES = HERE / "stages"
FULL_SUMMARY = HERE / "full-factor-summary.json"
TAIL_SUMMARY = HERE / "tail-factor-summary.json"


def verify(document: Any | None = None) -> bool:
    cert = json.loads(CERTIFICATE.read_text()) if document is None else document
    _require(
        cert.get("schema")
        == "phase3-axial-infinity-carrier-plane-to-r4-exact-point-v1",
        "exact-point infinity-plane schema drift",
    )
    _require(cert.get("lifecycle") == "CLASSIFIED", "lifecycle drift")
    _require(
        cert.get("construction", {}).get("factor_count")
        == STAGE_BOUNDARIES[-1] == 348,
        "factor count drift",
    )
    _require(
        cert.get("construction", {}).get("stage_count") == 11,
        "stage count drift",
    )
    full = json.loads(FULL_SUMMARY.read_text())
    tail = json.loads(TAIL_SUMMARY.read_text())
    _require(
        hashlib.sha256(FULL_SUMMARY.read_bytes()).hexdigest()
        == cert["provenance"]["full_factor_summary_sha256"],
        "full factor summary hash drift",
    )
    _require(
        hashlib.sha256(TAIL_SUMMARY.read_bytes()).hexdigest()
        == cert["provenance"]["tail_factor_summary_sha256"],
        "tail factor summary hash drift",
    )
    _require(
        len([x for x in full["results"] if x.get("status") == "PASS"]) == 220,
        "full factor pass count drift",
    )
    _require(
        tail.get("split") == 32 and tail.get("all_passed") is True
        and len(tail.get("results", [])) == 128
        and all(x.get("status") == "PASS" for x in tail["results"]),
        "tail factor pass disposition drift",
    )
    previous = None
    for stage in range(11):
        payload = json.loads((STAGES / f"stage{stage}.json").read_text())
        verify_stage_payload(payload, previous=previous)
        previous = payload
    _require(
        previous["radial"]
        == {"coordinate": "t=32-r", "start": "223/8", "end": "28"},
        "terminal radial cell drift",
    )
    _require(
        previous["payload_sha256"]
        == cert["construction"]["final_stage_payload_sha256"],
        "terminal stage hash drift",
    )
    _require(
        cert["results"]
        == {
            "Iminus_dimension_at_r4": 4,
            "Iplus_dimension_at_r4": 4,
            "combined_dimension_at_r4": 8,
            "Iminus_final_chart": 1,
            "Iplus_final_chart": 4,
            "all_factor_ranks_certified": True,
            "all_stage_graph_transports_certified": True,
            "frequency_neighbourhood_certified": False,
        },
        "result disposition drift",
    )
    flags = cert["claim_flags"]
    _require(flags["exact_point_infinity_carrier_planes_populated_at_r4"], "population flag drift")
    _require(flags["exact_point_infinity_planes_transverse_at_r4"], "transversality flag drift")
    for key in (
        "horizon_regular_plane_at_r4_certified",
        "direct_Cplus_rank_certified",
        "Tplus_rank_certified",
        "reflection_nonzero_certified",
        "global_scattering_channel_certified",
    ):
        _require(flags[key] is False, f"forbidden promotion: {key}")
    return True


def mutated_stage_hash_is_rejected() -> bool:
    payload = json.loads((STAGES / "stage10.json").read_text())
    mutated = copy.deepcopy(payload)
    mutated["transversality_proof"] = "sampled-centre-rank"
    unhashed = dict(mutated)
    unhashed.pop("payload_sha256")
    mutated["payload_sha256"] = canonical_sha256(unhashed)
    try:
        verify_stage_payload(
            mutated,
            previous=json.loads((STAGES / "stage9.json").read_text()),
        )
    except Exception:
        return True
    return False


def main() -> int:
    verify()
    _require(mutated_stage_hash_is_rejected(), "stage mutation was accepted")
    print("PASS exact-point infinity carrier planes reach r=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
