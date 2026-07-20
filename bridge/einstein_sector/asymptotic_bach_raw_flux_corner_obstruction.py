"""Exact reduced TT raw-flux obstruction at null infinity."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/asymptotic_bach_raw_flux_corner_obstruction.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/asymptotic_bach_raw_flux_corner_obstruction.schema.json"
INPUTS = {
    "asymptotic_seed": ROOT / "bridge/certificates/d_quotient_asymptotic_seed.json",
    "bondi_indicial": ROOT / "bridge/certificates/bondi_bach_indicial.json",
    "einstein_defect": ROOT / "bridge/certificates/einstein_defect_asymptotics.json",
    "flat_restriction": ROOT / "bridge/certificates/flat_einstein_symplectic_restriction.json",
}


class RawFluxObstructionError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RawFluxObstructionError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _box(phi: sp.Expr, u: sp.Symbol, r: sp.Symbol, angular: sp.Symbol) -> sp.Expr:
    """Scalar wave operator in outgoing retarded coordinates."""
    return sp.expand(
        -2 * sp.diff(phi, u, r)
        - 2 * sp.diff(phi, u) / r
        + sp.diff(phi, r, 2)
        + 2 * sp.diff(phi, r) / r
        - angular * phi / r**2
    )


def _upper_r(phi: sp.Expr, u: sp.Symbol, r: sp.Symbol) -> sp.Expr:
    """Contravariant radial derivative: nabla^r=-d_u+d_r."""
    return -sp.diff(phi, u) + sp.diff(phi, r)


def _raw_current(
    phi_1: sp.Expr,
    phi_2: sp.Expr,
    u: sp.Symbol,
    r: sp.Symbol,
    angular: sp.Symbol,
) -> sp.Expr:
    """Lee-Wald/Green current of S=(1/2) integral (Box phi)^2."""
    chi_1 = _box(phi_1, u, r, angular)
    chi_2 = _box(phi_2, u, r, angular)
    return sp.expand(
        chi_1 * _upper_r(phi_2, u, r)
        - _upper_r(chi_1, u, r) * phi_2
        - chi_2 * _upper_r(phi_1, u, r)
        + _upper_r(chi_2, u, r) * phi_1
    )


def _coefficient(expr: sp.Expr, r: sp.Symbol, power: int) -> sp.Expr:
    return sp.factor(sp.expand(expr).coeff(r, power))


def _direct_flux_algebra() -> dict[str, Any]:
    u, r, angular = sp.symbols("u r L", positive=True)
    f_0 = sp.Function("f_0")(u)
    f_1 = sp.Function("f_1")(u)
    g_0 = sp.Function("g_0")(u)
    g_1 = sp.Function("g_1")(u)

    p0_f = f_0 + f_1 / r
    p0_g = g_0 + g_1 / r
    p1_f = f_0 / r + f_1 / r**2
    p1_g = g_0 / r + g_1 / r**2

    flux_00 = sp.expand(r**2 * _raw_current(p0_f, p0_g, u, r, angular))
    flux_11 = sp.expand(r**2 * _raw_current(p1_f, p1_g, u, r, angular))
    flux_01 = sp.expand(r**2 * _raw_current(p0_f, p1_g, u, r, angular))

    leading_00 = _coefficient(flux_00, r, 1)
    finite_01 = _coefficient(flux_01, r, 0)
    leading_11 = _coefficient(flux_11, r, -2)
    expected_00 = 2 * (f_0 * sp.diff(g_0, u, 2) - g_0 * sp.diff(f_0, u, 2))
    expected_01 = 2 * (sp.diff(f_0, u) * sp.diff(g_0, u) - g_0 * sp.diff(f_0, u, 2))
    _require(sp.simplify(leading_00 - expected_00) == 0, "p0-p0 leading flux changed")
    _require(sp.simplify(finite_01 - expected_01) == 0, "p0-p1 finite flux changed")
    _require(all(_coefficient(flux_11, r, power) == 0 for power in (1, 0, -1)), "p1-p1 gained a finite term")
    _require(leading_11 != 0, "p1-p1 first decaying coefficient disappeared")

    wronskian = 2 * (f_0 * sp.diff(g_0, u) - g_0 * sp.diff(f_0, u))
    _require(sp.simplify(sp.diff(wronskian, u) - leading_00) == 0, "corner derivative identity changed")
    return {
        "action": "S_red=(1/2) integral (Box phi)^2",
        "potential": "theta^mu=chi nabla^mu(delta phi)-nabla^mu(chi) delta phi, chi=Box phi",
        "current": "j^mu=chi_1 nabla^mu phi_2-nabla^mu chi_1 phi_2-(1<->2)",
        "cut_density": "r^2*j^r before the common positive sphere harmonic norm",
        "p0_p0": {
            "leading_power": "r^1",
            "coefficient": str(leading_00),
            "corner_primitive": str(wronskian),
            "verdict": "GENERIC_LINEAR_CUT_DIVERGENCE",
        },
        "p0_p1": {
            "leading_power": "r^0",
            "coefficient": str(finite_01),
            "verdict": "FINITE_CROSS_TERM_NOT_A_P1_P1_RADIATIVE_FORM",
        },
        "p1_p1": {
            "powers_r1_r0_rminus1": ["0", "0", "0"],
            "first_nonzero_power": "r^-2",
            "first_nonzero_coefficient": str(leading_11),
            "verdict": "ZERO_RAW_NULL_INFINITY_FLUX",
        },
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["bondi_indicial"]["radiative_indicial_roots"] == ["0", "1"], "indicial roots changed")
    _require(
        records["bondi_indicial"]["p0_extra_bach_falloff"]["boundary_metric_changed"] is True,
        "p0 boundary-metric role changed",
    )
    _require(
        records["bondi_indicial"]["claim_flags"]["fixed_boundary_metric_isolates_full_einstein_sector"] is False,
        "upstream p1 obstruction was overpromoted",
    )
    _require(
        records["einstein_defect"]["claim_flags"]["kappa_zero_sufficient_for_einstein"] is False,
        "Einstein-defect tower was truncated upstream",
    )
    _require(
        records["flat_restriction"]["claim_flags"]["nonzero_symplectic_proportionality_refuted"] is True,
        "flat Einstein raw-current control changed",
    )
    seed = records["asymptotic_seed"]
    _require(
        seed["generator_dictionary"]["H_ESU_scri_test"]
        == "at Omega=0, H_ESU(Omega)=-1; a fixed Minkowski I_plus is not preserved",
        "H_ESU boundary result changed",
    )
    _require(
        seed["generator_dictionary"]["D_M_I_plus_tangency"] == "D_M(T+R-pi)=0 on T+R=pi",
        "D_M tangency changed",
    )

    algebra = _direct_flux_algebra()
    return {
        "schema": "asymptotic-bach-raw-flux-corner-obstruction-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "ASYMPTOTIC_BACH_RAW_FLUX_CORNER_OBSTRUCTION",
        "result_state": "FIRST_NULL_INFINITY_BOUNDARY_CORNER_OBSTRUCTION_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_REDUCED_TT_RAW_CURRENT_NULL_INFINITY",
        "scope": {
            "theory": "linearized pure-Weyl gravity reduced Cartesian TT polarization",
            "background": "Minkowski space in outgoing retarded coordinates",
            "boundaries": "large-r cuts of I+ in one fixed conformal completion",
            "charge_sector": "radiative p=1 and boundary-metric p=0 indicial data; Coulombic aspects absent",
            "carrier": "two-term scalar amplitudes for one TT polarization and one angular Laplacian eigenmode",
            "degree": 1,
            "parity": "one polarization; identical algebra for the other flat TT polarization",
            "ell": "scalar-amplitude angular eigenvalue L; not a full tensor-harmonic classification",
            "m": "suppressed by angular orthogonality",
            "k": "radial asymptotic expansion, not compact momentum",
            "omega": "arbitrary retarded-time profiles within the formal indicial channel",
        },
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
        "declared_raw_domain": {
            "fields": [
                "p=0: phi=f_0(u,x)+r^-1 f_1(u,x)+O(r^-2)",
                "p=1: phi=r^-1 g_0(u,x)+r^-2 g_1(u,x)+O(r^-3)",
            ],
            "boundary_metric_fixed_subspace": "p=0 data excluded",
            "ghosts": "NO_CERTIFIED_DOMAIN",
            "antifields": "NO_CERTIFIED_DOMAIN",
            "Coulombic_data": "NO_CERTIFIED_DOMAIN",
            "I_minus_matching": "NO_CERTIFIED_MAP",
            "i0_corner_matching": "OPEN; the divergent coefficient is an exact u-derivative corner term",
            "polyhomogeneous_logs": "OPEN; full tensor repeated-root reconstruction not performed",
        },
        "raw_flux_algebra": algebra,
        "obstruction_theorem": {
            "with_p0": "The unrenormalized cut density has a generic O(r) p0-p0 divergence. Its coefficient is an exact u derivative, so any whole-I cancellation is a corner condition, not a finite cutwise Lee-Wald form.",
            "without_p0": "Fixing the unphysical boundary metric removes p0, but the complete p1-p1 raw flux is O(r^-2) after the r^2 cut measure and vanishes at I+.",
            "cross_term": "The finite p0-p1 term does not supply a p1-p1 radiative symplectic form and cannot make the fixed-boundary p1 carrier nondegenerate.",
            "conclusion": "No nondegenerate finite raw Lee-Wald radiative phase space exists on the declared p0/p1 seed without a boundary counterterm/renormalized potential or additional boundary variables.",
            "first_missing_object": "a covariant tensor boundary counterterm and corner prescription whose improved current is finite, conserved and gauge compatible",
        },
        "repeated_root_and_reconstruction_audit": {
            "bulk_biwave": "(Box)^2 phi=0 has the Einstein kernel chi=Box phi=0 and generalized defect chi!=0",
            "p0": "changes the leading unphysical boundary metric",
            "p1": "contains Einstein radiation and the same-falloff Bach defect beginning with kappa; kappa=0 is not sufficient for Einstein",
            "metric_reconstruction": "OPEN beyond the reduced Cartesian TT representative",
            "Jordan_log_channels": "OPEN in the full tensor/polyhomogeneous complex",
        },
        "generator_charge_disposition": {
            "P0": {
                "boundary_action": "tangent to I+",
                "raw_charge": "OBSTRUCTED_BY_DIVERGENT_OR_RADICAL_RAW_FORM",
                "final_status": "OPEN",
            },
            "D_M": {
                "boundary_action": "tangent to I+ and preserves the reduced strong core",
                "raw_charge": "OBSTRUCTED_BY_DIVERGENT_OR_RADICAL_RAW_FORM",
                "final_status": "OPEN",
            },
            "H_ESU": {
                "boundary_action": "not tangent to the boundary of one fixed Minkowski patch because H_ESU(Omega)|I+=-1",
                "raw_charge": "NOT_APPLICABLE_ON_THIS_FIXED_PATCH_PHASE_SPACE",
                "final_status": "OBSTRUCTED",
            },
            "D_rad": {
                "boundary_action": "no real Lorentzian boundary lift declared",
                "raw_charge": "NO_CERTIFIED_MAP",
                "final_status": "NO_CERTIFIED_MAP",
            },
        },
        "classification": {
            "raw_reduced_current_derived": True,
            "p0_generic_cut_flux_divergence_certified": True,
            "p0_divergence_is_corner_derivative": True,
            "fixed_boundary_p1_raw_flux_radical": True,
            "finite_p0_p1_cross_term_certified": True,
            "nondegenerate_finite_raw_phase_space_constructed": False,
            "boundary_counterterm_constructed": False,
            "full_tensor_BV_BFV_phase_space_constructed": False,
            "P0_charge_computed": False,
            "D_M_charge_computed": False,
            "H_ESU_fixed_patch_charge_applicable": False,
            "Einstein_and_additional_scattering_classified": False,
            "causal_particle_stability_or_quantum_claim": False,
        },
        "verdicts": {
            "asymptotically_flat_D": "PHASE_SPACE_NOT_CLOSED",
            "Einstein_sector": "EINSTEIN_OPEN",
            "work_item": "OBSTRUCTED_AT_FIRST_BOUNDARY_CORNER_GATE",
        },
        "claim_boundary": "This exact obstruction is confined to the reduced flat TT raw fourth-order current. It proves that the existing p0/p1 seed is not yet a finite nondegenerate null-infinity phase space. It does not rule out an improved renormalized tensor BV-BFV phase space, compute asymptotic charges, identify particles, or establish scattering, stability or unitarity.",
        "next_gate": "derive the full tensor Bondi Lee-Wald potential, boundary counterterm and i0/I+ corner prescription, then repeat the P0 and D_M differentiability tests; H_ESU requires a different boundary architecture",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.asymptotic_bach_raw_flux_corner_obstruction --verify bridge/certificates/asymptotic_bach_raw_flux_corner_obstruction.json",
            "python3 bridge/einstein_sector/verify_asymptotic_bach_raw_flux_corner_obstruction.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_asymptotic_bach_raw_flux_corner_obstruction",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"raw-flux obstruction certificate stale: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
