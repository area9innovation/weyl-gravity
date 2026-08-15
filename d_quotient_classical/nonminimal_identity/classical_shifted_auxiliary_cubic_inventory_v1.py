#!/usr/bin/env python3
"""Export exact shifted-auxiliary cubic data and its honest completeness boundary."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ACTION = ROOT / "covariant_completion/certificates/curved_auxiliary_action_definition.json"
SPLIT = ROOT / "covariant_completion/certificates/curved_auxiliary_canonical_split.json"
QUADRATIC = ROOT / "d_quotient_classical/certificates/CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1.json"
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/classical-shifted-auxiliary-cubic-inventory-v1.md"

DIM = 4
COORDS = tuple((i, j) for i in range(DIM) for j in range(i, DIM))
SIGNS = (-1, 1, 1, 1)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def tensor(index: int) -> list[list[Fraction]]:
    out = [[Fraction(0) for _ in range(DIM)] for _ in range(DIM)]
    i, j = COORDS[index]
    out[i][j] = out[j][i] = Fraction(1)
    return out


def add(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[left[i][j] + right[i][j] for j in range(DIM)] for i in range(DIM)]


def trace(value: list[list[Fraction]]) -> Fraction:
    return sum((Fraction(SIGNS[i]) * value[i][i] for i in range(DIM)), Fraction(0))


def raised(value: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[Fraction(SIGNS[i] * SIGNS[j]) * value[i][j] for j in range(DIM)] for i in range(DIM)]


def inner(left: list[list[Fraction]], right: list[list[Fraction]]) -> Fraction:
    return sum((Fraction(SIGNS[i] * SIGNS[j]) * left[i][j] * right[i][j] for i in range(DIM) for j in range(DIM)), Fraction(0))


def shifted_mass_cubic(h: list[list[Fraction]], f_hat: list[list[Fraction]]) -> Fraction:
    """Coefficient linear in h and quadratic in f_hat.

    This is the first metric variation of
      sqrt(-g)/4 ((tr_g f_hat)^2-f_hat^{mu nu}f_hat_mu nu)
    at the Minkowski normal frame, with covariant f_hat coordinates fixed.
    """

    tr_h, tr_f = trace(h), trace(f_hat)
    h_up = raised(h)
    h_dot_f = sum((h_up[i][j] * f_hat[i][j] for i in range(DIM) for j in range(DIM)), Fraction(0))
    chain = sum(
        (h_up[mu][alpha] * Fraction(SIGNS[nu]) * f_hat[alpha][nu] * f_hat[mu][nu]
         for mu in range(DIM) for alpha in range(DIM) for nu in range(DIM)),
        Fraction(0),
    )
    return Fraction(1, 8) * tr_h * (tr_f * tr_f - inner(f_hat, f_hat)) - Fraction(1, 2) * tr_f * h_dot_f + Fraction(1, 2) * chain


def shifted_mass_entries() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for h_index, h_coord in enumerate(COORDS):
        h = tensor(h_index)
        for left_index, left_coord in enumerate(COORDS):
            left = tensor(left_index)
            left_value = shifted_mass_cubic(h, left)
            for right_index in range(left_index, len(COORDS)):
                right_coord = COORDS[right_index]
                if left_index == right_index:
                    coefficient = left_value
                else:
                    right = tensor(right_index)
                    coefficient = shifted_mass_cubic(h, add(left, right)) - left_value - shifted_mass_cubic(h, right)
                if coefficient:
                    derivative = coefficient * (2 if left_index == right_index else 1)
                    entries.append({
                        "h_row": f"h_{h_coord[0]}{h_coord[1]}",
                        "f_hat_left_row": f"f_hat_{left_coord[0]}{left_coord[1]}",
                        "f_hat_right_row": f"f_hat_{right_coord[0]}{right_coord[1]}",
                        "homogeneous_polynomial_coefficient": str(coefficient),
                        "D_h_D_f_left_D_f_right": str(derivative),
                    })
    return entries


def vv_entries() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for mu, nu in COORDS:
        for a in range(DIM):
            for b in range(a, DIM):
                coefficient = Fraction(int(mu == a and nu == b))
                if mu == nu and a == b:
                    coefficient -= Fraction(1, 2) * SIGNS[mu] * SIGNS[a]
                if coefficient:
                    entries.append({
                        "output_row": f"f_hat_{mu}{nu}",
                        "v_left_row": f"v_{a}",
                        "v_right_row": f"v_{b}",
                        "homogeneous_polynomial_coefficient": str(coefficient),
                        "second_Frechet_coefficient": str(coefficient * (2 if a == b else 1)),
                    })
    return entries


def conformal_trace_defects() -> int:
    metric_direction = [[Fraction(0) for _ in range(DIM)] for _ in range(DIM)]
    for i, sign in enumerate(SIGNS):
        metric_direction[i][i] = Fraction(sign)
    defects = 0
    for left_index in range(len(COORDS)):
        left = tensor(left_index)
        left_value = shifted_mass_cubic(metric_direction, left)
        for right_index in range(left_index, len(COORDS)):
            right = tensor(right_index)
            coefficient = left_value if left_index == right_index else shifted_mass_cubic(metric_direction, add(left, right)) - left_value - shifted_mass_cubic(metric_direction, right)
            defects += int(coefficient != 0)
    return defects


def build() -> dict[str, Any]:
    action, split, quadratic = (json.loads(path.read_text()) for path in (ACTION, SPLIT, QUADRATIC))
    if action.get("schema") != "pure-weyl-covariant-auxiliary-action-definition-v1":
        raise ValueError("ordinary-derivative action drift")
    if split.get("schema") != "pure-weyl-curved-auxiliary-canonical-split-v1":
        raise ValueError("canonical split drift")
    if split.get("canonical_lift", {}).get("local_BV_cotangent_lift_is_canonical") is not True:
        raise ValueError("local BV cotangent lift unavailable")
    if quadratic.get("result_id") != "CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1":
        raise ValueError("quadratic auxiliary map drift")

    mass_entries = shifted_mass_entries()
    field_entries = vv_entries()
    if len(mass_entries) != 72 or len(field_entries) != 22 or conformal_trace_defects() != 0:
        raise AssertionError("exact cubic component census drift")

    mass_vertex = {
        "source_density": "sqrt(-g)/4*((tr_g f_hat)^2-f_hat^{mu nu}f_hat_mu nu)",
        "cubic_density": "(tr h)((tr f_hat)^2-f_hat^2)/8-(tr f_hat)(h^sharp:f_hat)/2+h^{mu alpha}g^{nu beta}f_hat_{alpha beta}f_hat_{mu nu}/2",
        "block_family": ["ENDPOINT_M", "AUX_F_HAT", "AUX_F_HAT"],
        "component_basis": [f"{i}{j}" for i, j in COORDS],
        "possible_symmetric_component_monomials": 550,
        "nonzero_component_monomials": len(mass_entries),
        "entries": mass_entries,
        "pure_trace_h_defects": 0,
        "pure_trace_h_check_count": 55,
        "interpretation": "The zero pure-trace count is the componentwise four-dimensional Weyl-invariance check of the shifted auxiliary mass vertex.",
    }
    vv_map = {
        "homogeneous_component": "F_(2)(v)=v tensor v-(1/2)g v^2",
        "second_Frechet_component": "D^2F(v,w)=v tensor w+w tensor v-g(v,w)g",
        "block_family": {"inputs": ["AUX_V", "AUX_V"], "output": "AUX_F_HAT"},
        "possible_symmetric_component_coefficients": 100,
        "nonzero_homogeneous_component_coefficients": len(field_entries),
        "entries": field_entries,
    }
    families = [
        {"family_id": "SHIFTED_MASS_H_F_HAT_F_HAT", "cubic_vertex": ["ENDPOINT_M", "AUX_F_HAT", "AUX_F_HAT"], "status": "COMPONENT_COEFFICIENTS_SERIALIZED", "authority": "exact shifted auxiliary mass density", "derivative_order": 0},
        {"family_id": "TYPE_II_F_HAT_STAR_V_V", "cubic_vertex": ["AUX_F_HAT_STAR", "AUX_V", "AUX_V"], "status": "FIELD_COMPONENT_COEFFICIENTS_SERIALIZED_COTANGENT_PARTNER_REQUIRED", "authority": "quadratic vector component of the exact type-II generator", "derivative_order": 0},
        {"family_id": "TYPE_II_F_HAT_STAR_H_H", "cubic_vertex": ["AUX_F_HAT_STAR", "ENDPOINT_M", "ENDPOINT_M"], "status": "FORMULA_DEFINED_COMPONENT_COEFFICIENTS_OPEN", "authority": "D_g^2(A_g^-1 G^b) in the exact type-II generator", "derivative_order": 2},
        {"family_id": "TYPE_II_F_HAT_STAR_H_V", "cubic_vertex": ["AUX_F_HAT_STAR", "ENDPOINT_M", "AUX_V"], "status": "FORMULA_DEFINED_COMPONENT_COEFFICIENTS_OPEN", "authority": "D_g D_b(A_g^-1 G^b) in the exact type-II generator", "derivative_order": 2},
        {"family_id": "DIFF_C_F_HAT_F_HAT_STAR", "cubic_vertex": ["ENDPOINT_G_DIFF", "AUX_F_HAT", "AUX_F_HAT_STAR"], "status": "SOURCE_FORCED_COMPONENT_COEFFICIENTS_OPEN", "authority": "diffeomorphism Lie derivative and BV cotangent lift", "derivative_order": 1},
        {"family_id": "DIFF_C_V_V_STAR", "cubic_vertex": ["ENDPOINT_G_DIFF", "AUX_V", "AUX_V_STAR"], "status": "SOURCE_FORCED_COMPONENT_COEFFICIENTS_OPEN", "authority": "diffeomorphism Lie derivative and BV cotangent lift", "derivative_order": 1},
        {"family_id": "DIFF_C_ETA_ETA_STAR", "cubic_vertex": ["ENDPOINT_G_DIFF", "AUX_ETA", "AUX_ETA_STAR"], "status": "SOURCE_FORCED_COMPONENT_COEFFICIENTS_OPEN", "authority": "diffeomorphism semidirect action on the shifted boost ghost and its cotangent", "derivative_order": 1},
    ]
    completeness = {
        "known_required_cubic_block_families_enumerated": len(families),
        "component_coefficient_complete_families": 1,
        "component_coefficient_complete_after_vv_receiver_cotangent_partner": 2,
        "formula_defined_but_component_open_families": 2,
        "source_forced_gauge_BV_component_open_families": 3,
        "exhaustive_full_nonlinear_BV_family_census": False,
        "reason_not_exhaustive": "The portable source manifest gives the action, the exact field shift and linearized boost transformation, but not the complete nonlinear Weyl/boost ghost algebra and all antifield transformations. Those bytes are required before absence of further ghost families can be certified.",
        "full_component_coefficient_inventory": False,
    }
    candidate_comparison = {
        "trivial_stabilization_auxiliary_blocks_interaction_inert": True,
        "f_hat_v_v_mismatch_after_vv_pullback": "CLOSED",
        "h_f_hat_f_hat_source_vertex_nonzero_coefficients": 72,
        "h_f_hat_f_hat_candidate_vertex_nonzero_coefficients": 0,
        "exact_auxiliary_shift_alone_identifies_source_with_trivial_stabilization": False,
        "further_metric_dependent_canonical_or_L_infinity_normalization_may_exist": True,
        "full_nonlinear_equivalence_obstructed": False,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "classical-shifted-auxiliary-cubic-inventory-v1",
        "result_id": "CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1",
        "result_kind": "AUTHORITATIVE_SHIFTED_AUXILIARY_CUBIC_COMPONENT_EXPORT_AND_COMPLETENESS_AUDIT",
        "result_state": "H_F_HAT_F_HAT_AND_VV_MAP_COMPONENTS_EXACT_REQUIRED_FAMILIES_ENUMERATED_FULL_BV_CENSUS_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {"theory": "four-dimensional ordinary-derivative strict pure-Weyl gravity", "background": "Minkowski normal frame at zero Stueckelberg vector", "carrier_sector": "66-row generalized-auxiliary sector embedded in the strict 386-row carrier", "coefficient_field": "Q", "claim_scope": "zero-jet shifted-mass cubic coefficients, vv field-map coefficients, and evidence-typed required-family census"},
        "shifted_auxiliary_mass_vertex": mass_vertex,
        "quadratic_vv_field_map": vv_map,
        "required_cubic_family_inventory": families,
        "inventory_completeness": completeness,
        "candidate_comparison": candidate_comparison,
        "foundational_strength": {"exact_rational": True, "finite_component_tables": True, "support_local": True, "uses_green_operator": False, "uses_choice_principle": False},
        "claim_flags": {"SHIFTED_MASS_H_F_HAT_F_HAT_COMPONENTS_SERIALIZED": True, "VV_FIELD_MAP_COMPONENTS_SERIALIZED": True, "KNOWN_REQUIRED_CUBIC_FAMILIES_ENUMERATED": True, "EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS": False, "FULL_COMPONENT_COEFFICIENT_INVENTORY": False, "EXACT_SHIFT_ALONE_IDENTIFIES_TRIVIAL_STABILIZATION": False, "FULL_NONLINEAR_EQUIVALENCE_OBSTRUCTED": False, "CLASSICAL_IMPORT_GATE_PASSED": False, "HADAMARD_STATE_CONSTRUCTED": False, "QME_RESTORED": False},
        "does_not_establish": ["an exhaustive nonlinear Weyl/boost ghost-antifield family census", "the hh or hv component tables of the auxiliary shift", "the component tables of the three diffeomorphism representation vertices", "a complete 386-row BV cotangent lift or source q2/q3 pullback", "Gate A, Hadamard data, renormalized Lorentzian products, QME restoration, or residual transfer"],
        "canonical_hashes": {"shifted_auxiliary_mass_vertex_sha256": digest(mass_vertex), "quadratic_vv_field_map_sha256": digest(vv_map), "required_cubic_family_inventory_sha256": digest(families), "candidate_comparison_sha256": digest(candidate_comparison)},
        "provenance": {"inputs": [
            {"path": str(ACTION.relative_to(ROOT)), "schema": action["schema"], "sha256": sha(ACTION), "role": "authoritative ordinary-derivative action and gauge manifest"},
            {"path": str(SPLIT.relative_to(ROOT)), "schema": split["schema"], "sha256": sha(SPLIT), "role": "exact nonlinear split and type-II BV generator"},
            {"path": str(QUADRATIC.relative_to(ROOT)), "result_id": quadratic["result_id"], "sha256": sha(QUADRATIC), "role": "first exact quadratic vector component"},
        ]},
        "literature": {"reference": "R. R. Metsaev, Ordinary-derivative formulation of conformal low-spin fields, arXiv:0707.4437v3, Sec. 6", "url": "https://arxiv.org/abs/0707.4437"},
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Import the 72-entry shifted-mass vertex and 22-entry vv field map into the 386-row receiver, construct the paired vv antifield table, then derive the hh/hv and nonlinear gauge-BV component tables before claiming a full cotangent lift or exhaustive family census.",
    }


def render(value: dict[str, Any]) -> str:
    mass = value["shifted_auxiliary_mass_vertex"]
    complete = value["inventory_completeness"]
    return f"""# Classical shifted-auxiliary cubic inventory v1

