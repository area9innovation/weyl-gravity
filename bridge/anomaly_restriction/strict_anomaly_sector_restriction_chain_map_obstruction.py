#!/usr/bin/env python3
"""Produce the exact strict-anomaly sector-restriction obstruction certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "bridge/certificates/STRICT_ANOMALY_SECTOR_RESTRICTION_CHAIN_MAP_OBSTRUCTION_V1.json"
)

PINS = {
    "terminal_nondefinition": {
        "path": "quantum-weyl/transfer/certificates/STRICT_ANOMALY_ZERO_CHARGE_RESTRICTION_NONDEFINITION.json",
        "sha256": "d3eb2d00f6b91c2204c9d68418d4280e6da706671d630e4df50926e6b42ee30b",
        "source_commit": "29140f5c6717fe98e84d2e06b783753fff8de523",
    },
    "receiver_schema": {
        "path": "quantum-weyl/transfer/schema/strict-anomaly-sector-restriction-map-v1.schema.json",
        "sha256": "02204ce211813e5491b60d44d8159141b011fd15da974c857a7d4c1bd90cb427",
        "source_commit": "29140f5c6717fe98e84d2e06b783753fff8de523",
    },
    "local_anomaly_audit": {
        "path": "quantum-weyl/local_bv/certificates/LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT.json",
        "sha256": "07bf332cf1bece92f8a041002f3c787fe7e85e798871e4878fbbc3cd7b20bd3b",
        "source_commit": "c6d1c0bad4d7e609fccb8dc5581fab107a819d33",
    },
    "cylinder_taub_map": {
        "path": "field_bv_identification/zero_modes/certificates/taub_obstruction_map.json",
        "sha256": "72ac747c0b15c85c75f7a86d983960f305e486c96ab594c056f9b3377cfbf540",
        "source_commit": "9732ec1be74afd674bc50d8c1dfb37cfb1ed5dce",
    },
    "cylinder_minimal_bv_chain": {
        "path": "field_bv_identification/certificates/minimal_bv_chain.json",
        "sha256": "3f9d04dd729c911fbe07768158d96ae411634b7a91bf70a139e8c7cf1dcd8c64",
        "source_commit": "9732ec1be74afd674bc50d8c1dfb37cfb1ed5dce",
    },
    "cylinder_charge_audit": {
        "path": "d_quotient_classical/certificates/compact_cylinder_d_charge_audit.json",
        "sha256": "6e609dd850049fb7b85867033dbdce0b2b214f2d5196665015f8e2b552d493e4",
        "source_commit": "4a2e94986b849bfc1b9efca5c9fae825289eb55a",
    },
    "berger_background": {
        "path": "d_quotient_classical/certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json",
        "sha256": "35e1bb8a56b0591b3dd00aa8f22c328ad826ecd341c290564cfd1a68fcc3e687",
        "source_commit": "bb5738d6e3e30a68adcc9a70c35dac089079e3db",
    },
    "berger_fixed_coupling_charge": {
        "path": "d_quotient_classical/certificates/BERGER_FIXED_COUPLING_DELTA_CHARGE.json",
        "sha256": "0ae894432b065f9f4ba116e6e2d42e69d1d60cd37dbf6ef21a14d7073c75b786",
        "source_commit": "cc5df8d547f7d2119282590a824ce92cd1d76d17",
    },
    "berger_contraction": {
        "path": "d_quotient_classical/certificates/BERGER_MINIMAL_34_PORTABLE_CONTRACTION.json",
        "sha256": "f69d8664fb139860fb3bcb89bdf82ee1659e158f6f925535b17e2de364060db4",
        "source_commit": "9278ba7dffa2e8d85292c2a8cc25b03f0ca47847",
    },
    "berger_k_cartan": {
        "path": "d_quotient_classical/certificates/BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE.json",
        "sha256": "104ff269ddf10ed80ff796c090a2de90a40c62adb0194954e4509b200304184e",
        "source_commit": "b167d2bfaee02a541642fbdb360888eca31b6bf9",
    },
}

ANOMALY_CLASSES = (
    "ANOM_OMEGA_C2",
    "ANOM_OMEGA_E4",
    "ANOM_OMEGA_C_DUAL_C",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_pin(name: str) -> dict:
    pin = PINS[name]
    path = ROOT / pin["path"]
    actual = digest(path)
    if actual != pin["sha256"]:
        raise AssertionError(f"{name} hash drift: {actual} != {pin['sha256']}")
    return json.loads(path.read_text())


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def build_certificate() -> dict:
    terminal = load_pin("terminal_nondefinition")
    load_pin("receiver_schema")
    anomaly = load_pin("local_anomaly_audit")
    taub = load_pin("cylinder_taub_map")
    minimal = load_pin("cylinder_minimal_bv_chain")
    cylinder_charge = load_pin("cylinder_charge_audit")
    berger = load_pin("berger_background")
    berger_charge = load_pin("berger_fixed_coupling_charge")
    load_pin("berger_contraction")
    berger_k = load_pin("berger_k_cartan")

    assert terminal["result_id"] == "STRICT_ANOMALY_ZERO_CHARGE_RESTRICTION_NONDEFINITION"
    assert anomaly["claim_flags"]["FULL_LOCAL_BV_ANOMALY_COHOMOLOGY_COMPLETE"]
    assert taub["endpoint_dimension"] == taub["moment_map_components"] == 15
    assert "bulk-endpoint-to-BFV time-slice transgression" in minimal["not_proved"]
    assert cylinder_charge["phase_spaces"]["P_Taub0"]["definition"].startswith(
        "formal common derived zero fibre"
    )
    assert berger["exact_solution_family"]["metric_equations"].endswith("PASS")
    assert berger_charge["scientific_verdict"] == "D_GAUGE"
    assert berger_k["generator"]["symbol"] == "K_Berger=D-omega R"

    q = Fraction(9, 40)
    alpha_b = Fraction(5, 1)
    bach_00 = (1 - q) ** 2 / 6
    strict_metric_antifield_constant = alpha_b * bach_00
    assert bach_00 == Fraction(961, 9600)
    assert strict_metric_antifield_constant == Fraction(961, 1920)

    undefined_images = [
        {
            "class_id": class_id,
            "status": "UNDEFINED_CARRIER_OBSTRUCTION",
            "zero_claimed": False,
            "exact_claimed": False,
            "nontrivial_claimed": False,
        }
        for class_id in ANOMALY_CLASSES
    ]

    return {
        "schema": "pure-weyl-strict-anomaly-sector-restriction-chain-map-obstruction-v1",
        "result_id": "STRICT_ANOMALY_SECTOR_RESTRICTION_CHAIN_MAP_OBSTRUCTION_V1",
        "result_state": "SPLIT_OBSTRUCTION_BERGER_HARD_CYLINDER_DERIVED_CARRIER_MISSING",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "input_pins": PINS,
        "declared_map_class": {
            "source": "strict pure-Weyl full local Diff x Weyl BV jet complex, including fields, ghosts and antifields",
            "background_rule": "unit-preserving Taylor jet substitution, identity on the metric and Diff x Weyl ghost jets, zero fluctuation sent to the declared background",
            "filtration": "antifield-number preserving at leading order",
            "receiver": "quantum-weyl-strict-anomaly-sector-restriction-map-v1",
            "receiver_payload_produced": False,
        },
        "sector_dispositions": [
            {
                "sector_id": "cylinder_Taub_zero",
                "background_jet_map": "NOT_OBSTRUCTED_HERE",
                "charge_sector_inclusion": "NO_CERTIFIED_MAP",
                "residual_projection": "NO_CERTIFIED_MAP",
                "obstruction_kind": "MISSING_DERIVED_BFV_KOSZUL_CARRIER",
                "exact_witness": {
                    "moment_map_components": 15,
                    "moment_map_taylor_order": 2,
                    "unary_tangent_complex_changed": False,
                    "required_new_generators": "eta_A, A=1,...,15, with d eta_A=mu_A",
                    "missing_identity": "bulk-to-BFV time-slice transgression tau carrying the local current to the fifteen endpoint moment maps",
                    "pinned_source_statement": "bulk-endpoint-to-BFV time-slice transgression is explicitly in minimal_bv_chain.not_proved",
                },
                "theorem": "A plain unary subcomplex or deletion of charged modes cannot represent the requested derived quadratic fibre. The current receiver cannot be populated honestly until a derived Koszul/BFV carrier and its time-slice map are supplied.",
                "scope": "This is a no-certified-map result for the pinned carrier, not a proof that no enlarged derived BV-BFV construction exists.",
                "class_images": undefined_images,
                "Cartan_generator": "raw_D",
                "Cartan_defect": "UNDEFINED_CARRIER_OBSTRUCTION",
            },
            {
                "sector_id": "Berger_fixed_coupling",
                "background_jet_map": "OBSTRUCTED",
                "charge_sector_inclusion": "NOT_REACHED",
                "residual_projection": "NOT_REACHED",
                "obstruction_kind": "FULL_BV_ANTIFIELD_CHAIN_DEFECT",
                "exact_witness": {
                    "fixture": {
                        "q": fraction_text(q),
                        "alpha_B": fraction_text(alpha_b),
                    },
                    "pure_weyl_B00": fraction_text(bach_00),
                    "source_metric_antifield_constant_alphaB_B00": fraction_text(
                        strict_metric_antifield_constant
                    ),
                    "target_coupled_metric_antifield_constant": "0",
                    "chain_defect": fraction_text(strict_metric_antifield_constant),
                    "failed_identity": "j s_PW(gstar_00)=Q_Berger j(gstar_00) at zero fluctuation",
                },
                "theorem": "The positive Berger clock background is on shell only for the matter-coupled action. It is not Bach-flat, so strict pure-Weyl expansion there is curved. No unit-preserving identity-jet full-BV chain map into the uncurved coupled Berger complex exists in the declared class.",
                "scope": "An AFN0 gauge substitution or evaluation of gravitational densities is not promoted to a full BV pullback. A new matter-coupled anomaly complex would be a changed source theory.",
                "class_images": undefined_images,
                "Cartan_generator": "K_Berger=D-omega R",
                "Cartan_defect": "UNDEFINED_SOURCE_THEORY_MISMATCH",
            },
        ],
        "receiver_contract_verdict": {
            "cylinder_receiver_valid_payload_possible_from_pinned_inputs": False,
            "berger_receiver_valid_payload_possible_in_declared_map_class": False,
            "six_pullbacks_computed": False,
            "raw_D_cylinder_Cartan_defect_computed": False,
            "K_Berger_Cartan_defect_computed": False,
            "raw_D_substituted_for_K_Berger": False,
            "background_evaluation_used_as_pullback": False,
        },
        "repair_gates": [
            {
                "sector_id": "cylinder_Taub_zero",
                "need": "construct the 15-generator derived Koszul/BFV carrier, bulk-to-time-slice transgression, and residual projection before restricting anomaly descent classes",
            },
            {
                "sector_id": "Berger_fixed_coupling",
                "need": "compute the local anomaly cohomology of the actual gravity-clock(-Maxwell) BV theory, or provide a proved action/BV morphism that cancels the displayed antifield defect",
            },
        ],
        "claim_flags": {
            "CYLINDER_RESTRICTED_ANOMALY_FREE": False,
            "BERGER_RESTRICTED_ANOMALY_FREE": False,
            "ANY_CLASS_IMAGE_ZERO_OR_EXACT": False,
            "ANY_CARTAN_DEFECT_COMPUTED": False,
            "BERGER_FULL_BV_IDENTITY_JET_MAP_OBSTRUCTED": True,
            "CYLINDER_DERIVED_BFV_KOSZUL_CARRIER_CERTIFIED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_CLAIM": False,
        },
        "does_not_establish": [
            "anomaly freedom or anomaly nontriviality on either restricted sector",
            "nonexistence of an enlarged cylinder derived BV-BFV/Koszul construction",
            "the local anomaly cohomology of the matter-coupled Berger theory",
            "a compensator verdict",
            "a Lorentzian QME, Hadamard state, positivity, particles, scattering or unitarity",
        ],
        "next_gate": "Do not rerun the six pullbacks on the old receiver. Build the cylinder derived BFV/Koszul time-slice carrier; treat Berger only after changing the source to its actual matter-coupled BV theory or proving an explicit BV action morphism.",
    }


def canonical_text(data: dict) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = canonical_text(build_certificate())
    if args.write:
        CERTIFICATE.parent.mkdir(parents=True, exist_ok=True)
        CERTIFICATE.write_text(text)
        print(f"wrote {CERTIFICATE.relative_to(ROOT)}")
        return 0
    if not CERTIFICATE.exists() or CERTIFICATE.read_text() != text:
        raise SystemExit("certificate drift")
    print("strict anomaly sector restriction obstruction: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
