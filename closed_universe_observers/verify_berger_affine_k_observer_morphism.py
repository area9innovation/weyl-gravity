#!/usr/bin/env python3
"""Independent verifier for the affine-K observer morphism."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from jsonschema import Draft202012Validator, ValidationError
import sympy as sp

from closed_universe_observers.generate_berger_affine_k_observer_morphism import CERTIFICATE, DEPENDENCIES, SCHEMA, SOURCE_FILES, build


def _independent_ward() -> None:
    u, v, a, b, c = sp.symbols("u v a b c")
    variables = (u, v)
    Q = sp.Matrix([sp.diff((u**2 + v**2) ** 4, u), sp.diff((u**2 + v**2) ** 4, v)])
    A = sp.Matrix([[0, -1], [1, 0]])
    background = sp.Matrix([2, -1])
    directions = (sp.Matrix([a, 1]), sp.Matrix([2, b]), sp.Matrix([-1, c]))

    def derivative(items: tuple[sp.Matrix, ...]) -> sp.Matrix:
        result = Q
        for item in items:
            result = result.jacobian(variables) * item
        return result.subs({u: 2, v: -1})

    defect = derivative((A * background, *directions))
    defect += sum((derivative(tuple(A * item if i == slot else item for i, item in enumerate(directions))) for slot in range(3)), sp.zeros(2, 1))
    defect -= A * derivative(directions)
    if any(sp.expand(entry) != 0 for entry in defect):
        raise ValueError("independent fifth-derivative Ward identity failed")
    deleted = sp.simplify(defect - derivative((A * background, *directions)))
    if not any(sp.expand(entry) != 0 for entry in deleted):
        raise ValueError("independent q4 deletion mutation escaped")


def _independent_record_covariance(value: dict) -> None:
    t, shift = sp.symbols("t shift", real=True)
    first = sp.integrate((5 + sp.cos(t + shift)) * (7 + sp.sin(3 * (t + shift))), (t, 0, 2 * sp.pi))
    second = sp.integrate((11 + sp.sin(t + shift)) * (13 + sp.cos(2 * (t + shift))), (t, 0, 2 * sp.pi))
    if sp.diff(first, shift) != 0 or sp.diff(second, shift) != 0:
        raise ValueError("independent simultaneous record covariance failed")
    if sp.diag(first, second).rank() != 2:
        raise ValueError("independent record rank failed")
    audit = value["observer_morphism"]["exact_covariance_specialization"]
    if audit["K_covariance_defects"] != ["0", "0"] or audit["rank"] != 2:
        raise ValueError("record covariance payload drifted")


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("affine-K observer morphism certificate is stale")
    for name, path in DEPENDENCIES.items():
        if value["dependency_refs"][name]["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"dependency hash drifted: {name}")
    manifest = {item["path"]: item["sha256"] for item in value["provenance"]["source_manifest"]}
    for path in SOURCE_FILES.values():
        relative = str(path.relative_to(CERTIFICATE.parents[2]))
        if manifest.get(relative) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"source hash drifted: {relative}")
    _independent_ward()
    _independent_record_covariance(value)
    flags = value["flags"]
    for key in ("FULL_Q4_EXPORTED", "FIXED_BACKGROUND_LINEAR_K_DESCENT_CERTIFIED", "FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED", "SPATIALLY_LOCALIZED_EMITTER_WORLDTUBES_CERTIFIED", "EMITTER_RECOIL_CERTIFIED", "QUANTUM_CLAIM"):
        if flags[key] is not False:
            raise ValueError(f"overclaim accepted: {key}")
    mutant = deepcopy(value)
    mutant["unexpected"] = True
    try:
        Draft202012Validator(schema).validate(mutant)
    except ValidationError:
        pass
    else:
        raise ValueError("strict schema mutation escaped")
    return value


def main() -> int:
    verify()
    print("BERGER_AFFINE_K_OBSERVER_MORPHISM independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
