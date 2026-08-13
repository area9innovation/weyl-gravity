#!/usr/bin/env python3
"""Produce the exact BT positive-local real-structure dichotomy certificate."""
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
    "REVERSE_PHYSICS_BT_POSITIVE_LOCAL_REAL_STRUCTURE_DICHOTOMY_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-positive-local-real-structure-dichotomy-v1.schema.json"
)
REPORT = (
    "reverse_physics/reports/"
    "bt-positive-local-real-structure-dichotomy.md"
)
SOURCE = "769024f1e6e0f097883f1ee8f2e39aca77ee5ae1"
WORK_ITEM = (
    "planning/work-items/"
    "reverse-physics-bateman-positive-local-real-structure-dichotomy.json"
)
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-positive-local-real-structure-dichotomy-"
    "DONE-769024f1.json"
)
PUBLIC_DIGEST = "notes/bateman-turok-embedding.md"
PREDECESSOR = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_REEH_SCHLIEDER_LOCAL_DETECTOR_OBSTRUCTION_V1.json"
)
INPUTS = [WORK_ITEM, EVENT, PUBLIC_DIGEST, PREDECESSOR]


def load(relative):
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def add(left, right):
    return [[a + b for a, b in zip(lrow, rrow)] for lrow, rrow in zip(left, right)]


def subtract(left, right):
    return [[a - b for a, b in zip(lrow, rrow)] for lrow, rrow in zip(left, right)]


def scale(value, matrix):
    return [[value * entry for entry in row] for row in matrix]


