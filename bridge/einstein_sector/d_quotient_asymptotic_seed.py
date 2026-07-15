"""Exact E-D1a generator dictionary and fail-closed asymptotic seed.

This module separates three objects that are often all denoted ``D``:

* real Einstein-static-universe time translation ``H_ESU=partial_T``;
* real Lorentzian Minkowski dilation ``D_M=t partial_t+r partial_r``;
* the compact/radial-quantization grading called ``D`` in the residual module.

The first two are related to the same Penrose coordinate chart by different
vector fields.  In particular, ``H_ESU`` crosses the null boundary of a fixed
Minkowski patch, whereas ``D_M`` is tangent to it.  Therefore a cylinder
Cartan quotient has no automatic asymptotically-flat image.

The module also verifies the triangular reduced operator algebra for the
Einstein-defect variable ``chi=Box h``.  Neither calculation constructs the
full Lorentzian BV--BFV phase space or a surface charge.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge" / "certificates" / "d_quotient_asymptotic_seed.json"
SCHEMA_PATH = (
    ROOT
    / "bridge"
    / "einstein_sector"
    / "schema"
    / "d_quotient_asymptotic_seed.schema.json"
)
INPUTS = {
    "closed_universe_bfv": ROOT / "bridge" / "certificates" / "closed_universe_bfv.json",
    "asymptotic_bootstrap": ROOT
    / "bridge"
    / "certificates"
    / "asymptotically_flat_einstein_bootstrap.json",
    "einstein_defect": ROOT
    / "bridge"
    / "certificates"
    / "einstein_defect_asymptotics.json",
}


class DQuotientAsymptoticSeedError(RuntimeError):
    """Raised when the E-D1a identities or fail-closed guards regress."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DQuotientAsymptoticSeedError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _lie_derivative_metric(
    metric: sp.MatrixBase,
    vector: sp.MatrixBase,
    coordinates: tuple[sp.Symbol, ...],
) -> sp.Matrix:
    dimension = len(coordinates)
    return sp.Matrix(
        dimension,
        dimension,
        lambda mu, nu: sp.simplify(
            sum(vector[rho] * sp.diff(metric[mu, nu], coordinates[rho]) for rho in range(dimension))
            + sum(metric[rho, nu] * sp.diff(vector[rho], coordinates[mu]) for rho in range(dimension))
            + sum(metric[mu, rho] * sp.diff(vector[rho], coordinates[nu]) for rho in range(dimension))
        ),
    )


def _bracket(
    left: sp.MatrixBase,
    right: sp.MatrixBase,
    coordinates: tuple[sp.Symbol, ...],
) -> sp.Matrix:
    return sp.Matrix(
        [
            sp.simplify(
                sum(
                    left[index] * sp.diff(right[component], coordinates[index])
                    - right[index] * sp.diff(left[component], coordinates[index])
                    for index in range(len(coordinates))
                )
            )
            for component in range(len(coordinates))
        ]
    )


