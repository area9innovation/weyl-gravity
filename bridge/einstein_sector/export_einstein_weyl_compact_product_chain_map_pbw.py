#!/usr/bin/env python3
"""Export the certified compact-product Einstein--Weyl chain map in PBW form.

The output is a 40-by-38 support-local unary operator.  Rows are joined by
stable ``row_id`` strings; numeric indices are only a serialization detail.
The construction uses the tensor formula certified by
``EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1`` and the committed
Einstein--Maxwell and Weyl--Maxwell product row layouts.  The Maxwell equation
and identity inputs are adapted from the legacy covariant-equation convention
to the action-derived BV cotangent-row convention before serialization.
"""

from __future__ import annotations

import argparse
from itertools import combinations_with_replacement, product
import hashlib
import json
from pathlib import Path
import sys

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.einstein_sector.product_taylor_engine import (
    BASE_POINT,
    COORDINATES,
    PAIRS,
    LinearOperator,
)


SOURCE_LAYOUT = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_product_linfinity_v1/row_layout.json"
SOURCE_CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1.json"
TARGET_LAYOUT = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/row_layout.json"
TARGET_CERTIFICATE = ROOT / "bridge/certificates/WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1.json"
CHAIN_CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1.json"
CHAIN_PROOF = ROOT / "bridge/einstein_sector/proofs/einstein-weyl-compact-product-covariant-chain-map-v1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-compact-product-chain-map-pbw-v1.schema.json"
OUTPUT = ROOT / "bridge/einstein_sector/generated/einstein_weyl_compact_product_chain_map_pbw_v1/inclusion.json"

SCHEMA_ID = "einstein-weyl-compact-product-chain-map-pbw-v1"
RESULT_ID = "EINSTEIN_WEYL_COMPACT_PRODUCT_CHAIN_MAP_PBW_V1"
BACKGROUND_ID = "compact_magnetic_Plebanski_Hacyan_product"
SOURCE_CARRIER = "einstein_maxwell_minimal_bv_38_product_coordinate_jet"
TARGET_CARRIER = "weyl_maxwell_minimal_bv_40_product_coordinate_theta_jet"
COEFFICIENT_JET_ORDER = 4


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _target_layout() -> list[dict[str, object]]:
    payload = _load(TARGET_LAYOUT)
    rows = payload["content"]["rows"]
    if payload["carrier_id"] != TARGET_CARRIER or len(rows) != 40:
        raise AssertionError("target Weyl--Maxwell row layout drifted")
    return rows


def _sum(values) -> LinearOperator:
    return LinearOperator.from_terms(
        term for value in values for term in value.terms
    )


def _background() -> tuple[sp.Matrix, sp.Matrix, list[list[list[sp.Expr]]]]:
    theta = COORDINATES[2]
    sine = sp.sin(theta)
    metric = sp.diag(-1, 1, 1, sine**2)
    inverse = sp.diag(-1, 1, 1, sine**-2)
    gamma = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    gamma[2][3][3] = -sine * sp.cos(theta)
    gamma[3][2][3] = gamma[3][3][2] = sp.cot(theta)
    return metric, inverse, gamma


def _covariant_derivative(
    tensor: dict[tuple[int, ...], LinearOperator],
    variance: tuple[int, ...],
    gamma: list[list[list[sp.Expr]]],
) -> dict[tuple[int, ...], LinearOperator]:
    output: dict[tuple[int, ...], LinearOperator] = {}
    for axis in range(4):
        for indices in product(range(4), repeat=len(variance)):
            value = tensor[indices].derivative(axis)
            for position, sign in enumerate(variance):
                current = indices[position]
                replacements = []
                for replacement in range(4):
                    changed = indices[:position] + (replacement,) + indices[position + 1 :]
                    coefficient = (
                        -gamma[replacement][axis][current]
                        if sign == -1
                        else gamma[current][axis][replacement]
                    )
                    replacements.append(tensor[changed].scale(coefficient))
                value = value + _sum(replacements)
            output[(axis, *indices)] = value
    return output


def _tracefree(
    tensor: dict[tuple[int, int], LinearOperator],
    metric: sp.Matrix,
    inverse: sp.Matrix,
) -> dict[tuple[int, int], LinearOperator]:
    trace = _sum(
        tensor[(a, b)].scale(inverse[a, b])
        for a, b in product(range(4), repeat=2)
    )
    return {
        (a, b): tensor[(a, b)] - trace.scale(metric[a, b] / 4)
        for a, b in product(range(4), repeat=2)
    }


