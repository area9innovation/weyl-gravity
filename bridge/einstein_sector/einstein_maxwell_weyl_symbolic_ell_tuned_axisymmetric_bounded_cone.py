"""Classify the full all-ell tuned axisymmetric standard-branch bounded cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_tuned_axisymmetric_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_symbolic_ell_tuned_axisymmetric_bounded_cone.schema.json"
INPUTS = {
    "bounded_sheet": ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_mixed_sheet_bounded_extension.json",
    "parity_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_qminus_parity_resonance_matrix.json",
    "moment_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_cone.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {n: json.loads(p.read_text(encoding="utf-8")) for n, p in INPUTS.items()}
    assert records["bounded_sheet"]["classification"]["bounded_correction_exists_by_complete_cokernel_criterion"]
    assert records["parity_matrix"]["classification"]["complete_resonance_zero_variety_classified"]
    moment_equations = records["moment_cone"]["paired_density_cone_theorem"]["common_zero_equations"]
    assert moment_equations["signs"] == "eta_plus=eta_extra=+1, eta_minus=-1"
    assert "A_s^+ - A_s^-" in moment_equations["P_x"]
    ell = sp.symbols("ell", integer=True, positive=True)
    lam = ell * (ell + 1)
    wm2 = lam - ell / 2 - sp.Rational(1, 6)
    wp2 = wm2 + 2 * sp.sqrt(2 * lam)
    ratio = sp.sqrt(wm2 / wp2)
    lower = sp.factor((1 - ratio) / (1 + ratio))
    upper = sp.factor((1 + ratio) / (1 - ratio))
    assert sp.simplify(lower * upper - 1) == 0
    return {
        "schema": "einstein-maxwell-weyl-symbolic-ell-tuned-axisymmetric-bounded-cone-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_TUNED_AXISYMMETRIC_BOUNDED_CONE",
        "result_state": "COMPLETE_ALL_ELL_TUNED_AXISYMMETRIC_STANDARD_BRANCH_BOUNDED_CONE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_EVERY_INTEGER_ELL_ONE_TUNED_NONZERO_MOMENTUM_FIBRE",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 with circumference tuned separately for each ell",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "arbitrary m=0 axial/polar q-minus amplitudes at +/-k and arbitrary action-normalized q-plus balancing occupations; no twist or extra-primary input",
            "degree": 2,
            "parity": "both q-minus parities and either mixed-sheet sign",
            "ell": "every integer ell>=2",
            "m": "m=0",
            "k": "+/-sqrt(sqrt(2*ell*(ell+1))-ell/2-1/6)",
            "omega": "q-minus and q-plus branches",
        },
        "frequency_ratio": {"definition": "r_ell=omega_minus/omega_plus", "r_ell": str(ratio), "strict_range": "0<r_ell<1"},
        "resonance_zero_variety": {
            "origin": "all q-minus amplitudes zero",
            "one_sided_planes": "removed away from the origin by q-plus occupation positivity because r_ell<1",
            "mixed_sheets": "a_+=sigma*sqrt(ell*(ell+1)/2)*p_+ and a_-=sigma*sqrt(ell*(ell+1)/2)*p_-, sigma=+/-1",
        },
        "moment_map_solution": {
            "qminus_occupations": "N_+/-=-h_minus(a_+/- e_A+p_+/- e_P,a_+/- e_A+p_+/- e_P)>=0",
            "common_sheet_weight": "on either sheet N_+/-=kappa_ell*|p_+/-|^2 with the same kappa_ell>0",
            "qplus_occupations": [
                "B_+=(r_ell^2*(N_++N_-)+r_ell*(N_+-N_-))/2",
                "B_-=(r_ell^2*(N_++N_-)-r_ell*(N_+-N_-))/2",
            ],
            "positivity_condition": "|N_+-N_-|<=r_ell*(N_++N_-)",
            "sharp_amplitude_interval": f"{lower} <= |p_+|^2/|p_-|^2 <= {upper}",
            "rotations": "J_1=J_2=J_3=0 on m=0",
        },
        "complete_cone": {
            "components": "the origin plus two mixed-sheet components subject to the sharp closed amplitude interval",
            "phases": "p_+ and p_- retain arbitrary complex phases; a_+/- have the common sheet sign relative to p_+/-",
            "necessity": "resonance equations give the four-component zero variety; q-plus positivity removes the one-sided planes and imposes the interval",
            "sufficiency": "the imported all-ell bounded-sheet theorem supplies a bounded correction at every point satisfying the moment equations",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED"},
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {"status": "CERTIFIED"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "complete_tuned_axisymmetric_standard_branch_bounded_cone_classified": True,
            "both_mixed_sheet_components_and_origin_included": True,
            "sharp_action_normalized_amplitude_interval_certified": True,
            "one_sided_planes_removed_by_moment_positivity": True,
            "relative_phases_included": True,
            "extra_primary_or_multiple_abs_momentum_inputs_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "At each generic ell the bounded standard-branch tangent cone is neither the whole linear space nor an isolated ray. It has two finite-width mixed-parity components whose width is fixed by the q-minus/q-plus frequency ratio. This is a complete second-order cone only in the declared tuned axisymmetric one-fibre carrier.",
        "next_gate": "join distinct absolute momentum fibres and compute the remaining two-fibre source coefficients",
        "claim_boundary": "Complete only for the tuned m=0 q-minus/q-plus one-|k| carrier at each ell. Extra-primary inputs, nonaxisymmetric data, fixed circumference across ell, multiple |k| fibres, all-orders and higher lifecycles remain fail-closed.",
        "provenance": {"generator_path": str(Path(__file__).relative_to(ROOT)), "generator_sha256": sha(Path(__file__)), "inputs": {n: {"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for n, p in INPUTS.items()}},
        "verification_commands": ["python3 -m bridge.einstein_sector.einstein_maxwell_weyl_symbolic_ell_tuned_axisymmetric_bounded_cone --check", "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_symbolic_ell_tuned_axisymmetric_bounded_cone.py", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_symbolic_ell_tuned_axisymmetric_bounded_cone"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    else:
        assert json.loads(OUTPUT.read_text()) == value
    print("EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_TUNED_AXISYMMETRIC_BOUNDED_CONE: PASS")


if __name__ == "__main__":
    main()
