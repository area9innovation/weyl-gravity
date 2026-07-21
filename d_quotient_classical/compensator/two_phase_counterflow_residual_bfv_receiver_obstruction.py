#!/usr/bin/env python3
"""Exact activation obstruction for the counterflow residual BFV receiver.

This module derives the background stabilizer and its CE differential, then
audits the pinned 70-row causal parent for the rowwise spatial actions and
Hamiltonian moment maps required by a BFV receiver.  It deliberately does not
invent those missing operators from generator names.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name("TWO_PHASE_COUNTERFLOW_RESIDUAL_BFV_RECEIVER_OBSTRUCTION_V1.json")
PAYLOAD = Path(__file__).with_name("TWO_PHASE_COUNTERFLOW_RESIDUAL_BFV_RECEIVER_OBSTRUCTION_PAYLOAD_V1.json")

IMPORTS = {
    "fixed_charge_health": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_V1.json", "812f6a3c2308eaeef09bee25ec8c79c8f7c86de7a51383141f8cae46c2f9cae5"),
    "background_stabilizer": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_V1.json", "9fa277c57a28aa831d56cec4a49774f716cb000616afde74013d9320dc0a1763"),
    "background_payload": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_PAYLOAD_V1.json", "1eb9b83d1894a1b4905024c225bcd3b872e82bcfba25ac6e70bc28671d43e629"),
    "causal_parent": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1.json", "7d969e7e630f793dfe12fe07b0e98a67b2543f9aa85fa03277e491fb00296db7"),
    "causal_payload": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1.json", "7c73705cc07062baf652c9cc0cb0977beda2a96d5b642fa186d6bfaeae01db57"),
}

BASIS = ("L1", "L2", "L3", "R3", "K")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def imports() -> dict[str, Any]:
    result = {}
    for name, (relative, expected) in IMPORTS.items():
        path = ROOT / relative
        actual = digest(path)
        if actual != expected:
            raise AssertionError(f"import drift: {name}: {actual}")
        data = json.loads(path.read_text())
        result[name] = {"path": relative, "result_id": data["result_id"], "sha256": actual, "oracle_fields_consumed": []}
    return result


def bracket(a: str, b: str) -> dict[str, int]:
    if a == b:
        return {}
    if a.startswith("L") and b.startswith("L"):
        i, j = int(a[1]), int(b[1])
        k = 6 - i - j
        sign = 1 if (i, j) in ((1, 2), (2, 3), (3, 1)) else -1
        return {f"L{k}": sign}
    return {}


def jacobi_defects() -> list[list[str]]:
    defects = []
    for a in BASIS:
        for b in BASIS:
            for c in BASIS:
                total: dict[str, int] = {}
                for left, right in ((a, (b, c)), (b, (c, a)), (c, (a, b))):
                    for middle, coefficient in bracket(*right).items():
                        for target, value in bracket(left, middle).items():
                            total[target] = total.get(target, 0) + coefficient * value
                if any(total.values()):
                    defects.append([a, b, c])
    return defects


def ce_differential() -> dict[str, list[dict[str, Any]]]:
    # dc^k=-1/2 f^k_ij c^i c^j, stored once with i<j.
    result = {name: [] for name in BASIS}
    for i, a in enumerate(BASIS):
        for b in BASIS[i + 1:]:
            for target, coefficient in bracket(a, b).items():
                result[target].append({"coefficient": str(Fraction(-coefficient)), "ghosts": [f"c_{a}", f"c_{b}"]})
    return result


def nested_keys(value: Any, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            here = f"{prefix}.{key}" if prefix else key
            keys.add(here)
            keys |= nested_keys(child, here)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            keys |= nested_keys(child, f"{prefix}[{i}]")
    return keys


def build_payload() -> dict[str, Any]:
    pinned = imports()
    background = json.loads((ROOT / IMPORTS["background_stabilizer"][0]).read_text())
    background_payload = json.loads((ROOT / IMPORTS["background_payload"][0]).read_text())
    health = json.loads((ROOT / IMPORTS["fixed_charge_health"][0]).read_text())
    causal = json.loads((ROOT / IMPORTS["causal_parent"][0]).read_text())
    causal_payload = json.loads((ROOT / IMPORTS["causal_payload"][0]).read_text())
    if background["claim_flags"]["SO_4_2_RECEIVER"] is not False or background_payload["charge_and_stabilizer_stratification"]["residual_global_stabilizer_dimension"] != 5:
        raise AssertionError("five-dimensional stabilizer import failed")
    if health["claim_flags"]["POSITIVE_RELATIVE_CLOCK_SURVIVES"] is not False:
        raise AssertionError("fixed-charge obstruction import failed")
    if causal["complete_parent"]["complete_component_rank"] != 70:
        raise AssertionError("causal parent rank changed")
    defects = jacobi_defects()
    if defects:
        raise AssertionError(f"Jacobi defects: {defects}")

    exported = nested_keys(causal) | nested_keys(causal_payload)
    required_spatial = {
        "L1": "rowwise Lie-action operator on the 70-row carrier",
        "L2": "rowwise Lie-action operator on the 70-row carrier",
        "L3": "rowwise Lie-action operator on the 70-row carrier",
        "R3": "rowwise Lie-action operator on the 70-row carrier",
    }
    # The pinned artifacts expose K/R_rel/D/U1 Cartan prose and exact causal
    # unary data, but no serialized spatial representation or moment map.
    forbidden_hits = [key for key in exported if "spatial_lie_action_matrix" in key or "spatial_moment_map_matrix" in key]
    if forbidden_hits:
        raise AssertionError(f"unexpected spatial carrier landed: {forbidden_hits}")

    old_crosswalk = {
        "preserved_subalgebra": {
            "L1": "(R01+R23)/2",
            "L2": "(R02-R13)/2",
            "L3": "(R03+R12)/2",
            "R3": "(R03-R12)/2",
            "K": "D_old-Omega*R_rel (internal lift of old D)",
        },
        "broken_generators": ["R1=(R01-R23)/2", "R2=(R02+R13)/2", "K+_0", "K+_1", "K+_2", "K+_3", "K-_0", "K-_1", "K-_2", "K-_3"],
        "not_a_quotient_witness": "[K+_0,K-_0]=2 D_old lies in the preserved subspace, so the ten-dimensional broken complement is not an ideal",
        "classification": "five-generator stabilizer subalgebra with an internal helical lift; absence of the other ten generators is not a quotient",
    }

    return {
        "schema": "pure-weyl-two-phase-counterflow-residual-bfv-receiver-obstruction-payload-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_RESIDUAL_BFV_RECEIVER_OBSTRUCTION_PAYLOAD_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "imports": pinned,
        "automorphism_algebra": {
            "basis": list(BASIS),
            "dimension": 5,
            "isomorphism_type": "su(2)_L direct_sum u(1)_R3 direct_sum R_K",
            "nonzero_brackets": {"[L1,L2]": "L3", "[L2,L3]": "L1", "[L3,L1]": "L2"},
            "jacobi_defects": 0,
            "ce_differential": ce_differential(),
            "diagonal_U1_global_reducibility_dimension": 0,
            "diagonal_U1_reason": "the constant gauge ghost maps the Stueckelberg scalar chi nontrivially and belongs to an exact contractible pair",
        },
        "charge_and_leaf": {
            "unrestricted_moment_map_row_on_[D,R_rel,K]": ["Omega*Q_rel", "Q_rel", "0"],
            "coefficient_rank": 1,
            "kernel": ["K=D-Omega*R_rel"],
            "fixed_leaf": "delta Q_rel=0; D and R_rel become null only after the explicit derived restriction",
            "physical_relative_clock_dimension": 0,
            "D_K_identification_before_reduction": False,
        },
        "old_round_crosswalk": old_crosswalk,
        "available_receiver_data": {
            "Q70_and_cyclic_pairing": "CERTIFIED",
            "causal_Green_homotopy": "CERTIFIED",
            "K_Rrel_D_U1_Cartan_ledger": "CERTIFIED",
            "abstract_five_generator_CE_algebra": "CERTIFIED_HERE",
        },
        "missing_carrier": {
            "spatial_generators": required_spatial,
            "missing_objects": [
                "four rowwise operators L_L1,L_L2,L_L3,L_R3 on the ordered 70-row carrier",
                "their exact commutators with Q70 and cyclic skew-adjoint identities",
                "four Hamiltonian quadratic matrices M_X=-(1/2) J L_X and fixed-leaf tangency",
                "four causal Cartan contractions on the declared support class",
                "bulk-to-time-slice transgression and projection for the five-generator carrier",
            ],
            "first_undefined_identity": "[L_L1,L_L2]=L_L3 on the actual 70-row carrier",
            "consequence": "the matter representation and equivariant moment-map terms in Q_BFV cannot be assembled or tested",
            "required_export": "BERGER_COUNTERFLOW_70_ROW_SPATIAL_STABILIZER_LIFT_AND_MOMENT_MAPS",
        },
        "receiver_status": {
            "abstract_CE_nilpotency": "CERTIFIED",
            "full_BFV_nilpotency": "NOT_DEFINED_MISSING_MATTER_REPRESENTATION_AND_MOMENT_MAPS",
            "local_to_time_slice_chain_map": "NOT_DEFINED",
            "causal_Cartan_all_five_generators": "NOT_DEFINED",
            "residual_cohomology": "NOT_COMPUTED",
            "descended_pairing": "NOT_COMPUTED",
            "terminal_state": "OBSTRUCTED_MISSING_SPATIAL_STABILIZER_LIFT_AND_MOMENT_MAPS",
        },
        "claim_boundary": {
            "establishes": ["complete abstract five-generator background stabilizer and CE nilpotency", "zero diagonal-U1 global reducibility", "explicit preserved/broken round-cylinder crosswalk and non-quotient witness", "the first missing carrier identity blocking the BFV receiver"],
            "does_not_establish": ["a full residual BFV receiver", "residual cohomology or descended pairing", "an anomaly restriction", "nonlinear, Hadamard, QME, particle or asymptotic claims"],
        },
        "oracle_fields_consumed": [],
    }


def documents() -> tuple[dict[str, Any], dict[str, Any]]:
    payload = build_payload()
    payload["content_sha256"] = canonical_hash(payload)
    cert = {
        "schema": "pure-weyl-two-phase-counterflow-residual-bfv-receiver-obstruction-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_RESIDUAL_BFV_RECEIVER_OBSTRUCTION_V1",
        "result_state": payload["receiver_status"]["terminal_state"],
        "dependency_tags": payload["dependency_tags"],
        "imports": payload["imports"],
        "stabilizer_dimension": 5,
        "jacobi_defects": 0,
        "old_round_crosswalk_sha256": canonical_hash(payload["old_round_crosswalk"]),
        "missing_carrier_sha256": canonical_hash(payload["missing_carrier"]),
        "receiver_status": payload["receiver_status"],
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "content_sha256": payload["content_sha256"]},
        "claim_boundary": payload["claim_boundary"],
    }
    return cert, payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    cert, payload = documents()
    if args.check:
        if json.loads(OUT.read_text()) != cert or json.loads(PAYLOAD.read_text()) != payload:
            raise SystemExit("generated artifacts are stale")
    else:
        OUT.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
        PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print("TWO_PHASE_COUNTERFLOW_RESIDUAL_BFV_RECEIVER_OBSTRUCTION_V1: PASS")


if __name__ == "__main__":
    main()
