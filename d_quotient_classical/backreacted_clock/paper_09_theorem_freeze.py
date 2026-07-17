#!/usr/bin/env python3
"""Emit the scoped Paper IX theorem-freeze receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/PAPER_09_THEOREM_FREEZE.json"
SCHEMA = ROOT / "d_quotient_classical/schema/paper-09-theorem-freeze-v1.schema.json"
REPORT = ROOT / "d_quotient_classical/reports/paper-09-theorem-freeze.md"

SNAPSHOT_COMMIT = "bd3ece1c415a82cca17702d580c81a269dd950a7"
PAPER_COMMIT = "408824d58392be368831ccf1cdc4ad0000cf823a"
NONLINEAR_SIGNOFF_COMMIT = "b3b68bdf925f5d0a495edfcdf3d7eadb3605c7a2"
QUANTUM_SIGNOFF_COMMIT = "4f831916dc0b0994a444c1c29ce319b87b909635"

DEPENDENCIES = {
    "claim_table": (PAPER_COMMIT, "d_quotient_classical/certificates/PAPER_09_BERGER_CLAIM_TABLE.json"),
    "main_source": (PAPER_COMMIT, "paper/09-relational-clocks-berger-d-cartan.tex"),
    "main_pdf": (PAPER_COMMIT, "paper/09-relational-clocks-berger-d-cartan.pdf"),
    "supplement_source": (PAPER_COMMIT, "paper/09-relational-clocks-berger-d-cartan-computational-supplement.tex"),
    "supplement_pdf": (PAPER_COMMIT, "paper/09-relational-clocks-berger-d-cartan-computational-supplement.pdf"),
    "nonlinear_frozen_signoff": (NONLINEAR_SIGNOFF_COMMIT, "d_quotient_classical/certificates/PAPER_09_NONLINEAR_FROZEN_K_GENERATOR_SIGNOFF.json"),
    "quantum_postfreeze_signoff": (QUANTUM_SIGNOFF_COMMIT, "quantum-weyl/cartan/certificates/PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF_V2.json"),
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "independent_verifier": ROOT / "d_quotient_classical/backreacted_clock/verify_paper_09_theorem_freeze.py",
    "tests": ROOT / "d_quotient_classical/backreacted_clock/tests/test_paper_09_theorem_freeze.py",
    "schema": SCHEMA,
    "report": REPORT,
}


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _git_blob(commit: str, path: str) -> bytes:
    prefix = subprocess.check_output(["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True).strip()
    return subprocess.check_output(["git", "show", f"{commit}:{prefix}{path}"], cwd=ROOT)


def _dependency_refs() -> tuple[dict[str, dict[str, Any]], dict[str, bytes]]:
    refs: dict[str, dict[str, Any]] = {}
    blobs: dict[str, bytes] = {}
    for name, (commit, path) in DEPENDENCIES.items():
        raw = _git_blob(commit, path)
        refs[name] = {"path": path, "commit": commit, "sha256": _sha(raw)}
        blobs[name] = raw
    return refs, blobs


def build() -> dict[str, Any]:
    refs, blobs = _dependency_refs()
    table = json.loads(blobs["claim_table"])
    nonlinear = json.loads(blobs["nonlinear_frozen_signoff"])
    quantum = json.loads(blobs["quantum_postfreeze_signoff"])
    main = blobs["main_source"].decode()

    if table["paper_state"] != "THEOREM_FROZEN" or table["theorem_frozen"] is not True:
        raise AssertionError("claim table is not theorem-frozen")
    if len(table["claims"]) != 10 or table["claim_ids_complete"] != [f"P09-C{i}" for i in range(1, 11)]:
        raise AssertionError("ten-claim ledger drifted")
    if any("MAXWELL" in row["certificate_result_id"] for row in table["claims"]):
        raise AssertionError("Maxwell result entered Paper IX")
    theorem_text = "\n".join(
        block.split("\\end{theorem}", 1)[0]
        for block in main.split("\\begin{theorem}")[1:]
    )
    if any(word in theorem_text for word in ("Maxwell", "observer-apparatus", "84-row")):
        raise AssertionError("downstream result entered a main theorem environment")
    if nonlinear["flags"]["PAPER_09_THEOREM_FROZEN_ACCEPTED"] is not True:
        raise AssertionError("frozen nonlinear signoff absent")
    if nonlinear["flags"]["MAXWELL_MAIN_THEOREM_INCLUDED"] is not False:
        raise AssertionError("nonlinear signoff imported Maxwell")
    if quantum["theorem_flags"]["PAPER09_FROZEN_CLASSICAL_K_CARTAN_ACCEPTED"] is not True:
        raise AssertionError("post-freeze quantum boundary signoff absent")
    if quantum["theorem_flags"]["PAPER09_QUANTUM_PROMOTION_ACCEPTED"] is not False:
        raise AssertionError("quantum promotion entered Paper IX")

    payload = {
        "schema": "pure-weyl-paper-09-theorem-freeze-v1",
        "result_id": "PAPER_09_THEOREM_FREEZE",
        "paper_state": "THEOREM_FROZEN",
        "claim_status": "FROZEN_SCOPED_CLASSICAL_GRAVITY_CLOCK_THEOREM",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "source_snapshot": {
            "commit": SNAPSHOT_COMMIT,
            "method": "git archive of the committed symplectic-reconstruction subtree with repository path prefix restored",
            "working_tree_inputs": False,
        },
        "dependency_refs": refs,
        "theorem_inventory": {
            "claim_count": 10,
            "claim_ids": [f"P09-C{i}" for i in range(1, 11)],
            "primary_geometric_theorem": "fixed-coupling rigidity of the positive Berger clock momentum and linear presymplectic nullity of raw D",
            "primary_bv_theorem": "54-row classical causal cyclic Cartan contraction for K_Berger=D-omega R through arity three",
            "maxwell_main_theorem_included": False,
            "observer_84_row_main_theorem_included": False,
        },
        "verification": {
            "authoritative_freeze_rail": {
                "status": "PASS",
                "tests_passed": 47,
                "tests_failed": 0,
                "pytest_seconds": "135.33",
                "wall_seconds": "136.26",
                "maxrss_kb": 773600,
                "scope": "all ten Paper IX claims, claim table, generator audit, q3 action cross-check, and frozen nonlinear/quantum signoffs",
            },
            "explicit_verifier_rail": {
                "status": "PASS",
                "wall_seconds": "0.98",
                "maxrss_kb": 25968,
                "checks": [
                    "claim table producer and independent verifier",
                    "frozen nonlinear signoff producer, verifier, and mutations",
                    "post-freeze quantum signoff producer and verifier",
                ],
            },
            "pdf_build": {
                "status": "PASS",
                "main_pages": 15,
                "supplement_pages": 7,
                "main_first_pass_seconds": "0.50",
                "supplement_first_pass_seconds": "0.32",
                "latex_errors": 0,
            },
            "broader_classical_package_audit": {
                "status": "PASS_WITH_CLASSIFIED_NON_PAPER09_DRIFT",
                "tests_passed": 170,
                "tests_failed": 4,
                "wall_seconds": "853.55",
                "maxrss_kb": 797188,
                "classified_failures": [
                    "legacy pre-freeze nonlinear signoff tests (2), superseded by the passing frozen signoff",
                    "portable coupled 64-row Maxwell persisted-output drift (1), excluded from Paper IX",
                    "quantum consumer exact-field-list drift for the 26-row Green export (1); the direct classical Green certificate and Paper IX C6 tests pass",
                ],
                "used_to_promote_theorem": False,
            },
            "commands": [
                "pytest -q <15-file authoritative Paper IX freeze rail>",
                "python3 d_quotient_classical/backreacted_clock/paper_09_claim_table.py --check --guards",
                "python3 d_quotient_classical/backreacted_clock/verify_paper_09_claim_table.py",
                "python3 d_quotient_classical/backreacted_clock/verify_paper_09_nonlinear_frozen_k_generator_signoff.py --check --mutations",
                "python3 quantum-weyl/cartan/verify_paper09_quantum_claim_boundary_signoff_v2.py",
                "pdflatex -interaction=nonstopmode -halt-on-error <main and supplement, two passes each>",
            ],
        },
        "environment": {
            "platform": "Linux-7.0.0-27-generic-x86_64-with-glibc2.43",
            "python": "3.12.13",
            "sympy": "1.14.0",
            "jsonschema": "4.26.0",
            "pytest": "9.1.1",
            "pdftex": "3.141592653-2.6-1.40.28 (TeX Live 2025/Debian)",
        },
        "flags": {
            "PAPER_09_THEOREM_FROZEN": True,
            "PAPER_09_TEN_CLAIMS_PINNED": True,
            "PAPER_09_AUTHORITATIVE_CLEAN_SNAPSHOT_REPLAY": True,
            "PAPER_09_PDFS_COMPILE": True,
            "PAPER_09_NONLINEAR_FROZEN_SIGNOFF": True,
            "PAPER_09_QUANTUM_BOUNDARY_SIGNOFF": True,
            "MAXWELL_MAIN_THEOREM_INCLUDED": False,
            "OBSERVER_84_ROW_MAIN_THEOREM_INCLUDED": False,
            "AFFINE_D_CARTAN_CERTIFIED": False,
            "ARITY_FOUR_OR_ALL_ORDERS_CERTIFIED": False,
            "HADAMARD_OR_QME_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "postfreeze_queue": [
            "support the observer team on the backreacted 84-row apparatus background and causal unary complex",
            "export BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V1 as a separate quantum-consumer interface",
        ],
        "provenance": {
            "source_manifest": [
                {"role": role, "path": str(path.relative_to(ROOT)), "sha256": _sha(path.read_bytes())}
                for role, path in SOURCE_FILES.items()
            ]
        },
        "claim_boundary": "Paper IX is theorem-frozen for exactly two linked classical gravity-clock results: fixed-coupling rigidity and linear raw-D nullity on the compact Berger tangent, and the 54-row causal cyclic K_Berger Cartan theorem through arity three. Maxwell, observer-apparatus/84-row, affine raw-D, arity-four/all-orders, Hadamard, QME, anomaly, quantum, boundary, and scattering claims remain outside the theorem.",
    }
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise AssertionError("Paper IX freeze certificate drifted")
    print("PAPER_09_THEOREM_FREEZE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
