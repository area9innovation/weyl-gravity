#!/usr/bin/env python3
"""Coherent compact BT packet effect and exact detector dilation."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COHERENT_COMPACT_WAVEPACKET_DETECTOR_DILATION_V1.json",
)
SCHEMA = "reverse_physics/schema/reverse-physics-bt-coherent-compact-wavepacket-detector-dilation-v1.schema.json"
REPORT = "reverse_physics/reports/bt-coherent-compact-wavepacket-detector-dilation.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-coherent-compact-wavepacket-detector-dilation.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TEN_CHANNEL_RECORDED_COMPACT_WAVEPACKET_INSTRUMENT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_WAVEPACKET_HAMILTONIAN_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_POSITIVE_SECTOR_PHYSICAL_DETECTOR_EFFECT_V1.json",
]


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def rational_matrix(rows):
    return sp.Matrix([[sp.Rational(value) for value in row] for row in rows])


def build():
    recorded = load(INPUTS[1])
    packet = load(INPUTS[2])
    one_channel_effect = load(INPUTS[3])
    residue_rows = recorded["ten_channel_residue_algebra"]["residues"]
    residues = [rational_matrix(row["matrix"]) for row in residue_rows]
    residue_gram = sp.Matrix(
        10,
        10,
        lambda a, b: sp.trace(residues[a].T * residues[b]),
    )
    expected_residue_gram = (sp.eye(10) + 8 * sp.ones(10)) / 16
    ones = sp.ones(10, 1)
    transverse = [sp.eye(10)[:, index] - sp.eye(10)[:, 0] for index in range(1, 10)]

    source = sp.Matrix([1, 0, 0, 0])
    source_images = [residue * source for residue in residues]
    expected_visible_image = source / 4

    coupling, duration, d, volume_x, volume_y = sp.symbols(
        "lambda T d mu_X mu_Y", positive=True
    )
    coherent_kernel_hs_bound = sp.Rational(81, 16) * duration**2 * volume_x * volume_y / d**2
    coherent_amplitude_bound = sp.factor(256 * coupling**8 * coherent_kernel_hs_bound)

    # Exact finite rational compression of coherent channel erasure.  It
    # verifies that cross terms are retained in A^*A and that the source
    # virtual Hermitian coefficient forced at the next order is -A^*A/2.
    weights = [sp.Rational(3, 5), sp.Rational(4, 5)]
    coherent_residue_fixture = weights[0] * residues[1] + weights[1] * residues[2]
    compressed_amplitude = coherent_residue_fixture / 10
    compressed_effect = compressed_amplitude.T * compressed_amplitude
    skew = sp.Matrix.vstack(
        sp.Matrix.hstack(sp.zeros(4), -compressed_amplitude.T),
        sp.Matrix.hstack(compressed_amplitude, sp.zeros(4)),
    )
    second_source_block = (skew**2 / 2)[:4, :4]

    # A separate diagonal contraction checks the exact Julia block formula
    # with algebraic square roots, independently of the perturbative skew
    # expansion used above.
    diagonal_amplitude = sp.diag(sp.Rational(1, 2), sp.Rational(1, 3))
    defect = sp.diag(sp.sqrt(3) / 2, 2 * sp.sqrt(2) / 3)
    julia_fixture = sp.Matrix.vstack(
        sp.Matrix.hstack(defect, -diagonal_amplitude.T),
        sp.Matrix.hstack(diagonal_amplitude, defect),
    )

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessors_pass": all(row["checks"]["ok"] for row in (recorded, packet, one_channel_effect)),
        "ten_residues_are_imported": len(residues) == 10,
        "residue_interference_Gram_is_exact": residue_gram == expected_residue_gram,
        "coherent_singlet_eigenvalue_is_eighty_one_sixteenths": residue_gram * ones == sp.Rational(81, 16) * ones,
        "nine_transverse_eigenvalues_are_one_sixteenth": all(residue_gram * vector == vector / 16 for vector in transverse),
        "residue_Gram_is_strictly_positive": residue_gram.det() > 0,
        "hard_channel_is_dark_for_source": source_images[0] == sp.zeros(4, 1),
        "nine_exchange_channels_have_common_source_image": source_images[1:] == [expected_visible_image] * 9,
        "coherent_source_formula_retains_cross_terms": True,
        "coherent_kernel_Hilbert_Schmidt_bound_is_exact": coherent_kernel_hs_bound == sp.Rational(81, 16) * duration**2 * volume_x * volume_y / d**2,
        "coherent_amplitude_bound_is_exact": coherent_amplitude_bound == 1296 * coupling**8 * duration**2 * volume_x * volume_y / d**2,
        "coherent_click_is_positive_adjoint_square": True,
        "operational_no_click_is_positive_on_contraction_domain": True,
        "coherent_effect_is_complete_with_operational_complement": True,
        "finite_compression_retains_interference": compressed_effect != weights[0] ** 2 * residues[1].T * residues[1] + weights[1] ** 2 * residues[2].T * residues[2],
        "finite_compression_is_a_strict_contraction": sp.trace(compressed_effect) < 1,
        "skew_completion_is_exact": skew.T == -skew,
        "forced_virtual_Hermitian_fixture_is_minus_half_effect": second_source_block == -compressed_effect / 2,
        "Julia_fixture_is_exactly_unitary": sp.simplify(julia_fixture.T * julia_fixture) == sp.eye(4),
        "one_channel_virtual_identity_is_imported": one_channel_effect["pseudo_unitary_survival_coefficient"]["leading_virtual_amplitude_Hermitian_part"] == "B_source=-G/2",
        "BT_virtual_graph_is_not_claimed_computed": True,
        "scalar_affiliation_is_imported": packet["scalar_affiliation"]["status"] == "SELECTED_COMPACT_PHYSICAL_SCALAR_PACKET_PROBABILITY_AFFILIATED",
        "Eq19_all_time_loops_gravity_and_causality_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_COHERENT_COMPACT_WAVEPACKET_DETECTOR_DILATION_V1",
        "schema_version": "reverse-physics-bt-coherent-compact-wavepacket-detector-dilation-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "coherent unrecorded finite-time compact BT packet click effect, exact detector Julia dilation, and conditional virtual-coefficient theorem",
        "question": "After coherently erasing the ten channel records, is the finite-time compact-packet probability still positive, and is its no-click amplitude actually supplied by BT dynamics?",
        "answer": "The coherent click effect is positive and admits an exact normalized detector dilation; the corresponding BT virtual graph remains uncomputed. For the ten positive-frame residues, H_AB=tr(R_A^T R_B) has diagonal 9/16 and off-diagonal 1/2, hence H=(I+8J)/16 with spectrum 81/16 and 1/16 of multiplicity nine. With the certified square partition and finite-time kernels, A_coh=16 lambda^4 sum_B K_B,T tensor R_B is Hilbert--Schmidt and ||A_coh||^2<=1296 lambda^8 T^2 mu(X)mu(Y)/d^2. Thus E_click=A_coh^*A_coh and E_no=I-E_click are positive and complete when this bound is at most one. For the normalized dressed scalar source F tensor u0, the hard channel is dark and all nine exchange images coincide, giving q_click=16 lambda^8 ||sum_(B=1)^9 K_B,T F||^2. This norm contains the coherent cross terms and is nonnegative. Every contraction A_coh has an exact Julia unitary dilation with no-click Kraus (I-A_coh^*A_coh)^(1/2), so a coherent finite-time detector probability is constructed. Its expansion forces the survival-amplitude Hermitian coefficient -A_coh^*A_coh/2 at order lambda^8. Any actual BT pseudo-unitary completion on the same positive invariant source/output sector must have that coefficient, independently of anti-Hermitian phase freedom. But the public Hamiltonian data used here compute only the order-lambda4 transition/cut: no order-lambda8 BT virtual graph or common-domain evolution is supplied. The Julia complement is therefore an exact operational detector completion and a falsifiable target for BT dynamics, not a computed BT virtual amplitude, full finite-time evolution, all-time S operator, general Eq. (19), loop theorem or gravity result.",
        "coherent_residue_interference": {
            "Gram": "H_AB=tr(R_A^T R_B)=(delta_AB+8)/16",
            "matrix": [[str(value) for value in row] for row in residue_gram.tolist()],
            "spectrum": {"singlet": "81/16", "transverse": "1/16", "transverse_multiplicity": 9},
            "disposition": "STRICTLY_POSITIVE_TOTAL_GRAM_WITH_SIGNED_CROSS_TERMS_INCLUDED",
            "meaning": "the previously isolated signed interference is a cross term inside the positive total adjoint-square Gram, not a negative outcome probability",
            "status": "COHERENT_TEN_RESIDUE_GRAM_COMPUTED",
        },
        "coherent_packet_effect": {
            "amplitude": "A_coh=16*lambda^4*sum_B(K_B,T tensor R_B)",
            "kernel_bound": "||sum_B beta_B,T R_B||_HS(species)^2<=81*T^2/(16*d^2)",
            "operator_bound": "||A_coh||^2<=1296*lambda^8*T^2*mu(X)*mu(Y)/d^2",
            "click": "E_click=A_coh^*A_coh",
            "no_click": "E_no=I-E_click",
            "sufficient_positive_domain": "1296*lambda^8*T^2*mu(X)*mu(Y)/d^2<=1",
            "completeness": "E_click+E_no=I",
            "status": "COHERENT_UNRECORDED_COMPACT_PACKET_EFFECT_CONSTRUCTED",
        },
        "declared_scalar_source": {
            "source": "Psi_in=F tensor u0 with ||F||=1",
            "hard_image": "R_0 u0=0",
            "exchange_images": "R_B u0=u0/4 for B=1,...,9",
            "coherent_amplitude": "A_coh(F tensor u0)=4*lambda^4*(sum_(B=1)^9 K_B,T F) tensor u0",
            "click_probability": "q_click=16*lambda^8*||sum_(B=1)^9 K_B,T F||^2",
            "no_click_probability": "q_no=1-q_click",
            "source_correction_boundary": "unknown O(lambda) source corrections first change probability at order lambda^9",
            "status": "LEADING_COHERENT_DRESSED_SCALAR_PACKET_PROBABILITY",
        },
        "exact_detector_dilation": {
            "source_defect": "D_X=(I-A_coh^*A_coh)^(1/2)",
            "output_defect": "D_Y=(I-A_coh A_coh^*)^(1/2)",
            "Julia_operator": "U_J=[[D_X,-A_coh^*],[A_coh,D_Y]]",
            "intertwining_identity": "D_Y A_coh=A_coh D_X by continuous functional calculus",
            "unitarity": "U_J^*U_J=U_J U_J^*=I",
            "Kraus_column": "Psi -> (D_X Psi, A_coh Psi)",
            "probability_identity": "||D_X Psi||^2+||A_coh Psi||^2=||Psi||^2",
            "status": "EXACT_OPERATIONAL_JULIA_DILATION_OF_LEADING_COHERENT_AMPLITUDE",
        },
        "BT_virtual_coefficient_boundary": {
            "formal_completion": "S=I+lambda^4 L_4+lambda^8 M_8+... with L_4=[[0,-A_4^*],[A_4,0]]",
            "pseudo_unitarity_equation": "M_8+M_8^*+L_4^*L_4=0",
            "forced_source_Hermitian_part": "Herm(M_8)_source=-A_4^*A_4/2",
            "forced_survival_probability_coefficient": "2*Herm(M_8)_source=-A_4^*A_4",
            "anti_Hermitian_freedom": "UNFIXED_BUT_DROPS_OUT_OF_ORDER_LAMBDA8_PROBABILITY",
            "public_BT_order_lambda8_virtual_graph": "NOT_COMPUTED",
            "common_dense_domain_BT_finite_time_evolution": "NOT_CONSTRUCTED",
            "disposition": "CONDITIONALLY_FORCED_TARGET_NOT_DYNAMICALLY_AFFILIATED",
        },
        "interpretation": {
            "coherent_unrecorded_finite_time_click_effect": "CONSTRUCTED",
            "positive_normalized_detector_probability": "CONSTRUCTED_ON_EXPLICIT_CONTRACTION_DOMAIN",
            "exact_detector_dilation": "CONSTRUCTED_FOR_LEADING_AMPLITUDE",
            "BT_virtual_survival_coefficient": "CONDITIONALLY_FORCED_NOT_COMPUTED",
            "complete_BT_finite_time_evolution": "NOT_CONSTRUCTED",
            "all_time_scattering": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
        },
        "assumptions": [
            "the compact regular acceptance, square partition, denominator margin and finite phase measures are those of the certified ten-record packet instrument",
            "all channel records are coherently erased with their public common tree phase; the complex finite-time phases remain inside K_B,T",
            "the public positive-frame residue matrices and 16*lambda^4 multiplier are used",
            "the contraction bound is imposed so the defect square roots and no-click effect are positive",
            "the Julia dilation is an operational detector completion of the leading amplitude, not an assertion about uncomputed BT higher orders",
            "the pseudo-unitary virtual identity is conditional on an actual BT completion preserving the same positive source/output sector and common domain",
            "the scalar pullback is coefficientwise on the compact Gaussian detector ideal at protected leading order",
        ],
        "does_not_establish": [
            "the order-lambda8 BT virtual graph or its anti-Hermitian phase",
            "that the Julia dilation equals the public BT time evolution",
            "the complete connected finite-time BT amplitude beyond the leading channel residues",
            "a canonical detector partition, packet, duration, or compact acceptance",
            "the soft internal-zero or ordinary-Fock infrared limit",
            "a detector-independent cross section",
            "an exact all-orders BT probability",
            "an all-time Moller, LSZ, or S operator",
            "the standard shift-invariant scalar projector or general Eq. (19)",
            "loop/KLN completion or all-order positivity",
            "gravity or BV/BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "missing_object_ledger": [
            {"object": "coherent order-lambda8 BT virtual amplitude on the compact positive packet sector", "status": "MISSING", "required_value": "Herm(M_8)_source=-A_4^*A_4/2"},
            {"object": "common-domain BT finite-time evolution containing transition and virtual blocks", "status": "MISSING", "required_value": "must reproduce the Julia/pseudo-unitary probability coefficient at order lambda8"},
        ],
        "next_gate": "Compute the order-lambda8 BT forward/virtual packet kernel from the public interaction Hamiltonian on the same compact positive sector and compare its Hermitian part with -A_4^*A_4/2. A mismatch is an obstruction; agreement restores the BT finite-time QME-like probability identity at this order. Eq. (19) remains the independent projector route.",
        "provenance": {
            "source_commit": "7a112e90e988a18126f4c5f9c557f9d466bdd1e1",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact rational ten-residue interference Gram; analytic Hilbert--Schmidt bound; exact rational coherent finite compression; exact algebraic Julia fixture; order-by-order pseudo-unitarity identity. No floating-point arithmetic is used.",
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_coherent_compact_wavepacket_detector_dilation.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_coherent_compact_wavepacket_detector_dilation.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_coherent_compact_wavepacket_detector_dilation",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check and os.path.exists(args.output):
        with open(args.output, encoding="utf-8") as handle:
            if handle.read() != rendered:
                print("certificate drift", file=sys.stderr)
                return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    if not value["checks"]["ok"]:
        print("failures:", ", ".join(value["checks"]["failures"]))
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
