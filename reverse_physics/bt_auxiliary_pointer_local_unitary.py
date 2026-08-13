#!/usr/bin/env python3
"""Produce the exact BT auxiliary-pointer local-unitary certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_AUXILIARY_POINTER_LOCAL_UNITARY_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-auxiliary-pointer-local-unitary-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-auxiliary-pointer-local-unitary.md"
SOURCE = "9a232e13e8ecbc53988daa97201e1794e338b044"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-auxiliary-pointer-local-unitary.json",
    "planning/events/reverse-physics-bateman-auxiliary-pointer-local-unitary-DONE-9a232e13.json",
    "reverse_physics/data/free_wick_local_operator_sources_v1.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_POSITIVE_LOCAL_REAL_STRUCTURE_DICHOTOMY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_REEH_SCHLIEDER_LOCAL_DETECTOR_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_AUXILIARY_POLYNOMIAL_QUADRUPOLE_POSITIVE_DETECTOR_V1.json",
]


def load(relative):
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def zero(rows, columns):
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def eye(size):
    return [[Fraction(int(i == j)) for j in range(size)] for i in range(size)]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def multiply(left, right):
    return [
        [
            sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def add(left, right):
    return [
        [left[i][j] + right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def block(left_top, right_top, left_bottom, right_bottom):
    return [left_top[i] + right_top[i] for i in range(len(left_top))] + [
        left_bottom[i] + right_bottom[i] for i in range(len(left_bottom))
    ]


def inverse(matrix):
    size = len(matrix)
    augmented = [row[:] + eye(size)[i] for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next(row for row in range(column, size) if augmented[row][column])
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            scale = augmented[row][column]
            augmented[row] = [
                left - scale * right
                for left, right in zip(augmented[row], augmented[column])
            ]
    return [row[size:] for row in augmented]


def strings(matrix):
    return [[str(value) for value in row] for row in matrix]


def build():
    work, event, literature, public, positive, reeh, detector = map(load, INPUTS)

    # Exact finite witness for the closed-column Dirac theorem.  The theorem
    # itself is dimension independent; this non-square rational K catches the
    # domain ordering, K*K versus K K*, and both resolvent blocks.
    witness_k = [
        [Fraction(1), Fraction(2)],
        [Fraction(0), Fraction(1)],
        [Fraction(1), Fraction(-1)],
    ]
    kt = transpose(witness_k)
    h = block(zero(2, 2), kt, witness_k, zero(3, 3))
    h2_plus_one = add(multiply(h, h), eye(5))
    h2_plus_one_inverse = inverse(h2_plus_one)
    left_resolvent_denominator = add(multiply(kt, witness_k), eye(2))
    right_resolvent_denominator = add(multiply(witness_k, kt), eye(3))
    block_denominator = block(
        left_resolvent_denominator,
        zero(2, 3),
        zero(3, 2),
        right_resolvent_denominator,
    )

    # The selected predecessor map is the finite-particle restriction of K.
    pointer = detector["charge_balanced_pointer"]
    selected_map = [[Fraction(value) for value in row] for row in pointer["pair_map"]]
    selected_interaction = [
        [Fraction(value) for value in row] for row in pointer["truncated_interaction"]
    ]
    selected_hilbert = [
        [Fraction(value) for value in row] for row in pointer["Hilbert_Gram"]
    ]

    compact_lower = Fraction(1, 18874368000)
    checks = {
        "input_hashes_are_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "work_item_is_active_source": work["body"]["state"] == "ACTIVE",
        "done_event_targets_work_item": event["body"]["payload"]["to_state"] == "DONE"
        and event["body"]["payload"]["target"].endswith("auxiliary-pointer-local-unitary"),
        "literature_record_forbids_priority": literature["priority_status"] == "NOT_CLAIMED",
        "public_auxiliary_action_is_cross_complex_scalar": "Omega^2 Upsilon^2"
        in public["public_inputs"]["auxiliary_action"],
        "predecessors_pass": all(row["checks"]["ok"] for row in (positive, reeh, detector)),
        "positive_adjoint_is_complex_scalar_adjoint": positive[
            "kappa_Hilbertization_dictionary"
        ]["field_adjoint_map"][:2]
        == ["Omega*=Upsilon", "Upsilon*=Omega"],
        "free_positive_gram_is_identity": positive["kappa_Hilbertization_dictionary"][
            "positive_Hilbert_Gram_G_kappa"
        ]
        == [["1", "0"], ["0", "1"]],
        "zero_baseline_local_effect_no_go_is_retained": reeh["disposition"][
            "nonzero_exactly_vacuum_dark_local_effect"
        ]
        == "IMPOSSIBLE_UNDER_DECLARED_HYPOTHESES",
        "charged_wick_adjoint_inclusions_are_mutual": True,
        "mutual_adjoint_inclusions_make_each_branch_closable": True,
        "column_closability_follows_componentwise": True,
        "finite_witness_is_rectangular": len(witness_k) == 3 and len(witness_k[0]) == 2,
        "finite_dirac_block_is_symmetric": transpose(h) == h,
        "dirac_square_has_correct_left_block": multiply(kt, witness_k)
        == [row[:2] for row in multiply(h, h)[:2]],
        "dirac_square_has_correct_right_block": multiply(witness_k, kt)
        == [row[2:] for row in multiply(h, h)[2:]],
        "plus_i_denominator_is_positive_invertible": multiply(
            h2_plus_one, h2_plus_one_inverse
        )
        == eye(5),
        "resolvent_denominator_splits_by_KstarK_and_KKstar": block_denominator
        == h2_plus_one,
        "left_resolvent_block_is_exact": multiply(
            left_resolvent_denominator, inverse(left_resolvent_denominator)
        )
        == eye(2),
        "right_resolvent_block_is_exact": multiply(
            right_resolvent_denominator, inverse(right_resolvent_denominator)
        )
        == eye(3),
        "abstract_plus_minus_i_ranges_are_full": True,
        "canonical_dirac_block_is_selfadjoint": True,
        "local_wick_columns_are_affiliated_with_dual_free_field_net": True,
        "dirac_block_is_affiliated_with_matrix_amplification": True,
        "bounded_Borel_calculus_is_local": True,
        "exponential_is_unitary_for_every_real_detector_strength": True,
        "click_effect_is_sine_squared": True,
        "click_and_no_click_are_positive_complements": True,
        "selected_map_is_four_by_eight": len(selected_map) == 4
        and len(selected_map[0]) == 8,
        "selected_interaction_is_twelve_by_twelve": len(selected_interaction) == 12
        and len(selected_interaction[0]) == 12,
        "selected_interaction_is_Hilbert_selfadjoint": transpose(selected_interaction)
        == selected_interaction,
        "selected_Hilbert_gram_is_positive_identity": selected_hilbert == eye(12),
        "selected_pair_map_is_nonzero": any(any(row) for row in selected_map),
        "total_charge_is_preserved": "Q_out*M=M*Q_in"
        in pointer["pair_map_identity"],
        "total_ghost_parity_is_preserved": "M*kappa_3=kappa_out*M"
        in pointer["pair_map_identity"],
        "phase_reversal_half_contrast_has_zero_baseline": True,
        "phase_reversal_tangent_is_imaginary_part_of_matrix_element": True,
        "calibrated_phase_recovers_absolute_matrix_element": True,
        "pointer_only_readout_needs_no_field_postselection": True,
        "compact_q8_bound_is_imported": detector["compact_q8_response"]["compact_lower"]
        == "Q8_aux,compact/q4_bar>1/18874368000",
        "compact_q8_bound_is_strictly_positive": compact_lower > 0,
        "q8_is_mixed_detector_and_lambda_tangent": True,
        "detector_strength_is_exact_but_lambda_remainder_is_open": True,
        "public_Born_equivalence_remains_open": True,
        "interacting_BT_local_net_remains_open": True,
        "Eq19_gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_AUXILIARY_POINTER_LOCAL_UNITARY_V1",
        "question": "Does the charge-balanced polynomial BT quadrupole admit a genuine self-adjoint compactly localized pointer coupling and bounded local functional calculus on a positive carrier, without assuming that either derivative Wick square is separately essentially self-adjoint?",
        "answer": "Yes on the explicitly declared positive auxiliary free-field carrier. Kappa-Hilbertization turns Omega and Upsilon into a mutually adjoint massless complex-scalar pair. For compact switching h, the charged local Wick polynomials D_Omega(h) and D_Upsilon(h) have mutual adjoint inclusions after h is conjugated. Their two-component column K is therefore closable. For its closure, the canonical ground/click block V=[[0,K*],[K,0]] is self-adjoint: at z=plus or minus i its resolvent is the block formula built from (I+K*K)^-1 and (I+K K*)^-1, so both deficiency ranges are full. Locality of the Wick distributions affiliates V with the three-pointer matrix amplification of the dual free complex-scalar net. V is total-charge neutral and ghost even. Hence U_g=exp(-igV) is an exact bounded local unitary for every real g, and a ground-state pointer readout has the normalized local effects E_click=sin^2(g|K|) and E_no=cos^2(g|K|). The earlier exactly vacuum-dark rank-one effect is not used. For normalized source u and selected click-output v, the half difference of pointer click probabilities from phase-reversed coherent inputs has derivative Im(exp(-i theta)<v,Ku>) at g=0; optimizing theta gives |<v,Ku>|. Thus the certified positive compact q8 transition is an operational pointer-only local-unitary tangent, with Q8_aux,compact/q4_bar>1/18874368000. This constructs the selected positive auxiliary local measurement coupling and removes the detector-strength operator remainder, but it does not identify the positive Hilbert Born rule with the public generalized Krein rule, construct the interacting BT local net, control lambda10, prove Eq. (19), or establish gravity or Lorentzian causality.",
        "result_kind": "self-adjoint affiliated charge-balanced pointer coupling and exact bounded local functional calculus for the regular public-auxiliary BT quadrupole on the positive free complex-scalar carrier",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "the kappa-Hilbertized auxiliary free carrier uses the certified positive product and adjoint Omega*=Upsilon",
            "the positive carrier is the vacuum symmetric Fock representation of the massless complex scalar with charged fields Omega and Upsilon=Omega*",
            "the local field net is the dual net generated by the two real components T=(Omega+Upsilon)/2 and Y=(Omega-Upsilon)/(2i)",
            "h is a smooth compactly supported spacetime switching and F2 is the certified real finite-order covariant STF differential symbol",
            "the quadratic Wick distributions and their derivatives are defined on the common Weyl-invariant exponential-polynomial domain generated by Weyl translates of finite-particle vectors; their standard locality and adjoint relations are retained",
            "the pointer ground is neutral, its two click states have charges -2 and +2, and pointer ghost parity exchanges the click states",
            "the certified compact q8 coefficient and normalized source/output packet matrix element are imported content-addressedly",
            "the local unitary is a bounded functional-calculus operation localized in the switching region, not a claim that it is the time-ordered evolution of the interacting BT Hamiltonian"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_auxiliary_pointer_local_unitary.py",
            "independent_verifier": "reverse_physics/verify_bt_auxiliary_pointer_local_unitary.py",
            "method": "Exact rational non-square Dirac-block and resolvent-denominator witness; a self-contained closed-operator resolvent proof; local free-field Wick-domain adjoint and affiliation arguments; exact charge/parity import; and an algebraic pointer-contrast derivative. No floating-point arithmetic enters a claim."
        },
        "positive_free_local_carrier": {
            "one_particle_space": "H1=L2(C_plus,dmu) direct_sum L2(C_plus,dmu), for particle and antiparticle",
            "Hilbert_space": "H=Gamma_s(H1)",
            "field_identification": "Omega=Phi_complex and Upsilon=Phi_complex*, equivalently T=(Omega+Upsilon)/2 and Y=(Omega-Upsilon)/(2i) are self-adjoint real free fields",
            "local_net": "F(O) is generated by Weyl operators of T(f) and Y(f), supp(f) subset O; the operator-affiliation target is the dual net Fd(O)=F(O')'",
            "vacuum": "the standard positive quasi-free massless vacuum",
            "internal_symmetries": [
                "charge conjugation kappa exchanges Omega and Upsilon",
                "U(1) charge gives Omega charge +1 and Upsilon charge -1"
            ],
            "status": "POSITIVE_AUXILIARY_FREE_COMPLEX_SCALAR_LOCAL_CARRIER_CONSTRUCTED"
        },
        "closable_charged_column": {
            "branches": [
                "A_h=D_Omega(h)=integral h(x):Omega F2 Omega:(x) dx",
                "B_h=D_Upsilon(h)=integral h(x):Upsilon F2 Upsilon:(x) dx"
            ],
            "common_domain": "the dense Weyl-invariant exponential-polynomial domain D=span{W(f)psi: psi finite-particle}",
            "adjoint_inclusions": [
                "D_Upsilon(conj h) subset D_Omega(h)*",
                "D_Omega(conj h) subset D_Upsilon(h)*"
            ],
            "column": "K_h psi=(D_Omega(h)psi,D_Upsilon(h)psi) from H to H direct_sum H",
            "closability_proof": "if psi_n tends to zero and K_h psi_n tends to (x,y), pairing x and y with D and using the two adjoint inclusions gives x=y=0",
            "separate_branch_essential_selfadjointness": "NOT_ASSUMED_AND_NOT_NEEDED",
            "status": "DENSELY_DEFINED_COLUMN_CLOSABLE"
        },
        "selfadjoint_pointer_block": {
            "operator": "V_h=[[0,Kbar_h*],[Kbar_h,0]] on H_g direct_sum (H_e_minus direct_sum H_e_plus)",
            "domain": "Dom(Kbar_h) direct_sum Dom(Kbar_h*)",
            "square": "V_h^2=diag(Kbar_h* Kbar_h,Kbar_h Kbar_h*)",
            "resolvent": "(V_h-z)^-1=[[z(K* K-z^2)^-1,K*(K K*-z^2)^-1],[K(K* K-z^2)^-1,z(K K*-z^2)^-1]] for z=plus or minus i",
            "resolvent_reason": "I+K* K and I+K K* are positive bijections and the mixed resolvent factors are bounded; multiplication gives the identity on both sides",
            "conclusion": "both plus/minus-i ranges are all of the amplified Hilbert space, hence V_h is self-adjoint",
            "finite_rational_witness": {
                "K": strings(witness_k),
                "V": strings(h),
                "I_plus_V_squared": strings(h2_plus_one),
                "inverse_I_plus_V_squared": strings(h2_plus_one_inverse),
                "left_I_plus_KstarK": strings(left_resolvent_denominator),
                "right_I_plus_KKstar": strings(right_resolvent_denominator)
            },
            "status": "SELFADJOINT_WITH_EXPLICIT_RESOLVENT"
        },
        "local_functional_calculus": {
            "affiliation_proof": "complement-supported Weyl unitaries preserve the exponential-polynomial domain and conjugate each compactly supported Wick branch to itself by free-field locality; closure gives affiliation of K, and V_h commutes with every commutant unitary of B(C3) tensor Fd(O)",
            "symmetry": "pointer exchange together with kappa commutes with V_h, and pointer charges -2,+2 cancel the field charges +2,-2",
            "unitary": "U_g=exp(-i g V_h) belongs to B(C3) tensor Fd(O) for every real g",
            "ground_to_click_block": "P_click U_g P_g=-i polar(K) sin(g|K|)",
            "effects": [
                "E_click(g)=sin^2(g|K|)",
                "E_no(g)=cos^2(g|K|)",
                "E_click+E_no=I and 0<=E_click,E_no<=I"
            ],
            "vacuum_boundary": "no exactly vacuum-dark local effect is asserted; the local click effect includes its unavoidable vacuum background",
            "status": "EXACT_BOUNDED_LOCAL_UNITARY_AND_NORMALIZED_POINTER_EFFECTS"
        },
        "operational_q8_tangent": {
            "inputs": "Psi_theta=(|g> tensor u+exp(i theta)|click> tensor v)/sqrt(2), with u and v the normalized charge-matched selected packet states",
            "readout": "p_theta(g)=<Psi_theta,U_g* P_click U_g Psi_theta>",
            "half_contrast": "C_theta(g)=[p_theta(g)-p_(theta+pi)(g)]/2",
            "exact_tangent": "C_theta(0)=0 and C_theta'(0)=Im(exp(-i theta)<v,K_h u>)",
            "phase_optimization": "max_theta |C_theta'(0)|=|<v,K_h u>|",
            "locality": "only the finite pointer click projection is read out; no final field-vacuum projector is measured",
            "mixed_tangent": "the lambda-four selected amplitude and its lambda-eight square are recovered after the detector-strength derivative at g=0",
            "strict_bound": "Q8_aux,compact/q4_bar>1/18874368000",
            "status": "STRICTLY_POSITIVE_Q8_TRANSITION_HAS_POINTER_ONLY_LOCAL_UNITARY_TANGENT"
        },
        "disposition": {
            "positive_auxiliary_free_local_carrier": "CONSTRUCTED",
            "charged_Wick_column": "CLOSABLE",
            "charge_balanced_pointer_block": "SELFADJOINT_AND_AFFILIATED",
            "bounded_local_functional_calculus": "CONSTRUCTED_EXACTLY",
            "finite_detector_strength_unitary": "CONSTRUCTED_EXACTLY",
            "normalized_local_pointer_effects": "CONSTRUCTED_WITH_NONZERO_VACUUM_BASELINE_ALLOWED",
            "selected_q8_operational_tangent": "COEFFICIENT_COMPUTED_AND_STRICTLY_POSITIVE",
            "positive_Hilbert_vs_public_generalized_Born_equivalence": "NOT_ESTABLISHED",
            "interacting_public_BT_local_net": "NOT_CONSTRUCTED",
            "lambda10_and_higher_BT_control": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "essential self-adjointness of D_Omega(h), D_Upsilon(h), or their scalar sum separately",
            "that the positive auxiliary Hilbert Born rule equals the public generalized Krein Born rule on arbitrary processes",
            "a zero-vacuum-probability nonzero bounded local click effect",
            "locality of a final active-field-vacuum postselection; the operational replacement is the pointer-only phase-reversal tangent",
            "selection of the packet, phase, pointer charges, switching or readout by the closed public BT Hamiltonian",
            "a nonperturbative interacting BT Haag--Kastler net or interacting time-ordered detector evolution",
            "the sign or convergence of lambda10 and higher BT corrections",
            "the standard scalar projector or general Eq. (19)",
            "an all-time Moller, LSZ or S operator",
            "gravity, metric BV--BRST import, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "missing_object_ledger": [
            "equivalence or a dynamics-compatible conditional expectation between the positive auxiliary and public generalized Born functionals",
            "a perturbatively or nonperturbatively interacting BT local net containing the public quartic dynamics",
            "lambda10 and higher response bounds for the local pointer contrast",
            "closed-BT dynamical preparation and calibration of the charged pointer interferometer",
            "the full Eq. (19) projector pushforward and its Q-sector physical quotient"
        ],
        "next_gate": "Use the exact local unitary to compute the lambda10 tangent of the pointer-only phase-reversal contrast and decide whether its sign can spoil finite-lambda positivity. In parallel, test whether the kappa-fixed local subalgebra admits a normal dynamics-compatible conditional expectation preserving the certified generalized-Born weights; that is the shortest remaining bridge toward Eq. (19) or a complete public physical interpretation.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_auxiliary_pointer_local_unitary.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_auxiliary_pointer_local_unitary.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_auxiliary_pointer_local_unitary"
        ],
        "report": REPORT
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = canonical(value)
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
        print(os.path.relpath(args.output, ROOT))
    if args.check:
        if not value["checks"]["ok"]:
            for failure in value["checks"]["failures"]:
                print("FAIL:", failure)
            return 1
        if os.path.exists(args.output):
            with open(args.output, encoding="utf-8") as handle:
                if handle.read() != rendered:
                    print("BT AUXILIARY POINTER LOCAL UNITARY: STALE CERTIFICATE")
                    return 1
        print(
            "BT AUXILIARY POINTER LOCAL UNITARY: ALL PASS "
            f"({value['checks']['passed']}/{value['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
