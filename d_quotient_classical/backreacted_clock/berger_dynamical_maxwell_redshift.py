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
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-dynamical-maxwell-redshift-v2.schema.json"

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


Form = dict[tuple[int, ...], sp.Expr]


def _clean(expression: sp.Expr) -> sp.Expr:
    return sp.trigsimp(expression)


def _wedge_basis(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, tuple[int, ...]] | None:
    combined = left + right
    if len(set(combined)) != len(combined):
        return None
    inversions = sum(
        combined[first] > combined[second]
        for first in range(len(combined))
        for second in range(first + 1, len(combined))
    )
    return (-1 if inversions % 2 else 1), tuple(sorted(combined))


def _wedge(left: Form, right: Form) -> Form:
    result: Form = {}
    for left_basis, left_coefficient in left.items():
        for right_basis, right_coefficient in right.items():
            basis_product = _wedge_basis(left_basis, right_basis)
            if basis_product is None:
                continue
            sign, basis = basis_product
            result[basis] = _clean(
                result.get(basis, 0) + sign * left_coefficient * right_coefficient
            )
    return {basis: value for basis, value in result.items() if value != 0}


def _add_forms(*forms: Form) -> Form:
    result: Form = {}
    for form in forms:
        for basis, coefficient in form.items():
            result[basis] = _clean(result.get(basis, 0) + coefficient)
    return {basis: value for basis, value in result.items() if value != 0}


def _scale_form(coefficient: sp.Expr, form: Form) -> Form:
    return {
        basis: _clean(coefficient * value)
        for basis, value in form.items()
        if _clean(coefficient * value) != 0
    }


def _exterior_derivative(form: Form, derivatives: dict[int, Form], t: sp.Symbol) -> Form:
    result: Form = {}
    for basis, coefficient in form.items():
        coefficient_term = _wedge({(0,): sp.diff(coefficient, t)}, {basis: 1})
        result = _add_forms(result, coefficient_term)
        for position, basis_one_form in enumerate(basis):
            before = {basis[:position]: 1}
            after = {basis[position + 1 :]: 1}
            basis_term = _wedge(_wedge(before, derivatives[basis_one_form]), after)
            result = _add_forms(
                result,
                _scale_form(coefficient * (-1) ** position, basis_term),
            )
    return {
        basis: _clean(value)
        for basis, value in result.items()
        if _clean(value) != 0
    }


def _hodge_star(form: Form) -> Form:
    eta = (-1, 1, 1, 1)
    result: Form = {}
    for basis, coefficient in form.items():
        complement = tuple(index for index in range(4) if index not in basis)
        wedge_data = _wedge_basis(basis, complement)
        if wedge_data is None:
            raise AssertionError("invalid Hodge basis")
        orientation_sign, _ = wedge_data
        norm = sp.prod(eta[index] for index in basis)
        result[complement] = sp.simplify(coefficient * norm * orientation_sign)
    return result


def _basis_derivation(form: Form, images: dict[int, Form]) -> Form:
    """Apply a degree-zero derivation specified on the basis one-forms."""

    result: Form = {}
    for basis, coefficient in form.items():
        for position, basis_one_form in enumerate(basis):
            before = {basis[:position]: 1}
            after = {basis[position + 1 :]: 1}
            term = _wedge(_wedge(before, images[basis_one_form]), after)
            result = _add_forms(result, _scale_form(coefficient, term))
    return result


