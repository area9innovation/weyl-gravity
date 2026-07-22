"""Produce the Phase-3 Schwarzschild boundary/flux contract.

This module is a canonicalizer, not a radial solver.  It freezes the objects
that must exist before a horizon-to-infinity connection matrix can be called
a scattering matrix.  Frozen Phase-2 artifacts are consumed by content hash;
their producers are never imported or rerun here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import sympy as sp


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificate.json"
ATLAS = ROOT / "residual_atlas/phase3-black-hole-boundary-flux-contract-fragment-v1.json"

INPUTS = {
    "phase3_pilot_domain": ROOT / "notes/phase3-axial-pilot-domain-freeze-2026-07-22.md",
    "phase2_join": ROOT / "black_hole_programme/phase2/generic_l_synthesis/certificate.json",
    "axial_formal_module": ROOT / "black_hole_programme/phase2/general_l_axial_selection/certificate.json",
    "axial_einstein_current": ROOT / "black_hole_programme/phase2/general_l_axial_current/certificate.json",
    "polar_formal_module": ROOT / "black_hole_programme/phase2/general_l_polar_extendible_current_closure/certificate.json",
    "polar_exceptional_polynomial": ROOT / "black_hole_programme/phase2/general_l_polar_extendible_current_closure/current_artifacts/q21-finite-line-factor.json",
    "omega_zero_classification": ROOT / "black_hole_programme/certificates/BH2_OMEGA_ZERO.json",
    "lee_wald_engine": ROOT / "black_hole_programme/linearized_theta.py",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2) + "\n"


def rational_matrix(rows: Sequence[Sequence[int | str]]) -> sp.Matrix:
    return sp.Matrix([[sp.Rational(x) for x in row] for row in rows])


def canonicalize_boundary_pairing(
    divergent_map: Sequence[Sequence[int | str]],
    flux_form: Sequence[Sequence[int | str]],
    basis_change: Sequence[Sequence[int | str]],
) -> dict[str, Any]:
    """Return exact rank data before and after an invertible basis change.

    Coordinates transform as ``old = B new``.  Hence ``D' = D B`` and
    ``J' = B^T J B`` on this real rational control.  The physical construction
    uses conjugate transpose over the real-frequency complex shell.
    """

    D = rational_matrix(divergent_map)
    J = rational_matrix(flux_form)
    B = rational_matrix(basis_change)
    if B.rows != B.cols or B.det() == 0:
        raise ValueError("basis change must be square and invertible")
    if D.cols != B.rows or J.shape != (B.rows, B.rows):
        raise ValueError("incompatible boundary dimensions")
    Dp = D * B
    Jp = B.T * J * B
    finite_dim = B.rows - D.rank()
    finite_dim_p = B.rows - Dp.rank()
    # The control has D=0, so the restricted radical is ker J.  General
    # finite-subspace restriction is part of the mathematical contract below.
    radical_dim = B.rows - J.rank()
    radical_dim_p = B.rows - Jp.rank()
    return {
        "basis_dimension": B.rows,
        "basis_determinant": str(B.det()),
        "divergent_rank_before": D.rank(),
        "divergent_rank_after": Dp.rank(),
        "finite_dimension_before": finite_dim,
        "finite_dimension_after": finite_dim_p,
        "flux_rank_before": J.rank(),
        "flux_rank_after": Jp.rank(),
        "radical_dimension_before": radical_dim,
        "radical_dimension_after": radical_dim_p,
        "quotient_dimension_before": finite_dim - radical_dim,
        "quotient_dimension_after": finite_dim_p - radical_dim_p,
        "D_prime": [[str(v) for v in Dp.row(i)] for i in range(Dp.rows)],
        "J_prime": [[str(v) for v in Jp.row(i)] for i in range(Jp.rows)],
    }


def symbolic_invariance_witness() -> dict[str, str]:
    a, b, c, p, q, r, s = sp.symbols("a b c p q r s")
    J = sp.Matrix([[a, b], [b, c]])
    B = sp.Matrix([[p, q], [r, s]])
    determinant_defect = sp.factor((B.T * J * B).det() - B.det() ** 2 * J.det())
    x1, x2 = sp.symbols("x1 x2")
    x = sp.Matrix([x1, x2])
    radical_transport_defect = sp.simplify(
        (B.T * J * B) * (B.inv() * x) - B.T * J * x
    )
    d1, d2 = sp.symbols("d1 d2")
    D = sp.Matrix([[d1, d2]])
    finite_transport_defect = sp.simplify((D * B) * (B.inv() * x) - D * x)
    assert determinant_defect == 0
    assert radical_transport_defect == sp.zeros(2, 1)
    assert finite_transport_defect == sp.zeros(1, 1)
    return {
        "determinant_congruence": "det(B^T J B)=det(B)^2 det(J)",
        "determinant_defect": "0",
        "finite_kernel_transport": "ker(D B)=B^{-1} ker(D)",
        "finite_transport_defect": "0",
        "radical_transport": "ker(B^T J B)=B^{-1} ker(J) for invertible B",
        "radical_transport_defect": "[0,0]^T",
    }


def build_certificate() -> dict[str, Any]:
    phase2 = json.loads(INPUTS["phase2_join"].read_text())
    axial = json.loads(INPUTS["axial_formal_module"].read_text())
    omega_zero = json.loads(INPUTS["omega_zero_classification"].read_text())
    snapshots = {
        name: {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
        for name, path in INPUTS.items()
    }
    control = canonicalize_boundary_pairing(
        [[0, 0]], [[2, 1], [1, 0]], [[1, 2], [3, 5]]
    )
    assert control["finite_dimension_before"] == control["finite_dimension_after"]
    assert control["flux_rank_before"] == control["flux_rank_after"]
    assert control["quotient_dimension_before"] == control["quotient_dimension_after"]

    return {
        "schema": "phase3-black-hole-boundary-flux-contract-v1",
        "result_id": "PURE_WEYL_PHASE3_BOUNDARY_FLUX_CONTRACT_V1",
        "result_token": "BOUNDARY_FLUX_CONTRACT_DEFINED_GLOBAL_CHANNEL_SPACE_UNPOPULATED",
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "strict four-dimensional pure Weyl gravity S=alpha_W integral sqrt(-g) C_abcd C^abcd, alpha_W!=0",
            "background": "maximally extended Schwarzschild exterior pieces with M>0",
            "dimensionless_variables": "hat_r=r/M and hat_omega=M*omega",
            "mode_domain": "integer ell>=2; real nonzero hat_omega on the radiative strata; omega=0 is a separate static stratum",
            "fields": "complexified metric perturbations h_ab with the real-field involution pairing (ell,m,omega) with (ell,-m,-omega)",
            "gauge_group": "linearized diffeomorphisms h->h+L_xi g and Weyl shifts h->h+2 sigma g",
            "pilot_domain": {
                "parity": "axial",
                "ell": 2,
                "hat_omega_interval": ["1/2", "3/4"],
                "legacy_fixture_inside": "3/5",
                "negative_frequency_rule": "derived only by the declared real-field involution after the positive-frequency contract is verified",
                "omega_zero": "excluded and treated as a separate static stratum",
            },
        },
        "action_derived_current": {
            "E_tensor": "E^{abcd}=2 alpha_W C^{abcd}",
            "theta": "theta^a(h)=2 E^{abcd} nabla_d h_bc - 2 h_bc nabla_d E^{abcd}",
            "presymplectic_current": "omega^a(h1,h2)=delta_1 theta^a(h2)-delta_2 theta^a(h1), including density variation",
            "real_frequency_hermitian_flux": "J_B(h1,h2)=i integral_B omega^a(conj(h1),h2) dSigma_a",
            "representative": "the frozen LinearizedTheta representative; closed-sphere angular exact forms integrate to zero, while unrestricted radial/corner improvements remain unquotiented",
            "orientation": {
                "boundary_identity": "J_Hplus + J_Iplus - J_Hminus - J_Iminus = 0",
                "outgoing": ["Hplus", "Iplus"],
                "incoming": ["Hminus", "Iminus"],
                "convention": "future boundary components carry plus orientation and past boundary components minus orientation in the Stokes boundary of an exterior scattering diamond",
            },
        },
        "mathematical_contract": {
            "endpoint_labels": {
                "Hplus": "future event horizon; future-regular data are smooth/polyhomogeneous in ingoing EF coordinates and the phase e^{-i omega v}",
                "Hminus": "past event horizon; past-regular data are smooth/polyhomogeneous in outgoing EF coordinates and the phase e^{-i omega u}",
                "Iplus": "future null infinity; outgoing data use retarded time u=t-r_*",
                "Iminus": "past null infinity; incoming data use advanced time v=t+r_*",
            },
            "reconstruction_class": "A curvature carrier psi=delta Ric[h] is admitted only with a metric lift satisfying every original linearized Ricci row, the chosen local gauge conditions, the declared endpoint polyhomogeneous class and finite action-derived boundary flux. Homogeneous Einstein additions are retained as lift freedom, not silently set to zero.",
            "small_gauge_subspace": "Gauge parameters that preserve the endpoint class and have vanishing boundary Hamiltonian are quotiented. Large or charged endpoint symmetries are retained and classified separately.",
            "divergent_map": "For endpoint B, D_B maps a formal endpoint jet to all nonintegrable coefficients of its action-derived current against every admitted test jet.",
            "finite_space": "F_B=ker D_B inside the reconstructed endpoint solution space modulo small gauge.",
            "radical": "R_B={x in F_B: J_B(x,y)=0 for every y in F_B}.",
            "physical_endpoint_space": "P_B=F_B/R_B. Inertia is reported only for the induced Hermitian form on P_B, never for the antisymmetric real Lee-Wald form itself.",
            "incoming_space": "P_in=P_Hminus direct_sum P_Iminus",
            "outgoing_space": "P_out=P_Hplus direct_sum P_Iplus",
            "connection_vs_scattering": "A local-basis connection T is not a scattering matrix. S is defined only as the trace relation P_in->P_out of global exterior solutions after gauge, divergent and radical quotients, with existence and uniqueness established.",
            "conservation_gate": "For a connection written a_out=T a_in in compatible endpoint bases, the required identity is T^dagger J_out T=J_in, with the above orientations.",
        },
        "exceptional_strata": {
            "omega_zero": {
                "disposition": "SEPARATE_STATIC_STRATUM_NOT_IMPORTED_BY_CONTINUITY",
                "imported_result": omega_zero["result_id"],
                "remaining": omega_zero["missing_objects"],
            },
            "algebraically_special_or_repeated_root": "Any vanishing pivot, repeated indicial root, logarithmic partner, normalization pole or rank change defines a separate stratum. No division by the vanishing factor and no generic-rank continuation is allowed.",
            "polar_Q21": {
                "locus": "R_ell(hat_omega^2)=Q21(ell(ell+1),hat_omega^2)=0",
                "disposition": "the first finite p=-2 induced form vanishes; the deeper filtration and global meaning remain open",
                "not_a_second_wall": True,
            },
            "axial_imported": {
                "E0_X0_domain_exceptional_set": phase2["axial_phase"]["exceptional_set"],
                "X2": "UNCLASSIFIED",
            },
        },
        "basis_invariance": {
            "theorem": "For every invertible endpoint basis change B, D transforms to D B and J to B^dagger J B. Therefore F, R and P transform by B^{-1}; their dimensions, form rank and Hermitian inertia are invariant. Connection matrices transform contragrediently and the conservation defect transforms by congruence.",
            "symbolic_witness": symbolic_invariance_witness(),
            "independent_rational_control": control,
        },
        "phase2_application": {
            "imported_axial_basis": ["E0", "X0"],
            "formal_infinity_finiteness": {
                "E0": "finite nonzero r^-2 fixed-representative current",
                "X0": "finite X0|X0 and nonzero finite E0|X0 in the corrected all-orders formal class",
                "lift_shift": axial["literal_current"]["shift_invariance"],
            },
            "basis_invariant_statement": "The existence and dimension of the formal finite span generated by E0 and X0 are unchanged under every invertible mixing of those two imported representatives. This does not compute its full finite Hermitian Gram matrix or endpoint radical.",
            "first_exact_nondefinition": "Phase 2 provides no four-endpoint trace maps, no globally matched exterior solution relation and no convergent/wave-packet topology. Consequently P_in, P_out, T and S cannot yet be populated from the imported artifacts.",
            "global_channel_status": "UNPOPULATED_NOT_ZERO",
        },
        "input_snapshot": snapshots,
        "claim_flags": {
            "boundary_flux_contract_defined": True,
            "basis_invariance_proved": True,
            "phase2_formal_infinity_module_imported": True,
            "global_endpoint_spaces_populated": False,
            "connection_matrix_constructed": False,
            "scattering_matrix_constructed": False,
            "flux_inertia_computed": False,
            "stability_or_CPT_established": False,
        },
        "does_not_establish": [
            "convergence or summability of the Phase-2 formal radial series",
            "generic-ell horizon bases or any horizon-to-infinity matching",
            "a nonzero or zero additional global scattering channel",
            "a scattering matrix, QNM spectrum or time-domain evolution estimate",
            "positive energy, quantum norm, CPT metric, particles, unitarity or stability",
            "the axial X2 disposition or the deeper polar filtration on Q21=0",
        ],
        "verification": {
            "producer": "python3 -m black_hole_programme.phase3.boundary_flux_contract.produce --check",
            "independent": "python3 -m black_hole_programme.phase3.boundary_flux_contract.verify",
            "tests": "python3 -m unittest black_hole_programme.phase3.boundary_flux_contract.tests.test_contract -v",
            "atlas": "python3 residual_atlas/validate_fragment.py residual_atlas/phase3-black-hole-boundary-flux-contract-fragment-v1.json",
        },
    }


def build_atlas(cert: dict[str, Any]) -> dict[str, Any]:
    evidence_path = str(CERTIFICATE.relative_to(ROOT))
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "black_hole",
        "generated_by": str(Path(__file__).resolve().relative_to(ROOT)),
        "generated_by_sha256": sha256(Path(__file__).resolve()),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [
            {
                "id": "black_hole.schwarzschild.phase3.boundary_flux_contract",
                "scope": {
                    "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
                    "background": "Schwarzschild exterior, M>0",
                    "boundaries": "Hplus, Hminus, Iplus and Iminus contract; no global traces populated",
                    "charge_sector": "small endpoint gauge quotient; large or charged symmetries retained",
                    "carrier": "formal endpoint solution data reconstructed to metric perturbations",
                    "degree": 1,
                    "parity": "axial pilot; contract also names the future polar strata",
                    "ell": "pilot ell=2; abstract contract for integer ell>=2",
                    "m": "real-field conjugate harmonic pairs",
                    "k": "radial endpoint jets",
                    "omega": "pilot hat_omega in [1/2,3/4]; omega=0 separate",
                },
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "CERTIFIED",
                    "nonlinear": "NOT_APPLICABLE",
                    "observational": "NO_CERTIFIED_MAP",
                    "quantum": "NO_CERTIFIED_MAP",
                },
                "mode_data": {
                    "dispersion": {"status": "OPEN", "statement": "Complete four-endpoint bases and global exterior traces are not yet constructed."},
                    "lee_wald": {"status": "CERTIFIED", "statement": "The action-derived current, endpoint orientation, finite subspace, radical quotient and basis-covariance laws are frozen exactly."},
                    "taub_maps": {"status": "NOT_APPLICABLE", "statement": "No compact second-order Taub map enters this linear boundary contract."},
                    "resonance": {"status": "OPEN", "statement": "omega=0, repeated-root strata and the polar Q21 locus are separated rather than filled by generic continuation."},
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {"status": "NOT_APPLICABLE", "statement": "No nonlinear source is evaluated."},
                        "smooth_secular": {"status": "NOT_APPLICABLE", "statement": "No nonlinear correction is evaluated."},
                        "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No retarded Green operator or global scattering map is constructed."},
                    },
                },
                "evidence": [{"path": evidence_path, "result_id": cert["result_id"], "sha256": sha256(CERTIFICATE)}],
                "claim_boundary": "The boundary/flux quotient contract and its basis invariance are certified. The imported Phase-2 formal infinity module does not populate global endpoint traces, a connection matrix, scattering channels, flux inertia, stability or CPT data.",
            }
        ],
        "verification_commands": [
            "python3 -m black_hole_programme.phase3.boundary_flux_contract.produce --check",
            "python3 -m black_hole_programme.phase3.boundary_flux_contract.verify",
            "python3 residual_atlas/validate_fragment.py residual_atlas/phase3-black-hole-boundary-flux-contract-fragment-v1.json",
        ],
    }


def write_or_check(path: Path, text: str, check: bool) -> None:
    if check:
        if not path.exists() or path.read_text() != text:
            raise SystemExit(f"REFUSED: stale generated artifact {path.relative_to(ROOT)}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    cert = build_certificate()
    write_or_check(CERTIFICATE, canonical_json(cert), args.check)
    # The atlas hashes the already-written canonical certificate.
    if not args.check:
        cert = json.loads(CERTIFICATE.read_text())
    atlas = build_atlas(cert)
    write_or_check(ATLAS, canonical_json(atlas), args.check)


if __name__ == "__main__":
    main()
