from __future__ import annotations

import json
from pathlib import Path

from black_hole_programme.phase3.axial_global_connection_matrix_v5.chunks.infinity_plane_taylor_transport import (
    IVTAYLOR_COMMIT,
    parse_stage_output,
    render_stage,
)


ROOT = Path(__file__).resolve().parents[5]
ARTIFACTS = (
    ROOT
    / "black_hole_programme/phase3/axial_global_connection_matrix_v5"
    / "chunks/artifacts"
)


def test_q0_stage0_source_is_deterministic_and_pinned() -> None:
    source_a, metadata_a = render_stage(
        child=0, stage=0, artifact_dir=ARTIFACTS,
        repo_root=ROOT, previous=None,
    )
    source_b, metadata_b = render_stage(
        child=0, stage=0, artifact_dir=ARTIFACTS,
        repo_root=ROOT, previous=None,
    )
    assert source_a == source_b
    assert metadata_a == metadata_b
    assert metadata_a["ivtaylor"]["commit"] == IVTAYLOR_COMMIT
    assert metadata_a["factor_count"] == 32
    assert "ivtm_solve_right" in source_a
    assert "combined" in source_a


def test_stage_output_parser_requires_both_planes_and_combined_rank() -> None:
    model = {
        "schema": "ivtaylor-degree2-v1",
        "generator": 7315,
        "degree": 2,
        "rows": 12,
        "cols": 6,
        "refusal_code": 0,
        "coefficients": [],
        "remainder_bits": [],
    }
    text = "\n".join([
        "RANKS 6 6 12",
        "RANK_CERTS false true true CODES 7 0 0 CELLS 0 64 64",
        "RANK_PROOF minus=true plus=true combined=true derived_from_combined=true",
        "CHARTS 3 7",
        "BOUNDS 0 4607182418800017408 0 "
        "0 4607182418800017408 256 "
        "0 4611686018427387904 0 "
        "0 4611686018427387904 512",
        f"MINUS {json.dumps(model)}",
        f"PLUS {json.dumps(model)}",
        f"MINUS_Z {json.dumps({**model, 'rows': 6})}",
        f"PLUS_Z {json.dumps({**model, 'rows': 6})}",
    ])
    planes, ranks, evidence = parse_stage_output(text)
    assert set(planes) == {
        "Iminus", "Iplus", "_chart_states", "_basis_change_majorants",
    }
    assert ranks == {"Iminus": 6, "Iplus": 6, "combined": 12}
    assert evidence["direct"]["certified"]["Iminus"] is False
    assert evidence["proof"]["derived_from_combined"] is True
    assert planes["_chart_states"]["Iminus"]["chart"] == 3
    assert planes["_basis_change_majorants"]["Iplus"]["forward"][
        "mantissa_bits"
    ][1] == (
        4611686018427387904
    )
    assert planes["_basis_change_majorants"]["Iplus"]["inverse"][
        "binary_exponent"
    ] == 512
