import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]


def test_generator_and_independent_replay():
    subprocess.run(
        ["python3", "d_quotient_classical/backreacted_clock/berger_minimal_hyperbolic_branch_repair_orbit_obstruction.py", "--check"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        ["python3", "d_quotient_classical/backreacted_clock/verify_berger_minimal_hyperbolic_branch_repair_orbit_obstruction.py"],
        cwd=ROOT,
        check=True,
    )


def test_schema_and_fail_closed_flags():
    certificate = json.loads((ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_HYPERBOLIC_BRANCH_REPAIR_RESIDUAL_ORBIT_OBSTRUCTION_V1.json").read_text())
    schema = json.loads((ROOT / "d_quotient_classical/schema/berger-minimal-hyperbolic-branch-repair-residual-orbit-obstruction-v1.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    assert certificate["claim_flags"]["TWO_ROW_REAL_RESIDUAL_EQUIVARIANT_REPAIR"] is False
    assert certificate["claim_flags"]["GLOBAL_NONCONTRACTIBLE_STF2_REPAIR_CONSTRUCTED"] is False
    assert certificate["claim_flags"]["ELL3_BRANCH_PROJECTION_AUTHORIZED"] is False


def test_atlas_fragment():
    subprocess.run(
        ["python3", "residual_atlas/validate_fragment.py", "residual_atlas/berger-minimal-hyperbolic-branch-repair-residual-orbit-obstruction-fragment-v1.json"],
        cwd=ROOT,
        check=True,
    )
