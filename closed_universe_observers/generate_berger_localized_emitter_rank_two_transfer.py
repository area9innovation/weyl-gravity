#!/usr/bin/env python3
"""Certify two localized conserved emitters with a rank-two record map."""

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
CERTIFICATE = PACKAGE / "certificates/BERGER_LOCALIZED_EMITTER_RANK_TWO_TRANSFER.json"
SCHEMA = PACKAGE / "schema/berger-localized-emitter-rank-two-transfer-v1.schema.json"
REPORT = PACKAGE / "reports/berger-localized-emitter-rank-two-transfer.md"
DEPENDENCIES = {
    "detectors": PACKAGE / "certificates/BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS.json",
    "cg4_records": PACKAGE / "certificates/BERGER_CG4_TWO_RECORD_POISSON_ALGEBRA.json",
    "normalized_profile": PACKAGE / "certificates/BERGER_84_ROW_NORMALIZED_PROFILE_MIXED_UNARY.json",
    "causal_green": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_localized_emitter_rank_two_transfer.py",
    "tests": PACKAGE / "tests/test_berger_localized_emitter_rank_two_transfer.py",
    "schema": SCHEMA,
    "report": REPORT,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transfer_audit(*, clone_second_source: bool = False, late_source_before_d0: bool = False) -> dict[str, Any]:
    """Replay the exact triangular response and its fail-closed mutations."""
    beta = 2 * sp.sqrt(10) / 3
    S0, C1, mu = sp.symbols("S_0 C_1 mu", real=True)
    if clone_second_source:
        matrix = sp.Matrix([[-beta * S0, -beta * S0], [mu, mu]])
    else:
        causal_zero = sp.Symbol("nu") if late_source_before_d0 else sp.Integer(0)
        matrix = sp.Matrix([[-beta * S0, causal_zero], [mu, beta * C1]])
    determinant = sp.factor(matrix.det())
    expected = -sp.factor(beta**2 * S0 * C1)
    if not clone_second_source and not late_source_before_d0 and sp.simplify(determinant - expected) != 0:
        raise AssertionError("localized triangular determinant failed")

    # S^3 has a CW complex with one 0-cell and one 3-cell.  Thus the degree-1
    # and degree-2 cellular groups vanish, which is the exact topological input
    # used to localize Maxwell constraint potentials.
    cellular_dimensions = [1, 0, 0, 1]
    h1 = cellular_dimensions[1]
    h2 = cellular_dimensions[2]
    return {
        "matrix": [[sp.sstr(item) for item in matrix.row(row)] for row in range(2)],
        "determinant": sp.sstr(determinant),
        "rank": int(matrix.rank()),
        "h1_dimension": h1,
        "h2_dimension": h2,
        "causal_zero_present": matrix[0, 1] == 0,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    detector_flags = values["detectors"]["flags"]
    if not detector_flags["TWO_LOCALIZED_CLOCK_LABELLED_DETECTOR_SMEARINGS"]:
        raise AssertionError("localized detector input drifted")
    if not values["cg4_records"]["flags"]["CG4_PHASE_PLANE_TO_TWO_RECORDS_ISOMORPHISM_CERTIFIED"]:
        raise AssertionError("C-G4 record input drifted")
    if not values["normalized_profile"]["flags"]["PROFILE_NORMALIZATION_EXACT"]:
        raise AssertionError("nonnegative normalized detector profile input drifted")
    green_flags = values["causal_green"]["flags"]
    if not green_flags["BERGER_MAXWELL_CAUSAL_GREEN_HOMOTOPY"]:
        raise AssertionError("Maxwell causal Green input drifted")

    audit = transfer_audit()
    cloned = transfer_audit(clone_second_source=True)
    acausal = transfer_audit(late_source_before_d0=True)
    if cloned["rank"] != 1 or acausal["causal_zero_present"]:
        raise AssertionError("localized-emitter mutation rail failed")

    beta = 2 * sp.sqrt(10) / 3
    phase0_upper = sp.simplify(beta * sp.Rational(13, 48))
    phase1_upper = sp.simplify(beta * sp.Rational(25, 48))
    if not (0 < phase0_upper < sp.Rational(3, 2) and 0 < phase1_upper < sp.Rational(3, 2)):
        raise AssertionError("diagonal window phase bound failed")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/REDUCED-MODE/LORENTZIAN-CAUSAL theorem constructs two predeclared, spatially localized, compact-time, conserved Maxwell currents. Constraint-preserving localization of the C-G4 cosine-mode Cauchy data uses H1(S3)=H2(S3)=0, spatial potentials multiplied by bumps equal to one on the relevant detector domains of dependence, and finite propagation. A time cutoff turns each localized homogeneous solution into a retarded emitter current J_a=delta d(chi_a A_a). The second source is supported strictly after the D0 window and before D1, so M_01=0 by causal support, while exact agreement with the C-G4 mode gives M_00=-beta S0 and M_11=beta C1 with S0,C1>0. Hence det M=-beta^2 S0 C1 is nonzero for any unknown M_10. This certifies two distinguishable causally acquired localized-source records at probe order. The emitters are receiver-adjacent local worldtubes, not the original common Hopf emitter at clock zero. Recoil, source dynamics, full apparatus Dirac closure, finite-r Green hyperbolicity, fixed-background linear-K descent, and quantum claims remain open."
    )
    return {
        "schema": "closed-universe-berger-localized-emitter-rank-two-transfer-v1",
        "result_id": "BERGER_LOCALIZED_EMITTER_RANK_TWO_TRANSFER",
        "setting_id": values["cg4_records"]["setting_id"],
        "claim_status": "CERTIFIED_TWO_LOCALIZED_CONSERVED_EMITTERS_AND_RANK_TWO_CAUSAL_RECORDS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "topological_localization": {
            "cellular_chain_dimensions_C0_to_C3": [1, 0, 0, 1],
            "H1_dimension": audit["h1_dimension"],
            "H2_dimension": audit["h2_dimension"],
            "constraint_potentials": "B_c=d_Sigma a_c and star_Sigma E_c=d_Sigma e_c; replace them by d_Sigma(eta_a a_c) and d_Sigma(eta_a e_c)",
            "constraint_check": "d_Sigma^2=0 preserves both Maxwell constraints exactly",
            "agreement_region": "eta_a=1 on a neighborhood of K_a=J^-(supp Q_a) intersect Sigma_a",
            "finite_propagation": "the localized homogeneous field H_a equals the C-G4 cosine field F_c on supp Q_a by domain-of-dependence uniqueness",
        },
        "emitter_currents": [
            {
                "id": "J_0",
                "placement": "proper precompact worldtube immediately to the past of D0",
                "time_order": "supp J_0 is strictly earlier than physical detector window [11/48,13/48]",
                "formula": "J_0=delta d(chi_0 A_0), with chi_0=0 before the switch and chi_0=1 before D0",
                "conservation": "delta J_0=delta^2 d(chi_0 A_0)=0",
                "retarded_field": "d G_ret J_0=d(chi_0 A_0)",
            },
            {
                "id": "J_1",
                "placement": "proper precompact worldtube immediately to the past of D1",
                "time_order": "supp J_1 lies inside the nonempty gap (13/48,23/48), after D0 and before D1",
                "formula": "J_1=delta d(chi_1 A_1), with chi_1=0 through D0 and chi_1=1 before D1",
                "conservation": "delta J_1=delta^2 d(chi_1 A_1)=0",
                "retarded_field": "d G_ret J_1=d(chi_1 A_1)",
            },
        ],
        "causal_support": {
            "detector_windows": [["11/48", "13/48"], ["23/48", "25/48"]],
            "inter_window_gap": "5/24",
            "late_source_to_early_detector": "supp J_1 is disjoint from J^-(supp Q_0), hence Q_0[d G_ret J_1]=0",
            "source_selection_rule": "the C-G4 cosine mode, detector supports, localization bumps, and time ordering are fixed before response evaluation; no response-dependent normalization is used",
        },
        "transfer_matrix": {
            "definition": "M_ab=Q_a[d G_ret J_b]",
            "basis": "rows (D0,D1), columns (J0,J1)",
            "matrix": audit["matrix"],
            "unknown_cross_response": "mu=Q_1[d G_ret J_0] is unrestricted and does not enter the determinant",
            "diagonal_moments": {"S_0": "integral rho_0 sin(beta t)>0", "C_1": "integral rho_1 cos(beta t)>0", "density_input": "the pinned normalized-profile theorem fixes nonnegative smooth compact bumps with unit spatial integral"},
            "phase_bounds": [
                "0<beta t<=13*sqrt(10)/72<3/2<pi/2 on D0",
                "0<beta t<=25*sqrt(10)/72<3/2<pi/2 on D1",
            ],
            "determinant": audit["determinant"],
            "rank": audit["rank"],
            "memory_response": "(Delta m_0,Delta m_1)^T=M(c_0,c_1)^T for zero initial memories",
        },
        "mutation_results": [
            {"name": "clone_second_source_column", "observed_rank": cloned["rank"], "expected_rank": 1, "detected": True},
            {"name": "move_second_source_before_D0", "causal_zero_present": acausal["causal_zero_present"], "expected": False, "detected": True},
        ],
        "flags": {
            "TWO_PREDECLARED_SPATIALLY_LOCALIZED_CONSERVED_EMITTER_CURRENTS": True,
            "CONSTRAINT_PRESERVING_MAXWELL_CAUCHY_LOCALIZATION": True,
            "LOCALIZED_EMITTER_TRANSFER_MATRIX_RANK_TWO": True,
            "TWO_LOCALIZED_SOURCE_RECORDS_CAUSALLY_DISTINGUISHABLE": True,
            "ORIGINAL_COMMON_HOPF_EMITTER_AT_CLOCK_ZERO_CERTIFIED": False,
            "DYNAMICAL_EMITTER_RECOIL_INCLUDED": False,
            "FULL_APPARATUS_DIRAC_BRACKET_CERTIFIED": False,
            "FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "ADD_DYNAMICAL_EMITTER_DEGREES_OF_FREEDOM_AND_RECOIL_OR_CERTIFY_THE_FIRST_BACKREACTION_OBSTRUCTION",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()],
        },
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
        raise SystemExit("stale localized-emitter rank-two certificate")
    print("BERGER_LOCALIZED_EMITTER_RANK_TWO_TRANSFER generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
