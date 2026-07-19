#!/usr/bin/env python3
"""Einstein-background metric Bach biwave Green homotopy.

The unit-Nariai coefficient certificate diagonalized the algebraic curvature
action because the background Weyl tensor is parallel.  That diagonalization
is useful but unnecessary.  On every four-dimensional Einstein background
with ``Ric=g`` the complete gauge-fixed trace-free Bach block is

    B_action + (1/2) K T = (1/2) L_E (L_E - 2/3),

where ``L_E = Box + 2 Cdot - 2/3``.  The two factors are normally
hyperbolic and differ by a scalar shift.  This module records the invariant
proof and independently calibrates all normalizations against the exact
unit-Nariai PBW operator.
"""

from __future__ import annotations

import argparse
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
    _sha256,
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


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-metric-biwave-green-homotopy.md"
PROOF = ROOT / "d_quotient_classical/proofs/einstein-metric-biwave-green-homotopy.md"
SCHEMA = ROOT / "d_quotient_classical/schema/einstein-metric-biwave-green-homotopy-v1.schema.json"
VERIFIER = HERE / "verify_einstein_metric_biwave_green_homotopy.py"
TESTS = HERE / "tests/test_einstein_metric_biwave_green_homotopy.py"

UNIT_NARIAI = ROOT / "d_quotient_classical/certificates/NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json"
COMMON_SLAB = ROOT / "d_quotient_classical/certificates/NARIAI_KS_COMMON_SLAB_CAUSAL_DOMAIN_V1.json"
ACTION_ENDPOINT = ROOT / "d_quotient_classical/certificates/NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1.json"


Expr = dict[tuple[int, ...], sp.Matrix]
Table = dict[tuple[int, ...], sp.Matrix]


def _linearized_cosmological_einstein(h, pbw) -> list[list[Expr]]:
    """Return delta(Ric - R g/2 + g) on a Ric=g background."""

    eta = NariaiBackground.metric
    _, ricci, contracted_ricci, _ = _linearized_curvatures(h, pbw)
    trace_h = _sum_expr(
        _expr_scale(h[a][a], eta[a, a]) for a in range(4)
    )
    delta_scalar = _expr_add(contracted_ricci, _expr_scale(trace_h, -1))
    return [
        [
            _expr_add(
                ricci[a][b],
                _expr_scale(delta_scalar, -sp.Rational(1, 2) * eta[a, b]),
                _expr_scale(h[a][b], -1),
            )
            for b in range(4)
        ]
        for a in range(4)
    ]


def _trace(tensor: list[list[Expr]]) -> Expr:
    eta = NariaiBackground.metric
    return _sum_expr(
        _expr_scale(tensor[a][a], eta[a, a]) for a in range(4)
    )


def _pauli_fierz_inverse(tensor: list[list[Expr]]) -> list[list[Expr]]:
    """F^{-1} t = t - g tr(t)/3 in four dimensions."""

    eta = NariaiBackground.metric
    trace = _trace(tensor)
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


def _tensor_coordinates(
    tensor: list[list[Expr]], left_inverse: sp.Matrix
) -> Table:
    output: dict[tuple[int, ...], sp.Matrix] = defaultdict(lambda: sp.zeros(9))
    for coordinate in range(9):
        for a in range(4):
            for b in range(4):
                coefficient = left_inverse[coordinate, 4 * a + b]
                if coefficient == 0:
                    continue
                for word, row in tensor[a][b].items():
                    output[word][coordinate, :] += coefficient * row
    return {
        word: matrix.applyfunc(sp.expand)
        for word, matrix in output.items()
        if matrix != sp.zeros(9)
    }


def _weyl_action_matrix(carrier: sp.Matrix, left_inverse: sp.Matrix) -> sp.Matrix:
    eta = NariaiBackground.metric
    tensor = sp.zeros(16, 9)
    for a in range(4):
        for b in range(4):
            row = sp.zeros(1, 9)
            for c in range(4):
                for d in range(4):
                    row += (
                        _nariai_weyl(a, c, b, d)
                        * eta[c, c]
                        * eta[d, d]
                        * carrier[4 * c + d, :]
                    )
            tensor[4 * a + b, :] = row
    return (left_inverse * tensor).applyfunc(sp.expand)