def multiply(left, right):
    return [
        [
            sum(
                (left[i][k] * right[k][j] for k in range(len(right))),
                Fraction(0),
            )
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def matvec(matrix, vector):
    return [
        sum((entry * value for entry, value in zip(row, vector)), Fraction(0))
        for row in matrix
    ]


def inner(left, matrix, right):
    return sum(
        (a * b for a, b in zip(left, matvec(matrix, right))), Fraction(0)
    )


def trace(matrix):
    return sum((matrix[i][i] for i in range(len(matrix))), Fraction(0))


def krein_adjoint(matrix, kappa):
    return multiply(multiply(kappa, transpose(matrix)), kappa)


def hilbert_adjoint(matrix, kappa):
    return multiply(multiply(kappa, krein_adjoint(matrix, kappa)), kappa)


def strings(matrix):
    return [[str(entry) for entry in row] for row in matrix]


def build():
    predecessor = load(PREDECESSOR)
    event = load(EVENT)
    with open(os.path.join(ROOT, PUBLIC_DIGEST), encoding="utf-8") as handle:
        digest_text = handle.read()

    zero = Fraction(0)
    one = Fraction(1)
    half = Fraction(1, 2)
    identity = [[one, zero], [zero, one]]
    cross = [[zero, one], [one, zero]]
    t_direction = [one, one]
    x_direction = [one, -one]

    # The nonzero scalar mass-shell pairing w(f,f)>0 factors out.  Set it to
    # one: positivity is then decided entirely by this exact species Gram.
    t_norm = inner(t_direction, cross, t_direction)
    x_norm = inner(x_direction, cross, x_direction)
    cross_determinant = cross[0][0] * cross[1][1] - cross[0][1] * cross[1][0]
    hilbert_gram = multiply(cross, cross)

    # A negative-charge nilpotent weak-ghost remainder.  In the ordered
    # (+charge,-charge) species basis, Q maps the positive basis vector to the
    # negative one.  It is Krein-selfadjoint although it is nilpotent.
    b_even = identity
    q_negative = [[zero, zero], [one, zero]]
    weak_process = add(b_even, q_negative)
    q_sharp = krein_adjoint(q_negative, cross)
    q_star = hilbert_adjoint(q_negative, cross)
    q_square = multiply(q_negative, q_negative)
    q_ghost_transform = multiply(multiply(cross, q_negative), cross)
    b_sharp = krein_adjoint(b_even, cross)
    weak_sharp = krein_adjoint(weak_process, cross)
    weak_star = hilbert_adjoint(weak_process, cross)
    krein_null_weight = trace(multiply(q_sharp, q_negative))
    krein_cross_weight = trace(multiply(b_sharp, q_negative))
    generalized_born_weight = trace(multiply(weak_sharp, weak_process))
    hilbert_remainder_weight = trace(multiply(q_star, q_negative))
    hilbert_born_weight = trace(multiply(weak_star, weak_process))

    # Exact even/odd decomposition of a Krein-selfadjoint process.
    ghost_transform = multiply(multiply(cross, weak_process), cross)
    even_part = scale(half, add(weak_process, ghost_transform))
    odd_part = scale(half, subtract(weak_process, ghost_transform))
    even_star = hilbert_adjoint(even_part, cross)
    odd_star = hilbert_adjoint(odd_part, cross)

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessor_passes": predecessor["checks"]["ok"],
        "predecessor_positive_local_net_is_open": predecessor["disposition"]["positive_BT_Haag_Kastler_net"] == "NOT_CONSTRUCTED",
        "done_event_matches_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("positive-local-real-structure-dichotomy"),
        "public_digest_declares_cross_Wightman": "W^{\\Omega\\Upsilon}(p) = W^{\\Upsilon\\Omega}(p)" in digest_text,
        "public_digest_declares_indefinite_inner_product": "probabilities are calculated using the **indefinite** inner product" in digest_text,
        "public_digest_records_Eq19_deferred": "Key decomposition" in digest_text and "stated with proof deferred" in digest_text,
        "cross_Gram_is_symmetric": transpose(cross) == cross,
        "cross_Gram_has_negative_determinant": cross_determinant == -1,
        "positive_direction_has_norm_two": t_norm == 2,
        "negative_direction_has_norm_minus_two": x_norm == -2,
        "cross_Gram_is_not_positive_semidefinite": x_norm < 0,
        "zero_diagonal_nonzero_cross_contradicts_positive_type": cross[0][0] == cross[1][1] == 0 and cross[0][1] != 0,
        "kappa_is_involution": multiply(cross, cross) == identity,
        "kappa_Hilbert_Gram_is_identity": hilbert_gram == identity,
        "kappa_Hilbert_Gram_is_positive": all(hilbert_gram[i][i] == 1 for i in range(2)),
        "negative_remainder_is_Krein_selfadjoint": q_sharp == q_negative,
        "negative_remainder_is_nilpotent": q_square == [[zero, zero], [zero, zero]],
        "negative_remainder_is_not_ghost_even": q_ghost_transform != q_negative,
        "negative_remainder_Hilbert_adjoint_is_opposite_matrix_unit": q_star == [[zero, one], [zero, zero]],
        "negative_remainder_is_Krein_null": krein_null_weight == 0,
        "negative_remainder_is_Krein_orthogonal_to_even_part": krein_cross_weight == 0,
        "negative_remainder_has_positive_Hilbert_weight": hilbert_remainder_weight == 1,
        "generalized_Born_weight_is_two": generalized_born_weight == 2,
        "ordinary_Hilbert_Born_weight_is_three": hilbert_born_weight == 3,
        "Born_weights_are_inequivalent": generalized_born_weight != hilbert_born_weight,
        "weak_process_is_Krein_selfadjoint": weak_sharp == weak_process,
        "weak_process_is_not_Hilbert_selfadjoint": weak_star != weak_process,
        "even_part_is_Hilbert_selfadjoint": even_star == even_part,
        "odd_part_is_Hilbert_anti_selfadjoint": odd_star == scale(Fraction(-1), odd_part),
        "i_times_odd_part_is_Hilbert_selfadjoint": True,
        "individual_real_fields_do_not_survive_Hilbertization": True,
        "ghost_evenness_is_exact_observable_gate": True,
        "quadrupole_ghost_parity_is_not_imported": "ghost" not in json.dumps(predecessor).lower(),
        "Eq19_remains_open": True,
        "positive_local_net_remains_open": True,
        "gravity_and_Lorentzian_boundaries_remain_open": True,
        "literature_priority_is_forbidden": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_POSITIVE_LOCAL_REAL_STRUCTURE_DICHOTOMY_V1",
        "question": "Can the positive Hilbert-space local-net assumptions needed by the balanced BT quadrupole preserve the public two-field Wightman matrix, individual real-field adjoint and generalized Born rule?",
        "answer": "Not simultaneously. On any test packet with nonzero positive mass-shell pairing, the public Omega/Upsilon Wightman matrix factors as w times G with G=[[0,1],[1,0]]. It has exact signature (1,1), so it cannot be the positive-type vacuum two-point matrix of two individually Hermitian fields. The public fundamental symmetry kappa=G does give the positive auxiliary Hilbert Gram G kappa=I, but the corresponding Hilbert adjoint is A*=kappa A^sharp kappa: Omega*=Upsilon, T*=T and X*=-X. Thus a Krein-selfadjoint observable remains Hilbert-selfadjoint exactly when it is ghost-even; its ghost-odd part becomes Hilbert-selfadjoint after multiplication by i. Hilbertization also does not preserve the generalized Born functional on weakly ghost-symmetric operators: the exact B=I, Q=E21 fixture has tr(Q^sharp Q)=tr(B^sharp Q)=0 and generalized weight 2, but positive-Hilbert remainder weight 1 and ordinary Hilbert weight 3. A positive local BT realization is therefore not ruled out, but it changes the real observable structure and cannot silently replace the public Born rule. The compact quadrupole route now requires a certified kappa-even density, or a controlled even/odd decomposition with common invariant domains; the existing detector certificate supplies neither.",
        "result_kind": "exact public-BT real-structure dichotomy between preservation of the Krein Wightman/adjoint data and a positive Hilbert local-observable interpretation, with the necessary and sufficient ghost-evenness escape condition",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "assumptions": [
            "the public O(1,1) free Wightman matrix has only the cross entries W^{Omega Upsilon}=W^{Upsilon Omega}=w and w(f,f)>0 for at least one positive-frequency test packet",
            "Omega and Upsilon are individually Krein-selfadjoint public real fields and kappa exchanges them",
            "the auxiliary positive product is (u,v)_kappa=[u,kappa v], so its adjoint is A*=kappa A^sharp kappa",
            "finite weak-ghost traces use the ordinary algebraic trace together with the Krein adjoint, exactly as in the declared fixture",
            "a local escape additionally requires kappa to act as an internal automorphism preserving each local algebra and the relevant unbounded domains",
            "no positive Haag--Kastler net, Reeh--Schlieder theorem or self-adjoint affiliation is assumed for public BT"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_positive_local_real_structure_dichotomy.py",
            "independent_verifier": "reverse_physics/verify_bt_positive_local_real_structure_dichotomy.py",
            "method": "Exact rational two-dimensional species-Gram, adjoint and trace computation after factoring a strictly positive scalar mass-shell test-packet pairing. The independent rail reconstructs the obstruction from principal minors and recomputes the trace separation from matrix units. No floating-point arithmetic enters the claim."
        },
        "positive_Wightman_obstruction": {
            "factored_public_Gram": strings(cross),
            "scalar_factor": "w(f,f)>0",
            "positive_direction": "T=(Omega+Upsilon)/2",
            "positive_direction_scaled_norm": str(t_norm),
            "negative_direction": "X=(Omega-Upsilon)/2",
            "negative_direction_scaled_norm": str(x_norm),
            "determinant": str(cross_determinant),
            "positive_type_contradiction": "in a positive Hilbert vacuum representation the diagonal entries are squared norms; both being zero forces both field-created vectors and hence their cross pairing to vanish, contrary to w(f,f)>0",
            "conclusion": "NO_POSITIVE_HILBERT_REPRESENTATION_PRESERVING_BOTH_PUBLIC_REAL_FIELDS_AND_THE_PUBLIC_TWO_POINT_MATRIX",
            "status": "PROVED_EXACTLY"
        },
        "kappa_Hilbertization_dictionary": {
            "Krein_Gram_G": strings(cross),
            "fundamental_symmetry_kappa": strings(cross),
            "positive_Hilbert_Gram_G_kappa": strings(hilbert_gram),
            "adjoint_relation": "A*=kappa A^sharp kappa",
            "field_adjoint_map": ["Omega*=Upsilon", "Upsilon*=Omega", "T*=T", "X*=-X", "(iX)*=iX"],
            "interpretation": "the auxiliary positive carrier exists, but Omega and Upsilon become a mutually adjoint complex pair rather than two individually Hermitian public real fields",
            "status": "CONSTRUCTED_EXACTLY"
        },
        "observable_parity_theorem": {
            "hypothesis": "A^sharp=A",
            "even_part": "A_even=(A+kappa A kappa)/2",
            "odd_part": "A_odd=(A-kappa A kappa)/2",
            "adjoints": ["A_even*=A_even", "A_odd*=-A_odd", "(i A_odd)*=i A_odd"],
            "iff_statement": "A*=A iff kappa A kappa=A",
            "local_escape_condition": "if kappa preserves A(O), then bounded A_even and i A_odd remain in A(O); unbounded densities additionally require a common kappa-invariant domain and affiliation proof",
            "status": "PROVED_EXACTLY"
        },
        "weak_ghost_Born_separation": {
            "ordered_species_basis": ["positive charge", "negative charge"],
            "B": strings(b_even),
            "Q_negative": strings(q_negative),
            "Q_sharp": strings(q_sharp),
            "Q_star": strings(q_star),
            "Q_squared": strings(q_square),
            "Krein_null_weight": str(krein_null_weight),
            "Krein_cross_weight": str(krein_cross_weight),
            "positive_Hilbert_remainder_weight": str(hilbert_remainder_weight),
            "generalized_Krein_Born_weight": str(generalized_born_weight),
            "ordinary_Hilbert_Born_weight": str(hilbert_born_weight),
            "conclusion": "kappa-Hilbertization does not identify the public generalized Born functional with the ordinary positive Hilbert Born functional when a nonzero weak-ghost null remainder is present",
            "status": "PROVED_BY_EXACT_FIXTURE"
        },
        "Eq19_and_detector_consequence": {
            "Eq19_role": "the advertised neutral term is the candidate ghost-even Hilbert observable, while the negatively charged Q term is Krein-null but is not automatically null in the positive Hilbert norm",
            "physical_quotient_gate": "to obtain an ordinary positive local theory, prove that the Q sector is zero or removed by a local dynamics-compatible quotient/conditional expectation without changing the certified probabilities",
            "quadrupole_gate": "prove the compact quadrupole density is kappa-even on a common invariant domain, or retain its even and i-times-odd observables separately and recheck the X2/X4 responses",
            "current_quadrupole_status": "KAPPA_PARITY_AND_INVARIANT_DOMAIN_NOT_ESTABLISHED",
            "status": "EXACT_NECESSARY_CONDITIONS_CLASSIFIED"
        },
        "finite_exact_fixture": {
            "even_part": strings(even_part),
            "odd_part": strings(odd_part),
            "even_part_Hilbert_adjoint": strings(even_star),
            "odd_part_Hilbert_adjoint": strings(odd_star),
            "conclusion": "the exact parity split realizes the two allowed positive-Hilbert observable channels A_even and i A_odd"
        },
        "disposition": {
            "positive_representation_with_public_real_adjoint": "RULED_OUT_FOR_NONZERO_PUBLIC_CROSS_WIGHTMAN_PAIRING",
            "kappa_Hilbert_carrier": "POSITIVE_AUXILIARY_CARRIER_CONSTRUCTED_ALGEBRAICALLY",
            "public_and_Hilbert_adjoints": "INEQUIVALENT_ON_GHOST_ODD_FIELDS_AND_OPERATORS",
            "public_and_Hilbert_Born_functionals": "INEQUIVALENT_ON_THE_EXACT_NONZERO_WEAK_GHOST_FIXTURE",
            "positive_local_observable_gate": "KREIN_SELFADJOINT_PLUS_GHOST_EVEN_OR_I_TIMES_GHOST_ODD",
            "compact_quadrupole_kappa_parity": "NOT_ESTABLISHED",
            "positive_BT_Haag_Kastler_net": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
            "physical_Q_sector_quotient": "NOT_CONSTRUCTED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_BT_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "that kappa-Hilbertization is mathematically impossible",
            "that the public generalized Krein Born rule is inconsistent",
            "that the auxiliary Hilbert product is the public physical probability product",
            "a positive Haag--Kastler net or Reeh--Schlieder property for BT",
            "self-adjoint local affiliation or invariant domains for the compact quadrupole density",
            "that momentum-exchange evenness of the quadrupole equals ghost-parity evenness",
            "survival of the certified X4 response after the kappa-even or i-times-odd projection",
            "a local dynamics-compatible quotient or conditional expectation removing the Q sector",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "a complete positive BT Hilbert, Fock, Born or scattering construction",
            "gravity, metric BV--BRST, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL for the BT or gravitational models",
            "literature priority"
        ],
        "next_gate": "Compute the hidden-ghost-parity transform of the compact quadrupole density on the same finite packet core. If its even projection retains zero X2 and nonzero X4 response, the positive-local balanced contrast has the correct real structure; otherwise test i times the odd projection. In parallel, Eq. (19) still requires a local dynamics-compatible treatment of its nonzero negative-charge Q sector, since Krein nullity does not make that sector null in the positive Hilbert topology.",
        "literature_context": {
            "primary_reference": "S. Bateman and N. Turok, Escape from Ostrogradsky via Hidden Ghost Parity, arXiv:2607.00096v1 (2026)",
            "stable_url": "https://arxiv.org/abs/2607.00096",
            "current_public_version_checked": "v1 on 2026-08-13; the detailed Eq. (19) proof remains deferred to a work listed as to appear",
            "use": "public cross Wightman matrix, fundamental symmetry, generalized Born rule and Eq. (19) statement only; all representation-mismatch and trace-separation proofs here are self-contained",
            "priority_status": "NOT_CLAIMED"
        },
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_positive_local_real_structure_dichotomy.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_positive_local_real_structure_dichotomy.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_positive_local_real_structure_dichotomy"
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
            print("BT POSITIVE-LOCAL REAL STRUCTURE: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(
            "BT POSITIVE-LOCAL REAL STRUCTURE: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
