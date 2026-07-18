"""Independent verifier for the exceptional positive-sum resonance census."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_resonance_census.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ell1_resonance_census.schema.json"


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()

    lam = sp.symbols("lambda", real=True)
    equation = sp.factor((lam - sp.Rational(16, 3)) ** 2 - 2 * lam)
    roots = sp.solve(equation, lam)
    assert roots == [sp.Rational(19, 3) - sp.sqrt(105) / 3, sp.sqrt(105) / 3 + sp.Rational(19, 3)]
    assert bool(roots[0] < 6 < roots[1] < 12)
    assert sp.solve(sp.Eq(lam - sp.Rational(2, 3), sp.Rational(16, 3)), lam) == [6]

    classification = payload["classification"]
    assert classification["positive_sum_resonance_census_complete"] is True
    assert classification["homogeneous_nonzero_frequency_target_empty"] is True
    assert classification["unique_zero_plus_positive_resonance_is_global_times_ell2_extra"] is True
    assert classification["global_times_ell2_extra_source_pairing_computed"] is False
    assert classification["difference_frequency_resonances_classified"] is False


if __name__ == "__main__":
    main()
