from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator
import pytest

from d_quotient_classical.compensator import two_phase_counterflow_repaired_q70_health_assembly as producer


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_PAYLOAD_V1.json"
CERT_SCHEMA = ROOT / "d_quotient_classical/compensator/schema/two-phase-counterflow-repaired-q70-health-assembly-maximal-domain-v1.schema.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/compensator/schema/two-phase-counterflow-repaired-q70-health-assembly-maximal-domain-payload-v1.schema.json"
ATLAS = ROOT / "residual_atlas/two-phase-counterflow-repaired-q70-health-assembly-maximal-domain-fragment-v1.json"
RECEIPT = ROOT / "d_quotient_classical/compensator/receipts/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_V1_TIER_RECEIPT.json"


def _run(*parts: str) -> None:
    subprocess.run(parts, cwd=ROOT, check=True, timeout=20)


def test_producer_check() -> None:
    _run(sys.executable, "d_quotient_classical/compensator/two_phase_counterflow_repaired_q70_health_assembly.py", "--check")


def test_independent_replay() -> None:
    _run(sys.executable, "d_quotient_classical/compensator/verify_two_phase_counterflow_repaired_q70_health_assembly.py")


def test_strict_schemas() -> None:
    for data_path, schema_path in ((CERT, CERT_SCHEMA), (PAYLOAD, PAYLOAD_SCHEMA)):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(json.loads(data_path.read_text()))


def test_exact_partition_dimensions_and_fail_closed_remainder() -> None:
    payload = json.loads(PAYLOAD.read_text())
    blocks = payload["certified_block_ledger"]
    assert [block["two_j"] for block in blocks] == [0, 1, 2]
    assert [block["q70_total_dimension"] for block in blocks] == [70, 280, 630]
    assert [block["retained_total_dimension"] for block in blocks] == [26, 104, 234]
    assert [block["physical_total_dimension"] for block in blocks] == [7, 28, 63]
    assert payload["certified_domain_summary"]["q70_total_dimension_all_m_k"] == 980
    assert payload["certified_domain_summary"]["physical_total_dimension_all_m_k"] == 98
    assert payload["remaining_carrier"]["two_j_domain"] == "all integers two_j >= 3"
    assert payload["remaining_carrier"]["physical_quotient_status"] == "NO_CERTIFIED_MAP"
    assert payload["terminal_verdict"]["health_obstruction_complete"] is True
    assert payload["terminal_verdict"]["all_isotype_spectral_census_complete"] is False


def test_input_guards_reject_generic_scope_promotion() -> None:
    _, values = producer._load_imports()
    mutated = copy.deepcopy(values)
    mutated["generic_health"]["claim_boundary"]["does_not_establish"] = ["nonlinear instability"]
    with pytest.raises(AssertionError, match="higher-j fail-closed"):
        producer._validate_inputs(mutated)


def test_atlas_is_generated_and_fail_closed() -> None:
    _run(sys.executable, "d_quotient_classical/atlas/generate_two_phase_counterflow_repaired_q70_health_assembly_atlas_fragment.py", "--check")
    _run(sys.executable, "residual_atlas/validate_fragment.py", str(ATLAS.relative_to(ROOT)))
    atlas = json.loads(ATLAS.read_text())
    remaining = next(entry for entry in atlas["entries"] if entry["id"].endswith("remaining_j_ge_three_halves"))
    assert remaining["descriptions"]["symplectic"] == "NO_CERTIFIED_MAP"
    assert remaining["descriptions"]["quantum"] == "NO_CERTIFIED_MAP"
    assert remaining["mode_data"]["dispersion"]["status"] == "NO_CERTIFIED_MAP"


def test_receipt_artifact_hashes() -> None:
    receipt = json.loads(RECEIPT.read_text())
    for artifact in receipt["artifacts"]:
        actual = hashlib.sha256((ROOT / artifact["path"]).read_bytes()).hexdigest()
        assert actual == artifact["sha256"], artifact["path"]
