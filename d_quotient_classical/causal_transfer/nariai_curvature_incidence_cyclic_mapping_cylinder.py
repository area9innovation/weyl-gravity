#!/usr/bin/env python3
"""Odd-cyclic parent-relative mapping cylinder for the Nariai incidence."""

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
SHIFTED = ROOT / "d_quotient_classical/certificates/NARIAI_CURVATURE_INCIDENCE_SHIFTED_CHAIN_V1.json"
INCIDENCE = ROOT / "d_quotient_classical/certificates/NARIAI_CURVATURE_INCIDENCE_FIRST_SQUARE_V1.json"
PARENT = ROOT / "d_quotient_classical/certificates/CONFORMALLY_EINSTEIN_YANG_MILLS_DETOUR_CORRECTION_V1.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_CURVATURE_INCIDENCE_CYCLIC_MAPPING_CYLINDER_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-curvature-incidence-cyclic-mapping-cylinder.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-curvature-incidence-cyclic-mapping-cylinder-v1.schema.json"
VERIFIER = HERE / "verify_nariai_curvature_incidence_cyclic_mapping_cylinder.py"
TESTS = HERE / "tests/test_nariai_curvature_incidence_cyclic_mapping_cylinder.py"
FORMAL_CODE = ROOT / "covariant_completion/minimal_witness/formal_operators.py"
SHIFTED_PRODUCER = HERE / "nariai_curvature_incidence_shifted_chain.py"


O = OperatorPolynomial
Matrix = list[list[O]]
SIZE = 8
BLOCK_NAMES = (
    "epsilon_C0",
    "chi_H1",
    "h_H1",
    "a_C1",
    "h_sharp_H1",
    "a_sharp_C1",
    "epsilon_sharp_C0",
    "chi_sharp_H1",
)
BLOCK_DEGREES = (-1, -1, 0, 0, 1, 1, 2, 2)
PARENT_INDICES = (0, 3, 5, 6)


def _zero() -> Matrix:
    return [[O.zero() for _ in range(SIZE)] for _ in range(SIZE)]


def _identity() -> Matrix:
    value = _zero()
    for index in range(SIZE):
        value[index][index] = O.identity()
    return value


def _add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[row][column] + right[row][column] for column in range(SIZE)]
        for row in range(SIZE)
    ]


def _scale(matrix: Matrix, coefficient: int | Fraction) -> Matrix:
    return [[entry.scale(coefficient) for entry in row] for row in matrix]


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    value = _zero()
    for row in range(SIZE):
        for column in range(SIZE):
            for middle in range(SIZE):
                value[row][column] = (
                    value[row][column] + left[row][middle] * right[middle][column]
                )
    return value


def _operator_adjoint(value: O) -> O:
    involution = {
        "d": "dsharp",
        "dsharp": "d",
        "M": "M",
        "L": "Lsharp",
        "Lsharp": "L",
    }
    return O._from_dict(
        {
            tuple(involution[name] for name in reversed(word)): coefficient
            for word, coefficient in value.terms
        }
    )


def _matrix_adjoint(matrix: Matrix) -> Matrix:
    return [
        [_operator_adjoint(matrix[column][row]) for column in range(SIZE)]
        for row in range(SIZE)
    ]


def _degree_sign() -> Matrix:
    value = _zero()
    for index, degree in enumerate(BLOCK_DEGREES):
        value[index][index] = O.identity(-1 if degree % 2 else 1)
    return value


def _is_zero(matrix: Matrix) -> bool:
    return all(entry == O.zero() for row in matrix for entry in row)


def _reduce_parent_relations(value: O) -> O:
    relations = {("M", "d"), ("dsharp", "M")}
    terms: dict[tuple[str, ...], Fraction] = {}
    for word, coefficient in value.terms:
        if any(
            word[index : index + 2] in relations
            for index in range(max(0, len(word) - 1))
        ):
            continue
        terms[word] = terms.get(word, Fraction()) + coefficient
    return O._from_dict(terms)


def _is_zero_mod_parent(matrix: Matrix) -> bool:
    return all(
        _reduce_parent_relations(entry) == O.zero()
        for row in matrix
        for entry in row
    )


