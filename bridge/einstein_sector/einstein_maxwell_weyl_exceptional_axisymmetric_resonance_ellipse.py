"""Solve the axisymmetric exceptional L1/L2 resonance equations exactly."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_axisymmetric_resonance_ellipse.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_axisymmetric_resonance_ellipse.schema.json"
INPUTS = {
    "difference": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_ell2_extra_difference_matrix.json",
    "exceptional_self": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_two_polarization_resonance.json",
    "d_control": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_ell2_extra_resonance_completion.json",
    "exceptional_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
    "ell2_extra_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_twist_ell2_extra_compatibility_face.json",
    "global_moments": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    assert records["difference"]["classification"]["unique_ell2_polar_e2_control_amplitude"]
    assert records["d_control"]["classification"]["d_cross_adjoint_map_invertible_in_both_parities"]
    assert records["exceptional_current"]["current_theorem"]["normalized_extra_Hermitian_current_Gram"] == [["16", "0"], ["0", "3"]]
    assert records["ell2_extra_current"]["extra_current_gram_at_ell2_k0"]["diagonal"] == ["1296", "208/3", "22464", "12288"]
    assert records["global_moments"]["classification"]["standard_homogeneous_common_zero_locus_classified"]

    rx, rp, d, phase = sp.symbols("r_x r_p d s", nonzero=True)
    root = sp.sqrt(3)
    x = rx * phase
    polar = sp.I * rp * phase
    y2 = 5 * root * sp.I * d * phase**2 / 864
    y1 = sp.I * phase**2 * (sp.Rational(2, 3) * rx**2 + sp.Rational(1, 8) * rp**2) / (6 * root * d)
    xbar = rx / phase
    pbar = -sp.I * rp / phase
    equations = {
        "L1_axial": sp.factor(8 * root * sp.I * d * x / 9 - sp.Rational(768, 5) * xbar * y2),
        "L1_polar": sp.factor(-root * sp.I * d * polar - sp.Rational(864, 5) * pbar * y2),
        "L2_polar_first": sp.factor(-sp.Rational(2, 3) * x**2 + sp.Rational(1, 8) * polar**2 - 6 * root * sp.I * d * y1),
        "L2_polar_second": sp.factor(sp.Rational(4, 3) * x**2 - sp.Rational(1, 4) * polar**2 + 552 * root * sp.I * d * y2),
    }
    assert equations["L1_axial"] == 0
    assert equations["L1_polar"] == 0
    assert equations["L2_polar_first"] == 0
    ellipse_residual = sp.factor(equations["L2_polar_second"] / phase**2)
    assert sp.simplify(ellipse_residual - (16 * rx**2 + 3 * rp**2 - 115 * d**2) / 12) == 0

    return {
        "schema": "einstein-maxwell-weyl-exceptional-axisymmetric-resonance-ellipse-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_AXISYMMETRIC_RESONANCE_ELLIPSE",
        "result_state": "AXISYMMETRIC_EXCEPTIONAL_L1_L2_RESONANCE_COMPATIBILITY_ELLIPSE_SOLVED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded resonance compatibility only",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "axisymmetric exceptional axial/polar dipoles, circumference velocity d, and ell2 extra control amplitudes",
            "degree": 2,
            "parity": "both exceptional parities with polar and axial ell2 controls",
            "ell": "exceptional input 1; control input 2; resonant outputs L=1,2",
            "m": 0,
            "k": 0,
            "omega": "omega_exceptional and 2*omega_exceptional"
        },
        "parameterization": {
            "phase": "s in U(1)",
            "exceptional_axial": "x=r_x*s",
            "exceptional_polar": "p=i*r_p*s",
            "ell2_polar_e2": "y2=(5*sqrt(3)*i/864)*d*s^2",
            "ell2_polar_e1": "y1=i*s^2*((2/3)*r_x^2+(1/8)*r_p^2)/(6*sqrt(3)*d)",
            "ellipse": "16*r_x^2+3*r_p^2=115*d^2",
            "domain": "r_x,r_p>=0, d!=0, not both r_x,r_p zero"
        },
        "resonance_equations": {
            "L1_axial": "(8*sqrt(3)*i/9)*d*x-(768/5)*conj(x)*y2=0",
            "L1_polar": "-sqrt(3)*i*d*p-(864/5)*conj(p)*y2=0",
            "L2_polar_first": "-(2/3)*x^2+(1/8)*p^2-6*sqrt(3)*i*d*y1=0",
            "L2_polar_second": "(4/3)*x^2-(1/4)*p^2+552*sqrt(3)*i*d*y2=0",
            "L2_axial_cross": "the exceptional axial-polar defect is uniquely removable by ell2 axial controls because the d pairing is invertible"
        },
        "moment_map_audit": {
            "P_x": "0 on the k=0 axisymmetric carrier",
            "J_i": "0 for m=0",
            "H": "strictly negative for every nonzero displayed resonance-compatible point because every exceptional and ell2 control amplitude lies in a positive-current extra block and d carries no compensating positive oscillator occupation",
            "consequence": "no displayed point is in the five-moment-map zero cone without adjoining an opposite-sign standard Einstein occupation"
        },
        "classification": {
            "axisymmetric_L1_L2_resonance_zero_locus_nonempty": True,
            "explicit_resonance_ellipse_parameterized": True,
            "pure_axial_and_pure_polar_endpoints_included": True,
            "four_spatial_stabilizer_moment_maps_zero": True,
            "Hamiltonian_moment_map_zero": False,
            "Einstein_minus_balance_required": True,
            "complete_second_order_source_solved": False,
            "SO3_all_m_tensor_assembled": False,
            "causal_or_quantum_claim": False
        },
        "interpretation": "The exceptional defect is not algebraically absolute once circumference velocity and ell2 extra controls are admitted: its L1/L2 resonances have an exact nonzero ellipse. The ellipse still misses the tangent cone because its Hamiltonian moment map is strictly negative. A standard Einstein-minus occupation can balance that charge, but its mixed quadratic sources must be computed before any bounded extension is claimed.",
        "next_gate": "adjoin the minimal axisymmetric Einstein-minus occupation that cancels mu_H and compute every new Einstein-minus cross source against the exceptional and ell2 control amplitudes",
        "claim_boundary": "This is an axisymmetric resonance-compatibility theorem, not a complete bounded second-order extension. It does not solve the nonresonant source, the Hamiltonian-balanced enlargement, all m, nonzero momentum, causal propagation, residual descent, particles or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()}
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("exceptional resonance ellipse certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_AXISYMMETRIC_RESONANCE_ELLIPSE: PASS")


if __name__ == "__main__":
    main()
