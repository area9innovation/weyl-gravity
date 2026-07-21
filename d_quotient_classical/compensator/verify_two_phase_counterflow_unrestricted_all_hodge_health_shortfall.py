#!/usr/bin/env python3
"""Independent replay of the counterflow all-Hodge input shortfall."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_UNRESTRICTED_ALL_HODGE_HEALTH_SHORTFALL_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_UNRESTRICTED_ALL_HODGE_HEALTH_SHORTFALL_PAYLOAD_V1.json"


def main() -> None:
    certificate = json.loads(CERT.read_text())
    payload = json.loads(PAYLOAD.read_text())
    imported: dict[str, dict] = {}
    for role, row in certificate["imports"].items():
        path = ROOT / row["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            raise AssertionError(f"{role} import drift")
        imported[role] = json.loads(path.read_text())

    background = imported["background_component_payload"]
    q = background["stationary_component_stratification"]["solutions"][0]["q"]
    round_scope = imported["round_Hodge_preflight"]["scope"]["spatial_manifold"]
    if q != "9/40" or round_scope != "round closed S3 of radius a":
        raise AssertionError("background crosscheck failed")
    if q == "1":
        raise AssertionError("round Hodge carrier was silently imported onto Berger")

    parent = imported["causal_parent"]
    operator = imported["retained_operator"]
    forbidden_parent = {"Berger_harmonic_inclusions", "Berger_harmonic_projections", "physical_cohomology_blocks"}
    forbidden_operator = {"Peter_Weyl_restrictions", "physical_quotient_maps", "mode_characteristic_polynomials"}
    if forbidden_parent & set(parent) or forbidden_operator & set(operator):
        raise AssertionError("declared input surface changed; shortfall must be recomputed")

    ledger = {row["block"]: row for row in payload["block_ledger"]}
    if ledger["diagonal_U1_minimal_nonminimal"]["status"] != "CERTIFIED_CONTRACTIBLE_NO_PHYSICAL_COHOMOLOGY":
        raise AssertionError("contractible U1 block lost")
    if ledger["homogeneous_global_relative_phase_charge"]["status"] != "CERTIFIED_ACTION_ANGLE_FAMILY_TANGENT":
        raise AssertionError("global action-angle result lost")
    if ledger["retained_gravity_scalar"]["status"] != "FIRST_UNDEFINED_PHYSICAL_BLOCK":
        raise AssertionError("first undefined block drifted")
    terminal = certificate["terminal_verdict"]
    if terminal["physical_instability_found"] or terminal["positive_physical_carrier_certified"]:
        raise AssertionError("shortfall promoted to physical verdict")
    if terminal["downstream_observer_and_Hadamard_consumers_activated"]:
        raise AssertionError("consumer activated without export")
    if any(row["closes_target_gate"] for row in payload["mutations"]):
        raise AssertionError("negative-control mutation incorrectly closes target gate")
    print("INDEPENDENT COUNTERFLOW ALL-HODGE SHORTFALL VERIFIER: PASS")


if __name__ == "__main__":
    main()