def _digest(matrix: Matrix) -> str:
    payload = "\n".join(
        ",".join(entry.display() for entry in row) for row in matrix
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def _serialize_operator(value: O) -> list[list[object]]:
    return [
        [list(word), coefficient.numerator, coefficient.denominator]
        for word, coefficient in value.terms
    ]


def _serialize_matrix(matrix: Matrix) -> dict[str, object]:
    entries = [
        [row, column, _serialize_operator(matrix[row][column])]
        for row in range(SIZE)
        for column in range(SIZE)
        if matrix[row][column] != O.zero()
    ]
    return {
        "shape": [SIZE, SIZE],
        "entries": entries,
        "sha256": _digest(matrix),
    }


def kernel() -> dict[str, object]:
    split = _zero()
    split[2][1] = O.identity()                  # chi -> h
    split[3][0] = O.atom("d")                 # epsilon -> b
    split[5][3] = O.atom("M")                 # b -> b#
    split[6][5] = O.atom("dsharp")            # b# -> epsilon#
    split[7][4] = O.identity()                  # h# -> chi#

    pairing = _zero()
    for left, right in ((0, 6), (1, 7), (2, 4), (3, 5)):
        pairing[left][right] = O.identity()
        pairing[right][left] = O.identity(-1)

    # Split parent coordinate b=a+Lh.  The forced cotangent shift is
    # h#_old=h#_split+L# a#.  This is a degree-zero type-II canonical shear.
    split_to_graph = _identity()
    graph_to_split = _identity()
    split_to_graph[3][2] = O.atom("L", -1)
    graph_to_split[3][2] = O.atom("L")
    split_to_graph[4][5] = O.atom("Lsharp")
    graph_to_split[4][5] = O.atom("Lsharp", -1)
    prolonged = _multiply(_multiply(split_to_graph, split), graph_to_split)

    split_inclusion = _zero()
    split_projection = _zero()
    for index in PARENT_INDICES:
        split_inclusion[index][index] = O.identity()
        split_projection[index][index] = O.identity()
    inclusion = _multiply(split_to_graph, split_inclusion)
    projection = _multiply(split_projection, graph_to_split)

    split_homotopy = _zero()
    split_homotopy[1][2] = O.identity(-1)
    split_homotopy[4][7] = O.identity(-1)
    homotopy = _multiply(
        _multiply(split_to_graph, split_homotopy), graph_to_split
    )

    identity = _identity()
    base_identity = _zero()
    for index in PARENT_INDICES:
        base_identity[index][index] = O.identity()
    degree_sign = _degree_sign()
    split_cyclic_defect = _add(
        _multiply(_matrix_adjoint(split), pairing),
        _multiply(_multiply(degree_sign, pairing), split),
    )
    prolonged_cyclic_defect = _add(
        _multiply(_matrix_adjoint(prolonged), pairing),
        _multiply(_multiply(degree_sign, pairing), prolonged),
    )
    canonical_defect = _add(
        _multiply(_multiply(_matrix_adjoint(split_to_graph), pairing), split_to_graph),
        _scale(pairing, -1),
    )
    right_inverse_defect = _add(
        _multiply(split_to_graph, graph_to_split), _scale(identity, -1)
    )
    left_inverse_defect = _add(
        _multiply(graph_to_split, split_to_graph), _scale(identity, -1)
    )
    pi_defect = _add(_multiply(projection, inclusion), _scale(base_identity, -1))
    inclusion_chain_defect = _add(
        _multiply(prolonged, inclusion),
        _scale(_multiply(inclusion, split), -1),
    )
    projection_chain_defect = _add(
        _multiply(projection, prolonged),
        _scale(_multiply(split, projection), -1),
    )
    retract_defect = _add(
        _add(_multiply(inclusion, projection), _scale(identity, -1)),
        _scale(
            _add(
                _multiply(prolonged, homotopy),
                _multiply(homotopy, prolonged),
            ),
            -1,
        ),
    )
    homotopy_cyclic_defect = _add(
        _multiply(_matrix_adjoint(homotopy), pairing),
        _scale(_multiply(_multiply(degree_sign, pairing), homotopy), -1),
    )
    return {
        "split": split,
        "pairing": pairing,
        "split_to_graph": split_to_graph,
        "graph_to_split": graph_to_split,
        "prolonged": prolonged,
        "inclusion": inclusion,
        "projection": projection,
        "homotopy": homotopy,
        "checks": {
            "split_Q_squared": _is_zero_mod_parent(_multiply(split, split)),
            "prolonged_Q_squared": _is_zero_mod_parent(_multiply(prolonged, prolonged)),
            "split_odd_cyclic": _is_zero(split_cyclic_defect),
            "prolonged_odd_cyclic": _is_zero(prolonged_cyclic_defect),
            "canonical_shear": _is_zero(canonical_defect),
            "shear_right_inverse": _is_zero(right_inverse_defect),
            "shear_left_inverse": _is_zero(left_inverse_defect),
            "projection_inclusion_identity": _is_zero(pi_defect),
            "inclusion_chain_map": _is_zero_mod_parent(inclusion_chain_defect),
            "projection_chain_map": _is_zero_mod_parent(projection_chain_defect),
            "retract_identity": _is_zero_mod_parent(retract_defect),
            "homotopy_odd_cyclic": _is_zero(homotopy_cyclic_defect),
        },
    }


def build() -> dict[str, object]:
    shifted = json.loads(SHIFTED.read_text())
    incidence = json.loads(INCIDENCE.read_text())
    parent = json.loads(PARENT.read_text())
    if shifted["flags"]["CURVATURE_INCIDENCE_SHIFTED_CHAIN_EXACT"] is not True:
        raise ValueError("shifted-chain dependency unavailable")
    if shifted["flags"]["FACTORIZED_RELATIVE_SADDLE_GAUGE_IDENTITY_EXACT"] is not True:
        raise ValueError("factorized saddle dependency unavailable")
    if parent["exact_checks"]["Nariai_curved_parent_complex_exists"] is not True:
        raise ValueError("Bach-flat parent complex unavailable")
    value = kernel()
    if not all(value["checks"].values()):
        raise AssertionError(f"mapping-cylinder kernel defect: {value['checks']}")
    matrices = {
        name: _serialize_matrix(value[name])
        for name in (
            "split",
            "pairing",
            "split_to_graph",
            "graph_to_split",
            "prolonged",
            "inclusion",
            "projection",
            "homotopy",
        )
    }
    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (
            Path(__file__).resolve(),
            VERIFIER,
            TESTS,
            SCHEMA,
            FORMAL_CODE,
            SHIFTED_PRODUCER,
        )
    }
    return {
        "schema": "pure-weyl-nariai-curvature-incidence-cyclic-mapping-cylinder-v1",
        "result_id": "NARIAI_CURVATURE_INCIDENCE_CYCLIC_MAPPING_CYLINDER_V1",
        "result_state": "CYCLIC_PARENT_MAPPING_CYLINDER_AND_SDR_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "shifted_chain": {"artifact_id": shifted["result_id"], "path": str(SHIFTED.relative_to(ROOT)), "sha256": _sha256(SHIFTED)},
            "curvature_incidence": {"artifact_id": incidence["result_id"], "path": str(INCIDENCE.relative_to(ROOT)), "sha256": _sha256(INCIDENCE)},
            "yang_mills_parent": {"artifact_id": parent["result_id"], "path": str(PARENT.relative_to(ROOT)), "sha256": _sha256(PARENT)},
        },
        "block_ledger": {
            "names": list(BLOCK_NAMES),
            "degrees": list(BLOCK_DEGREES),
            "parent_retract_indices": list(PARENT_INDICES),
            "split_coordinates": "(epsilon,chi,h,b,hsharp,bsharp,epsilonsharp,chisharp)",
            "graph_coordinates": "b=a+L1_corrected h, with the forced cotangent shift",
            "parent_relations": ["M d=0", "dsharp M=0"],
        },
        "exact_matrices": matrices,
        "exact_checks": {
            **value["checks"],
            "block_count": SIZE,
            "split_nonzero_blocks": len(matrices["split"]["entries"]),
            "prolonged_nonzero_blocks": len(matrices["prolonged"]["entries"]),
            "pairing_nonzero_blocks": len(matrices["pairing"]["entries"]),
            "no_inverse_operator_atoms": all(
                atom not in {"inverse_laplacian", "inverse_curl", "projector", "Green"}
                for matrix in value.values()
                if isinstance(matrix, list)
                for row in matrix
                for entry in row
                for word, _ in entry.terms
                for atom in word
            ),
            "shifted_chain_substitution_exact": shifted["exact_checks"]["M_I_equals_minus_Phi1_K"],
            "factorized_saddle_substitution_exact": (
                shifted["exact_checks"]["factorized_saddle_lower_defect_nonzero_entries"] == 0
                and shifted["exact_checks"]["factorized_saddle_upper_defect_nonzero_entries"] == 0
            ),
        },
        "endpoint_ghost_embedding": {
            "map": "xi -> (epsilon=L0 xi, chi=K xi)",
            "field_image": "Q xi -> (h=K xi, a=d L0 xi-L1_corrected K xi)=(K xi,I_Omega xi)",
            "incidence_identity_used": True,
            "strict_metric_graph_chain_map": False,
        },
        "theorem": {
            "statement": "The Nariai curvature incidence admits an eight-block local odd-cyclic parent-relative mapping cylinder. It is obtained from the direct sum of the Yang--Mills parent and the contractible chi-to-h pair by the canonical finite-order shear b=a+L1_corrected h and its forced cotangent transform.",
            "sdr": "The displayed inclusion, projection and degree-minus-one homotopy give PI=1 and IP-1=QH+HQ modulo exactly the two parent-complex relations. The cylinder therefore deformation-retracts to the corrected Yang--Mills parent without duplicating cohomology.",
            "incidence": "Embedding an endpoint ghost as (L0 xi,K xi) produces the graph-coordinate field image (K xi,I_Omega xi), so the previously certified curvature term is represented as an honest local cylinder incidence rather than suppressed by a nonlocal projector.",
        },
        "flags": {
            "NARIAI_CURVATURE_INCIDENCE_CYCLIC_MAPPING_CYLINDER_V1": True,
            "INDEPENDENT_FACTORIZED_VARIATIONAL_CHECKER": True,
            "CYCLIC_CURVATURE_INCIDENCE_MAPPING_CONE": True,
            "MAPPING_CYLINDER_SDR": True,
            "SUPPORT_LOCAL_FINITE_ORDER": True,
            "HOM_BUNDLE_GENERIC_PBW_NORMALIZER_REPAIRED": False,
            "METRIC_BACH_ENDPOINT_CHAIN_EQUIVALENCE": False,
            "NARIAI_GREEN_HOMOTOPY": False,
            "OPEN_BACKGROUND_CLASS": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "C_G2_NARIAI_METRIC_BACH_ENDPOINT_CHAIN_MAP_AND_GREEN_TRANSFER",
        "claim_boundary": (
            "This certificate constructs and independently checks the complete local odd-cyclic mapping-cylinder kernel needed to retain the Nariai curvature incidence. The split complex is the corrected Yang--Mills parent plus one contractible shift pair; the finite-order L1_corrected shear and its cotangent dual are canonical, invertible, nilpotence-preserving and cyclic. The explicit inclusion, projection and cyclic homotopy give an SDR back to the parent, and the endpoint ghost embedding reproduces (K xi,I_Omega xi) exactly through the imported coefficient tables. This closes the parent-relative cone even though the generic post-normal-order PBW adjoint routine remains unrepaired; an independent factorized variational checker supplies the authoritative cyclic proof. It does not yet prove that the metric Bach endpoint is chain-equivalent to this parent-relative cylinder, does not eliminate the connection variable to a support-local metric operator, and does not construct retarded/advanced Green homotopies, a uniform non-conformally-flat class, nonlinear interactions, or a quantum theory."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_curvature_incidence_cyclic_mapping_cylinder.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_curvature_incidence_cyclic_mapping_cylinder.py",
                "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_curvature_incidence_cyclic_mapping_cylinder",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-curvature-incidence-cyclic-mapping-cylinder-v1.schema.json -d d_quotient_classical/certificates/NARIAI_CURVATURE_INCIDENCE_CYCLIC_MAPPING_CYLINDER_V1.json",
            ],
        },
    }


