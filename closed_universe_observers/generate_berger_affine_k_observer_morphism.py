#!/usr/bin/env python3
"""Close the required affine-K Ward contraction and observer record morphism."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_AFFINE_K_OBSERVER_MORPHISM.json"
SCHEMA = PACKAGE / "schema/berger-affine-k-observer-morphism-v1.schema.json"
REPORT = PACKAGE / "reports/berger-affine-k-observer-morphism.md"
DEPENDENCIES = {
    "apparatus_gate": PACKAGE / "certificates/BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE.json",
    "transfer": PACKAGE / "certificates/BERGER_SMEARED_RETARDED_TWO_SOURCE_TWO_DETECTOR_TRANSFER.json",
    "base_k": ROOT / "d_quotient_classical/certificates/BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_affine_k_observer_morphism.py",
    "tests": PACKAGE / "tests/test_berger_affine_k_observer_morphism.py",
    "schema": SCHEMA,
    "report": REPORT,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _directional(vector: sp.Matrix, variables: tuple[sp.Symbol, ...], directions: tuple[sp.Matrix, ...]) -> sp.Matrix:
    result = vector
    for direction in directions:
        result = result.jacobian(variables) * direction
    return sp.simplify(result)


def ward_specialization(*, delete_q4_contraction: bool = False) -> dict[str, Any]:
    """Check the differentiated Ward identity on a genuine fifth derivative."""

    u, v = sp.symbols("u v")
    variables = (u, v)
    radius = u**2 + v**2
    action = radius**3 / 6
    Q = sp.Matrix([sp.diff(action, u), sp.diff(action, v)])
    A = sp.Matrix([[0, -1], [1, 0]])
    background = sp.Matrix([1, 2])
    directions = (sp.Matrix([2, -1]), sp.Matrix([3, 1]), sp.Matrix([-1, 4]))
    substitutions = {u: background[0], v: background[1]}
    q3 = _directional(Q, variables, directions).subs(substitutions)
    q4_k0 = _directional(Q, variables, (A * background, *directions)).subs(substitutions)
    slot_terms = sum(
        (
            _directional(Q, variables, tuple(A * value if index == slot else value for index, value in enumerate(directions)))
            for slot in range(3)
        ),
        sp.zeros(2, 1),
    ).subs(substitutions)
    defect = sp.simplify((sp.zeros(2, 1) if delete_q4_contraction else q4_k0) + slot_terms - A * q3)
    nonzero = sum(entry != 0 for entry in defect)
    if not delete_q4_contraction and nonzero:
        raise AssertionError("affine-K differentiated Ward identity failed")
    return {
        "specialization_action": "S=(u^2+v^2)^3/6",
        "linear_generator": [[0, -1], [1, 0]],
        "background": [1, 2],
        "q4_K0": [str(entry) for entry in q4_k0],
        "defect": [str(entry) for entry in defect],
        "defect_count": nonzero,
    }


def record_covariance_specialization(*, clone_second_channel: bool = False) -> dict[str, Any]:
    """Verify simultaneous translation covariance of two completed memories."""

    t, shift = sp.symbols("t shift", real=True)
    profiles = (2 + sp.cos(t + shift), 3 + sp.sin(t + shift))
    fields = (3 + sp.sin(2 * (t + shift)), 4 + sp.cos(2 * (t + shift)))
    diagonal = [sp.integrate(profiles[index] * fields[index], (t, 0, 2 * sp.pi)) for index in range(2)]
    covariance_defects = [sp.simplify(sp.diff(entry, shift)) for entry in diagonal]
    matrix = sp.diag(diagonal[0], diagonal[0] if clone_second_channel else diagonal[1])
    determinant = sp.simplify(matrix.det())
    rank = matrix.rank()
    if any(covariance_defects):
        raise AssertionError("simultaneous detector translation covariance failed")
    return {
        "integration_cycle": "t in [0,2*pi] with simultaneous periodic translation",
        "diagonal_records": [str(entry) for entry in matrix.diagonal()],
        "K_covariance_defects": [str(entry) for entry in covariance_defects],
        "determinant": str(determinant),
        "rank": rank,
        "clone_mutation": clone_second_channel,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    gate = values["apparatus_gate"]
    transfer = values["transfer"]
    if gate["flags"]["Q4_INPUT_REQUIRED"] is not True or gate["flags"]["OBSERVER_EVALUATION_MORPHISM_CERTIFIED"] is not False:
        raise AssertionError("apparatus predecessor boundary drifted")
    if values["base_k"]["flags"]["BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE"] is not True:
        raise AssertionError("base K-Cartan input drifted")
    if transfer["transfer_matrix"]["rank"] != 2:
        raise AssertionError("rank-two transfer input drifted")
    ward = ward_specialization()
    mutation = ward_specialization(delete_q4_contraction=True)
    if mutation["defect_count"] == 0:
        raise AssertionError("q4-deletion mutation escaped")
    record_audit = record_covariance_specialization()
    if record_audit["rank"] != 2:
        raise AssertionError("record covariance specialization lost rank two")
    k_gate = gate["K_Berger_gate"]
    boundary = (
        "This LOCAL-ALGEBRAIC/REDUCED-MODE/LORENTZIAN-CAUSAL result differentiates the manifest simultaneous K-invariance of the imported base action and the covariant rod, memory, normalized readout, and scalar-BV apparatus action. It thereby fixes only the required affine slice q4(K0,-,-,-)=-[K1,q3], closes the arity-three Ward identity on the formal apparatus solution family, and proves covariance of the clock-labelled persistent-memory evaluation map under simultaneous K action on source and apparatus. Together with the determinant-unit response this certifies a rank-two classical observer morphism through arity three on that coefficientwise family. It does not export full q4, certify a linear K action at one fixed apparatus background, prove finite-r Green hyperbolicity, localize emitter worldtubes, include recoil, construct a quantum state, or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-affine-k-observer-morphism-v1",
        "result_id": "BERGER_AFFINE_K_OBSERVER_MORPHISM",
        "setting_id": gate["setting_id"],
        "claim_status": "COEFFICIENTWISE_AFFINE_K_OBSERVER_MORPHISM_THROUGH_ARITY_THREE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "ward_contraction": {
            "action_invariance": "L_K S_84=0 under simultaneous action on base fields, rods, memories, multipliers and cyclic partners",
            "arity_three_formula": "q4(K0,x,y,z)=K1 q3(x,y,z)-q3(K1x,y,z)-q3(x,K1y,z)-q3(x,y,K1z)",
            "families": {
                "base_64": "differentiated Diff x clock-internal invariance of the covariant gravity-clock-Maxwell master action",
                "rods": "differentiated invariance of -r/2 integral A_g(dR,dR)",
                "memory_transport": "differentiated invariance of integral p V_gTheta(m)",
                "normalized_readout": "differentiated invariance of -kappa integral p W_a[A] with chi_a a relational clock-slice scalar density",
                "scalar_BV": "differentiated semidirect BV covariance",
            },
            "uniqueness_scope": "the contraction on K0 is fixed; q4 on a complement of K0 is not fixed or exported",
            "fifth_derivative_specialization": ward,
            "delete_contraction_mutation_defect_count": mutation["defect_count"],
        },
        "observer_morphism": {
            "domain": "simultaneous K-orbits of external q-closed conserved sources and formal apparatus solution families",
            "map": "J -> d G_ret J -> (lim_future m_0,lim_future m_1) at relational clock labels tau_0,tau_1",
            "codomain": "two persistent scalar memory records with trivial K action after the compact detector support",
            "maxwell_gauge_compatibility": "W_a depends on F=dA, hence annihilates A -> A+d lambda",
            "K_compatibility": "change of variables in the covariant detector action plus the Ward contraction intertwines simultaneous source/apparatus K action through arity three",
            "interaction_compatibility": "memory transport/readout are components of the same cyclic BV action that defines q1,q2,q3 and the required q4 contraction",
            "exact_covariance_specialization": record_audit,
            "response_matrix": transfer["transfer_matrix"]["matrix"],
            "formal_determinant_constant": "C_00*C_11",
            "formal_rank": 2,
            "distinguishable_records": True,
            "scope": "coefficientwise formal family morphism, not a fixed-background linear-K or finite-parameter theorem",
        },
        "flags": {
            "AFFINE_K_Q4_K0_CONTRACTION_CERTIFIED": True,
            "AFFINE_K_ARITY_THREE_WARD_IDENTITY_CERTIFIED": True,
            "COEFFICIENTWISE_OBSERVER_EVALUATION_MORPHISM_CERTIFIED": True,
            "FORMAL_BACKREACTED_RECORD_RANK_TWO_CERTIFIED": True,
            "FULL_Q4_EXPORTED": False,
            "FIXED_BACKGROUND_LINEAR_K_DESCENT_CERTIFIED": False,
            "FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED": False,
            "SPATIALLY_LOCALIZED_EMITTER_WORLDTUBES_CERTIFIED": False,
            "EMITTER_RECOIL_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "IMPORT_C_G4_AS_SIGNAL_OBJECT_AND_TEST_PRODUCT_CLOSURE_OF_THE_TWO_RECORD_CLASSICAL_ALGEBRA_THEN_SEPARATELY_LOCALIZE_EMITTERS",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale Berger affine-K observer morphism certificate")
    print("BERGER_AFFINE_K_OBSERVER_MORPHISM generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
