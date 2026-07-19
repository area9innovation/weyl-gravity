"""Lift all 24 same-sign scalar extreme rays into the bounded tangent cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_extreme_ray_lifts.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_extreme_ray_lifts.schema.json"
INPUTS = {
    "scalar_rays": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_extreme_rays.json",
    "bounded_witnesses": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_collision_bounded_witnesses.json",
    "same_fibre": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_collision_same_fibre_census.json",
    "isolated": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json",
    "finite_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json",
    "candidate19": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_regular_pencil_L4_zero_varieties.json",
    "candidate21": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L4_zero_varieties.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decomposition(record: dict, index: int) -> dict:
    value = record["decompositions"]
    rows = value if isinstance(value, list) else [item for item in value.values() if isinstance(item, dict)]
    return next(row for row in rows if row.get("candidate_index") == index)


def node_id(branch: str, n: int) -> str:
    return f"{branch}_n{n}"


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    rays = records["scalar_rays"]["extreme_rays"]
    if [ray["ray_id"] for ray in rays] != ["R1", "R2", "R3", "R4"]:
        raise AssertionError("scalar extreme-ray dictionary changed")
    if not records["same_fibre"]["classification"]["all_864_target_shell_defects_nonzero"]:
        raise AssertionError("same-fibre gate changed")
    if not records["finite_cone"]["classification"]["complete_reduced_adjoint_cokernel_decomposition_certified"]:
        raise AssertionError("finite-cone sufficiency changed")
    isolated = records["isolated"]["candidate_ledger"]["rows"]
    c19 = decomposition(records["candidate19"], 19)
    c21 = decomposition(records["candidate21"], 21)
    mixed19 = [item for item in c19["zero_variety"]["irreducible_components_over_C"] if item["component_id"].startswith("mixed_eigenline_")]
    mixed21 = [item for item in c21["irreducible_components_over_C"] if item["component_id"] == "mixed_plus"]
    if len(mixed19) != 4 or not c19["zero_variety"]["all_mixed_components_real_supported"]:
        raise AssertionError("candidate-19 real pencil components changed")
    if len(mixed21) != 1 or not c21["r_squared_interval"]["positive"]:
        raise AssertionError("candidate-21 real mixed component changed")

    rows = []
    counts = {"RESONANT_FACTOR_ABSENT": 0, "AXISYMMETRIC_ODD_L_ZERO": 0, "REAL_REGULAR_PENCIL_L4_COMPONENT": 0, "REAL_SCALAR_MIXED_PARITY_L4_COMPONENT": 0}
    for candidate_index in range(16, 22):
        resonance = isolated[candidate_index - 1]
        first = node_id(resonance["first_branch"], 1)
        second = node_id(resonance["second_branch"], 2)
        output_ell = resonance["output_ell"]
        for ray in rays:
            support = set(ray["support"])
            if first not in support or second not in support:
                disposition = {"method": "RESONANT_FACTOR_ABSENT", "missing_nodes": [node for node in (first, second) if node not in support]}
            elif output_ell in (1, 3):
                if clebsch_gordan(2, 2, output_ell, 0, 0, 0) != 0:
                    raise AssertionError("odd-L axisymmetric zero changed")
                disposition = {"method": "AXISYMMETRIC_ODD_L_ZERO", "clebsch_gordan": f"<2,0;2,0|{output_ell},0>=0"}
            elif candidate_index == 19:
                disposition = {"method": "REAL_REGULAR_PENCIL_L4_COMPONENT", "component_id": mixed19[0]["component_id"], "independent_scaling": "the two nonzero fibre vectors may be scaled independently to the extreme-ray occupations"}
            elif candidate_index == 21:
                disposition = {"method": "REAL_SCALAR_MIXED_PARITY_L4_COMPONENT", "component_id": "mixed_plus", "r": mixed21[0]["r"], "s": mixed21[0]["s"], "independent_scaling": "the two nonzero parity vectors may be scaled independently to the extreme-ray occupations"}
            else:
                raise AssertionError("unhandled even-L extreme-ray lift")
            counts[disposition["method"]] += 1
            rows.append({
                "candidate_index": candidate_index,
                "ray_id": ray["ray_id"],
                "support": ray["support"],
                "angular_choice": "m=0 on every occupied node",
                "rotation_moment_maps": "mu_J1=mu_J2=mu_J3=0",
                "scalar_receiver": "mu_H=mu_Px=R_c=0 by the universal extreme-ray formula",
                "cross_fibre_disposition": disposition,
                "same_fibre_disposition": "all nonzero-frequency channels off shell",
                "bounded_verdict": "EXTREME_RAY_LIFTS_TO_NONZERO_Z2_BOUNDED_POINT",
            })
    if counts != {"RESONANT_FACTOR_ABSENT": 10, "AXISYMMETRIC_ODD_L_ZERO": 10, "REAL_REGULAR_PENCIL_L4_COMPONENT": 2, "REAL_SCALAR_MIXED_PARITY_L4_COMPONENT": 2}:
        raise AssertionError(f"extreme-ray disposition count changed: {counts}")
    return {
        "schema": "einstein-maxwell-weyl-same-sign-extreme-ray-lifts-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_EXTREME_RAY_LIFTS",
        "result_state": "ALL_24_SCALAR_EXTREME_RAYS_LIFT_TO_BOUNDED_SECOND_ORDER_POINTS",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_ALL_24_CANDIDATEWISE_SCALAR_EXTREME_RAY_LIFTS",
        "scope": {
            **records["scalar_rays"]["scope"],
            "background": "six distinct collision candidates 16--21, retained separately",
            "carrier": "one axisymmetric real amplitude lift for each of four scalar extreme-ray supports per candidate",
        },
        "lift_rows": rows,
        "summary": {"candidate_count": 6, "rays_per_candidate": 4, "total_lifts": 24, "disposition_counts": counts},
        "classification": {
            "all_24_scalar_extreme_rays_have_nonzero_bounded_lifts": True,
            "all_rotation_moment_maps_zero_on_lifts": True,
            "all_cross_fibre_resonances_zero_on_lifts": True,
            "all_same_fibre_nonzero_frequency_channels_removable": True,
            "arbitrary_nonnegative_sums_of_lifts_classified": False,
            "six_full_real_bounded_cones_classified": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The bounded cone projects onto every extreme ray of its scalar occupation cone on each same-sign background. The remaining geometry is phase-sensitive: a sum of ray lifts can reactivate the bilinear resonance even though each ray separately survives.",
        "next_gate": "classify pairwise sums of the four lifted ray strata candidate by candidate, retaining phases and parity vectors",
        "claim_boundary": "This is a ray-saturation theorem, not a proof that every scalar-null occupation has a bounded amplitude lift or a classification of arbitrary sums, exceptional/global inputs, all-orders solutions or higher lifecycles.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_extreme_ray_lifts --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_extreme_ray_lifts",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_extreme_ray_lifts",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
    elif not OUTPUT.exists() or OUTPUT.read_text() != rendered:
        raise AssertionError("same-sign extreme-ray lift certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_EXTREME_RAY_LIFTS: PASS")


if __name__ == "__main__":
    main()
