import json

from closed_universe_observers.generate_berger_108_row_temporal_common_action_ward_orbit import (
    CERTIFICATE,
    PAYLOAD,
)


def documents():
    return json.loads(CERTIFICATE.read_text()), json.loads(PAYLOAD.read_text())


def test_common_action_scale_system_has_no_nondegenerate_solution():
    certificate, payload = documents()
    audit = payload["normalization_compatibility"]
    assert audit["matrix"] == [[1, 0, -2], [1, -1, 0], [0, 1, -1]]
    assert (audit["determinant"], audit["rank"], audit["nullity"]) == (-1, 3, 0)
    assert audit["nondegenerate_common_action_pairing_exists"] is False
    assert certificate["common_action_export"]["disposition"] == "NO_CERTIFIED_MAP"


def test_factor_two_mutation_is_decisive_but_not_a_repair():
    _, payload = documents()
    mutation = payload["factor_two_mutation"]
    assert mutation["detected"] is True
    assert mutation["mutated_determinant"] == 0
    assert mutation["mutated_null_vector"] == [1, 1, 1]
    assert mutation["scientific_status"].startswith("MUTATION_ONLY")


def test_prior_temporal_witness_persists_under_action_equivalent_presentation():
    certificate, payload = documents()
    witness = certificate["persistent_witness"]
    current = witness["current"]
    assert witness["identical_to_prior_first_witness"] is True
    assert (
        current["output_row"],
        current["left_input_row"],
        current["right_input_row"],
    ) == (52, 55, 84)
    assert current["left_pbw_multiindex"] == [1, 1, 0, 0]
    assert (
        payload["action_equivalent_presentation_mutation"]["witness_survives"]
        is True
    )


def test_every_downstream_promotion_remains_fail_closed():
    certificate, payload = documents()
    assert certificate["atlas_status"] == "OBSTRUCTED"
    assert certificate["flags"]["COMPONENT_ARITY_IDENTITIES_CERTIFIED"] is False
    assert all(
        disposition is False
        for name, disposition in certificate["activation_disposition"].items()
        if name != "common_action_carrier_obstruction_certified"
    )
    assert (
        payload["later_memory_clock_rows"]["status"]
        == "NOT_EVALUATED_AFTER_FIRST_PERSISTENT_NONZERO_WITNESS"
    )
