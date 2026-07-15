"""Exact compensator-to-Einstein--Weyl phase theorem.

The model is the minimal four-dimensional Weyl uplift

    S = S_W + integral sqrt(-g) [
            zeta (phi^2 R - 6 phi Box phi) - lambda phi^4
        ].

For ``phi != 0`` the scalar is a Weyl Stueckelberg field.  The constant frame
``phi=v`` generates an Einstein-Hilbert coefficient ``c1=zeta v^2`` and a
cosmological term, but retaining ``S_W`` gives Einstein--Weyl gravity rather
than pure Einstein gravity.  On flat TT modes the massless Einstein branch
acquires a nonzero pairing while an opposite-residue massive spin-2 branch
remains.

This is a local algebraic and reduced-mode theorem.  It is not the canonical
scalar-clock model commissioned by the D-quotient programme and makes no
causal boundary or quantum claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge" / "certificates" / "compensator_einstein_phase.json"
SCHEMA_PATH = (
    ROOT
    / "bridge"
    / "einstein_sector"
    / "schema"
    / "compensator_einstein_phase.schema.json"
)
INPUTS = {
    "pure_weyl_restriction": ROOT
    / "bridge"
    / "certificates"
    / "flat_einstein_symplectic_restriction.json",
    "einstein_weyl_reduction_source": ROOT / "symbolic" / "verify_gravity_reduction.py",
    "scalar_clock_vertical_slice": ROOT
    / "d_quotient_classical"
    / "certificates"
    / "SCALAR_CLOCK_VERTICAL_SLICE.json",
}


class CompensatorEinsteinPhaseError(RuntimeError):
    """Raised when the phase theorem or a fail-closed guard regresses."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CompensatorEinsteinPhaseError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _background_checks() -> dict[str, Any]:
    zeta, v = sp.symbols("zeta v", nonzero=True)
    lam = sp.symbols("lambda")
    c1 = zeta * v**2
    planck_squared = -2 * c1
    vacuum_energy = lam * v**4
    lambda_eff = sp.simplify(vacuum_energy / (2 * c1))
    scalar_curvature = sp.simplify(2 * lam * v**2 / zeta)

    _require(
        sp.simplify(lambda_eff - lam * v**2 / (2 * zeta)) == 0,
        "effective cosmological constant changed",
    )
    _require(
        sp.simplify(scalar_curvature - 4 * lambda_eff) == 0,
        "constant scalar and metric equations are inconsistent",
    )
    _require(
        sp.simplify(planck_squared + 2 * zeta * v**2) == 0,
        "repository Planck-scale conversion changed",
    )
    _require(
        sp.solve(sp.Eq(lambda_eff, 0), lam) == [0],
        "isolated nonzero-v flat vacuum no longer forces lambda=0",
    )

    return {
        "constant_frame": "phi=v with v!=0",
        "metric_equation": "zeta v^2 G_mn+(1/2)lambda v^4 g_mn=0",
        "scalar_equation": "2 zeta v R-4 lambda v^3=0",
        "induced_eh_coefficient": "c1=zeta v^2",
        "repository_planck_definition": "c1=-M_P^2/2",
        "induced_planck_scale": "M_P^2=-2 zeta v^2",
        "effective_cosmological_constant": "Lambda_eff=lambda v^2/(2 zeta)",
        "consistency_identity": "R=4 Lambda_eff=2 lambda v^2/zeta",
        "flat_vacuum": (
            "lambda=0 when zeta and v are nonzero and no additional vacuum-energy "
            "source cancels lambda v^4"
        ),
        "surviving_einstein_backgrounds": (
            "every four-dimensional Einstein metric Ric=Lambda_eff g satisfies the "
            "constant-compensator equations and is Bach-flat"
        ),
        "status": "PASS",
    }


def _weyl_frame_checks() -> dict[str, Any]:
    sigma, v, varphi = sp.symbols("sigma v varphi", nonzero=True)
    delta_h = 2 * sigma
    delta_varphi = -v * sigma
    delta_hat_trace_amplitude = sp.simplify(delta_h + 2 * delta_varphi / v)
    gauge_parameter = varphi / v
    gauge_fixed_varphi = sp.simplify(varphi - v * gauge_parameter)

    _require(delta_hat_trace_amplitude == 0, "Stueckelberg metric combination is not invariant")
    _require(gauge_fixed_varphi == 0, "constant compensator gauge is not locally accessible")

    return {
        "weyl_action": "g_mn -> exp(2 sigma) g_mn; phi -> exp(-sigma) phi",
        "invariant_metric": "g_hat_mn=(phi/mu)^2 g_mn",
        "yamabe_density": "zeta(phi^2 R-6 phi Box phi)",
        "integrated_bulk_density": "zeta(phi^2 R+6 partial_phi.partial_phi) modulo a boundary term",
        "linearized_transformations": "delta h_mn=2 sigma eta_mn; delta varphi=-v sigma",
        "invariant_linear_metric": "h_hat_mn=h_mn+2(varphi/v)eta_mn",
        "unitary_frame": "sigma=varphi/v sets varphi to zero locally when v!=0",
        "local_residual_weyl": "none after varphi=0 on the v!=0 chart",
        "interpretation": (
            "the constant value is a Weyl frame for a Stueckelberg compensator, not by "
            "itself an order parameter proving spontaneous breaking of a local gauge symmetry"
        ),
        "status": "PASS",
    }


