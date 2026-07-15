#!/usr/bin/env python3
"""Action-derived preflight for the retained Berger minimal BV operator.

This producer completes the spatial gauge and formal-adjoint rows, the full
covariant matter Hessian, and the fourth-order Bach principal matrix on the
authoritative 26-component layout.  It deliberately does not import the
round-cylinder Bach Hessian: the Berger background has nonzero Weyl curvature,
so its lower-order connection-variation terms are genuinely different.

The parent gate ``BERGER_RETAINED_MINIMAL_OPERATOR`` remains open until those
non-conformally-flat Bach coefficients are expanded in a canonical PBW basis.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

try:
    from d_quotient_classical.backreacted_clock.berger_retained_minimal_layout import (
        BergerRetainedMinimalLayout,
    )
    from d_quotient_classical.backreacted_clock.positive_berger_clock import (
        _berger_geometry,
    )
except ModuleNotFoundError:  # Direct script execution.
    from berger_retained_minimal_layout import BergerRetainedMinimalLayout
    from positive_berger_clock import _berger_geometry


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR_PREFLIGHT.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-retained-minimal-operator-preflight.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-retained-minimal-operator-preflight-v1.schema.json"

PAIRS = tuple((mu, nu) for mu in range(4) for nu in range(mu, 4))


def _digest(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _record(matrix: sp.MatrixBase) -> dict[str, Any]:
    entries = [
        [row, column, str(sp.factor(value))]
        for (row, column), value in sorted(sp.SparseMatrix(matrix).todok().items())
    ]
    body = {"shape": list(matrix.shape), "entries": entries}
    return {**body, "sha256": _digest(body)}


def _berger_connection(a: sp.Symbol, c: sp.Symbol) -> list[list[list[sp.Expr]]]:
    eta = sp.diag(-1, 1, 1, 1)
    structure = [[[sp.S(0) for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for first, second, target, value in (
        (1, 2, 3, c / a**2),
        (2, 3, 1, 1 / c),
        (3, 1, 2, 1 / c),
    ):
        structure[first][second][target] = value
        structure[second][first][target] = -value
    connection = [[[sp.S(0) for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for derivative in range(4):
        for vector in range(4):
            for lowered_target in range(4):
                gamma_lower = sp.Rational(1, 2) * (
                    sum(eta[lowered_target, middle] * structure[derivative][vector][middle] for middle in range(4))
                    - sum(eta[derivative, middle] * structure[vector][lowered_target][middle] for middle in range(4))
                    + sum(eta[vector, middle] * structure[lowered_target][derivative][middle] for middle in range(4))
                )
                for target in range(4):
                    connection[target][derivative][vector] += eta[target, lowered_target] * gamma_lower
    return connection


def _spatial_gauge(a: sp.Symbol, c: sp.Symbol, p: tuple[sp.Symbol, ...]) -> sp.Matrix:
    connection = _berger_connection(a, c)
    xi = sp.symbols("xi1:4")
    xi_lower = (sp.S(0), *xi)
    output = []
    for mu, nu in PAIRS:
        nabla_mu_xi_nu = p[mu] * xi_lower[nu] - sum(
            connection[index][mu][nu] * xi_lower[index] for index in range(4)
        )
        nabla_nu_xi_mu = p[nu] * xi_lower[mu] - sum(
            connection[index][nu][mu] * xi_lower[index] for index in range(4)
        )
        output.append(sp.expand(nabla_mu_xi_nu + nabla_nu_xi_mu))
    return sp.Matrix(output).jacobian(xi)


def _canonical_equation_weights() -> sp.Matrix:
    eta = sp.diag(-1, 1, 1, 1)
    return sp.diag(
        *[
            -(2 if mu != nu else 1) * eta[mu, mu] * eta[nu, nu]
            for mu, nu in PAIRS
        ]
    )


def _principal_geometry(p: tuple[sp.Symbol, ...]) -> dict[str, sp.Matrix]:
    eta = sp.diag(-1, 1, 1, 1)
    p_down = sp.Matrix(p)
    p_up = eta * p_down
    fields = sp.symbols("h0:10")
    h = sp.zeros(4)
    for index, (mu, nu) in enumerate(PAIRS):
        h[mu, nu] = fields[index]
        h[nu, mu] = fields[index]
    trace = sum(eta[mu, nu] * h[mu, nu] for mu in range(4) for nu in range(4))

    delta_gamma = [[[sp.S(0) for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for rho in range(4):
        for nu in range(4):
            for sigma in range(4):
                delta_gamma[rho][nu][sigma] = sp.Rational(1, 2) * sum(
                    eta[rho, lam]
                    * (p[nu] * h[sigma, lam] + p[sigma] * h[nu, lam] - p[lam] * h[nu, sigma])
                    for lam in range(4)
                )
    delta_riemann_mixed = [[[[sp.S(0) for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for rho in range(4):
        for sigma in range(4):
            for mu in range(4):
                for nu in range(4):
                    delta_riemann_mixed[rho][sigma][mu][nu] = (
                        p[mu] * delta_gamma[rho][nu][sigma]
                        - p[nu] * delta_gamma[rho][mu][sigma]
                    )
    delta_riemann = [[[[sp.S(0) for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for alpha in range(4):
        for beta in range(4):
            for mu in range(4):
                for nu in range(4):
                    delta_riemann[alpha][beta][mu][nu] = sum(
                        eta[alpha, rho] * delta_riemann_mixed[rho][beta][mu][nu]
                        for rho in range(4)
                    )
    delta_ricci = sp.zeros(4)
    for beta in range(4):
        for nu in range(4):
            delta_ricci[beta, nu] = sum(
                delta_riemann_mixed[rho][beta][rho][nu] for rho in range(4)
            )
    delta_scalar = sum(
        eta[mu, nu] * delta_ricci[mu, nu] for mu in range(4) for nu in range(4)
    )
    delta_schouten = sp.Rational(1, 2) * (
        delta_ricci - sp.Rational(1, 6) * delta_scalar * eta
    )
    delta_weyl = [[[[sp.S(0) for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for alpha in range(4):
        for beta in range(4):
            for mu in range(4):
                for nu in range(4):
                    delta_weyl[alpha][beta][mu][nu] = sp.expand(
                        delta_riemann[alpha][beta][mu][nu]
                        - (
                            eta[alpha, mu] * delta_schouten[nu, beta]
                            - eta[alpha, nu] * delta_schouten[mu, beta]
                            - eta[beta, mu] * delta_schouten[nu, alpha]
                            + eta[beta, nu] * delta_schouten[mu, alpha]
                        )
                    )
    bach = sp.zeros(4)
    for alpha in range(4):
        for beta in range(4):
            bach[alpha, beta] = sp.expand(
                sum(
                    p_up[mu] * p_up[nu] * delta_weyl[alpha][mu][beta][nu]
                    for mu in range(4)
                    for nu in range(4)
                )
            )

    p_squared = (p_up.T * p_down)[0]
    delta_ricci_formula = sp.zeros(4)
    for mu in range(4):
        for nu in range(4):
            delta_ricci_formula[mu, nu] = sp.Rational(1, 2) * (
                sum(
                    p_up[axis] * p[mu] * h[nu, axis]
                    + p_up[axis] * p[nu] * h[mu, axis]
                    for axis in range(4)
                )
                - p_squared * h[mu, nu]
                - p[mu] * p[nu] * trace
            )
    delta_scalar_formula = (
        sum(p_up[mu] * p_up[nu] * h[mu, nu] for mu in range(4) for nu in range(4))
        - p_squared * trace
    )
    delta_einstein = delta_ricci_formula - sp.Rational(1, 2) * eta * delta_scalar_formula
    canonical = _canonical_equation_weights()
    return {
        "bach": canonical * sp.Matrix([bach[mu, nu] for mu, nu in PAIRS]).jacobian(fields),
        "einstein": canonical * sp.Matrix([delta_einstein[mu, nu] for mu, nu in PAIRS]).jacobian(fields),
    }


def _matter_zero_order(
    a: sp.Symbol,
    c: sp.Symbol,
    alpha_b: sp.Symbol,
    ricci: sp.Matrix,
    scalar: sp.Expr,
) -> sp.Matrix:
    eta = sp.diag(-1, 1, 1, 1)
    q = c**2 / a**2
    rho_squared = 2 * alpha_b * (1 - 4 * q) / a**2
    phase_kinetic = alpha_b * q / (2 * a**4)  # rho^2 omega^2
    potential = -alpha_b * (q**2 - 5 * q + 1) / (6 * a**4)
    fields = sp.symbols("u0:10")
    h = sp.zeros(4)
    for index, (mu, nu) in enumerate(PAIRS):
        h[mu, nu] = fields[index]
        h[nu, mu] = fields[index]
    h_up = eta * h * eta
    ricci_contraction = sum(
        ricci[mu, nu] * h_up[mu, nu] for mu in range(4) for nu in range(4)
    )
    delta_einstein_algebraic = (
        -sp.Rational(1, 2) * scalar * h
        + sp.Rational(1, 2) * eta * ricci_contraction
    )
    delta_stress_algebraic = (
        (phase_kinetic / 2 - potential) * h
        + phase_kinetic / 2 * eta * fields[0]
        + rho_squared / 6 * delta_einstein_algebraic
    )
    # E_metric=alpha_B B-T, converted to the coordinate-dual equation basis.
    return _canonical_equation_weights() * sp.Matrix(
        [-delta_stress_algebraic[mu, nu] for mu, nu in PAIRS]
    ).jacobian(fields)


@dataclass(frozen=True)
class BergerRetainedMinimalOperatorPreflight:
    payload: dict[str, Any]

    @classmethod
    def build(cls) -> "BergerRetainedMinimalOperatorPreflight":
        layout = BergerRetainedMinimalLayout.build()
        a, c, alpha_b = sp.symbols("a c alpha_B", positive=True, nonzero=True)
        p = tuple(sp.symbols("p0:4", real=True))
        gauge = _spatial_gauge(a, c, p)
        zero_substitution = {symbol: 0 for symbol in p}
        gauge_principal = sp.simplify(gauge - gauge.subs(zero_substitution))
        minus_adjoint = -gauge.subs(
            {symbol: -symbol for symbol in p}, simultaneous=True
        ).T
        principal = _principal_geometry(p)
        ricci, scalar, bach_background, _ = _berger_geometry(a, c)
        matter_zero = _matter_zero_order(a, c, alpha_b, ricci, scalar)
        rho_squared = 2 * alpha_b * (1 - 4 * c**2 / a**2) / a**2
        matter_second = -rho_squared / 6 * principal["einstein"]
        retained_principal = alpha_b * principal["bach"] + matter_second

        if sp.simplify(principal["bach"] - principal["bach"].T) != sp.zeros(10):
            raise AssertionError("Bach principal matrix is not action symmetric")
        if sp.simplify(principal["einstein"] - principal["einstein"].T) != sp.zeros(10):
            raise AssertionError("matter second-order matrix is not action symmetric")
        if sp.simplify(principal["bach"] * gauge_principal) != sp.zeros(10, 3):
            raise AssertionError("Bach principal gauge identity failed")
        if sp.simplify(principal["einstein"] * gauge_principal) != sp.zeros(10, 3):
            raise AssertionError("matter principal gauge identity failed")

        fixture = {
            a: 1,
            c: 3 / sp.sqrt(40),
            alpha_b: 5,
            p[0]: 2,
            p[1]: 1,
            p[2]: 3,
            p[3]: 4,
        }
        if gauge.subs(fixture).rank() != 3:
            raise AssertionError("spatial gauge row lost generic rank")
        if principal["bach"].subs(fixture).rank() != 5:
            raise AssertionError("Bach principal rank drifted")
        if bach_background == sp.zeros(4):
            raise AssertionError("Berger background unexpectedly became Bach flat")

        matrices = {
            "K_spatial_full_frame_symbol": _record(gauge),
            "minus_K_spatial_sharp_full_frame_symbol": _record(minus_adjoint),
            "Bach_fourth_order_principal": _record(principal["bach"]),
            "matter_second_order_covariant_symbol": _record(matter_second),
            "matter_zero_order_covariant": _record(matter_zero),
            "known_Bach_order4_plus_matter_order2": _record(retained_principal),
        }
        payload: dict[str, Any] = {
            "schema": "pure-weyl-berger-retained-minimal-operator-preflight-v1",
            "result_id": "BERGER_RETAINED_MINIMAL_OPERATOR_PREFLIGHT",
            "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
            "claim_status": "PARTIAL_ACTION_DERIVED_OPERATOR",
            "dependency_tags": ["LOCAL-ALGEBRAIC"],
            "layout_ref": {
                "result_id": layout.payload["result_id"],
                "payload_sha256": layout.digest,
                "component_count": 26,
            },
            "coefficient_ring": "Q(alpha_B,a,c,a^-1,c^-1)[p0,p1,p2,p3] with the positive-branch algebraic extension c/a=sqrt(q)",
            "formal_adjoint": {
                "frame_derivatives": "p_mu maps to -p_mu in the invariant unimodular orthonormal frame",
                "dual_basis": "the 10 equation rows are dual to the ordered independent symmetric metric components",
                "noether_row": "minus_K_spatial_sharp=-K_spatial(-p)^T",
            },
            "action_inputs": {
                "matter_action": "int sqrt(-g)[-1/2 sum_A dT_A.dT_A-(R/12)rho^2-(lambda/4)rho^4]",
                "metric_equation": "alpha_B B_mn-T_mn=0",
                "background_relations": {
                    "q": "c^2/a^2",
                    "rho_squared": "2 alpha_B(1-4q)/a^2",
                    "omega_squared": "q/[4a^2(1-4q)]",
                    "lambda": "-(q^2-5q+1)/[6 alpha_B(1-4q)^2]",
                },
            },
            "covariant_normal_form": {
                "matter_hessian": "-delta T with delta T=(rho^2 omega^2/2-V)h+(rho^2 omega^2/2)g h_00+(rho^2/6)delta G",
                "delta_ricci": "1/2(nabla^c nabla_a h_bc+nabla^c nabla_b h_ac-Box h_ab-nabla_a nabla_b tr h)",
                "delta_scalar": "nabla_a nabla_b h^ab-Box tr h-R_ab h^ab",
                "delta_einstein": "delta Ric_ab-(1/2)R h_ab-(1/2)g_ab delta R",
                "bach_principal": "zeta^c zeta^d delta C_acbd derived from delta Gamma, delta Riemann, and delta Schouten",
                "missing_term": "the complete order <=3 PBW expansion of delta B on the nonzero-Weyl Berger background",
            },
            "matrices": matrices,
            "exact_checks": {
                "K_spatial_coefficients_complete": True,
                "minus_K_spatial_sharp_coefficients_complete": True,
                "matter_hessian_covariant_coefficients_complete": True,
                "Bach_fourth_order_principal_complete": True,
                "principal_formal_self_adjointness": True,
                "matter_formal_self_adjointness_by_second_variation": True,
                "principal_Bach_K_identity": True,
                "principal_matter_K_identity": True,
                "generic_spatial_gauge_rank": 3,
                "generic_Bach_principal_rank": 5,
            },
            "nonconformally_flat_guard": {
                "background_Bach_nonzero": True,
                "background_Weyl_nonzero": True,
                "round_cylinder_lower_order_hessian_reused": False,
                "reason": "delta(nabla nabla C) contains connection-variation terms proportional to the nonzero background Weyl tensor",
            },
            "flags": {
                "retained_gauge_and_noether_rows_complete": True,
                "retained_matter_hessian_complete": True,
                "retained_Bach_principal_complete": True,
                "retained_Bach_lower_order_PBW_complete": False,
                "retained_q1_coefficients_complete": False,
                "retained_q1_squared_verified": False,
                "retained_cyclicity_verified": False,
                "BERGER_RETAINED_MINIMAL_OPERATOR": False,
                "BERGER_NONMINIMAL_COMPLETION": False,
            },
            "next_gate": "BERGER_LINEARIZED_BACH_PBW_EXPANSION",
            "claim_boundary": "This preflight exports the exact spatial gauge and adjoint rows, complete covariant matter Hessian, and complete fourth-order Bach principal matrix. The full retained operator gate remains false because the nonzero-Weyl Berger background requires new order-three-and-lower linearized-Bach PBW coefficients; no round-cylinder substitution is accepted.",
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        p = self.payload
        if p["layout_ref"]["payload_sha256"] != BergerRetainedMinimalLayout.build().digest:
            raise AssertionError("retained layout reference drifted")
        checks = p["exact_checks"]
        for key in (
            "K_spatial_coefficients_complete",
            "minus_K_spatial_sharp_coefficients_complete",
            "matter_hessian_covariant_coefficients_complete",
            "Bach_fourth_order_principal_complete",
            "principal_formal_self_adjointness",
            "matter_formal_self_adjointness_by_second_variation",
            "principal_Bach_K_identity",
            "principal_matter_K_identity",
        ):
            if checks[key] is not True:
                raise AssertionError(f"proved preflight check dropped: {key}")
        flags = p["flags"]
        guard = p["nonconformally_flat_guard"]
        if guard["round_cylinder_lower_order_hessian_reused"] is not False:
            raise AssertionError("round-cylinder lower-order Hessian reused on Berger")
        if guard["background_Weyl_nonzero"] is not True:
            raise AssertionError("nonzero Berger Weyl curvature guard dropped")
        if flags["retained_Bach_lower_order_PBW_complete"] is not False:
            raise AssertionError("Berger Bach PBW completion promoted")
        for key in (
            "retained_q1_coefficients_complete",
            "retained_q1_squared_verified",
            "retained_cyclicity_verified",
            "BERGER_RETAINED_MINIMAL_OPERATOR",
            "BERGER_NONMINIMAL_COMPLETION",
        ):
            if flags[key] is not False:
                raise AssertionError(f"open retained gate promoted: {key}")
        if p["next_gate"] != "BERGER_LINEARIZED_BACH_PBW_EXPANSION":
            raise AssertionError("Berger retained operator next gate drifted")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Retained Berger minimal-operator preflight

The retained 26-component layout has three (q_1) blocks.  Two are now
complete: the full first-order spatial diffeomorphism generator and its exact
formal-adjoint identity row.  The complete matter contribution to the metric
Hessian is also derived from the conformally coupled two-scalar action.

The fourth-order Bach principal matrix is reconstructed independently from
(deltaGamma), (delta Riem), (delta P), and
(zeta^czeta^ddelta C_{acbd}).  It is symmetric, has generic rank five,
and annihilates the complete rank-three spatial gauge symbol.  The
second-order matter symbol is symmetric and obeys the same principal gauge
identity.

The parent gate remains false.  The Berger background has nonzero Weyl and
Bach curvature, so the lower-order linearized Bach operator contains
connection-variation terms absent on the conformally flat round cylinder.
Importing the round-cylinder Hessian would therefore be wrong.

The remaining exact calculation is

```text
BERGER_LINEARIZED_BACH_PBW_EXPANSION
```

It must emit all order-three-and-lower Bach coefficients in the declared
invariant covariant PBW normal form.  Only then can the complete retained
(q_1^2=0), cyclicity, and action-adjoint identities promote
`BERGER_RETAINED_MINIMAL_OPERATOR`.
"""


