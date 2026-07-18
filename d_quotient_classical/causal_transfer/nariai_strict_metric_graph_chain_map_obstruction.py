#!/usr/bin/env python3
"""All-order obstruction to a strict metric graph in the Nariai cylinder.

The canonical endpoint ghost embedding is

``xi -> (epsilon=L0 xi, chi=K xi)``.

If a strict metric field graph retains the metric coordinate and has parent
connection component ``a=R h``, its first chain square necessarily requires

``R K = I_Omega``.

This file proves that no finite-order differential ``R`` can satisfy that
identity.  The proof is not an order-bounded ansatz: the Nariai Killing field
``partial_chi`` lies in ``ker K`` while ``I_Omega partial_chi`` is nonzero.
PBW screens through order four are included only as exact regression data.
"""

from __future__ import annotations

import argparse
from itertools import combinations_with_replacement
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_curvature_incidence_first_square import (
    OUTPUT as INCIDENCE_CERTIFICATE,
    curvature_incidence,
)
from d_quotient_classical.causal_transfer import nariai_curvature_incidence_first_square as incidence_module
from d_quotient_classical.causal_transfer.nariai_curvature_incidence_cyclic_mapping_cylinder import (
    OUTPUT as CYLINDER_CERTIFICATE,
)
from d_quotient_classical.causal_transfer import nariai_curvature_incidence_cyclic_mapping_cylinder as cylinder_module
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    ROOT,
    _sha256,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import (
    fixture as middle_fixture,
)
from d_quotient_classical.causal_transfer import nariai_yang_mills_middle_compression as middle_module
from covariant_completion.curved_operator import adjoint_tractor_bgg_curved_pbw as pbw_module


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_STRICT_METRIC_GRAPH_CHAIN_MAP_OBSTRUCTION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-strict-metric-graph-chain-map-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-strict-metric-graph-chain-map-obstruction-v1.schema.json"
VERIFIER = HERE / "verify_nariai_strict_metric_graph_chain_map_obstruction.py"
TESTS = HERE / "tests/test_nariai_strict_metric_graph_chain_map_obstruction.py"


def _coordinate_killing_check() -> dict[str, object]:
    """Check ``partial_chi`` is Killing in a unit-Nariai chart.

    We use

    ``g=-dt^2+cosh(t)^2 dchi^2+dtheta^2+sin(theta)^2 dphi^2``.

    At ``t=0, theta=pi/2`` the coordinate vector ``partial_chi`` is the
    certified orthonormal-frame vector ``e_1``.
    """

    t, chi, theta, phi = sp.symbols("t chi theta phi", real=True)
    coordinates = (t, chi, theta, phi)
    metric = sp.diag(-1, sp.cosh(t) ** 2, 1, sp.sin(theta) ** 2)
    vector = sp.Matrix([0, 1, 0, 0])
    lie = sp.zeros(4)
    for a in range(4):
        for b in range(4):
            lie[a, b] = sp.simplify(
                sum(vector[c] * sp.diff(metric[a, b], coordinates[c]) for c in range(4))
                + sum(metric[c, b] * sp.diff(vector[c], coordinates[a]) for c in range(4))
                + sum(metric[a, c] * sp.diff(vector[c], coordinates[b]) for c in range(4))
            )
    base_metric = metric.subs({t: 0, theta: sp.pi / 2})
    if lie != sp.zeros(4):
        raise AssertionError("partial_chi is not Killing in the declared chart")
    if base_metric != sp.diag(-1, 1, 1, 1):
        raise AssertionError("coordinate and orthonormal Nariai frames drifted")
    return {
        "chart": "g=-dt^2+cosh(t)^2 dchi^2+dtheta^2+sin(theta)^2 dphi^2",
        "field": "xi=partial_chi",
        "basepoint": "t=0, theta=pi/2",
        "lie_derivative_nonzero_entries": 0,
        "K_xi": "zero section",
        "orthonormal_value": [0, 1, 0, 0],
    }


