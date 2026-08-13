import copy
import json
import os
import unittest

from reverse_physics.verify_bt_auxiliary_pointer_local_unitary import (
    CERT_REL,
    ROOT,
    verify,
)


class AuxiliaryPointerLocalUnitaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, CERT_REL), encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    @staticmethod
    def set_path(row, path, value):
        cursor = row
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value

    def assert_rejected(self, path, value):
        row = copy.deepcopy(self.certificate)
        self.set_path(row, path, value)
        checks = verify(row)
        self.assertFalse(all(checks.values()), checks)

    def test_baseline(self):
        checks = verify(copy.deepcopy(self.certificate))
        self.assertTrue(all(checks.values()), [name for name, value in checks.items() if not value])

    def test_rejects_identity(self):
        self.assert_rejected(["certificate"], "PROMOTED")

    def test_rejects_lifecycle(self):
        self.assert_rejected(["lifecycle_state"], "LORENTZIAN_CERTIFIED")

    def test_rejects_tags(self):
        self.assert_rejected(["dependency_tags"], ["LORENTZIAN-CAUSAL"])

    def test_rejects_input_hash(self):
        self.assert_rejected(["provenance", "inputs", 6, "sha256"], "0" * 64)

    def test_rejects_carrier_fock_space(self):
        self.assert_rejected(["positive_free_local_carrier", "Hilbert_space"], "KREIN")

    def test_rejects_complex_adjoint(self):
        self.assert_rejected(["positive_free_local_carrier", "field_identification"], "Omega*=Omega")

    def test_rejects_dual_net(self):
        self.assert_rejected(["positive_free_local_carrier", "local_net"], "NO NET")

    def test_rejects_carrier_charge(self):
        self.assert_rejected(["positive_free_local_carrier", "internal_symmetries", 1], "neutral")

    def test_rejects_carrier_status(self):
        self.assert_rejected(["positive_free_local_carrier", "status"], "INTERACTING")

    def test_rejects_first_adjoint_inclusion(self):
        self.assert_rejected(["closable_charged_column", "adjoint_inclusions", 0], "A*=A")

    def test_rejects_second_adjoint_inclusion(self):
        self.assert_rejected(["closable_charged_column", "adjoint_inclusions", 1], "B*=B")

    def test_rejects_column(self):
        self.assert_rejected(["closable_charged_column", "column"], "K=0")

    def test_rejects_closability_proof(self):
        self.assert_rejected(["closable_charged_column", "closability_proof"], "assumed")

    def test_rejects_separate_esa_promotion(self):
        self.assert_rejected(["closable_charged_column", "separate_branch_essential_selfadjointness"], "PROVED")

    def test_rejects_column_status(self):
        self.assert_rejected(["closable_charged_column", "status"], "NOT_CLOSABLE")

    def test_rejects_K_entry(self):
        self.assert_rejected(["selfadjoint_pointer_block", "finite_rational_witness", "K", 0, 0], "2")

    def test_rejects_V_offdiagonal(self):
        self.assert_rejected(["selfadjoint_pointer_block", "finite_rational_witness", "V", 0, 2], "0")

    def test_rejects_V_diagonal(self):
        self.assert_rejected(["selfadjoint_pointer_block", "finite_rational_witness", "V", 0, 0], "1")

    def test_rejects_square(self):
        self.assert_rejected(["selfadjoint_pointer_block", "finite_rational_witness", "I_plus_V_squared", 0, 0], "0")

    def test_rejects_inverse(self):
        self.assert_rejected(["selfadjoint_pointer_block", "finite_rational_witness", "inverse_I_plus_V_squared", 0, 0], "0")

    def test_rejects_left_denominator(self):
        self.assert_rejected(["selfadjoint_pointer_block", "finite_rational_witness", "left_I_plus_KstarK", 0, 0], "0")

    def test_rejects_right_denominator(self):
        self.assert_rejected(["selfadjoint_pointer_block", "finite_rational_witness", "right_I_plus_KKstar", 0, 0], "0")

    def test_rejects_abstract_operator(self):
        self.assert_rejected(["selfadjoint_pointer_block", "operator"], "[[0,K],[K,0]]")

    def test_rejects_domain(self):
        self.assert_rejected(["selfadjoint_pointer_block", "domain"], "finite particles")

    def test_rejects_square_formula(self):
        self.assert_rejected(["selfadjoint_pointer_block", "square"], "V^2=0")

    def test_rejects_resolvent(self):
        self.assert_rejected(["selfadjoint_pointer_block", "resolvent"], "formal inverse")

    def test_rejects_range_criterion(self):
        self.assert_rejected(["selfadjoint_pointer_block", "conclusion"], "symmetric only")

    def test_rejects_selfadjoint_status(self):
        self.assert_rejected(["selfadjoint_pointer_block", "status"], "SYMMETRIC")

    def test_rejects_affiliation(self):
        self.assert_rejected(["local_functional_calculus", "affiliation_proof"], "assumed")

    def test_rejects_total_symmetry(self):
        self.assert_rejected(["local_functional_calculus", "symmetry"], "charge breaking")

    def test_rejects_local_unitary(self):
        self.assert_rejected(["local_functional_calculus", "unitary"], "formal Dyson series")

    def test_rejects_polar_block(self):
        self.assert_rejected(["local_functional_calculus", "ground_to_click_block"], "K")

    def test_rejects_click_effect(self):
        self.assert_rejected(["local_functional_calculus", "effects", 0], "E_click=0")

    def test_rejects_completeness(self):
        self.assert_rejected(["local_functional_calculus", "effects", 2], "sum<1")

    def test_rejects_vacuum_dark_promotion(self):
        self.assert_rejected(["local_functional_calculus", "vacuum_boundary"], "exactly vacuum dark")

    def test_rejects_calculus_status(self):
        self.assert_rejected(["local_functional_calculus", "status"], "PERTURBATIVE")

    def test_rejects_phase_inputs(self):
        self.assert_rejected(["operational_q8_tangent", "inputs"], "incoherent mixture")

    def test_rejects_pointer_readout(self):
        self.assert_rejected(["operational_q8_tangent", "readout"], "field vacuum projector")

    def test_rejects_half_contrast(self):
        self.assert_rejected(["operational_q8_tangent", "half_contrast"], "sum")

    def test_rejects_tangent_sign(self):
        self.assert_rejected(["operational_q8_tangent", "exact_tangent"], "minus")

    def test_rejects_phase_optimization(self):
        self.assert_rejected(["operational_q8_tangent", "phase_optimization"], "zero")

    def test_rejects_field_postselection(self):
        self.assert_rejected(["operational_q8_tangent", "locality"], "requires final field-vacuum projector")

    def test_rejects_q8_bound(self):
        self.assert_rejected(["operational_q8_tangent", "strict_bound"], "Q8=0")

    def test_rejects_tangent_status(self):
        self.assert_rejected(["operational_q8_tangent", "status"], "ALL_ORDER_BT")

    def test_rejects_Born_promotion(self):
        self.assert_rejected(["disposition", "positive_Hilbert_vs_public_generalized_Born_equivalence"], "PROVED")

    def test_rejects_interacting_net_promotion(self):
        self.assert_rejected(["disposition", "interacting_public_BT_local_net"], "CONSTRUCTED")

    def test_rejects_lambda10_promotion(self):
        self.assert_rejected(["disposition", "lambda10_and_higher_BT_control"], "PROVED")

    def test_rejects_Eq19_promotion(self):
        self.assert_rejected(["disposition", "general_Eq19"], "PROVED")

    def test_rejects_gravity_promotion(self):
        self.assert_rejected(["disposition", "gravity_or_metric_BV_BRST_transfer"], "CONSTRUCTED")

    def test_rejects_Lorentzian_promotion(self):
        self.assert_rejected(["disposition", "Lorentzian_causal_claim"], "ESTABLISHED")

    def test_rejects_missing_objects(self):
        self.assert_rejected(["missing_object_ledger"], [])

    def test_rejects_next_gate(self):
        self.assert_rejected(["next_gate"], "done")


if __name__ == "__main__":
    unittest.main()
