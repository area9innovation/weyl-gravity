#!/usr/bin/env python3
"""Independent receiver for the M1A2 local semantic extension."""

from __future__ import annotations

import copy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.weyl_3plus1 import stf_basis, weyl_component

HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1.json"
REPORT = HERE / "REPORT_STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1.md"
LOCAL = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
AUXILIARY = ROOT / "covariant_completion/certificates/curved_auxiliary_canonical_split.json"
GAUGE = ROOT / "d_quotient_classical/certificates/CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1.json"
CONE = ROOT / "covariant_completion/certificates/curved_curvature_mapping_cylinder_kernel.json"
HYPERBOLIC = ROOT / "covariant_completion/certificates/curved_weyl_cotton_hyperbolic.json"
THREE_PLUS_ONE = ROOT / "covariant_completion/certificates/curved_weyl_cotton_3plus1.json"
INPUTS = (LOCAL, AUXILIARY, GAUGE, CONE, HYPERBOLIC, THREE_PLUS_ONE)

AUX = {
    "AUX_ETA": (0, 0, 1, 0), "AUX_F_HAT": (0, 0, 2, 0), "AUX_V": (0, 0, 1, 0),
    "AUX_F_HAT_STAR": (1, 4, 2, 0), "AUX_V_STAR": (1, 4, 3, 0), "AUX_ETA_STAR": (2, 4, 3, 0),
}


def canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def primal_mass(family: str, index: int) -> int:
    if family == "U":
        return 2 if index < 10 else 3
    if family == "Eq":
        if index < 10 or 26 <= index < 32:
            return 3
        return 4
    if family == "Id":
        return 4 if index < 6 else 5
    raise ValueError(family)


def parse_cone(block: str) -> tuple[str, bool]:
    name = block.removeprefix("CONE_")
    sharp = name.endswith("_SHARP")
    if sharp:
        name = name.removesuffix("_SHARP")
    _, family = name.split("_", 1)
    return {"U": "U", "EQ": "Eq", "ID": "Id"}[family], sharp


