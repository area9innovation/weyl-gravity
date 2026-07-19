"""Independent verifier for the complete finite-harmonic tangent cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.schema.json"


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()

    t = sp.symbols("t")
    primitives = payload["complete_output_cokernel_theorem"]["L0_K0"]["polynomial_right_inverse"]
    for row in primitives["D_fourth_derivative_primitives"]:
        assert sp.diff(sp.sympify(row["primitive"]), t, 4) == sp.sympify(row["source"])
    for row in primitives["A_x_second_derivative_primitives"]:
        assert sp.diff(sp.sympify(row["primitive"]), t, 2) == sp.sympify(row["source"])

    cokernel = payload["complete_output_cokernel_theorem"]
    assert cokernel["decomposition"] == "coker L_smooth = span{zeta_H,zeta_Px,zeta_J1,zeta_J2,zeta_J3}"
    assert len(payload["Taub_identification"]["generators"]) == 5
    smooth = payload["smooth_global_theorem"]
    assert smooth["exceptional_and_global_inputs_included"] is True
    assert smooth["multiple_momenta_m_phases_and_branches_included"] is True
    bounded = payload["bounded_obstruction_ledger"]
    assert "P_(j,r)" in bounded["formula"] and "R_(j,a)" in bounded["formula"]
    assert bounded["coefficientwise_common_zero_locus"] == "OPEN"
    assert payload["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"


if __name__ == "__main__":
    main()
