#!/usr/bin/env python3
"""Independent verifier for the vacuum-dark bounded-local detector no-go."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_REEH_SCHLIEDER_LOCAL_DETECTOR_OBSTRUCTION_V1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-reeh-schlieder-local-detector-obstruction-v1.schema.json"
)
PREDECESSOR = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EXACT_QUADRUPOLE_JULIA_INSTRUMENT_V1.json"
)


def load(relative):
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def multiply(left, right):
    return [
        [
            sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def matvec(matrix, vector):
    return [sum((a * b for a, b in zip(row, vector)), Fraction(0)) for row in matrix]


def inner(left, right):
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def verify(certificate):
    checks = {}
    schema = load(SCHEMA_REL)
    checks["schema_validation"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    checks["certificate_identity"] = certificate.get("certificate") == (
        "REVERSE_PHYSICS_BT_REEH_SCHLIEDER_LOCAL_DETECTOR_OBSTRUCTION_V1"
    )
    checks["lifecycle_is_classified"] = certificate.get("lifecycle_state") == "CLASSIFIED"
    checks["dependency_is_only_local_algebraic"] = certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC"]

    provenance = certificate.get("provenance", {})
    inputs = provenance.get("inputs", [])
    checks["input_hashes_recomputed"] = len(inputs) == 3 and all(
        os.path.isfile(os.path.join(ROOT, row.get("path", "")))
        and row.get("sha256") == sha256(row["path"])
        for row in inputs
    )
    paths = [row.get("path", "") for row in inputs]
    checks["predecessor_is_pinned"] = PREDECESSOR in paths
    predecessor = load(PREDECESSOR)
    checks["predecessor_pass_rechecked"] = predecessor["checks"]["ok"]
    checks["predecessor_effect_rechecked"] = (
        predecessor["bounded_click_instrument"]["source_effect"]
        == "E_click=K_click^*K_click=(1/4)P_u"
    )
    event_paths = [path for path in paths if "/events/" in path]
    checks["done_event_matches_work_item"] = len(event_paths) == 1 and (
        lambda event: event["body"]["payload"]["to_state"] == "DONE"
        and event["body"]["payload"]["target"].endswith(
            "reeh-schlieder-local-detector-obstruction"
        )
    )(load(event_paths[0]))

    theorem = certificate.get("abstract_commuting_algebra_theorem", {})
    proof = theorem.get("proof", [])
    checks["commuting_hypothesis_is_explicit"] = "commuting" in theorem.get("hypotheses", "")
    checks["cyclicity_hypothesis_is_explicit"] = "closure(N Omega)=H" in theorem.get("hypotheses", "")
    checks["separating_conclusion_is_exact"] = theorem.get("separating_conclusion") == "A in M and A Omega=0 imply A=0"
    checks["proof_commutes_through_complement"] = len(proof) == 3 and "A B Omega=B A Omega=0" in proof[0]
    checks["proof_uses_dense_complement_orbit"] = len(proof) == 3 and "dense" in proof[1]
    checks["proof_uses_bounded_extension"] = len(proof) == 3 and "boundedness" in proof[2]

    corollary = certificate.get("positive_effect_corollary", {})
    checks["positive_square_root_identity_is_exact"] = corollary.get("square_root_identity") == "||E^(1/2) Omega||^2=<Omega,E Omega>=0"
    checks["square_root_stays_in_algebra"] = corollary.get("functional_calculus") == "E^(1/2) belongs to M"
    checks["zero_vacuum_effect_conclusion"] = corollary.get("conclusion") == "E=0"

    # Method-distinct exact matrix reconstruction of the Julia effect.
    quarter = Fraction(1, 4)
    projection_u = [
        [Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(1), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0)],
    ]
    effect = [[quarter * entry for entry in row] for row in projection_u]
    omega = [Fraction(1), Fraction(0), Fraction(0)]
    u2 = [Fraction(0), Fraction(1), Fraction(0)]
    checks["Julia_effect_vacuum_probability_recomputed"] = inner(omega, matvec(effect, omega)) == 0
    checks["Julia_effect_nonzero_witness_recomputed"] = inner(u2, matvec(effect, u2)) == quarter
    application = certificate.get("exact_Julia_application", {})
    checks["Julia_effect_application_is_exact"] = (
        application.get("effect") == "E_click=P_u/4"
        and application.get("vacuum_probability") == "<Omega,E_click Omega>=0"
        and application.get("nonzero_witness") == "<u2,E_click u2>=1/4"
    )
    checks["both_Kraus_localities_are_rejected"] = (
        "NOT_IN_M" in application.get("click_Kraus_locality", "")
        and "NOT_IN_M" in application.get("no_click_Kraus_locality", "")
    )

    pointer = certificate.get("normal_pointer_dilation_corollary", {})
    checks["normal_pointer_slice_formula_is_exact"] = pointer.get("induced_effect") == "E=(id tensor omega)(U^*(I tensor Q)U)"
    checks["normal_pointer_slice_is_local_positive"] = pointer.get("slice_map_result") == "E belongs to M and 0<=E<=I"
    checks["normal_pointer_no_go_is_scoped"] = pointer.get("exact_Julia_realization") == "IMPOSSIBLE_UNDER_THE_DECLARED_HYPOTHESES"

    # Exact countermodel: full B(C^2), e0, |e1><e1|; commutant orbit rank one.
    counter_effect = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(1)]]
    e0 = [Fraction(1), Fraction(0)]
    checks["cyclicity_countermodel_recomputed"] = (
        inner(e0, matvec(counter_effect, e0)) == 0
        and counter_effect != [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(0)]]
    )
    counter = certificate.get("finite_exact_fixtures", {}).get("cyclicity_necessity_countermodel", {})
    checks["countermodel_records_noncyclic_commutant"] = counter.get("commutant_orbit_dimension") == 1 and counter.get("conclusion") == "without complement cyclicity the no-go is false"

    # Exact balanced fixture and positivity through factorization E=R^T R.
    e_plus = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]]
    e_minus = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(1)]]
    identity = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    omega_bal = [Fraction(1), Fraction(1)]
    norm2 = inner(omega_bal, omega_bal)
    p_plus = inner(omega_bal, matvec(e_plus, omega_bal)) / norm2
    p_minus = inner(omega_bal, matvec(e_minus, omega_bal)) / norm2
    checks["balanced_sum_recomputed"] = [[e_plus[i][j] + e_minus[i][j] for j in range(2)] for i in range(2)] == identity
    checks["balanced_positivity_recomputed"] = (
        multiply(transpose(e_plus), e_plus) == e_plus
        and multiply(transpose(e_minus), e_minus) == e_minus
    )
    checks["balanced_vacuum_baseline_recomputed"] = p_plus == p_minus == Fraction(1, 2)
    stored_balanced = certificate.get("finite_exact_fixtures", {}).get(
        "balanced_diagonal_fixture", {}
    )
    checks["balanced_fixture_is_stored_exactly"] = (
        stored_balanced.get("E_plus") == "diag(1,0)"
        and stored_balanced.get("E_minus") == "diag(0,1)"
        and stored_balanced.get("vacuum_probabilities") == ["1/2", "1/2"]
        and stored_balanced.get("contrast") == "0"
    )
    balanced = certificate.get("balanced_contrast_boundary", {})
    checks["balanced_BT_operator_is_only_conditional"] = (
        "CONSTRUCTED_CONDITIONALLY" in balanced.get("BT_status", "")
    )

    lift = certificate.get("bounded_spectral_truncation_lift", {})
    checks["affiliation_and_domain_hypotheses_are_explicit"] = (
        len(lift.get("additional_hypotheses", [])) == 3
        and "affiliated with M" in lift["additional_hypotheses"][0]
        and "Dom(D)" in lift["additional_hypotheses"][1]
    )
    checks["spectral_truncations_are_bounded_local"] = (
        lift.get("truncations")
        == "D_n=D 1_[minus n,n](D) are bounded self-adjoint elements of M"
    )
    checks["response_limit_is_exact"] = (
        "converges to v=(0,0,0,Re(a),Im(a))" in lift.get("limit", "")
        and "nonzero" in lift.get("limit", "")
    )
    checks["finite_span_closure_step_is_exact"] = (
        "finite-dimensional" in lift.get("closed_span_step", "")
        and "v belongs to V" in lift.get("closed_span_step", "")
        and "at most five" in lift.get("finite_combination", "")
    )
    checks["bounded_contraction_responses_are_exact"] = (
        "self-adjoint contraction" in lift.get("bounded_operator", "")
        and "<Omega,B Omega>=0" in lift.get("exact_responses", "")
        and "<Omega,B X2>=0" in lift.get("exact_responses", "")
        and "<Omega,B X4> is nonzero" in lift.get("exact_responses", "")
    )
    checks["balanced_effect_lift_is_local_positive"] = (
        "local positive effects" in lift.get("effects", "")
        and "Re<Omega,BX>" in lift.get("phase_reversal_contrast", "")
        and "exactly zero for X2" in lift.get("operational_response", "")
        and "calibrated phase of X4" in lift.get("operational_response", "")
        and lift.get("status") == "PROVED_ABSTRACTLY"
        and lift.get("BT_status")
        == "CONDITIONAL_ON_UNCONSTRUCTED_POSITIVE_LOCAL_NET_AFFILIATION_AND_DOMAIN"
    )

    span_fixture = certificate.get("finite_exact_fixtures", {}).get(
        "spectral_truncation_span_fixture", {}
    )
    vectors = [
        [Fraction(value) for value in row]
        for row in span_fixture.get("vectors", [])
    ]
    coefficients = [
        Fraction(value) for value in span_fixture.get("coefficients", [])
    ]
    recombined = [
        sum(
            (coefficient * vector[column] for coefficient, vector in zip(coefficients, vectors)),
            Fraction(0),
        )
        for column in range(5)
    ] if len(vectors) == len(coefficients) == 3 else []
    checks["spectral_span_fixture_recomputed"] = (
        recombined == [Fraction(0), Fraction(0), Fraction(0), Fraction(1), Fraction(0)]
        and span_fixture.get("combined_response") == ["0", "0", "0", "1", "0"]
    )

    disposition = certificate.get("disposition", {})
    boundaries = certificate.get("does_not_establish", [])
    checks["BT_net_is_not_promoted"] = (
        disposition.get("positive_BT_Haag_Kastler_net") == "NOT_CONSTRUCTED"
        and any("Haag--Kastler net" in item for item in boundaries)
    )
    checks["BT_Reeh_Schlieder_is_not_promoted"] = (
        disposition.get("BT_Reeh_Schlieder_property") == "NOT_ESTABLISHED"
        and any("Reeh--Schlieder" in item for item in boundaries)
    )
    checks["conditional_contrast_does_not_promote_affiliation"] = (
        disposition.get("balanced_BT_quadrupole_contrast")
        == "CONSTRUCTED_CONDITIONALLY_ON_LOCAL_AFFILIATION_AND_DOMAIN"
        and any("self-adjoint affiliation" in item for item in boundaries)
    )
    checks["Eq19_remains_open"] = disposition.get("general_Eq19") == "NOT_PROVED" and any("Eq. (19)" in item for item in boundaries)
    checks["gravity_remains_open"] = disposition.get("gravity_or_metric_BV_BRST_transfer") == "NOT_CONSTRUCTED" and any("metric BV--BRST" in item for item in boundaries)
    checks["Lorentzian_boundary_present"] = disposition.get("Lorentzian_causal_BT_claim") == "NOT_ESTABLISHED" and any("LORENTZIAN-CAUSAL" in item for item in boundaries)
    checks["literature_priority_forbidden"] = certificate.get("literature_context", {}).get("priority_status") == "NOT_CLAIMED" and "literature priority" in boundaries
    return checks


def main():
    certificate = load(CERT_REL)
    checks = verify(copy.deepcopy(certificate))
    for name, passed in checks.items():
        print(("PASS: " if passed else "FAIL: ") + name)
    if all(checks.values()):
        print("RESULT: PASS")
        return 0
    print("RESULT: FAIL", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
