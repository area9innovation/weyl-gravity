from __future__ import annotations

from copy import deepcopy
import json
import unittest

from transfer.strict_anomaly_zero_charge_restriction_nondefinition import (
    build,
    validate,
)
from transfer.strict_anomaly_zero_charge_restriction_nondefinition_certificate import (
    OUTPUT,
    certificate,
)
from transfer.verify_strict_anomaly_zero_charge_restriction_nondefinition import (
    validate_receiver,
    verify,
    verify_payload,
)


HASH = "0" * 64


def receiver_fixture(sector: str) -> dict:
    generator = (
        "raw_D" if sector == "cylinder_Taub_zero" else "K_Berger=D-omega R"
    )
    map_row = {
        "domain": "source",
        "codomain": "target",
        "matrix_or_rule": "exact rule",
        "proof_hash": HASH,
    }
    return {
        "schema": "quantum-weyl-strict-anomaly-sector-restriction-map-v1",
        "sector_id": sector,
        "background_jet_map": map_row,
        "charge_sector_inclusion": map_row,
        "residual_projection": map_row,
        "chain_identities": ["a", "b", "c", "d", "e"],
        "domain": "declared completed fluctuation jets",
        "boundary_policy": "declared support and boundary current",
        "class_images": [
            {
                "class_id": class_id,
                "status": "NONTRIVIAL",
                "representative": "r",
                "witness": "w",
            }
            for class_id in (
                "ANOM_OMEGA_C2",
                "ANOM_OMEGA_E4",
                "ANOM_OMEGA_C_DUAL_C",
            )
        ],
        "Cartan_generator": generator,
        "Cartan_defect": {
            "status": "NONTRIVIAL",
            "representative": "x",
            "witness": "w",
        },
    }


class StrictAnomalyRestrictionNondefinitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(self.value, certificate())

    def test_independent_replay(self) -> None:
        self.assertEqual(
            verify()["result_id"],
            "STRICT_ANOMALY_ZERO_CHARGE_RESTRICTION_NONDEFINITION",
        )

    def test_six_pullbacks_remain_undefined(self) -> None:
        value = build()
        self.assertEqual(len(value["pullback_dispositions"]), 6)
        self.assertTrue(
            all(
                row["status"] == "UNDEFINED_MISSING_CHAIN_MAP"
                for row in value["pullback_dispositions"]
            )
        )

    def test_background_evaluation_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["pullback_dispositions"][0]["status"] = "ZERO"
        mutant["pullback_dispositions"][0][
            "background_evaluation_used_as_pullback"
        ] = True
        with self.assertRaisesRegex(ValueError, "schema|pullback"):
            verify_payload(mutant)

    def test_raw_D_for_Berger_receiver_rejected(self) -> None:
        mutant = receiver_fixture("Berger_fixed_coupling")
        mutant["Cartan_generator"] = "raw_D"
        with self.assertRaisesRegex(ValueError, "raw D"):
            validate_receiver(mutant)

    def test_K_Berger_for_cylinder_receiver_rejected(self) -> None:
        mutant = receiver_fixture("cylinder_Taub_zero")
        mutant["Cartan_generator"] = "K_Berger=D-omega R"
        with self.assertRaisesRegex(ValueError, "K_Berger"):
            validate_receiver(mutant)

    def test_missing_boundary_policy_rejected(self) -> None:
        mutant = receiver_fixture("cylinder_Taub_zero")
        mutant["boundary_policy"] = ""
        with self.assertRaisesRegex(ValueError, "receiver schema"):
            validate_receiver(mutant)

    def test_anomaly_freedom_promotion_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["CYLINDER_RESTRICTED_ANOMALY_FREE"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
