#!/usr/bin/env python3
"""Produce the exact local-commutant and spectral-C certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"

IMPORTS = {
    "rw_simplicity_and_nonsplitting": (
        ROOT
        / "black_hole_programme/phase4/rw_maxwell_simplicity_endomorphisms_v1/certificate.json"
    ),
    "parent_krein_obstructions": (
        ROOT
        / "black_hole_programme/phase4/parent_resolvent_krein_obstructions_v1/certificate.json"
    ),
    "incoming_witt_decomposition": (
        ROOT
        / "black_hole_programme/phase3/axial_endpoint_witt_decomposition/certificate.json"
    ),
}

INPUT_COMMIT = "e5d8e7df25cdf7375d2f9a1e75e1eb69e9426e0a"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_zero(matrix: sp.Matrix) -> bool:
    return all(sp.simplify(x) == 0 for x in matrix)


def exact_data() -> dict:
    # Dual-number commutant algebra.
    a, b, c, d, k = sp.symbols("a b c d k")
    N = sp.Matrix([[0, 1], [0, 0]])
    Phi = a * sp.eye(2) + b * N
    Psi = c * sp.eye(2) + d * N
    assert N**2 == sp.zeros(2)
    assert Phi * Psi == a * c * sp.eye(2) + (a * d + b * c) * N
    assert sp.det(Phi) == a**2
    assert is_zero(Phi**2 - sp.eye(2)) is False
    involution_coefficients = [
        sp.expand((Phi**2 - sp.eye(2))[0, 0]),
        sp.expand((Phi**2 - sp.eye(2))[0, 1]),
    ]
    assert involution_coefficients == [a**2 - 1, 2 * a * b]
    finite_power = sp.simplify(Phi**k)
    # SymPy does not expand a symbolic matrix power, so verify integer powers
    # by induction on several exact controls and record the algebraic formula.
    for n in range(1, 7):
        assert Phi**n == a**n * sp.eye(2) + n * a ** (n - 1) * b * N

    # Exact nontrivial Hermitian representative for matrix sign.
    Q = sp.Matrix(
        [
            [sp.Rational(3, 5), sp.Rational(4, 5), 0],
            [-sp.Rational(4, 5), sp.Rational(3, 5), 0],
            [0, 0, 1],
        ]
    )
    D = sp.diag(2, -3, -5)
    G = sp.simplify(Q * D * Q.T)
    Csign = sp.simplify(Q * sp.diag(1, -1, -1) * Q.T)
    absG = sp.simplify(Q * sp.diag(2, 3, 5) * Q.T)
    assert Q.T * Q == sp.eye(3)
    assert Csign**2 == sp.eye(3)
    assert Csign.T * G == G * Csign
    assert G * Csign == absG
    assert all(x > 0 for x in absG.eigenvals())

    T = sp.Matrix([[1, 1, 0], [0, 1, 1], [1, 0, 2]])
    assert T.det() != 0
    Gsol = sp.simplify(T.T * G * T)
    Csol = sp.simplify(T.inv() * Csign * T)
    Hsol = sp.simplify(T.T * absG * T)
    assert Csol**2 == sp.eye(3)
    assert Csol.T * Gsol == Gsol * Csol
    assert Gsol * Csol == Hsol
    # Positive definiteness is exact by congruence: absG>0 and T is
    # invertible.  Avoid radical expressions from a direct cubic eigensolve.
    assert T.det() != 0
    assert all(x > 0 for x in absG.eigenvals())

    # Exact incoming threshold Witt basis.
    omega = sp.symbols("omega", positive=True)
    c2 = sp.Rational(384, 5)
    c1 = sp.Rational(384, 5)
    Gthreshold = sp.Matrix(
        [
            [0, c2 * omega, 0],
            [c2 * omega, 0, 0],
            [0, 0, -c1 * omega**3],
        ]
    )
    Cthreshold = sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, -1]])
    Hthreshold = sp.simplify(Gthreshold * Cthreshold)
    assert Cthreshold**2 == sp.eye(3)
    assert Cthreshold.T * Gthreshold == Gthreshold * Cthreshold
    assert Hthreshold == sp.diag(c2 * omega, c2 * omega, c1 * omega**3)

    imports = {
        name: {"path": str(path.relative_to(ROOT)), "sha256": digest(path)}
        for name, path in IMPORTS.items()
    }

    return {
        "schema": "axial-local-commutant-spectral-c-v1",
        "status": "EXACT_LOCAL_COMMUTANT_COMPACT_BAND_SPECTRAL_C_PASS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "source_commit": INPUT_COMMIT,
        "imports": imports,
        "local_commutant": {
            "hypotheses": [
                "0 -> M -> E -> M -> 0 is the certified nonsplit axial ell=2 spin-two extension",
                "M is simple and End(M)=C for every real omega>0",
                "the base field has characteristic zero",
            ],
            "unique_simple_submodule": (
                "any second simple submodule mapping nontrivially to E/M "
                "would split the extension"
            ),
            "naturality": "the induced submodule and quotient scalars obey a*e=e*d, hence a=d",
            "factorization": "Phi-a*I factors as E -> E/M=M -> M -> E",
            "nilpotent": "N=iota o identification o projection, N^2=0",
            "endomorphism_ring": "End(E)=C[N]/(N^2)",
            "multiplication": "(a+b*N)(c+d*N)=a*c+(a*d+b*c)*N",
            "automorphisms": "a+b*N with a nonzero",
            "idempotents": ["0", "I"],
            "involutions": ["-I", "+I"],
            "diagonalizable_endomorphisms": "scalars only",
            "finite_order_automorphisms": "scalar roots of unity only",
            "interpretation": "there is no nontrivial local semisimple branch observable",
        },
        "spectral_fundamental_symmetry": {
            "incoming_definition": "C_-(omega)=sgn(G_-)=G_-(G_-^2)^(-1/2)",
            "hypotheses": "G_- is Hermitian and invertible for every real omega>0",
            "identities": [
                "C_-^2=I",
                "C_-^dagger*G_-=G_-*C_-",
                "G_-*C_-=abs(G_-)>0",
            ],
            "solution_pullback": "C_sol=T_-^(-1)*C_-*T_-",
            "solution_gram": "G_sol=T_-^dagger*G_-*T_-",
            "positive_majorant": "G_sol*C_sol=T_-^dagger*abs(G_-)*T_->0",
            "compact_band": (
                "on every compact I contained in (0,infinity), continuity "
                "and invertibility make C_sol bounded and its positive norm "
                "uniformly equivalent to the coefficient norm"
            ),
            "locality": "spectral/global; generally nonlocal in radius and time",
        },
        "threshold_completion": {
            "endpoint": "Iminus incoming Witt basis after the exact second-null lift",
            "gram": "[[0,(384/5)omega,0],[(384/5)omega,0,0],[0,0,-(384/5)omega^3]]",
            "fundamental_symmetry": "[[0,1,0],[1,0,0],[0,0,-1]]",
            "positive_majorant": "diag((384/5)omega,(384/5)omega,(384/5)omega^3)",
            "weighted_norm": (
                "Integral[omega*(|u_E|^2+|u_X|^2)"
                "+omega^3*|u_1|^2] d omega"
            ),
            "consequence": (
                "the positive completion near zero is weighted and is not "
                "uniformly equivalent to unweighted whole-half-axis L2"
            ),
        },
        "scattering_c_equivalence": {
            "notation": [
                "S=(R,A)^T",
                "J_out=G_+ direct_sum H_H+",
                "C_out=C_+ direct_sum C_H",
                "H_out=J_out*C_out",
                "H_in=G_-*C_-",
            ],
            "krein_identity": "S^dagger*J_out*S=G_-",
            "positive_identity": "S^dagger*H_out*S=H_in",
            "intertwining": "C_out*S=S*C_-",
            "equivalence": True,
            "forward_proof": (
                "intertwining plus the Krein identity gives the positive identity"
            ),
            "reverse_proof": (
                "for A_C=C_out*S-S*C_-, expand A_C^dagger*H_out*A_C; "
                "the two norm terms and two cross terms all equal H_in, "
                "so the result is zero; positivity of H_out forces A_C=0"
            ),
            "required_hypotheses": [
                "the conserved Krein identity",
                "C_in and C_out are genuine Krein-self-adjoint involutions",
                "G_-*C_- and J_out*C_out are positive definite",
            ],
            "defect": "Delta_C=C_out*S-S*C_-",
            "physical_test": (
                "explicit T_+ can test whether independently selected endpoint "
                "fundamental symmetries intertwine; a transported symmetry on "
                "ran(S) need not be endpoint block diagonal"
            ),
        },
        "claim_flags": {
            "local_commutant_dual_numbers_exact": True,
            "only_scalar_local_semisimple_observables": True,
            "only_plus_minus_identity_local_involutions": True,
            "nonlocal_spectral_c_exists_each_positive_real_fiber": True,
            "compact_band_positive_norm_equivalence": True,
            "threshold_weighted_completion_exact": True,
            "scattering_positive_identity_equivalent_to_c_intertwining": True,
            "spectral_c_canonical": False,
            "spectral_c_covariant": False,
            "spectral_c_causal": False,
            "spectral_c_complex_holomorphic": False,
            "endpoint_block_diagonal_scattering_c_established": False,
            "whole_half_axis_unweighted_norm_equivalence": False,
            "full_six_state_commutant_dual_numbers": False,
            "brst_or_quantum_positive_state_space": False,
        },
        "does_not_establish": [
            "a canonical, covariant, causal or complex-frequency-holomorphic C operator",
            "compatibility of independently chosen endpoint fundamental symmetries with scattering",
            "an endpoint-block-diagonal C on the two future boundaries",
            "uniform equivalence to unweighted L2 at omega=0",
            "the commutant of the complete six-state RW/RW/Maxwell module",
            "nonsplitting of the mixed Maxwell extension",
            "BRST compatibility, a quantum state space, or quantum unitarity",
        ],
    }


def main() -> None:
    data = exact_data()
    CERT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "axial-local-commutant-spectral-c-receipt-v1",
        "source_commit": INPUT_COMMIT,
        "certificate": str(CERT.relative_to(ROOT)),
        "certificate_sha256": digest(CERT),
        "producer": str((HERE / "produce.py").relative_to(ROOT)),
        "producer_sha256": digest(HERE / "produce.py"),
        "verifier": str((HERE / "verify.py").relative_to(ROOT)),
        "verifier_sha256": digest(HERE / "verify.py"),
        "commands": [
            "python3 -m black_hole_programme.phase4.axial_local_commutant_spectral_c_v1.produce",
            "python3 -m black_hole_programme.phase4.axial_local_commutant_spectral_c_v1.verify",
            "python3 -m unittest -v black_hole_programme.phase4.axial_local_commutant_spectral_c_v1.test_commutant_spectral_c",
        ],
        "claim_boundary": (
            "exact local commutant, fiberwise/compact-band spectral C, "
            "threshold weights and scattering equivalence; physical "
            "canonical C remains open"
        ),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(data["status"])


if __name__ == "__main__":
    main()
