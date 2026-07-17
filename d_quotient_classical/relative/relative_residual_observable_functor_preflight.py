#!/usr/bin/env python3
"""Build the classical preflight for the Einstein/Weyl relative functor.

The available common-background result is an on-shell, reduced-mode inclusion.
It is useful input, but it is not the off-shell BV triangle needed to define a
mapping cofiber, residual action, or observable pullback.  This producer records
that distinction exactly and refuses every downstream promotion.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STANDARD = ROOT / "d_quotient_programme/contributions/einstein-maxwell-weyl-standard-harmonic-inclusion.json"
BERGER = ROOT / "d_quotient_programme/contributions/einstein-berger-incidence.json"
QUANTUM = ROOT / "quantum-weyl/relative/certificates/QUANTUM_RELATIVE_EINSTEIN_WEYL_QME_DEFECT_READINESS.json"
CERTIFICATE = ROOT / "d_quotient_classical/certificates/RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/relative-residual-observable-functor-preflight-v1.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dependency(path: Path, artifact_id: str) -> dict[str, str]:
    return {
        "artifact_id": artifact_id,
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256(path),
    }


def build() -> dict:
    standard = load(STANDARD)
    berger = load(BERGER)
    quantum = load(QUANTUM)
    if standard["verdict"] != "G4_COMPLETE_STANDARD_HARMONIC_PULLBACK_NONDEGENERATE_BEFORE_FINAL_QUOTIENT":
        raise AssertionError("standard harmonic inclusion verdict drifted")
    if standard["generator_id"] != "H_product":
        raise AssertionError("relative common-background generator drifted")
    if berger["verdict"] != "EINSTEIN_TANGENT_NOT_APPLICABLE_AT_THIS_BACKGROUND":
        raise AssertionError("Berger incidence verdict drifted")
    if quantum["classical_import_gate"]["status"] != "NOT_SATISFIED":
        raise AssertionError("quantum import gate unexpectedly promoted")
    if quantum["shared_relative_row"]["map_iota"] != "ONSHELL_MAP_ONLY_IMPORTED_BY_HASH":
        raise AssertionError("quantum relative map disposition drifted")

    payload = {
        "schema": "pure-weyl-relative-residual-observable-functor-preflight-v1",
        "result_id": "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1",
        "result_state": "DEPENDENCY_CONTRACT_READY_OFFSHELL_TRIANGLE_MISSING",
        "setting": {
            "theory_pair": "Einstein-Maxwell_to_Weyl-Maxwell",
            "background": "compact_Einstein-Maxwell_product",
            "generator": "H_product",
            "phase_space": "complete_standard_harmonic_tangent_before_final_residual_quotient",
        },
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            "standard_harmonic_inclusion": dependency(
                STANDARD, "compact_einstein_maxwell_weyl_standard_harmonic_inclusion"
            ),
            "berger_same_base_no_go": dependency(
                BERGER, "compact_positive_berger_clock_einstein_incidence"
            ),
            "quantum_relative_readiness": dependency(
                QUANTUM, "QUANTUM_RELATIVE_EINSTEIN_WEYL_QME_DEFECT_READINESS"
            ),
        },
        "shared_relative_row": {
            "map_iota": "ONSHELL_MAP_ONLY",
            "cofiber": "BLOCKED_OFFSHELL_TRIANGLE_MISSING",
            "relative_pairing": "CLASSICAL_REDUCED_MODE_PULLBACK_ONLY",
            "O2": "PARTIAL_FIXTURES_ONLY",
            "residual_action": "BLOCKED_OFFSHELL_EQUIVARIANCE_MISSING",
            "observable_map": "BLOCKED_OFFSHELL_PULLBACK_MISSING",
            "quantum_lift": "NOT_APPLICABLE_TO_CLASSICAL_PREFLIGHT",
        },
        "required_import": {
            "result_id": "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1",
            "required_components": [
                "off_shell_chain_map_on_fields_ghosts_antifields_equations_and_identities",
                "support_local_mapping_cofiber_or_triangle",
                "global_zero_mode_and_residual_endpoint_map",
                "pairing_or_current_compatibility",
                "H_product_equivariance",
                "content_addressed_certificate_and_independent_verifier",
            ],
            "status": "MISSING",
        },
        "background_scope": {
            "common_product_background": "APPLICABLE",
            "berger_clock_background": "NOT_APPLICABLE_NO_SAME_BASE_EINSTEIN_TANGENT",
        },
        "flags": {
            "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1": True,
            "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1": False,
            "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_IMPORTED": False,
            "OBSERVABLE_PULLBACK_CONSTRUCTED": False,
            "RESIDUAL_EQUIVARIANCE_CERTIFIED": False,
            "COFIBER_COMPATIBILITY_CERTIFIED": False,
            "BERGER_SAME_BASE_RELATIVE_MAP_APPLICABLE": False,
        },
        "next_gate": "IMPORT_EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1_BY_HASH",
        "claim_boundary": (
            "The exact on-shell standard-harmonic inclusion and reduced-mode pairing are imported by content hash. "
            "They do not define an off-shell BV chain map, mapping cofiber, residual-equivariant observable pullback, "
            "or relative quantum lift. The Berger clock fixture is a separate Weyl-matter rail and is not a common "
            "Einstein/Weyl background."
        ),
    }
    verify(payload)
    return payload


def verify(payload: dict) -> None:
    if payload["result_id"] != "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1":
        raise AssertionError("result id drifted")
    for item in payload["dependency_refs"].values():
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise AssertionError(f"dependency hash drifted: {item['path']}")
    if payload["required_import"]["status"] != "MISSING":
        raise AssertionError("missing triangle was silently promoted")
    flags = payload["flags"]
    if flags["RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1"] is not True:
        raise AssertionError("preflight not certified")
    for key, value in flags.items():
        if key != "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1" and value is not False:
            raise AssertionError(f"forbidden relative promotion: {key}")


def report_text(payload: dict) -> str:
    return f"""# Relative residual and observable functor preflight

Result: `{payload['result_state']}`.

The compact Einstein-Maxwell product supplies an exact on-shell harmonic
inclusion and a nondegenerate reduced-mode pullback pairing.  It does not yet
supply the off-shell BV triangle needed for a mapping cofiber, residual action,
or observable pullback.  Those targets remain fail-closed until
`EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1` is imported by content hash.

The positive Berger clock is not a fallback common background: the certified
incidence result excludes a same-base Einstein tangent there.
"""


def guards(payload: dict) -> None:
    for key in (
        "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1",
        "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_IMPORTED",
        "OBSERVABLE_PULLBACK_CONSTRUCTED",
        "RESIDUAL_EQUIVARIANCE_CERTIFIED",
        "COFIBER_COMPATIBILITY_CERTIFIED",
        "BERGER_SAME_BASE_RELATIVE_MAP_APPLICABLE",
    ):
        mutant = deepcopy(payload)
        mutant["flags"][key] = True
        try:
            verify(mutant)
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard failed: {key}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.write:
        CERTIFICATE.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report_text(payload), encoding="utf-8")
    if args.check:
        if load(CERTIFICATE) != payload:
            raise AssertionError("certificate drifted")
        if REPORT.read_text(encoding="utf-8") != report_text(payload):
            raise AssertionError("report drifted")
    if args.guards:
        guards(payload)
    print("RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
