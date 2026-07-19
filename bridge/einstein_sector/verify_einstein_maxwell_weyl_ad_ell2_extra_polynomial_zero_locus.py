"""Independent verifier for the repaired a/d polynomial zero locus."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ad_ell2_extra_polynomial_zero_locus.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ad_ell2_extra_polynomial_zero_locus.schema.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = value["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        path = ROOT / record["path"]
        assert record["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()

    a, d, xa1, xa2, xp1, xp2 = sp.symbols("a d z_ax1 z_ax2 z_pol1 z_pol2")
    expected = [a * xa1, a * xa2, a * xp1, a * xp2, d * xp2]
    recorded = [sp.sympify(item, locals={name: symbol for name, symbol in zip(("a", "d", "z_ax1", "z_ax2", "z_pol1", "z_pol2"), (a, d, xa1, xa2, xp1, xp2), strict=True)}) for item in value["polynomial_zero_locus"]["ideal_generators"]]
    assert all(sp.factor(left - right) == 0 for left, right in zip(recorded, expected, strict=True))
    groebner = sp.groebner(expected, xa1, xa2, xp1, xp2, a, d, order="lex")
    assert value["polynomial_zero_locus"]["Groebner_basis"] == [str(polynomial.as_expr()) for polynomial in groebner.polys]
    classification = value["classification"]
    assert classification["complete_a_d_ell2_extra_cross_polynomial_ideal_classified"] is True
    assert classification["old_nonzero_extra_common_zero_cone_survives_repair"] is True
    assert classification["constant_resonance_zero_locus_solved_on_repaired_branches"] is False
    assert classification["complete_bounded_cone_solved"] is False


if __name__ == "__main__":
    main()
