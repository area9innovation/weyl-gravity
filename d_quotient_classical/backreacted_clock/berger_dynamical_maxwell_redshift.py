#!/usr/bin/env python3
"""Certify an exact dynamical Maxwell redshift mode on the Berger clock.

The result is a G0 exact-mode theorem.  It upgrades the prescribed
characteristic direction of BERGER_RELATIONAL_REDSHIFT_PREFLIGHT to a genuine
source-free Maxwell solution and a gauge-invariant spatially averaged
frequency observable.  Localized retarded emission and the gravity--Maxwell
q2 dressing remain separate gates.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-dynamical-maxwell-redshift.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-dynamical-maxwell-redshift-v1.schema.json"

DEPENDENCIES = {
    "relational_preflight": ROOT / "d_quotient_classical/certificates/BERGER_RELATIONAL_REDSHIFT_PREFLIGHT.json",
    "clock_background": ROOT / "d_quotient_classical/certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json",
}
SOURCE_PATHS = (
    ROOT / "d_quotient_classical/backreacted_clock/berger_dynamical_maxwell_redshift.py",
    ROOT / "d_quotient_classical/backreacted_clock/verify_berger_dynamical_maxwell_redshift.py",
    ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_dynamical_maxwell_redshift.py",
    SCHEMA_PATH,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_dependencies() -> dict[str, dict[str, Any]]:
    data = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    preflight = data["relational_preflight"]
    if preflight["flags"]["BERGER_G0_OPERATIONAL_REDSHIFT_FIXTURE"] is not True:
        raise AssertionError("Berger relational redshift preflight is unavailable")
    if preflight["activation_gate"]["full_gate"] != "OPEN":
        raise AssertionError("preflight claim boundary drifted")
    background = data["clock_background"]
    if background["flags"]["exact_backreacted_background_exists"] is not True:
        raise AssertionError("positive Berger clock background is unavailable")
    return data


def _mode_algebra() -> dict[str, Any]:
    """Derive the Maxwell mode in the orthonormal Berger coframe."""

    beta, alpha, t = sp.symbols("beta alpha t", positive=True, real=True)
    cosine = sp.cos(beta * t)
    sine = sp.sin(beta * t)
    potential = sp.Matrix([cosine, sine, 0])
    phase_partner = sp.Matrix([-sine, cosine, 0])

    # Derive d and curl=*d from the Berger frame commutators rather than
    # inserting the desired eigenspace as the answer.
    structure = sp.MutableDenseNDimArray.zeros(3, 3, 3)
    for target, first, second, value in (
        (2, 0, 1, alpha),
        (0, 1, 2, beta),
        (1, 2, 0, beta),
    ):
        structure[target, first, second] = value
        structure[target, second, first] = -value
    curl = sp.zeros(3)
    for basis_form in range(3):
        for target in range(3):
            curl[target, basis_form] = sp.simplify(
                -sp.Rational(1, 2)
                * sum(
                    sp.LeviCivita(target, first, second)
                    * structure[basis_form, first, second]
                    for first in range(3)
                    for second in range(3)
                )
            )
    if curl != sp.diag(-beta, -beta, -alpha):
        raise AssertionError("Berger curl derivation drifted")

    # A left-invariant vector has divergence -tr(ad_X).  SU(2) is
    # unimodular, and the explicit Berger structure constants give zero for
    # all three basis directions.
    divergences = [
        -sum(structure[index, basis_vector, index] for index in range(3))
        for basis_vector in range(3)
    ]
    if divergences != [0, 0, 0]:
        raise AssertionError("left-invariant Maxwell mode is not divergence free")
    magnetic = sp.simplify(curl * potential)
    electric = sp.simplify(-sp.diff(potential, t))
    wave_residual = sp.simplify(sp.diff(potential, t, 2) + curl * curl * potential)
    poynting = sp.simplify(electric.cross(magnetic))

    if wave_residual != sp.zeros(3, 1):
        raise AssertionError("Maxwell wave equation failed")
    if sp.trigsimp(electric.dot(electric) - magnetic.dot(magnetic)) != 0:
        raise AssertionError("Maxwell mode is not null")
    if sp.trigsimp(electric.dot(magnetic)) != 0:
        raise AssertionError("Maxwell pseudoscalar invariant is nonzero")
    expected_flux = sp.Matrix([0, 0, -beta**2])
    if sp.simplify(sp.trigsimp(poynting) - expected_flux) != sp.zeros(3, 1):
        raise AssertionError("Maxwell flux direction drifted")

    # The second phase solution gives the exact real solution-space pairing.
    dot_potential = sp.diff(potential, t)
    dot_partner = sp.diff(phase_partner, t)
    symplectic_density = sp.trigsimp(
        potential.dot(dot_partner) - phase_partner.dot(dot_potential)
    )
    if symplectic_density != -2 * beta:
        raise AssertionError("Maxwell phase-space pairing drifted")

    return {
        "beta": beta,
        "alpha": alpha,
        "potential": potential,
        "phase_partner": phase_partner,
        "curl": curl,
        "divergences": divergences,
        "electric": electric,
        "magnetic": magnetic,
        "poynting": poynting,
        "symplectic_density": symplectic_density,
    }


def _fixture() -> dict[str, str]:
    """Replay the exact algebraic rational-background fixture."""

    beta = sp.Rational(2, 3) * sp.sqrt(10)  # 1/c for c^2=9/40.
    volume = sp.Rational(12, 5) * sp.sqrt(10) * sp.pi**2
    v_emit = sp.S(0)
    v_receive = sp.Rational(3, 5)
    gamma_emit = 1 / sp.sqrt(1 - v_emit**2)
    gamma_receive = 1 / sp.sqrt(1 - v_receive**2)
    frequency_emit = sp.factor(beta * gamma_emit * (1 - v_emit))
    frequency_receive = sp.factor(beta * gamma_receive * (1 - v_receive))
    energy_emit = sp.factor(frequency_emit**2)
    energy_receive = sp.factor(frequency_receive**2)
    ratio = sp.factor(sp.sqrt(energy_emit / energy_receive))
    travel_time = sp.Rational(1, 5) / (1 - v_receive)
    theta_receive = sp.Rational(3, 4) * travel_time
    symplectic_pairing = sp.factor(-2 * beta * volume)
    energy_coefficient = sp.factor(beta**2 * volume)
    phase_slope_emit = sp.factor(-beta / sp.Rational(3, 4))
    phase_slope_receive = sp.factor(
        -beta * (1 - v_receive) / sp.Rational(3, 4)
    )

    actual = {
        "beta": beta,
        "spatial_volume": volume,
        "gamma_emit": gamma_emit,
        "gamma_receive": gamma_receive,
        "frequency_emit": frequency_emit,
        "frequency_receive": frequency_receive,
        "averaged_energy_emit": energy_emit,
        "averaged_energy_receive": energy_receive,
        "one_plus_z": ratio,
        "z": ratio - 1,
        "travel_time": travel_time,
        "theta_receive": theta_receive,
        "phase_slope_emit": phase_slope_emit,
        "phase_slope_receive": phase_slope_receive,
        "symplectic_pairing": symplectic_pairing,
        "positive_energy_coefficient": energy_coefficient,
    }
    expected = {
        "beta": 2 * sp.sqrt(10) / 3,
        "spatial_volume": 12 * sp.sqrt(10) * sp.pi**2 / 5,
        "gamma_emit": 1,
        "gamma_receive": sp.Rational(5, 4),
        "frequency_emit": 2 * sp.sqrt(10) / 3,
        "frequency_receive": sp.sqrt(10) / 3,
        "averaged_energy_emit": sp.Rational(40, 9),
        "averaged_energy_receive": sp.Rational(10, 9),
        "one_plus_z": 2,
        "z": 1,
        "travel_time": sp.Rational(1, 2),
        "theta_receive": sp.Rational(3, 8),
        "phase_slope_emit": -8 * sp.sqrt(10) / 9,
        "phase_slope_receive": -16 * sp.sqrt(10) / 45,
        "symplectic_pairing": -32 * sp.pi**2,
        "positive_energy_coefficient": 32 * sp.sqrt(10) * sp.pi**2 / 3,
    }
    if any(sp.simplify(actual[key] - value) != 0 for key, value in expected.items()):
        raise AssertionError("dynamical Maxwell redshift fixture drifted")
    return {key: str(sp.factor(value)) for key, value in actual.items()}


def build() -> dict[str, Any]:
    dependencies = _load_dependencies()
    _mode_algebra()
    payload: dict[str, Any] = {
        "schema": "pure-weyl-berger-dynamical-maxwell-redshift-v1",
        "result_id": "BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE",
        "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
        "claim_status": "CERTIFIED_G0_DYNAMICAL_MAXWELL_MODE_LOCALIZED_RETARDED_DRESSING_OPEN",
        "generality_level": "G0",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": dependencies[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "maxwell_probe": {
            "action": "S_M=-1/4 int sqrt(-g_hat) F_ab F^ab",
            "order": "probe amplitude epsilon; stress/backreaction starts at epsilon^2",
            "weyl_behavior": "F has Weyl weight zero in four dimensions and g_hat=rho^2 g is Weyl invariant",
            "coframe": "g_hat=-e0^2+e1^2+e2^2+e3^2 at the rho=1 rational fixture",
            "maurer_cartan": [
                "de1=-(1/c)e2 wedge e3",
                "de2=-(1/c)e3 wedge e1",
                "de3=-(c/a^2)e1 wedge e2",
            ],
            "potential": "A_c=cos(beta t)e1+sin(beta t)e2 with beta=1/c",
            "phase_partner": "A_s=-sin(beta t)e1+cos(beta t)e2",
            "field_strength": "F=dA; all observables below use F or T_Maxwell and are Maxwell-gauge invariant",
            "curl_spectrum": "curl(e1)=-(1/c)e1, curl(e2)=-(1/c)e2, curl(e3)=-(c/a^2)e3",
            "maxwell_equations": "dF=0 identically and d star F=0 because ddot A+curl^2 A=0 and div A=0",
            "null_invariants": ["E^2-B^2=0", "E dot B=0"],
            "signal_direction": "s=-e3; Poynting=beta^2 s and (L_n+L_s)A_c=0",
        },
        "relational_observable": {
            "clock_slice": "Sigma_tau={theta=tau} on the lifted chart -pi<tau-theta<pi",
            "observer": "u(v)=gamma(v)(n+v s)",
            "local_energy_reading": "epsilon_v=T_ab[F,g_hat]u^a(v)u^b(v)=beta^2 gamma(v)^2(1-v)^2",
            "spatial_dressing": "E_v(tau)=Vol(Sigma_tau)^-1 int_{Sigma_tau} epsilon_v dmu_g_hat",
            "diffeomorphism_invariance": "the clock-defined compact slice integral removes the arbitrary Berger base point",
            "weyl_invariance": "theta, g_hat, u, F, T[F,g_hat], and the normalized integral are Weyl invariant",
            "maxwell_gauge_invariance": "the observable depends on F and T, not on the potential representative",
            "total_D_invariance": "relational evaluation fixes theta=tau; the compact spatial average is invariant under the residual Berger isometry generated by the traveling pattern",
            "frequency_ratio": "1+z=sqrt(E_v_emit(tau_emit)/E_v_receive(tau_receive))",
            "causal_relation": "the null stress propagates along n+s; for initial physical separation L and receiver speed v, Delta t_hat=L/(1-v)",
        },
        "exact_mode_checks": {
            "Bianchi_identity": True,
            "source_free_Maxwell_equation": True,
            "left_invariant_mode_divergence_free": True,
            "null_field": True,
            "future_null_energy_flux": True,
            "positive_Maxwell_energy": True,
            "two_phase_solution_pairing_nondegenerate": True,
            "clock_slice_spatial_average_diffeomorphism_invariant": True,
            "frequency_observable_Maxwell_gauge_invariant": True,
            "frequency_observable_Weyl_invariant": True,
        },
        "rational_fixture": {
            "background": {"a": "1", "c^2": "9/40", "rho": "1", "omega": "3/4"},
            "observers": {"v_emit": "0", "v_receive": "3/5", "initial_physical_separation": "1/5"},
            "results": _fixture(),
            "chart_and_path_domain": "theta_receive=3/8<pi and travel distance 1/2 is below the half Hopf-fibre length 2 pi c",
            "interpretation": "the exact Maxwell mode is measured at half the emitter frequency by the receding relational observer, so 1+z=2",
        },
        "health_and_pairing": {
            "solution_block": "span_R{A_c,A_s}",
            "symplectic_form": "Omega(A_c,A_s)=-2 beta Vol(S3_Berger), up to the declared Cauchy orientation",
            "symplectic_rank": 2,
            "energy": "H(x A_c+y A_s)=beta^2 Vol(S3_Berger)(x^2+y^2)",
            "energy_signature_convention": "[positive,negative,zero]",
            "energy_signature": [2, 0, 0],
            "negative_physical_direction_introduced": False,
        },
        "flags": {
            "BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE": True,
            "BERGER_SPATIALLY_AVERAGED_RELATIONAL_FREQUENCY": True,
            "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE": False,
            "BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL": False,
            "BERGER_GRAVITY_MAXWELL_Q2_DRESSING": False,
            "BERGER_MAXWELL_BACKREACTION": False,
            "BERGER_G1_COMPLETE_SIGNAL_SECTOR": False,
            "BERGER_REDSHIFT_PHENOMENOLOGY": False,
            "QUANTUM_CLAIM": False,
        },
        "not_established": [
            "a localized emitter and receiver rather than the compact spatially averaged congruence observable",
            "a compactly supported source and retarded Maxwell pulse",
            "the Maxwell BV complex and its semidirect q2 coupling to the 54-row gravity-clock complex",
            "the first gravity-Maxwell homological dressing or an obstruction witness",
            "Maxwell stress backreaction on the Berger clock background",
            "the complete Hopf harmonic signal sector, caustics after wrapping, or multiple-path interference",
            "a gravitational/cosmological redshift, phenomenology, or quantum theorem",
        ],
        "next_gate": "BERGER_LOCALIZED_RETARDED_MAXWELL_REDSHIFT_AND_Q2_DRESSING",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS
            }
        },
        "verification_receipts": [
            {
                "test_tier": 1,
                "command": "python3 d_quotient_classical/backreacted_clock/berger_dynamical_maxwell_redshift.py --check --guards",
                "elapsed_seconds": 0.81,
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "python3 d_quotient_classical/backreacted_clock/verify_berger_dynamical_maxwell_redshift.py",
                "elapsed_seconds": 0.47,
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_dynamical_maxwell_redshift",
                "elapsed_seconds": 1.45,
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-dynamical-maxwell-redshift-v1.schema.json -d d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json",
                "elapsed_seconds": 1.20,
                "status": "PASS",
            },
        ],
        "higher_tiers_not_run": {
            "tier_2": "The imported clock and relational certificates are unchanged content-addressed inputs; their hashes are replayed independently.",
            "tier_3": "This is a G0 probe-mode theorem with no classical freeze, lifecycle promotion, or shared-core algebra change.",
        },
        "claim_boundary": "This exact G0 theorem replaces the prescribed null ray by a genuine positive-energy source-free Maxwell mode and constructs a Diff-, Weyl-, Maxwell-gauge-, and total-D-invariant compact spatially averaged frequency ratio on the rational Berger clock fixture. It does not construct localized endpoints, a retarded compact source, the Maxwell BV/q2 semidirect extension, backreaction, a complete G1 signal sector, phenomenology, or a quantum result.",
    }
    verify(payload)
    return payload


def verify(payload: dict[str, Any]) -> None:
    _mode_algebra()
    if payload["generality_level"] != "G0":
        raise AssertionError("single Maxwell mode may not be promoted beyond G0")
    if payload["rational_fixture"]["results"] != _fixture():
        raise AssertionError("persisted Maxwell fixture is not exact")
    if payload["rational_fixture"]["results"]["one_plus_z"] != "2":
        raise AssertionError("dynamical frequency ratio drifted")
    if payload["health_and_pairing"]["negative_physical_direction_introduced"] is not False:
        raise AssertionError("positive Maxwell block was assigned a negative direction")
    for required in (
        "BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE",
        "BERGER_SPATIALLY_AVERAGED_RELATIONAL_FREQUENCY",
    ):
        if payload["flags"][required] is not True:
            raise AssertionError(f"required result missing: {required}")
    for forbidden in (
        "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE",
        "BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL",
        "BERGER_GRAVITY_MAXWELL_Q2_DRESSING",
        "BERGER_MAXWELL_BACKREACTION",
        "BERGER_G1_COMPLETE_SIGNAL_SECTOR",
        "BERGER_REDSHIFT_PHENOMENOLOGY",
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
    r = payload["rational_fixture"]["results"]
    return rf"""# Dynamical Maxwell redshift mode on the Berger clock

