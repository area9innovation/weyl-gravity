#!/usr/bin/env python3
"""Curvature-corrected Nariai automorphism prolongation, first two rows.

The normal-adjoint-tractor differential detects parallel tractors and misses
metric Killing reducibilities on Nariai.  Correct it by the curvature
incidence

    d_aut = d^D - I_Omega p_0.

Together with the metric component K p_0 and the shifted equation map
Phi=M^D L_1, this gives the strict local complex

    C0 --(d_aut,Kp0)--> C1+H1 --(M^D,-Phi)--> C1*.

The corrected BGG graph (L0;L1,1) commutes exactly through the gauge row.
This module deliberately stops before the Bach equation and cyclic cotangent
completion.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_kostant_compression import (
    _adjoint_basis,
)
from covariant_completion.curved_operator.adjoint_tractor_bgg_differential_screen import (
    _adjoint_actions,
)
from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    FibrePBW,
    _add,
    _algebraic,
    _scale,
    _tensor_product_curvature,
)
from d_quotient_classical.causal_transfer.nariai_curvature_incidence_first_square import (
    curvature_incidence,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    NariaiBackground,
    ROOT,
    _derivative_rows,
    _lc_adjoint_curvature,
    _sha256,
    _sparse_table,
    candidate,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import (
    fixture as middle_fixture,
)


HERE = ROOT / "d_quotient_classical/causal_transfer"
MISMATCH = ROOT / "d_quotient_classical/certificates/NARIAI_PARENT_REDUCIBILITY_MISMATCH_V1.json"
INCIDENCE = ROOT / "d_quotient_classical/certificates/NARIAI_CURVATURE_INCIDENCE_FIRST_SQUARE_V1.json"
SHIFTED = ROOT / "d_quotient_classical/certificates/NARIAI_CURVATURE_INCIDENCE_SHIFTED_CHAIN_V1.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_AUTOMORPHISM_PROLONGATION_FIRST_TWO_ROWS_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-automorphism-prolongation-first-two-rows.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-automorphism-prolongation-first-two-rows-v1.schema.json"
VERIFIER = HERE / "verify_nariai_automorphism_prolongation_first_two_rows.py"
TESTS = HERE / "tests/test_nariai_automorphism_prolongation_first_two_rows.py"
INCIDENCE_PRODUCER = HERE / "nariai_curvature_incidence_first_square.py"
SHIFTED_PRODUCER = HERE / "nariai_curvature_incidence_shifted_chain.py"
MIDDLE_PRODUCER = HERE / "nariai_yang_mills_middle_compression.py"
STRICT_PRODUCER = HERE / "nariai_first_differential_bgg_correction.py"
PBW_SOURCE = ROOT / "covariant_completion/curved_operator/adjoint_tractor_bgg_curved_pbw.py"


Table = dict[tuple[int, ...], sp.Matrix]


def _count(table: Table) -> int:
    return sum(value != 0 for matrix in table.values() for value in matrix)


def _clean(table: Table) -> Table:
    return {
        word: matrix.applyfunc(sp.expand)
        for word, matrix in table.items()
        if matrix != sp.zeros(*matrix.shape)
    }


def _vertical(top: Table, bottom: Table) -> Table:
    top_sample = next(iter(top.values()))
    bottom_sample = next(iter(bottom.values()))
    if top_sample.cols != bottom_sample.cols:
        raise AssertionError("vertical operator blocks have different inputs")
    words = set(top) | set(bottom)
    return _clean(
        {
            word: sp.Matrix.vstack(
                top.get(word, sp.zeros(top_sample.rows, top_sample.cols)),
                bottom.get(word, sp.zeros(bottom_sample.rows, bottom_sample.cols)),
            )
            for word in words
        }
    )


def _horizontal(left: Table, right: Table) -> Table:
    words = set(left) | set(right)
    return _clean(
        {
            word: sp.Matrix.hstack(
                left.get(word, sp.zeros(60, 60)),
                right.get(word, sp.zeros(60, 9)),
            )
            for word in words
        }
    )


def fixture() -> dict[str, object]:
    middle = middle_fixture()
    strict = candidate()
    geometry = curvature_incidence()
    background = NariaiBackground()
    algebraic = middle["algebraic"]
    screen = middle["screen"]

    _, basis = _adjoint_basis()
    k_actions = _adjoint_actions(basis[11:15], basis)
    schouten = tuple(
        background.metric[axis, axis] / 6 for axis in range(4)
    )
    rho0 = sp.Matrix.vstack(
        *(schouten[axis] * k_actions[axis] for axis in range(4))
    )
    derivative0, _ = _derivative_rows()
    total0 = _add(
        _algebraic(screen.cohomology_d0),
        _add(_algebraic(rho0), derivative0),
    )

    corrected_l0 = _add(
        middle["inclusion0"], _algebraic(strict["correction0"])
    )
    corrected_l1 = _add(
        middle["inclusion1"], _algebraic(strict["correction1"])
    )
    projection0 = screen.harmonic_p0
    incidence_projection = geometry["incidence"] * projection0
    d_aut = _add(total0, _scale(_algebraic(incidence_projection), -1))
    k_p0 = {
        word: matrix * projection0
        for word, matrix in middle["first_bgg"].items()
    }
    phi = middle["pbw_h1"].compose(
        middle["yang_mills_middle"], corrected_l1
    )

    curvature0 = _tensor_product_curvature(
        background, _lc_adjoint_curvature(), 0
    )
    pbw_c0 = FibrePBW(curvature0, background, "Nariai-C0-automorphism")
    first_square_defect = _add(
        middle["pbw_h0"].compose(d_aut, corrected_l0),
        _scale(
            middle["pbw_h0"].compose(
                corrected_l1, middle["first_bgg"]
            ),
            -1,
        ),
    )
    projection_defect = _add(
        {word: projection0 * matrix for word, matrix in corrected_l0.items()},
        _scale(_algebraic(sp.eye(4)), -1),
    )
    degree_one_left = pbw_c0.compose(
        middle["yang_mills_middle"], d_aut
    )
    degree_one_right = pbw_c0.compose(phi, k_p0)
    degree_one_defect = _add(
        degree_one_left, _scale(degree_one_right, -1)
    )
    graph_constraint_defect = _add(
        middle["pbw_h1"].compose(
            middle["yang_mills_middle"], corrected_l1
        ),
        _scale(phi, -1),
    )

    graph_field = _vertical(corrected_l1, _algebraic(sp.eye(9)))
    prolonged_gauge = _vertical(d_aut, k_p0)
    prolonged_equation = _horizontal(
        middle["yang_mills_middle"], _scale(phi, -1)
    )
    return {
        "middle": middle,
        "corrected_l0": corrected_l0,
        "corrected_l1": corrected_l1,
        "projection0": projection0,
        "d_aut": d_aut,
        "k_p0": k_p0,
        "phi": phi,
        "prolonged_gauge": prolonged_gauge,
        "prolonged_equation": prolonged_equation,
        "graph_field": graph_field,
        "first_square_defect": first_square_defect,
        "projection_defect": projection_defect,
        "degree_one_left": degree_one_left,
        "degree_one_right": degree_one_right,
        "degree_one_defect": degree_one_defect,
        "graph_constraint_defect": graph_constraint_defect,
    }


def build() -> dict[str, object]:
    mismatch = json.loads(MISMATCH.read_text())
    incidence = json.loads(INCIDENCE.read_text())
    shifted = json.loads(SHIFTED.read_text())
    if mismatch["flags"]["CURVATURE_CORRECTED_AUTOMORPHISM_PROLONGATION_REQUIRED"] is not True:
        raise ValueError("reducibility-mismatch gate unavailable")
    if incidence["flags"]["CURVATURE_INCIDENCE_IDENTITY_EXACT"] is not True:
        raise ValueError("curvature-incidence identity unavailable")
    if shifted["flags"]["CURVATURE_INCIDENCE_SHIFTED_CHAIN_EXACT"] is not True:
        raise ValueError("shifted-chain identity unavailable")
    value = fixture()
    if any(
        _count(value[name])
        for name in (
            "first_square_defect",
            "projection_defect",
            "degree_one_defect",
            "graph_constraint_defect",
        )
    ):
        raise AssertionError("automorphism prolongation did not close")

    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (
            Path(__file__).resolve(),
            VERIFIER,
            TESTS,
            SCHEMA,
            INCIDENCE_PRODUCER,
            SHIFTED_PRODUCER,
            MIDDLE_PRODUCER,
            STRICT_PRODUCER,
            PBW_SOURCE,
        )
    }
    return {
        "schema": "pure-weyl-nariai-automorphism-prolongation-first-two-rows-v1",
        "result_id": "NARIAI_AUTOMORPHISM_PROLONGATION_FIRST_TWO_ROWS_V1",
        "result_state": "CURVATURE_CORRECTED_AUTOMORPHISM_GAUGE_CONSTRAINT_COMPLEX_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "reducibility_mismatch": {"artifact_id": mismatch["result_id"], "path": str(MISMATCH.relative_to(ROOT)), "sha256": _sha256(MISMATCH)},
            "curvature_incidence": {"artifact_id": incidence["result_id"], "path": str(INCIDENCE.relative_to(ROOT)), "sha256": _sha256(INCIDENCE)},
            "shifted_chain": {"artifact_id": shifted["result_id"], "path": str(SHIFTED.relative_to(ROOT)), "sha256": _sha256(SHIFTED)}
        },
        "construction": {
            "ghost_bundle": "C0 rank 15",
            "state_bundle": "C1 plus H1, ranks 60+9",
            "constraint_bundle": "C1dual rank 60",
            "d_aut": "d^D-I_Omega p0",
            "gauge_map": "G_aut=(d_aut,K p0)^T",
            "constraint_map": "P_aut=(M^D,-Phi)",
            "Phi": "M^D L1_corrected",
            "metric_gauge_graph": "F_-1=L0_corrected; F_0=(L1_corrected,identity_H1)^T"
        },
        "exact_operators": {
            "L0_corrected": _sparse_table(value["corrected_l0"]),
            "L1_corrected": _sparse_table(value["corrected_l1"]),
            "d_aut": _sparse_table(value["d_aut"]),
            "K_p0": _sparse_table(value["k_p0"]),
            "Phi": _sparse_table(value["phi"]),
            "G_aut": _sparse_table(value["prolonged_gauge"]),
            "P_aut": _sparse_table(value["prolonged_equation"]),
            "metric_field_graph": _sparse_table(value["graph_field"])
        },
        "exact_checks": {
            "p0_L0_minus_identity_entries": _count(value["projection_defect"]),
            "d_aut_L0_minus_L1_K_entries": _count(value["first_square_defect"]),
            "M_d_aut_minus_Phi_K_p0_entries": _count(value["degree_one_defect"]),
            "P_aut_G_aut_entries": _count(value["degree_one_defect"]),
            "P_aut_metric_graph_entries": _count(value["graph_constraint_defect"]),
            "d_aut_orders": sorted({len(word) for word in value["d_aut"]}),
            "G_aut_orders": sorted({len(word) for word in value["prolonged_gauge"]}),
            "P_aut_orders": sorted({len(word) for word in value["prolonged_equation"]}),
            "metric_reducibility_graph_exact": True,
            "support_local_finite_order": True
        },
        "flags": {
            "NARIAI_AUTOMORPHISM_PROLONGATION_FIRST_TWO_ROWS_V1": True,
            "CURVATURE_CORRECTED_GHOST_PROLONGATION": True,
            "AUTOMORPHISM_GAUGE_CONSTRAINT_COMPLEX": True,
            "METRIC_GAUGE_GRAPH_CHAIN_MAP": True,
            "CYCLIC_COTANGENT_COMPLETION": False,
            "METRIC_BACH_MIDDLE_EXTENSION": False,
            "FULL_PARENT_METRIC_QUASI_ISOMORPHISM": False,
            "NARIAI_GREEN_HOMOTOPY": False,
            "OPEN_BACKGROUND_CLASS": False,
            "QUANTUM_CLAIM": False
        },
        "next_gate": "C_G2_NARIAI_AUTOMORPHISM_CYCLIC_BACH_EXTENSION",
        "claim_boundary": (
            "This certificate constructs the curvature-corrected infinitesimal-automorphism ghost differential d_aut=d^D-I_Omega p0 and proves the exact support-local two-arrow complex C0 to C1+H1 to C1dual on unit Nariai. The corrected BGG graph carries every metric gauge variation and reducibility strictly: p0 L0=1, d_aut L0=L1 K, and (M^D,-Phi)(d_aut,Kp0)^T=0. It resolves the ghost-cohomology mismatch of the unmodified normal-tractor parent. It does not yet add the metric Bach equation to the prolonged middle, construct the cyclic cotangent/identity rows, prove a full quasi-isomorphism or SDR, build Green homotopies, establish an open background class, or make nonlinear or quantum claims."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_automorphism_prolongation_first_two_rows.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_automorphism_prolongation_first_two_rows.py",
                "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_automorphism_prolongation_first_two_rows",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-automorphism-prolongation-first-two-rows-v1.schema.json -d d_quotient_classical/certificates/NARIAI_AUTOMORPHISM_PROLONGATION_FIRST_TWO_ROWS_V1.json"
            ]
        }
    }


def render(value: dict[str, object]) -> str:
    return rf"""# Nariai automorphism prolongation: first two rows