def _generator_checks() -> dict[str, Any]:
    u, r, theta, phi = sp.symbols("u r theta phi", real=True)
    coordinates = (u, r, theta, phi)
    metric = sp.Matrix(
        [
            [-1, -1, 0, 0],
            [-1, 0, 0, 0],
            [0, 0, r**2, 0],
            [0, 0, 0, r**2 * sp.sin(theta) ** 2],
        ]
    )
    dilation = sp.Matrix([u, r, 0, 0])
    time_translation = sp.Matrix([1, 0, 0, 0])

    dilation_lie = _lie_derivative_metric(metric, dilation, coordinates)
    translation_lie = _lie_derivative_metric(metric, time_translation, coordinates)
    _require(dilation_lie == 2 * metric, "Minkowski dilation is not homothetic")
    _require(translation_lie == sp.zeros(4), "P_0 is not Killing in the Bondi chart")
    _require(
        _bracket(dilation, time_translation, coordinates) == -time_translation,
        "[D_M,P_0]=-P_0 failed",
    )

    omega = 1 / r
    _require(
        sp.simplify(sum(dilation[index] * sp.diff(omega, coordinates[index]) for index in range(4)))
        == -omega,
        "D_M Omega=-Omega failed",
    )

    # Real Penrose chart: u=tan U, v=tan V, U=(T-R)/2, V=(T+R)/2.
    # Push-forward of H_ESU=partial_T has the following Bondi components.
    v = u + 2 * r
    h_esu = sp.Matrix([(1 + u**2) / 2, r * (u + r), 0, 0])
    h_omega = sp.factor(-h_esu[1] / r**2)
    _require(sp.simplify(h_omega + 1 + u / r) == 0, "wrong H_ESU action on Omega")

    # Pull-back of D_M to the cylinder.
    T, R = sp.symbols("T R", real=True)
    d_cylinder = sp.Matrix([sp.sin(T) * sp.cos(R), sp.cos(T) * sp.sin(R)])
    boundary_defining = T + R - sp.pi
    boundary_action = sp.simplify(
        d_cylinder[0] * sp.diff(boundary_defining, T)
        + d_cylinder[1] * sp.diff(boundary_defining, R)
    )
    _require(
        sp.trigsimp(boundary_action.subs(R, sp.pi - T)) == 0,
        "D_M is not tangent to I_plus on the cylinder",
    )

    return {
        "bondi_metric": "ds^2=-du^2-2 du dr+r^2 q_AB dx^A dx^B",
        "minkowski_dilation": "D_M=u d_u+r d_r=t d_t+r d_r",
        "flat_time_translation": "P_0=d_u=d_t",
        "lie_D_metric": "2 g",
        "compensating_physical_weyl": "sigma=-1 in delta g=L_D g+2 sigma g",
        "lie_P0_metric": "0",
        "bracket": "[D_M,P_0]=-P_0",
        "penrose_factor": "Omega_P=cos(T)+cos(R)=2 cos(U) cos(V)",
        "penrose_coordinates": [
            "u=tan(U), v=tan(V)",
            "U=(T-R)/2, V=(T+R)/2",
        ],
        "real_cylinder_time_pushforward": (
            "H_ESU=(1+u^2)/2 d_u+r(u+r) d_r=(P_0+K_0)/2 in the stated convention"
        ),
        "H_ESU_action_on_inverse_radius": str(h_omega),
        "H_ESU_scri_test": "at Omega=0, H_ESU(Omega)=-1; a fixed Minkowski I_plus is not preserved",
        "D_M_action_on_inverse_radius": "D_M(Omega)=-Omega",
        "D_M_scri_restriction": "u d_u",
        "D_M_cylinder_pullback": [str(d_cylinder[0]), str(d_cylinder[1])],
        "D_M_I_plus_tangency": "D_M(T+R-pi)=0 on T+R=pi",
        "status": "PASS",
    }


def _radiative_core_checks() -> dict[str, Any]:
    u, s = sp.symbols("u s", real=True)
    shear = sp.Function("C")(u)
    transformed_shear = sp.exp(-s) * shear.subs(u, sp.exp(s) * u)
    transformed_news = sp.diff(transformed_shear, u)
    delta_shear = sp.simplify(sp.diff(transformed_shear, s).subs(s, 0))
    delta_news = sp.simplify(sp.diff(transformed_news, s).subs(s, 0))
    _require(delta_shear == u * sp.diff(shear, u) - shear, "wrong shear dilation")
    _require(delta_news == u * sp.diff(shear, u, 2), "wrong news dilation")
    _require(sp.simplify(sp.diff(delta_shear, u) - delta_news) == 0, "delta N != d_u delta C")
    return {
        "action_convention": "T_s(g)=exp(-2s) Phi_s^*g with Phi_s(u,r)=(exp(s)u,exp(s)r)",
        "background": "T_s(g_Minkowski)=g_Minkowski",
        "bondi_shear": "C_s(u,x)=exp(-s) C(exp(s)u,x)",
        "bondi_news": "N_s(u,x)=N(exp(s)u,x)",
        "infinitesimal_shear": "delta_D C=u d_u C-C",
        "infinitesimal_news": "delta_D N=u d_u N",
        "strong_core": "N in L1_u Hs(S2) intersect L2_u Hs(S2), C has finite Hs endpoint limits",
        "norm_scaling": {
            "L1_news": "||N_s||_L1=exp(-s)||N||_L1",
            "L2_news_squared": "||N_s||_L2^2=exp(-s)||N||_L2^2",
            "memory": "Delta C_s=exp(-s) Delta C",
        },
        "kinematic_conclusion": "the candidate strong radiative core is mapped into itself for finite real s",
        "not_checked": [
            "Bach constraints and the second fourth-order radiative pair",
            "mass and angular-momentum aspects",
            "soft completion and i0 corner matching",
            "presymplectic form, counterterms, charge, and flux",
        ],
        "status": "PASS_REDUCED_KINEMATICS",
    }


