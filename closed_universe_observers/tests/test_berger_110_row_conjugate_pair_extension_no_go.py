import json

from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    CERTIFICATE,
)


def result():
    return json.loads(CERTIFICATE.read_text())


def test_only_zero_one_degree_pair_survives():
    classes = result()["bounded_extension_ansatz"]["degree_classification"]
    assert classes == [
        {
            "degrees": [-1, 2],
            "reason": (
                "q2 on two degree-zero old inputs has degree one, but this "
                "pair contains no degree-one row"
            ),
            "status": "OBSTRUCTED_BY_DEGREE_SUPPORT",
        },
        {
            "degrees": [0, 1],
            "row_ids": ["chi", "chi_plus"],
            "status": "SOLE_SURVIVING_DEGREE_CLASS",
        },
    ]


def test_pairing_and_action_class_are_exact():
    value = result()
    pairing = value["bounded_extension_ansatz"]["pairing"]
    assert pairing["shape"] == [110, 110]
    assert pairing["rank"] == 110
    assert value["compatibility_solution_locus"]["quotient_representative"] == {
        "p": 1,
        "lambda": 1,
        "mu": 0,
        "beta_0": -1,
        "beta_1": -1,
    }
    assert value["compatibility_solution_locus"][
        "class_count_modulo_pair_rescaling"
    ] == 1


def test_regenerated_action_cancels_prior_but_not_second_witness():
    audit = result()["action_regeneration_and_substitution"]
    assert audit["regenerated_q1_key_count"] == 2
    assert audit["regenerated_q2_key_count"] == 276
    assert audit["prior_witness_after_substitution"]["nonzero"] is False
    assert audit["second_emitter_prior_witness_after_substitution"]["nonzero"] is False
    assert audit["constant_unary_exclusion_fixture"]["conclusion"] == "mu=0"
    obstruction = audit["first_scoped_obstruction"]
    assert obstruction["nonzero"] is True
    assert (
        obstruction["left_input_row_id"],
        obstruction["left_pbw_multiindex"],
        obstruction["right_input_row_id"],
        obstruction["right_pbw_multiindex"],
    ) == ("A_0", [0, 1, 0, 0], "K0_12", [0, 0, 1, 0])
    assert audit["auxiliary_action_support_at_first_obstruction"][
        "q2_chi_plus_A0_K0_12_key_count"
    ] == 0


def test_no_downstream_gate_is_promoted():
    value = result()
    assert value["atlas_status"] == "OBSTRUCTED"
    assert not any(value["activation_disposition"].values())
    assert value["minimal_no_go"]["next_dimension_not_claimed"] is True
