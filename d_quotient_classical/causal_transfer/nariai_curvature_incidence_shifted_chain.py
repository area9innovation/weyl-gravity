#!/usr/bin/env python3
"""Exact shifted-chain and factorized-saddle gate for Nariai incidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    FibrePBW,
    _add,
    _algebraic,
    _formal_adjoint,
    _scale,
    _tensor_product_curvature,
)
from d_quotient_classical.causal_transfer.nariai_curvature_incidence_first_square import (
    OUTPUT as INCIDENCE_CERTIFICATE,
    curvature_incidence,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    NariaiBackground,
    ROOT,
    _lc_adjoint_curvature,
    _sha256,
    _sparse_table,
    candidate,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import (
    OUTPUT as MIDDLE_CERTIFICATE,
    fixture as middle_fixture,
)


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_CURVATURE_INCIDENCE_SHIFTED_CHAIN_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-curvature-incidence-shifted-chain.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-curvature-incidence-shifted-chain-v1.schema.json"
VERIFIER = HERE / "verify_nariai_curvature_incidence_shifted_chain.py"
TESTS = HERE / "tests/test_nariai_curvature_incidence_shifted_chain.py"
PBW_CODE = ROOT / "covariant_completion/curved_operator/adjoint_tractor_bgg_curved_pbw.py"
INCIDENCE_PRODUCER = HERE / "nariai_curvature_incidence_first_square.py"
MIDDLE_PRODUCER = HERE / "nariai_yang_mills_middle_compression.py"


def _count(table: dict[tuple[int, ...], sp.Matrix]) -> int:
    return sum(entry != 0 for matrix in table.values() for entry in matrix)


def _ranks(table: dict[tuple[int, ...], sp.Matrix]) -> dict[str, int]:
    return {str(word): matrix.rank() for word, matrix in sorted(table.items())}


def fixture() -> dict[str, object]:
    strict = candidate()
    middle = middle_fixture()
    geometry = curvature_incidence()
    algebraic = middle["algebraic"]
    background = NariaiBackground()
    parent_pbw = FibrePBW(
        _tensor_product_curvature(background, _lc_adjoint_curvature(), 1),
        background,
        "Nariai-C1-shifted-chain",
    )

    corrected_l1 = _add(
        middle["inclusion1"], _algebraic(strict["correction1"])
    )
    incidence = _algebraic(geometry["incidence"])
    parent_middle = middle["yang_mills_middle"]
    endpoint_k = middle["first_bgg"]
    shifted_equation_map = middle["pbw_h1"].compose(
        parent_middle, corrected_l1
    )
    parent_on_incidence = middle["pbw_h0"].compose(
        parent_middle, incidence
    )
    shifted_on_k = middle["pbw_h0"].compose(
        shifted_equation_map, endpoint_k
    )
    shifted_chain_defect = _add(parent_on_incidence, shifted_on_k)

    # The cyclic saddle is retained in its authoritative factorized order.
    # This avoids applying the current PBW adjoint routine to an already
    # normal-ordered composite with nontrivial Hom-bundle cross coefficients.
    corrected_l1_sharp = _formal_adjoint(
        corrected_l1,
        algebraic.endpoint_field_pairing,
        algebraic.one_form_pairing,
        parent_pbw,
    )
    saddle_endpoint = middle["pbw_h1"].compose(
        corrected_l1_sharp, shifted_equation_map
    )
    saddle_lower_defect = shifted_chain_defect
    saddle_upper_defect = _add(
        middle["pbw_h0"].compose(saddle_endpoint, endpoint_k),
        middle["pbw_h0"].compose(
            corrected_l1_sharp, parent_on_incidence
        ),
    )

    # Diagnostic only: the generic canonical-table adjoint currently assumes
    # coefficient covariance which is not represented for the (01)/(23)
    # Hom-bundle cross terms.  The factorized variational adjoint above is the
    # mathematical one; this replay defect blocks a coefficientwise cyclic
    # mapping-cylinder promotion until that normalizer is repaired.
    parent_middle_sharp_replay = _formal_adjoint(
        parent_middle,
        algebraic.one_form_pairing,
        algebraic.one_form_pairing,
        parent_pbw,
    )
    pbw_adjoint_replay_defect = _add(
        parent_middle_sharp_replay, _scale(parent_middle, -1)
    )

    return {
        "corrected_l1": corrected_l1,
        "incidence": incidence,
        "parent_middle": parent_middle,
        "endpoint_k": endpoint_k,
        "shifted_equation_map": shifted_equation_map,
        "parent_on_incidence": parent_on_incidence,
        "shifted_on_k": shifted_on_k,
        "shifted_chain_defect": shifted_chain_defect,
        "corrected_l1_sharp": corrected_l1_sharp,
        "saddle_endpoint": saddle_endpoint,
        "saddle_lower_defect": saddle_lower_defect,
        "saddle_upper_defect": saddle_upper_defect,
        "pbw_adjoint_replay_defect": pbw_adjoint_replay_defect,
    }


def build() -> dict[str, object]:
    incidence_dependency = json.loads(INCIDENCE_CERTIFICATE.read_text())
    middle_dependency = json.loads(MIDDLE_CERTIFICATE.read_text())
    if incidence_dependency["flags"]["CURVATURE_INCIDENCE_IDENTITY_EXACT"] is not True:
        raise ValueError("curvature-incidence dependency is unavailable")
    if middle_dependency["exact_checks"]["corrected_parent_left_defect_entries"] != 0:
        raise ValueError("Yang--Mills parent complex is unavailable")
    value = fixture()
    adjoint_defect = value["pbw_adjoint_replay_defect"]
    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (
            Path(__file__).resolve(),
            VERIFIER,
            TESTS,
            SCHEMA,
            PBW_CODE,
            INCIDENCE_PRODUCER,
            MIDDLE_PRODUCER,
        )
    }
    return {
        "schema": "pure-weyl-nariai-curvature-incidence-shifted-chain-v1",
        "result_id": "NARIAI_CURVATURE_INCIDENCE_SHIFTED_CHAIN_V1",
        "result_state": "SHIFTED_CHAIN_AND_FACTORIZED_SADDLE_EXACT_PBW_ADJOINT_GATE_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "curvature_incidence": {
                "artifact_id": incidence_dependency["result_id"],
                "path": str(INCIDENCE_CERTIFICATE.relative_to(ROOT)),
                "sha256": _sha256(INCIDENCE_CERTIFICATE),
            },
            "yang_mills_middle": {
                "artifact_id": middle_dependency["result_id"],
                "path": str(MIDDLE_CERTIFICATE.relative_to(ROOT)),
                "sha256": _sha256(MIDDLE_CERTIFICATE),
            },
        },
        "conventions": {
            "shifted_map": "Phi_0=I_Omega and Phi_1=M^D L1_corrected",
            "shifted_chain_equation": "M^D I_Omega + Phi_1 K = 0",
            "factorized_saddle": "S=A^sharp M^D A with A=(L1_corrected, identity_C1)",
            "factorized_gauge": "G=(K,I_Omega)^T",
            "factorized_gauge_equation": "A G=L1_corrected K+I_Omega=d^D L0",
            "adjoint_policy": "formal adjoints of composites are retained in factorized variational order until the Hom-bundle PBW covariance normalizer is repaired",
        },
        "exact_data": {
            "corrected_L1": _sparse_table(value["corrected_l1"]),
            "curvature_incidence": _sparse_table(value["incidence"]),
            "shifted_equation_map": _sparse_table(value["shifted_equation_map"]),
            "M_on_incidence": _sparse_table(value["parent_on_incidence"]),
            "Phi1_on_K": _sparse_table(value["shifted_on_k"]),
            "shifted_chain_defect": _sparse_table(value["shifted_chain_defect"]),
            "factorized_endpoint_saddle": _sparse_table(value["saddle_endpoint"]),
            "factorized_saddle_lower_defect": _sparse_table(value["saddle_lower_defect"]),
            "factorized_saddle_upper_defect": _sparse_table(value["saddle_upper_defect"]),
            "pbw_parent_adjoint_replay_defect": _sparse_table(adjoint_defect),
        },
        "exact_checks": {
            "corrected_L1_orders": sorted({len(word) for word in value["corrected_l1"]}),
            "corrected_L1_nonzero_entries": _count(value["corrected_l1"]),
            "Phi1_orders": sorted({len(word) for word in value["shifted_equation_map"]}),
            "Phi1_nonzero_entries": _count(value["shifted_equation_map"]),
            "M_I_orders": sorted({len(word) for word in value["parent_on_incidence"]}),
            "M_I_nonzero_entries": _count(value["parent_on_incidence"]),
            "Phi1_K_orders": sorted({len(word) for word in value["shifted_on_k"]}),
            "Phi1_K_nonzero_entries": _count(value["shifted_on_k"]),
            "M_I_equals_minus_Phi1_K": value["parent_on_incidence"] == _scale(value["shifted_on_k"], -1),
            "shifted_chain_defect_nonzero_entries": _count(value["shifted_chain_defect"]),
            "factorized_endpoint_saddle_orders": sorted({len(word) for word in value["saddle_endpoint"]}),
            "factorized_endpoint_saddle_nonzero_entries": _count(value["saddle_endpoint"]),
            "factorized_saddle_lower_defect_nonzero_entries": _count(value["saddle_lower_defect"]),
            "factorized_saddle_upper_defect_nonzero_entries": _count(value["saddle_upper_defect"]),
            "pbw_parent_adjoint_replay_defect_orders": sorted({len(word) for word in adjoint_defect}),
            "pbw_parent_adjoint_replay_defect_rank": adjoint_defect.get((), sp.zeros(60)).rank(),
            "pbw_parent_adjoint_replay_defect_nonzero_entries": _count(adjoint_defect),
            "pbw_parent_adjoint_replay_normalized_witness": "defect[(),0,0]",
            "pbw_parent_adjoint_replay_normalized_witness_value": str(adjoint_defect[()][0, 0]),
            "pbw_parent_adjoint_replay_ranks": _ranks(adjoint_defect),
        },
        "theorem": {
            "shifted_chain": "The canonical Nariai curvature incidence extends to the next parent row as the exact degree-one chain map (I_Omega, M^D L1_corrected): M^D I_Omega+(M^D L1_corrected)K=0. Both terms are independently nonzero PBW operators with 154 coefficients, and their coefficientwise sum vanishes.",
            "factorized_saddle": "The factorized relative middle S=A^sharp M^D A annihilates G=(K,I_Omega)^T in both displayed blocks. The upper and lower block products vanish coefficientwise when the adjoints and compositions retain their variational factor order. This is the exact local algebra underlying the cyclic incidence saddle.",
            "remaining_verifier_gate": "The current generic PBW adjoint replay on an already normal-ordered parent middle leaves a rank-sixty algebraic defect. This is a Hom-bundle coefficient-covariance limitation of that replay path, not a no-go for the factorized formally self-adjoint Yang--Mills operator. A full cyclic mapping-cylinder certificate remains fail-closed until the normalizer or an independent variational-table checker resolves it.",
        },
        "flags": {
            "NARIAI_CURVATURE_INCIDENCE_SHIFTED_CHAIN_V1": True,
            "CURVATURE_INCIDENCE_SHIFTED_CHAIN_EXACT": True,
            "FACTORIZED_RELATIVE_SADDLE_GAUGE_IDENTITY_EXACT": True,
            "FACTORIZED_VARIATIONAL_CYCLICITY_AVAILABLE": True,
            "COEFFICIENTWISE_PBW_ADJOINT_REPLAY": False,
            "CYCLIC_CURVATURE_INCIDENCE_MAPPING_CONE": False,
            "MAPPING_CYLINDER_SDR": False,
            "NARIAI_GREEN_HOMOTOPY": False,
            "PARENT_FORMAL_SELF_ADJOINTNESS_NO_GO": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "C_G2_NARIAI_HOM_BUNDLE_PBW_COVARIANCE_AND_CYCLIC_CONE",
        "claim_boundary": (
            "This exact Nariai PBW calculation proves the degree-one shifted chain relation M^D I_Omega+(M^D L1_corrected)K=0 and both gauge-annihilation blocks of the factorized relative saddle S=A^sharp M^D A. It therefore supplies the algebraic incidence data needed by a cyclic mapping cylinder. It deliberately does not promote the full cylinder: the current generic PBW adjoint replay, when applied after normal ordering to the component parent middle, accumulates a rank-sixty algebraic defect on the cross-form Hom-bundle coefficients. The parent Yang--Mills operator remains formally self-adjoint by its factorized variational construction, so this receipt is not a mathematical self-adjointness no-go. The next gate is an exact Hom-bundle covariance-aware adjoint/associativity replay followed by the odd cotangent cone and SDR. No endpoint Bach equivalence, support, Green, open-family, nonlinear, or quantum claim follows."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_curvature_incidence_shifted_chain.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_curvature_incidence_shifted_chain.py",
                "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_curvature_incidence_shifted_chain",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-curvature-incidence-shifted-chain-v1.schema.json -d d_quotient_classical/certificates/NARIAI_CURVATURE_INCIDENCE_SHIFTED_CHAIN_V1.json",
            ],
        },
    }


def render(value: dict[str, object]) -> str:
    checks = value["exact_checks"]
    return rf"""# Nariai curvature-incidence shifted chain

