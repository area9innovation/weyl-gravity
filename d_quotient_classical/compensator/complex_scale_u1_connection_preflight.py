#!/usr/bin/env python3
"""Exact separated real-scale/compact-U(1) compensator preflight."""

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
    / "d_quotient_classical/compensator/"
    "COMPENSATOR_COMPLEX_SCALE_U1_CONNECTION_PREFLIGHT_V1.json"
)

IMPORTS = {
    "level3b": {
        "path": (
            ROOT
            / "d_quotient_classical/certificates/"
            "COMPENSATOR_CONVENTION_CORRECT_HORNDESKI_LEVEL3B_NO_GO_V1.json"
        ),
        "sha256": "78258a1a76c81183699e8fe6923c8eccb79c030ec8174c7fe8716a97a923713c",
        "source_commit": "801bff0c49a3f293fcf9402d554939b761b71341",
        "result_id": "COMPENSATOR_CONVENTION_CORRECT_HORNDESKI_LEVEL3B_NO_GO_V1",
        "result_state": "SCOPED_LEVEL3B_CORRECT_HORNDESKI_GOOD_LOCUS_EMPTY",
    },
    "minimal_ladder": {
        "path": (
            ROOT
            / "d_quotient_classical/compensator/"
            "COMPENSATOR_MINIMAL_LADDER_SYNTHESIS_AFTER_LEVEL3B_V1.json"
        ),
        "sha256": "a942ff6a15af0c8a79978dc22ff2cc128a238c3abd6feb2685197d48deaeaf37",
        "source_commit": "2497b1ace8415594bca64d8ba38e25475ca16858",
        "result_id": "COMPENSATOR_MINIMAL_LADDER_SYNTHESIS_AFTER_LEVEL3B_V1",
        "result_state": "SCOPED_MINIMAL_COMPENSATOR_LADDER_EXHAUSTED_WITHOUT_SELECTED_ACTION",
    },
    "level4_real_connection": {
        "path": (
            ROOT
            / "d_quotient_classical/certificates/"
            "COMPENSATOR_INDEPENDENT_WEYL_CONNECTION_LEVEL4_NO_GO_V1.json"
        ),
        "sha256": "d1037ef2fa9222d02513d093c27a02e6fc5da71ec0b731d3b9b2cd2f51e52652",
        "source_commit": "255c53253d7d846ebbe33418d03bad791945dfd4",
        "result_id": "COMPENSATOR_INDEPENDENT_WEYL_CONNECTION_LEVEL4_NO_GO_V1",
        "result_state": "SCOPED_LEVEL4_INDEPENDENT_WEYL_CONNECTION_GOOD_LOCUS_EMPTY",
    },
    "positive_Berger_clock": {
        "path": (
            ROOT
            / "d_quotient_classical/certificates/"
            "POSITIVE_BERGER_CLOCK_BACKGROUND.json"
        ),
        "sha256": "35e1bb8a56b0591b3dd00aa8f22c328ad826ecd341c290564cfd1a68fcc3e687",
        "source_commit": "bb5738d6e3e30a68adcc9a70c35dac089079e3db",
        "result_id": "POSITIVE_BERGER_CLOCK_BACKGROUND",
        "claim_status": "CERTIFIED_EXACT_BACKGROUND",
    },
    "Berger_charge": {
        "path": (
            ROOT
            / "d_quotient_classical/certificates/"
            "BERGER_FIXED_COUPLING_DELTA_CHARGE.json"
        ),
        "sha256": "0ae894432b065f9f4ba116e6e2d42e69d1d60cd37dbf6ef21a14d7073c75b786",
        "source_commit": "cc5df8d547f7d2119282590a824ce92cd1d76d17",
        "result_id": "BERGER_FIXED_COUPLING_DELTA_CHARGE",
        "scientific_verdict": "D_GAUGE",
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
            {"row": i, "column": j, "coefficient": _q(value[i, j])}
            for i in range(value.rows)
            for j in range(value.cols)
            if value[i, j] != 0
        ],
    }
    return {**core, "sha256": _digest(core)}


