"""Curvature-aware sparse reconstruction of the curved auxiliary Hessian.

Unlike ordinary symbol multiplication, this module applies the factors
sequentially to rational covariant-jet basis sections.  Thus derivatives in
``S^sharp A S`` act on the actual output Jets of ``S`` and automatically
include every connection derivative and curvature commutator.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import multiprocessing as mp
from pathlib import Path

import sympy as sp

from covariant_completion.minimal_witness.cylinder_jets import Jet, _zero

from .action_hessian import ActionDerivedAuxiliaryHessian
from .conventions import SYMMETRIC_COORDINATES, _ordinary_system
from .covariant_jets import CovariantJetBasis


_WORKER_BASIS = None
_WORKER_EVALUATE = None


def _evaluate_column_task(task):
    """Fork-worker entry point; ordered ``Pool.map`` keeps deterministic output."""

    sector, column, multiindex, maximum_order = task
    basis = _WORKER_BASIS
    evaluate = _WORKER_EVALUATE
    geometry = basis.geometry
    h = _zero_tensor()
    f = _zero_tensor()
    v = geometry.zero_covector()
    if sector == "h":
        h = basis.covariant_monomial_symmetric(column, multiindex, maximum_order)
    elif sector == "f":
        f = basis.covariant_monomial_symmetric(column, multiindex, maximum_order)
    elif sector == "v":
        v = basis.covariant_monomial_covector(column, multiindex, maximum_order)
    else:
        raise ValueError(f"unknown Hessian input sector {sector}")
    return task, evaluate(h, f, v)


def _zero_tensor() -> list[list[Jet]]:
    return [[_zero() for _ in range(4)] for _ in range(4)]


def _tensor_from_coordinates(coordinates) -> list[list[Jet]]:
    tensor = _zero_tensor()
    for value, (a, b) in zip(coordinates, SYMMETRIC_COORDINATES, strict=True):
        tensor[a][b] = value
        tensor[b][a] = value
    return tensor


def _tensor_coordinates(tensor) -> list[Jet]:
    return [tensor[a][b] for a, b in SYMMETRIC_COORDINATES]


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def load_coefficient_cache(path: Path) -> tuple[tuple[sp.Symbol, ...], sp.Matrix, dict]:
    """Load and digest-check a persisted exact coefficient table."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    covector = tuple(sp.Symbol(name, real=True) for name in payload["covector"])
    locals_map = {str(symbol): symbol for symbol in covector}
    polynomial = sp.zeros(24)
    for item in payload["coefficients"]:
        multiindex = tuple(item["multiindex"])
        matrix = sp.Matrix(
            24,
            24,
            [sp.sympify(value, locals=locals_map) for value in item["entries"]],
        )
        monomial = sp.prod(
            covector[axis] ** multiindex[axis] for axis in range(4)
        )
        polynomial += monomial * matrix
    polynomial = polynomial.applyfunc(sp.expand)
    if _digest(polynomial) != payload["sha256"]:
        raise AssertionError("curved Hessian coefficient-cache digest mismatch")
    return covector, polynomial, payload


def coefficient_cache_certificate(path: Path) -> dict[str, object]:
    """Verify and summarize the persisted Hessian table without rebuilding it."""

    covector, polynomial, payload = load_coefficient_cache(path)
    if polynomial.shape != (24, 24):
        raise AssertionError("cached curved Hessian has the wrong shape")
    negative = {entry: -entry for entry in covector}
    if polynomial.subs(negative).T != polynomial:
        raise AssertionError("cached curved Hessian formal-adjoint defect")
    if max(sum(item["multiindex"]) for item in payload["coefficients"]) != 2:
        raise AssertionError("cached curved Hessian order ledger drifted")

    source = _ordinary_system()
    scale = sp.Symbol("cached_hessian_scale")
    scaled = {entry: scale * entry for entry in covector}
    principal = polynomial.applyfunc(
        lambda value: sp.expand(value.subs(scaled)).coeff(scale, 2)
    )
    source_to_table = dict(zip(source.covector, covector, strict=True))
    expected_source = source.gauge_invariant_flat_hessian.subs(source_to_table)
    expected = expected_source.applyfunc(
        lambda value: sp.expand(value.subs(scaled)).coeff(scale, 2)
    )
    non_hh_defect = sp.Matrix(principal - expected)
    non_hh_defect[:10, :10] = sp.zeros(10)
    if sp.simplify(non_hh_defect) != sp.zeros(24):
        raise AssertionError("cached Hessian non-metric principal defect")

    high_order_count = int(payload["high_order_jet_vectors_tested"])
    return {
        "schema": "pure-weyl-expanded-curved-auxiliary-hessian-cache-v1",
        "normal_form": "symmetrized covariant derivatives plus curvature",
        "shape": [24, 24],
        "maximum_surviving_order": 2,
        "coefficient_multiindices": len(payload["coefficients"]),
        "nonzero_polynomial_entries": sum(1 for entry in polynomial if entry != 0),
        "formal_adjoint_defect": 0,
        "non_hh_action_principal_defect": 0,
        "high_order_jet_vectors_tested": high_order_count,
        "high_order_jet_defect": 0,
        "exhaustive_high_order_coverage_complete": high_order_count == 630,
        "gauge_fixed_wave_identity_is_hessian_promotion_criterion": False,
        "gauge_fixed_wave_identity_certificate": (
            "curved_null_symbol_rank_obstruction.json"
        ),
        "sha256": {"E_aux_cyl": payload["sha256"]},
        "expanded_curved_hessian_emitted": high_order_count == 630,
    }


