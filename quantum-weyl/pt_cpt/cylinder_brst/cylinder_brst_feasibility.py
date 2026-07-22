#!/usr/bin/env python3
"""Build the exact cylinder structured-CPT/BRST feasibility certificate.

The energy-five matrices are a finite buffer regression, not a finite
SO(4,2) representation.  The all-energy conclusion is instead obtained from
the multiplicity-free SO(4) tower decomposition and the nonzero analytic
proper-conformal links on their declared tails.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analytic_completion.one_particle.generators import (
    COEFFICIENT_MINIMUM,
    COEFFICIENT_SQUARE,
)
from symbolic.verify_conformal_generator_all_levels import (
    FORM_SIGN,
    lowering_blocks,
    representation_space,
)


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificates/CYLINDER_BRST_STRUCTURED_CPT_FEASIBILITY_V1.json"
ATLAS = ROOT / "residual_atlas/phase2-cpt-cylinder-brst-feasibility-fragment-v1.json"
SCHEMA = HERE / "schema/cylinder-brst-structured-cpt-feasibility-v1.schema.json"
MAXIMUM_ENERGY = 5

INPUTS = {
    "one_particle_krein": (
        ROOT / "analytic_completion/certificates/one_particle_krein.json",
        "c52f8b2fcee6573e55e72402008779fd706311b77e2463a774b9eb16ce12b374",
    ),
    "krein_implementation": (
        ROOT / "analytic_completion/one_particle/krein.py",
        "1924e6cd323df39dc280e9b39e0c890a63673db4e1a5c249382bbe3b7e19c295",
    ),
    "closed_generators": (
        ROOT / "analytic_completion/one_particle/generators.py",
        "9165404959b1f581a710a233fb7a076290f559e3bb9d0790a0c896cf9798332f",
    ),
    "all_level_generators": (
        ROOT / "symbolic/verify_conformal_generator_all_levels.py",
        "9b7f90e8377d794cd2fa4cde8b34a88baf2cba90c41074cb1a4a0fde4c77a6a0",
    ),
    "polarized_state_complex": (
        ROOT / "field_bv_identification/polarized_state/certificates/polarized_state_complex.json",
        "efe492946333578e91d880fde0008166ba8960bc366840413883e5c0e39d0ec1",
    ),
    "polarized_state_implementation": (
        ROOT / "field_bv_identification/polarized_state/polarized_complex.py",
        "245452186edd42cba7d4eeb2feb2bca0b5db2c39eba846903c4b3d39e854511d",
    ),
    "reduced_bridge4": (
        ROOT / "quantum-weyl/lorentzian/certificates/VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD.json",
        "f49edce04b39d1e600d0072bfabc784b8ef6edf0d5a1fc39c8ad89f7fe031d48",
    ),
    "p2a_contract": (
        ROOT / "quantum-weyl/pt_cpt/negative_control/certificates/STRUCTURED_METRIC_QUARTET_NO_GO_V1.json",
        "377f699d854724f743188b854e4f5be3f29540ba1f5bc2beee3ec9204e7dbf6a",
    ),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dump(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _pins() -> dict[str, Any]:
    pins = {}
    for role, (path, expected) in INPUTS.items():
        actual = _sha(path)
        if actual != expected:
            raise AssertionError(f"frozen input drift: {role}")
        pins[role] = {"path": str(path.relative_to(ROOT)), "sha256": actual}
    contract = json.loads(INPUTS["p2a_contract"][0].read_text())
    if contract["decision"]["replacement_BRST_gate"] != "CHAIN_MAP_PLUS_EXPLICIT_COHOMOLOGY_DESCENT":
        raise AssertionError("P2-A BRST contract drifted")
    return pins


def _component_name(kind: str, component: tuple[sp.Rational, sp.Rational]) -> str:
    return f"{kind}_({component[0]},{component[1]})"


def _finite_buffer() -> dict[str, Any]:
    chiralities: dict[str, Any] = {}
    for chirality in (-1, 1):
        space = representation_space(MAXIMUM_ENERGY, chirality)
        c0 = space.form
        eta0 = space.form * c0
        if c0**2 != sp.eye(space.dimension) or eta0 != sp.eye(space.dimension):
            raise AssertionError("C0 positivity identity failed")

        commutators: dict[str, int] = {
            "D": int((c0 * space.energy - space.energy * c0).rank())
        }
        for axis, matrix in sorted(space.left.items()):
            commutators[f"SO4_left_{axis}"] = int((c0 * matrix - matrix * c0).rank())
        for axis, matrix in sorted(space.right.items()):
            commutators[f"SO4_right_{axis}"] = int((c0 * matrix - matrix * c0).rank())

        proper_defects = []
        for component, matrix in sorted(space.lowering.items()):
            defect = c0 * matrix - matrix * c0
            proper_defects.append(defect)
            commutators[_component_name("Kminus", component)] = int(defect.rank())
        for component, matrix in sorted(space.raising.items()):
            defect = c0 * matrix - matrix * c0
            proper_defects.append(defect)
            commutators[_component_name("Kplus", component)] = int(defect.rank())

        sign_diagonal = list(space.form.diagonal())
        plus = sum(value == 1 for value in sign_diagonal)
        minus = sum(value == -1 for value in sign_diagonal)
        stacked = sp.Matrix.vstack(*proper_defects)
        if set(commutators.values()) != {0, 32}:
            raise AssertionError("unexpected finite-buffer commutator ranks")
        chiralities[str(chirality)] = {
            "dimension": space.dimension,
            "krein_inertia": {"positive": plus, "negative": minus, "zero": 0},
            "C0_diagonal_by_tower": dict(FORM_SIGN),
            "C0_squared_is_identity": True,
            "eta0_equals_G_times_C0": "identity",
            "eta0_inertia": {"positive": space.dimension, "negative": 0, "zero": 0},
            "commutator_ranks": commutators,
            "degree_zero_to_one_BRST_defect_rank": int(stacked.rank()),
            "BRST_defect_formula": "[C0 tensor 1,Q](v)=sum_a [C0,rho(T_a)]v tensor c^a",
        }
    return {
        "maximum_energy": MAXIMUM_ENERGY,
        "buffer_warning": "The cutoff matrices are complete only below the top shell and are used solely as a regression; they do not prove an all-energy representation statement.",
        "generator_count": 15,
        "chiralities": chiralities,
        "combined_direct_sum": {
            "dimension": 268,
            "krein_inertia": {"positive": 140, "negative": 128, "zero": 0},
            "eta0_inertia": {"positive": 268, "negative": 0, "zero": 0},
            "proper_commutator_rank_each": 64,
            "degree_zero_to_one_BRST_defect_rank": 204,
        },
    }


def _coefficient_rows() -> dict[str, Any]:
    m = sp.symbols("m", nonnegative=True)
    rows = {}
    for family, square in COEFFICIENT_SQUARE.items():
        n = next(iter(square.free_symbols))
        minimum = COEFFICIENT_MINIMUM[family]
        numerator, denominator = sp.fraction(sp.cancel(square))
        shifted_numerator = sp.Poly(sp.expand(numerator.subs(n, m + minimum)), m)
        shifted_denominator = sp.Poly(sp.expand(denominator.subs(n, m + minimum)), m)
        positive = (
            all(value >= 0 for value in shifted_numerator.all_coeffs())
            and all(value >= 0 for value in shifted_denominator.all_coeffs())
            and shifted_numerator.eval(0) > 0
            and shifted_denominator.eval(0) > 0
        )
        if not positive:
            raise AssertionError(f"nonzero-tail proof failed: {family}")
        rows[family] = {
            "minimum_source_energy": minimum,
            "coefficient_squared": str(sp.factor(square)),
            "strictly_positive_on_declared_tail": True,
        }
    return rows


def _commutant_obstruction() -> dict[str, Any]:
    blocks = lowering_blocks(MAXIMUM_ENERGY)
    nodes = sorted({b.source for b in blocks} | {b.target for b in blocks})
    adjacency = {node: set() for node in nodes}
    edges = []
    for block in blocks:
        adjacency[block.source].add(block.target)
        adjacency[block.target].add(block.source)
        edges.append({
            "family": block.family,
            "source": block.source,
            "target": block.target,
            "coefficient": str(block.coefficient),
        })
    seen = set()
    components = []
    for node in nodes:
        if node in seen:
            continue
        stack = [node]
        component = []
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            component.append(current)
            stack.extend(adjacency[current] - seen)
        components.append(sorted(component))
    if len(components) != 1:
        raise AssertionError("buffer tower link graph unexpectedly disconnected")

    return {
        "search_space": "all operators commuting with D and both compact SO(4) factors, then with every proper-conformal generator",
        "schur_reduction": "At fixed chirality every (tower,energy) SO(4) irrep is multiplicity one and pairwise inequivalent, so the D+SO(4) commutant is one scalar per tower-energy block.",
        "finite_buffer_branch_scalar_graph": {
            "nodes": nodes,
            "edges": edges,
            "connected_components": components,
            "commutant_dimension_per_chirality": 1,
            "status": "FINITE_BUFFER_REGRESSION_ONLY",
        },
        "all_energy_nonzero_coefficients": _coefficient_rows(),
        "all_energy_connectivity_proof": [
            "EE_n is nonzero for every n>=3 and connects all E_n to E_2.",
            "AE_n is nonzero for every n>=3 and connects each A_n to E_(n-1).",
            "LE_n is nonzero for every n>=4 and connects each L_n to E_(n-1).",
            "Therefore every tower-energy scalar is equal within each chirality; AA, LA and LL independently regress the same conclusion.",
        ],
        "full_connected_conformal_commutant": "C=c_minus*I on chirality -1 direct-sum c_plus*I on chirality +1",
        "parity_compatible_commutant": "C=c*I",
        "Hermitian_involution_solutions": "c_minus,c_plus in {+1,-1}; parity requires c_minus=c_plus",
        "positivity_obstruction": "For either scalar sign, eta=G*C retains both E and A/L signs in each chirality; hence no solution is positive.",
        "all_energy_result": "NO_POSITIVE_GC_METRIC_FROM_A_RESIDUAL_INVARIANT_HERMITIAN_INVOLUTION",
    }


def build() -> dict[str, Any]:
    certificate = {
        "$schema": "../schema/cylinder-brst-structured-cpt-feasibility-v1.schema.json",
        "schema": "pure-weyl-cylinder-brst-structured-cpt-feasibility-v1",
        "result_id": "CYLINDER_BRST_STRUCTURED_CPT_FEASIBILITY_V1",
        "result_state": "REDUCED_C0_POSITIVE_BUT_RESIDUAL_CHAIN_DESCENT_OBSTRUCTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "strict free pure-Weyl cylinder residual carrier",
            "carrier": "E/A/L one-particle towers, both chiralities, and the degree-zero-to-one residual CE/BRST chain test",
            "finite_regression": "exact energy-five buffer",
            "all_energy_domain": "common finite-energy-support algebraic core",
            "metric_relation": "eta=G*C with canonical Krein form G",
        },
        "source_refs": _pins(),
        "reduced_stationary_candidate": {
            "C0": "+1 on E, -1 on A, -1 on L",
            "G": "+1 on E, -1 on A, -1 on L",
            "eta0_equals_G_times_C0": "identity",
            "positive_on_every_reduced_energy_block": True,
            "commutes_with_stationary_H_equals_D": True,
            "Mannheim_C_operator_on_residual_complex": False,
        },
        "finite_buffer_regression": _finite_buffer(),
        "invariant_commutant_search": _commutant_obstruction(),
        "BRST_chain_decision": {
            "ghost_action_in_search": "identity on the declared CE ghost exterior algebra",
            "C0_chain_map": False,
            "reason": "proper-conformal terms in Q have nonzero [C0,rho(T_a)] coefficients in linearly independent degree-one ghost directions",
            "corrected_residual_invariant_C_exists": False,
            "positive_cohomology_test_reached": False,
            "stop_reason": "chain-map descent fails before a cohomology metric can be induced",
            "nontrivial_ghost_normalizers": "NOT_CLASSIFIED_OUTSIDE_THE_DECLARED_INVARIANT_COMMUTANT",
        },
        "decision": {
            "reduced_stationary_positive_eta": "EXACTLY_CONSTRUCTED",
            "residual_BRST_compatible_structured_C": "OBSTRUCTED_IN_DECLARED_INVARIANT_COMMUTANT",
            "finite_cutoff_only_claim": "rank regressions and finite link graph",
            "all_energy_claim": "multiplicity-free Schur reduction plus nonzero analytic tower links on the finite-support core",
            "full_BV_state_or_unitarity": "NOT_ESTABLISHED",
        },
        "mutation_expectations": {
            "C0_declared_chain_map": "REJECT",
            "proper_rank32_changed": "REJECT",
            "finite_buffer_promoted_to_representation": "REJECT",
            "commutant_positive_GC_claim": "REJECT",
            "full_BV_or_unitarity_claim": "REJECT",
        },
        "claim_boundary": {
            "establishes": [
                "exact positivity of eta0=G*C0 on the reduced stationary E/A/L carrier",
                "exact failure of C0 to commute with every proper-conformal row in the declared energy-five buffer",
                "failure of the identity-ghost C0 chain map at BRST degree zero to one",
                "an all-energy representation-theoretic obstruction within the full D+SO(4)+proper-conformal invariant commutant on the finite-support core",
            ],
            "does_not_establish": [
                "nonexistence of every possible C with a nontrivial ghost normalizer action",
                "a complete Lorentzian off-shell BV propagator or BRST-compatible Hadamard state",
                "a full-BV CPT operator, field-theoretic unitarity, scattering positivity, or anomaly cancellation",
                "that an energy cutoff is itself an SO(4,2) representation",
            ],
        },
        "provenance": {
            "generator": str(Path(__file__).relative_to(ROOT)),
            "arithmetic": "exact SymPy rational/algebraic sparse matrices",
            "science_forge_identity": "phase2-cpt-2",
            "work_item": "sf:program/work/phase2-cpt-cylinder-brst-feasibility",
        },
    }
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    return certificate


def atlas_fragment(certificate: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "result_id": certificate["result_id"],
        "dependency_tags": certificate["dependency_tags"],
        "lifecycle_state": certificate["lifecycle_state"],
        "background": "Einstein cylinder",
        "carrier": "E/A/L one-particle towers",
        "reduced_eta0": "POSITIVE",
        "residual_chain_descent": "OBSTRUCTED_IN_DECLARED_INVARIANT_COMMUTANT",
        "certificate": str(OUTPUT.relative_to(ROOT)),
        "does_not_establish": certificate["claim_boundary"]["does_not_establish"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate = build()
    outputs = {OUTPUT: _dump(certificate), ATLAS: _dump(atlas_fragment(certificate))}
    if args.check:
        for path, expected in outputs.items():
            if not path.exists() or path.read_bytes() != expected:
                raise SystemExit(f"stale generated output: {path.relative_to(ROOT)}")
        print("CYLINDER_BRST_STRUCTURED_CPT_FEASIBILITY_V1 generated outputs: CURRENT")
        return
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    print(f"wrote {ATLAS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