def _load_imports() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    records: dict[str, Any] = {}
    payloads: dict[str, dict[str, Any]] = {}
    for key, spec in IMPORTS.items():
        actual = _sha(spec["path"])
        payload = json.loads(spec["path"].read_text())
        if actual != spec["sha256"]:
            raise AssertionError(f"{key} hash drifted")
        if payload.get("result_id") != spec["result_id"]:
            raise AssertionError(f"{key} result id drifted")
        for state_key in ("result_state", "claim_status", "scientific_verdict"):
            if state_key in spec and payload.get(state_key) != spec[state_key]:
                raise AssertionError(f"{key} {state_key} drifted")
        records[key] = {
            "path": str(spec["path"].relative_to(ROOT)),
            "sha256": actual,
            "source_commit": spec["source_commit"],
            "result_id": spec["result_id"],
            **{
                state_key: spec[state_key]
                for state_key in (
                    "result_state",
                    "claim_status",
                    "scientific_verdict",
                )
                if state_key in spec
            },
        }
        payloads[key] = payload

    if (
        payloads["level3b"]["terminal_verdict"]["selected_level3b_action"]
        or payloads["minimal_ladder"]["terminal_verdict"]["selected_action"]
        or payloads["minimal_ladder"]["terminal_verdict"]["next_gate"]
        != "SEPARATED_SCALE_U1_CONNECTION_PREFLIGHT"
        or payloads["level4_real_connection"]["terminal_verdict"][
            "selected_level4_action"
        ]
    ):
        raise AssertionError("activation semantics drifted")
    return records, payloads


def _action_basis() -> dict[str, Any]:
    return {
        "fields": [
            "g_ab real Lorentz metric",
            "Phi=rho exp(i theta), rho>0 on the formal polar chart",
            "W_a real noncompact Weyl-scale connection",
            "A_a real compact U(1) connection",
        ],
        "reality_and_discrete_symmetry": [
            "g,rho,theta,W,A real",
            "complex conjugation sends (theta,A) to (-theta,-A)",
            "the mixed scalar rho D_W rho dot B is excluded because it is odd under complex conjugation",
        ],
        "gauge_parameters": [
            "omega: original real Weyl",
            "eta: candidate real scale",
            "gamma: compact internal U(1)",
        ],
        "transformations": {
            "delta_g": "2(omega+a eta) g",
            "delta_rho": "-(omega+b eta) rho",
            "delta_theta": "s eta+gamma",
            "delta_W": "-d(omega+a eta)",
            "delta_A": "-d(s eta+gamma)",
            "B": "d theta+A",
            "delta_B": "0",
        },
        "curvatures": {
            "F_W": "dW",
            "H_A": "dA",
            "R_W": "R-6 nabla_a W^a-6 W_a W^a",
            "Ricci_W_TF": "symmetric trace-free Ricci tensor of the torsion-free Weyl connection",
        },
        "density": (
            "sqrt(-g){alpha_C C^2/8+alpha_0 R_W^2"
            "+alpha_2 Ricci_W_TF^2-zeta_W F_W^2/4"
            "-zeta_A H_A^2/4-chi F_W.H_A/2"
            "-kappa_r(D_W rho)^2/2-kappa_R rho^2 R_W/12"
            "-kappa_theta rho^2 B^2/2-lambda rho^4/4}"
        ),
        "coefficient_order": [
            "alpha_C",
            "alpha_0",
            "alpha_2",
            "zeta_W",
            "zeta_A",
            "chi",
            "kappa_r",
            "kappa_R",
            "kappa_theta",
            "lambda",
        ],
        "four_dimensional_curvature_reduction": (
            "Ricci_TF^2=(C^2+R^2/6-E4)/2, hence on W=0 "
            "alpha_B_eff=alpha_C+4 alpha_2 and "
            "alpha_R_eff=alpha_0+alpha_2/12 modulo Euler"
        ),
        "completeness": (
            "Modulo Euler and total divergences, the displayed terms exhaust "
            "the parity-even minimal polar scalar terms with at most two "
            "derivatives and the dimension-four Abelian/Weyl geometric "
            "quadratic terms. F_W.H_A is the allowed real kinetic mixing. "
            "No charged source, extra compensator, higher derivative, "
            "C-odd scalar mixing or dimensionful spurion is admitted."
        ),
    }