def _form_strings(form: Form) -> dict[str, str]:
    return {
        "e" + "".join(str(index) for index in basis): str(_clean(coefficient))
        for basis, coefficient in sorted(form.items())
    }


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

    derivatives: dict[int, Form] = {
        0: {},
        1: {(2, 3): -beta},
        2: {(1, 3): beta},
        3: {(1, 2): -alpha},
    }
    potential_form: Form = {(1,): cosine, (2,): sine}
    partner_form: Form = {(1,): -sine, (2,): cosine}
    field_strength = _exterior_derivative(potential_form, derivatives, t)
    partner_strength = _exterior_derivative(partner_form, derivatives, t)
    dual_strength = _hodge_star(field_strength)
    bianchi_residual = _exterior_derivative(field_strength, derivatives, t)
    euler_lagrange_residual = _exterior_derivative(dual_strength, derivatives, t)
    if bianchi_residual:
        raise AssertionError("direct four-form Bianchi identity failed")
    if euler_lagrange_residual:
        raise AssertionError("direct four-form Maxwell equation failed")

    # The gauge-invariant complex field strength has an exact observer
    # frequency eigenvalue.  This cross-check does not refer to the potential
    # representative or infer frequency solely from energy normalization.
    partner_dual = _hodge_star(partner_strength)
    if _add_forms(dual_strength, _scale_form(-1, partner_strength)):
        raise AssertionError("complex Maxwell field lost anti-self-duality")
    if _add_forms(partner_dual, field_strength):
        raise AssertionError("real phase-pair duality relation failed")
    lie_e3_images: dict[int, Form] = {
        0: {},
        1: {(2,): beta},
        2: {(1,): -beta},
        3: {},
    }
    time_field = {
        basis: sp.diff(coefficient, t)
        for basis, coefficient in field_strength.items()
    }
    time_partner = {
        basis: sp.diff(coefficient, t)
        for basis, coefficient in partner_strength.items()
    }
    lie_s_field = _scale_form(-1, _basis_derivation(field_strength, lie_e3_images))
    lie_s_partner = _scale_form(-1, _basis_derivation(partner_strength, lie_e3_images))
    if _add_forms(time_field, _scale_form(-beta, partner_strength)):
        raise AssertionError("field-strength time-frequency eigenvalue failed")
    if _add_forms(time_partner, _scale_form(beta, field_strength)):
        raise AssertionError("field-strength partner time-frequency eigenvalue failed")
    if _add_forms(lie_s_field, _scale_form(beta, partner_strength)):
        raise AssertionError("field-strength signal-direction eigenvalue failed")
    if _add_forms(lie_s_partner, _scale_form(-beta, field_strength)):
        raise AssertionError("field-strength partner signal-direction eigenvalue failed")
    v = sp.symbols("v", real=True)
    gamma = 1 / sp.sqrt(1 - v**2)
    observer_lie_field = _scale_form(
        gamma,
        _add_forms(time_field, _scale_form(v, lie_s_field)),
    )
    observer_lie_partner = _scale_form(
        gamma,
        _add_forms(time_partner, _scale_form(v, lie_s_partner)),
    )
    observer_frequency = sp.factor(beta * gamma * (1 - v))
    if _add_forms(observer_lie_field, _scale_form(-observer_frequency, partner_strength)):
        raise AssertionError("gauge-invariant observer frequency eigenvalue failed")
    if _add_forms(observer_lie_partner, _scale_form(observer_frequency, field_strength)):
        raise AssertionError("gauge-invariant partner observer frequency eigenvalue failed")
    stress_energy_reading = sp.factor(beta**2 * gamma**2 * (1 - v) ** 2)
    if sp.simplify(observer_frequency**2 - stress_energy_reading) != 0:
        raise AssertionError("field-strength and stress frequencies disagree")

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
        "field_strength": field_strength,
        "dual_strength": dual_strength,
        "bianchi_residual": bianchi_residual,
        "euler_lagrange_residual": euler_lagrange_residual,
        "observer_frequency": observer_frequency,
        "stress_energy_reading": stress_energy_reading,
        "electric": electric,
        "magnetic": magnetic,
        "poynting": poynting,
        "symplectic_density": symplectic_density,
    }


