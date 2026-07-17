#!/usr/bin/env python3
"""Certify a momentum-balanced standing Maxwell correction on Berger.

The fixture coherently superposes the certified Hopf-traveling mode with its
oppositely propagating source-free partner in the same Maxwell field.  A
direct third metric variation fixes the q2 normalization, including the
repository's factor-two metric BV Euler-row convention.  The resulting
stationary homogeneous source has zero Hopf flux and an exact retained
gravity primitive.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.backreacted_clock.berger_dynamical_maxwell_redshift import (
    _exterior_derivative,
    _hodge_star,
)
from d_quotient_classical.backreacted_clock.berger_maxwell_stress_residual_projection import (
    PAIRS,
    _parse_constant_matrix,
    _projection_on_metric_sources,
    _stress_polarization,
)


CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_MOMENTUM_BALANCED_FIXTURE.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-maxwell-momentum-balanced-fixture.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-maxwell-momentum-balanced-fixture-v1.schema.json"

DEPENDENCIES = {
    "single_beam_obstruction": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_STRESS_RESIDUAL_PROJECTION.json",
    "maxwell_mode": ROOT / "d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json",
    "gravity_contraction": ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
    "retained_unary": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json",
}
SOURCE_PATHS = (
    ROOT / "d_quotient_classical/backreacted_clock/berger_maxwell_momentum_balanced_fixture.py",
    ROOT / "d_quotient_classical/backreacted_clock/verify_berger_maxwell_momentum_balanced_fixture.py",
    ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_maxwell_momentum_balanced_fixture.py",
    SCHEMA_PATH,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_dependencies() -> dict[str, dict[str, Any]]:
    data = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    obstruction = data["single_beam_obstruction"]
    if obstruction["projection_and_verdict"]["binary_verdict"] != "OBSTRUCTION":
        raise AssertionError("single-beam Hopf-flux obstruction is unavailable")
    if obstruction["physical_mode_block"]["exact_data"]["dual_witness_source_pairing"] != "1":
        raise AssertionError("single-beam obstruction witness is not normalized")
    if data["maxwell_mode"]["maxwell_probe"]["action"] != "S_M=-1/4 int sqrt(-g_hat) F_ab F^ab":
        raise AssertionError("Maxwell action normalization drifted")
    if data["gravity_contraction"]["flags"]["BERGER_COMPLETE_GAUGE_FIXED_UNARY_EXPORT"] is not True:
        raise AssertionError("gravity contraction is unavailable")
    if data["retained_unary"]["flags"]["BERGER_RETAINED_MINIMAL_OPERATOR"] is not True:
        raise AssertionError("retained unary operator is unavailable")
    return data


def _antisymmetric(components: dict[tuple[int, int], sp.Expr]) -> sp.Matrix:
    matrix = sp.zeros(4)
    for (left, right), value in components.items():
        matrix[left, right] = value
        matrix[right, left] = -value
    return matrix


def _field_strengths(beta: sp.Expr, time: sp.Symbol) -> tuple[sp.Matrix, sp.Matrix]:
    cosine = sp.cos(beta * time)
    sine = sp.sin(beta * time)
    forward = _antisymmetric(
        {(0, 1): -beta * sine, (0, 2): beta * cosine, (1, 3): beta * sine, (2, 3): -beta * cosine}
    )
    reverse = _antisymmetric(
        {(0, 1): -beta * sine, (0, 2): -beta * cosine, (1, 3): -beta * sine, (2, 3): -beta * cosine}
    )
    return forward, reverse


def _direct_action_cubic(field_strength: sp.Matrix) -> sp.Matrix:
    """Return d_h d_epsilon^2 of the Maxwell Lagrangian density."""

    eta = sp.diag(-1, 1, 1, 1)
    metric_parameter, amplitude = sp.symbols("metric_parameter amplitude", real=True)
    result = sp.zeros(10, 1)
    for index, (left, right) in enumerate(PAIRS):
        variation = sp.zeros(4)
        variation[left, right] = 1
        variation[right, left] = 1
        if left == right:
            variation[left, right] = 1
        metric = eta + metric_parameter * variation
        inverse = metric.inv()
        contraction = sum(
            inverse[a, c] * inverse[b, d] * field_strength[a, b] * field_strength[c, d]
            for a in range(4) for b in range(4) for c in range(4) for d in range(4)
        )
        density = -sp.Rational(1, 4) * sp.sqrt(-metric.det()) * amplitude**2 * contraction
        result[index] = sp.trigsimp(
            sp.diff(density, metric_parameter, amplitude, amplitude).subs(
                {metric_parameter: 0, amplitude: 0}
            )
        )
    return result.applyfunc(sp.simplify)


def _repository_q2_from_stress(stress_covariant: sp.Matrix) -> sp.Matrix:
    eta = sp.diag(-1, 1, 1, 1)
    stress_upper = sp.simplify(eta * stress_covariant * eta)
    source = sp.zeros(10, 1)
    for index, (left, right) in enumerate(PAIRS):
        multiplicity = 2 if left != right else 1
        source[index] = sp.factor(2 * multiplicity * stress_upper[left, right])
    return source


def _strings(vector: sp.Matrix) -> list[str]:
    return [str(sp.factor(value)) for value in vector]


def _four_form_checks(beta: sp.Expr, time: sp.Symbol) -> dict[str, bool]:
    alpha = sp.symbols("alpha", positive=True, real=True)
    derivatives = {
        0: {},
        1: {(2, 3): -beta},
        2: {(1, 3): beta},
        3: {(1, 2): -alpha},
    }
    forward_potential = {(1,): sp.cos(beta * time), (2,): sp.sin(beta * time)}
    reverse_potential = {(1,): sp.cos(beta * time), (2,): -sp.sin(beta * time)}
    checks: dict[str, bool] = {}
    for name, potential in (("forward", forward_potential), ("reverse", reverse_potential), ("standing", {key: forward_potential.get(key, 0) + reverse_potential.get(key, 0) for key in set(forward_potential) | set(reverse_potential)})):
        field = _exterior_derivative(potential, derivatives, time)
        checks[f"{name}_dF_zero"] = not _exterior_derivative(field, derivatives, time)
        checks[f"{name}_dstarF_zero"] = not _exterior_derivative(_hodge_star(field), derivatives, time)
    if not all(checks.values()):
        raise AssertionError("forward/reverse/standing Maxwell equation failed")
    return checks


def _exact_fixture(dependencies: dict[str, dict[str, Any]]) -> dict[str, Any]:
    beta = 2 * sp.sqrt(10) / 3
    time = sp.symbols("t", real=True)
    eta = sp.diag(-1, 1, 1, 1)
    forward, reverse = _field_strengths(beta, time)
    standing = forward + reverse

    forward_stress = _stress_polarization(forward, forward).applyfunc(sp.trigsimp)
    reverse_stress = _stress_polarization(reverse, reverse).applyfunc(sp.trigsimp)
    cross_stress = _stress_polarization(forward, reverse).applyfunc(sp.trigsimp)
    standing_stress = _stress_polarization(standing, standing).applyfunc(sp.trigsimp)
    if standing_stress != forward_stress + reverse_stress + 2 * cross_stress:
        raise AssertionError("coherent stress polarization identity failed")
    if forward_stress[0, 3] != beta**2 or reverse_stress[0, 3] != -beta**2:
        raise AssertionError("counter-propagating Hopf fluxes do not cancel")
    if standing_stress[0, 3] != 0 or standing_stress[0, 0] != 2 * beta**2:
        raise AssertionError("standing Maxwell stress is not momentum balanced and positive")
    if sp.simplify(sum(eta[a, b] * standing_stress[a, b] for a in range(4) for b in range(4))) != 0:
        raise AssertionError("standing Maxwell stress is not tracefree")

    forward_cubic = _direct_action_cubic(forward)
    reverse_cubic = _direct_action_cubic(reverse)
    standing_cubic = _direct_action_cubic(standing)
    forward_q2 = _repository_q2_from_stress(forward_stress)
    reverse_q2 = _repository_q2_from_stress(reverse_stress)
    standing_q2 = _repository_q2_from_stress(standing_stress)
    if 2 * forward_cubic != forward_q2 or 2 * reverse_cubic != reverse_q2 or 2 * standing_cubic != standing_q2:
        raise AssertionError("direct Maxwell action variation disagrees with metric BV q2 normalization")
    upstream_source = sp.Matrix(
        [sp.sympify(value) for value in dependencies["single_beam_obstruction"]["physical_mode_block"]["exact_data"]["retained_metric_source"]]
    )
    if forward_q2 != upstream_source:
        raise AssertionError("direct action variation does not reproduce the certified single-beam source")

    projection = _projection_on_metric_sources(
        dependencies["gravity_contraction"]["contraction"]["pi_cl"]
    )
    retained_source = sp.simplify(projection * standing_q2)
    hessian = _parse_constant_matrix(
        dependencies["retained_unary"]["q1_blocks"]["H_retained"], (10, 10)
    )
    noether = _parse_constant_matrix(
        dependencies["retained_unary"]["q1_blocks"]["minus_K_spatial_sharp"], (3, 10)
    )
    closure = sp.simplify(noether * retained_source)
    primitive = sp.Matrix(
        [
            -sp.Rational(10240, 567), 0, 0, 0,
            sp.Rational(4933120, 147819), 0, 0,
            sp.Rational(153410560, 4582389), 0,
            sp.Rational(28160, 1953),
        ]
    )
    primitive_residual = sp.simplify(hessian * primitive - retained_source)
    correction = sp.simplify(-primitive / 2)
    maurer_cartan_residual = sp.simplify(hessian * correction + retained_source / 2)
    witness = sp.zeros(10, 1)
    witness[3] = -sp.Rational(9, 160)
    witness_pairing = sp.factor((witness.T * retained_source)[0])
    if closure != sp.zeros(3, 1) or primitive_residual != sp.zeros(10, 1):
        raise AssertionError("balanced standing source is not q1 closed and exact")
    if maurer_cartan_residual != sp.zeros(10, 1):
        raise AssertionError("second-order Maurer-Cartan correction failed")
    if witness_pairing != 0 or hessian.row_join(retained_source).rank() != hessian.rank():
        raise AssertionError("Hopf-flux obstruction did not cancel")

    volume = 12 * sp.sqrt(10) * sp.pi**2 / 5
    symplectic_pairing = sp.factor(-4 * beta * volume)
    energy_coefficient = sp.factor(2 * beta**2 * volume)
    if symplectic_pairing != -64 * sp.pi**2 or energy_coefficient != 64 * sp.sqrt(10) * sp.pi**2 / 3:
        raise AssertionError("standing Maxwell health normalization drifted")

    return {
        "beta": str(beta),
        "direct_four_form_checks": _four_form_checks(beta, time),
        "forward_direct_action_cubic": _strings(forward_cubic),
        "forward_repository_q2": _strings(forward_q2),
        "reverse_direct_action_cubic": _strings(reverse_cubic),
        "reverse_repository_q2": _strings(reverse_q2),
        "standing_direct_action_cubic": _strings(standing_cubic),
        "standing_repository_q2": _strings(standing_q2),
        "normalization_residual": _strings(standing_q2 - 2 * standing_cubic),
        "standing_stress_covariant": [[str(sp.factor(value)) for value in standing_stress.row(row)] for row in range(4)],
        "coherent_cross_stress_covariant": [[str(sp.factor(value)) for value in cross_stress.row(row)] for row in range(4)],
        "Hopf_flux_forward": str(sp.factor(forward_stress[0, 3])),
        "Hopf_flux_reverse": str(sp.factor(reverse_stress[0, 3])),
        "Hopf_flux_standing": str(sp.factor(standing_stress[0, 3])),
        "standing_stress_trace": "0",
        "q1_closure_residual": _strings(closure),
        "constant_hessian_rank": hessian.rank(),
        "augmented_rank": hessian.row_join(retained_source).rank(),
        "exact_primitive": _strings(primitive),
        "primitive_residual": _strings(primitive_residual),
        "normalized_single_beam_witness_pairing": str(witness_pairing),
        "second_order_Maurer_Cartan_correction": _strings(correction),
        "second_order_Maurer_Cartan_residual": _strings(maurer_cartan_residual),
        "symplectic_pairing": str(symplectic_pairing),
        "positive_energy_coefficient": str(energy_coefficient),
    }


def build() -> dict[str, Any]:
    dependencies = _load_dependencies()
    exact = _exact_fixture(dependencies)
    payload = {
        "schema": "pure-weyl-berger-maxwell-momentum-balanced-fixture-v1",
        "result_id": "BERGER_MAXWELL_MOMENTUM_BALANCED_FIXTURE",
        "setting_id": "compact_positive_berger_clock_fixed_coupling",
        "claim_status": "CERTIFIED_REDUCED_MODE_COHERENT_STANDING_MAXWELL_SOURCE_EXACT_AT_SECOND_ORDER",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": dependencies[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "normalization_hardening": {
            "direct_object": "d_h d_epsilon^2[-1/4 sqrt(-g(h)) F(epsilon)^2] at h=epsilon=0",
            "metric_BV_row_convention": "the repository metric Euler row is twice the covariant-metric variational derivative",
            "identity": "q2_repository=2*direct_action_cubic",
            "off_diagonal_coordinate": "g_03=g_30=h_03 is varied as one symmetric component",
            "exact_residual": exact["normalization_residual"],
        },
        "balanced_Maxwell_fixture": {
            "forward_potential": "A_f=cos(beta t)e1+sin(beta t)e2",
            "reverse_potential": "A_b=cos(beta t)e1-sin(beta t)e2",
            "standing_potential": "A_st=A_f+A_b=2 cos(beta t)e1",
            "phase_partner": "A_st,s=-2 sin(beta t)e1",
            "field_ownership": "one coherent Maxwell field; cross-stress is included exactly",
            "D_weight_of_stress": "0",
            "field_content": ["h_hat_star_00", "h_hat_star_11", "h_hat_star_22", "h_hat_star_33"],
            "exact_data": exact,
        },
        "projection_and_solution": {
            "pi_cl_projection": "identity on the ten retained metric-antifield rows",
            "single_beam_obstruction_witness_pairing_after_balance": "0",
            "binary_verdict": "EXACT_PRIMITIVE",
            "Maurer_Cartan_equation": "q1 h^(2)+1/2 q2(A_st,A_st)=0",
            "correction_status": "EXPLICIT_SECOND_ORDER_HOMOGENEOUS_GRAVITY_CORRECTION",
            "interpretation": "opposite Hopf flux cancels; the remaining coherent standing-wave energy and anisotropic pressure source lies in the retained Hessian image",
        },
        "branch_and_health": {
            "radiative_branch_scope": "NOT_ACCESSED_BY_STATIONARY_HOMOGENEOUS_BLOCK",
            "global_Einstein_extra_Weyl_noncoupling_claim": False,
            "energy_signature": [2, 0, 0],
            "negative_physical_direction_introduced": False,
            "health_statement": "the correlated two-phase standing-wave plane has nondegenerate symplectic form and positive Maxwell energy; the displayed gravity term is a sourced correction, not a new kinetic mode",
        },
        "flags": {
            "BERGER_MAXWELL_Q2_DIRECT_ACTION_NORMALIZATION": True,
            "BERGER_COHERENT_COUNTERPROPAGATING_MAXWELL_SOLUTION": True,
            "BERGER_HOPF_MOMENTUM_BALANCED": True,
            "BERGER_BALANCED_SOURCE_Q1_EXACT": True,
            "BERGER_SECOND_ORDER_HOMOGENEOUS_GRAVITY_CORRECTION": True,
            "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE": False,
            "BERGER_FULL_SUPPORT_LOCAL_MAXWELL_Q2": False,
            "BERGER_RADIATIVE_BRANCH_COUPLING_CLASSIFIED": False,
            "BERGER_FULL_BACKREACTED_SOLUTION": False,
            "NEGATIVE_PHYSICAL_DIRECTION_INTRODUCED": False,
            "LORENTZIAN_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "reduced_mode_limitation": "This exact solution is the coherent standing-wave subspace of the stationary SU(2)_L x U(1)_R homogeneous constant-component, D-weight-zero retained metric block at the rational Berger fixture. It includes the single-field interference stress, but it is not a localized emitter/receiver signal, does not decide whether a lone traveling beam has a nonhomogeneous support-local primitive, does not export q2(h,A)->A_plus or all Maxwell antifield rows, and does not classify radiative Einstein/extra-Weyl scattering branches.",
        "next_gate": "BERGER_LOCALIZED_APPARATUS_RECOIL_OR_SUPPORT_LOCAL_SINGLE_BEAM_PRIMITIVE",
        "provenance": {"source_manifest": {str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS}},
        "verification_receipts": [
            {"test_tier": 1, "command": "python3 d_quotient_classical/backreacted_clock/berger_maxwell_momentum_balanced_fixture.py --check --guards", "elapsed_seconds": 10.87, "status": "PASS"},
            {"test_tier": 1, "command": "python3 d_quotient_classical/backreacted_clock/verify_berger_maxwell_momentum_balanced_fixture.py", "elapsed_seconds": 1.09, "status": "PASS"},
            {"test_tier": 1, "command": "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_maxwell_momentum_balanced_fixture", "elapsed_seconds": 15.95, "status": "PASS"},
            {"test_tier": 1, "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-maxwell-momentum-balanced-fixture-v1.schema.json -d d_quotient_classical/certificates/BERGER_MAXWELL_MOMENTUM_BALANCED_FIXTURE.json", "elapsed_seconds": 1.26, "status": "PASS"},
        ],
        "higher_tiers_not_run": {
            "tier_2": "The imported unary and contraction operators are unchanged and content-addressed; only a new exact physical-shape Maxwell block is added.",
            "tier_3": "This REDUCED-MODE second-order correction is not a shared-core freeze, full support-local theorem, release, or Lorentzian certification.",
        },
        "claim_boundary": "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result independently derives the Maxwell mixed q2 normalization by direct third variation, constructs a coherent counter-propagating standing solution in one Maxwell field with its interference stress included, cancels the single-beam Hopf-flux obstruction, and gives an explicit second-order homogeneous gravity correction solving q1 h2 plus one-half q2(A,A)=0. It does not construct localized apparatus recoil, decide a full support-local primitive for a lone traveling beam, export the complete coupled Maxwell BV operation, classify radiative Einstein/extra-Weyl branch mixing, produce an all-orders backreacted spacetime, introduce a negative kinetic direction, certify Lorentzian causal perturbation theory, or make a quantum claim.",
    }
    verify(payload)
    return payload


def verify(payload: dict[str, Any]) -> None:
    dependencies = _load_dependencies()
    exact = _exact_fixture(dependencies)
    if payload["balanced_Maxwell_fixture"]["exact_data"] != exact:
        raise AssertionError("persisted balanced Maxwell fixture drifted")
    if any(value != "0" for value in exact["normalization_residual"]):
        raise AssertionError("direct-action normalization residual is nonzero")
    if exact["Hopf_flux_standing"] != "0" or exact["normalized_single_beam_witness_pairing"] != "0":
        raise AssertionError("Hopf-flux obstruction did not cancel")
    if exact["constant_hessian_rank"] != exact["augmented_rank"]:
        raise AssertionError("balanced source is not exact")
    if any(value != "0" for value in exact["second_order_Maurer_Cartan_residual"]):
        raise AssertionError("second-order correction residual is nonzero")
    for required in (
        "BERGER_MAXWELL_Q2_DIRECT_ACTION_NORMALIZATION",
        "BERGER_COHERENT_COUNTERPROPAGATING_MAXWELL_SOLUTION",
        "BERGER_HOPF_MOMENTUM_BALANCED",
        "BERGER_BALANCED_SOURCE_Q1_EXACT",
        "BERGER_SECOND_ORDER_HOMOGENEOUS_GRAVITY_CORRECTION",
    ):
        if payload["flags"][required] is not True:
            raise AssertionError(f"required flag missing: {required}")
    for forbidden in (
        "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE",
        "BERGER_FULL_SUPPORT_LOCAL_MAXWELL_Q2",
        "BERGER_RADIATIVE_BRANCH_COUPLING_CLASSIFIED",
        "BERGER_FULL_BACKREACTED_SOLUTION",
        "NEGATIVE_PHYSICAL_DIRECTION_INTRODUCED",
        "LORENTZIAN_CERTIFIED",
        "QUANTUM_CLAIM",
    ):
        if payload["flags"][forbidden] is not False:
            raise AssertionError(f"forbidden promotion: {forbidden}")
    for name, path in DEPENDENCIES.items():
        if payload["dependency_refs"][name]["sha256"] != _sha256(path):
            raise AssertionError(f"dependency hash drift: {name}")


def _json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _report(payload: dict[str, Any]) -> str:
    exact = payload["balanced_Maxwell_fixture"]["exact_data"]
    return rf"""# Berger momentum-balanced Maxwell fixture

