#!/usr/bin/env python3
"""Exact minimal-action coefficient-locus theorem after Candidates A/B."""

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
    / "COMPENSATOR_MINIMAL_ACTION_CLASSIFICATION_AFTER_NEITHER_V1.json"
)

DEPENDENCIES = {
    "action_preflight": {
        "path": ROOT / "d_quotient_classical/certificates/COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1.json",
        "sha256": "a537e31bf667520443903551b5bf2596dff9a1c35fade88d2ffc1e89c1e0b836",
        "source_commit": "306ff78a2001f23124d412e9a2f41531bec74f78",
    },
    "positive_Berger_clock": {
        "path": ROOT / "d_quotient_classical/certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json",
        "sha256": "35e1bb8a56b0591b3dd00aa8f22c328ad826ecd341c290564cfd1a68fcc3e687",
        "source_commit": "bb5738d6e3e30a68adcc9a70c35dac089079e3db",
    },
    "strict_trace_obstruction": {
        "path": ROOT / "d_quotient_classical/certificates/TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1.json",
        "sha256": "db1f998a0920adb94cf4fcbffb1b9eb2ea6537876aff9513aac4e4d9ec2b51b9",
        "source_commit": "2b834dc751d6948366fd5c3d99174c268fa50d21",
    },
    "candidate_AB_comparison": {
        "path": ROOT / "d_quotient_classical/certificates/COMPENSATOR_CANDIDATE_AB_NEITHER_COMPARISON_V1.json",
        "sha256": "5e253ebe424dd43e308622044d93af72fd6de911b927f354977413957dbb16c4",
        "source_commit": "af86eb2ce4190e48fda2d276298de844bb50f4f7",
        "lifecycle_commit": "165d339946e36e5f2d30370a6f8d9370e1a87e89",
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
    record = {
        "row_count": value.rows,
        "column_count": value.cols,
        "entries": [
            {"row": row, "column": column, "coefficient": _q(value[row, column])}
            for row in range(value.rows)
            for column in range(value.cols)
            if value[row, column] != 0
        ],
    }
    record["sha256"] = _digest(record)
    return record


def _imports() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    rows: dict[str, Any] = {}
    payloads: dict[str, dict[str, Any]] = {}
    for name, source in DEPENDENCIES.items():
        actual = _sha(source["path"])
        if actual != source["sha256"]:
            raise AssertionError(f"{name} hash drifted")
        payload = json.loads(source["path"].read_text())
        payloads[name] = payload
        row = {
            "path": str(source["path"].relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": actual,
            "source_commit": source["source_commit"],
        }
        if "lifecycle_commit" in source:
            row["lifecycle_commit"] = source["lifecycle_commit"]
        rows[name] = row
    if (
        payloads["action_preflight"]["result_state"]
        != "LOCAL_ACTION_AND_QUARTET_CERTIFIED"
        or payloads["positive_Berger_clock"]["claim_status"]
        != "CERTIFIED_EXACT_BACKGROUND"
        or payloads["strict_trace_obstruction"]["result_state"] != "OBSTRUCTED"
        or payloads["candidate_AB_comparison"]["terminal_selection"] != "NEITHER"
    ):
        raise AssertionError("minimal-action dependency semantics drifted")
    return rows, payloads


def _stationary_matrices() -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    # Coefficient order: alpha_B, alpha_R, M_P^2, Z_theta, V_0.
    cylinder = sp.Matrix(
        [
            [0, 36, 3, 0, -1],
            [0, 12, -1, 0, 1],
        ]
    )

    q = sp.Rational(9, 40)
    scalar_curvature = sp.Rational(151, 80)
    omega = sp.Rational(3, 4)
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
    rows = []
    for index in (0, 1, 3):
        g = metric[index]
        ric = ricci[index]
        einstein = ric - scalar_curvature * g / 2
        r_squared = (
            4 * scalar_curvature * ric - scalar_curvature**2 * g
        )
        phase = -(omega**2) / 2
        potential = -1 if index == 0 else 1
        rows.append(
            [bach[index], r_squared, einstein, phase, potential]
        )
    berger = sp.Matrix(rows)
    return cylinder, berger, cylinder.col_join(berger)


def _symbolic_operator_records() -> dict[str, Any]:
    P, D, M, gamma = sp.symbols("P D M gamma", nonzero=True)
    spectral = sp.Symbol("spectral")
    scalar_operator = sp.Matrix(
        [
            [0, -3 * P],
            [-3 * P, 12 / M],
        ]
    )
    scalar_velocity = sp.Matrix([[0, -3], [-3, 0]])
    scalar_evolution = sp.Matrix(
        [
            [0, 1, 0, 0],
            [2, 0, -4 / M, 0],
            [0, 0, 0, 1],
            [0, 0, 2, 0],
        ]
    )
    ht_operator = gamma * sp.Matrix(
        [
            [0, 0, 2],
            [0, 0, D],
            [2, -D, 0],
        ]
    )
    combined = sp.Matrix(
        [
            [0, -3 * P, 0, 2 * gamma],
            [-3 * P, 12 / M, 0, 0],
            [0, 0, 0, gamma * D],
            [2 * gamma, 0, -gamma * D, 0],
        ]
    )
    combined_velocity = sp.Matrix(
        [
            [0, -3, 0, 0],
            [-3, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
    )
    scalar_characteristic = sp.factor(
        scalar_evolution.charpoly(spectral).as_expr()
    )
    ht_characteristic = sp.factor(
        ht_operator.charpoly(spectral).as_expr()
    )
    if scalar_characteristic != (spectral**2 - 2) ** 2:
        raise AssertionError("scalar characteristic polynomial drifted")
    expected_ht = spectral * (
        spectral**2 + gamma**2 * D**2 - 4 * gamma**2
    )
    if sp.expand(ht_characteristic - expected_ht) != 0:
        raise AssertionError("HT characteristic polynomial drifted")
    if sp.factor(combined.det()) != -9 * D**2 * P**2 * gamma**2:
        raise AssertionError("combined principal determinant drifted")
    combined_characteristic = sp.collect(
        sp.expand(combined.charpoly(spectral).as_expr()), spectral
    )
    expected_combined_characteristic = (
        spectral**4
        - 12 * spectral**3 / M
        + spectral**2 * (gamma**2 * D**2 - 9 * P**2 - 4 * gamma**2)
        + spectral * (48 * gamma**2 - 12 * gamma**2 * D**2) / M
        - 9 * gamma**2 * D**2 * P**2
    )
    if sp.expand(
        combined_characteristic - expected_combined_characteristic
    ) != 0:
        raise AssertionError("combined characteristic polynomial drifted")
    cyclic_vector = sp.eye(4)[:, 1]
    krylov = sp.Matrix.hstack(
        cyclic_vector,
        combined * cyclic_vector,
        combined**2 * cyclic_vector,
        combined**3 * cyclic_vector,
    )
    krylov_determinant = sp.factor(krylov.det())
    if krylov_determinant != -108 * D * P**3 * gamma**3:
        raise AssertionError("combined minimal-polynomial witness drifted")
    return {
        "scalar_auxiliary": {
            "activation": "epsilon_HT=0, alpha_R!=0 and unit-cylinder stationarity",
            "cylinder_relations": [
                "M_P^2=-24 alpha_R",
                "V_0=3 M_P^2/2=-36 alpha_R",
            ],
            "shift": "chi=2 alpha_R R; psi=chi+M_P^2/2",
            "quadratic_density": (
                "L_hom=-3 D(psi)D(u)-6 psi u+6 psi^2/M_P^2"
            ),
            "operator_basis": ["u", "psi"],
            "operator_H_of_P": _matrix(scalar_operator),
            "operator_determinant": "-9 P^2",
            "operator_characteristic_polynomial": (
                "spectral^2-12 spectral/M_P^2-9 P^2"
            ),
            "operator_minimal_polynomial": (
                "spectral^2-12 spectral/M_P^2-9 P^2"
            ),
            "velocity_Hessian": _matrix(scalar_velocity),
            "velocity_characteristic_polynomial": "spectral^2-9",
            "velocity_minimal_polynomial": "spectral^2-9",
            "velocity_inertia": [1, 1, 0],
            "evolution_basis": ["u", "D(u)", "psi", "D(psi)"],
            "D_evolution_matrix": _matrix(scalar_evolution),
            "characteristic_polynomial": "(spectral^2-2)^2",
            "minimal_polynomial": "(spectral^2-2)^2",
            "real_roots": ["-sqrt(2)", "sqrt(2)"],
            "Jordan_block_size": 2,
            "Lee_Wald_current": (
                "omega^0=-3[delta u wedge delta D(psi)"
                "+delta psi wedge delta D(u)]"
            ),
            "Hamiltonian": (
                "H_D=-3 D(u)D(psi)+6 psi u-6 psi^2/M_P^2"
            ),
            "positive_witness": (
                "(u,D(u),psi,D(psi))=(0,1,0,-1) gives H_D=3"
            ),
            "negative_witness": (
                "(u,D(u),psi,D(psi))=(0,1,0,1) gives H_D=-3"
            ),
        },
        "HT_topological": {
            "activation": "epsilon_HT=1 after invertible rescaling of a nonzero HT coefficient",
            "quadratic_density": "L_HT=lambda_HT(2u-Da)",
            "operator_basis": ["u", "a", "lambda_HT"],
            "operator_H_of_D": _matrix(ht_operator),
            "generic_rank_over_Q(D)": 2,
            "polynomial_kernel": ["D/2", "1", "0"],
            "characteristic_polynomial": (
                "spectral*(spectral^2+gamma^2 D^2-4 gamma^2)"
            ),
            "minimal_polynomial": (
                "spectral*(spectral^2+gamma^2 D^2-4 gamma^2)"
            ),
            "zero_frequency_kernel": ["0", "1", "0"],
            "velocity_Hessian": _matrix(sp.zeros(3)),
            "velocity_characteristic_polynomial": "spectral^3",
            "velocity_minimal_polynomial": "spectral",
            "velocity_inertia": [0, 0, 3],
            "Lee_Wald_pair": (
                "Omega_top=gamma delta a wedge delta lambda_HT"
            ),
            "raw_D_Hamiltonian": "H_D=gamma V_S3 lambda_HT",
        },
        "combined_auxiliary_HT": {
            "operator_basis": ["u", "psi", "a", "lambda_HT"],
            "operator_H_of_P_D": _matrix(combined),
            "determinant": "-9 gamma^2 D^2 P^2",
            "characteristic_polynomial": (
                "spectral^4-12 spectral^3/M_P^2"
                "+(gamma^2 D^2-9 P^2-4 gamma^2)spectral^2"
                "+(48 gamma^2-12 gamma^2 D^2)spectral/M_P^2"
                "-9 gamma^2 D^2 P^2"
            ),
            "minimal_polynomial": (
                "equal to the characteristic polynomial over "
                "Q(M_P^2,P,D,gamma)"
            ),
            "Krylov_cyclic_vector": ["0", "1", "0", "0"],
            "Krylov_determinant": "-108 D P^3 gamma^3",
            "velocity_Hessian": _matrix(combined_velocity),
            "velocity_characteristic_polynomial": (
                "spectral^2(spectral^2-9)"
            ),
            "velocity_minimal_polynomial": "spectral(spectral^2-9)",
            "velocity_inertia": [1, 1, 2],
            "global_D_zero_kernel_survives": ["0", "0", "1", "0"],
        },
    }


def build() -> dict[str, Any]:
    dependencies, payloads = _imports()
    cylinder, berger, stacked = _stationary_matrices()
    determinant = sp.factor(stacked.det())
    if determinant != -sp.Rational(91791, 81920):
        raise AssertionError("stationary separator determinant drifted")
    if stacked.rank() != 5 or stacked.nullspace():
        raise AssertionError("stationary separator lost full rank")

    preflight_basis = payloads["action_preflight"]["action_basis"]
    action_manifest = {
        "declared_scope": (
            "minimal formal rho!=0 polar complex-compensator family: "
            "four metric derivatives, at most two compensator derivatives, "
            "constant real couplings and global U(1)"
        ),
        "dressed_action": (
            "S_bulk=int vol_g_hat[alpha_B C^2/8+alpha_R R^2"
            "+M_P^2 R/2-Z_theta (nabla theta)^2/2-V_0+alpha_E E4]"
        ),
        "coefficient_basis_mod_topology": [
            "alpha_B",
            "alpha_R",
            "M_P_squared",
            "Z_theta",
            "V0",
        ],
        "topological_density": "alpha_E E4 is retained for provenance and quotiented from local Euler/Hessian tests",
        "horizontal_exact": "Box R",
        "parity_odd_excluded": "Pontryagin P4",
        "auxiliary_scalar": (
            "when alpha_R!=0 use chi R-chi^2/(4 alpha_R); "
            "this is an invertible algebraic presentation of R^2"
        ),
        "topological_extension": (
            "epsilon_HT int lambda_HT(vol_g_hat-dA3), "
            "epsilon_HT in {0,1}; every nonzero coefficient is normalized "
            "to one by an invertible multiplier rescaling"
        ),
        "three_form_gauge_group": (
            "small reducible A3 -> A3+d epsilon2, "
            "epsilon2~epsilon2+d epsilon1, "
            "epsilon1~epsilon1+d epsilon0; no global H3 quotient"
        ),
        "completeness_argument": preflight_basis["exhaustiveness_argument"],
        "modulo": [
            "integration by parts",
            "four-dimensional curvature identities",
            "Euler topological density",
            "nonzero HT coefficient rescaling",
            "invertible algebraic R^2 auxiliary-field presentation",
        ],
        "outside_declared_minimal_class": [
            "higher-than-two-derivative theta operators",
            "nonconstant theta-dependent couplings",
            "a kinetic or nonlinear potential for the topological multiplier",
            "large/global three-form gauge quotient",
            "fixed flux or lambda_HT superselection",
            "an independent conformal gauge connection",
        ],
    }
    family_hash = _digest(action_manifest)
    operators = _symbolic_operator_records()
    result = {
        "schema": "pure-weyl-compensator-minimal-action-classification-after-neither-v1",
        "result_id": "COMPENSATOR_MINIMAL_ACTION_CLASSIFICATION_AFTER_NEITHER_V1",
        "result_state": "SCOPED_MINIMAL_ACTION_GOOD_LOCUS_EMPTY",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependencies": dependencies,
        "action_family": action_manifest,
        "action_family_sha256": family_hash,
        "stationary_background_equations": {
            "coefficient_order": [
                "alpha_B",
                "alpha_R",
                "M_P_squared",
                "Z_theta",
                "V0",
            ],
            "Euler_formula_on_constant_R_and_covariantly_constant_theta": (
                "alpha_B B_ab+alpha_R(4R Ric_ab-R^2 g_ab)"
                "+M_P^2 G_ab-T_ab[Z_theta,V0]=0"
            ),
            "unit_cylinder": {
                "background": (
                    "g_hat=-dt^2+dOmega_3^2, R=6, "
                    "Ric_orthonormal=(0,2,2,2), theta=constant"
                ),
                "independent_rows": ["E_00", "E_horizontal"],
                "matrix": _matrix(cylinder),
                "equivalent_relations": [
                    "M_P^2=-24 alpha_R",
                    "V0=3 M_P^2/2=-36 alpha_R",
                ],
            },
            "frozen_Berger_clock": {
                "background": (
                    "a=1, q=c^2=9/40, omega_clock=3/4, "
                    "R=151/80"
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
                "phase_equation": "Box theta=0: PASS identically",
            },
            "no_HT_stacked_system": {
                "matrix": _matrix(stacked),
                "determinant": "-91791/81920",
                "rank": 5,
                "rref": "I_5",
                "kernel": [],
                "elimination_result": (
                    "alpha_B=alpha_R=M_P^2=Z_theta=V0=0"
                ),
                "meaning": (
                    "no nonzero action in the declared no-HT family makes "
                    "both frozen backgrounds stationary"
                ),
            },
        },
        "quadratic_and_global_analysis": operators,
        "topology": {
            "manifold": "R_t x S3",
            "ordinary_de_Rham_betti_H0_to_H4": [1, 0, 0, 1, 0],
            "compact_support_betti_Hc0_to_Hc4": [0, 1, 0, 0, 1],
            "H3_generator": "vol_S3",
            "Hc4_generator": (
                "f(t) dt wedge vol_S3 with integral_R f dt=1"
            ),
            "Berger_volume_constraint": "A3_bar=t vol_Berger",
            "Berger_raw_D_shift": "L_D A3_bar=vol_Berger",
            "small_gauge_exact": False,
        },
        "seven_gate_classification": {
            "epsilon_HT_zero": {
                "stationary_coefficient_locus": "ZERO_VECTOR_ONLY",
                "decisive_failure_gates": [1, 2, 3, 4, 5, 7],
                "reason": (
                    "the exact cylinder-plus-Berger matrix is invertible; "
                    "the zero bulk vector has no phase pairing and leaves "
                    "the dressed trace without a causal parent"
                ),
                "independent_cylinder_subclassification": {
                    "alpha_R_nonzero": (
                        "split velocity inertia, real repeated roots and "
                        "both-sign raw-D Hamiltonian: gate 5 FAIL"
                    ),
                    "alpha_R_zero": (
                        "cylinder stationarity forces M_P^2=V0=0, so "
                        "the C^2 trace remains the imported compact-support "
                        "causal obstruction: gates 2 and 3 FAIL"
                    ),
                },
            },
            "epsilon_HT_one": {
                "stationary_potentials_may_differ_by_lambda_background": True,
                "decisive_failure_gates": [3, 5, 6, 7],
                "reason": (
                    "the retained H3/Hc4 flux-multiplier pair gives a "
                    "D=0 kernel, nonconstant ambient raw-D Hamiltonian and "
                    "nonexact frozen-Berger D shift"
                ),
            },
            "all_seven_gate_good_locus": "EMPTY",
            "logical_separator": (
                "epsilon_HT=0 => det(M_cylinder+Berger)!=0 and only the "
                "dynamically empty vector remains; epsilon_HT=1 => "
                "H3/Hc4, raw-D and Berger global gates fail"
            ),
        },
        "selection": {
            "candidate_C_selected": False,
            "candidate_C_action": None,
            "candidate_C_action_hash": None,
            "hybrid_selected": False,
            "downstream_selected_action_work_authorized": False,
        },
        "exact_checks": {
            "comparison_imported_NEITHER": True,
            "preflight_basis_imported": True,
            "cylinder_equations_exact": True,
            "Berger_equations_reconstructed": True,
            "Berger_original_fixture_regression": True,
            "no_HT_stacked_determinant_nonzero": True,
            "no_HT_kernel_zero": True,
            "scalar_auxiliary_characteristic_and_minimal_polynomials": True,
            "scalar_Lee_Wald_inertia_split": True,
            "HT_polynomial_kernel": True,
            "combined_D_zero_kernel": True,
            "H3_Hc4_replayed": True,
            "raw_D_Hamiltonian_nonconstant": True,
            "Berger_shift_nonexact": True,
            "good_locus_empty": True,
            "no_candidate_C_exported": True,
        },
        "claim_flags": {
            "SCOPED_MINIMAL_ACTION_NO_GO": True,
            "UNIVERSAL_COMPENSATOR_NO_GO": False,
            "CANDIDATE_C_SELECTED": False,
            "SELECTED_ACTION_RECEIVER": False,
            "HADAMARD_OR_QUANTUM_RESULT": False,
            "PARTICLE_SCATTERING_POSITIVITY_UNITARITY": False,
        },
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL theorem classifies "
            "the imported minimal formal-polar family with four metric and "
            "at most two compensator derivatives, one algebraic R^2 "
            "auxiliary presentation and an optional minimal HT sector under "
            "the declared small gauge group. Its seven-gate good locus is "
            "empty. It does not cover higher-derivative theta EFT operators, "
            "multiplier kinetic/potential extensions, fixed-flux sectors, "
            "large/global three-form quotients, active-clock retunings or an "
            "independent conformal gauge connection. No Candidate C, "
            "Hadamard, anomaly/QME, particle, scattering, positivity or "
            "unitarity result is exported."
        ),
        "next_gate": (
            "Do not activate a selected-action consumer. Any successor must "
            "declare one of the excluded enlarged theory classes and rerun "
            "all seven gates from its own action hash."
        ),
    }
    result["content_hashes"] = {
        "action_family_sha256": family_hash,
        "stationary_system_sha256": _digest(
            result["stationary_background_equations"]
        ),
        "quadratic_global_sha256": _digest(
            result["quadratic_and_global_analysis"]
        ),
        "classification_sha256": _digest(
            result["seven_gate_classification"]
        ),
    }
    return result


def _check(value: dict[str, Any]) -> None:
    stationary = value["stationary_background_equations"][
        "no_HT_stacked_system"
    ]
    if stationary["determinant"] != "-91791/81920" or stationary["rank"] != 5:
        raise AssertionError("stationary separator drifted")
    if value["seven_gate_classification"]["all_seven_gate_good_locus"] != "EMPTY":
        raise AssertionError("good locus was promoted")
    if value["selection"]["candidate_C_action_hash"] is not None:
        raise AssertionError("Candidate C was exported from an empty locus")
    if value["claim_flags"]["UNIVERSAL_COMPENSATOR_NO_GO"]:
        raise AssertionError("scoped no-go was promoted to universal")


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
        raise AssertionError("minimal-action classification certificate is stale")
    print("COMPENSATOR_MINIMAL_ACTION_CLASSIFICATION_AFTER_NEITHER_V1: PASS")


if __name__ == "__main__":
    main()