def _tt_factorization_checks() -> dict[str, Any]:
    y, alpha, zeta, v = sp.symbols("y alpha zeta v", nonzero=True)
    c1 = zeta * v**2
    mass_squared = c1 / alpha
    kernel = sp.expand(alpha * y * (y + mass_squared) / 2)
    expanded = sp.expand(y * (c1 + alpha * y) / 2)
    _require(sp.simplify(kernel - expanded) == 0, "TT kernel did not factorize")

    derivative = sp.diff(kernel, y)
    massless_norm = sp.simplify(derivative.subs(y, 0))
    massive_norm = sp.simplify(derivative.subs(y, -mass_squared))
    _require(massless_norm == c1 / 2, "massless branch normalization changed")
    _require(massive_norm == -c1 / 2, "massive branch normalization changed")
    _require(sp.simplify(massless_norm + massive_norm) == 0, "branch residues lost opposition")

    inverse_kernel = sp.simplify(1 / kernel)
    partial_fraction = sp.simplify((sp.Rational(2, 1) / c1) * (1 / y - 1 / (y + mass_squared)))
    _require(sp.simplify(inverse_kernel - partial_fraction) == 0, "TT pole decomposition changed")

    pure_weyl_kernel = sp.simplify(kernel.subs(v, 0))
    pure_weyl_massless_norm = sp.simplify(massless_norm.subs(v, 0))
    _require(pure_weyl_kernel == alpha * y**2 / 2, "pure-Weyl limit is not the double root")
    _require(pure_weyl_massless_norm == 0, "Einstein-root norm survived the pure-Weyl limit")

    return {
        "repo_conventions": (
            "signature (+---); L=sqrt(-g)(c1 R+alpha Ric^2+beta R^2); "
            "alpha=-3 beta; healthy massless-graviton convention c1=-1"
        ),
        "one_polarization_lagrangian": (
            "L_TT=(alpha/4)(A_ddot+k^2 A)^2-(c1/4)(A_dot^2-k^2 A^2) modulo a divergence"
        ),
        "symbol": "K(y)=(1/2)y(c1+alpha y)=(alpha/2)y(y+M2)",
        "symbol_variable": "y is the second-order massless wave symbol",
        "mass_parameter": "M2=c1/alpha=zeta v^2/alpha",
        "roots": ["y=0 (massless Einstein helicity +/-2)", "y=-M2 (massive spin-2 branch)"],
        "branch_symplectic_normalizations": {
            "massless": "K'(0)=c1/2=zeta v^2/2",
            "massive": "K'(-M2)=-c1/2=-zeta v^2/2",
        },
        "inverse_kernel": "1/K=(2/c1)[1/y-1/(y+M2)]",
        "relative_signature": "the two simple spin-2 branches have opposite residues",
        "repository_healthy_sign": (
            "c1=-1 and alpha<0 give M2>0, a healthy massless branch, and a massive ghost branch"
        ),
        "pure_weyl_limit": (
            "v->0 at fixed zeta and alpha gives c1->0, M2->0, K->(alpha/2)y^2, "
            "and both simple-root normalizations vanish before the Jordan recombination"
        ),
        "status": "PASS",
    }


