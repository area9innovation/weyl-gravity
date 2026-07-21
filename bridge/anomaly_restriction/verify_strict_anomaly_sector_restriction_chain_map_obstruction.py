#!/usr/bin/env python3
"""Method-distinct verifier for the strict-anomaly restriction obstruction."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERT = json.loads(
    (
        ROOT
        / "bridge/certificates/STRICT_ANOMALY_SECTOR_RESTRICTION_CHAIN_MAP_OBSTRUCTION_V1.json"
    ).read_text()
)


def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main() -> int:
    for pin in CERT["input_pins"].values():
        assert sha(pin["path"]) == pin["sha256"]

    berger = json.loads(
        (ROOT / CERT["input_pins"]["berger_background"]["path"]).read_text()
    )
    q = Fraction(berger["rational_fixture"]["c_squared"])
    alpha = Fraction(berger["rational_fixture"]["alpha_B"])
    direct_bach = (1 - q) ** 2 / 6
    direct_defect = alpha * direct_bach
    assert direct_bach == Fraction(961, 9600)
    assert direct_defect == Fraction(961, 1920)
    assert berger["exact_solution_family"]["metric_equations"].endswith("PASS")

    sectors = {row["sector_id"]: row for row in CERT["sector_dispositions"]}
    bw = sectors["Berger_fixed_coupling"]["exact_witness"]
    assert Fraction(bw["pure_weyl_B00"]) == direct_bach
    assert Fraction(bw["chain_defect"]) == direct_defect
    assert bw["target_coupled_metric_antifield_constant"] == "0"
    assert sectors["Berger_fixed_coupling"]["background_jet_map"] == "OBSTRUCTED"
    assert sectors["Berger_fixed_coupling"]["Cartan_generator"] == "K_Berger=D-omega R"

    minimal = json.loads(
        (ROOT / CERT["input_pins"]["cylinder_minimal_bv_chain"]["path"]).read_text()
    )
    taub = json.loads(
        (ROOT / CERT["input_pins"]["cylinder_taub_map"]["path"]).read_text()
    )
    charge = json.loads(
        (ROOT / CERT["input_pins"]["cylinder_charge_audit"]["path"]).read_text()
    )
    assert "bulk-endpoint-to-BFV time-slice transgression" in minimal["not_proved"]
    assert taub["endpoint_dimension"] == taub["moment_map_components"] == 15
    quadratic_identity = charge["charge"]["quadratic_identity"]
    assert quadratic_identity.startswith("H_D=mu_D=")
    assert "zbar M_D z" in quadratic_identity
    cw = sectors["cylinder_Taub_zero"]["exact_witness"]
    assert cw["moment_map_components"] == 15
    assert cw["moment_map_taylor_order"] == 2
    assert cw["unary_tangent_complex_changed"] is False
    assert sectors["cylinder_Taub_zero"]["charge_sector_inclusion"] == "NO_CERTIFIED_MAP"
    assert sectors["cylinder_Taub_zero"]["Cartan_generator"] == "raw_D"

    for row in sectors.values():
        assert len(row["class_images"]) == 3
        assert all(
            image["status"] == "UNDEFINED_CARRIER_OBSTRUCTION"
            and not image["zero_claimed"]
            and not image["exact_claimed"]
            and not image["nontrivial_claimed"]
            for image in row["class_images"]
        )
    verdict = CERT["receiver_contract_verdict"]
    assert not verdict["six_pullbacks_computed"]
    assert not verdict["raw_D_substituted_for_K_Berger"]
    assert not CERT["claim_flags"]["QME_RESTORED"]
    print("independent strict anomaly restriction obstruction verifier: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