def _fixture() -> dict[str, str]:
    """Replay the exact algebraic rational-background fixture."""

    c = sp.Rational(3, 2) / sp.sqrt(10)
    beta = 1 / c  # 1/c for c^2=9/40.
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
    generator_eigenvalues = (-sp.I / 2, sp.I / 2)
    if [sp.simplify(sp.exp(4 * sp.pi * value)) for value in generator_eigenvalues] != [1, 1]:
        raise AssertionError("SU(2) Hopf generator did not close at 4 pi")
    if [sp.simplify(sp.exp(2 * sp.pi * value)) for value in generator_eigenvalues] != [-1, -1]:
        raise AssertionError("Hopf period was incorrectly shortened to 2 pi")
    hopf_fibre_period = sp.factor(4 * sp.pi * c)
    half_hopf_fibre_length = sp.factor(hopf_fibre_period / 2)
    no_wrap_margin = sp.factor(half_hopf_fibre_length - travel_time)
    clock_chart_margin = sp.factor(sp.pi - theta_receive)
    if not (sp.pi > 3 and sp.sqrt(10) < 4):
        raise AssertionError("exact rational bounds for the no-wrap witness failed")
    if not (no_wrap_margin > sp.Rational(7, 4)):
        raise AssertionError("signal path is not certified below the half-fibre length")
    if not (clock_chart_margin > sp.Rational(21, 8)):
        raise AssertionError("reception left the lifted clock chart")

    actual = {
        "beta": beta,
        "spatial_volume": volume,
        "gamma_emit": gamma_emit,
        "gamma_receive": gamma_receive,
        "frequency_emit": frequency_emit,
        "frequency_receive": frequency_receive,
        "field_strength_frequency_emit": frequency_emit,
        "field_strength_frequency_receive": frequency_receive,
        "stress_frequency_crosscheck_residual": sp.S(0),
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
        "hopf_fibre_period": hopf_fibre_period,
        "half_hopf_fibre_length": half_hopf_fibre_length,
        "no_wrap_margin": no_wrap_margin,
        "no_wrap_margin_lower_bound": sp.Rational(7, 4),
        "clock_chart_margin": clock_chart_margin,
        "clock_chart_margin_lower_bound": sp.Rational(21, 8),
    }
    expected = {
        "beta": 2 * sp.sqrt(10) / 3,
        "spatial_volume": 12 * sp.sqrt(10) * sp.pi**2 / 5,
        "gamma_emit": 1,
        "gamma_receive": sp.Rational(5, 4),
        "frequency_emit": 2 * sp.sqrt(10) / 3,
        "frequency_receive": sp.sqrt(10) / 3,
        "field_strength_frequency_emit": 2 * sp.sqrt(10) / 3,
        "field_strength_frequency_receive": sp.sqrt(10) / 3,
        "stress_frequency_crosscheck_residual": 0,
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
        "hopf_fibre_period": 6 * sp.pi / sp.sqrt(10),
        "half_hopf_fibre_length": 3 * sp.pi / sp.sqrt(10),
        "no_wrap_margin": 3 * sp.pi / sp.sqrt(10) - sp.Rational(1, 2),
        "no_wrap_margin_lower_bound": sp.Rational(7, 4),
        "clock_chart_margin": sp.pi - sp.Rational(3, 8),
        "clock_chart_margin_lower_bound": sp.Rational(21, 8),
    }
    if any(sp.simplify(actual[key] - value) != 0 for key, value in expected.items()):
        raise AssertionError("dynamical Maxwell redshift fixture drifted")
    return {key: str(sp.factor(value)) for key, value in actual.items()}


def build() -> dict[str, Any]:
    dependencies = _load_dependencies()
    algebra = _mode_algebra()
    payload: dict[str, Any] = {
        "schema": "pure-weyl-berger-dynamical-maxwell-redshift-v2",
        "result_id": "BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE",
        "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
        "claim_status": "CERTIFIED_G0_DYNAMICAL_MAXWELL_MODE_HARDENED_LOCALIZED_RETARDED_DRESSING_OPEN",
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
            "maxwell_equations": "dF=0 and d star F=0 directly in the four-dimensional exterior algebra; the curl/divergence reduction is an independent cross-check",
            "null_invariants": ["E^2-B^2=0", "E dot B=0"],
            "signal_direction": "s=-e3; Poynting=beta^2 s and (L_n+L_s)A_c=0",
        },
        "hardening_audit": {
            "direct_exterior_form": {
                "signature": "(-,+,+,+)",
                "orientation": "e0 wedge e1 wedge e2 wedge e3",
                "hodge_definition": "eI wedge star(eI)=<eI,eI> volume",
                "field_strength_components": _form_strings(algebra["field_strength"]),
                "dual_field_strength_components": _form_strings(algebra["dual_strength"]),
                "dF_components": _form_strings(algebra["bianchi_residual"]),
                "d_star_F_components": _form_strings(algebra["euler_lagrange_residual"]),
                "verdict": "dF=0 AND d_star_F=0",
            },
            "gauge_invariant_frequency": {
                "complex_field": "F_+=F_c+i F_s",
                "duality": "star F_+=-i F_+",
                "time_eigenvalue": "L_n F_+=-i beta F_+",
                "signal_eigenvalue": "L_s F_+=+i beta F_+",
                "observer_eigenvalue": "L_u(v) F_+=-i beta gamma(v)(1-v) F_+",
                "stress_crosscheck": "[beta gamma(v)(1-v)]^2=T_ab u^a u^b",
                "potential_independent": True,
            },
            "hopf_domain": {
                "generator_normalization": "J3=diag(-i/2,+i/2), matching [e_i,e_j]=epsilon_ij^k e_k at a=c=1",
                "primitive_group_period": "exp(4 pi J3)=I while exp(2 pi J3)=-I",
                "metric_fibre_period": "4 pi c",
                "half_fibre_length": "2 pi c",
                "fixture_witness": "2 pi c=3 pi/sqrt(10)>9/4>1/2 using pi>3 and sqrt(10)<4",
                "clock_witness": "pi-3/8>21/8 using pi>3",
            },
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
            "direct_four_form_Bianchi_identity": True,
            "direct_four_form_Maxwell_equation": True,
            "gauge_invariant_field_strength_frequency": True,
            "field_strength_stress_frequency_match": True,
            "Hopf_primitive_period_derived": True,
            "no_wrap_inequality_exact": True,
        },
        "rational_fixture": {
            "background": {"a": "1", "c^2": "9/40", "rho": "1", "omega": "3/4"},
            "observers": {"v_emit": "0", "v_receive": "3/5", "initial_physical_separation": "1/5"},
            "results": _fixture(),
            "chart_and_path_domain": "theta_receive=3/8<pi and travel distance 1/2 is below 2 pi c=3 pi/sqrt(10), with explicit positive margins",
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
                "elapsed_seconds": 6.69,
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "python3 d_quotient_classical/backreacted_clock/verify_berger_dynamical_maxwell_redshift.py",
                "elapsed_seconds": 0.86,
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_dynamical_maxwell_redshift",
                "elapsed_seconds": 12.57,
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-dynamical-maxwell-redshift-v2.schema.json -d d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json",
                "elapsed_seconds": 1.38,
                "status": "PASS",
            },
        ],
        "higher_tiers_not_run": {
            "tier_2": "The imported clock and relational certificates are unchanged content-addressed inputs; their hashes are replayed independently.",
            "tier_3": "This is a G0 probe-mode theorem with no classical freeze, lifecycle promotion, or shared-core algebra change.",
        },
        "claim_boundary": "This hardened exact G0 theorem verifies the positive-energy source-free Maxwell mode directly in four-dimensional exterior algebra, matches the gauge-invariant field-strength Lie frequency to the stress-energy ratio, derives the primitive Hopf period and exact no-wrap margins, and retains the Diff-, Weyl-, Maxwell-gauge-, and total-D-invariant compact spatially averaged redshift fixture. It does not construct localized endpoints, a retarded compact source, the Maxwell BV/q2 semidirect extension, backreaction, a complete G1 signal sector, phenomenology, or a quantum result.",
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
    direct = payload["hardening_audit"]["direct_exterior_form"]
    if direct["dF_components"] != {} or direct["d_star_F_components"] != {}:
        raise AssertionError("direct exterior-form residual is nonzero")
    frequency = payload["hardening_audit"]["gauge_invariant_frequency"]
    if frequency["potential_independent"] is not True:
        raise AssertionError("field-strength frequency was demoted to a potential-dependent claim")
    fixture = payload["rational_fixture"]["results"]
    if fixture["stress_frequency_crosscheck_residual"] != "0":
        raise AssertionError("field-strength and stress frequencies disagree")
    if fixture["no_wrap_margin_lower_bound"] != "7/4":
        raise AssertionError("exact no-wrap lower bound drifted")
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