def exact_calibration() -> dict[str, object]:
    """Replay the invariant identities in the exact unit-Nariai PBW algebra."""

    middle = middle_fixture()
    pbw = middle["pbw_h1"]
    h, carrier, gram, left_inverse = _h_basis(middle["algebraic"])
    einstein = _linearized_cosmological_einstein(h, pbw)
    einstein_pf_einstein = _linearized_cosmological_einstein(
        _pauli_fierz_inverse(einstein), pbw
    )
    einstein_coordinates = _tensor_coordinates(einstein, left_inverse)
    quadratic_coordinates = _tensor_coordinates(
        einstein_pf_einstein, left_inverse
    )
    einstein_covector = {
        word: (gram * matrix).applyfunc(sp.expand)
        for word, matrix in einstein_coordinates.items()
    }
    quadratic_covector = {
        word: (gram * matrix).applyfunc(sp.expand)
        for word, matrix in quadratic_coordinates.items()
    }
    standard_bach = endpoint_operator()["standard_bach_covector"]

    alpha, beta = sp.symbols("alpha beta")
    equations = []
    for word in set(standard_bach) | set(einstein_covector) | set(quadratic_covector):
        defect = (
            alpha * quadratic_covector.get(word, sp.zeros(9))
            + beta * einstein_covector.get(word, sp.zeros(9))
            - standard_bach.get(word, sp.zeros(9))
        )
        equations.extend(value for value in defect if value != 0)
    linear, rhs = sp.linear_eq_to_matrix(equations, (alpha, beta))
    solution = sp.linsolve((linear, rhs), (alpha, beta))
    expected_solution = sp.FiniteSet((-sp.Integer(1), -sp.Rational(1, 3)))
    if solution != expected_solution:
        raise AssertionError(f"Einstein detour normalization drifted: {solution}")

    fixture = metric_fixture()
    factor_einstein, factor_pm = fixture["metric_factors"]
    factor_einstein_matrix = fixture["factor_a_matrix"]
    factor_pm_matrix = fixture["factor_b_matrix"]
    weyl_action = _weyl_action_matrix(carrier, left_inverse)
    expected_einstein_matrix = (
        2 * weyl_action - sp.Rational(2, 3) * sp.eye(9)
    ).applyfunc(sp.expand)
    if factor_einstein_matrix != expected_einstein_matrix:
        raise AssertionError("Nariai factor is not the invariant Einstein wave")
    if factor_pm_matrix != factor_einstein_matrix - sp.Rational(2, 3) * sp.eye(9):
        raise AssertionError("partially-massless factor is not the scalar shift")

    basic = _basic_operators(fixture["coefficient"])
    k_div = pbw.compose(middle["first_bgg"], basic["divergence"])
    gauge_fixed_einstein = _add(
        _scale(einstein_coordinates, -2), k_div
    )
    gauge_fixed_defect = _add(
        gauge_fixed_einstein, _scale(factor_einstein, -1)
    )
    factor_shift_defect = _add(
        factor_pm,
        _scale(factor_einstein, -1),
        {(): sp.Rational(2, 3) * sp.eye(9)},
    )

    return {
        "detour_coefficient_rank": linear.rank(),
        "detour_augmented_rank": linear.row_join(rhs).rank(),
        "detour_solution": ["-1", "-1/3"],
        "weyl_action_eigenvalues": {
            str(value): multiplicity
            for value, multiplicity in weyl_action.eigenvals().items()
        },
        "weyl_action_pairing_defect_rank": (
            gram * weyl_action - weyl_action.T * gram
        ).rank(),
        "einstein_factor_invariant_defect_rank": (
            factor_einstein_matrix - expected_einstein_matrix
        ).rank(),
        "gauge_fixed_einstein_defect_entries": _entry_count(gauge_fixed_defect),
        "partially_massless_scalar_shift_defect_entries": _entry_count(
            factor_shift_defect
        ),
        "existing_metric_factorization_defect_entries": fixture["checks"][
            "metric_factorization_defect_entries"
        ],
        "factor_commutator_defect_entries": fixture["checks"][
            "metric_factor_order_commutator_entries"
        ],
        "factor_adjoint_defect_entries": fixture["checks"][
            "factor_a_formal_adjoint_defect_entries"
        ]
        + fixture["checks"]["factor_b_formal_adjoint_defect_entries"],
    }


