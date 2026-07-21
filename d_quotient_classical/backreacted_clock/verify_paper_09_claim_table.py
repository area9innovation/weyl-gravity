#!/usr/bin/env python3
"""Independent consumer for the Paper IX claim-to-certificate table."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
TABLE = ROOT / "d_quotient_classical/certificates/PAPER_09_BERGER_CLAIM_TABLE.json"
SCHEMA = ROOT / "d_quotient_classical/schema/paper-09-berger-claim-table-v1.schema.json"

EXPECTED_LEGACY_CLAIMS = (
    "An exact smooth non-conformally-flat positive Berger clock family exists.",
    "The clock has standard-sign matter, timelike phase and positive bounded-below quartic potential.",
    "The internal clock charge is nonzero and Omega_total(delta,L_D)=omega delta Q_R.",
    "At fixed couplings delta Q_R vanishes on every smooth allowed linearized tangent, so D is presymplectically null in the declared compact phase space.",
    "The complete 54-row gauge-fixed unary BV complex has a cyclic support-local contraction onto 26 retained rows.",
    "The complete 54-row complex has K-equivariant advanced and retarded chain contractions with causal support and adjointness.",
    "The complete arbitrary-input support-local q2 satisfies the arity-two L-infinity identity, cyclicity and K derivation.",
    "The complete arbitrary-input support-local q3 satisfies the arity-three L-infinity identity, quartic cyclicity and K derivation with L_K3=0.",
    "The complete 54-row classical complex has a cyclic causal K-Cartan contraction through arity two.",
    "The complete 54-row arbitrary-input arity-three K-Cartan source is closed and has a cyclic two-sided-causal primitive.",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _lookup(payload: dict[str, object], dotted: str) -> object:
    value: object = payload
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            raise AssertionError(f"missing required field: {dotted}")
        value = value[part]
    return value


def main() -> int:
    table = json.loads(TABLE.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(table)
    if table["theorem_frozen"] is not True or table["paper_state"] != "THEOREM_FROZEN":
        raise AssertionError("Paper IX theorem freeze is absent")
    ids = [entry["claim_id"] for entry in table["claims"]]
    if ids != [f"P09-C{index}" for index in range(1, 11)]:
        raise AssertionError("claim ids are not the complete canonical sequence")
    if tuple(entry["claim"] for entry in table["claims"]) != EXPECTED_LEGACY_CLAIMS:
        raise AssertionError("legacy claim wording or scope drifted")
    binding = table["source_binding_disposition"]
    if binding["selected_disposition"] != "REPIN_CURRENT_PUBLICATION_SOURCES":
        raise AssertionError("legacy source-binding disposition is not REPIN")
    if binding["scientific_claim_change"] is not False or binding["legacy_certificate_retained"] is not True:
        raise AssertionError("repin changed science or deleted the legacy certificate")
    if binding["legacy_claim_ids_preserved_in_superset"] != ids:
        raise AssertionError("22-claim superset does not preserve the legacy claim sequence")
    if binding["legacy_claim_count"] != 10 or binding["publication_superset_claim_count"] != 22:
        raise AssertionError("legacy/superset claim count mismatch")
    for key in ("publication_claim_map", "draft_allowed_report", "health_freeze_receipt"):
        ref = binding[key]
        path = ROOT / ref["path"]
        if _sha256(path) != ref["sha256"]:
            raise AssertionError(f"source-binding evidence hash mismatch: {key}")
    publication_map = json.loads((ROOT / binding["publication_claim_map"]["path"]).read_text())
    if publication_map["result_id"] != "PAPER09_COUNTERFLOW_HEALTH_NONACTIVATION_FREEZE_V1" or publication_map["freeze_decision"] != "DRAFT_ALLOWED":
        raise AssertionError("publication-current 22-claim map identity or decision drifted")
    if [entry["claim_id"] for entry in publication_map["claims"][:10]] != ids or len(publication_map["claims"]) != 22:
        raise AssertionError("publication-current map is not the required 22-claim superset")

    paper_text = ""
    for relative, expected in table["paper_sources"].items():
        path = ROOT / relative
        if _sha256(path) != expected:
            raise AssertionError(f"paper source hash mismatch: {relative}")
        paper_text += path.read_text()
    for entry in table["claims"]:
        if "MAXWELL" in entry["certificate_result_id"]:
            raise AssertionError("Maxwell certificate entered the main theorem")
        if entry["claim_id"] not in paper_text:
            raise AssertionError(f"claim id absent from paper sources: {entry['claim_id']}")
        certificate_path = ROOT / entry["certificate_path"]
        if _sha256(certificate_path) != entry["certificate_sha256"]:
            raise AssertionError(f"certificate digest mismatch: {entry['claim_id']}")
        certificate = json.loads(certificate_path.read_text())
        if certificate["result_id"] != entry["certificate_result_id"]:
            raise AssertionError(f"certificate result id mismatch: {entry['claim_id']}")
        if certificate["claim_boundary"] != entry["certificate_claim_boundary"]:
            raise AssertionError(f"certificate boundary mismatch: {entry['claim_id']}")
        for dotted in entry["required_true"]:
            if _lookup(certificate, dotted) is not True:
                raise AssertionError(f"required true field failed: {entry['claim_id']} {dotted}")
        for dotted in entry["required_false"]:
            if _lookup(certificate, dotted) is not False:
                raise AssertionError(f"required false field failed: {entry['claim_id']} {dotted}")
    for entry in table["independent_cross_checks"]:
        certificate_path = ROOT / entry["certificate_path"]
        if _sha256(certificate_path) != entry["certificate_sha256"]:
            raise AssertionError("independent cross-check digest mismatch")
        certificate = json.loads(certificate_path.read_text())
        if certificate["result_id"] != entry["certificate_result_id"]:
            raise AssertionError("independent cross-check result id mismatch")
        if certificate["claim_boundary"] != entry["certificate_claim_boundary"]:
            raise AssertionError("independent cross-check boundary mismatch")
        for dotted in entry["required_true"]:
            if _lookup(certificate, dotted) is not True:
                raise AssertionError(f"cross-check required true field failed: {dotted}")
        for dotted in entry["required_false"]:
            if _lookup(certificate, dotted) is not False:
                raise AssertionError(f"cross-check required false field failed: {dotted}")
    crosscheck_ids = [entry["certificate_result_id"] for entry in table["independent_cross_checks"]]
    if crosscheck_ids != [
        "BERGER_Q3_ACTION_SECTOR_CROSSCHECK",
        "BERGER_GENERATOR_CONJUGATION_AUDIT",
    ]:
        raise AssertionError("independent cross-check sequence drifted")
    expected_signoffs = [
        ("nonlinear_team", "PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF", "SIGNED_SCOPED_K_THEOREM"),
        ("quantum_team", "PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF", "SIGNED_OFF_CLASSICAL_K_ONLY_QUANTUM_BLOCKED"),
    ]
    if len(table["signoff_evidence"]) != 2:
        raise AssertionError("independent signoff evidence is incomplete")
    for entry, expected in zip(table["signoff_evidence"], expected_signoffs):
        observed = (entry["team"], entry["certificate_result_id"], entry["status"])
        if observed != expected:
            raise AssertionError(f"signoff identity or verdict mismatch: {observed}")
        certificate_path = ROOT / entry["certificate_path"]
        if _sha256(certificate_path) != entry["certificate_sha256"]:
            raise AssertionError(f"signoff digest mismatch: {entry['team']}")
        certificate = json.loads(certificate_path.read_text())
        if certificate["result_id"] != entry["certificate_result_id"]:
            raise AssertionError(f"signoff result id mismatch: {entry['team']}")
        if certificate["claim_boundary"] != entry["certificate_claim_boundary"]:
            raise AssertionError(f"signoff boundary mismatch: {entry['team']}")
        for dotted in entry["required_true"]:
            if _lookup(certificate, dotted) is not True:
                raise AssertionError(f"signoff required true field failed: {entry['team']} {dotted}")
        for dotted in entry["required_false"]:
            if _lookup(certificate, dotted) is not False:
                raise AssertionError(f"signoff forbidden promotion detected: {entry['team']} {dotted}")
    if table["required_signoffs"] != {
        "classical_team": "SIGNED_AND_FROZEN",
        "nonlinear_team": "SIGNED_K_GENERATOR_INTERPRETATION",
        "quantum_team": "SIGNED_OFF_CLASSICAL_K_ONLY_QUANTUM_BLOCKED",
        "einstein_team": "OPTIONAL_INTERNAL_REFEREE",
    }:
        raise AssertionError("authoritative signoff ledger drifted")
    if table["next_gate"] != "POST_FREEZE_OBSERVER_84_ROW_BACKGROUND_SUPPORT":
        raise AssertionError("post-freeze observer handoff drifted")
    if table["main_theorem_exclusions"][:2] != [
        "Maxwell signal or redshift results",
        "observer-apparatus or 84-row results",
    ]:
        raise AssertionError("main-theorem downstream exclusions drifted")
    print("PAPER_09_BERGER_CLAIM_TABLE independent audit: PASS")
    print("claims=10 cross_checks=2 signoffs=2 theorem_frozen=true maxwell_excluded hashes_and_boundaries=exact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
