"""Independent verifier for global spectator removability."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_spectator_ell2_extra_resonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_global_spectator_ell2_extra_resonance.schema.json"


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()

    eta, circumference = sp.symbols("eta c")
    radius = sp.sqrt(1 + eta * circumference)
    assert sp.diff(radius, eta).subs(eta, 0) == circumference / 2
    assert sp.diff(radius, eta, 2).subs(eta, 0) == -circumference**2 / 4
    # Pullback weights are multiplicative and their first derivatives give the
    # declared mixed correction for every number of covariant x indices.
    weight = sp.symbols("r", integer=True, nonnegative=True)
    assert sp.simplify(sp.diff(radius**weight, eta).subs(eta, 0) - weight * circumference / 2) == 0

    classification = payload["classification"]
    assert classification["circumference_times_ell2_extra_source_in_linear_image"] is True
    assert classification["Wilson_times_ell2_extra_source_identically_zero"] is True
    assert classification["remaining_homogeneous_a_b_d_Qe_cross_sources_classified"] is False


if __name__ == "__main__":
    main()
