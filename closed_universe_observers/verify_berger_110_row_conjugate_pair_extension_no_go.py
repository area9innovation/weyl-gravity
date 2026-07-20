#!/usr/bin/env python3
"""Independently verify the bounded 110-row conjugate-pair no-go."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.berger_108_row_component_jet_contract import serialize
from closed_universe_observers.generate_berger_108_row_arity_two_obstruction import (
    _q1_source_parts,
)
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    CERTIFICATE,
    CHI,
    CHI_PLUS,
    DEPENDENCIES,
    CONSTANT_UNARY_WITNESS_KEY,
    PRIOR_WITNESS_KEY,
    ROOT,
    SCHEMA,
    SECOND_WITNESS_KEY,
    SECOND_EMITTER_PRIOR_WITNESS_KEY,
    extension_q1,
    extension_q2,
    interaction_action,
)


def _extension_row(*, interaction_scale: int) -> arity.BilinearRow:
    q1 = {(0, 0): extension_q1()}
    q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
    for (output, left, left_word, right, right_word), coefficient in extension_q2(
        interaction_scale=interaction_scale
    ).items():
        arity.add_bilinear_term(
            q2[(0, 0)].setdefault(output, {}),
            (left, left_word, right, right_word),
            coefficient,
        )
    return arity.arity_two_row(
        52,
        (0, 0),
        q1,
        q2,
        arity.parities() + (0, 1),
    )


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    for name, reference in value["dependency_refs"].items():
        path = ROOT / reference["path"]
        assert path == DEPENDENCIES[name]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference["sha256"]

    ansatz = value["bounded_extension_ansatz"]
    assert ansatz["degree_classification"][0]["degrees"] == [-1, 2]
    assert ansatz["degree_classification"][0]["status"] == (
        "OBSTRUCTED_BY_DEGREE_SUPPORT"
    )
    assert ansatz["degree_classification"][1]["degrees"] == [0, 1]
    assert ansatz["pairing"]["new_entries"] == [
        [CHI, CHI_PLUS, "p"],
        [CHI_PLUS, CHI, "-p"],
    ]
    assert ansatz["pairing"]["rank"] == 110
    assert len(interaction_action()) == 30
    assert len(extension_q1()) == 2
    assert len(extension_q2()) == 276

    # Raw source-pair replay of both old coefficients.
    emitter_q1 = _q1_source_parts()["emitter"]
    old_prior_row = arity.arity_two_row(
        52,
        (0, 0),
        emitter_q1,
        arity.load_q2(sources={"emitter_Diff_BV"}),
        arity.parities(),
    )
    old_prior_row = arity.specialize_bilinear_rows({52: old_prior_row})[52]
    old_prior = old_prior_row[PRIOR_WITNESS_KEY]
    old_second_emitter_prior = old_prior_row[SECOND_EMITTER_PRIOR_WITNESS_KEY]
    old_second = arity.arity_two_row(
        52,
        (0, 0),
        emitter_q1,
        arity.load_q2(sources={"base_maxwell_typed"}),
        arity.parities(),
    )
    old_second = arity.specialize_bilinear_rows({52: old_second})[52][
        SECOND_WITNESS_KEY
    ]

    # The action-derived auxiliary contribution cancels the prior source pair.
    auxiliary = arity.specialize_bilinear_rows(
        {52: _extension_row(interaction_scale=-1)}
    )[52]
    cancelled = replay.add(old_prior, auxiliary[PRIOR_WITNESS_KEY])
    assert not cancelled
    assert not replay.add(
        old_second_emitter_prior,
        auxiliary[SECOND_EMITTER_PRIOR_WITNESS_KEY],
    )
    assert SECOND_WITNESS_KEY not in auxiliary

    audit = value["action_regeneration_and_substitution"]
    assert audit["prior_witness_after_substitution"]["coefficient"] == []
    assert audit["prior_witness_after_substitution"]["nonzero"] is False
    assert audit["second_emitter_prior_witness_after_substitution"]["nonzero"] is False
    assert serialize(old_second) == audit["first_scoped_obstruction"]["coefficient"]

    constant = arity.specialize_bilinear_rows(
        {
            52: arity.arity_two_row(
                52,
                (0, 0),
                {(0, 0): extension_q1(temporal_order=0)},
                {
                    degree: (
                        {
                            output: {
                                (left, left_word, right, right_word): coefficient
                                for (
                                    current_output,
                                    left,
                                    left_word,
                                    right,
                                    right_word,
                                ), coefficient in extension_q2().items()
                                if current_output == output
                            }
                            for output in {key[0] for key in extension_q2()}
                        }
                        if degree == (0, 0)
                        else {}
                    )
                    for degree in arity.SUPPORTED_BIDEGREES
                },
                arity.parities() + (0, 1),
            )
        }
    )[52][CONSTANT_UNARY_WITNESS_KEY]
    fixture = audit["constant_unary_exclusion_fixture"]
    assert serialize(constant) == fixture["mu_basis_coefficient"]
    assert fixture["coefficient_monomials_disjoint"]

    # Sign and decoupling mutations are independently sensitive.
    flipped = arity.specialize_bilinear_rows(
        {52: _extension_row(interaction_scale=1)}
    )[52]
    assert replay.add(old_prior, flipped[PRIOR_WITNESS_KEY])
    mutations = audit["mutations"]
    assert mutations["decouple_auxiliary_interaction"]["detected"]
    assert mutations["flip_auxiliary_interaction_sign"]["detected"]
    assert mutations["drop_typed_Maxwell_source"]["detected"]
    assert mutations["inherited_factor_two_control"]["mutated_null_vector"] == [
        1,
        1,
        1,
    ]

    disposition = value["activation_disposition"]
    assert not any(disposition.values())
    print("BERGER_110_ROW_CONJUGATE_PAIR_EXTENSION_NO_GO independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
