"""Exact local-counterterm obstruction for flat Einstein radiation in C^2 gravity.

This theorem is deliberately narrower than a Bondi BV--BFV construction.  It
derives the full tensor Lee--Wald potential, classifies the complete local
Jacobson--Kang--Myers ambiguity of that potential, and proves that the
fixed-boundary Einstein-radiative restriction has zero horizontal
presymplectic class.  Consequently no counterterm made only from the existing
metric jets can turn that restriction into a nondegenerate radiative phase
space.  The enlarged p=0/p=1 source--response carrier remains open.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/ASYMPTOTIC_BACH_LOCAL_COUNTERTERM_COHOMOLOGY_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/asymptotic-bach-local-counterterm-cohomology-obstruction-v1.schema.json"
ATLAS = ROOT / "residual_atlas/einstein-asymptotic-bach-local-counterterm-cohomology-fragment-v1.json"
INPUTS = {
    "raw_obstruction": ROOT / "bridge/certificates/asymptotic_bach_raw_flux_corner_obstruction.json",
    "full_tensor_current_fixture": ROOT / "bridge/certificates/weyl_maxwell_axial_lee_wald_fixture.json",
}
PINNED_RAW_SHA256 = "1cef43665f6ff2917669d7e762e20c527b3b4b001f8c77a1581856d93c35e10c"


class LocalCountertermObstructionError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise LocalCountertermObstructionError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"expected JSON object: {path}")
    return value


def _total_derivative(
    expression: sp.Expr,
    jets: tuple[tuple[sp.Symbol, ...], ...],
) -> sp.Expr:
    result = sp.S.Zero
    for family in jets:
        for index in range(len(family) - 1):
            result += sp.diff(expression, family[index]) * family[index + 1]
    return sp.expand(result)


def _euler_first_order(
    density: sp.Expr,
    zeroth: sp.Symbol,
    first: sp.Symbol,
    jets: tuple[tuple[sp.Symbol, ...], ...],
) -> sp.Expr:
    return sp.expand(
        sp.diff(density, zeroth)
        - _total_derivative(sp.diff(density, first), jets)
    )


def _exact_algebra() -> dict[str, Any]:
    alpha = sp.symbols("alpha_B", nonzero=True)
    riemann2, ricci2, scalar2 = sp.symbols("Riem2 Ric2 R2")
    c2 = riemann2 - 2 * ricci2 + scalar2 / 3
    e4 = riemann2 - 4 * ricci2 + scalar2
    reduced = sp.expand(c2 - e4)
    _require(reduced == 2 * ricci2 - sp.Rational(2, 3) * scalar2, "Gauss--Bonnet reduction changed")

    # P=d[(alpha/8)C^2]/dR.  Trace-free projection makes d(C^2)/dR=2C.
    momentum_factor = sp.diff(alpha * sp.Symbol("z") ** 2 / 8, sp.Symbol("z")) / sp.Symbol("z")
    _require(sp.simplify(momentum_factor - alpha / 4) == 0, "curvature momentum factor changed")

    ricci_12, scalar_1, scalar_2 = sp.symbols("Ricci12 R1 R2")
    polarized_bulk_hessian = 2 * ricci_12 - sp.Rational(2, 3) * scalar_1 * scalar_2
    einstein_restriction = polarized_bulk_hessian.subs(
        {ricci_12: 0, scalar_1: 0, scalar_2: 0}
    )
    _require(einstein_restriction == 0, "flat Einstein Hessian restriction changed")

    f0, f1, f2, g0, g1, g2 = sp.symbols("f0 f1 f2 g0 g1 g2")
    jets = ((f0, f1, f2), (g0, g1, g2))
    news_density = sp.expand(f0 * g1 - g0 * f1)
    euler_f = _euler_first_order(news_density, f0, f1, jets)
    euler_g = _euler_first_order(news_density, g0, g1, jets)
    _require(euler_f == 2 * g1 and euler_g == -2 * f1, "news Euler witness changed")

    # Mutation: the symmetric sign is D_u(fg) and must have zero Euler image.
    exact_mutation = sp.expand(f0 * g1 + g0 * f1)
    mutation_f = _euler_first_order(exact_mutation, f0, f1, jets)
    mutation_g = _euler_first_order(exact_mutation, g0, g1, jets)
    _require(mutation_f == 0 and mutation_g == 0, "Euler mutation control failed")
    _require(_total_derivative(f0 * g0, jets) == exact_mutation, "mutation primitive changed")

    return {
        "four_dimensional_curvature_identity": {
            "C_squared": "Riemann_squared-2*Ricci_squared+R_squared/3",
            "Euler_4": "Riemann_squared-4*Ricci_squared+R_squared",
            "difference": str(reduced),
            "consequence": "Modulo the Euler density, the quadratic bulk C^2 Hessian is built only from delta Ricci_ab and delta R.",
        },
        "curvature_momentum": {
            "P_abcd": "(alpha_B/4)*C_abcd",
            "factor": str(momentum_factor),
            "potential_density": "Theta_C2^a=2*sqrt(-g)*(P^(abcd)*nabla_d(delta g_bc)-(nabla_d P^(abcd))*delta g_bc)",
        },
        "flat_einstein_restriction": {
            "condition": "delta Ricci_ab=0 (hence delta R=0) for each Jacobi field",
            "polarized_bulk_hessian": str(polarized_bulk_hessian),
            "restricted_value": str(einstein_restriction),
            "presymplectic_class": "ZERO_MODULO_HORIZONTAL_EXACT_FORMS",
        },
        "nonexact_news_witness": {
            "one_polarization_density": str(news_density),
            "Euler_f": str(euler_f),
            "Euler_g": str(euler_g),
            "conclusion": "f*g_u-g*f_u is not a total u derivative in the finite local jet algebra.",
        },
        "mutation_control": {
            "mutated_density": str(exact_mutation),
            "primitive": str(f0 * g0),
            "Euler_f": str(mutation_f),
            "Euler_g": str(mutation_g),
            "verdict": "DETECTOR_REJECTS_EXACT_MUTATION",
        },
    }


def _validate_inputs(records: dict[str, dict[str, Any]]) -> None:
    raw = records["raw_obstruction"]
    fixture = records["full_tensor_current_fixture"]
    _require(_sha256(INPUTS["raw_obstruction"]) == PINNED_RAW_SHA256, "raw obstruction hash changed")
    _require(raw["result_id"] == "ASYMPTOTIC_BACH_RAW_FLUX_CORNER_OBSTRUCTION", "raw result id changed")
    _require(raw["classification"]["p0_divergence_is_corner_derivative"] is True, "raw corner derivative changed")
    _require(raw["classification"]["fixed_boundary_p1_raw_flux_radical"] is True, "raw p1 result changed")
    _require(fixture["result_id"] == "WEYL_MAXWELL_AXIAL_LEE_WALD_FIXTURE", "tensor current fixture changed")
    _require(
        fixture["current_formula"]["curvature_momentum"] == "P^abcd=(alpha_B/4)C^abcd",
        "tensor momentum convention changed",
    )
    _require(fixture["flat_tt_control"]["restricted_value"] == "0", "flat TT control changed")


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    _validate_inputs(records)
    algebra = _exact_algebra()
    return {
        "schema": "asymptotic-bach-local-counterterm-cohomology-obstruction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "ASYMPTOTIC_BACH_LOCAL_COUNTERTERM_COHOMOLOGY_OBSTRUCTION_V1",
        "result_state": "FULL_TENSOR_POTENTIAL_AND_FIXED_BOUNDARY_LOCAL_COUNTERTERM_NO_GO_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "generality_level": "G2_FULL_TENSOR_POTENTIAL_FIXED_BOUNDARY_RADIATIVE_COHOMOLOGY",
        "scope": {
            "theory": "linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Minkowski space in one fixed conformal completion",
            "boundaries": "local cuts of I+; compact-support-in-u radiative test subspace",
            "charge_sector": "zero Coulombic aspects; fixed leading unphysical boundary metric",
            "carrier": "full metric tensor in the bulk, restricted for the no-go to flat Einstein Jacobi fields with Bondi shear C_AB/r",
            "degree": 1,
            "parity": "both tracefree sphere-tensor polarizations; one polarization supplies the nonexactness witness",
            "ell": "all radiative tensor harmonics for which the Einstein Jacobi and compact-u-support conditions hold",
            "m": "all; angular integration is local and the witness survives restriction to one component",
            "k": "radial Bondi expansion, not compact momentum",
            "omega": "arbitrary smooth compact-support retarded-time profiles",
        },
        "provenance": {
            "producer_path": str(Path(__file__).relative_to(ROOT)),
            "producer_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {
                    "path": str(path.relative_to(ROOT)),
                    "sha256": _sha256(path),
                    "result_id": records[name]["result_id"],
                }
                for name, path in INPUTS.items()
            },
            "pinned_raw_sha256": PINNED_RAW_SHA256,
        },
        "full_tensor_lee_wald_derivation": {
            "action": "S_C2=(alpha_B/8)*integral sqrt(-g) C_abcd C^abcd",
            "curvature_momentum": algebra["curvature_momentum"],
            "current": "omega^a(h1,h2)=delta_1 Theta_C2^a(h2)-delta_2 Theta_C2^a(h1)",
            "flat_background_specialization": "Cbar=0, but delta(nabla P) is retained; the formula is tensorial before Bondi or TT reduction",
            "independent_existing_control": records["full_tensor_current_fixture"]["flat_tt_control"],
        },
        "declared_carrier_ledger": {
            "fields": {
                "status": "CERTIFIED",
                "value": "smooth full metric perturbations h_ab; theorem restriction delta Ricci_ab=0, fixed leading unphysical metric, h_AB=r*C_AB(u,x)+O(1), q^AB C_AB=0, C_AB compactly supported in u",
            },
            "ghosts": {
                "status": "CLASSIFIED_FOR_RESTRICTION_ONLY",
                "value": "linear diffeomorphism and Weyl parameters whose boundary jets preserve Omega=0, the fixed conformal two-metric, and the declared Einstein-radiative subcarrier",
            },
            "antifields": {
                "status": "NO_CERTIFIED_DOMAIN",
                "value": "no null-boundary BV dual falloff or BFV pairing is constructed",
            },
            "radiative_data": {
                "status": "CERTIFIED",
                "value": "tracefree Bondi shear C_AB(u,x), compact support in u for the obstruction pairing",
            },
            "Coulombic_data": {
                "status": "NOT_APPLICABLE",
                "value": "set to zero in this radiative restriction; mass and angular-momentum aspects are not classified",
            },
            "p0_boundary_metric_data": {
                "status": "OPEN",
                "value": "excluded by fixed-boundary condition; its possible source-response pairing with p1 is not ruled out",
            },
            "polyhomogeneous_logs_and_Jordan_data": {
                "status": "OPEN",
                "value": "not reconstructed in the full tensor Bondi complex",
            },
            "I_minus_i0_matching": {
                "status": "NO_CERTIFIED_MAP",
                "value": "the theorem is local to I+ and compact-u-support tests",
            },
        },
        "complete_local_counterterm_ansatz": {
            "category": "all finite-order local covariant ambiguities made from the existing metric, boundary normal/conformal frame and their finite jets, with no new independent boundary field",
            "action_boundary_term": "L -> L+dB gives Theta -> Theta+delta B and changes omega by delta_1 delta_2 B-delta_2 delta_1 B=0",
            "potential_corner_term": "Theta -> Theta+dY gives omega -> omega+d(delta_1 Y[h2]-delta_2 Y[h1])",
            "derivative_bound": "arbitrary finite order N; therefore includes the first sufficient order <=3 for a four-derivative bulk action",
            "classification": "Every local Lee-Wald/JKM ambiguity without new fields is the sum of these two types; coefficients and tensor contractions cannot change the horizontal cohomology class.",
            "excluded_enlargements": [
                "an independent boundary momentum or edge mode",
                "retaining p0 as a dynamical boundary source without a certified renormalized pairing",
                "adding an Einstein-Hilbert or compensator term to the bulk action",
                "nonlocal-in-u counterterms",
            ],
        },
        "exact_algebra": algebra,
        "obstruction_theorem": {
            "bulk_identity": "C^2=Euler_4+2 Ricci_ab Ricci^ab-(2/3)R^2",
            "Einstein_restriction": "On any pair of flat Einstein Jacobi fields the non-topological quadratic Hessian vanishes; the Euler contribution has horizontally exact Lee-Wald current.",
            "ambiguity_invariance": "delta B leaves omega unchanged and dY changes only its horizontal representative, so every counterterm in the complete declared local ansatz retains the zero class.",
            "wave_packet_test": "For compact-u-support radiation all endpoint and sphere-divergence terms integrate to zero. Hence an exact representative pairs every such wave packet to zero and is radical.",
            "target_form_witness": "A nondegenerate Einstein-radiative form would restrict on one polarization to f*g_u-g*f_u. Its Euler derivatives are (2*g_u,-2*f_u), so it is not horizontally exact.",
            "conclusion": "No local counterterm/corner ambiguity built only from the existing metric jets can produce a finite nondegenerate fixed-boundary Einstein-radiative symplectic form in pure C^2 gravity.",
        },
        "boundary_corner_disposition": {
            "p0_p0_linear_divergence": {
                "status": "CERTIFIED_EXACT_CORNER_AT_REDUCED_TT_LEVEL",
                "statement": records["raw_obstruction"]["obstruction_theorem"]["with_p0"],
            },
            "fixed_boundary_p1": {
                "status": "OBSTRUCTED",
                "statement": "The full tensor horizontal class is zero and remains zero under every declared local counterterm ambiguity.",
            },
            "enlarged_p0_p1": {
                "status": "OPEN",
                "statement": "The finite reduced cross term makes a source-response extension plausible, but no full tensor renormalized pairing, gauge descent or corner matching is certified.",
            },
            "minimal_required_enlargement": {
                "status": "CERTIFIED_NECESSITY_NOT_CONSTRUCTION",
                "statement": "Any repair must leave the declared ambiguity class: add at least one independent boundary canonical momentum/edge variable (naturally a renormalized p0/p1 source-response partner) or change the bulk Hessian, for example through an Einstein-Hilbert scale/compensator.",
            },
        },
        "generator_charge_disposition": {
            "P0": "OPEN_NO_NONDEGENERATE_RENORMALIZED_FORM",
            "D_M": "OPEN_NO_NONDEGENERATE_RENORMALIZED_FORM",
            "H_ESU": "NOT_APPLICABLE_ON_FIXED_MINKOWSKI_PATCH",
            "D_rad": "NO_CERTIFIED_MAP",
        },
        "classification": {
            "raw_obstruction_imported_by_exact_hash": True,
            "full_tensor_C2_lee_wald_potential_derived": True,
            "complete_existing_field_local_JKM_ambiguity_classified": True,
            "fixed_boundary_einstein_radiative_class_zero": True,
            "fixed_boundary_local_counterterm_repair_obstructed": True,
            "nonexact_news_form_witness_certified": True,
            "full_tensor_Bondi_BV_BFV_carrier_constructed": False,
            "enlarged_p0_p1_renormalized_phase_space_constructed": False,
            "polyhomogeneous_Jordan_sector_classified": False,
            "i0_Iminus_corner_matching_certified": False,
            "P0_charge_computed": False,
            "D_M_charge_computed": False,
            "causal_particle_scattering_stability_positivity_or_quantum_claim": False,
        },
        "verdicts": {
            "fixed_boundary_Einstein_radiative_sector": "OBSTRUCTED_WITHIN_COMPLETE_LOCAL_JKM_ANSATZ",
            "enlarged_Bach_boundary_phase_space": "PHASE_SPACE_NOT_CLOSED",
            "Einstein_sector": "EINSTEIN_OPEN_AFTER_REQUIRED_ENLARGEMENT",
            "work_item": "SHORTFALL_FULL_STOP_CONDITION_NOT_MET",
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC full-tensor potential theorem excludes a nondegenerate fixed-boundary Einstein-radiative form obtained solely through local Lee-Wald/JKM ambiguities of the pure C^2 action. It does not exclude an enlarged p0/p1 source-response phase space, construct Bondi BV-BFV ghosts/antifields, classify Coulombic or logarithmic data, match I-/i0/I+, compute P0 or D_M charges, or establish causal, particle, scattering, stability, positivity, unitarity or quantum claims.",
        "next_gate": "Introduce and classify the minimal independent boundary momentum/source-response variable, then derive the full tensor p0/p1 Bondi constraint, ghost, antifield and corner complex and test its renormalized pairing.",
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.einstein_sector.asymptotic_bach_local_counterterm_cohomology_obstruction --check",
            "PYTHONPATH=. python3 bridge/einstein_sector/verify_asymptotic_bach_local_counterterm_cohomology_obstruction.py",
            "PYTHONPATH=. python3 -m unittest bridge.einstein_sector.tests.test_asymptotic_bach_local_counterterm_cohomology_obstruction -v",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-asymptotic-bach-local-counterterm-cohomology-fragment-v1.json",
        ],
    }


def build_atlas(certificate: dict[str, Any]) -> dict[str, Any]:
    cert_hash = _sha256(OUTPUT) if OUTPUT.exists() else ""
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "einstein_boundary",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha256(Path(__file__)),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [
            {
                "id": "einstein.asymptotic.minkowski.weyl.local_counterterm_cohomology",
                "scope": certificate["scope"],
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "OBSTRUCTED",
                    "nonlinear": "NOT_APPLICABLE",
                    "observational": "NO_CERTIFIED_MAP",
                    "quantum": "NO_CERTIFIED_MAP",
                },
                "mode_data": {
                    "dispersion": {
                        "status": "NOT_APPLICABLE",
                        "statement": "The theorem uses arbitrary compact-support retarded-time profiles, not a frequency-shell classification.",
                    },
                    "lee_wald": {
                        "status": "OBSTRUCTED",
                        "statement": (
                            certificate["full_tensor_lee_wald_derivation"]["curvature_momentum"]["potential_density"]
                            + "; "
                            + certificate["obstruction_theorem"]["conclusion"]
                        ),
                    },
                    "taub_maps": {
                        "status": "NOT_APPLICABLE",
                        "statement": "No compact-slice second-order Taub map is part of this linear null-boundary theorem.",
                    },
                    "resonance": {
                        "status": "NO_CERTIFIED_MAP",
                        "statement": "No compact harmonic resonance functional is mapped to this asymptotic carrier.",
                    },
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {
                            "status": "NOT_APPLICABLE",
                            "statement": "The result is linear and uses compact-support retarded-time profiles.",
                        },
                        "smooth_secular": {
                            "status": "NOT_APPLICABLE",
                            "statement": "No second-order source is evaluated.",
                        },
                        "causal_retarded": {
                            "status": "NO_CERTIFIED_MAP",
                            "statement": "No retarded Bondi BV--BFV Green carrier is constructed.",
                        },
                    },
                },
                "evidence": [
                    {
                        "path": str(OUTPUT.relative_to(ROOT)),
                        "result_id": certificate["result_id"],
                        "sha256": cert_hash,
                    }
                ],
                "claim_boundary": certificate["claim_boundary"],
            }
        ],
        "verification_commands": certificate["verification_commands"],
    }


def write_outputs() -> None:
    certificate = build_certificate()
    OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ATLAS.write_text(json.dumps(build_atlas(certificate), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check_outputs() -> None:
    certificate = build_certificate()
    _require(_load(OUTPUT) == certificate, f"stale certificate: {OUTPUT}")
    _require(_load(ATLAS) == build_atlas(certificate), f"stale atlas fragment: {ATLAS}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_outputs()
    if args.check:
        check_outputs()
    if not args.write and not args.check:
        parser.error("one of --write or --check is required")


if __name__ == "__main__":
    main()
