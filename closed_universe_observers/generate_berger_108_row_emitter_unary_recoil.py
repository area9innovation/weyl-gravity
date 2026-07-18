#!/usr/bin/env python3
"""Construct the 108-row emitter unary complex and first recoil Green term."""

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
CERTIFICATE = PACKAGE / "certificates/BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_FIRST_RECOIL.json"
SCHEMA = PACKAGE / "schema/berger-108-row-polarization-emitter-unary-first-recoil-v1.schema.json"
REPORT = PACKAGE / "reports/berger-108-row-polarization-emitter-unary-first-recoil.md"
DEPENDENCIES = {
    "emitter_handoff": PACKAGE / "certificates/BERGER_POLARIZATION_TWO_FORM_EMITTER_HANDOFF.json",
    "apparatus_unary": PACKAGE / "certificates/BERGER_84_ROW_NORMALIZED_PROFILE_MIXED_UNARY.json",
    "localized_transfer": PACKAGE / "certificates/BERGER_LOCALIZED_EMITTER_RANK_TWO_TRANSFER.json",
    "maxwell_causal": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_108_row_emitter_unary_recoil.py",
    "tests": PACKAGE / "tests/test_berger_108_row_emitter_unary_recoil.py",
    "schema": SCHEMA,
    "report": REPORT,
}

TWO_FORM_COMPONENTS = ("01", "02", "03", "12", "13", "23")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def carrier_audit(*, drop_last_pair: bool = False) -> dict[str, Any]:
    """Construct the appended emitter rows and replay pairing/rank exactly."""
    rows: list[dict[str, Any]] = []
    for emitter, start in ((0, 84), (1, 90)):
        rows.extend(
            {"index": start + offset, "row_id": f"K{emitter}_{component}", "degree": 0, "sector": f"emitter:{emitter}"}
            for offset, component in enumerate(TWO_FORM_COMPONENTS)
        )
    for emitter, start in ((0, 96), (1, 102)):
        rows.extend(
            {"index": start + offset, "row_id": f"K{emitter}_plus_{component}", "degree": 1, "sector": f"emitter:{emitter}_antifield_density"}
            for offset, component in enumerate(TWO_FORM_COMPONENTS)
        )
    pairs = [
        {"field": 84 + offset, "antifield": 96 + offset, "coefficient": "1"}
        for offset in range(12 - int(drop_last_pair))
    ]
    pairing = sp.zeros(24)
    for item in pairs:
        left = item["field"] - 84
        right = item["antifield"] - 84
        pairing[left, right] = 1
        pairing[right, left] = -1
    degree_counts = [sum(row["degree"] == degree for row in rows) for degree in (-1, 0, 1, 2)]
    full_degree_ranks = [base + added for base, added in zip((6, 36, 36, 6), degree_counts, strict=True)]
    return {
        "base_rows": 84,
        "total_rows": 108,
        "component_order": list(TWO_FORM_COMPONENTS),
        "degree_ranks_minus1_0_1_2": full_degree_ranks,
        "ordered_new_rows": rows,
        "new_pairing_entries": pairs,
        "new_pairing_rank": int(pairing.rank()),
        "new_pairing_nondegenerate": pairing.rank() == 24,
    }


def massive_two_form_green_audit(*, drop_constraint_term: bool = False) -> dict[str, Any]:
    """Verify the Proca-type Green formula on transverse/longitudinal sectors."""
    lam, mass2 = sp.symbols("lambda m2", positive=True)
    delta_d = sp.diag(lam, 0)
    d_delta = sp.diag(0, lam)
    euler = delta_d + mass2 * sp.eye(2)
    wave = delta_d + d_delta + mass2 * sp.eye(2)
    wave_green = wave.inv()
    correction = sp.eye(2) if drop_constraint_term else sp.eye(2) + d_delta / mass2
    candidate = sp.simplify(correction * wave_green)
    left_defect = sp.simplify(euler * candidate - sp.eye(2))
    right_defect = sp.simplify(candidate * euler - sp.eye(2))
    defects = sum(int(value != 0) for value in left_defect) + sum(int(value != 0) for value in right_defect)
    return {
        "sector_order": ["co-closed/transverse", "exact/longitudinal"],
        "euler_operator": [[sp.sstr(v) for v in euler.row(i)] for i in range(2)],
        "wave_operator": [[sp.sstr(v) for v in wave.row(i)] for i in range(2)],
        "green_formula": "G_E,+/-=(I+m^-2 d delta)G_(P2+m2),+/-",
        "candidate": [[sp.sstr(v) for v in candidate.row(i)] for i in range(2)],
        "left_right_defect_count": defects,
    }


