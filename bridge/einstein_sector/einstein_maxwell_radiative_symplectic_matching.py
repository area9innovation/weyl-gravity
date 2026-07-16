"""Action-normalized radiative Einstein--Maxwell symplectic theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
AXIAL_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_axial_master_complex.json"
POLAR_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_polar_master_complex.json"
EXCEPTIONAL_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_polar_exceptional_complex.json"
ACTION_CHECK = ROOT / "bridge/einstein_sector/einstein_maxwell_radiative_symplectic_action_check.py"
LEE_WALD_CHECK = ROOT / "bridge/einstein_sector/einstein_maxwell_radiative_lee_wald_fixture.py"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_radiative_symplectic_matching.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_radiative_symplectic_matching.schema.json"


class RadiativeSymplecticError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RadiativeSymplecticError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_rows(matrix: sp.Matrix) -> list[list[str]]:
    return [
        [str(sp.factor(value)) for value in matrix.row(row)]
        for row in range(matrix.rows)
    ]


def _harmonic_reduction() -> dict[str, Any]:
    eigenvalue, norm = sp.symbols("lambda N_lm", positive=True)
    axial_local = [
        ["sin(theta)*(D_theta Y)^2/2", "0"],
        ["0", "sin(theta)*Y^2"],
    ]
    polar_local = [
        ["sin(theta)*Y^2/2", "-sin(theta)*Y^2"],
        ["-sin(theta)*Y^2", "sin(theta)*(D_theta Y)^2"],
    ]
    axial = norm * sp.Matrix([[eigenvalue, 0], [0, 2]]) / 2
    polar = norm * sp.Matrix([[1, -2], [-2, 2 * eigenvalue]]) / 2
    return {
        "normalization": "N_lm=int_(S2) conjugate(Y_lm) Y_lm dOmega > 0",
        "closed_sphere_identity": "int_(S2) conjugate(D_aY) D^aY dOmega=lambda*N_lm, obtained by integration by parts from -Delta Y=lambda Y",
        "axisymmetric_local_action_hessian_axial": axial_local,
        "axisymmetric_local_action_hessian_polar": polar_local,
        "all_m_extension": "SO(3) equivariance and Schur's lemma make the multiplicity-space matrices identical for every m; complex modes pair m with -m, while a real harmonic basis gives the displayed real form",
        "axial_rest_frame_coefficient_hessian": _matrix_rows(axial),
        "polar_integrated_hessian": _matrix_rows(polar),
        "no_interpolation": "the arbitrary-Y local Hessians are obtained from the exact second variation before imposing a fixed ell; only the eigenfunction integration identity is then used",
    }


def _master_matching() -> dict[str, Any]:
    eigenvalue = sp.symbols("lambda", positive=True)
    axial_master = sp.Matrix([[eigenvalue, 2], [eigenvalue, eigenvalue]])
    polar_master = sp.Matrix([[eigenvalue, -2 * eigenvalue], [-1, eigenvalue]])
    axial_coefficient_form = sp.diag(eigenvalue, 2)
    axial_form = axial_coefficient_form * axial_master
    polar_form = sp.Matrix([[1, -2], [-2, 2 * eigenvalue]])
    _require(
        axial_form * axial_master == axial_master.T * axial_form,
        "axial variational symmetrizer changed",
    )
    _require(
        polar_form * polar_master == polar_master.T * polar_form,
        "polar variational symmetrizer changed",
    )
    _require(
        sp.factor(axial_form.det()) == 2 * eigenvalue**2 * (eigenvalue - 2),
        "axial determinant changed",
    )
    _require(
        sp.expand(polar_form.det() - 2 * (eigenvalue - 2)) == 0,
        "polar determinant changed",
    )

    root = sp.sqrt(2 * eigenvalue)
    axial_vectors = (sp.Matrix([1, sp.sqrt(eigenvalue / 2)]), sp.Matrix([1, -sp.sqrt(eigenvalue / 2)]))
    polar_vectors = (sp.Matrix([-root, 1]), sp.Matrix([root, 1]))
    axial_norms = [
        sp.factor((vector.T * axial_form * vector)[0])
        for vector in axial_vectors
    ]
    polar_norms = [sp.factor((vector.T * polar_form * vector)[0]) for vector in polar_vectors]
    axial_masses = [eigenvalue + root, eigenvalue - root]
    expected_axial_norms = [2 * eigenvalue * mass for mass in axial_masses]
    _require(
        all(
            sp.simplify(actual - expected) == 0
            for actual, expected in zip(axial_norms, expected_axial_norms)
        ),
        "axial branch norms changed",
    )
    expected_polar_norms = [
        4 * eigenvalue + 4 * root,
        4 * eigenvalue - 4 * root,
    ]
    _require(
        all(
            sp.simplify(actual - expected) == 0
            for actual, expected in zip(polar_norms, expected_polar_norms)
        ),
        "polar branch norms changed",
    )
    return {
        "master_order": {"axial": ["H", "Q"], "polar": ["K", "U"]},
        "axial_master_matrix": _matrix_rows(axial_master),
        "polar_master_matrix": _matrix_rows(polar_master),
        "axial_rest_frame_coefficient_matrix_without_N_over_2": _matrix_rows(
            axial_coefficient_form
        ),
        "action_normalized_matrices_without_N_over_2": {
            "axial": _matrix_rows(axial_form),
            "polar": _matrix_rows(polar_form),
        },
        "symmetrizer_identities": ["G_A M_A=M_A^T G_A", "G_P M_P=M_P^T G_P"],
        "axial_curl_pullback": "the exact action Hessian diag(lambda,2) is for rest-frame transverse coefficients (h_x,q_x); the certified covariant curl potentials obey (h_A,q_A)=epsilon_A^B partial_B(H,Q), so periodic integration by parts and the master equation give G_A=diag(lambda,2) M_A",
        "radiative_positivity": "G_A has leading minor lambda^2 and determinant 2lambda^2(lambda-2); G_P has leading minor 1 and determinant 2(lambda-2). Both are positive for ell>=2 (lambda>=6)",
        "branch_vectors_plus_minus": {
            "axial": ["(1,sqrt(lambda/2))", "(1,-sqrt(lambda/2))"],
            "polar": ["(-sqrt(2lambda),1)", "(sqrt(2lambda),1)"],
        },
        "branch_weights_without_N_over_2": {
            "axial": [str(value) for value in axial_norms],
            "polar": [str(value) for value in polar_norms],
        },
        "all_S1_momenta": "the local 1+1 action and Lee-Wald current are Lorentz covariant. Pullback through the covariant curl representation and periodic integration by parts gives the same potential-master matrices for every k_n; no global boost of the cylinder is assumed",
    }


def _ell1_quotient() -> dict[str, Any]:
    polar_form = sp.Matrix([[1, -2], [-2, 4]])
    polar_gauge = sp.Matrix([2, 1])
    polar_representative = sp.Matrix([0, 1])
    axial_form = sp.Matrix([[4, 4], [4, 4]])
    axial_gauge = sp.Matrix([1, -1])
    axial_physical = sp.Matrix([1, 1])
    _require(polar_form.rank() == 1, "ell=1 polar form rank changed")
    _require(polar_form * polar_gauge == sp.zeros(2, 1), "ell=1 polar gauge kernel changed")
    polar_weight = (polar_representative.T * polar_form * polar_representative)[0]
    _require(polar_weight == 4, "ell=1 polar quotient weight changed")
    _require(axial_form.rank() == 1, "ell=1 axial form rank changed")
    _require(axial_form * axial_gauge == sp.zeros(2, 1), "ell=1 axial gauge kernel changed")
    axial_weight = (axial_physical.T * axial_form * axial_physical)[0]
    _require(axial_weight == 16, "ell=1 axial quotient weight changed")
    return {
        "polar_presymplectic_matrix_without_N_over_2": _matrix_rows(polar_form),
        "polar_kernel": "(K,U)=(2,1), exactly the smooth residual polar diffeomorphism",
        "polar_quotient_coordinate": "Psi=U-K/2; the K=0 representative is (K,U)=(0,Psi)",
        "polar_quotient_weight_without_N_over_2": str(polar_weight),
        "polar_quotient_weight_with_harmonic_normalization": "2*N_1m",
        "axial_presymplectic_matrix_without_N_over_2": _matrix_rows(axial_form),
        "axial_kernel": "(H,Q)=(1,-1), the massless combined Diff x U(1) branch away from the separate global twist analysis",
        "axial_physical_vector_and_weight": f"(H,Q)=(1,1) has bracket weight {axial_weight}, hence 8*N_1m after the universal factor",
        "coordinate_warning": "axial curl potentials and the polar master Psi have different fixed reconstruction conventions, so their raw quotient weights are not a parity-normalization comparison",
        "supersession": "This replaces the provisional '2 for Psi' inherited from a non-action-normalized diagonal conserved current in COMPACT_EM_POLAR_EXCEPTIONAL_COMPLEX. The correct bracket weight is 4, or 2*N_1m after the universal N_lm/2 factor.",
    }


def _covariant_and_bundle_statement() -> dict[str, Any]:
    return {
        "action_convention": "S=int sqrt(-g)[(R-2Lambda)/(2kappa)-F_mu_nu F^mu_nu/4], with kappa=1, Lambda=1/2, unit S2 radius, and background magnetic flux P=1",
        "lee_wald_potential": {
            "metric_variation": "h_mu_nu=delta g_mu_nu, h^mu_nu=g^mu_alpha g^nu_beta h_alpha_beta, h=g^mu_nu h_mu_nu",
            "gravity": "theta_g^mu=sqrt(-g)/(2kappa)*(nabla_nu h^mu_nu-nabla^mu h)",
            "Maxwell": "theta_M^mu=-sqrt(-g) F^(mu nu) delta A_nu",
            "symplectic_current": "omega^mu(delta1,delta2)=delta1 theta^mu(delta2)-delta2 theta^mu(delta1)",
        },
        "variational_identity": "the antisymmetrized field-space variation of theta equals the canonical current of the quadratic action modulo a spacetime-exact improvement; the integration by parts used in the Hessian check produces precisely such an improvement",
        "closed_cauchy_surface": "Sigma=S1 x S2 has no boundary, so the integral of the exact improvement vanishes and the action Hessian Wronskians equal the integrated covariant Lee-Wald presymplectic form",
        "fixed_bundle_argument": "although the magnetic background connection is patchwise, the difference of two connections on the fixed U(1) bundle P_N is a global one-form. Thus every allowed delta A is global, theta_M and omega_M agree on chart overlaps, and no Cech corner term occurs. Uniform magnetic-charge variation is excluded because it changes c1(P_N).",
        "orientation_and_cauchy_normal": "orientation dt wedge dx wedge sin(theta)dtheta wedge dphi; the future unit normal covector on t=constant is n_mu=(-1,0,0,0), so Omega_Sigma=int dSigma_mu omega^mu=-int dx dOmega omega^t",
        "reality": "real perturbations use real harmonics; the direct Fourier fixture pairs exp(i(kx-omega t)) with its conjugate, and real solutions are their real spans",
        "cauchy_form": "Omega_A=(N_lm/2) int_(S1) delta(H,Q)^T G_A wedge partial_t delta(H,Q) dx with G_A=diag(lambda,2)M_A; analogously Omega_P uses G_P directly on (K,U)",
    }


def _direct_lee_wald_fixtures() -> dict[str, Any]:
    return {
        "harmonic": "ell=2,m=0, Y=P_2(cos(theta)), lambda=6, N_20=4*pi/5",
        "momentum_scope": "k is retained as an arbitrary real symbol; in particular the identity holds at every nonzero periodic k_n",
        "variation_pair": [
            "delta1 proportional to exp(i(k x-omega t))",
            "delta2 proportional to exp(-i(k x-omega t))",
        ],
        "current_convention": "omega^t=delta1 theta^t(delta2)-delta2 theta^t(delta1)",
        "axial_coordinate_current": "int_S2 omega_A^t=-2*i*omega*(N_20/2)*(omega^2-k^2)*(H,Q)^T diag(6,2)(H,Q)",
        "axial_on_shell_reduction": "on either branch M_A v=(omega^2-k^2)v, hence the future-normal Cauchy contraction is +2*i*omega*(N_20/2)*v^T[diag(6,2)M_A]v",
        "polar_coordinate_current": "int_S2 omega_P^t=-2*i*omega*(N_20/2)*(K,U)^T[[1,-2],[-2,12]](K,U)",
        "polar_cauchy_reduction": "the future-normal contraction changes the sign and gives exactly the action-normalized polar master Wronskian",
        "remainders": {"axial": "0", "polar": "0"},
        "global_boost_used": False,
    }


def _supersession_ledger() -> list[dict[str, Any]]:
    return [
        {
            "certificate": "bridge/certificates/einstein_maxwell_polar_exceptional_complex.json",
            "json_pointer": "/ell1_complex/reduced_current_weight",
            "old_value": "2 for Psi, inherited from the physical eigenvector before covariant normalization",
            "replacement": "bracket weight 4 before the universal N_1m/2 factor; normalized quotient weight 2*N_1m",
            "scope": "normalization only; the gauge quotient, dispersion, and all-m classification remain valid",
            "status": "SUPERSEDED_BY_ACTION_NORMALIZED_LEE_WALD_MATCHING",
        }
    ]


def build_certificate() -> dict[str, Any]:
    axial = _load(AXIAL_CERTIFICATE)
    polar = _load(POLAR_CERTIFICATE)
    exceptional = _load(EXCEPTIONAL_CERTIFICATE)
    _require(axial["result_id"] == "COMPACT_EM_AXIAL_MASTER_COMPLEX", "axial input changed")
    _require(polar["result_id"] == "COMPACT_EM_POLAR_MASTER_COMPLEX", "polar input changed")
    _require(exceptional["result_id"] == "COMPACT_EM_POLAR_EXCEPTIONAL_COMPLEX", "exceptional input changed")
    return {
        "schema": "einstein-maxwell-radiative-symplectic-matching-v2",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "COMPACT_EM_RADIATIVE_SYMPLECTIC_MATCHING",
        "result_state": "COVARIANT_ACTION_NORMALIZED_RADIATIVE_PAIRING_MATCHED_GLOBAL_ZERO_MODES_AND_WEYL_PULLBACK_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_RADIATIVE_ALL_N_ELL_M_WITH_ELL1_QUOTIENT",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "exhaustive_action_check_path": str(ACTION_CHECK.relative_to(ROOT)),
            "exhaustive_action_check_sha256": _sha256(ACTION_CHECK),
            "direct_lee_wald_check_path": str(LEE_WALD_CHECK.relative_to(ROOT)),
            "direct_lee_wald_check_sha256": _sha256(LEE_WALD_CHECK),
            "inputs": {
                str(path.relative_to(ROOT)): _sha256(path)
                for path in (AXIAL_CERTIFICATE, POLAR_CERTIFICATE, EXCEPTIONAL_CERTIFICATE)
            },
        },
        "domain": "Einstein-Maxwell radiative tangent on R_t x S1_L x S2 at fixed magnetic bundle P_N, before the final residual SO(4,2) quotient; all n,m, ell>=2 plus the physical ell=1 quotient",
        "harmonic_reduction": _harmonic_reduction(),
        "master_matching": _master_matching(),
        "ell1_quotient": _ell1_quotient(),
        "covariant_and_bundle_statement": _covariant_and_bundle_statement(),
        "direct_lee_wald_fixtures": _direct_lee_wald_fixtures(),
        "supersedes": _supersession_ledger(),
        "classification": {
            "exact_arbitrary_harmonic_second_variation": True,
            "direct_nonzero_momentum_Lee_Wald_fixture": True,
            "covariant_Lee_Wald_integrated_matching": True,
            "fixed_magnetic_bundle_overlap_safe": True,
            "all_n_ell_ge_2_m_radiative_pairing": True,
            "polar_ell1_gauge_kernel_and_quotient": True,
            "kinetic_branch_weights_positive": True,
            "one_particle_complex_structure_constructed": False,
            "one_particle_norm_certified": False,
            "homogeneous_ell0_global_pairing": False,
            "axial_ell1_global_twist_pairing": False,
            "Weyl_Maxwell_pullback_matching": False,
            "Lorentzian_causal_or_scattering_theorem": False,
        },
        "interpretation": "The ordinary Einstein-Maxwell photon/graviton-like harmonic waves are nondegenerate directions with positive kinetic branch weights in the covariant phase space before the final residual quotient. The polar ell=1 zero branch disappears because it is exactly a presymplectic gauge kernel, not because its physical massive triplet vanishes. A one-particle Hilbert norm still requires a declared positive-frequency complex structure. Any later disappearance under the global conformal residual quotient is therefore a statement about the closed-cylinder global state space, not the absence of local radiation.",
        "next_gate": "separately compute the ell=0 radion/circumference/electric-charge and axial ell=1 twist global presymplectic pairs; then compare the pullback of the Weyl-Maxwell Lee-Wald form to this certified Einstein-Maxwell form, including any corner improvement",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem matches the action-normalized reduced Wronskians to the integrated Einstein-Maxwell Lee-Wald presymplectic form for every radiative ell>=2 mode and the physical ell=1 quotient on the closed compact Cauchy surface. Positivity here means positivity of the kinetic branch matrices, not a separately constructed one-particle Hilbert norm. It does not compute the homogeneous global-mode pairing, the axial ell=1 twist pair, the Weyl-Maxwell pullback, the final residual SO(4,2) cohomology, Lorentzian causal evolution, asymptotic scattering, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_radiative_symplectic_action_check --verify",
            "python3 -m bridge.einstein_sector.einstein_maxwell_radiative_lee_wald_fixture --verify",
            "python3 -m bridge.einstein_sector.einstein_maxwell_radiative_symplectic_matching --verify bridge/certificates/einstein_maxwell_radiative_symplectic_matching.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_radiative_symplectic_matching.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_radiative_symplectic_matching",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"radiative symplectic certificate stale: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(
            json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
