"""Independent verifier for the global finite-harmonic k0 bounded cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_finite_harmonic_k0_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_global_finite_harmonic_k0_bounded_cone.schema.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = value["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()
    lam = sp.symbols("lambda", positive=True)
    gap = sp.sqrt(2 * lam)
    axial = -3 * sp.I * sp.sqrt(lam - gap) * (3 * gap - 1)
    polar = lam**2 * (2 * lam - 1) / 6
    assert all(sp.simplify(axial.subs(lam, ell * (ell + 1))) != 0 for ell in range(2, 20))
    assert all(polar.subs(lam, ell * (ell + 1)) > 0 for ell in range(2, 20))
    cone = value["complete_bounded_cone"]
    assert cone["union_is_necessary_and_sufficient"] is False
    assert "finite generic k=0 common H,J_i zero" in cone["certified_wave_subcone"]
    assert "A=B=0" in cone["certified_wave_subcone"]
    assert cone["nonzero_A_wave_stratum"].startswith("OPEN")
    classification = value["classification"]
    assert classification["arbitrary_finite_generic_ell_global_bounded_cone_classified"] is False
    assert classification["A_arbitrary_wave_branch_withdrawn"] is True
    assert classification["A_zero_wave_subcone_certified"] is True
    assert classification["infinite_harmonic_completion_classified"] is False
    assert classification["nonzero_momentum_classified"] is False
    assert classification["exceptional_wave_inputs_classified"] is False
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"


if __name__ == "__main__":
    main()
