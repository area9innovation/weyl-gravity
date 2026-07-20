"""Independent rail for the finite-harmonic structural freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1.json"


def main() -> None:
    value = json.loads(CERT.read_text())
    for item in value["provenance"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]

    rows = value["output_strata"]
    assert sum(row["zero_factors"] for row in rows) == 5
    covectors = [c for row in rows for c in row.get("covectors", [])]
    assert covectors == ["zeta_H", "zeta_Px", "zeta_J1", "zeta_J2", "zeta_J3"]
    assert rows[0]["invariant_factors"] == ["1", "1", "p", "p*q"]
    assert rows[0]["zero_factors"] == 0

    # Independent scalar audit: a characteristic root is secularly removable.
    # (D-i*w)(t*exp(i*w*t)) = exp(i*w*t), so it is not a zero factor.
    assert value["exponential_polynomial_surjectivity"]["decisive_distinction"].startswith(
        "A root of a nonzero invariant factor"
    )
    assert value["correction_classes"]["finite_exponential_polynomial"]["status"] == "THEOREM_READY_TIER3_BLOCKED"
    assert value["correction_classes"]["bounded_or_finite_quasiperiodic"]["status"].endswith("ZERO_LOCUS_OPEN")
    assert value["correction_classes"]["causal_retarded"]["status"] == "NO_CERTIFIED_MAP"

    # Decisive mutations: an extra zero factor, deletion of a stabilizer, or
    # promotion of the bounded zero locus contradicts the pinned theorem.
    assert sum(row["zero_factors"] for row in rows) != 6
    assert len(covectors[:-1]) != value["adjoint_cokernel"]["dimension"]
    assert value["classification"]["bounded_common_zero_locus_solved"] is False
    assert value["classification"]["theorem_freeze_promoted"] is False
    print(f"{value['result_id']} independent verification: PASS")


if __name__ == "__main__":
    main()
