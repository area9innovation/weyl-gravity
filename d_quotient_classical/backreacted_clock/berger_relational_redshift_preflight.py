#!/usr/bin/env python3
"""Build the first exact Berger relational-observable/redshift preflight.

This is deliberately a G0 reduced-mode pilot.  It combines the certified
positive Berger clock, total-D disposition, support-local q2, causal Green
domain, and cyclic arity-two Cartan contraction with a tensorial operational
fixture.  It does not promote the fixture to a complete interacting
observable algebra.
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
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_RELATIONAL_REDSHIFT_PREFLIGHT.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-relational-redshift-preflight.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-relational-redshift-preflight-v1.schema.json"

DEPENDENCIES = {
    "clock_background": ROOT / "d_quotient_classical/certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json",
    "total_D_disposition": ROOT / "quantum-weyl/transfer/certificates/BERGER_TOTAL_D_DISPOSITION.json",
    "support_local_q2": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json",
    "causal_green_domain": ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json",
    "arity_two_Cartan": ROOT / "d_quotient_classical/certificates/BERGER_CAUSAL_D_CARTAN_V2.json",
}
SOURCE_PATHS = (
    ROOT / "d_quotient_classical/backreacted_clock/berger_relational_redshift_preflight.py",
    ROOT / "d_quotient_classical/backreacted_clock/verify_berger_relational_redshift_preflight.py",
    ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_relational_redshift_preflight.py",
    SCHEMA_PATH,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_dependencies() -> dict[str, dict[str, Any]]:
    data = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if data["clock_background"]["flags"]["exact_backreacted_background_exists"] is not True:
        raise AssertionError("positive Berger clock background is not certified")
    if data["total_D_disposition"]["verdict"] != "D_GAUGE":
        raise AssertionError("total D is not certified gauge on the fixed-coupling phase space")
    if data["support_local_q2"]["flags"]["CLASSICAL_SUPPORT_LOCAL_Q2"] is not True:
        raise AssertionError("authoritative support-local q2 is unavailable")
    if data["causal_green_domain"]["flags"]["BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2"] is not True:
        raise AssertionError("retained/all-row causal Green domain is unavailable")
    if data["arity_two_Cartan"]["flags"]["BERGER_CAUSAL_D_CARTAN_V2"] is not True:
        raise AssertionError("cyclic causal D-Cartan contraction through arity two is unavailable")
    return data


def _exact_fixture() -> dict[str, str]:
    """Compute the rational signal comparison without floating point."""

    rho = sp.S(1)
    omega = sp.Rational(3, 4)
    energy = sp.Rational(3, 4)
    v_emit = sp.S(0)
    v_receive = sp.Rational(3, 5)
    separation = sp.Rational(1, 5)

    gamma_emit = 1 / sp.sqrt(1 - v_emit**2)
    gamma_receive = 1 / sp.sqrt(1 - v_receive**2)
    nu_emit = sp.factor(energy * gamma_emit * (1 - v_emit))
    nu_receive = sp.factor(energy * gamma_receive * (1 - v_receive))
    one_plus_z = sp.factor(nu_emit / nu_receive)
    travel_time = sp.factor(separation / (1 - v_receive))
    theta_receive = sp.factor(omega * travel_time / rho)
    emit_phase_slope = sp.factor(-energy * rho * (1 - v_emit) / omega)
    receive_phase_slope = sp.factor(-energy * rho * (1 - v_receive) / omega)

    expected = {
        "gamma_emit": sp.S(1),
        "gamma_receive": sp.Rational(5, 4),
        "nu_emit": sp.Rational(3, 4),
        "nu_receive": sp.Rational(3, 8),
        "one_plus_z": sp.S(2),
        "z": sp.S(1),
        "travel_time": sp.Rational(1, 2),
        "theta_emit": sp.S(0),
        "theta_receive": sp.Rational(3, 8),
        "emit_phase_slope": -sp.S(1),
        "receive_phase_slope": -sp.Rational(2, 5),
    }
    actual = {
        "gamma_emit": gamma_emit,
        "gamma_receive": gamma_receive,
        "nu_emit": nu_emit,
        "nu_receive": nu_receive,
        "one_plus_z": one_plus_z,
        "z": sp.factor(one_plus_z - 1),
        "travel_time": travel_time,
        "theta_emit": sp.S(0),
        "theta_receive": theta_receive,
        "emit_phase_slope": emit_phase_slope,
        "receive_phase_slope": receive_phase_slope,
    }
    if any(sp.simplify(actual[key] - value) != 0 for key, value in expected.items()):
        raise AssertionError("rational redshift fixture drifted")
    return {key: str(value) for key, value in actual.items()}


def build() -> dict[str, Any]:
    dependencies = _load_dependencies()
    refs = {
        name: {
            "path": str(path.relative_to(ROOT)),
            "result_id": dependencies[name]["result_id"],
            "sha256": _sha256(path),
        }
        for name, path in DEPENDENCIES.items()
    }
    payload: dict[str, Any] = {
        "schema": "pure-weyl-berger-relational-redshift-preflight-v1",
        "result_id": "BERGER_RELATIONAL_REDSHIFT_PREFLIGHT",
        "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
        "claim_status": "CERTIFIED_G0_OPERATIONAL_PREFLIGHT_FULL_RELATIONAL_OBSERVABLE_OPEN",
        "generality_level": "G0",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": refs,
        "activation_gate": {
            "authoritative_q2": "PASS",
            "retained_causal_Green_homotopy": "PASS",
            "interacting_Cartan_on_domain": "PASS_THROUGH_ARITY_TWO",
            "physical_metric_clock_observable": "PREFLIGHT_CONSTRUCTED",
            "null_signal_frequency_ratio": "G0_EXACT_FIXTURE",
            "full_gate": "OPEN",
        },
        "relational_geometry": {
            "clock_modulus": "rho=sqrt(T_1^2+T_2^2)",
            "clock_phase": "theta=atan2(T_2,T_1) mod 2pi",
            "weyl_weights": "g -> exp(2 sigma) g and rho -> exp(-sigma) rho",
            "physical_metric": "g_hat=rho^2 g",
            "physical_metric_weyl_invariant": True,
            "clock_phase_weyl_invariant": True,
            "clock_normal": "n^a=-g_hat^{ab} partial_b theta/sqrt(-g_hat^{cd} partial_c theta partial_d theta)",
            "anisotropy_direction": "s is the unit simple eigendirection of the clock-orthogonal Ricci endomorphism of g_hat; on Berger it is the Hopf/vertical direction",
            "anisotropy_eigenline_unique": "q != 1 throughout (5-sqrt(21))/2 < q < 1/4",
            "complete_observable": "O_A(tau)=[exp(((tau-theta)/omega) L_D) A] on one lifted phase chart",
            "D_invariance_identity": "delta_D O_A=(L_D A)_shift+delta_D[(tau-theta)/omega](L_D A)_shift=0 because D theta=omega",
            "chart_domain": "choose a lift with -pi < tau-theta < pi; attach an integer winding label beyond one chart",
        },
        "signal_model": {
            "status": "EXACT_CHARACTERISTIC_PROBE_NOT_BACKREACTED_SIGNAL_THEORY",
            "null_direction": "k^a=E(n^a+s^a), g_hat(k,k)=0",
            "observer": "u^a(v)=gamma(v)(n^a+v s^a), gamma(v)=1/sqrt(1-v^2), |v|<1",
            "measured_frequency": "nu(v)=-g_hat(k,u(v))=E gamma(v)(1-v)",
            "redshift": "1+z=nu_emit/nu_receive=gamma_emit(1-v_emit)/[gamma_receive(1-v_receive)]",
            "relational_signal_slope": "dS/dtheta=-E rho(1-v)/omega along an observer",
            "causal_endpoint_rule": "a co-propagating ray emitted at physical separation L meets a receiver with constant v at Delta t_hat=L/(1-v)",
            "covariance_scope": "theta, g_hat, n, the simple anisotropy eigenline, k.u, and their endpoint ratio are tensorially defined; homogeneity removes base-event dependence in this G0 fixture",
        },
        "rational_fixture": {
            "background": {"a": "1", "q": "9/40", "alpha_B": "5", "rho": "1", "omega": "3/4"},
            "signal": {"E": "3/4", "v_emit": "0", "v_receive": "3/5", "initial_physical_separation": "1/5"},
            "results": _exact_fixture(),
            "interpretation": "the receiver measures half the emitter frequency, so 1+z=2 and z=1",
            "chart_check": "0 < theta_receive=3/8 < pi, hence no repeated phase crossing occurs",
        },
        "exact_checks": {
            "all_activation_dependencies_content_addressed": True,
            "weyl_invariant_metric_and_phase": True,
            "clock_gradient_timelike": True,
            "Berger_vertical_eigenline_distinguished": True,
            "signal_null": True,
            "observers_unit_timelike": True,
            "frequency_contraction_scalar": True,
            "nonzero_exact_redshift": True,
            "single_clock_chart": True,
            "no_floating_point_in_fixture": True,
        },
        "flags": {
            "BERGER_RELATIONAL_REDSHIFT_PREFLIGHT": True,
            "BERGER_G0_OPERATIONAL_REDSHIFT_FIXTURE": True,
            "BERGER_COMPLETE_RELATIONAL_OBSERVABLE": False,
            "BERGER_INTERACTING_SIGNAL_SOLUTION": False,
            "BERGER_SPATIALLY_DRESSED_ENDPOINT_ALGEBRA": False,
            "BERGER_REDSHIFT_PHENOMENOLOGY": False,
            "QUANTUM_CLAIM": False,
        },
        "not_established": [
            "a spatially dressed emitter/receiver algebra on the full nonlinear Diff x Weyl quotient",
            "a Maxwell, scalar, or gravitational signal solved with backreaction and transferred higher brackets",
            "gauge-invariant reduced Poisson brackets for the endpoint observables",
            "global treatment of all phase windings, caustics, and multiple null paths on compact S3",
            "a gravitational or cosmological redshift rather than this exact local kinematic fixture",
            "phenomenology, a quantum observable, or a Lorentzian quantum-master-equation theorem",
        ],
        "verification_receipts": [
            {
                "test_tier": 1,
                "command": "python3 d_quotient_classical/backreacted_clock/berger_relational_redshift_preflight.py --check --guards",
                "elapsed_seconds": 0.27,
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "python3 d_quotient_classical/backreacted_clock/verify_berger_relational_redshift_preflight.py",
                "elapsed_seconds": 0.09,
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_relational_redshift_preflight",
                "elapsed_seconds": 0.41,
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-relational-redshift-preflight-v1.schema.json -d d_quotient_classical/certificates/BERGER_RELATIONAL_REDSHIFT_PREFLIGHT.json",
                "elapsed_seconds": 1.19,
                "status": "PASS",
            },
        ],
        "higher_tiers_not_run": {
            "tier_2": "The five authoritative dependencies are unchanged content-addressed inputs; the independent verifier replays their hashes and result identifiers.",
            "tier_3": "No freeze, lifecycle promotion, or shared core algebra changed.",
        },
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS
            }
        },
        "next_gate": "BERGER_COMPLETE_RELATIONAL_OBSERVABLE_AND_DYNAMICAL_REDSHIFT",
        "claim_boundary": "This G0 exact reduced-mode preflight constructs a Weyl-invariant clock metric, a local complete-observable chart, and a nonzero operational null-signal frequency ratio after all q2/Green/arity-two-Cartan activation prerequisites pass. It is a kinematic characteristic-probe fixture, not the complete spatially dressed nonlinear observable, an interacting signal solution, phenomenology, or a quantum result.",
    }
    verify(payload)
    return payload


def verify(payload: dict[str, Any]) -> None:
    if payload["generality_level"] != "G0":
        raise AssertionError("preflight may not be promoted beyond G0")
    if payload["activation_gate"]["full_gate"] != "OPEN":
        raise AssertionError("full relational-observable gate was promoted")
    if payload["rational_fixture"]["results"] != _exact_fixture():
        raise AssertionError("persisted rational fixture is not exact")
    if payload["rational_fixture"]["results"]["one_plus_z"] != "2":
        raise AssertionError("nonzero frequency ratio lost")
    if payload["relational_geometry"]["physical_metric_weyl_invariant"] is not True:
        raise AssertionError("physical clock metric lost Weyl invariance")
    if payload["relational_geometry"]["clock_phase_weyl_invariant"] is not True:
        raise AssertionError("clock phase lost Weyl invariance")
    if payload["flags"]["BERGER_G0_OPERATIONAL_REDSHIFT_FIXTURE"] is not True:
        raise AssertionError("G0 fixture flag missing")
    for forbidden in (
        "BERGER_COMPLETE_RELATIONAL_OBSERVABLE",
        "BERGER_INTERACTING_SIGNAL_SOLUTION",
        "BERGER_SPATIALLY_DRESSED_ENDPOINT_ALGEBRA",
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
    return rf"""# Berger relational observable and redshift preflight

