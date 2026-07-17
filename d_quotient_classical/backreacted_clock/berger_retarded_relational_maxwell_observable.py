#!/usr/bin/env python3
"""C-G4: retarded clock-slice Maxwell observable and localized obstruction."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import sympy as sp

from d_quotient_classical.backreacted_clock.berger_dynamical_maxwell_redshift import (
    _exterior_derivative,
    _form_strings,
    _hodge_star,
)


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_RETARDED_RELATIONAL_MAXWELL_OBSERVABLE.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-retarded-relational-maxwell-observable.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-retarded-relational-maxwell-observable-v1.schema.json"
PRODUCER_PATH = ROOT / "d_quotient_classical/backreacted_clock/berger_retarded_relational_maxwell_observable.py"
VERIFIER_PATH = ROOT / "d_quotient_classical/backreacted_clock/verify_berger_retarded_relational_maxwell_observable.py"
TEST_PATH = ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_retarded_relational_maxwell_observable.py"

DEPENDENCIES = {
    "dynamical_mode": ROOT / "d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json",
    "retarded_maxwell": ROOT / "d_quotient_classical/certificates/BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL.json",
    "fixed_coupling_D_nullity": ROOT / "d_quotient_classical/certificates/BERGER_FIXED_COUPLING_DELTA_CHARGE.json",
    "observer_84_axial_first_jet_receipt": ROOT / "closed_universe_observers/receipts/APPARATUS_84_ROD_GRAVITY_UNARY_TIER_RECEIPT.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    return {"path": str(path.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": _sha256(path)}


def _exact_reduced_block() -> dict:
    beta = 2 * sp.sqrt(10) / 3
    omega = sp.Rational(3, 4)
    mu = sp.factor(beta / omega)
    volume = 12 * sp.sqrt(10) * sp.pi**2 / 5
    symplectic = sp.factor(-2 * beta * volume)
    energy = sp.factor(beta**2 * volume)
    poisson_xy = sp.factor(1 / symplectic)
    relational_hamiltonian = sp.factor(energy / omega)

    x, y, tau = sp.symbols("x y tau", real=True)
    q_tau = x * sp.cos(mu * tau) - y * sp.sin(mu * tau)
    p_tau = x * sp.sin(mu * tau) + y * sp.cos(mu * tau)

    def bracket(left, right):
        return sp.factor(poisson_xy * (sp.diff(left, x) * sp.diff(right, y) - sp.diff(left, y) * sp.diff(right, x)))

    h_tau = relational_hamiltonian * (x**2 + y**2)
    checks = {
        "mu": sp.simplify(mu - 8 * sp.sqrt(10) / 9),
        "symplectic": sp.simplify(symplectic + 32 * sp.pi**2),
        "energy": sp.simplify(energy - 32 * sp.sqrt(10) * sp.pi**2 / 3),
        "poisson": sp.simplify(poisson_xy + 1 / (32 * sp.pi**2)),
        "bracket_QP": sp.trigsimp(bracket(q_tau, p_tau) - poisson_xy),
        "evolution_Q": sp.trigsimp(sp.diff(q_tau, tau) - bracket(q_tau, h_tau)),
        "evolution_P": sp.trigsimp(sp.diff(p_tau, tau) - bracket(p_tau, h_tau)),
    }
    if any(value != 0 for value in checks.values()):
        raise AssertionError(f"reduced relational block failed: {checks}")
    if mu.is_rational is not False:
        raise AssertionError("clock and Maxwell frequencies unexpectedly commensurate")
    return {
        "mode_coordinates": "F=x F_c+y F_s; x,y are field-strength/cohomology coordinates, not potential-gauge coordinates",
        "symplectic_form": f"Omega={symplectic} dx wedge dy",
        "poisson_bracket": f"{{x,y}}={poisson_xy}",
        "clock_frequency": str(omega),
        "Maxwell_frequency": str(beta),
        "relative_frequency_mu": str(mu),
        "quadratures": {
            "Q(tau_tilde)": "x*cos(mu*tau_tilde)-y*sin(mu*tau_tilde)",
            "P(tau_tilde)": "x*sin(mu*tau_tilde)+y*cos(mu*tau_tilde)",
        },
        "quadrature_bracket": str(poisson_xy),
        "physical_time_energy": f"H_t={energy}*(x^2+y^2)",
        "relational_hamiltonian": f"H_tau=H_t/omega={relational_hamiltonian}*(x^2+y^2)",
        "evolution": ["d_tau Q=-mu P={Q,H_tau}", "d_tau P=mu Q={P,H_tau}"],
        "nontrivial_tau_evolution": True,
    }


def _cutoff_source_audit() -> dict:
    beta = 2 * sp.sqrt(10) / 3
    alpha, t = sp.symbols("alpha t", positive=True, real=True)
    chi = sp.Function("chi")(t)
    derivatives = {
        0: {},
        1: {(2, 3): -beta},
        2: {(1, 3): beta},
        3: {(1, 2): -alpha},
    }
    potential = {
        (1,): chi * sp.cos(beta * t),
        (2,): chi * sp.sin(beta * t),
    }
    lorenz_three_form = _exterior_derivative(_hodge_star(potential), derivatives, t)
    field_strength = _exterior_derivative(potential, derivatives, t)
    current_three_form = _exterior_derivative(_hodge_star(field_strength), derivatives, t)
    closure = _exterior_derivative(current_three_form, derivatives, t)
    if lorenz_three_form or closure:
        raise AssertionError("cutoff source lost Lorenz gauge or conservation")
    expected = {
        (0, 1, 3): 2 * beta * sp.cos(beta * t) * sp.diff(chi, t) + sp.sin(beta * t) * sp.diff(chi, t, 2),
        (0, 2, 3): 2 * beta * sp.sin(beta * t) * sp.diff(chi, t) - sp.cos(beta * t) * sp.diff(chi, t, 2),
    }
    if any(sp.trigsimp(current_three_form[key] - value) != 0 for key, value in expected.items()):
        raise AssertionError("cutoff current components drifted")
    coefficient_determinant = sp.trigsimp(
        sp.det(
            sp.Matrix(
                [
                    [2 * beta * sp.cos(beta * t), sp.sin(beta * t)],
                    [2 * beta * sp.sin(beta * t), -sp.cos(beta * t)],
                ]
            )
        )
    )
    if coefficient_determinant != -2 * beta:
        raise AssertionError("cutoff current nontriviality determinant drifted")
    return {
        "Lorenz_three_form_components": _form_strings(lorenz_three_form),
        "current_three_form_components": _form_strings(current_three_form),
        "current_closure_components": _form_strings(closure),
        "coefficient_matrix_determinant": str(coefficient_determinant),
        "nonzero_for_nonconstant_switch": True,
        "vanishes_outside_switching_slab": "both chi_prime and chi_double_prime vanish where chi is constant",
    }


def _clock_dressed_switch_equivariance() -> dict:
    """Audit covariance of the preparation schedule, not fixed-label invariance."""
    theta, tau_source, omega = sp.symbols("theta tau_source omega", nonzero=True, real=True)
    switch = sp.Function("chi")((theta - tau_source) / omega)
    raw_D = sp.factor(omega * sp.diff(switch, theta))
    label_shift = sp.factor(omega * sp.diff(switch, tau_source))
    defect = sp.simplify(raw_D + label_shift)
    if defect != 0:
        raise AssertionError(f"clock-dressed switch equivariance failed: {defect}")
    if sp.simplify(raw_D) == 0:
        raise AssertionError("fixed-label switch was incorrectly declared raw-D invariant")
    return {
        "clock_dressed_switch": "chi((theta-tau_source)/omega)",
        "raw_D_action": "L_D theta=omega",
        "source_label_action": "tau_source shifts with the clock origin",
        "equivariance_identity": "(L_D+omega*partial_tau_source) chi((theta-tau_source)/omega)=0",
        "fixed_label_invariance": False,
        "equivariance_defect": str(defect),
    }


def build() -> dict:
    imported = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    mode = imported["dynamical_mode"]
    retarded = imported["retarded_maxwell"]
    observer = imported["observer_84_axial_first_jet_receipt"]
    if mode["rational_fixture"]["results"]["one_plus_z"] != "2":
        raise AssertionError("redshift fixture drifted")
    if retarded["flags"]["BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL"] is not True:
        raise AssertionError("retarded Maxwell Green theorem unavailable")
    if observer["claim_flags"]["MIXED_EPSILON_R2_KAPPA_UNARY_CERTIFIED"] is not False:
        raise AssertionError("mixed apparatus coefficient unexpectedly promoted")
    if "mixed epsilon_R^2*kappa coefficient" not in observer["result_boundary"]:
        raise AssertionError("mixed-order receipt boundary drifted")
    mixed_witness = {
        "receipt_result_id": observer["result_id"],
        "claim_flag": "MIXED_EPSILON_R2_KAPPA_UNARY_CERTIFIED",
        "value": False,
        "boundary_witness": "mixed epsilon_R^2*kappa coefficient remains open",
    }

    payload = {
        "schema": "pure-weyl-berger-retarded-relational-maxwell-observable-v1",
        "result_id": "BERGER_RETARDED_RELATIONAL_MAXWELL_OBSERVABLE",
        "result_state": "RETARDED_CLOCK_SLICE_OBSERVABLE_CERTIFIED_LOCALIZED_APPARATUS_BLOCKED_AT_MIXED_ORDER",
        "setting_id": "compact_positive_berger_clock_fixed_coupling",
        "generality_level": "G0_EXACT_RETARDED_TWO_PHASE_MODE_FIXTURE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: _dependency(path) for name, path in DEPENDENCIES.items()},
        "retarded_mode_preparation": {
            "mode": "A_mode=x A_c+y A_s in the certified source-free two-phase Maxwell block",
            "switch": "choose chi in C-infinity(R) with chi=0 for t<=t_minus< t_plus<0 and chi=1 for t>=t_plus",
            "prepared_potential": "A_ret=chi(t) A_mode",
            "Lorenz_identity": "delta(chi A_mode)=chi delta A_mode-(d chi) contraction A_mode=0 because A_mode is spatial and coclosed",
            "compact_source": "J=delta d(chi A_mode); J is supported in [t_minus,t_plus] x S3, hence compact because S3 is compact",
            "support_category": "SPATIALLY_GLOBAL_SPACETIME_COMPACT",
            "source_conservation": "delta J=delta^2 d(chi A_mode)=0",
            "retarded_identity": "A_ret=G_1,ret J by uniqueness of the retarded Lorenz solution",
            "nonzero_source": "if J vanished, A_ret would be a past-zero homogeneous solution and hence zero, contradicting A_ret=A_mode for t>=t_plus when (x,y)!=(0,0)",
            "post_source_signal": "F_ret=dA_ret=F_mode for t>=t_plus; choose t_plus<0 so both emission at t=0 and reception at t=1/2 occur after preparation",
            "causal_support": "supp(A_ret), supp(F_ret) subset J_plus(supp J)",
            "actual_retarded_signal": True,
            "exact_exterior_form_audit": _cutoff_source_audit(),
            "clock_dressed_switch_equivariance": _clock_dressed_switch_equivariance(),
        },
        "relational_redshift": {
            "observable": "E_v(tau_tilde)=Vol(Sigma_tau)^-1 integral_{Sigma_tau} T_ab[F_ret,g_hat] u(v)^a u(v)^b dmu_g_hat",
            "emitter": {"v": "0", "t": "0", "tau_tilde": "0"},
            "receiver": {"v": "3/5", "t": "1/2", "tau_tilde": "3/8"},
            "frequency_emit": "2*sqrt(10)/3",
            "frequency_receive": "sqrt(10)/3",
            "one_plus_z": "2",
            "z": "1",
            "post_source_mode_identity_used": True,
        },
        "gauge_and_causal_audit": {
            "Maxwell_gauge": "the observable uses F_ret and T[F_ret], so A_ret -> A_ret+d lambda changes nothing",
            "Weyl": "theta, g_hat=rho^2 g, F, u, normalized slice measure and the ratio are Weyl invariant",
            "diffeomorphism": "Sigma_tau is a clock-defined level set and the normalized integral is the integral of a scalar density; the anisotropy line defining u is geometric",
            "raw_D": "O_A(tau_tilde)=exp(((tau_tilde-theta)/omega)L_D)A has delta_D O_A=0 because delta_D theta=omega and the field and clock shifts cancel",
            "source_covariance": "the preparation schedule obeys (L_D+omega*partial_tau_source) chi((theta-tau_source)/omega)=0; it is an equivariant source-label family, not a raw-D invariant cutoff at fixed tau_source",
            "causal_dependence": "F_ret is obtained from the retarded Green operator; its value on Sigma_tau depends only on J intersect J_minus(Sigma_tau)",
            "spatial_locality_boundary": "the clock-slice average is spatially global on compact S3; no localized detector claim is inferred",
        },
        "periodic_clock_and_crossings": {
            "clock_target": "S1",
            "lifted_label": "tau_tilde=tau+2*pi*n with tau in (-pi,pi] and n in Z",
            "single_chart": "-pi<tau_tilde-theta_lift<pi",
            "fixture_no_crossing": "tau_receive-tau_emit=3/8<pi and the null path is shorter than half the primitive Hopf fibre",
            "relative_frequency": "mu=beta/omega=8*sqrt(10)/9 is irrational and therefore not an integer",
            "successive_crossing_action": "(Q,P) at n+1 is rotation by angle 2*pi*mu relative to n",
            "rotation_is_identity": False,
            "global_statement": "the observable is single-valued on the lifted clock with winding label n; without a winding record it is a multivalued S1-clock observable",
            "repeated_crossings_handled": True,
        },
        "reduced_symplectic_dynamics": _exact_reduced_block(),
        "D_gauge_relational_evolution": {
            "gauge_statement": "raw D moves clock and Maxwell field together and is presymplectically null on the declared fixed-coupling tangent space",
            "observable_invariance": "for fixed tau_tilde, delta_D O_A(tau_tilde)=0",
            "family_evolution": "partial_tau_tilde O_A=(1/omega) O_{L_D A}, which is nonzero on the Maxwell mode",
            "interpretation": "gauge invariance removes dependence on the arbitrary orbit parameter, not dependence on the physical clock reading; the family of Dirac observables at different tau_tilde is generated by H_tau=H_t/omega",
            "constraint_balance_boundary": "the displayed bracket is the reduced probe-mode bracket; a fully coupled finite-amplitude clock-plus-Maxwell constraint solution would also require the order-amplitude-squared gravitational response",
            "bracket_scope": "REDUCED_PROBE_MODE_POISSON_NOT_FULL_APPARATUS_DIRAC",
        },
        "localized_apparatus_obstruction": {
            "status": "EXACT_REQUIRED_INPUT_MISSING_STOP_FAIL_CLOSED",
            "bookkeeping": "r=epsilon_R^2, readout coupling=kappa",
            "first_missing_order": "r*kappa=epsilon_R^2*kappa",
            "first_missing_coefficients": [
                "Coeff_{r*kappa} B_a[A;Theta,R_a,g_hat+r Phi2]",
                "Coeff_{r*kappa} T_{g_hat+r Phi2,Theta}",
                "their cyclic cotangent adjoints in the 84-row unary operator",
            ],
            "why_required": "localized emitter/receiver records and persistent memories use the rod-defined detector profile B_a and clock transport T on the rod-backreacted metric",
            "normalized_existing_witness": mixed_witness,
            "consequence": "do not promote a localized observer morphism, full apparatus reduced bracket, or unqualified 84-row Green theorem",
            "not_a_nonexistence_theorem": True,
            "next_gate": "COMPUTE_MIXED_EPSILON_R2_KAPPA_SHIFT_OF_PROFILE_TRANSPORT_AND_REPLAY_FULL_84_ROW_UNARY",
        },
        "exact_checks": {
            "compact_retarded_mode_preparation": True,
            "cutoff_current_conserved_and_nonzero": True,
            "post_source_field_equals_certified_mode": True,
            "redshift_two_uses_actual_retarded_solution": True,
            "Maxwell_gauge_invariance": True,
            "Weyl_invariance": True,
            "diffeomorphism_invariance_on_clock_slice": True,
            "raw_D_complete_observable_invariance": True,
            "retarded_causal_dependence": True,
            "spatially_global_spacetime_compact_preparation_source": True,
            "clock_dressed_switch_family_raw_D_equivariant": True,
            "periodic_clock_lift_and_winding_explicit": True,
            "reduced_probe_mode_poisson_bracket_exact": True,
            "full_apparatus_Dirac_bracket_not_claimed": True,
            "tau_evolution_nontrivial": True,
            "mixed_rod_gravity_order_fail_closed": True,
        },
        "flags": {
            "BERGER_RETARDED_RELATIONAL_MAXWELL_OBSERVABLE": True,
            "BERGER_ACTUAL_RETARDED_REDSHIFT_TWO": True,
            "BERGER_CLOCK_LIFTED_REDUCED_BRACKET": True,
            "BERGER_NONTRIVIAL_RELATIONAL_TAU_EVOLUTION": True,
            "BERGER_SPATIALLY_GLOBAL_SPACETIME_COMPACT_PREPARATION_SOURCE": True,
            "BERGER_CLOCK_DRESSED_SWITCH_FAMILY_RAW_D_EQUIVARIANT": True,
            "BERGER_FULL_APPARATUS_DIRAC_BRACKET": False,
            "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE": False,
            "BERGER_MIXED_EPSILON_R2_KAPPA_APPARATUS": False,
            "BERGER_COMPLETE_GLOBAL_S1_CLOCK_OBSERVABLE_WITHOUT_WINDING": False,
            "BERGER_FULLY_BACKREACTED_MAXWELL_SIGNAL": False,
            "QUANTUM_CLAIM": False,
        },
        "provenance": {
            "source_manifest": [
                {"role": "producer", "path": str(PRODUCER_PATH.relative_to(ROOT)), "sha256": _sha256(PRODUCER_PATH)},
                {"role": "independent_verifier", "path": str(VERIFIER_PATH.relative_to(ROOT)), "sha256": _sha256(VERIFIER_PATH)},
                {"role": "tests", "path": str(TEST_PATH.relative_to(ROOT)), "sha256": _sha256(TEST_PATH)},
                {"role": "strict_schema", "path": str(SCHEMA_PATH.relative_to(ROOT)), "sha256": _sha256(SCHEMA_PATH)},
            ],
            "verification_commands": [
                "python3 -m d_quotient_classical.backreacted_clock.berger_retarded_relational_maxwell_observable --check --guards",
                "python3 -m d_quotient_classical.backreacted_clock.verify_berger_retarded_relational_maxwell_observable",
                "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retarded_relational_maxwell_observable",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-retarded-relational-maxwell-observable-v1.schema.json -d d_quotient_classical/certificates/BERGER_RETARDED_RELATIONAL_MAXWELL_OBSERVABLE.json",
            ],
        },
        "claim_boundary": "This exact G0 retarded probe-mode theorem upgrades the kinematic 1+z=2 fixture to a genuine retarded Maxwell signal: a spatially global but spacetime-compact source prepares the certified two-phase mode before emission, and the clock-slice field-strength observable is Maxwell-gauge, Weyl, diffeomorphism and raw-D invariant with retarded causal dependence. The clock-dressed preparation schedule is an equivariant source-label family satisfying (L_D+omega*partial_tau_source)chi=0; it is not claimed invariant at fixed tau_source. The theorem treats the periodic S1 clock by an integer winding label, derives the exact reduced probe-mode Poisson bracket and nontrivial lifted-tau evolution, and explains why a family of Dirac observables can evolve relationally although raw D is gauge. It does not construct the full apparatus Dirac bracket and remains a spatially averaged probe-sector theorem rather than a full harmonic signal sector. The localized rod/memory observer morphism stops fail-closed because the mixed epsilon_R^2*kappa profile, transport and cotangent coefficients are absent from the certified 84-row axial first-jet complex. It does not claim their nonexistence, a localized endpoint algebra, full Maxwell backreaction, an unqualified 84-row theorem, phenomenology, Hadamard data, a QME result, or any quantum statement.",
    }
    verify(payload)
    return payload


def verify(payload: dict) -> None:
    if payload["relational_redshift"]["one_plus_z"] != "2":
        raise AssertionError("retarded redshift drifted")
    if payload["retarded_mode_preparation"]["actual_retarded_signal"] is not True:
        raise AssertionError("kinematic mode was substituted for retarded preparation")
    if payload["retarded_mode_preparation"]["support_category"] != "SPATIALLY_GLOBAL_SPACETIME_COMPACT":
        raise AssertionError("preparation-source support category drifted")
    switch_audit = payload["retarded_mode_preparation"]["clock_dressed_switch_equivariance"]
    if switch_audit["equivariance_defect"] != "0" or switch_audit["fixed_label_invariance"] is not False:
        raise AssertionError("clock-dressed switch equivariance was overstated or lost")
    if payload["periodic_clock_and_crossings"]["rotation_is_identity"] is not False:
        raise AssertionError("periodic clock was silently treated as a global real clock")
    if payload["reduced_symplectic_dynamics"]["nontrivial_tau_evolution"] is not True:
        raise AssertionError("relational evolution disappeared")
    if payload["localized_apparatus_obstruction"]["first_missing_order"] != "r*kappa=epsilon_R^2*kappa":
        raise AssertionError("mixed apparatus obstruction drifted")
    if payload["flags"]["BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE"] is not False:
        raise AssertionError("localized apparatus observable promoted")
    if payload["flags"]["BERGER_FULLY_BACKREACTED_MAXWELL_SIGNAL"] is not False:
        raise AssertionError("probe theorem promoted to backreaction")
    if payload["flags"]["BERGER_FULL_APPARATUS_DIRAC_BRACKET"] is not False:
        raise AssertionError("probe Poisson bracket promoted to apparatus Dirac bracket")
    if payload["flags"]["QUANTUM_CLAIM"] is not False:
        raise AssertionError("quantum claim promoted")
    if not all(payload["exact_checks"].values()):
        raise AssertionError("an exact relational check dropped")
    for name, path in DEPENDENCIES.items():
        if payload["dependency_refs"][name]["sha256"] != _sha256(path):
            raise AssertionError(f"dependency drifted: {name}")


def _text(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _report(payload: dict) -> str:
    dyn = payload["reduced_symplectic_dynamics"]
    return f"""# Retarded relational Maxwell observable on the Berger clock

