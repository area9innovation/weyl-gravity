from __future__ import annotations

from black_hole_programme.phase3.axial_global_connection_matrix_v5.chunks.point_infinity_endpoint import (
    build_point_source,
)


def test_point_endpoint_is_deterministic_and_zero_radius() -> None:
    source_a, receipt_a = build_point_source()
    source_b, receipt_b = build_point_source()
    assert source_a == source_b
    assert receipt_a == receipt_b
    assert receipt_a["frequency"]["radius"] == "0/1"
    assert "whole-frequency-cell" in receipt_a["not_constructed_from"]
