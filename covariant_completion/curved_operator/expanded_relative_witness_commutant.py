"""Coefficientwise SO(3) audit for every relative witness block.

The incidence-only expanded-relative certificate records the expected
rotation multiplicities of the sixteen mapping-cylinder blocks.  This module
replaces that ledger by the actual infinitesimal rotation matrices in the
project's component bases and solves every relevant intertwiner equation

``G_target T - T G_source = 0``

over the rationals.  It also checks the concrete pair-(1,6) temporal
coefficients used by :mod:`expanded_relative_witness_scalar_completion`.
This is a representation/leading-coefficient certificate only; it does not
assemble a Douglis symbol or promote a Green-theoretic flag.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from .expanded_relative_witness import SO3_MULTIPLICITIES
from .expanded_relative_witness_scalar_completion import (
    ExpandedRelativeScalarCompletion,
)
from .conventions import CurvedBVConventions
from .invariant_pairings import InvariantFibrePairingAnsatz, _rotation_generators
from .relative_saddle_witness import PRIMARY_RELATIVE_ENTRIES
from .weyl_3plus1 import stf_basis


EXPECTED_BLOCK_SIZES = (9, 24, 24, 9, 26, 40, 14, 26, 40, 14, 14, 40, 26, 14, 40, 26)
EXPECTED_HOM_DIMENSIONS = (4, 18, 4, 36, 14, 14, 22, 36, 14)


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _stf_generator(spatial_rotation: sp.Matrix) -> sp.Matrix:
    basis = stf_basis()
    gram = sp.Matrix(
        [
            [sum(left[i, j] * right[i, j] for i in range(3) for j in range(3))
             for right in basis]
            for left in basis
        ]
    )
    inverse = gram.inv()
    result = sp.zeros(5)
    for column, tensor in enumerate(basis):
        image = spatial_rotation * tensor + tensor * spatial_rotation.T
        result[:, column] = inverse * sp.Matrix(
            [sum(item[i, j] * image[i, j] for i in range(3) for j in range(3))
             for item in basis]
        )
    return result


def _direct_sum(*blocks: sp.Matrix) -> sp.Matrix:
    return sp.diag(*blocks)


def _curvature_generators() -> tuple[
    tuple[sp.Matrix, ...], tuple[sp.Matrix, ...], tuple[sp.Matrix, ...]
]:
    state: list[sp.Matrix] = []
    identity: list[sp.Matrix] = []
    equation: list[sp.Matrix] = []
    for rotation in _rotation_generators():
        vector = rotation[1:, 1:]
        stf = _stf_generator(vector)
        state_generator = _direct_sum(stf, stf, stf, stf, vector, vector)
        identity_generator = _direct_sum(
            vector, vector, vector, vector, sp.zeros(1), sp.zeros(1)
        )
        state.append(state_generator)
        identity.append(identity_generator)
        equation.append(_direct_sum(state_generator, identity_generator))
    return tuple(state), tuple(equation), tuple(identity)


def _block_generators() -> tuple[tuple[sp.Matrix, ...], ...]:
    auxiliary = InvariantFibrePairingAnsatz.build()
    state, equation, identity = _curvature_generators()
    primal = (
        auxiliary.ghost_generators,
        auxiliary.field_generators,
        auxiliary.field_generators,
        auxiliary.ghost_generators,
        state,
        equation,
        identity,
        state,
        equation,
        identity,
    )
    dual = tuple(
        tuple(-generator.T for generator in primal[index])
        for index in (9, 8, 7, 9, 8, 7)
    )
    result = primal + dual
    if tuple(generators[0].rows for generators in result) != EXPECTED_BLOCK_SIZES:
        raise AssertionError("rotation block-size ledger drifted")
    return result


def _casimir_spectrum(generators: tuple[sp.Matrix, ...]) -> tuple[tuple[int, int], ...]:
    size = generators[0].rows
    casimir = -sum((generator * generator for generator in generators), sp.zeros(size))
    if casimir * (casimir - 2 * sp.eye(size)) * (casimir - 6 * sp.eye(size)) != sp.zeros(size):
        raise AssertionError("a block contains a non-spin-0/1/2 rotation module")
    return tuple(sorted((int(value), int(multiplicity)) for value, multiplicity in casimir.eigenvals().items()))


def _commutant_matrix(
    target: tuple[sp.Matrix, ...], source: tuple[sp.Matrix, ...]
) -> sp.SparseMatrix:
    target_size = target[0].rows
    source_size = source[0].rows
    entries: dict[tuple[int, int], sp.Expr] = {}
    for generator_index, (target_generator, source_generator) in enumerate(
        zip(target, source, strict=True)
    ):
        offset = generator_index * target_size * source_size
        for output in range(target_size):
            target_nonzero = [
                (middle, target_generator[output, middle])
                for middle in range(target_size)
                if target_generator[output, middle] != 0
            ]
            for input_ in range(source_size):
                equation = offset + input_ * target_size + output
                for middle, value in target_nonzero:
                    variable = input_ * target_size + middle
                    entries[(equation, variable)] = entries.get((equation, variable), 0) + value
                for middle in range(source_size):
                    value = source_generator[middle, input_]
                    if value != 0:
                        variable = middle * target_size + output
                        entries[(equation, variable)] = entries.get((equation, variable), 0) - value
    clean = {key: sp.expand(value) for key, value in entries.items() if sp.expand(value) != 0}
    return sp.SparseMatrix(
        3 * target_size * source_size,
        target_size * source_size,
        clean,
    )


def _intertwining_defect(
    target: tuple[sp.Matrix, ...],
    coefficient: sp.Matrix,
    source: tuple[sp.Matrix, ...],
) -> int:
    return sum(
        int(value != 0)
        for target_generator, source_generator in zip(target, source, strict=True)
        for value in (target_generator * coefficient - coefficient * source_generator)
    )


@dataclass(frozen=True)
class ExpandedRelativeWitnessCommutant:
    block_generators: tuple[tuple[sp.Matrix, ...], ...]
    block_casimir_spectra: tuple[tuple[tuple[int, int], ...], ...]
    commutant_shapes: tuple[tuple[int, int], ...]
    commutant_sha256: tuple[str, ...]
    commutant_ranks: tuple[int, ...]
    commutant_dimensions: tuple[int, ...]
    r1_defect: int
    r6_sharp_defect: int
    generator_defect: int
    identity_sharp_defect: int
    numerator_defect: int
    scalar_diagonal_defect: int

    @staticmethod
    def build() -> "ExpandedRelativeWitnessCommutant":
        generators = _block_generators()
        spectra = tuple(_casimir_spectrum(block) for block in generators)
        shapes: list[tuple[int, int]] = []
        equation_hashes: list[str] = []
        ranks: list[int] = []
        dimensions: list[int] = []
        for target_index, source_index in PRIMARY_RELATIVE_ENTRIES:
            equations = _commutant_matrix(
                generators[target_index], generators[source_index]
            )
            rank = DomainMatrix.from_Matrix(equations).rank()
            shapes.append(equations.shape)
            equation_hashes.append(_digest(equations))
            ranks.append(rank)
            dimensions.append(equations.cols - rank)

        completion = ExpandedRelativeScalarCompletion.build()
        # Pair 1: X_Eq# -> G_aux.  Pair 6 sharp: M_aux -> X_Id#.
        r1_defect = _intertwining_defect(
            generators[0], completion.relative_r1_temporal, generators[11]
        )
        r6_defect = _intertwining_defect(
            generators[10], completion.relative_r6_sharp_temporal, generators[1]
        )
        temporal_generator = CurvedBVConventions.build().gauge_generator.derivative_coefficients[0]
        generator_defect = _intertwining_defect(
            generators[1], temporal_generator, generators[0]
        )
        identity_sharp_defect = _intertwining_defect(
            generators[11],
            completion.curvature_identity_sharp_temporal,
            generators[10],
        )
        numerator_defect = _intertwining_defect(
            generators[1], completion.relative_pair16_product, generators[1]
        )
        scalar_defect = _intertwining_defect(
            generators[1], completion.gauge_scalar_diagonal, generators[1]
        )
        result = ExpandedRelativeWitnessCommutant(
            block_generators=generators,
            block_casimir_spectra=spectra,
            commutant_shapes=tuple(shapes),
            commutant_sha256=tuple(equation_hashes),
            commutant_ranks=tuple(ranks),
            commutant_dimensions=tuple(dimensions),
            r1_defect=r1_defect,
            r6_sharp_defect=r6_defect,
            generator_defect=generator_defect,
            identity_sharp_defect=identity_sharp_defect,
            numerator_defect=numerator_defect,
            scalar_diagonal_defect=scalar_defect,
        )
        result.verify()
        return result

    def verify(self) -> None:
        expected_spectra = tuple(
            tuple(
                (spin * (spin + 1), multiplicity * (2 * spin + 1))
                for spin, multiplicity in enumerate(multiplicities)
                if multiplicity
            )
            for multiplicities in SO3_MULTIPLICITIES
        )
        if self.block_casimir_spectra != expected_spectra:
            raise AssertionError("coefficientwise Casimir decomposition drifted")
        if self.commutant_dimensions != EXPECTED_HOM_DIMENSIONS:
            raise AssertionError("coefficientwise relative Hom dimensions drifted")
        if any(
            rank + dimension != shape[1]
            for shape, rank, dimension in zip(
                self.commutant_shapes,
                self.commutant_ranks,
                self.commutant_dimensions,
                strict=True,
            )
        ):
            raise AssertionError("commutant rank-nullity failed")
        if (
            self.r1_defect,
            self.r6_sharp_defect,
            self.generator_defect,
            self.identity_sharp_defect,
            self.numerator_defect,
            self.scalar_diagonal_defect,
        ) != (0, 0, 0, 0, 0, 0):
            raise AssertionError("pair-(1,6) rotation intertwining failed")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-expanded-relative-witness-commutant-v1",
            "rotation_generators": {
                "count_per_block": 3,
                "block_sizes": list(EXPECTED_BLOCK_SIZES),
                "coordinatewise_exact_rational": True,
                "dual_blocks_use_contragredient_generators": True,
                "sha256_by_block": [
                    [_digest(generator) for generator in block]
                    for block in self.block_generators
                ],
                "casimir_spectra_by_block": [
                    {str(value): multiplicity for value, multiplicity in spectrum}
                    for spectrum in self.block_casimir_spectra
                ],
            },
            "relative_Hom_commutants": {
                "primary_entries": [list(entry) for entry in PRIMARY_RELATIVE_ENTRIES],
                "equation_shapes": [list(shape) for shape in self.commutant_shapes],
                "equation_sha256": list(self.commutant_sha256),
                "ranks": list(self.commutant_ranks),
                "nullities": list(self.commutant_dimensions),
                "total_dimension": sum(self.commutant_dimensions),
                "expected_ledger_recovered": list(EXPECTED_HOM_DIMENSIONS),
                "all_three_generator_equations_solved": True,
            },
            "pair_1_plus_6_coefficients": {
                "R1_XEqSharp_to_Gaux_intertwining_defect": self.r1_defect,
                "R6sharp_Maux_to_XIdSharp_intertwining_defect": self.r6_sharp_defect,
                "K_temporal_Gaux_to_Maux_intertwining_defect": self.generator_defect,
                "NcurvSharp_temporal_XIdSharp_to_XEqSharp_intertwining_defect": self.identity_sharp_defect,
                "numerator_projector_endomorphism_defect": self.numerator_defect,
                "retained_scalar_diagonal_endomorphism_defect": self.scalar_diagonal_defect,
                "coefficientwise_SO3_intertwiners": True,
            },
            "outcome": {
                "hardcoded_multiplicity_ledger_replaced": True,
                "complete_relative_Hom_dimension": sum(self.commutant_dimensions),
                "pair16_numerator_equivariant": True,
                "full_Douglis_symbol_assembled": False,
                "green_realization_proved": False,
                "flag_promoted": False,
            },
            "theorem_boundary": (
                "actual component-basis rotation generators recover the complete "
                "162-dimensional relative Hom family and the displayed pair-(1,6) "
                "temporal numerator maps are exact intertwiners.  This does not "
                "supply the missing curvature inverse, arbitrary-covector Douglis "
                "symbol, symmetrizer, Green operator, or causal homotopy"
            ),
            "fail_closed": True,
        }
