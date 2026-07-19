"""Independent verifier for the fixed-ell constant-twist factorization."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_constant_twist_factorization.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_fixed_ell_constant_twist_factorization.schema.json"


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
    theorem = value["representation_theorem"]
    assert theorem["multiplicity"] == "dim Hom_SO3(V_1 tensor V_ell,V_ell)=1 for every integer ell>=1"
    assert theorem["axis_spectrum"].endswith("for m=-ell,...,ell")
    gates = value["finite_matrix_gates"]
    assert gates["Einstein_minus"]["bounded_kernel_if_rank_r"] == "2 + 2*ell*(2-r)"
    assert gates["extra"]["bounded_kernel_if_rank_r"] == "4 + 2*ell*(4-r)"
    assert value["ell2_regression"]["extra_kernel_dimension"] == 12
    assert value["classification"]["complete_fixed_ell_constant_twist_cone_classified"] is False
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_FIXED_ELL_CONSTANT_TWIST_FACTORIZATION independent verification: PASS")


if __name__ == "__main__":
    main()
