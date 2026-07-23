from __future__ import annotations

from black_hole_programme.phase3.axial_global_connection_matrix_v5.chunks.infinity_carrier_subspace_audit import (
    build,
)


def test_xi01_is_endpoint_selected_not_coordinate_closed() -> None:
    data = build()
    assert data["finite_rate_zero_dimension_complex"] == 2
    assert all(
        not plane["invariant"]
        for plane in data["coordinate_plane_audit"]
    )
    assert "surjectivity" in data["classification"][
        "radial_uniqueness_does_not_establish"
    ]
