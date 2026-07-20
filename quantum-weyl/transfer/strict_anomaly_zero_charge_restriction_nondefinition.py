#!/usr/bin/env python3
"""Fail-closed strict-anomaly restriction to selected zero-charge sectors."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = {
    "local_anomaly_audit": (
        "quantum-weyl/local_bv/certificates/LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT.json",
        "07bf332cf1bece92f8a041002f3c787fe7e85e798871e4878fbbc3cd7b20bd3b",
        "c6d1c0bad4d7e609fccb8dc5581fab107a819d33",
    ),
    "cylinder_restriction_preflight": (
        "quantum-weyl/cylinder/certificates/AFN0_CYLINDER_RESTRICTION_PREFLIGHT.json",
        "02691f09c945afaabca5233ee574842c3cf9219fb329ed2e03a51ce5bc124613",
        "81f535f0dd8a28bb700e5597906960e1b25e3e1a",
    ),
    "cylinder_taub_map": (
        "field_bv_identification/zero_modes/certificates/taub_obstruction_map.json",
        "72ac747c0b15c85c75f7a86d983960f305e486c96ab594c056f9b3377cfbf540",
        "9732ec1be74afd674bc50d8c1dfb37cfb1ed5dce",
    ),
    "cylinder_charge_audit": (
        "d_quotient_classical/certificates/compact_cylinder_d_charge_audit.json",
        "6e609dd850049fb7b85867033dbdce0b2b214f2d5196665015f8e2b552d493e4",
        "4a2e94986b849bfc1b9efca5c9fae825289eb55a",
    ),
    "Berger_background": (
        "d_quotient_classical/certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json",
        "35e1bb8a56b0591b3dd00aa8f22c328ad826ecd341c290564cfd1a68fcc3e687",
        "bb5738d6e3e30a68adcc9a70c35dac089079e3db",
    ),
    "Berger_contraction": (
        "d_quotient_classical/certificates/BERGER_MINIMAL_34_PORTABLE_CONTRACTION.json",
        "f69d8664fb139860fb3bcb89bdf82ee1659e158f6f925535b17e2de364060db4",
        "9278ba7dffa2e8d85292c2a8cc25b03f0ca47847",
    ),
    "Berger_fixed_coupling_charge": (
        "d_quotient_classical/certificates/BERGER_FIXED_COUPLING_DELTA_CHARGE.json",
        "0ae894432b065f9f4ba116e6e2d42e69d1d60cd37dbf6ef21a14d7073c75b786",
        "cc5df8d547f7d2119282590a824ce92cd1d76d17",
    ),
    "Berger_K_Cartan": (
        "d_quotient_classical/certificates/BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE.json",
        "104ff269ddf10ed80ff796c090a2de90a40c62adb0194954e4509b200304184e",
        "b167d2bfaee02a541642fbdb360888eca31b6bf9",
    ),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _map_contract(sector: str) -> dict[str, Any]:
    if sector == "cylinder_Taub_zero":
        charge = (
            "derived common zero fibre of all fifteen quadratic moment maps; "
            "not a linear unary subcomplex"
        )
        generator = "raw_D"
        boundary = (
            "closed oriented S3 has no spatial corner; horizontal descent "
            "still requires a declared time/support or compact-time policy"
        )
    else:
        charge = (
            "fixed alpha_B and lambda smooth fluctuation complex with "
            "delta Q_R=0; the 34-to-26 contraction alone does not define "
            "a local-anomaly pullback"
        )
        generator = "K_Berger=D-omega R"
        boundary = (
            "compact Berger S3 has no spatial corner; local descent still "
            "requires the declared temporal/support policy"
        )
    return {
        "sector_id": sector,
        "local_to_background_jet_map": "MISSING",
        "charge_sector_inclusion": "MISSING_AS_CHAIN_MAP",
        "charge_sector_definition": charge,
        "local_to_residual_projection": "MISSING",
        "required_chain_identities": [
            "j s = Q_background j",
            "j d_h = d_background j",
            "Q charge_inclusion = charge_inclusion Q_charge",
            "pi_res Q_charge = Q_res pi_res",
            "descent boundary current is compatible with the declared domain",
        ],
        "domain": (
            "formal local fluctuation jets completed in h on the declared "
            "smooth background, with full Diff x Weyl ghosts and antifields"
        ),
        "boundary_policy": boundary,
        "certified_Cartan_generator": generator,
        "map_status": "UNDEFINED_MISSING_CHAIN_MAP",
    }


def build() -> dict[str, Any]:
    pins = {}
    loaded = {}
    for name, (rel, expected, commit) in PINS.items():
        path = ROOT / rel
        actual = _sha(path)
        if actual != expected:
            raise ValueError(f"input hash drifted: {name}")
        loaded[name] = json.loads(path.read_text(encoding="utf-8"))
        pins[name] = {
            "path": rel,
            "sha256": expected,
            "source_commit": commit,
        }
    if (
        loaded["local_anomaly_audit"]["result_id"]
        != "LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT"
        or loaded["cylinder_restriction_preflight"][
            "local_to_cylinder_map_status"
        ]
        != "NOT_COMPUTED"
        or loaded["Berger_contraction"]["result_id"]
        != "BERGER_MINIMAL_34_PORTABLE_CONTRACTION"
        or "K_Berger" not in loaded["Berger_K_Cartan"]["claim_boundary"]
    ):
        raise ValueError("pinned input semantic boundary drifted")

    cylinder_orders = {
        "ANOM_OMEGA_C2": {
            "first_possible_h_order": 2,
            "reason": "C(gbar)=0, so C2 starts with C1(h)^2",
        },
        "ANOM_OMEGA_E4": {
            "first_possible_h_order": 1,
            "reason": (
                "E4(gbar)=0 and the first variation is a total derivative; "
                "the full type-A descent needs the missing boundary/current map"
            ),
        },
        "ANOM_OMEGA_C_DUAL_C": {
            "first_possible_h_order": 2,
            "reason": "C(gbar)=0, so C dual C starts with C1(h) dual C1(h)",
        },
    }
    berger_orders = {
        "ANOM_OMEGA_C2": {
            "first_possible_h_order": 0,
            "reason": (
                "the pinned Berger background has "
                "C2=4(a2-c2)^2/(3a8), nonzero on its solution interval"
            ),
        },
        "ANOM_OMEGA_E4": {
            "first_possible_h_order": 1,
            "reason": (
                "the static product R x Berger-S3 has zero Euler four-form; "
                "its first variation is a transgression"
            ),
        },
        "ANOM_OMEGA_C_DUAL_C": {
            "first_possible_h_order": 1,
            "reason": (
                "the static product has no time-index curvature, so the "
                "Pontryagin four-form vanishes at order zero"
            ),
        },
    }
    pullbacks = []
    for sector, orders in (
        ("cylinder_Taub_zero", cylinder_orders),
        ("Berger_fixed_coupling", berger_orders),
    ):
        for class_id, onset in orders.items():
            pullbacks.append(
                {
                    "sector_id": sector,
                    "class_id": class_id,
                    "status": "UNDEFINED_MISSING_CHAIN_MAP",
                    "background_evaluation_used_as_pullback": False,
                    "exact_primitive": None,
                    "nontriviality_witness": None,
                    "onset_ledger": onset,
                }
            )

    value = {
        "schema": "quantum-weyl-strict-anomaly-zero-charge-restriction-nondefinition-v1",
        "result_id": "STRICT_ANOMALY_ZERO_CHARGE_RESTRICTION_NONDEFINITION",
        "result_state": "PULLBACKS_UNDEFINED_TYPED_CHAIN_MAP_RECEIVER_REQUIRED",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "input_pins": pins,
        "source_anomaly_basis": [
            "ANOM_OMEGA_C2",
            "ANOM_OMEGA_E4",
            "ANOM_OMEGA_C_DUAL_C",
        ],
        "restriction_map_contracts": [
            _map_contract("cylinder_Taub_zero"),
            _map_contract("Berger_fixed_coupling"),
        ],
        "pullback_dispositions": pullbacks,
        "Cartan_obstruction_dispositions": [
            {
                "sector_id": "cylinder_Taub_zero",
                "generator": "raw_D",
                "status": "UNDEFINED_MISSING_ANOMALY_PULLBACK",
            },
            {
                "sector_id": "Berger_fixed_coupling",
                "generator": "K_Berger=D-omega R",
                "status": "UNDEFINED_MISSING_ANOMALY_PULLBACK",
            },
            {
                "sector_id": "Berger_fixed_coupling",
                "generator": "raw_D",
                "status": "NOT_APPLICABLE_AFFINE_GENERATOR_NOT_CERTIFIED_CARTAN",
            },
        ],
        "receiver_schema": (
            "quantum-weyl/transfer/schema/"
            "strict-anomaly-sector-restriction-map-v1.schema.json"
        ),
        "producer_request": (
            "planning/forge-requests/"
            "local-anomaly-zero-charge-sector-chain-maps.json"
        ),
        "exact_checks": {
            "local_anomaly_audit_pinned_at_requested_commit": True,
            "classical_sector_artifacts_content_addressed": True,
            "background_evaluation_not_used_as_pullback": True,
            "cylinder_onset_ledger_imported": True,
            "Berger_C2_order_zero_derived_from_pinned_invariant": True,
            "raw_D_and_K_Berger_kept_distinct": True,
            "no_restricted_anomaly_freedom_claim": True,
            "no_compensator_dispensability_claim": True,
        },
        "claim_flags": {
            "CYLINDER_RESTRICTED_ANOMALY_FREE": False,
            "BERGER_RESTRICTED_ANOMALY_FREE": False,
            "ANY_PULLBACK_COMPUTED": False,
            "ANY_CARTAN_ANOMALY_COMPUTED": False,
            "WZ_COMPENSATOR_DISPENSABLE_IN_SECTOR": False,
            "LORENTZIAN_QME_CERTIFIED": False,
        },
        "next_gate": (
            "Supply receiver-valid local-to-background, derived charge-sector "
            "and residual projection chain maps with descent boundary data; "
            "then compute the six pullbacks and the two distinct Cartan defects."
        ),
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/REDUCED-MODE result pins the complete local "
            "strict anomaly basis and the selected classical sector data, but "
            "proves that their cohomological pullbacks are undefined because "
            "the local-to-background and charge-to-residual chain maps are "
            "absent. Background vanishing and perturbative onset are not "
            "cohomological triviality. No sector anomaly freedom, primitive, "
            "Cartan anomaly, compensator dispensability, Lorentzian QME, "
            "state, particle, positivity or unitarity result follows."
        ),
    }
    validate(value)
    return value


def validate(value: dict[str, Any]) -> None:
    if len(value["pullback_dispositions"]) != 6:
        raise ValueError("six sector/class pullbacks required")
    if any(
        row["status"] != "UNDEFINED_MISSING_CHAIN_MAP"
        or row["background_evaluation_used_as_pullback"]
        or row["exact_primitive"] is not None
        or row["nontriviality_witness"] is not None
        for row in value["pullback_dispositions"]
    ):
        raise ValueError("missing pullback was promoted")
    cartan = {
        (row["sector_id"], row["generator"]): row["status"]
        for row in value["Cartan_obstruction_dispositions"]
    }
    if (
        cartan[("cylinder_Taub_zero", "raw_D")]
        != "UNDEFINED_MISSING_ANOMALY_PULLBACK"
        or cartan[("Berger_fixed_coupling", "K_Berger=D-omega R")]
        != "UNDEFINED_MISSING_ANOMALY_PULLBACK"
        or cartan[("Berger_fixed_coupling", "raw_D")]
        != "NOT_APPLICABLE_AFFINE_GENERATOR_NOT_CERTIFIED_CARTAN"
    ):
        raise ValueError("raw-D/K_Berger distinction drifted")
    if not all(value["exact_checks"].values()) or any(
        value["claim_flags"].values()
    ):
        raise ValueError("restriction nondefinition boundary over-promoted")


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
