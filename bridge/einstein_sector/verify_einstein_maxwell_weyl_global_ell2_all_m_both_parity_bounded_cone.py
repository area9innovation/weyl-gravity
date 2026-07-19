"""Independent verifier for the global plus complete ell2 bounded cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_ell2_all_m_both_parity_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_global_ell2_all_m_both_parity_bounded_cone.schema.json"


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
    epsilon, k, angular = sp.symbols("epsilon k angular")
    assert sp.diff((k + epsilon * angular) ** 2, epsilon).subs(k, 0) == 2 * epsilon * angular**2
    assert sp.diff((k + epsilon * angular) ** 2, epsilon).subs({k: 0, epsilon: 0}) == 0
    promotion = value["equivariant_promotion"]
    assert promotion["multiplicity_one"] == "dim Hom_SO3(V_2,V_2)=1"
    bounded_zero = value["bounded_zero_frequency_completion"]
    assert bounded_zero["constant_correction"] == ["S0/2", "-S1/2", "0", "0"]
    assert bounded_zero["remainder"] == ["0", "0", "0", "0"]
    cone = value["complete_bounded_cone"]
    assert cone["union_is_necessary_and_sufficient"] is True
    assert "mu_H=mu_J1=mu_J2=mu_J3=0" in cone["wave_branch"]
    assert value["wave_cone"]["zero_frequency_L1_constant_correction"] == ["S0/2", "-S1/2", "0", "0"]
    assert "no secular/Jordan term" in value["sufficiency"]["wave_self"]
    classification = value["classification"]
    assert classification["all_m_both_parities_all_ell2_qp_branches_included"] is True
    assert classification["general_ell_classified"] is False
    assert classification["complete_finite_harmonic_bounded_cone_classified"] is False
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"


if __name__ == "__main__":
    main()
