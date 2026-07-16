#!/usr/bin/env python3
"""Independent verification of the axial Weyl--Maxwell import boundary."""

from __future__ import annotations

from copy import deepcopy
import json

from . import einstein_maxwell_weyl_axial_import as IMPORTER
from . import einstein_maxwell_weyl_axial_import_certificate as CERTIFICATE


def main() -> int:
    checked = json.loads(CERTIFICATE.OUTPUT.read_text(encoding="utf-8"))
    expected = CERTIFICATE.build_certificate()
    if checked != expected:
        raise ValueError("axial Weyl--Maxwell import certificate is stale")
    if not checked.get("exact_import_checks") or not all(
        checked["exact_import_checks"].values()
    ):
        raise ValueError("axial Weyl--Maxwell exact import check dropped")
    if (
        checked.get("physical_interpretation", {}).get("interacting_light_model_available")
        is not False
        or checked.get("claim_flags", {}).get("PHYSICAL_PARTICLE_OR_GHOST_CLASSIFICATION")
        is not False
        or checked.get("claim_flags", {}).get("QUANTUM_CLAIM") is not False
    ):
        raise ValueError("axial Weyl--Maxwell claim boundary was promoted")

    operator = IMPORTER._git_json(IMPORTER.OPERATOR_CERTIFICATE)
    green = IMPORTER._git_json(IMPORTER.GREEN_CERTIFICATE)
    pairing = IMPORTER._git_json(IMPORTER.PAIRING_CERTIFICATE)
    Lee_Wald = IMPORTER._git_json(IMPORTER.LEE_WALD_CERTIFICATE)
    Lee_Wald_fixture = IMPORTER._git_json(IMPORTER.LEE_WALD_FIXTURE)
    schemas = {
        "operator": IMPORTER._git_json(IMPORTER.OPERATOR_SCHEMA),
        "green": IMPORTER._git_json(IMPORTER.GREEN_SCHEMA),
        "pairing": IMPORTER._git_json(IMPORTER.PAIRING_SCHEMA),
        "Lee_Wald": IMPORTER._git_json(IMPORTER.LEE_WALD_SCHEMA),
        "Lee_Wald_fixture": IMPORTER._git_json(IMPORTER.LEE_WALD_FIXTURE_SCHEMA),
    }
    registration = IMPORTER._git_json(IMPORTER.REGISTRATION)

    forged = deepcopy(green)
    forged["ungauged_current"]["space_current_terms"][0]["coefficient"] += "+1"
    try:
        IMPORTER.validate_bridge_payloads(
            operator, forged, pairing, Lee_Wald, Lee_Wald_fixture, schemas, registration
        )
    except ValueError as error:
        if "Green identity replay" not in str(error):
            raise
    else:
        raise ValueError("altered ungauged Green current was accepted")

    forged = deepcopy(pairing)
    forged["classification"]["particle_claim"] = True
    try:
        IMPORTER.validate_bridge_payloads(
            operator, green, forged, Lee_Wald, Lee_Wald_fixture, schemas, registration
        )
    except ValueError as error:
        if "claim boundary" not in str(error):
            raise
    else:
        raise ValueError("promoted particle claim was accepted")

    print("AXIAL WEYL--MAXWELL IMPORT independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