def _flatten(
    table: dict[tuple[int, ...], sp.Matrix],
    words: tuple[tuple[int, ...], ...],
) -> sp.Matrix:
    return sp.Matrix(
        [
            table.get(word, sp.zeros(1, 4))[0, component]
            for word in words
            for component in range(4)
        ]
    )


def _pbw_order_screen(maximum_order: int = 4) -> list[dict[str, int]]:
    """Return exact finite-order regressions for ``R K=I_Omega``.

    The same coefficient map applies independently to every one of the sixty
    parent output rows.  Appending all sixty incidence rows raises its rank by
    four at every tested order.  This is deliberately secondary evidence;
    the Killing-kernel argument proves the all-order theorem.
    """

    middle = middle_fixture()
    first_bgg = middle["first_bgg"]
    pbw = middle["pbw_h0"]
    incidence = curvature_incidence()["incidence"]
    output: list[dict[str, int]] = []
    for order in range(maximum_order + 1):
        operator_words = tuple(
            word
            for degree in range(order + 1)
            for word in combinations_with_replacement(range(4), degree)
        )
        columns: list[dict[tuple[int, ...], sp.Matrix]] = []
        normal_words: set[tuple[int, ...]] = {()}
        for word in operator_words:
            for middle_component in range(9):
                coefficient = sp.zeros(1, 9)
                coefficient[0, middle_component] = 1
                image = pbw.compose({word: coefficient}, first_bgg)
                columns.append(image)
                normal_words.update(image)
        ordered_normal_words = tuple(
            sorted(normal_words, key=lambda value: (len(value), value))
        )
        matrix = sp.Matrix.hstack(
            *(_flatten(column, ordered_normal_words) for column in columns)
        )
        targets = sp.Matrix.hstack(
            *(
                _flatten({(): incidence[row : row + 1, :]}, ordered_normal_words)
                for row in range(60)
            )
        )
        rank = matrix.rank()
        augmented_rank = matrix.row_join(targets).rank()
        output.append(
            {
                "maximum_order": order,
                "unknown_coefficients_per_output_row": matrix.cols,
                "normal_form_equations_per_output_row": matrix.rows,
                "coefficient_rank": rank,
                "augmented_rank": augmented_rank,
                "rank_gap": augmented_rank - rank,
            }
        )
    return output


