from __future__ import annotations

from copy import deepcopy
import json
import unittest

from cartan.quantum_cartan_d_one_loop_disposition import evaluate, validate
from cartan.quantum_cartan_d_one_loop_disposition_certificate import (
    OUTPUT,
    build,
)
from cartan.verify_quantum_cartan_d_one_loop_disposition import verify


class QuantumCartanDOneLoopDispositionTests(unittest.TestCase):
    def test_exact_disposition_passes(self) -> None:
        value = evaluate()
        self.assertTrue(all(value["exact_checks"].values()))
        self.assertEqual(
            {row["classification"] for row in value["theory_setting_dispositions"]},
            {"UNDEFINED_ANALYTICALLY"},
        )

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_strict_and_extended_are_distinct(self) -> None:
        rows = {row["row_id"]: row for row in build()["theory_setting_dispositions"]}
        self.assertEqual(
            rows["strict_vacuum_cylinder_D_compact"]["qme_status"],
            "OBSTRUCTED_NONZERO_LOCAL_SOURCE",
        )
        self.assertEqual(
            rows["tau_adic_extended_regular_bach_raw_D"]["qme_status"],
            "RESTORED_ONE_LOOP_LOCAL_EUCLIDEAN",
        )

    def test_raw_D_and_K_Berger_are_distinct(self) -> None:
        rows = {row["row_id"]: row for row in build()["theory_setting_dispositions"]}
        self.assertEqual(
            rows["positive_berger_clock_K_Berger"]["generator_id"], "K_BERGER"
        )
        self.assertEqual(
            rows["positive_berger_clock_raw_D"]["classical_generator_status"],
            "AFFINE_NONZERO_ARITY_ZERO_NO_CARTAN_CONTRACTION",
        )

    def test_request_events_are_content_addressed(self) -> None:
        rows = build()["producer_requests"]
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(len(row["event_sha256"]) == 64 for row in rows))

    def test_classification_overpromotion_is_rejected(self) -> None:
        mutant = deepcopy(build())
        mutant["theory_setting_dispositions"][0]["classification"] = "ZERO"
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_generator_identification_is_rejected(self) -> None:
        mutant = deepcopy(build())
        mutant["claim_flags"]["RAW_D_IDENTIFIED_WITH_K_BERGER"] = True
        with self.assertRaisesRegex(ValueError, "claim flags"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
