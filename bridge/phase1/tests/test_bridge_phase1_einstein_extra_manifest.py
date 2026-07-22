import json
import subprocess
import copy
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[3]


def test_producer_and_independent_verifier():
    subprocess.run(["python3", "bridge/phase1/generate_bridge_phase1_einstein_extra_manifest.py", "--check"], cwd=ROOT, check=True)
    subprocess.run(["python3", "bridge/phase1/verify_bridge_phase1_einstein_extra_manifest.py"], cwd=ROOT, check=True)


def test_strict_schema_and_mutation_guards():
    d = json.loads((ROOT / "bridge/phase1/BRIDGE_PHASE1_EINSTEIN_EXTRA_CONTRIBUTION_V1.json").read_text())
    s = json.loads((ROOT / "bridge/phase1/schema/bridge-phase1-einstein-extra-contribution-v1.schema.json").read_text())
    Draft202012Validator.check_schema(s); Draft202012Validator(s).validate(d)
    assert len(d["branch_traces"]) == 4
    assert all(v.startswith("REJECTED_") for v in d["adversarial_mutations"].values())


def test_independent_verifier_rejects_boundary_mutations(tmp_path):
    source = ROOT / "bridge/phase1/BRIDGE_PHASE1_EINSTEIN_EXTRA_CONTRIBUTION_V1.json"
    original = json.loads(source.read_text())
    mutations = []
    missing = copy.deepcopy(original); missing["branch_traces"] = missing["branch_traces"][:-1]; mutations.append(missing)
    charge = copy.deepcopy(original); next(r for r in charge["rows"] if r["row_id"] == "mixed_charge_derived_correspondence")["scope"]["charge_fibre"] = "separately neutral"; mutations.append(charge)
    smooth = copy.deepcopy(original); next(r for r in smooth["rows"] if r["row_id"] == "balanced_axial_third_order")["disposition"] = "GLOBAL_QUOTIENT_CERTIFIED_BOUNDED_REPRESENTATIVE_CERTIFIED_SMOOTH_SECULAR_CERTIFIED"; mutations.append(smooth)
    scoped = copy.deepcopy(original); next(r for r in scoped["rows"] if r["row_id"] == "balanced_axial_third_order")["representative_dependence"] = "INTRINSIC_ALL_CORRECTIONS"; mutations.append(scoped)
    for i, mutation in enumerate(mutations):
        path = tmp_path / f"mutation-{i}.json"; path.write_text(json.dumps(mutation))
        result = subprocess.run(["python3", "bridge/phase1/verify_bridge_phase1_einstein_extra_manifest.py", "--manifest", str(path)], cwd=ROOT)
        assert result.returncode != 0


def test_materiality_is_reverse_audit_only():
    d = json.loads((ROOT / "planning/paper-coverage/bridge-phase1-einstein-extra-materiality-2026-07-22.json").read_text())
    assert [r["paper"] for r in d["records"]] == ["10", "13", "91", "92"]
    assert d["records"][0]["status"] == "SCOPED_CORRECTION_REQUIRED"
    assert all(r["requested_change"] == "NONE" for r in d["records"][1:])


def test_fail_closed_atlas_fragment():
    subprocess.run(["python3", "bridge/phase1/generate_bridge_phase1_atlas_fragment.py", "--check"], cwd=ROOT, check=True)
    subprocess.run(["python3", "residual_atlas/validate_fragment.py", "residual_atlas/bridge-phase1-einstein-extra-contribution-fragment-v1.json"], cwd=ROOT, check=True)
    d = json.loads((ROOT / "residual_atlas/bridge-phase1-einstein-extra-contribution-fragment-v1.json").read_text())
    assert len(d["entries"]) == 4
    assert all(e["descriptions"]["causal"] == "NO_CERTIFIED_MAP" for e in d["entries"])
