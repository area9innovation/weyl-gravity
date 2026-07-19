from closed_universe_observers.generate_berger_108_row_apparatus_scalar_bv_q2_pbw import build, payload, scalar_template


def test_scalar_template_is_complete_certified_theta_block():
    assert len(scalar_template()) == 24


def test_ten_apparatus_scalar_blocks_are_exported():
    value = build()
    assert value["payload"]["block_count"] == 10
    assert value["payload"]["term_count"] == 240
    assert all(block["term_count"] == 24 for block in value["payload"]["blocks"])


def test_pairing_isometry_transfers_cyclicity():
    audit = build()["pairing_and_cyclicity_audit"]
    assert audit["apparatus_pairing_isometry_defect_count"] == 0
    assert audit["term_bijection_defect_count"] == 0


def test_term_deletion_is_detected():
    exact = payload()
    mutated = payload(delete_last_term=True)
    assert mutated["term_count"] == exact["term_count"] - 1
    assert mutated["canonical_sha256"] != exact["canonical_sha256"]


def test_subblock_does_not_promote_complete_interactions():
    disposition = build()["activation_disposition"]
    assert disposition["scalar_BV_q2_subblock_exported"] is True
    assert disposition["complete_apparatus_q2_exported"] is False
    assert disposition["scalar_q3_exported"] is False
    assert disposition["detector_response_on_second_order_cone_authorized"] is False