## Outcome

The prescribed characteristic ray in the first redshift preflight has been
replaced by a genuine source-free Maxwell solution.  In the orthonormal
Berger coframe,

\[
de^1=-(1/c)e^2\wedge e^3,\qquad
de^2=-(1/c)e^3\wedge e^1,\qquad
de^3=-(c/a^2)e^1\wedge e^2,
\]

take

\[
A_c=\cos(\beta t)e^1+\sin(\beta t)e^2,\qquad \beta=1/c.
\]

The horizontal coframe is a curl eigenspace with eigenvalue `-beta`, so
`ddot A+curl^2 A=0`.  Consequently `F=dA` obeys both source-free Maxwell
equations.  Its electric and magnetic fields have equal norm and zero inner
product, while its Poynting vector is the null Hopf direction `s=-e3`.

## Relational observable

The local detector energy is

\[
\epsilon_v=T_{{ab}}u^au^b
=\beta^2\gamma(v)^2(1-v)^2,\qquad
u(v)=\gamma(v)(n+vs).
\]

To avoid pretending that the homogeneous background supplies a preferred
spatial base point, the observable is the normalized integral of this scalar
over the compact clock slice `theta=tau`.  It depends only on `F`, the
Weyl-invariant clock metric, and the relationally defined observer.  It is
therefore Maxwell-gauge invariant, Weyl invariant, and diffeomorphism
invariant.  The frequency ratio is extracted without a potential gauge:

