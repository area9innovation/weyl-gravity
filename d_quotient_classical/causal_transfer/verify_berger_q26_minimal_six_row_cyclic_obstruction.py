#!/usr/bin/env python3
"""Independent verifier for the minimal six-row Berger cyclic obstruction.

This consumer deliberately does not import the producer.  It independently
loads the pinned predecessor from Git, enumerates every admissible six-row
degree profile, audits the degree-one pairing ranks, and checks the decoupled
sparse mutation control.
"""

from __future__ import annotations

from itertools import product
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/BERGER_Q26_MINIMAL_SIX_ROW_CYCLIC_OBSTRUCTION_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/generated/berger_q26_minimal_six_row_cyclic_obstruction_v1/degree_and_sparse_control.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-q26-minimal-six-row-cyclic-obstruction-v1.schema.json"
WORKING_INPUT = ROOT / "d_quotient_classical/certificates/BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1.json"
Q104 = ROOT / "quantum-weyl/lorentzian/generated/berger_canonical_graph_q_cauchy_obstruction/rejected_candidate_q_Cauchy_104.json"
A104 = ROOT / "quantum-weyl/lorentzian/generated/berger_a104_endpoint_completion/global_A104.json"

PINNED_COMMIT = "988f8ee6c59b539ae516eb8a8f882a57a95f71e0"
PINNED_PATH = (
    "physics/symplectic-reconstruction/d_quotient_classical/certificates/"
    "BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1.json"
)
PINNED_SHA256 = "24d2db35fb3dc696081d1e93208fdbd0b8f31922cdac7a063033650a9e686a01"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _pinned_blob() -> bytes:
    return subprocess.run(
        ["git", "show", f"{PINNED_COMMIT}:{PINNED_PATH}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def _verify_sparse(path: Path, expected_entries: int) -> dict[str, Any]:
    value = _load(path)
    body = {key: item for key, item in value.items() if key != "sha256"}
    if value.get("sha256") != _digest(body):
        raise AssertionError(f"internal sparse digest drifted: {path}")
    if value.get("shape") != [104, 104]:
        raise AssertionError(f"sparse shape drifted: {path}")
    if len(value.get("entries", [])) != expected_entries:
        raise AssertionError(f"sparse entry count drifted: {path}")
    return value


def _rank_replay() -> dict[str, Any]:
    """Recompute the finite grading problem without producer code."""
    profiles = sorted(
        list(candidate)
        for candidate in product(range(7), repeat=4)
        if sum(candidate) == 6 and candidate[1] >= 5 and candidate[2] >= 1
    )
    if profiles != [[0, 5, 1, 0]]:
        raise AssertionError("complete six-row profile enumeration failed")
    base = [12, 40, 40, 12]
    extended = [left + right for left, right in zip(base, profiles[0])]
    deficits = {
        "-1:2": abs(extended[0] - extended[3]),
        "0:1": abs(extended[1] - extended[2]),
    }

    cyclic_profiles = sorted(
        list(candidate)
        for total in range(6, 11)
        for candidate in product(range(total + 1), repeat=4)
        if sum(candidate) == total
        and candidate[1] >= 5
        and candidate[2] >= 1
        and base[0] + candidate[0] == base[3] + candidate[3]
        and base[1] + candidate[1] == base[2] + candidate[2]
    )
    if cyclic_profiles != [[0, 5, 5, 0]]:
        raise AssertionError("rank-minimal cyclic completion enumeration failed")
    return {
        "profiles": profiles,
        "extended": extended,
        "deficits": deficits,
        "cyclic_profiles_through_ten_rows": cyclic_profiles,
    }


def verify() -> None:
    certificate = _load(CERT)
    payload = _load(PAYLOAD)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)

    pinned_blob = _pinned_blob()
    if hashlib.sha256(pinned_blob).hexdigest() != PINNED_SHA256:
        raise AssertionError("pinned predecessor digest drifted")
    pinned = json.loads(pinned_blob)
    working = _load(WORKING_INPUT)
    for field in ("result_id", "exact_replay", "extension_lower_bound", "claim_flags"):
        if pinned[field] != working[field]:
            raise AssertionError(f"scientific predecessor field drifted: {field}")

    for ref in certificate["dependencies"].values():
        path = ROOT / ref["path"]
        if _sha(path) != ref["sha256"]:
            raise AssertionError(f"dependency digest drifted: {path}")
    for relative, expected in certificate["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != expected:
            raise AssertionError(f"source digest drifted: {relative}")
    if _sha(PAYLOAD) != certificate["exact_payload"]["sha256"]:
        raise AssertionError("payload digest drifted")

    q_value = _verify_sparse(Q104, 1018)
    a_value = _verify_sparse(A104, 470)
    control = payload["decoupled_sparse_control"]
    if (
        control["q_old_old"]["internal_sha256"] != q_value["sha256"]
        or control["A_old_old"]["internal_sha256"] != a_value["sha256"]
        or control["q_square_nonzero_sparse_entries"] != 157
        or control["A_q_commutator_nonzero_sparse_entries"] != 207
    ):
        raise AssertionError("decoupled 157/207 mutation control drifted")

    replay = _rank_replay()
    audit = certificate["rank_audit"]
    if (
        audit["complete_six_row_profiles"] != replay["profiles"]
        or audit["six_row_extended_ranks"] != replay["extended"]
        or audit["minimum_pairing_radical_dimension"] != replay["deficits"]["0:1"]
        or audit["unique_rank_minimal_cyclic_additions"]
        != replay["cyclic_profiles_through_ten_rows"][0]
    ):
        raise AssertionError("independent rank replay disagrees with certificate")
    if replay["deficits"] != {"-1:2": 0, "0:1": 4}:
        raise AssertionError("degree-one pairing deficit drifted")

    flags = certificate["classification"]
    if (
        flags["six_row_cyclic_BV_extension_exists"]
        or flags["ten_row_extension_sufficient"]
        or flags["Hadamard_or_quantum_claim"]
        or not flags["complete_six_row_grading_enumerated"]
    ):
        raise AssertionError("fail-closed classification flags drifted")
    print("BERGER_Q26_MINIMAL_SIX_ROW_CYCLIC_OBSTRUCTION_V1: VERIFIED")


if __name__ == "__main__":
    verify()
