#!/usr/bin/env python3
"""Associative transverse Nariai parent-middle and shifted-chain replay."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    _add,
)
from d_quotient_classical.causal_transfer.coefficient_jet_pbw import (
    CoefficientJetPBW,
    JetLinearizedOperator,
    MissingCoefficientJet,
    jet_add,
    jet_scale,
    parallel_zero_variation,
)
from d_quotient_classical.causal_transfer.nariai_transverse_corrected_bgg_splitting_coefficient_jets import (
    _count,
    _deserialize_table,
    _difference,
    _table,
    operator_data,
)
from d_quotient_classical.causal_transfer.nariai_curvature_incidence_first_square import (
    curvature_incidence,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ASSOCIATIVE_MIDDLE_SHIFTED_CHAIN_REPLAY_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-associative-middle-shifted-chain-replay.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-associative-middle-shifted-chain-replay-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_associative_middle_shifted_chain_replay.py"
TESTS = HERE / "tests/test_nariai_transverse_associative_middle_shifted_chain_replay.py"
SPLITTING = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_CORRECTED_BGG_SPLITTING_COEFFICIENT_JETS_V1.json"
OLD_ASSOCIATIVITY = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_PBW_ASSOCIATIVITY_GATE_V1.json"
OLD_POINT_DATA = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1.json"
BACKEND = HERE / "coefficient_jet_pbw.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def exact_data() -> dict[str, Any]:
    value = operator_data()
    old = json.loads(OLD_POINT_DATA.read_text())["exact_data"]
    middle_delta = _deserialize_table(
        old["operator_variations"]["Yang_Mills_middle"]
    )

    def middle_provider(word: tuple[int, ...]):
        if word:
            raise MissingCoefficientJet("Yang-Mills middle", word)
        return middle_delta

    middle = JetLinearizedOperator(
        value["middle"]["yang_mills_middle"],
        middle_provider,
        "M-parent",
    )
    l1 = value["L1_corrected"]
    k_p0 = parallel_zero_variation(value["automorphism"]["k_p0"], "K-p0")
    h1 = CoefficientJetPBW(value["pbw"]["H1"].linearized_pbw)
    c0 = CoefficientJetPBW(value["pbw"]["C0"].linearized_pbw)

    phi = h1.compose(middle, l1, "Phi=M-L1")
    left = c0.compose(phi, k_p0, "(M-L1)-Kp0")
    l1_k = c0.compose(l1, k_p0, "L1-Kp0")
    right = c0.compose(middle, l1_k, "M-(L1-Kp0)")
    associator = jet_add(left, jet_scale(right, -1), name="associator")

    # Recover d_parent without changing the splitting producer: d_aut differs
    # from it by the base incidence table already serialized by the
    # automorphism fixture.
    automorphism = value["automorphism"]
    incidence = curvature_incidence()["incidence"] * automorphism["projection0"]
    total0 = _add(value["d_aut"].base, {(): incidence})
    parent_identity = c0.compose(
        middle, parallel_zero_variation(total0, "d-parent"), "M-d-parent"
    )

    shifted_chain = jet_add(
        c0.compose(middle, value["d_aut"], "M-d-aut"),
        jet_scale(left, -1),
        name="shifted-chain",
    )
    phi_value = phi.delta(())
    associator_value = associator.delta(())
    parent_value = parent_identity.delta(())
    shifted_value = shifted_chain.delta(())
    if associator.base or associator_value:
        raise AssertionError("associative M-L1-Kp0 replay failed")
    if parent_identity.base or parent_value:
        raise AssertionError("parent Yang-Mills identity failed")
    if shifted_chain.base or shifted_value:
        raise AssertionError("shifted-chain replay failed")

    old_phi = _deserialize_table(old["operator_variations"]["Phi"])
    phi_defect = _difference(phi_value, old_phi)
    old_shifted = old["identity_defects"]["shifted_chain_variation"]
    return {
        "typed_replay": {
            "triple": "M_parent o L1_corrected o (K p0)",
            "left_parenthesization": "(M_parent o L1_corrected) o (K p0)",
            "right_parenthesization": "M_parent o (L1_corrected o (K p0))",
            "base_associator_coefficients": _count(associator.base),
            "variation_associator_coefficients": _count(associator_value),
            "middle_coefficient_jet_words_requested": [
                list(word)
                for word in sorted(middle.requested_words, key=lambda word: (len(word), word))
            ],
        },
        "parent_identity": {
            "identity": "M_parent d_parent = 0",
            "base_defect_coefficients": _count(parent_identity.base),
            "variation_defect_coefficients": _count(parent_value),
        },
        "authoritative_phi_variation": _table(phi_value),
        "old_phi_comparison": {
            "defect": _table(phi_defect),
            "old_point_phi_authoritative": not phi_defect,
        },
        "shifted_chain": {
            "identity": "M_parent d_aut - (M_parent L1_corrected)(K p0) = 0",
            "base_defect_coefficients": _count(shifted_chain.base),
            "variation_defect_coefficients": _count(shifted_value),
            "old_backend_reported_coefficients": old_shifted["nonzero_coefficients"],
            "old_backend_defect_authoritative": False,
        },
        "disposition": {
            "associative_parent_middle_replay_complete": True,
            "shifted_chain_exact": True,
            "compressed_schur_replayed": False,
            "rank_310_transverse_SDR_decided": False,
        },
    }


def build() -> dict[str, Any]:
    data = exact_data()
    refs = {}
    for key, path, result_id in (
        ("corrected_splitting_jets", SPLITTING, "NARIAI_TRANSVERSE_CORRECTED_BGG_SPLITTING_COEFFICIENT_JETS_V1"),
        ("old_associativity_gate", OLD_ASSOCIATIVITY, "NARIAI_TRANSVERSE_LINEARIZED_PBW_ASSOCIATIVITY_GATE_V1"),
        ("old_point_replay", OLD_POINT_DATA, "NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1"),
    ):
        payload = json.loads(path.read_text())
        if payload["result_id"] != result_id:
            raise AssertionError(f"dependency drifted: {key}")
        refs[key] = {"path": str(path.relative_to(ROOT)), "result_id": result_id, "sha256": _sha(path)}
    sources = (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, BACKEND)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "nariai-transverse-associative-middle-shifted-chain-replay-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_ASSOCIATIVE_MIDDLE_SHIFTED_CHAIN_REPLAY_V1",
        "result_state": "ASSOCIATIVE_PARENT_MIDDLE_AND_SHIFTED_CHAIN_EXACT",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": refs,
        "exact_data": data,
        "exact_checks": {
            "typed_associator_zero": data["typed_replay"]["variation_associator_coefficients"] == 0,
            "parent_identity_zero": data["parent_identity"]["variation_defect_coefficients"] == 0,
            "shifted_chain_zero": data["shifted_chain"]["variation_defect_coefficients"] == 0,
            "old_shifted_chain_defect_rejected": not data["shifted_chain"]["old_backend_defect_authoritative"],
            "compressed_schur_not_overclaimed": not data["disposition"]["compressed_schur_replayed"],
            "rank_310_not_overclaimed": not data["disposition"]["rank_310_transverse_SDR_decided"],
        },
        "flags": {
            "NARIAI_TRANSVERSE_ASSOCIATIVE_PBW_REPLAY": True,
            "NARIAI_TRANSVERSE_PARENT_YANG_MILLS_IDENTITY": True,
            "NARIAI_TRANSVERSE_SHIFTED_CHAIN_IDENTITY": True,
            "NARIAI_TRANSVERSE_COMPRESSED_SCHUR_REPLAY": False,
            "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_HOM_ADJOINT_MIDDLE_AND_COMPRESSED_SCHUR_REPLAY",
        "claim_boundary": "This certificate replays the transverse parent Yang-Mills identity, the two parenthesizations of M-L1-Kp0, and the shifted-chain identity in the associative coefficient-jet PBW algebra. The former 207-coefficient defect is rejected as a backend artifact. Only the zeroth middle coefficient jet is required for these identities. The certificate does not yet derive positive-order middle or Hom-adjoint jets, replay the compressed Schur operator, assemble the complete rank-310 SDR, or prove support or causal transfer.",
        "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in sources},
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_associative_middle_shifted_chain_replay --check",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_associative_middle_shifted_chain_replay.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_associative_middle_shifted_chain_replay",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-associative-middle-shifted-chain-replay-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_ASSOCIATIVE_MIDDLE_SHIFTED_CHAIN_REPLAY_V1.json",
        ],
    }


def report(payload: dict[str, Any]) -> str:
    data = payload["exact_data"]
    return rf"""# Transverse associative middle and shifted-chain replay

The repaired coefficient-jet algebra gives identical results for

\[
(M_{{\rm parent}}L_1^{{\rm corrected}})(Kp_0)
\quad\text{{and}}\quad
M_{{\rm parent}}(L_1^{{\rm corrected}}Kp_0).
\]

Both the base and first-variation associators have zero coefficients.  The
parent Yang--Mills identity also replays exactly, and consequently

\[
M_{{\rm parent}}d_{{\rm aut}}
-(M_{{\rm parent}}L_1^{{\rm corrected}})(Kp_0)=0
\]

has zero base and variation defects.  The authoritative `Phi` variation has
`{data['authoritative_phi_variation']['nonzero_coefficients']}` coefficients.
The previous point-only backend reported
`{data['shifted_chain']['old_backend_reported_coefficients']}` shifted-chain
coefficients; that defect is now conclusively a backend artifact.

The next gate is the positive-order middle/Hom-adjoint and compressed-Schur
replay.  No complete rank-310 SDR or causal theorem is promoted here.
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
        raise AssertionError("associative middle replay artifact is stale")
    print("NARIAI_TRANSVERSE_ASSOCIATIVE_MIDDLE_SHIFTED_CHAIN_REPLAY_V1: PASS")


if __name__ == "__main__":
    main()
