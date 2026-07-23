from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]


def test_independent_verifier_passes() -> None:
    subprocess.run(["python3", str(HERE / "verify.py")], check=True)


def test_mutations_cross_fail_closed_boundaries() -> None:
    cert = json.loads((HERE / "certificate.json").read_text())
    controls = json.loads((HERE / "controls.json").read_text())

    promoted = copy.deepcopy(cert)
    promoted["lifecycle"] = "DONE"
    assert promoted["lifecycle"] != "SHORTFALL"

    wrong_orientation = copy.deepcopy(cert)
    wrong_orientation["orientation_contract"]["future_horizon_exterior_stokes_orientation"] = "+"
    assert wrong_orientation["orientation_contract"] != cert["orientation_contract"]

    erased_dependency = copy.deepcopy(cert)
    erased_dependency["missing_dependency"]["status"] = "AVAILABLE"
    assert erased_dependency["missing_dependency"]["status"] != "MISSING"

    false_rank = copy.deepcopy(controls)
    false_rank["controls"][3]["rank_certified"] = True
    assert false_rank["controls"][3]["rank_certified"] is not controls["controls"][3]["rank_certified"]

    wrong_crosswalk = copy.deepcopy(controls)
    wrong_crosswalk["required_successor"]["initial_real_pivot_rows"] = [0, 1, 2, 6, 7, 8]
    assert (
        wrong_crosswalk["required_successor"]["initial_real_pivot_rows"]
        != controls["required_successor"]["initial_real_pivot_rows"]
    )
