from __future__ import annotations

from fractions import Fraction

from black_hole_programme.phase3.axial_global_connection_matrix_v5.chunks.run_point_microfactor_batch import (
    build_point_context,
    render_point_factor,
    verify_point_source,
)
import pytest


def test_point_context_has_no_frequency_uncertainty() -> None:
    omega0 = Fraction(4097, 8192)
    context = build_point_context()
    assert context["omega_cell"] == (omega0, omega0)
    assert context["declared_frequency_radius"] == 0
    assert context["point_frequency"] is True
    assert all(
        value == 0
        for frame in context["frames"]
        for row in frame.derivative
        for value in row
    )
    source, metadata = render_point_factor(0, context)
    assert metadata["omega_radius"] == "0"
    assert 'big("4097/8192")' in source
    assert 'big("1/1")' in source  # nonphysical bookkeeping cell radius
    assert verify_point_source(source)


def test_point_source_rejects_a_frequency_linear_mutation() -> None:
    source, _ = render_point_factor(0, build_point_context())
    with pytest.raises(ValueError, match="nonzero linear"):
        verify_point_source(source + "\nd=qm_set(d,0,0,rat(1,1));\n")
