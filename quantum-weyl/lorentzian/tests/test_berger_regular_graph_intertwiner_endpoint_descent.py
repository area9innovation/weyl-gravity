from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_regular_graph_intertwiner_endpoint_descent import (
    endpoint_source_pullback_replay,
    regular_graph_principal_replay,
    validate,
)
from lorentzian.berger_regular_graph_intertwiner_endpoint_descent_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_regular_graph_intertwiner_endpoint_descent import (
    verify,
)


class BergerRegularGraphEndpointDescentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (
                HERE
                / "schema/"
                "berger-regular-graph-intertwiner-endpoint-descent-v1.schema.json"
            ).read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_complete_regular_graph_class_is_obstructed(self) -> None:
        result = regular_graph_principal_replay()
        self.assertTrue(result["all_pass"])
        self.assertFalse(result["nondegenerate_graph_exists"])

    def test_regularity_gain_is_load_bearing(self) -> None:
        result = regular_graph_principal_replay(
            enforce_graph_sobolev_regularity=False
        )
        self.assertFalse(result["all_pass"])

    def test_generic_v2_rank_is_load_bearing(self) -> None:
        result = regular_graph_principal_replay(
            v2_generically_invertible=False
        )
        self.assertFalse(result["all_pass"])

    def test_typed_endpoint_source_pullback(self) -> None:
        result = endpoint_source_pullback_replay()
        self.assertTrue(result["all_pass"])
        self.assertEqual(
            result["symbolic_pulled_matrix"], [["0", "e12"], ["e12", "0"]]
        )

    def test_symmetric_source_inclusion_mutation_fails(self) -> None:
        result = endpoint_source_pullback_replay(
            use_adjoint_source_inclusion=False
        )
        self.assertFalse(result["all_pass"])

    def test_BRST_overpromotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_26_ROW_BRST_HADAMARD"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
