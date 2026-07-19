#!/usr/bin/env python3
"""Independent structural and exact-sample verification of the L3 matrix."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import (
    axial_basis,
    branch_mass,
    fraction_string,
    parse,
    rational_interval,
)
from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_polar_polar_L4_matrix import polar_basis
from bridge.einstein_sector.nonaxisymmetric_pbw_projector import axisymmetric_conversion, canonical, reduced_source


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L3_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L3_matrix.schema.json"
SLICE = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_nonaxisymmetric_L3_q2_slice.json"
WORKLOAD = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_parity_workload.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target_mass(branch: str) -> sp.Expr:
    return {"q_minus": 12 - 2 * sp.sqrt(6), "p_extra": sp.Rational(34, 3), "q_plus": 12 + 2 * sp.sqrt(6)}[branch]


def adjoints(parity: str, branch: str, momentum: sp.Expr, frequency: sp.Expr) -> list[sp.Matrix]:
    eigenvalue = sp.Integer(12)
    if parity == "axial":
        if branch == "p_extra":
            return [sp.Matrix([-momentum**2-eigenvalue,momentum*frequency,eigenvalue,0]),sp.Matrix([-momentum*frequency,momentum**2-sp.Rational(2,3),0,eigenvalue])]
        mass = target_mass(branch)
        return [sp.Matrix([2*momentum,-2*frequency,momentum*(mass-eigenvalue),-frequency*(mass-eigenvalue)])]
    if branch == "p_extra":
        return [sp.Matrix([1,-(6*momentum**2+3*eigenvalue-2)/(6*momentum*frequency),1,0]),sp.Matrix([sp.Rational(4,3),-2*(momentum**2+eigenvalue)/(3*momentum*frequency),0,1])]
    mass = target_mass(branch)
    return [sp.Matrix([-2*(eigenvalue*momentum**2-mass*momentum**2-eigenvalue),2*momentum*frequency*(eigenvalue-mass),-2*(eigenvalue*momentum**2-mass*momentum**2+eigenvalue**2-eigenvalue*mass-eigenvalue),eigenvalue])]


def l4_calibration() -> None:
    cases = (
        ("axial", "axial", (1,0,0,0), (1,0,0,0), "einstein_maxwell_weyl_ell2_axial_axial_L4_q2_slice.json", "first_amplitudes_Ht_Hx_Qt_Qx", "second_amplitudes_Ht_Hx_Qt_Qx"),
        ("polar", "polar", (1,2,3,4), (5,6,7,8), "einstein_maxwell_weyl_ell2_polar_polar_L4_q2_slice.json", "first_amplitudes_At_B_Ct_U", "second_amplitudes_At_B_Ct_U"),
        ("axial", "polar", (1,2,3,4), (5,6,7,8), "einstein_maxwell_weyl_ell2_axial_polar_L4_q2_slice.json", "axial_amplitudes_Ht_Hx_Qt_Qx", "polar_amplitudes_At_B_Ct_U"),
    )
    for first_parity, second_parity, first, second, filename, first_key, second_key in cases:
        coupled = reduced_source(first_parity, second_parity, first, second, 1, 2, 3, 5, 4, 4, max_jet_order=0)
        value = json.loads((ROOT / "bridge/einstein_sector/generated" / filename).read_text())
        names = value["variables"] + value[first_key] + value[second_key]
        local = {name: sp.symbols(name, real=True) for name in names}
        substitutions = {local["k_1"]:1,local["omega_1"]:2,local["k_2"]:3,local["omega_2"]:5}
        substitutions.update({local[f"a_{index}"]: entry for index, entry in enumerate(first)})
        substitutions.update({local[f"b_{index}"]: entry for index, entry in enumerate(second)})
        stored = sp.Matrix([sp.sympify(entry, locals=local).subs(substitutions) for entry in value["source_action_rows"]])
        if (stored-axisymmetric_conversion(4)*coupled).applyfunc(canonical) != sp.zeros(4,1):
            raise AssertionError(f"nonaxisymmetric projector lost {first_parity}-{second_parity} L4 calibration")


def verify() -> None:
    value, schema = json.loads(CERT.read_text()), json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value["schema_sha256"] != sha(SCHEMA) or value["source_slice"]["sha256"] != sha(SLICE):
        raise AssertionError("L3 schema or source-slice provenance changed")
    for item in value["provenance"]["inputs"].values():
        if sha(ROOT/item["path"]) != item["sha256"]:
            raise AssertionError(f"stale L3 provenance: {item['path']}")
    l4_calibration()
    slice_value = json.loads(SLICE.read_text())
    variables = sp.symbols("k_1 omega_1 k_2 omega_2", real=True)
    first_symbols, second_symbols = sp.symbols("a_0:4", real=True), sp.symbols("b_0:4", real=True)
    local = {str(symbol):symbol for symbol in (*variables,*first_symbols,*second_symbols)}
    sources = {name:sp.Matrix([sp.sympify(entry,locals={"sqrt":sp.sqrt,**local}) for entry in entries]) for name,entries in slice_value["source_action_rows"].items()}
    workload = {row["candidate_index"]:row for row in json.loads(WORKLOAD.read_text())["source_workload"]["rows"] if row["output_ell"]==3}
    fixtures = coefficients = zeros = obstructed = 0
    for record in value["candidate_rows"]:
        row = workload[record["candidate_index"]]
        rho=parse(row["rho"]); signs=row["canonical_signed_momenta"]
        momenta=(signs[0]*sp.sqrt(rho),signs[1]*sp.sqrt(rho)); frequencies=(sp.sqrt(momenta[0]**2+branch_mass(row["first_branch"])),sp.sqrt(momenta[1]**2+branch_mass(row["second_branch"])))
        total_momentum,total_frequency=sum(momenta),sum(frequencies)
        if canonical(total_frequency**2-total_momentum**2-target_mass(row["target_branch"])) != 0:
            raise AssertionError("stored L3 row left shell")
        for channel_index, channel in enumerate(record["parity_channels"]):
            first_parity,second_parity=channel["first_parity"],channel["second_parity"]
            first_basis=(axial_basis if first_parity=="axial" else polar_basis)(row["first_branch"],momenta[0],frequencies[0])
            second_basis=(axial_basis if second_parity=="axial" else polar_basis)(row["second_branch"],momenta[1],frequencies[1])
            target=adjoints(channel["target_parity"],row["target_branch"],total_momentum,total_frequency)
            for fixture_index, fixture in enumerate(channel["basis_fixtures"]):
                fixtures+=1; stored_pairings=[parse(entry) for entry in fixture["pairings"]];coefficients+=len(stored_pairings)
                for pairing, interval in zip(stored_pairings,fixture["pairing_intervals"],strict=True):
                    if pairing==0: zeros+=1; assert interval is None
                    else:
                        assert interval is not None
                        bounds=rational_interval(pairing,int(interval["decimal_digits"]))
                        assert [fraction_string(bounds[0]),fraction_string(bounds[1])]==[interval["lower"],interval["upper"]]
                        assert bounds[0]>0 or bounds[1]<0
                obstructed += fixture["bounded_status"]=="OBSTRUCTED"
                # Replay one exact basis fixture in each of the four ordered
                # parity classes.  The exhaustive producer covers all six
                # circumference rows; keeping this independent rail to one
                # row makes it suitable for routine scoped verification.
                if record["candidate_index"]==1 and fixture_index==0:
                    first_vector=first_basis[fixture["first_basis_index"]];second_vector=second_basis[fixture["second_basis_index"]]
                    source=sources[f"{first_parity}_{second_parity}"].subs({variables[0]:momenta[0],variables[1]:frequencies[0],variables[2]:momenta[1],variables[3]:frequencies[1],**dict(zip(first_symbols,first_vector,strict=True)),**dict(zip(second_symbols,second_vector,strict=True))},simultaneous=True).applyfunc(canonical)
                    replay=[canonical((vector.T*source)[0]) for vector in target]
                    mismatches = [
                        (left, right)
                        for left, right in zip(replay, stored_pairings, strict=True)
                        if left != right
                        and sp.to_number_field(left - right).as_expr() != 0
                    ]
                    if mismatches:
                        raise AssertionError(f"exact L3 channel replay failed: {[sp.N(left-right, 20) for left, right in mismatches]}")
    summary=value["matrix_summary"]
    if (fixtures,coefficients,zeros,obstructed)!=(summary["ordered_input_basis_fixtures"],summary["target_adjoint_coefficients"],summary["zero_target_adjoint_coefficients"],summary["basis_fixtures_with_nonzero_cokernel_vector"]):
        raise AssertionError("L3 summary changed")


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_NONAXISYMMETRIC_L3_MATRIX independent verification: PASS")
