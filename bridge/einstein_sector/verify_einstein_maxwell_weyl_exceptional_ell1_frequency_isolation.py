"""Independent verifier for exceptional ell=1 same-frequency isolation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_frequency_isolation.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ell1_frequency_isolation.schema.json"


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()

    lam = sp.symbols("lambda", real=True)
    target = sp.Rational(4, 3)
    assert sp.Rational(16, 3) - target == 4
    assert sp.expand((6 - target) ** 2 - 12) == sp.Rational(88, 9)
    assert bool(6 - 2 * sp.sqrt(3) > target)
    assert sp.simplify(sp.diff(lam - sp.sqrt(2 * lam), lam) - (1 - 1 / sp.sqrt(2 * lam))) == 0

    classification = payload["classification"]
    assert classification["same_frequency_nonexceptional_cancellation_excluded"] is True
    assert classification["complete_pure_exceptional_ell1_k0_second_order_no_go_frozen"] is True
    assert classification["different_frequency_pair_sums_classified"] is False
    assert classification["different_momentum_pairs_classified"] is False


if __name__ == "__main__":
    main()
