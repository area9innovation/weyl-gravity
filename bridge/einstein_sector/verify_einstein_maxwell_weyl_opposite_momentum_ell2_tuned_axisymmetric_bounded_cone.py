"""Independent verifier for the tuned axisymmetric bounded cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_tuned_axisymmetric_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_opposite_momentum_ell2_tuned_axisymmetric_bounded_cone.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    for entry in payload["provenance"]["inputs"].values():
        assert _sha256(ROOT / entry["path"]) == entry["sha256"]

    ap, am, pp, pm = sp.symbols("a_plus a_minus p_plus p_minus")
    equations = [ap * am - 3 * pp * pm, ap * pm - am * pp]
    for sign in (-1, 1):
        substitution = {ap: sign * sp.sqrt(3) * pp, am: sign * sp.sqrt(3) * pm}
        assert all(sp.expand(equation.subs(substitution)) == 0 for equation in equations)
    assert all(sp.expand(equation.subs({ap: 0, pp: 0})) == 0 for equation in equations)
    assert all(sp.expand(equation.subs({am: 0, pm: 0})) == 0 for equation in equations)

    root = sp.sqrt(3)
    r = sp.sqrt(sp.Rational(29, 6) / (sp.Rational(29, 6) + 4 * root))
    assert 0 < float(r.evalf()) < 1
    lower = (1 - r) / (1 + r)
    upper = (1 + r) / (1 - r)
    assert sp.simplify(lower * upper - 1) == 0
    stored = payload["nonzero_bounded_components"]["complete_imbalance_interval"]
    assert sp.simplify(sp.sympify(stored["lower"]) - lower) == 0
    assert sp.simplify(sp.sympify(stored["upper"]) - upper) == 0

    n_plus, n_minus = sp.symbols("N_plus N_minus", nonnegative=True)
    b_plus = (r**2 * (n_plus + n_minus) + r * (n_plus - n_minus)) / 2
    b_minus = (r**2 * (n_plus + n_minus) - r * (n_plus - n_minus)) / 2
    assert sp.expand(b_plus + b_minus - r**2 * (n_plus + n_minus)) == 0
    assert sp.expand(b_plus - b_minus - r * (n_plus - n_minus)) == 0
    # A one-sided nonzero occupation would require 1<=r for B on the
    # opposite signed momentum to stay nonnegative.
    assert sp.simplify((r**2 - r) * n_minus / 2).is_nonpositive

    flags = payload["classification"]
    assert flags["complete_tuned_axisymmetric_common_moment_and_resonance_cone_classified"] is True
    assert flags["bounded_necessity_and_sufficiency_certified"] is True
    assert flags["p_primary_inputs_included"] is False
    assert flags["causal_or_quantum_claim"] is False
    assert payload["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] == "CERTIFIED"
    assert payload["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_OPPOSITE_MOMENTUM_ELL2_TUNED_AXISYMMETRIC_BOUNDED_CONE independent verification: PASS")


if __name__ == "__main__":
    main()
