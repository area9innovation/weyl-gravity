#!/usr/bin/env python3
"""Independent exact replay of the Berger Maxwell redshift mode."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-dynamical-maxwell-redshift-v2.schema.json"


def _clean(expression):
    return sp.trigsimp(expression)


def _wedge_basis(left, right):
    combined = left + right
    if len(set(combined)) != len(combined):
        return None
    inversions = sum(
        combined[first] > combined[second]
        for first in range(len(combined))
        for second in range(first + 1, len(combined))
    )
    return (-1 if inversions % 2 else 1), tuple(sorted(combined))


def _wedge(left, right):
    result = {}
    for left_basis, left_value in left.items():
        for right_basis, right_value in right.items():
            product = _wedge_basis(left_basis, right_basis)
            if product is None:
                continue
            sign, basis = product
            result[basis] = _clean(result.get(basis, 0) + sign * left_value * right_value)
    return {basis: value for basis, value in result.items() if value != 0}


def _d(form, derivatives, t):
    result = {}
    for basis, coefficient in form.items():
        terms = [_wedge({(0,): sp.diff(coefficient, t)}, {basis: 1})]
        for position, index in enumerate(basis):
            term = _wedge(_wedge({basis[:position]: 1}, derivatives[index]), {basis[position + 1 :]: 1})
            terms.append({key: coefficient * (-1) ** position * value for key, value in term.items()})
        for term in terms:
            for key, value in term.items():
                result[key] = _clean(result.get(key, 0) + value)
    return {basis: value for basis, value in result.items() if value != 0}


def _star(form):
    eta = (-1, 1, 1, 1)
    result = {}
    for basis, coefficient in form.items():
        complement = tuple(index for index in range(4) if index not in basis)
        sign, _ = _wedge_basis(basis, complement)
        norm = sp.prod(eta[index] for index in basis)
        result[complement] = sp.simplify(coefficient * sign * norm)
    return result


def _linear(*terms):
    result = {}
    for multiplier, form in terms:
        for basis, value in form.items():
            result[basis] = _clean(result.get(basis, 0) + multiplier * value)
    return {basis: value for basis, value in result.items() if value != 0}


def _basis_derivation(form, images):
    result = {}
    for basis, coefficient in form.items():
        for position, index in enumerate(basis):
            term = _wedge(_wedge({basis[:position]: 1}, images[index]), {basis[position + 1 :]: 1})
            for key, value in term.items():
                result[key] = _clean(result.get(key, 0) + coefficient * value)
    return {basis: value for basis, value in result.items() if value != 0}


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)

    for record in certificate["dependency_refs"].values():
        source = ROOT / record["path"]
        if hashlib.sha256(source.read_bytes()).hexdigest() != record["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {source}")
        if json.loads(source.read_text())["result_id"] != record["result_id"]:
            raise AssertionError(f"dependency result mismatch: {source}")
    for relative_path, expected_hash in certificate["provenance"]["source_manifest"].items():
        source = ROOT / relative_path
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected_hash:
            raise AssertionError(f"source manifest mismatch: {source}")

    # Independent field-equation replay in the left-invariant coframe.
    beta_symbol, alpha, t = sp.symbols("beta alpha t", positive=True, real=True)
    potential = sp.Matrix(
        [sp.cos(beta_symbol * t), sp.sin(beta_symbol * t), 0]
    )
    curl = sp.diag(-beta_symbol, -beta_symbol, -alpha)
    electric = -sp.diff(potential, t)
    magnetic = curl * potential
    if sp.simplify(sp.diff(potential, t, 2) + curl * curl * potential) != sp.zeros(3, 1):
        raise AssertionError("independent source-free Maxwell replay failed")
    if sp.trigsimp(electric.dot(electric) - magnetic.dot(magnetic)) != 0:
        raise AssertionError("independent null-field norm replay failed")
    if sp.trigsimp(electric.dot(magnetic)) != 0:
        raise AssertionError("independent null-field pseudoscalar replay failed")
    if sp.simplify(sp.trigsimp(electric.cross(magnetic)) - sp.Matrix([0, 0, -beta_symbol**2])) != sp.zeros(3, 1):
        raise AssertionError("independent Poynting direction replay failed")

    derivatives = {
        0: {},
        1: {(2, 3): -beta_symbol},
        2: {(1, 3): beta_symbol},
        3: {(1, 2): -alpha},
    }
    potential_form = {
        (1,): sp.cos(beta_symbol * t),
        (2,): sp.sin(beta_symbol * t),
    }
    field_strength = _d(potential_form, derivatives, t)
    if _d(field_strength, derivatives, t):
        raise AssertionError("independent direct dF replay failed")
    if _d(_star(field_strength), derivatives, t):
        raise AssertionError("independent direct d-star-F replay failed")
    if certificate["hardening_audit"]["direct_exterior_form"]["dF_components"] != {}:
        raise AssertionError("persisted Bianchi residual is nonzero")
    if certificate["hardening_audit"]["direct_exterior_form"]["d_star_F_components"] != {}:
        raise AssertionError("persisted Maxwell residual is nonzero")
    partner_form = {
        (1,): -sp.sin(beta_symbol * t),
        (2,): sp.cos(beta_symbol * t),
    }
    partner_strength = _d(partner_form, derivatives, t)
    if _linear((1, _star(field_strength)), (-1, partner_strength)):
        raise AssertionError("independent anti-self-duality replay failed")
    if _linear((1, _star(partner_strength)), (1, field_strength)):
        raise AssertionError("independent phase-pair duality replay failed")
    time_field = {
        basis: sp.diff(value, t) for basis, value in field_strength.items()
    }
    time_partner = {
        basis: sp.diff(value, t) for basis, value in partner_strength.items()
    }
    lie_e3_field = _basis_derivation(
        field_strength,
        {0: {}, 1: {(2,): beta_symbol}, 2: {(1,): -beta_symbol}, 3: {}},
    )
    lie_e3_partner = _basis_derivation(
        partner_strength,
        {0: {}, 1: {(2,): beta_symbol}, 2: {(1,): -beta_symbol}, 3: {}},
    )
    lie_s_field = _linear((-1, lie_e3_field))
    lie_s_partner = _linear((-1, lie_e3_partner))
    if _linear((1, time_field), (-beta_symbol, partner_strength)):
        raise AssertionError("independent time-frequency replay failed")
    if _linear((1, time_partner), (beta_symbol, field_strength)):
        raise AssertionError("independent partner time-frequency replay failed")
    if _linear((1, lie_s_field), (beta_symbol, partner_strength)):
        raise AssertionError("independent signal-frequency replay failed")
    if _linear((1, lie_s_partner), (-beta_symbol, field_strength)):
        raise AssertionError("independent partner signal-frequency replay failed")
    v = sp.Rational(3, 5)
    gamma = sp.Rational(5, 4)
    observer_lie_field = _linear((gamma, time_field), (gamma * v, lie_s_field))
    observer_lie_partner = _linear((gamma, time_partner), (gamma * v, lie_s_partner))
    observer_frequency = sp.factor(beta_symbol * gamma * (1 - v))
    if _linear((1, observer_lie_field), (-observer_frequency, partner_strength)):
        raise AssertionError("independent observer-frequency replay failed")
    if _linear((1, observer_lie_partner), (observer_frequency, field_strength)):
        raise AssertionError("independent partner observer-frequency replay failed")
    if sp.simplify(observer_frequency**2 - beta_symbol**2 * gamma**2 * (1 - v) ** 2) != 0:
        raise AssertionError("independent stress-frequency replay failed")

    beta = 2 * sp.sqrt(10) / 3
    volume = 12 * sp.sqrt(10) * sp.pi**2 / 5
    gamma_receive = sp.Rational(5, 4)
    frequency_emit = beta
    frequency_receive = sp.factor(beta * gamma_receive * sp.Rational(2, 5))
    expected = {
        "beta": str(beta),
        "spatial_volume": str(volume),
        "gamma_emit": "1",
        "gamma_receive": "5/4",
        "frequency_emit": str(frequency_emit),
        "frequency_receive": str(frequency_receive),
        "field_strength_frequency_emit": str(frequency_emit),
        "field_strength_frequency_receive": str(frequency_receive),
        "stress_frequency_crosscheck_residual": "0",
        "averaged_energy_emit": "40/9",
        "averaged_energy_receive": "10/9",
        "one_plus_z": "2",
        "z": "1",
        "travel_time": "1/2",
        "theta_receive": "3/8",
        "phase_slope_emit": "-8*sqrt(10)/9",
        "phase_slope_receive": "-16*sqrt(10)/45",
        "symplectic_pairing": "-32*pi**2",
        "positive_energy_coefficient": "32*sqrt(10)*pi**2/3",
        "hopf_fibre_period": "3*sqrt(10)*pi/5",
        "half_hopf_fibre_length": "3*sqrt(10)*pi/10",
        "no_wrap_margin": "(-5 + 3*sqrt(10)*pi)/10",
        "no_wrap_margin_lower_bound": "7/4",
        "clock_chart_margin": "(-3 + 8*pi)/8",
        "clock_chart_margin_lower_bound": "21/8",
    }
    if certificate["rational_fixture"]["results"] != expected:
        raise AssertionError("independent Maxwell fixture replay failed")
    if certificate["health_and_pairing"]["energy_signature"] != [2, 0, 0]:
        raise AssertionError("positive Maxwell energy signature drifted")
    if certificate["flags"]["BERGER_GRAVITY_MAXWELL_Q2_DRESSING"] is not False:
        raise AssertionError("missing q2 extension was promoted")
    print("BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE independent replay: PASS")


if __name__ == "__main__":
    main()
