"""Method-distinct audit of the mixed-charge derived correspondence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/EINSTEIN_WEYL_MIXED_CHARGE_DERIVED_CORRESPONDENCE_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-mixed-charge-derived-correspondence-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_payload(payload: dict, files: bool = True) -> None:
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).validate(payload)
    if files:
        assert payload["schema_sha256"] == sha(SCHEMA)
        assert payload["provenance"]["generator_sha256"] == sha(ROOT / payload["provenance"]["generator_path"])
        for item in payload["provenance"]["inputs"].values():
            path = ROOT / item["path"]
            assert sha(path) == item["sha256"]
            assert json.loads(path.read_text())["result_id"] == item["result_id"]

    # Rebuild the 10 by 7 tangent differential without importing the producer.
    d = sp.zeros(10, 7)
    for a in range(5):
        d[a, a + 2] = -1
        d[a + 5, a + 2] = 1
    dims = payload["derived_correspondence"]["balanced_fixture_tangent_complex"]
    assert d.rank() == dims["rank_d"] == 5
    assert d.cols - d.rank() == dims["H0"] == 2
    assert d.rows - d.rank() == dims["H1"] == 5
    assert payload["derived_correspondence"]["balanced_fixture_differential"] == [
        [str(x) for x in row] for row in d.tolist()
    ]

    # Independently reconstruct the charge transfer and its forbidden projections.
    tau_e = sp.Rational(48, 5) * (-6 + 5 * sp.sqrt(3))
    amp2 = sp.Rational(27, 52) * (-6 + 5 * sp.sqrt(3))
    tau_x = -sp.Rational(832, 45) * amp2
    assert sp.simplify(tau_e + tau_x) == 0
    assert tau_e != 0 and tau_x != 0
    fixture = payload["balanced_fixture"]
    parse = lambda x: sp.sympify(x, locals={"sqrt": sp.sqrt})
    assert sp.simplify(parse(fixture["Einstein_mu_H"]) - tau_e) == 0
    assert sp.simplify(parse(fixture["extra_mu_H"]) - tau_x) == 0
    assert sp.simplify(parse(fixture["transfer_c"][0]) - tau_e) == 0

    # Independently reconstruct the lift-invariant Schur complement.
    ge = sp.Matrix([[6, 18], [18, 2]])
    cross = sp.Matrix([[-84, 0], [112, 0]])
    raw = sp.diag(-76, sp.Rational(208, 3))
    schur = sp.simplify(raw - cross.T * ge.inv() * cross)
    assert schur == sp.diag(1296, sp.Rational(208, 3))
    schur_entry = next(x for x in payload["map_and_form_ledger"] if x["object"] == "p_X^*S_X")
    assert schur_entry["fixture"] == [[str(x) for x in row] for row in schur.tolist()]

    assert payload["classification"]["separate_neutral_projection_exists"] is False
    assert payload["classification"]["Schur_form_is_derived_quotient_pairing"] is False
    assert payload["classification"]["derived_differential_nilpotent"] is True


def main() -> None:
    verify_payload(json.loads(CERT.read_text()))


if __name__ == "__main__":
    main()
