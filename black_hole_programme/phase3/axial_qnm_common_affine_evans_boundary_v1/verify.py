#!/usr/bin/env python3
"""Independent verifier for the bounded common-affine boundary attempt."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .common_affine import RUN, compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    certificate = json.loads(CERT.read_text())
    recorded = json.loads(RUN.read_text())
    reproduced = compute()
    assert reproduced == recorded
    assert recorded["gates"]["boundary_nonvanishing"]["status"] == "FAIL_CLOSED"
    assert recorded["gates"]["argument_principle_root_count"]["status"] == "NOT_RUN"
    assert len(recorded["rows"]) == 1
    assert recorded["panel_limit"] == 1
    row = recorded["rows"][0]
    assert row["omega_generator_id"] == row["horizon"]["omega_generator_id"]
    assert row["omega_generator_id"] == row["outgoing"]["omega_generator_id"]
    assert row["horizon"]["phase_convention"] == (
        "psi=exp(+I*omega*r_star)*P_H"
    )
    assert row["outgoing"]["phase_convention"] == (
        "psi=exp(-I*omega*r_star)*P_out"
    )
    assert row["horizon"]["passed"]
    assert row["outgoing"]["passed"]
    assert row["horizon"]["q_polynomial_coefficients"] is not None
    assert row["outgoing"]["q_polynomial_coefficients"] is not None
    assert row["boundary_nonvanishing"]["failure"] == (
        "COMMON_AFFINE_DELTA_ENCLOSURE_CONTAINS_ZERO"
    )
    assert row["physical_mismatch"]["modulus_lower"] == "0"
    assert certificate["run"]["sha256"] == sha(RUN)
    for item in certificate["imports"].values():
        assert sha(ROOT / item["path"]) == item["sha256"]
    assert certificate["claim_flags"]["both_endpoint_polynomial_exports_completed"]
    assert not certificate["claim_flags"][
        "panel0_Evans_boundary_nonzero_certified"
    ]
    assert not certificate["claim_flags"][
        "full_Evans_boundary_nonzero_certified"
    ]
    assert not certificate["claim_flags"]["argument_principle_root_count_certified"]
    print(
        "common-affine panel-0 verifier: PASS "
        "(endpoint exports repaired; boundary fail-closed)"
    )


if __name__ == "__main__":
    main()
