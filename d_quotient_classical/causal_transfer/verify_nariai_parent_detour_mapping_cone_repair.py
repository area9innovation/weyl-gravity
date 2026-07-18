#!/usr/bin/env python3
"""Independent replay of the Nariai parent-detour cone repair."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_kostant_compression import _parse_sparse
from d_quotient_classical.causal_transfer.nariai_automorphism_prolongation_first_two_rows import fixture as automorphism_fixture
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT
from d_quotient_classical.causal_transfer.nariai_linearized_bach_endpoint import endpoint_operator


OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-parent-detour-mapping-cone-repair-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_table(value: object) -> dict[tuple[int, ...], sp.Matrix]:
    if not isinstance(value, dict) or set(value) != {"entries", "sha256"}:
        raise AssertionError("malformed PBW table")
    table = {}
    for item in value["entries"]:
        table[tuple(item["word"])] = _parse_sparse(item["matrix"])
    return table


def _add(left: dict[tuple[int, ...], sp.Matrix], right: dict[tuple[int, ...], sp.Matrix]) -> dict[tuple[int, ...], sp.Matrix]:
    sample = next(iter(left.values()), next(iter(right.values())))
    return {
        word: matrix
        for word in set(left) | set(right)
        if (matrix := (left.get(word, sp.zeros(*sample.shape)) + right.get(word, sp.zeros(*sample.shape))).applyfunc(sp.expand)) != sp.zeros(*sample.shape)
    }


def _scale(value: dict[tuple[int, ...], sp.Matrix], coefficient: sp.Rational) -> dict[tuple[int, ...], sp.Matrix]:
    return {
        word: (coefficient * matrix).applyfunc(sp.expand)
        for word, matrix in value.items()
        if coefficient * matrix != sp.zeros(*matrix.shape)
    }


def _left(matrix: sp.Matrix, value: dict[tuple[int, ...], sp.Matrix]) -> dict[tuple[int, ...], sp.Matrix]:
    return {word: matrix * coefficient for word, coefficient in value.items() if matrix * coefficient != sp.zeros(matrix.rows, coefficient.cols)}


def _right(value: dict[tuple[int, ...], sp.Matrix], matrix: sp.Matrix) -> dict[tuple[int, ...], sp.Matrix]:
    return {word: coefficient * matrix for word, coefficient in value.items() if coefficient * matrix != sp.zeros(coefficient.rows, matrix.cols)}


def _assert_zero(value: dict[tuple[int, ...], sp.Matrix], label: str) -> None:
    if value:
        raise AssertionError(f"{label}: {sum(x != 0 for m in value.values() for x in m)} entries")


def _abstract_layout(certificate: dict[str, object], name: str) -> dict[tuple[int, int], list[list[object]]]:
    value = certificate["abstract_matrices"][name]
    return {(entry[0], entry[1]): entry[2] for entry in value["entries"]}


def verify() -> None:
    certificate = json.loads(OUTPUT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    for dependency in certificate["dependency_refs"].values():
        if _sha(ROOT / dependency["path"]) != dependency["sha256"]:
            raise AssertionError(f"dependency digest drifted: {dependency['artifact_id']}")
    for relative, digest in certificate["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise AssertionError(f"source digest drifted: {relative}")

    if certificate["carrier"]["total_rank"] != 310:
        raise AssertionError("carrier rank drifted")
    if sum(certificate["carrier"]["block_ranks"]) != 310:
        raise AssertionError("block-rank sum drifted")

    automorphism = automorphism_fixture()
    endpoint = endpoint_operator()
    p0 = automorphism["projection0"]
    j0 = sp.Matrix.hstack(*p0.nullspace())
    r0 = (j0.T * j0).inv() * j0.T
    if _parse_sparse(certificate["algebraic_complement"]["J0"]) != j0:
        raise AssertionError("J0 was not reconstructed from ker p0")
    if _parse_sparse(certificate["algebraic_complement"]["r0"]) != r0:
        raise AssertionError("r0 was not the declared normalized left inverse")
    if p0 * j0 != sp.zeros(4, 11) or r0 * j0 != sp.eye(11):
        raise AssertionError("algebraic complement does not split")

    l0 = automorphism["corrected_l0"]
    l0p0 = _right(l0, p0)
    r_complement = _add({(): sp.eye(15)}, _scale(l0p0, -1))
    serialized_r = _parse_table(certificate["algebraic_complement"]["R0"])
    if serialized_r != r_complement:
        raise AssertionError("R0 coefficient table drifted")
    g = _left(r0, r_complement)
    if _parse_table(certificate["algebraic_complement"]["g"]) != g:
        raise AssertionError("g coefficient table drifted")
    _assert_zero(_add(_right(g, j0), {(): -sp.eye(11)}), "g J0-1")
    _assert_zero(_add(_left(j0, g), _scale(r_complement, -1)), "J0 g-R0")
    _assert_zero(_add(_left(p0, l0), {(): -sp.eye(4)}), "p0 L0-1")

    middle = automorphism["middle"]
    algebraic = middle["algebraic"]
    expected_pairings = {
        "C0": algebraic.adjoint_pairing,
        "C1": algebraic.one_form_pairing,
        "H0": algebraic.endpoint_ghost_pairing,
        "H1": algebraic.endpoint_field_pairing,
        "ker_p0_coordinate_evaluation": sp.eye(11),
    }
    for name, expected in expected_pairings.items():
        if _parse_sparse(certificate["fibre_pairings"][name]) != expected:
            raise AssertionError(f"fibre pairing drifted: {name}")
    compressed = middle["compressed_middle"]
    q_unique = middle["endpoint_correction"]
    effective = _add(_scale(compressed, sp.Rational(-1, 2)), {(): -sp.Rational(1, 2) * q_unique})
    _assert_zero(_add(effective, _scale(endpoint["action_bach"], -1)), "effective Hessian-Bach")
    if _parse_table(certificate["operators"]["effective_Hessian"]) != effective:
        raise AssertionError("effective Hessian serialization drifted")

    q_layout = _abstract_layout(certificate, "q")
    expected_q_positions = {(1, 0), (3, 0), (6, 2), (6, 4), (7, 3), (8, 2), (9, 5), (9, 7)}
    if set(q_layout) != expected_q_positions:
        raise AssertionError("split Q layout drifted")
    h_layout = _abstract_layout(certificate, "homotopy")
    expected_h_positions = {(0, 1), (2, 8), (4, 6), (4, 8), (5, 9)}
    if set(h_layout) != expected_h_positions:
        raise AssertionError("local homotopy layout drifted")
    if q_layout[(6, 2)] != [[['M'], -1, 2]]:
        raise AssertionError("parent saddle normalization drifted")
    if h_layout[(4, 8)] != [[['M'], 1, 2]]:
        raise AssertionError("parent saddle inverse drifted")

    checks = certificate["exact_checks"]
    if any(not checks[name] for name in (
        "split_Q_squared", "split_odd_cyclic", "projection_inclusion_identity",
        "inclusion_chain_map", "projection_chain_map", "retract_identity",
        "homotopy_odd_cyclic", "metric_pairing_pullback", "canonical_transform",
        "transform_left_inverse", "transform_right_inverse", "original_Q_squared",
        "original_odd_cyclic", "original_retract_identity",
    )):
        raise AssertionError("an abstract SDR obligation was not promoted")
    if certificate["flags"]["NARIAI_GREEN_HOMOTOPY"] is not False:
        raise AssertionError("algebraic repair overclaimed Green propagation")
    if certificate["flags"]["SUPPORT_LOCAL_AUTOMORPHISM_SDR"] is not True:
        raise AssertionError("support-local SDR was not promoted")
    if certificate["next_gate"] != "C_G2_NARIAI_REPAIRED_PARENT_GREEN_TRANSFER":
        raise AssertionError("next gate drifted")
    print("NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1: independently verified")


if __name__ == "__main__":
    verify()
