from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from d_quotient_classical.compensator import (
    closed_s3_relative_phase_clock_atlas as producer,
)
from d_quotient_classical.compensator import (
    verify_closed_s3_relative_phase_clock_atlas as verifier,
)


class ClosedS3RelativePhaseClockAtlasTest(unittest.TestCase):
    def test_exact_producer_is_deterministic(self) -> None:
        self.assertEqual(producer.build_all(), producer.build_all())

    def test_independent_exact_replay(self) -> None:
        verifier.verify()

    def test_float_input_rejected(self) -> None:
        raw = producer.build_raw_export()
        raw["cases"][0]["M"][0][0] = 2.0
        with self.assertRaisesRegex(AssertionError, "floating-point"):
            producer._canonicalize_case(raw["cases"][0])

    def test_smith_witness_mutation_rejected(self) -> None:
        _, result, _ = producer.build_all()
        result["exact_cases"][1]["smith"]["UQV_equals_D"] = False
        with self.assertRaisesRegex(AssertionError, "quotient witness"):
            producer.validate_result(result)

    def test_lattice_witness_mutation_rejected(self) -> None:
        _, result, _ = producer.build_all()
        result["exact_cases"][1]["lattices"]["checks"]["NT_B_identity"] = False
        with self.assertRaisesRegex(AssertionError, "quotient witness"):
            producer.validate_result(result)

    def test_positive_sign_promotion_rejected(self) -> None:
        _, result, _ = producer.build_all()
        result["exact_cases"][1]["kinetic_restriction"]["sign_status"] = "NEGATIVE"
        with self.assertRaisesRegex(AssertionError, "positive quotient"):
            producer.validate_result(result)

    def test_declared_indefinite_census_mutation_rejected(self) -> None:
        _, result, _ = producer.build_all()
        case = next(
            item
            for item in result["exact_cases"]
            if item["case_id"] == "n2_indefinite_c"
        )
        case["kinetic_restriction"]["sign_status"] = "POSITIVE"
        with self.assertRaisesRegex(AssertionError, "sign census"):
            producer.validate_result(result)

    def test_conflux_promotion_rejected(self) -> None:
        _, result, _ = producer.build_all()
        result["conflux_export"]["certified_conflux_map"] = True
        with self.assertRaisesRegex(AssertionError, "Conflux boundary"):
            producer.validate_result(result)

    def test_physical_mode_promotion_rejected(self) -> None:
        _, result, _ = producer.build_all()
        result["claim_flags"]["PHYSICAL_RESIDUAL_MODE"] = True
        with self.assertRaisesRegex(AssertionError, "claim boundary"):
            producer.validate_result(result)

    def test_request_refusal_fails_closed(self) -> None:
        request = {
            "id": (
                "sf:forge-request/"
                "closed-s3-relative-phase-clock-atlas-conflux-consumer"
            ),
            "body": {"state": "DECLINED"},
        }
        raw = producer.build_raw_export()
        raw_sha = hashlib.sha256(producer._dump(raw).encode()).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            path.write_text(json.dumps(request))
            with mock.patch.object(producer, "REQUEST", path):
                with self.assertRaisesRegex(AssertionError, "request drifted"):
                    producer.build_result(raw, raw_sha)

    def test_stratum_census_mutation_rejected(self) -> None:
        _, result, _ = producer.build_all()
        result["strata"].pop()
        with self.assertRaisesRegex(AssertionError, "census incomplete"):
            producer.validate_result(result)


if __name__ == "__main__":
    unittest.main()