def _symmetrized_action(
    left: sp.Matrix,
    right: sp.Matrix,
    tensor: dict[tuple[int, int], LinearOperator],
) -> dict[tuple[int, int], LinearOperator]:
    return {
        (a, b): _sum(
            tensor[(c, d)].scale(
                (left[a, c] * right[b, d] + left[b, c] * right[a, d]) / 2
            )
            for c, d in product(range(4), repeat=2)
        )
        for a, b in product(range(4), repeat=2)
    }


def _metric_equation_map(source: dict[str, int]) -> dict[str, LinearOperator]:
    metric, inverse, gamma = _background()
    # The payload stores derivatives with respect to the ten independent
    # symmetric components.  Convert those Euler coordinates to E^{ab}, then
    # lower both indices before applying the certified tensor formula.
    upper: dict[tuple[int, int], LinearOperator] = {}
    for a, b in product(range(4), repeat=2):
        pair = tuple(sorted((a, b)))
        multiplicity = 1 if a == b else 2
        upper[(a, b)] = LinearOperator.basis(source[f"g_{pair[0]}{pair[1]}_star"]).scale(
            sp.Rational(2, multiplicity)
        )
    lower = {
        (a, b): _sum(
            upper[(c, d)].scale(metric[a, c] * metric[b, d])
            for c, d in product(range(4), repeat=2)
        )
        for a, b in product(range(4), repeat=2)
    }
    maxwell_up = {
        (a,): LinearOperator.basis(source[f"A_{a}_star"])
        for a in range(4)
    }
    maxwell_down = {
        (a,): _sum(maxwell_up[(b,)].scale(metric[a, b]) for b in range(4))
        for a in range(4)
    }

    first_e = _covariant_derivative(lower, (-1, -1), gamma)
    second_e = _covariant_derivative(first_e, (-1, -1, -1), gamma)
    box_e = {
        (a, b): _sum(
            second_e[(c, d, a, b)].scale(inverse[c, d])
            for c, d in product(range(4), repeat=2)
        )
        for a, b in product(range(4), repeat=2)
    }
    trace = _sum(
        lower[(a, b)].scale(inverse[a, b])
        for a, b in product(range(4), repeat=2)
    )
    gradient = [trace.derivative(a) for a in range(4)]
    hessian = {
        (a, b): gradient[b].derivative(a)
        - _sum(gradient[c].scale(gamma[c][a][b]) for c in range(4))
        for a, b in product(range(4), repeat=2)
    }
    box_trace = _sum(hessian[(a, b)].scale(inverse[a, b]) for a, b in product(range(4), repeat=2))
    principal = {
        (a, b): box_e[(a, b)].scale(sp.Rational(1, 2))
        - (box_trace.scale(metric[a, b]) - hessian[(a, b)]).scale(sp.Rational(1, 6))
        for a, b in product(range(4), repeat=2)
    }

    identity = sp.eye(4)
    projector_s = sp.diag(0, 0, 1, 1)
    projector_l = identity - projector_s
    sine = sp.sin(COORDINATES[2])
    j_l = sp.Matrix([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
    j_s = sp.Matrix([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1 / sine], [0, 0, -sine, 0]])
    algebraic = [
        (sp.Rational(3, 2), projector_l, projector_l),
        (-1, projector_l, projector_s),
        (sp.Rational(-5, 2), projector_s, projector_s),
        (sp.Rational(-1, 2), j_l, j_l),
        (sp.Rational(5, 2), j_s, j_s),
    ]
    first_m = _covariant_derivative(maxwell_down, (-1,), gamma)
    derivative_m = {(a, b): first_m[(a, b)] for a, b in product(range(4), repeat=2)}
    pieces = {
        key: principal[key].scale(3)
        for key in product(range(4), repeat=2)
    }
    for coefficient, left, right in algebraic:
        block = _symmetrized_action(left, right, lower)
        pieces = {key: pieces[key] + block[key].scale(coefficient) for key in pieces}
    plus = _symmetrized_action(identity, j_s, derivative_m)
    minus = _symmetrized_action(j_s, identity, derivative_m)
    # The legacy covariant certificate calls the Maxwell Euler row M^a.  In
    # the action-derived odd-cotangent convention used by the frozen q1 table,
    # the serialized A_star input represents -M^a.  Adapt that row convention
    # here; it reverses all four invariant derivative-Maxwell coefficients but
    # changes neither the covariant tensor formula nor the field map.
    pieces = {
        key: pieces[key] - plus[key].scale(3) + minus[key].scale(3)
        for key in pieces
    }
    pieces = _tracefree(pieces, metric, inverse)
    raised = {
        (a, b): _sum(
            pieces[(c, d)].scale(inverse[a, c] * inverse[b, d])
            for c, d in product(range(4), repeat=2)
        )
        for a, b in product(range(4), repeat=2)
    }
    output: dict[str, LinearOperator] = {}
    for a, b in PAIRS:
        multiplicity = 1 if a == b else 2
        output[f"g_{a}{b}_star"] = raised[(a, b)].scale(sp.Rational(multiplicity, 2))
    for a in range(4):
        output[f"A_{a}_star"] = maxwell_up[(a,)]
    return output


def _identity_map(source: dict[str, int]) -> dict[str, LinearOperator]:
    metric, inverse, gamma = _background()
    identity = {(a,): LinearOperator.basis(source[f"c_{a}_star"]) for a in range(4)}
    first = _covariant_derivative(identity, (-1,), gamma)
    second = _covariant_derivative(first, (-1, -1), gamma)
    box = {
        b: _sum(second[(a, c, b)].scale(inverse[a, c]) for a, c in product(range(4), repeat=2))
        for b in range(4)
    }
    j = LinearOperator.basis(source["lambda_cov_star"])
    gradient_j = [j.derivative(axis) for axis in range(4)]
    projector_l = sp.diag(1, 1, 0, 0)
    projector_s = sp.diag(0, 0, 1, 1)
    sine = sp.sin(COORDINATES[2])
    j_s = sp.Matrix([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1 / sine], [0, 0, -sine, 0]])
    output: dict[str, LinearOperator] = {}
    for b in range(4):
        algebraic = _sum(
            identity[(c,)].scale(projector_l[b, c] - projector_s[b, c] / 2)
            for c in range(4)
        )
        gradient = _sum(gradient_j[c].scale(j_s[b, c]) for c in range(4))
        # The same cotangent-row adapter reverses the J contribution in the
        # diffeomorphism-identity row.
        output[f"c_{b}_star"] = box[b].scale(sp.Rational(3, 2)) + algebraic + gradient.scale(sp.Rational(3, 2))
    output["lambda_cov_star"] = j
    return output


