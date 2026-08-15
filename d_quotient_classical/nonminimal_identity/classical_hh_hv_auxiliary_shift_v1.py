#!/usr/bin/env python3
"""Export exact cylinder hh/hv jets of the nonlinear auxiliary shift."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ACTION = ROOT / "covariant_completion/certificates/curved_auxiliary_action_definition.json"
SPLIT = ROOT / "covariant_completion/certificates/curved_auxiliary_canonical_split.json"
PREDECESSOR = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_HH_HV_AUXILIARY_SHIFT_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/classical-hh-hv-auxiliary-shift-v1.md"

DIM = 4
SIGNS = (-1, 1, 1, 1)
COORDS = tuple((i, j) for i in range(DIM) for j in range(i, DIM))
MULTI2 = tuple(sorted((x for x in itertools.product(range(3), repeat=DIM) if sum(x) <= 2), key=lambda x: (sum(x), x)))
MULTI1 = tuple(x for x in MULTI2 if sum(x) <= 1)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(data).hexdigest()


def zero_matrix() -> list[list[Fraction]]:
    return [[Fraction(0) for _ in range(DIM)] for _ in range(DIM)]


def matmul(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[sum((left[i][k] * right[k][j] for k in range(DIM)), Fraction(0)) for j in range(DIM)] for i in range(DIM)]


ETA = [[Fraction(SIGNS[i] if i == j else 0) for j in range(DIM)] for i in range(DIM)]
RICCI0 = [[Fraction(2 if i == j and i > 0 else 0) for j in range(DIM)] for i in range(DIM)]
R0 = Fraction(6)


def background_metric_second(axis: int, other: int, mu: int, nu: int) -> Fraction:
    """Second coordinate jet of -dt^2+(1+|x|^2/4)^-2 dx^i dx^i at x=0."""

    return Fraction(-int(axis == other and axis > 0 and mu == nu and mu > 0))


def symmetric_basis(coord: tuple[int, int]) -> list[list[Fraction]]:
    out = zero_matrix()
    left, right = coord
    out[left][right] = out[right][left] = Fraction(1)
    return out


def direction(coord_index: int, multiindex: tuple[int, ...]) -> dict[str, Any]:
    value = zero_matrix()
    first = [zero_matrix() for _ in range(DIM)]
    second = [[zero_matrix() for _ in range(DIM)] for _ in range(DIM)]
    tensor = symmetric_basis(COORDS[coord_index])
    order = sum(multiindex)
    if order == 0:
        value = tensor
    elif order == 1:
        axis = multiindex.index(1)
        first[axis] = tensor
    elif order == 2:
        axes = [axis for axis, count in enumerate(multiindex) for _ in range(count)]
        second[axes[0]][axes[1]] = tensor
        second[axes[1]][axes[0]] = tensor
    else:
        raise ValueError("only two-jets are supported")
    return {"value": value, "first": first, "second": second}


def q1(data: dict[str, Any]) -> list[list[Fraction]]:
    return [[-SIGNS[i] * SIGNS[j] * data["value"][i][j] for j in range(DIM)] for i in range(DIM)]


def dq1(data: dict[str, Any], axis: int) -> list[list[Fraction]]:
    return [[-SIGNS[i] * SIGNS[j] * data["first"][axis][i][j] for j in range(DIM)] for i in range(DIM)]


def q2(left: dict[str, Any], right: dict[str, Any]) -> list[list[Fraction]]:
    return [[
        sum((
            ETA[i][a] * left["value"][a][b] * ETA[b][c]
            * right["value"][c][d] * ETA[d][j]
            + ETA[i][a] * right["value"][a][b] * ETA[b][c]
            * left["value"][c][d] * ETA[d][j]
        for a in range(DIM) for b in range(DIM) for c in range(DIM) for d in range(DIM)), Fraction(0))
        for j in range(DIM)
    ] for i in range(DIM)]


def q2_direct(left: dict[str, Any], right: dict[str, Any]) -> list[list[Fraction]]:
    first = matmul(matmul(matmul(matmul(ETA, left["value"]), ETA), right["value"]), ETA)
    second = matmul(matmul(matmul(matmul(ETA, right["value"]), ETA), left["value"]), ETA)
    return [[first[i][j] + second[i][j] for j in range(DIM)] for i in range(DIM)]


def metric_derivative_combo(data: dict[str, Any], mu: int, nu: int, sigma: int) -> Fraction:
    return data["first"][mu][sigma][nu] + data["first"][nu][sigma][mu] - data["first"][sigma][mu][nu]


def metric_second_combo(data: dict[str, Any], axis: int, mu: int, nu: int, sigma: int) -> Fraction:
    return data["second"][axis][mu][sigma][nu] + data["second"][axis][nu][sigma][mu] - data["second"][axis][sigma][mu][nu]


def background_second_combo(axis: int, mu: int, nu: int, sigma: int) -> Fraction:
    return (
        background_metric_second(axis, mu, sigma, nu)
        + background_metric_second(axis, nu, sigma, mu)
        - background_metric_second(axis, sigma, mu, nu)
    )


def gamma1(data: dict[str, Any]) -> list[list[list[Fraction]]]:
    return [[[
        Fraction(1, 2) * SIGNS[rho] * metric_derivative_combo(data, mu, nu, rho)
        for nu in range(DIM)
    ] for mu in range(DIM)] for rho in range(DIM)]


def dgamma1(data: dict[str, Any], axis: int) -> list[list[list[Fraction]]]:
    inverse_one = q1(data)
    return [[[
        Fraction(1, 2) * (
            SIGNS[rho] * metric_second_combo(data, axis, mu, nu, rho)
            + sum((inverse_one[rho][sigma] * background_second_combo(axis, mu, nu, sigma) for sigma in range(DIM)), Fraction(0))
        )
        for nu in range(DIM)
    ] for mu in range(DIM)] for rho in range(DIM)]


def gamma2(left: dict[str, Any], right: dict[str, Any]) -> list[list[list[Fraction]]]:
    left_inverse, right_inverse = q1(left), q1(right)
    return [[[
        Fraction(1, 2) * sum((
            left_inverse[rho][sigma] * metric_derivative_combo(right, mu, nu, sigma)
            + right_inverse[rho][sigma] * metric_derivative_combo(left, mu, nu, sigma)
        for sigma in range(DIM)), Fraction(0))
        for nu in range(DIM)
    ] for mu in range(DIM)] for rho in range(DIM)]


def dgamma2(left: dict[str, Any], right: dict[str, Any], inverse_two: list[list[Fraction]], axis: int) -> list[list[list[Fraction]]]:
    left_inverse, right_inverse = left["q1"], right["q1"]
    dleft_inverse, dright_inverse = left["dq1"][axis], right["dq1"][axis]
    left_data, right_data = left["data"], right["data"]
    return [[[
        Fraction(1, 2) * sum((
            dleft_inverse[rho][sigma] * metric_derivative_combo(right_data, mu, nu, sigma)
            + left_inverse[rho][sigma] * metric_second_combo(right_data, axis, mu, nu, sigma)
            + dright_inverse[rho][sigma] * metric_derivative_combo(left_data, mu, nu, sigma)
            + right_inverse[rho][sigma] * metric_second_combo(left_data, axis, mu, nu, sigma)
            + inverse_two[rho][sigma] * background_second_combo(axis, mu, nu, sigma)
        for sigma in range(DIM)), Fraction(0))
        for nu in range(DIM)
    ] for mu in range(DIM)] for rho in range(DIM)]


def ricci1(data: dict[str, Any]) -> list[list[Fraction]]:
    derivatives = [dgamma1(data, axis) for axis in range(DIM)]
    return [[
        sum((derivatives[rho][rho][mu][nu] - derivatives[nu][rho][mu][rho] for rho in range(DIM)), Fraction(0))
        for nu in range(DIM)
    ] for mu in range(DIM)]


def ricci2(left: dict[str, Any], right: dict[str, Any]) -> tuple[list[list[Fraction]], list[list[Fraction]]]:
    left_gamma, right_gamma = left["gamma1"], right["gamma1"]
    inverse_two = q2_direct(left["data"], right["data"])
    derivatives = [dgamma2(left, right, inverse_two, axis) for axis in range(DIM)]
    return [[
        sum((derivatives[rho][rho][mu][nu] - derivatives[nu][rho][mu][rho] for rho in range(DIM)), Fraction(0))
        + sum((
            left_gamma[rho][rho][lam] * right_gamma[lam][mu][nu]
            + right_gamma[rho][rho][lam] * left_gamma[lam][mu][nu]
            - left_gamma[rho][nu][lam] * right_gamma[lam][mu][rho]
            - right_gamma[rho][nu][lam] * left_gamma[lam][mu][rho]
        for rho in range(DIM) for lam in range(DIM)), Fraction(0))
        for nu in range(DIM)
    ] for mu in range(DIM)], inverse_two


def contraction(left: list[list[Fraction]], right: list[list[Fraction]]) -> Fraction:
    return sum((left[i][j] * right[i][j] for i in range(DIM) for j in range(DIM)), Fraction(0))


def scalar1(data: dict[str, Any], ricci: list[list[Fraction]] | None = None) -> Fraction:
    return contraction(ETA, ricci or ricci1(data)) + contraction(q1(data), RICCI0)


def prepare(data: dict[str, Any]) -> dict[str, Any]:
    inverse_one = q1(data)
    inverse_derivatives = [dq1(data, axis) for axis in range(DIM)]
    connection = gamma1(data)
    ricci = ricci1(data)
    scalar = contraction(ETA, ricci) + contraction(inverse_one, RICCI0)
    return {"data": data, "q1": inverse_one, "dq1": inverse_derivatives, "gamma1": connection, "ricci1": ricci, "scalar1": scalar}


def hh_second_frechet(left: dict[str, Any], right: dict[str, Any]) -> list[list[Fraction]]:
    left_ricci, right_ricci = left["ricci1"], right["ricci1"]
    mixed_ricci, inverse_two = ricci2(left, right)
    scalar_two = (
        contraction(ETA, mixed_ricci)
        + contraction(left["q1"], right_ricci)
        + contraction(right["q1"], left_ricci)
        + contraction(inverse_two, RICCI0)
    )
    left_scalar, right_scalar = left["scalar1"], right["scalar1"]
    left_data, right_data = left["data"], right["data"]
    return [[
        2 * mixed_ricci[mu][nu]
        - Fraction(1, 3) * (
            ETA[mu][nu] * scalar_two
            + left_data["value"][mu][nu] * right_scalar
            + right_data["value"][mu][nu] * left_scalar
        )
        for nu in range(DIM)
    ] for mu in range(DIM)]


def hv_second_frechet(metric: dict[str, Any], vector_index: int) -> list[list[Fraction]]:
    connection = gamma1(metric)
    return [[-2 * connection[vector_index][mu][nu] for nu in range(DIM)] for mu in range(DIM)]


def jet_label(multiindex: tuple[int, ...]) -> str:
    return "d" + "".join(str(x) for x in multiindex)


def hh_entries() -> list[dict[str, Any]]:
    basis = tuple((coord, multi) for coord in range(len(COORDS)) for multi in MULTI2)
    directions = tuple(prepare(direction(coord, multi)) for coord, multi in basis)
    entries: list[dict[str, Any]] = []
    for left_index, ((left_coord, left_multi), left) in enumerate(zip(basis, directions, strict=True)):
        for right_index in range(left_index, len(basis)):
            right_coord, right_multi = basis[right_index]
            if sum(left_multi) + sum(right_multi) not in (0, 2):
                continue
            values = hh_second_frechet(left, directions[right_index])
            for output, (mu, nu) in enumerate(COORDS):
                coefficient = values[mu][nu]
                if coefficient:
                    homogeneous = coefficient / 2 if left_index == right_index else coefficient
                    entries.append({
                        "output_row": f"f_hat_{mu}{nu}",
                        "h_left_row": f"h_{COORDS[left_coord][0]}{COORDS[left_coord][1]}",
                        "h_left_jet": list(left_multi),
                        "h_right_row": f"h_{COORDS[right_coord][0]}{COORDS[right_coord][1]}",
                        "h_right_jet": list(right_multi),
                        "second_Frechet_coefficient": str(coefficient),
                        "homogeneous_polynomial_coefficient": str(homogeneous),
                    })
    return entries


def hv_entries() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for coord in range(len(COORDS)):
        for multi in MULTI1:
            values_by_vector = [hv_second_frechet(direction(coord, multi), vector) for vector in range(DIM)]
            for vector, values in enumerate(values_by_vector):
                for mu, nu in COORDS:
                    coefficient = values[mu][nu]
                    if coefficient:
                        entries.append({
                            "output_row": f"f_hat_{mu}{nu}",
                            "h_row": f"h_{COORDS[coord][0]}{COORDS[coord][1]}",
                            "h_jet": list(multi),
                            "v_row": f"v_{vector}",
                            "v_jet": [0, 0, 0, 0],
                            "second_Frechet_coefficient": str(coefficient),
                            "homogeneous_polynomial_coefficient": str(coefficient),
                        })
    return entries


def cylinder_ricci_regression() -> dict[str, Any]:
    # At the normal point Gamma vanishes, so the background Ricci tensor is
    # obtained only from the differentiated background Christoffels.
    derivative_gamma = [[[[
        Fraction(1, 2) * SIGNS[rho] * background_second_combo(axis, mu, nu, rho)
        for nu in range(DIM)
    ] for mu in range(DIM)] for rho in range(DIM)] for axis in range(DIM)]
    ricci = [[sum((derivative_gamma[rho][rho][mu][nu] - derivative_gamma[nu][rho][mu][rho] for rho in range(DIM)), Fraction(0)) for nu in range(DIM)] for mu in range(DIM)]
    scalar = contraction(ETA, ricci)
    return {"Ricci_covariant": [[str(x) for x in row] for row in ricci], "scalar_curvature": str(scalar), "matches_unit_cylinder": ricci == RICCI0 and scalar == R0}


def scalar_direction(multiindex: tuple[int, ...]) -> dict[str, Any]:
    value = Fraction(int(sum(multiindex) == 0))
    first = [Fraction(int(sum(multiindex) == 1 and multiindex[axis] == 1)) for axis in range(DIM)]
    second = [[Fraction(0) for _ in range(DIM)] for _ in range(DIM)]
    if sum(multiindex) == 2:
        axes = [axis for axis, count in enumerate(multiindex) for _ in range(count)]
        second[axes[0]][axes[1]] = second[axes[1]][axes[0]] = Fraction(1)
    return {"value": value, "first": first, "second": second}


def scalar_times_metric(scalar: dict[str, Any]) -> dict[str, Any]:
    value = [[scalar["value"] * ETA[i][j] for j in range(DIM)] for i in range(DIM)]
    first = [[[scalar["first"][axis] * ETA[i][j] for j in range(DIM)] for i in range(DIM)] for axis in range(DIM)]
    second = [[[[
        scalar["second"][axis][other] * ETA[i][j]
        + scalar["value"] * background_metric_second(axis, other, i, j)
        for j in range(DIM)
    ] for i in range(DIM)] for other in range(DIM)] for axis in range(DIM)]
    return {"value": value, "first": first, "second": second}


def scalar_product_times_metric(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    product_value = left["value"] * right["value"]
    product_first = [left["first"][axis] * right["value"] + left["value"] * right["first"][axis] for axis in range(DIM)]
    product_second = [[
        left["second"][axis][other] * right["value"]
        + left["value"] * right["second"][axis][other]
        + left["first"][axis] * right["first"][other]
        + right["first"][axis] * left["first"][other]
        for other in range(DIM)
    ] for axis in range(DIM)]
    return scalar_times_metric({"value": product_value, "first": product_first, "second": product_second})


def linear_metric_shift(data: dict[str, Any]) -> list[list[Fraction]]:
    ricci = ricci1(data)
    scalar = scalar1(data, ricci)
    return [[2 * ricci[i][j] - Fraction(1, 3) * (data["value"][i][j] * R0 + ETA[i][j] * scalar) for j in range(DIM)] for i in range(DIM)]


def weyl_second_variation_regression() -> dict[str, Any]:
    scalar_basis = tuple(scalar_direction(multiindex) for multiindex in MULTI2)
    metric_basis = tuple(prepare(scalar_times_metric(item)) for item in scalar_basis)
    checks = 0
    defects = 0
    for left_index, (left_scalar, left_metric) in enumerate(zip(scalar_basis, metric_basis, strict=True)):
        for right_index in range(left_index, len(scalar_basis)):
            right_scalar, right_metric = scalar_basis[right_index], metric_basis[right_index]
            linear = linear_metric_shift(scalar_product_times_metric(left_scalar, right_scalar))
            hh = hh_second_frechet(left_metric, right_metric)
            hv_left = [[sum((hv_second_frechet(left_metric["data"], axis)[i][j] * right_scalar["first"][axis] for axis in range(DIM)), Fraction(0)) for j in range(DIM)] for i in range(DIM)]
            hv_right = [[sum((hv_second_frechet(right_metric["data"], axis)[i][j] * left_scalar["first"][axis] for axis in range(DIM)), Fraction(0)) for j in range(DIM)] for i in range(DIM)]
            inner = sum((SIGNS[axis] * left_scalar["first"][axis] * right_scalar["first"][axis] for axis in range(DIM)), Fraction(0))
            vv = [[
                left_scalar["first"][i] * right_scalar["first"][j]
                + right_scalar["first"][i] * left_scalar["first"][j]
                - ETA[i][j] * inner
                for j in range(DIM)
            ] for i in range(DIM)]
            for i, j in COORDS:
                checks += 1
                defects += int(linear[i][j] + hh[i][j] + hv_left[i][j] + hv_right[i][j] + vv[i][j] != 0)
    return {"identity": "D H[(s t)g]+D2 H[(s g,d s),(t g,d t)]=0", "scalar_two_jet_pairs": len(MULTI2) * (len(MULTI2) + 1) // 2, "component_checks": checks, "defects": defects}


def build() -> dict[str, Any]:
    action, split, predecessor = (json.loads(path.read_text()) for path in (ACTION, SPLIT, PREDECESSOR))
    if action.get("schema") != "pure-weyl-covariant-auxiliary-action-definition-v1":
        raise ValueError("ordinary-derivative action drift")
    if split.get("schema") != "pure-weyl-curved-auxiliary-canonical-split-v1":
        raise ValueError("canonical split drift")
    if split.get("canonical_lift", {}).get("local_BV_cotangent_lift_is_canonical") is not True:
        raise ValueError("local BV cotangent lift unavailable")
    if predecessor.get("result_id") != "CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1":
        raise ValueError("shifted cubic predecessor drift")
    if q2(direction(0, MULTI2[0]), direction(1, MULTI2[0])) != q2_direct(direction(0, MULTI2[0]), direction(1, MULTI2[0])):
        raise AssertionError("inverse-metric second variation drift")
    regression = cylinder_ricci_regression()
    if regression["matches_unit_cylinder"] is not True:
        raise AssertionError("cylinder curvature normalization drift")
    hh, hv = hh_entries(), hv_entries()
    weyl_regression = weyl_second_variation_regression()
    if not hh or not hv:
        raise AssertionError("empty hh/hv component table")
    if weyl_regression["defects"]:
        raise AssertionError("nonlinear Weyl second-variation regression failed")
    field_tables = {
        "nonlinear_source_to_split_map": "phi_hat=phi-A_g^{-1}G^b(g,b)",
        "simplified_exact_shift": "phi_hat=phi+2 Ric-(1/3)g R+sym(nabla b)+b tensor b-(1/2)g b^2",
        "coordinate_background": "unit conformal cylinder at the stereographic spatial origin",
        "coordinate_convention": "covariant symmetric components; raw commuting partial-derivative jets in normal coordinates",
        "metric_jet_multiindices": [list(x) for x in MULTI2],
        "vector_jet_multiindices_used_by_hv": [[0, 0, 0, 0]],
        "hh_second_Frechet": {
            "input_jet_coordinates_per_metric_field": len(MULTI2),
            "input_field_jet_coordinates": len(COORDS) * len(MULTI2),
            "possible_symmetric_input_pairs": len(COORDS) * len(MULTI2) * (len(COORDS) * len(MULTI2) + 1) // 2,
            "nonzero_output_component_coefficients": len(hh),
            "maximum_total_derivative_order": 2,
            "entries": hh,
        },
        "hv_second_Frechet": {
            "metric_input_jet_coordinates_considered": len(COORDS) * len(MULTI1),
            "vector_input_coordinates": DIM,
            "nonzero_output_component_coefficients": len(hv),
            "maximum_total_derivative_order": 1,
            "entries": hv,
        },
        "cylinder_curvature_regression": regression,
        "nonlinear_Weyl_second_variation_regression": weyl_regression,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "classical-hh-hv-auxiliary-shift-v1",
        "result_id": "CLASSICAL_HH_HV_AUXILIARY_SHIFT_V1",
        "result_kind": "AUTHORITATIVE_CURVED_NONLINEAR_AUXILIARY_SHIFT_SECOND_FRECHET_COMPONENT_EXPORT",
        "result_state": "CYLINDER_HH_HV_FIELD_COMPONENT_JETS_EXACT_COTANGENT_RECEIVER_PENDING",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {"theory": "four-dimensional ordinary-derivative strict pure-Weyl gravity", "background": "unit conformal cylinder", "basepoint": "stereographic spatial origin", "carrier_sector": "metric/vector to shifted auxiliary tensor", "coefficient_field": "Q", "jet_order": 2},
        "field_component_tables": field_tables,
        "foundational_strength": {"exact_rational": True, "finite_jet_table": True, "finite_upper_bound": "PRA", "support_local": True, "uses_green_operator": False, "uses_spectral_projector": False, "uses_choice_principle": False},
        "claim_flags": {"HH_SECOND_FRECHET_COMPONENT_JETS_SERIALIZED": True, "HV_SECOND_FRECHET_COMPONENT_JETS_SERIALIZED": True, "CURVED_CYLINDER_ZEROTH_ORDER_TERMS_INCLUDED": True, "HH_HV_COTANGENT_PARTNERS_SERIALIZED": False, "FULL_386_QUADRATIC_BV_COTANGENT_LIFT_SERIALIZED": False, "CLASSICAL_IMPORT_GATE_PASSED": False, "HADAMARD_STATE_CONSTRUCTED": False, "QME_RESTORED": False},
        "does_not_establish": ["the hh/hv BV cotangent partners on the 386-row carrier", "the three diffeomorphism auxiliary representation vertices", "an exhaustive nonlinear Weyl/boost ghost-antifield family census", "the full source q2/q3 pullback or cyclic L-infinity equivalence", "Gate A, causal lambda-squared closure, Hadamard data, renormalized Lorentzian products, QME restoration, or residual transfer"],
        "canonical_hashes": {"field_component_tables_sha256": digest(field_tables), "hh_entries_sha256": digest(hh), "hv_entries_sha256": digest(hv)},
        "provenance": {"inputs": [
            {"path": str(ACTION.relative_to(ROOT)), "schema": action["schema"], "sha256": sha(ACTION), "role": "authoritative exact ordinary-derivative action and G^b definition"},
            {"path": str(SPLIT.relative_to(ROOT)), "schema": split["schema"], "sha256": sha(SPLIT), "role": "authoritative exact nonlinear auxiliary shift and type-II generator"},
            {"path": str(PREDECESSOR.relative_to(ROOT)), "result_id": predecessor["result_id"], "sha256": sha(PREDECESSOR), "role": "predecessor cubic family census and vv component sector"},
        ]},
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Import the hh/hv field jets into the 386-row receiver and construct their formal-adjoint h-star/v-star cotangent partners before promoting the full quadratic BV cotangent lift.",
    }


def render(value: dict[str, Any]) -> str:
    tables = value["field_component_tables"]
    hh, hv = tables["hh_second_Frechet"], tables["hv_second_Frechet"]
    return f"""# Classical hh/hv auxiliary-shift jets v1

