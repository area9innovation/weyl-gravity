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
OUTPUT = ROOT / "paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json"
INPUTS = {
    "strict_breaking": ROOT / "quantum-weyl/anomalies/certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json",
    "matter_no_go": ROOT / "quantum-weyl/anomalies/certificates/UNITARY_CONFORMAL_MATTER_CANCELLATION_NO_GO.json",
    "cotangent_lift": ROOT / "quantum-weyl/anomalies/certificates/WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json",
    "extended_cohomology": ROOT / "quantum-weyl/anomalies/certificates/WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_inputs() -> dict[str, dict[str, Any]]:
    values = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    strict = values["strict_breaking"]
    matter = values["matter_no_go"]
    lift = values["cotangent_lift"]
    extended = values["extended_cohomology"]
    if (
        strict.get("qme_disposition", {}).get("status")
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
    ):
        raise ValueError("Paper 12 theorem dependency drifted")
    return values


def build() -> dict[str, Any]:
    values = _load_inputs()
    strict = values["strict_breaking"]
    extended = values["extended_cohomology"]
    return {
        "schema": "paper-12-pure-weyl-one-loop-bv-anomaly-claim-map-v1",
        "result_id": "PAPER_12_PURE_WEYL_ONE_LOOP_BV_ANOMALY_DRAFT",
        "result_state": "DRAFT_ALLOWED_STRICT_OBSTRUCTION_AND_TAU_ADIC_EXTENDED_ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORATION",
        "lifecycle_state": "WRITING_STARTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "headline": "Strict pure Weyl gravity is locally QME-obstructed at one loop; the formal tau-adic compensator extension has a restored one-loop local Euclidean QME.",
        "manuscript": _relative(MANUSCRIPT),
        "manuscript_sha256": _sha256(MANUSCRIPT),
        "compiled_pdf": _relative(PDF),
        "compiled_pdf_sha256": _sha256(PDF),
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
            "quantum_Cartan_identity": False,
            "Bridge_4_particle_crosswalk": False,
            "Bridge_5_interacting_BRST_map": False,
            "theorem_frozen": False,
        },
        "next_gate": {
            "status": "EXTENDED_CLASSICAL_CONTRACTION_AND_ONE_LOOP_SLAVNOV_OPERATOR_Q1",
            "required_inputs": [
                "compensator-inclusive classical contraction",
                "coefficient-bearing restored one-loop Slavnov operator Q1",
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
