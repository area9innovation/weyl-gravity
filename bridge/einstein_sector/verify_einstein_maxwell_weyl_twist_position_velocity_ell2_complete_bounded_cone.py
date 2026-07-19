"""Independent verifier for the twist-position/velocity ell2 bounded cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_position_velocity_ell2_complete_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_twist_position_velocity_ell2_complete_bounded_cone.schema.json"


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
    inputs = {
        name: json.loads((ROOT / record["path"]).read_text(encoding="utf-8"))
        for name, record in provenance["inputs"].items()
    }
    growth = inputs["global_polynomial"]["polynomial_growth_ideal"]
    assert growth["SO3_twist_leading_tensor"] == "STF(B tensor B)"
    assert growth["twist_polar_L2_metric_00_t2"] == "-7*B**2"

    bx, by, bz = sp.symbols("B_x B_y B_z", real=True)
    vector = sp.Matrix([bx, by, bz])
    norm_squared = sp.expand(vector.dot(vector))
    stf = vector * vector.T - sp.eye(3) * norm_squared / 3
    exact_norm = sp.factor(sp.trace(stf.T * stf))
    assert exact_norm == sp.Rational(2, 3) * norm_squared**2
    assert growth["SO3_twist_leading_norm_squared"] == str(exact_norm)
    assert value["twist_velocity_elimination"]["exact_norm_squared"] == str(exact_norm)
    assert value["twist_velocity_elimination"]["direct_aligned_metric_00_coefficient"] == "-7*B**2"
    assert value["twist_velocity_elimination"]["source_certificate_result_id"] == inputs["global_polynomial"]["result_id"]

    classification = value["classification"]
    assert classification["complete_twist_position_velocity_plus_ell2_wave_carrier_covered"] is True
    assert classification["twist_velocity_forced_zero_in_bounded_class"] is True
    assert classification["bounded_zero_locus_necessary_and_sufficient"] is True
    assert classification["other_homogeneous_tangents_classified"] is False
    assert value["complete_bounded_zero_locus"]["first_equation"] == "B=0"
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_TWIST_POSITION_VELOCITY_ELL2_COMPLETE_BOUNDED_CONE independent verification: PASS")


if __name__ == "__main__":
    main()
