#!/usr/bin/env python3
"""Produce the local/nonlocal positivity dichotomy certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
INPUT_COMMIT = "d76cf4487265933fc4c3ded743af3e943bad8970"
IMPORTS = {
    "commutant_and_spectral_c": ROOT / "black_hole_programme/phase4/axial_local_commutant_spectral_c_v1/certificate.json",
    "critical_mass_jet": ROOT / "black_hole_programme/phase4/einstein_weyl_critical_mass_jet_v1/certificate.json",
    "rw_simplicity": ROOT / "black_hole_programme/phase4/rw_maxwell_simplicity_endomorphisms_v1/certificate.json",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_data() -> dict:
    a, b, g = sp.symbols("a b g", real=True)
    G = sp.Matrix([[0, g], [g, 0]])
    N = sp.Matrix([[0, 1], [0, 0]])
    eta = a * sp.eye(2) + b * N
    H = G * eta
    assert eta.T * G == G * eta
    assert sp.factor(H.det()) == -a**2 * g**2
    assert H.subs(a, 0).det() == 0

    # Exact witness that matrix sign is not congruence-covariant under a
    # general nonunitary frame change.
    J = sp.diag(1, -1)
    M = sp.Matrix([[1, 1], [0, 1]])
    Gp = M.T * J * M
    transported = sp.simplify(M.inv() * J * M)
    assert Gp == sp.Matrix([[1, 1], [1, 0]])
    assert transported == sp.Matrix([[1, 2], [0, -1]])
    assert transported != transported.T
    # sign(Gp) is Hermitian by spectral calculus, so it cannot equal this
    # non-Hermitian transported matrix.

    omega = sp.symbols("omega", positive=True)
    Wsqrt = sp.diag(sp.sqrt(omega), sp.sqrt(omega), omega ** sp.Rational(3, 2))
    W = sp.simplify(Wsqrt.T * Wsqrt)
    assert W == sp.diag(omega, omega, omega**3)

    # Opposite horizon/infinity signs differ by a rational horizon power only
    # if 4*i*omega is integral.  Algebraically special frequencies lie on it.
    ell = sp.symbols("ell", integer=True, positive=True)
    star = sp.Rational(1, 12) * (ell - 1) * ell * (ell + 1) * (ell + 2)
    lattice_value = sp.simplify(4 * sp.I * (sp.I * star))
    assert sp.simplify(
        lattice_value
        + sp.Rational(1, 3) * (ell - 1) * ell * (ell + 1) * (ell + 2)
    ) == 0

    return {
        "schema": "axial-local-nonlocal-positivity-v1",
        "status": "EXACT_LOCAL_NONLOCAL_POSITIVITY_DICHOTOMY_PASS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "source_commit": INPUT_COMMIT,
        "imports": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": digest(path)}
            for name, path in IMPORTS.items()
        },
        "local_metric_obstruction": {
            "commutant": "eta=a*I+b*N, N^2=0",
            "self_adjoint_condition": "a and b real in the canonical null basis",
            "flux_metric": "G2*eta=[[0,g*a],[g*a,g*b]]",
            "determinant": "-g^2*a^2",
            "conclusion": "a nonzero gives an indefinite form; a=0 gives a degenerate form",
            "theorem": "no rational local dynamically compatible metric operator makes the spin-two form positive definite",
        },
        "combined_future_c": {
            "premises": [
                "S is an injective Krein isometry from a nondegenerate incoming space",
                "ran(S) is nondegenerate",
                "K_out=ran(S) direct_sum ran(S)^perp",
            ],
            "transport": "C_ran*S=S*C_-",
            "extension": "choose any fundamental symmetry on ran(S)^perp and take the orthogonal direct sum",
            "conclusion": "a scattering-compatible fundamental symmetry always exists on the combined future space",
            "factorization_question": "whether C_out=C_+ direct_sum C_H",
        },
        "matrix_sign_noncanonicity": {
            "frame_law": "G -> M^dagger*G*M",
            "witness_G": "diag(1,-1)",
            "witness_M": "[[1,1],[0,1]]",
            "transformed_G": "[[1,1],[1,0]]",
            "transported_sign": "[[1,2],[0,-1]]",
            "reason": "transported_sign is non-Hermitian, whereas sign(transformed_G) is Hermitian",
            "conclusion": "matrix sign proves existence after choosing a positive coefficient norm, not canonical covariance",
        },
        "threshold_variables": {
            "weights": ["omega", "omega", "omega^3"],
            "renormalized": [
                "u_E_hat=omega^(1/2)*u_E",
                "u_X_hat=omega^(1/2)*u_X",
                "u_1_hat=omega^(3/2)*u_1",
            ],
            "W_half": "diag(omega^(1/2),omega^(1/2),omega^(3/2))",
            "normalized_transfer": "T_hat=W_out^(1/2)*T*W_in^(-1/2)",
            "warning": "the conserved Krein identity alone does not prove boundedness in the positive weighted norm",
        },
        "mass_crosswalk_ladder": {
            "gate_1": "[I_mass]=[I_Bach] modulo K_U proves local repeated-block equivalence up to rational gauge and parameter scale",
            "gate_2": "complete filtered equivalence must also include the mixed Maxwell-to-spin-two deformation",
            "gate_3": "moving endpoint phases and matched Jost germ normalizations are required for b=-partial_mass a",
            "gate_4": "analytic Fredholm realization is required for beta/alpha=d omega_n/d mass",
            "unique_nilpotent": "if the local extensions agree nontrivially, the critical branch-sign residue is proportional to the unique commutant nilpotent N",
        },
        "complex_reducibility_confinement": {
            "same_sign": "the existing terminal rational ansatz gives zero frequency or algebraically special controls",
            "opposite_sign": "a rational prefactor must change the horizon exponent by 4*i*omega, hence 4*i*omega is integral",
            "conclusion": "all remaining rational reducibility candidates lie on the quarter-integer imaginary lattice",
            "ell2_controls": ["i/4 excluded", "i/2 excluded", "i excluded", "plus/minus 2*i algebraically special"],
            "status": "CONFINEMENT_ONLY_NOT_COMPLETE_CLASSIFICATION",
        },
        "claim_flags": {
            "no_local_positive_metric_operator_even_without_involution": True,
            "combined_future_compatible_c_exists": True,
            "channel_factorized_c_automatic": False,
            "matrix_sign_canonical_under_general_frames": False,
            "threshold_ir_variables_exact": True,
            "whole_axis_positive_scattering_bounded": False,
            "mass_bach_local_equality_implies_global_jost_derivative": False,
            "mass_bach_local_equality_implies_qnm_slope": False,
            "unique_nilpotent_residue_direction": True,
            "complex_reducibility_quarter_lattice_confinement": True,
            "complete_complex_reducibility_classification": False,
            "quantum_statement": False,
        },
        "does_not_establish": [
            "a canonical, covariant, causal, holomorphic or BRST-compatible C",
            "factorization of the combined-future C over null infinity and the horizon",
            "whole-axis bounded positive scattering",
            "the physical mass/Jost derivative or QNM-slope identities",
            "the complete complex reducibility locus",
            "a full six-state commutant theorem or quantum positivity",
        ],
    }


def main() -> None:
    data = exact_data()
    CERT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "axial-local-nonlocal-positivity-receipt-v1",
        "source_commit": INPUT_COMMIT,
        "certificate": str(CERT.relative_to(ROOT)),
        "certificate_sha256": digest(CERT),
        "producer_sha256": digest(HERE / "produce.py"),
        "verifier_sha256": digest(HERE / "verify.py"),
        "commands": [
            "python3 -m black_hole_programme.phase4.axial_local_nonlocal_positivity_v1.produce",
            "python3 -m black_hole_programme.phase4.axial_local_nonlocal_positivity_v1.verify",
            "python3 -m unittest -v black_hole_programme.phase4.axial_local_nonlocal_positivity_v1.test_positivity",
        ],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(data["status"])


if __name__ == "__main__":
    main()
