"""Independent verifier for the post-freeze Paper IX quantum signoff."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "quantum-weyl/cartan/certificates/PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF_V2.json"
SCHEMA = ROOT / "quantum-weyl/cartan/schema/paper09-quantum-claim-boundary-signoff-v2.schema.json"


def main() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for source in value["source_manifest"].values():
        path = ROOT / source["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise AssertionError(f"source hash drift: {source['path']}")
        commit = subprocess.check_output(
            ["git", "log", "-1", "--format=%H", "--", source["path"]],
            cwd=ROOT,
            text=True,
        ).strip()
        if commit != source["commit"]:
            raise AssertionError(f"source commit drift: {source['path']}")

    table_source = value["source_manifest"]["frozen_claim_table"]
    table = json.loads((ROOT / table_source["path"]).read_text())
    predecessor_source = value["source_manifest"]["predecessor_quantum_signoff"]
    predecessor = json.loads((ROOT / predecessor_source["path"]).read_text())
    qsign = next(x for x in table["signoff_evidence"] if x["team"] == "quantum_team")
    flags = value["theorem_flags"]
    checks = {
        "frozen": table["theorem_frozen"] is True and table["paper_state"] == "THEOREM_FROZEN",
        "predecessor pinned by frozen table": qsign["certificate_sha256"]
        == predecessor_source["sha256"],
        "predecessor blocks quantum": predecessor["theorem_flags"][
            "PAPER09_QUANTUM_PROMOTION_ACCEPTED"
        ]
        is False,
        "accepts only frozen classical K": flags["PAPER09_FROZEN_CLASSICAL_K_CARTAN_ACCEPTED"]
        is True,
        "blocks affine D": flags["PAPER09_AFFINE_D_CARTAN_ACCEPTED"] is False,
        "blocks Hadamard": flags["PAPER09_HADAMARD_ACCEPTED"] is False,
        "blocks QME": flags["PAPER09_QME_ACCEPTED"] is False,
        "blocks anomaly": flags["PAPER09_ANOMALY_CANCELLATION_ACCEPTED"] is False,
        "blocks residual transfer": flags["PAPER09_RESIDUAL_QUANTUM_TRANSFER_ACCEPTED"]
        is False,
        "blocks quantum": flags["PAPER09_QUANTUM_PROMOTION_ACCEPTED"] is False,
        "Maxwell excluded": value["approved_classical_scope"]["maxwell_in_main_theorem"]
        is False,
        "retained branch basis is post-freeze": value["outside_paper09_followups"][0]
        == "BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V1",
        "QME lifecycle blocked": value["quantum_lifecycle"]["QME_RESTORED"] == "NOT_REACHED",
    }
    failed = [key for key, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"post-freeze quantum signoff failed: {failed}")
    print("Paper IX post-freeze quantum claim-boundary signoff: PASS")


if __name__ == "__main__":
    main()
