"""Exact null-symbol obstruction for the current curved ``E`` and ``K``.

For a normally hyperbolic field block with a pointwise invertible fibre form
``J`` and a first-order companion ``C``, the homogeneous symbols must obey

``J^{-1} E_2(zeta) + K_1(zeta) C_1(zeta) = q(zeta) I``.

At a null covector this forces ``rank(E_2) <= rank(K_1)``.  The exact cached
action Hessian and exact curved gauge generator violate that necessary
condition at ``zeta=(1,1,0,0)``: their ranks are 11 and 9.  This obstruction
is independent of SO(3) invariance and therefore rules out the entire
pointwise-pairing ansatz for the current ``E`` and ``K`` inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import sympy as sp

from .conventions import CurvedBVConventions, _ordinary_system
from .expanded_hessian import load_coefficient_cache


DEFAULT_CACHE = (
    Path(__file__).resolve().parents[1]
    / "certificates"
    / "curved_hessian_coefficient_table.json"
)


@dataclass(frozen=True)
class NullSymbolRankObstruction:
    covector: tuple[int, int, int, int]
    covector_square: int
    hessian_rank: int
    gauge_rank: int
    hessian_minor_rows: tuple[int, ...]
    hessian_minor_columns: tuple[int, ...]
    hessian_minor_determinant: int
    gauge_minor_rows: tuple[int, ...]
    gauge_minor_columns: tuple[int, ...]
    gauge_minor_determinant: int
    fixed_j_left_nullity: int
    fixed_j_obstruction_rank: int
    polarization_witnesses: tuple[dict[str, object], ...]
    field_operator_rank: int
    combined_image_rank: int
    image_intersection_dimension: int
    image_quotient_dimension: int
    quotient_witnesses: tuple[dict[str, object], ...]
    hessian_high_order_jet_vectors_tested: int
    hessian_cache_sha256: str

    @staticmethod
    def build(cache_path: Path = DEFAULT_CACHE) -> "NullSymbolRankObstruction":
        zeta, hessian, payload = load_coefficient_cache(cache_path)
        scale = sp.Symbol("null_symbol_scale")
        scaled = {entry: scale * entry for entry in zeta}
        principal = hessian.applyfunc(
            lambda value: sp.expand(value.subs(scaled)).coeff(scale, 2)
        )
        null_covector = (1, 1, 0, 0)
        substitution = dict(zip(zeta, null_covector, strict=True))
        hessian_at_null = principal.subs(substitution)

        conventions = CurvedBVConventions.build()
        gauge_at_null = sum(
            (
                null_covector[axis]
                * conventions.gauge_generator.derivative_coefficients[axis]
                for axis in range(4)
            ),
            sp.zeros(24, 9),
        )
        fixed_j_gauge = _ordinary_system().field_fibre_pairing * gauge_at_null
        field_operator = (
            _ordinary_system().field_fibre_pairing.inv() * hessian_at_null
        )
        left_nullspace = fixed_j_gauge.T.nullspace()
        left_null_matrix = sp.Matrix.hstack(*left_nullspace)
        obstruction_rank = (left_null_matrix.T * hessian_at_null).rank()

        first_polarization = sp.zeros(24, 1)
        first_polarization[8] = 1
        second_polarization = sp.zeros(24, 1)
        second_polarization[7] = -1
        second_polarization[9] = 1
        polarization_data = []
        for name, vector in (
            ("h_23", first_polarization),
            ("h_33_minus_h_22", second_polarization),
        ):
            gauge_row = vector.T * fixed_j_gauge
            hessian_row = vector.T * hessian_at_null
            polarization_data.append(
                {
                    "name": name,
                    "ell_nonzero_components": [
                        [index, int(vector[index])]
                        for index in range(24)
                        if vector[index] != 0
                    ],
                    "ell_T_JK_is_zero": gauge_row == sp.zeros(1, 9),
                    "ell_T_E_nonzero_components": [
                        [index, int(hessian_row[index])]
                        for index in range(24)
                        if hessian_row[index] != 0
                    ],
                }
            )
        quotient_data = []
        for column, gauge_coefficients, name in (
            (
                7,
                sp.Matrix(
                    [
                        sp.Rational(1, 2),
                        sp.Rational(1, 2),
                        0,
                        0,
                        -2,
                        2,
                        0,
                        0,
                        0,
                    ]
                ),
                "f_22_minus_f_33",
            ),
            (8, sp.zeros(9, 1), "f_23"),
        ):
            representative = (
                field_operator[:, column] - gauge_at_null * gauge_coefficients
            )
            quotient_data.append(
                {
                    "name": name,
                    "input_column": column,
                    "subtracted_gauge_coefficients": [
                        str(value) for value in gauge_coefficients
                    ],
                    "representative_nonzero_components": [
                        [index, int(representative[index])]
                        for index in range(24)
                        if representative[index] != 0
                    ],
                }
            )
        combined_rank = field_operator.row_join(gauge_at_null).rank()
        intersection_dimension = (
            field_operator.rank() + gauge_at_null.rank() - combined_rank
        )
        hessian_rows = (0, 2, 3, 7, 8, 9, 10, 12, 13, 17, 20)
        gauge_rows = (0, 1, 2, 3, 10, 11, 12, 13, 20)
        result = NullSymbolRankObstruction(
            covector=null_covector,
            covector_square=int(
                (
                    sp.Matrix(null_covector).T
                    * _ordinary_system().metric
                    * sp.Matrix(null_covector)
                )[0]
            ),
            hessian_rank=hessian_at_null.rank(),
            gauge_rank=gauge_at_null.rank(),
            hessian_minor_rows=hessian_rows,
            hessian_minor_columns=hessian_rows,
            hessian_minor_determinant=int(
                hessian_at_null.extract(hessian_rows, hessian_rows).det()
            ),
            gauge_minor_rows=gauge_rows,
            gauge_minor_columns=tuple(range(9)),
            gauge_minor_determinant=int(
                gauge_at_null.extract(gauge_rows, tuple(range(9))).det()
            ),
            fixed_j_left_nullity=len(left_nullspace),
            fixed_j_obstruction_rank=obstruction_rank,
            polarization_witnesses=tuple(polarization_data),
            field_operator_rank=field_operator.rank(),
            combined_image_rank=combined_rank,
            image_intersection_dimension=intersection_dimension,
            image_quotient_dimension=field_operator.rank() - intersection_dimension,
            quotient_witnesses=tuple(quotient_data),
            hessian_high_order_jet_vectors_tested=int(
                payload["high_order_jet_vectors_tested"]
            ),
            hessian_cache_sha256=payload["sha256"],
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.covector_square != 0:
            raise AssertionError("rank obstruction covector is not null")
        if self.hessian_rank != 11 or self.hessian_minor_determinant != -1:
            raise AssertionError("curved Hessian null-rank witness drifted")
        if self.gauge_rank != 9 or self.gauge_minor_determinant != 4:
            raise AssertionError("curved gauge null-rank witness drifted")
        if self.hessian_rank <= self.gauge_rank:
            raise AssertionError("expected strict null-symbol rank obstruction vanished")
        if self.fixed_j_left_nullity != 15:
            raise AssertionError("fixed-J gauge cokernel dimension drifted")
        if self.fixed_j_obstruction_rank != 2:
            raise AssertionError("fixed-J obstruction channel rank drifted")
        expected_rows = (
            ("h_23", ((8, 1),), ((8, 4),)),
            ("h_33_minus_h_22", ((7, -1), (9, 1)), ((7, -2), (9, 2))),
        )
        actual_rows = tuple(
            (
                witness["name"],
                tuple(tuple(entry) for entry in witness["ell_nonzero_components"]),
                tuple(
                    tuple(entry)
                    for entry in witness["ell_T_E_nonzero_components"]
                ),
            )
            for witness in self.polarization_witnesses
        )
        if actual_rows != expected_rows:
            raise AssertionError("transverse spin-2 obstruction witnesses drifted")
        if not all(
            witness["ell_T_JK_is_zero"]
            for witness in self.polarization_witnesses
        ):
            raise AssertionError("a claimed cokernel witness is not left-null")
        if (
            self.field_operator_rank,
            self.combined_image_rank,
            self.image_intersection_dimension,
            self.image_quotient_dimension,
        ) != (11, 11, 9, 2):
            raise AssertionError("field-operator quotient dimensions drifted")
        expected_quotient = (
            ("f_22_minus_f_33", 7, ((17, 2), (19, -2))),
            ("f_23", 8, ((18, 4),)),
        )
        actual_quotient = tuple(
            (
                witness["name"],
                witness["input_column"],
                tuple(
                    tuple(entry)
                    for entry in witness["representative_nonzero_components"]
                ),
            )
            for witness in self.quotient_witnesses
        )
        if actual_quotient != expected_quotient:
            raise AssertionError("helicity-2 quotient representatives drifted")

    @property
    def pointwise_pairing_companion_solution_exists(self) -> bool:
        return self.hessian_rank <= self.gauge_rank

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-curved-null-symbol-rank-obstruction-v1",
            "atomic_flag": "curved_scalar_wave_no_go",
            "curved_scalar_wave_no_go": True,
            "identity_under_test": "J^-1 E_2 + K_1 C_1 = q I",
            "covector": list(self.covector),
            "covector_square": self.covector_square,
            "exact_hessian_rank": self.hessian_rank,
            "exact_gauge_rank": self.gauge_rank,
            "hessian_nonzero_minor": {
                "rows": list(self.hessian_minor_rows),
                "columns": list(self.hessian_minor_columns),
                "determinant": self.hessian_minor_determinant,
            },
            "gauge_nonzero_minor": {
                "rows": list(self.gauge_minor_rows),
                "columns": list(self.gauge_minor_columns),
                "determinant": self.gauge_minor_determinant,
            },
            "rank_inequality_required_at_null_covector": "rank(E_2)<=rank(K_1)",
            "rank_inequality_defect": self.hessian_rank - self.gauge_rank,
            "fixed_action_pairing_cokernel": {
                "left_nullity_of_JK": self.fixed_j_left_nullity,
                "rank_of_L_T_E_2": self.fixed_j_obstruction_rank,
                "witnesses": list(self.polarization_witnesses),
                "tensor_coordinate_legend": {
                    "7": "(2,2)",
                    "8": "(2,3)",
                    "9": "(3,3)",
                },
                "little_group_channels": (
                    "the two transverse spatial trace-free spin-2 polarizations "
                    "relative to the null covector along x1"
                ),
            },
            "fixed_action_field_operator_quotient": {
                "conversion": "N=J_act^-1 E_2 (E_2 itself is dual-valued)",
                "rank_N": self.field_operator_rank,
                "rank_K": self.gauge_rank,
                "rank_concatenated_N_K": self.combined_image_rank,
                "image_intersection_dimension": self.image_intersection_dimension,
                "image_N_mod_image_K_dimension": self.image_quotient_dimension,
                "representatives": list(self.quotient_witnesses),
                "field_coordinate_legend": {
                    "17": "f_(2,2)",
                    "18": "f_(2,3)",
                    "19": "f_(3,3)",
                },
                "channel": (
                    "real helicity-2 SO(2) pair transverse to the null covector "
                    "along x1"
                ),
            },
            "pointwise_pairing_companion_solution_exists": (
                self.pointwise_pairing_companion_solution_exists
            ),
            "scope": (
                "all invertible pointwise J and all first-order C; no invariance or "
                "formal-adjoint ansatz was imposed"
            ),
            "hessian_cache_sha256": self.hessian_cache_sha256,
            "hessian_high_order_jet_vectors_tested": (
                self.hessian_high_order_jet_vectors_tested
            ),
            "repair_boundary": (
                "the current E_2 or K_1 input must change (or the gauge bundle/order "
                "architecture must change); varying only J, Y, C, or the gauge density "
                "cannot remove this rank obstruction"
            ),
            "fail_closed": True,
        }
