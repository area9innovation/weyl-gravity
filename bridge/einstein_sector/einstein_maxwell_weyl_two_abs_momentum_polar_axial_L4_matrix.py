"""Compute the ordered polar--axial L=4 cross-|n| source matrix."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import axial_basis, branch_mass, certified_nonzero_interval, fraction_string, parse, rational_interval, target_mass
from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_polar_L4_matrix import SLICE, generic_source, target_adjoints
from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_polar_polar_L4_matrix import polar_basis
from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_candidate4_pbw_probe import canonical


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_polar_axial_L4_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_polar_axial_L4_matrix.schema.json"
PARITY = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_parity_workload.json"
FORWARD_GENERATOR = ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_two_abs_momentum_axial_polar_L4_matrix.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute() -> dict[str, object]:
    if json.loads(SLICE.read_text())["result_id"] != "EINSTEIN_MAXWELL_WEYL_ELL2_AXIAL_POLAR_L4_Q2_SLICE":
        raise AssertionError("ordered cross-parity source slice changed")
    variables, axial_symbols, polar_symbols, source, counts = generic_source()
    if counts != {"axial_then_polar": 832, "polar_then_axial": 832}:
        raise AssertionError("generic slice lost graded-symmetric PBW support")
    rows = json.loads(PARITY.read_text())["source_workload"]["rows"]
    records = []
    coefficients = fixtures = zeros = obstructed = 0
    for row in rows:
        if row["output_ell"] != 4:
            continue
        rho = parse(row["rho"])
        signs = row["canonical_signed_momenta"]
        momenta = [signs[0] * sp.sqrt(rho), signs[1] * sp.sqrt(rho)]
        frequencies = [sp.sqrt(momenta[0] ** 2 + branch_mass(row["first_branch"])), sp.sqrt(momenta[1] ** 2 + branch_mass(row["second_branch"]))]
        K, Omega = sum(momenta), sum(frequencies)
        shell_defect = canonical(Omega**2 - K**2 - target_mass(row["target_branch"]))
        if shell_defect != 0:
            raise AssertionError(f"candidate {row['candidate_index']} left target shell")
        first_basis = polar_basis(row["first_branch"], momenta[0], frequencies[0])
        second_basis = axial_basis(row["second_branch"], momenta[1], frequencies[1])
        adjoints = target_adjoints(row["target_branch"], K, Omega)
        basis_records = []
        for first_index, first_vector in enumerate(first_basis):
            for second_index, second_vector in enumerate(second_basis):
                # The shared slice is parameterized by axial role first and polar
                # role second.  Reverse workload ordering therefore swaps the
                # branch/momentum substitutions, not the physical q2 arguments.
                specialized = source.subs({variables[0]: momenta[1], variables[1]: frequencies[1], variables[2]: momenta[0], variables[3]: frequencies[0], **dict(zip(axial_symbols, second_vector, strict=True)), **dict(zip(polar_symbols, first_vector, strict=True))}, simultaneous=True)
                pairings = [canonical((adjoint.T * specialized)[0]) for adjoint in adjoints]
                intervals = [certified_nonzero_interval(value) for value in pairings]
                nonzero = next((index for index, value in enumerate(intervals) if value is not None), None)
                status = "OBSTRUCTED" if nonzero is not None else "OPEN"
                coefficients += len(pairings); fixtures += 1; zeros += sum(value == 0 for value in pairings); obstructed += status == "OBSTRUCTED"
                basis_records.append({"first_basis_index": first_index, "second_basis_index": second_index, "pairings": [str(value) for value in pairings], "nonzero_component": nonzero, "pairing_intervals": [None if interval is None else {"lower": fraction_string(interval[0][0]), "upper": fraction_string(interval[0][1]), "decimal_digits": interval[1]} for interval in intervals], "bounded_status": status})
                print(f"candidate {row['candidate_index']} polar-axial basis ({first_index},{second_index}): {status}", flush=True)
        records.append({"candidate_index": row["candidate_index"], "first_branch": row["first_branch"], "second_branch": row["second_branch"], "target_branch": row["target_branch"], "rho": row["rho"], "signed_momenta": signs, "shell_defect": str(shell_defect), "target_cokernel_dimension": len(adjoints), "basis_fixtures": basis_records})
    if (coefficients, fixtures) != (27, 20):
        raise AssertionError(f"polar--axial L4 workload changed: {coefficients}/{fixtures}")
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-polar-axial-L4-matrix-v1", "schema_path": str(SCHEMA.relative_to(ROOT)), "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_POLAR_AXIAL_L4_MATRIX", "lifecycle_state": "CLASSIFIED", "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"], "generality_level": "G2_COMPLETE_ORDERED_POLAR_AXIAL_L4_BASIS_MATRIX",
        "scope": {"theory": "Weyl-Maxwell target", "background": "compact magnetically supported Plebanski-Hacyan product", "boundaries": "closed S1_L times S2 at twelve separately tuned algebraic circumference rows", "charge_sector": "fixed N=2 magnetic bundle", "carrier": "all ordered axisymmetric polar-first axial-second ell=2 branch-basis cross products between |n|=1 and |n|=2 resonating at L=4", "degree": 2, "parity": "polar then axial input; axial output", "ell": "2 times 2 -> 4", "m": "0+0 -> 0", "k": "row-specific signed compact momenta", "omega": "row-specific positive-frequency SUM channel"},
        "source_slice": {"path": str(SLICE.relative_to(ROOT)), "sha256": sha(SLICE), "role_substitution": "axial role receives the workload second branch/momentum; polar role receives the workload first branch/momentum"},
        "graded_symmetry_audit": {"axial_then_polar_PBW_terms": 832, "polar_then_axial_PBW_terms": 832, "both_orders_in_shared_slice": True, "reverse_matrix_obtained_by_explicit_role_substitution": True, "name_based_mode_identification_used": False},
        "candidate_rows": records,
        "matrix_summary": {"candidate_rows": len(records), "ordered_input_basis_fixtures": fixtures, "target_adjoint_coefficients": coefficients, "zero_target_adjoint_coefficients": zeros, "nonzero_target_adjoint_coefficients": coefficients - zeros, "basis_fixtures_with_nonzero_cokernel_vector": obstructed, "basis_fixtures_without_this_resonant_witness": fixtures - obstructed},
        "second_order_verdict": {"basis_fixture_statuses": "OBSTRUCTED_OR_OPEN_AS_LISTED", "smooth_secular_status": "OPEN", "causal_retarded_status": "NO_CERTIFIED_MAP"},
        "workload_progress": {"resolved_axisymmetric_L4_coefficients": 108, "remaining_axisymmetric_L4_coefficients": 0, "remaining_nonaxisymmetric_L1_L3_coefficients": 56, "complete_two_fibre_tangent_cone_classified": False},
        "classification": {"complete_ordered_polar_axial_L4_basis_matrix_classified": True, "all_twenty_basis_fixtures_bounded_obstructed": obstructed == fixtures, "all_axisymmetric_L4_basis_coefficients_classified": True, "arbitrary_cross_parity_linear_combinations_classified": False, "complete_two_fibre_tangent_cone_classified": False, "causal_or_quantum_claim": False},
        "claim_boundary": "This closes the final ordered 27-coefficient L4 basis matrix and hence all 108 axisymmetric L4 basis coefficients. It does not classify cancellations among arbitrary amplitudes, the 56 nonaxisymmetric L1/L3 coefficients, smooth-secular or causal corrections, the complete tangent cone, residual observables or quantum states.",
        "provenance": {"generator_path": str(Path(__file__).relative_to(ROOT)), "generator_sha256": sha(Path(__file__)), "inputs": {"parity_workload": {"path": str(PARITY.relative_to(ROOT)), "sha256": sha(PARITY)}, "shared_cross_parity_generator": {"path": str(FORWARD_GENERATOR.relative_to(ROOT)), "sha256": sha(FORWARD_GENERATOR)}, "shared_source_slice": {"path": str(SLICE.relative_to(ROOT)), "sha256": sha(SLICE)}}},
        "verification_commands": ["python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_polar_axial_L4_matrix --check", "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_two_abs_momentum_polar_axial_L4_matrix.py", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_two_abs_momentum_polar_axial_L4_matrix", "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_polar_axial_L4_matrix --recompute-exhaustive"]
    }


def fast_check() -> None:
    value = json.loads(OUTPUT.read_text())
    if value["provenance"]["generator_sha256"] != sha(Path(__file__)): raise AssertionError("polar--axial generator hash changed")
    for item in value["provenance"]["inputs"].values():
        if sha(ROOT / item["path"]) != item["sha256"]: raise AssertionError(f"stale input {item['path']}")
    fixtures = coefficients = zeros = obstructed = 0
    for row in value["candidate_rows"]:
        if row["shell_defect"] != "0": raise AssertionError("stored row left shell")
        for fixture in row["basis_fixtures"]:
            fixtures += 1; pairings = [parse(item) for item in fixture["pairings"]]; coefficients += len(pairings)
            for pairing, stored in zip(pairings, fixture["pairing_intervals"], strict=True):
                if pairing == 0: zeros += 1; assert stored is None
                else:
                    assert stored is not None; interval = rational_interval(pairing, int(stored["decimal_digits"])); assert [fraction_string(x) for x in interval] == [stored["lower"], stored["upper"]]; assert interval[0] > 0 or interval[1] < 0
            obstructed += fixture["bounded_status"] == "OBSTRUCTED"
    summary = value["matrix_summary"]
    if (fixtures, coefficients, zeros, obstructed) != (summary["ordered_input_basis_fixtures"], summary["target_adjoint_coefficients"], summary["zero_target_adjoint_coefficients"], summary["basis_fixtures_with_nonzero_cokernel_vector"]): raise AssertionError("stored summary changed")


def main() -> None:
    parser = argparse.ArgumentParser(); group = parser.add_mutually_exclusive_group(required=True); group.add_argument("--write", action="store_true"); group.add_argument("--check", action="store_true"); group.add_argument("--recompute-exhaustive", action="store_true"); args = parser.parse_args()
    if args.write: OUTPUT.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    elif args.check: fast_check()
    elif json.loads(OUTPUT.read_text()) != compute(): raise AssertionError("stale exhaustive polar--axial certificate")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_POLAR_AXIAL_L4_MATRIX: PASS")


if __name__ == "__main__": main()
