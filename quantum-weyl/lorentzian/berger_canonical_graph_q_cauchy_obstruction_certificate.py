"""Emit or check the canonical Berger graph-lift obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from .berger_canonical_graph_q_cauchy_obstruction import (
    A104_CERTIFICATE,
    GENERATED,
    OUTPUT,
    Q1_CERTIFICATE,
    REPORT,
    build,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCHEMA = HERE / "schema/berger-canonical-graph-q-cauchy-obstruction-v1.schema.json"
SOURCE_PATHS = (
    "quantum-weyl/lorentzian/berger_canonical_graph_q_cauchy_obstruction.py",
    "quantum-weyl/lorentzian/berger_canonical_graph_q_cauchy_obstruction_certificate.py",
    "quantum-weyl/lorentzian/verify_berger_canonical_graph_q_cauchy_obstruction.py",
    "quantum-weyl/lorentzian/schema/berger-canonical-graph-q-cauchy-obstruction-v1.schema.json",
    "quantum-weyl/lorentzian/tests/test_berger_canonical_graph_q_cauchy_obstruction.py",
)


def _text(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def certificate_payload() -> tuple[dict, dict[str, dict]]:
    result, artifacts = build()
    artifact_refs = {}
    for name, artifact in artifacts.items():
        body = _text(artifact).encode()
        artifact_refs[name] = {
            "format": "JSON_EXACT_SPARSE_OPERATOR",
            "path": str((GENERATED / f"{name}.json").relative_to(ROOT)),
            "sha256": hashlib.sha256(body).hexdigest(),
        }
    manifest = {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
    result.update(
        {
            "lifecycle_layer": "LORENTZIAN_FREE_QUANTUM_PREFLIGHT",
            "dependency_refs": {
                "full_A104": {
                    "artifact_id": "BERGER_A104_ENDPOINT_COMPLETION",
                    "path": str(A104_CERTIFICATE.relative_to(ROOT)),
                    "sha256": _sha256(A104_CERTIFICATE),
                },
                "retained_q26": {
                    "artifact_id": "BERGER_RETAINED_MINIMAL_OPERATOR",
                    "path": str(Q1_CERTIFICATE.relative_to(ROOT)),
                    "sha256": _sha256(Q1_CERTIFICATE),
                },
            },
            "candidate_artifacts": artifact_refs,
            "provenance": {
                "coefficient_backend": "sparse exact QQ[alpha_B,u,v] monomials with PBW word reduction",
                "source_manifest": manifest,
                "source_manifest_sha256": _digest(manifest),
            },
        }
    )
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(result)
    return result, artifacts


def report_text(result: dict) -> str:
    square = result["defects"]["candidate_q_Cauchy_square"]
    commutator = result["defects"]["A104_candidate_q_Cauchy_commutator"]
    return f"""# Canonical Berger graph-lift obstruction

The retained `q26` is exact and nilpotent.  Its tautological solution-graph
lift

```text
q52 = i_solution q26 p_solution
```

is also degree `+1` and nilpotent.  However, after exact stationary first-jet
reduction through the completed `A104`, the resulting candidate has
{square['nonzero_sparse_entries']} nonzero entries in its square and
{commutator['nonzero_sparse_entries']} nonzero entries in its `A104`
commutator.  The first witnesses are stored coefficientwise with normalized
SHA-256 digests.

This rejects only the canonical graph lift.  It does not prove that no local
corrected lift exists.  The missing classical-to-quantum carrier is now exact:
either export a `q26`-compatible companion/Cauchy BRST lift for the frozen
`A104`, or replace the companion witness by a BRST-compatible one and derive
its Cauchy evolution.

This stationary obstruction does not invalidate the separately certified
26-row advanced/retarded causal Green homotopy.  Consequently the direct
causal/Microlocal Hadamard route remains open even though this stationary
spectral route cannot yet be promoted.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, artifacts = certificate_payload()
    certificate = _text(result)
    report = report_text(result)
    if args.emit:
        GENERATED.mkdir(parents=True, exist_ok=True)
        for name, artifact in artifacts.items():
            (GENERATED / f"{name}.json").write_text(_text(artifact))
        OUTPUT.write_text(certificate)
        REPORT.write_text(report)
    if args.check:
        if OUTPUT.read_text() != certificate:
            raise SystemExit("stale canonical graph-lift obstruction certificate")
        for name, artifact in artifacts.items():
            if (GENERATED / f"{name}.json").read_text() != _text(artifact):
                raise SystemExit(f"stale canonical graph-lift artifact: {name}")
        if REPORT.read_text() != report:
            raise SystemExit("stale canonical graph-lift obstruction report")
    if not args.emit and not args.check:
        print(certificate, end="")
    print("BERGER CANONICAL GRAPH Q-CAUCHY OBSTRUCTION: 157 SQUARE / 207 COMMUTATOR DEFECTS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
