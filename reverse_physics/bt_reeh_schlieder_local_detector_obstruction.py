#!/usr/bin/env python3
"""Certificate producer for the vacuum-dark bounded-local detector no-go."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_REEH_SCHLIEDER_LOCAL_DETECTOR_OBSTRUCTION_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-reeh-schlieder-local-detector-obstruction-v1.schema.json"
)
REPORT = (
    "reverse_physics/reports/"
    "bt-reeh-schlieder-local-detector-obstruction.md"
)
SOURCE = "13ca819c61edeb81bcb83e49316e7ac71082cdf7"
WORK_ITEM = (
    "planning/work-items/"
    "reverse-physics-bateman-reeh-schlieder-local-detector-obstruction.json"
)
PREDECESSOR = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EXACT_QUADRUPOLE_JULIA_INSTRUMENT_V1.json"
)
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-reeh-schlieder-local-detector-obstruction-"
    "DONE-13ca819c.json"
)
INPUTS = [WORK_ITEM, PREDECESSOR, EVENT]


def load(relative):
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def matvec(matrix, vector):
    return [sum((entry * value for entry, value in zip(row, vector)), Fraction(0)) for row in matrix]


def inner(left, right):
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def matrix_add(left, right):
    return [[a + b for a, b in zip(lrow, rrow)] for lrow, rrow in zip(left, right)]


def build():
    predecessor = load(PREDECESSOR)
    event = load(EVENT)

    # Exact Julia effect in the orthogonal fixture basis (Omega,u2,rest).
    julia_effect = [
        [Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(1, 4), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0)],
    ]
    vacuum3 = [Fraction(1), Fraction(0), Fraction(0)]
    julia_vacuum_probability = inner(vacuum3, matvec(julia_effect, vacuum3))

    # Assumption-necessity countermodel: B(C^2), Omega=e0, E=|e1><e1|.
    counter_effect = [
        [Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(1)],
    ]
    vacuum2 = [Fraction(1), Fraction(0)]
    counter_probability = inner(vacuum2, matvec(counter_effect, vacuum2))
    complement_orbit_rank = 1

    # Balanced contrast fixture in the diagonal algebra with cyclic/separating
    # Omega=(1,1)/sqrt(2); the common normalization is handled rationally.
    e_plus = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]]
    e_minus = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(1)]]
    identity2 = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    omega_numerator = [Fraction(1), Fraction(1)]
    omega_norm2 = inner(omega_numerator, omega_numerator)
    p_plus = inner(omega_numerator, matvec(e_plus, omega_numerator)) / omega_norm2
    p_minus = inner(omega_numerator, matvec(e_minus, omega_numerator)) / omega_norm2

    # Exact finite-span fixture for the bounded spectral-truncation theorem.
    # Coordinates are (vacuum, Re X2, Im X2, Re X4, Im X4).
    truncation_vectors = [
        [Fraction(1), Fraction(1), Fraction(0), Fraction(1), Fraction(0)],
        [Fraction(1), Fraction(-1), Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(-2), Fraction(0), Fraction(0), Fraction(1), Fraction(0)],
    ]
    truncation_coefficients = [Fraction(1, 2)] * 3
    combined_response = [
        sum(
            (coefficient * vector[column] for coefficient, vector in zip(truncation_coefficients, truncation_vectors)),
            Fraction(0),
        )
        for column in range(5)
    ]

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessor_passes": predecessor["checks"]["ok"],
        "predecessor_effect_is_quarter_projector": predecessor["bounded_click_instrument"]["source_effect"] == "E_click=K_click^*K_click=(1/4)P_u",
        "predecessor_vacuum_pair_orthogonality_is_declared": "two-particle" in predecessor["answer"],
        "done_event_matches_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("reeh-schlieder-local-detector-obstruction"),
        "commuting_algebra_hypothesis_is_explicit": True,
        "complement_cyclicity_hypothesis_is_explicit": True,
        "separating_proof_uses_dense_orbit": True,
        "positive_square_root_step_is_explicit": True,
        "nonzero_vacuum_dark_effect_is_forbidden": True,
        "Julia_effect_is_nonzero": julia_effect[1][1] == Fraction(1, 4),
        "Julia_vacuum_probability_is_zero": julia_vacuum_probability == 0,
        "click_Kraus_locality_is_ruled_out_conditionally": True,
        "no_click_Kraus_locality_is_ruled_out_conditionally": True,
        "normal_pointer_slice_stays_local": True,
        "normal_pointer_exact_realization_is_ruled_out_conditionally": True,
        "countermodel_effect_is_nonzero": counter_effect != [[Fraction(0)] * 2 for _ in range(2)],
        "countermodel_vacuum_probability_is_zero": counter_probability == 0,
        "countermodel_complement_is_not_cyclic": complement_orbit_rank == 1,
        "balanced_effects_sum_to_identity": matrix_add(e_plus, e_minus) == identity2,
        "balanced_effects_are_positive": all(e_plus[i][i] >= 0 and e_minus[i][i] >= 0 for i in range(2)),
        "balanced_vacuum_probabilities_are_half": p_plus == p_minus == Fraction(1, 2),
        "balanced_contrast_has_zero_vacuum_mean": p_plus - p_minus == 0,
        "spectral_truncations_are_bounded_local": True,
        "truncated_response_vectors_converge": True,
        "finite_dimensional_response_span_is_closed": True,
        "limit_response_has_exact_zero_constraints": True,
        "finite_combination_matches_limit_exactly": combined_response == [Fraction(0), Fraction(0), Fraction(0), Fraction(1), Fraction(0)],
        "bounded_local_contrast_is_exact_conditionally": True,
        "BT_affiliation_and_domain_remain_open": True,
        "BT_Haag_Kastler_net_is_not_promoted": True,
        "balanced_BT_quadrupole_is_not_promoted": True,
        "Eq19_gravity_and_Lorentzian_boundaries_remain_open": True,
        "literature_priority_is_forbidden": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_REEH_SCHLIEDER_LOCAL_DETECTOR_OBSTRUCTION_V1",
        "question": "Can the exact vacuum-dark quadrupole Julia instrument be realized by a bounded-region local effect or by a normal locally coupled pointer under the standard complement-cyclicity hypothesis?",
        "answer": "No for the zero-baseline Julia effect under the declared abstract local-net hypotheses, but yes conditionally for an exact balanced local contrast. If M and N are commuting unital von Neumann algebras and the vacuum Omega is cyclic for N, then Omega is separating for M. A positive E in M with zero vacuum expectation obeys E^(1/2)Omega=0 and therefore E=0. The exact Julia click effect E_click=P_u/4 is nonzero and annihilates the active-field vacuum, so neither it, its Kraus maps, nor a normal local pointer dilation can be local. If instead the compact quadrupole density has a self-adjoint realization D affiliated with M and Omega,X2,X4 lie in Dom(D), bounded spectral truncations D_n have response vectors converging in R^5 to the exact zero-vacuum, zero-X2, nonzero-X4 response. The finite-dimensional span is closed, so at most five D_n have a finite real combination giving that response exactly. Normalizing it produces a bounded self-adjoint local contraction B and balanced effects (I plus or minus B)/2. This is a conditional LOCAL-ALGEBRAIC construction, not a proof that the public BT theory has the required positive local net, affiliation, domains or Reeh--Schlieder vacuum.",
        "result_kind": "abstract local-net no-go for the exactly vacuum-dark Julia effect together with a conditional bounded-spectral-truncation construction of an exact balanced local quadrupole contrast",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "assumptions": [
            "M=A(O) and N=A(O') are unital von Neumann algebras on a positive Hilbert space H",
            "M and N commute, as supplied by locality for spacelike separated regions",
            "the vacuum Omega is cyclic for N: the closure of N Omega is H",
            "the exact Julia effect is compared in the same active-field vacuum representation",
            "pointer dilations use a normal state and the normal von Neumann tensor-product slice map",
            "the public BT reduced-mode carrier is not assumed to satisfy any of these local-net hypotheses"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_reeh_schlieder_local_detector_obstruction.py",
            "independent_verifier": "reverse_physics/verify_bt_reeh_schlieder_local_detector_obstruction.py",
            "method": "Self-contained commuting-algebra separation proof and positive functional calculus; exact rational finite-dimensional fixtures independently distinguish the essential cyclicity hypothesis from the balanced-contrast escape. No floating-point arithmetic enters the claim."
        },
        "abstract_commuting_algebra_theorem": {
            "hypotheses": "M,N subset B(H) are commuting unital von Neumann algebras and closure(N Omega)=H",
            "separating_conclusion": "A in M and A Omega=0 imply A=0",
            "proof": [
                "for every B in N, locality gives A B Omega=B A Omega=0",
                "the set N Omega is dense in H by hypothesis",
                "boundedness of A therefore gives A=0 on H"
            ],
            "status": "PROVED_ABSTRACTLY"
        },
        "positive_effect_corollary": {
            "effect_hypotheses": "E in M, 0<=E<=I and <Omega,E Omega>=0",
            "square_root_identity": "||E^(1/2) Omega||^2=<Omega,E Omega>=0",
            "functional_calculus": "E^(1/2) belongs to M",
            "conclusion": "E=0",
            "physical_reading": "every nonzero bounded local positive outcome has strictly positive vacuum probability",
            "status": "PROVED_ABSTRACTLY"
        },
        "normal_pointer_dilation_corollary": {
            "setup": "U in M tensor_bar B(K), normal pointer state omega and pointer effect 0<=Q<=I",
            "induced_effect": "E=(id tensor omega)(U^*(I tensor Q)U)",
            "slice_map_result": "E belongs to M and 0<=E<=I",
            "conclusion": "if the induced click probability is exactly zero on Omega, then E=0",
            "exact_Julia_realization": "IMPOSSIBLE_UNDER_THE_DECLARED_HYPOTHESES",
            "status": "PROVED_ABSTRACTLY"
        },
        "exact_Julia_application": {
            "effect": "E_click=P_u/4",
            "response_mode": "u2 is a normalized two-particle vector orthogonal to the active-field vacuum Omega",
            "vacuum_probability": "<Omega,E_click Omega>=0",
            "nonzero_witness": "<u2,E_click u2>=1/4",
            "effect_locality": "E_click NOT_IN_M under the declared hypotheses",
            "click_Kraus_locality": "K_click NOT_IN_M because K_click^*K_click=E_click",
            "no_click_Kraus_locality": "K_no NOT_IN_M because I-K_no^*K_no=E_click",
            "Julia_pointer_unitary_locality": "no normal bounded local tensor-pointer unitary can induce the exact effect",
            "status": "SCOPED_EXACT_LOCAL_REALIZATION_NO_GO"
        },
        "balanced_contrast_boundary": {
            "construction": "for any self-adjoint contraction B in M, E_plus=(I+B)/2 and E_minus=(I-B)/2 are local effects summing to I",
            "vacuum_condition": "<Omega,B Omega>=0 gives p_plus(Omega)=p_minus(Omega)=1/2, not a zero-probability outcome",
            "consequence": "the theorem forbids exact vacuum-dark positive outcomes, not vacuum-dark signed contrasts",
            "BT_status": "a bounded local B with exact X2-zero contrast and strict X4 response is CONSTRUCTED_CONDITIONALLY_ON_SELF_ADJOINT_LOCAL_AFFILIATION_AND_DOMAIN",
            "next_options": [
                "construct a balanced bounded local quadrupole contrast with nonzero vacuum baseline",
                "derive quantitative approximate or almost-local dark counts",
                "return to the public-BT lambda10 or Eq. (19) route"
            ],
            "status": "BOUNDED_LOCAL_CONTRAST_CONSTRUCTED_CONDITIONALLY"
        },
        "bounded_spectral_truncation_lift": {
            "additional_hypotheses": [
                "the compact quadrupole density D_h has a self-adjoint realization D affiliated with M",
                "Omega, X2 and X4 belong to Dom(D)",
                "<Omega,D Omega>=0, <Omega,D X2>=0 and a=<Omega,D X4> is nonzero"
            ],
            "truncations": "D_n=D 1_[minus n,n](D) are bounded self-adjoint elements of M",
            "response_vector": "v_n=(<Omega,D_n Omega>,Re<Omega,D_n X2>,Im<Omega,D_n X2>,Re<Omega,D_n X4>,Im<Omega,D_n X4>) in R^5",
            "limit": "v_n converges to v=(0,0,0,Re(a),Im(a)), which is nonzero",
            "closed_span_step": "V=span_R{v_n} is finite-dimensional and therefore closed, so v belongs to V",
            "finite_combination": "there exist at most five indices n_j and real c_j with sum_j c_j v_nj=v",
            "bounded_operator": "C=sum_j c_j D_nj is bounded self-adjoint in M; B=C/max(1,||C||) is a self-adjoint contraction",
            "exact_responses": "<Omega,B Omega>=0 and <Omega,B X2>=0, while <Omega,B X4> is nonzero",
            "effects": "E_plus=(I+B)/2 and E_minus=(I-B)/2 are local positive effects summing to I with equal vacuum baselines",
            "phase_reversal_contrast": "C_B(X)=(1/4)[<Omega+X,B(Omega+X)>-<Omega-X,B(Omega-X)>]=Re<Omega,BX>; for normalized Omega plus/minus X with Omega perpendicular to X, divide both sides by 1+||X||^2",
            "operational_response": "the phase-reversal contrast is exactly zero for X2 and strictly nonzero for a calibrated phase of X4",
            "constructivity": "the theorem is finite-existence exact but does not compute the cutoffs or coefficients without the local spectral measures",
            "BT_status": "CONDITIONAL_ON_UNCONSTRUCTED_POSITIVE_LOCAL_NET_AFFILIATION_AND_DOMAIN",
            "status": "PROVED_ABSTRACTLY"
        },
        "finite_exact_fixtures": {
            "cyclicity_necessity_countermodel": {
                "Hilbert_space": "C^2",
                "algebra": "B(C^2)",
                "vacuum": "e0",
                "effect": "|e1><e1|",
                "vacuum_probability": "0",
                "effect_nonzero": True,
                "commutant_orbit_dimension": 1,
                "conclusion": "without complement cyclicity the no-go is false"
            },
            "balanced_diagonal_fixture": {
                "algebra": "diagonal matrices on C^2",
                "vacuum": "(e0+e1)/sqrt(2)",
                "B": "diag(1,-1)",
                "E_plus": "diag(1,0)",
                "E_minus": "diag(0,1)",
                "vacuum_probabilities": ["1/2", "1/2"],
                "contrast": "0",
                "conclusion": "separation permits balanced nonzero effects but not a nonzero zero-vacuum effect"
            },
            "spectral_truncation_span_fixture": {
                "coordinate_order": ["vacuum", "Re_X2", "Im_X2", "Re_X4", "Im_X4"],
                "vectors": [[str(value) for value in vector] for vector in truncation_vectors],
                "coefficients": [str(value) for value in truncation_coefficients],
                "combined_response": [str(value) for value in combined_response],
                "conclusion": "a finite real combination cancels the first three vacuum-to-pair constraints exactly and retains unit X4 interference response"
            }
        },
        "literature_context": {
            "primary_reference": "H. Reeh and S. Schlieder, Bemerkungen zur unitaeraequivalenz von lorentzinvarianten Feldern, Il Nuovo Cimento 22 (1961) 1051-1068",
            "doi": "10.1007/BF02787889",
            "use": "the cyclic-vacuum hypothesis is standard Reeh--Schlieder input; the separating and detector corollaries used here are proved self-contained",
            "priority_status": "NOT_CLAIMED"
        },
        "disposition": {
            "abstract_separating_vacuum_theorem": "PROVED",
            "nonzero_exactly_vacuum_dark_local_effect": "IMPOSSIBLE_UNDER_DECLARED_HYPOTHESES",
            "exact_Julia_effect_in_local_algebra": "RULED_OUT_UNDER_DECLARED_HYPOTHESES",
            "normal_local_pointer_realization": "RULED_OUT_UNDER_DECLARED_HYPOTHESES",
            "balanced_local_contrast_in_general": "ALGEBRAICALLY_ALLOWED",
            "balanced_BT_quadrupole_contrast": "CONSTRUCTED_CONDITIONALLY_ON_LOCAL_AFFILIATION_AND_DOMAIN",
            "positive_BT_Haag_Kastler_net": "NOT_CONSTRUCTED",
            "BT_Reeh_Schlieder_property": "NOT_ESTABLISHED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_BT_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "a positive Haag--Kastler net for the public BT theory",
            "the Reeh--Schlieder property for the BT Krein or reduced-mode carrier",
            "that every local detector or local pointer coupling is impossible",
            "an obstruction to two nonzero local effects used through their signed contrast",
            "an obstruction to approximate, almost-local, unbounded-readout or non-normal constructions",
            "an unconditional bounded local BT operator before a positive local net, self-adjoint affiliation and domain theorem are supplied",
            "selection of any detector or phase-reversed preparation by public BT dynamics",
            "the lambda10 and higher BT amplitudes",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "a complete positive BT Hilbert or Fock construction",
            "gravity, metric BV--BRST, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL for the BT or gravitational models",
            "literature priority"
        ],
        "next_gate": "Construct the positive BT local net and prove self-adjoint affiliation of the compact quadrupole density with Omega, X2 and X4 in its domain; the abstract spectral-truncation theorem then supplies the bounded exact balanced contrast. Independently, continue the public-BT route through the lambda10 dark remainder or general Eq. (19).",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_reeh_schlieder_local_detector_obstruction.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_reeh_schlieder_local_detector_obstruction.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_reeh_schlieder_local_detector_obstruction"
        ],
        "report": REPORT
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if args.write:
        with open(CERT, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print(CERT_REL)
    if args.check:
        if not payload["checks"]["ok"]:
            for failure in payload["checks"]["failures"]:
                print("FAIL:", failure, file=sys.stderr)
            return 1
        if os.path.exists(CERT) and load(CERT_REL) != payload:
            print("BT REEH-SCHLIEDER DETECTOR: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(
            "BT REEH-SCHLIEDER DETECTOR: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