def _triangular_complex_checks() -> dict[str, Any]:
    b, g = sp.symbols("B G", commutative=True)
    operator = sp.Matrix([[b, -1], [0, b]])
    green = sp.Matrix([[g, g**2], [0, g]])
    defect = sp.Matrix([[b * g - 1, g * (b * g - 1)], [0, b * g - 1]])
    _require(
        (operator * green - sp.eye(2) - defect).applyfunc(sp.simplify) == sp.zeros(2),
        "wrong left triangular Green identity",
    )
    _require(
        (green * operator - sp.eye(2) - defect).applyfunc(sp.simplify) == sp.zeros(2),
        "wrong right triangular Green identity",
    )
    _require(defect.subs(b, 1 / g) == sp.zeros(2), "triangular inverse does not close")
    return {
        "field_order": ["h", "chi"],
        "operator": [["Box", "-1"], ["0", "Box"]],
        "equations": ["Box h-chi=f_h", "Box chi=f_chi"],
        "formal_green": [["G^+/-", "G^+/- G^+/-"], ["0", "G^+/-"]],
        "inverse_remainder": [["Box G-1", "G(Box G-1)"], ["0", "Box G-1"]],
        "support_identity": "J^+/- (J^+/-(K))=J^+/-(K) by causal transitivity",
        "einstein_subspace": "chi=0 with zero chi source and zero chi Cauchy data",
        "status": "FORMAL_OPERATOR_IDENTITY_ONLY",
        "open_domain_problem": (
            "no weighted/polyhomogeneous domain, constraint-compatible tensor Green operator, "
            "or null-infinity corner map has been constructed"
        ),
    }


