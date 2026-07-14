"""Factor the polarized field pairing into matter and residual ghost parts."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from bridge.residual_bfv import (
    CoefficientCEComplex,
    ConformalCE,
    columns_to_matrix,
)
from bridge.transfer import (
    energy_two_metric_form,
    energy_two_symmetric_module,
    normalized_kernel_basis,
    symmetric_square_form,
)
from field_bv_identification.polarized_state.polarized_complex import (
    PolarizedStateComplex,
)


def _unit_e_primary_norm() -> sp.Expr:
    """Direct action-normalized lower-TT norm at the primary energy."""

    time = sp.symbols("t", real=True)
    j = sp.Integer(1)
    frequency = 2 * j
    normalization = 1 / (4 * sp.sqrt(j * (2 * j + 1)))
    mode = normalization * sp.exp(-sp.I * frequency * time)
    barred = sp.conjugate(mode)
    gamma = -sp.Integer(1)
    omega_l = 2 * j + 2

    def momenta(value: sp.Expr):
        p1 = gamma * sp.diff(value, time, 2)
        p0 = -gamma * (frequency**2 + omega_l**2) * sp.diff(value, time)
        p0 -= gamma * sp.diff(value, time, 3)
        return sp.simplify(p0), sp.simplify(p1)

    p0, p1 = momenta(mode)
    p0_bar, p1_bar = momenta(barred)
    omega = (
        p0_bar * mode
        + p1_bar * sp.diff(mode, time)
        - p0 * barred
        - p1 * sp.diff(barred, time)
    )
    return sp.simplify(-sp.I * omega)


def _energy_two_isometry(form: sp.Matrix) -> sp.Matrix:
    """Exact map from a unit normalized primary basis to the raw basis."""

    lower, diagonal = form.LDLdecomposition(hermitian=False)
    inverse_sqrt = sp.diag(
        *(sp.simplify(1 / sp.sqrt(diagonal[index, index])) for index in range(form.rows))
    )
    result = sp.simplify(lower.T.inv() * inverse_sqrt)
    if sp.simplify(result.T * form * result) != sp.eye(form.rows):
        raise AssertionError("energy-two field/raw isometry failed")
    return sp.Matrix(result)


@dataclass(frozen=True)
class PolarizedPairingTransfer:
    state: PolarizedStateComplex
    energy_two_field_to_raw: sp.Matrix
    direct_primary_norm: sp.Expr
    matter_form: sp.Matrix
    ghost_norm: sp.Expr
    raw_kernel_gram: sp.Matrix
    normalized_field_gram: sp.Matrix

    @classmethod
    def build(cls, maximum_energy: int = 4) -> "PolarizedPairingTransfer":
        state = PolarizedStateComplex.build(maximum_energy)
        raw = state.form.raw
        j2 = energy_two_metric_form(raw)
        field_to_raw = _energy_two_isometry(j2)
        primary_norm = _unit_e_primary_norm()

        ce = ConformalCE.build()
        two_module = energy_two_symmetric_module(raw)
        complex_ = CoefficientCEComplex(ce, two_module)
        source = complex_.basis(4, 0)
        target = complex_.basis(5, 0)
        differential = complex_.differential(source, target)
        matrix = columns_to_matrix(differential, len(target))
        kernel = sp.Matrix.hstack(*matrix.nullspace())
        matter = symmetric_square_form(j2)
        normalized, raw_gram = normalized_kernel_basis(kernel, matter)
        ghost_norm = ce.polarized_pair(ce.lowering_ghosts, ce.lowering_ghosts)
        field_gram = sp.simplify(
            normalized.T * matter * normalized * ghost_norm
        )

        result = cls(
            state=state,
            energy_two_field_to_raw=field_to_raw,
            direct_primary_norm=primary_norm,
            matter_form=matter,
            ghost_norm=ghost_norm,
            raw_kernel_gram=sp.Matrix(raw_gram),
            normalized_field_gram=sp.Matrix(field_gram),
        )
        result.verify()
        return result

    def verify(self) -> None:
        j2 = self.state.form.forms[2]
        if self.direct_primary_norm != 1:
            raise AssertionError("action-normalized E primary does not have unit norm")
        if (
            self.energy_two_field_to_raw.T
            * j2
            * self.energy_two_field_to_raw
            != sp.eye(10)
        ):
            raise AssertionError("lowest-energy field/raw scalar is inconsistent")
        if self.state.induced_positive_form != self.state.form.block_diagonal_form():
            raise AssertionError("phase-space polarization did not induce J_raw")
        if self.ghost_norm != 1:
            raise AssertionError("oriented BFV/CE ghost factor is not one")
        if self.state.transgression.ghost_volume_orientation != 1:
            raise AssertionError("BFV cotangent orientation disagrees with CE volume")
        if self.normalized_field_gram != sp.eye(2):
            raise AssertionError("field-theoretic residual Gram matrix is not I2")