def _validate_contract(payload: dict[str, Any]) -> None:
    schema = _load(SCHEMA_PATH)
    _require(
        schema.get("$id") == "pure-weyl-compensator-einstein-phase-v1",
        "wrong compensator phase schema id",
    )
    for key in schema.get("required", []):
        _require(key in payload, f"compensator phase certificate is missing {key}")
    _require(payload.get("schema") == schema.get("$id"), "schema mismatch")
    _require(payload.get("schema_sha256") == _sha256(SCHEMA_PATH), "schema hash mismatch")
    _require(
        payload.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "wrong dependency tags",
    )
    _require(
        payload.get("provenance", {}).get("generator_sha256") == _sha256(Path(__file__)),
        "generator hash mismatch",
    )
    _require(
        payload.get("verdict")
        == "EINSTEIN_WEYL_PHASE_REPAIRS_MASSLESS_PAIRING_BUT_RETAINS_EXTRA_SPIN2",
        "compensator phase verdict changed",
    )
    flags = payload.get("claim_flags", {})
    required_flags = schema.get("properties", {}).get("claim_flags", {}).get("required", [])
    _require(set(flags) == set(required_flags), "claim flag inventory mismatch")
    true_flags = {
        "weyl_uplift_identity_derived",
        "constant_nonzero_unitary_frame_accessible",
        "induced_eh_coefficient_derived",
        "background_equations_derived",
        "flat_vacuum_requires_lambda_zero_without_cancellation",
        "tt_operator_factorized",
        "massless_einstein_pairing_nonzero_for_c1_nonzero",
        "extra_massive_spin2_branch_present",
        "opposite_branch_residues_derived",
        "pure_weyl_limit_coalesces_and_pairing_vanishes",
        "compensator_distinguished_from_scalar_clock",
        "scalar_clock_vertical_slice_imported",
    }
    _require(all(flags.get(name) is True for name in true_flags), "proved flag missing")
    _require(
        all(flags.get(name) is False for name in set(required_flags) - true_flags),
        "an open claim was promoted",
    )