def _gauge_rank() -> dict[str, Any]:
    a, b, s = sp.symbols("a b s", real=True)
    delta = sp.factor(a - b)
    # Rows: log metric, log rho, longitudinal W, theta, longitudinal A.
    # Columns: omega, eta, gamma.
    gauge = sp.Matrix(
        [
            [1, a, 0],
            [-1, -b, 0],
            [-1, -a, 0],
            [0, s, 1],
            [0, -s, -1],
        ]
    )
    minor = sp.factor(gauge.extract([0, 1, 3], [0, 1, 2]).det())
    if minor != delta:
        raise AssertionError("gauge independence minor drifted")
    dependent = gauge.subs(b, a)
    reducibility = sp.Matrix([-a, 1, -s])
    if dependent.rank() != 2 or dependent * reducibility != sp.zeros(5, 1):
        raise AssertionError("dependent gauge complex drifted")
    if gauge.subs({a: 2, b: 3, s: 5}).rank() != 3:
        raise AssertionError("independent gauge rank drifted")
    return {
        "symbol_row_order": [
            "logarithmic metric scale",
            "logarithmic radial scale",
            "normalized longitudinal W",
            "phase theta",
            "normalized longitudinal A",
        ],
        "ghost_column_order": ["omega", "eta", "gamma"],
        "gauge_symbol": _matrix(gauge),
        "independence_minor": "Delta=a-b",
        "dressed_metric": "g_hat=(rho/f)^2 g",
        "dressed_metric_variation": "delta_eta g_hat=2 Delta eta g_hat",
        "strata": {
            "Delta_nonzero": {
                "rank": 3,
                "reducibility": "NONE",
                "candidate_scale_contracts_dressed_trace": True,
            },
            "Delta_zero": {
                "rank": 2,
                "reducibility_vector_(omega,eta,gamma)": ["-a", "1", "-s"],
                "identity": "G(-a,1,-s)^T=0",
                "candidate_column": "a times omega column+s times gamma column",
                "candidate_scale_contracts_dressed_trace": False,
            },
        },
    }


def _ward_system() -> dict[str, Any]:
    delta, kr, kR, kt, lam = sp.symbols(
        "Delta kappa_r kappa_R kappa_theta lambda"
    )
    generators = [
        delta * kr,
        delta * kR,
        delta * kt,
        delta * lam,
    ]
    independent = [sp.factor(value / delta) for value in generators]
    if independent != [kr, kR, kt, lam]:
        raise AssertionError("Ward elimination drifted")
    return {
        "constant_eta_weights": {
            "(D_W rho)^2": "2 Delta",
            "rho^2 R_W": "2 Delta",
            "rho^2 B^2": "2 Delta",
            "rho^4": "4 Delta",
            "F_W^2,H_A^2,F_W.H_A": "0",
        },
        "key_observation": (
            "B=dtheta+A is derivative-gauge invariant, but the density "
            "sqrt(-g) rho^2 g^{ab}B_aB_b still has constant eta weight "
            "2(a-b). The compact connection cannot cancel that weight."
        ),
        "exact_Ward_ideal_generators": [_q(value) for value in generators],
        "strata": {
            "Delta_nonzero": {
                "forced_zero": [
                    "kappa_r",
                    "kappa_R",
                    "kappa_theta",
                    "lambda",
                ],
                "phase_residue_Z_theta": "0",
                "dressed_trace_gauged": True,
            },
            "Delta_zero": {
                "candidate_scale_column": "REDUCIBLE",
                "dressed_trace_gauged_by_candidate": False,
                "scalar_coefficients": "not constrained by constant eta weight",
            },
        },
        "exhaustiveness": (
            "A constant eta already kills every derivative improvement, so "
            "local Ward terms can add constraints but cannot reopen the "
            "Delta-nonzero branch."
        ),
    }


