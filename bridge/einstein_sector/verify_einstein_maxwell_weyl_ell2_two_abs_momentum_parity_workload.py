#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator
from sympy.physics.wigner import wigner_3j


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_parity_workload.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_parity_workload.schema.json"
CANDIDATES = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json"


def independently_verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]

    candidates = json.loads(CANDIDATES.read_text())["candidate_ledger"]["rows"]
    multiplicity = {"q_minus": 1, "p_extra": 2, "q_plus": 1, "extra": 1}
    counts: Counter[int] = Counter()
    parity_channels = 0
    axial_coefficients = 0
    polar_coefficients = 0
    for candidate, row in zip(candidates, value["source_workload"]["rows"], strict=True):
        assert candidate["rho"] == row["rho"]
        output_ell = candidate["output_ell"]
        channel_count = (
            multiplicity[candidate["first_branch"]]
            * multiplicity[candidate["second_branch"]]
            * multiplicity[candidate["target_branch"]]
        )
        for channel in row["parity_channels"]:
            same = channel["first_parity"] == channel["second_parity"]
            expected = (
                ("polar" if output_ell % 2 == 0 else "axial")
                if same else
                ("axial" if output_ell % 2 == 0 else "polar")
            )
            assert channel["target_parity"] == expected
            assert channel["reduced_scalar_source_coefficients"] == channel_count
            m_1, m_2, output_m, encoded = channel["angular_witness_m1_m2_M_3j"]
            assert output_m == m_1 + m_2
            assert str(wigner_3j(2, 2, output_ell, m_1, m_2, -output_m)) == encoded
            assert encoded != "0"
            assert channel["axisymmetric_fixture_available"] == (output_ell % 2 == 0)
            parity_channels += 1
            counts[output_ell] += channel_count
            if expected == "axial":
                axial_coefficients += channel_count
            else:
                polar_coefficients += channel_count

    assert parity_channels == 84
    assert counts == Counter({4: 108, 3: 44, 1: 12})
    assert axial_coefficients == polar_coefficients == 82
    assert value["source_workload"]["reduced_scalar_source_coefficients"] == 164
    assert not value["classification"]["projected_source_coefficients_computed"]


if __name__ == "__main__":
    independently_verify()
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_PARITY_WORKLOAD independent verification: PASS")
