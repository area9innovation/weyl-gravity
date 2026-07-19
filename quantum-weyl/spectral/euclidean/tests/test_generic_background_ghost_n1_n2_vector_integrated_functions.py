import json

from spectral.euclidean import generic_background_ghost_n1_n2_vector_integrated_functions as producer
from spectral.euclidean import verify_generic_background_ghost_n1_n2_vector_integrated_functions as consumer


def _certificate():
    value = json.loads(producer.OUTPUT.read_text())
    producer.validate(value)
    return value


def test_exact_moment_reduction_and_channel_counts():
    value = _certificate()
    identities = value["identity_ledger"]
    assert all(
        status == "ZERO"
        for status in identities["moment_boundary_identity_status"].values()
    )
    assert identities["channel_count"] == 11
    assert identities["nonzero_channel_count"] == 6
    assert identities["zero_channel_count"] == 5
    assert identities["maximum_numerator_degree"] == 2


def test_vector_slice_is_fail_closed():
    flags = _certificate()["claim_flags"]
    assert flags["GENERIC_GHOST_VECTOR_N1_N2_INTEGRATED_FUNCTIONS_COMPUTED"]
    assert flags["NO_NEW_TRANSCENDENTAL_MASTER_REQUIRED"]
    assert not flags["ALL_FIVE_HODGE_RESOLVENT_CARRIERS_EVALUATED"]
    assert not flags["GENERIC_GHOST_LONGITUDINAL_CARRIERS_EVALUATED"]
    assert not flags["COMPLETE_GENERIC_GHOST_THIRD_CURVATURE_FUNCTIONS_COMPUTED"]


def test_zero_channels_and_i28_relation():
    value = _certificate()
    zeros = {row["channel_id"] for row in value["channel_rows"] if row["identically_zero"]}
    assert zeros == {"I25_312", "I28_123", "I28_132", "I28_231", "I29_123"}
    assert value["identity_ledger"]["I28_relation_status"] == "ZERO_COEFFICIENTWISE"


def test_independent_consumer_and_direct_quadrature():
    assert consumer.main() == 0
