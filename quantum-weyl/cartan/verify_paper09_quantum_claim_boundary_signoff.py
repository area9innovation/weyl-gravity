"""Independent verifier for the Paper IX quantum claim-boundary signoff."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import subprocess
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "quantum-weyl/cartan/certificates/PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF.json"
SCHEMA = ROOT / "quantum-weyl/cartan/schema/paper09-quantum-claim-boundary-signoff-v1.schema.json"

# Exact aliases for the six fail-closed fields commissioned in the quantum
# team brief.  The persisted v1 signoff predates that spelling, so the
# verifier binds each commissioned name to its accepted v1 semantic field
# without rewriting the content-addressed certificate consumed by Paper IX.
COMMISSION_FALSE_PATHS = {
    "AFFINE_RAW_D_CARTAN": "forbidden_promotions.affine_raw_D_Cartan",
    "ALL_ORDERS_K_CARTAN": "forbidden_promotions.all_orders_K_Cartan",
    "HADAMARD_STATE": "forbidden_promotions.Hadamard_state",
    "QME_RESTORED": "theorem_flags.PAPER09_QME_ACCEPTED",
    "ANOMALY_CANCELLED": "theorem_flags.PAPER09_ANOMALY_CANCELLATION_ACCEPTED",
    "QUANTUM_THEOREM": "forbidden_promotions.quantum_theorem",
}


def _git_blob(commit: str, relpath: str) -> bytes:
    prefix = subprocess.check_output(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True
    ).strip()
    return subprocess.check_output(
        ["git", "show", f"{commit}:{prefix}{relpath}"], cwd=ROOT
    )


def _at(obj: object, path: str) -> object:
    cur = obj
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            raise AssertionError(f"missing semantic path {path}")
        cur = cur[key]
    return cur


def _set_at(obj: dict[str, object], path: str, value: object) -> None:
    parts = path.split(".")
    cursor: dict[str, object] = obj
    for key in parts[:-1]:
        child = cursor.get(key)
        if not isinstance(child, dict):
            raise AssertionError(f"missing semantic path {path}")
        cursor = child
    cursor[parts[-1]] = value


def _assert_commission_false_fields(cert: dict[str, object]) -> None:
    promoted = [
        name
        for name, path in COMMISSION_FALSE_PATHS.items()
        if _at(cert, path) is not False
    ]
    if promoted:
        raise AssertionError(f"Paper IX forbidden promotion detected: {promoted}")


def _load_sources(cert: dict[str, object]) -> dict[str, object]:
    manifest = cert["source_manifest"]
    if not isinstance(manifest, dict):
        raise AssertionError("source manifest is not an object")
    loaded: dict[str, object] = {}
    for key, item in manifest.items():
        if not isinstance(item, dict):
            raise AssertionError(f"invalid source record: {key}")
        path = item["path"]
        if not isinstance(path, str) or not path.endswith(".json"):
            continue
        if key == "claim_table":
            raw = _git_blob(str(item["commit"]), path)
            loaded[key] = json.loads(raw)
        else:
            loaded[key] = json.loads((ROOT / path).read_text())
    return loaded


def _assert_semantics(cert: dict[str, object], loaded: dict[str, object]) -> None:
    _assert_commission_false_fields(cert)

    manifest = cert["source_manifest"]
    if not isinstance(manifest, dict):
        raise AssertionError("source manifest is not an object")
    paper_record = manifest["paper"]
    if not isinstance(paper_record, dict):
        raise AssertionError("paper source record is not an object")

    generator = loaded["generator_audit"]
    arity3 = loaded["causal_k_cartan_arity_three"]
    qboundary = loaded["quantum_cartan_boundary"]
    paper = (ROOT / str(paper_record["path"])).read_text()
    paper_flat = " ".join(paper.split())

    assertions = {
        "generator corrected to K": _at(generator, "flags.EXPORTED_UNARY_GENERATOR_IS_K") is True,
        "raw D rejected": _at(generator, "flags.EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D") is False,
        "raw D affine": _at(generator, "flags.AFFINE_D_ZERO_ARITY_NONZERO") is True,
        "no affine D primitive": _at(generator, "flags.AFFINE_D_CARTAN_CONSTRUCTED") is False,
        "arity three classical complete": _at(arity3, "flags.BERGER_ARITY_THREE_D_CARTAN_FULL_4D")
        is True,
        "arity three nonquantum": _at(arity3, "flags.QUANTUM_CLAIM") is False,
        "arity three no Hadamard": _at(arity3, "flags.BERGER_HADAMARD_DATA") is False,
        "quantum boundary blocked": _at(qboundary, "claim_status") == "BLOCKED",
        "paper theorem is K": "[Q,\\iota_K]-L_K" in paper,
        "paper rejects affine D": "No affine $D$-Cartan theorem is claimed" in paper_flat
        and "L_D^{(0)}=\\omega R(\\rho,0)" in paper,
        "paper rejects quantum theorem": "quantum-master-equation result" in paper,
        "signoff accepts classical K": _at(
            cert,
            "theorem_flags.PAPER09_CLASSICAL_K_CARTAN_THROUGH_ARITY_THREE_ACCEPTED",
        )
        is True,
        "signoff is the accepted legacy id": _at(cert, "result_id")
        == "PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF",
        "signoff blocks affine D": _at(
            cert, "theorem_flags.PAPER09_AFFINE_D_CARTAN_ACCEPTED"
        )
        is False,
        "signoff blocks Hadamard": _at(cert, "theorem_flags.PAPER09_HADAMARD_ACCEPTED")
        is False,
        "signoff blocks QME": _at(cert, "theorem_flags.PAPER09_QME_ACCEPTED") is False,
        "signoff blocks anomaly": _at(
            cert, "theorem_flags.PAPER09_ANOMALY_CANCELLATION_ACCEPTED"
        )
        is False,
        "signoff blocks quantum": _at(
            cert, "theorem_flags.PAPER09_QUANTUM_PROMOTION_ACCEPTED"
        )
        is False,
    }
    failed = [name for name, passed in assertions.items() if not passed]
    if failed:
        raise AssertionError(f"independent signoff verification failed: {failed}")


def _verify_source_hashes(cert: dict[str, object]) -> None:
    manifest = cert["source_manifest"]
    if not isinstance(manifest, dict):
        raise AssertionError("source manifest is not an object")
    for key, item in manifest.items():
        if not isinstance(item, dict):
            raise AssertionError(f"invalid source record: {key}")
        path = ROOT / item["path"]
        blob = _git_blob(item["commit"], item["path"])
        if hashlib.sha256(blob).hexdigest() != item["sha256"]:
            raise AssertionError(f"pinned source hash mismatch: {item['path']}")
        if (
            key != "claim_table"
            and hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]
        ):
            raise AssertionError(f"live source hash mismatch: {item['path']}")


def run_mutation_guards(
    cert: dict[str, object], schema: dict[str, object], loaded: dict[str, object]
) -> tuple[str, ...]:
    """Prove that every commissioned forbidden promotion is rejected."""

    rejected: list[str] = []
    for name, path in COMMISSION_FALSE_PATHS.items():
        mutant = deepcopy(cert)
        _set_at(mutant, path, True)
        try:
            jsonschema.validate(
                mutant, schema, cls=jsonschema.Draft202012Validator
            )
            _assert_semantics(mutant, loaded)
        except (AssertionError, jsonschema.ValidationError):
            rejected.append(name)
        else:
            raise AssertionError(f"forbidden promotion mutation survived: {name}")
    return tuple(rejected)


def verify(*, mutations: bool = True) -> tuple[str, ...]:
    cert = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(cert, schema, cls=jsonschema.Draft202012Validator)
    _verify_source_hashes(cert)
    loaded = _load_sources(cert)
    _assert_semantics(cert, loaded)
    rejected = run_mutation_guards(cert, schema, loaded) if mutations else ()
    return rejected


def main() -> None:
    rejected = verify()
    suffix = f"; {len(rejected)} promotion mutations rejected" if rejected else ""
    print(f"Paper IX quantum claim-boundary signoff: PASS{suffix}")


if __name__ == "__main__":
    main()
