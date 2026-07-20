#!/usr/bin/env python3
"""Exact topology ledger and global-anomaly carrier non-definition."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPO = ROOT.parents[1]
PINS = {
    "complex_compensator_action": {
        "path": "d_quotient_classical/certificates/COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1.json",
        "source_commit": "306ff78a2001f23124d412e9a2f41531bec74f78",
        "sha256": "a537e31bf667520443903551b5bf2596dff9a1c35fade88d2ffc1e89c1e0b836",
    },
    "conditional_all_loop_QME": {
        "path": "quantum-weyl/anomalies/certificates/TAU_ADIC_ALL_LOOP_LOCAL_QME_STABILITY.json",
        "source_commit": "54c3c180ded58ec4463d8af2db341ce878ab7035",
        "sha256": "3649925e44d99bea0020f3d1c20a16c54a44f6c9714a3c273c20a6e6d8f84dbc",
    },
    "DR_MS_QAP_obstruction": {
        "path": "quantum-weyl/anomalies/certificates/TAU_ADIC_DR_MS_QAP_EVANESCENT_CLOSURE_OBSTRUCTION.json",
        "source_commit": "e2c48b7a2e96652f929845f700337a30cbf9e0ea",
        "sha256": "20915ec21d0c96534a7091b57ee2c3baf5728526a32d00de83dd75b4b94e7e5f",
    },
    "vacuum_cylinder_topology": {
        "path": "d_quotient_classical/certificates/WESS_ZUMINO_D_CARTAN_CONTRACTION_V1.json",
        "source_commit": "e15ec011688def11effb9c0b5ca3dc88fc28318b",
        "sha256": "7d55dd68a6d5460fc5abb8d0d338e56b3890de2209aa72b4a7838ac31d9b3507",
    },
    "Berger_spatial_topology": {
        "path": "quantum-weyl/lorentzian/certificates/BERGER_FREE_DILATION_HADAMARD_BISOLUTION_SEED.json",
        "source_commit": "f0363e16574d1effc3d23fb4862088695ba55a55",
        "sha256": "4c0f6650a627817db419c9d1c8ddf797d99258009705e7da9868fc52f41217cf",
    },
}


def _historical(pin: dict[str, str]) -> bytes:
    return subprocess.run(
        [
            "git",
            "show",
            f"{pin['source_commit']}:physics/symplectic-reconstruction/{pin['path']}",
        ],
        cwd=REPO,
        check=True,
        capture_output=True,
    ).stdout


def _product_betti(left: list[int], right: list[int]) -> list[int]:
    out = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] += a * b
    return out


def build() -> dict[str, Any]:
    for name, pin in PINS.items():
        if hashlib.sha256(_historical(pin)).hexdigest() != pin["sha256"]:
            raise ValueError(f"global-anomaly input drifted: {name}")

    betti = _product_betti([1, 1], [1, 0, 0, 1])
    if betti != [1, 1, 0, 1, 1]:
        raise ValueError("S1 x S3 Kunneth replay failed")

    value = {
        "schema": "quantum-weyl-complex-compensator-global-anomaly-carrier-preflight-v1",
        "result_id": "COMPLEX_COMPENSATOR_GLOBAL_ANOMALY_CARRIER_NONDEFINITION",
        "result_state": "EXACT_TOPOLOGY_LEDGER_COMPLETE_GLOBAL_PHASE_CARRIER_UNDEFINED",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "input_pins": PINS,
        "imported_theory": {
            "gauge_group_connected_identity": "Diff_0 semidirect C_infinity(M,R_positive)",
            "internal_phase_symmetry": "GLOBAL_U1_NOT_GAUGED",
            "internal_connection_present": False,
            "internal_U1_ghost_present": False,
            "fermion_or_chiral_pfaffian_sector_present": False,
            "local_QME_status": "CONDITIONAL_ALL_ORDER_FORMAL_LOCAL_QME_RESTORABLE",
            "declared_DR_MS_status": "OBSTRUCTED_AT_EVANESCENT_CLOSURE",
        },
        "candidate_backgrounds": [
            {
                "id": "vacuum_cylinder_periodic_Euclidean_candidate",
                "Lorentzian_topology": "R x S3",
                "Euclidean_candidate": "S1_beta x S3",
                "Euclidean_selection_status": "PERIODIC_CONTINUATION_DECLARED_BUT_FULL_CHANGED_ACTION_OPERATOR_ABSENT",
                "integral_betti_numbers": betti,
                "integral_cohomology_torsion": [],
            },
            {
                "id": "Berger_periodic_Euclidean_candidate",
                "Lorentzian_topology": "R x S3_Berger",
                "Euclidean_candidate": "S1_beta x S3_with_Berger_metric",
                "Euclidean_selection_status": "CANDIDATE_ONLY_CLASSICAL_COMPLEX_COMPENSATOR_PARENT_NOT_LANDED",
                "integral_betti_numbers": betti,
                "integral_cohomology_torsion": [],
            },
        ],
        "group_component_ledger": [
            {
                "factor": "Weyl=C_infinity(M,R_positive)",
                "connected_component": "SINGLE_CONTRACTIBLE_COMPONENT",
                "disconnected_components": "NONE",
                "global_phase_test": "NO_LARGE_WEYL_COMPONENT",
            },
            {
                "factor": "U1_phase",
                "connected_component": "CONNECTED_WITH_PI1_EQUAL_Z",
                "disconnected_components": "NONE",
                "global_phase_test": "GLOBAL_SYMMETRY_BACKGROUND_PROBE_ONLY_NOT_A_GAUGE_LOOP",
            },
            {
                "factor": "Diff",
                "connected_component": "Diff_0",
                "disconnected_components": "UNDEFINED_ALLOWED_MAPPING_CLASS_SUBGROUP_NOT_EXPORTED",
                "global_phase_test": "MAPPING_TORI_REQUIRED_FOR_EACH_ACCEPTED_COMPONENT",
            },
        ],
        "bundle_and_winding_ledger": {
            "candidate_manifold": "S1 x S3",
            "H1": "Z",
            "H2": "0",
            "circle_valued_theta_homotopy_sectors": "H1(M;Z)=Z",
            "principal_U1_Chern_classes_if_background_U1_is_introduced": "H2(M;Z)=0",
            "flat_background_U1_holonomy": "Hom(H1,U1)=U1",
            "internal_phase_gauge_bundle": "NOT_APPLICABLE_GLOBAL_SYMMETRY_NO_CONNECTION",
            "Berger_magnetic_bundle": "NOT_IMPORTED_DIFFERENT_WEYL_MAXWELL_CARRIER",
        },
        "mapping_torus_ledger": [
            {
                "source": "large_diffeomorphism",
                "family": "T_phi=(M x [0,1])/(x,1)~(phi(x),0)",
                "status": "UNDEFINED_MAPPING_CLASS_SUBGROUP_AND_LIFT_NOT_EXPORTED",
            },
            {
                "source": "Weyl",
                "family": "contractible loop in positive functions",
                "status": "NO_DISCONNECTED_COMPONENT_CANDIDATE",
            },
            {
                "source": "global_U1_phase",
                "family": "background-U1 mapping torus after adjoining a background connection",
                "status": "UNDEFINED_NOT_A_GAUGE_TRANSFORMATION_IN_IMPORTED_THEORY",
            },
            {
                "source": "theta_winding_n",
                "family": "circle-valued field sector n in H1(M;Z)",
                "status": "SECTOR_ENUMERATED_DETERMINANT_FAMILY_NOT_SUPPLIED",
            },
        ],
        "family_operator_requirements": {
            "full_changed_action_Euclidean_BV_operator": False,
            "elliptic_gauge_fixed_family_over_mapping_tori": False,
            "Berezinian_determinant_line": False,
            "real_structure_and_line_orientation": False,
            "zero_mode_and_stabilizer_policy": False,
            "regulator_compatible_with_local_QME": False,
            "required_line": "Det(K_even)^(-1/2) tensor Det(K_ghost) tensor Det(K_nonminimal) with exponents fixed by the complete BV Hessian",
            "Pfaffian_line": "NOT_APPLICABLE_NO_FERMIONIC_CHIRAL_MATTER",
        },
        "finite_index_ledger": {
            "betti_numbers_S1xS3": betti,
            "theta_winding_rank": 1,
            "principal_U1_Chern_class_rank": 0,
            "fermionic_mod_two_index": "NOT_APPLICABLE",
            "determinant_line_holonomy": "NOT_COMPUTED_FAMILY_OPERATOR_UNDEFINED",
            "global_anomaly_verdict": "UNDEFINED",
        },
        "missing_input_contract": [
            "global manifold and orientation/time-orientation choice for each Euclidean continuation",
            "allowed disconnected diffeomorphism subgroup and lifts to every field bundle",
            "decision whether global U1 is merely global or coupled to a background connection for an 't Hooft anomaly audit",
            "complete background-specific minimal/nonminimal gauge-fixed Euclidean BV Hessian family",
            "mapping-torus domains and boundary conditions for every operator block",
            "Berezinian determinant-line real structure, orientation and contour",
            "zero-mode, stabilizer and theta-winding-sector policy",
            "regulator/subtraction compatible with the local QME and evanescent completion",
        ],
        "audit_receiver": {
            "schema": "quantum-weyl-complex-compensator-global-anomaly-audit-input-v1",
            "current_payload_status": "REJECT_INCOMPLETE_CARRIER",
            "acceptance_fixture": "quantum-weyl/anomalies/fixtures/complex_compensator_global_anomaly_audit_input_accept.json",
        },
        "claim_flags": {
            "GLOBAL_ANOMALY_FREE": False,
            "NONTRIVIAL_GLOBAL_ANOMALY": False,
            "FULL_GLOBAL_GAUGE_GROUP_CLASSIFIED": False,
            "DETERMINANT_LINE_HOLONOMY_COMPUTED": False,
            "BERGER_MAGNETIC_BUNDLE_TRIVIALIZED": False,
            "LORENTZIAN_QME_CERTIFIED": False,
        },
        "next_gate": "Import the terminal changed-action classical parent, declare the global gauge group and Euclidean families, and satisfy the strict audit-input receiver before computing determinant-line holonomy.",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL preflight exactly computes "
            "the S1 x S3 cohomology, phase winding, hypothetical background-U1 "
            "bundle rank, and connected Weyl/global-phase component data. It "
            "proves that the imported U1_phase is global rather than gauged and "
            "does not replace the distinct Weyl-Maxwell Berger magnetic bundle "
            "by a trivial bundle. The global anomaly is undefined because the "
            "allowed disconnected diffeomorphisms, full changed-action elliptic "
            "family, determinant-line orientation, zero modes and compatible "
            "regulator are absent. Local H14=0 is not global anomaly freedom. "
            "No Lorentzian QME, state, positivity, particle, scattering or "
            "unitarity claim follows."
        ),
    }
    validate(value)
    return value


def validate(value: dict[str, Any]) -> None:
    diff_rows = [
        row for row in value["group_component_ledger"]
        if row["factor"] == "Diff"
    ]
    if (
        value["finite_index_ledger"]["betti_numbers_S1xS3"]
        != [1, 1, 0, 1, 1]
        or value["bundle_and_winding_ledger"]["H2"] != "0"
        or value["imported_theory"]["internal_phase_symmetry"]
        != "GLOBAL_U1_NOT_GAUGED"
        or value["audit_receiver"]["current_payload_status"]
        != "REJECT_INCOMPLETE_CARRIER"
        or len(diff_rows) != 1
        or diff_rows[0]["disconnected_components"]
        != "UNDEFINED_ALLOWED_MAPPING_CLASS_SUBGROUP_NOT_EXPORTED"
        or any(value["claim_flags"].values())
    ):
        raise ValueError("global-anomaly carrier boundary crossed")


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