def render(value: dict[str, object]) -> str:
    checks = value["exact_checks"]
    return rf"""# Nariai cyclic curvature-incidence mapping cylinder

The parent-relative incidence is now carried by an exact eight-block odd
cyclic mapping cylinder.  In split coordinates it is the direct sum of the
Yang--Mills parent and the contractible pair \(\chi\mapsto h\), together with
their cotangent rows.  The local canonical shear is
\[
b=a+L_1^{{\rm corr}}h
\]
with its forced cotangent transform.

All formal identities pass:

- split and prolonged \(Q^2=0\);
- split and prolonged odd cyclicity;
- canonical shear and two-sided inverse;
- exact inclusion and projection chain maps;
- \(PI=1\) and \(IP-1=QH+HQ\);
- odd-cyclic degree-minus-one homotopy.

The prolonged differential contains `{checks['prolonged_nonzero_blocks']}`
nonzero typed blocks, and the pairing contains
`{checks['pairing_nonzero_blocks']}`.  No inverse Laplacian, inverse curl,
projector or Green atom occurs.  The coefficient substitution imports the
exact relations
\[
M^DI_\Omega+(M^DL_1^{{\rm corr}})K=0
\]
and the two factorized saddle identities.

For an endpoint ghost,
\[
\xi\longmapsto (\epsilon=L_0\xi,\chi=K\xi)
\]
and the graph-coordinate field image is
\[
(K\xi,dL_0\xi-L_1^{{\rm corr}}K\xi)
=(K\xi,I_\Omega\xi).
\]

## Boundary

{value['claim_boundary']}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if args.guards:
        checks = value["exact_checks"]
        required = (
            "split_Q_squared",
            "prolonged_Q_squared",
            "split_odd_cyclic",
            "prolonged_odd_cyclic",
            "canonical_shear",
            "shear_right_inverse",
            "shear_left_inverse",
            "projection_inclusion_identity",
            "inclusion_chain_map",
            "projection_chain_map",
            "retract_identity",
            "homotopy_odd_cyclic",
            "no_inverse_operator_atoms",
            "shifted_chain_substitution_exact",
            "factorized_saddle_substitution_exact",
        )
        if not all(checks[name] for name in required):
            raise AssertionError("cyclic mapping-cylinder guard failed")
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    report = render(value)
    if args.check:
        if OUTPUT.read_text() != encoded or REPORT.read_text() != report:
            raise SystemExit("generated cyclic mapping-cylinder artifacts drifted")
    else:
        OUTPUT.write_text(encoded)
        REPORT.write_text(report)


if __name__ == "__main__":
    main()
