from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import unittest

from spectral.euclidean.full_bv_ledger_composer import (
    ROOT,
    compose_from_path,
    validate_composed_repository_multiplicity_export,
)
from spectral.euclidean.verify_repository_full_bv_multiplicity_ledger import (
    LEDGER,
    TT_DICTIONARY,
    verify,
)


class RepositoryFullBVMultiplicityLedgerTests(unittest.TestCase):
    def test_committed_ledger_matches_composer_and_independent_replay(self) -> None:
        self.assertEqual(json.loads(LEDGER.read_text()), compose_from_path(TT_DICTIONARY))
        self.assertEqual(
            verify()["status"],
            "PHYSICAL_FULL_BV_LEDGER_INDEPENDENTLY_ACCEPTED",
        )

    def test_physical_factor_mutation_fails_closed(self) -> None:
        ledger = json.loads(LEDGER.read_text())
        tt = json.loads(TT_DICTIONARY.read_text())
        artifact = {
            "format": "JSON_DATA",
            "path": str(TT_DICTIONARY.relative_to(ROOT)),
            "sha256": hashlib.sha256(TT_DICTIONARY.read_bytes()).hexdigest(),
        }
        mutant = deepcopy(ledger)
        mutant["repository_factors"][0]["operator"] = "Delta_2_perp(5)"
        with self.assertRaises(ValueError):
            validate_composed_repository_multiplicity_export(
                mutant,
                tt_payload=tt,
                tt_dictionary_artifact=artifact,
                expected_classical_commit=tt["classical_commit"],
            )


if __name__ == "__main__":
    unittest.main()
