#!/usr/bin/env python3
"""Fail-closed audit of the inputs required for the counterflow all-Hodge census."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(__file__).with_name(
    "TWO_PHASE_COUNTERFLOW_UNRESTRICTED_ALL_HODGE_HEALTH_SHORTFALL_V1.json"
)
PAYLOAD = Path(__file__).with_name(
    "TWO_PHASE_COUNTERFLOW_UNRESTRICTED_ALL_HODGE_HEALTH_SHORTFALL_PAYLOAD_V1.json"
)
IMPORTS = {
    "causal_parent": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1.json",
        "7d969e7e630f793dfe12fe07b0e98a67b2543f9aa85fa03277e491fb00296db7",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1",
        "951e88307abbea0996513773a33e66b37555272b",
    ),
    "causal_parent_payload": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1.json",
        "7c73705cc07062baf652c9cc0cb0977beda2a96d5b642fa186d6bfaeae01db57",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1",
        "951e88307abbea0996513773a33e66b37555272b",
    ),
    "background_component": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_V1.json",
        "9fa277c57a28aa831d56cec4a49774f716cb000616afde74013d9320dc0a1763",
        "TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_V1",
        "589adebec9da020a06e69cb99ce3e3fabefce123",
    ),
    "background_component_payload": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_PAYLOAD_V1.json",
        "1eb9b83d1894a1b4905024c225bcd3b872e82bcfba25ac6e70bc28671d43e629",
        "TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_PAYLOAD_V1",
        "589adebec9da020a06e69cb99ce3e3fabefce123",
    ),
    "charge_clock_complementarity": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1.json",
        "cd1fe1bf22604d17c65b941032c6b31c404bfd5cc01bd7f8399642840da01ed4",
        "TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1",
        "59764067a16a55d695fbe583724d7fb27c808b2e",
    ),
    "orbital_stability": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_SECULAR_CLOCK_ORBITAL_STABILITY_V1.json",
        "679c0b889da5ed9042414dac29bef5608b60490869d1d198c5570ab332af3bde",
        "TWO_PHASE_COUNTERFLOW_SECULAR_CLOCK_ORBITAL_STABILITY_V1",
        "dafb1bb6bcc88dbd27c2fabdaf124583d9d39a1c",
    ),
    "orbital_stability_payload": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_SECULAR_CLOCK_ORBITAL_STABILITY_PAYLOAD_V1.json",
        "f4b002b87f1e966c3f9a3f8bcf2030023e9de076854a0471bddf6a662c7b5d67",
        "TWO_PHASE_COUNTERFLOW_SECULAR_CLOCK_ORBITAL_STABILITY_PAYLOAD_V1",
        "dafb1bb6bcc88dbd27c2fabdaf124583d9d39a1c",
    ),
    "round_Hodge_preflight": (
        "d_quotient_classical/compensator/CLOSED_S3_RELATIVE_PHASE_NONHOMOGENEOUS_HODGE_PREFLIGHT_V1.json",
        "8bea19daa641aed5d771dd440624e5c7ea6128ce857ebd04c3d9b010c7acd5f9",
        "CLOSED_S3_RELATIVE_PHASE_NONHOMOGENEOUS_HODGE_PREFLIGHT_V1",
        "fcfa6f88b390a19a83f844791400f16da121e5d4",
    ),
    "retained_layout": (
        "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_LAYOUT.json",
        "3eccbcc1076eaf29ab1dc540440f8f2d3ffd5c9aa5be9265443db2997f68b1ba",
        "BERGER_RETAINED_MINIMAL_LAYOUT",
        "46d95a1f6f04e446a4d5290ec5666af3af6cd392",
    ),
    "retained_operator": (
        "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json",
        "296bd46e4d94320a6a5b227167d722da1793d1f81891dcf2e494f9b631dcdd77",
        "BERGER_RETAINED_MINIMAL_OPERATOR",
        "b37bf3bd504a7745fbe80448cd0ab578a3a135ea",
    ),
    "gauge_fixed_54": (
        "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
        "6e3baf6ecfab2c2854ccfbfb5c69122fe0bbe621ddcf8ab2a5651e3decf113e0",
        "BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION",
        "445e26663d06764bc858ff0a004ba6178acce75f",
    ),
    "residual_receiver_shortfall": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_RESIDUAL_BFV_RECEIVER_OBSTRUCTION_V1.json",
        "461474f7b9e35b75d862566f075d2cf3c6dc09c5333a5afada707304d15cbaea",
        "TWO_PHASE_COUNTERFLOW_RESIDUAL_BFV_RECEIVER_OBSTRUCTION_V1",
        "51207639e7dc6c47ecc33bdf8ce8e121cff2219f",
    ),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _load_imports() -> tuple[dict[str, Any], dict[str, Any]]:
    records: dict[str, Any] = {}
    values: dict[str, Any] = {}
    for role, (relative, expected, result_id, source_commit) in IMPORTS.items():
        path = ROOT / relative
        value = json.loads(path.read_text())
        actual = _sha(path)
        if actual != expected or value.get("result_id") != result_id:
            raise AssertionError(f"{role} import drifted")
        records[role] = {
            "path": relative,
            "sha256": actual,
            "result_id": result_id,
            "source_commit": source_commit,
            "oracle_fields_consumed": [],
        }
        values[role] = value

    if values["causal_parent"]["complete_parent"]["complete_component_rank"] != 70:
        raise AssertionError("complete 70-row parent not imported")
    if values["background_component_payload"]["stationary_component_stratification"]["solutions"][0]["q"] != "9/40":
        raise AssertionError("selected squashed Berger background drifted")
    if values["orbital_stability"]["terminal_verdict"]["all_Hodge_gate_activated"] is not True:
        raise AssertionError("orbital-stability predecessor did not activate this audit")
    if values["round_Hodge_preflight"]["scope"]["spatial_manifold"] != "round closed S3 of radius a":
        raise AssertionError("round Hodge preflight scope drifted")
    if values["retained_layout"]["flags"]["stability_proved"] is not False:
        raise AssertionError("retained layout unexpectedly claims stability")
    return records, values


def _require_absent(mapping: dict[str, Any], keys: list[str], label: str) -> list[str]:
    present = [key for key in keys if key in mapping]
    if present:
        raise AssertionError(f"{label} unexpectedly exports {present}")
    return keys


def _input_surface(values: dict[str, Any]) -> dict[str, Any]:
    parent = values["causal_parent"]
    parent_payload = values["causal_parent_payload"]
    layout = values["retained_layout"]
    operator = values["retained_operator"]
    q54 = values["gauge_fixed_54"]
    round_hodge = values["round_Hodge_preflight"]

    absent_parent = _require_absent(
        parent,
        [
            "Berger_harmonic_inclusions",
            "Berger_harmonic_projections",
            "physical_cohomology_blocks",
            "descended_pairing_Gram_matrices",
            "characteristic_block_matrices",
        ],
        "70-row parent certificate",
    )
    absent_operator = _require_absent(
        operator,
        [
            "Peter_Weyl_restrictions",
            "scalar_vector_tensor_block_decomposition",
            "physical_quotient_maps",
            "mode_characteristic_polynomials",
        ],
        "retained PBW operator certificate",
    )
    if q54["row_layout"]["total_rows"] != 54 or len(layout["component_rows"]) != 26:
        raise AssertionError("retained/complete row counts drifted")
    if layout["component_rows"][0]["row_id"] != "c_spatial_1" or layout["component_rows"][-1]["row_id"] != "c_spatial_star_3":
        raise AssertionError("retained row ordering drifted")
    if parent_payload["complete_parent"]["formula"] != "Q70=Q54 direct_sum Q_U1; Lambda70,+/-=Lambda54,+/- direct_sum S_U1":
        raise AssertionError("70-row direct-sum construction drifted")

    return {
        "selected_background": {
            "geometry": "biaxial Berger S3 with q=c_squared/a_squared=9/40",
            "round": False,
            "continuous_spatial_stabilizer": "SU(2)_L x U(1)_R",
        },
        "available": {
            "complete_local_BV_rows": 70,
            "complete_gauge_fixed_rows": 54,
            "retained_PBW_rows": 26,
            "retained_coefficient_ring": operator["coefficient_ring"],
            "support_local_advanced_retarded_chain_homotopy": True,
            "cyclic_BV_pairing": True,
            "global_relative_action_angle_normal_form": True,
            "diagonal_U1_contractible_sector": True,
        },
        "absent_from_declared_same_background_import_surface": {
            "parent_keys": absent_parent,
            "operator_keys": absent_operator,
            "first_missing_maps": ["iota_Berger,type,j,m,k", "pi_Berger,type,j,m,k"],
            "first_undefined_restriction": "q70_(type,j,m,k)=pi_(type,j,m,k) q70 iota_(type,j,m,k)",
            "consequence": "physical cocycle/boundary matrices cannot be assembled, so descended pairings, characteristic roots, Jordan chains, gradient signs, causal cones and radicals are not defined blockwise",
        },
        "round_Hodge_crosswalk_rejected": {
            "imported_scope": round_hodge["scope"]["spatial_manifold"],
            "imported_background": "round q=1",
            "target_background": "Berger q=9/40",
            "same_background_crosswalk": False,
            "reason": "the scalar, exact-one-form and coexact-one-form eigenvalues and degeneracies in the round theorem cannot be substituted for biaxial Berger tensor harmonics",
        },
        "causal_does_not_imply_positive": {
            "Green_chain_identity_available": True,
            "physical_pairing_inertia_available": False,
            "implication_rejected": "support-local causal chain contraction => positive physical carrier",
        },
    }


def _block_ledger() -> list[dict[str, Any]]:
    undefined = {
        "physical_cohomology": "NOT_COMPUTABLE_MISSING_HARMONIC_RESTRICTION",
        "pairing_and_inertia": "NOT_COMPUTABLE_MISSING_PHYSICAL_QUOTIENT",
        "characteristic_roots": "NOT_COMPUTABLE_MISSING_BLOCK_MATRIX",
        "geometric_multiplicities_and_Jordan": "NOT_COMPUTABLE_MISSING_BLOCK_MATRIX",
        "gradient_sign": "NOT_COMPUTABLE_MISSING_SPATIAL_SYMBOL_RESTRICTION",
        "causal_cone": "NOT_COMPUTABLE_MISSING_PHYSICAL_PRINCIPAL_BLOCK",
        "radical": "NOT_COMPUTABLE_MISSING_DESCENDED_PAIRING",
    }
    return [
        {
            "block": "diagonal_U1_minimal_nonminimal",
            "scope": "all local modes of the 16-row diagonal extension",
            "status": "CERTIFIED_CONTRACTIBLE_NO_PHYSICAL_COHOMOLOGY",
            "pairing": "orthogonal canonical BV summand",
            "health": "NOT_APPLICABLE_AFTER_EXACT_CONTRACTION",
        },
        {
            "block": "homogeneous_global_relative_phase_charge",
            "scope": "ell=0 unrestricted (psi,Q_rel) Darboux pair",
            "status": "CERTIFIED_ACTION_ANGLE_FAMILY_TANGENT",
            "pairing_and_inertia": "canonical rank two; augmented Hessian inertia (1,0,1)",
            "characteristic": "lambda^2, geometric multiplicity one, one size-two zero Jordan chain",
            "gradient_sign": "NOT_APPLICABLE_AT_ELL_ZERO",
            "causal_cone": "NOT_APPLICABLE_TO_FINITE_GLOBAL_PAIR",
            "radical": "zero on unrestricted pair",
            "stability": "absolute dephasing; orbital and frequency-modulated stability",
        },
        {
            "block": "nonhomogeneous_relative_phase",
            "scope": "Berger scalar harmonics beyond the global pair",
            "status": "NO_CERTIFIED_SAME_BACKGROUND_MAP",
            **undefined,
        },
        {
            "block": "retained_gravity_scalar",
            "scope": "scalar-type restrictions of the retained 26-row metric/diffeomorphism complex",
            "status": "FIRST_UNDEFINED_PHYSICAL_BLOCK",
            **undefined,
        },
        {
            "block": "retained_gravity_vector",
            "scope": "vector-type restrictions of the retained 26-row metric/diffeomorphism complex",
            "status": "NOT_REACHED_AFTER_FIRST_SHORTFALL",
            **undefined,
        },
        {
            "block": "retained_gravity_tensor",
            "scope": "tensor-type restrictions of the retained 26-row metric/diffeomorphism complex",
            "status": "NOT_REACHED_AFTER_FIRST_SHORTFALL",
            **undefined,
        },
        {
            "block": "exceptional_and_spatial_global",
            "scope": "SU(2)_L x U(1)_R exceptional harmonics and stabilizer zero modes",
            "status": "NOT_COMPUTABLE_MISSING_HARMONIC_CARRIERS_AND_SPATIAL_ACTIONS",
            **undefined,
            "additional_missing_input": "BERGER_COUNTERFLOW_70_ROW_SPATIAL_STABILIZER_LIFT_AND_MOMENT_MAPS",
        },
    ]


def _mutations() -> list[dict[str, Any]]:
    return [
        {
            "id": "ROUND_GEOMETRY_SUBSTITUTION",
            "mutation": "q=9/40 -> q=1",
            "result": "round Hodge formulas become geometrically applicable, but the imported fixed action has no positive same-action round stationary background",
            "closes_target_gate": False,
        },
        {
            "id": "PHASE_ONLY_TRUNCATION",
            "mutation": "discard retained gravity and keep the positive two-derivative relative phase class",
            "result": "the round preflight gives positive relative waves only in its declared round fixed-modulus class",
            "closes_target_gate": False,
        },
        {
            "id": "CAUSAL_IMPLIES_POSITIVE",
            "mutation": "treat the 70-row causal homotopy as a positive physical pairing",
            "result": "rejected: Green support/chain identities contain no descended physical Gram inertia",
            "closes_target_gate": False,
        },
        {
            "id": "HOMOGENEOUS_EXTRAPOLATION",
            "mutation": "assign the ell=0 action-angle characteristic and sign to every harmonic",
            "result": "rejected: no Berger harmonic restrictions or gradient matrices exist in the import surface",
            "closes_target_gate": False,
        },
    ]


def _required_export() -> dict[str, Any]:
    return {
        "result_id": "BERGER_COUNTERFLOW_70_ROW_ALL_HODGE_PHYSICAL_BLOCK_EXPORT_V1",
        "background": "same selected biaxial Berger S3 with q=9/40",
        "charge_sector": "unrestricted Q_rel; retain physical D and R_rel",
        "must_supply": [
            "complete scalar/vector/tensor/exceptional Peter-Weyl carrier bases with (j,m,k), parity, degree and real-structure labels",
            "exact rowwise inclusion and projection matrices for every 70-row tensor type",
            "restricted q70 block matrices and local Diff/Weyl/diagonal-U1 cocycle, boundary and quotient bases",
            "descended cyclic physical pairing Gram matrices and exact inertia/radical certificates",
            "time-evolution and characteristic matrices with roots, geometric multiplicities and Jordan chains",
            "spatial principal/gradient matrices and characteristic causal cones",
            "zero-mode and exceptional-block crosswalk to the rowwise SU(2)_L x U(1)_R actions",
            "independent same-background reconstruction and mutation fixtures",
        ],
        "first_acceptance_identity": "q70_(type,j,m,k)=pi_(type,j,m,k) q70 iota_(type,j,m,k) is defined and pi*iota=1 on every declared block",
        "does_not_require": ["Hadamard two-point data", "QME restoration", "particle interpretation"],
    }


def _payload(imports: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
    input_surface = _input_surface(values)
    ledger = _block_ledger()
    value = {
        "schema": "pure-weyl-two-phase-counterflow-unrestricted-all-hodge-health-shortfall-payload-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_UNRESTRICTED_ALL_HODGE_HEALTH_SHORTFALL_PAYLOAD_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "oracle_fields_consumed": [],
        "input_surface_audit": input_surface,
        "block_ledger": ledger,
        "mutations": _mutations(),
        "required_export": _required_export(),
        "terminal_verdict": {
            "result_state": "FIRST_EXACT_SHORTFALL_BERGER_HARMONIC_PHYSICAL_CARRIERS_NOT_EXPORTED",
            "complete_all_Hodge_health_verdict": "NOT_COMPUTABLE",
            "first_undefined_block": "retained_gravity_scalar",
            "first_undefined_operation": input_surface["absent_from_declared_same_background_import_surface"]["first_undefined_restriction"],
            "homogeneous_action_angle_result_retained": True,
            "causal_parent_retained": True,
            "physical_instability_found": False,
            "positive_physical_carrier_certified": False,
            "downstream_observer_and_Hadamard_consumers_activated": False,
        },
        "claim_boundary": {
            "establishes": [
                "exact content-addressed audit of the all-Hodge input surface",
                "complete separation of the contractible U1 and homogeneous action-angle blocks from unresolved Berger harmonic blocks",
                "same-background rejection of the round-S3 Hodge formulas",
                "the first undefined harmonic restriction and the minimal typed export required to resume",
            ],
            "does_not_establish": [
                "a negative-energy, exponential or gradient instability",
                "a positive or indefinite complete physical carrier",
                "nonexistence of Berger tensor harmonics or physical quotients",
                "that D or R_rel is gauge",
                "an observer, Hadamard, QME, particle, scattering, positivity or unitarity theorem",
            ],
        },
        "content_sha256": "PENDING",
    }
    value["content_sha256"] = _digest({k: v for k, v in value.items() if k != "content_sha256"})
    return value


def _certificate(imports: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    terminal = payload["terminal_verdict"]
    return {
        "schema": "pure-weyl-two-phase-counterflow-unrestricted-all-hodge-health-shortfall-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_UNRESTRICTED_ALL_HODGE_HEALTH_SHORTFALL_V1",
        "result_state": terminal["result_state"],
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": payload["dependency_tags"],
        "imports": imports,
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": "PENDING_WRITE",
            "content_sha256": payload["content_sha256"],
        },
        "terminal_verdict": terminal,
        "block_statuses": {row["block"]: row["status"] for row in payload["block_ledger"]},
        "required_export": payload["required_export"],
        "claim_boundary": payload["claim_boundary"],
        "content_hashes": {
            "input_surface_sha256": _digest(payload["input_surface_audit"]),
            "block_ledger_sha256": _digest(payload["block_ledger"]),
            "mutations_sha256": _digest(payload["mutations"]),
            "required_export_sha256": _digest(payload["required_export"]),
            "terminal_sha256": _digest(terminal),
            "boundary_sha256": _digest(payload["claim_boundary"]),
        },
    }


def validate(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    expected_payload = _digest({k: v for k, v in payload.items() if k != "content_sha256"})
    if payload["content_sha256"] != expected_payload or payload["oracle_fields_consumed"] != []:
        raise AssertionError("payload provenance failed")
    terminal = certificate["terminal_verdict"]
    if terminal["complete_all_Hodge_health_verdict"] != "NOT_COMPUTABLE":
        raise AssertionError("all-Hodge verdict silently promoted")
    if terminal["physical_instability_found"] or terminal["positive_physical_carrier_certified"]:
        raise AssertionError("input shortfall promoted to a physical sign verdict")
    if terminal["downstream_observer_and_Hadamard_consumers_activated"]:
        raise AssertionError("downstream consumer activated without physical blocks")
    if certificate["block_statuses"]["homogeneous_global_relative_phase_charge"] != "CERTIFIED_ACTION_ANGLE_FAMILY_TANGENT":
        raise AssertionError("certified homogeneous result was discarded")
    if certificate["block_statuses"]["retained_gravity_scalar"] != "FIRST_UNDEFINED_PHYSICAL_BLOCK":
        raise AssertionError("first shortfall moved")
    expected_hashes = {
        "input_surface_sha256": _digest(payload["input_surface_audit"]),
        "block_ledger_sha256": _digest(payload["block_ledger"]),
        "mutations_sha256": _digest(payload["mutations"]),
        "required_export_sha256": _digest(payload["required_export"]),
        "terminal_sha256": _digest(terminal),
        "boundary_sha256": _digest(payload["claim_boundary"]),
    }
    if certificate["content_hashes"] != expected_hashes:
        raise AssertionError("content hash ledger drifted")


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    imports, values = _load_imports()
    payload = _payload(imports, values)
    certificate = _certificate(imports, payload)
    validate(certificate, payload)
    return certificate, payload


def write() -> None:
    certificate, payload = build()
    PAYLOAD.write_text(_render(payload))
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD)
    validate(certificate, payload)
    OUTPUT.write_text(_render(certificate))


def check() -> None:
    certificate, payload = build()
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD)
    if json.loads(OUTPUT.read_text()) != certificate or json.loads(PAYLOAD.read_text()) != payload:
        raise AssertionError("stored all-Hodge shortfall artifacts drifted")
    print("TWO_PHASE_COUNTERFLOW_UNRESTRICTED_ALL_HODGE_HEALTH_SHORTFALL_V1: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else write()


if __name__ == "__main__":
    main()