def build_certificate() -> dict[str, Any]:
    pure_weyl = _load(INPUTS["pure_weyl_restriction"])
    scalar_clock = _load(INPUTS["scalar_clock_vertical_slice"])
    _require(
        pure_weyl.get("verdict") == "REDUCED_FLAT_EINSTEIN_SYMPLECTIC_EMBEDDING_REFUTED",
        "pure-Weyl pairing obstruction changed",
    )
    _require(
        scalar_clock.get("result_id") == "SCALAR_CLOCK_VERTICAL_SLICE"
        and scalar_clock.get("claim_status") == "CERTIFIED_OBSTRUCTION"
        and scalar_clock.get("gate_result", {}).get("status")
        == "OBSTRUCTED_ON_EXACT_VACUUM_CYLINDER"
        and scalar_clock.get("gate_result", {}).get("next_gate")
        == "BACKREACTED_OR_COMPOSITE_CLOCK_MODEL",
        "canonical scalar-clock obstruction gate changed",
    )

    certificate = {
        "schema": "pure-weyl-compensator-einstein-phase-v1",
        "schema_path": "bridge/einstein_sector/schema/compensator_einstein_phase.schema.json",
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "COMPENSATOR_EINSTEIN_PHASE",
        "result_state": "EINSTEIN_WEYL_PHASE_CERTIFIED_FULL_EINSTEIN_EQUIVALENCE_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "input_base_commit": "704787c06de9e3746c1230e130bb652cb787a825",
            "generator_path": "bridge/einstein_sector/compensator_einstein_phase.py",
            "generator_sha256": _sha256(Path(__file__)),
        },
        "inputs": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
            for name, path in INPUTS.items()
        },
        "model_definition": {
            "dimension": 4,
            "fields": ["metric g_mn", "Weyl Stueckelberg compensator phi"],
            "action": (
                "S=S_W+int sqrt(-g)[zeta(phi^2 R-6 phi Box phi)-lambda phi^4]"
            ),
            "assumptions": [
                "zeta is nonzero",
                "the local frame chart has phi=v nonzero",
                "the flat TT theorem uses alpha=-3 beta and lambda=0",
                "no additional matter vacuum energy is included",
            ],
            "literature_comparisons": [
                {
                    "reference": "https://arxiv.org/abs/2307.13531",
                    "use": "primary comparison for the invariant metric and four-dimensional Yamabe uplift",
                    "non_use": "not imported as this certificate's sign or spectrum calculation",
                },
                {
                    "reference": "https://arxiv.org/abs/1101.1971",
                    "use": "primary comparison for the massless plus massive spin-2 structure of curvature-squared gravity",
                    "non_use": "its AdS critical theory is not a flat compensator certificate",
                },
                {
                    "reference": "https://arxiv.org/abs/hep-th/0603131",
                    "use": "primary example of conformal matter supplying a scale and an Einstein effective action",
                    "non_use": "its Georgi-Glashow matter vacuum is not the minimal Stueckelberg model used here",
                },
            ],
        },
        "weyl_frame_theorem": _weyl_frame_checks(),
        "constant_background_theorem": _background_checks(),
        "flat_tt_factorization": _tt_factorization_checks(),
        "symplectic_repair": {
            "pure_weyl_input": (
                "on the flat TT Schwartz Einstein core the pure-Weyl current restricts to zero"
            ),
            "compensated_result": (
                "for c1=zeta v^2 nonzero the massless-root normalization is c1/2, so the "
                "Einstein TT branch is no longer a zero-pairing subspace"
            ),
            "meaning": (
                "the compensator-generated Einstein-Hilbert term repairs the specific reduced "
                "pairing obstruction, but does not remove the extra fourth-order branch"
            ),
        },
        "phase_classification": {
            "exact_full_theory_after_constant_frame": "Einstein-Weyl gravity with a cosmological term",
            "exact_einstein_solution_sector": (
                "Einstein metrics with Ric=Lambda_eff g form a solution sector because their Bach tensor vanishes"
            ),
            "not_exactly_einstein_gravity": (
                "the massive spin-2 root remains whenever alpha is nonzero and c1 is finite"
            ),
            "low_energy_statement": (
                "Einstein gravity is a conditional effective sector for wave symbols |alpha y/c1|<<1 "
                "after a declared prescription for the massive branch"
            ),
            "boundary_selected_statement": (
                "an exact Einstein phase would require independent causal or boundary conditions eliminating "
                "the massive branch while preserving the Einstein symplectic form"
            ),
            "nonlinear_extra_solutions": (
                "the flat massive spin-2 branch proves extra local solutions; a complete nonlinear "
                "classification of non-Einstein Einstein-Weyl solutions remains open"
            ),
        },
        "sign_and_degree_of_freedom_audit": {
            "healthy_graviton_choice": "c1=-1 in the repository curvature convention",
            "consequence_for_compensator": "zeta=-1/v^2 and the integrated scalar kinetic coefficient 6 zeta is negative",
            "interpretation": (
                "the wrong-sign scalar coordinate is locally removed by Weyl gauge on phi!=0; "
                "this is not a proof of full BV positivity"
            ),
            "remaining_problem": (
                "the massive spin-2 branch has the opposite residue and is the conventional ghost branch"
            ),
        },
        "scalar_clock_coordination": {
            "d_quotient_gate": "SCALAR_CLOCK_VERTICAL_SLICE",
            "canonical_model_owner": "classical D-quotient team",
            "imported_certificate": "d_quotient_classical/certificates/SCALAR_CLOCK_VERTICAL_SLICE.json",
            "imported_status": "OBSTRUCTED_ON_EXACT_VACUUM_CYLINDER",
            "imported_result": (
                "the canonical homogeneous scalar has exact local monotone charts, but no nonzero "
                "homogeneous clock is compatible with the exact vacuum cylinder and the zero "
                "background has no linearized clock incidence"
            ),
            "this_compensator": "constant-frame Stueckelberg scalar",
            "why_not_a_clock": "phi=v is constant and therefore supplies no monotone relational time variable",
            "next_shared_gate": "BACKREACTED_OR_COMPOSITE_CLOCK_MODEL",
            "import_rule": "this theorem must not be registered as compact_scalar_clock or used as a replacement for the imported clock certificate",
        },
        "verdict": "EINSTEIN_WEYL_PHASE_REPAIRS_MASSLESS_PAIRING_BUT_RETAINS_EXTRA_SPIN2",
        "claim_flags": {
            "weyl_uplift_identity_derived": True,
            "constant_nonzero_unitary_frame_accessible": True,
            "induced_eh_coefficient_derived": True,
            "background_equations_derived": True,
            "flat_vacuum_requires_lambda_zero_without_cancellation": True,
            "tt_operator_factorized": True,
            "massless_einstein_pairing_nonzero_for_c1_nonzero": True,
            "extra_massive_spin2_branch_present": True,
            "opposite_branch_residues_derived": True,
            "pure_weyl_limit_coalesces_and_pairing_vanishes": True,
            "compensator_distinguished_from_scalar_clock": True,
            "scalar_clock_vertical_slice_imported": True,
            "constant_compensator_is_monotone_clock": False,
            "backreacted_or_composite_clock_model_constructed": False,
            "full_bv_scalar_constraint_count_completed": False,
            "spontaneous_local_weyl_breaking_proved": False,
            "massive_branch_causally_excluded": False,
            "nonlinear_einstein_truncation_proved": False,
            "asymptotically_flat_scattering_equivalence_proved": False,
            "positive_quantum_hilbert_space_constructed": False,
            "weyl_anomaly_cancelled": False,
            "full_theory_equals_pure_einstein_gravity": False,
        },
        "scope_guards": [
            "the covariant compensator and constant-background identities are LOCAL-ALGEBRAIC",
            "the spin-2 factorization and pairing repair are REDUCED-MODE flat TT statements",
            "no result in this certificate carries the LORENTZIAN-CAUSAL tag",
            "constant compensator gauge is not spontaneous breaking without additional gauge-invariant vacuum data",
            "the result repairs the massless pairing but retains an opposite-residue massive spin-2 branch",
            "the exact-cylinder one-scalar clock obstruction is imported; its backreacted/composite repair, total coupled D verdict, nonlinear closure, boundary selection, scattering, and quantum theory remain open",
        ],
        "verification_command": (
            "python3 -m bridge.einstein_sector.compensator_einstein_phase "
            "--verify bridge/certificates/compensator_einstein_phase.json"
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
