from __future__ import annotations

import json
import unittest
from pathlib import Path

from black_hole_programme.phase3.axial_null_flux_gram.verify import (
    verify_document,
)


HERE = Path(__file__).resolve().parents[1]


class AxialNullFluxGramTest(unittest.TestCase):
    def test_certificate(self) -> None:
        verify_document(json.loads((HERE / "certificate.json").read_text()))

    def test_uniform_l2_constants_and_scope(self) -> None:
        document = json.loads((HERE / "certificate.json").read_text())
        self.assertEqual(
            document["trace_space_geometry"]["common_uniform_constants"],
            {
                "c": "1",
                "C": "645",
                "estimate": (
                    "||a||_L2 <= ||G_endpoint*a||_L2 <= "
                    "645||a||_L2 at either endpoint"
                ),
            },
        )
        self.assertEqual(
            document["current_representative"]["improvement_audit"][
                "unrestricted_status"
            ],
            "OPEN",
        )
        self.assertFalse(
            document["claim_flags"][
                "unrestricted_improvement_invariance_certified"
            ]
        )


if __name__ == "__main__":
    unittest.main()
