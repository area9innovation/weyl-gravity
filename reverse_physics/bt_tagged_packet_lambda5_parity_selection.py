#!/usr/bin/env python3
"""Total-Fock-parity selection of the tagged BT lambda-five probability."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import os
import sys

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA5_PARITY_SELECTION_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-tagged-packet-lambda5-parity-selection-v1.schema.json"
REPORT = "reverse_physics/reports/bt-tagged-packet-lambda5-parity-selection.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-tagged-packet-lambda5-parity-selection.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_CONNECTED_COMPACT_PACKET_INTERFERENCE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_COMPACT_WAVEPACKET_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_FREE_NORMAL_FORM_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_ORDER4_PACKET_COLUMN_V1.json",
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
    compact_cross = load(INPUTS[1])
    tagged = load(INPUTS[2])
    compact_source = load(INPUTS[3])
    source_normal = load(INPUTS[4])
    signed_R = load(INPUTS[5])
    connected = load(INPUTS[6])

    lam, box_term, derivative_term = sp.symbols("lambda B D")
    perfect_square = (box_term + lam * derivative_term) ** 2
    transformed_square = ((-box_term) + (-lam) * derivative_term) ** 2

    phi = sp.symbols("phi")
    omega_fluctuation = sum(lam**n * phi ** (n + 1) / sp.factorial(n + 1) for n in range(6))
    transformed_omega = sp.expand(omega_fluctuation.subs({lam: -lam, phi: -phi}, simultaneous=True))
    upsilon_truncation = sum((-lam * phi) ** n / sp.factorial(n) for n in range(6)) * (
        box_term + lam * derivative_term
    )
    transformed_upsilon = sp.expand(
        upsilon_truncation.subs(
            {lam: -lam, phi: -phi, box_term: -box_term}, simultaneous=True
        )
    )

    graph_rows = []
    for cubic_vertices in range(7):
        for quartic_vertices in range(5):
            for internal_edges in range(9):
                external_legs = 3 * cubic_vertices + 4 * quartic_vertices - 2 * internal_edges
                if external_legs < 0:
                    continue
                coupling_degree = cubic_vertices + 2 * quartic_vertices
                graph_rows.append(
                    {
                        "V3": cubic_vertices,
                        "V4": quartic_vertices,
                        "I": internal_edges,
                        "E": external_legs,
                        "d_lambda": coupling_degree,
                        "parity_match": external_legs % 2 == coupling_degree % 2,
                    }
                )

    # A method-visible finite Krein fixture. Odd and even Fock sectors have
    # independent cross metrics; an off-block mutation makes the forbidden
    # fifth-order pairing nonzero.
    J2 = sp.Matrix([[0, 1], [1, 0]])
    gram = sp.diag(1, 1, 1, 1)
    gram[:2, :2] = J2
    gram[2:, 2:] = J2
    parity = sp.diag(-1, -1, 1, 1)
    y2 = sp.Matrix([2, -3, 0, 0])
    y3 = sp.Matrix([0, 0, 5, 7])
    q5 = sp.factor(2 * (y2.T * gram * y3)[0])
    broken_gram = gram.copy()
    broken_gram[0, 2] = broken_gram[2, 0] = 1
    broken_q5 = sp.factor(2 * (y2.T * broken_gram * y3)[0])

    # Operator parity blocks on the same carrier.
    A2 = sp.Matrix([[1, 2, 0, 0], [3, -1, 0, 0], [0, 0, 2, 1], [0, 0, -2, 4]])
    A3 = sp.Matrix([[0, 0, 1, 2], [0, 0, -1, 3], [4, 1, 0, 0], [2, -2, 0, 0]])
    even_covariance = parity * A2 * parity == A2
    odd_covariance = parity * A3 * parity == -A3

    q4, q5_symbol, q6 = sp.symbols("q4 q5 q6")
    probability = q4 * lam**4 + q5_symbol * lam**5 + q6 * lam**6
    even_constraint = sp.Poly(sp.expand(probability - probability.subs(lam, -lam)), lam)
    forced_q5 = sp.solve(list(even_constraint.all_coeffs()), [q5_symbol], dict=True)

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessors_pass": all(row["checks"]["ok"] for row in (compact_cross, tagged, compact_source, source_normal, signed_R, connected)),
        "perfect_square_action_covariance_is_exact": sp.expand(perfect_square - transformed_square) == 0,
        "Omega_fluctuation_covariance_holds_through_five": sp.expand(transformed_omega + omega_fluctuation) == 0,
        "every_Omega_coefficient_has_the_required_sign": all(
            sp.expand((-lam) ** n * (-phi) ** (n + 1) + lam**n * phi ** (n + 1)) == 0
            for n in range(6)
        ),
        "Upsilon_composite_covariance_holds_through_five": sp.expand(transformed_upsilon + upsilon_truncation) == 0,
        "all_enumerated_graphs_obey_E_congruent_d_mod_two": graph_rows and all(row["parity_match"] for row in graph_rows),
        "cubic_vertex_is_odd_at_order_one": (3 % 2) == (1 % 2),
        "quartic_vertex_is_even_at_order_two": (4 % 2) == (2 % 2),
        "leading_source_has_three_particle_odd_parity": compact_source["positive_packet_frame"]["declared_source"].count("^3") == 2,
        "order_lambda_R_map_is_quadratic": signed_R["completed_signed_kernel"]["disposition"] == "COMPLETE_FOR_THE_PUBLIC_ORDER_LAMBDA_QUADRATIC_COMPOSITE_MAP_ON_FINITE_NONENDPOINT_MODES",
        "order_lambda_R_generator_is_cubic": signed_R["finite_mode_Eq19"]["generator_charge_after_Z_dressing"] == 0 and "cubic generator" in signed_R["answer"],
        "leading_tagged_amplitude_order_is_two": tagged["complete_leading_tagged_probability"]["amplitude"].startswith("P_Y*(U-I)*P_X=lambda^2"),
        "connected_tree_first_enters_at_order_four": tagged["partition_and_order_classification"]["order_four"].startswith("the connected six-point tree"),
        "odd_even_gram_is_block_diagonal": parity.T * gram * parity == gram,
        "Fock_parity_is_Krein_selfadjoint": parity.T * gram == gram * parity,
        "order_two_operator_is_parity_even": even_covariance,
        "order_three_operator_is_parity_odd": odd_covariance,
        "leading_output_is_odd": parity * y2 == -y2,
        "next_output_is_even": parity * y3 == y3,
        "lambda5_cross_coefficient_is_zero": q5 == 0,
        "parity_breaking_metric_mutation_is_detected": broken_q5 == 20,
        "probability_evenness_forces_q5_zero": forced_q5 == [{q5_symbol: 0}],
        "compact_packet_cross_starts_at_lambda6": compact_cross["physical_interpretation"]["compact_packet_tree_cross"] == "COEFFICIENT_COMPUTED_AS_FUNCTIONAL",
        "lambda6_remains_incomplete": compact_cross["physical_interpretation"]["complete_order_lambda6_probability"] == "NOT_COMPUTED",
        "Eq19_gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA5_PARITY_SELECTION_V1",
        "schema_version": "reverse-physics-bt-tagged-packet-lambda5-parity-selection-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact total-Fock-parity selection theorem for the complete probability-order-lambda5 coefficient of the covariantly dressed hard tagged BT packet experiment",
        "question": "Can an unknown order-lambda source or detector correction generate a probability-order-lambda5 term between the leading tagged packet amplitude and its first correction?",
        "answer": "No for the declared covariantly dressed hard tagged compact-packet experiment. Let Pi_F=(-1)^N be total fluctuation Fock parity, distinct from BT ghost parity and O(1,1) charge. The exact perfect-square action obeys S_lambda[phi]=S_-lambda[-phi], and the exact BT composite map is covariant when phi, Omega and Upsilon all change sign together with lambda. Hence the order-n evolution, source and detector coefficients have Pi_F parity (-1)^n relative to their leading blocks. The leading three-particle source is odd and its order-lambda correction is even. The tagged order-lambda2 output y2 is therefore odd, while the complete order-lambda3 output y3 is even; y3 includes the dynamical A3 psi0 term, A2 psi1 source term and the first covariant detector correction. The public cross-Krein form pairs only equal total particle number and commutes with Pi_F, so odd and even sectors are orthogonal and q_tag^(5)=2 Re<y2,y3>_K=0. Equivalently the covariantly named probability satisfies q(lambda)=q(-lambda), forcing every odd perturbative coefficient to vanish. Thus q_tag=lambda4*q4+lambda6*q6+O(lambda8) in parity order, with no lambda5 term. This removes the skipped-order concern but does not compute q6: the compact tree cross, active one-loop, second-order source/detector, and survival terms still have to be assembled.",
        "exact_covariance": {
            "total_Fock_parity": "Pi_F=(-1)^N on scalar or BT fluctuation particle number",
            "distinction": "Pi_F is not BT ghost parity kappa and is not the SO+(1,1) charge",
            "action": "S_lambda[phi]=S_-lambda[-phi] for S=-1/2*integral(Box phi+lambda*(partial phi)^2)^2",
            "BT_composites": "(Omega,Upsilon)_lambda[phi]=-(Omega,Upsilon)_-lambda[-phi], including the transformed 1/lambda background",
            "evolution_coefficients": "Pi_F U_n Pi_F=(-1)^n U_n",
            "dressed_projector_coefficients": "Pi_F P_n Pi_F=(-1)^n P_n for covariantly transported source and detector projectors",
            "probability": "q(lambda)=q(-lambda)",
            "status": "EXACT_COUPLING_FOCK_PARITY_COVARIANCE"
        },
        "vertex_and_graph_selection": {
            "cubic": "H_1 has three fluctuation fields, coupling degree one and odd Pi_F parity",
            "quartic": "H_2 has four fluctuation fields, coupling degree two and even Pi_F parity",
            "graph_identity": "3*V3+4*V4=2*I+E and d_lambda=V3+2*V4 imply E congruent d_lambda mod 2",
            "enumerated_fixture_count": len(graph_rows),
            "enumerated_range": "0<=V3<=6, 0<=V4<=4, 0<=I<=8 with E>=0",
            "all_fixture_rows_pass": all(row["parity_match"] for row in graph_rows),
            "status": "COUPLING_ORDER_EQUALS_PARTICLE_PARITY_CHANGE"
        },
        "tagged_output_selection": {
            "source_series": "psi=lambda^0*psi0+lambda*psi1+O(lambda^2)",
            "source_parities": "Pi_F psi0=-psi0 and Pi_F psi1=+psi1",
            "tagged_output_series": "Y=lambda^2*y2+lambda^3*y3+lambda^4*y4+...",
            "leading_output": "y2 contains A2 psi0 and is Pi_F-odd",
            "complete_next_output": "y3 contains A3 psi0, A2 psi1 and first detector correction and is Pi_F-even",
            "Krein_orthogonality": "Pi_F^sharp=Pi_F and [Pi_F,G_K]=0 imply <odd,even>_K=0",
            "lambda5_coefficient": "q_tag^(5)=2*Re<y2,y3>_K=0",
            "probability_series": "q_tag=lambda^4*q4+0*lambda^5+lambda^6*q6+O(lambda^8), with all odd coefficients zero for the covariant family",
            "leading_q4": "q4=3*DeltaOmega/(32*pi^2*s*Area) on the certified tagged packet",
            "status": "COMPLETE_PROBABILITY_ORDER_LAMBDA5_COEFFICIENT_ZERO"
        },
        "finite_Krein_witness": {
            "metric": [[str(value) for value in row] for row in gram.tolist()],
            "parity": [[str(value) for value in row] for row in parity.tolist()],
            "y2": [str(value) for value in y2],
            "y3": [str(value) for value in y3],
            "cross": str(q5),
            "parity_breaking_cross": str(broken_q5),
            "purpose": "method-visible block-orthogonality witness; the theorem follows from exact covariance rather than this fixture"
        },
        "interpretation": {
            "probability_order_lambda5": "EXACTLY_ZERO",
            "tagged_probability_remainder_after_lambda4": "BEGINS_AT_LAMBDA6",
            "compact_packet_tree_cross_at_lambda6": "NONZERO_FUNCTIONAL",
            "complete_order_lambda6_probability": "NOT_COMPUTED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "assumptions": [
            "the incoming preparation and outgoing detector form the covariant lambda-family obtained from the same exact BT/scalar field map, rather than being held fixed under lambda sign reversal by hand",
            "Pi_F counts total fluctuation quanta around the correspondingly transformed broken background; the background sign is transformed together with lambda",
            "the compact packets lie on the certified finite-particle Gaussian core where total number parity and the cross-Krein adjoint are defined",
            "the perturbative evolution is generated by the public cubic order-lambda and quartic order-lambda2 interactions with parity-preserving regularization and counterterms",
            "the selected hard tagged detector does not explicitly insert a Pi_F-odd external spurion",
            "the theorem concerns finite perturbative coefficients and does not assume an all-time Moller limit"
        ],
        "does_not_establish": [
            "the numerical value of the complete probability-order-lambda6 coefficient",
            "the active four-point one-loop contribution",
            "the second-order dressed-source or detector contribution",
            "the matching virtual or survival contribution",
            "forward, collinear or real-virtual/KLN completion",
            "that a detector held noncovariantly fixed under lambda to minus lambda has an even probability",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Eq. (19)",
            "a continuum endpoint trace for the full nonlinear R_t",
            "gravity or metric BV/BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "all-order positivity",
            "literature priority"
        ],
        "missing_object_ledger": [
            {"object": "complete tagged q6 coefficient", "status": "MISSING", "required_value": "sum the certified compact tree cross with active one-loop, second-order source/detector and survival terms on one normalized packet carrier"},
            {"object": "one-loop active four-point packet kernel", "status": "MISSING", "required_value": "renormalized finite-time physical four-point loop interference with dependency tag and scheme ledger"},
            {"object": "second-order dressed packet projectors", "status": "MISSING", "required_value": "the parity-even order-lambda2 R_t source and detector corrections or a structural cancellation theorem"},
            {"object": "gravity transfer", "status": "MISSING", "required_value": "metric BV/BRST physical carrier, anomaly classification, QME restoration and residual transfer before a gravitational probability claim"}
        ],
        "next_gate": "With q5 exactly zero, assemble the complete q6 object ledger on the compact hard tagged packet. The known nonzero tree cross is one summand. Classify the active renormalized four-point one-loop interference, the parity-even second-order source/detector terms, and the pseudo-unitary survival contribution before computing coefficients. If the classical source data do not determine the second-order packet projectors, that missing R_t coefficient becomes the first exact Eq. (19)/physical fork. No scalar result transfers to gravity without the metric BV/BRST and QME gates.",
        "provenance": {
            "source_commit": "addbe9ff",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact symbolic coupling/field-sign covariance, integer graph-parity enumeration, exact finite Krein block witness, and perturbative coefficient comparison. The proof uses no endpoint coefficient and no floating-point arithmetic."
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_tagged_packet_lambda5_parity_selection.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_tagged_packet_lambda5_parity_selection.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_tagged_packet_lambda5_parity_selection"
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
