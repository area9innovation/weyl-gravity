#!/usr/bin/env python3
"""Adversarial mutations for the normalized-plane preactivation contract."""
from __future__ import annotations

from copy import deepcopy
import json

from .verify import (
    CERTIFICATE,
    ContractError,
    validate_handoff_shape,
    verify_certificate,
)


def mutation_cases() -> list[tuple[str, dict]]:
    source = json.loads(CERTIFICATE.read_text())
    cases: list[tuple[str, dict]] = []

    def add(name: str, mutate) -> None:
        document = deepcopy(source)
        mutate(document)
        cases.append((name, document))

    add(
        "minus-i-current",
        lambda d: d["normalization_contract"]["current"].update(
            hermitian="K4 = -i*Jhat(r=4,omega)"
        ),
    )
    add(
        "wrong-horizon-orientation",
        lambda d: d["normalization_contract"]["pullbacks"].update(
            GHplus="H^dagger*K4*H"
        ),
    )
    add(
        "drop-cross-block",
        lambda d: d["normalization_contract"]["pullbacks"].pop("cross"),
    )
    add(
        "wrong-basis-covariance",
        lambda d: d["normalization_contract"]["connection"].update(
            basis_covariance="Cpm' = Apm*Cpm*AH"
        ),
    )
    add(
        "promote-normalized-connection",
        lambda d: d["claim_flags"].update(
            normalized_plane_connection_certified=True
        ),
    )
    add(
        "promote-canonical-amplitudes",
        lambda d: d["claim_flags"].update(
            canonical_endpoint_amplitudes_certified=True
        ),
    )
    add(
        "promote-origin-labels",
        lambda d: d["claim_flags"].update(
            Einstein_additional_origin_labels_certified=True
        ),
    )
    add(
        "wrong-state-order",
        lambda d: d["normalization_contract"]["real_state_order"].reverse(),
    )
    add(
        "weaken-limit",
        lambda d: d["does_not_establish"].remove(
            "a full two-ended scattering matrix"
        ),
    )
    add(
        "drop-sign-mutation",
        lambda d: d["mandatory_mutations"].remove(
            "replace +i*Jhat by -i*Jhat"
        ),
    )
    add(
        "fabricate-amplitudes",
        lambda d: d["normalization_contract"].update(
            accumulated_endpoint_amplitudes_available=True
        ),
    )
    add(
        "import-hash-drift",
        lambda d: d["imports"]["arbitrary_radius_current"].update(
            sha256="0" * 64
        ),
    )
    add(
        "index-lower-bound-drift",
        lambda d: d["normalization_contract"]["index_pullback"].update(
            lower_bound="n_minus >= 0"
        ),
    )
    add(
        "drop-infinite-dimensional-refinement",
        lambda d: d["normalization_contract"]["index_pullback"].update(
            infinite_dimensional_refinement="not established"
        ),
    )
    add(
        "promote-endpoint-flux-to-total-energy",
        lambda d: d["normalization_contract"]["index_pullback"].update(
            claim_boundary="negative total conserved energy and quantum ghost"
        ),
    )
    add("premature-activation", lambda d: d.update(status="CERTIFIED"))
    return cases


def run_mutations() -> int:
    rejected = 0
    for name, document in mutation_cases():
        try:
            verify_certificate(document)
        except (ContractError, KeyError, TypeError):
            rejected += 1
        else:
            raise AssertionError(f"mutation unexpectedly passed: {name}")
    return rejected


def _artifact() -> dict:
    return {
        "result_id": "MUTATION_FIXTURE_WITNESS",
        "path": "black_hole_programme/example.json",
        "sha256": "1" * 64,
        "verifier_path": "black_hole_programme/verify_example.py",
        "verifier_sha256": "2" * 64,
        "replay_command": ["python3", "black_hole_programme/verify_example.py"],
        "certified_claim_path": ["claim_flags", "whole_cell_certified"],
    }


def _future_fixture() -> dict:
    evidence = {
        name: _artifact()
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


def run_handoff_mutations() -> int:
    source = _future_fixture()
    documents: list[tuple[str, dict]] = []
    for gate in source["cells"][0]["gates"]:
        document = deepcopy(source)
        document["cells"][0]["gates"][gate] = False
        documents.append((f"gate-{gate}", document))
    for flag in source["claim_flags"]:
        if flag in {
            "normalized_plane_connection_certified",
            "negative_endpoint_wavepacket_certified",
        }:
            continue
        document = deepcopy(source)
        document["claim_flags"][flag] = True
        documents.append((f"claim-{flag}", document))
    document = deepcopy(source)
    document["state_conventions"]["hermitian_current"] = (
        "K4 = -i*Jhat(r=4,omega)"
    )
    documents.append(("minus-i-current", document))
    document = deepcopy(source)
    document["normalization"]["canonical_endpoint_normalization"] = True
    documents.append(("fabricated-canonical-normalization", document))
    document = deepcopy(source)
    document["does_not_establish"].remove("a full two-ended scattering matrix")
    document["does_not_establish"].append("unrelated replacement limitation")
    documents.append(("weakened-full-scattering-limit", document))
    document = deepcopy(source)
    document["cells"][0]["results"]["rank_Cplus"] = 1
    documents.append(("rank-one-negative-wavepacket", document))
    document = deepcopy(source)
    document["cells"][0]["results"]["endpoint_Gplus_inertia"] = [2, 1, 0]
    documents.append(("endpoint-inertia-drift", document))
    document = deepcopy(source)
    document["cells"][0]["results"]["negative_index_lower_bound"] = 1
    documents.append(("wrong-negative-index-bound", document))
    document = deepcopy(source)
    document["cells"][0]["results"]["gplus_inertia"] = [2, 1, 0]
    documents.append(("insufficient-pullback-negative-index", document))
    document = deepcopy(source)
    document["claim_flags"]["negative_endpoint_wavepacket_certified"] = False
    documents.append(("root-negative-wavepacket-flag-drift", document))
    document = deepcopy(source)
    document["cells"][0]["results"][
        "infinite_dimensional_negative_endpoint_flux_subspace"
    ] = False
    documents.append(("drop-disjoint-support-refinement", document))
    document = deepcopy(source)
    document["does_not_establish"].remove(
        "negative total conserved energy or a horizon-completed energy sign"
    )
    document["does_not_establish"].append("unrelated energy limitation")
    documents.append(("promote-endpoint-flux-to-total-energy", document))

    rejected = 0
    for name, document in documents:
        try:
            validate_handoff_shape(document)
        except (ContractError, KeyError, TypeError):
            rejected += 1
        else:
            raise AssertionError(f"handoff mutation unexpectedly passed: {name}")
    return rejected


def main() -> int:
    count = run_mutations()
    handoff_count = run_handoff_mutations()
    print(
        f"PASS {count + handoff_count} normalized-plane mutations rejected "
        f"({count} preactivation, {handoff_count} handoff)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
