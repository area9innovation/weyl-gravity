import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]


def test_generated_manifest_and_independent_audit():
    subprocess.run(["python3", "nonlinear/phase1/generate_nonlinear_phase1_interaction_disposition.py", "--check"], cwd=ROOT, check=True)
    subprocess.run(["python3", "nonlinear/phase1/verify_nonlinear_phase1_interaction_disposition.py"], cwd=ROOT, check=True)


def test_schema_and_mutation_ledger():
    manifest = json.loads((ROOT / "nonlinear/phase1/NONLINEAR_PHASE1_INTERACTION_DISPOSITION_V1.json").read_text())
    schema = json.loads((ROOT / "nonlinear/phase1/schema/nonlinear-phase1-interaction-disposition-v1.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(manifest)
    assert set(manifest["adversarial_mutations"]) == {
        "stale_q2", "representative_equals_class", "physical_only_redefinition", "counterflow_healthy", "undefined_branch"
    }


def test_atlas_and_reverse_materiality():
    subprocess.run(["python3", "nonlinear/phase1/generate_nonlinear_phase1_interaction_atlas.py", "--check"], cwd=ROOT, check=True)
    subprocess.run(["python3", "residual_atlas/validate_fragment.py", "residual_atlas/nonlinear-phase1-interaction-disposition-fragment-v1.json"], cwd=ROOT, check=True)
    subprocess.run(["python3", "nonlinear/phase1/generate_nonlinear_phase1_paper_materiality.py", "--check"], cwd=ROOT, check=True)