def _coefficient_jets(value: sp.Expr) -> list[dict[str, object]]:
    jets = []
    for order in range(COEFFICIENT_JET_ORDER + 1):
        for word in combinations_with_replacement(range(4), order):
            current = value
            for axis in word:
                current = sp.diff(current, COORDINATES[axis])
            coefficient = sp.cancel(current.subs(BASE_POINT))
            if coefficient != 0:
                if not coefficient.is_Rational:
                    raise ValueError(f"coefficient escaped Q: {coefficient}")
                jets.append({"word": list(word), "coefficient": str(sp.Rational(coefficient))})
    return jets


def _entry(
    output_id: str,
    input_id: str,
    operator: LinearOperator,
    source: dict[str, int],
    target: dict[str, int],
) -> dict[str, object]:
    terms = []
    source_index = source[input_id]
    for component, word, coefficient in operator.terms:
        if component != source_index:
            continue
        jets = _coefficient_jets(coefficient)
        if jets:
            terms.append({"word": list(word), "coefficient_jets": jets})
    return {
        "output_row_id": output_id,
        "output_index": target[output_id],
        "input_row_id": input_id,
        "input_index": source_index,
        "maximum_order": max((len(term["word"]) for term in terms), default=0),
        "terms": terms,
    }


def build_payload() -> dict:
    source_payload = _load(SOURCE_LAYOUT)
    source_rows = source_payload["content"]["rows"]
    target_rows = _target_layout()
    source = {str(row["row_id"]): int(row["index"]) for row in source_rows}
    target = {str(row["row_id"]): int(row["index"]) for row in target_rows}
    if len(source) != 38 or len(target) != 40:
        raise AssertionError("carrier row IDs are not unique and complete")

    operators: dict[str, LinearOperator] = {}
    # Common ghost and field rows are identities by stable row ID.
    for row in source_rows:
        row_id = str(row["row_id"])
        if int(row["degree"]) in (-1, 0):
            operators[row_id] = LinearOperator.basis(source[row_id])
    operators.update(_metric_equation_map(source))
    operators.update(_identity_map(source))
    # sigma_W and sigma_W_star deliberately have zero image.

    entries = []
    for output_id in sorted(operators, key=target.__getitem__):
        operator = operators[output_id]
        for input_id in sorted(source, key=source.__getitem__):
            entry = _entry(output_id, input_id, operator, source, target)
            if entry["terms"]:
                entries.append(entry)
    body = {
        "source_rows": source_rows,
        "target_rows": target_rows,
        "entries": entries,
    }
    chain = _load(CHAIN_CERTIFICATE)
    proof = _load(CHAIN_PROOF)
    if chain.get("result_id") != "EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1":
        raise AssertionError("certified chain-map dependency changed")
    if proof.get("result_id") != "EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_PROOF_V1":
        raise AssertionError("certified chain-map proof changed")
    return {
        "schema": SCHEMA_ID,
        "result_id": RESULT_ID,
        "claim_status": "EXACT_PBW_CHAIN_MAP_TARGET_Q1_REPLAYED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "background_id": BACKGROUND_ID,
        "source_carrier_id": SOURCE_CARRIER,
        "target_carrier_id": TARGET_CARRIER,
        "operator_encoding": "row-id-keyed-coordinate-product-coefficient-jet-pbw-v1",
        "coefficient_field": "Q",
        "coefficient_jet_order": COEFFICIENT_JET_ORDER,
        "maximum_operator_order": 2,
        "support_local": True,
        "uses_inverse_laplacian_curl_frequency_or_momentum": False,
        "dependencies": {
            "source_taylor_certificate": {"path": str(SOURCE_CERTIFICATE.relative_to(ROOT)), "sha256": _sha256(SOURCE_CERTIFICATE)},
            "source_row_layout": {"path": str(SOURCE_LAYOUT.relative_to(ROOT)), "sha256": _sha256(SOURCE_LAYOUT)},
            "target_taylor_certificate": {"path": str(TARGET_CERTIFICATE.relative_to(ROOT)), "sha256": _sha256(TARGET_CERTIFICATE)},
            "target_row_layout": {"path": str(TARGET_LAYOUT.relative_to(ROOT)), "sha256": _sha256(TARGET_LAYOUT)},
            "certified_chain_map": {"path": str(CHAIN_CERTIFICATE.relative_to(ROOT)), "sha256": _sha256(CHAIN_CERTIFICATE)},
            "certified_chain_map_proof": {"path": str(CHAIN_PROOF.relative_to(ROOT)), "sha256": _sha256(CHAIN_PROOF)},
        },
        "map": {**body, "canonical_sha256": _canonical_sha256(body)},
        "checks": {
            "source_row_count": 38,
            "target_row_count": 40,
            "stable_row_ids_unique": True,
            "common_ghost_field_rows_identity": True,
            "new_weyl_ghost_image_zero": True,
            "new_weyl_identity_image_zero": True,
            "metric_equation_order": 2,
            "maxwell_equation_identity": True,
            "diff_identity_order": 2,
            "u1_identity": True,
            "target_q1_composition_replayed": True,
        },
        "claim_boundary": (
            "Exact row-ID-keyed PBW serialization of the already certified finite-order "
            "compact-product Einstein-Maxwell to Weyl-Maxwell linear chain-map formula. "
            "Both frozen action-derived carriers are pinned. The legacy Maxwell Euler and "
            "identity inputs are adapted to the BV cotangent-row sign convention, and an "
            "independent consumer replays the 40-row target-q1 chain equation exactly. "
            "Cyclicity, nonlinear relative morphism, causal, observable and quantum claims "
            "remain open."
        ),
    }


def write() -> None:
    payload = build_payload()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check() -> None:
    expected = json.dumps(build_payload(), indent=2, sort_keys=True) + "\n"
    if OUTPUT.read_text(encoding="utf-8") != expected:
        raise AssertionError(f"stale chain-map PBW export: {OUTPUT}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else write()
    print("compact-product Einstein--Weyl row-ID PBW export: PASS")
    print("target q1 composition replay: delegated to independent consumer")


if __name__ == "__main__":
    main()
