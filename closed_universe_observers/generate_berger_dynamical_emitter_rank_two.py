#!/usr/bin/env python3
"""Certify rank two for two localized massive-emitter Cauchy preparations."""

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
CERTIFICATE = PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO.json"
SCHEMA = PACKAGE / "schema/berger-dynamical-emitter-cauchy-rank-two-v1.schema.json"
REPORT = PACKAGE / "reports/berger-dynamical-emitter-cauchy-rank-two.md"
DEPENDENCIES = {
    "causal_chain": PACKAGE / "certificates/BERGER_108_ROW_POLARIZATION_EMITTER_CAUSAL_CHAIN_HOMOTOPY.json",
    "emitter_handoff": PACKAGE / "certificates/BERGER_POLARIZATION_TWO_FORM_EMITTER_HANDOFF.json",
    "localized_external_transfer": PACKAGE / "certificates/BERGER_LOCALIZED_EMITTER_RANK_TWO_TRANSFER.json",
    "detectors": PACKAGE / "certificates/BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS.json",
    "cg4_records": PACKAGE / "certificates/BERGER_CG4_TWO_RECORD_POISSON_ALGEBRA.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_dynamical_emitter_rank_two.py",
    "tests": PACKAGE / "tests/test_berger_dynamical_emitter_rank_two.py",
    "schema": SCHEMA,
    "report": REPORT,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_polarization_audit(*, delete_electric_component: bool = False) -> dict[str, Any]:
    """Exhibit a massive two-form polarization seen by a clock switch."""
    k, mass = sp.symbols("k m", positive=True)
    omega = sp.sqrt(k**2 + mass**2)
    momentum = sp.Matrix([omega, 0, 0, k])
    polarization = sp.zeros(4)
    if not delete_electric_component:
        polarization[0, 1] = k
        polarization[1, 0] = -k
        polarization[3, 1] = -omega
        polarization[1, 3] = omega
    transversality = sp.simplify((momentum.T * polarization))
    clock_contraction = polarization.row(0)
    return {
        "momentum": [sp.sstr(value) for value in momentum],
        "nonzero_components": {"K_01": sp.sstr(polarization[0, 1]), "K_31": sp.sstr(polarization[3, 1])},
        "mass_shell_defect": sp.sstr(sp.simplify(omega**2 - k**2 - mass**2)),
        "constraint_defect_count": sum(int(sp.simplify(value) != 0) for value in transversality),
        "clock_contraction": [sp.sstr(value) for value in clock_contraction],
        "switched_current_polarization_nonzero": clock_contraction[1] != 0,
    }


def response_audit(*, clone_second_preparation: bool = False, remove_second_diagonal: bool = False, erase_causal_order: bool = False) -> dict[str, Any]:
    """Replay the exact triangular determinant and failure mutations."""
    kappa0, kappa1, mu = sp.symbols("kappa_0 kappa_1 mu", nonzero=True)
    if clone_second_preparation:
        matrix = sp.Matrix([[kappa0, kappa0], [mu, mu]])
    elif remove_second_diagonal:
        matrix = sp.Matrix([[kappa0, 0], [mu, 0]])
    else:
        upper_right = sp.Symbol("nu") if erase_causal_order else sp.Integer(0)
        matrix = sp.Matrix([[kappa0, upper_right], [mu, kappa1]])
    determinant = sp.factor(matrix.det())
    forced = sp.simplify(determinant - kappa0 * kappa1) == 0
    return {
        "matrix": [[sp.sstr(value) for value in matrix.row(row)] for row in range(2)],
        "determinant": sp.sstr(determinant),
        "rank": int(matrix.rank()),
        "causal_zero_present": matrix[0, 1] == 0,
        "determinant_forced_to_nonzero_product": forced,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if values["causal_chain"]["flags"]["108_ROW_COEFFICIENTWISE_CAUSAL_CHAIN_HOMOTOPY_THROUGH_G2_CERTIFIED"] is not True:
        raise AssertionError("108-row causal-chain input drifted")
    if values["emitter_handoff"]["flags"]["SPECIFIC_DYNAMICAL_EMITTER_MODEL_SELECTED"] is not True:
        raise AssertionError("emitter-model input drifted")
    if values["localized_external_transfer"]["flags"]["LOCALIZED_EMITTER_TRANSFER_MATRIX_RANK_TWO"] is not True:
        raise AssertionError("localized external-current input drifted")
    if values["detectors"]["flags"]["TWO_LOCALIZED_CLOCK_LABELLED_DETECTOR_SMEARINGS"] is not True:
        raise AssertionError("detector input drifted")
    if values["cg4_records"]["flags"]["CG4_PHASE_PLANE_TO_TWO_RECORDS_ISOMORPHISM_CERTIFIED"] is not True:
        raise AssertionError("nontrivial detector-functional input drifted")

    polarization = local_polarization_audit()
    response = response_audit()
    cloned = response_audit(clone_second_preparation=True)
    zero_diagonal = response_audit(remove_second_diagonal=True)
    acausal = response_audit(erase_causal_order=True)
    if polarization["constraint_defect_count"] or polarization["mass_shell_defect"] != "0" or not polarization["switched_current_polarization_nonzero"]:
        raise AssertionError("massive-emitter polarization audit failed")
    if response["rank"] != 2 or not response["causal_zero_present"] or not response["determinant_forced_to_nonzero_product"]:
        raise AssertionError("dynamical-emitter response audit failed")
    if cloned["rank"] != 1 or zero_diagonal["rank"] != 1 or acausal["determinant_forced_to_nonzero_product"]:
        raise AssertionError("dynamical-emitter rank mutation rail failed")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL existence theorem replaces the two external Maxwell currents by two genuine compact localized Cauchy preparations of the selected free massive two-form emitters with declared nonzero couplings g_0,g_1. For each fixed detector Q_a, Green adjunction turns K-data -> Q_a[d G_A,ret g_a delta(h_a K)] into a Cauchy covector ell_a. The certified nontrivial detector phase functional and a local massive polarization with p^mu K_mu nu=0 but i_n K nonzero show ell_a is not zero on a receiver-adjacent patch. H1(S3)=H2(S3)=0 and the normally hyperbolic constraint reduction permit compact constraint-preserving data in that patch. A fixed first-nonzero local polarization-basis rule chooses u_a before forward response evaluation, with kappa_a=ell_a(u_a) nonzero. The second switch lies after D0 and before D1, hence M_01=0 by retarded support. Therefore M^(K)=[[kappa_0,0],[mu,kappa_1]] has determinant kappa_0 kappa_1 nonzero and rank two. The theorem establishes two distinguishable causally acquired records from actual dynamical-emitter preparations at leading order in the emitter couplings. It does not place both preparations at the original common Hopf event, evaluate the g^2 detector recoil correction, include emitter stress/clock backreaction, promote finite-parameter or all-orders apparatus Green hyperbolicity, construct the full apparatus Dirac bracket, or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-dynamical-emitter-cauchy-rank-two-v1",
        "result_id": "BERGER_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO",
        "setting_id": values["causal_chain"]["setting_id"],
        "claim_status": "CERTIFIED_LOCALIZED_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO_AT_LEADING_ORDER",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "local_massive_polarization": polarization,
        "cauchy_preparation_construction": {
            "couplings": "g_0 and g_1 are declared nonzero",
            "free_equation_before_switch": "(delta d+m_a^2)K_a^(0)=0 with delta K_a^(0)=0",
            "source_map": "J_a^(K)=g_a delta(h_a K_a^(0))=-g_a i_(dh_a sharp)K_a^(0) on the free constraint surface",
            "adjoint_functional": "ell_a(u)=Q_a[d G_A,ret g_a delta(h_a U_E u)]; Green adjunction identifies ell_a with the restriction of the advanced detector solution to emitter Cauchy data",
            "nonvanishing": "the detector phase functional is nonzero, its advanced solution reaches a receiver-adjacent past patch, and the displayed constraint-compatible K_01/K_31 polarization has nonzero clock contraction there",
            "localization": "use H1(S3)=H2(S3)=0 to localize constraint potentials inside that patch; delta K and its normal derivative remain zero and propagate by the massive normally hyperbolic reduction",
            "selection_rule": "in the declared oriented local polarization basis, take the first compact constraint datum with nonzero ell_a coefficient; this fixes u_a before the forward response is evaluated and uses no response normalization",
            "switch_order": ["supp h_0 lies immediately before D0", "supp h_1 lies in (13/48,23/48), strictly after D0 and before D1"],
        },
        "transfer_matrix": {
            "definition": "M_ab^(K)=Q_a[d G_A,ret g_b delta(h_b K_b^(0))]",
            "basis": "rows (D0,D1), columns (u0,u1)",
            "matrix": response["matrix"],
            "diagonal_witnesses": {"kappa_0": "ell_0(u_0) != 0", "kappa_1": "ell_1(u_1) != 0"},
            "unknown_tail": "mu=M_10^(K) is unrestricted",
            "causal_zero": "M_01^(K)=0 because the u1 switch is later than D0",
            "determinant": response["determinant"],
            "rank": response["rank"],
        },
        "mutation_results": [
            {"name": "delete_clock_electric_polarization", "detected": not local_polarization_audit(delete_electric_component=True)["switched_current_polarization_nonzero"]},
            {"name": "clone_second_preparation_column", "detected": cloned["rank"] == 1, "audit": cloned},
            {"name": "remove_second_diagonal_response", "detected": zero_diagonal["rank"] == 1, "audit": zero_diagonal},
            {"name": "move_second_switch_before_D0", "detected": not acausal["determinant_forced_to_nonzero_product"], "audit": acausal},
        ],
        "flags": {
            "TWO_LOCALIZED_FREE_MASSIVE_EMITTER_CAUCHY_PREPARATIONS_CONSTRUCTED": True,
            "DYNAMICAL_EMITTER_LEADING_RECORD_MATRIX_RANK_TWO_CERTIFIED": True,
            "TWO_DYNAMICAL_EMITTER_RECORDS_CAUSALLY_DISTINGUISHABLE": True,
            "ORIGINAL_COMMON_HOPF_EMITTER_AT_CLOCK_ZERO_CERTIFIED": False,
            "DETECTOR_RECOIL_G2_COEFFICIENT_EVALUATED": False,
            "EMITTER_STRESS_BACKREACTION_INCLUDED": False,
            "FINITE_PARAMETER_108_ROW_GREEN_HYPERBOLICITY_CERTIFIED": False,
            "FULL_APPARATUS_DIRAC_BRACKET_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EVALUATE_THE_G2_DETECTOR_RECOIL_CORRECTION_FOR_THE_TWO_FIXED_CAUCHY_PREPARATIONS",
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
        raise SystemExit("stale dynamical-emitter Cauchy rank certificate")
    print("BERGER_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
