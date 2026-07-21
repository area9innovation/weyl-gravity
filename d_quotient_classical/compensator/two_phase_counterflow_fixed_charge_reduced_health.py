#!/usr/bin/env python3
"""Exact first obstruction for the fixed-relative-charge counterflow reduction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_PAYLOAD_V1.json"
IMPORTS = {
    "causal_parent": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1.json", "7d969e7e630f793dfe12fe07b0e98a67b2543f9aa85fa03277e491fb00296db7", "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1", "951e88307abbea0996513773a33e66b37555272b"),
    "causal_parent_payload": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1.json", "7c73705cc07062baf652c9cc0cb0977beda2a96d5b642fa186d6bfaeae01db57", "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1", "951e88307abbea0996513773a33e66b37555272b"),
    "receiver_contract": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_RECEIVER_CONTRACT_V1.json", "d5efdfed97286aa9554e88a449e87941c3c589940845dbfe70209b513c59e3f7", "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_RECEIVER_CONTRACT_V1", "951e88307abbea0996513773a33e66b37555272b"),
    "positive_54_parent": ("d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json", "6e3baf6ecfab2c2854ccfbfb5c69122fe0bbe621ddcf8ab2a5651e3decf113e0", "BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION", "445e26663d06764bc858ff0a004ba6178acce75f"),
    "positive_54_green": ("d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json", "e92642b3225ab87b6058987f73f9ade3909646f2d0d3b95cc45cc9c5712b9c3b", "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2", "743183594a7a33dbb869154dafd7eb2c3482bac0"),
    "trace_charge_preflight": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_V1.json", "2b578967ece7a2e6a8079c8fd84665ac40cf2b7e0aeef41d96882553c35115ea", "TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_V1", "d6d54a6efaa30ffe48dd7b9718c1954fa4ea514b"),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _matrix(value: sp.Matrix) -> list[list[str]]:
    return [[str(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]


def _imports() -> tuple[dict[str, Any], dict[str, Any]]:
    records: dict[str, Any] = {}
    values: dict[str, Any] = {}
    for role, (relative, expected, result_id, commit) in IMPORTS.items():
        path = ROOT / relative
        actual = _sha(path)
        value = json.loads(path.read_text())
        if actual != expected or value.get("result_id") != result_id:
            raise AssertionError(f"{role} import drifted")
        records[role] = {"path": relative, "sha256": actual, "result_id": result_id, "source_commit": commit, "oracle_fields_consumed": []}
        values[role] = value
    if values["causal_parent"]["complete_parent"]["complete_component_rank"] != 70:
        raise AssertionError("70-component parent drifted")
    if values["positive_54_parent"]["contraction"]["identity"] != "pi_cl iota_cl=1_26 and ell_1 S_cl+S_cl ell_1=1_54-iota_cl pi_cl":
        raise AssertionError("54-to-26 contraction drifted")
    if values["positive_54_green"]["exact_checks"]["zero_modes_retained"] is not True:
        raise AssertionError("global zero-mode policy drifted")
    return records, values


def _derived_charge_fibre() -> dict[str, Any]:
    # Basis (r, psi_0, delta_Q_rel, epsilon) in degrees (-1,0,0,1).
    differential = sp.zeros(4)
    differential[1, 0] = 1
    differential[3, 2] = 1
    homotopy = sp.zeros(4)
    homotopy[0, 1] = 1
    homotopy[2, 3] = 1
    if differential * differential != sp.zeros(4):
        raise AssertionError("derived fibre is not a complex")
    if differential * homotopy + homotopy * differential != sp.eye(4):
        raise AssertionError("derived charge fibre is not exact")

    omega = sp.Matrix([[0, 0, 0, 1], [0, 0, 1, 0], [0, -1, 0, 0], [-1, 0, 0, 0]])
    if omega.det() != 1:
        raise AssertionError("shifted charge pairing became degenerate")
    level_pullback = sp.Matrix([[0]])
    return {
        "construction": "derived level set/homotopy fibre of Q_rel at its selected nonzero value, followed by the R_rel quotient",
        "basis": ["r_R_rel", "delta_psi_0", "delta_Q_rel", "epsilon_Q_rel"],
        "degrees": [-1, 0, 0, 1],
        "differential": _matrix(differential),
        "contracting_homotopy": _matrix(homotopy),
        "d_squared_zero": True,
        "dS_plus_Sd_identity": True,
        "degree_ranks": [1, 2, 1],
        "cohomology_dimensions": [0, 0, 0],
        "unreduced_phase_space": {
            "basis": ["delta_psi_0", "delta_Q_rel"],
            "symplectic_matrix": [["0", "1"], ["-1", "0"]],
            "inertia": "one canonical positive-clock Darboux pair before fixing charge",
        },
        "level_tangent": {
            "equation": "delta_Q_rel=0",
            "basis": ["delta_psi_0"],
            "pullback_symplectic_matrix": _matrix(level_pullback),
            "radical_basis": ["delta_psi_0=L_R_rel background"],
        },
        "quotient": {
            "formula": "ker(d Q_rel)/im(L_R_rel)=span(delta_psi_0)/span(delta_psi_0)=0",
            "relative_clock_dimension": 0,
            "pairing_rank": 0,
            "inertia": [0, 0, 0],
            "positive_relative_clock_survives": False,
        },
        "shifted_pairing_matrix": _matrix(omega),
        "shifted_pairing_rank": 4,
        "zero_mode_retained_until_map_explicit": True,
    }


def _sector_ledger(values: dict[str, Any]) -> dict[str, Any]:
    preflight = values["trace_charge_preflight"]
    selected = preflight["selected_fixture"]
    return {
        "diagonal_U1_16": {"status": "EXACT_CONTRACTIBLE", "cohomology_dimension": 0, "basis": ["chi,c_U1,A_star,B,c_U1_star,H,bar_c,b,b_star,bar_c_star"]},
        "clock_nonminimal_gaugefixing_28": {"status": "EXACT_CONTRACTIBLE_BY_IMPORTED_54_TO_26_SDR", "retained_rows": 26, "removed_rows": 28},
        "relative_global_zero_mode": {"status": "EXACT_AFTER_DERIVED_FIXED_CHARGE_REDUCTION", "cohomology_dimension": 0},
        "diffeomorphism_and_Weyl": {"status": "IMPORTED_EXACT_CONTRACTION", "relative_phase_row": "Theta pairs with the temporal diffeomorphism ghost tau", "radial_scale_row": "R pairs with the Weyl ghost sigma"},
        "dressed_trace": {
            "representative": "u=(h_hat_11+h_hat_22+h_hat_33)/3 on the homogeneous fixed-squashing scalar line",
            "status": "SURVIVES_IN_RETAINED_DRESSED_METRIC_CARRIER",
            "reduced_L2": selected["reduced_L2"],
            "velocity_hessian": selected["velocity_Hessian"],
            "characteristic_roots": selected["characteristic_roots"],
            "Hamiltonian_positive": selected["Hamiltonian_positive"],
        },
        "retained_metric_26": {"status": "CAUSAL_UNARY_CERTIFIED", "complete_physical_cohomology_and_all_Hodge_sign_census": "NOT_REACHED_AFTER_FIRST_EXACT_PASS_FAILURE"},
        "Hodge_policy": {"homogeneous_scalar_constant": "explicitly retained through the derived fibre", "exact": "retained in imported 70-row parent until its certified contractions", "coexact": "retained in imported 70-row parent until its certified contractions", "harmonic_one_forms": "absent because H1(S3)=0", "exceptional_zero_modes": "not deleted by an elliptic projector"},
    }


def _charge_ledger() -> dict[str, Any]:
    return {
        "unrestricted_parent": {
            "Q_diag": "zero by local Gauss; diagonal U1 is gauge",
            "Q_rel": "nonzero conserved global charge",
            "D": "charged, H_D=Omega*Q_rel; not gauge",
            "K": "D-Omega*R_rel; null Hamiltonian background stabilizer",
        },
        "fixed_Q_rel_fibre": {
            "Q_diag": "zero by Gauss",
            "Q_rel": "constant by definition; delta_Q_rel=0",
            "R_rel": "entire presymplectic radical and removed by quotient",
            "D": "null because i_D Omega=Omega_background*delta_Q_rel=0",
            "K": "null stabilizer independently",
            "D_equals_K_on_reduced_quotient": True,
            "D_identified_with_K_before_reduction": False,
        },
    }


def _payload(imports: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema": "pure-weyl-two-phase-counterflow-fixed-charge-reduced-health-obstruction-payload-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_PAYLOAD_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "oracle_fields_consumed": [],
        "derived_fixed_charge_fibre": _derived_charge_fibre(),
        "sector_ledger": _sector_ledger(values),
        "charge_ledger": _charge_ledger(),
        "first_failed_property": {
            "required": "one positive relative-clock direction survives the physical fixed-charge reduction",
            "actual": "relative-clock quotient dimension is zero",
            "status": "OBSTRUCTED",
            "later_gates": "NOT_REACHED_AFTER_FIRST_EXACT_FAILURE",
        },
        "content_sha256": "PENDING",
    }
    result["content_sha256"] = _digest({k: v for k, v in result.items() if k != "content_sha256"})
    return result


def _certificate(imports: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    verdict = {
        "result_state": "OBSTRUCTED_FIXED_CHARGE_REDUCTION_REMOVES_RELATIVE_CLOCK",
        "fixed_charge_D_null": True,
        "positive_relative_clock_survives": False,
        "physically_healthy_reduced_theory": False,
        "first_failed_property": "relative-clock quotient dimension zero",
    }
    boundary = {
        "establishes": ["exact derived fixed-Q_rel fibre with the charge zero mode retained until the maps are explicit", "zero physical relative-clock cohomology and zero descended phase pairing", "separate unrestricted and fixed-leaf Q_diag/Q_rel/D/K dispositions", "persistence of the imported positive homogeneous dressed-trace representative", "the first exact failure of the requested reduced-health PASS condition"],
        "does_not_establish": ["a negative-norm mode in the retained 26-row metric carrier", "a complete all-Hodge physical cohomology or characteristic census after the first failure", "identification of K with raw D before fixed-charge reduction", "Hadamard or quantum positivity", "nonlinear q2, observer, Einstein-source, QME or particle claims"],
    }
    return {
        "schema": "pure-weyl-two-phase-counterflow-fixed-charge-reduced-health-obstruction-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_V1",
        "result_state": verdict["result_state"],
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "sha256": "PENDING_WRITE", "content_sha256": payload["content_sha256"]},
        "terminal_verdict": verdict,
        "claim_boundary": boundary,
        "claim_flags": {"DERIVED_FIXED_CHARGE_FIBRE": True, "D_NULL_ON_FIXED_LEAF": True, "POSITIVE_RELATIVE_CLOCK_SURVIVES": False, "FULL_REDUCED_HEALTH_PASS": False, "ALL_HODGE_PHYSICAL_CENSUS": False, "HADAMARD_OR_QUANTUM": False},
        "content_hashes": {"fibre_sha256": _digest(payload["derived_fixed_charge_fibre"]), "sectors_sha256": _digest(payload["sector_ledger"]), "charges_sha256": _digest(payload["charge_ledger"]), "failure_sha256": _digest(payload["first_failed_property"]), "boundary_sha256": _digest(boundary)},
    }


def validate(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    if payload["content_sha256"] != _digest({k: v for k, v in payload.items() if k != "content_sha256"}):
        raise AssertionError("payload hash mismatch")
    fibre = payload["derived_fixed_charge_fibre"]
    if fibre["cohomology_dimensions"] != [0, 0, 0] or fibre["quotient"]["relative_clock_dimension"] != 0:
        raise AssertionError("fixed-charge obstruction was erased")
    if not payload["charge_ledger"]["fixed_Q_rel_fibre"]["D_equals_K_on_reduced_quotient"]:
        raise AssertionError("reduced D/K disposition drifted")
    if payload["charge_ledger"]["fixed_Q_rel_fibre"]["D_identified_with_K_before_reduction"]:
        raise AssertionError("raw D was identified with K")
    if certificate["claim_flags"]["POSITIVE_RELATIVE_CLOCK_SURVIVES"] or certificate["claim_flags"]["FULL_REDUCED_HEALTH_PASS"] or certificate["claim_flags"]["HADAMARD_OR_QUANTUM"]:
        raise AssertionError("claim boundary promoted")


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    imports, values = _imports()
    payload = _payload(imports, values)
    certificate = _certificate(imports, payload)
    validate(certificate, payload)
    return certificate, payload


def write() -> None:
    certificate, payload = build()
    PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD)
    validate(certificate, payload)
    OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")


def check() -> None:
    certificate, payload = build()
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD)
    if json.loads(PAYLOAD.read_text()) != payload or json.loads(OUTPUT.read_text()) != certificate:
        raise AssertionError("stored fixed-charge artifacts drifted")
    print("TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_V1: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else write()


if __name__ == "__main__":
    main()
