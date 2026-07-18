"""Independent verifier for the opposite-momentum resonance divisor."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor.schema.json"


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    assert payload["provenance"]["generator_sha256"] == hashlib.sha256((ROOT / payload["provenance"]["generator_path"]).read_bytes()).hexdigest()
    for record in payload["provenance"]["inputs"].values():
        assert hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"]

    u, A, B, C = sp.symbols("u A B C")
    D = C - A - B
    for h in (0, 4):
        polynomial = sp.factor((D + (h - 2) * u) ** 2 - 4 * (u + A) * (u + B))
        candidate = (
            (D**2 - 4 * A * B) / (4 * C)
            if h == 0
            else (4 * A * B - D**2) / (4 * (C - 2 * A - 2 * B))
        )
        assert sp.factor(polynomial.subs(u, candidate)) == 0

    ell = sp.symbols("ell", integer=True, positive=True)
    lam = ell * (ell + 1)
    k2 = sp.sqrt(2 * lam) - ell / 2 - sp.Rational(1, 6)
    input_offset = lam - sp.sqrt(2 * lam)
    output_offset = 2 * ell * (2 * ell + 1) - sp.Rational(2, 3)
    assert sp.factor(4 * (k2 + input_offset) - output_offset) == 0
    positivity = sp.factor(2 * lam - (ell / 2 + sp.Rational(1, 6)) ** 2)
    assert sp.expand(positivity - (63 * ell**2 + 66 * ell - 1) / 36) == 0
    assert all(coefficient > 0 for coefficient in sp.Poly(sp.expand(positivity.subs(ell, ell + 2)), ell).all_coeffs())

    classification = payload["classification"]
    assert classification["phase_sensitive_resonance_divisor_formula_exact"] is True
    assert classification["resonance_divisor_nonempty_for_every_ell"] is True
    assert classification["bounded_or_finite_quasiperiodic_extension_follows_from_moment_maps_alone"] is False
    assert classification["generic_nonzero_resonance_removable_in_smooth_global_secular_class"] is True
    assert classification["static_L0_K2k_exceptional_block_classified"] is False


if __name__ == "__main__":
    main()