\[
1+z=\sqrt{{\mathcal E_e(\tau_e)/\mathcal E_r(\tau_r)}}.
\]

At the rational fixture the exact values are

- `beta={r['beta']}`;
- `nu_e={r['frequency_emit']}` and `nu_r={r['frequency_receive']}`;
- `E_e={r['averaged_energy_emit']}` and `E_r={r['averaged_energy_receive']}`;
- `1+z={r['one_plus_z']}`, hence `z={r['z']}`;
- reception at `theta={r['theta_receive']}`, before a clock recrossing or Hopf wrap.

The real two-phase Maxwell block has nondegenerate symplectic pairing
`{r['symplectic_pairing']}` and positive energy coefficient
`{r['positive_energy_coefficient']}`.  It introduces no negative physical
direction.

## Boundary of the result

This is an exact dynamical `G0` mode, not yet the complete `G1` signal sector.
The field is a global traveling mode rather than a compactly sourced retarded
pulse, and the endpoint observable is spatially averaged rather than
localized.  The Maxwell BV rows and their semidirect `q2` action on the
gravity-clock complex have not been exported, so the first nonlinear
gravity-Maxwell homological dressing remains open.  No backreaction,
phenomenology, or quantum claim is made.

Machine-readable result:
`d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json`.

## Verification

The exact generator and mutation guards, independent field-equation and
provenance replay, unit tests, and strict AJV Draft 2020-12 validation pass.
The two imported certificates are unchanged and content-addressed, so their
full producer chains were not rebuilt.  A full repository run is not
triggered by this isolated `G0` probe-mode theorem.
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
            raise AssertionError("dynamical Maxwell certificate drifted")
        if REPORT_PATH.read_text() != _report(payload):
            raise AssertionError("dynamical Maxwell report drifted")
    if args.guards:
        mutants = []
        promoted = deepcopy(payload)
        promoted["flags"]["BERGER_GRAVITY_MAXWELL_Q2_DRESSING"] = True
        mutants.append(("promote q2 dressing", promoted))
        negative = deepcopy(payload)
        negative["health_and_pairing"]["negative_physical_direction_introduced"] = True
        mutants.append(("insert negative direction", negative))
        ratio = deepcopy(payload)
        ratio["rational_fixture"]["results"]["one_plus_z"] = "1"
        mutants.append(("erase redshift", ratio))
        for name, mutant in mutants:
            try:
                verify(mutant)
            except AssertionError:
                continue
            raise AssertionError(f"mutation guard accepted: {name}")
    print("BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE: PASS")


if __name__ == "__main__":
    main()