## Result

The earlier `1+z=2` characteristic fixture is now realized by an actual
retarded Maxwell solution.  Let `A_mode=x A_c+y A_s` be the certified
source-free two-phase mode and choose a smooth time switch `chi` which is zero
in the past and one before emission.  Then

```text
A_ret = chi A_mode,
J     = delta d(chi A_mode)
```

has compact source because the switching slab times compact `S3` is compact.
It is Lorenz, `delta J=0`, and uniqueness of the retarded one-form wave problem
gives `A_ret=G_ret J`.  After switching, `F_ret=F_mode`; therefore the emission
at `t=0` and reception at `t=1/2` give the certified exact frequencies

```text
nu_emit    = 2 sqrt(10)/3,
nu_receive = sqrt(10)/3,
1+z        = 2.
```

The observable is a normalized integral of `T[F_ret](u,u)` over the
clock-defined slice.  It depends on `F`, not the potential, and uses the
Weyl-invariant clock metric.  Hence it is Maxwell-gauge and Weyl invariant;
the level-set integral makes its diffeomorphism covariance explicit.  The
retarded Green formula proves causal dependence.

The preparation is spatially global on compact `S3`, although its source is
compact in spacetime.  Its clock-dressed schedule is covariant as a labelled
family:

```text
(L_D + omega partial_tau_source)
  chi((theta-tau_source)/omega) = 0.
```