The curvature correction required by the reducibility mismatch is

\[
d_{{\rm aut}}=d^D-I_\Omega p_0.
\]

It produces the exact local complex

\[
C_0\xrightarrow{{(d_{{\rm aut}},Kp_0)^T}}
C_1\oplus H_1
\xrightarrow{{(M^D,-\Phi)}}C_1^*,
\qquad \Phi=M^DL_1^{{\rm corr}}.
\]

Both coefficient identities are exact:

\[
d_{{\rm aut}}L_0^{{\rm corr}}=L_1^{{\rm corr}}K,
\qquad
M^Dd_{{\rm aut}}=\Phi Kp_0.
\]

Thus the metric gauge graph
(\xi\mapsto L_0^{{\rm corr}}\xi) and
(h\mapsto(L_1^{{\rm corr}}h,h)) is a strict chain map through the gauge and
constraint rows.  In particular every metric Killing reducibility is now a
closed prolonged ghost.

## Boundary

{value['claim_boundary']}
"""


def verify(value: dict[str, object]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("automorphism prolongation certificate drifted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.guards:
        flags = value["flags"]
        if flags["NARIAI_AUTOMORPHISM_PROLONGATION_FIRST_TWO_ROWS_V1"] is not True:
            raise AssertionError("automorphism prolongation guard failed")
        if flags["CYCLIC_COTANGENT_COMPLETION"] is not False:
            raise AssertionError("cyclic completion was overpromoted")
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
