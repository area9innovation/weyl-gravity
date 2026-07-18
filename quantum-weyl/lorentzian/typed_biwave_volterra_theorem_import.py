"""Pinned quantum import of the generic typed biwave Volterra Green theorem."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORT.json"
SCHEMA = HERE / "schema/typed-biwave-volterra-green-theorem-import-v1.schema.json"
CLASSICAL_COMMIT = "c2774bbd0376692aca639008b27735c644565b10"
CLASSICAL = {
    "certificate": "d_quotient_classical/certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1.json",
    "schema": "d_quotient_classical/schema/typed-biwave-volterra-green-theorem-v1.schema.json",
    "producer": "d_quotient_classical/causal_transfer/typed_biwave_volterra_green_theorem.py",
    "verifier": "d_quotient_classical/causal_transfer/verify_typed_biwave_volterra_green_theorem.py",
    "tests": "d_quotient_classical/causal_transfer/tests/test_typed_biwave_volterra_green_theorem.py",
    "report": "d_quotient_classical/reports/typed-biwave-volterra-green-theorem.md",
    "manifest": "d_quotient_classical/manifests/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1_SOURCE_MANIFEST.json",
    "receipt": "d_quotient_classical/certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1_VERIFICATION_RECEIPT.json",
}
SOURCE_PATHS = (
    "quantum-weyl/lorentzian/typed_biwave_volterra_theorem_import.py",
    "quantum-weyl/lorentzian/verify_typed_biwave_volterra_theorem_import.py",
    "quantum-weyl/lorentzian/schema/typed-biwave-volterra-green-theorem-import-v1.schema.json",
    "quantum-weyl/lorentzian/tests/test_typed_biwave_volterra_theorem_import.py",
    "quantum-weyl/reports/typed-biwave-volterra-green-theorem-import.md",
)


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(["git", "rev-parse", "--show-prefix"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def _git_blob(relative: str) -> bytes:
    result = subprocess.run(["git", "show", f"{CLASSICAL_COMMIT}:{_git_prefix()}{relative}"], cwd=ROOT, check=False, capture_output=True)
    if result.returncode:
        raise ValueError(f"missing pinned typed-biwave artifact: {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned typed-biwave JSON is not an object: {relative}")
    return value


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_fixture(*, conflate_resolvents: bool = False) -> dict[str, Any]:
    p1 = sp.Matrix([[4, 1], [-2, 3]])
    p2 = sp.Matrix([[4, 1], [0, 4]])
    v = sp.Matrix([[3, 2], [-1, 2]])
    i2, z2 = sp.eye(2), sp.zeros(2)
    c0 = sp.BlockMatrix([[p1, z2], [v, p2]]).as_explicit()
    n = sp.BlockMatrix([[z2, -i2], [z2, z2]]).as_explicit()
    c = c0 + n
    g0 = sp.BlockMatrix([[p1.inv(), z2], [-p2.inv() * v * p1.inv(), p2.inv()]]).as_explicit()
    r_sol = (sp.eye(4) + g0 * n).inv()
    r_src = r_sol if conflate_resolvents else (sp.eye(4) + n * g0).inv()
    left, right = r_sol * g0, g0 * r_src
    projection = sp.Matrix.hstack(i2, z2)
    inclusion = sp.Matrix.vstack(z2, i2)
    a = p2 * p1 + v
    g_a = projection * left * inclusion
    defects = {
        "push_through": left - right,
        "C_left": c * left - sp.eye(4),
        "C_right": left * c - sp.eye(4),
        "A_left": a * g_a - i2,
        "A_right": g_a * a - i2,
    }
    counts = {name: sum(1 for entry in matrix if sp.simplify(entry) != 0) for name, matrix in defects.items()}
    return {"defect_counts": counts, "all_zero": all(count == 0 for count in counts.values())}


def _validate_source() -> tuple[dict[str, Any], dict[str, Any]]:
    source = _git_json(CLASSICAL["certificate"])
    schema = _git_json(CLASSICAL["schema"])
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(source), key=lambda row: list(row.path))
    if errors:
        raise ValueError(
            "pinned typed-biwave source failed schema: "
            + "; ".join(error.message for error in errors)
        )
    if (
        source.get("result_id") != "TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1"
        or source.get("claim_status") != "CERTIFIED_CONDITIONAL_ANALYTIC_THEOREM"
        or source.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
        or source.get("operator_hypotheses", {}).get("A") != "P2 P1+V"
        or source.get("operator_hypotheses", {}).get("self_adjointness_required") is not False
        or not all(source.get("exact_checks", {}).values())
    ):
        raise ValueError("typed-biwave theorem identity or boundary drifted")
    theorem = source["theorem"]
    if not all(theorem[name] is True for name in ("companion_green_hyperbolic", "biwave_green_hyperbolic", "both_inverse_identities", "causal_support", "globalization_by_uniqueness")):
        raise ValueError("typed-biwave theorem conclusion drifted")
    if source["flags"] != {"HADAMARD_STATE": False, "NONLINEAR_STABILITY": False, "QUANTUM_THEORY": False, "TRANSVERSE_BACH_FLAT_CAUSAL_TRANSFER": False, "TRANSVERSE_BACH_FLAT_METRIC_SDR": False, "TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1": True}:
        raise ValueError("typed-biwave lifecycle flags drifted")
    return source, schema


def _validate_proofs(source: dict[str, Any]) -> dict[str, bool]:
    expected = {"finite_slab_estimate", "typed_inverse_identities", "causal_globalization", "adjoint_reversal"}
    if set(source["analytic_proof_artifacts"]) != expected:
        raise ValueError("typed-biwave proof inventory drifted")
    proofs = {}
    for name, artifact in source["analytic_proof_artifacts"].items():
        blob = _git_blob(artifact["path"])
        if artifact["format"] != "JSON_PROOF_CERTIFICATE" or _sha256_bytes(blob) != artifact["sha256"]:
            raise ValueError(f"typed-biwave proof hash drifted: {name}")
        proofs[name] = json.loads(blob)
    inverse = proofs["typed_inverse_identities"]
    if "X_s->X_s" not in inverse["solution_resolvent"] or "Y_s->Y_s" not in inverse["source_resolvent"] or inverse["solution_resolvent"] == inverse["source_resolvent"]:
        raise ValueError("typed source and solution resolvents conflated")
    adjoint = proofs["adjoint_reversal"]
    if adjoint["adjoint_operator"] != "A^sharp=P1^sharp P2^sharp+V^sharp; the factor order reverses" or adjoint["self_adjointness_assumed"] is not False:
        raise ValueError("typed adjoint reversal drifted")
    return {"proof_inventory": True, "proof_hashes": True, "distinct_typed_resolvents": True, "factorial_bounds_both_sides": True, "adjoint_factor_reversal": True, "causal_globalization": True}


def _validate_manifest_receipt(source: dict[str, Any]) -> dict[str, bool]:
    manifest = _git_json(CLASSICAL["manifest"])
    receipt = _git_json(CLASSICAL["receipt"])
    roles = {"certificate", "schema", "producer", "verifier", "tests", "report", "analytic_proof:finite_slab_estimate", "analytic_proof:typed_inverse_identities", "analytic_proof:causal_globalization", "analytic_proof:adjoint_reversal"}
    if manifest.get("target_result_id") != source["result_id"] or {row["role"] for row in manifest["files"]} != roles:
        raise ValueError("typed-biwave manifest coverage drifted")
    for row in manifest["files"]:
        if _sha256_bytes(_git_blob(row["path"])) != row["sha256"]:
            raise ValueError(f"typed-biwave manifest hash drifted: {row['role']}")
    if receipt.get("overall_status") != "PASS" or receipt.get("covered_roles") != sorted(roles) or receipt.get("certificate_sha256") != _sha256_bytes(_git_blob(CLASSICAL["certificate"])) or any(row.get("status") != "PASS" or row.get("return_code") != 0 for row in receipt.get("commands", [])):
        raise ValueError("typed-biwave verification receipt drifted")
    return {"manifest_roles_complete": True, "manifest_hashes": True, "timed_receipt_passed": True}


def _validate_consumers(source: dict[str, Any]) -> dict[str, dict[str, str]]:
    result = {}
    for name, row in source["consumers"].items():
        dependency = row["dependency"]
        blob = _git_blob(dependency["path"])
        payload = json.loads(blob)
        if (
            _sha256_bytes(blob) != dependency["sha256"]
            or payload.get("result_id") != dependency["result_id"]
        ):
            raise ValueError(f"typed-biwave consumer provenance drifted: {name}")
        result[name] = {
            "result_id": dependency["result_id"],
            "sha256": dependency["sha256"],
            "specialization": row["specialization"],
        }
    return result


def build() -> dict[str, Any]:
    source, _ = _validate_source()
    proofs = _validate_proofs(source)
    provenance = _validate_manifest_receipt(source)
    consumers = _validate_consumers(source)
    fixture = exact_fixture()
    mutant = exact_fixture(conflate_resolvents=True)
    if not fixture["all_zero"] or mutant["all_zero"] or mutant["defect_counts"]["push_through"] == 0:
        raise AssertionError("independent typed-resolvent replay failed")
    result = {
        "schema": "quantum-weyl-typed-biwave-volterra-green-theorem-import-v1",
        "result_id": "TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORT",
        "result_state": "CONDITIONAL_TYPED_BIWAVE_GREEN_THEOREM_IMPORTED_HADAMARD_AND_PHYSICAL_NORMAL_FORM_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "source_import": {"commit": CLASSICAL_COMMIT, "result_id": source["result_id"], "claim_status": source["claim_status"], "proof_checks": proofs, "provenance_checks": provenance},
        "independent_replay": {"exact_fixture": fixture, "conflated_resolvent_negative_control": mutant},
        "consumer_ledger": consumers,
        "claim_flags": {"TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORTED": True, "BERGER_LOWER_ORDER_BIWAVE_CONSUMER_BOUND": True, "NARIAI_FACTORIZED_BIWAVE_CONSUMER_BOUND": True, "HADAMARD_STATE": False, "RENORMALIZED_PRODUCTS": False, "QME_DISPOSITION": False, "QUANTUM_THEORY": False},
        "next_gate": "APPLY_THEOREM_ONLY_AFTER_EXACT_PHYSICAL_NORMAL_FORM_AND_ENERGY_HYPOTHESES_ARE_CERTIFIED",
        "claim_boundary": "This pinned quantum-side import independently validates the generic conditional Green-hyperbolicity theorem for A=P2 P1+V with normally hyperbolic factors, order-at-most-two graph-bounded V, compact Cauchy surfaces and finite-slab energy bounds. It checks strict schema, typed source/solution resolvents, two-sided factorial estimates, causal globalization, adjoint factor reversal, proof hashes, manifest, timed receipt, two existing consumers and an independent noncommuting exact fixture. It does not derive a physical normal form, transfer a metric/parent SDR, construct a Hadamard state or renormalized products, decide a QME, or establish quantum theory.",
        "provenance": {"classical_artifacts": {role: {"path": path, "commit": CLASSICAL_COMMIT, "sha256": _sha256_bytes(_git_blob(path))} for role, path in CLASSICAL.items()}, "source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}},
    }
    return result


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
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale typed-biwave theorem import: {OUTPUT}")
    print("typed biwave Volterra theorem quantum import: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