The canonical incidence extends one row further through the corrected
Yang--Mills parent:

\[
 \Phi_0=I_\Omega,\qquad
 \Phi_1=M^D L_1^{{\rm corr}},\qquad
 M^D\Phi_0+\Phi_1K=0.
\]

Both nonzero summands have orders `{checks['M_I_orders']}` and
`{checks['M_I_nonzero_entries']}` coefficients; their sum has
`{checks['shifted_chain_defect_nonzero_entries']}`.  The factorized saddle
\(S=A^\sharp M^D A\), with
\(A=(L_1^{{\rm corr}},1)\), annihilates
\(G=(K,I_\Omega)^T\) in both blocks: the lower and upper defects contain
respectively `{checks['factorized_saddle_lower_defect_nonzero_entries']}` and
`{checks['factorized_saddle_upper_defect_nonzero_entries']}` coefficients.

## Remaining cyclic verifier gate

Applying the current generic PBW adjoint routine *after* normal ordering the
parent middle leaves an algebraic rank-`{checks['pbw_parent_adjoint_replay_defect_rank']}`
replay defect with `{checks['pbw_parent_adjoint_replay_defect_nonzero_entries']}`
entries and normalized witness
`{checks['pbw_parent_adjoint_replay_normalized_witness_value']}`.  This is a
coefficient-covariance limitation of that replay path.  The factorized
variational operator remains formally self-adjoint; no parent no-go is
claimed.  Full cyclic mapping-cylinder promotion waits for a Hom-bundle-aware
normalizer or an independent variational-table checker.

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
        if checks["M_I_equals_minus_Phi1_K"] is not True:
            raise AssertionError("shifted chain relation failed")
        if checks["shifted_chain_defect_nonzero_entries"] != 0:
            raise AssertionError("shifted chain did not close")
        if checks["factorized_saddle_upper_defect_nonzero_entries"] != 0:
            raise AssertionError("factorized saddle upper block did not close")
        if [
            checks["pbw_parent_adjoint_replay_defect_rank"],
            checks["pbw_parent_adjoint_replay_defect_nonzero_entries"],
            checks["pbw_parent_adjoint_replay_normalized_witness_value"],
        ] != [60, 60, "1"]:
            raise AssertionError("PBW adjoint replay diagnostic drifted")
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    report = render(value)
    if args.check:
        if OUTPUT.read_text() != encoded or REPORT.read_text() != report:
            raise SystemExit("generated shifted-chain artifacts drifted")
    else:
        OUTPUT.write_text(encoded)
        REPORT.write_text(report)


if __name__ == "__main__":
    main()