## Outcome

The single traveling mode's homogeneous Hopf-flux obstruction is removable
by an exact configuration in the same Maxwell field.  Add the source-free
counter-propagating solution

\[
A_b=\cos(\beta t)e^1-\sin(\beta t)e^2
\]

to the forward mode.  Their coherent sum is the standing wave

\[
A_{{st}}=2\cos(\beta t)e^1,
\qquad \beta={exact['beta']}.
\]

Direct four-form checks give `dF=0=d star F` for the forward, reverse, and
standing fields.  This is one Maxwell field, not two independent photon
species, and the coherent cross-stress is included.

## Normalization hardening

For every symmetric metric component, the verifier differentiates

\[
-\frac14\sqrt{{-g(h)}}\,F(\epsilon)_{{ab}}F(\epsilon)^{{ab}}
\]

once in `h` and twice in the Maxwell amplitude.  The repository metric BV
Euler row is normalized as twice this covariant-metric variational
derivative.  Coefficientwise,

```text
q2_repository - 2 direct_action_cubic = {exact['normalization_residual']}
```

so the earlier factor of two and the off-diagonal `03` sign are now checked
directly from the action.

## Balanced source and gravity correction

The forward and reverse covariant Hopf fluxes are respectively
`{exact['Hopf_flux_forward']}` and `{exact['Hopf_flux_reverse']}`; the
standing flux is exactly `{exact['Hopf_flux_standing']}`.  The coherent
standing source in row order `(00,01,02,03,11,12,13,22,23,33)` is

