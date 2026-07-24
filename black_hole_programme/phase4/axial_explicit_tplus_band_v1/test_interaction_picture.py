"""Mutation tests for the outgoing interaction-picture checkpoint."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .interaction_picture import exact_fixture, physical_point_fixture
from .verify_interaction import HERE, verify


class InteractionPictureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads(
            (HERE / "interaction_certificate.json").read_text()
        )

    def mutate_fails(self, mutate) -> None:
        data = json.loads(json.dumps(self.data))
        mutate(data)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "certificate.json"
            path.write_text(json.dumps(data))
            with self.assertRaises(AssertionError):
                verify(path)

    def test_exact_fixture(self) -> None:
        self.assertTrue(exact_fixture()["all_zero"])

    def test_physical_point_fixture(self) -> None:
        result = physical_point_fixture()
        self.assertEqual(result["status"], "POINT_FIXTURE_PASS")

    def test_certificate(self) -> None:
        verify(HERE / "interaction_certificate.json")

    def test_dotk_mutation(self) -> None:
        self.mutate_fails(
            lambda data: data["exact_interaction_picture"]["derived"]["dotK"][
                0
            ].__setitem__(0, "999")
        )

    def test_radial_endpoint_mutation(self) -> None:
        self.mutate_fails(
            lambda data: data["validated_micro_successor"].__setitem__(
                "radial_end", "4"
            )
        )

    def test_tplus_overclaim_mutation(self) -> None:
        self.mutate_fails(
            lambda data: data["claim_flags"].__setitem__(
                "explicit_Tplus_certified", True
            )
        )


if __name__ == "__main__":
    unittest.main()