@lru_cache(maxsize=1)
def cotton_weyl_mixing_counts() -> tuple[int, int, int]:
    metric = sp.diag(-1, 1, 1, 1)
    basis = stf_basis()
    checks = defects = nonzero = 0
    for basis_index in range(10):
        electric = basis[basis_index] if basis_index < 5 else sp.zeros(3)
        magnetic = basis[basis_index - 5] if basis_index >= 5 else sp.zeros(3)

        def W(a: int, d: int, b: int, c: int) -> sp.Expr:
            return weyl_component(electric, magnetic, a, d, b, c)

        for omega_index in range(4):
            omega = [sp.Integer(int(i == omega_index)) for i in range(4)]
            omega_up = [sum(metric[p, q] * omega[q] for q in range(4)) for p in range(4)]

            def C(p: int, e: int, a: int) -> sp.Expr:
                return int(p == e) * omega[a] + int(p == a) * omega[e] - metric[e, a] * omega_up[p]

            for a in range(4):
                for b in range(4):
                    for c in range(4):
                        actual = sp.Integer(0)
                        for d in range(4):
                            for e in range(4):
                                if metric[d, e] == 0:
                                    continue
                                term = 2 * omega[e] * W(a, d, b, c)
                                term -= sum(C(p, e, a) * W(p, d, b, c) for p in range(4))
                                term -= sum(C(p, e, d) * W(a, p, b, c) for p in range(4))
                                term -= sum(C(p, e, b) * W(a, d, p, c) for p in range(4))
                                term -= sum(C(p, e, c) * W(a, d, b, p) for p in range(4))
                                actual += metric[d, e] * term
                        expected = sum(omega_up[p] * W(a, p, b, c) for p in range(4))
                        checks += 1
                        defects += int(sp.expand(actual - expected) != 0)
                        nonzero += int(expected != 0)
    return checks, defects, nonzero


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    local = json.loads(LOCAL.read_text())
    if value.get("result_id") != "STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")

    provenance = {row.get("path"): row for row in value.get("provenance", {}).get("inputs", [])}
    for path in INPUTS:
        relative = str(path.relative_to(ROOT))
        if provenance.get(relative, {}).get("sha256") != file_hash(path):
            errors.append(f"input hash {relative}")

    rows = value.get("local_extension_rows", [])
    sources = local["component_basis"]["rows"][30:]
    if len(rows) != 356 or len(sources) != 356:
        errors.append("extension count")
    else:
        for source, actual in zip(sources, rows, strict=True):
            expected_common = {
                "index": source["index"], "row_id": source["row_id"], "block": source["block"],
                "chain_degree": source["degree"], "bv_ghost_number": -source["degree"],
                "Grassmann_parity": source["degree"] % 2, "intrinsic_jet_order_bound": 0,
            }
            if any(actual.get(key) != expected for key, expected in expected_common.items()):
                errors.append(f"common row semantics {source['row_id']}")
                continue
            if actual.get("conformal_compact_weight", {}).get("status") != "NOT_APPLICABLE" or actual.get("ce_ghost_number", {}).get("status") != "NOT_APPLICABLE":
                errors.append(f"not-applicable tags {source['row_id']}")
            if source["block"] in AUX:
                afn, form, mass, weight = AUX[source["block"]]
                if (actual.get("antifield_number"), actual.get("form_degree"), actual.get("mass_dimension"), actual.get("Weyl_weight"), actual.get("semantic_state")) != (afn, form, mass, weight, "FULLY_NAMESPACED"):
                    errors.append(f"auxiliary semantics {source['row_id']}")
            else:
                family, sharp = parse_cone(source["block"])
                mass = primal_mass(family, source["local_index"])
                if sharp:
                    mass = 4 - mass
                expected = (max(source["degree"], 0), 4 if source["degree"] > 0 else 0, mass)
                if (actual.get("antifield_number"), actual.get("form_degree"), actual.get("mass_dimension")) != expected:
                    errors.append(f"cone grading {source['row_id']}")
                weight = actual.get("Weyl_weight")
                if not isinstance(weight, dict) or weight.get("status") != "NOT_APPLICABLE" or actual.get("semantic_state") != "FULLY_NAMESPACED_NONLINEAR_SCALAR_WEYL_WEIGHT_NOT_APPLICABLE":
                    errors.append(f"cone Weyl applicability {source['row_id']}")

    expected_counts = {
        "extension_rows": 356, "auxiliary_rows_fully_namespaced": 36,
        "mapping_cone_rows_fully_namespaced": 320,
        "mapping_cone_rows_with_not_applicable_scalar_Weyl_weight": 320,
        "rows_with_unresolved_fields": 0,
        "local_386_rows_fully_namespaced_after_this_result": 386,
        "local_386_rows_remaining_partial": 0,
    }
    if value.get("counts") != expected_counts:
        errors.append("counts")
    applicability = value.get("scalar_weyl_weight_applicability", {})
    if applicability.get("affected_rows") != 320 or applicability.get("classification") != "NOT_APPLICABLE" or applicability.get("not_unknown") is not True:
        errors.append("Weyl applicability")
    checks, defects, nonzero = cotton_weyl_mixing_counts()
    witness = value.get("cotton_nonlinear_weyl_non_eigen_witness", {})
    if (witness.get("component_checks"), witness.get("defects"), witness.get("nonzero_mixing_checks")) != (checks, defects, nonzero) or checks != 2560 or defects != 0 or nonzero == 0:
        errors.append("Cotton non-eigen witness")
    if value.get("mapping_cone_dimension_functor", {}).get("cotangent_rule") != "dim(z_sharp)=4-dim(z)":
        errors.append("dimension functor")

    flags = value.get("claim_flags", {})
    if flags.get("M1A2_AUXILIARY_36_FULLY_NAMESPACED") is not True or flags.get("M1A2_MAPPING_CONE_320_FULLY_NAMESPACED") is not True or flags.get("M1A2_SCALAR_WEYL_WEIGHT_APPLICABILITY_CLASSIFIED") is not True or flags.get("LOCAL_386_FULLY_TYPED") is not True:
        errors.append("positive claim flags")
    for flag in ("M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE", "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE", "M1C_COMMON_MANIFEST_REPLAY_COMPLETE", "CLASSICAL_IMPORT_GATE_PASSED", "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED"):
        if flags.get(flag) is not False:
            errors.append(f"fail-closed flag {flag}")

    replay = copy.deepcopy(value)
    expected_digest = replay.get("independent_checker", {}).get("expected_digest")
    replay.setdefault("independent_checker", {})["expected_digest"] = ""
    if expected_digest != canonical_digest(replay):
        errors.append("certificate digest")
    if not REPORT.exists():
        errors.append("human report absent")
    else:
        report = REPORT.read_text()
        for token in ("36 generalized-auxiliary", "320 contractible cone", "NOT_APPLICABLE", "386 of 386", "Gate A", "Hadamard", "QME"):
            if token not in report:
                errors.append(f"report token {token}")
    return errors


def main() -> int:
    errors = check(json.loads(RESULT.read_text()))
    if errors:
        print("STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1: PASS")
    print("  - 36 shifted auxiliary rows fully namespaced")
    print("  - 320 cone rows fully namespaced; scalar nonlinear Weyl weight is exactly not applicable")
    print("  - 2,560 Cotton transformation components verify the non-eigenrow witness")
    print("  - M1A, Gate A, Hadamard and QME remain fail closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
