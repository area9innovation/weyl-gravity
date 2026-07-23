"""Typed factor manifest for validated infinity-plane propagation."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from ..affine_rail import build_microfactor_render_context
from .child_cell_factor import (
    cell_payload,
    frequency_cell,
    prefix_boundary_crosswalk,
)
from .child_tail_join import load_cover as load_tail_cover
from .compose_child_global import restrict_prefix_matrix
from .factor_cover import factor_bounds, factor_id
from .infinity_plane_contract import contract_payload, verify_contract
from .prefix_join import load_prefix_cover
from .verify_handoff import (
    _file_sha256,
    _require,
    canonical_sha256,
)


SCHEMA = "phase3-axial-infinity-plane-factor-manifest-v1"
STAGE_BOUNDARIES = tuple(Fraction(4 * index) for index in range(8))


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _rational(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _radial_step(
    *,
    ordinal: int,
    kind: str,
    path: Path,
    payload: dict,
    matrix: dict,
    input_chart: str,
    output_chart: str,
    repo_root: Path,
) -> dict:
    if "domain" in payload:
        start, end = factor_bounds(payload)
    else:
        start = Fraction(payload["radial"]["start"])
        end = Fraction(payload["radial"]["end"])
    return {
        "ordinal": ordinal,
        "kind": kind,
        "radial": {
            "start": _rational(start),
            "end": _rational(end),
        },
        "input_chart": input_chart,
        "output_chart": output_chart,
        "factor_id": factor_id(payload),
        "source_artifact": {
            "path": _relative(path, repo_root),
            "sha256": _file_sha256(path),
            "payload_sha256": canonical_sha256(payload),
        },
        "restricted_matrix_payload_sha256": canonical_sha256(matrix),
    }


def _stage_index(start: Fraction) -> int:
    return min(int(start // 4), 6)


def build_manifest(
    child: int,
    artifact_dir: Path,
    repo_root: Path,
) -> dict[str, Any]:
    contract = contract_payload()
    verify_contract(contract)
    prefix_context = build_microfactor_render_context()
    child_context = build_microfactor_render_context(frequency_cell(child))
    prefix_paths, prefix = load_prefix_cover(
        artifact_dir, repo_root, context=prefix_context
    )
    tail_dir = artifact_dir / "child_tail"
    tail_paths, tail = load_tail_cover(
        tail_dir, child, repo_root,
        context=child_context, prefix_context=prefix_context,
    )

    steps = []
    for path, payload in zip(prefix_paths, prefix):
        steps.append(_radial_step(
            ordinal=len(steps),
            kind="restricted-prefix-factor",
            path=path,
            payload=payload,
            matrix=restrict_prefix_matrix(payload["matrix"], child),
            input_chart="global-moving-block-lower-12",
            output_chart="global-moving-block-lower-12",
            repo_root=repo_root,
        ))

    crosswalk = prefix_boundary_crosswalk(child, prefix_context)
    boundary = Fraction(crosswalk["radial_boundary"])
    steps.append({
        "ordinal": len(steps),
        "kind": "exact-prefix-to-fixed-frame-crosswalk",
        "radial": {
            "start": _rational(boundary),
            "end": _rational(boundary),
        },
        "input_chart": crosswalk["input_chart"],
        "output_chart": crosswalk["output_chart"],
        "factor_id": f"prefix-crosswalk-q{child:02d}",
        "source_artifact": None,
        "restricted_matrix_payload_sha256": canonical_sha256(crosswalk),
        "crosswalk_sha256": crosswalk["crosswalk_sha256"],
    })

    for path, payload in zip(tail_paths, tail):
        steps.append(_radial_step(
            ordinal=len(steps),
            kind="child-fixed-frame-tail-factor",
            path=path,
            payload=payload,
            matrix=payload["matrix"],
            input_chart="fixed-standard-frame-block-order-12",
            output_chart="fixed-standard-frame-block-order-12",
            repo_root=repo_root,
        ))

    stages = []
    for index, (start, end) in enumerate(
        zip(STAGE_BOUNDARIES[:-1], STAGE_BOUNDARIES[1:])
    ):
        ordinals = [
            step["ordinal"] for step in steps
            if (
                Fraction(step["radial"]["start"]) >= start
                and Fraction(step["radial"]["start"]) < end
            )
        ]
        stages.append({
            "stage": index,
            "radial": {"start": _rational(start), "end": _rational(end)},
            "step_ordinals": ordinals,
            "rechart_and_rebase_at_end": True,
        })

    initializer_cert = (
        repo_root
        / "black_hole_programme/phase3/axial_infinity_practical_transfer"
        / "certificate.json"
    )
    initializer_adapter = initializer_cert.with_name(
        "validated_infinity_transfer.forge"
    )
    contract_path = artifact_dir / "infinity_physical_plane_contract.json"
    payload = {
        "schema": SCHEMA,
        "status": "READY_FOR_VALIDATED_PROPAGATION",
        "cell": cell_payload(child),
        "domain": {
            "coordinate": "t=32-r",
            "orientation": "increasing-t/inward-r",
            "start": "0/1",
            "end": "28/1",
        },
        "plane_contract": {
            "path": _relative(contract_path, repo_root),
            "sha256": _file_sha256(contract_path),
            "payload_sha256": canonical_sha256(contract),
        },
        "infinity_initializer": {
            "certificate_path": _relative(initializer_cert, repo_root),
            "certificate_sha256": _file_sha256(initializer_cert),
            "adapter_path": _relative(initializer_adapter, repo_root),
            "adapter_sha256": _file_sha256(initializer_adapter),
            "selection_is_applied_after_initializer": True,
        },
        "steps": steps,
        "stages": stages,
        "proof": {
            "prefix_factor_count": len(prefix),
            "crosswalk_count": 1,
            "tail_factor_count": len(tail),
            "total_step_count": len(steps),
            "exact_radial_factor_cover": True,
            "exact_chart_crosswalk": True,
            "factorwise_rank_certified": True,
            "full_matrix_join_not_used_for_plane_classification": True,
        },
        "required_terminal_gate": contract["required_terminal_gate"],
        "does_not_establish": [
            "successful degree-two Taylor propagation",
            "rank-six propagated endpoint planes",
            "rank-twelve concatenated endpoint basis",
            "horizon-to-infinity matching",
            "endpoint flux, scattering, stability, CPT, or unitarity",
        ],
    }
    payload["payload_sha256"] = canonical_sha256(payload)
    verify_manifest(payload, child, artifact_dir, repo_root, rebuild=False)
    return payload


def verify_manifest(
    data: Any,
    child: int,
    artifact_dir: Path,
    repo_root: Path,
    *,
    rebuild: bool = True,
) -> bool:
    _require(data.get("schema") == SCHEMA, "plane manifest: wrong schema")
    _require(
        data.get("status") == "READY_FOR_VALIDATED_PROPAGATION",
        "plane manifest: wrong status",
    )
    _require(data["cell"] == cell_payload(child), "plane manifest: cell drift")
    steps = data["steps"]
    _require(
        len(steps) == 279
        and [step["ordinal"] for step in steps] == list(range(279)),
        "plane manifest: incomplete or unordered steps",
    )
    radial = [step for step in steps if step["radial"]["start"] != step["radial"]["end"]]
    cursor = Fraction(0)
    for step in radial:
        start = Fraction(step["radial"]["start"])
        end = Fraction(step["radial"]["end"])
        _require(
            start == cursor and end > start,
            "plane manifest: radial gap, overlap, or reversal",
        )
        cursor = end
    _require(cursor == 28, "plane manifest: radial cover ends early")
    crosswalks = [
        step for step in steps
        if step["kind"] == "exact-prefix-to-fixed-frame-crosswalk"
    ]
    _require(
        len(crosswalks) == 1
        and crosswalks[0]["radial"]["start"] == "191/8",
        "plane manifest: exact chart crosswalk missing",
    )
    stage_ordinals = [
        ordinal for stage in data["stages"]
        for ordinal in stage["step_ordinals"]
    ]
    _require(
        stage_ordinals == list(range(279)),
        "plane manifest: stage partition is not exact",
    )
    _require(
        data["proof"] == {
            "prefix_factor_count": 212,
            "crosswalk_count": 1,
            "tail_factor_count": 66,
            "total_step_count": 279,
            "exact_radial_factor_cover": True,
            "exact_chart_crosswalk": True,
            "factorwise_rank_certified": True,
            "full_matrix_join_not_used_for_plane_classification": True,
        },
        "plane manifest: proof drift",
    )
    stored_hash = data["payload_sha256"]
    without_hash = dict(data)
    without_hash.pop("payload_sha256")
    _require(
        stored_hash == canonical_sha256(without_hash),
        "plane manifest: payload hash drift",
    )
    if rebuild:
        expected = build_manifest(child, artifact_dir, repo_root)
        _require(data == expected, "plane manifest: source rerender drift")
    return True