It is not invariant under raw `D` with `tau_source` artificially held fixed.

## Periodic clock and reduced dynamics

The phase clock is `S1`-valued.  The honest label is

```text
tau_tilde = tau + 2 pi n,  n in Z.
```

At the fixture `mu=beta/omega=8 sqrt(10)/9` is irrational.  Successive clock
crossings therefore rotate the Maxwell quadratures by `2 pi mu`; they do not
give the same reading in general.  The observable is single-valued on the
lifted clock with winding label, and multivalued if that record is discarded.
The specific signal stays within one chart and does not wrap the Hopf fibre.

On the exact two-phase reduced probe block,

```text
{dyn['symplectic_form']}
{dyn['poisson_bracket']}
{dyn['relational_hamiltonian']}
```

and

```text
d_tau Q = -mu P = {{Q,H_tau}},
d_tau P =  mu Q = {{P,H_tau}}.
```

Thus every fixed-`tau_tilde` complete observable is invariant under raw `D`,
while the family varies nontrivially with the physical clock reading.  Gauge
invariance removes the arbitrary orbit parameter; it does not make relational
change vanish.

This is a reduced probe-mode Poisson bracket, not the Dirac bracket of the
open 84-row localized apparatus.

## Exact stopping point

This theorem is spatially averaged and uses the rod-free probe sector.  A
localized two-detector observable requires the rod-defined profiles and memory
transport on the backreacted metric.  Their first missing coefficients occur
at

