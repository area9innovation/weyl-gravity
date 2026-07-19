"""Independent structural verifier for the canonical graph-lift obstruction."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator

from .berger_canonical_graph_q_cauchy_obstruction import GENERATED, OUTPUT
from .berger_canonical_graph_q_cauchy_obstruction_certificate import (
    ROOT,
    SCHEMA,
    SOURCE_PATHS,
    _digest,
)


def _witness_hash(witness: dict) -> str:
    body = {key: value for key, value in witness.items() if key != "sha256"}
    return _digest(body)


def verify() -> None:
    certificate = json.loads(OUTPUT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)

    expected_checks = {
        "q26_squared_zero": True,
        "q52_has_degree_plus_one": True,
        "q52_squared_zero": True,
        "q_Cauchy_has_degree_plus_one": True,
        "candidate_is_exact_stationary_jet_reduction_of_q52": True,
        "candidate_q_Cauchy_squared_zero": False,
        "full_A104_commutes_with_candidate_q_Cauchy": False,
    }
    if certificate["exact_checks"] != expected_checks:
        raise AssertionError("canonical graph-lift disposition changed")
    expected_counts = {
        "candidate_q_Cauchy_square": 157,
        "A104_candidate_q_Cauchy_commutator": 207,
    }
    for name, count in expected_counts.items():
        defect = certificate["defects"][name]
        if defect["nonzero_sparse_entries"] != count:
            raise AssertionError(f"{name} defect count changed")
        if defect["first_witness"]["sha256"] != _witness_hash(
            defect["first_witness"]
        ):
            raise AssertionError(f"{name} witness hash mismatch")

    for name, reference in certificate["candidate_artifacts"].items():
        path = ROOT / reference["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
            raise AssertionError(f"candidate artifact hash mismatch: {name}")
        artifact = json.loads(path.read_text())
        body = {"shape": artifact["shape"], "entries": artifact["entries"]}
        if artifact["sha256"] != _digest(body):
            raise AssertionError(f"candidate internal hash mismatch: {name}")

    manifest = certificate["provenance"]["source_manifest"]
    expected_manifest = {
        path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        for path in SOURCE_PATHS
    }
    if manifest != expected_manifest:
        raise AssertionError("canonical graph-lift source manifest mismatch")
    if certificate["provenance"]["source_manifest_sha256"] != _digest(manifest):
        raise AssertionError("canonical graph-lift manifest aggregate mismatch")

    flags = certificate["claim_flags"]
    if flags["BERGER_Q_CAUCHY_104"] or flags["BERGER_HADAMARD_DATA"]:
        raise AssertionError("failed canonical lift was promoted")


def main() -> int:
    verify()
    print("BERGER CANONICAL GRAPH Q-CAUCHY OBSTRUCTION independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