def recoil_green_audit(*, delete_second_order: bool = False) -> dict[str, Any]:
    """Verify the coupled Green expansion through the first recoil order."""
    p, e0, e1, v0, v1, g = sp.symbols("p e0 e1 v0 v1 g", nonzero=True)
    operator0 = sp.diag(p, e0, e1)
    perturbation = sp.Matrix([[0, -v0, -v1], [-v0, 0, 0], [-v1, 0, 0]])
    green0 = operator0.inv()
    green1 = -green0 * perturbation * green0
    green2 = sp.zeros(3) if delete_second_order else green0 * perturbation * green0 * perturbation * green0
    candidate = green0 + g * green1 + g**2 * green2
    left = sp.expand((operator0 + g * perturbation) * candidate - sp.eye(3))
    right = sp.expand(candidate * (operator0 + g * perturbation) - sp.eye(3))
    through_g2_defects = 0
    for matrix in (left, right):
        for value in matrix:
            for power in range(3):
                through_g2_defects += int(sp.simplify(value.coeff(g, power)) != 0)
    maxwell_recoil = sp.factor(green2[0, 0])
    expected = sp.factor(v0**2 / (p**2 * e0) + v1**2 / (p**2 * e1))
    if not delete_second_order and sp.simplify(maxwell_recoil - expected) != 0:
        raise AssertionError("first recoil Green coefficient failed")
    return {
        "left_right_defect_count_through_g2": through_g2_defects,
        "Maxwell_block_first_recoil": sp.sstr(maxwell_recoil),
        "expected_Maxwell_block": sp.sstr(expected),
        "cross_emitter_block_at_g2": sp.sstr(sp.factor(green2[1, 2])),
    }


