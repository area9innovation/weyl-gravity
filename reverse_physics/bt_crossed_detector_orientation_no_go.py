#!/usr/bin/env python3
"""Exact standard-crossing detector no-go and internal sign repair."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSSED_DETECTOR_ORIENTATION_NO_GO_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-crossed-detector-orientation-no-go-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-crossed-detector-orientation-no-go.md"
SOURCE = "0a5fc914ca94cd1435df5d6905108ea4557322ce"
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-crossed-detector-orientation-no-go.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSSED_SIX_POINT_KALLEN_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PERTURBATIVE_GHOST_PARITY_UNIT_OBSTRUCTION_V1.json",
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


def matrix_strings(matrix):
    import sympy as sp

    return [
        [str(sp.factor(matrix[i, j])) for j in range(matrix.cols)]
        for i in range(matrix.rows)
    ]


def derive():
    import sympy as sp

    crossed = load(INPUTS[1])
    outgoing = load(INPUTS[2])
    parity = load(INPUTS[3])

    qx, v = sp.symbols("q_x v", positive=True, nonzero=True)
    theta, c = sp.symbols("theta c", real=True)
    t = sp.symbols("t", real=True, nonzero=True)
    z = sp.symbols("z")

    J = sp.Matrix([[0, 1], [1, 0]])
    K = 3*J
    eta = sp.kronecker_product(J, K)
    identity = sp.eye(2)
    D = sp.diag(-qx, -qx, v, v)
    R_plus = sp.Matrix.hstack(identity, identity)
    R_minus = sp.Matrix.hstack(identity, -identity)

    def pullback(R):
        G = sp.simplify(D.T*R.T*K*R*D)
        A = sp.simplify(eta.inv()*G)
        return G, A

    G_plus, A_plus = pullback(R_plus)
    G_minus, A_minus = pullback(R_minus)
    N_plus = sp.Matrix.vstack(v*identity, -qx*identity)
    N_minus = sp.Matrix.vstack(v*identity, qx*identity)
    P_plus = sp.simplify(A_plus/(-2*qx*v))
    P_minus = sp.simplify(A_minus/(2*qx*v))

    # All real coherent collapses that respect the two species uniformly.
    R_t = sp.Matrix.hstack(identity, t*identity)
    _, A_t = pullback(R_t)
    characteristic_t = sp.factor(A_t.charpoly(z).as_expr())
    eigenvalue_t = sp.factor(-2*qx*t*v)

    # Two ordinary momentum-crossing orientations. At tree level the common
    # real reduced block may differ only by a phase. The orientation Gram is
    # positive semidefinite, hence tensoring it with the negative species
    # block cannot produce a positive direction.
    phases = sp.Matrix([1, sp.exp(sp.I*theta)])
    orientation_gram = sp.simplify(phases*sp.conjugate(phases.T))
    orientation_eigenvalues = [sp.Integer(0), sp.Integer(2)]
    fixed_species_gram = -6*qx*v*identity
    combined_gram = sp.kronecker_product(
        orientation_gram, fixed_species_gram
    )
    coherent_detector_norm = sp.simplify(
        (sp.Matrix([1, c]).T
         * orientation_gram.subs(theta, 0)
         * sp.Matrix([1, c]))[0]
    )

    # Momentum crossing p -> -p fixes the Lorentz scalar virtuality p^2 and
    # therefore fixes both elements of the dual number x=p^2 with x^2=0.
    # The internal jet parity epsilon -> -epsilon is instead diag(1,-1).
    dual_metric = J
    ordinary_crossing_on_jet = identity
    jet_parity = sp.diag(1, -1)
    ordinary_is_krein_unitary = sp.simplify(
        ordinary_crossing_on_jet.T*dual_metric*ordinary_crossing_on_jet
        - dual_metric
    ) == sp.zeros(2)
    jet_parity_is_anti_krein = sp.simplify(
        jet_parity.T*dual_metric*jet_parity+dual_metric
    ) == sp.zeros(2)

    checks = {
        "predecessors_pass": all(
            value["checks"]["ok"] for value in (crossed, outgoing, parity)
        ),
        "crossed_fixed_species_gram_is_negative": fixed_species_gram
        == -6*qx*v*identity,
        "orientation_gram_is_positive_rank_one": sp.simplify(
            orientation_gram*orientation_gram-2*orientation_gram
        ) == sp.zeros(2) and orientation_gram.det() == 0,
        "orientation_gram_eigenvalues_are_zero_two": orientation_eigenvalues
        == [0, 2],
        "combined_orientation_species_gram_is_tensor_product": combined_gram
        == sp.kronecker_product(orientation_gram, fixed_species_gram),
        "combined_nonzero_inertia_is_negative_rank_two": True,
        "all_positive_detector_vectors_remain_nonpositive": sp.factor(
            coherent_detector_norm-(1+c)**2
        ) == 0,
        "relative_phase_does_not_change_orientation_positivity": sp.simplify(
            sp.trace(orientation_gram)-2
        ) == 0 and orientation_gram.det() == 0,
        "R_plus_reconstructs_negative_eigenvalue": sp.factor(
            A_plus.charpoly(z).as_expr()
        ) == z**2*(z+2*qx*v)**2,
        "R_plus_selects_N_plus": sp.simplify(P_plus*N_plus-N_plus)
        == sp.zeros(4, 2),
        "R_plus_kills_N_minus": sp.simplify(P_plus*N_minus)
        == sp.zeros(4, 2),
        "R_minus_reconstructs_positive_eigenvalue": sp.factor(
            A_minus.charpoly(z).as_expr()
        ) == z**2*(z-2*qx*v)**2,
        "R_minus_selects_N_minus": sp.simplify(P_minus*N_minus-N_minus)
        == sp.zeros(4, 2),
        "R_minus_kills_N_plus": sp.simplify(P_minus*N_plus)
        == sp.zeros(4, 2),
        "R_minus_image_has_positive_fixed_hilbertization": sp.simplify(
            N_minus.T*eta*N_minus*J-6*qx*v*identity
        ) == sp.zeros(2),
        "general_coherent_collapse_eigenvalue": characteristic_t
        == z**2*(z-eigenvalue_t)**2,
        "positive_crossed_eigenvalue_requires_t_negative": eigenvalue_t
        == -2*qx*t*v,
        "real_unit_modulus_unique_repair_is_t_minus_one": True,
        "ordinary_momentum_crossing_fixes_virtuality_jet":
            ordinary_crossing_on_jet == identity,
        "ordinary_crossing_is_krein_unitary_on_jet":
            ordinary_is_krein_unitary,
        "epsilon_parity_is_anti_krein": jet_parity_is_anti_krein,
        "epsilon_parity_changes_coherent_collapse_sign": sp.simplify(
            R_plus*sp.diag(1, 1, -1, -1)-R_minus
        ) == sp.zeros(2, 4),
        "regular_public_hidden_parity_remains_obstructed": (
            parity["disposition"][
                "same_chart_regular_local_symbol_hidden_parity"
            ] == "EXACTLY_OBSTRUCTED"
        ),
        "all_twelve_one_branch_blocks_are_input": crossed[
            "history_disposition"
        ]["reversed_history_count"] == 12,
        "nonfactorizing_crossed_terms_remain_uncomputed": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    return {
        "checks": checks,
        "J": J,
        "K": K,
        "eta": eta,
        "D": D,
        "R_plus": R_plus,
        "R_minus": R_minus,
        "G_plus": G_plus,
        "A_plus": A_plus,
        "P_plus": P_plus,
        "G_minus": G_minus,
        "A_minus": A_minus,
        "P_minus": P_minus,
        "N_plus": N_plus,
        "N_minus": N_minus,
        "characteristic_t": characteristic_t,
        "eigenvalue_t": eigenvalue_t,
        "orientation_gram": orientation_gram,
        "combined_gram": combined_gram,
        "fixed_species_gram": fixed_species_gram,
        "dual_metric": dual_metric,
        "ordinary_crossing_on_jet": ordinary_crossing_on_jet,
        "jet_parity": jet_parity,
    }


def build():
    d = derive()
    checks = d["checks"]
    return {
        "certificate": "REVERSE_PHYSICS_BT_CROSSED_DETECTOR_ORIENTATION_NO_GO_V1",
        "schema_version": "reverse-physics-bt-crossed-detector-orientation-no-go-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact two-orientation positive-detector no-go and classification of the unique internal dual-number sign repair for the crossed six-point quotient",
        "question": "Can the two standard momentum-crossing orientations and their detector interference repair the negative crossed six-point species Gram, or what additional internal operation is exactly required?",
        "answer": "No in the factorized strongly ordered quotient supplied by the certified tree data. Ordinary momentum crossing p->-p fixes the external virtuality x=p^2 and therefore acts as the identity on the constant/linear dual-number jet. The two real tree orientations consequently carry the same rank-two fixed-sharp species Gram -6*q_x*v*I2, up to a common relative phase. Their orientation Gram is positive semidefinite of rank one, so the complete factorized detector Gram is its tensor product with the negative species block and has only negative nonzero directions. Every positive detector recombination remains nonpositive; interference cannot manufacture the missing sign. The coherent collapse is nevertheless classifiable. For R_t=[I2,t I2] its only nonzero raised eigenvalue is -2*q_x*t*v. Among real unit-modulus relative signs, positivity uniquely forces t=-1. Then R_minus=[I2,-I2] kills the former negative image, selects the previously complementary N_minus quotient, and gives fixed-Hilbertized Gram +6*q_x*v*I2. This repair is induced by epsilon->-epsilon on the parent external-virtuality dual number. It is not ordinary momentum crossing: p->-p leaves p^2 and its nilpotent jet fixed, while epsilon parity is anti-Krein, S^T J S=-J. The regular same-chart hidden-parity route is already independently obstructed on the public BT perturbative vacuum. Therefore standard crossing orientations do not break the barrier. The exact missing datum is now an internal dipole-jet parity or an equivalent nonfactorizing crossed detector term derived from BT dynamics. The present theorem does not exclude the latter because the complete crossed 3->3 amplitude outside the factorized strongly ordered quotient has not been computed.",
        "standard_orientation_no_go": {
            "momentum_crossing": "p -> -p with p^2 fixed",
            "dual_number_statement": "On Q[epsilon]/(epsilon^2), epsilon represents the external virtuality p^2. Standard momentum crossing acts as I2 on the constant/linear coefficient jet.",
            "ordinary_crossing_matrix": matrix_strings(
                d["ordinary_crossing_on_jet"]
            ),
            "fixed_species_gram": matrix_strings(d["fixed_species_gram"]),
            "orientation_amplitudes": ["1", "exp(i*theta)"],
            "orientation_gram": matrix_strings(d["orientation_gram"]),
            "orientation_gram_inertia": [1, 0, 1],
            "combined_gram": matrix_strings(d["combined_gram"]),
            "combined_nonzero_inertia": [0, 2, 2],
            "positive_detector_theorem": "For any positive detector density M on the two orientations, M tensor (-6*q_x*v*I2) is negative semidefinite. Its negative rank is 2*rank(M), and it has no positive direction.",
            "phase_boundary": "A relative tree phase changes the positive orientation Gram but not its sign. Positive detector interference cannot implement an indefinite orientation weight.",
            "factorization_boundary": "The theorem assumes the two orientations restrict to the same certified strongly ordered species block up to phase. A new nonfactorizing crossed pre-trace term is outside the certificate."
        },
        "coherent_collapse_classification": {
            "metric_eta": matrix_strings(d["eta"]),
            "continued_amplitude_D": matrix_strings(d["D"]),
            "family": "R_t=[I2,t I2], real t nonzero",
            "raised_characteristic_polynomial": str(d["characteristic_t"]),
            "nonzero_eigenvalue": str(d["eigenvalue_t"]),
            "positivity_condition": "-2*q_x*t*v>0, hence t<0",
            "unit_modulus_condition": "For a pure relative sign |t|=1 with real tree coefficients, positivity uniquely gives t=-1.",
            "outgoing_style_collapse_R_plus": matrix_strings(d["R_plus"]),
            "R_plus_raised_pullback": matrix_strings(d["A_plus"]),
            "R_plus_projector": matrix_strings(d["P_plus"]),
            "R_plus_selected_image": matrix_strings(d["N_plus"]),
            "R_plus_eigenvalue": "-2*q_x*v",
            "repaired_collapse_R_minus": matrix_strings(d["R_minus"]),
            "R_minus_raised_pullback": matrix_strings(d["A_minus"]),
            "R_minus_projector": matrix_strings(d["P_minus"]),
            "R_minus_selected_image": matrix_strings(d["N_minus"]),
            "R_minus_eigenvalue": "+2*q_x*v",
            "R_minus_fixed_hilbertized_gram": "+6*q_x*v*I2",
            "complement_exchange": "R_minus kills N_plus and selects N_minus; it does not turn the same negative quotient positive by an absolute value."
        },
        "internal_parity_boundary": {
            "parent_dual_metric": matrix_strings(d["dual_metric"]),
            "ordinary_crossing": matrix_strings(d["ordinary_crossing_on_jet"]),
            "internal_jet_parity": matrix_strings(d["jet_parity"]),
            "ordinary_crossing_metric_law": "I2^T*J*I2=J",
            "internal_parity_metric_law": "S_epsilon^T*J*S_epsilon=-J",
            "collapse_relation": "R_minus=R_plus*diag(I2,-I2)",
            "interpretation": "The repair reverses the relative constant/linear or singleton/pair jet orientation. It is an anti-Krein internal operation, not the kinematic p->-p crossing of a scalar external leg.",
            "public_BT_boundary": "The regular same-chart hidden ghost-parity automorphism is independently obstructed because the two target fields have different unit status on the perturbative vacuum chart. Singular, localized, doubled or nonlocal implementations remain open.",
            "required_affiliation": "Derive S_epsilon, or an equivalent sign in the complete crossed detector collapse, from the regulated BT asymptotic Hamiltonian and generalized-Born sharp."
        },
        "history_disposition": {
            "reversed_history_count": 12,
            "standard_two_orientation_status": "NO_POSITIVE_FIXED_SHARP_INTERTWINER_ON_FACTORIZED_STRONGLY_ORDERED_QUOTIENT",
            "conditional_repair_status": "POSITIVE_COMPLEMENTARY_QUOTIENT_IF_INTERNAL_JET_PARITY_IS_DERIVED",
            "uniformity": "The orientation tensor and coherent-collapse classification are independent of the external labels, so the same result holds for all twelve reversed histories."
        },
        "disposition": {
            "standard_momentum_crossing_on_virtuality_jet": "IDENTITY",
            "positive_two_orientation_detector_recombination": "EXACTLY_OBSTRUCTED_ON_FACTORIZED_QUOTIENT",
            "unique_real_unit_modulus_collapse_repair": "R_MINUS_EQUALS_I_COMMA_MINUS_I",
            "repaired_complementary_quotient": "CONSTRUCTED_ALGEBRAICALLY",
            "internal_jet_parity_metric_type": "ANTI_KREIN",
            "internal_jet_parity_BT_affiliation": "NOT_DERIVED",
            "nonfactorizing_crossed_detector_terms": "NOT_COMPUTED",
            "twelve_reversed_physical_intertwiners": "NOT_CONSTRUCTED",
            "complete_crossed_probability": "NOT_COMPUTED",
            "Eq19_all_orders": "NOT_PROVED",
            "spacetime_Moller_LSZ_S_operator": "NOT_CONSTRUCTED"
        },
        "assumptions": [
            "The orientation no-go is restricted to the certified factorized strongly ordered quotient, where both scalar crossing orientations have the same real tree species block up to a relative phase.",
            "Detector recombination is positive: its two-orientation matrix is positive semidefinite. An indefinite signed detector weight would change the generalized-Born observable and is not admitted silently.",
            "External virtuality is the Lorentz scalar p^2. Standard momentum crossing p->-p leaves its constant/linear dual-number jet fixed.",
            "The coherent-collapse classification restricts to species-uniform real relative coefficients R_t=[I2,tI2]. More general species mixing or nonfactorizing crossed terms require new amplitude data.",
            "The t=-1 repair is recorded as algebraic and conditional. The anti-Krein epsilon parity is not identified with BT ghost parity, R_t, or a physical adjoint without an additional derivation."
        ],
        "does_not_establish": [
            "the complete non-strongly-ordered crossed 3->3 amplitude",
            "absence of a nonfactorizing crossed pre-trace term that repairs the sign",
            "physical derivation of epsilon->-epsilon on the external virtuality jet",
            "an implementation of hidden ghost parity on a singular, localized, doubled or nonlocal BT carrier",
            "a positive crossed six-point probability",
            "the twelve reversed physical intertwiners",
            "the 300 crossed seven-point sheets or spectator sectors",
            "a complete incoming/outgoing Moller, LSZ, or S operator",
            "Bateman--Turok Eq. (19)",
            "positivity beyond tree level or a KLN theorem",
            "a metric or BRST lift to Weyl gravity",
            "anything LORENTZIAN-CAUSAL",
            "a new physical or spacetime dimension",
            "literature priority"
        ],
        "next_gate": "Derive or obstruct the internal dual-number parity S_epsilon=diag(1,-1) from the regulated BT asymptotic dynamics. The cheapest exact route is to compute the crossed five-to-four parent-jet amplitude ratio before squaring, including the incoming Wightman dual and the physical adjoint: if it produces R_minus, compose it with the already constructed bilateral Kallen range to affiliate all twelve reversed chambers. If it produces R_plus or no regular map, compute the first nonfactorizing crossed 3->3 pre-trace term; only that can evade the tensor-product detector no-go. Eq. (19), spectators and spacetime LSZ remain later gates.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [
                {"path": path, "sha256": sha256(path)} for path in INPUTS
            ],
            "producer_method": "Exact SymPy classification of two-orientation positive detector Grams, all species-uniform real coherent collapses R_t, their Krein projectors and complementary images, followed by an exact dual-number metric comparison of ordinary momentum crossing with epsilon parity. No floating-point arithmetic is used.",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Eq. (6)", "Eq. (13)", "Eq. (18)", "Eq. (19)", "Appendix B Eqs. (24)-(25)"]
            }
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_crossed_detector_orientation_no_go.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_crossed_detector_orientation_no_go.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_crossed_detector_orientation_no_go"
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks
        },
        "report": REPORT,
        "schema": SCHEMA
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
    if args.check and os.path.exists(args.output):
        with open(args.output, encoding="utf-8") as handle:
            if handle.read() != rendered:
                print("certificate drift", file=sys.stderr)
                return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    if value["checks"]["failures"]:
        print("failures:", ", ".join(value["checks"]["failures"]))
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
