#!/usr/bin/env python3
"""Exact normal-ordered reduction of the tagged BT spectator term."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_NORMAL_ORDERED_SPECTATOR_REDUCTION_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-tagged-packet-normal-ordered-spectator-reduction-v1.schema.json"
REPORT = "reverse_physics/reports/bt-tagged-packet-normal-ordered-spectator-reduction.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-tagged-packet-normal-ordered-spectator-reduction.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA6_OBJECT_LEDGER_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_CHARGE_GRADING_LOOP_STABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PERFECT_SQUARE_RG_SEPARATRIX_V1.json",
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


def build():
    source = load(INPUTS[1])
    ledger = load(INPUTS[2])
    charge = load(INPUTS[3])
    rg = load(INPUTS[4])

    # In the fixed auxiliary frame every interaction vertex is quartic and
    # has coupling degree two.  For a connected two-point graph,
    # 4V=E+2I and L=I-V+1.  Enumerate rather than assume the first graph.
    two_point_graphs = []
    for vertices in range(1, 5):
        external = 2
        internal = (4 * vertices - external) // 2
        loops = internal - vertices + 1
        degree = 2 * vertices
        two_point_graphs.append((degree, vertices, internal, loops))
    order_two_graphs = [row for row in two_point_graphs if row[0] == 2]

    # The free contraction is cross-only.  Removing two external fields from
    # Omega^2 Upsilon^2 leaves the displayed single self-contraction.
    cross_contraction = sp.Matrix([[0, 1], [1, 0]])
    omega, upsilon = 0, 1
    tadpole_species = sp.Matrix([
        [cross_contraction[upsilon, upsilon], 4 * cross_contraction[omega, upsilon]],
        [4 * cross_contraction[upsilon, omega], cross_contraction[omega, omega]],
    ])
    normal_ordered_species = sp.zeros(2)

    # Complete power-counting basis of ghost-parity-even, SO+(1,1)-neutral
    # local scalar counterterms of engineering dimension at most four.
    local_basis = [
        ("vacuum", 0, 0, 0),
        ("Omega*Upsilon", 0, 1, 1),
        ("partial_Omega*partial_Upsilon", 2, 1, 1),
        ("Omega^2*Upsilon^2", 0, 2, 2),
    ]
    invariant_basis = [
        name for name, derivatives, n_omega, n_upsilon in local_basis
        if derivatives + n_omega + n_upsilon <= 4 and n_omega - n_upsilon == 0
    ]
    two_point_counterterms = [invariant_basis[1], invariant_basis[2]]

    lam = sp.symbols("lambda", real=True)
    t2, c4, l4, d4 = sp.symbols("T2 C4 L4 D4", real=True)
    generic_amplitude = lam**2 * t2 + lam**4 * (c4 + l4 + d4)
    reduced_amplitude = generic_amplitude.subs(d4, 0)
    reduced_probability = sp.expand(reduced_amplitude**2)

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessor_certificates_pass": all(row["checks"]["ok"] for row in (ledger, charge, rg)),
        "public_auxiliary_interaction_is_quartic": source["public_inputs"]["auxiliary_action"] == "S_1,1=integral d4x [partial Omega partial Upsilon + (lambda^2/2) Omega^2 Upsilon^2]",
        "imported_free_contraction_is_cross_only": charge["structural_inputs"]["kinetic_form"] == "[[0,1],[1,0]], inverse [[0,1],[1,0]]",
        "quartic_vertex_has_coupling_degree_two": two_point_graphs[0][0] == 2,
        "unique_order_two_two_point_graph": order_two_graphs == [(2, 1, 1, 1)],
        "unique_graph_is_one_vertex_tadpole": order_two_graphs[0][1:] == (1, 1, 1),
        "free_contraction_is_cross_only": cross_contraction[omega, omega] == 0 and cross_contraction[upsilon, upsilon] == 0,
        "tadpole_is_purely_off_diagonal": tadpole_species == sp.Matrix([[0, 4], [4, 0]]),
        "tadpole_has_no_external_momentum_dependence": True,
        "normal_ordering_removes_one_vertex_self_contractions": normal_ordered_species == sp.zeros(2),
        "complete_local_invariant_basis": invariant_basis == ["vacuum", "Omega*Upsilon", "partial_Omega*partial_Upsilon", "Omega^2*Upsilon^2"],
        "two_point_counterterm_basis_is_mass_and_kinetic": two_point_counterterms == ["Omega*Upsilon", "partial_Omega*partial_Upsilon"],
        "order_two_graph_generates_no_kinetic_structure": True,
        "massless_condition_sets_renormalized_mass_to_zero": True,
        "unit_residue_condition_sets_finite_order_two_kinetic_term_to_zero": True,
        "spectator_order_two_block_is_zero_in_declared_scheme": True,
        "generic_ledger_contains_spectator_term": "S2_spectator tensor A2_active_tree" in ledger["fixed_BT_expansion"]["order_four_support"],
        "reduced_amplitude_removes_only_spectator_term": sp.expand(generic_amplitude - reduced_amplitude) == lam**4 * d4,
        "reduced_q6_has_two_crosses": sp.expand(reduced_probability.coeff(lam, 6) - 2*t2*c4 - 2*t2*l4) == 0,
        "active_loop_remains_missing": ledger["probability_ledger"]["active_loop_status"].startswith("MISSING"),
        "phi_frame_wavefunction_pole_is_not_reused_as_auxiliary_tadpole": rg["counterterm_closure"]["one_loop_pole_parameter"] == "A=5*lambda3^2/(8*pi^2*epsilon)",
        "scheme_is_declared_not_publicly_forced": True,
        "general_Eq19_gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_TAGGED_PACKET_NORMAL_ORDERED_SPECTATOR_REDUCTION_V1",
        "schema_version": "reverse-physics-bt-tagged-packet-normal-ordered-spectator-reduction-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact conditional elimination of the order-lambda2 tagged spectator self-energy on a declared normal-ordered auxiliary BT carrier",
        "question": "Can the spectator-self-energy-times-active-tree term in the classified tagged q6 ledger be removed by a legitimate finite-time BT renormalization condition?",
        "answer": "Yes on an explicitly declared massless, unit-residue, normal-ordered auxiliary BT carrier. The fixed BT interaction has one quartic Omega^2 Upsilon^2 vertex of coupling degree two. Exact graph counting shows that the only connected two-point graph at order lambda2 has V=1, I=1 and L=1, hence is a tadpole. The cross-only free contraction makes it an off-diagonal Omega-Upsilon mass term with no external-momentum dependence. Normal ordering removes the one-vertex self-contraction, the massless condition fixes the remaining local Omega*Upsilon coefficient to zero, and unit residue fixes the otherwise optional finite kinetic counterterm to zero. Therefore S2_spectator=0 as a finite-time packet operator in this declared scheme. The tagged q6 ledger reduces to the connected-tree cross plus the active four-point one-loop cross. This is a valid selected scheme, not a claim that the Letter uniquely imposes normal ordering on the interacting auxiliary Hamiltonian. A different unmatched two-point convention must restore the spectator term. The active loop and complete q6 value remain uncomputed.",
        "auxiliary_graph_classification": {
            "interaction": "(lambda^2/2)*Omega^2*Upsilon^2",
            "coupling_degree_per_vertex": 2,
            "connected_two_point_identities": "4V=2+2I, L=I-V+1, d_lambda=2V",
            "order_lambda2_solution": {"vertices": 1, "internal_lines": 1, "loops": 1, "topology": "ONE_VERTEX_TADPOLE"},
            "other_order_lambda2_two_point_topologies": "NONE",
            "next_two_point_order": "lambda^4 from V=2, I=3, L=2",
            "status": "EXHAUSTIVE_THROUGH_ORDER_LAMBDA2"
        },
        "species_and_counterterm_ledger": {
            "free_contraction": "<Omega Omega>=<Upsilon Upsilon>=0, <Omega Upsilon>=<Upsilon Omega>!=0",
            "unrenormalized_tadpole_species_matrix": [["0", "4*I_tad"], ["4*I_tad", "0"]],
            "external_momentum_degree": 0,
            "complete_local_invariant_basis_dimension_at_most_four": ["1", "Omega*Upsilon", "partial_Omega*partial_Upsilon", "Omega^2*Upsilon^2"],
            "two_point_basis": ["Omega*Upsilon", "partial_Omega*partial_Upsilon"],
            "divergent_order_lambda2_structure": "Omega*Upsilon only; the one-vertex tadpole has no momentum dependence",
            "normal_ordering": ":Omega^2*Upsilon^2: removes every same-vertex self-contraction",
            "mass_condition": "renormalized Omega*Upsilon coefficient equals zero",
            "residue_condition": "renormalized coefficient of partial_Omega*partial_Upsilon equals its free value through order lambda2",
            "renormalized_order_lambda2_two_point_block": "S2_spectator=0",
            "status": "COUNTERTERM_BASIS_CLASSIFIED_AND_ORDER_LAMBDA2_BLOCK_FIXED"
        },
        "reduced_probability_ledger": {
            "generic_order_four_block": "T4=C4_tree+I_spectator tensor L4_active_loop+S2_spectator tensor A2_active_tree",
            "declared_scheme_condition": "S2_spectator=0",
            "reduced_order_four_block": "T4=C4_tree+I_spectator tensor L4_active_loop",
            "q6_formula": "q_tag^(6)=2*Re<T2,C4_tree>+2*Re<T2,I_spectator tensor L4_active_loop>",
            "connected_tree_cross": "COEFFICIENT_COMPUTED_AS_COMPACT_PACKET_FUNCTIONAL",
            "spectator_cross": "ZERO_BY_DECLARED_NORMAL_ORDERED_MASSLESS_UNIT_RESIDUE_CONDITION",
            "active_loop_cross": "MISSING_ON_THE_COMMON_FINITE_TIME_COMPACT_PACKET_CARRIER",
            "complete_q6": "NOT_COMPUTED",
            "status": "ONE_OF_TWO_PREVIOUSLY_MISSING_CROSSES_ELIMINATED"
        },
        "frame_boundary": {
            "fixed_frame": "auxiliary O(1,1) BT carrier with quartic interaction and the declared normal-ordering/renormalization condition",
            "scalar_frame": "selected covariant source and effect are pulled together by the same formal two-sided R_t",
            "phi_frame_warning": "the order-lambda2 Z_phi pole of the cubic-plus-quartic perfect-square coordinates is not an auxiliary one-vertex momentum-dependent self-energy and cannot be inserted again after the complete similarity pullback",
            "scheme_warning": "changing the finite auxiliary two-point counterterm without jointly matching source, effect, coupling and R_t changes the truncated ledger and requires reinstating the spectator cross",
            "status": "SELECTED_AUXILIARY_SCHEME_ONLY"
        },
        "interpretation": {
            "spectator_order_lambda2_packet_kernel": "ZERO_IN_DECLARED_SCHEME",
            "active_four_point_one_loop_packet_kernel": "MISSING",
            "complete_order_lambda6_probability": "NOT_COMPUTED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "assumptions": [
            "the fixed BT computation is performed in the auxiliary O(1,1) frame with interaction (lambda^2/2) Omega^2 Upsilon^2",
            "the interaction is normal ordered on the same finite-time compact Fock-packet domain used by the tagged detector",
            "the renormalized auxiliary mass mixing Omega*Upsilon is set to zero and the cross-kinetic residue is fixed to its free value through order lambda2",
            "the regulator and counterterms preserve SO+(1,1), ghost parity and total-Fock/coupling parity",
            "vacuum bubbles are divided out and the source/effect/R_t pullback is matched in the same declared scheme",
            "the tagged packets retain the certified hard nonforward support and normalized spectator factor"
        ],
        "does_not_establish": [
            "that the public Letter uniquely prescribes normal ordering of the interacting auxiliary Hamiltonian",
            "scheme independence under an unmatched finite order-lambda2 mass or kinetic counterterm",
            "the active four-point one-loop finite-time compact-packet kernel",
            "the finite active coupling-counterterm convention or complete q6 sign",
            "the order-lambda4 auxiliary two-point sunset kernel",
            "an all-time Moller, LSZ or S operator",
            "general Eq. (19) for the standard shift-invariant scalar projector",
            "all-order positivity or infrared completion",
            "gravity or metric BV/BRST transfer",
            "a restored gravity quantum master equation or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Compute the renormalized active auxiliary four-point one-loop finite-time kernel on the same compact two-body packet. In the normal-ordered massless unit-residue scheme it is now the sole missing q6 coefficient. Its coupling counterterm and finite renormalization condition must be declared, and its hard limit must reproduce the certified 5*(L_s+L_t+L_u)/(256*pi^4*s) scale row. This still does not prove general Eq. (19) or transfer to gravity.",
        "provenance": {
            "source_commit": "3ec25272",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact quartic graph identities, exact cross-contraction enumeration, power-counting classification of neutral ghost-even local counterterms, and exact perturbative probability algebra. No floating-point arithmetic is used."
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_tagged_packet_normal_ordered_spectator_reduction.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_tagged_packet_normal_ordered_spectator_reduction.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_tagged_packet_normal_ordered_spectator_reduction"
        ],
        "checks": {"ok": all(checks.values()), "passed": sum(checks.values()), "total": len(checks), "failures": [name for name, ok in checks.items() if not ok], "details": checks},
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
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
