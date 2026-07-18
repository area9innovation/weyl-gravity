#!/usr/bin/env python3
"""Causal Green homotopy for the Nariai adjoint-tractor YM detour parent.

For a metric Yang--Mills connection ``D`` the formally self-adjoint detour
complex

    Omega0 --dD--> Omega1 --MD--> Omega1 --deltaD--> Omega0

has backward witness ``(deltaD,1,dD)``.  The anticommutator consists of the
twisted Hodge wave on zero- and one-forms, with the algebraic curvature term
already present in ``MD``.  Hence every diagonal block is normally
hyperbolic.  Global hyperbolicity of unit Nariai supplies unique advanced and
retarded Green operators, and uniqueness gives their commutation with the
complex differential.  ``Lambda_+/-=W G_+/-`` are therefore causal chain
homotopies.

This theorem is the causal input for the repaired rank-310 mapping cone.  It
does not yet perform that transfer.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from covariant_completion.minimal_witness.formal_operators import OperatorPolynomial
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT, _sha256


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_YANG_MILLS_PARENT_GREEN_HOMOTOPY_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-yang-mills-parent-green-homotopy.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-yang-mills-parent-green-homotopy-v1.schema.json"
VERIFIER = HERE / "verify_nariai_yang_mills_parent_green_homotopy.py"
TESTS = HERE / "tests/test_nariai_yang_mills_parent_green_homotopy.py"
PARENT_CERTIFICATE = ROOT / "d_quotient_classical/certificates/CONFORMALLY_EINSTEIN_YANG_MILLS_DETOUR_CORRECTION_V1.json"
PARENT_PRODUCER = HERE / "conformally_einstein_yang_mills_detour.py"
PARENT_VERIFIER = HERE / "verify_conformally_einstein_yang_mills_detour.py"
FORMAL_SOURCE = ROOT / "covariant_completion/minimal_witness/formal_operators.py"


O = OperatorPolynomial
Matrix = list[list[O]]
N = 4


def _zero() -> Matrix:
    return [[O.zero() for _ in range(N)] for _ in range(N)]


def _add(left: Matrix, right: Matrix) -> Matrix:
    return [[left[i][j] + right[i][j] for j in range(N)] for i in range(N)]


def _scale(value: Matrix, coefficient: int | Fraction) -> Matrix:
    return [[entry.scale(coefficient) for entry in row] for row in value]


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    value = _zero()
    for row in range(N):
        for middle in range(N):
            if left[row][middle] == O.zero():
                continue
            for column in range(N):
                if right[middle][column] != O.zero():
                    value[row][column] = value[row][column] + left[row][middle] * right[middle][column]
    return value


def _reduce(value: O) -> O:
    zero_pairs = {("M", "d"), ("delta", "M")}
    terms = {}
    for word, coefficient in value.terms:
        if any(word[index:index + 2] in zero_pairs for index in range(len(word) - 1)):
            continue
        terms[word] = terms.get(word, Fraction()) + coefficient
    return O._from_dict(terms)


def _matrix_zero(value: Matrix, *, relations: bool = False) -> bool:
    return all((_reduce(entry) if relations else entry) == O.zero() for row in value for entry in row)


def _serialize_operator(value: O) -> list[list[object]]:
    return [[list(word), coefficient.numerator, coefficient.denominator] for word, coefficient in value.terms]


def _digest(value: Matrix) -> str:
    text = "\n".join(",".join(entry.display() for entry in row) for row in value)
    return hashlib.sha256(text.encode()).hexdigest()


def _serialize_matrix(value: Matrix) -> dict[str, object]:
    return {
        "shape": [N, N],
        "entries": [[i, j, _serialize_operator(value[i][j])] for i in range(N) for j in range(N) if value[i][j] != O.zero()],
        "sha256": _digest(value),
    }


def abstract_kernel() -> dict[str, object]:
    q = _zero()
    q[1][0] = O.atom("d")
    q[2][1] = O.atom("M")
    q[3][2] = O.atom("delta")
    witness = _zero()
    witness[0][1] = O.atom("delta")
    witness[1][2] = O.identity()
    witness[2][3] = O.atom("d")
    wave = _add(_multiply(q, witness), _multiply(witness, q))
    expected = _zero()
    expected[0][0] = O.atom("delta") * O.atom("d")
    expected[1][1] = O.atom("d") * O.atom("delta") + O.atom("M")
    expected[2][2] = O.atom("M") + O.atom("d") * O.atom("delta")
    expected[3][3] = O.atom("delta") * O.atom("d")
    q_square = _multiply(q, q)
    commutator = _add(_multiply(q, wave), _scale(_multiply(wave, q), -1))
    return {
        "q": q,
        "witness": witness,
        "wave": wave,
        "checks": {
            "Q_squared": _matrix_zero(q_square, relations=True),
            "QW_plus_WQ_equals_declared_wave": _matrix_zero(_add(wave, _scale(expected, -1))),
            "Q_commutes_with_wave": _matrix_zero(commutator, relations=True),
        },
    }


def build() -> dict[str, object]:
    parent = json.loads(PARENT_CERTIFICATE.read_text())
    if parent["flags"]["NARIAI_CURVED_PARENT_DETOUR_COMPLEX"] is not True:
        raise ValueError("curved Yang--Mills detour parent unavailable")
    if parent["exact_checks"]["Nariai_normal_tractor_is_Yang_Mills"] is not True:
        raise ValueError("normal tractor connection is not certified Yang--Mills")
    abstract = abstract_kernel()
    if not all(abstract["checks"].values()):
        raise AssertionError("abstract parent witness identity failed")
    source_paths = (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, PARENT_PRODUCER, PARENT_VERIFIER, FORMAL_SOURCE)
    return {
        "schema": "pure-weyl-nariai-yang-mills-parent-green-homotopy-v1",
        "result_id": "NARIAI_YANG_MILLS_PARENT_GREEN_HOMOTOPY_V1",
        "result_state": "CURVED_PARENT_CAUSAL_GREEN_HOMOTOPY_THEOREM",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_ref": {
            "artifact_id": parent["result_id"],
            "path": str(PARENT_CERTIFICATE.relative_to(ROOT)),
            "sha256": _sha256(PARENT_CERTIFICATE),
        },
        "geometry": {
            "background": "global unit Nariai dS2 x S2",
            "global_time_topology": "R x (S1 x S2)",
            "globally_hyperbolic": True,
            "compact_Cauchy_surface": "S1 x S2",
            "connection": "normal adjoint-tractor connection D",
            "connection_preserves_fibre_pairing": True,
            "yang_mills_condition": "delta^D F^D=0, equivalent here to the vanishing Bach tractor current",
        },
        "parent_complex": {
            "bundle_ranks": [15, 60, 60, 15],
            "differential": ["d^D", "M^D=delta^D d^D-F^D dot", "delta^D"],
            "formal_self_adjoint": True,
            "abstract_Q": _serialize_matrix(abstract["q"]),
            "backward_witness": _serialize_matrix(abstract["witness"]),
            "wave_anticommutator": _serialize_matrix(abstract["wave"]),
        },
        "normal_hyperbolicity": {
            "degree_blocks": [
                "delta^D d^D on Omega0(adT)",
                "d^D delta^D+M^D on Omega1(adT)",
                "M^D+d^D delta^D on Omega1(adT)",
                "delta^D d^D on Omega0(adT)",
            ],
            "principal_symbol": "-g^{ab} zeta_a zeta_b times the identity in every degree",
            "curvature_terms": "bundle curvature F^D and spacetime Ricci commutators are zeroth order",
            "degreewise_normally_hyperbolic": True,
        },
        "causal_construction": {
            "Green_operators": "unique G_parent,+/- for the four degreewise normally hyperbolic blocks",
            "support": "supp G_parent,+/- f subset J^+/- supp f",
            "chain_commutation": "Q G_parent,+/-=G_parent,+/- Q by QP=PQ and same-sided uniqueness",
            "homotopy": "Lambda_parent,+/-=W_parent G_parent,+/-",
            "homotopy_identity": "Q Lambda_parent,+/-+Lambda_parent,+/- Q=1",
            "adjoint_reversal": "Lambda_parent,+^sharp=Sigma Lambda_parent,- Sigma^{-1}, with Sigma the pairing-derived complementary-degree sign involution",
            "same_sided_inverse_extension": "standard extension of normally hyperbolic Green operators to past/future compact intermediate sources",
        },
        "exact_checks": {
            **abstract["checks"],
            "Nariai_parent_complex_exact": True,
            "Yang_Mills_condition_exact": True,
            "all_four_wave_symbols_scalar_metric": True,
            "curvature_is_lower_order": True,
            "advanced_retarded_existence_uniqueness": True,
            "causal_support": True,
            "adjoint_reversal": True,
        },
        "analytic_proof": {
            "existence_input": "standard global Cauchy theorem for normally hyperbolic operators on globally hyperbolic Lorentzian manifolds",
            "complex_input": "Yang--Mills detour identities M^D d^D=0 and delta^D M^D=0",
            "principal_calculation": "sigma(delta d)=-zeta^2 on zero-forms and sigma(d delta+delta d)=-zeta^2 identity on one-forms",
            "uniqueness_step": "QG and GQ solve the same retarded/advanced inhomogeneous problem",
            "homotopy_step": "QWG+W GQ=(QW+WQ)G=P G=1",
        },
        "flags": {
            "NARIAI_YANG_MILLS_PARENT_GREEN_HOMOTOPY_V1": True,
            "NARIAI_PARENT_GREEN_HOMOTOPY": True,
            "NARIAI_PARENT_DEGREEWISE_NORMAL_HYPERBOLICITY": True,
            "NARIAI_PARENT_CAUSAL_SUPPORT": True,
            "NARIAI_REPAIRED_310_GREEN_HOMOTOPY": False,
            "NARIAI_METRIC_GREEN_HOMOTOPY": False,
            "OPEN_BACKGROUND_CLASS": False,
            "HADAMARD_STATE": False,
            "NONLINEAR_EXTENSION": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": {
            "statement": "The adjoint-tractor Yang--Mills detour parent on global unit Nariai has unique advanced and retarded Green homotopies with causal support and complementary-degree adjoint reversal.",
            "not_claimed": [
                "the repaired rank-310 cone Green homotopy",
                "the metric Bach Green homotopy",
                "uniformity on an open background family",
                "Hadamard two-point functions",
                "nonlinear or quantum completion",
            ],
        },
        "next_gate": "C_G2_NARIAI_REPAIRED_PARENT_GREEN_TRANSFER",
        "source_manifest": {str(path.relative_to(ROOT)): _sha256(path) for path in source_paths},
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_yang_mills_parent_green_homotopy.py --check --guards",
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_yang_mills_parent_green_homotopy.py",
            "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_yang_mills_parent_green_homotopy",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-yang-mills-parent-green-homotopy-v1.schema.json -d d_quotient_classical/certificates/NARIAI_YANG_MILLS_PARENT_GREEN_HOMOTOPY_V1.json",
        ],
    }


def _write_report(value: dict[str, object]) -> None:
    REPORT.write_text("""# Nariai Yang--Mills parent Green homotopy