def build() -> dict[str, object]:
    incidence_dependency = json.loads(INCIDENCE_CERTIFICATE.read_text())
    cylinder_dependency = json.loads(CYLINDER_CERTIFICATE.read_text())
    if incidence_dependency["flags"]["CURVATURE_INCIDENCE_IDENTITY_EXACT"] is not True:
        raise ValueError("curvature-incidence dependency unavailable")
    if cylinder_dependency["flags"]["CYCLIC_CURVATURE_INCIDENCE_MAPPING_CONE"] is not True:
        raise ValueError("cyclic incidence cylinder unavailable")

    coordinate = _coordinate_killing_check()
    incidence = curvature_incidence()["incidence"]
    killing_value = sp.Matrix(coordinate["orthonormal_value"])
    image = incidence * killing_value
    if image == sp.zeros(60, 1):
        raise AssertionError("chosen Nariai Killing value missed the incidence")
    if image[4] != sp.Rational(2, 3):
        raise AssertionError("normalized curvature-incidence witness drifted")
    screens = _pbw_order_screen()
    if [entry["rank_gap"] for entry in screens] != [4, 4, 4, 4, 4]:
        raise AssertionError("finite-order PBW regression drifted")

    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (
            Path(__file__).resolve(),
            VERIFIER,
            TESTS,
            SCHEMA,
            Path(incidence_module.__file__).resolve(),
            Path(cylinder_module.__file__).resolve(),
            Path(middle_module.__file__).resolve(),
            Path(pbw_module.__file__).resolve(),
        )
    }
    return {
        "schema": "pure-weyl-nariai-strict-metric-graph-chain-map-obstruction-v1",
        "result_id": "NARIAI_STRICT_METRIC_GRAPH_CHAIN_MAP_OBSTRUCTION_V1",
        "result_state": "STRICT_CANONICAL_METRIC_GRAPH_CHAIN_MAP_OBSTRUCTED_AT_ALL_DIFFERENTIAL_ORDERS",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "curvature_incidence": {
                "artifact_id": incidence_dependency["result_id"],
                "path": str(INCIDENCE_CERTIFICATE.relative_to(ROOT)),
                "sha256": _sha256(INCIDENCE_CERTIFICATE),
            },
            "cyclic_mapping_cylinder": {
                "artifact_id": cylinder_dependency["result_id"],
                "path": str(CYLINDER_CERTIFICATE.relative_to(ROOT)),
                "sha256": _sha256(CYLINDER_CERTIFICATE),
            },
        },
        "typed_chain_condition": {
            "canonical_ghost_embedding": "xi -> (epsilon=L0 xi,chi=K xi)",
            "strict_metric_graph": "h -> (h,a=R h)",
            "necessary_equation": "R K=I_Omega",
            "operator_type": "R:H1[9]->C1[60], arbitrary finite differential order",
            "reason": "the h component already matches K xi; equality of the a component forces R K xi=I_Omega xi",
        },
        "all_order_witness": {
            **coordinate,
            "incidence_image_nonzero_entries": sum(value != 0 for value in image),
            "incidence_image_entries": [
                [row, str(value)] for row, value in enumerate(image) if value != 0
            ],
            "normalized_witness": "(3/2)*(I_Omega partial_chi)[4]",
            "normalized_witness_value": "1",
            "contradiction": "R K partial_chi=R(0)=0 but I_Omega partial_chi is nonzero",
            "independent_of_order_and_coefficients": True,
        },
        "pbw_regression": {
            "role": "finite exact regression only, not the proof of all-order nonexistence",
            "screens": screens,
        },
        "exact_checks": {
            "partial_chi_is_global_Killing": True,
            "K_partial_chi_is_zero_section": True,
            "I_Omega_partial_chi_is_nonzero": True,
            "normalized_witness_value": "1",
            "all_order_contradiction": True,
            "pbw_orders_tested": [0, 1, 2, 3, 4],
            "pbw_rank_gaps": [entry["rank_gap"] for entry in screens],
        },
        "theorem": {
            "statement": "No linear operator R:H1->C1 can satisfy R K=I_Omega on unit Nariai; in particular, none exists at any finite differential order. Hence the canonical ghost embedding cannot extend to a strict metric graph h->(h,Rh) in the certified curvature-incidence cylinder.",
            "proof": "The global Killing field partial_chi obeys K partial_chi=0. At the certified homogeneous basepoint its value is e1, and the exact incidence table gives (I_Omega e1)[4]=2/3. Applying a differential operator to the zero section is zero, contradicting R K=I_Omega.",
            "scope": "canonical ghost embedding, identity metric component, and a field-only finite-order graph component R",
        },
        "flags": {
            "NARIAI_STRICT_METRIC_GRAPH_CHAIN_MAP_OBSTRUCTION_V1": True,
            "STRICT_CANONICAL_METRIC_GRAPH_CHAIN_MAP_EXISTS": False,
            "ALL_FINITE_DIFFERENTIAL_ORDERS_EXCLUDED": True,
            "RELATIVE_EQUATION_LEVEL_METRIC_CONE_STILL_OPEN": True,
            "METRIC_BACH_ENDPOINT_CHAIN_EQUIVALENCE": False,
            "NARIAI_GREEN_HOMOTOPY": False,
            "OPEN_BACKGROUND_CLASS": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "C_G2_NARIAI_RELATIVE_EQUATION_LEVEL_METRIC_BACH_ENDPOINT_CONE",
        "claim_boundary": (
            "This theorem excludes every linear field-only graph h->(h,Rh), and in "
            "particular every finite-order differential graph, "
            "that extends the certified canonical ghost embedding and retains the "
            "metric coordinate identically. It is stronger than an ansatz or bounded-order "
            "rank failure. It does not exclude a relative equation-level chain morphism, "
            "a homotopy-coherent/A-infinity BGG translation, an enlarged mapping cylinder, "
            "a map with different endpoint incidence, or an independently constructed metric "
            "Green homotopy. No metric-Bach equivalence, causal, open-family, nonlinear, or "
            "quantum claim is promoted."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_strict_metric_graph_chain_map_obstruction.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_strict_metric_graph_chain_map_obstruction.py",
                "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_strict_metric_graph_chain_map_obstruction",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-strict-metric-graph-chain-map-obstruction-v1.schema.json -d d_quotient_classical/certificates/NARIAI_STRICT_METRIC_GRAPH_CHAIN_MAP_OBSTRUCTION_V1.json",
            ],
        },
    }


