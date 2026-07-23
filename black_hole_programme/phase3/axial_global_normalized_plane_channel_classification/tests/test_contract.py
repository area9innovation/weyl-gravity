from __future__ import annotations

from copy import deepcopy
import json
import unittest

from black_hole_programme.phase3.axial_global_normalized_plane_channel_classification.mutations import (
    mutation_cases,
    run_handoff_mutations,
    run_mutations,
)
from black_hole_programme.phase3.axial_global_normalized_plane_channel_classification.verify import (
    CERTIFICATE,
    ContractError,
    validate_handoff_shape,
    verify,
    verify_certificate,
    verify_reference_algebra,
)


def artifact() -> dict:
    return {
        "result_id": "SYNTHETIC_NORMALIZED_PLANE_WITNESS",
        "path": "black_hole_programme/example.json",
        "sha256": "1" * 64,
        "verifier_path": "black_hole_programme/verify_example.py",
        "verifier_sha256": "2" * 64,
        "replay_command": ["python3", "black_hole_programme/verify_example.py"],
        "certified_claim_path": ["claim_flags", "whole_cell_certified"],
    }


def future_handoff() -> dict:
    evidence = {
        name: artifact()
        for name in (
            "horizon_plane",
            "iminus_plane",
            "iplus_plane",
            "connection",
            "current_and_pullbacks",
            "basis_covariance",
        )
    }
    gates = {
        "plus_i_current_sign": True,
        "standard_state_order": True,
        "complex_structure_equivariance": True,
        "separate_plane_rank": True,
        "combined_endpoint_rank": True,
        "validated_connection_solve": True,
        "endpoint_cross_block_zero": True,
        "stokes_identity": True,
        "continuous_endpoint_gram_and_connection": True,
        "basis_covariance": True,
        "whole_cell": True,
    }
    return {
        "schema": "phase3-axial-normalized-r4-plane-handoff-v1",
        "status": "CERTIFIED",
        "dependency_tags": ["LORENTZIAN-CAUSAL", "REDUCED-MODE"],
        "scope": {
            "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Schwarzschild exterior",
            "ell": 2,
            "mass": "M=1",
            "matching_radius": "r=4M",
        },
        "normalization": {
            "kind": "chart-identity-normalized-r4-planes",
            "accumulated_endpoint_amplitudes": False,
            "canonical_endpoint_normalization": False,
            "basis_covariance": "Cpm' = Apm^-1*Cpm*AH; G' = A^dagger*G*A",
        },
        "state_conventions": {
            "phase": "exp(+i*omega*v)",
            "complex_state_order": ["P", "Pprime", "Q", "Qprime", "H1", "F"],
            "real_state_order": [
                "Re(P)", "Re(Pprime)", "Re(Q)", "Re(Qprime)", "Re(H1)", "Re(F)",
                "Im(P)", "Im(Pprime)", "Im(Q)", "Im(Qprime)", "Im(H1)", "Im(F)",
            ],
            "current": "F^r/(pi*alpha_W) = z^dagger*Jhat*y",
            "hermitian_current": "K4 = +i*Jhat(r=4,omega)",
            "realification": "R(K4) = [[Re(K4),-Im(K4)],[Im(K4),Re(K4)]]",
            "horizon_orientation": "GHplus = -H^dagger*K4*H",
            "stokes_identity": "GHplus+gplus-gminus=0",
        },
        "cells": [{
            "id": "q0",
            "omega_interval": ["1/2", "2049/4096"],
            "generator": 7315,
            "disposition": "CERTIFIED",
            "evidence": evidence,
            "gates": gates,
            "results": {
                "rank_Cminus": 3,
                "rank_Cplus": 3,
                "endpoint_Gplus_inertia": [1, 2, 0],
                "GHplus_inertia": [1, 2, 0],
                "gminus_inertia": [1, 2, 0],
                "gplus_inertia": [1, 2, 0],
                "negative_index_lower_bound": 2,
                "compact_frequency_negative_endpoint_flux_wavepacket": True,
                "infinite_dimensional_negative_endpoint_flux_subspace": True,
                "activation_branch": "full-rank-normalized-one-sided-J-isometry",
                "normalized_one_sided_J_isometry": True,
            },
            "shortfall": None,
        }],
        "claim_flags": {
            "normalized_plane_connection_certified": True,
            "negative_endpoint_wavepacket_certified": True,
            "canonical_amplitudes_certified": False,
            "origin_labels_certified": False,
            "frozen_endpoint_L2_equivalence_certified": False,
            "full_scattering_matrix_certified": False,
            "stability_or_CPT_certified": False,
            "quantum_ghost_or_unitarity_certified": False,
        },
        "does_not_establish": [
            "canonical endpoint or scattering amplitudes",
            "Einstein/additional origin restrictions after plane mixing",
            "equivalence with the frozen endpoint L2 normalization",
            "a full two-ended scattering matrix",
            "negative total conserved energy or a horizon-completed energy sign",
            "upper-half-plane pole exclusion or stability",
            "CPT positivity or a positive quantum state",
            "a physical quantum ghost, particles, or unitarity",
        ],
    }


