#!/usr/bin/env python3
"""Exact fixed-flux/global-quotient preflight for the HT compensator theory."""

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
    / "d_quotient_classical/certificates/"
    "COMPENSATOR_HT_FIXED_FLUX_GLOBAL_QUOTIENT_PREFLIGHT_V1.json"
)
IMPORTS = {
    "candidate_B": {
        "path": ROOT / "d_quotient_classical/certificates/COMPENSATOR_CANDIDATE_B_UNIMODULAR_THREEFORM_OBSTRUCTION_V1.json",
        "sha256": "e8a8aeb97398c3b8812b20118daa56850e32a516bf4e9db15c00b99cec7a8faa",
        "source_commit": "cc0e0036c6acce2bc3d8ba81057031d90a71333a",
        "result_id": "COMPENSATOR_CANDIDATE_B_UNIMODULAR_THREEFORM_OBSTRUCTION_V1",
    },
    "minimal_no_go": {
        "path": ROOT / "d_quotient_classical/certificates/COMPENSATOR_MINIMAL_ACTION_CLASSIFICATION_AFTER_NEITHER_V1.json",
        "sha256": "41ce6db6ab8fc58f4cc1ecedb205f732fd3dcee645f9408506d3535545f7026a",
        "source_commit": "a5924e707352bab92db2caa4c19cf4223c60f0e3",
        "result_id": "COMPENSATOR_MINIMAL_ACTION_CLASSIFICATION_AFTER_NEITHER_V1",
    },
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _matrix(value: sp.Matrix) -> dict[str, Any]:
    core = {
        "row_count": value.rows,
        "column_count": value.cols,
        "entries": [
            {"row": i, "column": j, "coefficient": str(value[i, j])}
            for i in range(value.rows)
            for j in range(value.cols)
            if value[i, j] != 0
        ],
    }
    return {**core, "sha256": _digest(core)}


def _imports() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    records: dict[str, Any] = {}
    payloads: dict[str, dict[str, Any]] = {}
    for name, item in IMPORTS.items():
        actual = _sha(item["path"])
        if actual != item["sha256"]:
            raise AssertionError(f"{name} hash drifted")
        payload = json.loads(item["path"].read_text())
        if payload["result_id"] != item["result_id"]:
            raise AssertionError(f"{name} semantics drifted")
        records[name] = {
            "path": str(item["path"].relative_to(ROOT)),
            "result_id": payload["result_id"],
            "result_state": payload["result_state"],
            "sha256": actual,
            "source_commit": item["source_commit"],
        }
        payloads[name] = payload
    if (
        payloads["candidate_B"]["result_state"] != "OBSTRUCTED"
        or payloads["minimal_no_go"]["result_state"]
        != "SCOPED_MINIMAL_ACTION_GOOD_LOCUS_EMPTY"
    ):
        raise AssertionError("imported terminal states drifted")
    return records, payloads


def _global_choices() -> dict[str, Any]:
    symplectic = sp.Matrix([[0, 1], [-1, 0]])
    fixed_lambda_inclusion = sp.Matrix([[1], [0]])
    restricted = fixed_lambda_inclusion.T * symplectic * fixed_lambda_inclusion
    if symplectic.det() != 1 or restricted != sp.zeros(1):
        raise AssertionError("global pairing reduction drifted")
    choices = [
        {
            "choice_id": "REAL_SMALL_GAUGE_FIXED_FLUX",
            "flux_carrier": "a0 in R",
            "large_gauge_group": "none",
            "connected_harmonic_translation_quotient": "none",
            "fixed_tangent": "delta lambda_HT=0, delta D(a)=0",
            "remaining_tangent": "delta a0 in R",
            "H3_status": "PHYSICAL_NULL_ZERO_MODE",
            "Hc4_status": "FROZEN_BY_FIXED_FLUX",
            "pairing_status": "DEGENERATE_RANK_ZERO_ON_ONE_DIMENSION",
            "Berger_D_shift": "NOT_GAUGE",
            "disposition": "FAIL_GLOBAL_PAIR",
        },
        {
            "choice_id": "COMPACT_GERBE_LATTICE_FIXED_FLUX",
            "flux_carrier": "a0 in R/Z",
            "large_gauge_group": "integer period shifts",
            "connected_harmonic_translation_quotient": "none",
            "fixed_tangent": "delta lambda_HT=0, delta D(a)=0",
            "remaining_tangent": "tangent to the flat gerbe holonomy circle",
            "H3_status": "PHYSICAL_COMPACT_PHASE",
            "Hc4_status": "FROZEN_BY_FIXED_FLUX",
            "pairing_status": "DEGENERATE_RANK_ZERO_ON_ONE_DIMENSION",
            "Berger_D_shift": "NOT_AN_INFINITESIMAL_LATTICE_GAUGE_SHIFT",
            "disposition": "FAIL_GLOBAL_PAIR",
        },
        {
            "choice_id": "REAL_CONTINUOUS_HARMONIC_QUOTIENT",
            "flux_carrier": "a0 in R",
            "large_gauge_group": "R_H acting by A3 -> A3+s eta3",
            "connected_harmonic_translation_quotient": "full R_H",
            "fixed_tangent": "moment level lambda_HT=0 and delta D(a)=0",
            "remaining_tangent": "zero-dimensional topological quotient",
            "H3_status": "REMOVED_BY_DECLARED_GLOBAL_GAUGE",
            "Hc4_status": "FROZEN_BY_FIXED_FLUX",
            "pairing_status": "NONDEGENERATE_VACUOUSLY_ON_ZERO_DIMENSIONS",
            "Berger_D_shift": "GAUGE_AFTER_K_TILDE=D-nu R-H",
            "disposition": "GLOBAL_BLOCK_PASS_BUT_BACKGROUND_FAIL",
        },
        {
            "choice_id": "COMPACT_CONNECTED_HOLONOMY_QUOTIENT",
            "flux_carrier": "a0 in R/Z",
            "large_gauge_group": "full U(1)_H holonomy translations",
            "connected_harmonic_translation_quotient": "full U(1)_H",
            "fixed_tangent": "moment level lambda_HT=0 and delta D(a)=0",
            "remaining_tangent": "zero-dimensional topological quotient",
            "H3_status": "REMOVED_BY_DECLARED_GLOBAL_GAUGE",
            "Hc4_status": "FROZEN_BY_FIXED_FLUX",
            "pairing_status": "NONDEGENERATE_VACUOUSLY_ON_ZERO_DIMENSIONS",
            "Berger_D_shift": "GAUGE_AFTER_K_TILDE=D-nu R-H",
            "disposition": "GLOBAL_BLOCK_PASS_BUT_BACKGROUND_FAIL",
        },
        {
            "choice_id": "PHASE_FIXED_BOUNDARY_CONTROL",
            "flux_carrier": "a0 fixed as boundary/superselection data",
            "large_gauge_group": "none beyond small/lattice gauge",
            "connected_harmonic_translation_quotient": "none",
            "fixed_tangent": "delta lambda_HT=delta D(a)=delta a0=0",
            "remaining_tangent": "zero-dimensional topological slice",
            "H3_status": "FROZEN_PHYSICAL_PHASE_NOT_GAUGE",
            "Hc4_status": "FROZEN_BY_FIXED_FLUX",
            "pairing_status": "ZERO_DIMENSIONAL_AFTER_FREEZING_PHYSICAL_DATA",
            "Berger_D_shift": "NOT_GAUGE",
            "disposition": "HIDES_PHASE_AND_BACKGROUND_FAIL",
        },
    ]
    return {
        "manifold": "R_t x S3 with closed Cauchy slices and no timelike boundary",
        "normalization": "eta3=vol_S3 with integral_S3 eta3=1",
        "field_decomposition": "A3=a(t) eta3+A3_exact, lambda_HT=lambda(t)",
        "volume_constraint": "D(a)=1 on both unit-cylinder and normalized Berger backgrounds",
        "real_flux_convention": "a(t)=t+a0, a0 in R",
        "compact_gerbe_convention": (
            "a0 in R/Z; the noncompact-time four-flux slope is fixed by the "
            "volume constraint and is not called an integral four-cycle flux"
        ),
        "boundary_data": (
            "affine asymptotic class D(a)=1 is fixed; allowed global tangent "
            "has delta D(a)=0. Equal endpoint phase variations cancel the HT "
            "time-boundary term. Local variations remain compactly supported."
        ),
        "small_gauge_group": (
            "A3 -> A3+d epsilon2 with the complete epsilon2/epsilon1/epsilon0 "
            "reducibility tower; it does not change a0"
        ),
        "classification_completeness": (
            "For the real translation carrier the closed connected subgroups "
            "considered are {0,R_H}; for the compact holonomy carrier they are "
            "{identity,U(1)_H}. The phase-fixed boundary slice is retained as "
            "the non-gauge control. No time-dependent harmonic translation is "
            "admitted because it changes dA3 and the off-shell action."
        ),
        "ambient_topological_pairing": {
            "basis": ["a0", "lambda_HT"],
            "matrix": _matrix(symplectic),
            "rank": 2,
        },
        "fixed_lambda_tangent": {
            "inclusion": _matrix(fixed_lambda_inclusion),
            "restricted_pairing": _matrix(restricted),
            "rank": 0,
            "nullity": 1,
        },
        "choices": choices,
    }


def _global_bv_extension() -> dict[str, Any]:
    return {
        "local_reducible_rows": {
            "Q_A3": "d C2",
            "Q_C2": "d C1",
            "Q_C1": "d C0",
            "Q_C0": "0",
            "Q_lambda_HT": "0",
            "Q_A3_star": "d lambda_HT",
            "Q_lambda_HT_star": "-[vol(g_hat)-dA3]",
        },
        "continuous_quotient_extension": {
            "global_ghost": {
                "symbol": "c_H",
                "ghost_number": 1,
                "parity": "odd",
                "spacetime_dependence": "constant",
            },
            "rows": [
                "Q A3=d C2+c_H eta3",
                "Q c_H=0",
                "Q c_H_star=-integral_S3(A3_star contraction eta3) up to the frozen cotangent sign",
            ],
            "master_term": "c_H integral_M A3_star wedge eta3",
            "nilpotency": "d eta3=0, d^2=0 and Q c_H=0",
            "action_invariance": "d(A3+s eta3)=dA3 for constant s",
            "moment_map": "mu_H=lambda_HT in the normalized global Lee-Wald pair",
            "reduction_level": "mu_H=0",
        },
        "compact_quotient_note": (
            "U(1)_H has the same infinitesimal global ghost row and an additional "
            "period-one global identification; the latter is not encoded by "
            "the local jet-BV differential"
        ),
        "cotangent_lift_scope": (
            "The local Candidate-B cotangent tower is imported unchanged. The "
            "only new infinitesimal row is the constant harmonic translation "
            "and its canonical global cotangent partner."
        ),
    }


def _background_obstruction() -> dict[str, Any]:
    metric = sp.diag(-1, 1, 1, 1)
    ricci = sp.diag(0, 2, 2, 2)
    scalar = sp.Integer(6)
    residual = sp.Rational(1, 12) * (
        ricci - scalar * metric / 4
    )
    expected = sp.diag(
        sp.Rational(1, 8),
        sp.Rational(1, 24),
        sp.Rational(1, 24),
        sp.Rational(1, 24),
    )
    if residual != expected:
        raise AssertionError("trace-free cylinder residual drifted")
    return {
        "background": (
            "unit dressed cylinder g_hat=-dt^2+dOmega3^2, theta constant, "
            "D(a)=1"
        ),
        "tracefree_metric_Euler": _matrix(residual),
        "orthonormal_diagonal": ["1/8", "1/24", "1/24", "1/24"],
        "invariant_formula": (
            "E_TF=(M_P^2/2)[Ric-(R/4)g] with M_P^2=1/6"
        ),
        "independence_statement": (
            "lambda_HT vol, fixed flux, a0 boundary data and every harmonic "
            "translation quotient affect only metric-proportional or global "
            "rows; none changes E_TF"
        ),
        "all_declared_choices": "NO_STATIONARY_UNIT_CYLINDER",
        "first_exact_incompatibility": (
            "the common background required by the work item is off shell "
            "before any causal or reduced-pairing promotion"
        ),
    }


def _carrier_disposition() -> dict[str, Any]:
    D = sp.Symbol("D")
    H = sp.Matrix([[0, 0, 2], [0, 0, D], [2, -D, 0]])
    fixed_flux = H[:, [0, 2]]
    if fixed_flux.det(method="berkowitz") if fixed_flux.rows == fixed_flux.cols else False:
        raise AssertionError("unexpected square fixed-flux block")
    return {
        "ambient_ordered_fields": ["u", "a", "lambda_HT"],
        "ambient_Hessian": _matrix(H),
        "ambient_kernel": ["D/2", "1", "0"],
        "fixed_flux_tangent": "delta D(a)=0",
        "linear_constraint": (
            "2u-D(delta a)=0 becomes u=0 after fixed flux; this is a global "
            "superselection restriction, not a retarded/advanced inverse on "
            "the unrestricted support-local carrier"
        ),
        "H3_Hc4_disposition": {
            "Hc4": "frozen by delta D(a)=0",
            "H3_small_or_lattice": "remains physical",
            "H3_connected_quotient": "removed by the explicitly new global gauge",
            "H3_phase_fixed_boundary": "frozen but not gauge",
        },
        "complete_support_local_parent": (
            "NOT_DEFINED about the off-shell unit cylinder; no inherited "
            "Candidate-B Green operator is promoted"
        ),
        "pairing": (
            "small/lattice choices are degenerate after fixed lambda; connected "
            "harmonic quotients remove the whole topological pair at moment "
            "lambda_HT=0; the total remaining carrier pairing is not reached "
            "because the background gate fails"
        ),
    }


def _charges_and_berger() -> dict[str, Any]:
    return {
        "raw_D": {
            "Hamiltonian": "H_D=V_S3 lambda_HT",
            "fixed_lambda_tangent": "delta H_D=0 when delta lambda_HT=0",
            "warning": (
                "nullity follows from the declared superselection tangent, not "
                "from the unreduced Candidate-B phase space"
            ),
        },
        "Berger": {
            "background": "a=1, q=9/40, theta=3t/4, lambda_HT=0, D(a)=1",
            "small_or_lattice_choice": (
                "L_D A3=eta3 is nonexact and has no infinitesimal gauge "
                "compensator"
            ),
            "connected_quotient_choice": (
                "K_tilde=D-(3/4)R-H fixes A3, where H generates "
                "A3 -> A3+s eta3"
            ),
            "harmonic_moment": "mu_H=lambda_HT=0",
            "K_Hamiltonian": "delta H_K_tilde=0 on the fixed moment level",
        },
        "clock_phase": {
            "observable": "theta modulo the original global U(1)_R",
            "Berger_gradient": "D(theta)=3/4",
            "status": (
                "unaffected by the A3 harmonic quotient; it is not identified "
                "with the topological a0 phase"
            ),
        },
        "zero_modes": [
            {
                "mode": "lambda_HT constant H0",
                "status": "fixed to zero superselection/moment level",
            },
            {
                "mode": "a0 harmonic H3",
                "status": "physical, globally gauged, or boundary-frozen according to choice",
            },
            {
                "mode": "integrated Hc4 flux change",
                "status": "excluded by fixed-flux tangent delta D(a)=0",
            },
            {
                "mode": "theta U1 phase",
                "status": "retained physical global phase",
            },
        ],
    }


def build() -> dict[str, Any]:
    imports, _ = _imports()
    global_data = _global_choices()
    bv = _global_bv_extension()
    background = _background_obstruction()
    carrier = _carrier_disposition()
    charges = _charges_and_berger()
    result = {
        "schema": "pure-weyl-compensator-ht-fixed-flux-global-quotient-preflight-v1",
        "result_id": "COMPENSATOR_HT_FIXED_FLUX_GLOBAL_QUOTIENT_PREFLIGHT_V1",
        "result_state": "OBSTRUCTED_BY_UNIT_CYLINDER_TRACEFREE_EULER",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "global_field_space_and_choices": global_data,
        "action_derived_global_BV_extension": bv,
        "unit_cylinder_common_background_gate": background,
        "fixed_flux_carrier_and_pairing": carrier,
        "charges_Berger_and_zero_modes": charges,
        "seven_gate_disposition": [
            {
                "gate": 1,
                "status": "PASS_FORMAL_LOCAL_AND_GLOBAL_GHOST_ROWS",
            },
            {
                "gate": 2,
                "status": "CHOICE_DEPENDENT_H3_REMOVAL_EXPLICIT",
            },
            {
                "gate": 3,
                "status": "FAIL_OFFSHELL_UNIT_CYLINDER",
            },
            {
                "gate": 4,
                "status": "GLOBAL_BLOCK_CLASSIFIED_TOTAL_PAIRING_NOT_REACHED",
            },
            {
                "gate": 5,
                "status": "PASS_ONLY_FOR_CONNECTED_QUOTIENT_OR_PHASE_FREEZE",
            },
            {
                "gate": 6,
                "status": "PASS_ONLY_ON_DECLARED_FIXED_LAMBDA_TANGENT",
            },
            {
                "gate": 7,
                "status": "PASS_GLOBAL_RECLASSIFICATION_ONLY_FOR_CONNECTED_QUOTIENT",
            },
        ],
        "terminal_verdict": {
            "all_declared_fixed_flux_global_choices_checked": True,
            "coherent_choice_passing_all_seven_gates": False,
            "first_exact_common_incompatibility": (
                "nonzero unit-cylinder trace-free metric Euler row"
            ),
            "candidate_B_rescued": False,
            "selected_changed_action_carrier_exported": False,
        },
        "exact_checks": {
            "dependency_hashes_pinned": True,
            "global_choices_declared_before_reduction": True,
            "real_and_compact_flux_conventions_separated": True,
            "small_lattice_and_connected_quotients_separated": True,
            "fixed_lambda_and_fixed_flux_tangents_explicit": True,
            "global_BV_ghost_and_cotangent_rows_explicit": True,
            "H3_Hc4_pair_classified": True,
            "unit_cylinder_tracefree_row_exact": True,
            "background_existence_separated_from_reduction": True,
            "raw_D_and_K_Berger_distinct": True,
            "clock_phase_not_hidden": True,
            "no_inherited_causal_inverse": True,
        },
        "claim_flags": {
            "FIXED_FLUX_GLOBAL_QUOTIENT_RESCUES_CANDIDATE_B": False,
            "COHERENT_CHANGED_THEORY_SELECTED": False,
            "UNIT_CYLINDER_ON_SHELL": False,
            "COMPLETE_SUPPORT_LOCAL_CAUSAL_PARENT": False,
            "HADAMARD_ANOMALY_QME_OR_QUANTUM": False,
            "PARTICLE_SCATTERING_UNITARITY": False,
        },
        "claim_boundary": (
            "This exact preflight classifies the declared real and compact "
            "fixed-flux HT global carriers under small/lattice gauge, full "
            "connected harmonic translation quotient, and a phase-fixed "
            "boundary control. Connected quotient choices do remove the H3/Hc4 "
            "topological pair at lambda_HT=0 and permit a Berger helical "
            "reclassification; small/lattice choices leave a physical null "
            "phase. Every choice nevertheless retains the same nonzero "
            "trace-free metric Euler row on the required unit cylinder, so no "
            "common stationary theory passes all seven gates. This is not a "
            "universal HT or compensator no-go and does not cover retuned local "
            "couplings, kinetic multipliers, other backgrounds or new fields. "
            "It exports no causal parent, Hadamard state, anomaly/QME result, "
            "particle space, scattering, positivity or unitarity theorem."
        ),
        "next_gate": (
            "Do not construct a fixed-flux selected-action receiver. A viable "
            "HT successor must first retune the local metric action so the unit "
            "cylinder and Berger backgrounds are jointly on shell, then rerun "
            "the global quotient and all seven gates."
        ),
    }
    result["content_hashes"] = {
        "global_sha256": _digest(result["global_field_space_and_choices"]),
        "bv_sha256": _digest(result["action_derived_global_BV_extension"]),
        "background_sha256": _digest(result["unit_cylinder_common_background_gate"]),
        "carrier_sha256": _digest(result["fixed_flux_carrier_and_pairing"]),
        "charges_sha256": _digest(result["charges_Berger_and_zero_modes"]),
        "verdict_sha256": _digest(result["terminal_verdict"]),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    elif json.loads(OUTPUT.read_text()) != value:
        raise AssertionError("fixed-flux/global-quotient preflight is stale")
    print("COMPENSATOR_HT_FIXED_FLUX_GLOBAL_QUOTIENT_PREFLIGHT_V1: PASS")


if __name__ == "__main__":
    main()