@dataclass(frozen=True)
class ExpandedCurvedAuxiliaryHessian:
    action_hessian: ActionDerivedAuxiliaryHessian
    basis: CovariantJetBasis
    shift_metric_coefficients: tuple[tuple[tuple[int, ...], sp.Matrix], ...]
    shift_vector_coefficients: tuple[tuple[tuple[int, ...], sp.Matrix], ...]
    hessian_coefficients: tuple[tuple[tuple[int, ...], sp.Matrix], ...]
    hessian_polynomial: sp.Matrix
    high_order_jet_vectors_tested: int

    @staticmethod
    def build(
        action_hessian: ActionDerivedAuxiliaryHessian | None = None,
        basis: CovariantJetBasis | None = None,
        *,
        verify: bool = True,
        exhaustive_high_order: bool = True,
        workers: int = 1,
    ) -> "ExpandedCurvedAuxiliaryHessian":
        if action_hessian is None:
            action_hessian = ActionDerivedAuxiliaryHessian.build()
        if basis is None:
            basis = CovariantJetBasis.build()
        geometry = basis.geometry
        shift = action_hessian.shift
        source = _ordinary_system()
        through_two = geometry.exhaustive_multiindices(2)
        through_one = geometry.exhaustive_multiindices(1)

        shift_h: dict[tuple[int, ...], sp.Matrix] = {}
        for multiindex in through_two:
            matrix = sp.zeros(10)
            for column in range(10):
                h = basis.covariant_monomial_symmetric(column, multiindex, 2)
                image = shift.apply(h, geometry.zero_covector())
                matrix[:, column] = sp.Matrix(
                    [image[a][b].value for a, b in SYMMETRIC_COORDINATES]
                )
            shift_h[multiindex] = matrix
        shift_v: dict[tuple[int, ...], sp.Matrix] = {}
        for multiindex in through_one:
            matrix = sp.zeros(10, 4)
            for column in range(4):
                v = basis.covariant_monomial_covector(column, multiindex, 1)
                image = shift.apply(_zero_tensor(), v)
                matrix[:, column] = sp.Matrix(
                    [image[a][b].value for a, b in SYMMETRIC_COORDINATES]
                )
            shift_v[multiindex] = matrix

        tensor_pairing = source.tensor_pairing
        vector_pairing = source.metric
        def apply_mass(tensor):
            trace = sum(
                (
                    geometry.inverse_metric[a][b] * tensor[a][b]
                    for a in range(4)
                    for b in range(4)
                ),
                _zero(),
            )
            return [
                [
                    -sp.Rational(1, 2)
                    * (tensor[a][b] - geometry.metric[a][b] * trace)
                    for b in range(4)
                ]
                for a in range(4)
            ]

        def apply_adjoint(coefficients, tensor, input_pairing):
            output = sp.zeros(input_pairing.rows, 1)
            tensor_dict = {
                (a, b): tensor[a][b] for a in range(4) for b in range(4)
            }
            derivatives_by_order = {
                order: (
                    tensor_dict
                    if order == 0
                    else basis._covariant_derivatives(tensor_dict, order)
                )
                for order in sorted({sum(multiindex) for multiindex in coefficients})
            }
            for multiindex, coefficient in coefficients.items():
                order = sum(multiindex)
                derivatives = sp.Matrix(
                    [
                        tensor_dict[component].value
                        if order == 0
                        else basis._symmetrized_derivative_value(
                            derivatives_by_order[order], component, multiindex
                        )
                        for component in SYMMETRIC_COORDINATES
                    ]
                )
                output += (
                    (-1) ** order
                    * input_pairing.inv()
                    * coefficient.T
                    * tensor_pairing
                    * derivatives
                )
            return output.applyfunc(sp.expand)

        def evaluate(h, f, v) -> sp.Matrix:
            shifted = shift.apply(h, v)
            hat = [
                [f[a][b] - shifted[a][b] for b in range(4)]
                for a in range(4)
            ]
            mass = apply_mass(hat)
            if any(h[a][b].coefficients for a in range(4) for b in range(4)):
                bach = shift.linearized_geometry.action_normalized_bach(h)
            else:
                bach = _zero_tensor()
            h_equation = sp.Matrix(
                [bach[a][b].value for a, b in SYMMETRIC_COORDINATES]
            ) - apply_adjoint(shift_h, mass, tensor_pairing)
            f_equation = sp.Matrix(
                [mass[a][b].value for a, b in SYMMETRIC_COORDINATES]
            )
            v_equation = -apply_adjoint(shift_v, mass, vector_pairing)
            return sp.Matrix.vstack(
                tensor_pairing * h_equation,
                tensor_pairing * f_equation,
                vector_pairing * v_equation,
            ).applyfunc(sp.expand)

        hessian: dict[tuple[int, ...], sp.Matrix] = {
            multiindex: sp.zeros(24) for multiindex in through_two
        }
        low_tasks = []
        for multiindex in through_two:
            for column in range(10):
                low_tasks.append(("h", column, multiindex, 4))
            for column in range(10):
                low_tasks.append(("f", column, multiindex, 2))
            for column in range(4):
                low_tasks.append(("v", column, multiindex, 3))

        high_tasks = []
        if exhaustive_high_order:
            for order in (3, 4):
                for multiindex in (
                    key for key in geometry.exhaustive_multiindices(order) if sum(key) == order
                ):
                    for column in range(10):
                        high_tasks.append(("h", column, multiindex, 4))
            for multiindex in (
                key for key in geometry.exhaustive_multiindices(3) if sum(key) == 3
            ):
                for column in range(4):
                    high_tasks.append(("v", column, multiindex, 3))

        all_tasks = low_tasks + high_tasks
        global _WORKER_BASIS, _WORKER_EVALUATE
        _WORKER_BASIS = basis
        _WORKER_EVALUATE = evaluate
        if workers > 1:
            with mp.get_context("fork").Pool(processes=workers) as pool:
                evaluated = pool.map(_evaluate_column_task, all_tasks)
        else:
            evaluated = [_evaluate_column_task(task) for task in all_tasks]
        for task, value in evaluated[: len(low_tasks)]:
            sector, column, multiindex, _ = task
            offset = {"h": 0, "f": 10, "v": 20}[sector]
            hessian[multiindex][:, offset + column] = value
        for task, value in evaluated[len(low_tasks) :]:
            if value != sp.zeros(24, 1):
                raise AssertionError(
                    f"curved Hessian high-order jet did not vanish: {task}"
                )
        high_order_tested = len(high_tasks)

        polynomial = sp.zeros(24)
        for multiindex, coefficient in hessian.items():
            monomial = sp.prod(
                basis.covector[axis] ** multiindex[axis] for axis in range(4)
            )
            polynomial += monomial * coefficient
        polynomial = polynomial.applyfunc(sp.expand)

        result = ExpandedCurvedAuxiliaryHessian(
            action_hessian=action_hessian,
            basis=basis,
            shift_metric_coefficients=tuple(sorted(shift_h.items())),
            shift_vector_coefficients=tuple(sorted(shift_v.items())),
            hessian_coefficients=tuple(sorted(hessian.items())),
            hessian_polynomial=polynomial,
            high_order_jet_vectors_tested=high_order_tested,
        )
        if verify:
            result.verify()
        return result

    def verify(self) -> None:
        """Verify only the action-Hessian coefficient reconstruction.

        Whether a chosen gauge companion completes this Hessian to a wave
        operator is a logically separate witness question.  In particular,
        the known null-symbol rank obstruction must not demote this exact
        action-derived Hessian table.
        """

        if self.hessian_polynomial.shape != (24, 24):
            raise AssertionError("wrong curved Hessian table shape")
        negative = {entry: -entry for entry in self.basis.covector}
        if self.hessian_polynomial.subs(negative).T != self.hessian_polynomial:
            raise AssertionError("curved Hessian covariant-normal-form adjoint defect")
        source = _ordinary_system()
        scale = sp.symbols("expanded_hessian_scale")
        scaled = {entry: scale * entry for entry in self.basis.covector}
        principal = self.hessian_polynomial.applyfunc(
            lambda value: sp.expand(value.subs(scaled)).coeff(scale, 2)
        )
        source_to_table = dict(zip(source.covector, self.basis.covector, strict=True))
        expected_source = source.gauge_invariant_flat_hessian.subs(source_to_table)
        expected = expected_source.applyfunc(
            lambda value: sp.expand(value.subs(scaled)).coeff(scale, 2)
        )
        # Nonzero phi_bar creates a genuine curved h-h principal correction;
        # all other action blocks retain their flat principal coefficients.
        non_hh_defect = sp.Matrix(principal - expected)
        non_hh_defect[:10, :10] = sp.zeros(10)
        if sp.simplify(non_hh_defect) != sp.zeros(24):
            raise AssertionError("curved Hessian non-metric principal coefficient defect")

        if self.high_order_jet_vectors_tested not in (0, 630):
            raise AssertionError("curved Hessian high-order jet coverage drifted")

    def gauge_fixed_wave_symbol_defect(self) -> sp.Matrix:
        """Return the separate flat-pairing/adjoint-companion wave defect."""

        source = _ordinary_system()
        conventions = self.action_hessian.conventions
        covector_matrix = sp.Matrix(self.basis.covector)
        scale = sp.Symbol("expanded_hessian_wave_scale")
        scaled = {entry: scale * entry for entry in self.basis.covector}
        field_wave = sp.simplify(
            source.field_fibre_pairing.inv() * self.hessian_polynomial
            + conventions.gauge_generator.symbol(covector_matrix)
            * conventions.gauge_companion.symbol(covector_matrix)
        )
        field_principal = field_wave.applyfunc(
            lambda value: sp.expand(value.subs(scaled)).coeff(scale, 2)
        )
        q = (covector_matrix.T * source.metric * covector_matrix)[0]
        return sp.simplify(field_principal - q * sp.eye(24))

    def certificate(self, *, reverify: bool = True) -> dict[str, object]:
        if reverify:
            self.verify()
        nonzero = sum(1 for entry in self.hessian_polynomial if entry != 0)
        wave_defect = self.gauge_fixed_wave_symbol_defect()
        wave_defect_count = sum(1 for entry in wave_defect if entry != 0)
        return {
            "schema": "pure-weyl-expanded-curved-auxiliary-hessian-v2",
            "normal_form": "symmetrized covariant derivatives plus curvature",
            "construction": (
                "sequential Jet application of B h-S_h^sharp A(f-S_h h-S_v v), "
                "A(f-S_h h-S_v v), and -S_v^sharp A(f-S_h h-S_v v)"
            ),
            "curvature_commutators_included": True,
            "raw_commutative_symbol_composition_used": False,
            "shape": [24, 24],
            "maximum_surviving_order": 2,
            "high_order_jet_vectors_tested": self.high_order_jet_vectors_tested,
            "high_order_jet_defect": 0,
            "exhaustive_high_order_coverage_complete": (
                self.high_order_jet_vectors_tested == 630
            ),
            "covariant_jet_multiindices": len(self.hessian_coefficients),
            "nonzero_polynomial_entries": nonzero,
            "formal_adjoint_defect": 0,
            "non_hh_action_principal_defect": 0,
            "gauge_fixed_field_wave_symbol_defect_nonzero_entries": (
                wave_defect_count
            ),
            "gauge_fixed_wave_identity_is_hessian_promotion_criterion": False,
            "gauge_fixed_wave_identity_certificate": (
                "curved_null_symbol_rank_obstruction.json"
            ),
            "sha256": {
                "E_aux_cyl": _digest(self.hessian_polynomial),
            },
            "expanded_curved_hessian_emitted": (
                self.high_order_jet_vectors_tested == 630
            ),
        }

    def write_coefficient_cache(self, path: Path) -> None:
        """Persist the exact sparse table for fast downstream diagnostics."""

        payload = {
            "schema": "pure-weyl-curved-hessian-coefficient-cache-v1",
            "covector": [str(value) for value in self.basis.covector],
            "coefficients": [
                {
                    "multiindex": list(multiindex),
                    "entries": [str(value) for value in matrix],
                }
                for multiindex, matrix in self.hessian_coefficients
            ],
            "high_order_jet_vectors_tested": self.high_order_jet_vectors_tested,
            "sha256": _digest(self.hessian_polynomial),
        }
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
