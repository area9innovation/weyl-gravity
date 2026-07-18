#!/usr/bin/env python3
"""Build the classical preflight for the Einstein/Weyl relative functor.

The committed noncyclic three-form triangle supplies the off-shell mapping
cofiber, product-equivariance and endpoint maps.  This producer imports those
facts while leaving the actual observable pullback fail-closed.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
STANDARD = ROOT / "d_quotient_programme/contributions/einstein-maxwell-weyl-standard-harmonic-inclusion.json"
BERGER = ROOT / "d_quotient_programme/contributions/einstein-berger-incidence.json"
QUANTUM = ROOT / "quantum-weyl/relative/certificates/QUANTUM_RELATIVE_EINSTEIN_WEYL_QME_DEFECT_READINESS.json"
PARTIAL_TRIANGLE = ROOT / "d_quotient_programme/contributions/einstein-weyl-relative-linear-triangle-preflight.json"
CERTIFICATE = ROOT / "d_quotient_classical/certificates/RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/relative-residual-observable-functor-preflight-v1.md"
TRIANGLE_CANDIDATES = (
    ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1.json",
    ROOT / "bridge/certificates/einstein_weyl_relative_linear_triangle_v1.json",
)
TRIANGLE_FLAGS = (
    "OFF_SHELL_CHAIN_MAP_ALL_BV_ROWS",
    "SUPPORT_LOCAL_MAPPING_COFIBER",
    "GLOBAL_ENDPOINTS_INCLUDED",
    "THREE_ACTION_DERIVED_FORMS_EXPORTED",
    "GENERIC_STANDARD_PAIRING_CYCLIC_OBSTRUCTION_RESPECTED",
    "H_PRODUCT_EQUIVARIANT",
    "INDEPENDENT_VERIFIER_PASS",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def committed_bytes(commit: str, path: Path) -> bytes:
    relative = path.relative_to(ROOT)
    return subprocess.check_output(["git", "show", f"{commit}:./{relative}"], cwd=ROOT)


def dependency(path: Path, artifact_id: str) -> dict[str, str]:
    relative = str(path.relative_to(ROOT))
    commit = git("log", "-1", "--format=%H", "--", relative)
    if not commit:
        raise AssertionError(f"dependency is not committed: {relative}")
    committed_hash = hashlib.sha256(committed_bytes(commit, path)).hexdigest()
    if sha256(path) != committed_hash:
        raise AssertionError(f"dependency has uncommitted drift: {relative}")
    return {
        "artifact_id": artifact_id,
        "path": relative,
        "commit": commit,
        "sha256": committed_hash,
    }


def triangle_import() -> tuple[dict | None, Path | None]:
    present = [path for path in TRIANGLE_CANDIDATES if path.exists()]
    if len(present) > 1:
        raise AssertionError("multiple authoritative triangle candidates exist")
    if not present:
        return None, None
    path = present[0]
    payload = load(path)
    if payload.get("result_id") != "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1":
        raise AssertionError("triangle candidate has the wrong result_id")
    if payload.get("claim_status") not in {
        "CERTIFIED",
        "THEOREM_FROZEN",
        "CERTIFIED_OFF_SHELL_LINEAR_TRIANGLE",
    }:
        raise AssertionError("triangle candidate is not certified")
    flags = payload.get("acceptance_flags", payload.get("flags", {}))
    missing = [key for key in TRIANGLE_FLAGS if flags.get(key) is not True]
    if missing:
        raise AssertionError("triangle candidate misses acceptance flags: " + ", ".join(missing))
    return payload, path


def build() -> dict:
    standard = load(STANDARD)
    berger = load(BERGER)
    quantum = load(QUANTUM)
    partial_triangle = load(PARTIAL_TRIANGLE)
    if standard["verdict"] != "G4_COMPLETE_STANDARD_HARMONIC_PULLBACK_NONDEGENERATE_BEFORE_FINAL_QUOTIENT":
        raise AssertionError("standard harmonic inclusion verdict drifted")
    if standard["generator_id"] != "H_product":
        raise AssertionError("relative common-background generator drifted")
    if berger["verdict"] != "EINSTEIN_TANGENT_NOT_APPLICABLE_AT_THIS_BACKGROUND":
        raise AssertionError("Berger incidence verdict drifted")
    if quantum["classical_import_gate"]["status"] != "NOT_SATISFIED":
        raise AssertionError("quantum import gate unexpectedly promoted")
    if quantum["shared_relative_row"]["map_iota"] != "PRINCIPAL_GENERIC_AXIAL_AND_GENERIC_POLAR_UNGAUGED_OFFSHELL_PREFLIGHT_IMPORTED_GLOBAL_V1_OPEN":
        raise AssertionError("quantum relative map disposition drifted")
    if partial_triangle["verdict"] != "G2_PRINCIPAL_AND_GENERIC_AXIAL_OFFSHELL_RELATIVE_TRIANGLE_PREFLIGHT":
        raise AssertionError("partial relative-triangle preflight verdict drifted")
    if "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1" not in partial_triangle["not_established"]:
        raise AssertionError("partial preflight silently claims the full triangle")
    triangle, triangle_path = triangle_import()
    imported = triangle is not None

    refs = {
        "standard_harmonic_inclusion": dependency(
            STANDARD, "compact_einstein_maxwell_weyl_standard_harmonic_inclusion"
        ),
        "berger_same_base_no_go": dependency(
            BERGER, "compact_positive_berger_clock_einstein_incidence"
        ),
        "quantum_relative_readiness": dependency(
            QUANTUM, "QUANTUM_RELATIVE_EINSTEIN_WEYL_QME_DEFECT_READINESS"
        ),
        "partial_offshell_triangle_preflight": dependency(
            PARTIAL_TRIANGLE,
            "compact_einstein_maxwell_weyl_relative_linear_triangle_preflight",
        ),
    }
    if imported:
        refs["off_shell_relative_triangle"] = dependency(
            triangle_path, "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1"
        )

    payload = {
        "schema": "pure-weyl-relative-residual-observable-functor-preflight-v1",
        "result_id": "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1",
        "result_state": (
            "OFFSHELL_TRIANGLE_EQUIVARIANT_COFIBER_IMPORTED_OBSERVABLE_PULLBACK_OPEN"
            if imported
            else "PARTIAL_OFFSHELL_PREFLIGHT_IMPORTED_FULL_TRIANGLE_MISSING"
        ),
        "setting": {
            "theory_pair": "Einstein-Maxwell_to_Weyl-Maxwell",
            "background": "compact_Einstein-Maxwell_product",
            "generator": "H_product",
            "phase_space": "complete_standard_harmonic_tangent_before_final_residual_quotient",
        },
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": refs,
        "shared_relative_row": {
            "map_iota": "IMPORTED_OFFSHELL_TRIANGLE" if imported else "PARTIAL_OFFSHELL_GENERIC_AXIAL_PREFLIGHT",
            "cofiber": "IMPORTED_MAPPING_COFIBER" if imported else "PARTIAL_GENERIC_AXIAL_COFIBER_FULL_GLOBAL_BLOCKED",
            "relative_pairing": "NONCYCLIC_THREE_ACTION_FORMS_IMPORTED" if imported else "CLASSICAL_REDUCED_MODE_PULLBACK_ONLY",
            "O2": "PARTIAL_FIXTURES_ONLY",
            "residual_action": "IMPORTED_H_PRODUCT_EQUIVARIANCE_AND_ENDPOINT_MAPS" if imported else "BLOCKED_OFFSHELL_EQUIVARIANCE_MISSING",
            "observable_map": "BLOCKED_OFFSHELL_PULLBACK_MISSING",
            "quantum_lift": "NOT_APPLICABLE_TO_CLASSICAL_PREFLIGHT",
        },
        "required_import": {
            "result_id": "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1",
            "required_components": [
                "off_shell_chain_map_on_fields_ghosts_antifields_equations_and_identities",
                "support_local_mapping_cofiber_or_triangle",
                "global_zero_mode_and_residual_endpoint_map",
                "three_action_derived_forms_with_standard_cyclic_obstruction",
                "H_product_equivariance",
                "content_addressed_certificate_and_independent_verifier",
            ],
            "acceptance_flags": list(TRIANGLE_FLAGS),
            "candidate_paths": [str(path.relative_to(ROOT)) for path in TRIANGLE_CANDIDATES],
            "status": "IMPORTED" if imported else "MISSING",
        },
        "background_scope": {
            "common_product_background": "APPLICABLE",
            "berger_clock_background": "NOT_APPLICABLE_NO_SAME_BASE_EINSTEIN_TANGENT",
        },
        "flags": {
            "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1": True,
            "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1": False,
            "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_IMPORTED": imported,
            "OBSERVABLE_PULLBACK_CONSTRUCTED": False,
            "RESIDUAL_EQUIVARIANCE_CERTIFIED": imported,
            "COFIBER_COMPATIBILITY_CERTIFIED": imported,
            "BERGER_SAME_BASE_RELATIVE_MAP_APPLICABLE": False,
        },
        "next_gate": (
            "CONSTRUCT_OBSERVABLE_PULLBACK_ON_IMPORTED_NONCYCLIC_TRIANGLE"
            if imported
            else "IMPORT_EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1_BY_HASH"
        ),
        "claim_boundary": (
            "The committed all-row noncyclic triangle, support-local mapping cofiber, H_product equivariance, fixed-N=2 endpoint maps and three distinct action forms are imported by content hash. "
            "The standard-pairing cyclic route remains obstructed. No observable pullback, causal Green relative functor, complete q2/q3 morphism or quantum lift is claimed. "
            "The Berger clock fixture is a separate Weyl-matter rail and is not a common Einstein/Weyl background."
            if imported
            else "The exact on-shell standard-harmonic inclusion, reduced-mode pairing, and principal/generic-axial off-shell preflight are imported by commit and content hash. The full triangle, residual-equivariant observable pullback and quantum lift remain absent. The Berger clock fixture is a separate Weyl-matter rail."
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
    imported = payload["required_import"]["status"] == "IMPORTED"
    if payload["flags"]["EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_IMPORTED"] is not imported:
        raise AssertionError("triangle status and flag disagree")
    flags = payload["flags"]
    if flags["RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1"] is not True:
        raise AssertionError("preflight not certified")
    allowed_true = {"RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1"}
    if imported:
        allowed_true.update({
            "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_IMPORTED",
            "RESIDUAL_EQUIVARIANCE_CERTIFIED",
            "COFIBER_COMPATIBILITY_CERTIFIED",
        })
    for key, value in flags.items():
        if key not in allowed_true and value is not False:
            raise AssertionError(f"forbidden relative promotion: {key}")


def report_text(payload: dict) -> str:
    return f"""# Relative residual and observable functor preflight

Result: `{payload['result_state']}`.

The compact Einstein-Maxwell product triangle import status is
`{payload['required_import']['status']}`.  When imported, the support-local
cofiber, product-equivariance, endpoint maps and three noncyclic action forms
are certified.  The observable pullback remains a separate fail-closed
construction.

The positive Berger clock is not a fallback common background: the certified
incidence result excludes a same-base Einstein tangent there.
"""


def guards(payload: dict) -> None:
    for key in (
        "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1",
        "OBSERVABLE_PULLBACK_CONSTRUCTED",
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