**Result:** `{value['result_id']}`
**Dependency:** `LOCAL-ALGEBRAIC`

The exact shifted auxiliary mass is not interaction-inert.  Its
`h-f_hat-f_hat` cubic vertex has **{mass['nonzero_component_monomials']}**
nonzero rational monomials among {mass['possible_symmetric_component_monomials']}
possible component monomials.  All {mass['pure_trace_h_check_count']} pure-trace
metric checks vanish, as required by four-dimensional Weyl invariance.

The already constructed vector part of the nonlinear shift has **22** nonzero
component coefficients.  Together these results enumerate seven currently
required cubic block families, but only {complete['component_coefficient_complete_families']}
is coefficient-complete in this classical export.  The vv cotangent partner,
the hh/hv shift tables, the three Diff representation vertices, and the full
nonlinear Weyl/boost ghost manifest remain separate obligations.

Consequently the vv shift repairs the old `f_hat-v-v` mismatch, but the exact
auxiliary shift alone does **not** identify the source with an interaction-inert
trivial stabilization.  This is not a no-go for a further metric-dependent
canonical or cyclic L-infinity normalization.

## Reproduction

```text
python3 d_quotient_classical/nonminimal_identity/classical_shifted_auxiliary_cubic_inventory_v1.py --check
python3 d_quotient_classical/nonminimal_identity/check_classical_shifted_auxiliary_cubic_inventory_v1.py
python3 d_quotient_classical/nonminimal_identity/verify_classical_shifted_auxiliary_cubic_inventory_v1.py
python3 -m unittest d_quotient_classical.nonminimal_identity.tests.test_classical_shifted_auxiliary_cubic_inventory_v1
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
