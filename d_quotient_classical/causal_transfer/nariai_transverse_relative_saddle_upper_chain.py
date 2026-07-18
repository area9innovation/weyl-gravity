#!/usr/bin/env python3
"""Replay the transverse upper relative-saddle chain at unit Nariai."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from d_quotient_classical.causal_transfer.coefficient_jet_pbw import (
    jet_add,
    jet_scale,
    parallel_zero_variation,
)
from d_quotient_classical.causal_transfer.nariai_transverse_corrected_bgg_splitting_coefficient_jets import (
    _count,
    _table,
)
from d_quotient_classical.causal_transfer.nariai_transverse_factorized_hom_schur_replay import (
    _parent_primitives,
    operator_data,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_RELATIVE_SADDLE_UPPER_CHAIN_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-relative-saddle-upper-chain.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-relative-saddle-upper-chain-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_relative_saddle_upper_chain.py"
TESTS = HERE / "tests/test_nariai_transverse_relative_saddle_upper_chain.py"
DEPENDENCY = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1.json"
PRODUCER_DEPENDENCY = HERE / "nariai_transverse_factorized_hom_schur_replay.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def exact_data() -> dict[str, Any]:
    data = operator_data()
    value = data["value"]
    primitive = _parent_primitives(value)
    pbw_c0 = value["pbw"]["C0"]

    # The returned incidence is typed on C0 because the harmonic projection
    # p0 is already included: I_Omega p0 = d_parent-d_aut.
    incidence_p0 = jet_add(
        primitive["total0"],
        jet_scale(value["d_aut"], -1),
        name="I-Omega-p0",
    )
    k_p0 = parallel_zero_variation(
        value["automorphism"]["k_p0"], "K-p0"
    )
    schur_k = pbw_c0.compose(data["schur"], k_p0, "Schur-Kp0")
    middle_incidence = pbw_c0.compose(
        data["parent_middle"], incidence_p0, "M-parent-I-Omega-p0"
    )
    adjoint_incidence = pbw_c0.compose(
        data["l1_sharp"],
        middle_incidence,
        "L1-sharp-M-parent-I-Omega-p0",
    )
    defect = jet_add(
        schur_k,
        adjoint_incidence,
        name="upper-relative-saddle-chain",
    )

    base = defect.base
    point = defect.delta(())
    if base or point:
        raise AssertionError("upper relative-saddle chain failed")

    def coverage(operator) -> dict[str, int]:
        words = operator.requested_words
        return {
            "word_count": len(words),
            "maximum_order": max(map(len, words)) if words else 0,
        }

    return {
        "typed_identity": {
            "domain": "C0",
            "codomain": "H1dual",
            "formula": "Schur (K p0)+L1_corrected^sharp M_parent (I_Omega p0)=0",
            "incidence_definition": "I_Omega p0=d_parent-d_aut",
            "base_defect": _table(base),
            "first_variation_defect": _table(point),
        },
        "coefficient_jet_coverage": {
            "incidence_p0": coverage(incidence_p0),
            "parent_middle": coverage(data["parent_middle"]),
            "L1_corrected_sharp": coverage(data["l1_sharp"]),
            "certified_curvature_maximum_order": 5,
            "above_maximum_fails_closed": True,
        },
        "derivation": {
            "method": "factorized Hom adjoint followed by associative coefficient-jet PBW composition",
            "post_normal_order_adjoint_used": False,
            "interpolation_used": False,
            "action_Bach_variation_used": False,
        },
        "disposition": {
            "upper_relative_saddle_chain_exact": True,
            "outer_incidence_rows_exact": True,
            "complete_rank_310_first_variation_SDR": False,
            "transverse_action_Bach_Hessian_variation_available": False,
            "transverse_causal_transfer": False,
        },
    }


def build() -> dict[str, Any]:
    dependency = json.loads(DEPENDENCY.read_text())
    if dependency["result_id"] != "NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1":
        raise AssertionError("factorized Hom/Schur dependency drifted")
    data = exact_data()
    sources = (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, PRODUCER_DEPENDENCY)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "nariai-transverse-relative-saddle-upper-chain-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_RELATIVE_SADDLE_UPPER_CHAIN_V1",
        "result_state": "TRANSVERSE_UPPER_RELATIVE_SADDLE_CHAIN_EXACT",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "factorized_Hom_schur": {
                "path": str(DEPENDENCY.relative_to(ROOT)),
                "result_id": dependency["result_id"],
                "sha256": _sha(DEPENDENCY),
            }
        },
        "exact_data": data,
        "exact_checks": {
            "base_upper_chain_zero": data["typed_identity"]["base_defect"]["nonzero_coefficients"] == 0,
            "varied_upper_chain_zero": data["typed_identity"]["first_variation_defect"]["nonzero_coefficients"] == 0,
            "factorized_adjoint_used": not data["derivation"]["post_normal_order_adjoint_used"],
            "no_action_Bach_variation_smuggled_in": not data["derivation"]["action_Bach_variation_used"],
            "rank_310_not_overclaimed": not data["disposition"]["complete_rank_310_first_variation_SDR"],
            "causal_transfer_not_overclaimed": not data["disposition"]["transverse_causal_transfer"],
        },
        "flags": {
            "NARIAI_TRANSVERSE_RELATIVE_SADDLE_UPPER_CHAIN": True,
            "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_AND_RANK_310_SDR",
        "claim_boundary": "This exact coefficient-jet calculation closes the upper relative-saddle chain through first variation using the factorized Hom adjoint and the curvature incidence I_Omega p0. It uses no fitted Schur term and no action Bach-Hessian variation. The remaining rank-310 gate requires the independently action-derived transverse Hessian variation and the differentiated all-row SDR; no causal transfer is promoted.",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha(path) for path in sources
        },
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_relative_saddle_upper_chain --check",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_relative_saddle_upper_chain.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_relative_saddle_upper_chain",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-relative-saddle-upper-chain-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_RELATIVE_SADDLE_UPPER_CHAIN_V1.json",
        ],
    }


def report(payload: dict[str, Any]) -> str:
    data = payload["exact_data"]
    return rf"""# Transverse Nariai upper relative-saddle chain

The fully typed coefficient-jet replay proves

\[
\mathsf S(Kp_0)+L_1^\sharp M^D(I_\Omega p_0)=0
\]

at the base point and through the certified transverse first variation.  Both
defect tables contain zero coefficients.  The calculation uses the
factorized Hom adjoint before PBW normal ordering and requests curvature jets
only inside the certified order-five envelope.

This closes the last relative-incidence chain row.  It deliberately does not
identify the varied compressed Schur operator with the third variation of
the Weyl-squared action.  That independent action-derived Hessian variation,
followed by the differentiated all-row rank-310 SDR, is the next gate.
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
        raise AssertionError("upper relative-saddle artifact is stale")
    print("NARIAI_TRANSVERSE_RELATIVE_SADDLE_UPPER_CHAIN_V1: PASS")


if __name__ == "__main__":
    main()