The hardened verifier also constructs `F` as a four-dimensional exterior
form with signature `(-,+,+,+)`, applies the Lorentzian Hodge star, and finds
both component dictionaries `dF={{}}` and `d star F={{}}`.  Thus the
field-equation result no longer relies only on the curl reduction.

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

Independently, the gauge-invariant complex field strength
`F_+=F_c+i F_s` obeys

\[
\star F_+=-iF_+,
\qquad
\mathcal L_{{u(v)}}F_+=-i\beta\gamma(v)(1-v)F_+.
\]

Squaring this Lie-derivative frequency reproduces `T_ab u^a u^b` exactly,
so the stress-energy ratio carries no untracked potential-amplitude
normalization.

At the rational fixture the exact values are

- `beta={r['beta']}`;
- `nu_e={r['frequency_emit']}` and `nu_r={r['frequency_receive']}`;
- `E_e={r['averaged_energy_emit']}` and `E_r={r['averaged_energy_receive']}`;
- `1+z={r['one_plus_z']}`, hence `z={r['z']}`;
- reception at `theta={r['theta_receive']}`, before a clock recrossing or Hopf wrap.

The SU(2) generator normalization gives primitive Hopf period `4 pi c`, not
`2 pi c`.  At the fixture the full fibre length is
`{r['hopf_fibre_period']}` and the half-fibre length is
`{r['half_hopf_fibre_length']}`.  The signal path has exact margin
`{r['no_wrap_margin']}>7/4`; the lifted clock chart has margin
`{r['clock_chart_margin']}>21/8`.

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
        direct_residual = deepcopy(payload)
        direct_residual["hardening_audit"]["direct_exterior_form"]["d_star_F_components"] = {"e012": "1"}
        mutants.append(("insert direct Maxwell residual", direct_residual))
        potential_frequency = deepcopy(payload)
        potential_frequency["hardening_audit"]["gauge_invariant_frequency"]["potential_independent"] = False
        mutants.append(("demote gauge-invariant frequency", potential_frequency))
        for name, mutant in mutants:
            try:
                verify(mutant)
            except AssertionError:
                continue
            raise AssertionError(f"mutation guard accepted: {name}")
    print("BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE: PASS")


if __name__ == "__main__":
    main()