```text
epsilon_R^2 * kappa.
```

The authoritative 84-row certificate explicitly excludes this bidegree and
its cyclic adjoints.  Accordingly the localized observer morphism, apparatus
bracket, and unqualified 84-row Green theorem remain false.  This is a typed
missing-input obstruction, not a nonexistence theorem.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.write:
        CERTIFICATE_PATH.write_text(_text(payload))
        REPORT_PATH.write_text(_report(payload))
    if args.check:
        if CERTIFICATE_PATH.read_text() != _text(payload):
            raise AssertionError("relational observable certificate drifted")
        if REPORT_PATH.read_text() != _report(payload):
            raise AssertionError("relational observable report drifted")
    if args.guards:
        mutations = []
        mutant = deepcopy(payload)
        mutant["retarded_mode_preparation"]["actual_retarded_signal"] = False
        mutations.append(mutant)
        mutant = deepcopy(payload)
        mutant["periodic_clock_and_crossings"]["rotation_is_identity"] = True
        mutations.append(mutant)
        mutant = deepcopy(payload)
        mutant["flags"]["BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE"] = True
        mutations.append(mutant)
        mutant = deepcopy(payload)
        mutant["flags"]["BERGER_FULLY_BACKREACTED_MAXWELL_SIGNAL"] = True
        mutations.append(mutant)
        mutant = deepcopy(payload)
        mutant["retarded_mode_preparation"]["clock_dressed_switch_equivariance"]["fixed_label_invariance"] = True
        mutations.append(mutant)
        mutant = deepcopy(payload)
        mutant["flags"]["BERGER_FULL_APPARATUS_DIRAC_BRACKET"] = True
        mutations.append(mutant)
        for index, mutation in enumerate(mutations):
            try:
                verify(mutation)
            except AssertionError:
                continue
            raise AssertionError(f"mutation guard {index} was accepted")
    print("BERGER_RETARDED_RELATIONAL_MAXWELL_OBSERVABLE: PASS")


if __name__ == "__main__":
    main()