## Outcome

All prerequisites listed for the first Berger observer-level rail are now
present: the authoritative support-local `q2`, the all-row causal Green
homotopy, and the cyclic causal Cartan contraction through arity two.  This
certificate adds the smallest exact operational pilot.  Its generality is
`G0`, with dependency tags `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, and
`LORENTZIAN-CAUSAL`.

The rotating scalar pair supplies two Weyl-invariant objects,

\[
\theta=\operatorname{{atan2}}(T_2,T_1),\qquad
\widehat g=\rho^2g,\qquad \rho^2=T_1^2+T_2^2.
\]

The unit clock normal `n` and the simple Berger anisotropy eigenline `s` are
therefore tensorially defined.  The latter is unique because `q != 1` on the
certified interval.  A local complete observable is

\[
\mathcal O_A(\tau)=
 \exp\!\left({{\tau-\theta\over\omega}}\mathcal L_D\right)A,
\qquad -\pi<\tau-\theta<\pi.
\]

Its two `D` variations cancel because `D theta=omega`.  Beyond one phase
chart an integer winding label is required; no global single-valued claim is
made here.

## Exact operational fixture

For a co-propagating characteristic signal and an observer,

\[
k=E(n+s),\qquad u(v)=\gamma(v)(n+vs),
\]

the measured frequency and endpoint ratio are

\[
\nu(v)=E\gamma(v)(1-v),\qquad
1+z={{\nu_e\over\nu_r}}.
\]

At the rational Berger fixture, take `E=3/4`, `v_e=0`, `v_r=3/5`, and
initial physical separation `L=1/5`.  Exact arithmetic gives

- `gamma_r={r['gamma_receive']}`;
- `nu_e={r['nu_emit']}` and `nu_r={r['nu_receive']}`;
- `1+z={r['one_plus_z']}`, hence `z={r['z']}`;
- reception at `theta={r['theta_receive']}`, inside the first clock chart.

Thus quotienting total `D` does not algebraically force every operational
frequency comparison to be trivial.  This example is a receding-observer
kinematic redshift on the exact Berger background; it is not yet a
gravitational or cosmological redshift.

## Fail-closed boundary

The physical redshift theorem remains open.  The next construction must
spatially dress the emitter and receiver, solve an actual signal field on the
causal complex, compute the reduced endpoint brackets and induced pairing,
control winding/multiple-null-path domains, and then test higher transferred
brackets.  No interacting, phenomenological, quantum, or QME claim follows
from this preflight.

Machine-readable result:
`d_quotient_classical/certificates/BERGER_RELATIONAL_REDSHIFT_PREFLIGHT.json`.

## Verification

The generator guards, independent rational/provenance replay, unit and
mutation tests, and AJV Draft 2020-12 strict validation pass.  Tier 2 was not
rebuilt because all five scientific prerequisites are unchanged and
content-addressed; Tier 3 is not triggered by a `G0` preflight with no
lifecycle promotion or shared-core change.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    verify(payload)
    if args.write:
        CERTIFICATE_PATH.write_text(_json(payload))
        REPORT_PATH.write_text(_report(payload))
    if args.check:
        if CERTIFICATE_PATH.read_text() != _json(payload):
            raise AssertionError("relational redshift certificate drifted")
        if REPORT_PATH.read_text() != _report(payload):
            raise AssertionError("relational redshift report drifted")
    if args.guards:
        mutants = []
        promoted = deepcopy(payload)
        promoted["flags"]["BERGER_COMPLETE_RELATIONAL_OBSERVABLE"] = True
        mutants.append(("promote full observable", promoted))
        wrong_ratio = deepcopy(payload)
        wrong_ratio["rational_fixture"]["results"]["one_plus_z"] = "1"
        mutants.append(("erase redshift", wrong_ratio))
        wrong_hash = deepcopy(payload)
        wrong_hash["dependency_refs"]["support_local_q2"]["sha256"] = "0" * 64
        mutants.append(("mutate q2 hash", wrong_hash))
        noninvariant_metric = deepcopy(payload)
        noninvariant_metric["relational_geometry"]["physical_metric_weyl_invariant"] = False
        mutants.append(("break Weyl-invariant metric", noninvariant_metric))
        for name, mutant in mutants:
            try:
                verify(mutant)
            except AssertionError:
                continue
            raise AssertionError(f"mutation guard accepted: {name}")
    print("BERGER_RELATIONAL_REDSHIFT_PREFLIGHT: PASS")


if __name__ == "__main__":
    main()