def _validate_contract(payload: dict[str, Any]) -> None:
    schema = _load(SCHEMA_PATH)
    _require(schema.get("$id") == "pure-weyl-d-quotient-asymptotic-seed-v1", "wrong schema id")
    for key in schema.get("required", []):
        _require(key in payload, f"D-quotient seed is missing {key}")
    _require(payload.get("schema") == schema.get("$id"), "schema mismatch")
    _require(payload.get("schema_sha256") == _sha256(SCHEMA_PATH), "schema hash mismatch")
    _require(payload.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"], "wrong tags")
    provenance = payload.get("provenance", {})
    _require(provenance.get("generator_sha256") == _sha256(Path(__file__)), "generator hash mismatch")
    _require(payload.get("verdicts") == {
        "asymptotically_flat_D": "PHASE_SPACE_NOT_CLOSED",
        "einstein_sector": "EINSTEIN_OPEN",
    }, "verdict was promoted or changed")
    flags = payload.get("claim_flags", {})
    required_flags = schema.get("properties", {}).get("claim_flags", {}).get("required", [])
    _require(set(flags) == set(required_flags), "claim flag inventory mismatch")
    true_flags = {
        "real_penrose_generator_dictionary_derived",
        "flat_dilation_tangent_to_scri",
        "candidate_radiative_core_preserved_by_flat_dilation",
        "formal_triangular_green_identity_derived",
    }
    _require(all(flags.get(name) is True for name in true_flags), "proved seed flag missing")
    false_flags = set(required_flags) - true_flags
    _require(all(flags.get(name) is False for name in false_flags), "open claim was promoted")


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    closed = records["closed_universe_bfv"]
    bootstrap = records["asymptotic_bootstrap"]
    defect = records["einstein_defect"]
    _require(closed.get("surface_charge_rank") == 0, "closed-cylinder surface-charge premise changed")
    _require(closed.get("boundary_components") == [], "closed-cylinder boundary premise changed")
    _require(
        bootstrap.get("claim_flags", {}).get("pure_weyl_surface_charges_computed") is False,
        "asymptotic charge was computed upstream; this seed needs promotion review",
    )
    _require(
        bootstrap.get("claim_flags", {}).get("full_asymptotically_flat_function_space_admissible") is False,
        "asymptotic phase space was closed upstream; this verdict needs promotion review",
    )
    _require(defect.get("geometric_definition", {}).get("einstein_equation") == "chi=0", "chi premise changed")

    certificate = {
        "schema": "pure-weyl-d-quotient-asymptotic-seed-v1",
        "schema_path": "bridge/einstein_sector/schema/d_quotient_asymptotic_seed.schema.json",
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "E_D1A_D_GENERATOR_ASYMPTOTIC_SEED",
        "result_state": "KINEMATICS_PROVED_PHASE_SPACE_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "input_base_commit": "69b2b240d9a06a5473d275a16ed41d6df12687f8",
            "generator_path": "bridge/einstein_sector/d_quotient_asymptotic_seed.py",
            "generator_sha256": _sha256(Path(__file__)),
        },
        "inputs": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
            for name, path in INPUTS.items()
        },
        "generator_dictionary": _generator_checks(),
        "radial_quantization_warning": {
            "statement": (
                "the compact grading called D in radial quantization is related to Minkowski "
                "dilation by a Cayley/Wick continuation; it is not, without that continuation, "
                "the real Penrose push-forward of H_ESU=partial_T"
            ),
            "consequence": (
                "a real form, conformal chart, and boundary-preserving lift must be declared "
                "before asking for the asymptotic charge of cylinder D"
            ),
            "time_translation_charge_rule": (
                "nonzero ADM/Bondi P_0 charge does not decide the charge of D_M or H_ESU"
            ),
        },
        "flat_dilation_radiative_seed": _radiative_core_checks(),
        "triangular_einstein_defect_seed": _triangular_complex_checks(),
        "asymptotic_symmetry_gate": {
            "standard_fixed_frame_BMS_membership": "NOT_ESTABLISHED",
            "BMSW_or_extended_phase_space_membership": "OPEN",
            "physical_weyl_compensator_status": "OPEN_AT_BOUNDARY",
            "required_charge_test": "delta H=Omega_Sigma(delta phi,delta_(xi,sigma) phi) including boundary and corner terms",
            "charge_normalization": "OPEN",
            "integrability": "OPEN",
            "flux": "OPEN",
            "reason": (
                "boundary preservation of a reduced shear core is weaker than preservation of "
                "the full Bach phase space and does not establish presymplectic degeneracy"
            ),
        },
        "literature_scope": [
            {
                "reference": "https://arxiv.org/abs/2104.05793",
                "use": "primary comparison showing that a BMSW extension requires an enlarged renormalized null-infinity phase space and carries charges",
                "non_use": "not imported as a pure-Weyl null-infinity charge computation",
            },
            {
                "reference": "https://arxiv.org/abs/2311.03130",
                "use": "primary source for the fully nonlinear BMSW action on Bondi data",
                "non_use": "not a substitute for deriving the pure-Weyl Bach boundary complex",
            },
            {
                "reference": "https://arxiv.org/abs/1412.7508",
                "use": "primary evidence that conformal-gravity Weyl and diffeomorphism charges depend on declared boundary conditions",
                "non_use": "its boundary conditions are not an asymptotically-flat null-infinity certificate",
            },
        ],
        "verdicts": {
            "asymptotically_flat_D": "PHASE_SPACE_NOT_CLOSED",
            "einstein_sector": "EINSTEIN_OPEN",
        },
        "claim_flags": {
            "real_penrose_generator_dictionary_derived": True,
            "flat_dilation_tangent_to_scri": True,
            "candidate_radiative_core_preserved_by_flat_dilation": True,
            "formal_triangular_green_identity_derived": True,
            "cylinder_D_has_unique_real_asymptotic_image": False,
            "H_ESU_preserves_fixed_minkowski_scri": False,
            "full_asymptotically_flat_phase_space_closed": False,
            "BMSW_embedding_proved": False,
            "pure_weyl_D_charge_computed": False,
            "D_proved_proper_gauge": False,
            "D_proved_charged": False,
            "lorentzian_bv_bfv_complex_constructed": False,
            "null_infinity_green_complex_constructed": False,
            "einstein_causal_selection_proved": False,
            "helicity_two_scattering_space_recovered": False,
            "einstein_scattering_equivalence_proved": False,
        },
        "scope_guards": [
            "the Penrose generator dictionary is exact real Lorentzian coordinate algebra",
            "the shear transformation is a reduced Bondi kinematic calculation",
            "the triangular Green matrix is conditional on a two-sided wave Green operator on a common invariant domain",
            "no result in this certificate carries the LORENTZIAN-CAUSAL tag",
            "no charge, symplectic form, BRST cohomology, one-particle space, or scattering map is computed",
            "PHASE_SPACE_NOT_CLOSED is a fail-closed verdict, not evidence that D is charged or gauge",
        ],
        "verification_command": (
            "python3 -m bridge.einstein_sector.d_quotient_asymptotic_seed "
            "--verify bridge/certificates/d_quotient_asymptotic_seed.json"
        ),
    }
    _validate_contract(certificate)
    return certificate


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"certificate is stale or altered: {path}")


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