def _bv_and_dressed_trace() -> dict[str, Any]:
    return {
        "minimal_generators": [
            "g_ab",
            "rho",
            "theta",
            "W_a",
            "A_a",
            "xi^a",
            "omega",
            "eta",
            "gamma",
            "and canonical antifields",
        ],
        "BRST_rows_Delta_generic": {
            "Q g": "L_xi g+2(omega+a eta)g",
            "Q rho": "L_xi rho-(omega+b eta)rho",
            "Q theta": "L_xi theta+s eta+gamma",
            "Q W": "L_xi W-d(omega+a eta)",
            "Q A": "L_xi A-d(s eta+gamma)",
            "Q xi": "xi^nu partial_nu xi",
            "Q omega": "L_xi omega",
            "Q eta": "L_xi eta",
            "Q gamma": "L_xi gamma",
        },
        "odd_pairing": (
            "the direct canonical cotangent pairing on "
            "(g,rho,theta,W,A,xi,omega,eta,gamma) and antifields"
        ),
        "Delta_zero_reducible_completion": {
            "reducibility_vector_(omega,eta,gamma)": ["-a", "1", "-s"],
            "even_ghost_for_ghost": "z, ghost number 2",
            "additional_rows": {
                "Q omega": "L_xi omega-a z",
                "Q eta": "L_xi eta+z",
                "Q gamma": "L_xi gamma-s z",
                "Q z": "L_xi z",
            },
            "identity": (
                "the z contribution to every field row is "
                "G(-a,1,-s)^T=0"
            ),
            "irreducible_alternative": (
                "quotient eta to a omega+s gamma and retain only omega,gamma"
            ),
            "physical_effect": (
                "no additional dressed-trace contraction after either "
                "reducible presentation"
            ),
        },
        "dressed_trace_constraint": {
            "g_hat": "(rho/f)^2 g",
            "linearized_dressed_conformal_variable": (
                "u_hat=u+delta rho/f in the normalization delta g=2u g"
            ),
            "Q_eta_u_hat": "Delta eta",
            "Delta_nonzero": (
                "u_hat is gauge, but the Ward ideal removes the complete "
                "declared scalar action"
            ),
            "Delta_zero": (
                "Q_eta u_hat=0 and the candidate column is reducible, so the "
                "old dressed trace is not contracted"
            ),
        },
        "nilpotency_scope": (
            "The three internal factors are Abelian Diff-scalars. Their "
            "semidirect Chevalley-Eilenberg rows square to zero; on Delta=0 "
            "the displayed reducibility identity cancels the ghost-for-ghost "
            "contribution exactly."
        ),
    }


