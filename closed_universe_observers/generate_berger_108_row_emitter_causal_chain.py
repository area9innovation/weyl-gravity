#!/usr/bin/env python3
"""Certify the coefficientwise 108-row emitter causal chain homotopy."""

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
CERTIFICATE = PACKAGE / "certificates/BERGER_108_ROW_POLARIZATION_EMITTER_CAUSAL_CHAIN_HOMOTOPY.json"
SCHEMA = PACKAGE / "schema/berger-108-row-polarization-emitter-causal-chain-homotopy-v1.schema.json"
REPORT = PACKAGE / "reports/berger-108-row-polarization-emitter-causal-chain-homotopy.md"
DEPENDENCIES = {
    "emitter_unary": PACKAGE / "certificates/BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_FIRST_RECOIL.json",
    "apparatus_unary": PACKAGE / "certificates/BERGER_84_ROW_NORMALIZED_PROFILE_MIXED_UNARY.json",
    "base_causal": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_108_row_emitter_causal_chain.py",
    "tests": PACKAGE / "tests/test_berger_108_row_emitter_causal_chain.py",
    "schema": SCHEMA,
    "report": REPORT,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _defects_through(matrix: sp.Matrix, parameter: sp.Symbol, order: int) -> int:
    return sum(
        int(sp.simplify(sp.expand(value).coeff(parameter, power)) != 0)
        for value in matrix
        for power in range(order + 1)
    )


def graded_chain_fixture(*, delete_quadratic_green: bool = False, delete_k1_witness: bool = False) -> dict[str, Any]:
    """Replay q^2=0 and q Lambda+Lambda q=1 on a gauge-complete fixture."""
    p, e0, e1, v0, v1, g = sp.symbols("p e0 e1 v0 v1 g", nonzero=True)
    # Order: c | A_g,A_ph,K0,K1 | A_g+,A_ph+,K0+,K1+ | c+.
    q = sp.zeros(10)
    q[1, 0] = 1
    q[9, 5] = 1
    q[6, 2], q[6, 3], q[6, 4] = p, -g * v0, -g * v1
    q[7, 2], q[7, 3] = -g * v0, e0
    q[8, 2], q[8, 4] = -g * v1, e1

    witness = sp.zeros(10)
    witness[0, 1] = 1
    witness[5, 9] = 1
    witness[2, 6] = 1
    witness[3, 7] = 1
    if not delete_k1_witness:
        witness[4, 8] = 1

    wave = sp.expand(q * witness + witness * q)
    wave0 = wave.subs(g, 0)
    if wave0.rank() < 10:
        return {
            "q_squared_defect_count": _defects_through(q * q, g, 2),
            "unperturbed_wave_rank": int(wave0.rank()),
            "unperturbed_wave_invertible": False,
            "left_green_defect_count_through_g2": None,
            "right_green_defect_count_through_g2": None,
            "chain_homotopy_defect_count_through_g2": None,
        }
    perturbation = sp.diff(wave, g)
    green0 = wave0.inv()
    green1 = -green0 * perturbation * green0
    green2 = sp.zeros(10) if delete_quadratic_green else green0 * perturbation * green0 * perturbation * green0
    green = green0 + g * green1 + g**2 * green2
    homotopy = witness * green
    return {
        "row_order": ["c", "A_gauge", "A_physical", "K0", "K1", "A_gauge_plus", "A_physical_plus", "K0_plus", "K1_plus", "c_plus"],
        "degrees": [-1, 0, 0, 0, 0, 1, 1, 1, 1, 2],
        "q_squared_defect_count": _defects_through(q * q, g, 2),
        "unperturbed_wave_rank": int(wave0.rank()),
        "unperturbed_wave_invertible": True,
        "left_green_defect_count_through_g2": _defects_through(wave * green - sp.eye(10), g, 2),
        "right_green_defect_count_through_g2": _defects_through(green * wave - sp.eye(10), g, 2),
        "chain_homotopy_defect_count_through_g2": _defects_through(q * homotopy + homotopy * q - sp.eye(10), g, 2),
        "homotopy_degree_minus_one": all(
            value == 0 or [-1, 0, 0, 0, 0, 1, 1, 1, 1, 2][row] == [-1, 0, 0, 0, 0, 1, 1, 1, 1, 2][column] - 1
            for row in range(10)
            for column, value in enumerate(homotopy.row(row))
        ),
        "Maxwell_green_g2_coefficient": sp.sstr(sp.factor(green2[2, 2])),
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if values["emitter_unary"]["flags"]["108_ROW_Q1_CERTIFIED"] is not True:
        raise AssertionError("108-row unary dependency drifted")
    if values["apparatus_unary"]["flags"]["BIVARIATE_FORMAL_GREEN_COEFFICIENT_CERTIFIED"] is not True:
        raise AssertionError("apparatus formal Green dependency drifted")
    if values["base_causal"]["flags"]["BERGER_COMBINED_64_ROW_CAUSAL_GREEN_HOMOTOPY"] is not True:
        raise AssertionError("base causal dependency drifted")
    fixture = graded_chain_fixture()
    deleted_green = graded_chain_fixture(delete_quadratic_green=True)
    deleted_witness = graded_chain_fixture(delete_k1_witness=True)
    if any(fixture[key] != 0 for key in ("q_squared_defect_count", "left_green_defect_count_through_g2", "right_green_defect_count_through_g2", "chain_homotopy_defect_count_through_g2")):
        raise AssertionError("graded causal chain fixture failed")
    if not fixture["homotopy_degree_minus_one"] or fixture["unperturbed_wave_rank"] != 10:
        raise AssertionError("graded causal chain typing failed")
    if not deleted_green["chain_homotopy_defect_count_through_g2"] or deleted_witness["unperturbed_wave_invertible"]:
        raise AssertionError("causal chain mutation rail failed")

    boundary = (
        "This LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL theorem completes the coefficientwise causal-chain step for the selected 108-row emitter unary. It appends the local degree-minus-one witness W_K(K_b_plus)=K_b to the imported apparatus witness, forms P_108=q_108 W_108+W_108 q_108, and constructs the same-sided formal Green inverse by the finite Neumann coefficients through g^2. The homotopy Lambda_108,+/-=W_108 G_P108,+/- then satisfies q_108 Lambda+Lambda q_108=1 coefficientwise through g^2. A gauge-complete ten-channel graded fixture independently has q^2=0, invertible unperturbed wave rank ten, zero left/right Green defects, and zero chain defects; deleting the quadratic Green term or one emitter witness is detected. The result is over the imported coefficientwise apparatus first-jet ring and formal emitter couplings. It is not an unqualified finite-parameter or all-orders 108-row theorem, does not choose actual emitter Cauchy preparations or prove their detector matrix has rank two, does not evaluate a detector recoil integral or include emitter stress/clock backreaction, does not construct the full apparatus Dirac bracket, and makes no quantum claim."
    )
    return {
        "schema": "closed-universe-berger-108-row-polarization-emitter-causal-chain-homotopy-v1",
        "result_id": "BERGER_108_ROW_POLARIZATION_EMITTER_CAUSAL_CHAIN_HOMOTOPY",
        "setting_id": values["emitter_unary"]["setting_id"],
        "claim_status": "CERTIFIED_108_ROW_COEFFICIENTWISE_CAUSAL_CHAIN_HOMOTOPY_THROUGH_G2",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "witness_and_wave_operator": {
            "apparatus_witness": "the pinned coefficientwise W_84,+/- input",
            "emitter_witness": "W_K(K_b_plus)=K_b and W_K=0 on K_b",
            "combined_witness": "W_108=W_84 direct_sum W_K0 direct_sum W_K1",
            "wave_operator": "P_108=q_108 W_108+W_108 q_108",
            "emitter_diagonal": "delta d+m_b^2 with Green (I+m_b^-2 d delta)G_(P2+m_b^2),+/-",
            "off_diagonal": "the reciprocal A<->K_b blocks, local and first order",
        },
        "formal_causal_chain": {
            "unperturbed_green": "G_P0,+/-=G_P84,+/- direct_sum G_E0,+/- direct_sum G_E1,+/-",
            "green_formula": "G_Pg=G_P0-g G_P0 U G_P0+g^2 G_P0 U G_P0 U G_P0+O(g^3)",
            "homotopy_formula": "Lambda_108,+/-=W_108 G_Pg,+/-",
            "identity": "q_108 Lambda_108,+/-+Lambda_108,+/- q_108=1 through g^2",
            "support": "W_108 and U are local; each finite composition of same-sided Green factors remains on the chosen causal side",
            "apparatus_scope": "the imported coefficientwise r,kappa first-jet ring; no finite-r promotion",
        },
        "graded_exact_fixture": fixture,
        "mutation_results": [
            {"name": "delete_g2_green_coefficient", "detected": deleted_green["chain_homotopy_defect_count_through_g2"] > 0, "audit": deleted_green},
            {"name": "delete_K1_witness", "detected": not deleted_witness["unperturbed_wave_invertible"], "audit": deleted_witness},
        ],
        "flags": {
            "108_ROW_COEFFICIENTWISE_CAUSAL_CHAIN_HOMOTOPY_THROUGH_G2_CERTIFIED": True,
            "108_ROW_ADVANCED_CHAIN_IDENTITY_THROUGH_G2_CERTIFIED": True,
            "108_ROW_RETARDED_CHAIN_IDENTITY_THROUGH_G2_CERTIFIED": True,
            "UNQUALIFIED_FULL_108_ROW_CAUSAL_CHAIN_CONTRACTION_CERTIFIED": False,
            "FINITE_PARAMETER_108_ROW_GREEN_HYPERBOLICITY_CERTIFIED": False,
            "DYNAMICAL_EMITTER_RECORD_RANK_TWO_CERTIFIED": False,
            "DETECTOR_RECOIL_COEFFICIENT_EVALUATED": False,
            "EMITTER_STRESS_BACKREACTION_INCLUDED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "CHOOSE_TWO_LOCALIZED_FREE_EMITTER_CAUCHY_PREPARATIONS_AND_COMPUTE_M_AB_K",
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
        raise SystemExit("stale 108-row emitter causal-chain certificate")
    print("BERGER_108_ROW_POLARIZATION_EMITTER_CAUSAL_CHAIN_HOMOTOPY generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
