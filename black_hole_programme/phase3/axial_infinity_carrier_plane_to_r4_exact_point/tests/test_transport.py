from __future__ import annotations

from black_hole_programme.phase3.axial_infinity_carrier_plane_to_r4_exact_point.verify import (
    mutated_stage_hash_is_rejected,
    verify,
)


def test_transport_chain() -> None:
    assert verify()


def test_mutated_final_chart_is_rejected() -> None:
    assert mutated_stage_hash_is_rejected()