def render(value: dict[str, object]) -> str:
    witness = value["all_order_witness"]
    return rf"""# Nariai strict metric-graph chain-map obstruction

## Result

The canonical endpoint ghost map into the cyclic incidence cylinder is

\[
\xi\longmapsto (L_0\xi,K\xi).
\]

A strict field graph retaining the metric coordinate,

\[
h\longmapsto(h,Rh),
\]

would therefore have to satisfy

\[
RK=I_\Omega.
\]

No finite-order differential operator \(R:H_1\to C_1\) can satisfy this
identity on unit Nariai.  In the global chart

\[
g=-dt^2+\cosh^2t\,d\chi^2+d\theta^2+\sin^2\theta\,d\phi^2,
\]

the field \(\xi=\partial_\chi\) is Killing, hence \(K\xi=0\).  At
\(t=0,\theta=\pi/2\), its orthonormal-frame value is \(e_1\), while the
certified incidence gives

\[
(I_\Omega e_1)_4=\frac23,
\qquad
\frac32(I_\Omega e_1)_4={witness['normalized_witness_value']}.
\]

Thus \(RK\xi=R(0)=0\) but \(I_\Omega\xi\ne0\).  The contradiction is
independent of the differential order and coefficients of \(R\).

As a regression, complete curved-PBW coefficient screens at orders zero
through four have augmented-rank gaps
`{value['exact_checks']['pbw_rank_gaps']}`.  These finite screens are not used
to infer the all-order theorem.

## Consequence

The next admissible comparison is a relative equation-level or
homotopy-coherent metric--Bach cone.  Repeating field-only graph ansatzes at
higher order cannot succeed.

## Boundary

{value['claim_boundary']}
"""


def verify(value: dict[str, object]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("certificate drifted from exact reconstruction")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if args.guards:
        checks = value["exact_checks"]
        if checks["all_order_contradiction"] is not True:
            raise AssertionError("all-order obstruction guard failed")
        if checks["pbw_rank_gaps"] != [4, 4, 4, 4, 4]:
            raise AssertionError("PBW rank regression guard failed")
        if value["flags"]["METRIC_BACH_ENDPOINT_CHAIN_EQUIVALENCE"] is not False:
            raise AssertionError("metric endpoint was overpromoted")
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    report = render(value)
    if args.write:
        OUTPUT.write_text(encoded)
        REPORT.write_text(report)
    if args.check and (
        not OUTPUT.exists()
        or not REPORT.exists()
        or OUTPUT.read_text() != encoded
        or REPORT.read_text() != report
    ):
        raise SystemExit("generated strict-metric-graph artifacts drifted")
    print(f"{value['result_id']}: PASS")


if __name__ == "__main__":
    main()