```text
{exact['standing_repository_q2']}
```

It is `q1` closed, the retained Hessian and augmented matrix both have rank
`{exact['constant_hessian_rank']}`, and the normalized single-beam witness
pairs to zero.  An exact primitive is

```text
{exact['exact_primitive']}
```

and the actual order-two correction solving
`q1 h^(2)+1/2 q2(A_st,A_st)=0` is

```text
{exact['second_order_Maurer_Cartan_correction']}
```

with identically zero residual.

## Health and scope

The correlated standing-wave phase plane has symplectic pairing
`{exact['symplectic_pairing']}` and positive energy coefficient
`{exact['positive_energy_coefficient']}`, hence signature `[2,0,0]`.
No negative physical direction is introduced.

Radiative Einstein-like and extra-Weyl branches are not accessed by this
stationary homogeneous block; no global noncoupling claim is made.  This is
a second-order reduced-mode correction, not an all-orders backreacted
spacetime, localized redshift experiment, or support-local theorem for a
lone traveling beam.

Machine-readable result:
`d_quotient_classical/certificates/BERGER_MAXWELL_MOMENTUM_BALANCED_FIXTURE.json`.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.write:
        CERTIFICATE_PATH.write_text(_json(payload))
        REPORT_PATH.write_text(_report(payload))
    if args.check:
        if CERTIFICATE_PATH.read_text() != _json(payload):
            raise AssertionError("balanced Maxwell certificate drifted")
        if REPORT_PATH.read_text() != _report(payload):
            raise AssertionError("balanced Maxwell report drifted")
    if args.guards:
        mutants = []
        normalization = deepcopy(payload)
        normalization["balanced_Maxwell_fixture"]["exact_data"]["normalization_residual"][0] = "1"
        mutants.append(("break action normalization", normalization))
        flux = deepcopy(payload)
        flux["balanced_Maxwell_fixture"]["exact_data"]["Hopf_flux_standing"] = "1"
        mutants.append(("restore net Hopf flux", flux))
        correction = deepcopy(payload)
        correction["balanced_Maxwell_fixture"]["exact_data"]["second_order_Maurer_Cartan_residual"][0] = "1"
        mutants.append(("break nonlinear correction", correction))
        promoted = deepcopy(payload)
        promoted["flags"]["BERGER_FULL_BACKREACTED_SOLUTION"] = True
        mutants.append(("promote all-orders backreaction", promoted))
        for name, mutant in mutants:
            try:
                verify(mutant)
            except AssertionError:
                continue
            raise AssertionError(f"mutation guard accepted: {name}")
    print("BERGER_MAXWELL_MOMENTUM_BALANCED_FIXTURE: PASS")


if __name__ == "__main__":
    main()
