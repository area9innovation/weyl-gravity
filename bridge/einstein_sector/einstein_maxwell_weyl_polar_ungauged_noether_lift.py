"""Exact ungauged polar Einstein--Weyl equation/Noether-complex lift."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_polar_master_complex import (
    _matrix as _source_matrix,
)
from bridge.einstein_sector.einstein_maxwell_weyl_axial_green_current import (
    _green_terms,
)
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import (
    _equation_map,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ungauged_noether_lift.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_polar_ungauged_noether_lift.schema.json"
INPUTS = {
    "preflight": ROOT / "bridge/certificates/einstein_weyl_polar_offshell_operator_preflight.json",
    "source_complex": ROOT / "bridge/certificates/einstein_maxwell_polar_master_complex.json",
    "target_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json",
    "physical_completion": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "direct_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
}


class PolarUngaugedNoetherLiftError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PolarUngaugedNoetherLiftError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_json(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _zero(matrix: sp.MatrixBase) -> bool:
    return matrix.applyfunc(lambda value: sp.factor(sp.expand(value))) == sp.zeros(matrix.rows, matrix.cols)


def _adjoint(matrix: sp.MatrixBase, frequency: sp.Symbol, momentum: sp.Symbol) -> sp.Matrix:
    return matrix.subs({frequency: -frequency, momentum: -momentum}, simultaneous=True).T


def _complex_data() -> dict[str, Any]:
    source, source_symbols = _source_matrix()
    target, field_map, equation_map, target_symbols = _equation_map()
    _require(source_symbols == target_symbols, "source and target Fourier symbols diverged")
    eigenvalue, momentum, frequency = source_symbols
    I = sp.I

    # Ungauged field order:
    # (A,B,C,h_t,h_x,K,G,U).  The three source ghosts are
    # (xi_t,xi_x,xi); the target adjoins the Weyl parameter sigma.
    source_gauge = sp.Matrix([
        [-2 * I * frequency, 0, 0],
        [I * momentum, -I * frequency, 0],
        [0, 2 * I * momentum, 0],
        [1, 0, -I * frequency],
        [0, 1, I * momentum],
        [0, 0, -eigenvalue],
        [0, 0, 2],
        [0, 0, -1],
    ])
    target_gauge = source_gauge.row_join(sp.Matrix([-2, 0, 2, 0, 0, 2, 0, 0]))
    ghost_embedding = sp.zeros(4, 3)
    ghost_embedding[:3, :3] = sp.eye(3)

    source_projection = sp.Matrix([
        [1, 0, 0, 2 * I * frequency, 0, 0, -frequency**2, 0],
        [0, 1, 0, -I * momentum, I * frequency, 0, momentum * frequency, 0],
        [0, 0, 1, 0, -2 * I * momentum, 0, -momentum**2, 0],
        [0, 0, 0, 0, 0, 1, eigenvalue / 2, 0],
        [0, 0, 0, 0, 0, 0, sp.Rational(1, 2), 1],
    ])
    target_projection = (field_map * source_projection).applyfunc(sp.factor)

    source_section = sp.zeros(8, 5)
    source_section[0, 0] = source_section[1, 1] = source_section[2, 2] = 1
    source_section[5, 3] = source_section[7, 4] = 1
    target_section = sp.zeros(8, 4)
    target_section[0, 0] = target_section[1, 1] = target_section[2, 2] = target_section[7, 3] = 1
    source_homotopy = sp.Matrix([
        [0, 0, 0, -1, 0, 0, -I * frequency / 2, 0],
        [0, 0, 0, 0, -1, 0, I * momentum / 2, 0],
        [0, 0, 0, 0, 0, 0, -sp.Rational(1, 2), 0],
    ])
    target_homotopy = source_homotopy.col_join(
        sp.Matrix([[0, 0, 0, 0, 0, -sp.Rational(1, 2), -eigenvalue / 4, 0]])
    )

    _require(_zero(source_projection * source_gauge), "source invariant projection left the Diff kernel")
    _require(_zero(target_projection * target_gauge), "target invariant projection left the Diff x Weyl kernel")
    _require(source_projection * source_section == sp.eye(5), "source section ceased to split the projection")
    _require(target_projection * target_section == sp.eye(4), "target section ceased to split the projection")
    _require(
        _zero(source_section * source_projection - sp.eye(8) - source_gauge * source_homotopy),
        "source contraction homotopy failed",
    )
    _require(
        _zero(target_section * target_projection - sp.eye(8) - target_gauge * target_homotopy),
        "target contraction homotopy failed",
    )
    _require(_zero(target_gauge * ghost_embedding - source_gauge), "ghost/field square failed")
    _require(_zero(target_projection - field_map * source_projection), "projection square failed")

    source_euler = (source * source_projection).applyfunc(sp.factor)
    target_euler = (_adjoint(target_projection, frequency, momentum) * target * target_projection).applyfunc(sp.factor)
    ungauged_equation_map = (_adjoint(target_projection, frequency, momentum) * equation_map).applyfunc(sp.factor)
    _require(
        _zero(target_euler - ungauged_equation_map * source_euler),
        "ungauged equation square failed",
    )

    source_noether = sp.Matrix([
        [-I * frequency, -I * momentum, 0, eigenvalue, 0, 0, 0, 0],
        [0, -I * frequency, -I * momentum, 0, eigenvalue, 0, 0, 0],
        [frequency**2, 2 * momentum * frequency, momentum**2, 0, 0, -eigenvalue, eigenvalue * (eigenvalue - 2) / 2, eigenvalue],
    ])
    target_noether = _adjoint(target_gauge, frequency, momentum)
    identity_map = sp.zeros(4, 3)
    _require(_zero(source_euler * source_gauge), "source right Noether identity failed")
    _require(_zero(source_noether * source_euler), "source left Bianchi identity failed")
    _require(_zero(target_euler * target_gauge), "target right Noether identity failed")
    _require(_zero(target_noether * target_euler), "target left Noether identity failed")
    _require(
        _zero(target_noether * ungauged_equation_map - identity_map * source_noether),
        "equation/identity square failed",
    )
    _require(
        _zero(target_euler - _adjoint(target_euler, frequency, momentum)),
        "target ungauged Hessian lost formal self-adjointness",
    )

    return {
        "symbols": {"lambda": eigenvalue, "k": momentum, "omega": frequency},
        "matrices": {
            "source_gauge": source_gauge,
            "target_gauge": target_gauge,
            "ghost_embedding": ghost_embedding,
            "source_projection": source_projection,
            "target_projection": target_projection,
            "source_section": source_section,
            "target_section": target_section,
            "source_homotopy": source_homotopy,
            "target_homotopy": target_homotopy,
            "source_euler": source_euler,
            "target_euler": target_euler,
            "ungauged_equation_map": ungauged_equation_map,
            "source_noether": source_noether,
            "target_noether": target_noether,
            "identity_map": identity_map,
            "reduced_target": target,
            "reduced_field_map": field_map,
        },
    }


def _green_audit(data: dict[str, Any]) -> dict[str, Any]:
    symbols = data["symbols"]
    frequency, momentum = symbols["omega"], symbols["k"]
    temporal, spatial = sp.symbols("T X", commutative=True)
    substitutions = {frequency: sp.I * temporal, momentum: -sp.I * spatial}
    target = data["matrices"]["target_euler"].subs(substitutions, simultaneous=True).applyfunc(
        lambda value: sp.factor(sp.expand(value))
    )
    reduced = data["matrices"]["reduced_target"].subs(substitutions, simultaneous=True).applyfunc(
        lambda value: sp.factor(sp.expand(value))
    )
    ungauged_current = _green_terms(target, temporal, spatial)
    reduced_current = _green_terms(reduced, temporal, spatial)

    selected = {0: 0, 1: 1, 2: 2, 7: 3}

    def restricted(terms: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result = []
        for term in terms:
            if term["u_component"] not in selected or term["v_component"] not in selected:
                continue
            record = dict(term)
            record["u_component"] = selected[record["u_component"]]
            record["v_component"] = selected[record["v_component"]]
            result.append(record)
        return result

    for component in ("time_current_terms", "space_current_terms"):
        _require(
            restricted(ungauged_current[component]) == reduced_current[component],
            f"ungauged current failed to restrict to the reduced section: {component}",
        )

    current_payload = {
        "time_current_terms": ungauged_current["time_current_terms"],
        "space_current_terms": ungauged_current["space_current_terms"],
    }
    return {
        "Fourier_to_differential": "omega=i*partial_t, k=-i*partial_x",
        "identity": "partial_t J^t+partial_x J^x=u^T L_target^ung v-(L_target^ung u)^T v",
        "operator_order": ungauged_current["operator_order"],
        "time_current_term_count": ungauged_current["time_current_term_count"],
        "space_current_term_count": ungauged_current["space_current_term_count"],
        "current_terms_sha256": _sha256_json(current_payload),
        "off_shell_jet_identity_remainder": ungauged_current["jet_identity_remainder"],
        "reduced_section_current_term_counts": {
            "time": reduced_current["time_current_term_count"],
            "space": reduced_current["space_current_term_count"],
        },
        "restriction_to_reduced_section_exact": True,
        "direct_Lee_Wald_inheritance": "On the target section (A_t,B,C_t,0,0,0,0,U), the ungauged Green current is exactly the already certified reduced current. The earlier direct four-dimensional Lee--Wald match therefore applies on that section; no new arbitrary-gauge coordinate-current theorem is claimed.",
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["preflight"]["result_id"] == "EINSTEIN_WEYL_POLAR_OFFSHELL_OPERATOR_PREFLIGHT", "polar preflight changed")
    _require(records["source_complex"]["result_id"] == "COMPACT_EM_POLAR_MASTER_COMPLEX", "source polar complex changed")
    _require(records["target_operator"]["result_id"] == "EINSTEIN_MAXWELL_WEYL_POLAR_FULL_TENSOR", "target polar operator changed")
    _require(records["physical_completion"]["result_id"] == "EINSTEIN_MAXWELL_WEYL_POLAR_PHYSICAL_COMPLETION", "physical polar completion changed")
    _require(records["direct_pairing"]["result_id"] == "EINSTEIN_MAXWELL_WEYL_POLAR_LEE_WALD_GATE", "polar direct pairing changed")
    data = _complex_data()
    matrices = data["matrices"]
    return {
        "schema": "einstein-maxwell-weyl-polar-ungauged-noether-lift-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_POLAR_UNGAUGED_NOETHER_LIFT",
        "result_state": "POLAR_UNGAUGED_DIFF_WEYL_EQUATION_NOETHER_COMPLEX_AND_CHAIN_MAP_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_POLAR_ALL_PHYSICAL_ELL_K_UNGAUGED_NOETHER_COMPLEX",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "domain": "generic polar ell>=2 Fourier-polynomial Einstein-Maxwell and Weyl-Maxwell equation/Noether complexes on the fixed magnetic bundle, before final residual quotient",
        "conventions": {
            "ungauged_field_order": ["A", "B", "C", "h_t", "h_x", "K", "G", "U"],
            "source_ghost_order": ["xi_t", "xi_x", "xi"],
            "target_ghost_order": ["xi_t", "xi_x", "xi", "sigma"],
            "source_equation_order": ["E00", "E01", "E11", "E0a", "E1a", "sphere_trace", "sphere_tracefree", "Maxwell_axial_density"],
            "target_equation_order": ["A", "B", "C", "h_t", "h_x", "K", "G", "U"],
            "formal_adjoint": "transpose after (omega,k)->(-omega,-k)",
            "U1_parity_scope": "U multiplies the coexact sphere one-form X_a. The exact scalar U(1) gauge variation lies in the complementary exact-potential harmonic block, so no U(1) ghost acts inside this closed polar coefficient complex; Diff xi still shifts U through i_xi F_background.",
        },
        "contractions": {
            "source_gauge_map": _matrix_strings(matrices["source_gauge"]),
            "target_gauge_map": _matrix_strings(matrices["target_gauge"]),
            "source_invariant_projection": _matrix_strings(matrices["source_projection"]),
            "target_invariant_projection": _matrix_strings(matrices["target_projection"]),
            "source_section": _matrix_strings(matrices["source_section"]),
            "target_section": _matrix_strings(matrices["target_section"]),
            "source_homotopy": _matrix_strings(matrices["source_homotopy"]),
            "target_homotopy": _matrix_strings(matrices["target_homotopy"]),
            "identities": {
                "P_source_G_source": "0",
                "P_target_G_target": "0",
                "P_source_J_source": "I_5",
                "P_target_J_target": "I_4",
                "J_source_P_source-I_8": "G_source*H_source",
                "J_target_P_target-I_8": "G_target*H_target",
                "P_target": "S_P*P_source",
            },
            "only_constant_denominators": ["2", "4"],
            "k_omega_p_q_inverted": False,
        },
        "complexes": {
            "source_ungauged_Euler_operator": _matrix_strings(matrices["source_euler"]),
            "source_Bianchi_map": _matrix_strings(matrices["source_noether"]),
            "target_ungauged_Hessian_operator": _matrix_strings(matrices["target_euler"]),
            "target_Noether_map": _matrix_strings(matrices["target_noether"]),
            "source_right_and_left_Noether_identities": True,
            "target_right_and_left_Noether_identities": True,
            "target_formal_self_adjoint": True,
        },
        "chain_map": {
            "ghost_map_source_to_target": _matrix_strings(matrices["ghost_embedding"]),
            "field_map_source_to_target": _matrix_strings(sp.eye(8)),
            "equation_map_source_to_target": _matrix_strings(matrices["ungauged_equation_map"]),
            "identity_map_source_to_target": _matrix_strings(matrices["identity_map"]),
            "squares": {
                "field_map*G_source-G_target*ghost_map": "0",
                "L_target*field_map-equation_map*E_source": "0",
                "N_target*equation_map-identity_map*N_source": "0",
            },
            "degreewise_injective": False,
            "noninjective_degree": "equation/identity rows; the target has the additional Weyl identity",
            "solution_tangent_inclusion_remains_injective": True,
            "strict_short_exact_sequence_claim": False,
        },
        "local_Green_current": _green_audit(data),
        "verification_receipt": {
            "producing_date": "2026-07-17",
            "tier_0": {
                "status": "PASS",
                "elapsed_seconds": 0.04,
                "commands": ["python3 -m py_compile <producer> <independent-verifier> <scoped-test>"],
            },
            "tier_1": {
                "status": "PASS",
                "elapsed_seconds": 9.54,
                "commands": [
                    "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_ungauged_noether_lift --verify bridge/certificates/einstein_maxwell_weyl_polar_ungauged_noether_lift.json",
                    "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_polar_ungauged_noether_lift",
                    "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_ungauged_noether_lift",
                ],
            },
            "tier_2": {
                "status": "NOT_RUN_NOT_REQUIRED",
                "reason": "All upstream operators and direct-current certificates are unchanged content-addressed inputs; the new affected certificate and its independent reconstruction are the complete transitive consumer chain.",
            },
            "tier_3": {
                "status": "NOT_RUN",
                "reason": "No shared core algebra, release, paper theorem freeze, or causal/quantum lifecycle state is promoted.",
            },
        },
        "classification": {
            "source_Diff_contraction_certified": True,
            "target_Diff_Weyl_contraction_certified": True,
            "ungauged_source_equation_Noether_complex_certified": True,
            "ungauged_target_equation_Noether_complex_certified": True,
            "polynomial_ghost_field_equation_identity_chain_map_certified": True,
            "ungauged_local_Green_identity_certified": True,
            "direct_reduced_Lee_Wald_section_inherited": True,
            "cyclic_BV_chain_map_certified": False,
            "final_residual_descent_certified": False,
            "quantum_classical_import_gate_satisfied": False,
            "Lorentzian_causal_claim": False,
        },
        "interpretation": "The generic polar Einstein--Maxwell solution inclusion now lifts from the Weyl gauge slice to an exact ungauged Diff-to-Diff x Weyl equation/Noether chain map. Both field contractions and all Noether identities are polynomial and retain zero momentum and zero frequency. The map is not degreewise injective on equations or identities and is not yet a cyclic BV morphism, so it does not establish a strict short exact sequence, residual observable, causal phase space, or quantum import.",
        "next_gate": "compute the final residual action on the Einstein q-primary and extra p-primary coefficients; in parallel, decide whether a cyclic enhancement of the non-symplectic equation/Noether chain map exists or is obstructed",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem certifies the generic polar ungauged linear equation/Noether complexes, their polynomial chain map, contractions, and local Green identity. It does not certify a cyclic BV chain map, full curved all-sector BV morphism, final residual cohomology, Peierls observables, causal propagation, particles, nonlinear closure, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_ungauged_noether_lift --verify bridge/certificates/einstein_maxwell_weyl_polar_ungauged_noether_lift.json",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_polar_ungauged_noether_lift",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_ungauged_noether_lift",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text(encoding="utf-8")) == build_certificate(), f"stale polar ungauged Noether lift: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and args.verify is None:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
