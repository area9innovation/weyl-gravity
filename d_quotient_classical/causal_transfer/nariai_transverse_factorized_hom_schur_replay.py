#!/usr/bin/env python3
"""Factorized Hom-adjoint and compressed-Schur replay on transverse Nariai."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    _add,
    _algebraic,
)
from covariant_completion.curved_operator.adjoint_tractor_bgg_differential_screen import (
    _adjoint_actions,
)
from covariant_completion.curved_operator.adjoint_tractor_kostant_compression import (
    _adjoint_basis,
)
from d_quotient_classical.causal_transfer.coefficient_jet_formal_adjoint import (
    formal_adjoint,
)
from d_quotient_classical.causal_transfer.coefficient_jet_pbw import (
    JetLinearizedOperator,
    jet_add,
    jet_scale,
    parallel_zero_variation,
)
from d_quotient_classical.causal_transfer.nariai_curvature_incidence_first_square import (
    curvature_incidence,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    NariaiBackground,
    _derivative_rows,
)
from d_quotient_classical.causal_transfer.nariai_transverse_coordinate_curvature_jets import (
    MAX_JET_ORDER,
)
from d_quotient_classical.causal_transfer.nariai_transverse_corrected_bgg_splitting_coefficient_jets import (
    _count,
    _deserialize_table,
    _difference,
    _table,
    operator_data as splitting_operator_data,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-factorized-hom-schur-replay.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-factorized-hom-schur-replay-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_factorized_hom_schur_replay.py"
TESTS = HERE / "tests/test_nariai_transverse_factorized_hom_schur_replay.py"
ADJOINT_TESTS = HERE / "tests/test_coefficient_jet_formal_adjoint.py"
HIGH_ORDER_TESTS = HERE / "tests/test_nariai_transverse_high_order_curvature_jets.py"
ADJOINT_BACKEND = HERE / "coefficient_jet_formal_adjoint.py"
COEFFICIENT_BACKEND = HERE / "coefficient_jet_pbw.py"
CURVATURE_JETS = HERE / "nariai_transverse_coordinate_curvature_jets.py"
SPLITTING = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_CORRECTED_BGG_SPLITTING_COEFFICIENT_JETS_V1.json"
MIDDLE_REPLAY = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ASSOCIATIVE_MIDDLE_SHIFTED_CHAIN_REPLAY_V1.json"
PAIRING = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1.json"
OLD_POINT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1.json"


Table = dict[tuple[int, ...], sp.Matrix]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _algebraic_adjoint(
    operator: JetLinearizedOperator,
    source_pairing: sp.Matrix,
    target_pairing: sp.Matrix,
    name: str,
) -> JetLinearizedOperator:
    inverse = source_pairing.inv()

    def transform(table: Table) -> Table:
        return {
            word: (inverse * matrix.T * target_pairing).applyfunc(sp.expand)
            for word, matrix in table.items()
        }

    return JetLinearizedOperator(
        transform(operator.base),
        lambda word: transform(operator.delta(word)),
        name,
    )


def _parent_primitives(value):
    middle = value["middle"]
    algebraic = middle["algebraic"]
    screen = middle["screen"]
    pbw = value["pbw"]
    _, basis = _adjoint_basis()
    k_actions = _adjoint_actions(basis[11:15], basis)
    rho = tuple(
        NariaiBackground.metric[axis, axis] * k_actions[axis] / 6
        for axis in range(4)
    )
    rho1_rows = []
    for left in range(4):
        for right in range(left + 1, 4):
            block = sp.zeros(15, 60)
            block[:, 15 * right : 15 * (right + 1)] = rho[left]
            block[:, 15 * left : 15 * (left + 1)] = -rho[right]
            rho1_rows.append(block)
    rho1 = sp.Matrix.vstack(*rho1_rows)
    _, derivative1 = _derivative_rows()
    delta1_base = _add(_algebraic(rho1), derivative1)
    total1_base = _add(_algebraic(screen.cohomology_d1), delta1_base)
    incidence = curvature_incidence()["incidence"] * value["automorphism"]["projection0"]
    total0_base = _add(value["d_aut"].base, {(): incidence})
    pairs = tuple(
        (left, right)
        for left in range(4)
        for right in range(left + 1, 4)
    )
    eta = NariaiBackground.metric
    two_form_metric = sp.diag(
        *(eta[left, left] * eta[right, right] for left, right in pairs)
    )
    two_form_pairing = sp.kronecker_product(
        two_form_metric, algebraic.adjoint_pairing
    )
    return {
        "delta1": parallel_zero_variation(delta1_base, "delta1"),
        "total1": parallel_zero_variation(total1_base, "d-parent-1"),
        "total0": parallel_zero_variation(total0_base, "d-parent-0"),
        "q2": parallel_zero_variation(_algebraic(screen.q2), "q2"),
        "i1": parallel_zero_variation(_algebraic(algebraic.i1), "i1"),
        "pairs": pairs,
        "two_form_pairing": two_form_pairing,
        "eta": eta,
        "pbw": pbw,
    }


def _curvature_action(square: JetLinearizedOperator, pairs, eta):
    def action(table: Table) -> sp.Matrix:
        raw = table.get((), sp.zeros(90, 15))
        blocks = {
            pair: raw[15 * index : 15 * (index + 1), :]
            for index, pair in enumerate(pairs)
        }

        def curvature(left: int, right: int) -> sp.Matrix:
            if left == right:
                return sp.zeros(15)
            return blocks[(left, right)] if left < right else -blocks[(right, left)]

        return sp.Matrix.vstack(
            *(
                sp.Matrix.hstack(
                    *(
                        eta[source, source] * curvature(target, source)
                        for source in range(4)
                    )
                )
                for target in range(4)
            )
        )

    return JetLinearizedOperator(
        _algebraic(action(square.base)),
        lambda word: _algebraic(action(square.delta(word))),
        "curvature-action",
    )


@lru_cache(maxsize=1)
def operator_data():
    value = splitting_operator_data()
    middle_data = value["middle"]
    algebraic = middle_data["algebraic"]
    pbw = value["pbw"]
    primitive = _parent_primitives(value)
    one_pairing = algebraic.one_form_pairing
    endpoint_pairing = algebraic.endpoint_field_pairing
    two_pairing = primitive["two_form_pairing"]

    delta1_sharp = formal_adjoint(
        primitive["delta1"], one_pairing, two_pairing, pbw["C2"], "delta1-sharp"
    )
    q2_sharp = formal_adjoint(
        primitive["q2"], two_pairing, one_pairing, pbw["C1"], "q2-sharp"
    )
    i1_sharp = formal_adjoint(
        primitive["i1"], endpoint_pairing, one_pairing, pbw["C1"], "i1-sharp"
    )
    n1_sharp = pbw["C1"].compose(delta1_sharp, q2_sharp, "n1-sharp")
    i1_n1_sharp = pbw["C1"].compose(i1_sharp, n1_sharp, "i1-sharp-n1-sharp")
    raw_l1_sharp = jet_add(
        i1_sharp,
        jet_scale(i1_n1_sharp, -1),
        pbw["C1"].compose(i1_n1_sharp, n1_sharp, "i1-sharp-n1-sharp2"),
        name="L1-raw-sharp-factorized",
    )
    correction_sharp = _algebraic_adjoint(
        value["L1_correction"], endpoint_pairing, one_pairing, "Delta-L1-sharp"
    )
    l1_sharp = jet_add(
        raw_l1_sharp, correction_sharp, name="L1-corrected-sharp-factorized"
    )

    total1_sharp = formal_adjoint(
        primitive["total1"], one_pairing, two_pairing, pbw["C2"], "d1-sharp"
    )
    normal_square = pbw["C0"].compose(
        primitive["total1"], primitive["total0"], "normal-square"
    )
    curvature_action = _curvature_action(
        normal_square, primitive["pairs"], primitive["eta"]
    )
    parent_middle = jet_add(
        pbw["C1"].compose(total1_sharp, primitive["total1"], "rough-middle"),
        jet_scale(curvature_action, -1),
        name="M-parent-factorized",
    )
    phi = pbw["H1"].compose(
        parent_middle, value["L1_corrected"], "Phi-factorized"
    )
    schur = pbw["H1"].compose(l1_sharp, phi, "Schur-factorized")

    return {
        "value": value,
        "l1_sharp": l1_sharp,
        "parent_middle": parent_middle,
        "curvature_action": curvature_action,
        "phi": phi,
        "schur": schur,
        "one_pairing": one_pairing,
        "endpoint_pairing": endpoint_pairing,
    }


@lru_cache(maxsize=1)
def exact_data() -> dict[str, Any]:
    data = operator_data()
    value = data["value"]
    old = json.loads(OLD_POINT.read_text())["exact_data"]["operator_variations"]
    previous_phi = json.loads(MIDDLE_REPLAY.read_text())["exact_data"][
        "authoritative_phi_variation"
    ]
    old_middle = _deserialize_table(old["Yang_Mills_middle"])
    old_phi = _deserialize_table(previous_phi)

    middle_base_defect = _difference(
        data["parent_middle"].base, value["middle"]["yang_mills_middle"]
    )
    middle_point_defect = _difference(data["parent_middle"].delta(()), old_middle)
    phi_base_defect = _difference(data["phi"].base, value["automorphism"]["phi"])
    phi_point_defect = _difference(data["phi"].delta(()), old_phi)

    one = data["one_pairing"]
    curvature_sharp = _algebraic_adjoint(
        data["curvature_action"], one, one, "curvature-action-sharp"
    )
    curvature_base_cyclic = _difference(
        curvature_sharp.base, data["curvature_action"].base
    )
    curvature_point_cyclic = _difference(
        curvature_sharp.delta(()), data["curvature_action"].delta(())
    )

    generic_l1_sharp = formal_adjoint(
        value["L1_corrected"],
        data["endpoint_pairing"],
        data["one_pairing"],
        value["pbw"]["C1"],
        "L1-sharp-naive-normal-table",
    )
    naive_base_defect = _difference(data["l1_sharp"].base, generic_l1_sharp.base)
    naive_point_defect = _difference(
        data["l1_sharp"].delta(()), generic_l1_sharp.delta(())
    )
    # Evaluate the complete varied Schur operator before recording the lazy
    # coefficient-jet coverage which that composition requested.
    schur_point = data["schur"].delta(())

    if any(
        (
            middle_base_defect,
            middle_point_defect,
            phi_base_defect,
            phi_point_defect,
            curvature_base_cyclic,
            curvature_point_cyclic,
        )
    ):
        raise AssertionError("factorized Hom/Schur replay identity failed")
    l1_words = sorted(
        value["L1_corrected"].requested_words, key=lambda word: (len(word), word)
    )
    middle_words = sorted(
        data["parent_middle"].requested_words, key=lambda word: (len(word), word)
    )
    curvature_words = sorted(
        set().union(
            *(
                layer.linearized_pbw.requested_jet_words
                for layer in value["pbw"].values()
            )
        ),
        key=lambda word: (len(word), word),
    )
    if max(map(len, l1_words)) != 4:
        raise AssertionError(
            "compressed Schur corrected-splitting jet coverage drifted: "
            f"max={max(map(len, l1_words))}, words={len(l1_words)}"
        )
    if max(map(len, curvature_words)) != MAX_JET_ORDER:
        raise AssertionError(
            "compressed Schur did not exercise the highest certified curvature "
            f"jet layer: max={max(map(len, curvature_words))}, "
            f"words={len(curvature_words)}"
        )
    return {
        "jet_coverage": {
            "certified_curvature_max_order": MAX_JET_ORDER,
            "L1_requested_word_count": len(l1_words),
            "L1_max_requested_order": max(map(len, l1_words)),
            "middle_requested_word_count": len(middle_words),
            "middle_max_requested_order": max(map(len, middle_words)),
            "curvature_requested_word_count": len(curvature_words),
            "curvature_max_requested_order": max(map(len, curvature_words)),
            "above_maximum_fails_closed": True,
        },
        "factorized_Hom_adjoint": {
            "construction": "reverse primitive covariant HPL factors before PBW composition; adjoint the algebraic strict-square correction coefficient-jet by coefficient-jet",
            "L1sharp_base_coefficients": _count(data["l1_sharp"].base),
            "L1sharp_variation": _table(data["l1_sharp"].delta(())),
            "naive_normal_table_base_defect": _table(naive_base_defect),
            "naive_normal_table_variation_defect": _table(naive_point_defect),
            "naive_normal_table_adjoint_authoritative": False,
        },
        "parent_middle": {
            "construction": "d1^sharp d1 minus the curvature action extracted from d1 d0",
            "base_defect": _table(middle_base_defect),
            "variation": _table(data["parent_middle"].delta(())),
            "old_point_defect": _table(middle_point_defect),
            "curvature_action_base_cyclic_defect": _table(curvature_base_cyclic),
            "curvature_action_variation_cyclic_defect": _table(curvature_point_cyclic),
            "factorized_formal_self_adjoint": True,
        },
        "compressed_schur": {
            "formula": "L1_corrected^sharp M_parent L1_corrected",
            "base_coefficients": _count(data["schur"].base),
            "variation": _table(schur_point),
            "phi_base_defect": _table(phi_base_defect),
            "phi_variation_defect": _table(phi_point_defect),
            "factorized_cyclic": True,
        },
        "next_gate_requirements": {
            "gate": "complete rank-310 first-variation SDR",
            "upper_chain_identity": "Schur K + L1_corrected^sharp M_parent incidence = 0",
            "current_certified_curvature_coefficient_jet_order": MAX_JET_ORDER,
            "upper_chain_replayed": False,
        },
        "disposition": {
            "Hom_adjoint_resolved_factorized": True,
            "compressed_schur_replayed": True,
            "rank_310_transverse_SDR_decided": False,
            "transverse_causal_transfer": False,
        },
    }


def build() -> dict[str, Any]:
    data = exact_data()
    refs = {}
    for key, path, result_id in (
        ("splitting_jets", SPLITTING, "NARIAI_TRANSVERSE_CORRECTED_BGG_SPLITTING_COEFFICIENT_JETS_V1"),
        ("middle_replay", MIDDLE_REPLAY, "NARIAI_TRANSVERSE_ASSOCIATIVE_MIDDLE_SHIFTED_CHAIN_REPLAY_V1"),
        ("pairing_variation", PAIRING, "NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1"),
        ("old_point_replay", OLD_POINT, "NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1"),
    ):
        payload = json.loads(path.read_text())
        if payload["result_id"] != result_id:
            raise AssertionError(f"dependency drifted: {key}")
        refs[key] = {
            "path": str(path.relative_to(ROOT)),
            "result_id": result_id,
            "sha256": _sha(path),
        }
    sources = (
        Path(__file__).resolve(), VERIFIER, TESTS, ADJOINT_TESTS, HIGH_ORDER_TESTS,
        SCHEMA, ADJOINT_BACKEND, COEFFICIENT_BACKEND, CURVATURE_JETS,
    )
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "nariai-transverse-factorized-hom-schur-replay-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1",
        "result_state": "FACTORIZED_HOM_ADJOINT_AND_COMPRESSED_SCHUR_EXACT",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": refs,
        "exact_data": data,
        "exact_checks": {
            "order_five_jet_layer_exercised": data["jet_coverage"]["curvature_max_requested_order"] == 5,
            "factorized_Hom_adjoint": data["disposition"]["Hom_adjoint_resolved_factorized"],
            "parent_middle_self_adjoint": data["parent_middle"]["factorized_formal_self_adjoint"],
            "compressed_schur_cyclic": data["compressed_schur"]["factorized_cyclic"],
            "upper_chain_not_overclaimed": not data["next_gate_requirements"]["upper_chain_replayed"],
            "rank_310_not_overclaimed": not data["disposition"]["rank_310_transverse_SDR_decided"],
        },
        "flags": {
            "NARIAI_TRANSVERSE_FACTORIZED_HOM_ADJOINT": True,
            "NARIAI_TRANSVERSE_COMPRESSED_SCHUR_REPLAY": True,
            "NARIAI_TRANSVERSE_RELATIVE_SADDLE_UPPER_CHAIN": False,
            "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION",
        "claim_boundary": "This certificate derives the corrected Hom adjoint by reversing primitive covariant HPL factors before PBW composition, extends the curvature recurrence to the fifth coefficient-jet order required by the compressed operator, and replays the factorized parent middle and compressed Schur operator. It rejects the adjoint of an already normal-ordered Hom table as non-authoritative. The upper relative-saddle chain remains fail-closed with the complete rank-310 deformation retract, support preservation and transverse Green homotopies.",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha(path) for path in sources
        },
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_factorized_hom_schur_replay --check",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_factorized_hom_schur_replay.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_factorized_hom_schur_replay d_quotient_classical.causal_transfer.tests.test_coefficient_jet_formal_adjoint d_quotient_classical.causal_transfer.tests.test_nariai_transverse_high_order_curvature_jets",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-factorized-hom-schur-replay-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1.json",
        ],
    }


def report(payload: dict[str, Any]) -> str:
    data = payload["exact_data"]
    return rf"""# Transverse factorized Hom-adjoint and Schur replay

