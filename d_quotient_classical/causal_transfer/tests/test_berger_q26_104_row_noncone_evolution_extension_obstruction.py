from __future__ import annotations

from copy import deepcopy
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer import (
    berger_q26_104_row_noncone_evolution_extension_obstruction as subject,
)
from d_quotient_classical.causal_transfer import (
    verify_berger_q26_104_row_noncone_evolution_extension_obstruction
    as verifier,
)


class NonconeEvolutionExtensionObstructionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.witness = subject.exact_witness()
        cls.certificate = subject.build()
        cls.schema = subject._load(subject.SCHEMA)

    def test_normalized_boundary_cokernel(self) -> None:
        identities = self.witness["identities"]
        self.assertTrue(identities["d_source_is_pure_old_e5"])
        self.assertTrue(
            identities["cokernel_annihilates_old_boundary_projection"]
        )
        self.assertEqual(identities["cokernel_on_A104_e5"], "-51/2")

    def test_free_new_blocks_are_eliminated(self) -> None:
        obstruction = self.certificate["exact_obstruction"]
        self.assertTrue(obstruction["free_new_evolution_blocks_eliminated"])
        self.assertFalse(
            self.certificate["classification"][
                "fixed_noncone_witness_A104_chain_extension_exists"
            ]
        )

    def test_fail_closed_global_scope(self) -> None:
        mutated = deepcopy(self.certificate)
        mutated["classification"][
            "all_104_row_noncone_differentials_obstructed"
        ] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(mutated)

    def test_independent_verifier(self) -> None:
        verifier.verify()


if __name__ == "__main__":
    unittest.main()
