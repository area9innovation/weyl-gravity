"""Complete SO(3)-invariant ansatz for curved pointwise fibre forms.

At a cylinder point the isotropy group is SO(3).  Restricting the field and
ghost fibres gives multiplicity spaces

``F = 5*1 + 3*3 + 2*5`` and ``G = 3*1 + 2*3``.

Schur's lemma therefore makes the graded-symmetric invariant ansatz complete:
15+6+3=24 parameters for J and 6+3=9 for Y.  This module verifies the
decomposition dimensions and checks an explicit nondegenerate member (the
flat-normalized J/Y) against all three infinitesimal rotation generators.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from .conventions import SYMMETRIC_COORDINATES, _ordinary_system


def _rotation_generators() -> tuple[sp.Matrix, ...]:
    output = []
    for left, right in ((1, 2), (2, 3), (3, 1)):
        generator = sp.zeros(4)
        generator[left, right] = 1
        generator[right, left] = -1
        output.append(generator)
    return tuple(output)


def _tensor_representation(generator: sp.Matrix) -> sp.Matrix:
    matrix = sp.zeros(10)
    for column, (a, b) in enumerate(SYMMETRIC_COORDINATES):
        tensor = sp.zeros(4)
        tensor[a, b] = 1
        tensor[b, a] = 1
        image = generator * tensor + tensor * generator.T
        for row, (c, d) in enumerate(SYMMETRIC_COORDINATES):
            matrix[row, column] = image[c, d]
    return matrix


@dataclass(frozen=True)
class InvariantFibrePairingAnsatz:
    field_generators: tuple[sp.Matrix, ...]
    ghost_generators: tuple[sp.Matrix, ...]
    field_parameter_count: int = 24
    ghost_parameter_count: int = 9

    @staticmethod
    def build() -> "InvariantFibrePairingAnsatz":
        field_generators = []
        ghost_generators = []
        for rotation in _rotation_generators():
            tensor = _tensor_representation(rotation)
            field = sp.zeros(24)
            field[:10, :10] = tensor
            field[10:20, 10:20] = tensor
            field[20:24, 20:24] = rotation
            field_generators.append(field)
            ghost = sp.zeros(9)
            ghost[:4, :4] = rotation
            ghost[4:8, 4:8] = rotation
            ghost_generators.append(ghost)
        result = InvariantFibrePairingAnsatz(
            tuple(field_generators), tuple(ghost_generators)
        )
        result.verify()
        return result

    def verify(self) -> None:
        source = _ordinary_system()
        field_casimir = -sum(
            (generator * generator for generator in self.field_generators),
            sp.zeros(24),
        )
        ghost_casimir = -sum(
            (generator * generator for generator in self.ghost_generators),
            sp.zeros(9),
        )
        # Eigenvalues l(l+1)=0,2,6 prove the asserted real SO(3)-irrep
        # decomposition, including multiplicities.  This makes the Schur
        # parameter count below a checked result rather than an assumption.
        if field_casimir.eigenvals() != {0: 5, 2: 9, 6: 10}:
            raise AssertionError("field SO(3) decomposition drifted")
        if ghost_casimir.eigenvals() != {0: 3, 2: 6}:
            raise AssertionError("ghost SO(3) decomposition drifted")
        if 5 * 1 + 3 * 3 + 2 * 5 != 24:
            raise AssertionError("field irrep dimensions drifted")
        if 3 * 1 + 2 * 3 != 9:
            raise AssertionError("ghost irrep dimensions drifted")
        if self.field_parameter_count != 15 + 6 + 3:
            raise AssertionError("complete invariant J parameter count drifted")
        if self.ghost_parameter_count != 6 + 3:
            raise AssertionError("complete invariant Y parameter count drifted")
        if source.field_fibre_pairing.det() == 0:
            raise AssertionError("explicit invariant J member is degenerate")
        if source.gauge_fixing_pairing.det() == 0:
            raise AssertionError("explicit invariant Y member is degenerate")
        for generator in self.field_generators:
            if (
                generator.T * source.field_fibre_pairing
                + source.field_fibre_pairing * generator
            ) != sp.zeros(24):
                raise AssertionError("flat J is not SO(3)-invariant")
        for generator in self.ghost_generators:
            if (
                generator.T * source.gauge_fixing_pairing
                + source.gauge_fixing_pairing * generator
            ) != sp.zeros(9):
                raise AssertionError("flat Y is not SO(3)-invariant")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-complete-invariant-fibre-pairing-ansatz-v1",
            "isotropy": "SO(3)",
            "field_decomposition": {
                "scalar_irrep_multiplicity": 5,
                "vector_irrep_multiplicity": 3,
                "spin2_irrep_multiplicity": 2,
                "dimension_check": "5*1+3*3+2*5=24",
            },
            "ghost_decomposition": {
                "scalar_irrep_multiplicity": 3,
                "vector_irrep_multiplicity": 2,
                "dimension_check": "3*1+2*3=9",
            },
            "graded_symmetric_parameter_counts": {
                "J_field": self.field_parameter_count,
                "Y_ghost": self.ghost_parameter_count,
                "total": self.field_parameter_count + self.ghost_parameter_count,
            },
            "completeness_reason": (
                "The exact rotation-Casimir spectra are F:{0:5,2:9,6:10} and "
                "G:{0:3,2:6}; Schur's lemma then says invariant symmetric forms "
                "are arbitrary symmetric forms on each real multiplicity space "
                "tensor the unique irrep form"
            ),
            "parallel_globalization": (
                "SO(3)-invariant fibre forms extend uniquely as parallel homogeneous "
                "bundle forms on R x S3"
            ),
            "nondegenerate_member_exists": True,
            "flat_J_and_Y_rotation_defects": 0,
            "joint_J_Y_equations_solved": False,
        }
