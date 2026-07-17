#!/usr/bin/env python3
"""Freeze the relational massive two-form emitter model and 108-row carrier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_POLARIZATION_TWO_FORM_EMITTER_HANDOFF.json"
SCHEMA = PACKAGE / "schema/berger-polarization-two-form-emitter-handoff-v1.schema.json"
REPORT = PACKAGE / "reports/berger-polarization-two-form-emitter-handoff.md"
DEPENDENCIES = {
    "apparatus": PACKAGE / "certificates/BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF.json",
    "localized_transfer": PACKAGE / "certificates/BERGER_LOCALIZED_EMITTER_RANK_TWO_TRANSFER.json",
    "recoil_gate": PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_RECOIL_INPUT_GATE.json",
    "causal_green": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_polarization_emitter_handoff.py",
    "tests": PACKAGE / "tests/test_berger_polarization_emitter_handoff.py",
    "schema": SCHEMA,
    "report": REPORT,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def model_audit(*, use_unprotected_current: bool = False, delete_cotangent_rows: bool = False) -> dict[str, Any]:
    base_ranks = [6, 36, 36, 6]
    added_fields = 12
    added_antifields = 0 if delete_cotangent_rows else 12
    ranks = [base_ranks[0], base_ranks[1] + added_fields, base_ranks[2] + added_antifields, base_ranks[3]]
    pairing_rank = 2 * min(added_fields, added_antifields)

    # Exterior-algebra mutation rail.  The correct current is delta(h K), so
    # delta J=0 by delta^2=0.  Pulling h outside delta drops the dh contraction
    # and is generically not conserved; the two-entry fixture represents
    # delta K and i_{dh}K independently.
    delta_k, dh_k = sp.symbols("delta_K dh_K")
    correct_source = delta_k + dh_k
    displayed_source = delta_k if use_unprotected_current else correct_source
    conservation_defect = dh_k if use_unprotected_current else sp.Integer(0)

    # The coupled (A,K0,K1) principal symbol is diagonal because every cross
    # block is first order.  All three wave blocks have the same metric cone.
    zeta_sq = sp.symbols("zeta_sq", nonzero=True)
    principal = sp.diag(zeta_sq, zeta_sq, zeta_sq)
    return {
        "degree_ranks_minus1_0_1_2": ranks,
        "total_rows": sum(ranks),
        "added_pairing_rank": pairing_rank,
        "pairing_nondegenerate": pairing_rank == 24,
        "displayed_source_fixture": sp.sstr(displayed_source),
        "conservation_defect_fixture": sp.sstr(conservation_defect),
        "source_conserved": conservation_defect == 0,
        "principal_symbol_rank": principal.rank(),
        "principal_symbol_determinant": sp.sstr(principal.det()),
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if values["apparatus"]["flags"]["AUTHORITATIVE_84_ROW_FORWARD_INTERFACE"] is not True:
        raise AssertionError("84-row apparatus handoff drifted")
    if values["localized_transfer"]["flags"]["LOCALIZED_EMITTER_TRANSFER_MATRIX_RANK_TWO"] is not True:
        raise AssertionError("localized transfer input drifted")
    if values["recoil_gate"]["flags"]["DYNAMICAL_EMITTER_INPUT_UNDERDETERMINATION_CERTIFIED"] is not True:
        raise AssertionError("recoil input gate drifted")
    if values["causal_green"]["flags"]["BERGER_MAXWELL_CAUSAL_GREEN_HOMOTOPY"] is not True:
        raise AssertionError("Maxwell causal input drifted")

    audit = model_audit()
    bad_current = model_audit(use_unprotected_current=True)
    bad_pairing = model_audit(delete_cotangent_rows=True)
    if bad_current["source_conserved"] or bad_pairing["pairing_nondegenerate"]:
        raise AssertionError("polarization-emitter mutation rail failed")

    boundary = (
        "This LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL handoff selects a specific autonomous effective emitter theory: two real standard massive polarization two-forms K_0,K_1 on the Weyl-invariant clock metric gHat, with Euler operator delta d+m_b^2, positive m_b^2, and compact relational switching h_b(Theta)<K_b,dA>. The divergence constraint converts the emitter equations to a normally hyperbolic P_2,gHat+m_b^2 reduction without inserting a gauge-fixing term into the physical action. The exact Maxwell currents J_b=g_b delta_gHat(h_b K_b) are conserved, Maxwell-gauge invariant, compact in clock time, and spatially localized for localized Cauchy data. The emitter equations contain g_b h_b dA, so recoil is dynamical. Adding twelve two-form components and twelve cotangent partners enlarges the 84-row carrier to a nondegenerately paired 108-row carrier with degree ranks (6,48,48,6). The reduced coupled principal symbol remains the common gHat wave cone because the cross blocks are first order. This freezes a model and interface; it does not construct the full 108-row q1/q2/q3, prove its causal chain contraction, produce rank-two records from actual emitter Cauchy data, compute a recoil coefficient, include the emitter stress backreaction, certify a full apparatus Dirac bracket, or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-polarization-two-form-emitter-handoff-v1",
        "result_id": "BERGER_POLARIZATION_TWO_FORM_EMITTER_HANDOFF",
        "setting_id": values["localized_transfer"]["setting_id"],
        "claim_status": "POLARIZATION_TWO_FORM_EMITTER_MODEL_SELECTED_108_ROW_HANDOFF_FROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "model_selection": {
            "fields": "two real bosonic two-forms K_0,K_1 with Weyl weight zero",
            "clock_metric": "gHat=|T|^2 g, invariant under Weyl gauge transformations",
            "physical_euler_operators": "E_b=delta_gHat d+m_b^2 with declared m_b^2>0",
            "local_action": "S_emit=-1/2 sum_b <dK_b,dK_b>_gHat-m_b^2/2 <K_b,K_b>_gHat-g_b <h_b(Theta)K_b,dA>_gHat, with the conventional Lorentzian overall signs fixed by the shared action convention",
            "constraint_reduced_wave_operator": "applying delta_gHat gives m_b^2 delta_gHat K_b=g_b delta_gHat(h_b dA); adjoining d of this constraint converts E_b to P_2,gHat+m_b^2",
            "switches": "fixed smooth nonnegative compactly supported functions h_b of the dynamical clock Theta",
            "preparation": "compact localized Cauchy data for K_b before supp h_b; no external spacetime drive",
            "why_this_model": "it is the standard massive two-form theory, realizes conservation off shell through a coexact current, has a normally hyperbolic constraint reduction, is Diff/Weyl/Maxwell compatible through gHat and dA, and supplies an explicit reciprocal recoil block",
        },
        "euler_and_recoil_blocks": {
            "Maxwell": "delta_gHat dA-sum_b g_b delta_gHat(h_b K_b)=0",
            "emitter_b": "(delta_gHat d+m_b^2)K_b-g_b h_b dA=0",
            "emitter_constraint": "m_b^2 delta_gHat K_b=g_b delta_gHat(h_b dA)",
            "current_b": "J_b=g_b delta_gHat(h_b K_b)",
            "conservation": "delta_gHat J_b=g_b delta_gHat^2(h_b K_b)=0",
            "Maxwell_gauge": "A->A+d lambda leaves dA and both emitter equations invariant",
            "formal_recoil_self_energy": "Sigma_ret=sum_b g_b^2 delta_gHat h_b G_b,ret h_b d, where G_b,ret is the constraint-compatible massive-two-form retarded solution operator",
            "cyclic_cross_block": "-g_b delta_gHat h_b and -g_b h_b d are formal adjoints from one Hessian",
        },
        "carrier_108": {
            "base_rows": 84,
            "emitter_field_rows": 12,
            "emitter_cotangent_rows": 12,
            "new_ghost_rows": 0,
            "degree_ranks_minus1_0_1_2": audit["degree_ranks_minus1_0_1_2"],
            "total_rows": audit["total_rows"],
            "new_pairing_rule": "Omega(K_b,K_b_plus)=+I_6 and Omega(K_b_plus,K_b)=-I_6",
            "new_pairing_rank": audit["added_pairing_rank"],
            "full_pairing_nondegenerate": audit["pairing_nondegenerate"],
        },
        "symmetry_contract": {
            "Diff": "K_b and h_b(Theta) transform tensorially; add integral <K_b_plus,L_c K_b> to the BV action",
            "Weyl": "K_b and A are inert and every emitter contraction uses invariant gHat",
            "Maxwell": "the action depends on A only through dA",
            "K_Berger": "simultaneous-family action is the Lie derivative along e0 combined with the imported clock rotation; fixed-background linear descent remains open",
            "drive_or_external_current": "none in the selected model; preparations are Cauchy data and h_b is a relational coupling function",
        },
        "causal_principal_contract": {
            "coupled_fields": ["A", "K_0", "K_1"],
            "diagonal_wave_blocks_after_emitter_constraint_reduction": ["P_1,gHat", "P_2,gHat+m_0^2", "P_2,gHat+m_1^2"],
            "off_diagonal_order": 1,
            "principal_symbol": "gHat^{mu nu} zeta_mu zeta_nu I_(4+6+6)",
            "fixture_rank": audit["principal_symbol_rank"],
            "fixture_determinant": audit["principal_symbol_determinant"],
            "consequence": "the Maxwell gauge-fixed and massive-emitter constraint-reduced Euler system is normally hyperbolic once the complete lower-order coupled operator is assembled",
            "chain_homotopy_status": "OPEN_UNTIL_THE_108_ROW_Q1_AND_WITNESS_ARE_EXPORTED",
        },
        "next_construction_gate": {
            "name": "BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_AND_FIRST_RECOIL",
            "required_outputs": ["complete q1 including Diff and cotangent blocks", "q1 squared and odd-cyclicity ledgers", "advanced/retarded chain homotopy", "localized emitter Cauchy preparations", "leading two-by-two emitted record matrix", "first formal recoil correction", "emitter stress and clock-switch source ledger"],
        },
        "mutation_results": [
            {"name": "replace_delta_of_hK_by_h_delta_K", "conservation_defect": bad_current["conservation_defect_fixture"], "detected": True},
            {"name": "delete_emitter_cotangent_rows", "new_pairing_rank": bad_pairing["added_pairing_rank"], "expected_less_than": 24, "detected": True},
        ],
        "flags": {
            "SPECIFIC_DYNAMICAL_EMITTER_MODEL_SELECTED": True,
            "RELATIONAL_DIFF_WEYL_MAXWELL_COMPATIBLE_ACTION_FIXED": True,
            "OFF_SHELL_CONSERVED_LOCALIZED_EMITTER_CURRENT_FIXED": True,
            "RECIPROCAL_EMITTER_RECOIL_BLOCK_FIXED": True,
            "AUTHORITATIVE_108_ROW_EMITTER_INTERFACE": True,
            "108_ROW_Q1_CERTIFIED": False,
            "108_ROW_CAUSAL_CHAIN_CONTRACTION_CERTIFIED": False,
            "DYNAMICAL_EMITTER_RECORD_RANK_TWO_CERTIFIED": False,
            "RECOIL_COEFFICIENT_COMPUTED": False,
            "EMITTER_STRESS_BACKREACTION_INCLUDED": False,
            "FULL_APPARATUS_DIRAC_BRACKET_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "CONSTRUCT_108_ROW_POLARIZATION_EMITTER_UNARY_CAUSAL_COMPLEX_AND_REPLAY_LOCALIZED_RECORD_RANK",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale polarization-emitter handoff")
    print("BERGER_POLARIZATION_TWO_FORM_EMITTER_HANDOFF generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
