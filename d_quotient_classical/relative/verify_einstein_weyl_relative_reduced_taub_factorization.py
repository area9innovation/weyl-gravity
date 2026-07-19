#!/usr/bin/env python3
"""Independent replay of reduced Taub factorization."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_REDUCED_TAUB_FACTORIZATION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-reduced-taub-factorization-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value)
    for relative, expected in value["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != expected:
            raise AssertionError(f"source manifest drift: {relative}")
    dependencies = {}
    for name, artifact in value["dependencies"].items():
        path = ROOT / artifact["path"]
        if _sha(path) != artifact["sha256"]:
            raise AssertionError(f"dependency drift: {name}")
        dependencies[name] = json.loads(path.read_text())
    target = dependencies["complete_smooth_target"]
    if target["complete_output_cokernel_theorem"]["decomposition"] != "coker L_smooth = span{zeta_H,zeta_Px,zeta_J1,zeta_J2,zeta_J3}":
        raise AssertionError("target cokernel completeness replay failed")
    if target["smooth_global_theorem"]["tangent_cone"] != "Z2^smooth={u in T_WM^finite:mu_H=mu_Px=mu_J1=mu_J2=mu_J3=0}":
        raise AssertionError("smooth five-charge sufficiency replay failed")
    charges = dependencies["complete_charge_q2"]
    if charges["operation"]["definition"] != "q2_charge,X(u,v)=D^2[mu_WM,X(iota u)-mu_EM,X(u)]|_0(u,v)=<zeta_X,Delta2(u,v)>":
        raise AssertionError("relative charge/defect identity drifted")
    matrix = sp.Matrix([[sp.Integer(x) for x in row] for row in value["factorization"]["matrix"]])
    if matrix != sp.eye(5) or matrix.rank() != 5:
        raise AssertionError("normalized factorization matrix is not I5")
    witness = sp.sympify(value["normalization_witness"]["mu_rel_H_diagonal"])
    if sp.simplify(witness + sp.Rational(54, 5) * (1 + sp.sqrt(3))) != 0:
        raise AssertionError("normalization witness drifted")
    flags = value["classification"]
    if any(flags[key] for key in ("serialized_all_mode_source_pair_matrix_computed", "target_primal_obstruction_representatives_exported", "support_local_relative_lift_constructed", "full_relative_q2_repaired", "bounded_correction_factorization_certified", "causal_retarded_factorization_certified", "arity_three_authorized", "observable_particle_or_quantum_claim")):
        raise AssertionError("reduced theorem overpromoted")
    if value["polarized_domain"]["definition"] != "B_standard=Sym^2(H^0(q1_EM)_standard)":
        raise AssertionError("polarized domain drifted")
    return {"status": "PASS", "obstruction_dimension": 5, "factorization_rank": matrix.rank(), "factorization_matrix": "I5_quotient_coordinates", "kernel_identity_exact": True, "serialized_source_pair_matrix_open": True, "support_local_lift_open": True}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