def _stationary_systems() -> dict[str, Any]:
    # Effective coefficient order:
    # alpha_B_eff, alpha_R_eff, K_R=kappa_R f^2,
    # Z_theta=kappa_theta f^2, V=lambda f^4.
    cylinder = sp.Matrix(
        [
            [0, 36, -sp.Rational(1, 2), 0, -sp.Rational(1, 4)],
            [0, 12, sp.Rational(1, 6), 0, sp.Rational(1, 4)],
            [0, 0, 1, 0, 1],
        ]
    )
    cylinder_kernel = cylinder.nullspace()
    expected_cylinder = [
        sp.Matrix([1, 0, 0, 0, 0]),
        sp.Matrix([0, 0, 0, 1, 0]),
        sp.Matrix([0, -sp.Rational(1, 144), -1, 0, 1]),
    ]
    if (
        cylinder.rank() != 2
        or cylinder.rref()[1] != (1, 2)
        or cylinder_kernel != expected_cylinder
    ):
        raise AssertionError("cylinder stationarity drifted")

    b2 = sp.Rational(9, 16)
    berger = sp.Matrix(
        [
            [
                sp.Rational(961, 9600),
                sp.Rational(22801, 6400),
                -sp.Rational(151, 960),
                -b2 / 2,
                -sp.Rational(1, 4),
            ],
            [
                sp.Rational(403, 9600),
                sp.Rational(20083, 6400),
                sp.Rational(3, 320),
                -b2 / 2,
                sp.Rational(1, 4),
            ],
            [
                sp.Rational(31, 1920),
                -sp.Rational(3473, 1280),
                sp.Rational(133, 960),
                -b2 / 2,
                sp.Rational(1, 4),
            ],
            [0, 0, sp.Rational(151, 480), -b2, 1],
            [0, 0, 0, 1, 0],
        ]
    )
    berger_kernel = berger.nullspace()
    expected_berger = sp.Matrix(
        [0, -sp.Rational(1600, 22801), -sp.Rational(480, 151), 0, 1]
    )
    positive_fixture = sp.Matrix(
        [5, 0, 1, 1, sp.Rational(119, 480)]
    )
    pivot_minor = sp.factor(
        berger.extract([0, 1, 2, 4], [0, 1, 2, 3]).det()
    )
    if (
        berger.rank() != 4
        or berger.rref()[1] != (0, 1, 2, 3)
        or berger_kernel != [expected_berger]
        or pivot_minor != sp.Rational(2120493, 40960000)
        or berger[:4, :] * positive_fixture != sp.zeros(4, 1)
        or berger * positive_fixture != sp.Matrix([0, 0, 0, 0, 1])
    ):
        raise AssertionError("Berger stationarity/Gauss system drifted")

    return {
        "coefficient_order": [
            "alpha_B_eff=alpha_C+4 alpha_2",
            "alpha_R_eff=alpha_0+alpha_2/12",
            "K_R=kappa_R f^2",
            "Z_theta=kappa_theta f^2",
            "V=lambda f^4",
        ],
        "metric_Euler_formula": (
            "alpha_B_eff B_ab+alpha_R_eff(4R Ric_ab-R^2 g_ab)"
            "-K_R G_ab/6-T_ab=0, "
            "T_ab=Z_theta B_aB_b+"
            "(Z_theta beta^2/2-V/4)g_ab"
        ),
        "radial_Euler_formula": (
            "K_R R/6-Z_theta beta^2+V=0"
        ),
        "internal_connection_Euler_formula": (
            "nabla_b(zeta_A H_A^{ba}+chi F_W^{ba})"
            "=Z_theta B^a"
        ),
        "unit_cylinder_constant_phase": {
            "background": (
                "g=-dt^2+dOmega_3^2, R=6, W=A=0, rho=f, beta=B_t=0"
            ),
            "row_order": ["E_00", "E_horizontal", "E_rho"],
            "matrix": _matrix(cylinder),
            "rank": 2,
            "pivot_columns": [1, 2],
            "kernel_generators": [
                [_q(x) for x in vector] for vector in cylinder_kernel
            ],
            "relations": [
                "K_R=144 alpha_R_eff",
                "V=-144 alpha_R_eff",
                "alpha_B_eff and Z_theta free",
            ],
            "clock_status": "NO_CLOCK_BACKGROUND_B_t_ZERO",
        },
        "frozen_Berger_clock_lift": {
            "background": (
                "a=1, q=c^2=9/40, R=151/80, W=A=0, rho=f, "
                "beta=B_t=3/4"
            ),
            "row_order": [
                "E_00",
                "E_horizontal",
                "E_vertical",
                "E_rho",
                "normalized temporal U1 Gauss row",
            ],
            "matrix": _matrix(berger),
            "rank": 4,
            "pivot_columns": [0, 1, 2, 3],
            "rank_witness_minor": "2120493/40960000",
            "kernel_generator": [_q(x) for x in expected_berger],
            "complete_locus": (
                "(alpha_B_eff,alpha_R_eff,K_R,Z_theta,V)"
                "=t(0,-1600/22801,-480/151,0,1)"
            ),
            "ungauged_positive_fixture_regression": {
                "coefficient_vector": ["5", "0", "1", "1", "119/480"],
                "metric_and_radial_rows": "ZERO_EXACTLY",
                "normalized_compact_Gauss_residual": "1",
                "interpretation": (
                    "The certified positive Berger scalar clock remains an "
                    "exact solution before the phase is gauged; precisely the "
                    "new compact Gauss row excludes it."
                ),
            },
            "decisive_relation": "Z_theta=0",
            "clock_status": "ZERO_PHASE_PAIRING_AND_ZERO_INTERNAL_CHARGE",
        },
        "scope": (
            "The printed matrices are complete for the homogeneous "
            "flat-connection lift of the certified cylinder and Berger "
            "fixtures. The temporal Gauss separator is stronger: by the "
            "closed-S3 divergence theorem it applies to every smooth "
            "stationary invariant spatial connection, including nonzero "
            "magnetic F_W or H_A."
        ),
    }


