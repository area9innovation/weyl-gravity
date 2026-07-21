#!/usr/bin/env python3
"""Generate the fail-closed repaired-q70 health-assembly atlas fragment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_PAYLOAD_V1.json"
OUTPUT = ROOT / "residual_atlas/two-phase-counterflow-repaired-q70-health-assembly-maximal-domain-fragment-v1.json"
GENERATOR = Path(__file__).resolve()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def _scope(carrier: str, degree: str, j: str, m: str, k: str, omega: str) -> dict[str, str]:
    return {
        "theory": "selected fixed-action two-phase counterflow theory with repaired diagonal-U1 q70 chain",
        "background": "stationary biaxial Berger R x S3, a=1, c_squared=9/40",
        "boundaries": "none; closed S3 Cauchy slices",
        "charge_sector": "unrestricted and fixed-Q_rel branches are separate; nonzero-frequency witnesses survive fixed charge",
        "carrier": carrier,
        "degree": degree,
        "parity": "Berger Peter-Weyl reality orbit; no round-S3 parity identification",
        "ell": f"NOT_APPLICABLE: Berger Peter-Weyl spin j={j}",
        "m": m,
        "k": k,
        "omega": omega,
    }


def _descriptions(symplectic: str = "CERTIFIED") -> dict[str, str]:
    return {
        "causal": "CERTIFIED",
        "symplectic": symplectic,
        "nonlinear": "OPEN",
        "observational": "NO_CERTIFIED_MAP",
        "quantum": "NO_CERTIFIED_MAP",
    }


def _physical_entry(block: dict, evidence: list[dict[str, str]]) -> dict:
    two_j = block["two_j"]
    identity = {0: "j0_real_exponential", 1: "jhalf_hamiltonian_hopf", 2: "j1_complex_frequency"}[two_j]
    return {
        "id": f"classical.counterflow.berger.repaired_q70.health_assembly.{identity}",
        "scope": _scope(
            f"complete repaired q70 j={block['j']} all-m/all-k carrier and exact nonzero-frequency physical quotient",
            f"physical H0/H1 on a {block['physical_dimension_per_fixed_m']}-dimensional quotient per fixed m",
            block["j"],
            ",".join(block["m_values"]),
            ",".join(block["k_values"]),
            "; ".join(block["unstable_factors"]),
        ),
        "descriptions": _descriptions(),
        "mode_data": {
            "dispersion": _claim("OBSTRUCTED", block["instability_class"]),
            "lee_wald": _claim("CERTIFIED", f"Every displayed unstable factor has zero pairing radical; exact action inertias are {block['energy_inertias']}."),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "No repaired-q70 nonlinear q2 source is imported by this assembly."),
            "resonance": _claim("CERTIFIED", "The imported factor audits have geometric multiplicity equal to determinant exponent and no polynomial-time partner."),
            "second_order": {
                "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                "bounded_or_finite_quasiperiodic": _claim("OBSTRUCTED", "The certified linear physical carrier already contains an exponential or Hamiltonian-Hopf direction."),
                "smooth_secular": _claim("OPEN", "Nonlinear continuation is not computed by the health assembly."),
                "causal_retarded": _claim("CERTIFIED", "The repaired support-local causal q70 parent is imported; causal solvability does not remove the instability."),
            },
        },
        "evidence": evidence,
        "claim_boundary": "This linear physical-health witness survives the fixed-Q_rel restriction. It is not an observer, particle, Hadamard, QME, positivity, unitarity or nonlinear blow-up theorem.",
    }


def build() -> dict:
    source = json.loads(SOURCE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    evidence = [
        {"path": str(SOURCE.relative_to(ROOT)), "result_id": source["result_id"], "sha256": _sha(SOURCE)},
        {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": _sha(PAYLOAD)},
    ]
    entries = [_physical_entry(block, evidence) for block in payload["certified_block_ledger"]]
    remaining = payload["remaining_carrier"]
    entries.append(
        {
            "id": "classical.counterflow.berger.repaired_q70.health_assembly.remaining_j_ge_three_halves",
            "scope": _scope(
                "repaired 70-row q70 Peter-Weyl carrier before a physical quotient",
                "full graded q70 carrier; physical H0/H1 not exported",
                ">=3/2",
                "all m=-j,...,+j",
                "all k=-j,...,+j",
                "all z; no certified characteristic divisor",
            ),
            "descriptions": _descriptions("NO_CERTIFIED_MAP"),
            "mode_data": {
                "dispersion": _claim("NO_CERTIFIED_MAP", remaining["why_remaining"]),
                "lee_wald": _claim("NO_CERTIFIED_MAP", "No descended physical pairing or inertia is exported on this remaining carrier."),
                "taub_maps": _claim("NO_CERTIFIED_MAP", "No physical quotient exists here on which to evaluate q2."),
                "resonance": _claim("NO_CERTIFIED_MAP", "No higher-j characteristic or Jordan census is certified."),
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": _claim("NO_CERTIFIED_MAP", "The physical linear carrier is not yet certified."),
                    "smooth_secular": _claim("NO_CERTIFIED_MAP", "The physical linear carrier is not yet certified."),
                    "causal_retarded": _claim("CERTIFIED", "The support-local repaired q70 causal parent is imported for all spatial coefficients, without a physical-state promotion."),
                },
            },
            "evidence": evidence,
            "claim_boundary": "The assembly proves that this is exactly the unclassified isotype domain. It does not extrapolate the j=1/2 counterexample or identify a physical mode across the missing quotient.",
        }
    )
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
            "python3 d_quotient_classical/compensator/two_phase_counterflow_repaired_q70_health_assembly.py --check",
            "python3 d_quotient_classical/compensator/verify_two_phase_counterflow_repaired_q70_health_assembly.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-repaired-q70-health-assembly-maximal-domain-fragment-v1.json",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.check:
        if json.loads(OUTPUT.read_text()) != value:
            raise AssertionError("repaired-q70 health-assembly atlas drifted")
        print("COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_ATLAS: PASS")
    else:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
