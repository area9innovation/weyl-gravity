from __future__ import annotations

from copy import deepcopy
import json
import unittest

from anomalies.conformal_gauge_field_carrier_obstruction import build, validate
from anomalies.conformal_gauge_field_carrier_obstruction_certificate import (
    OUTPUT,
    certificate,
)
from anomalies.verify_conformal_gauge_field_carrier_obstruction import (
    validate_receiver,
    verify,
    verify_payload,
)


HASH = "0" * 64
ZERO = {"numerator": 0, "denominator": 1}


def complete_receiver_fixture() -> dict:
    return {
        "schema": "quantum-weyl-conformal-gauge-field-carrier-receiver-v1",
        "candidate_id": "fixture_complex_gauge_field",
        "background_scope": "generic compact Riemannian four-manifold",
        "fields": [
            {
                "field_id": "h",
                "tensor_type": "(2,1)",
                "Grassmann_parity": "ODD",
                "Weyl_weight": "1/2",
            },
            {
                "field_id": "hbar",
                "tensor_type": "(1,2)",
                "Grassmann_parity": "ODD",
                "Weyl_weight": "1/2",
            },
        ],
        "ghosts": [
            {
                "symbol": "ell",
                "tensor_type": "(1,0) plus conjugate",
                "ghost_number": 1,
                "Grassmann_parity": "EVEN",
            }
        ],
        "antifields": [
            {
                "symbol": "h_star",
                "tensor_type": "(2,1)",
                "ghost_number": -1,
                "Grassmann_parity": "EVEN",
            },
            {
                "symbol": "ell_star",
                "tensor_type": "(1,0)",
                "ghost_number": -2,
                "Grassmann_parity": "ODD",
            },
        ],
        "reducibility": {
            "stage": 0,
            "rows": [],
            "completeness": "CERTIFIED_COMPLETE",
        },
        "minimal_q": {
            "rows": ["Qh=Rell", "Qell=0"],
            "nilpotency_certificate": HASH,
        },
        "noether_identity": {
            "kinetic_operator": "K",
            "gauge_operator": "R",
            "identity": "K_R_EQUALS_ZERO_OFF_SHELL_ON_DECLARED_BACKGROUND",
            "certificate": HASH,
        },
        "nonminimal_pairs": [
            {
                "antighost": "bar_ell",
                "multiplier": "b",
                "q_row": "Q bar_ell=b; Qb=0",
            }
        ],
        "gauge_fermion": "Psi=<bar_ell,Fh>",
        "gauge_fixed_operator": "K_Psi",
        "ellipticity_certificate": {
            "status": "GENERIC_RIEMANNIAN_ELLIPTIC",
            "generic_covector_symbol_hash": HASH,
        },
        "domain": "closed Sobolev realization with explicit kernel projector",
        "reality_structure": "COMPLEX_WITH_CONJUGATE",
        "chiral_components": ["UNDOTTED", "DOTTED_CONJUGATE"],
        "zero_mode_policy": "prime every declared kernel and retain its ledger",
        "determinant_ledger": [
            {
                "field_id": "h",
                "operator": "K_Psi",
                "statistics": "FERMIONIC",
                "power": {"numerator": -1, "denominator": 2},
                "zero_mode_policy": "prime",
                "contour": "real Berezin",
            },
            {
                "field_id": "hbar",
                "operator": "K_Psi_bar",
                "statistics": "FERMIONIC",
                "power": {"numerator": -1, "denominator": 2},
                "zero_mode_policy": "prime",
                "contour": "conjugate Berezin",
            },
        ],
        "contour_policy": "all bosonic and fermionic contours declared",
        "coefficient_routes": [
            {
                "route_id": "route_a",
                "independent_role": "producer",
                "raw_column": [ZERO, ZERO, ZERO, ZERO],
                "proof_hash": HASH,
            },
            {
                "route_id": "route_b",
                "independent_role": "verifier",
                "raw_column": [ZERO, ZERO, ZERO, ZERO],
                "proof_hash": HASH,
            },
        ],
        "kinetic_sign_audit": {
            "classification": "KREIN_INDEFINITE",
            "proof": "fixture sign proof",
        },
        "lattice_action": "APPEND_NEW_COLUMN",
        "claim_boundary": "schema fixture only",
    }


class ConformalGaugeFieldCarrierObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(self.value, certificate())

    def test_independent_replay(self) -> None:
        self.assertEqual(
            verify()["result_id"],
            "FIRST_NEW_CONFORMAL_GAUGE_FIELD_CARRIER_OBSTRUCTION",
        )

    def test_all_exact_checks(self) -> None:
        value = build()
        self.assertTrue(all(value["exact_checks"].values()))
        self.assertFalse(value["anomaly_lattice"]["new_column_appended"])

    def test_missing_ghost_mutation_rejected(self) -> None:
        mutant = complete_receiver_fixture()
        mutant["ghosts"] = []
        with self.assertRaisesRegex(ValueError, "receiver schema"):
            validate_receiver(mutant)

    def test_wrong_chirality_mutation_rejected(self) -> None:
        mutant = complete_receiver_fixture()
        mutant["chiral_components"] = ["UNDOTTED"]
        with self.assertRaisesRegex(ValueError, "wrong chirality"):
            validate_receiver(mutant)

    def test_omitted_nonminimal_mutation_rejected(self) -> None:
        mutant = complete_receiver_fixture()
        mutant["nonminimal_pairs"] = []
        with self.assertRaisesRegex(ValueError, "receiver schema"):
            validate_receiver(mutant)

    def test_partial_determinant_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["determinant_ledger"]["status"] = "COMPLETE"
        with self.assertRaisesRegex(ValueError, "schema|determinant"):
            verify_payload(mutant)

    def test_spin3_maximal_depth_substitution_rejected(self) -> None:
        mutant = deepcopy(self.value)
        row = next(
            item
            for item in mutant["candidate_audits"]
            if item["candidate_id"] == "bosonic_conformal_spin_3_minimal_depth"
        )
        row["first_missing_carrier"] = "use the maximal-depth scalar-ghost model"
        with self.assertRaisesRegex(ValueError, "spin-3"):
            validate(mutant)

    def test_column_promotion_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["anomaly_lattice"]["new_column_appended"] = True
        with self.assertRaisesRegex(ValueError, "schema|coefficient"):
            verify_payload(mutant)


if __name__ == "__main__":
    unittest.main()
