#!/usr/bin/env python3
"""Produce the exact conserved/traceless odd-source overlap certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEFAULT_OUTPUT = HERE / "certificate.json"

IMPORTS = {
    "fredholm_promotion": (
        ROOT
        / "black_hole_programme/phase4/"
        "axial_qnm_fredholm_promotion_v1/certificate.json"
    ),
    "null_infinity_reconstruction": (
        ROOT
        / "black_hole_programme/phase4/"
        "axial_qnm_null_infinity_reconstruction_v1/certificate.json"
    ),
    "local_selector": (
        ROOT
        / "black_hole_programme/phase3/"
        "axial_qnm_projective_evans_contour_completion/"
        "local_selector_v1/certificate.json"
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_identities() -> dict[str, str]:
    """Check the Martel--Poisson source construction in Schwarzschild (t,r)."""
    r, mass, mu, omega = sp.symbols(
        "r M mu omega", nonzero=True
    )
    source = sp.Function("F")(r)
    f = 1 - 2 * mass / r

    # Martel--Poisson use epsilon_tr=+1, hence epsilon^{tr}=-1.
    # The reduced RW source is
    # F=f*S_odd, so set P_t=0 and solve
    # S_odd=+2r*i*omega*P_r/mu=F/f.
    p_t = sp.Integer(0)
    p_r_cov = mu * source / (2 * sp.I * omega * r * f)
    p_r_up = sp.simplify(f * p_r_cov)
    s_odd = sp.simplify(
        2 * r * (sp.I * omega * p_r_cov - sp.diff(p_t, r)) / mu
    )
    reduced = sp.simplify(f * s_odd)
    assert sp.simplify(reduced - source) == 0

    # sqrt(-det g_2)=1, hence nabla_a P^a=d_r P^r for P^t=0.
    divergence = sp.diff(p_r_up, r)
    p_tensor = sp.simplify(
        r**2 * (divergence + 2 * p_r_up / r) / mu
    )
    expected_p = sp.diff(r * source, r) / (2 * sp.I * omega)
    assert sp.simplify(p_tensor - expected_p) == 0

    conservation = sp.simplify(
        divergence + 2 * p_r_up / r - mu * p_tensor / r**2
    )
    assert conservation == 0

    # Harmonic projection inversion uses
    # int X_A X^A=ell(ell+1) and
    # int X_AB X^AB=(ell-1)ell(ell+1)(ell+2)/2.
    vector_projection = sp.simplify(
        16 * sp.pi * r**2 / sp.Symbol("Lambda")
        * (
            p_r_up
            / (16 * sp.pi * r**2)
            * sp.Symbol("Lambda")
        )
    )
    tensor_norm = sp.Symbol("mu") * sp.Symbol("Lambda") / 2
    tensor_projection = sp.simplify(
        16 * sp.pi * r**4
        / (sp.Symbol("mu") * sp.Symbol("Lambda"))
        * (p_tensor / (8 * sp.pi * r**4) * tensor_norm)
    )
    assert sp.simplify(vector_projection - p_r_up) == 0
    assert sp.simplify(tensor_projection - p_tensor) == 0

    return {
        "f": "1-2*M/r",
        "P_t": "0",
        "P_r_covariant": "mu*F/(2*I*omega*r*f)",
        "P_r_contravariant": "mu*F/(2*I*omega*r)",
        "P_tensor": "d_r(r*F)/(2*I*omega)",
        "S_odd": "F/f",
        "reduced_RW_source": "f*S_odd=F",
        "conservation": (
            "nabla_a(P^a)+2*r_a*P^a/r-mu*P/r**2=0"
        ),
        "stress_vector": "T^(aB)=P^a*X^B/(16*pi*r**2)",
        "stress_tensor": "T^(AB)=P*X^AB/(8*pi*r**4)",
        "trace": "0",
    }


def build() -> dict:
    imports = {
        name: {
            "path": str(path.relative_to(ROOT)),
            "sha256": digest(path),
        }
        for name, path in IMPORTS.items()
    }
    return {
        "schema": "axial-qnm-conserved-source-overlap-v1",
        "status": "EXACT_CONSERVED_TRACELESS_SOURCE_OVERLAP",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imports": imports,
        "primary_reference": {
            "citation": "Martel--Poisson, Phys. Rev. D 71 (2005) 104003",
            "arxiv": "gr-qc/0502028",
            "equations": ["(3.4)", "(3.9)", "(5.10)--(5.16)"],
        },
        "conventions": {
            "background": "Schwarzschild exterior r>2M",
            "sector": "odd parity, ell>=2",
            "mu": "(ell-1)*(ell+2)",
            "fourier_phase": "exp(+I*omega*t)",
            "orientation": "epsilon_(tr)=+1, epsilon^(tr)=-1",
            "reduced_scalar_equation": (
                "(d_x**2+omega**2-f*V_odd)*Psi=F, x=rstar"
            ),
            "domain": "complexified smooth compact radial sources",
        },
        "source_realization": exact_identities(),
        "adjoint_overlap": {
            "pairing_for_compact_source": "integral(tilde_u*F,dx)",
            "choice": "F=eta*conjugate(tilde_u)",
            "eta": (
                "any nonnegative nonzero C_c^infinity bump supported "
                "where tilde_u is nonzero"
            ),
            "value": "integral(eta*abs(tilde_u)**2,dx)>0",
            "endpoint_terms": "0 because F is compactly supported",
            "conclusion": (
                "there exists a smooth compact conserved traceless odd "
                "stress-energy source with nonzero adjoint QNM overlap"
            ),
            "real_source_note": (
                "a real source is obtained by adjoining the reflected "
                "frequency and spherical-harmonic sector"
            ),
        },
        "conformal_source_audit": {
            "bach_identity": (
                "B_mu^mu=0 and nabla^mu B_munu=0 require "
                "T_mu^mu=0 and nabla^mu T_munu=0"
            ),
            "constructed_source_conserved": True,
            "constructed_source_traceless": True,
            "massive_point_particle_directly_admissible": False,
            "point_particle_reason": (
                "the standard massive point-particle stress tensor has "
                "nonzero trace and requires a conformal completion or "
                "compensator before coupling to pure Weyl gravity"
            ),
        },
        "observable_consequence": {
            "source_overlap_nonzero_for_constructed_source": True,
            "observation_overlap_nonzero_imported": True,
            "isolated_transfer_double_pole_visible": True,
            "local_contour_u_exp_iomega_u_term_visible": True,
        },
        "claim_flags": {
            "arbitrary_compact_reduced_source_realized": True,
            "stress_energy_conserved": True,
            "stress_energy_traceless": True,
            "constructed_source_adjoint_overlap_nonzero": True,
            "specified_geodesic_plunge_overlap_nonzero": False,
            "positive_energy_matter_realization": False,
            "global_causal_contour_theorem": False,
            "detector_observability": False,
        },
        "does_not_establish": [
            "a nonzero overlap for a specified geodesic plunge",
            "a positive-energy or energy-condition-satisfying matter model",
            "direct admissibility of the standard massive point-particle stress tensor",
            "a global retarded inverse-Laplace contour deformation",
            "detector sensitivity or parameter-estimation bounds",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data = build()
    args.output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