def _principal_and_charge() -> dict[str, Any]:
    zW, zA, chi = sp.symbols("zeta_W zeta_A chi", real=True)
    kinetic = sp.Matrix([[zW, chi], [chi, zA]])
    if sp.factor(kinetic.det()) != zW * zA - chi**2:
        raise AssertionError("vector kinetic determinant drifted")
    return {
        "transverse_vector_principal_form": {
            "curvature_order": ["F_W", "H_A"],
            "kinetic_matrix": _matrix(kinetic),
            "positive_Maxwell_cone_conditions": [
                "zeta_W>0",
                "zeta_A>0",
                "zeta_W zeta_A-chi^2>0",
            ],
        },
        "scale_Stueckelberg_block": {
            "D_W_rho": "d rho-W rho",
            "W_mass_coefficient_at_rho=f": "(kappa_R-kappa_r)f^2",
            "dressed_Einstein_coefficient": "M_eff^2=-kappa_R f^2/6",
            "independent_scale_branch": (
                "Delta nonzero forces kappa_R=kappa_r=0, so the declared "
                "minimal scalar/trace principal block vanishes"
            ),
        },
        "phase_Stueckelberg_block": {
            "gauge_invariant_one_form": "B=d theta+A",
            "residue": "Z_theta=kappa_theta f^2",
            "healthy_scalar_or_longitudinal_sign": "Z_theta>0",
            "independent_scale_branch": "Z_theta=0 by the constant Ward ideal",
            "Berger_stationary_branch": "Z_theta=0 by the temporal Gauss row",
        },
        "closed_S3_Gauss_identity": {
            "local_equation": (
                "nabla_b(zeta_A H_A^{ba}+chi F_W^{ba})=Z_theta B^a"
            ),
            "integrated_equation": (
                "Q_int=integral_S3 n_a Z_theta B^a"
                "=boundary_flux(zeta_A H_A+chi F_W)=0"
            ),
            "homogeneous_clock_consequence": (
                "f nonzero and B_t=beta nonzero imply kappa_theta=0"
            ),
            "source_independence": (
                "No smooth source-free stationary invariant magnetic sector "
                "changes the temporal integrated constraint on closed S3."
            ),
        },
        "raw_D_and_clock_charge": {
            "phase_current_before_gauging": "J_theta^a=-Z_theta B^a",
            "internal_U1_charge": "ZERO_ON_THE_GAUSS_CONSTRAINT_SURFACE",
            "phase_contribution_to_raw_D_moment_map": (
                "beta delta Q_int=0 on every allowed closed-S3 tangent"
            ),
            "scale_gauge_charge": (
                "constraint charge with no boundary term on closed S3"
            ),
            "interpretation": (
                "The compact connection converts the former global phase "
                "charge into a Gauss constraint. A gauge orbit is not a "
                "physical relational clock."
            ),
        },
    }


