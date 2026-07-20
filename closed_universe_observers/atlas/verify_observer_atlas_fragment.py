#!/usr/bin/env python3
"""Verify the generated observer atlas fragment and its evidence hashes."""
import hashlib, json
from closed_universe_observers.atlas.generate_observer_atlas_fragment import OUTPUT, ROOT, STATUSES, build
from residual_atlas.validate_fragment import validate

def main() -> int:
    value = json.loads(OUTPUT.read_text())
    assert value == build()
    validate(OUTPUT)
    assert value["status_vocabulary"] == STATUSES
    ids = {row["id"] for row in value["entries"]}
    assert "observer.berger.second_order_cone_restriction" in ids
    assert "observer.berger.detector_profile.recoil_numerical_input_contract_v2" in ids
    assert "observer.berger.interaction.pbw_108_component_map" in ids
    assert "observer.berger.interaction.pbw_108_component_jet_contract" in ids
    assert "observer.berger.interaction.pbw_108_background_differential_quotient" in ids
    assert "observer.berger.interaction.pbw_108_emitter_q1_overlay" in ids
    assert "observer.berger.interaction.pbw_108_memory_q1_overlay" in ids
    assert "observer.berger.interaction.pbw_108_shifted_q2_phi2_overlay" in ids
    assert "observer.berger.interaction.pbw_108_local_rod_hessian_overlay" in ids
    assert "observer.berger.interaction.pbw_108_nonlinear_clock_second_jet" in ids
    assert "observer.berger.interaction.pbw_108_apparatus_q2_q3_scalarization_obstruction" in ids
    assert "observer.berger.interaction.nonlinear_clock_radial_canonical_map_f2_f3" in ids
    assert "observer.berger.interaction.apparatus_scalar_bv_q2_pbw" in ids
    assert "observer.berger.interaction.dressed_rod_clock_q2_pbw" in ids
    assert "observer.berger.interaction.rod_metric_q2_pbw" in ids
    assert "observer.berger.interaction.memory_transport_q2_pbw" in ids
    assert "observer.berger.interaction.normalized_readout_q2_pbw" in ids
    assert "observer.berger.interaction.emitter_physical_q2_pbw" in ids
    assert "observer.berger.interaction.emitter_diff_bv_q2_pbw" in ids
    assert "observer.berger.interaction.complete_q2_pbw" in ids
    assert "observer.berger.interaction.rod_metric_q3_pbw" in ids
    assert "observer.berger.interaction.memory_transport_q3_pbw" in ids
    assert "observer.berger.interaction.normalized_readout_q3_pbw" in ids
    assert "observer.berger.interaction.emitter_physical_q3_pbw" in ids
    assert "observer.berger.interaction.q3_structural_zero_ledger" in ids
    assert "observer.berger.interaction.complete_q3_pbw" in ids
    assert "observer.berger.interaction.complete_arity_two_obstruction" in ids
    assert "observer.berger.interaction.temporal_common_action_carrier_obstruction" in ids
    assert "observer.berger.interaction.common_action_obstruction_module" in ids
    assert "observer.berger.interaction.two_pair_112_no_go" in ids
    assert "observer.berger.interaction.ward_cokernel_irrep_closure_obstruction" in ids
    assert "observer.berger.interaction.minimal_invariant_scalar_hessian_channel_no_go" in ids
    assert "observer.berger.interaction.common_action_observable_replay_disposition" in ids
    assert "observer.berger.interaction.profile_jet_invariant_hessian_action_repair" in ids
    assert "observer.berger.interaction.higher_jet_invariant_action_module_classification" in ids
    assert "observer.berger.interaction.order_three_common_action_promotion_gate" in ids
    assert "observer.berger.interaction.quartic_common_action_completion_module" in ids
    assert "observer.berger.interaction.quartic_completion_moduli_observer_invariance" in ids
    assert "observer.berger.interaction.auxiliary_diff_bv_scalar_orbit_repair" in ids
    assert "observer.berger.interaction.direct_temporal_ak_diff_covariance_repair" in ids
    assert "observer.berger.interaction.quartic_calibration_relational_redshift_disposition" in ids
    assert "observer.berger.interaction.temporal_maxwell_emitter_antifield_covariance_module" in ids
    crosswalks = [row for row in value["entries"] if row["id"].startswith("observer.crosswalk")]
    assert {row["id"] for row in crosswalks} == {
        "observer.crosswalk.berger_physical_branch_to_detector",
        "observer.crosswalk.compact_product_exceptional_resonance_to_berger",
    }
    for crosswalk in crosswalks:
        assert set(crosswalk["descriptions"].values()) == {"NO_CERTIFIED_MAP"}
        assert set(crosswalk["observer_data"][name]["status"] for name in crosswalk["observer_data"]) == {"NO_CERTIFIED_MAP"}
    for entry in value["entries"]:
        for evidence in entry["evidence"]:
            path = ROOT / evidence["path"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
            assert json.loads(path.read_text())["result_id"] == evidence["result_id"]
    print("observer residual-atlas fragment verification: PASS"); return 0

if __name__ == "__main__": raise SystemExit(main())
