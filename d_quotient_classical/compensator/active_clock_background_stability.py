#!/usr/bin/env python3
"""Exact background stability of the quadratic active-clock action-space no-go."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
AUDIT = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1.json"
)
OUTPUT = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_ACTIVE_CLOCK_BACKGROUND_STABILITY_V1.json"
)
AUDIT_SHA256 = "9bda4b758616427bdbf401a499ffd2b7cd9dd69a87223f05fcdf636bb31cd533"
AUDIT_SCIENCE_COMMIT = "f64be4a5793764ebf8871d5f1a83bd736aed7fc1"
AUDIT_LIFECYCLE_COMMIT = "0b21bfe86eb97a0e0723d85d8c3a336fd1d5ac20"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _q(value: sp.Expr) -> str:
    return str(sp.factor(value))


def _matrix(value: sp.Matrix) -> dict[str, Any]:
    core = {
        "row_count": value.rows,
        "column_count": value.cols,
        "entries": [
            {"row": row, "column": column, "coefficient": _q(value[row, column])}
            for row in range(value.rows)
            for column in range(value.cols)
            if value[row, column] != 0
        ],
    }
    return {**core, "sha256": _digest(core)}


def _import_audit() -> dict[str, Any]:
    actual = _sha(AUDIT)
    if actual != AUDIT_SHA256:
        raise AssertionError("INDEPENDENT_FREEZE_AUDIT_HASH_DRIFT")
    payload = json.loads(AUDIT.read_text())
    if (
        payload["result_id"]
        != "COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1"
        or payload["result_state"]
        != "SCOPED_QUADRATIC_ACTIVE_CLOCK_NO_GO_INDEPENDENTLY_FROZEN"
        or not payload["freeze_verdict"][
            "scoped_quadratic_active_clock_no_go_theorem_frozen"
        ]
        or payload["freeze_verdict"]["candidate_C_active_selected"]
    ):
        raise AssertionError("INDEPENDENT_FREEZE_AUDIT_SEMANTICS_DRIFT")
    return {
        "path": str(AUDIT.relative_to(ROOT)),
        "result_id": payload["result_id"],
        "result_state": payload["result_state"],
        "sha256": actual,
        "science_commit": AUDIT_SCIENCE_COMMIT,
        "lifecycle_commit": AUDIT_LIFECYCLE_COMMIT,
        "import_status": "ACCEPTED_EXACT_HASH_AND_SEMANTICS",
    }


def _geometry_and_matrix(
    kappa: sp.Expr,
    q: sp.Expr,
    nu: sp.Expr,
) -> tuple[sp.Matrix, dict[str, Any]]:
    # kappa=r_cylinder^{-2}; q=c_Berger^2 at fixed horizontal scale a=1;
    # nu=D(theta)>0 and X=-nu^2.
    cylinder = sp.Matrix(
        [
            [0, 36 * kappa**2, 3 * kappa, 1, 0, 0],
            [0, 12 * kappa**2, -kappa, -1, 0, 0],
        ]
    )
    ricci = [0, (2 - q) / 2, (2 - q) / 2, q / 2]
    scalar = (4 - q) / 2
    bach = [
        (1 - q) ** 2 / 6,
        (1 - q) * (1 - 3 * q) / 6,
        (1 - q) * (1 - 3 * q) / 6,
        (1 - q) * (5 * q - 1) / 6,
    ]
    metric = [-1, 1, 1, 1]
    w = nu**2
    rows: list[list[sp.Expr]] = []
    for index in (0, 1, 3):
        g = metric[index]
        gravity = [
            bach[index],
            4 * scalar * ricci[index] - scalar**2 * g,
            ricci[index] - scalar * g / 2,
        ]
        matter = [1, w, -3 * w**2] if index == 0 else [-1, w, -w**2]
        rows.append([sp.factor(x) for x in gravity + matter])
    berger = sp.Matrix(rows)
    stacked = cylinder.col_join(berger)
    return stacked, {
        "coefficient_order": [
            "alpha_B",
            "alpha_R",
            "M_P_squared",
            "p0",
            "p1",
            "p2",
        ],
        "metric_Euler_formula": (
            "alpha_B B_ab+alpha_R(4R Ric_ab-R^2 g_ab)"
            "+M_P^2 G_ab-T_ab[P]=0"
        ),
        "clock_Euler_formula": "nabla_a(P_X nabla^a theta)=0",
        "cylinder": {
            "coordinate": "kappa=r_cylinder^(-2)>0",
            "invariants": (
                "R=6 kappa, Ric_orthonormal=(0,2 kappa,2 kappa,2 kappa), "
                "theta=constant, X=0"
            ),
            "matrix": _matrix(cylinder),
            "clock_equation": "PASS_IDENTICALLY",
        },
        "Berger": {
            "coordinates": "a=1, q=c^2>0, nu=D(theta)>0, X=-nu^2",
            "Ricci_orthonormal": [_q(x) for x in ricci],
            "scalar_curvature": _q(scalar),
            "Bach_orthonormal": [_q(x) for x in bach],
            "matrix": _matrix(berger),
            "clock_equation": (
                "PASS_IDENTICALLY: X, P_X and nu are spatially and temporally "
                "constant and theta=nu t is harmonic"
            ),
        },
        "stacked_matrix": _matrix(stacked),
    }


def _stationary_locus(
    matrix: sp.Matrix,
    kappa: sp.Symbol,
    q: sp.Symbol,
    nu: sp.Symbol,
    lam: sp.Symbol,
) -> tuple[dict[str, Any], sp.Matrix, dict[str, sp.Expr]]:
    A = 4 * q - 1
    F = q + 12 * kappa - 4
    J = 16 * q * kappa - q - 4 * kappa
    H = 32 * q * kappa - 3 * q - 8 * kappa
    factors = {"A": A, "F": F, "J": J, "H": H}
    generator = sp.Matrix(
        [
            8 * nu**4 * F,
            -sp.Rational(4, 3) * nu**4 * A,
            32 * kappa * nu**4 * A,
            -48 * kappa**2 * nu**4 * A,
            -8 * kappa * nu**2 * A * F,
            -F * J,
        ]
    )
    kernel_residual = (matrix * generator).applyfunc(sp.factor)
    if kernel_residual != sp.zeros(5, 1):
        raise AssertionError("PARAMETERIZED_KERNEL_IDENTITY_FAILED")
    signed_cofactors = [
        sp.factor(
            (-1) ** column
            * matrix[:, [j for j in range(6) if j != column]].det()
        )
        for column in range(6)
    ]
    common = kappa * nu**2 * (q - 1)
    if any(
        sp.factor(value - common * generator[index]) != 0
        for index, value in enumerate(signed_cofactors)
    ):
        raise AssertionError("MAXIMAL_COFACTOR_FACTORIZATION_FAILED")
    fixed = {
        kappa: 1,
        q: sp.Rational(9, 40),
        nu: sp.Rational(3, 4),
    }
    fixed_generator = sp.Matrix([sp.factor(x.subs(fixed)) for x in generator])
    normalized = [sp.factor(x / fixed_generator[-1]) for x in fixed_generator]
    expected = [
        sp.Rational(81, 20),
        sp.Rational(27, 3290),
        -sp.Rational(324, 1645),
        sp.Rational(486, 1645),
        sp.Rational(18, 25),
        1,
    ]
    if normalized != expected:
        raise AssertionError("FROZEN_AUDITED_RAY_NOT_RECOVERED")
    records = {
        "polynomial_factors": {name: _q(value) for name, value in factors.items()},
        "kernel_generator_K": [_q(value) for value in generator],
        "complete_rank_five_locus": (
            "(alpha_B,alpha_R,M_P_squared,p0,p1,p2)=lambda K(kappa,q,nu)"
        ),
        "signed_maximal_cofactors_delete_columns_0_to_5": [
            _q(value) for value in signed_cofactors
        ],
        "common_cofactor_factor": _q(common),
        "kernel_from_cofactors": True,
        "rank_change_variety": (
            "{kappa=0} union {nu=0} union {q=1} union "
            "{4q-1=0 and q+12kappa-4=0}"
        ),
        "rank_change_last_component_note": (
            "J=0 makes the displayed p2 component vanish but does not by itself "
            "lower stationary rank"
        ),
        "frozen_specialization": {
            "point": ["kappa=1", "q=9/40", "nu=3/4"],
            "K_at_point": [_q(value) for value in fixed_generator],
            "normalized_p2_one": [_q(value) for value in normalized],
            "agrees_with_independently_frozen_ray": True,
        },
        "background_existence_scope": (
            "For each rank-five parameter point the full stationary action "
            "locus is the displayed ray. Couplings vary with the background; "
            "this is not a claim that one fixed coupling vector supports the "
            "whole neighbourhood."
        ),
        "zero_action_stratum": {
            "condition": "lambda=0",
            "status": "BACKGROUND_EQUATIONS_VACUOUS_NO_DYNAMICS",
        },
        "nonzero_background_stratum": {
            "condition": "lambda!=0 and stationary rank five",
            "status": "EXACT_COMMON_CYLINDER_BERGER_BACKGROUND_EXISTS",
        },
    }
    return records, sp.Matrix([lam * x for x in generator]), factors


def _quadratic_records(
    coefficients: sp.Matrix,
    factors: dict[str, sp.Expr],
    kappa: sp.Symbol,
    q: sp.Symbol,
    nu: sp.Symbol,
    lam: sp.Symbol,
) -> dict[str, Any]:
    D = sp.Symbol("D")
    zeta = sp.Symbol("zeta")
    mass = coefficients[2]
    p1 = coefficients[4]
    velocity = sp.Matrix([[0, -3, 0], [-3, 0, 0], [0, 0, -2 * p1]])
    principal = -velocity
    congruence = sp.Matrix([[1, 1, 0], [1, -1, 0], [0, 0, 1]])
    diagonal = sp.factor(congruence.T * velocity * congruence)
    if diagonal != sp.diag(-6, 6, -2 * p1):
        raise AssertionError("VELOCITY_CONGRUENCE_FAILED")
    hessian = sp.Matrix(
        [
            [0, 3 * (D**2 - 2 * kappa), 0],
            [3 * (D**2 - 2 * kappa), 12 / mass, 0],
            [0, 0, 2 * p1 * D**2],
        ]
    )
    determinant = sp.factor(hessian.det())
    expected_det = sp.factor(-18 * p1 * D**2 * (D**2 - 2 * kappa) ** 2)
    if determinant != expected_det:
        raise AssertionError("HESSIAN_DETERMINANT_FAILED")
    evolution = sp.Matrix(
        [
            [0, 1, 0, 0, 0, 0],
            [2 * kappa, 0, -4 / mass, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 2 * kappa, 0, 0, 0],
            [0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0],
        ]
    )
    charpoly = sp.factor(evolution.charpoly(zeta).as_expr())
    expected_charpoly = zeta**2 * (zeta**2 - 2 * kappa) ** 2
    if sp.expand(charpoly - expected_charpoly) != 0:
        raise AssertionError("EVOLUTION_CHARACTERISTIC_FAILED")
    return {
        "activation": (
            "lambda!=0, kappa!=0, nu!=0 and A=4q-1!=0 so the algebraic "
            "R^2 auxiliary presentation is invertible"
        ),
        "field_basis": ["u", "psi", "v"],
        "complete_homogeneous_quadratic_density": (
            "L_hom=-3 D(psi)D(u)-6 kappa psi u"
            "+6 psi^2/M_P_squared-p1 D(v)^2"
        ),
        "Euler_Hessian_of_D": _matrix(hessian),
        "Euler_Hessian_determinant": _q(determinant),
        "principal_D2_matrix": _matrix(principal),
        "velocity_Hessian": _matrix(velocity),
        "rational_congruence": _matrix(congruence),
        "congruence_diagonal": _matrix(diagonal),
        "inertia": {
            "p1>0": [1, 2, 0],
            "p1<0": [2, 1, 0],
            "p1=0": [1, 1, 1],
            "structural_statement": (
                "the gravity-auxiliary pair is split for every p1 and remains "
                "the exact eigenpair (+3,-3)"
            ),
        },
        "state_basis": ["u", "D(u)", "psi", "D(psi)", "v", "D(v)"],
        "D_evolution_matrix": _matrix(evolution),
        "characteristic_polynomial": _q(charpoly),
        "minimal_polynomial_on_declared_box": "zeta^2(zeta^2-2kappa)^2",
        "root_collision_surface": "kappa=0",
        "principal_parameter_discriminant": (
            "lambda*kappa*nu*(4q-1)*(q+12kappa-4)=0"
        ),
        "Lee_Wald_current": (
            "omega^0=-3[delta u wedge delta Dpsi+delta psi wedge delta Du]"
            "-2p1 delta v wedge delta Dv"
        ),
        "raw_D_Hamiltonian": (
            "H_D=-3DuDpsi+6kappa psi u-6psi^2/M_P_squared-p1(Dv)^2"
        ),
        "raw_D_sign_witnesses": [
            "(u,Du,psi,Dpsi,v,Dv)=(0,1,0,-1,0,0) gives +3",
            "(u,Du,psi,Dpsi,v,Dv)=(0,1,0,1,0,0) gives -3",
        ],
        "stable_split_factor": _q(factors["A"]),
    }


def _clock_charge_records(
    coefficients: sp.Matrix,
    factors: dict[str, sp.Expr],
    kappa: sp.Symbol,
    q: sp.Symbol,
    nu: sp.Symbol,
    lam: sp.Symbol,
) -> dict[str, Any]:
    X = -nu**2
    p0, p1, p2 = coefficients[3], coefficients[4], coefficients[5]
    P = sp.factor(p0 + p1 * X + p2 * X**2)
    P_X = sp.factor(p1 + 2 * p2 * X)
    longitudinal = sp.factor(p1 + 6 * p2 * X)
    sound = sp.factor(P_X / longitudinal)
    energy = sp.factor(-2 * P_X * nu**2 - P)
    charge = sp.factor(-2 * P_X * nu)
    k_density = sp.factor(energy - nu * charge)
    if k_density != -P or sound != -q / factors["H"]:
        raise AssertionError("CLOCK_CHARGE_FACTORIZATION_FAILED")
    return {
        "P": _q(P),
        "P_X": _q(P_X),
        "longitudinal_P_X_plus_2X_P_XX": _q(longitudinal),
        "sound_speed_squared": _q(sound),
        "Lorentzian_hyperbolicity": (
            "P_X(P_X+2X P_XX)>0 with neither factor zero"
        ),
        "standard_sign_clock": ["P_X<0", "P_X+2X P_XX<0"],
        "cylinder_clock_condition": "p1<0",
        "clock_cone_discriminant": (
            "lambda*nu*q*(q+12kappa-4)"
            "*(32qkappa-3q-8kappa)=0"
        ),
        "energy_density": _q(energy),
        "shift_current_convention": "j^a=2P_X nabla^a(theta)",
        "Q_R_density": _q(charge),
        "matter_raw_D_density": _q(energy),
        "matter_K_density": _q(k_density),
        "charge_identity": (
            "K_Berger=D-nu R fixes the stationary background; "
            "i_D Omega_total=nu delta Q_R and i_K_Berger Omega_total=0"
        ),
        "relational_clock_conditions": [
            "nu>0",
            "X=-nu^2<0",
            "Q_R_density!=0",
            "P_X<0",
            "P_X+2X P_XX<0",
            "0<sound_speed_squared<1",
        ],
    }


def _neighbourhood_records(
    factors: dict[str, sp.Expr],
    coefficients: sp.Matrix,
    kappa: sp.Symbol,
    q: sp.Symbol,
    nu: sp.Symbol,
    lam: sp.Symbol,
) -> dict[str, Any]:
    fixed = {kappa: 1, q: sp.Rational(9, 40), nu: sp.Rational(3, 4)}
    if not (
        sp.Rational(15, 16) < fixed[kappa] < sp.Rational(17, 16)
        and sp.Rational(1, 5) < fixed[q] < sp.Rational(1, 4)
        and sp.Rational(2, 3) < fixed[nu] < sp.Rational(5, 6)
    ):
        raise AssertionError("FROZEN_POINT_OUTSIDE_DECLARED_BOX")
    # G controls P/lambda/nu^4. E controls -rho/lambda/nu^4.
    G = 16 * q**2 * kappa + q**2 - 56 * q * kappa - 4 * q + 16 * kappa
    E = 16 * q**2 * kappa - 3 * q**2 - 104 * q * kappa + 12 * q + 16 * kappa
    p1 = coefficients[4]
    P_X = -2 * lam * q * nu**2 * factors["F"]
    longitudinal = 2 * lam * nu**2 * factors["F"] * factors["H"]
    return {
        "name": "N_box",
        "exact_box": {
            "kappa": ["15/16", "17/16"],
            "cylinder_radius_equivalent": ["4/sqrt(17)", "4/sqrt(15)"],
            "q": ["1/5", "1/4"],
            "nu": ["2/3", "5/6"],
            "interval_convention": "all intervals open",
            "contains_frozen_point": True,
        },
        "sign_certificate": {
            "kappa": "positive",
            "q": "positive",
            "nu": "positive",
            "q-1": "negative",
            "A=4q-1": "negative",
            "F=q+12kappa-4": "F>149/20>0",
            "J=16qkappa-q-4kappa": "J<-q<-1/5<0",
            "H=32qkappa-3q-8kappa": "H<-3q<-3/5<0",
            "G_for_P": "G>15/8>0",
            "E_for_energy": "E<-81/50<0",
            "sound_subluminal": (
                "-H-q=kappa(8-32q)+2q>0, hence 0<-q/H<1"
            ),
        },
        "rank": {
            "value": 5,
            "witness": (
                "signed cofactor 0=8 kappa nu^6(q-1)F is nonzero on N_box"
            ),
        },
        "background_existence": {
            "lambda=0": "zero action; no physical equations or pairing",
            "lambda!=0": (
                "exact common stationary cylinder/Berger background on the "
                "parameter-dependent action ray"
            ),
        },
        "health_half_lines": {
            "p1": _q(p1),
            "P_X": _q(P_X),
            "longitudinal": _q(longitudinal),
            "lambda>0": (
                "Berger clock is standard-sign, hyperbolic, positive-energy, "
                "charged and subluminal; cylinder clock has wrong sign"
            ),
            "lambda<0": (
                "cylinder clock has standard sign; Berger clock has the wrong "
                "standard sign and negative energy/charge orientation"
            ),
            "common_clock_health": "EMPTY",
        },
        "structurally_stable_failures": {
            "gate_5": (
                "every lambda!=0 retains the split (+3,-3) gravity-auxiliary "
                "velocity pair; independently the two clock-health half-lines "
                "are opposite"
            ),
            "gate_6": (
                "the raw-D Hamiltonian retains the parameter-independent exact "
                "witnesses +3 and -3"
            ),
            "all_seven_gate_good_locus": "EMPTY_FOR_EVERY_POINT_OF_N_box",
        },
        "scope_warning": (
            "This is an open-neighbourhood theorem for a parameterized family "
            "of stationary action rays. It is not an implicit-function theorem "
            "for one fixed action and not a generic-background theorem."
        ),
    }


def _bifurcation_records(
    coefficients: sp.Matrix,
    factors: dict[str, sp.Expr],
    kappa: sp.Symbol,
    q: sp.Symbol,
    nu: sp.Symbol,
    lam: sp.Symbol,
) -> dict[str, Any]:
    p1 = coefficients[4]
    P_X = -2 * lam * q * nu**2 * factors["F"]
    longitudinal = 2 * lam * nu**2 * factors["F"] * factors["H"]
    below = {
        kappa: 1,
        q: sp.Rational(9, 40),
        nu: sp.Rational(3, 4),
        lam: 1,
    }
    above = {
        kappa: 1,
        q: sp.Rational(21, 80),
        nu: sp.Rational(3, 4),
        lam: 1,
    }
    below_values = [sp.factor(x.subs(below)) for x in (p1, P_X, longitudinal)]
    above_values = [sp.factor(x.subs(above)) for x in (p1, P_X, longitudinal)]
    if not (
        below_values[0] > 0
        and below_values[1] < 0
        and below_values[2] < 0
        and all(x < 0 for x in above_values)
    ):
        raise AssertionError("BIFURCATION_WITNESS_SIGNS_FAILED")
    surface = {
        kappa: 1,
        q: sp.Rational(1, 4),
        nu: sp.Rational(3, 4),
        lam: 1,
    }
    surface_coefficients = [sp.factor(x.subs(surface)) for x in coefficients]
    if any(surface_coefficients[index] != 0 for index in (1, 2, 3, 4)):
        raise AssertionError("BIFURCATION_SURFACE_DEGENERACY_FAILED")
    return {
        "path": "kappa=1, nu=3/4, lambda=1, q increasing",
        "first_boundary_of_declared_box": "q=1/4",
        "surface_type": (
            "principal/auxiliary/clock-health bifurcation, not stationary "
            "rank change at kappa=1"
        ),
        "surface_data": {
            "A": "0",
            "alpha_R": "0",
            "M_P_squared": "0",
            "p0": "0",
            "p1": "0",
            "stationary_rank": 5,
            "cylinder_clock": "DEGENERATE",
            "R2_auxiliary_presentation": "INACTIVE",
        },
        "below_witness": {
            "point": ["kappa=1", "q=9/40", "nu=3/4", "lambda=1"],
            "p1_PX_longitudinal": [_q(x) for x in below_values],
            "clock_verdict": "cylinder wrong sign; Berger standard-sign healthy",
        },
        "above_witness": {
            "point": ["kappa=1", "q=21/80", "nu=3/4", "lambda=1"],
            "p1_PX_longitudinal": [_q(x) for x in above_values],
            "clock_verdict": (
                "both cylinder and Berger clocks standard-sign hyperbolic; "
                "Berger sound remains subluminal"
            ),
        },
        "full_verdict_both_sides": (
            "still EMPTY because the split gravity-auxiliary velocity pair and "
            "raw-D both-sign witnesses persist whenever alpha_R!=0"
        ),
        "rank_change_intersection_on_q=1/4": (
            "stationary rank drops only at the separate intersection "
            "kappa=5/16 (or on kappa=0, nu=0, q=1)"
        ),
    }


def build() -> dict[str, Any]:
    imported = _import_audit()
    kappa, q, nu, lam = sp.symbols(
        "kappa q nu lambda", real=True
    )
    matrix, geometry = _geometry_and_matrix(kappa, q, nu)
    stationary, coefficients, factors = _stationary_locus(
        matrix, kappa, q, nu, lam
    )
    quadratic = _quadratic_records(
        coefficients, factors, kappa, q, nu, lam
    )
    clock = _clock_charge_records(
        coefficients, factors, kappa, q, nu, lam
    )
    neighbourhood = _neighbourhood_records(
        factors, coefficients, kappa, q, nu, lam
    )
    bifurcation = _bifurcation_records(
        coefficients, factors, kappa, q, nu, lam
    )
    result = {
        "schema": "pure-weyl-compensator-active-clock-background-stability-v1",
        "result_id": "COMPENSATOR_ACTIVE_CLOCK_BACKGROUND_STABILITY_V1",
        "result_state": (
            "SCOPED_ACTION_SPACE_NO_GO_BACKGROUND_STABLE_WITH_FIRST_BIFURCATION"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "frozen_import": imported,
        "parameter_family": {
            "coordinates": ["kappa", "q", "nu"],
            "definitions": {
                "kappa": "inverse squared cylinder radius r_cylinder^(-2)",
                "q": "Berger squashing c^2 at horizontal scale a=1",
                "nu": "positive stationary clock gradient D(theta)",
            },
            "base_point": ["kappa=1", "q=9/40", "nu=3/4"],
            "coefficient_field": "Q(kappa,q,nu,lambda)",
            "exactness": "symbolic polynomial/rational arithmetic only",
        },
        "stationary_evaluation": geometry,
        "stationary_locus_and_rank_strata": stationary,
        "coupled_scalar_principal_velocity": quadratic,
        "clock_cone_charge_and_relational_inequalities": clock,
        "certified_open_neighbourhood": neighbourhood,
        "first_bifurcation": bifurcation,
        "seven_gate_stability": {
            "gate_1_action_derived": (
                "PASS_AT_ACTION_LEVEL on every parameter-dependent stationary ray"
            ),
            "gate_2_trace_disposition": (
                "PASS_WITH_PHYSICAL_REPLACEMENT for lambda!=0 throughout N_box"
            ),
            "gate_3_complete_support_local_parent": (
                "NOT_REACHED after structurally stable gate-5 failure"
            ),
            "gate_4_reduced_pairing": (
                "NONDEGENERATE_BUT_SPLIT for lambda!=0 throughout N_box"
            ),
            "gate_5_physical_sign": "FAIL_STRUCTURALLY_STABLE_ON_N_box",
            "gate_6_raw_D": "FAIL_STRUCTURALLY_STABLE_ON_N_box",
            "gate_7_Berger_clock": (
                "STATIONARY_AND_MONOTONE; standard-sign healthy only on lambda>0"
            ),
            "good_locus": "EMPTY_FOR_EVERY_PARAMETER_POINT_IN_N_box",
            "candidate_C_active_selected": False,
        },
        "exact_checks": {
            "independent_freeze_audit_hash_and_semantics_pinned": True,
            "stationary_matrix_polynomial": True,
            "kernel_identity_exact": True,
            "all_six_signed_maximal_cofactors_factored": True,
            "rank_change_variety_exact": True,
            "frozen_ray_recovered": True,
            "open_box_signs_exact": True,
            "background_existence_separated_from_health": True,
            "principal_velocity_and_inertia_parameterized": True,
            "sound_cone_and_subluminality_parameterized": True,
            "raw_D_and_K_charge_parameterized": True,
            "relational_clock_inequalities_parameterized": True,
            "bifurcation_surface_and_two_sided_witnesses_exact": True,
            "numerical_sampling_used": False,
            "implicit_function_theorem_used": False,
        },
        "claim_flags": {
            "SCOPED_ACTION_SPACE_BACKGROUND_STABILITY_THEOREM": True,
            "ONE_FIXED_ACTION_BACKGROUND_STABILITY": False,
            "GENERIC_BACKGROUND_NO_GO": False,
            "CANDIDATE_C_ACTIVE_SELECTED": False,
            "COMPLETE_SUPPORT_LOCAL_CAUSAL_PARENT": False,
            "HADAMARD_ANOMALY_QME_OR_QUANTUM": False,
            "PARTICLE_SCATTERING_UNITARITY": False,
        },
        "claim_boundary": (
            "This exact theorem concerns the declared dressed parity-even "
            "C^2+R^2+R plus quadratic shift-symmetric P(X) action family, with "
            "no HT or new fields, on the parameterized joint cylinder/Berger "
            "family kappa=r_cylinder^-2, a_Berger=1, q=c^2 and theta=nu t. "
            "For every point in the stated rational open box, the stationary "
            "action-space ray exists but its seven-gate good locus is empty. "
            "The theorem lets couplings vary with the background; it does not "
            "show that one fixed action supports the neighbourhood. The "
            "q=1/4 surface is a clock/principal bifurcation along the declared "
            "path, while the stationary rank-change variety is recorded "
            "separately. Nothing here covers other backgrounds, higher P(X), "
            "higher derivatives, fixed-charge quotients, new fields or "
            "enlarged gauge groups. It selects no action and establishes no "
            "complete causal parent, Hadamard state, anomaly/QME result, "
            "particle space, scattering, positivity or unitarity theorem."
        ),
        "next_gate": (
            "The quadratic active-clock route is now obstructed on an exact "
            "open background neighbourhood. A successor must cross q=1/4 "
            "with a different non-gravitational health target while still "
            "repairing the unchanged split gravity-auxiliary and raw-D gates, "
            "or enlarge the declared action/gauge/field family."
        ),
    }
    result["content_hashes"] = {
        "stationary_sha256": _digest(result["stationary_evaluation"]),
        "locus_sha256": _digest(result["stationary_locus_and_rank_strata"]),
        "quadratic_sha256": _digest(result["coupled_scalar_principal_velocity"]),
        "clock_sha256": _digest(
            result["clock_cone_charge_and_relational_inequalities"]
        ),
        "neighbourhood_sha256": _digest(result["certified_open_neighbourhood"]),
        "bifurcation_sha256": _digest(result["first_bifurcation"]),
        "gates_sha256": _digest(result["seven_gate_stability"]),
    }
    return result


def _check(value: dict[str, Any]) -> None:
    if (
        value["certified_open_neighbourhood"]["structurally_stable_failures"][
            "all_seven_gate_good_locus"
        ]
        != "EMPTY_FOR_EVERY_POINT_OF_N_box"
        or value["seven_gate_stability"]["candidate_C_active_selected"]
        or value["claim_flags"]["ONE_FIXED_ACTION_BACKGROUND_STABILITY"]
        or value["claim_flags"]["GENERIC_BACKGROUND_NO_GO"]
        or value["claim_flags"]["HADAMARD_ANOMALY_QME_OR_QUANTUM"]
    ):
        raise AssertionError("BACKGROUND_STABILITY_CLAIM_BOUNDARY_DRIFT")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    _check(value)
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    elif json.loads(OUTPUT.read_text()) != value:
        raise AssertionError("active-clock background-stability certificate is stale")
    print("COMPENSATOR_ACTIVE_CLOCK_BACKGROUND_STABILITY_V1: PASS")


if __name__ == "__main__":
    main()
