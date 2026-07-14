"""Split normal-form free-BV fixture after CKV separation.

The minimal trace-free detour row is augmented by the Weyl trace doublet,
its antifield dual, and a scalar antighost/multiplier test doublet.
Every eliminated coordinate is therefore accompanied by a concrete
contracting homotopy.  The only cohomology is the two-chirality physical
metric block.

This exact ``D x SO(4)``-finite fixture predates the field-derived gauge
fermion and is not the complete nonminimal field domain.  The complete
vector-plus-scalar nonminimal extension and both antifield duals are built in
``field_bv_identification.gauge_fixed_equivalence``.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb

import sympy as sp

from bridge.bgg_operators import CylinderBGGBlock


@dataclass(frozen=True)
class FieldSlice:
    name: str
    start: int
    stop: int
    ghost_number: int
    antifield_number: int
    role: str

    @property
    def dimension(self) -> int:
        return self.stop - self.start


def _identity_entries(row_start: int, column_start: int, size: int):
    return {
        (row_start + offset, column_start + offset): sp.Integer(1)
        for offset in range(size)
    }


@dataclass(frozen=True)
class FreeBVBlock:
    energy: int
    fields: tuple[FieldSlice, ...]
    q: sp.SparseMatrix
    inclusion: sp.SparseMatrix
    projection: sp.SparseMatrix
    homotopy: sp.SparseMatrix
    physical_dimension: int

    @classmethod
    def at_energy(cls, energy: int) -> "FreeBVBlock":
        bgg = CylinderBGGBlock.at_energy(energy)
        d = bgg.dimensions
        scalar = comb(energy + 3, 3)
        specifications = (
            ("diff_ghost", d.gauge, -1, 0, "minimal ghost, CKVs removed"),
            ("weyl_ghost", scalar, -1, 0, "minimal Weyl ghost"),
            ("metric_trace", scalar, 0, 0, "Weyl-contractible trace"),
            ("metric_tf", d.metric, 0, 0, "trace-free metric"),
            ("metric_antifield", d.bach_target, 1, 1, "Bach equation row"),
            ("diff_ghost_antifield", d.noether_identity, 2, 2, "Noether identity row"),
            ("trace_antifield", scalar, 1, 1, "dual Weyl-contractible source"),
            ("weyl_ghost_antifield", scalar, 2, 2, "dual Weyl-contractible target"),
            ("antighost", scalar, -1, 0, "nonminimal source"),
            ("multiplier", scalar, 0, 0, "nonminimal target"),
        )
        fields: list[FieldSlice] = []
        offset = 0
        for name, dimension, ghost_number, antifield_number, role in specifications:
            fields.append(
                FieldSlice(
                    name,
                    offset,
                    offset + dimension,
                    ghost_number,
                    antifield_number,
                    role,
                )
            )
            offset += dimension
        by_name = {field.name: field for field in fields}
        entries: dict[tuple[int, int], sp.Expr] = {}

        def insert(target: str, source: str, matrix: sp.MatrixBase) -> None:
            target_slice = by_name[target]
            source_slice = by_name[source]
            if matrix.shape != (target_slice.dimension, source_slice.dimension):
                raise AssertionError(f"shape mismatch for {source}->{target}")
            for (row, column), value in matrix.todok().items():
                entries[target_slice.start + row, source_slice.start + column] = value

        insert("metric_tf", "diff_ghost", bgg.gauge_map)
        insert("metric_trace", "weyl_ghost", sp.SparseMatrix.eye(scalar))
        insert("metric_antifield", "metric_tf", bgg.bach)
        insert("diff_ghost_antifield", "metric_antifield", bgg.noether)
        insert(
            "weyl_ghost_antifield",
            "trace_antifield",
            sp.SparseMatrix.eye(scalar),
        )
        insert("multiplier", "antighost", sp.SparseMatrix.eye(scalar))
        q = sp.SparseMatrix(offset, offset, entries)

        # Physical H coordinates are the W+ and W- slots immediately after
        # the gauge image in the trace-free metric block.
        physical = d.physical
        metric = by_name["metric_tf"]
        physical_start = metric.start + d.gauge
        inclusion_entries = _identity_entries(physical_start, 0, physical)
        inclusion = sp.SparseMatrix(offset, physical, inclusion_entries)
        projection_entries = _identity_entries(0, physical_start, physical)
        projection = sp.SparseMatrix(physical, offset, projection_entries)

        # Explicit inverse on every contractible pair.
        s_entries: dict[tuple[int, int], sp.Expr] = {}

        def inverse_pair(source: str, target: str, size: int, source_shift: int = 0, target_shift: int = 0):
            source_slice = by_name[source]
            target_slice = by_name[target]
            s_entries.update(
                _identity_entries(
                    source_slice.start + source_shift,
                    target_slice.start + target_shift,
                    size,
                )
            )

        inverse_pair("diff_ghost", "metric_tf", d.gauge)
        inverse_pair("weyl_ghost", "metric_trace", scalar)
        inverse_pair(
            "metric_tf",
            "metric_antifield",
            d.equation,
            source_shift=d.gauge + d.physical,
        )
        inverse_pair(
            "metric_antifield",
            "diff_ghost_antifield",
            d.noether_identity,
            source_shift=d.equation,
        )
        inverse_pair("trace_antifield", "weyl_ghost_antifield", scalar)
        inverse_pair("antighost", "multiplier", scalar)
        homotopy = sp.SparseMatrix(offset, offset, s_entries)

        result = cls(
            energy,
            tuple(fields),
            q,
            inclusion,
            projection,
            homotopy,
            physical,
        )
        result.verify()
        return result

    @property
    def dimension(self) -> int:
        return self.q.rows

    def field(self, name: str) -> FieldSlice:
        return next(field for field in self.fields if field.name == name)

    def verify(self) -> None:
        identity = sp.SparseMatrix.eye(self.dimension)
        reduced_identity = sp.SparseMatrix.eye(self.physical_dimension)
        if self.q * self.q != sp.SparseMatrix(self.dimension, self.dimension, {}):
            raise AssertionError("q^2 != 0")
        if self.projection * self.inclusion != reduced_identity:
            raise AssertionError("p j != identity")
        if self.inclusion * self.projection != identity - self.q * self.homotopy - self.homotopy * self.q:
            raise AssertionError("j p != 1-q s-s q")
        if self.homotopy * self.homotopy != sp.SparseMatrix(self.dimension, self.dimension, {}):
            raise AssertionError("s^2 != 0")
        if self.homotopy * self.inclusion != sp.SparseMatrix(self.dimension, self.physical_dimension, {}):
            raise AssertionError("s j != 0")
        if self.projection * self.homotopy != sp.SparseMatrix(self.physical_dimension, self.dimension, {}):
            raise AssertionError("p s != 0")
        if self.q * self.inclusion != sp.SparseMatrix(self.dimension, self.physical_dimension, {}):
            raise AssertionError("physical inclusion is not closed")
        if self.projection * self.q != sp.SparseMatrix(self.physical_dimension, self.dimension, {}):
            raise AssertionError("projection does not kill exacts")