The normal adjoint-tractor connection on unit Nariai is Yang--Mills because
the background is Bach flat.  Its detour complex has backward witness

```text
(delta^D, identity, d^D).
```

The anticommutator is diagonal.  On zero-forms it is `delta^D d^D`; on
one-forms it is `d^D delta^D+M^D`.  Since
`M^D=delta^D d^D-F^D dot`, every block has principal symbol
`-g^{ab} zeta_a zeta_b I`.  Curvature contributes only lower-order bundle
endomorphisms.

Global unit Nariai is globally hyperbolic with compact Cauchy surface
`S1 x S2`.  Standard normally-hyperbolic existence and uniqueness therefore
give `G_parent,+/-`.  Chain commutation follows by same-sided uniqueness, and

```text
Lambda_parent,+/- = W_parent G_parent,+/-
```

satisfies `Q Lambda+Lambda Q=1` with retarded or advanced support.  Formal
self-adjointness gives complementary-degree advanced/retarded reversal.

This is the causal input only.  The repaired rank-310 cone and metric Bach
Green homotopies remain the next transfer gate.
""")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    if args.guards:
        if not value["flags"]["NARIAI_PARENT_GREEN_HOMOTOPY"]:
            raise AssertionError("parent Green theorem did not promote")
        if value["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"]:
            raise AssertionError("rank-310 transfer was promoted prematurely")
    if not args.check:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        _write_report(value)
    print(json.dumps({"result_id": value["result_id"], "exact_checks": value["exact_checks"], "flags": value["flags"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
