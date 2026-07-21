#!/usr/bin/env python3
"""Generate fail-closed atlas rows for repaired-q70 exceptional isotypes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_PAYLOAD_V1.json"
OUTPUT = ROOT / "residual_atlas/two-phase-counterflow-repaired-q70-low-j-stabilizer-health-fragment-v1.json"
GENERATOR = Path(__file__).resolve()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def _common_scope(carrier: str, degree: str, m: str, k: str, omega: str) -> dict[str, str]:
    return {
        "theory": "selected fixed-action two-phase counterflow theory with repaired diagonal-U1 chain",
        "background": "stationary biaxial Berger R x S3, a=1, c_squared=9/40",
        "boundaries": "none; closed S3 Cauchy slices",
        "charge_sector": "unrestricted and fixed-Q_rel dispositions are recorded separately; spatial Killing stabilizers are not the charged R_rel orbit",
        "carrier": carrier,
        "degree": degree,
        "parity": "Berger Peter-Weyl reality orbit; no round-S3 parity identification",
        "ell": "NOT_APPLICABLE: Berger Peter-Weyl spin j is used instead of a round-S3 Hodge label",
        "m": m,
        "k": k,
        "omega": omega,
    }


def _descriptions() -> dict[str, str]:
    return {
        "causal": "CERTIFIED",
        "symplectic": "CERTIFIED",
        "nonlinear": "OPEN",
        "observational": "NO_CERTIFIED_MAP",
        "quantum": "NO_CERTIFIED_MAP",
    }


def build() -> dict:
    source = json.loads(SOURCE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    evidence = [
        {"path": str(SOURCE.relative_to(ROOT)), "result_id": source["result_id"], "sha256": _sha(SOURCE)},
        {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": _sha(PAYLOAD)},
    ]
    j0_factor = "3200*z^6+12600*z^4+7605*z^2-7812"
    j1_factors = "3240*z^4+113013*z^2+986578 and the degree-ten mixed factor"
    entries = [
        {
            "id": "classical.counterflow.berger.repaired_q70.j0_spatial_killing_torsion",
            "scope": _common_scope(
                "complete repaired 70-row j=0 all-k carrier; 26-row retained complex after the explicit diagonal-U1 contraction",
                "z=0 cohomology H^-1,H^0,H^1,H^2=(1,1,1,1)",
                "m=0",
                "k=0 (the complete j=0 representation, not a truncation)",
                "z=0 only",
            ),
            "descriptions": _descriptions(),
            "mode_data": {
                "dispersion": _claim("NOT_APPLICABLE", "This row is the right-U(1) spatial Killing stabilizer torsion quartet, not a propagating characteristic mode."),
                "lee_wald": _claim("CERTIFIED", "The descended graded BV pairing has rank four and zero radical; ordinary symmetric-form inertia is not applicable."),
                "taub_maps": _claim("NO_CERTIFIED_MAP", "No repaired-q70 q2 map has been replayed on this torsion quartet."),
                "resonance": _claim("CERTIFIED", "The zero-frequency class is kept in the full complex and is not inferred by localizing the nonzero-frequency quotient."),
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": _claim("OPEN", "No q2 source has been evaluated on this stabilizer class."),
                    "smooth_secular": _claim("OPEN", "No secular correction-class theorem has been evaluated on this stabilizer class."),
                    "causal_retarded": _claim("CERTIFIED", "The repaired q70 parent retains its causal contraction; this does not turn stabilizer torsion into a particle."),
                },
            },
            "evidence": evidence,
            "claim_boundary": "This is local Diff reducibility for the right-U(1) Berger spatial Killing generator. It is not the global charged R_rel action-angle orbit and is not a particle, observer or quantum mode.",
        },
        {
            "id": "classical.counterflow.berger.repaired_q70.j0_exponential_physical_mode",
            "scope": _common_scope(
                "j=0 repaired q70 nonzero-frequency quotient, exact 7-by-7 physical Hessian",
                "physical H0/H1 at a simple characteristic factor after explicit gauge quotient",
                "m=0",
                "k=0 (complete j=0 representation)",
                j0_factor,
            ),
            "descriptions": _descriptions(),
            "mode_data": {
                "dispersion": _claim("OBSTRUCTED", f"The factor {j0_factor} has one positive y=z^2 root, hence a real exponential pair."),
                "lee_wald": _claim("CERTIFIED", "The characteristic root space has zero pairing radical; the sixth-order action representative has inertia (3,3,0)."),
                "taub_maps": _claim("NO_CERTIFIED_MAP", "No repaired-q70 q2 source has been replayed against this physical quotient."),
                "resonance": _claim("CERTIFIED", "The factor has geometric multiplicity one equal to its determinant exponent, so it has no polynomial-time Jordan partner."),
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": _claim("OBSTRUCTED", "The linear physical carrier already contains a real exponentially growing direction."),
                    "smooth_secular": _claim("OPEN", "Nonlinear continuation has not been computed."),
                    "causal_retarded": _claim("CERTIFIED", "Causal solvability of the parent coexists with, and does not remove, the physical exponential mode."),
                },
            },
            "evidence": evidence,
            "claim_boundary": "The mode survives the fixed-Q_rel restriction and is neither spatial gauge, diagonal-U1, global action-angle, nor a pairing radical. This is linear instability, not nonlinear blow-up or a particle/QME theorem.",
        },
        {
            "id": "classical.counterflow.berger.repaired_q70.j1_spatial_killing_torsion",
            "scope": _common_scope(
                "complete repaired 210-component j=1 all-k carrier per reality orbit; 78 retained components after diagonal-U1 contraction",
                "one z=0 torsion quartet per fixed m; total left-SU(2) stabilizer dimension three",
                "m=-1,0,+1 retained as the exact degeneracy orbit",
                "all k=-1,0,+1 retained; isolated k=0 is rejected by the ladder boundary",
                "z=0 only",
            ),
            "descriptions": _descriptions(),
            "mode_data": {
                "dispersion": _claim("NOT_APPLICABLE", "This row records the left-SU(2) spatial Killing stabilizer torsion, not a propagating characteristic mode."),
                "lee_wald": _claim("CERTIFIED", "Each fixed-m torsion quartet has a rank-four graded BV pairing with zero radical."),
                "taub_maps": _claim("NO_CERTIFIED_MAP", "No repaired-q70 q2 map has been replayed on these stabilizer classes."),
                "resonance": _claim("CERTIFIED", "The exact representation census accounts for all three j=1 Killing generators without deleting low-j tensor-component rows."),
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": _claim("OPEN", "No q2 source has been evaluated on the torsion classes."),
                    "smooth_secular": _claim("OPEN", "No secular correction-class theorem has been evaluated on the torsion classes."),
                    "causal_retarded": _claim("CERTIFIED", "The repaired all-k parent is causal; this is not a propagating-state assertion."),
                },
            },
            "evidence": evidence,
            "claim_boundary": "These are local spatial Diff reducibilities. They are not the charged R_rel carrier, cannot be isolated to k=0, and are not particle or quantum entries.",
        },
        {
            "id": "classical.counterflow.berger.repaired_q70.j1_complex_frequency_physical_modes",
            "scope": _common_scope(
                "j=1 repaired q70 nonzero-frequency quotient, exact 21-by-21 physical Hessian per fixed m",
                "physical H0/H1 at two exact Hamiltonian-Hopf characteristic factors",
                "m=-1,0,+1 retained as the exact degeneracy orbit",
                "all k=-1,0,+1 retained",
                j1_factors,
            ),
            "descriptions": _descriptions(),
            "mode_data": {
                "dispersion": _claim("OBSTRUCTED", f"Two exact factors contain complex-frequency roots: {j1_factors}."),
                "lee_wald": _claim("CERTIFIED", "Both multiplicity-two characteristic sectors have zero pairing radical; their two-copy action inertias are (4,4,0) and (8,12,0)."),
                "taub_maps": _claim("NO_CERTIFIED_MAP", "No repaired-q70 q2 source has been replayed against this j=1 quotient."),
                "resonance": _claim("CERTIFIED", "Every nonzero factor has factor-field nullity equal to its determinant exponent and therefore no polynomial-time Jordan partner."),
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": _claim("OBSTRUCTED", "The linear physical carrier already has exponentially growing oscillatory directions."),
                    "smooth_secular": _claim("OPEN", "Nonlinear continuation has not been computed."),
                    "causal_retarded": _claim("CERTIFIED", "The causal parent remains valid but does not remove the Hamiltonian-Hopf sectors."),
                },
            },
            "evidence": evidence,
            "claim_boundary": "The physical modes survive fixed charge and are not spatial gauge, diagonal-U1, charged R_rel orbit or pairing radical. No observer, Hadamard, QME, particle, positivity or nonlinear blow-up claim follows.",
        },
    ]
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "classical",
        "generated_by": str(GENERATOR.relative_to(ROOT)),
        "generated_by_sha256": _sha(GENERATOR),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": entries,
        "verification_commands": [
            "python3 -m d_quotient_classical.compensator.two_phase_counterflow_repaired_q70_low_j_stabilizer_health --check",
            "python3 d_quotient_classical/compensator/verify_two_phase_counterflow_repaired_q70_low_j_stabilizer_health.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-repaired-q70-low-j-stabilizer-health-fragment-v1.json",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.check:
        if json.loads(OUTPUT.read_text()) != value:
            raise AssertionError("repaired-q70 low-j atlas fragment drifted")
        print("COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_ATLAS: PASS")
    else:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