**Result:** `{value['result_id']}`
**Dependency:** `LOCAL-ALGEBRAIC`

The exact nonlinear shift was differentiated twice on the unit conformal
cylinder.  The hh table contains **{hh['nonzero_output_component_coefficients']}**
nonzero rational output coefficients over {hh['possible_symmetric_input_pairs']}
symmetric metric two-jet input pairs.  The hv table contains
**{hv['nonzero_output_component_coefficients']}** nonzero rational coefficients.
Curvature-dependent order-zero hh terms are included; this is not merely a
flat principal-symbol calculation.

The source export stops before the BV cotangent lift.  The 386-row receiver
must independently import these bytes and construct the formal-adjoint
h-star/v-star partners before the full quadratic canonical map can be claimed.

## Reproduction

```text
python3 d_quotient_classical/nonminimal_identity/classical_hh_hv_auxiliary_shift_v1.py --check
python3 d_quotient_classical/nonminimal_identity/check_classical_hh_hv_auxiliary_shift_v1.py
python3 d_quotient_classical/nonminimal_identity/check_classical_hh_hv_auxiliary_shift_v1.py --exhaustive  # Tier 2
python3 d_quotient_classical/nonminimal_identity/verify_classical_hh_hv_auxiliary_shift_v1.py
python3 -m unittest d_quotient_classical.nonminimal_identity.tests.test_classical_hh_hv_auxiliary_shift_v1
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
        print("CLASSICAL_HH_HV_AUXILIARY_SHIFT_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print("CLASSICAL_HH_HV_AUXILIARY_SHIFT_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
