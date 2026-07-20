"""Exact corner zero-mode obstruction for the minimal asymptotic Schouten pair."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/ASYMPTOTIC_BACH_SCHOUTEN_CORNER_ZERO_MODE_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/asymptotic-bach-schouten-corner-zero-mode-obstruction-v1.schema.json"
ATLAS = ROOT / "residual_atlas/einstein-asymptotic-bach-schouten-corner-zero-mode-fragment-v1.json"
INPUTS = {
    "raw": ROOT / "bridge/certificates/asymptotic_bach_raw_flux_corner_obstruction.json",
    "local_no_go": ROOT / "bridge/certificates/ASYMPTOTIC_BACH_LOCAL_COUNTERTERM_COHOMOLOGY_OBSTRUCTION_V1.json",
    "auxiliary_pair": ROOT / "bridge/certificates/ASYMPTOTIC_BACH_AUXILIARY_SCHOUTEN_EDGE_PAIR_PREFLIGHT_V1.json",
}
PINNED = {
    "raw": "1cef43665f6ff2917669d7e762e20c527b3b4b001f8c77a1581856d93c35e10c",
    "local_no_go": "6ccb79e0626ff81fa2ffbe79166f578e50436078eaab3787da5c826112434b7d",
    "auxiliary_pair": "e97bbcdf96ea9f7b47581841430399ccca77caf558acff137840a712e6a6ad43",
}


class SchoutenCornerError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SchoutenCornerError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"expected object: {path}")
    return value


def _jet_witness(order: int = 4) -> dict[str, Any]:
    # Q(u)=sum_{j=0}^N q_j u^j.  S=(alpha/2)D_u Q has coefficient
    # s_j=(alpha/2)(j+1)q_{j+1}; suppress the invertible alpha/2 factor.
    derivative = sp.zeros(order, order + 1)
    for row in range(order):
        derivative[row, row + 1] = row + 1
    _require(derivative.rank() == order, "derivative rank changed")
    kernel = derivative.nullspace()
    _require(kernel == [sp.eye(order + 1)[:, 0]], "constant kernel changed")

    selector = sp.zeros(1, order + 1)
    selector[0, 0] = 1
    completed = selector.col_join(derivative)
    _require(completed.det() == math.factorial(order), "corner completion determinant changed")
    two_polarizations = sp.diag(completed, completed)
    _require(
        two_polarizations.rank() == 2 * (order + 1),
        "two-polarization corner completion rank changed",
    )
    one_corner_missing = two_polarizations[:-1, :]
    _require(
        one_corner_missing.rank() == 2 * (order + 1) - 1,
        "missing-corner mutation rank changed",
    )
    return {
        "order": order,
        "derivative_matrix": [[str(value) for value in row] for row in derivative.tolist()],
        "derivative_rank": derivative.rank(),
        "kernel_basis": [[str(value) for value in vector] for vector in kernel],
        "one_component_corner_completed_matrix": [[str(value) for value in row] for row in completed.tolist()],
        "one_component_corner_completed_determinant": str(completed.det()),
        "two_tracefree_components_completed_rank": two_polarizations.rank(),
        "two_tracefree_components_dimension": 2 * (order + 1),
        "one_corner_component_missing_rank": one_corner_missing.rank(),
        "mutation_verdict": "ONE_MISSING_TRACEFREE_CORNER_COMPONENT_LEAVES_ONE_RADICAL_DIRECTION",
    }


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    for name, path in INPUTS.items():
        _require(_sha256(path) == PINNED[name], f"pinned {name} input changed")
    _require(
        records["local_no_go"]["classification"]["fixed_boundary_local_counterterm_repair_obstructed"],
        "local no-go changed",
    )
    _require(
        records["auxiliary_pair"]["classification"]["prequotient_tracefree_normal_jet_principal_pairing_nondegenerate"],
        "auxiliary principal pair changed",
    )
    jet = _jet_witness()
    return {
        "schema": "asymptotic-bach-schouten-corner-zero-mode-obstruction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "ASYMPTOTIC_BACH_SCHOUTEN_CORNER_ZERO_MODE_OBSTRUCTION_V1",
        "result_state": "MINIMAL_SCHOUTEN_PAIR_OBSTRUCTED_BY_TWO_COMPONENT_CORNER_ZERO_MODE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "generality_level": "G2_TRACEFREE_TENSOR_PRINCIPAL_BONDI_JET",
        "scope": {
            "theory": "linearized four-dimensional pure Weyl C^2 gravity in auxiliary-Schouten form",
            "background": "Minkowski space",
            "boundaries": "I+ retarded-time line with explicit endpoint/corner data",
            "charge_sector": "tracefree radiative principal Bondi jet; Coulombic aspects absent",
            "carrier": "leading p0 tracefree metric source Q_AB, leading auxiliary response S_AB, and p1 radiative response C_AB",
            "degree": 1,
            "parity": "both tracefree tensor polarizations",
            "ell": "local tensor principal relation; angular lower-order recursion remains open",
            "m": "local tensor principal relation",
            "k": "radial Bondi expansion, not compact momentum",
            "omega": "smooth retarded-time profiles, including endpoint memory",
        },
        "provenance": {
            "producer_path": str(Path(__file__).relative_to(ROOT)),
            "producer_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {
                    "path": str(path.relative_to(ROOT)),
                    "sha256": _sha256(path),
                    "result_id": records[name]["result_id"],
                }
                for name, path in INPUTS.items()
            },
        },
        "principal_Bondi_relation": {
            "auxiliary_equation": "G_ab=(2/alpha_B)*(s_ab-g_ab*s)",
            "tracefree_TT_identity": "G_AB^TF=-(1/2)*Box h_AB^TF",
            "p0_wave_leading_term": "Box Q_AB(u,x)=-2*r^-1*partial_u Q_AB+O(r^-2)",
            "leading_auxiliary_coefficient": "s_AB^TF=r^-1*S_AB+O(r^-2)",
            "result": "S_AB=(alpha_B/2)*partial_u Q_AB",
            "status": "CERTIFIED_AT_TRACEFREE_PRINCIPAL_BONDI_JET",
        },
        "retarded_advanced_reconstruction": {
            "retarded": "Q_AB(u)=Q_AB^-+(2/alpha_B)*integral_{-infinity}^u S_AB(v)dv",
            "advanced": "Q_AB(u)=Q_AB^+-(2/alpha_B)*integral_u^{+infinity} S_AB(v)dv",
            "matching_condition": "Q_AB^+-Q_AB^-=(2/alpha_B)*integral_{-infinity}^{+infinity}S_AB(v)dv",
            "homogeneous_ambiguity": "Q_AB -> Q_AB+q_AB(x), with q_AB tracefree and u-independent",
            "conclusion": "S_AB alone determines neither endpoint source; choosing a retarded or advanced inverse is a corner condition, not an intrinsic local inverse.",
        },
        "exact_finite_jet_witness": jet,
        "minimal_pair_obstruction": {
            "bulk_principal_flux": "omega_I_principal proportional to integral_I (delta S^AB wedge partial_u delta C_AB)",
            "radical": "u-independent q_AB has delta S_AB=0 and is invisible to the bulk principal flux",
            "minimal_missing_degree": "one tracefree symmetric corner tensor q_AB per angle, i.e. exactly two real components before boundary gauge descent",
            "rank_proof": "For each polarization D_u on order-N jets has rank N and a one-dimensional constant kernel; adjoining q_0 gives determinant N!. Two polarizations therefore require exactly two corner coordinates.",
            "mutation": jet["mutation_verdict"],
            "conclusion": "The minimal bulk Schouten pair (Q_AB,S_AB,C_AB) is not a nondegenerate memory-inclusive boundary phase space until a two-component tracefree corner coordinate and a conjugate corner momentum/constraint are supplied.",
        },
        "function_space_disposition": {
            "compact_support_Q": "D_u is injective, but S must have zero total integral; this removes the corner mode by boundary condition rather than representing it.",
            "memory_inclusive_Q": "D_u has the u-independent tracefree kernel q_AB and retarded/advanced inverses differ by endpoint data.",
            "retarded_only": "well-defined only after declaring Q_AB^-; not equivalent to an advanced construction unless the matching condition holds",
            "causal_two_sided": "NO_CERTIFIED_MAP across I-/i0/I+",
        },
        "gauge_and_BFV_disposition": {
            "Weyl_ghost": "delta_sigma s_AB=-alpha_B*(D_A D_B sigma)^TF at the boundary principal level",
            "corner_ghost_action": "OPEN; the allowed endpoint sigma and boundary diffeomorphism jets are not classified",
            "antifields_constraints": "NO_CERTIFIED_DOMAIN",
            "postquotient_corner_rank": "OPEN",
        },
        "charge_disposition": {
            "P0": "OPEN_UNTIL_CORNER_PAIR_AND_QUOTIENT_EXIST",
            "D_M": "OPEN_UNTIL_CORNER_PAIR_AND_QUOTIENT_EXIST",
            "H_ESU": "NOT_APPLICABLE_ON_FIXED_MINKOWSKI_PATCH",
            "D_rad": "NO_CERTIFIED_MAP",
        },
        "classification": {
            "three_inputs_imported_by_exact_hash": True,
            "principal_Bondi_auxiliary_relation_certified": True,
            "retarded_advanced_mismatch_certified": True,
            "two_component_corner_kernel_certified": True,
            "minimal_bulk_Schouten_pair_nondegenerate_with_memory": False,
            "minimal_additional_corner_coordinate_count_certified": True,
            "conjugate_corner_momentum_constructed": False,
            "full_tensor_angular_and_Coulombic_recursion_constructed": False,
            "boundary_gauge_BFV_descent_certified": False,
            "Iminus_i0_Iplus_matching_certified": False,
            "P0_charge_computed": False,
            "D_M_charge_computed": False,
            "causal_particle_scattering_stability_positivity_or_quantum_claim": False,
        },
        "verdicts": {
            "minimal_bulk_edge_pair": "OBSTRUCTED_BY_TRACEFREE_CORNER_ZERO_MODE",
            "smallest_additional_edge_degree": "TWO_COMPONENT_TRACEFREE_CORNER_TENSOR_PLUS_CONJUGATE_CONSTRAINT_OR_MOMENTUM",
            "renormalized_boundary_phase_space": "PHASE_SPACE_NOT_CLOSED",
            "work_item": "OBSTRUCTED_AT_FIRST_EDGE_ZERO_MODE_GATE",
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC tensor-principal theorem proves that S_AB=(alpha_B/2)partial_u Q_AB forgets a two-component u-independent tracefree corner tensor and that the minimal bulk Schouten pair is radical on a memory-inclusive carrier. It does not construct the conjugate corner momentum, angular/Coulombic Bondi recursion, boundary ghost/antifield/BFV quotient, I-/i0/I+ matching, P0/D_M charges, or any causal, particle, scattering, stability, positivity, unitarity or quantum result.",
        "next_gate": "Add the tracefree corner coordinate and classify its conjugate momentum/constraint together with endpoint Weyl and diffeomorphism ghosts; only then retest finite-cut nondegeneracy and charges.",
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.einstein_sector.asymptotic_bach_schouten_corner_zero_mode_obstruction --check",
            "PYTHONPATH=. python3 bridge/einstein_sector/verify_asymptotic_bach_schouten_corner_zero_mode_obstruction.py",
            "PYTHONPATH=. python3 -m unittest bridge.einstein_sector.tests.test_asymptotic_bach_schouten_corner_zero_mode_obstruction -v",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-asymptotic-bach-schouten-corner-zero-mode-fragment-v1.json",
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
                "id": "einstein.asymptotic.minkowski.weyl.schouten_corner_zero_mode",
                "scope": certificate["scope"],
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "OBSTRUCTED",
                    "nonlinear": "NOT_APPLICABLE",
                    "observational": "NO_CERTIFIED_MAP",
                    "quantum": "NO_CERTIFIED_MAP",
                },
                "mode_data": {
                    "dispersion": {
                        "status": "NOT_APPLICABLE",
                        "statement": "The obstruction is the zero mode of D_u, not a frequency-shell dispersion theorem.",
                    },
                    "lee_wald": {
                        "status": "OBSTRUCTED",
                        "statement": certificate["minimal_pair_obstruction"]["conclusion"],
                    },
                    "taub_maps": {
                        "status": "NOT_APPLICABLE",
                        "statement": "No compact second-order Taub map is involved.",
                    },
                    "resonance": {
                        "status": "NO_CERTIFIED_MAP",
                        "statement": "No compact harmonic resonance carrier is identified.",
                    },
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {
                            "status": "NOT_APPLICABLE",
                            "statement": "The theorem is linear and asymptotic.",
                        },
                        "smooth_secular": {
                            "status": "NOT_APPLICABLE",
                            "statement": "No quadratic source is evaluated.",
                        },
                        "causal_retarded": {
                            "status": "NO_CERTIFIED_MAP",
                            "statement": "Retarded reconstruction requires declared corner data and is not matched through i0.",
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
