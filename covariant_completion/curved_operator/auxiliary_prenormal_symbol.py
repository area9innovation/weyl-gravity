"""Exact mixed-order principal-symbol diagnostic for the auxiliary field block.

The scalar-wave witness is impossible for the action-normalized curved
``24``-field block, but that does not decide Green hyperbolicity.  This module
tests the weaker mixed-order possibility without fitting a new companion.

For the exact cached Hessian and exact adjoint companion, let

``P_2 = J_act^{-1} E_2 + K_1 C_1`` and ``q=g^{-1}(zeta,zeta)``.

The key identity is

``(P_2-q I)^2=0``.

Thus ``D_2=2qI-P_2`` obeys ``D_2 P_2=P_2 D_2=q^2 I``.  This is a genuine
prenormal *principal-symbol* identity.  It is not yet an operator
factorization: covariant derivative commutators and the complete lower-order
coefficients still have to be absorbed into a local operator ``D`` whose
product with ``P`` is independently Green hyperbolic.

The aligned one-variable Smith data are also recorded.  They show exactly
six algebraic, twelve wave, and six biwave invariant factors.  No local
unimodular row/column transformations realizing those factors globally are
constructed here.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

import sympy as sp

from .conventions import CurvedBVConventions, _ordinary_system
from .expanded_hessian import load_coefficient_cache
from .null_symbol_rank_obstruction import DEFAULT_CACHE


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _homogeneous_part(
    matrix: sp.MatrixBase,
    covector: tuple[sp.Symbol, ...],
    degree: int,
) -> sp.Matrix:
    scale = sp.Symbol("auxiliary_prenormal_scale")
    scaled = {entry: scale * entry for entry in covector}
    return sp.Matrix(matrix).applyfunc(
        lambda value: sp.expand(value.subs(scaled)).coeff(scale, degree)
    )


@dataclass(frozen=True)
class AuxiliaryPrenormalSymbol:
    covector: tuple[sp.Symbol, ...]
    wave_quadratic: sp.Expr
    field_principal_symbol: sp.Matrix
    complementary_principal_symbol: sp.Matrix
    square_zero_defect: sp.Matrix
    left_product_defect: sp.Matrix
    right_product_defect: sp.Matrix
    aligned_determinant: sp.Expr
    nilpotent_deviation_nonzero_entries: int
    future_null_rank: int
    past_null_rank: int
    invariant_factor_multiplicities: tuple[int, int, int]
    frozen_lower_defect_counts: tuple[int, ...]
    frozen_quadratic_null_ranks: tuple[int, int]
    frozen_lower_defect_witnesses: tuple[str, ...]
    hessian_cache_sha256: str
    gauge_generator_sha256: str
    gauge_companion_sha256: str
    field_pairing_sha256: str
    principal_sha256: str
    complement_sha256: str
    frozen_lower_defect_sha256: str

    @staticmethod
    def build(cache_path: Path = DEFAULT_CACHE) -> "AuxiliaryPrenormalSymbol":
        covector, hessian, payload = load_coefficient_cache(cache_path)
        conventions = CurvedBVConventions.build()
        source = _ordinary_system()
        zeta = sp.Matrix(covector)
        q = sp.expand((zeta.T * source.metric * zeta)[0])

        hessian_2 = _homogeneous_part(hessian, covector, 2)
        gauge_1 = sum(
            (
                covector[axis]
                * conventions.gauge_generator.derivative_coefficients[axis]
                for axis in range(4)
            ),
            sp.zeros(24, 9),
        )
        companion_1 = sum(
            (
                covector[axis]
                * conventions.gauge_companion.derivative_coefficients[axis]
                for axis in range(4)
            ),
            sp.zeros(9, 24),
        )
        principal = sp.Matrix(
            source.field_fibre_pairing.inv() * hessian_2
            + gauge_1 * companion_1
        ).applyfunc(sp.expand)
        identity = sp.eye(24)
        nilpotent = sp.Matrix(principal - q * identity).applyfunc(sp.expand)
        complement = sp.Matrix(2 * q * identity - principal).applyfunc(sp.expand)
        square_zero_defect = sp.Matrix(nilpotent * nilpotent).applyfunc(sp.expand)
        left_defect = sp.Matrix(
            complement * principal - q**2 * identity
        ).applyfunc(sp.expand)
        right_defect = sp.Matrix(
            principal * complement - q**2 * identity
        ).applyfunc(sp.expand)

        omega, kappa = sp.symbols("omega kappa", real=True)
        aligned = principal.subs(
            {
                covector[0]: omega,
                covector[1]: kappa,
                covector[2]: 0,
                covector[3]: 0,
            }
        )
        aligned_determinant = sp.factor(aligned.det(method="domain-ge"))
        future_rank = principal.subs(
            dict(zip(covector, (1, 1, 0, 0), strict=True))
        ).rank()
        past_rank = principal.subs(
            dict(zip(covector, (-1, 1, 0, 0), strict=True))
        ).rank()

        # Test whether the literal frozen-coefficient completion
        # D_naive=2qI-P closes beyond principal order.  It does not.  This is
        # only a lower-order construction ledger: covariant commutators can
        # modify orders two and zero, so the nonzero remainder is not promoted
        # to a no-go theorem for a corrected complementary operator.
        gauge = conventions.gauge_generator.symbol(zeta)
        companion = conventions.gauge_companion.symbol(zeta)
        full_field = sp.Matrix(
            source.field_fibre_pairing.inv() * hessian + gauge * companion
        ).applyfunc(sp.expand)
        naive_complement = sp.Matrix(2 * q * identity - full_field)
        frozen_remainder = sp.Matrix(
            naive_complement * full_field - q**2 * identity
        ).applyfunc(sp.expand)
        lower_parts = tuple(
            _homogeneous_part(frozen_remainder, covector, degree)
            for degree in range(5)
        )
        lower_counts = tuple(
            sum(value != 0 for value in part) for part in lower_parts
        )
        quadratic_null_ranks = tuple(
            lower_parts[2]
            .subs(dict(zip(covector, null_covector, strict=True)))
            .rank()
            for null_covector in ((1, 1, 0, 0), (-1, 1, 0, 0))
        )
        lower_witnesses = (
            str(lower_parts[0][0, 0]),
            str(lower_parts[1][0, 20]),
            str(lower_parts[2][0, 0]),
        )

        result = AuxiliaryPrenormalSymbol(
            covector=covector,
            wave_quadratic=q,
            field_principal_symbol=principal,
            complementary_principal_symbol=complement,
            square_zero_defect=square_zero_defect,
            left_product_defect=left_defect,
            right_product_defect=right_defect,
            aligned_determinant=aligned_determinant,
            nilpotent_deviation_nonzero_entries=sum(
                value != 0 for value in nilpotent
            ),
            future_null_rank=future_rank,
            past_null_rank=past_rank,
            invariant_factor_multiplicities=(6, 12, 6),
            frozen_lower_defect_counts=lower_counts,
            frozen_quadratic_null_ranks=quadratic_null_ranks,
            frozen_lower_defect_witnesses=lower_witnesses,
            hessian_cache_sha256=str(payload["sha256"]),
            gauge_generator_sha256=(
                conventions.gauge_generator.coefficient_sha256
            ),
            gauge_companion_sha256=(
                conventions.gauge_companion.coefficient_sha256
            ),
            field_pairing_sha256=_digest(source.field_fibre_pairing),
            principal_sha256=_digest(principal),
            complement_sha256=_digest(complement),
            frozen_lower_defect_sha256=_digest(frozen_remainder),
        )
        result.verify()
        return result

    def verify(self) -> None:
        zero = sp.zeros(24)
        if self.wave_quadratic != (
            -self.covector[0] ** 2
            + self.covector[1] ** 2
            + self.covector[2] ** 2
            + self.covector[3] ** 2
        ):
            raise AssertionError("cylinder wave quadratic drifted")
        if self.square_zero_defect != zero:
            raise AssertionError("(P_2-qI)^2 is not zero")
        if self.nilpotent_deviation_nonzero_entries != 76:
            raise AssertionError("the non-scalar nilpotent deviation drifted")
        if self.left_product_defect != zero or self.right_product_defect != zero:
            raise AssertionError("the two-sided prenormal symbol identity failed")

        omega, kappa = sp.symbols("omega kappa", real=True)
        expected_determinant = (omega - kappa) ** 24 * (omega + kappa) ** 24
        if sp.expand(self.aligned_determinant - expected_determinant) != 0:
            raise AssertionError("aligned characteristic determinant drifted")
        if (self.future_null_rank, self.past_null_rank) != (6, 6):
            raise AssertionError("null rank of P_2 drifted")

        # Over Q[omega] at fixed nonzero spatial magnitude, D_2 P_2=q^2 I
        # says every Smith factor divides q^2.  Null rank six gives six unit
        # factors; det(P_2)=q^24 then uniquely forces 12 q and 6 q^2 factors.
        if self.invariant_factor_multiplicities != (6, 12, 6):
            raise AssertionError("mixed algebraic/wave/biwave Smith ledger drifted")
        if self.frozen_lower_defect_counts != (65, 95, 240, 0, 0):
            raise AssertionError("naive lower-order completion ledger drifted")
        if self.frozen_quadratic_null_ranks != (12, 12):
            raise AssertionError("naive quadratic null defect rank drifted")
        expected_witnesses = (
            "-6",
            f"4*{self.covector[0]}",
            f"-4*{self.covector[0]}**2",
        )
        if self.frozen_lower_defect_witnesses != expected_witnesses:
            raise AssertionError("naive lower-order defect witnesses drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        units, waves, biwaves = self.invariant_factor_multiplicities
        return {
            "schema": "pure-weyl-curved-auxiliary-prenormal-symbol-v1",
            "input_block": "P_2=J_act^-1 E_2+K_1 C_1",
            "exact_inputs": {
                "hessian": "cached exhaustive curved action Hessian",
                "gauge_generator": "exact curved first-order K",
                "companion": "C=Y^-1 K^sharp J_act coefficientwise",
                "scalar_wave_no_go_unchanged": True,
            },
            "wave_quadratic": str(self.wave_quadratic),
            "arbitrary_covector_identity": {
                "nilpotent_deviation": "(P_2-q I_24)^2=0",
                "nilpotent_deviation_nonzero_entries": (
                    self.nilpotent_deviation_nonzero_entries
                ),
                "complement": "D_2=2q I_24-P_2",
                "left_product": "D_2 P_2=q^2 I_24",
                "right_product": "P_2 D_2=q^2 I_24",
                "exact_polynomial_defect": 0,
            },
            "aligned_characteristic_data": {
                "covector": "(omega,kappa,0,0)",
                "determinant": str(self.aligned_determinant),
                "future_null_rank": self.future_null_rank,
                "past_null_rank": self.past_null_rank,
                "globalization": (
                    "SO(3) aligns every nonzero spatial covector; homogeneity "
                    "covers the two nonzero null orbits"
                ),
            },
            "univariate_smith_ledger": {
                "unit_factors": units,
                "q_factors": waves,
                "q_squared_factors": biwaves,
                "interpretation": {
                    "algebraic": units,
                    "wave": waves,
                    "biwave": biwaves,
                },
                "derivation": (
                    "D_2P_2=q^2I bounds every invariant-factor exponent by 2; "
                    "null rank 6 and det(P_2)=q^24 fix multiplicities 6,12,6"
                ),
                "global_unimodular_transform_constructed": False,
            },
            "field_and_cotangent_blocks": {
                "field": "the displayed identity",
                "cotangent": "formal-adjoint copy has the same invariant factors",
            },
            "support_local_symbol_candidate": {
                "D_2_order": 2,
                "contains_inverse_covector": False,
                "contains_spectral_projector": False,
            },
            "lower_order_completion": {
                "literal_frozen_candidate": "D_naive=2qI-P",
                "commutative_normal_frame_remainder_nonzero_counts_by_order_0_to_4": list(
                    self.frozen_lower_defect_counts
                ),
                "sample_nonzero_coefficients_orders_0_1_2": list(
                    self.frozen_lower_defect_witnesses
                ),
                "quadratic_remainder_rank_at_future_and_past_null_covectors": list(
                    self.frozen_quadratic_null_ranks
                ),
                "orders_3_and_4_cancel": True,
                "interpretation": (
                    "the exact principal complement does not by itself supply the "
                    "curved lower-order complementary operator; curvature "
                    "commutators and correction coefficients remain to be solved"
                ),
                "narrow_frozen_ansatz_obstruction": (
                    "the rank-12 quadratic remainder on q=0 is not q times a "
                    "zeroth-order matrix, so the literal commutative normal-frame "
                    "candidate does not factor into two wave operators having "
                    "zero first-order symbols; this is not a no-go for corrected "
                    "first-order factors or the full covariant composition"
                ),
                "lower_order_operator_factorization_proved": False,
            },
            "outcome": {
                "principal_symbol_obstruction_to_mixed_order_route": False,
                "mixed_order_prenormal_symbol_exact": True,
                "support_local_block_triangularization_constructed": False,
                "mixed_order_green_realization": False,
                "curved_operator_identity_promoted": False,
            },
            "sha256": {
                "hessian_cache": self.hessian_cache_sha256,
                "gauge_generator": self.gauge_generator_sha256,
                "gauge_companion": self.gauge_companion_sha256,
                "field_pairing": self.field_pairing_sha256,
                "P_2": self.principal_sha256,
                "D_2": self.complement_sha256,
                "naive_lower_remainder": self.frozen_lower_defect_sha256,
            },
            "theorem_boundary": (
                "the two open auxiliary field/cotangent blocks have an exact "
                "mixed algebraic-wave-biwave prenormal principal symbol.  No "
                "curved complementary operator, global local Smith transform, "
                "causal Green inverse, or BV Green homotopy is inferred"
            ),
        }
