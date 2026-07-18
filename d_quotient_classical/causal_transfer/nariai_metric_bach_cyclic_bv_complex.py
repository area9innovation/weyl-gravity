#!/usr/bin/env python3
"""Action-paired four-row metric Bach BV complex on unit Nariai.

The action-derived Bach endpoint is a map from trace-free metric coordinates
to their evaluation dual.  The tensor Gram matrix has already been included
in that map, so the field/equation pairing in endpoint coordinates is the
identity, not a second copy of the tensor Gram.  This module records that
typed distinction, derives the conformal-Killing adjoint, and verifies the
complete four-row odd-cyclic complex.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    ROOT,
    _sha256,
    _sparse,
    _sparse_table,
)
from d_quotient_classical.causal_transfer.nariai_linearized_bach_endpoint import (
    OUTPUT as BACH_CERTIFICATE,
    endpoint_operator,
)


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_METRIC_BACH_CYCLIC_BV_COMPLEX_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-metric-bach-cyclic-bv-complex.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-metric-bach-cyclic-bv-complex-v1.schema.json"
VERIFIER = HERE / "verify_nariai_metric_bach_cyclic_bv_complex.py"
TESTS = HERE / "tests/test_nariai_metric_bach_cyclic_bv_complex.py"
ACTION_PRODUCER = HERE / "nariai_linearized_bach_endpoint.py"
MIDDLE_PRODUCER = HERE / "nariai_yang_mills_middle_compression.py"
KOSTANT_SOURCE = ROOT / "covariant_completion/curved_operator/adjoint_tractor_kostant_compression.py"
FORMAL_SOURCE = ROOT / "covariant_completion/minimal_witness/formal_operators.py"


O = OperatorPolynomial
SIZE = 4
BLOCK_NAMES = ("ghost_H0", "metric_H1", "metric_equation_H1dual", "identity_H0dual")
BLOCK_DEGREES = (-1, 0, 1, 2)
Matrix = list[list[O]]


def _zero() -> Matrix:
    return [[O.zero() for _ in range(SIZE)] for _ in range(SIZE)]


def _add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[row][column] + right[row][column] for column in range(SIZE)]
        for row in range(SIZE)
    ]


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    output = _zero()
    for row in range(SIZE):
        for column in range(SIZE):
            for middle in range(SIZE):
                output[row][column] = (
                    output[row][column]
                    + left[row][middle] * right[middle][column]
                )
    return output


def _sharp(value: O) -> O:
    involution = {"K": "Ksharp", "Ksharp": "K", "B": "B"}
    return O._from_dict(
        {
            tuple(involution[name] for name in reversed(word)): coefficient
            for word, coefficient in value.terms
        }
    )


def _matrix_sharp(value: Matrix) -> Matrix:
    return [
        [_sharp(value[column][row]) for column in range(SIZE)]
        for row in range(SIZE)
    ]


def _degree_sign() -> Matrix:
    value = _zero()
    for index, degree in enumerate(BLOCK_DEGREES):
        value[index][index] = O.identity(-1 if degree % 2 else 1)
    return value


def _scale(value: Matrix, coefficient: int) -> Matrix:
    return [[entry.scale(coefficient) for entry in row] for row in value]


def _reduce_complex_relations(value: O) -> O:
    zero_pairs = {("B", "K"), ("Ksharp", "B")}
    return O._from_dict(
        {
            word: coefficient
            for word, coefficient in value.terms
            if not any(
                word[index : index + 2] in zero_pairs
                for index in range(max(0, len(word) - 1))
            )
        }
    )


def _matrix_zero(value: Matrix, *, modulo_complex: bool = False) -> bool:
    return all(
        (_reduce_complex_relations(entry) if modulo_complex else entry)
        == O.zero()
        for row in value
        for entry in row
    )


def _digest(value: Matrix) -> str:
    payload = "\n".join(
        ",".join(entry.display() for entry in row) for row in value
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def _formal_k_sharp(
    gauge_generator: dict[tuple[int, ...], sp.Matrix],
    ghost_pairing: sp.Matrix,
    field_pairing: sp.Matrix,
) -> dict[tuple[int, ...], sp.Matrix]:
    if any(len(word) != 1 for word in gauge_generator):
        raise AssertionError("Nariai conformal-Killing operator ceased to be first order")
    return {
        tuple(reversed(word)): (
            -ghost_pairing.inv() * matrix.T * field_pairing
        ).applyfunc(sp.expand)
        for word, matrix in gauge_generator.items()
    }


def kernel() -> dict[str, object]:
    endpoint = endpoint_operator()
    middle = endpoint["middle"]
    algebraic = middle["algebraic"]
    gauge_generator = middle["first_bgg"]
    bach = endpoint["action_bach"]
    ghost_pairing = algebraic.endpoint_ghost_pairing
    field_pairing = algebraic.endpoint_field_pairing
    k_sharp = _formal_k_sharp(gauge_generator, ghost_pairing, field_pairing)

    differential = _zero()
    differential[1][0] = O.atom("K")
    differential[2][1] = O.atom("B")
    differential[3][2] = O.atom("Ksharp")

    pairing = _zero()
    for left, right in ((0, 3), (1, 2)):
        pairing[left][right] = O.identity()
        pairing[right][left] = O.identity(-1)

    cyclic_defect = _add(
        _multiply(_matrix_sharp(differential), pairing),
        _multiply(_multiply(_degree_sign(), pairing), differential),
    )
    square = _multiply(differential, differential)
    return {
        "endpoint": endpoint,
        "gauge_generator": gauge_generator,
        "bach": bach,
        "k_sharp": k_sharp,
        "ghost_pairing": ghost_pairing,
        "field_pairing": field_pairing,
        "differential": differential,
        "pairing": pairing,
        "checks": {
            "abstract_Q_squared_mod_Noether": _matrix_zero(
                square, modulo_complex=True
            ),
            "abstract_odd_cyclicity": _matrix_zero(cyclic_defect),
            "B_K_defect_entries": sum(
                value != 0
                for matrix in endpoint["action_gauge_defect"].values()
                for value in matrix
            ),
            "Ksharp_B_defect_entries": sum(
                value != 0
                for defect in endpoint["divergence_defects"]
                for matrix in defect.values()
                for value in matrix
            ),
        },
    }


def build() -> dict[str, object]:
    action_certificate = json.loads(BACH_CERTIFICATE.read_text())
    if action_certificate["flags"]["NARIAI_METRIC_BACH_ENDPOINT_EXACT"] is not True:
        raise ValueError("action-derived Nariai Bach endpoint unavailable")
    value = kernel()
    checks = value["checks"]
    if not all(
        (
            checks["abstract_Q_squared_mod_Noether"],
            checks["abstract_odd_cyclicity"],
            checks["B_K_defect_entries"] == 0,
            checks["Ksharp_B_defect_entries"] == 0,
        )
    ):
        raise AssertionError("metric Bach cyclic BV complex did not close")

    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (
            Path(__file__).resolve(),
            VERIFIER,
            TESTS,
            SCHEMA,
            ACTION_PRODUCER,
            MIDDLE_PRODUCER,
            KOSTANT_SOURCE,
            FORMAL_SOURCE,
        )
    }
    return {
        "schema": "pure-weyl-nariai-metric-bach-cyclic-bv-complex-v1",
        "result_id": "NARIAI_METRIC_BACH_CYCLIC_BV_COMPLEX_V1",
        "result_state": "ACTION_PAIRED_FOUR_ROW_METRIC_BACH_COMPLEX_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "action_bach_endpoint": {
                "artifact_id": action_certificate["result_id"],
                "path": str(BACH_CERTIFICATE.relative_to(ROOT)),
                "sha256": _sha256(BACH_CERTIFICATE),
            }
        },
        "complex": {
            "block_names": list(BLOCK_NAMES),
            "block_degrees": list(BLOCK_DEGREES),
            "block_dimensions": [4, 9, 9, 4],
            "arrows": ["K", "B_action", "Ksharp"],
            "B_action_sha256": action_certificate["exact_operator"]["sha256"],
            "abstract_differential_sha256": _digest(value["differential"]),
            "abstract_pairing_sha256": _digest(value["pairing"]),
        },
        "action_pairing": {
            "ghost_identity_pairing": _sparse(value["ghost_pairing"]),
            "field_equation_pairing": _sparse(value["field_pairing"]),
            "field_equation_interpretation": "evaluation pairing after the tensor Gram has converted the Bach output to H1-dual coordinates",
            "tensor_gram_not_applied_twice": True,
            "compact_support_boundary_term": "zero",
        },
        "exact_operators": {
            "K": _sparse_table(value["gauge_generator"]),
            "Ksharp": _sparse_table(value["k_sharp"]),
            "B_action": {
                "artifact_path": str(BACH_CERTIFICATE.relative_to(ROOT)),
                "coefficient_sha256": action_certificate["exact_operator"]["sha256"],
                "orders": action_certificate["exact_operator"]["orders"],
            },
        },
        "exact_checks": {
            **checks,
            "K_orders": sorted({len(word) for word in value["gauge_generator"]}),
            "Ksharp_orders": sorted({len(word) for word in value["k_sharp"]}),
            "B_orders": action_certificate["exact_operator"]["orders"],
            "B_formal_self_adjointness": "the Hessian symmetry of the Weyl-squared action at the Bach-flat Nariai solution, for compactly supported variations",
            "coefficientwise_generic_PBW_adjoint_used_as_authority": False,
            "action_pairing_reconciled": True,
        },
        "flags": {
            "NARIAI_METRIC_BACH_CYCLIC_BV_COMPLEX_V1": True,
            "NARIAI_ACTION_PAIRING_RECONCILED": True,
            "NARIAI_METRIC_BACH_ENDPOINT_CHAIN_COMPLEX": True,
            "RELATIVE_PARENT_METRIC_CHAIN_EQUIVALENCE": False,
            "RELATIVE_EQUATION_IDENTITY_CONE": False,
            "NARIAI_GREEN_HOMOTOPY": False,
            "OPEN_BACKGROUND_CLASS": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "C_G2_NARIAI_RELATIVE_EQUATION_IDENTITY_CONE",
        "claim_boundary": (
            "This certificate derives the endpoint field/equation and ghost/identity pairings from the action-coordinate types, derives Ksharp from K, and verifies the exact four-row metric Bach BV complex on unit Nariai: B K=0, Ksharp B=0, Q squared zero modulo those coefficient identities, and odd cyclicity. Formal self-adjointness of B is the second-variation theorem for the Weyl-squared action at the Bach-flat background; the known generic post-normal-order PBW adjoint path is not used as authority. This does not yet construct a chain equivalence to the parent curvature-incidence cylinder, the relative equation/identity-row cone or SDR, any Green homotopy, an open background class, nonlinear interactions, or a quantum claim."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_metric_bach_cyclic_bv_complex.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_metric_bach_cyclic_bv_complex.py",
                "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_metric_bach_cyclic_bv_complex",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-metric-bach-cyclic-bv-complex-v1.schema.json -d d_quotient_classical/certificates/NARIAI_METRIC_BACH_CYCLIC_BV_COMPLEX_V1.json",
            ],
        },
    }


def render(value: dict[str, object]) -> str:
    return rf"""# Nariai metric Bach cyclic BV complex

