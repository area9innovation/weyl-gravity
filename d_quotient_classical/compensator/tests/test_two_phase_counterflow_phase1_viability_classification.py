import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[3]


def test_producer_and_independent_verifier():
    subprocess.run(["python3", "d_quotient_classical/compensator/two_phase_counterflow_phase1_viability_classification.py", "--check"], cwd=ROOT, check=True)
    subprocess.run(["python3", "d_quotient_classical/compensator/verify_two_phase_counterflow_phase1_viability_classification.py"], cwd=ROOT, check=True)


def test_fail_closed_branch_disposition():
    p = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_PHASE1_VIABILITY_CLASSIFICATION_V1.json"
    d = json.loads(p.read_text())
    assert not d["decision"]["robust_stationary_retuning_exists"]
    assert d["decision"]["all_isotype_retuning_branch"] == "NOT_ACTIVATED"
    assert d["decision"]["familywide_green_homotopy"] == "NO_CERTIFIED_MAP"
    assert d["adversarial_mutations"]["isolated_cross_factor_collision_called_stable"].startswith("REJECTED_")
    assert d["adversarial_mutations"]["finite_harmonic_cutoff_called_uniform_health"].startswith("REJECTED_")
    assert d["adversarial_mutations"]["unstable_sector_deleted_as_gauge"].startswith("REJECTED_")


def test_strict_schema_and_atlas():
    cert = json.loads((ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_PHASE1_VIABILITY_CLASSIFICATION_V1.json").read_text())
    schema = json.loads((ROOT / "d_quotient_classical/compensator/schema/two-phase-counterflow-phase1-viability-classification-v1.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(cert)
    subprocess.run(["python3", "d_quotient_classical/atlas/generate_two_phase_counterflow_phase1_viability_classification_atlas.py", "--check"], cwd=ROOT, check=True)
    subprocess.run(["python3", "residual_atlas/validate_fragment.py", "residual_atlas/two-phase-counterflow-phase1-viability-classification-fragment-v1.json"], cwd=ROOT, check=True)
