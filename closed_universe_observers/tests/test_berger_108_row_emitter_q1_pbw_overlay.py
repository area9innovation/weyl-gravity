from closed_universe_observers.generate_berger_108_row_emitter_q1_pbw_overlay import (
    build,
    coderivative,
    compose,
    exterior_derivative,
)


def test_support_local_de_rham_complex_is_exactly_nilpotent():
    for degree in range(3):
        assert compose(exterior_derivative(degree + 1), exterior_derivative(degree)) == {}
    for degree in range(1, 4):
        assert compose(coderivative(degree), coderivative(degree + 1)) == {}


def test_six_covariant_ranges_are_scalarized():
    overlay = build()["emitter_overlay"]
    assert overlay["block_count"] == 6
    assert [block["id"] for block in overlay["blocks"]] == [
        "A_to_K0_plus", "K0_to_A_plus", "K0_massive_equation",
        "A_to_K1_plus", "K1_to_A_plus", "K1_massive_equation",
    ]
    assert overlay["serialized_term_count"] > overlay["nonzero_matrix_position_count"]


def test_switch_leibniz_jets_are_explicit():
    value = build()
    blocks = {block["id"]: block for block in value["emitter_overlay"]["blocks"]}
    for emitter in (0, 1):
        factors = [
            factor
            for entry in blocks[f"K{emitter}_to_A_plus"]["entries"]
            for term in entry["terms"]
            for factor in term["coefficient_factors"]
            if factor["kind"] == "profile"
        ]
        assert any(sum(factor["spacetime_multiindex"]) == 1 for factor in factors)


def test_mass_terms_and_base_hash_are_pinned():
    value = build()
    rendered = str(value["emitter_overlay"]["blocks"])
    assert "m0_squared" in rendered and "m1_squared" in rendered
    assert len(value["base_composition_contract"]["base_payload_sha256"]) == 64


def test_complete_q1_remains_fail_closed_on_apparatus_overlay():
    value = build()
    assert value["flags"]["SCALAR_EMITTER_Q1_PBW_OVERLAY_EXPORTED"]
    assert not value["flags"]["SCALAR_APPARATUS_Q1_PBW_OVERLAY_EXPORTED"]
    assert not value["flags"]["SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED"]
