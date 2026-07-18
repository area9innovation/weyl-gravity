#!/usr/bin/env python3
"""Generate the fail-closed claim map for the Paper 12 working draft."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "paper/12-pure-weyl-one-loop-bv-anomaly.tex"
PDF = ROOT / "paper/12-pure-weyl-one-loop-bv-anomaly.pdf"
SUPPLEMENT = ROOT / "paper/12-pure-weyl-one-loop-bv-anomaly-computational-supplement.tex"
SUPPLEMENT_PDF = ROOT / "paper/12-pure-weyl-one-loop-bv-anomaly-computational-supplement.pdf"
GENERATED_TABLES = ROOT / "paper/generated/12-quantum-anomaly-certificate-tables.tex"
TABLE_GENERATOR = ROOT / "paper/generate_12_quantum_anomaly_tables.py"
TABLE_VERIFIER = ROOT / "paper/verify_12_quantum_anomaly_tables.py"
OUTPUT = ROOT / "paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json"
INPUTS = {
    "strict_AFN0_even": ROOT / "quantum-weyl/local_bv/certificates/AFN0_H14_EVEN_CANONICAL_QUOTIENT.json",
    "strict_AFN0_odd": ROOT / "quantum-weyl/local_bv/certificates/AFN0_H14_ODD_CANONICAL_QUOTIENT.json",
    "strict_gauge_fixed": ROOT / "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json",
    "strict_breaking": ROOT / "quantum-weyl/anomalies/certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json",
    "matter_no_go": ROOT / "quantum-weyl/anomalies/certificates/UNITARY_CONFORMAL_MATTER_CANCELLATION_NO_GO.json",
    "cotangent_lift": ROOT / "quantum-weyl/anomalies/certificates/WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json",
    "extended_cohomology": ROOT / "quantum-weyl/anomalies/certificates/WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY.json",
    "Q1_disposition": ROOT / "quantum-weyl/transfer/certificates/ONE_LOOP_SLAVNOV_Q1_DISPOSITION.json",
    "anomaly_induced_Gamma1": ROOT / "quantum-weyl/transfer/certificates/ANOMALY_INDUCED_NONLOCAL_GAMMA1.json",
    "flat_TT_logarithmic_Gamma1": ROOT / "quantum-weyl/transfer/certificates/FLAT_TT_LOGARITHMIC_GAMMA1.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_inputs() -> dict[str, dict[str, Any]]:
    values = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    even = values["strict_AFN0_even"]
    odd = values["strict_AFN0_odd"]
    gauge = values["strict_gauge_fixed"]
    strict = values["strict_breaking"]
    matter = values["matter_no_go"]
    lift = values["cotangent_lift"]
    extended = values["extended_cohomology"]
    q1 = values["Q1_disposition"]
    gamma1 = values["anomaly_induced_Gamma1"]
    flat_tt_log = values["flat_TT_logarithmic_Gamma1"]
    if (
        even.get("result_state") != "COMPLETE_AFN0_EVEN_CANDIDATE_QUOTIENT"
        or even.get("smallest_relative_sector", {}).get("closure_rank") != 6
        or even.get("smallest_relative_sector", {}).get("boundary_rank") != 4
        or odd.get("result_state") != "COMPLETE_AFN0_ODD_CANDIDATE_QUOTIENT"
        or odd.get("smallest_relative_sector", {}).get("quotient_dimension") != 1
        or gauge.get("gauge_fixed_cohomology", {}).get("H14_even_dimension") != 2
        or gauge.get("gauge_fixed_cohomology", {}).get("H14_odd_dimension") != 1
        or strict.get("qme_disposition", {}).get("status")
        != "OBSTRUCTED_STRICT_FIELD_CONTENT"
        or strict.get("coefficients", {}).get("ANOM_OMEGA_C2")
        != {"numerator": 199, "denominator": 30}
        or strict.get("coefficients", {}).get("ANOM_OMEGA_E4")
        != {"numerator": -87, "denominator": 20}
        or matter.get("result_state")
        != "NO_NONNEGATIVE_STANDARD_UNITARY_FREE_MATTER_CANCELLATION"
        or lift.get("contractible_quartet", {}).get("status")
        != "EXACT_CONTRACTIBLE_WEYL_QUARTET_IN_DRESSED_VARIABLES"
        or extended.get("result_state")
        != "TAU_ADIC_EXTENDED_GAUGE_FIXED_H04_H14_COMPLETE_ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORED"
        or extended.get("H04", {}).get("even_quotient_dimension") != 3
        or extended.get("H04", {}).get("odd_quotient_dimension") != 1
        or extended.get("H14", {}).get("even_quotient_dimension") != 0
        or extended.get("H14", {}).get("odd_quotient_dimension") != 0
        or extended.get("one_loop_QME", {}).get("status")
        != "QME_RESTORED_AT_ONE_LOOP_LOCAL_EUCLIDEAN_TAU_ADIC_EXTENDED_THEORY"
        or q1.get("finite_counterterm_ambiguity", {}).get("bulk_response_rank") != 2
        or q1.get("decision", {}).get("complete_Q1") != "NO_CERTIFIED_OPERATOR"
        or q1.get("decision", {}).get("residual_transfer") != "FORBIDDEN"
        or gamma1.get("result_state")
        != "ANOMALY_INDUCED_EUCLIDEAN_GAMMA1_REPRESENTATIVE_CERTIFIED_WEYL_INVARIANT_REMAINDER_OPEN"
        or gamma1.get("exact_coefficient_solve", {}).get("rank") != 3
        or gamma1.get("decision", {}).get("complete_finite_nonlocal_Gamma1")
        != "NO_CERTIFIED_FUNCTIONAL"
        or flat_tt_log.get("decision", {}).get("flat_TT_universal_logarithmic_form_factor")
        != "CERTIFIED"
        or flat_tt_log.get("exact_logarithmic_form_factor", {}).get("logarithmic_coefficient")
        != {"numerator": -199, "denominator": 60}
        or flat_tt_log.get("claim_flags", {}).get("FINITE_C2_NORMALIZATION_FIXED")
        is not False
    ):
        raise ValueError("Paper 12 theorem dependency drifted")
    return values


def build() -> dict[str, Any]:
    values = _load_inputs()
    strict = values["strict_breaking"]
    extended = values["extended_cohomology"]
    gamma1 = values["anomaly_induced_Gamma1"]
    flat_tt_log = values["flat_TT_logarithmic_Gamma1"]
    return {
        "schema": "paper-12-pure-weyl-one-loop-bv-anomaly-claim-map-v1",
        "result_id": "PAPER_12_PURE_WEYL_ONE_LOOP_BV_ANOMALY_DRAFT",
        "result_state": "DRAFT_ALLOWED_STRICT_OBSTRUCTION_TAU_ADIC_EXTENDED_QME_RESTORATION_ANOMALY_INDUCED_GAMMA1_AND_FLAT_TT_LOGARITHM",
        "lifecycle_state": "WRITING_STARTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "headline": "Strict pure Weyl gravity is locally QME-obstructed at one loop; the formal tau-adic compensator extension has a restored one-loop local Euclidean QME, one exact conditional anomaly-induced Gamma1 representative, and an exact universal flat-TT logarithmic form factor.",
        "manuscript": _relative(MANUSCRIPT),
        "manuscript_sha256": _sha256(MANUSCRIPT),
        "compiled_pdf": _relative(PDF),
        "compiled_pdf_sha256": _sha256(PDF),
        "publication_artifacts": {
            _relative(path): _sha256(path)
            for path in (
                SUPPLEMENT,
                SUPPLEMENT_PDF,
                GENERATED_TABLES,
                TABLE_GENERATOR,
                TABLE_VERIFIER,
            )
        },
        "theory_dispositions": {
            "strict_fixed_field_content": "OBSTRUCTED",
            "tau_adic_compensator_extended_local_Euclidean_one_loop": "QME_RESTORED",
        },
        "certified_claims": {
            "strict_full_gauge_fixed_H14_even_dimension": 2,
            "strict_full_gauge_fixed_H14_odd_dimension": 1,
            "pure_Diff_and_mixed_additional_classes": 0,
            "C2_coefficient": strict["coefficients"]["ANOM_OMEGA_C2"],
            "E4_coefficient": strict["coefficients"]["ANOM_OMEGA_E4"],
            "CdualC_coefficient": strict["coefficients"]["ANOM_OMEGA_C_DUAL_C"],
            "BoxR_coefficient": strict["coefficients"]["ANOM_OMEGA_BOX_R"],
            "strict_one_loop_local_Euclidean_QME_obstructed": True,
            "standard_unitary_free_matter_cancellation_excluded": True,
            "minimal_BV_compensator_cotangent_lift_exact": True,
            "Weyl_quartet_contractible": True,
            "formal_tau_adic_coordinate_change_invertible": True,
            "extended_H04_even_dimension": extended["H04"]["even_quotient_dimension"],
            "extended_H04_odd_dimension": extended["H04"]["odd_quotient_dimension"],
            "extended_H14_even_dimension": extended["H14"]["even_quotient_dimension"],
            "extended_H14_odd_dimension": extended["H14"]["odd_quotient_dimension"],
            "extended_one_loop_local_Euclidean_QME_restored": True,
            "WZ_local_counterterm_Q1_contribution_fixed": True,
            "finite_counterterm_bulk_Q1_ambiguity_rank": 2,
            "anomaly_induced_nonlocal_Gamma1_representative": True,
            "anomaly_induced_functional_coefficients": gamma1["exact_coefficient_solve"]["solution_vector"],
            "flat_TT_logarithmic_form_factor": True,
            "flat_TT_logarithmic_coefficient": flat_tt_log["exact_logarithmic_form_factor"]["logarithmic_coefficient"],
            "flat_TT_scale_response": flat_tt_log["exact_logarithmic_form_factor"]["RG_scale_response"],
        },
        "explicit_nonclaims": {
            "finite_polynomial_in_tau_theorem": False,
            "all_loop_extended_QME": False,
            "Lorentzian_QME": False,
            "renormalized_Lorentzian_products": False,
            "global_BRST_Hadamard_state": False,
            "positive_particle_Hilbert_space": False,
            "unitarity_theorem": False,
            "residual_quantum_transfer": False,
            "complete_renormalized_Q1_supplied": False,
            "complete_renormalized_Gamma1_supplied": False,
            "quantum_Cartan_identity": False,
            "Bridge_4_particle_crosswalk": False,
            "Bridge_5_interacting_BRST_map": False,
            "theorem_frozen": False,
        },
        "next_gate": {
            "status": "CURVED_WEYL_INVARIANT_GAMMA1_REMAINDER_FINITE_C2_R2_NORMALIZATION_AND_EXTENDED_CLASSICAL_CONTRACTION",
            "required_inputs": [
                "compensator-inclusive classical contraction",
                "finite C2 and R2 normalization conditions",
                "curved Weyl-invariant Gamma1 completion and global Paneitz Green data",
                "renormalized BV operator data fixing complete Q1",
            ],
            "required_outputs": [
                "q1=pi_ext Q1 iota_ext",
                "first-order residual nilpotency",
                "quantum D-Cartan defect",
                "H3-to-H4 and H4-to-H5 maps",
                "pairing correction",
            ],
        },
        "inputs": {
            _relative(path): {
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in INPUTS.items()
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text() != rendered:
            raise SystemExit("Paper 12 claim map is stale; rerun with --emit")
    if not args.emit and not args.check:
        print(rendered, end="")


if __name__ == "__main__":
    main()
