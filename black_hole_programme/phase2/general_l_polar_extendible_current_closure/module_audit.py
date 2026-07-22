"""Bounded exact algebra for the polar homogeneous-module audit.

The four-state Bach master is deliberately kept distinct from the seven-row
source-zero Ricci kernel.  Conflating them changes the current basis count.
"""

from __future__ import annotations

import sympy as sp


def master_infinity_audit() -> dict:
    w, z = sp.symbols("omega z", real=True, nonzero=True)
    A = sp.Matrix([
        [0, sp.I*w/2, sp.Rational(1, 2), sp.I*w],
        [0, 0, 1, 0],
        [0, 0, -2*sp.I*w, 0],
        [0, sp.I*w, sp.Rational(1, 2), 0],
    ])
    return {
        "matrix": [[sp.sstr(x) for x in row] for row in A.tolist()],
        "characteristic_polynomial": sp.sstr(sp.factor(A.charpoly(z).as_expr())),
        "zero_algebraic_multiplicity": 3,
        "zero_geometric_multiplicity": len(A.nullspace()),
        "zero_generalized_nullities": [len((A**k).nullspace()) for k in (1, 2, 3)],
        "oscillatory_geometric_multiplicity": len((A+2*sp.I*w*sp.eye(4)).nullspace()),
    }


def polynomial_master_ricci_residual() -> dict:
    """Exact seven-row residual of the advertised polynomial Bach-master mode."""
    L, w, r, k, a0 = sp.symbols("Lambda omega r kappa a0", nonzero=True)
    angp = (L*k + 2*a0 - 2*k)/(2*r**2)
    vv = sp.I*(-sp.I*L*a0 + L*k*w*r + 2*a0*w*r - 2*k*w*r + 6*k*w)/(2*r**2)
    a_for_angp = (2-L)*k/2
    vv_after = sp.factor(vv.subs(a0, a_for_angp))
    return {
        "mode": "Ch=Bh=0, Kh=kappa, Ah=I*omega*kappa*r+a0",
        "nonzero_rows": {"angP": sp.sstr(angp), "vv": sp.sstr(vv)},
        "angP_zero_choice": sp.sstr(a_for_angp),
        "remaining_vv_residual": sp.sstr(vv_after),
        "physical_domain_reading": (
            "The polynomial four-state Bach-master direction is not a nontrivial "
            "source-zero seven-Ricci-row direction for generic Lambda=ell(ell+1), "
            "ell>=2 and real omega!=0."
        ),
    }


def shallow_log_audit() -> dict:
    L, w = sp.symbols("Lambda omega", real=True, nonzero=True)
    defect = 3*L - 48*w**2 + 15 + 12*sp.I*w
    return {
        "defect": sp.sstr(defect),
        "imaginary_part": sp.sstr(sp.im(defect)),
        "nowhere_zero": sp.simplify(sp.im(defect)/(12*w)) == 1,
        "disposition": "NONEXTENDIBLE_SHALLOW_SOURCE_ARTIFACT",
    }

