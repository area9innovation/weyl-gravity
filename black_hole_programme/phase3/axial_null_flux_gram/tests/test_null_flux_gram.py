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


if __name__ == "__main__":
    unittest.main()
