#!/usr/bin/env python3
"""Independent consumer for the Einstein metric biwave theorem."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    _add,
    _scale,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    NariaiBackground,
    ROOT,
)
from d_quotient_classical.causal_transfer.nariai_linearized_bach_endpoint import (
    _expr_add,
    _expr_scale,
    _h_basis,
    _linearized_curvatures,
    _nariai_weyl,
    _sum_expr,
    endpoint_operator,
)
from d_quotient_classical.causal_transfer.nariai_metric_biwave_green_homotopy import (
    _basic_operators,
    fixture as metric_fixture,
)
from d_quotient_classical.causal_transfer.nariai_parent_detour_mapping_cone_repair import (
    _entry_count,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import (
    fixture as middle_fixture,
)


OUTPUT = ROOT / "d_quotient_classical/certificates/EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/einstein-metric-biwave-green-homotopy-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _coordinates(tensor, left_inverse):
    output = defaultdict(lambda: sp.zeros(9))
    for coordinate in range(9):
        for a in range(4):
            for b in range(4):
                coefficient = left_inverse[coordinate, 4 * a + b]
                if coefficient:
                    for word, row in tensor[a][b].items():
                        output[word][coordinate, :] += coefficient * row
    return {
        word: matrix.applyfunc(sp.expand)
        for word, matrix in output.items()
        if matrix != sp.zeros(9)
    }


def _linearized_einstein(h, pbw):
    eta = NariaiBackground.metric
    _, ricci, contracted, _ = _linearized_curvatures(h, pbw)
    trace = _sum_expr(
        _expr_scale(h[a][a], eta[a, a]) for a in range(4)
    )
    delta_r = _expr_add(contracted, _expr_scale(trace, -1))
    return [
        [
            _expr_add(
                ricci[a][b],
                _expr_scale(delta_r, -sp.Rational(1, 2) * eta[a, b]),
                _expr_scale(h[a][b], -1),
            )
            for b in range(4)
        ]
        for a in range(4)
    ]


def _pf_inverse(tensor):
    eta = NariaiBackground.metric
    trace = _sum_expr(
        _expr_scale(tensor[a][a], eta[a, a]) for a in range(4)
    )
    return [
        [
            _expr_add(
                tensor[a][b],
                _expr_scale(trace, -sp.Rational(1, 3) * eta[a, b]),
            )
            for b in range(4)
        ]
        for a in range(4)
    ]


def verify() -> None:
    value = json.loads(OUTPUT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    for dependency in value["dependency_refs"].values():
        if _sha(ROOT / dependency["path"]) != dependency["sha256"]:
            raise AssertionError(f"dependency drifted: {dependency['artifact_id']}")
    for relative, digest in value["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise AssertionError(f"source drifted: {relative}")

    middle = middle_fixture()
    pbw = middle["pbw_h1"]
    eta = NariaiBackground.metric
    h, carrier, gram, left_inverse = _h_basis(middle["algebraic"])
    einstein_tensor = _linearized_einstein(h, pbw)
    einstein = _coordinates(einstein_tensor, left_inverse)
    quadratic = _coordinates(
        _linearized_einstein(_pf_inverse(einstein_tensor), pbw), left_inverse
    )
    einstein_covector = {word: gram * matrix for word, matrix in einstein.items()}
    quadratic_covector = {word: gram * matrix for word, matrix in quadratic.items()}
    standard_bach = endpoint_operator()["standard_bach_covector"]
    detour_defect = _add(
        standard_bach,
        quadratic_covector,
        _scale(einstein_covector, sp.Rational(1, 3)),
    )
    if _entry_count(detour_defect):
        raise AssertionError("serialized Einstein detour normalization failed")

    weyl_tensor = sp.zeros(16, 9)
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    weyl_tensor[4 * a + b, :] += (
                        _nariai_weyl(a, c, b, d)
                        * eta[c, c]
                        * eta[d, d]
                        * carrier[4 * c + d, :]
                    )
    weyl_action = (left_inverse * weyl_tensor).applyfunc(sp.expand)

    fixture = metric_fixture()
    factor_e, factor_pm = fixture["metric_factors"]
    expected_matrix = 2 * weyl_action - sp.Rational(2, 3) * sp.eye(9)
    if fixture["factor_a_matrix"] != expected_matrix:
        raise AssertionError("Einstein wave failed invariant Weyl reconstruction")
    if fixture["factor_b_matrix"] != expected_matrix - sp.Rational(2, 3) * sp.eye(9):
        raise AssertionError("partially-massless scalar shift failed")
    if gram * weyl_action != weyl_action.T * gram:
        raise AssertionError("Weyl action is not pairing self-adjoint")

    divergence = _basic_operators(fixture["coefficient"])["divergence"]
    k_div = pbw.compose(middle["first_bgg"], divergence)
    gauge_fixed = _add(_scale(einstein, -2), k_div)
    if _entry_count(_add(gauge_fixed, _scale(factor_e, -1))):
        raise AssertionError("L_E=-2 Pi_TF G+K div failed")
    shifted = _add(
        factor_pm,
        _scale(factor_e, -1),
        {(): sp.Rational(2, 3) * sp.eye(9)},
    )
    if _entry_count(shifted):
        raise AssertionError("factor scalar-shift identity failed")

    flags = value["flags"]
    if flags["KANTOWSKI_SACHS_COMMON_SLAB_METRIC_GREEN_HOMOTOPY"] is not True:
        raise AssertionError("common-slab metric theorem was not promoted")
    if flags["KANTOWSKI_SACHS_RANK310_GREEN_TRANSFER"] is not False:
        raise AssertionError("rank-310 transfer was overpromoted")
    if flags["NON_EINSTEIN_BACH_FLAT_METRIC_THEOREM"] is not False:
        raise AssertionError("Einstein theorem escaped its scope")
    print("EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1: independently verified")


if __name__ == "__main__":
    verify()
