"""Exact linear obstruction test for a curved first-order companion.

Given the persisted action-Hessian principal table, solve

``J_flat^{-1} E_2 + K_1 (C_flat,1 + Delta C_1) = zeta^2 I``

for an unrestricted first-order correction ``Delta C_1``.  Unrestricted
solvability is weaker than the desired SO(3)-equivariant/natural ansatz, so a
rank obstruction here is decisive: no invariant correction can exist with
the frozen flat fibre pairing.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import sympy as sp

from .conventions import CurvedBVConventions, _ordinary_system


@dataclass(frozen=True)
class CurvedCompanionLinearObstruction:
    coefficient_rank: int
    augmented_ranks: tuple[int, ...]
    inconsistent_columns: tuple[int, ...]
    equation_count_per_column: int
    unknown_count_per_column: int

    @staticmethod
    def build(cache_path: Path) -> "CurvedCompanionLinearObstruction":
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
        zeta = sp.symbols("covariant_jet_zeta_0:4", real=True)
        locals_map = {str(symbol): symbol for symbol in zeta}
        coefficients = {}
        for item in payload["coefficients"]:
            multiindex = tuple(item["multiindex"])
            entries = [sp.sympify(value, locals=locals_map) for value in item["entries"]]
            coefficients[multiindex] = sp.Matrix(24, 24, entries)

        conventions = CurvedBVConventions.build()
        source = _ordinary_system()
        j_inverse = source.field_fibre_pairing.inv()
        k = conventions.gauge_generator.derivative_coefficients
        c = conventions.gauge_companion.derivative_coefficients
        pairs = tuple((mu, nu) for mu in range(4) for nu in range(mu, 4))

        defects = {}
        for mu, nu in pairs:
            multiindex = tuple(
                int(axis == mu) + int(axis == nu) for axis in range(4)
            )
            wave = source.metric[mu, nu] * (2 if mu != nu else 1) * sp.eye(24)
            kc = k[mu] * c[nu]
            if mu != nu:
                kc += k[nu] * c[mu]
            defects[(mu, nu)] = sp.simplify(
                wave - j_inverse * coefficients[multiindex] - kc
            )

        # The left coefficient matrix is the same for every input column of C.
        rows = []
        for mu, nu in pairs:
            for output in range(24):
                row = [sp.Integer(0)] * 36
                for ghost in range(9):
                    row[nu * 9 + ghost] += k[mu][output, ghost]
                    if mu != nu:
                        row[mu * 9 + ghost] += k[nu][output, ghost]
                rows.append(row)
        matrix = sp.Matrix(rows)
        rank = matrix.rank()
        augmented_ranks = []
        inconsistent = []
        for column in range(24):
            rhs = sp.Matrix(
                [
                    defects[(mu, nu)][output, column]
                    for mu, nu in pairs
                    for output in range(24)
                ]
            )
            augmented = matrix.row_join(rhs).rank()
            augmented_ranks.append(augmented)
            if augmented != rank:
                inconsistent.append(column)
        result = CurvedCompanionLinearObstruction(
            coefficient_rank=rank,
            augmented_ranks=tuple(augmented_ranks),
            inconsistent_columns=tuple(inconsistent),
            equation_count_per_column=matrix.rows,
            unknown_count_per_column=matrix.cols,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.equation_count_per_column != 240:
            raise AssertionError("curved companion ansatz equation ledger drifted")
        if self.unknown_count_per_column != 36:
            raise AssertionError("curved companion ansatz unknown ledger drifted")

    @property
    def solvable_with_flat_pairing(self) -> bool:
        return not self.inconsistent_columns

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-curved-companion-linear-obstruction-v1",
            "ansatz": "unrestricted first-order Delta C_mu (9x24 per derivative)",
            "fixed_pairing": "flat J_aux",
            "equations_per_input_column": self.equation_count_per_column,
            "unknowns_per_input_column": self.unknown_count_per_column,
            "coefficient_rank": self.coefficient_rank,
            "augmented_ranks": list(self.augmented_ranks),
            "inconsistent_input_columns": list(self.inconsistent_columns),
            "solvable_with_flat_pairing": self.solvable_with_flat_pairing,
            "interpretation": (
                "if false, even an unrestricted correction C cannot restore the wave "
                "symbol with frozen J_flat; J and C must be reconstructed jointly"
            ),
        }
