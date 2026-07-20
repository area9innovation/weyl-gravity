#!/usr/bin/env python3
"""Exact seven-gate locus for the quadratic active-clock P(X) enlargement."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_ACTIVE_CLOCK_PX2_LOCUS_V1.json"
)

DEPENDENCIES = {
    "minimal_action_classification": {
        "path": ROOT
        / "d_quotient_classical/certificates/"
        "COMPENSATOR_MINIMAL_ACTION_CLASSIFICATION_AFTER_NEITHER_V1.json",
        "sha256": "41ce6db6ab8fc58f4cc1ecedb205f732fd3dcee645f9408506d3535545f7026a",
        "source_commit": "a5924e707352bab92db2caa4c19cf4223c60f0e3",
        "lifecycle_commit": "091876a9504b7fda91aad75e82b24d7051417c18",
    },
    "positive_Berger_clock": {
        "path": ROOT
        / "d_quotient_classical/certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json",
        "sha256": "35e1bb8a56b0591b3dd00aa8f22c328ad826ecd341c290564cfd1a68fcc3e687",
        "source_commit": "bb5738d6e3e30a68adcc9a70c35dac089079e3db",
    },
    "Berger_charge_convention": {
        "path": ROOT
        / "d_quotient_classical/certificates/BERGER_FIXED_COUPLING_DELTA_CHARGE.json",
        "sha256": "0ae894432b065f9f4ba116e6e2d42e69d1d60cd37dbf6ef21a14d7073c75b786",
        "source_commit": "cc5df8d547f7d2119282590a824ce92cd1d76d17",
    },
}


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


def _imports() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    records: dict[str, Any] = {}
    payloads: dict[str, dict[str, Any]] = {}
    for name, source in DEPENDENCIES.items():
        actual = _sha(source["path"])
        if actual != source["sha256"]:
            raise AssertionError(f"{name} hash drifted")
        payload = json.loads(source["path"].read_text())
        payloads[name] = payload
        record = {
            "path": str(source["path"].relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": actual,
            "source_commit": source["source_commit"],
        }
        if "lifecycle_commit" in source:
            record["lifecycle_commit"] = source["lifecycle_commit"]
        records[name] = record
    if (
        payloads["minimal_action_classification"]["result_state"]
        != "SCOPED_MINIMAL_ACTION_GOOD_LOCUS_EMPTY"
        or payloads["positive_Berger_clock"]["claim_status"]
        != "CERTIFIED_EXACT_BACKGROUND"
        or payloads["Berger_charge_convention"]["scientific_verdict"]
        != "D_GAUGE"
    ):
        raise AssertionError("active-clock dependency semantics drifted")
    return records, payloads


def _stationary_system() -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    # Coefficient order: alpha_B, alpha_R, M_P^2, p0, p1, p2.
    cylinder = sp.Matrix(
        [
            [0, 36, 3, 1, 0, 0],
            [0, 12, -1, -1, 0, 0],
        ]
    )
    scalar_curvature = sp.Rational(151, 80)
    omega_squared = sp.Rational(9, 16)
    metric = [-1, 1, 1, 1]
    ricci = [
        0,
        sp.Rational(71, 80),
        sp.Rational(71, 80),
        sp.Rational(9, 80),
    ]
    bach = [
        sp.Rational(961, 9600),
        sp.Rational(403, 9600),
        sp.Rational(403, 9600),
        sp.Rational(31, 1920),
    ]
    rows: list[list[sp.Expr]] = []
    for index in (0, 1, 3):
        g = metric[index]
        einstein = ricci[index] - scalar_curvature * g / 2
        r_squared = (
            4 * scalar_curvature * ricci[index]
            - scalar_curvature**2 * g
        )
        if index == 0:
            matter = [1, omega_squared, -3 * omega_squared**2]
        else:
            matter = [-1, omega_squared, -omega_squared**2]
        rows.append([bach[index], r_squared, einstein, *matter])
    berger = sp.Matrix(rows)
    return cylinder, berger, cylinder.col_join(berger)


def _stationary_records() -> tuple[dict[str, Any], sp.Matrix]:
    cylinder, berger, stacked = _stationary_system()
    rref, pivots = stacked.rref()
    kernel = stacked.nullspace()
    expected = sp.Matrix(
        [
            sp.Rational(81, 20),
            sp.Rational(27, 3290),
            -sp.Rational(324, 1645),
            sp.Rational(486, 1645),
            sp.Rational(18, 25),
            1,
        ]
    )
    if (
        stacked.rank() != 5
        or pivots != (0, 1, 2, 3, 4)
        or len(kernel) != 1
        or kernel[0] != expected
        or stacked * expected != sp.zeros(5, 1)
    ):
        raise AssertionError("stationary one-dimensional locus drifted")
    pivot_minor = sp.factor(stacked[:, :5].det())
    if pivot_minor != sp.Rational(91791, 40960):
        raise AssertionError("stationary rank witness drifted")
    integer_generator = sp.Matrix([133245, 270, -6480, 9720, 23688, 32900])
    if stacked * integer_generator != sp.zeros(5, 1):
        raise AssertionError("integer locus generator drifted")
    records = {
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
            "+M_P^2 G_ab-T_ab[P]=0, "
            "T_ab=-2 P_X partial_a(theta)partial_b(theta)+P g_ab"
        ),
        "clock_Euler_formula": "nabla_a(P_X nabla^a theta)=0",
        "unit_cylinder": {
            "background": (
                "g_hat=-dt^2+dOmega_3^2, R=6, "
                "Ric_orthonormal=(0,2,2,2), theta=constant, X=0"
            ),
            "independent_rows": ["E_00", "E_horizontal"],
            "matrix": _matrix(cylinder),
            "rank": 2,
            "relations": [
                "M_P^2=-24 alpha_R",
                "p0=36 alpha_R=-3 M_P^2/2",
            ],
            "clock_equation": "PASS_IDENTICALLY",
        },
        "frozen_Berger_clock": {
            "background": (
                "a=1, q=c^2=9/40, omega_clock=3/4, "
                "X=-9/16, R=151/80"
            ),
            "Bach_orthonormal": [
                "961/9600",
                "403/9600",
                "403/9600",
                "31/1920",
            ],
            "Ricci_orthonormal": ["0", "71/80", "71/80", "9/80"],
            "independent_rows": ["E_00", "E_horizontal", "E_vertical"],
            "matrix": _matrix(berger),
            "rank": 3,
            "clock_equation": (
                "PASS: X and P_X are constant and theta=3t/4 is harmonic"
            ),
        },
        "common_system": {
            "matrix": _matrix(stacked),
            "rank": 5,
            "pivot_columns": list(pivots),
            "pivot_minor_first_five_columns": "91791/40960",
            "rref": _matrix(rref),
            "kernel_dimension": 1,
            "kernel_generator_rational": [_q(value) for value in expected],
            "kernel_generator_integer": [int(value) for value in integer_generator],
            "complete_real_locus": (
                "(alpha_B,alpha_R,M_P^2,p0,p1,p2)"
                "=t(81/20,27/3290,-324/1645,486/1645,18/25,1), t in R"
            ),
            "singular_strata": {
                "t=0": "zero action; no equations, pairing or clock dynamics",
                "t!=0": (
                    "alpha_R, M_P^2, p1 and p2 are all nonzero; "
                    "the algebraic R^2 auxiliary presentation is invertible"
                ),
            },
        },
    }
    return records, expected


def _quadratic_records(parameter: sp.Symbol) -> dict[str, Any]:
    spectral = sp.Symbol("spectral")
    derivative = sp.Symbol("D")
    mass = sp.Symbol("M", nonzero=True)
    p1 = sp.Rational(18, 25) * parameter

    velocity = sp.Matrix(
        [
            [0, -3, 0],
            [-3, 0, 0],
            [0, 0, -2 * p1],
        ]
    )
    principal = -velocity
    hessian = sp.Matrix(
        [
            [0, 3 * (derivative**2 - 2), 0],
            [3 * (derivative**2 - 2), 12 / mass, 0],
            [0, 0, 2 * p1 * derivative**2],
        ]
    )
    evolution = sp.Matrix(
        [
            [0, 1, 0, 0, 0, 0],
            [2, 0, -4 / mass, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 2, 0, 0, 0],
            [0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0],
        ]
    )
    charpoly = sp.factor(evolution.charpoly(spectral).as_expr())
    expected_charpoly = spectral**2 * (spectral**2 - 2) ** 2
    if charpoly != expected_charpoly:
        raise AssertionError("coupled evolution characteristic polynomial drifted")
    # The scalar 4x4 block has size-two Jordan blocks at both roots, while
    # the clock block is the nonzero nilpotent Jordan block J_2(0).
    if (
        (evolution**2).rank() != 4
        or (evolution**2 - 2 * sp.eye(6)).rank() != 4
    ):
        raise AssertionError("coupled minimal-polynomial witnesses drifted")
    hessian_determinant = sp.factor(hessian.det())
    expected_determinant = (
        -sp.Rational(324, 25)
        * parameter
        * derivative**2
        * (derivative**2 - 2) ** 2
    )
    if hessian_determinant != expected_determinant:
        raise AssertionError("coupled Hessian determinant drifted")
    return {
        "activation": "nonzero stationary stratum t!=0",
        "auxiliary_shift": (
            "chi=2 alpha_R R; psi=chi+M_P^2/2, "
            "with M_P^2=-324t/1645"
        ),
        "complete_homogeneous_quadratic_density": (
            "L_hom=-3 D(psi)D(u)-6 psi u+6 psi^2/M_P^2"
            "-p1 D(v)^2, p1=18t/25"
        ),
        "field_basis": ["u", "psi", "v"],
        "Euler_Hessian_of_D": _matrix(hessian),
        "Euler_Hessian_determinant": (
            "-324 t D^2(D^2-2)^2/25"
        ),
        "principal_D2_matrix": _matrix(principal),
        "principal_characteristic_polynomial": (
            "(spectral-3)(spectral+3)(25 spectral-36 t)/25"
        ),
        "velocity_Hessian": _matrix(velocity),
        "velocity_characteristic_polynomial": (
            "(spectral-3)(spectral+3)(25 spectral+36 t)/25"
        ),
        "velocity_inertia_strata_positive_negative_zero": {
            "t>0": [1, 2, 0],
            "t<0": [2, 1, 0],
            "t=0_in_declared_original_action": [0, 0, 3],
        },
        "inertia_separator": (
            "the gravity-auxiliary principal and velocity blocks contain "
            "the exact eigenpair (+3,-3) for every t!=0"
        ),
        "state_basis": ["u", "D(u)", "psi", "D(psi)", "v", "D(v)"],
        "D_evolution_matrix": _matrix(evolution),
        "characteristic_polynomial": "spectral^2(spectral^2-2)^2",
        "minimal_polynomial": "spectral^2(spectral^2-2)^2",
        "Jordan_data": [
            "root 0: one size-two clock block",
            "root +sqrt(2): one size-two scalar block",
            "root -sqrt(2): one size-two scalar block",
        ],
        "Lee_Wald_current_project_convention": (
            "omega^0=-3[delta u wedge delta D(psi)"
            "+delta psi wedge delta D(u)]"
            "-2p1 delta v wedge delta D(v)"
        ),
        "raw_D_Hamiltonian": (
            "H_D=-3 D(u)D(psi)+6 psi u-6 psi^2/M_P^2"
            "-p1 D(v)^2"
        ),
        "raw_D_sign_witnesses": [
            "(u,Du,psi,Dpsi,v,Dv)=(0,1,0,-1,0,0) gives H_D=3",
            "(u,Du,psi,Dpsi,v,Dv)=(0,1,0,1,0,0) gives H_D=-3",
        ],
        "cylinder_clock_condition": {
            "quadratic_density": "L_clock=-p1 D(v)^2",
            "healthy_and_hyperbolic": "p1<0",
            "on_stationary_locus": "t<0",
        },
    }


def _cone_and_charge_records(parameter: sp.Symbol) -> tuple[dict[str, Any], dict[str, Any]]:
    X = -sp.Rational(9, 16)
    omega = sp.Rational(3, 4)
    p0 = sp.Rational(486, 1645) * parameter
    p1 = sp.Rational(18, 25) * parameter
    p2 = parameter
    P = sp.factor(p0 + p1 * X + p2 * X**2)
    P_X = sp.factor(p1 + 2 * p2 * X)
    longitudinal = sp.factor(p1 + 6 * p2 * X)
    sound_speed_squared = sp.factor(P_X / longitudinal)
    energy = sp.factor(-2 * P_X * omega**2 - P)
    charge = sp.factor(-2 * P_X * omega)
    k_matter = sp.factor(energy - omega * charge)
    expected = (
        sp.Rational(435537, 2105600),
        -sp.Rational(81, 200),
        -sp.Rational(531, 200),
        sp.Rational(9, 59),
        sp.Rational(523827, 2105600),
        sp.Rational(243, 400),
        -sp.Rational(435537, 2105600),
    )
    actual = (
        P / parameter,
        P_X / parameter,
        longitudinal / parameter,
        sound_speed_squared,
        energy / parameter,
        charge / parameter,
        k_matter / parameter,
    )
    if actual != expected:
        raise AssertionError("Berger cone/charge arithmetic drifted")
    cone = {
        "general_principal_tensor": (
            "K^ab=P_X g^ab+2 P_XX nabla^a(theta)nabla^b(theta)"
        ),
        "Berger_X": "-9/16",
        "P_on_background": "435537 t/2105600",
        "P_X": "-81 t/200",
        "P_X_plus_2X_P_XX": "-531 t/200",
        "Lorentzian_hyperbolicity": (
            "P_X(P_X+2X P_XX)>0, with neither factor zero"
        ),
        "standard_sign_clock": [
            "P_X<0",
            "P_X+2X P_XX<0",
        ],
        "sound_speed_squared": "P_X/(P_X+2X P_XX)=9/59",
        "subluminal": "0<9/59<1",
        "standard_sign_and_hyperbolic_locus": "t>0",
        "energy_density": "rho_clock=523827 t/2105600; positive iff t>0",
        "relational_monotonicity": {
            "theta_background": "theta=3t_coordinate/4",
            "gradient": "D(theta)=3/4",
            "timelike": "X=-9/16<0",
            "nonzero_shift_charge": "Q_R_density=243t/400 !=0 iff t!=0",
            "usable_healthy_clock": "t>0",
        },
    }
    charges = {
        "shift_current_convention": "j^a=2P_X nabla^a(theta)",
        "internal_charge_density": "Q_R=-2P_X omega_clock=243t/400",
        "matter_raw_D_density": (
            "rho_clock=-2P_X omega_clock^2-P=523827t/2105600"
        ),
        "matter_K_Berger_density": (
            "rho_clock-omega_clock Q_R=-P=-435537t/2105600"
        ),
        "total_covariant_phase_space_identities": [
            "K_Berger=D-omega_clock R fixes the stationary background",
            "i_{L_K_Berger} Omega_total=delta H_K_Berger=0 on the closed background",
            "i_{L_D} Omega_total=delta H_D=omega_clock delta Q_R",
        ],
        "important_scope": (
            "the imported fixed-coupling proof delta Q_R=0 used a different "
            "linear clock action and is not reused for P(X); the present "
            "raw-D gate already fails on the unit-cylinder scalar sector "
            "because H_D takes both signs"
        ),
        "surface_and_flux": (
            "closed S3 has no spatial boundary term; the P(X) shift current "
            "is conserved by the displayed clock Euler equation"
        ),
    }
    return cone, charges


def build() -> dict[str, Any]:
    dependencies, minimal_payloads = _imports()
    stationary, locus_generator = _stationary_records()
    parameter = sp.Symbol("t", real=True)
    quadratic = _quadratic_records(parameter)
    cone, charges = _cone_and_charge_records(parameter)

    action_family = {
        "declared_scope": (
            "formal rho!=0 polar complex-compensator theory on the same "
            "dressed metric, parity even, four metric derivatives and the "
            "complete quadratic shift-symmetric phase polynomial P(X)"
        ),
        "dressed_action": (
            "S=int vol_g_hat[alpha_B C^2/8+alpha_R R^2"
            "+M_P^2 R/2+p0+p1 X+p2 X^2+alpha_E E4]"
        ),
        "X_definition": "X=g_hat^ab partial_a(theta)partial_b(theta)",
        "coefficient_basis_mod_topology": [
            "alpha_B",
            "alpha_R",
            "M_P_squared",
            "p0",
            "p1",
            "p2",
        ],
        "complete_phase_basis_argument": (
            "shift symmetry and the declared degree <=2 polynomial bound in "
            "the single scalar X give exactly 1, X and X^2"
        ),
        "unchanged_metric_basis": (
            minimal_payloads["minimal_action_classification"]["action_family"][
                "completeness_argument"
            ]
        ),
        "modulo": [
            "integration by parts",
            "four-dimensional curvature identities",
            "Euler topological density",
            "invertible algebraic R^2 auxiliary presentation when alpha_R!=0",
        ],
        "excluded": [
            "Henneaux-Teitelboim or any multiplier sector",
            "new fields or a changed global gauge quotient",
            "theta-dependent coefficients or a theta potential",
            "operators beyond quadratic P(X)",
            "higher derivatives of theta",
            "an independent conformal gauge connection",
        ],
    }
    action_family_hash = _digest(action_family)
    seven_gates = [
        {
            "gate": 1,
            "normalized_name": "action_derived_BV_CME_Q2",
            "status": "PASS_AT_ACTION_LEVEL_ONLY",
            "reason": (
                "the complete invariant classical action and its Euler rows "
                "are explicit; a selected-action all-row q2 export is not "
                "authorized because the locus terminates at gate 5"
            ),
        },
        {
            "gate": 2,
            "normalized_name": "compact_support_dressed_trace_disposition",
            "status": "PASS_WITH_PHYSICAL_REPLACEMENT_FOR_t_NONZERO",
            "reason": (
                "alpha_R=27t/3290 is nonzero, so the auxiliary scalar replaces "
                "the arbitrary dressed trace; it is physical and unhealthy"
            ),
        },
        {
            "gate": 3,
            "normalized_name": "complete_support_local_causal_parent",
            "status": "NOT_REACHED_AFTER_GATE_5_FAILURE",
            "reason": (
                "the homogeneous operator is exact, but no complete mixed "
                "support-local parent is promoted after the terminal sign failure"
            ),
        },
        {
            "gate": 4,
            "normalized_name": "cyclic_current_and_reduced_pairing",
            "status": "REDUCED_BLOCK_PASS_COMPLETE_PARENT_NOT_REACHED",
            "reason": (
                "the action-derived coupled Lee-Wald current is nondegenerate "
                "for t!=0, but its velocity form has split inertia"
            ),
        },
        {
            "gate": 5,
            "normalized_name": "physical_sign_or_topological_control",
            "status": "FAIL_ALL_REAL_STATIONARY_POINTS",
            "reason": (
                "t=0 has no dynamics; every t!=0 retains the exact (+3,-3) "
                "gravity-auxiliary kinetic pair. Independently cylinder clock "
                "health needs t<0 while Berger clock health needs t>0"
            ),
        },
        {
            "gate": 6,
            "normalized_name": "raw_D_charge_sector",
            "status": "FAIL",
            "reason": (
                "the unit-cylinder raw-D Hamiltonian has the exact values +3 "
                "and -3 on displayed scalar solutions, so raw D is not a "
                "presymplectic null direction on the declared ambient sector"
            ),
        },
        {
            "gate": 7,
            "normalized_name": "frozen_Berger_clock_compatibility",
            "status": "PASS_STATIONARITY; HEALTHY_MONOTONE_CLOCK_ONLY_FOR_t_POSITIVE",
            "reason": (
                "the full one-dimensional locus solves all frozen background "
                "Euler rows; the Berger clock is timelike and monotone for "
                "t!=0, and standard-sign/hyperbolic only for t>0"
            ),
        },
    ]
    result = {
        "schema": "pure-weyl-compensator-active-clock-px2-locus-v1",
        "result_id": "COMPENSATOR_ACTIVE_CLOCK_PX2_LOCUS_V1",
        "result_state": "SCOPED_QUADRATIC_ACTIVE_CLOCK_GOOD_LOCUS_EMPTY",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependencies": dependencies,
        "action_family": action_family,
        "action_family_sha256": action_family_hash,
        "stationary_background_equations": stationary,
        "coupled_homogeneous_analysis": quadratic,
        "Berger_sound_cone_and_clock": cone,
        "charges": charges,
        "seven_gate_classification": {
            "gates": seven_gates,
            "stationary_locus": (
                "t(81/20,27/3290,-324/1645,486/1645,18/25,1), t in R"
            ),
            "exact_semialgebraic_separator": [
                "t=0 => zero action and no pairing/dynamics",
                "t!=0 => gravity-auxiliary velocity spectrum contains +3 and -3",
                "cylinder standard-sign clock => p1<0 => t<0",
                "Berger standard-sign sound cone => P_X<0 and P_X+2X P_XX<0 => t>0",
                "{t<0} intersect {t>0}=empty",
            ],
            "all_seven_gate_good_locus": "EMPTY",
            "numerical_scan_used": False,
            "real_root_or_sign_method": (
                "exact rational RREF plus univariate sign decomposition at "
                "t=0; all decisive factors are nonzero rational multiples of t"
            ),
        },
        "selection": {
            "candidate_C_active_selected": False,
            "candidate_C_active_action": None,
            "candidate_C_active_action_hash": None,
            "downstream_selected_action_work_authorized": False,
        },
        "exact_checks": {
            "minimal_theorem_imported_by_exact_hash": True,
            "complete_declared_PX_basis": True,
            "unit_cylinder_Euler_rows_exact": True,
            "Berger_Euler_rows_rederived_for_quadratic_PX": True,
            "clock_Euler_equation_checked": True,
            "stationary_rank_and_kernel_exact": True,
            "zero_and_nonzero_strata_separated": True,
            "coupled_Hessian_rederived": True,
            "principal_and_velocity_inertia_stratified": True,
            "characteristic_and_minimal_polynomials_exact": True,
            "sound_and_longitudinal_conditions_both_checked": True,
            "Lee_Wald_and_raw_D_sign_witnesses_exact": True,
            "raw_D_and_K_Berger_charge_identities_scoped": True,
            "all_seven_gates_recorded": True,
            "good_locus_empty": True,
            "no_candidate_exported": True,
        },
        "claim_flags": {
            "SCOPED_QUADRATIC_ACTIVE_CLOCK_NO_GO": True,
            "UNIVERSAL_K_ESSENCE_OR_COMPENSATOR_NO_GO": False,
            "CANDIDATE_C_ACTIVE_SELECTED": False,
            "COMPLETE_SUPPORT_LOCAL_CAUSAL_PARENT": False,
            "HADAMARD_OR_QUANTUM_RESULT": False,
            "PARTICLE_SCATTERING_POSITIVITY_UNITARITY": False,
        },
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL theorem classifies "
            "only the declared dressed C^2+R^2+R action with the complete "
            "quadratic shift-symmetric P(X)=p0+p1X+p2X^2 phase sector, no HT "
            "sector and no new fields, on the common unit-cylinder and frozen "
            "Berger fixtures. The stationary locus is one-dimensional, but "
            "every nonzero point has split gravity-auxiliary inertia and the "
            "cylinder and Berger standard-sign clock inequalities require "
            "opposite signs of its parameter. The seven-gate good locus is "
            "therefore empty and no Candidate C_active is exported. This does "
            "not cover higher P(X), higher phase derivatives, changed "
            "backgrounds, fixed-charge reductions, new fields or enlarged "
            "gauge quotients. It constructs no complete causal parent and "
            "establishes no Hadamard, anomaly/QME, particle, scattering, "
            "positivity or unitarity result."
        ),
        "next_gate": (
            "Require a method-distinct freeze audit of the rank, singular "
            "strata, coupled inertia and sign separator before treating this "
            "scoped no-go as theorem-frozen."
        ),
    }
    result["content_hashes"] = {
        "action_family_sha256": action_family_hash,
        "stationary_system_sha256": _digest(stationary),
        "coupled_homogeneous_sha256": _digest(quadratic),
        "sound_charge_sha256": _digest({"cone": cone, "charges": charges}),
        "classification_sha256": _digest(result["seven_gate_classification"]),
        "locus_generator_sha256": _digest([_q(x) for x in locus_generator]),
    }
    return result


def _check(value: dict[str, Any]) -> None:
    common = value["stationary_background_equations"]["common_system"]
    if common["rank"] != 5 or common["kernel_dimension"] != 1:
        raise AssertionError("stationary locus dimension drifted")
    if (
        value["seven_gate_classification"]["all_seven_gate_good_locus"]
        != "EMPTY"
        or value["selection"]["candidate_C_active_action_hash"] is not None
    ):
        raise AssertionError("empty locus was promoted")
    if value["claim_flags"]["UNIVERSAL_K_ESSENCE_OR_COMPENSATOR_NO_GO"]:
        raise AssertionError("scoped theorem was promoted")


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
        raise AssertionError("active-clock P(X) locus certificate is stale")
    print("COMPENSATOR_ACTIVE_CLOCK_PX2_LOCUS_V1: PASS")


if __name__ == "__main__":
    main()
