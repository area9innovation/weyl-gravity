from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_hadamard_regular_morphism_boundary import (
    finite_microlocal_replay,
    validate,
)
from lorentzian.berger_hadamard_regular_morphism_boundary_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_hadamard_regular_morphism_boundary import verify


class BergerHadamardRegularMorphismBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (HERE / "schema/berger-hadamard-regular-morphism-boundary-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_finite_graph_maps_are_wavefront_safe(self) -> None:
        replay = finite_microlocal_replay()
        self.assertTrue(all(replay["checks"].values()))
        self.assertEqual(
            max(row["maximum_order"] for row in replay["graph_maps"].values()),
            2,
        )

    def test_two_old_obligations_are_narrowly_closed(self) -> None:
        disposition = self.certificate["old_obligation_disposition"]
        self.assertEqual(
            disposition["A10_graph_pullback_wavefront_safe"],
            "CERTIFIED_FOR_EVERY_DEFINED_INPUT_DISTRIBUTION",
        )
        self.assertEqual(
            disposition["ghost_biwave_factor_transport_included"],
            "CERTIFIED_LOCAL_DIRECT_SUM_FACTOR_ONLY",
        )

    def test_current_volterra_map_is_not_a_regular_morphism(self) -> None:
        scope = self.certificate["primary_theorem_scope"]
        self.assertFalse(
            scope["fewster_2503_12537_theorem_5_16"][
                "applies_to_current_stationary_volterra_map"
            ]
        )
        self.assertFalse(
            scope["dappiaggi_drago_1506_09122"]["applies_directly"]
        )

    def test_minimal_cutoff_request_is_fail_closed(self) -> None:
        request = self.certificate["classical_import_request"]
        self.assertEqual(
            request["result_id"], "BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY"
        )
        self.assertEqual(request["status"], "NOT_SUPPLIED")

    def test_hadamard_promotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
