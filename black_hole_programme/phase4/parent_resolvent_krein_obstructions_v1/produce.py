#!/usr/bin/env python3
"""Produce the exact parent-resolvent and Krein-obstruction certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"

PARENT = (
    ROOT
    / "black_hole_programme/phase4/second_order_parent_flux_v1/certificate.json"
)
COCYCLE = (
    ROOT
    / "black_hole_programme/phase3/axial_qnm_projective_cocycle_v1/certificate.json"
)
EP2 = (
    ROOT
    / "black_hole_programme/phase3/axial_qnm_spin_one_local_unit_v1/certificate.json"
)
FLUX = ROOT / "black_hole_programme/phase3/axial_null_flux_gram/certificate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_data() -> dict:
    # Exact finite-matrix realization of the noncommutative block identity.
    e11, e12, e21, e22 = sp.symbols("e11 e12 e21 e22")
    a11, a12, a21, a22 = sp.symbols("a11 a12 a21 a22")
    E = sp.Matrix([[e11, e12], [e21, e22]])
    A = sp.Matrix([[a11, a12], [a21, a22]])
    Einv = E.inv()
    zero = sp.zeros(2)
    H = sp.Matrix.vstack(
        sp.Matrix.hstack(zero, E),
        sp.Matrix.hstack(E, -A),
    )
    Hinv = sp.Matrix.vstack(
        sp.Matrix.hstack(Einv * A * Einv, Einv),
        sp.Matrix.hstack(Einv, zero),
    )
    assert all(sp.simplify(x) == 0 for x in H * Hinv - sp.eye(4))
    assert all(sp.simplify(x) == 0 for x in Hinv * H - sp.eye(4))

    # Rank-one Laurent coefficient P A P.
    u1, u2, v1, v2, alpha = sp.symbols(
        "u1 u2 v1 v2 alpha", nonzero=True
    )
    u = sp.Matrix([u1, u2])
    vT = sp.Matrix([[v1, v2]])
    P = u * vT / alpha
    beta = (vT * A * u)[0]
    rank_one_residual = P * A * P - beta * (u * vT) / alpha**2
    assert all(sp.simplify(x) == 0 for x in rank_one_residual)

    # Endomorphisms of the length-two Jordan model commute with J and have
    # form a I+b N.  In characteristic zero, C^2=I forces b=0 and a=±1.
    c11, c12, c21, c22 = sp.symbols("c11 c12 c21 c22")
    C = sp.Matrix([[c11, c12], [c21, c22]])
    J = sp.Matrix([[0, 1], [0, 0]])
    commuting = sp.solve(
        list(C * J - J * C),
        [c11, c21, c22],
        dict=True,
    )
    assert commuting == [{c11: c22, c21: 0}]
    a, b = sp.symbols("a b")
    CJ = sp.Matrix([[a, b], [0, a]])
    involution_equations = list(CJ**2 - sp.eye(2))
    assert sp.solve(involution_equations, [a, b], dict=True) == [
        {a: -1, b: 0},
        {a: 1, b: 0},
    ]

    # Hyperbolic plane quotient duality and positive graph boundary.
    k1, k2 = sp.symbols("k1 k2", complex=True)
    norm_k_squared = sp.symbols("norm_k_squared", nonnegative=True)
    graph_norm = 1 - norm_k_squared
    assert graph_norm.subs(norm_k_squared, 1) == 0
    hyperbolic = sp.Matrix([[0, 1], [1, 0]])
    e = sp.Matrix([1, 0])
    x = sp.Matrix([0, 1])
    assert (e.T * hyperbolic * e)[0] == 0
    assert (e.T * hyperbolic * x)[0] == 1
    assert hyperbolic.det() == -1

    imports = {}
    for name, path in {
        "second_order_parent": PARENT,
        "generic_projective_cocycle": COCYCLE,
        "physical_connection_ep2": EP2,
        "axial_flux_gram": FLUX,
    }.items():
        imports[name] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
        }

    return {
        "schema": "parent-resolvent-krein-obstructions-v1",
        "status": "EXACT_PARENT_RESOLVENT_KREIN_OBSTRUCTIONS_PASS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imports": imports,
        "parent_resolvent": {
            "hessian": "H=4*alpha*[[0,E],[E,-A]]",
            "domain": (
                "a gauge-fixed space and spectral point where E(omega) is invertible"
            ),
            "inverse": (
                "H^-1=(1/(4*alpha))*"
                "[[E^-1*A*E^-1,E^-1],[E^-1,0]]"
            ),
            "metric_block": "G_hh=(1/(4*alpha))*E^-1*A*E^-1",
            "normalization_note": (
                "the common scalar factor 1/(4*alpha) may be stripped when "
                "discussing pole order and Smith structure"
            ),
            "interpretation": (
                "the metric response is an Einstein resolvent, an algebraic "
                "trace-reversal insertion, and a second Einstein resolvent"
            ),
        },
        "conditional_qnm_laurent": {
            "hypotheses": [
                "an analytic Fredholm realization of the gauge-fixed Einstein QNM problem",
                "a simple Einstein resonance omega_n",
                "graph-norm boundedness of the algebraic insertion on the Fredholm spaces",
            ],
            "einstein_resolvent": "E^-1=P_n/z+R_n, z=omega-omega_n",
            "projector": "P_n=(u_n tensor u_tilde_n)/alpha_n",
            "alpha": "<u_tilde_n,E'(omega_n)u_n>",
            "beta_parent": "<u_tilde_n,A*u_n>",
            "double_coefficient": (
                "(1/(4*alpha_W))*(beta_parent/alpha_n^2)"
                "*(u_n tensor u_tilde_n)"
            ),
            "simple_coefficient": (
                "(1/(4*alpha_W))*(P_n*A*R_n+R_n*A*P_n)"
            ),
            "radial_overlap_agreement": (
                "predicted after scalar projection; commutator terms must be "
                "checked in the regularized adjoint pairing"
            ),
            "status": "CONDITIONAL_NOT_PHYSICAL_FREDHOLM_CERTIFIED",
        },
        "involution_lemma": {
            "statement": (
                "over characteristic zero, a nonsplit self-extension of a "
                "simple object admits no involution except plus or minus identity"
            ),
            "proof": (
                "a nontrivial involution gives complementary nonzero idempotents; "
                "their images are the two simple composition factors and split "
                "the length-two extension"
            ),
            "jordan_model": "End(E)=k[I,N], N^2=0; (aI+bN)^2=I gives a=±1,b=0",
            "bach_application": (
                "requires generic simplicity of the Regge-Wheeler differential "
                "module or an equivalent exact endomorphism-ring certificate"
            ),
            "bach_application_status": "OPEN_SIMPLICITY_GATE",
            "existing_unconditional_result": (
                "no rational branch-resolving involution assigning opposite signs "
                "to the certified nonsplit layers"
            ),
        },
        "positive_subspace_obstruction": {
            "finite_fiber": (
                "a maximal uniformly positive line in signature (1,2) is "
                "Graph(K) with ||K||<1"
            ),
            "einstein_vector": "E=(1,1,0)/sqrt(2)",
            "inclusion_requirement": "K(1)=(1,0), hence ||K||=1",
            "conclusion": (
                "no uniformly positive closed endpoint subspace contains the "
                "pure Einstein channel; nonnegative inclusion is degenerate"
            ),
            "wave_packet_scope": (
                "for a general closed graph use an operator contraction; "
                "the pointwise K(omega) statement applies to decomposable "
                "frequency-multiplication-invariant subspaces"
            ),
        },
        "cotangent_type_duality": {
            "spin_two_space": "B_2 with hyperbolic nondegenerate form",
            "einstein_line": "E is isotropic and E^perp=E inside B_2",
            "canonical_map": "B_2/E -> E^*, [x] maps to (e -> G(e,x))",
            "isomorphism": True,
            "splitting": (
                "the endpoint duality is canonical; a radial differential-module "
                "splitting is not"
            ),
        },
        "experiment_specs": {
            "parent_overlap_audit": {
                "input": "the certified simple axial spin-two QNM disk",
                "compute": (
                    "regularized beta_parent=<f_tilde,A f> including endpoint terms"
                ),
                "compare": (
                    "the normalized radial projective/extension overlap beta_RW"
                ),
                "gate": (
                    "certify the scalar projection and commutator cancellation "
                    "before declaring equality"
                ),
            },
            "retarded_convolution_control": {
                "formal_identity": "G_hh_ret=G_E_ret*A*G_E_ret",
                "schwarzschild_algorithm": (
                    "evolve the target Einstein/Maxwell field, source a second "
                    "Einstein evolution, and add the homogeneous Einstein solution"
                ),
                "minkowski_control": (
                    "for E=Box and A=1 compare with "
                    "G_Box2_ret=theta(t-r)/(8*pi), up to sign convention"
                ),
                "status": "EXPERIMENT_SPEC_NOT_SCHWARZSCHILD_TIME_DOMAIN_THEOREM",
            },
        },
        "claim_flags": {
            "parent_block_inverse_exact": True,
            "rank_one_double_coefficient_algebra_exact": True,
            "physical_qnm_double_pole_established": False,
            "generalized_ringdown_established": False,
            "simple_self_extension_involution_lemma_exact": True,
            "generic_rw_module_simplicity_certified": False,
            "only_plus_minus_identity_on_bach_spin_two_certified": False,
            "branch_resolving_rational_involution_excluded": True,
            "uniform_positive_einstein_containing_subspace_exists": False,
            "cotangent_type_endpoint_duality_exact": True,
            "retarded_convolution_formal_identity": True,
            "schwarzschild_retarded_evolution_certified": False,
            "quantum_statement": False,
        },
        "does_not_establish": [
            "the analytic Fredholm QNM realization or a physical Green-resolvent double pole",
            "a generalized t exp(i omega_n t) ringdown term",
            "defectiveness of every simple spin-two QNM",
            "generic simplicity of the Regge-Wheeler differential module",
            "the unconditional claim that every rational involution of the Bach spin-two block is plus or minus identity",
            "absence of nonlocal, scattering-dependent, spectral, or BRST C operators",
            "a Schwarzschild retarded propagator or time-domain stability theorem",
            "a quantum positivity or unitarity theorem",
        ],
    }


def main() -> None:
    data = exact_data()
    CERT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "parent-resolvent-krein-obstructions-receipt-v1",
        "status": data["status"],
        "source_commit": "3212158362b6d96e273668ffff9b50665565933e",
        "artifacts": {
            "certificate": {"path": CERT.name, "sha256": sha256(CERT)},
            "producer": {"path": Path(__file__).name, "sha256": sha256(Path(__file__))},
            "verifier": {
                "path": "verify.py",
                "sha256": sha256(HERE / "verify.py"),
            },
            "tests": {
                "path": "test_resolvent.py",
                "sha256": sha256(HERE / "test_resolvent.py"),
            },
            "imports": data["imports"],
        },
        "verification": {
            "independence_level": "Level II: separately written block and module verifier",
            "independent_verifier": "python3 verify.py",
            "tests": "python3 -m unittest -v test_resolvent.py",
        },
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(data["status"])


if __name__ == "__main__":
    main()
