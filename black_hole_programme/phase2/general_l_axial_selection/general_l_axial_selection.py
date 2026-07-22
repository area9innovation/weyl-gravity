"""Certify the first exact obstruction to generic-ell axial Einstein selection.

The inherited ell=2 composed-lift fixture drops the derivative of the
curvature source when differentiating H0'.  The corrected generic-ell
rate-zero lift is an additional formal curvature mode with finite Lee--Wald
radial pairing, so it is a counterexample to the proposed selection theorem.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from current_probe import pair_table
from derive_selection import I, L, M, W, corrected_x0_lift

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"

import sys
sys.path.insert(0, str(ROOT / "black_hole_programme/phase2/general_l_axial_current"))
from general_l_axial_current import LAMBDA as CUR_L, literal_unsummed_current

INPUTS = {
    "generic_axial_asymptotics": ROOT / "black_hole_programme/phase2/general_l_axial_asymptotics/certificate.json",
    "generic_axial_current": ROOT / "black_hole_programme/phase2/general_l_axial_current/certificate.json",
    "legacy_fixture_certificate": ROOT / "black_hole_programme/certificates/BH2C_FLUX_CLASS.json",
    "legacy_fixture_source": ROOT / "black_hole_programme/bh2c_flux_class.py",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def build_certificate():
    ell = sp.Symbol("ell", integer=True, positive=True)
    alpha = sp.Symbol("alpha")
    lift = corrected_x0_lift(2)
    if lift["H0_log_obstruction"] != 0:
        raise RuntimeError("corrected X0 lift acquired a logarithmic obstruction")
    h0 = [sp.sympify(lift["H0"].get(n, 0)).subs(L, CUR_L)
          for n in range(max(lift["H0"]) + 1)]
    x0 = (sp.Integer(0), ((sp.Integer(2), h0),
                          (sp.Integer(-1), [value.subs(L, CUR_L) for value in lift["H1"]])))
    e0 = (sp.Integer(0), ((sp.Integer(1), [-I * W / 2, (CUR_L - 2) / 4, M]),
                          (sp.Integer(0), [sp.Rational(1, 2)])))
    current, names = literal_unsummed_current()
    ex = pair_table(current, names, e0, x0, ell, -2)
    xx_dangerous = pair_table(current, names, x0, x0, ell, -1)
    expected_ex = (-8 * I * sp.pi * names["alpha"] * CUR_L
                   * (CUR_L**2 - 2 * CUR_L - 6 * I * W)
                   / (W * (CUR_L - 2) * (2 * ell + 1)))
    if set(ex) != {-2} or sp.simplify(ex[-2] - expected_ex) != 0:
        raise RuntimeError(f"corrected E0|X0 coefficient changed: {ex}")
    if xx_dangerous:
        raise RuntimeError(f"corrected X0|X0 acquired a divergent coefficient: {xx_dangerous}")
    source_manifest = {str(path.relative_to(ROOT.parent.parent)): git_blob(path)
                       for path in INPUTS.values()}
    content_manifest = {str(path.relative_to(ROOT.parent.parent)): sha256(path)
                        for path in INPUTS.values()}
    return {
        "schema": "phase2-black-hole-general-l-axial-selection-counterexample-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "result_id": "PURE_WEYL_PHASE2_GENERAL_L_AXIAL_SELECTION_COUNTEREXAMPLE",
        "result_token": "BH_PHASE2_GENERIC_L_AXIAL_SELECTION_OBSTRUCTED_BY_CORRECTED_X0",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "declaration": {
            "background": "Schwarzschild M>0 in ingoing EF coordinates; current coefficient displayed in M=1 units with omega understood as M*omega",
            "domain": "integer ell>=2, Lambda=ell(ell+1), real omega!=0",
            "radial_class": "formal polyhomogeneous 1/r series; no convergence claim",
            "sector": "axial rate-zero top curvature carrier P=1+O(r^-1), Q=O(r^-2)",
        },
        "exact_metric_forcing": {
            "c": "[r^2(P'+Q'+i*omega*Q)+2r(P+Q-Q')-2Q]/(Lambda-2)",
            "H0_prime_source": "2*c",
            "F_prime_source": "2*r*(c'-Q)/(r-2*M), F=H1'",
            "scalar_master_source": "2*(r^2*c''-r^2*Q'-2*r*Q+2*r*c'-2*c)",
            "scalar_operator": "(r^2-2Mr)F''+(2i*omega*r^2+2r+2M)F'+(6i*omega*r-Lambda)F",
        },
        "corrected_X0": {
            "carrier_nonzero": True,
            "not_einstein_or_gauge_reason": "delta Ric[h]=psi has P-leading coefficient 1; Einstein-image and diffeomorphism modes have delta Ric=0 on Ricci-flat Schwarzschild, while an axisymmetric conformal scalar has no axial phi component",
            "H0": "2*r^2/(Lambda-2)+(Lambda^2-2*Lambda-4*i*M*omega)/(4*omega^2*(Lambda-2))+O(r^-1)",
            "H1": "-i*(Lambda^2-2*Lambda+4*i*M*omega)/(2*omega^3*(Lambda-2))*r^-1+O(r^-3)",
            "F_resonance_obstruction": "0",
            "H0_log_obstruction": "0",
            "all_order_pivots": "carrier: -4*n*(n-1)*omega^2 then nonzero n>=2; metric F: 2*i*omega*(1-n), nonzero n>=2 after compatible n=1",
            "Einstein_lift_freedom": "the free F~r^-3 coefficient and H1 integration constant are set to zero; adding them is X0->X0+beta*E0",
        },
        "literal_current": {
            "E0|X0": {"leading_power": -2, "log_power": 0,
                        "coefficient": str(sp.factor(ex[-2])), "finite": True},
            "X0|X0": {"coefficients_at_p_ge_minus_1": {}, "finite": True,
                        "reading": "all potentially divergent coefficients vanish exactly"},
            "tail_filtration": "literal F^v has maximal rate-zero shifts h0h0:-3, h0h1:-2, h1h1:-1 and radial derivative order 3. With H0=C2*r^2+C0+O(r^-1), H1=O(r^-1), only p=1 and p=-1 can threaten X0|X0. At p=-1 the r^2 x C0 h0h0 and r^2 x r^-1 h0h1 contributions jointly cancel; all p>=-1 coefficients reduce exactly to zero. After retaining the r^-1 lift jet, every omitted tail contributes p<=-2.",
            "shift_invariance": "adding beta*E0 changes X0|X0 only by finite E0|X0 and E0|E0 terms and cannot create a p>=-1 coefficient",
        },
        "legacy_fixture_obstruction": {
            "dropped_term": "2*r*c'(r)/(r-2*M)",
            "mechanism": "bh2c_flux_class.py replaces c(r) by XSRC before differentiating H0', so diff(XSRC,r)=0",
            "original_row_residual": "delta Ric_{r phi}[h_legacy]-q*S_ell = c'(r)*S_ell",
            "X0_residual_head": "2*S_ell/(Lambda-2)+O(r^-2)",
            "ell2_control": "Lambda=6 gives residual S_2/2+O(r^-2), nonzero",
            "consequence": "the inherited log tail and divergent X0 table are not certificates for delta Ric[h]=psi",
        },
        "exceptional_set": {
            "poles": ["Lambda=2 (ell=1, outside declared domain)", "omega=0 (excluded)"],
            "zeros": ["E0|X0 bracket has real part Lambda*(Lambda-2) and imaginary part -6*omega, hence no zero for ell>=2, real omega!=0 and alpha!=0; the overall factor 8 is nonzero"],
            "declared_domain_exception_free": True,
        },
        "disposition": {
            "headline_selection_theorem": "OBSTRUCTED_BY_COUNTEREXAMPLE",
            "reason": "a non-Einstein rate-zero axial curvature carrier has a corrected formal metric lift with finite radial Lee-Wald pairing",
            "X2": "unclassified after the first exact counterexample stop condition fired",
        },
        "source_manifest": source_manifest,
        "content_sha256_manifest": content_manifest,
        "claim_flags": {
            "generic_l_axial_einstein_selection_certified": False,
            "first_exact_counterexample_certified": True,
            "legacy_fixture_defect_certified": True,
            "polar_certified": False,
            "asymptotic_phase_space_constructed": False,
        },
        "does_not_establish": [
            "convergence of the formal mode, horizon extendibility, a global scattering state or phase space",
            "the oscillatory X2 disposition, polar parity, omega=0, QNMs, stability, particles or quantum positivity",
        ],
        "verification": {
            "producer": "python3 black_hole_programme/phase2/general_l_axial_selection/general_l_axial_selection.py --check",
            "independent": "python3 black_hole_programme/phase2/general_l_axial_selection/verify_general_l_axial_selection.py",
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=CERTIFICATE)
    args = parser.parse_args()
    encoded = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.out.exists() or args.out.read_text() != encoded:
            raise SystemExit("certificate drift")
        print("PASS certificate reproduces byte-for-byte")
    else:
        args.out.write_text(encoded)
        print("wrote", args.out)


if __name__ == "__main__":
    main()
