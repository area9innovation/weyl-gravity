"""Independent verifier for the finite-generic smooth-global theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.schema.json"


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    generator = ROOT / provenance["generator_path"]
    assert provenance["generator_sha256"] == hashlib.sha256(generator.read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()

    lam, u = sp.symbols("Lambda u", nonnegative=True)
    p = -u - lam + sp.Rational(2, 3)
    q = u**2 + 2 * lam * u + lam * (lam - 2)
    assert p.subs(lam, 6) < 0
    assert all(value > 0 for value in sp.Poly(sp.expand(q.subs(lam, lam + 6)), lam, u).coeffs())

    decomposition = payload["complete_adjoint_cokernel_decomposition"]
    assert "zeta_H" in decomposition["zero_block"]["decomposition"]
    assert decomposition["nonzero_Fourier_blocks"]["physical_cokernel_in_smooth_secular_class"] == "zero"
    assert "stab^*" in decomposition["global_formula"]

    smooth = payload["smooth_global_theorem"]
    assert smooth["multiple_absolute_momentum_fibres"].startswith("included")
    assert "mu_H=mu_Px=mu_J1=mu_J2=mu_J3=0" in smooth["tangent_cone"]
    bounded = payload["bounded_resonance_functionals"]
    assert bounded["coefficientwise_zero_locus"] == "OPEN"
    assert payload["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"


if __name__ == "__main__":
    main()
