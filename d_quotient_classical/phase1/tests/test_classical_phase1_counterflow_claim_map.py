import json
import hashlib
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[3]


def test_generated_map_and_independent_audit():
    subprocess.run(["python3", "d_quotient_classical/phase1/generate_classical_phase1_counterflow_claim_map.py", "--check"], cwd=ROOT, check=True)
    subprocess.run(["python3", "d_quotient_classical/phase1/verify_classical_phase1_counterflow_claim_map.py"], cwd=ROOT, check=True)


def test_schema_and_mutations():
    d = json.loads((ROOT / "d_quotient_classical/phase1/CLASSICAL_PHASE1_COUNTERFLOW_CLAIM_MAP_V1.json").read_text())
    s = json.loads((ROOT / "d_quotient_classical/phase1/schema/classical-phase1-counterflow-claim-map-v1.schema.json").read_text())
    Draft202012Validator.check_schema(s); Draft202012Validator(s).validate(d)
    assert len(d["adversarial_mutations"]) == 5
    assert all(value.startswith("REJECTED_") for value in d["adversarial_mutations"].values())


def test_atlas_and_materiality_records():
    subprocess.run(["python3", "d_quotient_classical/atlas/generate_classical_phase1_counterflow_claim_map_atlas.py", "--check"], cwd=ROOT, check=True)
    subprocess.run(["python3", "residual_atlas/validate_fragment.py", "residual_atlas/classical-phase1-counterflow-claim-map-fragment-v1.json"], cwd=ROOT, check=True)
    p = json.loads((ROOT / "planning/paper-coverage/classical-phase1-counterflow-materiality-2026-07-21.json").read_text())
    source = ROOT / "d_quotient_classical/phase1/CLASSICAL_PHASE1_COUNTERFLOW_CLAIM_MAP_V1.json"
    assert p["source_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert [r["paper"] for r in p["records"]] == ["00", "09", "11", "12", "98", "99"]
    assert all(r["publication_edit"] == "NOT_PERFORMED_BY_CLASSICAL_FREEZE" for r in p["records"])
