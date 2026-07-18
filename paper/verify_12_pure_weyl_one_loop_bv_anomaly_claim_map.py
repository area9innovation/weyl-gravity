#!/usr/bin/env python3
"""Independent fail-closed verification of the Paper 12 claim map."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAIM_MAP = ROOT / "paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    payload = json.loads(CLAIM_MAP.read_text())
    assert payload["schema"] == "paper-12-pure-weyl-one-loop-bv-anomaly-claim-map-v1"
    assert payload["result_id"] == "PAPER_12_PURE_WEYL_ONE_LOOP_BV_ANOMALY_DRAFT"
    assert payload["lifecycle_state"] == "WRITING_STARTED"
    assert payload["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
        "REDUCED-MODE",
        "LORENTZIAN-CAUSAL",
    ]
    manuscript = ROOT / payload["manuscript"]
    assert manuscript.is_file()
    assert _sha256(manuscript) == payload["manuscript_sha256"]
    compiled_pdf = ROOT / payload["compiled_pdf"]
    assert compiled_pdf.is_file()
    assert _sha256(compiled_pdf) == payload["compiled_pdf_sha256"]
    artifacts = payload["publication_artifacts"]
    assert len(artifacts) == 5
    for relative, expected in artifacts.items():
        artifact = ROOT / relative
        assert artifact.is_file(), relative
        assert _sha256(artifact) == expected, relative

    dispositions = payload["theory_dispositions"]
    assert dispositions == {
        "strict_fixed_field_content": "OBSTRUCTED",
        "tau_adic_compensator_extended_local_Euclidean_one_loop": "QME_RESTORED",
    }
    claims = payload["certified_claims"]
    assert claims["strict_full_gauge_fixed_H14_even_dimension"] == 2
    assert claims["strict_full_gauge_fixed_H14_odd_dimension"] == 1
    assert claims["pure_Diff_and_mixed_additional_classes"] == 0
    assert claims["C2_coefficient"] == {"numerator": 199, "denominator": 30}
    assert claims["E4_coefficient"] == {"numerator": -87, "denominator": 20}
    assert claims["CdualC_coefficient"] == {"numerator": 0, "denominator": 1}
    assert claims["BoxR_coefficient"] == {"numerator": 0, "denominator": 1}
    assert claims["extended_H04_even_dimension"] == 3
    assert claims["extended_H04_odd_dimension"] == 1
    assert claims["extended_H14_even_dimension"] == 0
    assert claims["extended_H14_odd_dimension"] == 0
    assert claims["finite_counterterm_bulk_Q1_ambiguity_rank"] == 2
    assert claims["anomaly_induced_nonlocal_Gamma1_representative"] is True
    assert claims["anomaly_induced_functional_coefficients"] == [
        {"numerator": 199, "denominator": 120},
        {"numerator": -87, "denominator": 160},
        {"numerator": 29, "denominator": 120},
    ]
    assert claims["flat_TT_logarithmic_form_factor"] is True
    assert claims["flat_TT_logarithmic_coefficient"] == {
        "numerator": -199,
        "denominator": 60,
    }
    assert claims["flat_TT_scale_response"] == {
        "numerator": 199,
        "denominator": 30,
    }
    assert claims["covariant_C2_log_through_curvature_order_two"] is True
    assert claims["first_unresolved_C2_log_completion_order"] == 3
    assert claims["Berger_WZ_tau_contraction_merge_rejected"] is True
    assert claims["reduced_vacuum_cylinder_Bridge_4"] is True
    assert claims["reduced_vacuum_cylinder_state_space_sign"] == "PLUS_E_MINUS_A_MINUS_L"
    boolean_claims = {
        key: value for key, value in claims.items() if isinstance(value, bool)
    }
    assert boolean_claims and all(boolean_claims.values())
    assert payload["explicit_nonclaims"]
    assert all(value is False for value in payload["explicit_nonclaims"].values())
    assert (
        payload["next_gate"]["status"]
        == "C2_CUBIC_CURVATURE_COMPLETION_R2_FORM_FACTOR_FINITE_C2_R2_NORMALIZATION_AND_SAME_BACKGROUND_EXTENDED_CLASSICAL_CONTRACTION"
    )

    dependencies = {}
    assert len(payload["inputs"]) == 12
    for relative, reference in payload["inputs"].items():
        path = ROOT / relative
        assert path.is_file(), relative
        assert _sha256(path) == reference["sha256"], relative
        value = json.loads(path.read_text())
        assert value["result_id"] == reference["result_id"], relative
        dependencies[reference["result_id"]] = value

    strict = dependencies["REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING"]
    extended = dependencies["WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY"]
    q1 = dependencies["ONE_LOOP_SLAVNOV_Q1_DISPOSITION"]
    gamma1 = dependencies["ANOMALY_INDUCED_NONLOCAL_GAMMA1"]
    flat_tt_log = dependencies["FLAT_TT_LOGARITHMIC_GAMMA1"]
    curvature_squared_log = dependencies["CURVATURE_SQUARED_COVARIANT_LOG_GAMMA1"]
    reduced_bridge4 = dependencies["VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD"]
    assert strict["qme_disposition"]["status"] == "OBSTRUCTED_STRICT_FIELD_CONTENT"
    assert strict["coefficients"]["ANOM_OMEGA_C2"] == claims["C2_coefficient"]
    assert strict["coefficients"]["ANOM_OMEGA_E4"] == claims["E4_coefficient"]
    assert extended["H04"]["even_quotient_dimension"] == 3
    assert extended["H14"]["boundary_rank"] == 4
    assert (
        extended["one_loop_QME"]["strict_breaking_coordinates"]
        == extended["one_loop_QME"]["boundary_image_coordinates"]
    )
    assert extended["lifecycle"]["residual_transfer"].startswith("FORBIDDEN_")
    assert q1["finite_counterterm_ambiguity"]["bulk_response_rank"] == 2
    assert q1["decision"]["complete_Q1"] == "NO_CERTIFIED_OPERATOR"
    assert q1["decision"]["residual_transfer"] == "FORBIDDEN"
    assert gamma1["exact_coefficient_solve"]["rank"] == 3
    assert gamma1["decision"]["complete_finite_nonlocal_Gamma1"] == "NO_CERTIFIED_FUNCTIONAL"
    assert flat_tt_log["decision"]["flat_TT_universal_logarithmic_form_factor"] == "CERTIFIED"
    assert flat_tt_log["claim_flags"]["FINITE_C2_NORMALIZATION_FIXED"] is False
    assert curvature_squared_log["operator_choice_independence"]["first_difference_order"] == 3
    assert curvature_squared_log["decision"]["residual_transfer"] == "FORBIDDEN"
    assert reduced_bridge4["decision"]["Bridge_4_reduced_vacuum_cylinder"] == "CERTIFIED"
    assert reduced_bridge4["decision"]["Bridge_4_full_BV"] == "NO_CERTIFIED_MAP"
    print("Paper 12 pure-Weyl one-loop BV anomaly claim map: PASS")


if __name__ == "__main__":
    main()
