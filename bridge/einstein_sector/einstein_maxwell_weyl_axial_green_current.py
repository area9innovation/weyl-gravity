"""Exact off-shell local Green currents for the generic axial operator."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import _generic_rows


ROOT = Path(__file__).resolve().parents[2]
OPERATOR_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_green_current.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_green_current.schema.json"


class AxialGreenCurrentError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialGreenCurrentError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zero(matrix: sp.MatrixBase) -> bool:
    return matrix.applyfunc(lambda value: sp.factor(sp.expand(value))) == sp.zeros(matrix.rows, matrix.cols)


def _differential_operators() -> tuple[sp.Matrix, sp.Matrix, dict[str, sp.Symbol]]:
    rows, symbols = _generic_rows()
    eigenvalue, momentum, frequency = symbols["lambda"], symbols["k"], symbols["omega"]
    temporal, spatial = sp.symbols("T X", commutative=True)
    coefficients = sp.Matrix([symbols["h_t"], symbols["h_x"], symbols["q_t"], symbols["q_x"]])
    fourier = sp.Matrix(
        [
            eigenvalue * rows["metric_t"],
            -eigenvalue * rows["metric_x"],
            rows["maxwell_t"],
            rows["maxwell_x"],
        ]
    ).jacobian(coefficients)
    reduced = fourier.subs(
        {frequency: sp.I * temporal, momentum: -sp.I * spatial}, simultaneous=True
    ).applyfunc(lambda value: sp.factor(sp.expand(value)))
    projection = sp.Matrix(
        [
            [1, 0, -temporal / 2, 0, 0, 0],
            [0, 1, -spatial / 2, 0, 0, 0],
            [0, 0, temporal / 2, 1, 0, -temporal],
            [0, 0, spatial / 2, 0, 1, -spatial],
        ]
    )
    projection_adjoint = projection.subs(
        {temporal: -temporal, spatial: -spatial}, simultaneous=True
    ).T
    ungauged = (projection_adjoint * reduced * projection).applyfunc(
        lambda value: sp.factor(sp.expand(value))
    )
    _require(
        _zero(reduced - reduced.subs({temporal: -temporal, spatial: -spatial}, simultaneous=True).T),
        "reduced differential operator lost formal self-adjointness",
    )
    _require(
        _zero(ungauged - ungauged.subs({temporal: -temporal, spatial: -spatial}, simultaneous=True).T),
        "ungauged differential operator lost formal self-adjointness",
    )
    return reduced, ungauged, {"lambda": eigenvalue, "T": temporal, "X": spatial}


JetKey = tuple[int, int, int, int, int, int]


def _coefficient_matrices(operator: sp.Matrix, temporal: sp.Symbol, spatial: sp.Symbol) -> dict[tuple[int, int], sp.Matrix]:
    matrices: dict[tuple[int, int], sp.Matrix] = {}
    for row in range(operator.rows):
        for column in range(operator.cols):
            polynomial = sp.Poly(sp.expand(operator[row, column]), temporal, spatial)
            for (time_order, space_order), coefficient in polynomial.terms():
                matrices.setdefault((time_order, space_order), sp.zeros(operator.rows))
                matrices[(time_order, space_order)][row, column] += coefficient
    for (time_order, space_order), matrix in matrices.items():
        sign = (-1) ** (time_order + space_order)
        _require(_zero(matrix.T - sign * matrix), f"coefficient adjoint parity failed at {(time_order, space_order)}")
    return matrices


def _add(store: dict[JetKey, sp.Expr], key: JetKey, value: sp.Expr) -> None:
    if value != 0:
        store[key] = sp.factor(store[key] + value)
        if store[key] == 0:
            del store[key]


def _green_terms(operator: sp.Matrix, temporal: sp.Symbol, spatial: sp.Symbol) -> dict[str, Any]:
    matrices = _coefficient_matrices(operator, temporal, spatial)
    time_current: dict[JetKey, sp.Expr] = defaultdict(lambda: sp.S.Zero)
    space_current: dict[JetKey, sp.Expr] = defaultdict(lambda: sp.S.Zero)
    rhs: dict[JetKey, sp.Expr] = defaultdict(lambda: sp.S.Zero)
    for (time_order, space_order), matrix in matrices.items():
        for left in range(operator.rows):
            for right in range(operator.cols):
                coefficient = sp.factor(matrix[left, right])
                if coefficient == 0:
                    continue
                _add(rhs, (left, 0, 0, right, time_order, space_order), coefficient)
                _add(rhs, (right, time_order, space_order, left, 0, 0), -coefficient)
                for index in range(time_order):
                    _add(
                        time_current,
                        (left, index, 0, right, time_order - 1 - index, space_order),
                        (-1) ** index * coefficient,
                    )
                for index in range(space_order):
                    _add(
                        space_current,
                        (left, time_order, index, right, 0, space_order - 1 - index),
                        (-1) ** (time_order + index) * coefficient,
                    )

    divergence: dict[JetKey, sp.Expr] = defaultdict(lambda: sp.S.Zero)
    for (left, ut, ux, right, vt, vx), coefficient in time_current.items():
        _add(divergence, (left, ut + 1, ux, right, vt, vx), coefficient)
        _add(divergence, (left, ut, ux, right, vt + 1, vx), coefficient)
    for (left, ut, ux, right, vt, vx), coefficient in space_current.items():
        _add(divergence, (left, ut, ux + 1, right, vt, vx), coefficient)
        _add(divergence, (left, ut, ux, right, vt, vx + 1), coefficient)
    all_keys = set(rhs) | set(divergence)
    remainder = {
        key: sp.factor(divergence.get(key, 0) - rhs.get(key, 0))
        for key in all_keys
        if sp.factor(divergence.get(key, 0) - rhs.get(key, 0)) != 0
    }
    _require(remainder == {}, "off-shell Green identity failed on jet coefficients")

    def serialize(store: dict[JetKey, sp.Expr]) -> list[dict[str, Any]]:
        return [
            {
                "u_component": key[0],
                "u_t_order": key[1],
                "u_x_order": key[2],
                "v_component": key[3],
                "v_t_order": key[4],
                "v_x_order": key[5],
                "coefficient": str(sp.factor(value)),
            }
            for key, value in sorted(store.items())
        ]

    return {
        "operator_order": max(sum(order) for order in matrices),
        "nonzero_operator_monomials": len(matrices),
        "time_current_terms": serialize(time_current),
        "space_current_terms": serialize(space_current),
        "time_current_term_count": len(time_current),
        "space_current_term_count": len(space_current),
        "jet_identity_remainder": [],
        "off_shell_identity_verified": True,
    }


def build_certificate() -> dict[str, Any]:
    parent = json.loads(OPERATOR_CERTIFICATE.read_text(encoding="utf-8"))
    _require(parent["result_id"] == "EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR", "parent operator changed")
    reduced, ungauged, symbols = _differential_operators()
    reduced_current = _green_terms(reduced, symbols["T"], symbols["X"])
    ungauged_current = _green_terms(ungauged, symbols["T"], symbols["X"])
    return {
        "schema": "einstein-maxwell-weyl-axial-green-current-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_GREEN_CURRENT",
        "result_state": "GENERIC_AXIAL_REDUCED_AND_UNGAUGED_OFF_SHELL_LOCAL_GREEN_IDENTITIES_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_GENERIC_AXIAL_LOCAL_GREEN_CURRENT",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "input": {"path": str(OPERATOR_CERTIFICATE.relative_to(ROOT)), "sha256": _sha256(OPERATOR_CERTIFICATE)},
        },
        "domain": "generic axial ell>=2 harmonic coefficient jets on the local (t,x) base, symbolic lambda, before final residual quotient",
        "convention": {
            "Fourier_to_differential": "omega=i*partial_t and k=-i*partial_x for exp(i(kx-omega t))",
            "identity": "partial_t J^t(u,v)+partial_x J^x(u,v)=u^T L v-(L u)^T v",
            "jet_term_order": ["u_component", "u_t_order", "u_x_order", "v_component", "v_t_order", "v_x_order"],
            "construction": "coefficientwise multivariate Lagrange identity, telescoped first in t and then in x",
        },
        "reduced_current": {"field_order": ["H_t", "H_x", "Q_t", "Q_x"], **reduced_current},
        "ungauged_current": {"field_order": ["h_t", "h_x", "h_2", "q_t", "q_x", "b"], **ungauged_current},
        "classification": {
            "reduced_off_shell_local_Green_identity": True,
            "ungauged_off_shell_local_Green_identity": True,
            "arbitrary_off_shell_jets": True,
            "dispersion_or_equations_of_motion_used": False,
            "direct_four_dimensional_action_Hessian": False,
            "Lee_Wald_pairing_or_particle_claim": False,
            "Lorentzian_causal_claim": False,
        },
        "interpretation": "The generic axial operator now has an explicit local bilinear Green current on the two-dimensional harmonic base, both after gauge contraction and on the six-field ungauged lift. This closes the off-shell integration-by-parts rail but does not yet identify the current with the directly varied four-dimensional Lee-Wald current or assign a norm to the extra module.",
        "next_gate": "match this local concomitant to the direct four-dimensional action Hessian and Lee-Wald current, then evaluate the complete Einstein/extra pairing matrix",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE certificate proves a local off-shell Green identity for the exact harmonic coefficient operator. It does not construct Green functions, causal propagators, a Hadamard state, a covariant phase-space norm, or a particle spectrum.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_green_current --verify bridge/certificates/einstein_maxwell_weyl_axial_green_current.json",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_green_current",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text(encoding="utf-8")) == build_certificate(), f"stale Green-current certificate: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and args.verify is None:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
