#!/usr/bin/env python3
"""Independent arithmetic and boundary checker for the BT foundations import."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def canonical_digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if value is None else value
    errors: list[str] = []
    for item in result.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append("source hash " + item.get("path", ""))

    decisions = result.get("capability_decisions", [])
    direct = [item for item in decisions if item.get("evidence_role") == "DIRECT_LOCAL"]
    supporting = [item for item in decisions if item.get("evidence_role") == "SUPPORTING"]
    expected_direct = {
        "KINEMATICS_OBSERVABLES", "STATE_EXISTENCE", "STATE_REPRESENTATION",
        "PROBABILITY_RULE", "INTERACTION_CONSTRUCTION",
    }
    if {item.get("coordinate", {}).get("obligation") for item in direct} != expected_direct or len(direct) != 5:
        errors.append("five direct capabilities")
    if len(supporting) != 1 or supporting[0].get("coordinate", {}).get("obligation") != "RECONSTRUCTION_LIMITS" or supporting[0].get("status_change") is not False:
        errors.append("supporting-only reconstruction decision")
    for item in decisions:
        coordinate = item.get("coordinate", {})
        if coordinate.get("foundation") != "FINITE_DISCRETE" or coordinate.get("carrier") != "SMOOTH_DISTRIBUTIONAL":
            errors.append("source classification")
            break

    # From 2*cosh(2a)-4*cosh(a)+2, the a^4 coefficient is 7/6;
    # a=2*lambda*t and the overall factor is 1/(2*lambda^2).
    quartic = (Fraction(7, 6) * 2**4) / 2
    witness = result.get("exact_evidence", {}).get("interaction_witness", {})
    if quartic != Fraction(28, 3) or witness.get("quartic_coefficient") != "28/3*lambda^2":
        errors.append("exact quartic witness")

    records = result.get("numerical_reproducibility_records", [])
    if len(records) != 1:
        errors.append("one numerical reproduction record")
    else:
        record = records[0]
        zmax = record.get("maximum_absolute_cross_sampler_z")
        if record.get("status") != "COARSE_REPRODUCTION_ONLY" or not isinstance(zmax, (int, float)) or not (2 < zmax < 4):
            errors.append("four-sigma pass and two-sigma non-pass")
        if record.get("continuum_status") != "NOT_ESTABLISHED":
            errors.append("continuum numerical boundary")

    interface = result.get("carrier_interface", {})
    if interface.get("id") != "EUCLIDEAN_TO_KREIN_CARRIER" or interface.get("relation") != "INCOMPATIBLE" or interface.get("status") != "CERTIFIED":
        errors.append("carrier interface classification")
    witness = interface.get("witness", {})
    if ">0" not in witness.get("source_domain", "") or "all Omega" not in witness.get("target_domain_caveat", ""):
        errors.append("carrier domain witness")
    if "No obstruction" not in interface.get("does_not_establish", ""):
        errors.append("scoped incompatibility boundary")

    flags = result.get("claim_flags", {})
    for name in (
        "five_finite_euclidean_capabilities_imported",
        "finite_partition_function_supports_normalized_gibbs_state",
        "independent_sampler_coarse_reproduction_recorded",
    ):
        if flags.get(name) is not True:
            errors.append("positive flag " + name)
    for name in (
        "full_nonperturbative_carriers_identified", "continuum_reconstruction_established",
        "physical_state_selection_established", "empirical_agreement_assessed",
        "lorentzian_transfer_established", "new_physics_dimension_established",
    ):
        if flags.get(name) is not False:
            errors.append("boundary flag " + name)
    digest = canonical_digest(result)
    if digest != result.get("canonical_digest"):
        errors.append("canonical digest")
    return errors, {"direct_capabilities": len(direct), "supporting_decisions": len(supporting), "quartic_coefficient": str(quartic), "digest": digest}


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