def _terminal_verdict() -> dict[str, Any]:
    return {
        "result": "SCOPED_SEPARATED_SCALE_U1_MINIMAL_GOOD_LOCUS_EMPTY",
        "selected_action": False,
        "healthy_locus": "EMPTY",
        "first_incompatible_conditions": [
            "Delta!=0 is required for a new dressed-trace gauge direction",
            "Delta*kappa_theta=0 is required by the exact constant scale Ward identity",
            "kappa_theta f^2>0 is required for a nonzero healthy phase residue",
        ],
        "independent_Gauss_separator": [
            "B_t!=0 is required for the frozen homogeneous phase clock",
            "the source-free compact-U1 Gauss law on closed S3 gives kappa_theta f^2 B_t=0",
        ],
        "complete_strata": {
            "Delta_nonzero": (
                "three independent gauge columns, but the scalar Ward ideal "
                "sets kappa_r,kappa_R,kappa_theta,lambda to zero"
            ),
            "Delta_zero": (
                "the candidate scale column is reducible against the original "
                "Weyl and compact-U1 columns and does not gauge the dressed trace"
            ),
        },
        "Berger_disposition": (
            "the exact stationary/Gauss kernel has Z_theta=0 and therefore "
            "no phase pairing or internal clock charge"
        ),
        "cylinder_disposition": (
            "the constant-phase cylinder can be stationary but supplies no "
            "clock; on the independent scale branch its scalar/trace action vanishes"
        ),
        "causal_completion_activated": False,
        "nonlinear_or_quantum_promotion": False,
        "next_gate": (
            "No automatic next action. Any successor must change the "
            "representation content (for example a second modulus or charged "
            "source sector) or abandon the nonzero closed-S3 phase-clock gate."
        ),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    if (
        payload["result_state"]
        != "SCOPED_SEPARATED_SCALE_U1_MINIMAL_GOOD_LOCUS_EMPTY"
        or payload["dependency_tags"]
        != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
    ):
        raise AssertionError("result state or dependency boundary drifted")
    gauge = payload["gauge_rank_and_reducibility"]["strata"]
    if (
        gauge["Delta_nonzero"]["rank"] != 3
        or not gauge["Delta_nonzero"][
            "candidate_scale_contracts_dressed_trace"
        ]
        or gauge["Delta_zero"]["rank"] != 2
        or gauge["Delta_zero"]["candidate_scale_contracts_dressed_trace"]
        or gauge["Delta_zero"]["reducibility_vector_(omega,eta,gamma)"]
        != ["-a", "1", "-s"]
    ):
        raise AssertionError("gauge rank/reducibility promotion detected")
    if payload["constant_scale_Ward_system"][
        "exact_Ward_ideal_generators"
    ] != [
        "Delta*kappa_r",
        "Delta*kappa_R",
        "Delta*kappa_theta",
        "Delta*lambda",
    ]:
        raise AssertionError("constant Ward ideal drifted")
    berger = payload["stationary_systems"]["frozen_Berger_clock_lift"]
    if (
        berger["decisive_relation"] != "Z_theta=0"
        or berger["kernel_generator"]
        != ["0", "-1600/22801", "-480/151", "0", "1"]
        or berger["ungauged_positive_fixture_regression"][
            "metric_and_radial_rows"
        ]
        != "ZERO_EXACTLY"
        or berger["ungauged_positive_fixture_regression"][
            "normalized_compact_Gauss_residual"
        ]
        != "1"
    ):
        raise AssertionError("Berger/Gauss promotion detected")
    verdict = payload["terminal_verdict"]
    if (
        verdict["healthy_locus"] != "EMPTY"
        or verdict["selected_action"]
        or verdict["causal_completion_activated"]
        or verdict["nonlinear_or_quantum_promotion"]
        or any(payload["claim_flags"].values())
    ):
        raise AssertionError("downstream promotion detected")
    if "content_hashes" in payload:
        expected = {
            "imports_sha256": _digest(payload["imports"]),
            "action_sha256": _digest(payload["action_basis"]),
            "gauge_sha256": _digest(payload["gauge_rank_and_reducibility"]),
            "ward_sha256": _digest(payload["constant_scale_Ward_system"]),
            "bv_sha256": _digest(payload["bv_and_dressed_trace"]),
            "stationary_sha256": _digest(payload["stationary_systems"]),
            "principal_charge_sha256": _digest(
                payload["principal_forms_and_charges"]
            ),
            "verdict_sha256": _digest(payload["terminal_verdict"]),
            "claim_boundary_sha256": _digest(payload["claim_boundary"]),
        }
        if payload["content_hashes"] != expected:
            raise AssertionError("content hash drifted")


def build() -> dict[str, Any]:
    imports, _ = _load_imports()
    action = _action_basis()
    gauge = _gauge_rank()
    ward = _ward_system()
    stationary = _stationary_systems()
    principal = _principal_and_charge()
    bv = _bv_and_dressed_trace()
    verdict = _terminal_verdict()
    claim_boundary = (
        "This exact preflight covers one formal-polar complex compensator, "
        "one real Weyl-scale connection, one independent compact U(1) "
        "connection, the displayed three gauge generators, complex "
        "conjugation, the complete declared minimal parity-even terms and "
        "the certified unit-cylinder and frozen-Berger homogeneous fixtures "
        "on closed S3. The compact connection makes B=dtheta+A derivative-"
        "gauge invariant but does not remove its constant scale weight; "
        "independently, its Gauss law turns the former global phase charge "
        "into a zero constraint charge. Arbitrary charged sources, extra "
        "moduli, nontrivial boundaries, higher derivatives, other "
        "backgrounds, general metric-affine geometry and nonstationary "
        "electric sectors are outside scope. No selected action, causal "
        "parent, nonlinear q2, Hadamard state, anomaly/QME, particle, "
        "scattering, positivity or unitarity theorem follows."
    )
    payload = {
        "schema": "pure-weyl-compensator-complex-scale-u1-connection-preflight-v1",
        "result_id": "COMPENSATOR_COMPLEX_SCALE_U1_CONNECTION_PREFLIGHT_V1",
        "result_state": "SCOPED_SEPARATED_SCALE_U1_MINIMAL_GOOD_LOCUS_EMPTY",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "action_basis": action,
        "gauge_rank_and_reducibility": gauge,
        "constant_scale_Ward_system": ward,
        "bv_and_dressed_trace": bv,
        "stationary_systems": stationary,
        "principal_forms_and_charges": principal,
        "terminal_verdict": verdict,
        "claim_flags": {
            "SELECTED_ACTION": False,
            "COMPLETE_CAUSAL_PARENT": False,
            "NONLINEAR_Q2": False,
            "HADAMARD_OR_QUANTUM": False,
            "ARBITRARY_COMPLEX_OR_METRIC_AFFINE_GEOMETRY_EXCLUDED": False,
            "CHARGED_SOURCE_SECTORS_EXCLUDED": False,
        },
        "claim_boundary": claim_boundary,
    }
    payload["content_hashes"] = {
        "imports_sha256": _digest(imports),
        "action_sha256": _digest(action),
        "gauge_sha256": _digest(gauge),
        "ward_sha256": _digest(ward),
        "bv_sha256": _digest(bv),
        "stationary_sha256": _digest(stationary),
        "principal_charge_sha256": _digest(principal),
        "verdict_sha256": _digest(verdict),
        "claim_boundary_sha256": _digest(claim_boundary),
    }
    validate_payload(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            raise SystemExit("generated separated scale/U1 result drifted")
        print(f"{payload['result_id']}: PASS")
        return
    OUTPUT.write_text(rendered)
    print(OUTPUT)


if __name__ == "__main__":
    main()
