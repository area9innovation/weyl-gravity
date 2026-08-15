#!/usr/bin/env python3
"""Independent checks for the q2-only lambda-squared source obstruction."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

import cylinder_polarized_bach_evaluator as point
from local_q1_q2_receiver import apply_primary_q2, apply_q1, field_fixture


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def section_digest(value: dict[str, Any]) -> str:
    return digest({key: item for key, item in value.items() if key != "sha256"})


def independent_witness() -> tuple[bool, Fraction, int, int]:
    background = point.flat_background(7)
    parameter = field_fixture("c", 1, 7)
    field = apply_q1("q1_h_c", parameter, background, 6)
    linear = apply_q1("q1_hstar_h", field, background, 1)
    quadratic = apply_primary_q2("q2_hstar_hh", field, field, 1, background=background)
    diff = apply_primary_q2("q2_cstar_hhstar", field, quadratic, 0, background=background)
    weyl = apply_primary_q2("q2_omegastar_hhstar", field, quadratic, 0, background=background)
    return (
        not any(item.terms for item in linear.values()),
        weyl.constant_term,
        sum(len(item.terms) for item in diff.values()),
        len(weyl.terms),
    )


def check(value: dict[str, Any] | None = None) -> list[str]:
    if value is None:
        value = json.loads(RESULT.read_text())
    errors: list[str] = []
    if value.get("result_id") != "STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1":
        return ["result identity drift"]
    for item in value.get("provenance", {}).get("inputs", []) + value.get("provenance", {}).get("implementation", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            errors.append("dependency hash drift: " + item.get("path", ""))

    literature = value.get("literature_context", {})
    if literature.get("artifact", {}).get("sha256") != "91006d01123242f2e5cb8c673cde0263caf2e3de6110f44e928167203240d893":
        errors.append("L-infinity literature pin drift")
    if "q1 q3" not in literature.get("imported_statement", "") or "3 q2" not in literature.get("imported_statement", ""):
        errors.append("arity-three literature boundary drift")

    closed, jacobiator, diff_terms, weyl_terms = independent_witness()
    fixture = value.get("exact_q1_closed_fixture", {})
    if not closed or fixture.get("field_status") != "q1(x)=0 exactly" or fixture.get("linear_equation_terms") != []:
        errors.append("q1-closed fixture drift")
    if jacobiator != Fraction(75760, 27) or fixture.get("jacobiator_weyl_identity_value") != "75760/27" or diff_terms or weyl_terms != 1:
        errors.append("exact q2 Jacobiator witness drift")

    derivation = value.get("source_closure_derivation", {})
    if derivation.get("structural_derivation_defects") != 0 or derivation.get("typed_noether_form") != "N S2[q3=0]=(1/2)J2(x)":
        errors.append("source-closure derivation drift")
    if Fraction(1, 2) * jacobiator != Fraction(37880, 27):
        errors.append("source defect arithmetic drift")
    if -3 * jacobiator != Fraction(-75760, 9):
        errors.append("q3 target arithmetic drift")
    if Fraction(1, 2) * jacobiator + Fraction(1, 6) * (-3 * jacobiator) != 0:
        errors.append("arity-three cancellation arithmetic drift")

    disposition = value.get("quadratic_truncation_disposition", {})
    if disposition.get("quadratic_only_lambda_squared_source_closed") is not False or disposition.get("q3_required_for_this_candidate") is not True:
        errors.append("quadratic truncation disposition drift")
    if disposition.get("witness_source_closure_defect") != "37880/27" or disposition.get("required_q3_q1_image_on_witness") != "-75760/9":
        errors.append("recorded witness target drift")
    if disposition.get("not_an_obstruction_to_full_weyl_theory") is not True:
        errors.append("full-theory boundary drift")

    contract = value.get("authoritative_q3_export_contract", {})
    if contract.get("authoritative_export_present") is not False or contract.get("minimum_witness_target") != "q1(q3(x,x,x))_omega_star=-75760/9 on FLAT_PURE_DIFF_GAUGE_SEED_1":
        errors.append("authoritative q3 export contract drift")
    if len(contract.get("required_objects", [])) != 6 or len(contract.get("acceptance_checks", [])) != 5:
        errors.append("q3 contract completeness drift")

    authority = value.get("authority_boundary", {})
    required_authority = {
        "candidate_q2_only": True,
        "q1_closed_witness": True,
        "quadratic_truncation_obstruction_certified": True,
        "authoritative_q2_imported": False,
        "authoritative_q3_imported": False,
        "full_weyl_lambda_squared_source_closure_decided": False,
        "analytic_green_action_needed_for_obstruction": False,
        "classical_import_gate_a_status": "FAIL_CLOSED",
    }
    if authority != {**required_authority, "sha256": authority.get("sha256")}:
        errors.append("authority boundary drift")

    flags = value.get("claim_flags", {})
    for key in ("STRICT_386_Q2_ONLY_LAMBDA2_SOURCE_OBSTRUCTED", "STRICT_386_Q2_JACOBIATOR_NONZERO_WITNESS_CERTIFIED", "STRICT_386_AUTHORITATIVE_Q3_REQUIRED"):
        if flags.get(key) is not True:
            errors.append("positive flag missing: " + key)
    for key in ("STRICT_386_AUTHORITATIVE_Q3_IMPORTED", "STRICT_386_FULL_WEYL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED", "STRICT_386_AUTHORITATIVE_FORMAL_MOLLER_MAP_CERTIFIED", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"):
        if flags.get(key) is not False:
            errors.append("firewall flag missing: " + key)

    hashes = value.get("canonical_hashes", {})
    fields = {
        "literature_context_sha256": "literature_context",
        "fixture_sha256": "exact_q1_closed_fixture",
        "source_closure_derivation_sha256": "source_closure_derivation",
        "quadratic_truncation_disposition_sha256": "quadratic_truncation_disposition",
        "authoritative_q3_export_contract_sha256": "authoritative_q3_export_contract",
        "foundational_strength_sha256": "foundational_strength",
        "authority_boundary_sha256": "authority_boundary",
    }
    for key, field in fields.items():
        if hashes.get(key) != section_digest(value.get(field, {})):
            errors.append("canonical hash drift: " + key)
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    if not errors:
        print("  - exact q1-closed fixture and nonzero q2 Jacobiator replay")
        print("  - q2-only lambda-squared source closure rejected")
        print("  - authoritative q3 cancellation target fixed without promoting full Weyl closure")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