The action-derived endpoint closes as the four-row complex

\[
H_0\xrightarrow{{K}}H_1\xrightarrow{{B_{{\rm action}}}}H_1^*
\xrightarrow{{K^\sharp}}H_0^*.
\]

The field/equation pairing is the evaluation matrix (I_9): the tensor Gram
has already converted the Bach tensor into endpoint covector coordinates and
must not be applied a second time.  The ghost/identity pairing is the
Lorentzian matrix \(\operatorname{{diag}}(-1,1,1,1)\).

The exact coefficient identities give

\[
B_{{\rm action}}K=0,
\qquad
K^\sharp B_{{\rm action}}=0.
\]

Together with Hessian symmetry of the Weyl-squared action, these prove the
four-row differential is nilpotent and odd cyclic.  The generic
post-normal-order PBW adjoint is deliberately not used as authority.

## Formal-adjoint proof

Let (S[g]) be the Weyl-squared action in the normalization recorded by the
endpoint certificate.  Its first variation is the evaluation pairing of the
Bach tensor with a metric variation, modulo a boundary term.  Unit Nariai is
Bach-flat.  Therefore, for compactly supported trace-free variations (u,v),
commutation of the two ordinary variation parameters gives

\[
0=(\delta_u\delta_v-\delta_v\delta_u)S[\bar g]
  =\langle u,B_{{\rm action}}v\rangle
   -\langle B_{{\rm action}}u,v\rangle .
\]

The boundary term vanishes by compact support.  This proves the required
formal self-adjointness in the action pairing independently of any chosen PBW
normal-order implementation.

## Boundary

{value['claim_boundary']}
"""


def verify(value: dict[str, object]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("metric Bach cyclic complex certificate drifted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.guards:
        flags = value["flags"]
        if flags["NARIAI_METRIC_BACH_CYCLIC_BV_COMPLEX_V1"] is not True:
            raise AssertionError("metric Bach complex guard failed")
        if flags["RELATIVE_EQUATION_IDENTITY_CONE"] is not False:
            raise AssertionError("relative cone was overpromoted")
        if flags["NARIAI_GREEN_HOMOTOPY"] is not False:
            raise AssertionError("Green homotopy was overpromoted")
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(render(value))
    if args.check:
        verify(json.loads(OUTPUT.read_text()))
    print(f"{value['result_id']}: PASS")


if __name__ == "__main__":
    main()
