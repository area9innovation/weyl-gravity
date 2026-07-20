from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import unittest

from d_quotient_classical.compensator.tau_adic_vacuum_cylinder_causal_bv_trace_obstruction import (
    build,
    validate,
)
from d_quotient_classical.compensator.verify_tau_adic_vacuum_cylinder_causal_bv_trace_obstruction import (
    verify,
)


def _rehash_matrix(record: dict[str, object]) -> None:
    canonical = {
        "row_count": record["row_count"],
        "column_count": record["column_count"],
        "entries": record["entries"],
    }
    record["sha256"] = hashlib.sha256(
        json.dumps(
            canonical, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()


class TauAdicVacuumCylinderCausalBVTraceObstructionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_producer_and_independent_verifier_agree(self) -> None:
        validate(self.value)
        verify(self.value)

    def test_convention_bridge_is_not_name_matching(self) -> None:
        bridge = self.value["normalization_bridge"]
        self.assertEqual(bridge["derived_identification"], "sigma=2 omega")
        self.assertEqual(
            bridge["derived_compensator_arrow"], "sigma -> tau/2"
        )
        self.assertEqual(
            bridge["dressed_trace"], "u=phi_trace-2 tau"
        )

    def test_trace_kinetic_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        matrix = mutant["scalar_trace_obstruction"]["Q_dressed"]
        matrix["entries"].append(
            {"row": 3, "column": 1, "coefficient": 1}
        )
        _rehash_matrix(matrix)
        with self.assertRaises(AssertionError):
            verify(mutant)

    def test_wrong_compensator_normalization_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        q = mutant["scalar_trace_obstruction"]["Q_original"]
        entry = next(
            item
            for item in q["entries"]
            if item["row"] == 2 and item["column"] == 0
        )
        entry["coefficient"] = 1
        _rehash_matrix(q)
        with self.assertRaises(AssertionError):
            verify(mutant)

    def test_finite_zero_mode_promotion_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["scalar_trace_obstruction"]["principal_symbol"][
            "defect_is_finite_zero_mode"
        ] = True
        with self.assertRaises(AssertionError):
            verify(mutant)

    def test_global_ckv_completeness_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        support = mutant["scalar_trace_obstruction"][
            "compact_support_witness"
        ]
        support["global_CKV_nonmembership"] = support[
            "global_CKV_nonmembership"
        ].replace("exactly fifteen CKV modes", "fourteen CKV modes")
        with self.assertRaises(AssertionError):
            verify(mutant)

    def test_hadamard_promotion_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["FULL_TAU_ADIC_BRST_HADAMARD_KERNEL"] = True
        with self.assertRaises(AssertionError):
            verify(mutant)


if __name__ == "__main__":
    unittest.main()
