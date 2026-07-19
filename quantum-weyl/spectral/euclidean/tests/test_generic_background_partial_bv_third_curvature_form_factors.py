import json

from spectral.euclidean import generic_background_partial_bv_third_curvature_form_factors as producer
from spectral.euclidean import verify_generic_background_partial_bv_third_curvature_form_factors as consumer


def _certificate():
    value = json.loads(producer.OUTPUT.read_text())
    producer.validate(value)
    return value


def test_sector_disposition_is_fail_closed():
    value = _certificate()
    assert value["sector_disposition"] == {
        "physical_Hessian": "COMPUTED",
        "ghost_n3": "COMPUTED",
        "ghost_vector_n1_n2": "COMPUTED",
        "ghost_longitudinal_and_mixed": "NOT_COMPUTED",
        "remaining_BV": "NOT_COMPUTED",
        "finite_C2_normalization": "NOT_FIXED",
    }
    flags = value["claim_flags"]
    assert flags["PARTIAL_BV_FIVE_CARRIER_REPRESENTATIVE_COMPUTED"]
    assert not flags["GHOST_LONGITUDINAL_CARRIERS_INCLUDED"]
    assert not flags["FULL_BV_FORM_FACTORS_COMPUTED"]


def test_channel_and_quotient_ledger():
    value = _certificate()
    assert len(value["channel_rows"]) == 11
    assert value["quotient_ledger"]["quotient_dimension"] == 10
    assert value["quotient_ledger"]["relation_status"] == "ZERO_COEFFICIENTWISE"


def test_every_channel_has_sector_receipts_and_holdouts():
    for row in _certificate()["channel_rows"]:
        assert set(row["included_sector_recipe"]) == {
            "physical_Hessian", "ghost_n3", "ghost_vector_n1_n2"
        }
        assert [holdout["point"] for holdout in row["exact_holdouts"]] == [
            [2, 3, 5], [3, 5, 7]
        ]


def test_independent_consumer():
    assert consumer.main() == 0
