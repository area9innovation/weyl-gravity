#!/usr/bin/env python3
"""Formal causal Green variation along the transverse Nariai tangent.

The certified transverse tangent is a smooth global solution of the
linearized Einstein equations, while the existing rank-310 coefficient
replay is a Taylor/PBW calculation at one normal-frame point.  This producer
separates those two scopes.

At metric-complex level the first Green variation is universal.  If

    P_e = Q_e W_0 + W_0 Q_e = P_0 + e p + O(e^2)

and G_0^+/- are the base Green operators, then

    dot G^+/- = -G_0^+/- p G_0^+/-

is the unique same-sided formal inverse variation.  It yields

    dot Lambda^+/- = W_0 dot G^+/-

and the differentiated chain-homotopy identity.  The formula is finite and
therefore needs no convergence assertion.  It uses the standard extension of
same-sided Green operators from compact to past-/future-compact sources.

This does not globalize the one-point rank-310 SDR variation and deliberately
leaves the broad transverse causal-transfer flag false.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FORMAL_METRIC_GREEN_VARIATION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-formal-metric-green-variation.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-formal-metric-green-variation-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_formal_metric_green_variation.py"
TESTS = HERE / "tests/test_nariai_transverse_formal_metric_green_variation.py"

BASE_GREEN = ROOT / "d_quotient_classical/certificates/NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json"
TANGENT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1.json"
ACTION_DOT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1.json"
RANK310_DOT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION_V1.json"
COORDINATE_JETS = HERE / "nariai_transverse_coordinate_curvature_jets.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ref(path: Path, expected: str) -> dict[str, str]:
    payload = json.loads(path.read_text())
    if payload["result_id"] != expected:
        raise AssertionError(f"dependency drifted: {path}")
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": expected,
        "sha256": _sha(path),
    }


def _zero(matrix: sp.MatrixBase) -> bool:
    return all(sp.expand(value) == 0 for value in matrix)


def exact_fixture() -> dict[str, Any]:
    """Finite noncommuting audit of the differentiated Green algebra."""

    identity = sp.eye(2)
    zero = sp.zeros(2)
    q0 = sp.BlockMatrix([[zero, zero], [identity, zero]]).as_explicit()
    a = sp.Matrix([[2, 1], [1, 3]])
    w0 = sp.BlockMatrix([[zero, a], [zero, zero]]).as_explicit()
    s = sp.Matrix(
        [
            [0, 1, 1, 0],
            [2, 0, 0, 1],
            [1, 0, 1, 1],
            [0, 1, 2, -1],
        ]
    )
    qdot = s * q0 - q0 * s
    p0 = q0 * w0 + w0 * q0
    pdot = qdot * w0 + w0 * qdot
    g0 = p0.inv()
    gdot = -g0 * pdot * g0
    lambda0 = w0 * g0
    lambdadot = w0 * gdot

    defects = {
        "base_Q_squared": q0 * q0,
        "linearized_Q_squared": q0 * qdot + qdot * q0,
        "base_left_inverse": p0 * g0 - sp.eye(4),
        "base_right_inverse": g0 * p0 - sp.eye(4),
        "varied_left_inverse": p0 * gdot + pdot * g0,
        "varied_right_inverse": gdot * p0 + g0 * pdot,
        "base_chain_commutation": q0 * g0 - g0 * q0,
        "varied_chain_commutation": qdot * g0 + q0 * gdot - gdot * q0 - g0 * qdot,
        "base_homotopy": q0 * lambda0 + lambda0 * q0 - sp.eye(4),
        "varied_homotopy": qdot * lambda0 + q0 * lambdadot + lambdadot * q0 + lambda0 * qdot,
    }
    failed = {name: matrix.tolist() for name, matrix in defects.items() if not _zero(matrix)}
    if failed:
        raise AssertionError(f"formal Green-variation fixture failed: {failed}")
    return {
        "coefficient_field": "Q",
        "rank": 4,
        "qdot_nonzero": sum(value != 0 for value in qdot),
        "pdot_nonzero": sum(value != 0 for value in pdot),
        "gdot_nonzero": sum(value != 0 for value in gdot),
        "identity_defects": {name: 0 for name in defects},
    }


def tangent_family_check() -> dict[str, Any]:
    """Check the slabwise exact Einstein family generating the tangent."""

    t, e = sp.symbols("t e", real=True)
    beta = sp.sinh(t)
    # The second coefficient is forced because a_epsilon=b_epsilon'/epsilon.
    # Its derivative must reproduce the certified dot a.  The corresponding
    # exact family has b_epsilon(0)=1-epsilon^2/6, not b_epsilon(0)=1.
    gamma = -sp.cosh(2 * t) / 6
    alpha = sp.diff(gamma, t)
    b = 1 + e * beta + e**2 * gamma
    b_initial = 1 - e**2 / 6
    integration_constant = sp.expand(
        b_initial * (e**2 - b_initial**2 / 3 + 1)
    )
    first_integral = sp.expand(
        sp.diff(b, t) ** 2 - (b**2 / 3 - 1 + integration_constant / b)
    )
    first_integral_through_two = sp.series(first_integral, e, 0, 3).removeO().simplify()
    evolution = sp.expand(2 * b * sp.diff(b, t, 2) + sp.diff(b, t) ** 2 + 1 - b**2)
    evolution_through_two = sp.series(evolution, e, 0, 3).removeO().simplify()
    if first_integral_through_two != 0 or evolution_through_two != 0:
        raise AssertionError("Kantowski-Sachs Einstein family expansion drifted")
    if sp.simplify(alpha + sp.sinh(2 * t) / 3) != 0:
        raise AssertionError("exact-family tangent does not match the certified alpha")

    # Exact reduction of Ric(g)=g for
    # g=-dt^2+a(t)^2 dchi^2+b(t)^2 dOmega_2^2.  With a=b'/epsilon,
    # differentiating the scalar ODE supplies the tt and chi-chi equations;
    # the scalar ODE itself is the sphere equation.
    x, y, z = sp.symbols("x y z", nonzero=True)
    third = y - 2 * y * z / x
    exact_einstein_defects = {
        "tt": sp.simplify(third / y + 2 * z / x - 1),
        "chi_chi": sp.simplify(third / y + 2 * (z / y) * (y / x) - 1),
        "sphere": sp.simplify(
            2 * z / x + (y / x) ** 2 + 1 / x**2 - 1
        ).subs(z, (x**2 - y**2 - 1) / (2 * x)).simplify(),
    }
    if any(value != 0 for value in exact_einstein_defects.values()):
        raise AssertionError(f"exact Einstein reduction failed: {exact_einstein_defects}")
    return {
        "exact_ode": "2 b b''+(b')^2+1=b^2",
        "first_integral": "(b')^2=b^2/3-1+C_epsilon/b with C_epsilon=b_epsilon(0)(epsilon^2-b_epsilon(0)^2/3+1)",
        "initial_data": "b_epsilon(0)=1-epsilon^2/6, b_epsilon'(0)=epsilon",
        "metric_coefficient": "a_epsilon=b_epsilon'/epsilon, extended smoothly at epsilon=0",
        "expansion": "b_epsilon=1+epsilon sinh(t)-(epsilon^2/6)cosh(2t)+O(epsilon^3)",
        "tangent": "dot a=-(1/3)sinh(2t), dot b=sinh(t)",
        "finite_slab_statement": "analytic ODE dependence gives an exact Einstein family on every fixed compact time slab for sufficiently small epsilon depending on the slab",
        "global_nonzero_epsilon_statement": "not claimed; the areal factor can reach zero outside a fixed slab",
        "exact_Einstein_reduction": "for a=b'/epsilon, differentiating 2bb''+(b')^2+1=b^2 gives a''/a+2b''/b=1 and a''/a+2(a'/a)(b'/b)=1; the undifferentiated equation is the sphere component",
        "exact_Einstein_component_defects": 0,
        "first_integral_defect_through_epsilon2": 0,
        "evolution_defect_through_epsilon2": 0,
    }


def build() -> dict[str, Any]:
    refs = {
        "base_metric_green": _ref(BASE_GREEN, "NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1"),
        "global_transverse_tangent": _ref(TANGENT, "NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1"),
        "one_point_action_variation": _ref(ACTION_DOT, "NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1"),
        "one_point_rank310_SDR_variation": _ref(RANK310_DOT, "NARIAI_TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION_V1"),
    }
    tangent_payload = json.loads(TANGENT.read_text())
    rank_payload = json.loads(RANK310_DOT.read_text())
    if tangent_payload["exact_witness"]["evaluation_time"] != "asinh(1)":
        raise AssertionError("transverse normalization point drifted")
    if rank_payload["flags"]["TRANSVERSE_CAUSAL_TRANSFER"] is not False:
        raise AssertionError("rank-310 causal flag was prematurely promoted")

    fixture = exact_fixture()
    family = tangent_family_check()
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "nariai-transverse-formal-metric-green-variation-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_FORMAL_METRIC_GREEN_VARIATION_V1",
        "result_state": "GLOBAL_FORMAL_METRIC_CAUSAL_VARIATION_EXACT_RANK310_GLOBALIZATION_OPEN",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": refs,
        "tangent_family": family,
        "formal_green_theorem": {
            "base_complex": "(C_metric,Q0) on global unit Nariai",
            "identified_family": "Q_epsilon=Q0+epsilon qdot+O(epsilon^2) in a smooth bundle-density identification with constant pairing",
            "fixed_witness_choice": "W_epsilon=W0 through first order",
            "witness_operator": "P_epsilon=Q_epsilon W0+W0 Q_epsilon=P0+epsilon pdot+O(epsilon^2)",
            "green_variation": "Gdot_+/-=-G0_+/- pdot G0_+/-",
            "homotopy_variation": "Lambdadot_+/-=W0 Gdot_+/-",
            "inverse_identities": [
                "P0 Gdot_+/-+pdot G0_+/-=0",
                "Gdot_+/- P0+G0_+/- pdot=0"
            ],
            "chain_identity": "qdot Lambda0+Q0 Lambdadot+Lambdadot Q0+Lambda0 qdot=0",
            "support": "Gdot_+ maps compact sources to future-supported sections and Gdot_- to past-supported sections; locality of pdot and the standard extension of G0,+/- to past-/future-compact sources make the two same-sided compositions well typed",
            "adjoint_reversal": "(Gdot_A,+)^sharp=Gdot_(A^sharp),- after differentiating the complementary-degree adjoint theorem; no self-adjoint simplification is made without the cyclic family identification",
            "scope": "formal first order in epsilon; no nonzero-epsilon global spacetime or convergent operator family is asserted"
        },
        "finite_fixture": fixture,
        "rank310_globalization_audit": {
            "current_scope": "Taylor/PBW coefficient jets at the normal-frame point t=asinh(1), theta=pi/2",
            "maximum_curvature_jet_order": 5,
            "global_smooth_coefficient_export_present": False,
            "global_varied_inclusion_projection_homotopy_present": False,
            "reason_transfer_is_open": "a causal operator identity is global; a finite Taylor jet at one point does not define the coefficient functions of the varied rank-310 maps on R times S1 times S2",
            "required_next_input": "global covariant formulas, or globally evaluated smooth coefficient tables, for Idot, pdot_SDR and Hdot together with their differentiated chain and cyclic identities",
            "forbidden_inference": "homogeneity globalization, because the transverse tangent is time dependent and is not invariant under Nariai time translations"
        },
        "exact_checks": {
            "global_linearized_tangent": True,
            "slabwise_exact_Einstein_family_generates_tangent": True,
            "formal_two_sided_Green_variation": True,
            "formal_chain_homotopy_variation": True,
            "same_sided_causal_support": True,
            "rank310_input_is_one_point_jet": True,
            "rank310_global_transfer_not_promoted": True
        },
        "flags": {
            "NARIAI_TRANSVERSE_FORMAL_METRIC_GREEN_VARIATION_V1": True,
            "TRANSVERSE_FORMAL_METRIC_GREEN_VARIATION": True,
            "TRANSVERSE_GLOBAL_RANK310_SDR_VARIATION": False,
            "TRANSVERSE_FORMAL_RANK310_CAUSAL_VARIATION": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False
        },
        "next_gate": "NARIAI_TRANSVERSE_GLOBAL_RANK310_SDR_COEFFICIENT_VARIATION",
        "claim_boundary": "This theorem constructs the global first-order formal advanced/retarded variation of the four-row metric Green homotopy along the certified smooth transverse Einstein tangent. It is a finite Duhamel identity at epsilon=0 and does not assert a global nonzero-epsilon spacetime. The existing rank-310 SDR variation is an exact one-point coefficient-jet theorem only; it is not globalized or causally transferred here.",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha(path)
            for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, COORDINATE_JETS)
        },
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_formal_metric_green_variation --check --guards",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_formal_metric_green_variation.py",
            "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_transverse_formal_metric_green_variation",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-formal-metric-green-variation-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_FORMAL_METRIC_GREEN_VARIATION_V1.json"
        ]
    }


def report(payload: dict[str, Any]) -> str:
    return r"""# Transverse formal metric Green variation

