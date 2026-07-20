"""Certify the locked k -> 2k exceptional/generic resonance family."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ARBITRARY_K_LOCKED_RESONANCE_V1.json"
ATLAS = ROOT / "residual_atlas/einstein-exceptional-arbitrary-k-locked-resonance-fragment.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-exceptional-arbitrary-k-locked-resonance-v1.schema.json"
INPUTS = {
    "join": ROOT / "bridge/certificates/einstein_maxwell_weyl_harmonic_sign_resonance_join.json",
    "exceptional_nonzero_k": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json",
    "k0_difference_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_ell2_extra_difference_matrix.json",
    "generic_polar": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "ell1_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
}


class LockedResonanceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise LockedResonanceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"expected object: {path}")
    return value


def _kinematics() -> dict[str, Any]:
    k = sp.symbols("k", real=True)
    mass_sq = sp.Rational(4, 3)
    omega = sp.sqrt(k**2 + mass_sq)
    output_omega = 2 * omega
    output_k = 2 * k
    target_p = sp.factor(output_omega**2 - output_k**2 - 6 + sp.Rational(2, 3))
    difference_omega = sp.factor(output_omega - omega)
    difference_k = sp.factor(output_k - k)
    exceptional_shell = sp.factor(difference_omega**2 - difference_k**2 - mass_sq)
    _require(target_p == 0, "doubled momentum left the ell=2 p shell")
    _require(exceptional_shell == 0, "difference momentum left the exceptional shell")
    rapidity = sp.symbols("eta", real=True)
    boost = sp.Matrix([[sp.cosh(rapidity), sp.sinh(rapidity)], [sp.sinh(rapidity), sp.cosh(rapidity)]])
    minkowski = sp.diag(1, -1)
    _require(sp.simplify(boost.T * minkowski * boost - minkowski) == sp.zeros(2), "boost covariance failed")
    _require(sp.simplify(boost.det()) == 1, "boost determinant changed")
    return {
        "exceptional_mass_squared": "4/3",
        "generic_ell2_extra_mass_squared": "16/3",
        "exceptional_frequency": "omega_e(k)=sqrt(k^2+4/3)",
        "locked_generic_frequency": "omega_2(2k)=sqrt((2k)^2+16/3)=2*omega_e(k)",
        "positive_positive_target_identity": "4*omega_e(k)^2-(2*k)^2-6+2/3=0",
        "difference_return_identity": "(2*omega_e(k)-omega_e(k))^2-(2*k-k)^2=4/3",
        "allowed_lattice_closure": "k=2*pi*n/L implies 2k=2*pi*(2n)/L on the same circumference background",
        "boost_matrix": [["cosh(eta)", "sinh(eta)"], ["sinh(eta)", "cosh(eta)"]],
        "boost_determinant": "1",
    }


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    _require(_sha256(INPUTS["join"]) == "723083a24436059f19ae70f53287e6141c58f54b27eae50064896fd12eba7fbb", "authoritative join hash changed")
    _require(records["join"]["classification"]["complete_branch_labelled_obstruction_map_joined"], "join theorem changed")
    _require(not records["join"]["classification"]["exceptional_generic_global_arbitrary_k_common_zero_classified"], "upstream already classified this cone")
    _require(records["exceptional_nonzero_k"]["classification"]["nonzero_k_exceptional_solution_cofiber_certified"], "exceptional nonzero-k input changed")
    _require(records["generic_polar"]["classification"]["canonical_extra_polar_quotient_two_p_summands"], "generic polar extra input changed")
    _require(records["ell1_current"]["classification"]["exceptional_extra_ell1_current_nonradical_positive_definite"], "exceptional current changed")
    sparse = records["k0_difference_matrix"]["sparse_matrix"]
    _require(sparse["axial_output"] == "R_ax=-(768/5)*conj(x_exceptional_axial)*y_extra_polar_e2", "axial rest coefficient changed")
    _require(sparse["polar_output"] == "R_pol=-(864/5)*conj(x_exceptional_polar)*y_extra_polar_e2", "polar rest coefficient changed")
    _require(records["k0_difference_matrix"]["classification"]["six_adjoint_columns_zero"], "rest zero columns changed")
    _require(records["k0_difference_matrix"]["classification"]["two_adjoint_columns_nonzero"], "rest nonzero columns changed")

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "einstein-maxwell-weyl-exceptional-arbitrary-k-locked-resonance-v1",
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ARBITRARY_K_LOCKED_RESONANCE_V1",
        "result_state": "FIRST_ARBITRARY_K_EXCEPTIONAL_GENERIC_CROSS_FIBRE_FUNCTIONAL_CERTIFIED_CANCELLATION_GEOMETRY_OPEN",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_LOCKED_EXCEPTIONAL_ELL1_K_BY_GENERIC_ELL2_2K_FAMILY",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "one fixed closed S1_L times S2; no circumference identification",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "one exceptional ell=1 extra mode at allowed k crossed with the Lorentz-transported ell=2 polar-extra multiplicity at 2k",
            "degree": 2,
            "parity": "all four exceptional/generic parity pairs and both transported ell2 extra multiplicities",
            "ell": "1 x 2 -> L=1 difference and L=2 positive-positive blocks",
            "m": "axisymmetric coefficient matrix; all-m tensor cancellation remains open",
            "k": "every allowed k=2*pi*n/L with its distinct locked 2k fibre",
            "omega": "omega_e(k), 2*omega_e(k), and their exact difference omega_e(k)",
        },
        "kinematics": _kinematics(),
        "covariant_transport_lemma": {
            "statement": "Apply the same proper SO(1,1) boost to the rest exceptional representative, the rest ell2-extra representative, the target row basis and its adjoint covectors. Naturality of the local Weyl-Maxwell Euler operator makes the bilinear source map intertwine these invertible transformations.",
            "coefficient_consequence": "in the transported row/covector normalization, every adjoint coefficient equals its certified rest coefficient",
            "periodicity": "the boost is used only as an algebraic tensor transport of polarization coefficients; the transported fields retain exp(-i*omega*t+i*k*x), and allowed k and 2k are periodic on the original circle",
            "not_claimed": "the boost is not asserted to be a global automorphism of the compact quotient and no modes or circumference backgrounds are identified",
            "normalized_defect": "0",
        },
        "locked_difference_matrix": {
            "input_order": records["k0_difference_matrix"]["input_order"],
            "six_zero_columns": True,
            "nonzero_columns": {
                "axial_L1_output": "R_ax(k)=-(768/5)*conj(x_exceptional_axial(k))*y_boosted_extra_polar_e2(2k)",
                "polar_L1_output": "R_pol(k)=-(864/5)*conj(x_exceptional_polar(k))*y_boosted_extra_polar_e2(2k)",
            },
            "rank_per_output_parity": 1,
            "coefficients_nonzero_for_every_real_k": True,
            "output_block": "(L=1,M=0,K=k,Omega=omega_e(k),output parity)",
        },
        "cross_fibre_functional": {
            "bounded_ledger_location": "R_(L=1,M=0,K=k,Omega=omega_e(k),parity)",
            "restriction_to_locked_two_mode_carrier": "the two displayed monomials are necessary and sufficient for this difference-channel projection to vanish",
            "enlarged_carrier": "other exceptional, generic and global inputs can share the same output labels; their complete coefficients and simultaneous cancellations are not classified",
            "common_zero_geometry": "OPEN",
            "first_unclassified_row": "the all-m completion of R_ax(k),R_pol(k) jointly with exceptional self-doubling, a/d, twist, moment-map and other wave-pair terms",
        },
        "coverage_ledger": {
            "circumference_c_times_every_exceptional_oscillator": "CERTIFIED upstream for all k",
            "electric_Qe_and_Wilson_Wx_times_every_exceptional_oscillator": "CERTIFIED upstream for all k",
            "a_and_d_times_exceptional": "CERTIFIED only at k=0; arbitrary-k polynomial columns OPEN",
            "constant_twist_position_times_exceptional": "OPEN",
            "twist_velocity_times_exceptional": "OPEN",
            "exceptional_times_generic": "this certificate covers the first exact locked ell2-extra 2k family; all other branch/momentum pairs OPEN",
            "multiple_abs_momentum_union": "OPEN",
        },
        "classification": {
            "authoritative_join_imported_by_exact_hash": True,
            "same_background_lattice_closure_certified": True,
            "arbitrary_k_locked_shell_collision_certified": True,
            "eight_column_axisymmetric_rest_matrix_transport_certified": True,
            "two_nonzero_locked_adjoint_functionals_certified": True,
            "first_exact_cross_fibre_functional_exported": True,
            "all_exceptional_cross_columns_computed": False,
            "all_m_tensor_assembled": False,
            "enlarged_common_zero_geometry_classified": False,
            "multiple_abs_momentum_full_cone_classified": False,
            "causal_all_orders_residual_observer_particle_quantum_claim": False,
        },
        "provenance": {
            "producer_path": str(Path(__file__).relative_to(ROOT)),
            "producer_sha256": _sha256(Path(__file__)),
            "schema_path": str(SCHEMA.relative_to(ROOT)),
            "schema_sha256": _sha256(SCHEMA),
            "inputs": {
                name: {
                    "path": str(path.relative_to(ROOT)),
                    "result_id": records[name]["result_id"],
                    "sha256": _sha256(path),
                }
                for name, path in INPUTS.items()
            },
        },
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_arbitrary_k_locked_resonance --check",
            "PYTHONPATH=. python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_arbitrary_k_locked_resonance.py",
            "PYTHONPATH=. python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_arbitrary_k_locked_resonance -v",
        ],
        "next_gate": "compute the arbitrary-k a/d and twist exceptional columns, then assemble the all-m locked tensor and its cancellations with every source sharing the L1,k,omega_e output block",
        "claim_boundary": "This is the first exact same-background arbitrary-k exceptional/generic cross-fibre R-functional. It is not the complete exceptional cross-column matrix or bounded cone. It does not identify circumference backgrounds or imply an infinite-harmonic, causal, all-orders, residual, observer, particle, positivity or quantum statement.",
    }


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def build_atlas(certificate: dict[str, Any]) -> dict[str, Any]:
    evidence = {
        "path": str(OUTPUT.relative_to(ROOT)),
        "result_id": certificate["result_id"],
        "sha256": hashlib.sha256(_render(certificate).encode()).hexdigest(),
    }
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
                "id": "einstein.ph.wm.interaction.exceptional_arbitrary_k_locked_resonance",
                "scope": certificate["scope"],
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "CERTIFIED",
                    "nonlinear": "OPEN",
                    "observational": "NO_CERTIFIED_MAP",
                    "quantum": "NO_CERTIFIED_MAP",
                },
                "mode_data": {
                    "dispersion": {
                        "status": "CERTIFIED",
                        "statement": "The same-background lattice relation (omega_2,2k)=2(omega_e,k) is exact for every allowed k.",
                    },
                    "lee_wald": {
                        "status": "CERTIFIED",
                        "statement": "Nonradical exceptional and generic-extra blocks support the transported adjoint projection.",
                    },
                    "taub_maps": {
                        "status": "OPEN",
                        "statement": "The five moment maps have not been intersected with the complete arbitrary-k cross-column ideal.",
                    },
                    "resonance": {
                        "status": "CERTIFIED",
                        "statement": "Two locked exceptional-by-ell2-extra difference columns are nonzero for every allowed k; six are zero in the transported axisymmetric basis.",
                    },
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {
                            "status": "OPEN",
                            "statement": "The first exact cross-fibre R row is exported, but its enlarged all-m cancellation geometry is unclassified.",
                        },
                        "smooth_secular": {
                            "status": "CERTIFIED",
                            "statement": "The imported complete finite-harmonic smooth-secular theorem supplies a finite secular primitive after the stabilizer moments vanish.",
                        },
                        "causal_retarded": {
                            "status": "NO_CERTIFIED_MAP",
                            "statement": "No causal/retarded compact-product Green carrier is certified.",
                        },
                    },
                },
                "evidence": [evidence],
                "claim_boundary": certificate["claim_boundary"],
            }
        ],
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_arbitrary_k_locked_resonance --check",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-exceptional-arbitrary-k-locked-resonance-fragment.json",
            "PYTHONPATH=. python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_arbitrary_k_locked_resonance.py",
        ],
    }


def verify_output() -> None:
    value = build_certificate()
    atlas = build_atlas(value)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    _require(OUTPUT.read_text(encoding="utf-8") == _render(value), "certificate is stale")
    _require(ATLAS.read_text(encoding="utf-8") == _render(atlas), "atlas fragment is stale")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        verify_output()
        print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ARBITRARY_K_LOCKED_RESONANCE_V1: PASS")
    else:
        certificate = build_certificate()
        OUTPUT.write_text(_render(certificate), encoding="utf-8")
        ATLAS.write_text(_render(build_atlas(certificate)), encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(ROOT)}")
        print(f"wrote {ATLAS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