class NormalizedPlaneContractTests(unittest.TestCase):
    def test_preactivation_certificate_verifies(self) -> None:
        verify()

    def test_exact_reference_algebra(self) -> None:
        verify_reference_algebra()

    def test_future_handoff_shape_accepts_normalized_claim_only(self) -> None:
        validate_handoff_shape(future_handoff())

    def test_future_handoff_rejects_canonical_amplitude_promotion(self) -> None:
        document = future_handoff()
        document["claim_flags"]["canonical_amplitudes_certified"] = True
        with self.assertRaises(ContractError):
            validate_handoff_shape(document)

    def test_future_handoff_rejects_minus_i_or_missing_gate(self) -> None:
        document = future_handoff()
        document["state_conventions"]["hermitian_current"] = (
            "K4 = -i*Jhat(r=4,omega)"
        )
        with self.assertRaises(ContractError):
            validate_handoff_shape(document)
        document = future_handoff()
        document["cells"][0]["gates"]["endpoint_cross_block_zero"] = False
        with self.assertRaises(ContractError):
            validate_handoff_shape(document)

    def test_future_handoff_rejects_status_or_shortfall_drift(self) -> None:
        document = future_handoff()
        document["status"] = "SCOPED_SHORTFALL"
        with self.assertRaises(ContractError):
            validate_handoff_shape(document)
        document = future_handoff()
        document["cells"][0]["shortfall"] = {"reason": "invented"}
        with self.assertRaises(ContractError):
            validate_handoff_shape(document)

    def test_rank_two_activates_negative_endpoint_wavepacket(self) -> None:
        document = future_handoff()
        results = document["cells"][0]["results"]
        results.update(
            rank_Cminus=2,
            rank_Cplus=2,
            gminus_inertia=[1, 1, 1],
            gplus_inertia=[1, 1, 1],
            negative_index_lower_bound=1,
            compact_frequency_negative_endpoint_flux_wavepacket=True,
            infinite_dimensional_negative_endpoint_flux_subspace=True,
            activation_branch="rank-two-endpoint-negative-flux",
            normalized_one_sided_J_isometry=False,
        )
        validate_handoff_shape(document)

    def test_rank_one_does_not_activate_negative_endpoint_wavepacket(self) -> None:
        document = future_handoff()
        results = document["cells"][0]["results"]
        results.update(
            rank_Cminus=2,
            rank_Cplus=1,
            gminus_inertia=[1, 1, 1],
            gplus_inertia=[1, 0, 2],
            negative_index_lower_bound=0,
            compact_frequency_negative_endpoint_flux_wavepacket=False,
            infinite_dimensional_negative_endpoint_flux_subspace=False,
            activation_branch="no-negative-endpoint-activation",
            normalized_one_sided_J_isometry=False,
        )
        document["claim_flags"]["negative_endpoint_wavepacket_certified"] = False
        validate_handoff_shape(document)

    def test_scoped_shortfall_is_typed_and_does_not_promote(self) -> None:
        document = future_handoff()
        document["status"] = "SCOPED_SHORTFALL"
        document["cells"][0].update(
            disposition="SCOPED_SHORTFALL",
            evidence=None,
            gates=None,
            results=None,
            shortfall={"reason": "uniform rank not enclosed"},
        )
        document["claim_flags"]["normalized_plane_connection_certified"] = False
        document["claim_flags"]["negative_endpoint_wavepacket_certified"] = False
        validate_handoff_shape(document)

    def test_all_preactivation_mutations_are_rejected(self) -> None:
        source = json.loads(CERTIFICATE.read_text())
        verify_certificate(source)
        for name, document in mutation_cases():
            with self.subTest(name=name):
                with self.assertRaises((ContractError, KeyError, TypeError)):
                    verify_certificate(document)
        self.assertEqual(run_mutations(), len(mutation_cases()))
        self.assertEqual(run_handoff_mutations(), 27)

    def test_future_handoff_rejects_weakened_limit(self) -> None:
        document = future_handoff()
        document["does_not_establish"].remove("a full two-ended scattering matrix")
        document["does_not_establish"].append(
            "some unrelated limitation retained only to satisfy array length"
        )
        with self.assertRaises(ContractError):
            validate_handoff_shape(document)


if __name__ == "__main__":
    unittest.main()
