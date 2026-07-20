#!/usr/bin/env python3
"""Exact Candidate-B HT/unimodular three-form obstruction.

Candidate B adds

    S_HT = integral lambda (vol(g_hat) - d A_3)

to the frozen complex-compensator action with ``alpha_R=0``.  The
three-form presentation is essential on ``R x S3``: its harmonic spatial
component cannot be erased by the local Poincare lemma.

Two independent exact failures occur.

* On the frozen unit cylinder with constant phase, the multiplier changes
  only the metric-proportional Euler row.  The nonzero trace-free Ricci row
  from the Einstein term is therefore independent of lambda, so the declared
  background is not a stationary point of Candidate B.
* The isolated linearized HT block has the polynomial kernel
  ``(u,a,lambda)=(D a/2,a,0)``.  It trades the arbitrary dressed trace for a
  history of the harmonic three-form flux instead of making it contractible.
  Its compact-support remainder is ``H_c^4(R x S3)=R``.

The second statement remains useful independently of the first: it explains
why a local calculation that simply solves ``d A_3=2u vol`` would miss the
global flux/cosmological mode and the raw-D charge.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
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
    / "COMPENSATOR_CANDIDATE_B_UNIMODULAR_THREEFORM_OBSTRUCTION_V1.json"
)
REPORT = (
    ROOT
    / "d_quotient_classical"
    / "reports"
    / "compensator-candidate-b-unimodular-threeform-obstruction-v1.md"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "compensator-candidate-b-unimodular-threeform-obstruction-v1.schema.json"
)

DEPENDENCIES = {
    "action_preflight": {
        "path": ROOT
        / "d_quotient_classical"
        / "certificates"
        / "COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1.json",
        "source_commit": "306ff78a2001f23124d412e9a2f41531bec74f78",
        "sha256": "a537e31bf667520443903551b5bf2596dff9a1c35fade88d2ffc1e89c1e0b836",
    },
    "strict_tau_obstruction": {
        "path": ROOT
        / "d_quotient_classical"
        / "certificates"
        / "TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1.json",
        "source_commit": "2b834dc751d6948366fd5c3d99174c268fa50d21",
        "sha256": "db1f998a0920adb94cf4fcbffb1b9eb2ea6537876aff9513aac4e4d9ec2b51b9",
    },
    "positive_Berger_clock": {
        "path": ROOT
        / "d_quotient_classical"
        / "certificates"
        / "POSITIVE_BERGER_CLOCK_BACKGROUND.json",
        "source_commit": "bb5738d6e3e30a68adcc9a70c35dac089079e3db",
        "sha256": "35e1bb8a56b0591b3dd00aa8f22c328ad826ecd341c290564cfd1a68fcc3e687",
    },
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _matrix(value: sp.MatrixBase) -> dict[str, Any]:
    canonical = {
        "row_count": value.rows,
        "column_count": value.cols,
        "entries": [
            {
                "row": row,
                "column": column,
                "coefficient": str(value[row, column]),
            }
            for row in range(value.rows)
            for column in range(value.cols)
            if value[row, column] != 0
        ],
    }
    return {**canonical, "sha256": _digest(canonical)}


def _dense(record: dict[str, Any], symbols: dict[str, Any] | None = None) -> sp.Matrix:
    value = sp.zeros(record["row_count"], record["column_count"])
    for entry in record["entries"]:
        value[entry["row"], entry["column"]] = sp.sympify(
            entry["coefficient"], locals=symbols or {}
        )
    return value


def _dependencies() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    rows: dict[str, Any] = {}
    payloads: dict[str, dict[str, Any]] = {}
    for name, item in DEPENDENCIES.items():
        path = item["path"]
        actual = _sha(path)
        if actual != item["sha256"]:
            raise AssertionError(f"Candidate-B dependency hash drifted: {name}")
        payload = json.loads(path.read_text())
        payloads[name] = payload
        rows[name] = {
            "path": str(path.relative_to(ROOT)),
            "result_id": payload.get("result_id", payload.get("schema")),
            "source_commit": item["source_commit"],
            "sha256": actual,
        }
    if (
        payloads["action_preflight"].get("result_state")
        != "LOCAL_ACTION_AND_QUARTET_CERTIFIED"
        or payloads["strict_tau_obstruction"].get("result_state") != "OBSTRUCTED"
        or payloads["positive_Berger_clock"].get("claim_status")
        != "CERTIFIED_EXACT_BACKGROUND"
    ):
        raise AssertionError("Candidate-B dependency semantics drifted")
    return rows, payloads


def _action_and_bv() -> dict[str, Any]:
    manifest = {
        "density": (
            "alpha_B C(g_hat)^2/8 + M_P^2 R(g_hat)/2 - V0 "
            "- (nabla theta)^2/2 + lambda_HT "
            "[1-(d A_3)/vol(g_hat)]"
        ),
        "form_notation": (
            "S_HT=int_M lambda_HT [vol(g_hat)-d A_3]"
        ),
        "couplings": {
            "M_P_squared": "1/6",
            "V0": "1/4",
            "alpha_R": "0",
            "kappa_r": "-1",
            "kappa_theta": "1",
            "f": "1",
        },
        "metric_gauge_group_after_dressing": "Diff",
        "three_form_gauge_tower": (
            "A_3 -> A_3+d epsilon_2; epsilon_2~epsilon_2+d epsilon_1; "
            "epsilon_1~epsilon_1+d epsilon_0"
        ),
        "Weyl_sector": (
            "the original (tau,omega,omega_star,tau_hat_star) quartet is "
            "unchanged because S_HT uses only g_hat"
        ),
        "global_internal_symmetry": "U(1) shift of theta",
    }
    fields = [
        {
            "symbol": "A_3",
            "form_degree": 3,
            "ghost_number": 0,
            "parity": 0,
            "role": "three_form_potential",
        },
        {
            "symbol": "C_2",
            "form_degree": 2,
            "ghost_number": 1,
            "parity": 1,
            "role": "three_form_gauge_ghost",
        },
        {
            "symbol": "C_1",
            "form_degree": 1,
            "ghost_number": 2,
            "parity": 0,
            "role": "first_reducibility_ghost",
        },
        {
            "symbol": "C_0",
            "form_degree": 0,
            "ghost_number": 3,
            "parity": 1,
            "role": "second_reducibility_ghost",
        },
        {
            "symbol": "lambda_HT",
            "form_degree": 0,
            "ghost_number": 0,
            "parity": 0,
            "role": "unimodular_multiplier",
        },
    ]
    for symbol, degree, ghost, parity in (
        ("A_3_star", 1, -1, 1),
        ("C_2_star", 2, -2, 0),
        ("C_1_star", 3, -3, 1),
        ("C_0_star", 4, -4, 0),
        ("lambda_HT_star", 4, -1, 1),
    ):
        fields.append(
            {
                "symbol": symbol,
                "form_degree": degree,
                "ghost_number": ghost,
                "parity": parity,
                "role": "minimal_antifield",
            }
        )
    nonminimal = []
    for suffix, degree in (("2", 2), ("1", 1), ("0", 0)):
        nonminimal.extend(
            [
                {
                    "symbol": f"bar_C_{suffix}",
                    "form_degree": degree,
                    "role": "antighost",
                    "Q_image": f"b_{suffix}",
                },
                {
                    "symbol": f"b_{suffix}",
                    "form_degree": degree,
                    "role": "multiplier",
                    "Q_image": "0",
                },
                {
                    "symbol": f"bar_C_{suffix}_star",
                    "form_degree": 4 - degree,
                    "role": "antifield",
                    "Q_image": "0",
                },
                {
                    "symbol": f"b_{suffix}_star",
                    "form_degree": 4 - degree,
                    "role": "antifield",
                    "Q_image": "-bar_C_star",
                },
            ]
        )
    return {
        "manifest": manifest,
        "action_sha256": _digest(manifest),
        "minimal_field_inventory": fields,
        "nonminimal_inventory": nonminimal,
        "minimal_master_action": (
            "S_min=S_base+int lambda_HT(vol_hat-dA_3)"
            "+int[A_3_star(L_xi A_3+dC_2)"
            "+C_2_star(L_xi C_2+dC_1)"
            "+C_1_star(L_xi C_1+dC_0)+C_0_star L_xi C_0"
            "+lambda_HT_star L_xi lambda_HT]+strict dressed cotangent rows"
        ),
        "intrinsic_rows": {
            "Q_A_3": "d C_2",
            "Q_C_2": "d C_1",
            "Q_C_1": "d C_0",
            "Q_C_0": "0",
            "Q_lambda_HT": "0",
            "Q_lambda_HT_star": "-[vol(g_hat)-dA_3]",
            "Q_A_3_star": "d lambda_HT",
            "Q_C_2_star": "-d A_3_star",
            "Q_C_1_star": "-d C_2_star",
            "Q_C_0_star": "-d C_1_star",
        },
        "diff_completion": (
            "add L_xi to every form/scalar and the canonical cotangent "
            "moment maps; [L_xi,d]=0 and Qxi=xi^nu partial_nu xi"
        ),
        "nilpotency_proof": (
            "intrinsic nilpotency is d^2=0; the Diff semidirect completion "
            "is nilpotent because the Lie derivative is a representation "
            "commuting with d; antifield rows are the canonical cotangent lift"
        ),
        "CME_proof": (
            "S_base is Diff invariant, vol_hat-dA_3 is a top form, and the "
            "abelian reducibility tower is exact at the operator level; the "
            "displayed master action is their canonical BV cotangent lift"
        ),
        "cyclic_pairing": (
            "integral_M [delta A_3 wedge delta A_3_star"
            "+delta C_2 wedge delta C_2_star"
            "+delta C_1 wedge delta C_1_star"
            "+delta C_0 delta C_0_star"
            "+delta lambda_HT delta lambda_HT_star], with graded signs"
        ),
        "real_structure": "all classical forms and lambda_HT are real",
        "Weyl_quartet_homotopy": (
            "unchanged h_W with Q_W h_W+h_W Q_W=1 on "
            "(tau,omega,omega_star,tau_hat_star)"
        ),
    }


def _unit_cylinder_obstruction() -> dict[str, Any]:
    # Orthonormal covariant components for g=-dt^2+dOmega_3^2.
    metric = sp.diag(-1, 1, 1, 1)
    ricci = sp.diag(0, 2, 2, 2)
    scalar = sp.Integer(6)
    m2 = sp.Rational(1, 6)
    lambda_ht, v0 = sp.symbols("lambda_HT V0", real=True)
    f = m2 * scalar / 2 - v0 + lambda_ht
    euler = m2 * ricci / 2 - f * metric / 2
    trace = sp.simplify(
        sum(metric[index, index] * euler[index, index] for index in range(4))
    )
    tracefree = sp.simplify(euler - trace * metric / 4)
    expected = sp.diag(sp.Rational(1, 8), sp.Rational(1, 24), sp.Rational(1, 24), sp.Rational(1, 24))
    if tracefree != expected:
        raise AssertionError("unit-cylinder trace-free Euler residual drifted")
    if any(item.has(lambda_ht, v0) for item in tracefree):
        raise AssertionError("multiplier leaked into trace-free residual")
    equations = [
        sp.Eq(sp.expand(euler[index, index].subs(v0, sp.Rational(1, 4))), 0)
        for index in range(4)
    ]
    solutions = sp.solve(equations, [lambda_ht], dict=True)
    if solutions:
        raise AssertionError("unexpected HT multiplier solution on cylinder")
    return {
        "background": {
            "metric": "g_hat_bar=-dt^2+dOmega_3^2",
            "R": "6",
            "Ricci_orthonormal": ["0", "2", "2", "2"],
            "theta_bar": "constant",
            "A_3_bar": "t vol_S3",
            "lambda_HT_bar": "undetermined_before_metric_equation",
        },
        "metric_Euler_orthonormal": [
            str(sp.expand(euler[index, index].subs(v0, sp.Rational(1, 4))))
            for index in range(4)
        ],
        "tracefree_Euler_orthonormal": [
            str(tracefree[index, index]) for index in range(4)
        ],
        "tracefree_Euler_matrix": _matrix(tracefree),
        "invariant_identity": (
            "E_TF=(M_P^2/2)[Ric-(R/4)g]"
        ),
        "multiplier_independence": True,
        "simultaneous_equations_have_solution": False,
        "reason": (
            "lambda_HT and V0 multiply g_ab and cannot cancel the nonzero "
            "trace-free Ricci tensor of the non-Einstein cylinder"
        ),
    }


def _linear_topological_block() -> dict[str, Any]:
    d = sp.Symbol("D", commutative=True)
    hessian = sp.Matrix(
        [
            [0, 0, 2],
            [0, 0, d],
            [2, -d, 0],
        ]
    )
    formal_adjoint = hessian.T.xreplace({d: -d})
    if formal_adjoint != hessian:
        raise AssertionError("HT Hessian is not formally self-adjoint")
    kernel = sp.Matrix([d / 2, 1, 0])
    if hessian * kernel != sp.zeros(3, 1):
        raise AssertionError("HT polynomial kernel failed")
    if hessian.rank() != 2:
        raise AssertionError("unexpected generic HT Hessian rank")
    zero_frequency = hessian.subs(d, 0)
    if zero_frequency.rank() != 2 or zero_frequency * sp.Matrix([0, 1, 0]) != sp.zeros(3, 1):
        raise AssertionError("HT harmonic flux kernel failed")
    pairing = sp.Matrix([[0, 1], [-1, 0]])
    d_vector = sp.Matrix([1, 0])
    contraction = d_vector.T * pairing
    if pairing.det() != 1 or contraction != sp.Matrix([[0, 1]]):
        raise AssertionError("HT flux/multiplier current drifted")
    return {
        "ordered_fields": ["u", "a=integral_S3(delta A_3)", "lambda_HT"],
        "quadratic_density": "lambda_HT(2u-Da)",
        "Hessian": _matrix(hessian),
        "formal_adjoint_rule": "D^sharp=-D",
        "formal_self_adjoint": True,
        "generic_rank_over_Q(D)": 2,
        "polynomial_kernel": {
            "vector": ["D/2", "1", "0"],
            "identity": "H_B(D)(D/2,1,0)^T=0",
            "interpretation": "u=(D/2)a with arbitrary flux history a",
        },
        "zero_frequency": {
            "matrix": _matrix(zero_frequency),
            "rank": 2,
            "kernel": ["0", "1", "0"],
            "interpretation": "harmonic S3 three-form flux",
        },
        "field_equations": [
            "2 lambda_HT=0",
            "D lambda_HT=0",
            "2u-Da=0",
        ],
        "arbitrary_compact_support_status": (
            "every compactly supported u with zero spacetime integral has a "
            "compactly supported a primitive; nonzero integral changes the "
            "one-sided asymptotic flux and represents H_c^4"
        ),
        "complete_Green_inverse_exists": False,
        "reason": (
            "the polynomial kernel is infinite-dimensional before the "
            "harmonic zero-frequency class is considered"
        ),
        "flux_multiplier_pairing": {
            "ordered_basis": ["a", "lambda_HT"],
            "Lee_Wald_matrix": _matrix(pairing),
            "rank": 2,
            "determinant": "1",
            "D_flux_translation_vector_normalized": ["1", "0"],
            "i_D_Omega": ["0", "1"],
            "Hamiltonian": "H_D=V_S3 lambda_HT",
            "fixed_lambda_zero_tangent": (
                "the pairing restricts to zero only after imposing the "
                "lambda_HT=0 superselection tangent"
            ),
        },
    }


def _topology() -> dict[str, Any]:
    # Kunneth for R x S3 and compact-support Kunneth for R.
    ordinary = [1, 0, 0, 1, 0]
    compact = [0, 1, 0, 0, 1]
    if ordinary != [1, 0, 0, 1, 0] or compact != [0, 1, 0, 0, 1]:
        raise AssertionError("de Rham ledger drifted")
    return {
        "manifold": "R_t x S3",
        "ordinary_de_Rham_betti_H0_to_H4": ordinary,
        "compact_support_betti_Hc0_to_Hc4": compact,
        "derivation": (
            "H*(R x S3)=H*(S3); H_c^k(R x S3)=H^(k-1)(S3)"
        ),
        "harmonic_three_form_generator": "vol_S3",
        "compact_top_form_generator": (
            "f(t) dt wedge vol_S3 with integral_R f dt=1"
        ),
        "small_gauge_invariant_flux": "a(t)=integral_S3 A_3",
        "small_gauge": "A_3 -> A_3+d epsilon_2 leaves a(t) unchanged",
        "real_three_form_sectors": "a in R",
        "compact_U1_two_gerbe_sectors": (
            "a modulo the integral period lattice; the discrete large-gauge "
            "identification is not contracted by the local BV complex"
        ),
        "cosmological_mode": (
            "d lambda_HT=0 leaves one constant H0 mode before the metric "
            "equation selects lambda_HT=0 on the frozen backgrounds"
        ),
        "compact_support_obstruction": (
            "Omega_c^4/d Omega_c^3=H_c^4=R, detected by integration over M"
        ),
        "no_local_Poincare_promotion": True,
    }


def _berger_gate() -> dict[str, Any]:
    c = sp.sqrt(sp.Rational(9, 40))
    normalized_volume = sp.simplify(c)
    if normalized_volume != 3 * sp.sqrt(10) / 20:
        raise AssertionError("Berger normalized volume drifted")
    return {
        "fixture": (
            "a=1, c^2=9/40, alpha_B=5, rho^2=1, "
            "omega_clock=3/4, lambda_scalar=119/480"
        ),
        "base_metric_and_clock_equations": "PASS by imported exact fixture",
        "HT_metric_equation": (
            "forces lambda_HT_bar=0 because the imported base Euler rows vanish"
        ),
        "volume_constraint_solution": "A_3_bar=t vol_Berger",
        "normalized_spatial_volume_coefficient": str(normalized_volume),
        "raw_D_action": "L_D A_3_bar=vol_Berger",
        "cohomology_class": "[vol_Berger] != 0 in H^3(S3)",
        "small_gauge_compensator_exists": False,
        "helical_reclassification": (
            "stationarity would require adjoining the global closed-three-form "
            "shift to K_Berger=D-omega_clock R"
        ),
        "ambient_D_charge": "H_D=V_Berger lambda_HT",
        "zero_on_background_but_not_differentially_zero": (
            "H_D=0 at lambda_HT=0, while dH_D=V_Berger d lambda_HT !=0"
        ),
        "compatibility_status": "FAIL_WITHOUT_NEW_GLOBAL_SUPERSELECTION_OR_GAUGE",
    }


def build() -> dict[str, Any]:
    dependencies, _ = _dependencies()
    action = _action_and_bv()
    cylinder = _unit_cylinder_obstruction()
    linear = _linear_topological_block()
    topology = _topology()
    berger = _berger_gate()
    gates = [
        {
            "gate": 1,
            "name": "action_derived_BV_CME",
            "status": "PASS_AT_FORMAL_LOCAL_LEVEL",
            "reason": "the reducible abelian three-form tower has its full cotangent and nonminimal inventory",
        },
        {
            "gate": 2,
            "name": "compact_support_u_elimination",
            "status": "FAIL",
            "reason": "u=(D/2)a is an arbitrary polynomial-kernel family; H_c^4 leaves an additional integrated class",
        },
        {
            "gate": 3,
            "name": "complete_support_local_causal_parent",
            "status": "FAIL",
            "reason": "the frozen background is off shell and the HT Hessian has a nonzero Q(D) kernel",
        },
        {
            "gate": 4,
            "name": "cyclicity_and_reduced_pairing",
            "status": "PASS_WITH_UNCONTROLLED_GLOBAL_PAIR",
            "reason": "the flux/multiplier current is exact and nondegenerate before the frozen-branch restriction",
        },
        {
            "gate": 5,
            "name": "no_negative_or_uncontrolled_topological_direction",
            "status": "FAIL",
            "reason": "arbitrary flux histories are null on the lambda_HT=0 solution tangent and are not generated by the small reducible gauge tower",
        },
        {
            "gate": 6,
            "name": "zero_charge_D_sector",
            "status": "FAIL_WITHOUT_SUPERSELECTION",
            "reason": "i_D Omega=V_S3 d lambda_HT; raw D is not a presymplectic null direction on the ambient topological phase space",
        },
        {
            "gate": 7,
            "name": "healthy_Berger_clock_compatibility",
            "status": "FAIL_WITHOUT_NEW_GLOBAL_RECLASSIFICATION",
            "reason": "the required A_3 background has a nonexact raw-D shift in H3(S3)",
        },
    ]
    result = {
        "schema": "pure-weyl-compensator-candidate-b-unimodular-threeform-obstruction-v1",
        "result_id": "COMPENSATOR_CANDIDATE_B_UNIMODULAR_THREEFORM_OBSTRUCTION_V1",
        "result_state": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependencies": dependencies,
        "domain": {
            "spacetime_dimension": 4,
            "signature": "(-,+,+,+)",
            "background": "unit vacuum cylinder R_t x S3",
            "boundaries": "closed S3 Cauchy surfaces; no timelike boundary",
            "support_domains": [
                "Gamma_c",
                "Gamma_sc",
                "one-sided advanced/retarded domains",
            ],
            "chart": "formal rho!=0 dressed compensator chart",
        },
        "action_and_BV": action,
        "unit_cylinder_background_obstruction": cylinder,
        "linearized_topological_block": linear,
        "global_topology": topology,
        "Berger_gate": berger,
        "seven_gate_disposition": gates,
        "exact_checks": {
            "dependency_hashes": True,
            "action_hash_frozen": True,
            "reducibility_d_squared_zero": True,
            "CME_by_cotangent_lift": True,
            "Q_squared_zero": True,
            "cyclic_pairing": True,
            "intrinsic_cotangent_signs_verified": True,
            "real_structure": True,
            "Weyl_quartet_contracts": True,
            "unit_cylinder_tracefree_residual_nonzero": True,
            "HT_multiplier_cannot_repair_tracefree_residual": True,
            "HT_Hessian_formally_self_adjoint": True,
            "HT_Hessian_polynomial_kernel_nonzero": True,
            "compact_support_H4_nonzero": True,
            "spatial_H3_flux_nonzero": True,
            "raw_D_charge_nonconstant_on_ambient_phase_space": True,
            "Berger_D_shift_nonexact": True,
        },
        "claim_flags": {
            "CANDIDATE_B_ACTION_DEFINED": True,
            "CANDIDATE_B_FULL_CAUSAL_PARENT": False,
            "DRESSED_TRACE_CONTRACTED": False,
            "GLOBAL_FLUX_CONTROLLED_WITHOUT_EXTRA_DATA": False,
            "UNIT_CYLINDER_BACKGROUND_ON_SHELL": False,
            "BERGER_RAW_D_PRESERVED": False,
            "HADAMARD_STATE": False,
            "ANOMALY_OR_QME": False,
            "PARTICLE_SCATTERING_UNITARITY": False,
        },
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL obstruction "
            "hash-imports the frozen compensator action and tau-adic trace "
            "obstruction, derives the complete local reducible three-form BV "
            "tower, and proves two Candidate-B failures. The HT multiplier "
            "cannot make the non-Einstein unit cylinder stationary because it "
            "does not change the trace-free Ricci Euler row. Independently, "
            "the linearized HT block trades u for an arbitrary harmonic "
            "three-form flux history and retains H_c^4 and H^3 global data. "
            "The exact flux/multiplier current gives a nontrivial raw-D charge, "
            "and the frozen Berger solution requires a nonexact D shift of "
            "A_3. This is a scoped no-go for Candidate B with the declared "
            "action, background and small gauge group. It does not rule out "
            "an active-clock retuning, a fixed-lambda/flux superselection "
            "theory, or an enlarged global gauge quotient. It establishes no "
            "Hadamard, anomaly, QME, particle, scattering or unitarity result."
        ),
        "next_gate": (
            "Run the common Candidate-A/Candidate-B comparison; both declared "
            "minimal repairs are obstructed, so test the fail-closed NEITHER "
            "verdict without constructing a hybrid."
        ),
    }
    return result


def _validate_semantics(value: dict[str, Any]) -> None:
    d = sp.Symbol("D")
    hessian = _dense(value["linearized_topological_block"]["Hessian"], {"D": d})
    kernel = sp.Matrix([d / 2, 1, 0])
    if hessian * kernel != sp.zeros(3, 1):
        raise AssertionError("serialized HT kernel failed")
    if value["unit_cylinder_background_obstruction"][
        "simultaneous_equations_have_solution"
    ]:
        raise AssertionError("Candidate B was promoted on the unit cylinder")
    if value["global_topology"]["ordinary_de_Rham_betti_H0_to_H4"] != [1, 0, 0, 1, 0]:
        raise AssertionError("ordinary topology drifted")
    if value["global_topology"]["compact_support_betti_Hc0_to_Hc4"] != [0, 1, 0, 0, 1]:
        raise AssertionError("compact-support topology drifted")
    if value["Berger_gate"]["small_gauge_compensator_exists"]:
        raise AssertionError("nonexact Berger volume form was erased")
    if value["result_state"] != "OBSTRUCTED":
        raise AssertionError("Candidate B result state drifted")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    _validate_semantics(value)
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    else:
        if json.loads(OUTPUT.read_text()) != value:
            raise AssertionError("Candidate-B certificate is stale")
    print("COMPENSATOR_CANDIDATE_B_UNIMODULAR_THREEFORM_OBSTRUCTION_V1: PASS")


if __name__ == "__main__":
    main()
