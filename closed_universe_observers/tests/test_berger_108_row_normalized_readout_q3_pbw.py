import json
from closed_universe_observers.generate_berger_108_row_normalized_readout_q3_pbw import CERTIFICATE, PAYLOAD, readout_jet

def documents(): return json.loads(CERTIFICATE.read_text()),json.loads(PAYLOAD.read_text())
def test_second_jet_regresses_q2_and_profiles():
    certificate,_=documents(); audit=certificate["second_jet_and_cyclicity_audit"]; assert audit["first_jet_regression_defect_count"]==0; assert audit["second_jet_permutation_defect_count"]==0; assert audit["missing_second_profile_derivative_family_count"]==0; assert readout_jet(0,(0,1)).bilinear
def test_q3_is_symmetric_cyclic_and_fail_closed():
    certificate,payload=documents(); audit=certificate["second_jet_and_cyclicity_audit"]; assert audit["graded_symmetry_defect_count"]==0; assert audit["p_to_Maxwell_formal_transpose_defect_count"]==0; assert audit["p_to_geometry_formal_transpose_defect_count"]==0; assert payload["operator_key_count"]>0; assert certificate["activation_disposition"]["complete_scalar_q3_exported"] is False; assert certificate["activation_disposition"]["detector_response_on_second_order_cone_authorized"] is False
