"""Antifield-number filtered block interface for later BV imports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .relative_cohomology import Bidegree, FiniteBicomplex, SparseMatrix


LIFT_COMPARISON_STATUSES = (
    "LIFTS_UNCHANGED",
    "REQUIRES_ANTIFIELD_COMPLETION",
    "BECOMES_EXACT",
    "IS_OBSTRUCTED",
)


@dataclass(frozen=True, order=True)
class FilteredDegree:
    antifield_number: int
    ghost_number: int
    form_degree: int

    def __post_init__(self) -> None:
        if self.antifield_number < 0:
            raise ValueError("antifield number must be nonnegative")
        if not 0 <= self.form_degree <= 4:
            raise ValueError("form degree is outside 0,...,4")


class FilteredLocalComplex:
    """Sparse ``Q`` blocks ordered by antifield-number shift.

    A key ``(source, shift)`` targets ghost number ``g+1``, the same form
    degree, and antifield number ``afn+shift``.  Shift ``-1`` is ``delta``,
    shift zero is ``gamma``, and positive shifts are distinct ``Q_gt0``
    components from the classical import contract.
    """

    def __init__(
        self,
        spaces: Mapping[FilteredDegree, Sequence[str]],
        q_blocks: Mapping[tuple[FilteredDegree, int], SparseMatrix],
        d_maps: Mapping[FilteredDegree, SparseMatrix],
    ) -> None:
        self.spaces = {degree: tuple(labels) for degree, labels in spaces.items()}
        self.q_blocks = dict(q_blocks)
        self.d_maps = dict(d_maps)
        self._validate()

    def _dimension(self, degree: FilteredDegree) -> int:
        return len(self.spaces.get(degree, ()))

    @staticmethod
    def component_name(shift: int) -> str:
        if shift == -1:
            return "delta"
        if shift == 0:
            return "gamma"
        if shift > 0:
            return f"Q_gt0[{shift}]"
        raise ValueError("Q components below delta are forbidden")

    def _validate(self) -> None:
        for degree, labels in self.spaces.items():
            if len(labels) != len(set(labels)):
                raise ValueError(f"duplicate filtered basis label at {degree}")
        for (source, shift), matrix in self.q_blocks.items():
            self.component_name(shift)
            target_afn = source.antifield_number + shift
            if target_afn < 0:
                raise ValueError("Q block targets negative antifield number")
            target = FilteredDegree(
                target_afn, source.ghost_number + 1, source.form_degree
            )
            if (matrix.row_count, matrix.column_count) != (
                self._dimension(target),
                self._dimension(source),
            ):
                raise ValueError(f"filtered Q block shape disagrees at {source}")
        for source, matrix in self.d_maps.items():
            target = FilteredDegree(
                source.antifield_number,
                source.ghost_number,
                source.form_degree + 1,
            )
            if (matrix.row_count, matrix.column_count) != (
                self._dimension(target),
                self._dimension(source),
            ):
                raise ValueError(f"filtered d_h block shape disagrees at {source}")

    def block_manifest(self) -> dict[str, object]:
        return {
            "ordering": "increasing_antifield_number",
            "components": [
                {
                    "source": {
                        "antifield_number": source.antifield_number,
                        "ghost_number": source.ghost_number,
                        "form_degree": source.form_degree,
                    },
                    "antifield_number_shift": shift,
                    "component": self.component_name(shift),
                    "matrix": matrix.canonical_payload(),
                }
                for (source, shift), matrix in sorted(self.q_blocks.items())
            ],
            "comparison_statuses": list(LIFT_COMPARISON_STATUSES),
        }

    def afn0_view(self) -> FiniteBicomplex:
        spaces = {
            Bidegree(degree.ghost_number, degree.form_degree): labels
            for degree, labels in self.spaces.items()
            if degree.antifield_number == 0 and labels
        }
        q_maps = {
            Bidegree(source.ghost_number, source.form_degree): matrix
            for (source, shift), matrix in self.q_blocks.items()
            if source.antifield_number == 0 and shift == 0
        }
        d_maps = {
            Bidegree(source.ghost_number, source.form_degree): matrix
            for source, matrix in self.d_maps.items()
            if source.antifield_number == 0
        }
        return FiniteBicomplex(spaces, q_maps, d_maps)
