import json

from closed_universe_observers import generate_berger_apparatus_combined_q1_after_replacement_112 as subject


def test_pushout_row_count_is_derived():
    pushout = subject.build_payload()["typed_pushout"]
    assert pushout["direct_sum_row_count"] == 168
    assert pushout["relation_rank"] == 8
    assert pushout["combined_row_count"] == 160


def test_only_semantically_equal_memory_rows_are_shared():
    pushout = subject.build_payload()["typed_pushout"]
    assert len(pushout["shared_semantic_rows"]) == 8
    assert all(row["semantic_equality"] for row in pushout["shared_semantic_rows"])
    assert len(pushout["parent_only_rows"]) == 48


def test_complete_unary_identities_pass():
    unary = subject.build_payload()["complete_q1"]
    assert unary["q1_squared_defect_count"] == 0
    assert unary["odd_cyclicity_defect_count"] == 0
    assert unary["K_commutator_defect_count"] == 0


def test_detector_map_is_chain_compatible_but_not_reduced():
    detector = subject.build_payload()["support_and_detector"]
    assert detector["detector_chain_defect_count"] == 0
    assert detector["leading_response_rank"] == 2
    assert detector["full_physical_reduction"] == "NO_CERTIFIED_MAP"


def test_written_certificate_matches_fresh_build():
    assert json.loads(subject.CERTIFICATE.read_text()) == subject.build_certificate(subject.build_payload())
