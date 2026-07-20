import json

from closed_universe_observers import generate_berger_apparatus_z2_memory_nondefinition_after_repaired_reduction as subject


def test_terminal_physical_reduction_is_replayed():
    replay = subject.build_payload()["terminal_prerequisite_replay"]
    assert replay["physical_reduction_atlas_status"] == "NO_CERTIFIED_MAP"
    assert replay["required_fields_present"] == []


def test_every_receiver_stage_is_undefined():
    assert set(subject.build_payload()["undefined_receiver_chain"].values()) == {"NO_CERTIFIED_MAP"}


def test_correction_classes_remain_separate_and_fail_closed():
    classes = subject.build_payload()["correction_class_disposition"]
    assert set(classes) == {"bounded_or_quasiperiodic", "smooth_secular", "causal_or_retarded"}
    assert set(classes.values()) == {"NO_CERTIFIED_MAP"}


def test_forbidden_substitutions_are_rejected():
    assert all(value.startswith("REJECTED") for value in subject.build_payload()["forbidden_substitutions"].values())


def test_written_certificate_matches_fresh_build():
    payload = subject.build_payload()
    assert json.loads(subject.CERTIFICATE.read_text()) == subject.build_certificate(payload)
