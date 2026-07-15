"""Exact flat-space TT reduction of the linearized Bach tensor.

The computation uses the geometric convention

    B_mn = partial^r partial^s C_m r n s

on a flat four-dimensional background of signature ``(-,+,+,+)``.  A
two-polarization TT plane-wave ansatz is kept off shell, so the result derives
the operator rather than testing it only on solutions.
"""

from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge" / "certificates" / "flat_tt_bach_operator.json"
DIMENSION = 4


class FlatTTBachError(RuntimeError):
    """Raised when an exact tensor identity fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FlatTTBachError(message)


def _matrix_rows(matrix: sp.MatrixBase) -> list[list[str]]:
    return [
        [str(sp.factor(matrix[row, column])) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def _tensor_nonzero(tensor: sp.MutableDenseNDimArray) -> dict[str, str]:
    result: dict[str, str] = {}
    for indices in product(range(DIMENSION), repeat=tensor.rank()):
        value = sp.factor(tensor[indices])
        if value != 0:
            result["".join(str(index) for index in indices)] = str(value)
    return result


def build_certificate() -> dict[str, Any]:
    eta = sp.diag(-1, 1, 1, 1)
    inverse = eta
    frequency, wave_number = sp.symbols("omega k", real=True)
    plus, cross = sp.symbols("h_plus h_cross")
    derivative = sp.Matrix([frequency, 0, 0, wave_number])
    raised_derivative = inverse * derivative
    box_symbol = sp.factor((derivative.T * inverse * derivative)[0])

    metric_perturbation = sp.MutableDenseNDimArray.zeros(DIMENSION, DIMENSION)
    metric_perturbation[1, 1] = plus
    metric_perturbation[2, 2] = -plus
    metric_perturbation[1, 2] = cross
    metric_perturbation[2, 1] = cross

    trace = sp.factor(
        sum(
            inverse[first, second] * metric_perturbation[first, second]
            for first in range(DIMENSION)
            for second in range(DIMENSION)
        )
    )
    divergence = sp.Matrix(
        [
            sp.factor(
                sum(
                    raised_derivative[first] * metric_perturbation[first, second]
                    for first in range(DIMENSION)
                )
            )
            for second in range(DIMENSION)
        ]
    )
    _require(trace == 0, "TT ansatz is not trace-free")
    _require(divergence == sp.zeros(DIMENSION, 1), "TT ansatz is not transverse")

    # R_(m n r s) = 1/2(d_r d_n h_ms + d_s d_m h_nr
    #                         - d_s d_n h_mr - d_r d_m h_ns).
    riemann = sp.MutableDenseNDimArray.zeros(*(DIMENSION,) * 4)
    for mu, nu, rho, sigma in product(range(DIMENSION), repeat=4):
        riemann[mu, nu, rho, sigma] = sp.expand(
            (
                derivative[rho] * derivative[nu] * metric_perturbation[mu, sigma]
                + derivative[sigma]
                * derivative[mu]
                * metric_perturbation[nu, rho]
                - derivative[sigma]
                * derivative[nu]
                * metric_perturbation[mu, rho]
                - derivative[rho]
                * derivative[mu]
                * metric_perturbation[nu, sigma]
            )
            / 2
        )

    ricci = sp.MutableDenseNDimArray.zeros(DIMENSION, DIMENSION)
    for mu, nu in product(range(DIMENSION), repeat=2):
        ricci[mu, nu] = sp.factor(
            sum(
                inverse[rho, sigma] * riemann[rho, mu, sigma, nu]
                for rho in range(DIMENSION)
                for sigma in range(DIMENSION)
            )
        )
    scalar = sp.factor(
        sum(
            inverse[mu, nu] * ricci[mu, nu]
            for mu in range(DIMENSION)
            for nu in range(DIMENSION)
        )
    )
    _require(scalar == 0, "linearized scalar curvature does not vanish in TT gauge")
    _require(
        all(
            sp.factor(
                ricci[mu, nu] + box_symbol * metric_perturbation[mu, nu] / 2
            )
            == 0
            for mu, nu in product(range(DIMENSION), repeat=2)
        ),
        "linearized Ricci tensor is not -Box h/2",
    )

    weyl = sp.MutableDenseNDimArray.zeros(*(DIMENSION,) * 4)
    for mu, rho, nu, sigma in product(range(DIMENSION), repeat=4):
        weyl[mu, rho, nu, sigma] = sp.factor(
            riemann[mu, rho, nu, sigma]
            - (
                eta[mu, nu] * ricci[sigma, rho]
                - eta[mu, sigma] * ricci[nu, rho]
                - eta[rho, nu] * ricci[sigma, mu]
                + eta[rho, sigma] * ricci[nu, mu]
            )
            / 2
            + scalar
            * (
                eta[mu, nu] * eta[sigma, rho]
                - eta[mu, sigma] * eta[nu, rho]
            )
            / 6
        )

    weyl_trace = sp.Matrix(
        DIMENSION,
        DIMENSION,
        lambda mu, nu: sp.factor(
            sum(
                inverse[rho, sigma] * weyl[mu, rho, nu, sigma]
                for rho in range(DIMENSION)
                for sigma in range(DIMENSION)
            )
        ),
    )
    _require(weyl_trace == sp.zeros(DIMENSION), "linearized Weyl tensor has a trace")

    bach = sp.MutableDenseNDimArray.zeros(DIMENSION, DIMENSION)
    for mu, nu in product(range(DIMENSION), repeat=2):
        bach[mu, nu] = sp.factor(
            sum(
                raised_derivative[rho]
                * raised_derivative[sigma]
                * weyl[mu, rho, nu, sigma]
                for rho in range(DIMENSION)
                for sigma in range(DIMENSION)
            )
        )

    expected_bach = sp.MutableDenseNDimArray.zeros(DIMENSION, DIMENSION)
    for mu, nu in product(range(DIMENSION), repeat=2):
        expected_bach[mu, nu] = sp.factor(
            -box_symbol**2 * metric_perturbation[mu, nu] / 4
        )
    _require(
        all(
            sp.factor(bach[mu, nu] - expected_bach[mu, nu]) == 0
            for mu, nu in product(range(DIMENSION), repeat=2)
        ),
        "flat TT Bach tensor is not -Box^2 h/4",
    )

    polarization_operator = sp.eye(2) * sp.factor(-box_symbol**2 / 4)
    helicity_generator = sp.Matrix([[0, 2], [-2, 0]])
    _require(
        polarization_operator * helicity_generator
        == helicity_generator * polarization_operator,
        "flat TT Bach operator does not preserve both helicities",
    )

    return {
        "schema": "pure-weyl-flat-tt-bach-operator-v1",
        "result_id": "FLAT_TT_LINEARIZED_BACH_OPERATOR",
        "result_state": "PROVED",
        "source_commit": "439a8e6bcc42a2458a7e1adf96ff0a5bb0dcac78",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "background": {
            "dimension": 4,
            "metric": "diag(-1,1,1,1)",
            "derivative_covector": ["omega", "0", "0", "k"],
            "box_symbol": str(box_symbol),
        },
        "gauge_hypotheses": {
            "trace": str(trace),
            "divergence": [str(value) for value in divergence],
            "polarizations": ["h_plus=h_11=-h_22", "h_cross=h_12=h_21"],
            "off_shell": True,
        },
        "curvature_identities": {
            "linearized_scalar": str(scalar),
            "linearized_ricci": "Ric_1=-Box h_TT/2",
            "weyl_trace_matrix": _matrix_rows(weyl_trace),
        },
        "bach_convention": "B_mn=partial^r partial^s C_m r n s on flat space",
        "operator_identity": "B_1(h_TT)=-(1/4) Box^2 h_TT",
        "polarization_operator": _matrix_rows(polarization_operator),
        "helicity_generator": _matrix_rows(helicity_generator),
        "helicity_commutator_zero": True,
        "nonzero_bach_components": _tensor_nonzero(bach),
        "equation_consequence": "B_1=0 iff Box^2 h_TT=0",
        "normalization_guard": (
            "an action Euler-Lagrange tensor may rescale this geometric Bach tensor; "
            "any nonzero overall rescaling leaves the kernel unchanged"
        ),
        "assumptions": [
            "flat four-dimensional background",
            "signature (-,+,+,+)",
            "trace-free and transverse reduced metric perturbation",
            "commuting formal derivatives evaluated off shell",
        ],
        "not_proved": [
            "TT reduced physical block only",
            "not a complete gauge-fixed BV operator",
            "not a null-infinity falloff or support theorem",
        ],
        "verification_command": (
            "python3 -m bridge.einstein_sector.flat_tt_bach --verify "
            "bridge/certificates/flat_tt_bach_operator.json"
        ),
    }


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"certificate is stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(
            json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
