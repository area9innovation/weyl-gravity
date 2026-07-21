#!/usr/bin/env python3
"""Build the fail-closed Paper IX claim-to-certificate table."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_DIR = ROOT / "d_quotient_classical/certificates"
OUTPUT = CERTIFICATE_DIR / "PAPER_09_BERGER_CLAIM_TABLE.json"
SCHEMA = ROOT / "d_quotient_classical/schema/paper-09-berger-claim-table-v1.schema.json"
MAIN_PAPER = ROOT / "paper/09-relational-clocks-berger-d-cartan.tex"
SUPPLEMENT = ROOT / "paper/09-relational-clocks-berger-d-cartan-computational-supplement.tex"
Q3_CROSSCHECK = CERTIFICATE_DIR / "BERGER_Q3_ACTION_SECTOR_CROSSCHECK.json"
GENERATOR_AUDIT = CERTIFICATE_DIR / "BERGER_GENERATOR_CONJUGATION_AUDIT.json"
NONLINEAR_SIGNOFF = CERTIFICATE_DIR / "PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF.json"
QUANTUM_SIGNOFF = ROOT / "quantum-weyl/cartan/certificates/PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF.json"
PUBLICATION_CLAIM_MAP = ROOT / "paper/09-relational-clocks-berger-d-cartan-claim-map.json"
DRAFT_ALLOWED_REPORT = ROOT / "reports/observer-paper09-counterflow-health-nonactivation-freeze-closeout-2026-07-21.md"
HEALTH_FREEZE_RECEIPT = ROOT / "closed_universe_observers/receipts/PAPER09_COUNTERFLOW_HEALTH_NONACTIVATION_FREEZE_V1_TIER_RECEIPT.json"
PRE_REPIN_PAPER_SOURCES = {
    "paper/09-relational-clocks-berger-d-cartan.tex": "817771965e1f32120743214a87124cc3e70ea2f46cc136a6caeada21e333f919",
    "paper/09-relational-clocks-berger-d-cartan-computational-supplement.tex": "c18235ff2e41372949e2d63a7f3ec30a7ae0df497b92e4eb9a540656e7b997ce",
}


CLAIMS = (
    {
        "claim_id": "P09-C1",
        "paper_sections": ["2"],
        "claim": "An exact smooth non-conformally-flat positive Berger clock family exists.",
        "certificate": "POSITIVE_BERGER_CLOCK_BACKGROUND.json",
        "required_true": ["flags.exact_backreacted_background_exists"],
        "required_false": [],
    },
    {
        "claim_id": "P09-C2",
        "paper_sections": ["2"],
        "claim": "The clock has standard-sign matter, timelike phase and positive bounded-below quartic potential.",
        "certificate": "POSITIVE_BERGER_CLOCK_BACKGROUND.json",
        "required_true": [
            "flags.positive_standard_scalar_kinetic",
            "flags.everywhere_timelike_phase_clock",
            "flags.bounded_below_quartic",
        ],
        "required_false": ["flags.quantum_admissibility_proved"],
    },
    {
        "claim_id": "P09-C3",
        "paper_sections": ["3"],
        "claim": "The internal clock charge is nonzero and Omega_total(delta,L_D)=omega delta Q_R.",
        "certificate": "BERGER_CLOCK_REDUCED_CHARGE_SEED.json",
        "required_true": [
            "flags.covariant_internal_current_derived",
            "flags.global_internal_charge_computed",
            "flags.helical_presymplectic_identity_derived",
        ],
        "required_false": ["flags.total_covariant_D_charge_computed"],
    },
    {
        "claim_id": "P09-C4",
        "paper_sections": ["3"],
        "claim": "At fixed couplings delta Q_R vanishes on every smooth allowed linearized tangent, so D is presymplectically null in the declared compact phase space.",
        "certificate": "BERGER_FIXED_COUPLING_DELTA_CHARGE.json",
        "required_true": [
            "flags.homogeneous_lapse_constraint_exact",
            "flags.full_mode_average_argument_exact",
            "flags.total_helical_presymplectic_contraction_zero",
            "flags.scoped_D_verdict_promoted",
        ],
        "required_false": ["flags.nonlinear_stability_proved"],
    },
    {
        "claim_id": "P09-C5",
        "paper_sections": ["5"],
        "claim": "The complete 54-row gauge-fixed unary BV complex has a cyclic support-local contraction onto 26 retained rows.",
        "certificate": "BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
        "required_true": [
            "flags.BERGER_COMPLETE_GAUGE_FIXED_UNARY_EXPORT",
            "flags.BERGER_GAUGE_FERMION_CANONICAL_TRANSFORM",
            "flags.BERGER_NONMINIMAL_COMPLETION",
        ],
        "required_false": ["flags.BERGER_HADAMARD_DATA"],
    },
    {
        "claim_id": "P09-C6",
        "paper_sections": ["5"],
        "claim": "The complete 54-row complex has K-equivariant advanced and retarded chain contractions with causal support and adjointness.",
        "certificate": "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json",
        "required_true": [
            "flags.BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2",
            "flags.BERGER_CAUSAL_GREEN_HOMOTOPY_V2",
            "exact_checks.advanced_chain_homotopy_identity",
            "exact_checks.retarded_chain_homotopy_identity",
            "exact_checks.D_equivariance",
            "exact_checks.cyclic_advanced_retarded_adjointness",
        ],
        "required_false": ["flags.BERGER_HADAMARD_DATA"],
    },
    {
        "claim_id": "P09-C7",
        "paper_sections": ["6"],
        "claim": "The complete arbitrary-input support-local q2 satisfies the arity-two L-infinity identity, cyclicity and K derivation.",
        "certificate": "BERGER_SUPPORT_LOCAL_Q2.json",
        "required_true": [
            "flags.CLASSICAL_SUPPORT_LOCAL_Q2",
            "flags.BERGER_LOCAL_D_ACTION_EQUIVARIANT_AT_ARITY_TWO",
            "exact_checks.q1_q2_arity_two_nilpotency_raw_coefficientwise",
            "exact_checks.BV_cyclicity_q2_coefficientwise_and_by_canonical_transport",
        ],
        "required_false": ["flags.GENERAL_LOCAL_ANTIFIELD_KOSZUL_TATE_EXPORT"],
    },
    {
        "claim_id": "P09-C8",
        "paper_sections": ["6"],
        "claim": "The complete arbitrary-input support-local q3 satisfies the arity-three L-infinity identity, quartic cyclicity and K derivation with L_K3=0.",
        "certificate": "BERGER_SUPPORT_LOCAL_Q3.json",
        "required_true": [
            "flags.CLASSICAL_SUPPORT_LOCAL_Q3",
            "flags.BERGER_LOCAL_D_ACTION_EQUIVARIANT_AT_ARITY_THREE",
            "exact_checks.q1_q3_plus_q2_q2_arity_three_nilpotency_raw_coefficientwise",
            "exact_checks.quartic_action_cyclicity_raw_coefficientwise",
            "local_D_arity_three.D_q3_derivation",
        ],
        "required_false": ["flags.GENERAL_LOCAL_ANTIFIELD_KOSZUL_TATE_EXPORT"],
    },
    {
        "claim_id": "P09-C9",
        "paper_sections": ["7"],
        "claim": "The complete 54-row classical complex has a cyclic causal K-Cartan contraction through arity two.",
        "certificate": "BERGER_CAUSAL_D_CARTAN_V2.json",
        "required_true": [
            "flags.BERGER_CAUSAL_D_CARTAN_V2",
            "flags.BERGER_CAUSAL_ARITY_TWO_SOURCE_CLOSED",
            "flags.BERGER_CAUSAL_ARITY_TWO_CYCLIC_COMPLETION",
        ],
        "required_false": ["flags.BERGER_HADAMARD_DATA", "flags.QUANTUM_CLAIM"],
    },
    {
        "claim_id": "P09-C10",
        "paper_sections": ["7"],
        "claim": "The complete 54-row arbitrary-input arity-three K-Cartan source is closed and has a cyclic two-sided-causal primitive.",
        "certificate": "BERGER_ARITY_THREE_D_CARTAN_FULL_4D.json",
        "required_true": [
            "flags.BERGER_ARITY_THREE_D_CARTAN_SOURCE_CLOSED",
            "flags.BERGER_ARITY_THREE_D_CARTAN_CYCLIC_COMPLETION",
            "flags.BERGER_ARITY_THREE_D_CARTAN_FULL_4D",
            "flags.BERGER_CAUSAL_D_CARTAN_THROUGH_ARITY_THREE",
        ],
        "required_false": ["flags.BERGER_HADAMARD_DATA", "flags.QUANTUM_CLAIM"],
    },
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def _lookup(payload: dict[str, object], dotted: str) -> object:
    cursor: object = payload
    for part in dotted.split("."):
        if not isinstance(cursor, dict) or part not in cursor:
            raise AssertionError(f"missing certificate field: {dotted}")
        cursor = cursor[part]
    return cursor


def build() -> dict[str, object]:
    claims: list[dict[str, object]] = []
    for spec in CLAIMS:
        path = CERTIFICATE_DIR / str(spec["certificate"])
        payload = _read(path)
        for dotted in spec["required_true"]:
            if _lookup(payload, dotted) is not True:
                raise AssertionError(f"{spec['claim_id']}: required true field failed: {dotted}")
        for dotted in spec["required_false"]:
            if _lookup(payload, dotted) is not False:
                raise AssertionError(f"{spec['claim_id']}: required false field failed: {dotted}")
        claims.append(
            {
                **spec,
                "certificate_path": str(path.relative_to(ROOT)),
                "certificate_result_id": payload["result_id"],
                "certificate_sha256": _sha256(path),
                "certificate_claim_boundary": payload["claim_boundary"],
            }
        )
    crosscheck = _read(Q3_CROSSCHECK)
    crosscheck_required_true = [
        "flags.BERGER_Q3_ACTION_SECTOR_CROSSCHECK",
        "exact_checks.all_eight_action_derivatives_match",
        "exact_checks.all_sixteen_ordered_payload_coefficients_match",
        "exact_checks.q3_producer_not_imported",
    ]
    crosscheck_required_false = [
        "flags.FULL_INDEPENDENT_Q3_REDERIVATION",
        "flags.THEOREM_FROZEN",
    ]
    for dotted in crosscheck_required_true:
        if _lookup(crosscheck, dotted) is not True:
            raise AssertionError(f"q3 cross-check required true field failed: {dotted}")
    for dotted in crosscheck_required_false:
        if _lookup(crosscheck, dotted) is not False:
            raise AssertionError(f"q3 cross-check required false field failed: {dotted}")
    generator_audit = _read(GENERATOR_AUDIT)
    generator_required_true = [
        "flags.EXPORTED_UNARY_GENERATOR_IS_K",
        "flags.AFFINE_D_ZERO_ARITY_NONZERO",
        "flags.PAPER09_K_CARTAN_INTERPRETATION",
        "exact_checks.frozen_e0_action_equals_K_unary_action",
    ]
    generator_required_false = [
        "flags.EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D",
        "flags.PAPER09_D_CARTAN_AS_PREVIOUSLY_WRITTEN",
        "flags.AFFINE_D_CARTAN_CONSTRUCTED",
        "flags.THEOREM_FROZEN",
    ]
    for dotted in generator_required_true:
        if _lookup(generator_audit, dotted) is not True:
            raise AssertionError(f"generator audit required true field failed: {dotted}")
    for dotted in generator_required_false:
        if _lookup(generator_audit, dotted) is not False:
            raise AssertionError(f"generator audit required false field failed: {dotted}")

    nonlinear_signoff = _read(NONLINEAR_SIGNOFF)
    nonlinear_required_true = [
        "flags.PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF",
        "flags.K_BERGER_CARTAN_THROUGH_ARITY_THREE",
        "exact_checks.q2_action_derived_support_local_and_K_equivariant",
        "exact_checks.q3_action_derived_support_local_and_K_equivariant",
        "exact_checks.causal_chain_contractions_cover_all_54_rows",
        "exact_checks.cyclic_K_Cartan_identity_through_arity_three",
    ]
    nonlinear_required_false = [
        "flags.RAW_D_CARTAN_CERTIFIED",
        "flags.ARITY_FOUR_CARTAN_CERTIFIED",
        "flags.ALL_ORDERS_CARTAN_CERTIFIED",
        "flags.QUANTUM_CLAIM",
        "flags.THEOREM_FROZEN",
    ]
    for dotted in nonlinear_required_true:
        if _lookup(nonlinear_signoff, dotted) is not True:
            raise AssertionError(f"nonlinear signoff required true field failed: {dotted}")
    for dotted in nonlinear_required_false:
        if _lookup(nonlinear_signoff, dotted) is not False:
            raise AssertionError(f"nonlinear signoff forbidden promotion detected: {dotted}")
    if nonlinear_signoff.get("review_status") != "SIGNED_SCOPED_K_THEOREM":
        raise AssertionError("nonlinear signoff verdict drifted")

    quantum_signoff = _read(QUANTUM_SIGNOFF)
    quantum_required_true = [
        "theorem_flags.PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF",
        "theorem_flags.PAPER09_CLASSICAL_K_CARTAN_THROUGH_ARITY_THREE_ACCEPTED",
    ]
    quantum_required_false = [
        "theorem_flags.PAPER09_AFFINE_D_CARTAN_ACCEPTED",
        "theorem_flags.PAPER09_HADAMARD_ACCEPTED",
        "theorem_flags.PAPER09_QME_ACCEPTED",
        "theorem_flags.PAPER09_ANOMALY_CANCELLATION_ACCEPTED",
        "theorem_flags.PAPER09_QUANTUM_PROMOTION_ACCEPTED",
    ]
    for dotted in quantum_required_true:
        if _lookup(quantum_signoff, dotted) is not True:
            raise AssertionError(f"quantum signoff required true field failed: {dotted}")
    for dotted in quantum_required_false:
        if _lookup(quantum_signoff, dotted) is not False:
            raise AssertionError(f"quantum signoff forbidden promotion detected: {dotted}")
    if quantum_signoff.get("claim_status") != "SIGNED_OFF_CLASSICAL_K_ONLY_QUANTUM_BLOCKED":
        raise AssertionError("quantum signoff verdict drifted")
    publication_map = _read(PUBLICATION_CLAIM_MAP)
    if publication_map.get("result_id") != "PAPER09_COUNTERFLOW_HEALTH_NONACTIVATION_FREEZE_V1":
        raise AssertionError("publication-current Paper 9 claim map identity drifted")
    if publication_map.get("freeze_decision") != "DRAFT_ALLOWED":
        raise AssertionError("publication-current Paper 9 decision is not DRAFT_ALLOWED")
    publication_claim_ids = [entry.get("claim_id") for entry in publication_map.get("claims", [])]
    if len(publication_claim_ids) != 22 or publication_claim_ids[:10] != [spec["claim_id"] for spec in CLAIMS]:
        raise AssertionError("22-claim superset no longer preserves the ten legacy claim identities")
    health_receipt = _read(HEALTH_FREEZE_RECEIPT)
    if health_receipt.get("result_id") != "PAPER09_COUNTERFLOW_HEALTH_NONACTIVATION_FREEZE_V1_TIER_RECEIPT":
        raise AssertionError("Paper 9 health-freeze receipt identity drifted")
    draft_report = DRAFT_ALLOWED_REPORT.read_text()
    if "Decision: `DRAFT_ALLOWED`" not in draft_report or "LEGACY_TEN_CLAIM_SOURCE_BINDING_SUPERSESSION" not in draft_report:
        raise AssertionError("DRAFT_ALLOWED report no longer records this source-binding gate")
    return {
        "schema": "pure-weyl-paper-09-berger-claim-table-v1",
        "result_id": "PAPER_09_BERGER_CLAIM_TABLE",
        "paper_state": "THEOREM_FROZEN",
        "theorem_frozen": True,
        "paper_sources": {
            str(MAIN_PAPER.relative_to(ROOT)): _sha256(MAIN_PAPER),
            str(SUPPLEMENT.relative_to(ROOT)): _sha256(SUPPLEMENT),
        },
        "source_binding_disposition": {
            "selected_disposition": "REPIN_CURRENT_PUBLICATION_SOURCES",
            "scientific_claim_change": False,
            "legacy_certificate_retained": True,
            "legacy_claim_count": 10,
            "publication_superset_claim_count": 22,
            "legacy_claim_ids_preserved_in_superset": [spec["claim_id"] for spec in CLAIMS],
            "pre_repin_paper_sources": PRE_REPIN_PAPER_SOURCES,
            "publication_claim_map": {
                "path": str(PUBLICATION_CLAIM_MAP.relative_to(ROOT)),
                "sha256": _sha256(PUBLICATION_CLAIM_MAP),
                "result_id": publication_map["result_id"],
                "freeze_decision": publication_map["freeze_decision"],
            },
            "draft_allowed_report": {
                "path": str(DRAFT_ALLOWED_REPORT.relative_to(ROOT)),
                "sha256": _sha256(DRAFT_ALLOWED_REPORT),
                "decision": "DRAFT_ALLOWED",
            },
            "health_freeze_receipt": {
                "path": str(HEALTH_FREEZE_RECEIPT.relative_to(ROOT)),
                "sha256": _sha256(HEALTH_FREEZE_RECEIPT),
                "result_id": health_receipt["result_id"],
            },
            "superset_followup": "The publication claim-map owner must regenerate its exact import of PAPER_09_BERGER_CLAIM_TABLE after this repin; no observer claim is imported into the ten-claim table.",
        },
        "setting": "one-parameter compact positive Berger S1 clock incidence family across the scalar coupling for fixed-coupling momentum rigidity and linear D nullity; exact rational q=9/40 representative for the 54-row classical K-Cartan result through arity three",
        "claims": claims,
        "claim_ids_complete": [spec["claim_id"] for spec in CLAIMS],
        "independent_cross_checks": [
            {
                "supports_claim": "P09-C8",
                "certificate_path": str(Q3_CROSSCHECK.relative_to(ROOT)),
                "certificate_result_id": crosscheck["result_id"],
                "certificate_sha256": _sha256(Q3_CROSSCHECK),
                "certificate_claim_boundary": crosscheck["claim_boundary"],
                "required_true": crosscheck_required_true,
                "required_false": crosscheck_required_false,
            },
            {
                "supports_claim": "P09-C6--P09-C10",
                "certificate_path": str(GENERATOR_AUDIT.relative_to(ROOT)),
                "certificate_result_id": generator_audit["result_id"],
                "certificate_sha256": _sha256(GENERATOR_AUDIT),
                "certificate_claim_boundary": generator_audit["claim_boundary"],
                "required_true": generator_required_true,
                "required_false": generator_required_false,
            }
        ],
        "signoff_evidence": [
            {
                "team": "nonlinear_team",
                "status": nonlinear_signoff["review_status"],
                "certificate_path": str(NONLINEAR_SIGNOFF.relative_to(ROOT)),
                "certificate_result_id": nonlinear_signoff["result_id"],
                "certificate_sha256": _sha256(NONLINEAR_SIGNOFF),
                "certificate_claim_boundary": nonlinear_signoff["claim_boundary"],
                "required_true": nonlinear_required_true,
                "required_false": nonlinear_required_false,
            },
            {
                "team": "quantum_team",
                "status": quantum_signoff["claim_status"],
                "certificate_path": str(QUANTUM_SIGNOFF.relative_to(ROOT)),
                "certificate_result_id": quantum_signoff["result_id"],
                "certificate_sha256": _sha256(QUANTUM_SIGNOFF),
                "certificate_claim_boundary": quantum_signoff["claim_boundary"],
                "required_true": quantum_required_true,
                "required_false": quantum_required_false,
            },
        ],
        "required_signoffs": {
            "classical_team": "SIGNED_AND_FROZEN",
            "nonlinear_team": "SIGNED_K_GENERATOR_INTERPRETATION",
            "quantum_team": "SIGNED_OFF_CLASSICAL_K_ONLY_QUANTUM_BLOCKED",
            "einstein_team": "OPTIONAL_INTERNAL_REFEREE",
        },
        "forbidden_promotions": [
            "affine D-Cartan at any nonlinear order",
            "unconditional or convergent all-orders K-Cartan",
            "Hadamard state",
            "quantum master equation",
            "anomaly cancellation",
            "positive graviton Hilbert space",
            "boundary or asymptotic charge theorem",
            "integrated nonlinear D quotient",
            "global complete relational observable",
        ],
        "main_theorem_exclusions": [
            "Maxwell signal or redshift results",
            "observer-apparatus or 84-row results",
            "affine raw-D Cartan",
            "quantum or Hadamard results",
        ],
        "next_gate": "POST_FREEZE_OBSERVER_84_ROW_BACKGROUND_SUPPORT",
        "claim_boundary": "This theorem-frozen table binds Paper IX to exactly ten scoped classical Berger gravity-clock certificates, an exact generator-conjugation audit, one strategic independent action-to-q3 sector cross-check, and content-addressed nonlinear and quantum-team signoffs. It proves fixed-coupling momentum rigidity and linear presymplectic nullity for raw D, while the based classical Cartan identity through arity three is for K=D-omega R. Maxwell signal, redshift, observer-apparatus, and 84-row results are excluded from the main theorem. No affine D-Cartan, integrated nonlinear quotient, global complete observable, full second q3 derivation, convergent all-orders, Hadamard, quantum, boundary, scattering, or unitarity claim is promoted.",
    }


def verify(payload: dict[str, object]) -> None:
    if payload["theorem_frozen"] is not True or payload["paper_state"] != "THEOREM_FROZEN":
        raise AssertionError("Paper IX theorem freeze is absent")
    expected = [spec["claim_id"] for spec in CLAIMS]
    if payload["claim_ids_complete"] != expected:
        raise AssertionError("claim-id ledger is incomplete or reordered")
    if [entry["claim_id"] for entry in payload["claims"]] != expected:
        raise AssertionError("claim entries are incomplete or reordered")
    for entry, spec in zip(payload["claims"], CLAIMS):
        for key in ("claim_id", "paper_sections", "claim", "certificate", "required_true", "required_false"):
            if entry[key] != spec[key]:
                raise AssertionError(f"legacy claim scope drifted: {spec['claim_id']} {key}")
    for relative, expected_hash in payload["paper_sources"].items():
        if _sha256(ROOT / relative) != expected_hash:
            raise AssertionError(f"paper source hash drifted: {relative}")
    binding = payload["source_binding_disposition"]
    if binding["selected_disposition"] != "REPIN_CURRENT_PUBLICATION_SOURCES":
        raise AssertionError("source-binding disposition is not REPIN")
    if binding["scientific_claim_change"] is not False or binding["legacy_certificate_retained"] is not True:
        raise AssertionError("repin changed science or retired the legacy certificate")
    if binding["legacy_claim_count"] != 10 or binding["publication_superset_claim_count"] != 22:
        raise AssertionError("legacy/superset claim counts drifted")
    if binding["legacy_claim_ids_preserved_in_superset"] != expected:
        raise AssertionError("legacy claim identities are not preserved in the superset")
    for key in ("publication_claim_map", "draft_allowed_report", "health_freeze_receipt"):
        ref = binding[key]
        if _sha256(ROOT / ref["path"]) != ref["sha256"]:
            raise AssertionError(f"source-binding import hash drifted: {key}")
    main = MAIN_PAPER.read_text()
    supplement = SUPPLEMENT.read_text()
    for claim_id in expected:
        if claim_id not in main or claim_id not in supplement:
            raise AssertionError(f"claim id is absent from a paper source: {claim_id}")
    theorem_blocks = main.split("\\begin{theorem}")[1:]
    theorem_text = "\n".join(block.split("\\end{theorem}", 1)[0] for block in theorem_blocks)
    for forbidden in ("Maxwell", "observer-apparatus", "84-row"):
        if forbidden in theorem_text:
            raise AssertionError(f"main theorem illegally imports downstream result: {forbidden}")
    if any("MAXWELL" in entry["certificate_result_id"] for entry in payload["claims"]):
        raise AssertionError("Maxwell certificate entered the ten-claim theorem ledger")
    if payload["main_theorem_exclusions"][:2] != [
        "Maxwell signal or redshift results",
        "observer-apparatus or 84-row results",
    ]:
        raise AssertionError("main-theorem downstream exclusions drifted")
    if payload["required_signoffs"]["nonlinear_team"] != "SIGNED_K_GENERATOR_INTERPRETATION":
        raise AssertionError("nonlinear signoff is absent or overpromoted")
    if payload["required_signoffs"]["quantum_team"] != "SIGNED_OFF_CLASSICAL_K_ONLY_QUANTUM_BLOCKED":
        raise AssertionError("quantum claim-boundary signoff is absent or overpromoted")
    for entry in payload["claims"]:
        path = ROOT / entry["certificate_path"]
        if _sha256(path) != entry["certificate_sha256"]:
            raise AssertionError(f"certificate hash drifted: {entry['claim_id']}")
        certificate = _read(path)
        for dotted in entry["required_true"]:
            if _lookup(certificate, dotted) is not True:
                raise AssertionError(f"{entry['claim_id']}: required true flag drifted")
        for dotted in entry["required_false"]:
            if _lookup(certificate, dotted) is not False:
                raise AssertionError(f"{entry['claim_id']}: forbidden promotion detected")
    for entry in payload["independent_cross_checks"]:
        path = ROOT / entry["certificate_path"]
        if _sha256(path) != entry["certificate_sha256"]:
            raise AssertionError("independent cross-check hash drifted")
        certificate = _read(path)
        for dotted in entry["required_true"]:
            if _lookup(certificate, dotted) is not True:
                raise AssertionError(f"cross-check required true flag drifted: {dotted}")
        for dotted in entry["required_false"]:
            if _lookup(certificate, dotted) is not False:
                raise AssertionError(f"cross-check scope promotion detected: {dotted}")
    expected_signoffs = [
        ("nonlinear_team", "PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF", "SIGNED_SCOPED_K_THEOREM"),
        ("quantum_team", "PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF", "SIGNED_OFF_CLASSICAL_K_ONLY_QUANTUM_BLOCKED"),
    ]
    if len(payload["signoff_evidence"]) != len(expected_signoffs):
        raise AssertionError("signoff evidence is incomplete")
    for entry, (team, result_id, status) in zip(payload["signoff_evidence"], expected_signoffs):
        if (entry["team"], entry["certificate_result_id"], entry["status"]) != (team, result_id, status):
            raise AssertionError("signoff identity or verdict drifted")
        path = ROOT / entry["certificate_path"]
        if _sha256(path) != entry["certificate_sha256"]:
            raise AssertionError(f"signoff hash drifted: {team}")
        certificate = _read(path)
        for dotted in entry["required_true"]:
            if _lookup(certificate, dotted) is not True:
                raise AssertionError(f"signoff required true flag drifted: {team} {dotted}")
        for dotted in entry["required_false"]:
            if _lookup(certificate, dotted) is not False:
                raise AssertionError(f"signoff scope promotion detected: {team} {dotted}")


def _text(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    verify(payload)
    if args.write:
        OUTPUT.write_text(_text(payload))
    if args.check and OUTPUT.read_text() != _text(payload):
        raise AssertionError("Paper IX claim table drifted")
    if args.guards:
        mutants = (
            ("unfreeze theorem", ("theorem_frozen",), False),
            ("overpromote nonlinear signoff", ("required_signoffs", "nonlinear_team"), "APPROVED_UNSCOPED"),
            ("overpromote quantum signoff", ("required_signoffs", "quantum_team"), "QUANTUM_THEOREM_APPROVED"),
            ("drop signoff evidence", ("signoff_evidence",), payload["signoff_evidence"][:-1]),
            ("stale old paper hash", ("paper_sources", "paper/09-relational-clocks-berger-d-cartan.tex"), PRE_REPIN_PAPER_SOURCES["paper/09-relational-clocks-berger-d-cartan.tex"]),
            ("dropped legacy claim", ("claims",), payload["claims"][:-1]),
            ("scope widening", ("claims", 0, "claim"), payload["claims"][0]["claim"] + " This holds for every background."),
            ("silent certificate deletion", ("claims", 0, "certificate_sha256"), "0" * 64),
        )
        for name, path, value in mutants:
            mutant = deepcopy(payload)
            cursor = mutant
            for part in path[:-1]:
                cursor = cursor[part]
            cursor[path[-1]] = value
            try:
                verify(mutant)
            except AssertionError:
                continue
            raise AssertionError(f"mutation guard accepted: {name}")
    print("PAPER_09_BERGER_CLAIM_TABLE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
