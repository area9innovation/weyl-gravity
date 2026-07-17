#!/usr/bin/env python3
"""Independent verifier for the Paper IX nonlinear K-generator signoff.

This consumer imports no signoff producer.  It validates the strict schema,
recomputes every content hash, checks the pinned Git object, and audits the
generator/arity boundary directly in the source certificates and manuscript.
"""

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
CERTIFICATE = ROOT / "d_quotient_classical/certificates/PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF.json"
SCHEMA = ROOT / "d_quotient_classical/schema/paper-09-nonlinear-k-generator-signoff-v1.schema.json"


class VerificationError(RuntimeError):
    """Raised when the scoped signoff is not justified."""


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise VerificationError(f"expected JSON object: {path}")
    return value


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _git_blob(commit: str, path: str) -> bytes:
    prefix_proc = subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    repository_path = f"{prefix_proc.stdout.strip()}{path}"
    proc = subprocess.run(
        ["git", "show", f"{commit}:{repository_path}"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode:
        raise VerificationError(
            f"missing pinned Git object {commit}:{path}: "
            f"{proc.stderr.decode('utf-8', errors='replace').strip()}"
        )
    return proc.stdout


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def _validate_schema(payload: dict[str, Any]) -> None:
    schema = _load_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda error: list(error.path))
    if errors:
        rendered = "; ".join(
            f"{'/'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
            for error in errors
        )
        raise VerificationError(f"schema validation failed: {rendered}")


def _audit_manifest(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for key, evidence in payload["source_manifest"].items():
        path_text = evidence["path"]
        path = ROOT / path_text
        _require(path.is_file(), f"missing evidence file: {path_text}")
        pinned_blob = _git_blob(evidence["commit"], path_text)
        committed_hash = _sha256_bytes(pinned_blob)
        _require(committed_hash == evidence["sha256"], f"pinned Git hash mismatch: {key}")
        if key != "claim_table":
            current_hash = _sha256_file(path)
            _require(current_hash == evidence["sha256"], f"worktree hash mismatch: {path_text}")
        if "result_id" in evidence:
            source = json.loads(pinned_blob) if key == "claim_table" else _load_json(path)
            _require(source.get("result_id") == evidence["result_id"], f"result_id mismatch: {key}")
            loaded[key] = source
    return loaded


def _audit_sources(payload: dict[str, Any], sources: dict[str, dict[str, Any]]) -> None:
    claim_table = sources["claim_table"]
    audit = sources["generator_audit"]
    q2 = sources["support_local_q2"]
    q3 = sources["support_local_q3"]
    green = sources["causal_green_homotopy"]
    cartan2 = sources["causal_cartan_arity_two"]
    cartan3 = sources["causal_cartan_arity_three"]

    _require(claim_table.get("paper_state") == "WRITING_STARTED", "Paper IX is not WRITING_STARTED")
    _require(claim_table.get("theorem_frozen") is False, "Paper IX was prematurely theorem-frozen")
    _require(
        claim_table.get("required_signoffs", {}).get("nonlinear_team")
        == "PENDING_K_GENERATOR_INTERPRETATION_REVIEW",
        "claim table no longer requests the scoped nonlinear K-generator review",
    )

    claims = {entry["claim_id"]: entry for entry in claim_table.get("claims", [])}
    _require(set(claims) == {f"P09-C{i}" for i in range(1, 11)}, "Paper IX claim set is incomplete")
    for claim_id in ("P09-C6", "P09-C7", "P09-C8", "P09-C9", "P09-C10"):
        _require("K" in claims[claim_id]["claim"], f"{claim_id} is not stated as a K claim")

    audit_flags = audit.get("flags", {})
    audit_checks = audit.get("exact_checks", {})
    _require(audit_flags.get("EXPORTED_UNARY_GENERATOR_IS_K") is True, "frozen generator is not K")
    _require(audit_flags.get("EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D") is False, "raw D was promoted")
    _require(audit_flags.get("AFFINE_D_ZERO_ARITY_NONZERO") is True, "raw-D affine term was erased")
    _require(audit_flags.get("AFFINE_D_CARTAN_CONSTRUCTED") is False, "affine raw-D Cartan was promoted")
    _require(audit_flags.get("THEOREM_FROZEN") is False, "generator audit freezes the theorem")
    _require(audit_checks.get("frozen_e0_action_equals_K_unary_action") is True, "K conjugation check failed")
    _require(audit.get("exact_conjugation", {}).get("K_zero_arity") == ["0", "0"], "K does not fix background")
    _require(
        audit.get("exact_conjugation", {}).get("raw_D_zero_arity") == ["0", "omega*rho"],
        "raw-D zero-arity component is not pinned",
    )

    _require(q2.get("classical_binary_q2", {}).get("support_local") is True, "q2 is not support-local")
    _require(q2.get("classical_binary_q2", {}).get("total_rows") == 54, "q2 is not all-row")
    _require(q2.get("derivation", {}).get("not_fitted_to_residual_data") is True, "q2 was fitted")
    _require(q2.get("exact_checks", {}).get("q1_q2_arity_two_nilpotency_raw_coefficientwise") is True, "q2 identity failed")
    _require(q2.get("exact_checks", {}).get("D_q2_derivation_termwise") is True, "legacy unary q2 derivation failed")

    _require(q3.get("classical_ternary_q3", {}).get("support_local") is True, "q3 is not support-local")
    _require(q3.get("classical_ternary_q3", {}).get("total_rows") == 54, "q3 is not all-row")
    _require(q3.get("derivation", {}).get("not_fitted_to_residual_data") is True, "q3 was fitted")
    _require(q3.get("exact_checks", {}).get("q1_q3_plus_q2_q2_arity_three_nilpotency_raw_coefficientwise") is True, "q3 identity failed")
    _require(q3.get("exact_checks", {}).get("D_q3_derivation_termwise") is True, "legacy unary q3 derivation failed")
    _require(
        q3.get("local_D_arity_three", {}).get("reason")
        == "the helical generator acts linearly as the central invariant derivative e0 on dressed component coefficients",
        "q3 does not identify the helical unary action",
    )

    green_checks = green.get("exact_checks", {})
    for check in (
        "advanced_chain_homotopy_identity",
        "retarded_chain_homotopy_identity",
        "advanced_support",
        "retarded_support",
        "all_54_rows_included",
        "cyclic_advanced_retarded_adjointness",
    ):
        _require(green_checks.get(check) is True, f"causal Green check failed: {check}")
    _require(green.get("flags", {}).get("BERGER_HADAMARD_DATA") is False, "Hadamard data overpromoted")

    cartan2_checks = cartan2.get("exact_checks", {})
    for check in ("unary_Cartan_identity", "arity_two_Cartan_identity", "arity_two_cyclic_primitive", "two_sided_causal_support"):
        _require(cartan2_checks.get(check) is True, f"arity-two Cartan check failed: {check}")
    _require(cartan2.get("flags", {}).get("BERGER_ARITY_THREE_D_CARTAN") is False, "arity-two artifact overpromotes arity three")
    _require(cartan2.get("flags", {}).get("QUANTUM_CLAIM") is False, "arity-two artifact overpromotes quantum claim")

    cartan3_checks = cartan3.get("exact_checks", {})
    for check in (
        "arity_three_Cartan_identity",
        "arity_three_source_closed",
        "arity_three_cyclic_primitive",
        "complete_arbitrary_input_q3_imported",
        "all_54_rows_included",
        "two_sided_causal_support",
    ):
        _require(cartan3_checks.get(check) is True, f"arity-three Cartan check failed: {check}")
    _require(cartan3.get("flags", {}).get("BERGER_HADAMARD_DATA") is False, "arity-three artifact overpromotes Hadamard")
    _require(cartan3.get("flags", {}).get("QUANTUM_CLAIM") is False, "arity-three artifact overpromotes quantum claim")
    _require("BERGER_ARITY_FOUR_D_CARTAN_IF_REQUIRED" in cartan3.get("next_gates", []), "arity four is not left as a next gate")

    _require(payload["review_scope"]["maximum_certified_arity"] == 3, "signoff exceeds arity three")
    flags = payload["flags"]
    _require(flags["K_BERGER_CARTAN_THROUGH_ARITY_THREE"] is True, "K signoff missing")
    for false_flag in (
        "RAW_D_CARTAN_CERTIFIED",
        "ARITY_FOUR_CARTAN_CERTIFIED",
        "ALL_ORDERS_CARTAN_CERTIFIED",
        "QUANTUM_CLAIM",
        "THEOREM_FROZEN",
    ):
        _require(flags[false_flag] is False, f"forbidden promotion: {false_flag}")
    recorded_commands = [entry["command"] for entry in payload["verification"]["recorded_run"]]
    _require(
        recorded_commands == payload["verification"]["commands"],
        "recorded verification commands do not match the declared commands",
    )


def _audit_paper(payload: dict[str, Any]) -> None:
    paper_path = ROOT / payload["source_manifest"]["paper_source"]["path"]
    paper = paper_path.read_text(encoding="utf-8")
    required_fragments = (
        r"K:=D-\omega R",
        r"\cL_K\bar\Phi=0",
        r"L_D^{(0)}=\omega R(\rho,0)",
        r"\begin{theorem}[Causal BV Cartan theorem for the helical stabilizer]",
        r"\bigl([Q,\iota_K]-L_K\bigr)^{(n)}=0",
        r"n=1,2,3",
        r"No affine $D$-Cartan homotopy, including its zeroth-arity equation, is",
        r"No convergent all-orders contraction is",
        r"\texttt{WRITING\_STARTED}, not",
        r"\texttt{THEOREM\_FROZEN}",
    )
    for fragment in required_fragments:
        _require(fragment in paper, f"Paper IX boundary fragment missing: {fragment}")

    theorem_start = paper.index(r"\begin{theorem}[Causal BV Cartan theorem for the helical stabilizer]")
    theorem_end = paper.index(r"\end{theorem}", theorem_start)
    theorem = paper[theorem_start:theorem_end]
    _require(r"\iota_D" not in theorem, "scoped K theorem contains iota_D")
    _require(r"L_D" not in theorem, "scoped K theorem contains L_D")
    _require("all orders" not in theorem.lower(), "scoped K theorem claims all orders")
    _require("arity four" not in theorem.lower(), "scoped K theorem claims arity four")


def verify_payload(payload: dict[str, Any], *, check_files: bool = True) -> None:
    _validate_schema(payload)
    if check_files:
        sources = _audit_manifest(payload)
        _audit_sources(payload, sources)
        _audit_paper(payload)


def run_mutation_tests(payload: dict[str, Any]) -> None:
    mutations: list[tuple[str, tuple[str, ...], Any]] = [
        ("promote raw D", ("flags", "RAW_D_CARTAN_CERTIFIED"), True),
        ("promote arity four", ("flags", "ARITY_FOUR_CARTAN_CERTIFIED"), True),
        ("promote all orders", ("flags", "ALL_ORDERS_CARTAN_CERTIFIED"), True),
        ("promote quantum", ("flags", "QUANTUM_CLAIM"), True),
        ("freeze theorem", ("flags", "THEOREM_FROZEN"), True),
        ("raise maximum arity", ("review_scope", "maximum_certified_arity"), 4),
        ("rename generator as D", ("review_scope", "certified_generator"), "D=partial_t"),
        ("forge source hash", ("source_manifest", "generator_audit", "sha256"), "0" * 64),
    ]
    for label, path, value in mutations:
        mutant = copy.deepcopy(payload)
        cursor: dict[str, Any] = mutant
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value
        try:
            verify_payload(mutant, check_files=True)
        except VerificationError:
            continue
        raise VerificationError(f"mutation was not rejected: {label}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify schema, hashes and semantics")
    parser.add_argument("--mutations", action="store_true", help="run fail-closed mutation tests")
    args = parser.parse_args()
    if not args.check and not args.mutations:
        args.check = True

    payload = _load_json(CERTIFICATE)
    if args.check:
        verify_payload(payload, check_files=True)
        print("PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF: PASS")
    if args.mutations:
        run_mutation_tests(payload)
        print("PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF mutations: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VerificationError as error:
        print(f"PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
