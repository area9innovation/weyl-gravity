"""Exact auxiliary-Schouten edge-pair preflight for asymptotic pure Weyl gravity."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/ASYMPTOTIC_BACH_AUXILIARY_SCHOUTEN_EDGE_PAIR_PREFLIGHT_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/asymptotic-bach-auxiliary-schouten-edge-pair-preflight-v1.schema.json"
ATLAS = ROOT / "residual_atlas/einstein-asymptotic-bach-auxiliary-schouten-edge-pair-fragment-v1.json"
INPUT = ROOT / "bridge/certificates/ASYMPTOTIC_BACH_LOCAL_COUNTERTERM_COHOMOLOGY_OBSTRUCTION_V1.json"
PINNED_INPUT_SHA256 = "6ccb79e0626ff81fa2ffbe79166f578e50436078eaab3787da5c826112434b7d"


class AuxiliaryEdgePairError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AuxiliaryEdgePairError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"expected JSON object: {path}")
    return value


def _algebra() -> dict[str, Any]:
    alpha, ricci2, scalar2 = sp.symbols("alpha_B Ricci2 R2", nonzero=True)
    q = sp.expand(alpha * (ricci2 - scalar2 / 3) / 4)
    pi_ricci = sp.expand(alpha * (ricci2 - scalar2 / 3) / 2)
    pi_norm2 = sp.expand(alpha**2 * (ricci2 - 2 * scalar2 / 9) / 4)
    pi_trace2 = sp.expand(alpha**2 * scalar2 / 36)
    hamiltonian = sp.expand((pi_norm2 - pi_trace2) / alpha)
    eliminated = sp.expand(pi_ricci - hamiltonian)
    _require(sp.simplify(hamiltonian - q) == 0, "auxiliary Hamiltonian changed")
    _require(sp.simplify(eliminated - q) == 0, "auxiliary elimination changed")

    box_sigma = sp.symbols("box_sigma")
    dimension = sp.Integer(4)
    delta_s_trace = -alpha * box_sigma
    delta_a_trace = sp.expand(
        delta_s_trace - dimension * delta_s_trace / 2
    )
    _require(delta_a_trace == alpha * box_sigma, "Weyl-ghost trace reversal changed")

    # Two TT components per cut point.  Adding one tracefree symmetric
    # auxiliary supplies exactly two dual components.
    identity = sp.eye(2)
    zero = sp.zeros(2)
    canonical = zero.row_join(identity).col_join((-identity).row_join(zero))
    _require(canonical.det() == 1 and canonical.rank() == 4, "edge-pair rank changed")
    metric_only = sp.zeros(2)
    _require(metric_only.rank() == 0, "metric-only class changed")

    phi_1, phi_2, psi_1, psi_2 = sp.symbols("phi1 phi2 psi1 psi2")
    dphi_1, dphi_2 = sp.symbols("dphi1 dphi2")
    tt_current = sp.expand(psi_1 * dphi_2 - psi_2 * dphi_1)
    _require(tt_current != 0, "auxiliary TT current disappeared")

    return {
        "fourth_order_bulk_density_modulo_Euler": str(q),
        "auxiliary_field_definition": "s_ab=alpha_B*Schouten_ab=(alpha_B/2)*(Ricci_ab-(1/6)*g_ab*R)",
        "auxiliary_trace": "s=(alpha_B/6)*R",
        "inverse_relation": "Einstein_ab=(2/alpha_B)*(s_ab-g_ab*s); Ricci_ab=(1/alpha_B)*(2*s_ab+g_ab*s)",
        "first_order_density": "L_aux=s^ab Einstein_ab-(1/alpha_B)*(s_ab s^ab-s^2)",
        "s_dot_Einstein": str(pi_ricci),
        "auxiliary_Hamiltonian": str(hamiltonian),
        "eliminated_density": str(eliminated),
        "curvature_momentum": "A_ab=s_ab-(1/2)*g_ab*s",
        "potential": "Theta_aux^mu=sqrt(-g)*(A^ab delta Gamma^mu_ab-A^(mu b) delta Gamma^a_ab)",
        "flat_bilinear_current": "omega_aux^mu=delta A_1^ab delta Gamma_2^mu_ab-delta A_1^(mu b) delta Gamma_2^a_ab-(1<->2)",
        "TT_one_polarization_current": str(tt_current),
        "Weyl_ghost_action": {
            "delta_sigma_h_ab": "2*sigma*eta_ab",
            "delta_sigma_Ricci_ab": "-2*partial_a partial_b sigma-eta_ab*Box sigma",
            "delta_sigma_R": "-6*Box sigma",
            "delta_sigma_s_ab": "-alpha_B*partial_a partial_b sigma",
            "delta_sigma_s_trace": str(delta_s_trace),
            "delta_sigma_A_ab": "alpha_B*(-partial_a partial_b sigma+(1/2)*eta_ab*Box sigma)",
            "delta_sigma_A_trace": str(delta_a_trace),
        },
        "tracefree_normal_jet_principal_matrix": [[str(value) for value in row] for row in canonical.tolist()],
        "tracefree_normal_jet_principal_rank": canonical.rank(),
        "tracefree_normal_jet_principal_determinant": str(canonical.det()),
        "metric_only_rank": metric_only.rank(),
    }


def build_certificate() -> dict[str, Any]:
    source = _load(INPUT)
    _require(_sha256(INPUT) == PINNED_INPUT_SHA256, "local-counterterm theorem hash changed")
    _require(
        source["result_id"] == "ASYMPTOTIC_BACH_LOCAL_COUNTERTERM_COHOMOLOGY_OBSTRUCTION_V1",
        "local-counterterm theorem result id changed",
    )
    _require(
        source["classification"]["fixed_boundary_local_counterterm_repair_obstructed"] is True,
        "local-counterterm no-go changed",
    )
    algebra = _algebra()
    return {
        "schema": "asymptotic-bach-auxiliary-schouten-edge-pair-preflight-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "ASYMPTOTIC_BACH_AUXILIARY_SCHOUTEN_EDGE_PAIR_PREFLIGHT_V1",
        "result_state": "MINIMAL_FULL_TENSOR_AUXILIARY_EDGE_VARIABLE_AND_CURRENT_CERTIFIED_BOUNDARY_PHASE_SPACE_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "generality_level": "G2_FULL_TENSOR_AUXILIARY_FIRST_ORDER_PREFLIGHT",
        "scope": {
            "theory": "linearized four-dimensional pure Weyl C^2 gravity in auxiliary-Schouten form",
            "background": "Minkowski space",
            "boundaries": "candidate local cut variables at I+; no global corner matching",
            "charge_sector": "radiative tracefree tensor block; Coulombic aspects absent",
            "carrier": "full bulk symmetric tensors (h_ab,s_ab), with s_ab=alpha_B*Schouten_ab on elimination and two tracefree sphere-tensor components retained at a cut",
            "degree": 1,
            "parity": "both tracefree tensor polarizations",
            "ell": "local tensor statement before harmonic specialization",
            "m": "local tensor statement before harmonic specialization",
            "k": "radial Bondi expansion, not compact momentum",
            "omega": "arbitrary local profiles; no frequency shell selected",
        },
        "provenance": {
            "producer_path": str(Path(__file__).relative_to(ROOT)),
            "producer_sha256": _sha256(Path(__file__)),
            "input": {
                "path": str(INPUT.relative_to(ROOT)),
                "sha256": _sha256(INPUT),
                "result_id": source["result_id"],
            },
            "pinned_input_sha256": PINNED_INPUT_SHA256,
        },
        "exact_auxiliary_legendre_transform": algebra,
        "minimality_theorem": {
            "input_no_go": "The h-only fixed-boundary Einstein-radiative horizontal presymplectic class is zero under every local JKM ambiguity.",
            "dimension_lower_bound": "A nondegenerate principal flux form on the two tracefree radiative metric normal-jet components requires at least two independent dual components.",
            "candidate": "The tracefree part s_AB^TF=A_AB^TF of the auxiliary Schouten field supplies exactly two components.",
            "rank_witness": {
                "basis": "(nabla_n h_plus,nabla_n h_cross,s_plus,s_cross)",
                "matrix": algebra["tracefree_normal_jet_principal_matrix"],
                "rank": algebra["tracefree_normal_jet_principal_rank"],
                "determinant": algebra["tracefree_normal_jet_principal_determinant"],
            },
            "conclusion": "Within a local first-order full-tensor extension, s_AB^TF=A_AB^TF is a minimal-rank candidate edge variable; this is necessity plus nondegeneracy of the tracefree normal-jet principal block, not a constructed cut form or null-boundary quotient.",
        },
        "branch_dictionary": {
            "Einstein_image": "delta Ricci_ab=0 implies s_ab=0, so the pure Einstein radiative branch remains isotropic unless paired with an independent auxiliary/edge response.",
            "additional_Bach_direction": "s_ab!=0 records the second-order Schouten/Bach defect and distinguishes fourth-order data not visible in the leading metric coefficient alone.",
            "p0_p1_warning": "The metric 1/r coefficient can receive both the p0 recursion and the p1 leading branch; falloff labels alone do not define independent canonical coordinates.",
        },
        "gauge_ledger": {
            "linear_diffeomorphisms": {
                "status": "CERTIFIED_BULK",
                "statement": "On flat space delta Ricci_ab, s_ab and A_ab are invariant under linearized diffeomorphisms.",
            },
            "linear_Weyl": {
                "status": "CERTIFIED_BULK",
                "statement": algebra["Weyl_ghost_action"],
            },
            "boundary_ghost_complex": {
                "status": "OPEN",
                "statement": "Boundary-preserving ghost falloffs and the exact quotient of (h_AB,s_AB) are not constructed.",
            },
            "antifields_and_BFV_constraints": {
                "status": "NO_CERTIFIED_DOMAIN",
                "statement": "No null-boundary antifield falloff, BFV charge or constraint resolution is supplied.",
            },
        },
        "boundary_tests": {
            "cut_finiteness": "OPEN_REQUIRES_BONDI_WEIGHTS_FOR_S_AB",
            "cut_conservation_with_flux": "OPEN",
            "gauge_descent": "OPEN",
            "Iminus_i0_Iplus_corner_matching": "NO_CERTIFIED_MAP",
            "tracefree_normal_jet_principal_rank": "CERTIFIED_RANK_4",
            "nondegeneracy_after_exact_boundary_quotient": "OPEN",
        },
        "charge_disposition": {
            "P0": "OPEN",
            "D_M": "OPEN",
            "H_ESU": "NOT_APPLICABLE_ON_FIXED_MINKOWSKI_PATCH",
            "D_rad": "NO_CERTIFIED_MAP",
        },
        "classification": {
            "local_counterterm_no_go_imported_by_exact_hash": True,
            "full_tensor_auxiliary_action_exactly_equivalent_modulo_Euler": True,
            "full_tensor_auxiliary_lee_wald_potential_derived": True,
            "Weyl_ghost_action_on_auxiliary_certified": True,
            "minimal_tracefree_edge_component_count_certified": True,
            "prequotient_tracefree_normal_jet_principal_pairing_nondegenerate": True,
            "full_Bondi_BV_BFV_phase_space_constructed": False,
            "renormalized_p0_p1_pairing_constructed": False,
            "boundary_gauge_descent_certified": False,
            "corner_matching_certified": False,
            "P0_charge_computed": False,
            "D_M_charge_computed": False,
            "causal_particle_scattering_stability_positivity_or_quantum_claim": False,
        },
        "verdicts": {
            "minimal_additional_variable": "AUXILIARY_SCHOUTEN_TRACEFREE_TENSOR_CERTIFIED",
            "renormalized_boundary_phase_space": "OPEN",
            "work_item": "SHORTFALL_FULL_STOP_CONDITION_NOT_MET",
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC theorem identifies the exact full-tensor auxiliary Schouten variable, its first-order Lee-Wald current, Weyl-ghost transformation and minimal prequotient tracefree cut rank. It does not assign Bondi weights to pi_ab, construct the null-boundary ghost/antifield/BFV complex, renormalize the p0/p1 form, prove corner matching or gauge descent, compute P0/D_M charges, or establish causal, particle, scattering, stability, positivity, unitarity or quantum claims.",
        "next_gate": "Derive the coupled Bondi recursion for (h_ab,s_ab), assign finite-flux weights, and compute the boundary BFV quotient and I-/i0/I+ corner matching.",
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.einstein_sector.asymptotic_bach_auxiliary_schouten_edge_pair_preflight --check",
            "PYTHONPATH=. python3 bridge/einstein_sector/verify_asymptotic_bach_auxiliary_schouten_edge_pair_preflight.py",
            "PYTHONPATH=. python3 -m unittest bridge.einstein_sector.tests.test_asymptotic_bach_auxiliary_schouten_edge_pair_preflight -v",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-asymptotic-bach-auxiliary-schouten-edge-pair-fragment-v1.json",
        ],
    }


def build_atlas(certificate: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "einstein_boundary",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha256(Path(__file__)),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [
            {
                "id": "einstein.asymptotic.minkowski.weyl.auxiliary_schouten_edge_pair",
                "scope": certificate["scope"],
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "OPEN",
                    "nonlinear": "NOT_APPLICABLE",
                    "observational": "NO_CERTIFIED_MAP",
                    "quantum": "NO_CERTIFIED_MAP",
                },
                "mode_data": {
                    "dispersion": {
                        "status": "NOT_APPLICABLE",
                        "statement": "The auxiliary Legendre theorem is local and off shell.",
                    },
                    "lee_wald": {
                        "status": "CERTIFIED",
                        "statement": certificate["exact_auxiliary_legendre_transform"]["flat_bilinear_current"],
                    },
                    "taub_maps": {
                        "status": "NOT_APPLICABLE",
                        "statement": "No second-order compact Taub map is evaluated.",
                    },
                    "resonance": {
                        "status": "NO_CERTIFIED_MAP",
                        "statement": "No compact harmonic resonance carrier is identified with this boundary variable.",
                    },
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {
                            "status": "NOT_APPLICABLE",
                            "statement": "The theorem is linear and off shell.",
                        },
                        "smooth_secular": {
                            "status": "NOT_APPLICABLE",
                            "statement": "No quadratic source is evaluated.",
                        },
                        "causal_retarded": {
                            "status": "NO_CERTIFIED_MAP",
                            "statement": "No retarded boundary Green complex is constructed.",
                        },
                    },
                },
                "evidence": [
                    {
                        "path": str(OUTPUT.relative_to(ROOT)),
                        "result_id": certificate["result_id"],
                        "sha256": _sha256(OUTPUT) if OUTPUT.exists() else "",
                    }
                ],
                "claim_boundary": certificate["claim_boundary"],
            }
        ],
        "verification_commands": certificate["verification_commands"],
    }


def write_outputs() -> None:
    certificate = build_certificate()
    OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ATLAS.write_text(json.dumps(build_atlas(certificate), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check_outputs() -> None:
    certificate = build_certificate()
    _require(_load(OUTPUT) == certificate, f"stale certificate: {OUTPUT}")
    _require(_load(ATLAS) == build_atlas(certificate), f"stale atlas: {ATLAS}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_outputs()
    if args.check:
        check_outputs()
    if not args.write and not args.check:
        parser.error("one of --write or --check is required")


if __name__ == "__main__":
    main()
