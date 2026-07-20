"""Exact completion audit for the local one-loop BV anomaly programme."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

DEPENDENCIES = {
    "H04_gauge_fixed": HERE / "cohomology/H04_GAUGE_FIXED_BV_RESULT.json",
    "H14_gauge_fixed": HERE / "cohomology/H14_GAUGE_FIXED_BV_RESULT.json",
    "full_BV_contraction": (
        HERE / "certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json"
    ),
    "type_D_triviality": HERE / "certificates/TRIVIALITY_CERTIFICATE.json",
    "standard_coefficients": (
        ROOT
        / "spectral/euclidean/certificates/"
        "WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT.json"
    ),
    "repository_coefficients": (
        ROOT
        / "spectral/euclidean/certificates/"
        "REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH.json"
    ),
    "round_S4_Euler": (
        ROOT
        / "spectral/euclidean/certificates/"
        "REPOSITORY_ROUND_S4_EULER_COEFFICIENT.json"
    ),
    "strict_Slavnov": (
        ROOT
        / "anomalies/certificates/"
        "REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json"
    ),
    "strict_antifield_completion": (
        ROOT
        / "anomalies/certificates/"
        "REGULATED_SLAVNOV_ANTIFIELD_COMPLETION.json"
    ),
    "WZ_cotangent_lift": (
        ROOT
        / "anomalies/certificates/"
        "WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json"
    ),
    "WZ_extended_cohomology": (
        ROOT
        / "anomalies/certificates/"
        "WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY.json"
    ),
}

EXPECTED_VECTOR = {
    "ANOM_OMEGA_C2": Fraction(199, 30),
    "ANOM_OMEGA_E4": Fraction(-87, 20),
    "ANOM_OMEGA_C_DUAL_C": Fraction(0),
    "ANOM_OMEGA_BOX_R": Fraction(0),
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _fraction(value: str | dict[str, int]) -> Fraction:
    if isinstance(value, str):
        return Fraction(value)
    return Fraction(value["numerator"], value["denominator"])


def _rank(matrix: list[list[dict[str, int]]]) -> int:
    rows = [[_fraction(item) for item in row] for row in matrix]
    if not rows:
        return 0
    rank = 0
    column = 0
    while rank < len(rows) and column < len(rows[0]):
        pivot = next(
            (index for index in range(rank, len(rows)) if rows[index][column]),
            None,
        )
        if pivot is None:
            column += 1
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for index in range(len(rows)):
            if index == rank:
                continue
            scale = rows[index][column]
            if scale:
                rows[index] = [
                    value - scale * pivot_value
                    for value, pivot_value in zip(rows[index], rows[rank])
                ]
        rank += 1
        column += 1
    return rank


def _matrix_is_identity(matrix: list[list[int]]) -> bool:
    return matrix == [
        [1 if row == column else 0 for column in range(len(matrix))]
        for row in range(len(matrix))
    ]


def evaluate() -> dict[str, Any]:
    values = {name: _load(path) for name, path in DEPENDENCIES.items()}
    h04 = values["H04_gauge_fixed"]
    h14 = values["H14_gauge_fixed"]
    contraction = values["full_BV_contraction"]
    triviality = values["type_D_triviality"]
    standard = values["standard_coefficients"]
    repository = values["repository_coefficients"]
    sphere = values["round_S4_Euler"]
    strict = values["strict_Slavnov"]
    strict_afn = values["strict_antifield_completion"]
    lift = values["WZ_cotangent_lift"]
    extended = values["WZ_extended_cohomology"]

    h04_classes = {
        row["representative_id"] for row in h04["classes"]
        if row["status"] == "NONTRIVIAL"
    }
    h14_classes = {
        row["representative_id"] for row in h14["classes"]
        if row["status"] == "NONTRIVIAL"
    }
    cohomology_checks = {
        "regular_Bach_locus_scope": (
            h04["regularity_scope"] == h14["regularity_scope"]
            == "REGULAR_BACH_LOCUS"
        ),
        "H04_dimensions_two_even_one_odd": (
            h04["parity_dimensions"] == {"even": 2, "odd": 1}
        ),
        "H04_basis_complete": h04_classes
        == {"CT_C2", "CT_E4", "CT_C_DUAL_C"},
        "H14_dimensions_two_even_one_odd": (
            h14["parity_dimensions"] == {"even": 2, "odd": 1}
        ),
        "H14_basis_complete": h14_classes
        == {"ANOM_OMEGA_C2", "ANOM_OMEGA_E4", "ANOM_OMEGA_C_DUAL_C"},
        "type_D_rows_exact": (
            h04["exact_rows"] == ["CT_BOX_R"]
            and h14["exact_rows"] == ["ANOM_OMEGA_BOX_R"]
            and triviality["checks"]["omega_box_r_relative_trivialization"]
            == "VERIFIED"
        ),
        "positive_antifield_spectral_sequence_collapsed": contraction[
            "claim_flags"
        ]["FULL_BV_G2_COMPLETE"],
        "nonminimal_doublets_contracted": contraction["claim_flags"][
            "GENERAL_NONMINIMAL_DOUBLETS_CONTRACTED"
        ],
        "canonical_gauge_fixing_invariance": contraction["claim_flags"][
            "LOCAL_CANONICAL_GAUGE_FIXING_INVARIANCE_PROVED"
        ],
        "H14_proof_digest_matches_full_BV_contraction": (
            h14["proof_certificate"]["proof_sha256"]
            == contraction["proof_sha256"]
        ),
        "regulated_positive_antifield_rows_empty": (
            strict_afn["status"] == "COMPLETE_ZERO_POSITIVE_ANTIFIELD_ROWS"
            and strict_afn["positive_antifield_components"] == []
        ),
        "regulated_antifield_edges_content_addressed": (
            {
                row["sha256"] for row in strict_afn["proof_artifacts"]
            }
            == {
                _sha256(DEPENDENCIES["full_BV_contraction"]),
                _sha256(DEPENDENCIES["H14_gauge_fixed"]),
            }
        ),
    }

    standard_calc = standard["coefficient_calculation"]
    factor_a = sum(
        (_fraction(row["signed_a_contribution"])
         for row in standard_calc["constant_curvature_factor_ledger"]),
        Fraction(0),
    )
    closed_a = _fraction(standard_calc["closed_form_a"])
    beta_one = _fraction(
        standard_calc["ricci_flat_sum_beta1_equals_c_minus_a"]
    )
    ricci_flat_c = factor_a + beta_one
    conical_c = _fraction(standard_calc["independent_conical_sphere_c"])

    repository_sum: dict[str, Fraction] = {
        key: Fraction(0) for key in ("C2", "E4", "CdualC", "BoxR")
    }
    for row in repository["coefficient_result"]["factor_contributions"]:
        for key, value in row["coordinates"].items():
            repository_sum[key] += _fraction(value)
    repository_expected = {
        "C2": EXPECTED_VECTOR["ANOM_OMEGA_C2"],
        "E4": EXPECTED_VECTOR["ANOM_OMEGA_E4"],
        "CdualC": EXPECTED_VECTOR["ANOM_OMEGA_C_DUAL_C"],
        "BoxR": EXPECTED_VECTOR["ANOM_OMEGA_BOX_R"],
    }
    coefficient_checks = {
        "type_A_factor_sum": factor_a == Fraction(87, 20),
        "type_A_independent_closed_formula": closed_a == factor_a,
        "type_B_Ricci_flat_reconstruction": ricci_flat_c == Fraction(199, 30),
        "type_B_independent_conical_formula": conical_c == ricci_flat_c,
        "repository_factor_sum": repository_sum == repository_expected,
        "round_S4_Euler_cross_check": (
            _fraction(sphere["coefficient_result"]["E4_coordinate"])
            == EXPECTED_VECTOR["ANOM_OMEGA_E4"]
        ),
        "round_S4_edge_content_addressed": (
            repository["consistency"]["round_S4_cross_check_artifact"][
                "sha256"
            ]
            == _sha256(DEPENDENCIES["round_S4_Euler"])
        ),
        "parity_odd_Ward_zero": repository["consistency"]["parity_status"]
        == "WARD_VERIFIED",
        "scheme_removable_BoxR_zero": repository_sum["BoxR"] == 0,
    }

    strict_vector = {
        key: _fraction(value) for key, value in strict["coefficients"].items()
    }
    strict_checks = {
        "coefficient_vector_matches_two_method_reconstruction": (
            strict_vector == EXPECTED_VECTOR
        ),
        "cohomology_reduction_uses_complete_H14": strict[
            "insertion_decomposition"
        ]["cohomology_reduction_status"]
        == "VERIFIED_AGAINST_COMPLETE_GAUGE_FIXED_H14",
        "antifield_completion_included": strict["insertion_decomposition"][
            "antifield_completion_status"
        ]
        == "COMPLETE_INCLUDING_ZERO",
        "strict_antifield_edge_content_addressed": strict[
            "insertion_decomposition"
        ]["antifield_completion_artifact"]["sha256"]
        == _sha256(DEPENDENCIES["strict_antifield_completion"]),
        "strict_breaking_nontrivial": strict["classification"]["status"]
        == "NONTRIVIAL",
        "strict_QME_obstructed": strict["qme_disposition"]["status"]
        == "OBSTRUCTED_STRICT_FIELD_CONTENT",
    }

    quartet = lift["contractible_quartet"]
    extended_h14 = extended["H14"]
    extended_vector = [
        _fraction(value)
        for value in extended["one_loop_QME"]["strict_breaking_coordinates"]
    ]
    extended_checks = {
        "minimal_cotangent_lift_exact": lift["result_state"]
        == "EXACT_MINIMAL_BV_COTANGENT_LIFT_CERTIFIED_EXTENDED_COHOMOLOGY_OPEN",
        "quartet_homotopy_identity": (
            _matrix_is_identity(quartet["anticommutator"])
            and quartet["status"]
            == "EXACT_CONTRACTIBLE_WEYL_QUARTET_IN_DRESSED_VARIABLES"
        ),
        "extended_H14_boundary_full_rank": (
            _rank(extended_h14["boundary_matrix"]) == 4
            == extended_h14["boundary_rank"]
        ),
        "extended_H14_zero_both_parities": (
            extended_h14["even_quotient_dimension"] == 0
            and extended_h14["odd_quotient_dimension"] == 0
            and extended_h14["pure_Diff_quotient_dimension"] == 0
        ),
        "extended_H04_complete_three_even_one_odd": (
            extended["H04"]["even_quotient_dimension"] == 3
            and extended["H04"]["odd_quotient_dimension"] == 1
        ),
        "extended_counterterm_matches_strict_vector": extended_vector
        == [
            EXPECTED_VECTOR["ANOM_OMEGA_C2"],
            EXPECTED_VECTOR["ANOM_OMEGA_E4"],
            EXPECTED_VECTOR["ANOM_OMEGA_C_DUAL_C"],
            EXPECTED_VECTOR["ANOM_OMEGA_BOX_R"],
        ],
        "extended_local_one_loop_QME_restored": extended["one_loop_QME"][
            "status"
        ]
        == "QME_RESTORED_AT_ONE_LOOP_LOCAL_EUCLIDEAN_TAU_ADIC_EXTENDED_THEORY",
        "extended_edges_content_addressed": (
            extended["dependencies"]["cotangent_lift"]["sha256"]
            == _sha256(DEPENDENCIES["WZ_cotangent_lift"])
            and extended["dependencies"]["nonminimal_contraction"]["sha256"]
            == _sha256(DEPENDENCIES["full_BV_contraction"])
            and extended["dependencies"]["regulated_breaking"]["sha256"]
            == _sha256(DEPENDENCIES["strict_Slavnov"])
        ),
        "strict_and_extended_lifecycles_separate": (
            extended["lifecycle"]["strict_fixed_field_content"] == "OBSTRUCTED"
            and extended["lifecycle"][
                "tau_adic_compensator_extended_local_Euclidean_one_loop"
            ]
            == "QME_RESTORED"
            and extended["lifecycle"]["Lorentzian_QME"] == "OPEN"
        ),
    }

    all_checks = {
        **cohomology_checks,
        **coefficient_checks,
        **strict_checks,
        **extended_checks,
    }
    if not all(all_checks.values()):
        failed = [name for name, passed in all_checks.items() if not passed]
        raise ValueError(f"local anomaly completion audit failed: {failed}")

    return {
        "schema": "quantum-weyl-local-anomaly-antifield-completion-audit-v1",
        "result_id": "LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT",
        "result_state": (
            "FULL_LOCAL_BV_ANOMALY_AND_TWO_METHOD_COEFFICIENT_AUDIT_COMPLETE_"
            "STRICT_QME_OBSTRUCTED_EXTENDED_TAU_ADIC_QME_RESTORED"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "regularity_scope": "REGULAR_BACH_LOCUS",
        "dependency_refs": {
            name: {
                "result_id": value["result_id"],
                "sha256": _sha256(DEPENDENCIES[name]),
            }
            for name, value in values.items()
        },
        "exact_checks": all_checks,
        "full_BV_cohomology": {
            "H04_parity_dimensions": {"even": 2, "odd": 1},
            "H14_parity_dimensions": {"even": 2, "odd": 1},
            "H14_positive_antifield_components": [],
            "type_D_status": "EXACT_WITH_STORED_PRIMITIVE",
        },
        "two_method_coefficients": {
            "type_A": {
                "method_1_constant_curvature_factor_sum": str(factor_a),
                "method_2_closed_higher_spin_formula": str(closed_a),
            },
            "type_B": {
                "method_1_Ricci_flat_reconstruction": str(ricci_flat_c),
                "method_2_conical_sphere_formula": str(conical_c),
            },
            "repository_vector": {
                key: _q(value) for key, value in EXPECTED_VECTOR.items()
            },
        },
        "QME_lifecycles": {
            "strict_fixed_field_content": "OBSTRUCTED_AT_ONE_LOOP_LOCAL_EUCLIDEAN",
            "tau_adic_compensator_extended": (
                "RESTORED_AT_ONE_LOOP_LOCAL_EUCLIDEAN"
            ),
            "Lorentzian": "OPEN",
        },
        "science_forge": {
            "work_item": (
                "sf:program/work/quantum-local-anomaly-antifield-completion"
            ),
            "stop_condition_status": "DONE",
        },
        "claim_flags": {
            "FULL_LOCAL_BV_ANOMALY_COHOMOLOGY_COMPLETE": True,
            "TYPE_A_COEFFICIENT_TWO_METHOD_AGREEMENT": True,
            "TYPE_B_COEFFICIENT_TWO_METHOD_AGREEMENT": True,
            "STRICT_LOCAL_EUCLIDEAN_QME_OBSTRUCTED": True,
            "TAU_ADIC_EXTENDED_LOCAL_EUCLIDEAN_QME_RESTORED": True,
            "STRICT_THEORY_ANOMALY_FREE": False,
            "LORENTZIAN_QME_CERTIFIED": False,
            "HADAMARD_STATE_CERTIFIED_HERE": False,
            "PARTICLE_INTERPRETATION": False,
        },
        "does_not_establish": [
            "global completeness away from the declared regular Bach locus",
            "anomaly freedom of strict pure-Weyl gravity",
            "equivalence of strict and compensator-extended theories",
            "a finite polynomial-in-tau restoration",
            "an all-loop or Lorentzian quantum master equation",
            "renormalized Lorentzian products or a BRST Hadamard state",
            "residual quantum transfer, positivity, or particles",
        ],
        "claim_boundary": (
            "This exact consumer joins the complete local minimal, nonminimal "
            "and canonically gauge-fixed BV quotient on the regular Bach "
            "locus to two independent exact reconstructions of each even "
            "coefficient and to the repository operator/measure Slavnov "
            "insertion. It certifies a strict fixed-field-content one-loop "
            "local Euclidean QME obstruction and, separately, restoration in "
            "the formal tau-adic compensator-extended local algebra. It does "
            "not identify the theories, prove strict anomaly freedom, extend "
            "the theorem to singular Bach strata, or establish an all-loop "
            "or Lorentzian QME, products, Hadamard state, residual transfer, "
            "positivity, particles, scattering, or unitarity."
        ),
    }


def validate(value: dict[str, Any]) -> None:
    if (
        value.get("result_id")
        != "LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT"
        or value.get("science_forge", {}).get("stop_condition_status")
        != "DONE"
        or not all(value.get("exact_checks", {}).values())
        or value.get("QME_lifecycles", {}).get("strict_fixed_field_content")
        != "OBSTRUCTED_AT_ONE_LOOP_LOCAL_EUCLIDEAN"
        or value.get("QME_lifecycles", {}).get("tau_adic_compensator_extended")
        != "RESTORED_AT_ONE_LOOP_LOCAL_EUCLIDEAN"
    ):
        raise ValueError("local anomaly completion result failed")
    flags = value.get("claim_flags", {})
    if (
        flags.get("STRICT_THEORY_ANOMALY_FREE") is not False
        or flags.get("LORENTZIAN_QME_CERTIFIED") is not False
        or flags.get("HADAMARD_STATE_CERTIFIED_HERE") is not False
        or flags.get("PARTICLE_INTERPRETATION") is not False
    ):
        raise ValueError("local anomaly completion over-promoted")
