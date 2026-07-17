#!/usr/bin/env python3
"""Independent verifier for the frozen Paper IX nonlinear re-signoff."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/PAPER_09_NONLINEAR_FROZEN_K_GENERATOR_SIGNOFF.json"
SCHEMA = ROOT / "d_quotient_classical/schema/paper-09-nonlinear-frozen-k-generator-signoff-v1.schema.json"


class VerificationError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise VerificationError(f"not an object: {path}")
    return value


def _require(value: bool, message: str) -> None:
    if not value:
        raise VerificationError(message)


def _git_blob(commit: str, path: str) -> bytes:
    prefix = subprocess.run(["git", "rev-parse", "--show-prefix"], cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE).stdout.strip()
    result = subprocess.run(["git", "show", f"{commit}:{prefix}{path}"], cwd=ROOT, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise VerificationError(f"missing pinned blob: {commit}:{path}")
    return result.stdout


def verify_payload(payload: dict[str, Any], *, files: bool = True) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(payload))
    if errors:
        raise VerificationError(f"schema failure: {errors[0].message}")
    if not files:
        return

    sources: dict[str, dict[str, Any]] = {}
    for key, evidence in payload["source_manifest"].items():
        path = ROOT / evidence["path"]
        _require(path.is_file(), f"missing source: {key}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        _require(digest == evidence["sha256"], f"worktree hash mismatch: {key}")
        _require(hashlib.sha256(_git_blob(evidence["commit"], evidence["path"])).hexdigest() == digest, f"Git hash mismatch: {key}")
        if "result_id" in evidence:
            source = _load(path)
            _require(source.get("result_id") == evidence["result_id"], f"result ID mismatch: {key}")
            sources[key] = source

    table = sources["frozen_claim_table"]
    prior = sources["prefreeze_nonlinear_signoff"]
    audit = sources["generator_audit"]
    _require(table.get("paper_state") == "THEOREM_FROZEN", "claim table is not theorem-frozen")
    _require(table.get("theorem_frozen") is True, "claim table freeze flag is false")
    expected_signoffs = {
        "classical_team": "SIGNED_AND_FROZEN",
        "einstein_team": "OPTIONAL_INTERNAL_REFEREE",
        "nonlinear_team": "SIGNED_K_GENERATOR_INTERPRETATION",
        "quantum_team": "SIGNED_OFF_CLASSICAL_K_ONLY_QUANTUM_BLOCKED",
    }
    _require(table.get("required_signoffs") == expected_signoffs, "frozen signoff set changed")
    _require(table.get("claim_ids_complete") == [f"P09-C{i}" for i in range(1, 11)], "ten-claim ledger changed")
    claims = {entry["claim_id"]: entry["claim"] for entry in table.get("claims", [])}
    for claim_id in ("P09-C6", "P09-C7", "P09-C8", "P09-C9", "P09-C10"):
        _require("K" in claims.get(claim_id, ""), f"{claim_id} is not K-scoped")
    exclusions = set(table.get("main_theorem_exclusions", []))
    _require("Maxwell signal or redshift results" in exclusions, "Maxwell entered the frozen theorem")
    _require("observer-apparatus or 84-row results" in exclusions, "84-row observer entered the frozen theorem")
    _require("affine raw-D Cartan" in exclusions, "affine raw D entered the frozen theorem")
    _require("quantum or Hadamard results" in exclusions, "quantum/Hadamard entered frozen theorem")

    prior_flags = prior.get("flags", {})
    _require(prior_flags.get("K_BERGER_CARTAN_THROUGH_ARITY_THREE") is True, "prior K signoff absent")
    for key in ("RAW_D_CARTAN_CERTIFIED", "ARITY_FOUR_CARTAN_CERTIFIED", "ALL_ORDERS_CARTAN_CERTIFIED", "QUANTUM_CLAIM"):
        _require(prior_flags.get(key) is False, f"prior signoff overpromotes {key}")
    audit_flags = audit.get("flags", {})
    _require(audit_flags.get("EXPORTED_UNARY_GENERATOR_IS_K") is True, "generator audit does not identify K")
    _require(audit_flags.get("AFFINE_D_ZERO_ARITY_NONZERO") is True, "raw D affine term disappeared")
    _require(audit_flags.get("AFFINE_D_CARTAN_CONSTRUCTED") is False, "affine D Cartan was promoted")

    paper = (ROOT / payload["source_manifest"]["paper_source"]["path"]).read_text(encoding="utf-8")
    required = (
        r"K:=D-\omega R",
        r"\begin{theorem}[Causal BV Cartan theorem for the helical stabilizer]",
        r"\bigl([Q,\iota_K]-L_K\bigr)^{(n)}=0",
        r"n=1,2,3",
        r"The manuscript status is \texttt{THEOREM\_FROZEN}",
        "Maxwell signal and observer-apparatus",
        "No convergent all-orders contraction is",
        "No affine $D$-Cartan homotopy",
    )
    for fragment in required:
        _require(fragment in paper, f"paper boundary missing: {fragment}")
    theorem_start = paper.index(r"\begin{theorem}[Causal BV Cartan theorem for the helical stabilizer]")
    theorem_end = paper.index(r"\end{theorem}", theorem_start)
    theorem = paper[theorem_start:theorem_end]
    _require(r"\iota_D" not in theorem and "all orders" not in theorem.lower(), "K theorem overclaims")

    flags = payload["flags"]
    _require(flags["PAPER_09_THEOREM_FROZEN_ACCEPTED"] is True, "frozen lifecycle not accepted")
    _require(flags["K_BERGER_CARTAN_THROUGH_ARITY_THREE"] is True, "K theorem not signed")
    for key in (
        "RAW_D_CARTAN_CERTIFIED", "ARITY_FOUR_CARTAN_CERTIFIED", "ALL_ORDERS_CARTAN_CERTIFIED",
        "MAXWELL_MAIN_THEOREM_INCLUDED", "OBSERVER_84_ROW_MAIN_THEOREM_INCLUDED",
        "HADAMARD_CERTIFIED", "QUANTUM_CLAIM",
    ):
        _require(flags[key] is False, f"forbidden promotion: {key}")


def mutations(payload: dict[str, Any]) -> None:
    cases = [
        (("approved_scope", "generator"), "D=partial_t"),
        (("approved_scope", "maximum_arity"), 4),
        (("flags", "RAW_D_CARTAN_CERTIFIED"), True),
        (("flags", "ALL_ORDERS_CARTAN_CERTIFIED"), True),
        (("flags", "MAXWELL_MAIN_THEOREM_INCLUDED"), True),
        (("flags", "OBSERVER_84_ROW_MAIN_THEOREM_INCLUDED"), True),
        (("flags", "QUANTUM_CLAIM"), True),
        (("source_manifest", "frozen_claim_table", "sha256"), "0" * 64),
    ]
    for path, value in cases:
        mutant = copy.deepcopy(payload)
        cursor = mutant
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value
        try:
            verify_payload(mutant, files=True)
        except VerificationError:
            continue
        raise VerificationError(f"mutation accepted: {'/'.join(path)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    if not args.check and not args.mutations:
        args.check = True
    payload = _load(CERTIFICATE)
    if args.check:
        verify_payload(payload)
        print("PAPER_09_NONLINEAR_FROZEN_K_GENERATOR_SIGNOFF: PASS")
    if args.mutations:
        mutations(payload)
        print("PAPER_09_NONLINEAR_FROZEN_K_GENERATOR_SIGNOFF mutations: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VerificationError as exc:
        print(f"PAPER_09_NONLINEAR_FROZEN_K_GENERATOR_SIGNOFF: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