The corrected Hom adjoint is constructed before normal ordering by reversing
the primitive covariant HPL factors.  The direct adjoint of the already
normal-ordered table differs by
`{data['factorized_Hom_adjoint']['naive_normal_table_base_defect']['nonzero_coefficients']}`
base and
`{data['factorized_Hom_adjoint']['naive_normal_table_variation_defect']['nonzero_coefficients']}`
first-variation coefficients and is retained only as a negative regression.

The factorized parent middle recovers the authoritative base and point
variation and is formally self-adjoint.  The compressed operator

\[
L_1^\sharp M_{{\rm parent}}L_1
\]

has `{data['compressed_schur']['base_coefficients']}` base and
`{data['compressed_schur']['variation']['nonzero_coefficients']}` varied
coefficients.  Its construction exercises
`{data['jet_coverage']['L1_requested_word_count']}` corrected-splitting jets
through order `{data['jet_coverage']['L1_max_requested_order']}`.  The upper
relative-saddle chain remains the next rank-310 SDR gate; no causal theorem
is promoted here.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if args.write:
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report(payload))
    if args.check and json.loads(OUTPUT.read_text()) != payload:
        raise AssertionError("factorized Hom/Schur artifact is stale")
    print("NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1: PASS")


if __name__ == "__main__":
    main()