def _dependency(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "artifact_id": value["result_id"],
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def build() -> dict[str, object]:
    unit = json.loads(UNIT_NARIAI.read_text())
    slab = json.loads(COMMON_SLAB.read_text())
    action = json.loads(ACTION_ENDPOINT.read_text())
    if unit["flags"]["NARIAI_METRIC_GREEN_HOMOTOPY"] is not True:
        raise ValueError("unit-Nariai metric Green theorem unavailable")
    if slab["flags"]["KS_COMMON_REFERENCE_CAUSAL_CONE"] is not True:
        raise ValueError("Kantowski--Sachs common slab unavailable")
    if action["flags"]["NARIAI_METRIC_BACH_ENDPOINT_EXACT"] is not True:
        raise ValueError("action-derived Bach normalization unavailable")

    checks = exact_calibration()
    if checks["detour_coefficient_rank"] != checks["detour_augmented_rank"] or checks[
        "detour_coefficient_rank"
    ] != 2:
        raise AssertionError("Einstein detour normalization is not unique")
    for name, value in checks.items():
        if (name.endswith("_entries") or name.endswith("_defect_rank")) and value:
            raise AssertionError(f"nonzero exact calibration defect: {name}={value}")

    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (
            Path(__file__).resolve(),
            VERIFIER,
            TESTS,
            SCHEMA,
            PROOF,
        )
    }
    return {
        "schema": "pure-weyl-einstein-metric-biwave-green-homotopy-v1",
        "result_id": "EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1",
        "result_state": "EINSTEIN_BACKGROUND_FOUR_ROW_METRIC_CAUSAL_GREEN_HOMOTOPY_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            "unit_nariai_metric": _dependency(UNIT_NARIAI),
            "unit_nariai_action_endpoint": _dependency(ACTION_ENDPOINT),
            "kantowski_sachs_common_slab": _dependency(COMMON_SLAB),
        },
        "scope": {
            "dimension": 4,
            "background_equation": "Ric(g)=g",
            "spacetime": "any oriented time-oriented globally hyperbolic Einstein background in the declared normalization",
            "field_bundle": "S^2_0 T* with the metric Bach four-row BV complex",
            "kantowski_sachs_application": "every certified common slab (-T,T) x S1 x S2 for |epsilon|<delta_T",
        },
        "invariant_operators": {
            "cosmological_Einstein": "G(h)=delta[Ric-(1/2)R g+g](h)",
            "Pauli_Fierz_inverse": "F^{-1}(t)=t-(1/3)g tr(t)",
            "Weyl_action": "(Cdot h)_ab=C_a^c_b^d h_cd",
            "gauge_fixed_Einstein": "L_E=-2 Pi_TF G+K div=Box+2 Cdot-2/3",
            "partially_massless": "L_PM=L_E-2/3=Box+2 Cdot-4/3",
            "companion": "T=Box div-(1/3)d div div+(1/3)div",
        },
        "exact_identities": {
            "Einstein_detour": "B_standard=-G F^{-1} G-(1/3)G",
            "action_normalization": "B_action=-2 B_standard",
            "ghost_factorization": "T K=(Box+1)(Box+1/3) on T*",
            "metric_factorization": "B_action+(1/2)K T=(1/2)L_E L_PM",
            "factor_commutation": "[L_E,L_PM]=0 because L_PM=L_E-(2/3)I",
            "principal_symbols": "sigma_2(L_E)=sigma_2(L_PM)=g^{-1}(zeta,zeta)I",
        },
        "unit_nariai_exact_calibration": checks,
        "causal_construction": {
            "normal_hyperbolicity": "the Weyl actions and scalar shifts are zeroth order, so both metric factors and both ghost factors are normally hyperbolic",
            "metric_Green_formula": "G_metric,+/-=2 G_PM,+/- G_E,+/-",
            "ghost_Green_formula": "G_ghost,+/-=G_(Box+1/3),+/- G_(Box+1),+/-",
            "support": "each same-sided composition has support in J^+ or J^- of the source",
            "inverse_identities": "factor commutation and uniqueness give both left and right inverse identities",
            "adjoint_reversal": "formal self-adjointness gives G_E,+^sharp=G_E,- and G_PM,+^sharp=G_PM,-; complementary BV degrees use the certified pairing sign",
            "four_row_homotopy": "the certified metric witness formula applies unchanged with the displayed Einstein factors",
        },
        "exact_checks": checks,
        "flags": {
            "EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1": True,
            "FOUR_DIMENSIONAL_EINSTEIN_METRIC_BIWAVE_THEOREM": True,
            "KANTOWSKI_SACHS_COMMON_SLAB_METRIC_GREEN_HOMOTOPY": True,
            "VARIABLE_WEYL_ALLOWED": True,
            "PARALLEL_WEYL_REQUIRED": False,
            "KANTOWSKI_SACHS_RANK310_GEOMETRIC_BINDING": False,
            "KANTOWSKI_SACHS_RANK310_GREEN_TRANSFER": False,
            "NON_EINSTEIN_BACH_FLAT_METRIC_THEOREM": False,
            "HADAMARD_STATE": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": {
            "statement": "The complete gauge-fixed four-row trace-free metric Bach complex has causal Green homotopies on every globally hyperbolic four-dimensional Einstein background with Ric=g. In particular, the theorem applies on every certified common Kantowski--Sachs slab. The proof uses the invariant Einstein/partially-massless biwave identity, not parallel-Weyl diagonalization.",
            "not_claimed": [
                "coefficient-complete binding of the six rank-310 HPL differences",
                "rank-310 Green transfer away from unit Nariai",
                "a non-Einstein Bach-flat metric endpoint theorem",
                "a whole-cylinder nonzero Kantowski--Sachs family",
                "Hadamard states or renormalized time-ordered products",
                "nonlinear or quantum claims",
            ],
        },
        "next_gate": "NARIAI_KS_RANK310_SIX_BLOCK_GEOMETRIC_COEFFICIENT_BINDING",
        "source_manifest": sources,
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/einstein_metric_biwave_green_homotopy.py --write --guards",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/einstein-metric-biwave-green-homotopy-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json",
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_einstein_metric_biwave_green_homotopy.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_einstein_metric_biwave_green_homotopy",
        ],
    }