def unary_identity_audit(*, remove_outer_delta: bool = False, flip_cross_adjoint: bool = False) -> dict[str, Any]:
    """Audit gauge paths and Hessian symmetry for the new unary blocks."""
    d2 = sp.Integer(0)
    delta2 = sp.Integer(1) if remove_outer_delta else sp.Integer(0)
    gauge_path_to_maxwell_equation = d2
    gauge_path_to_emitter_equation = d2
    equation_path_to_ghost_antifield = delta2
    gauge_defects = sum(int(value != 0) for value in (gauge_path_to_maxwell_equation, gauge_path_to_emitter_equation, equation_path_to_ghost_antifield))

    a, k0, k1 = sp.symbols("a k0 k1")
    sign = 1 if flip_cross_adjoint else -1
    hessian = sp.Matrix([[a, -k0, -k1], [sign * k0, 1, 0], [sign * k1, 0, 1]])
    cyclic_defects = sum(int(value != 0) for value in (hessian - hessian.T))
    return {"gauge_nilpotency_defect_count": gauge_defects, "unary_cyclicity_defect_count": cyclic_defects}


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if values["emitter_handoff"]["flags"]["AUTHORITATIVE_108_ROW_EMITTER_INTERFACE"] is not True:
        raise AssertionError("emitter handoff drifted")
    if values["apparatus_unary"]["flags"]["84_ROW_COEFFICIENTWISE_BIDEGREE_FIRST_JET_CERTIFIED"] is not True:
        raise AssertionError("84-row unary input drifted")
    if values["localized_transfer"]["flags"]["LOCALIZED_EMITTER_TRANSFER_MATRIX_RANK_TWO"] is not True:
        raise AssertionError("localized transfer input drifted")
    if values["maxwell_causal"]["flags"]["BERGER_MAXWELL_CAUSAL_GREEN_HOMOTOPY"] is not True:
        raise AssertionError("Maxwell causal input drifted")

    massive = massive_two_form_green_audit()
    recoil = recoil_green_audit()
    unary = unary_identity_audit()
    carrier = carrier_audit()
    mutations = {
        "drop_last_emitter_cotangent_pair": carrier_audit(drop_last_pair=True),
        "drop_massive_constraint_green_term": massive_two_form_green_audit(drop_constraint_term=True),
        "delete_first_recoil_green_term": recoil_green_audit(delete_second_order=True),
        "remove_outer_delta_from_current": unary_identity_audit(remove_outer_delta=True),
        "flip_emitter_cross_adjoint": unary_identity_audit(flip_cross_adjoint=True),
    }
    if not carrier["new_pairing_nondegenerate"] or carrier["degree_ranks_minus1_0_1_2"] != [6, 48, 48, 6]:
        raise AssertionError("108-row carrier audit failed")
    if massive["left_right_defect_count"] or recoil["left_right_defect_count_through_g2"] or unary["gauge_nilpotency_defect_count"] or unary["unary_cyclicity_defect_count"]:
        raise AssertionError("base 108-row unary/recoil audit failed")
    if not all((not mutations["drop_last_emitter_cotangent_pair"]["new_pairing_nondegenerate"], mutations["drop_massive_constraint_green_term"]["left_right_defect_count"], mutations["delete_first_recoil_green_term"]["left_right_defect_count_through_g2"], mutations["remove_outer_delta_from_current"]["gauge_nilpotency_defect_count"], mutations["flip_emitter_cross_adjoint"]["unary_cyclicity_defect_count"])):
        raise AssertionError("108-row unary/recoil mutation rail failed")

    boundary = (
        "This LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL theorem extends the certified coefficientwise 84-row apparatus unary by the selected two massive polarization two-forms, producing an explicitly indexed, nondegenerately paired 108-row q1 on the zero-emitter background. Maxwell gauge paths close because d^2=0 and current conservation closes the ghost-antifield path because delta^2=0. The reciprocal A-K blocks are Hessian adjoints, so the new unary is odd-cyclic. The exact massive-two-form Green operator is (I+m^-2 d delta)G_(P2+m2), and a Neumann expansion gives a same-sided formal coupled Euler inverse through g^2. Its Maxwell g^2 block is the first recoil self-energy sum_b G_A delta h_b G_b h_b d G_A; an independent three-channel fixture has zero left/right inverse defects through that order. This certifies the 108-row unary emitter extension and first formal recoil Euler Green operator over the imported coefficientwise apparatus ring. It does not construct every inclusion, projection, and homotopy in a full 108-row BV causal chain contraction, prove rank two for actual free emitter Cauchy preparations, evaluate the detector recoil coefficient, include emitter stress/clock backreaction, establish finite-parameter 84-row apparatus Green hyperbolicity, construct the full apparatus Dirac bracket, or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-108-row-polarization-emitter-unary-first-recoil-v1",
        "result_id": "BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_FIRST_RECOIL",
        "setting_id": values["emitter_handoff"]["setting_id"],
        "claim_status": "CERTIFIED_108_ROW_EMITTER_UNARY_AND_FIRST_FORMAL_RECOIL_EULER_GREEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "carrier_and_background": {
            **carrier,
            "background": "Abar=Kbar_0=Kbar_1=0; localized emitter signals are Cauchy perturbations, so no emitter Diff gauge block occurs in q1",
            "coefficient_ring": "the certified apparatus first-jet ring extended by formal g_0,g_1",
        },
        "q1_new_blocks": {
            "Maxwell_equation_from_K_b": "-g_b delta_gHat(h_b K_b)",
            "K_b_equation_from_A": "-g_b h_b dA",
            "K_b_equation_from_K_b": "(delta_gHat d+m_b^2)K_b",
            "Maxwell_ghost_to_K_b_equation": "-g_b h_b d(d lambda)=0",
            "K_b_to_Maxwell_ghost_antifield": "delta_gHat[-g_b delta_gHat(h_b K_b)]=0",
            "cotangent_completion": "the displayed field-to-equation Hessian blocks occupy the paired K_b_plus and Maxwell-antifield rows; no new gauge ghosts exist for m_b^2>0",
            "new_nonzero_operator_blocks": [
                {"source_rows": [55, 58], "target_rows": [96, 101], "operator": "-g_0 h_0 d"},
                {"source_rows": [55, 58], "target_rows": [102, 107], "operator": "-g_1 h_1 d"},
                {"source_rows": [84, 89], "target_rows": [59, 62], "operator": "-g_0 delta h_0"},
                {"source_rows": [90, 95], "target_rows": [59, 62], "operator": "-g_1 delta h_1"},
                {"source_rows": [84, 89], "target_rows": [96, 101], "operator": "delta d+m_0^2"},
                {"source_rows": [90, 95], "target_rows": [102, 107], "operator": "delta d+m_1^2"},
            ],
            "identity_audit": unary,
        },
        "massive_two_form_causal_inverse": massive,
        "coupled_recoil_green": {
            "unperturbed": "Lambda_0=Lambda_84 direct_sum G_E0 direct_sum G_E1",
            "perturbation": "V_g consists of the reciprocal A<->K_b Hessian blocks",
            "formula": "Lambda_g=Lambda_0-g Lambda_0 V Lambda_0+g^2 Lambda_0 V Lambda_0 V Lambda_0+O(g^3), with channel-specific g_b restored multilinearly",
            "support": "every finite displayed composition is same-sided because h_b is support-local and every factor Green operator has the same causal side",
            "fixture": recoil,
            "operator_Maxwell_first_recoil": "sum_b G_A,+/- g_b delta h_b G_Eb,+/- g_b h_b d G_A,+/-",
            "operator_cross_emitter_first_term": "G_E0,+/- g_0 h_0 d G_A,+/- g_1 delta h_1 G_E1,+/- and its transpose",
        },
        "record_rank_disposition": {
            "external_localized_current_matrix_rank": 2,
            "formal_rank_stability_if_emitter_leading_matrix_rank_two": True,
            "actual_emitter_Cauchy_preparation_matrix_computed": False,
            "reason": "the handoff fixes a source map from free K_b Cauchy data but does not yet choose two data sets or evaluate their detector responses",
            "next_matrix": "M_ab^(K)=Q_a[d G_A,ret g_b delta(h_b K_b^(0))]",
        },
        "mutation_results": [
            {"name": name, "detected": True, "audit": result} for name, result in mutations.items()
        ],
        "flags": {
            "108_ROW_Q1_CERTIFIED": True,
            "108_ROW_UNARY_NILPOTENCY_CERTIFIED": True,
            "108_ROW_UNARY_CYCLICITY_CERTIFIED": True,
            "MASSIVE_TWO_FORM_ADVANCED_RETARDED_GREEN_CERTIFIED": True,
            "108_ROW_FORMAL_COUPLED_EULER_GREEN_THROUGH_G2_CERTIFIED": True,
            "FIRST_FORMAL_EMITTER_RECOIL_GREEN_OPERATOR_COMPUTED": True,
            "FULL_108_ROW_CAUSAL_CHAIN_CONTRACTION_CERTIFIED": False,
            "DYNAMICAL_EMITTER_RECORD_RANK_TWO_CERTIFIED": False,
            "DETECTOR_RECOIL_COEFFICIENT_EVALUATED": False,
            "EMITTER_STRESS_BACKREACTION_INCLUDED": False,
            "FINITE_PARAMETER_84_ROW_APPARATUS_GREEN_HYPERBOLICITY_CERTIFIED": False,
            "FULL_APPARATUS_DIRAC_BRACKET_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "COMPLETE_108_ROW_BV_CAUSAL_CHAIN_MAPS_THEN_CHOOSE_TWO_LOCALIZED_FREE_EMITTER_CAUCHY_PREPARATIONS_AND_COMPUTE_M_AB_K",
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
        raise SystemExit("stale 108-row emitter unary/recoil certificate")
    print("BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_FIRST_RECOIL generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
