"""Independent verifier for the smooth-global opposite-momentum theorem."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order.schema.json"


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"]

    lam, u = sp.symbols("Lambda u", real=True, positive=True)
    p = -u - lam + sp.Rational(2, 3)
    q = u**2 + 2 * lam * u + lam * (lam - 2)
    assert p.subs({lam: 6, u: 0}) < 0
    shifted_q = sp.Poly(sp.expand(q.subs(lam, lam + 6)), lam, u)
    assert all(coefficient > 0 for coefficient in shifted_q.coeffs())

    descent = payload["complete_channel_descent"]
    assert descent["ell0_nonzero_Fourier"]["coverage"].startswith("every")
    assert len(descent["ell1_nonzero_Fourier"]["shells"]) == 2
    theorem = payload["second_order_theorem"]
    assert theorem["all_Noether_compatible_channels_in_image_or_secular_image"] is True
    assert theorem["complete_fixed_ell_absolute_k_common_zero_cone_extendible"] is True
    classification = payload["classification"]
    assert classification["opposite_momentum_relative_phases_classified_in_smooth_global_class"] is True
    assert classification["bounded_or_finite_quasiperiodic_cone_classified"] is False
    assert classification["all_orders_integrability"] is False


if __name__ == "__main__":
    main()
