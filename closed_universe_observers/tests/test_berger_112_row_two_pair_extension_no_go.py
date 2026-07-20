import json

from closed_universe_observers.generate_berger_112_row_two_pair_extension_no_go import (
    CERTIFICATE,
    PAYLOAD,
)


def result():
    return json.loads(CERTIFICATE.read_text())


def payload():
    return json.loads(PAYLOAD.read_text())


def test_complete_two_pair_carrier_and_action_basis():
    value = result()["complete_enlarged_ansatz"]
    assert value["carrier"]["total_rows"] == 112
    assert [row["degree"] for row in value["carrier"]["new_rows"]] == [0, 1, 0, 1]
    assert value["pairing"]["new_block_rank"] == 4
    assert value["pairing"]["total_pairing_rank"] == 112
    basis = value["basis_regeneration"]
    assert basis["complete_unary_basis_key_count"] == 8
    assert basis["complete_binary_basis_key_count"] == 552


def test_two_pairs_remove_rank_one_locus_but_not_cokernel():
    value = result()
    quotient = value["field_redefinition_quotient"]
    assert quotient["invariant"] == "Z=U^T B"
    assert quotient["one_pair_locus"] == "rank(Z)<=1"
    assert quotient["two_pair_locus"] == "rank(Z)<=2=all 2x2 matrices"
    theorem = value["action_to_ward_theorem"]
    assert theorem["two_pair_reachable_parameter_space_dimension"] == 4
    assert theorem["linear_image_rank"] == 4
    assert theorem["cokernel_dimension"] == 440


def test_every_original_tau_star_coefficient_is_serialized():
    audit = payload()["complete_original_tau_star_replay"]
    assert audit["all_input_key_count"] == 856
    assert audit["all_input_monomial_count"] == 880
    assert audit["original_108_input_key_count"] == len(audit["entries"]) == 824
    assert audit["original_108_input_monomial_count"] == 848
    assert audit["prior_witness_zero"]
    assert audit["second_emitter_prior_witness_zero"]


def test_first_obstruction_and_forced_next_class():
    value = result()
    obstruction = value["first_exact_obstruction"]
    assert obstruction["display"] == (
        "tau_star <- (e1 A_0,e2 K0_12) = -2 g0 h0"
    )
    next_gate = value["next_minimal_enlargement"]
    assert next_gate["more_scalar_pairs"] == "PROVED_INSUFFICIENT_FOR_ALL_N>=2"
    assert next_gate["higher_outer_scalar_jet_only"] == (
        "PROVED_INSUFFICIENT_AT_EVERY_FINITE_ORDER_BY_PREDECESSOR"
    )
    assert next_gate["smallest_representation"] == "OPEN"
    assert not any(value["activation_disposition"].values())
