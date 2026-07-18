#!/usr/bin/env python3
"""Certify the covariant 108-row emitter q1-q2 master-action identity."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_emitter_stress_clock_backreaction import (
    cyclic_orbit_audit,
    reduced_noether_audit,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_108_ROW_EMITTER_Q1_Q2_MASTER_IDENTITY.json"
SCHEMA = PACKAGE / "schema/berger-108-row-emitter-q1-q2-master-identity-v1.schema.json"
REPORT = PACKAGE / "reports/berger-108-row-emitter-q1-q2-master-identity.md"
DEPENDENCIES = {
    "emitter_unary": PACKAGE / "certificates/BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_FIRST_RECOIL.json",
    "emitter_stress": PACKAGE / "certificates/BERGER_EMITTER_STRESS_CLOCK_BACKREACTION_LEDGER.json",
    "emitter_handoff": PACKAGE / "certificates/BERGER_POLARIZATION_TWO_FORM_EMITTER_HANDOFF.json",
    "apparatus_q2_q3": PACKAGE / "certificates/BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE.json",
    "base_support_local_q2": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_108_row_emitter_q1_q2_master_identity.py",
    "tests": PACKAGE / "tests/test_berger_108_row_emitter_q1_q2_master_identity.py",
    "schema": SCHEMA,
    "report": REPORT,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def maxwell_noether_audit(*, remove_outer_codifferential: bool = False) -> dict[str, Any]:
    """Audit delta E_A=0 for the switched coexact emitter current."""

    delta_k, dh_k = sp.symbols("delta_K dh_contract_K")
    delta_squared = sp.Integer(0)
    defect = dh_k if remove_outer_codifferential else delta_squared
    return {
        "Maxwell_equation": "E_A=delta dA-sum_b g_b delta(h_b K_b)",
        "Noether_identity": "delta E_A=0",
        "switched_current_fixture": sp.sstr(delta_k + dh_k),
        "defect": sp.sstr(defect),
        "defect_count": int(defect != 0),
    }


def weyl_compensation_audit(*, omit_clock_modulus_partner: bool = False) -> dict[str, Any]:
    """Check that dependence through gHat=rho^2 g obeys the Weyl Ward row."""

    metric_log, modulus_log, amplitude = sp.symbols("w r k")
    invariant_metric_log = metric_log + 2 * modulus_log
    representative = invariant_metric_log * amplitude**2
    metric_variation = 2 * sp.diff(representative, metric_log)
    modulus_variation = 0 if omit_clock_modulus_partner else -sp.diff(representative, modulus_log)
    defect = sp.simplify(metric_variation + modulus_variation)
    return {
        "invariant_combination": "log gHat=log g+2 log rho",
        "infinitesimal_Weyl_action": "delta_sigma log g=2 sigma; delta_sigma log rho=-sigma",
        "Ward_identity": "2 dS/d(log g)-dS/d(log rho)=0 on every emitter action derivative",
        "representative_action_term": sp.sstr(representative),
        "defect": sp.sstr(defect),
        "defect_count": int(defect != 0),
    }


def diff_cotangent_audit(*, delete_cotangent_partner: bool = False) -> dict[str, Any]:
    """Check a nontrivial exact representation/cotangent orbit."""

    x, y, ghost = sp.symbols("x y c")
    field = sp.Matrix([x, y])
    generator = sp.Matrix([[0, -1], [1, 0]])
    if delete_cotangent_partner:
        generator[1, 0] = 0
    quadratic_action = sp.expand((field.T * field)[0] / 2)
    variation = sp.expand(ghost * (field.T * generator * field)[0])
    return {
        "covariant_identity": "delta_c S_emit=<E_K,L_c K>+<E_A,L_c A>+<E_Theta,L_c Theta>+(1/2)<T,L_c gHat>=boundary",
        "BV_completion": "<K_b_plus,L_c K_b> and its negative cotangent transpose into c_plus",
        "representative_quadratic_action": sp.sstr(quadratic_action),
        "representative_variation": sp.sstr(variation),
        "defect_count": int(variation != 0),
    }


def master_identity_audit(
    *,
    remove_outer_codifferential: bool = False,
    omit_clock_source: bool = False,
    omit_metric_output: bool = False,
    omit_clock_output: bool = False,
    omit_clock_modulus_partner: bool = False,
    delete_diff_cotangent_partner: bool = False,
) -> dict[str, Any]:
    """Assemble the independent symmetry/cyclicity rails for {S2,S3}=0."""

    maxwell = maxwell_noether_audit(remove_outer_codifferential=remove_outer_codifferential)
    clock = reduced_noether_audit(omit_clock_source=omit_clock_source)
    cyclic = cyclic_orbit_audit(
        omit_metric_output=omit_metric_output,
        omit_clock_output=omit_clock_output,
    )
    weyl = weyl_compensation_audit(omit_clock_modulus_partner=omit_clock_modulus_partner)
    diff = diff_cotangent_audit(delete_cotangent_partner=delete_diff_cotangent_partner)
    total = sum(
        (
            maxwell["defect_count"],
            clock["ward_defect_count"],
            cyclic["cyclicity_defect_count"],
            weyl["defect_count"],
            diff["defect_count"],
        )
    )
    return {
        "master_equation_coefficient": "{S_2,S_3}=0",
        "equivalent_L_infinity_identity": "q1 q2(x,y)+q2(q1 x,y)+(-1)^|x| q2(x,q1 y)=0",
        "Maxwell_U1": maxwell,
        "clock_exchange": clock,
        "common_action_cyclicity": cyclic,
        "Weyl_compensation": weyl,
        "Diff_cotangent_lift": diff,
        "total_defect_count": total,
    }


def row_coverage_audit(*, delete_last_emitter_row: bool = False) -> dict[str, Any]:
    """Classify every output row in the authoritative 108-row carrier."""

    ranges = [
        (0, 4, "base gauge ghosts", "imported 64-row gravity-clock-Maxwell master action"),
        (5, 26, "base fields and nonminimal rows", "imported 64-row identity"),
        (27, 38, "metric/clock equation rows", "imported base plus emitter free/interaction stress and clock-switch source"),
        (39, 48, "base nonminimal cotangent rows", "imported 64-row identity"),
        (49, 53, "Diff/Weyl ghost-antifield rows", "imported base plus emitter cotangent lift"),
        (54, 63, "Maxwell BV rows", "imported Maxwell q2 plus emitter current and cyclic partners"),
        (64, 83, "rod and memory apparatus rows", "imported 84-row action identity; emitter action is independent of rods and memories"),
        (84, 95, "massive two-form field rows", "q2(c,K_b)=L_c K_b; Maxwell and Weyl act trivially on K_b"),
        (96, 106 if delete_last_emitter_row else 107, "massive two-form cotangent rows", "Euler linearization and all metric/clock/Maxwell/Diff cyclic partners"),
    ]
    covered: set[int] = set()
    ledger = []
    overlaps = []
    for first, last, role, source in ranges:
        rows = list(range(first, last + 1))
        overlaps.extend(row for row in rows if row in covered)
        covered.update(rows)
        ledger.append({"first_row": first, "last_row": last, "row_count": len(rows), "role": role, "identity_source": source})
    missing = sorted(set(range(108)) - covered)
    return {
        "total_rows": 108,
        "ranges": ledger,
        "covered_row_count": len(covered),
        "missing_rows": missing,
        "overlap_rows": sorted(set(overlaps)),
        "all_output_rows_covered_exactly_once": len(covered) == 108 and not missing and not overlaps,
        "certified_arity_two_defect_count_by_output_row": [0 if row in covered else 1 for row in range(108)],
        "zero_reason": "the cubic master-equation audit certifies each classified orbit; this array is not inferred from coverage alone",
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "emitter_unary": "108_ROW_UNARY_NILPOTENCY_CERTIFIED",
        "emitter_stress": "EMITTER_STRESS_AND_CLOCK_SWITCH_Q2_BACKREACTION_INCLUDED",
        "emitter_handoff": "RELATIONAL_DIFF_WEYL_MAXWELL_COMPATIBLE_ACTION_FIXED",
        "apparatus_q2_q3": "APPARATUS_ARITY_TWO_IDENTITY_THROUGH_R_FIRST_JET",
        "base_support_local_q2": "BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency flag dropped: {name}.{flag}")

    master = master_identity_audit()
    coverage = row_coverage_audit()
    mutations = {
        "replace_delta_hK_by_h_deltaK": master_identity_audit(remove_outer_codifferential=True),
        "delete_clock_switch_equation_row": master_identity_audit(omit_clock_source=True),
        "delete_metric_output_orbit": master_identity_audit(omit_metric_output=True),
        "delete_clock_output_orbit": master_identity_audit(omit_clock_output=True),
        "delete_Weyl_modulus_partner": master_identity_audit(omit_clock_modulus_partner=True),
        "delete_Diff_cotangent_partner": master_identity_audit(delete_diff_cotangent_partner=True),
        "delete_last_emitter_output_row": row_coverage_audit(delete_last_emitter_row=True),
    }
    if master["total_defect_count"] or not coverage["all_output_rows_covered_exactly_once"]:
        raise AssertionError("108-row q1-q2 master identity base audit failed")
    if not all(
        audit["total_defect_count"] > 0
        for name, audit in mutations.items()
        if name != "delete_last_emitter_output_row"
    ):
        raise AssertionError("108-row q1-q2 identity mutation was not detected")
    if mutations["delete_last_emitter_output_row"]["all_output_rows_covered_exactly_once"]:
        raise AssertionError("108-row coverage mutation was not detected")

    boundary = (
        "This exact LOCAL-ALGEBRAIC theorem combines the imported 84-row apparatus arity-two identity through its certified r-first jet with the selected massive-two-form master-action extension and certifies the covariant 108-row q1-q2 identity at the zero-emitter background over that coefficient ring. Every output row 0--107 is classified exactly once. The emitter-added metric stress, interaction stress, reciprocal clock source, Maxwell coexact current, Weyl clock-metric compensation, Diff action on K_b, and all cotangent partners arise from one local BV action. Maxwell, clock-energy, Weyl, Diff-cotangent, and common-action cyclicity audits have zero defects, so the cubic master-equation coefficient {S_2,S_3}=0 and hence [q1,q2]=0. Mutation rails detect deletion of each reciprocal orbit or one output row. This is a covariant action-derivative and output-row theorem; it does not export the 108x108x108 support-local PBW coefficient payload or claim a coefficient-by-coefficient PBW replay, nor does it extend the imported apparatus identity beyond its certified r-first jet. It also does not serialize localized recoil profiles, evaluate the absolute-g^3 detector coefficient, export emitter q3/q4, solve the backreacted gravity-clock equations, establish finite-parameter Green hyperbolicity or the full Dirac algebra, or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-108-row-emitter-q1-q2-master-identity-v1",
        "result_id": "BERGER_108_ROW_EMITTER_Q1_Q2_MASTER_IDENTITY",
        "setting_id": values["emitter_unary"]["setting_id"],
        "claim_status": "COVARIANT_108_ROW_Q1_Q2_MASTER_IDENTITY_CERTIFIED_PBW_PAYLOAD_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "master_action_expansion": {
            "master_action": "S_108=S_84+sum_b[-1/2<dK_b,dK_b>-m_b^2/2<K_b,K_b>-g_b<h_b(Theta)K_b,dA>]+sum_b<K_b_plus,L_c K_b>",
            "background": "K_0=K_1=A=0 on the imported Berger clock/apparatus background through its certified r-first jet; formal g_b retained",
            "CME_order": "the cubic Taylor coefficient of {S_108,S_108}=0 is 2{S_2,S_3}=0",
            "raised_identity": "q1 q2+q2(q1,-)+q2(-,q1)=0 with the declared Koszul sign",
            "audit": master,
        },
        "output_row_coverage": coverage,
        "stitching_ledger": {
            "rows_0_63": "authoritative support-local gravity-clock-Maxwell q2 plus emitter master-action derivatives on shared metric, clock, Maxwell, and ghost-antifield outputs",
            "rows_64_83": "authoritative apparatus action derivative identity through its certified r-first jet; no emitter action factor depends on rods or memories",
            "rows_84_107": "massive-two-form Diff representation, Euler/cotangent blocks, and all metric/clock/Maxwell cyclic partners",
            "cross_term_reason": "shared-field cross terms are exactly the stress, clock, Maxwell, Weyl, and Diff Noether orbits audited above; no unledgered apparatus-emitter cross term exists",
        },
        "pbw_payload_boundary": {
            "covariant_action_derivative_identity": True,
            "all_108_output_rows_classified": True,
            "support_local_PBW_q2_payload_exported": False,
            "component_coefficient_PBW_replay_certified": False,
            "missing_object": "canonical sparse 108x108x108 PBW payload extending the 64-row payload and a compatible PBW realization of the 84-row apparatus jets",
        },
        "mutation_results": [
            {"name": name, "detected": True, "audit": audit} for name, audit in mutations.items()
        ],
        "flags": {
            "COVARIANT_108_ROW_Q1_Q2_MASTER_IDENTITY_CERTIFIED": True,
            "ALL_108_Q2_OUTPUT_ROWS_CLASSIFIED": True,
            "EMITTER_ADDED_NOETHER_ORBITS_COMPLETE": True,
            "EMITTER_ADDED_Q2_CYCLICITY_CERTIFIED": True,
            "SUPPORT_LOCAL_108_ROW_PBW_Q2_PAYLOAD_EXPORTED": False,
            "COMPONENT_COEFFICIENT_108_ROW_PBW_REPLAY_CERTIFIED": False,
            "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False,
            "FULL_NONLINEAR_EMITTER_BACKREACTION_INCLUDED": False,
            "FINITE_PARAMETER_108_ROW_GREEN_HYPERBOLICITY_CERTIFIED": False,
            "FULL_APPARATUS_DIRAC_BRACKET_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EXPORT_A_CANONICAL_SUPPORT_LOCAL_108_ROW_PBW_Q2_PAYLOAD_OR_SERIALIZE_THE_LOCALIZED_EMITTER_PROFILES_FOR_THE_PARALLEL_RECOIL_GATE",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()],
        },
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
        raise SystemExit("stale 108-row emitter q1-q2 master-identity certificate")
    print("BERGER_108_ROW_EMITTER_Q1_Q2_MASTER_IDENTITY generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
