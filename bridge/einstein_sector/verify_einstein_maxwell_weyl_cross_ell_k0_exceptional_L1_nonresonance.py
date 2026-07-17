"""Independent verifier for adjacent-input exceptional L=1 nonresonance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_exceptional_L1_nonresonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_cross_ell_k0_exceptional_L1_nonresonance.schema.json"


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    generator = ROOT / payload["provenance"]["generator_path"]
    assert payload["provenance"]["generator_sha256"] == hashlib.sha256(generator.read_bytes()).hexdigest()
    generic = ROOT / payload["provenance"]["generic_output_theorem"]["path"]
    assert payload["provenance"]["generic_output_theorem"]["sha256"] == hashlib.sha256(generic.read_bytes()).hexdigest()

    ell = sp.symbols("ell", integer=True, positive=True)
    lam = ell * (ell + 1)
    next_lam = (ell + 1) * (ell + 2)
    target = sp.Rational(4, 3)
    first_extra = lam - sp.Rational(2, 3)
    next_extra = next_lam - sp.Rational(2, 3)
    extra_defect = sp.factor((target - first_extra - next_extra) ** 2 - 4 * first_extra * next_extra)
    assert sp.expand(extra_defect + sp.Rational(4, 3) * (ell - 1) * (ell + 3)) == 0

    ratio_remainder = sp.factor(
        ell * (3 * ell + 5) ** 2 - (ell + 2) * (3 * ell + 1) ** 2
    )
    assert sp.expand(ratio_remainder - 2 * (3 * ell**2 + 6 * ell - 1)) == 0
    shifted = sp.Poly(sp.expand(ratio_remainder.subs(ell, ell + 2)), ell)
    assert all(coefficient > 0 for coefficient in shifted.all_coeffs())

    # The cross-branch signed intervals are disjoint from {0,2/sqrt(3),2};
    # rational comparison uses 1 < 2/sqrt(3) < 6/5.
    assert sp.Rational(1) < 2 / sp.sqrt(3) < sp.Rational(6, 5)
    intervals = [
        (sp.Rational(3, 2), sp.Rational(2)),
        (sp.Rational(11, 5), sp.Rational(11, 4)),
        (sp.Rational(0), sp.Rational(1, 2)),
        (sp.Rational(3, 2), sp.Rational(39, 20)),
        (sp.Rational(1, 5), sp.Rational(3, 4)),
        (sp.Rational(1, 20), sp.Rational(1, 2)),
    ]
    exceptional = (sp.Rational(0), 2 / sp.sqrt(3), sp.Rational(2))
    for lower, upper in intervals:
        assert all(not (lower < root < upper) for root in exceptional)

    classification = payload["classification"]
    assert classification["all_nine_input_branch_pairs_covered"] is True
    assert classification["complete_exceptional_L1_root_set_covered"] is True
    assert classification["no_exceptional_L1_output_resonance"] is True
    assert classification["complete_unbounded_cross_ell_nonzero_output_nonresonance"] is True
    assert classification["cross_ell_quadratic_source_solved"] is False


if __name__ == "__main__":
    main()