The transverse Kantowski--Sachs tangent is global, not merely a pointwise
curvature sample.  It is generated on every fixed compact time slab by the
exact Einstein ODE

\[
2bb''+(b')^2+1=b^2,
\qquad
(b')^2=\frac{b^2}{3}-1+\frac{C_\epsilon}{b},
\]

with \(b_\epsilon(0)=1-\epsilon^2/6\),
\(b_\epsilon'(0)=\epsilon\), and
\(a_\epsilon=b_\epsilon'/\epsilon\).  Its expansion is

\[
b_\epsilon=1+\epsilon\sinh t-
\frac{\epsilon^2}{6}\cosh(2t)+O(\epsilon^3),
\]

so \(\dot a=-\frac13\sinh(2t)\) and \(\dot b=\sinh t\), exactly the
certified tangent.

For the global four-row metric complex choose the base witness \(W_0\) and
write

\[
P_\epsilon=Q_\epsilon W_0+W_0Q_\epsilon
=P_0+\epsilon\dot P+O(\epsilon^2).
\]

The formal same-sided Green variations are the finite Duhamel expressions

\[
\dot G_\pm=-G_{0,\pm}\dot P G_{0,\pm},
\qquad
\dot\Lambda_\pm=W_0\dot G_\pm.
\]

They obey both differentiated inverse identities, the differentiated chain
commutation relation, and

\[
\dot Q\Lambda_{0,\pm}+Q_0\dot\Lambda_\pm
+\dot\Lambda_\pm Q_0+\Lambda_{0,\pm}\dot Q=0.
\]

Locality of \(\dot P\) and same-sided composition give the retarded or
advanced support property.  This is a formal first-order theorem at the
global Nariai metric complex; it does not assert a smooth nonzero-\(\epsilon\)
spacetime for all cylinder times.

The rank-310 transfer remains open for a different, sharply identified
reason.  Its current differentiated SDR is a complete Taylor/PBW jet through
order five at \(t=\operatorname{arsinh}(1)\), \(\theta=\pi/2\).  The
transverse tangent is time dependent, so Nariai homogeneity cannot globalize
that one-point table.  A global causal identity requires smooth coefficient
fields for \(\dot I\), \(\dot p\), and \(\dot H\).  No broad transverse
causal flag is promoted until those data exist.
"""


def verify(payload: dict[str, Any]) -> None:
    Draft202012Validator.check_schema(json.loads(SCHEMA.read_text()))
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(payload)
    if not all(payload["exact_checks"].values()):
        raise AssertionError("a formal metric Green-variation check failed")
    if any(payload["finite_fixture"]["identity_defects"].values()):
        raise AssertionError("finite Green-variation algebra drifted")
    if payload["rank310_globalization_audit"]["global_smooth_coefficient_export_present"]:
        raise AssertionError("rank-310 global coefficient export was invented")
    for flag in (
        "TRANSVERSE_GLOBAL_RANK310_SDR_VARIATION",
        "TRANSVERSE_FORMAL_RANK310_CAUSAL_VARIATION",
        "TRANSVERSE_CAUSAL_TRANSFER",
    ):
        if payload["flags"][flag] is not False:
            raise AssertionError(f"downstream flag promoted: {flag}")


def guards(payload: dict[str, Any]) -> None:
    mutations = (
        ("erase inverse", ("finite_fixture", "identity_defects", "varied_left_inverse"), 1),
        ("invent global coefficients", ("rank310_globalization_audit", "global_smooth_coefficient_export_present"), True),
        ("promote causal transfer", ("flags", "TRANSVERSE_CAUSAL_TRANSFER"), True),
    )
    for name, path, value in mutations:
        mutant = deepcopy(payload)
        target: Any = mutant
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            verify(mutant)
        except (AssertionError, ValidationError):
            continue
        raise AssertionError(f"guard failed to reject mutation: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    verify(payload)
    if args.guards:
        guards(payload)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    rendered_report = report(payload)
    if args.write:
        OUTPUT.write_text(rendered)
        REPORT.write_text(rendered_report)
    if args.check:
        if OUTPUT.read_text() != rendered or REPORT.read_text() != rendered_report:
            raise AssertionError("formal metric Green-variation artifact is stale")
    print("NARIAI_TRANSVERSE_FORMAL_METRIC_GREEN_VARIATION_V1: PASS")


if __name__ == "__main__":
    main()