def _report(value: dict[str, object]) -> str:
    return r"""# Einstein-background metric biwave Green homotopy

The unit-Nariai factorization does not rely on parallel Weyl curvature.  On
every four-dimensional Einstein background in the normalization `Ric=g`, the
gauge-fixed Einstein and partially-massless factors are

\[
L_E=\Box+2C\!\cdot-\frac23,
\qquad
L_{\rm PM}=L_E-\frac23.
\]

The exact invariant identity is

\[
B_{\rm action}+\frac12KT=\frac12L_E L_{\rm PM},
\qquad
T=\Box\operatorname{div}-\frac13d\operatorname{div}\operatorname{div}
  +\frac13\operatorname{div}.
\]

Both factors have scalar metric principal symbol.  The Weyl action is
zeroth-order and pairing-self-adjoint, and the two factors commute because
they differ by a scalar multiple of the identity.  Their same-sided Green
compositions therefore give both inverse identities and causal support.  The
ghost block retains the Einstein factorization
`(Box+1)(Box+1/3)`.

The normalization was replayed coefficientwise in the exact unit-Nariai PBW
algebra.  The unique detour coefficients are `(-1,-1/3)`, the common factor
is exactly `-2 Pi_TF G+K div`, and every factorization, adjoint and scalar-shift
defect vanishes.

Every metric in the certified Kantowski--Sachs common-slab family satisfies
`Ric=g`; hence this theorem closes its 30-component metric endpoint without
assuming `nabla C=0`.  It does not yet bind the six geometric operator
differences in the rank-310 HPL presentation, so the all-row transfer remains
fail-closed.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator(schema).validate(value)
    if args.guards:
        if value["flags"]["KANTOWSKI_SACHS_RANK310_GREEN_TRANSFER"]:
            raise AssertionError("rank-310 transfer was overpromoted")
        if value["flags"]["NON_EINSTEIN_BACH_FLAT_METRIC_THEOREM"]:
            raise AssertionError("Einstein theorem escaped its scope")
    serialized = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(serialized)
        REPORT.write_text(_report(value))
    if args.check and OUTPUT.read_text() != serialized:
        raise AssertionError("Einstein metric biwave certificate drifted")
    print(value["result_id"])


if __name__ == "__main__":
    main()
