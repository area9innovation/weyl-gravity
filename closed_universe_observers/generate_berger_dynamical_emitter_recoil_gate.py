#!/usr/bin/env python3
"""Certify the dynamical-emitter recoil input obstruction and rank lemma."""

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
CERTIFICATE = PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_RECOIL_INPUT_GATE.json"
SCHEMA = PACKAGE / "schema/berger-dynamical-emitter-recoil-input-gate-v1.schema.json"
REPORT = PACKAGE / "reports/berger-dynamical-emitter-recoil-input-gate.md"
DEPENDENCIES = {
    "apparatus_handoff": PACKAGE / "certificates/BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF.json",
    "localized_transfer": PACKAGE / "certificates/BERGER_LOCALIZED_EMITTER_RANK_TWO_TRANSFER.json",
    "observer_morphism": PACKAGE / "certificates/BERGER_AFFINE_K_OBSERVER_MORPHISM.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_dynamical_emitter_recoil_gate.py",
    "tests": PACKAGE / "tests/test_berger_dynamical_emitter_recoil_gate.py",
    "schema": SCHEMA,
    "report": REPORT,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recoil_audit(*, collapse_masses: bool = False, erase_constant_determinant: bool = False) -> dict[str, Any]:
    """Construct two compatible polarization completions and the rank lemma."""
    lam = sp.Integer(1)
    mass0 = sp.Integer(1)
    mass1 = mass0 if collapse_masses else sp.Integer(4)
    response0 = sp.factor(1 / (lam + mass0))
    response1 = sp.factor(1 / (lam + mass1))
    difference = sp.factor(response0 - response1)
    resolvent_rhs = sp.factor((mass1 - mass0) / ((lam + mass0) * (lam + mass1)))
    if sp.simplify(difference - resolvent_rhs) != 0:
        raise AssertionError("emitter resolvent identity failed")

    beta = 2 * sp.sqrt(10) / 3
    s0, c1, mu, eps = sp.symbols("S_0 C_1 mu epsilon", nonzero=True)
    a, b, c, d = sp.symbols("a b c d")
    base = sp.zeros(2) if erase_constant_determinant else sp.Matrix([[-beta * s0, 0], [mu, beta * c1]])
    correction = sp.Matrix([[a, b], [c, d]])
    determinant = sp.expand((base + eps * correction).det())
    constant = sp.factor(determinant.coeff(eps, 0))
    expected = 0 if erase_constant_determinant else -beta**2 * s0 * c1
    if sp.simplify(constant - expected) != 0:
        raise AssertionError("formal recoil determinant constant failed")
    return {
        "spectral_value_lambda": sp.sstr(lam),
        "mass_squared_values": [sp.sstr(mass0), sp.sstr(mass1)],
        "retarded_recoil_coefficients": [sp.sstr(response0), sp.sstr(response1)],
        "coefficient_difference": sp.sstr(difference),
        "resolvent_identity_rhs": sp.sstr(resolvent_rhs),
        "different_recoil": difference != 0,
        "formal_determinant": sp.sstr(sp.factor(determinant)),
        "formal_determinant_constant": sp.sstr(constant),
        "constant_is_nonzero": constant != 0,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    handoff = values["apparatus_handoff"]
    if handoff["source_boundary"]["role"] != "EXTERNAL_Q_CLOSED_CONSERVED_SOURCE":
        raise AssertionError("external-source handoff boundary drifted")
    if values["localized_transfer"]["flags"]["LOCALIZED_EMITTER_TRANSFER_MATRIX_RANK_TWO"] is not True:
        raise AssertionError("localized rank-two input drifted")
    if values["observer_morphism"]["flags"]["COEFFICIENTWISE_OBSERVER_EVALUATION_MORPHISM_CERTIFIED"] is not True:
        raise AssertionError("observer morphism input drifted")

    audit = recoil_audit()
    collapsed = recoil_audit(collapse_masses=True)
    erased = recoil_audit(erase_constant_determinant=True)
    if collapsed["different_recoil"] or erased["constant_is_nonzero"]:
        raise AssertionError("recoil mutation rail failed")

    boundary = (
        "This LOCAL-ALGEBRAIC/REDUCED-MODE/LORENTZIAN-CAUSAL input gate proves that the current 84-row apparatus and localized-source certificates do not determine dynamical emitter recoil. They fix conserved external currents but no emitter carrier, pairing, kinetic operator, background equation, drive, or K_Berger action. Two local cyclic polarization-two-form completions with L_m=P_2+m^2 and the same background current J=delta Kbar are compatible after choosing f_m=L_m Kbar-g dAbar, yet their exact retarded recoil coefficients on a lambda=1 mode are 1/2 and 1/5. Thus the recoil kernel and first response correction are not inferable. Independently, the certified nonzero localized determinant is the constant term of every gauge-compatible formal recoil deformation M(epsilon)=M_0+epsilon M_1+..., so rank two survives over the formal coefficient ring. No specific emitter theory, recoil coefficient, enlarged BV complex, finite-parameter Green theorem, common-Hopf emitter, or quantum claim is certified."
    )
    return {
        "schema": "closed-universe-berger-dynamical-emitter-recoil-input-gate-v1",
        "result_id": "BERGER_DYNAMICAL_EMITTER_RECOIL_INPUT_GATE",
        "setting_id": values["localized_transfer"]["setting_id"],
        "claim_status": "DYNAMICAL_EMITTER_RECOIL_INPUT_UNDERDETERMINED_FORMAL_RANK_TWO_STABLE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "frozen_external_source_data": {
            "current": "J_b=delta Kbar_b, equivalently star J_b=d kappa_b",
            "properties": ["compact-time", "spatially localized", "conserved", "q-closed external input"],
            "not_supplied": ["emitter field carrier", "odd pairing and antifields", "kinetic operator", "background emitter equation or drive", "retarded emitter Green operator", "Diff/Weyl/K_Berger transformation", "initial emitter state"],
            "handoff_rule": handoff["source_boundary"]["rule"],
        },
        "two_completion_witness": {
            "candidate_carrier": "for each b, a real polarization two-form K_b with canonical BV cotangent partner",
            "quadratic_operator_family": "L_m=P_2+m^2 on Omega^2, with P_2=d delta+delta d",
            "interaction": "S_int=-g sum_b <K_b,dA>; Maxwell current is g delta K_b and emitter recoil is g dA",
            "cyclicity": "the two cross blocks are formal adjoints because they are Hessian derivatives of the same local action",
            "same_background_current": "fix Kbar_b with delta Kbar_b=J_b for both masses",
            "compatible_background_drive": "f_m=L_m Kbar_b-g dAbar; the external certificates do not constrain f_m",
            "linearized_elimination": "Sigma_m=g^2 delta G_m,ret d",
            "exact_specialization": audit,
            "conclusion": "the same certified external current admits different exact recoil kernels",
        },
        "formal_rank_stability": {
            "base_matrix": [["-beta*S_0", "0"], ["mu", "beta*C_1"]],
            "deformation": "M(epsilon)=M_0+epsilon M_1+epsilon^2 M_2+...",
            "determinant_constant": audit["formal_determinant_constant"],
            "coefficient_ring": "R[[epsilon]] localized at beta^2 S_0 C_1",
            "rank": 2,
            "scope": "conditional on a local cyclic gauge-compatible emitter completion admitting the displayed formal response expansion",
        },
        "required_emitter_handoff": {
            "fields": ["carrier and form degree/statistics", "BV antifields and odd pairing", "local emitter action", "Maxwell current map", "background solution or physical preparation data", "advanced/retarded emitter Green operator", "Diff/Weyl/Maxwell/K_Berger action"],
            "identities": ["q1^2=0", "unary cyclicity", "conservation of the Maxwell source", "same-sided causal support", "q1/q2 and q2/q2+q1/q3 identities at the requested order"],
            "rank_replay": "compute the first nonzero recoil correction only after the carrier and preparation are fixed; formal rank two itself is already protected by the constant determinant",
        },
        "mutation_results": [
            {"name": "collapse_two_mass_completions", "coefficient_difference": collapsed["coefficient_difference"], "expected": "0", "detected": True},
            {"name": "erase_localized_base_determinant", "constant_is_nonzero": erased["constant_is_nonzero"], "expected": False, "detected": True},
        ],
        "flags": {
            "DYNAMICAL_EMITTER_INPUT_UNDERDETERMINATION_CERTIFIED": True,
            "TWO_COMPATIBLE_RECOIL_COMPLETIONS_DIFFER": True,
            "FORMAL_RECOIL_RANK_TWO_STABILITY_CERTIFIED": True,
            "SPECIFIC_DYNAMICAL_EMITTER_MODEL_SELECTED": False,
            "EMITTER_BV_COMPLEX_CONSTRUCTED": False,
            "RECOIL_COEFFICIENT_COMPUTED": False,
            "FINITE_PARAMETER_COUPLED_GREEN_HYPERBOLICITY_CERTIFIED": False,
            "ORIGINAL_COMMON_HOPF_EMITTER_AT_CLOCK_ZERO_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "RECEIVE_A_DYNAMICAL_EMITTER_HANDOFF_OR_SELECT_AND_JUSTIFY_A_SPECIFIC_EMITTER_MATTER_MODEL_BEFORE_COMPUTING_RECOIL",
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
        raise SystemExit("stale dynamical-emitter recoil gate")
    print("BERGER_DYNAMICAL_EMITTER_RECOIL_INPUT_GATE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