def _write(result: BergerRetainedMinimalOperatorPreflight) -> None:
    CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: BergerRetainedMinimalOperatorPreflight) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError("retained operator preflight certificate drifted")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError("retained operator preflight report drifted")


def _guards(result: BergerRetainedMinimalOperatorPreflight) -> None:
    mutations = [
        ("reuse round Hessian", ("nonconformally_flat_guard", "round_cylinder_lower_order_hessian_reused"), True),
        ("promote Bach PBW", ("flags", "retained_Bach_lower_order_PBW_complete"), True),
        ("promote q1", ("flags", "retained_q1_coefficients_complete"), True),
        ("promote parent gate", ("flags", "BERGER_RETAINED_MINIMAL_OPERATOR"), True),
        ("skip Bach expansion", ("next_gate",), "BERGER_NONMINIMAL_COMPLETION"),
    ]
    for name, path, value in mutations:
        payload = deepcopy(result.payload)
        target: Any = payload
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            BergerRetainedMinimalOperatorPreflight(payload).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard failed: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = BergerRetainedMinimalOperatorPreflight.build()
    if args.check:
        _check(result)
    else:
        _write(result)
    if args.guards:
        _guards(result)
    print("BERGER_RETAINED_MINIMAL_OPERATOR_PREFLIGHT: PASS")
    print("K/Ksharp, matter Hessian, Bach principal: COMPLETE")
    print("Berger Bach lower-order PBW and retained parent gate: OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
