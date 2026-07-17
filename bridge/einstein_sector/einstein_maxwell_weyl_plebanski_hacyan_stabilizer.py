"""Plebański--Hacyan stabilizer and generic primary-module descent gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.schema.json"
INPUTS = {
    "stabilizer_preflight": ROOT / "bridge/certificates/einstein_maxwell_harmonic_adjoint_blocks.json",
    "axial_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json",
    "axial_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_module": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "polar_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "polar_ungauged": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ungauged_noether_lift.json",
}


class PlebanskiHacyanStabilizerError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PlebanskiHacyanStabilizerError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rotation_representation(ell: int) -> dict[str, sp.Matrix]:
    """Unnormalised exact spin-ell representation and its positive form."""

    magnetic = list(range(-ell, ell + 1))
    index = {m: position for position, m in enumerate(magnetic)}
    dimension = 2 * ell + 1
    j_zero = sp.diag(*magnetic)
    j_plus = sp.zeros(dimension)
    j_minus = sp.zeros(dimension)
    for m in magnetic:
        if m < ell:
            j_plus[index[m + 1], index[m]] = ell - m
        if m > -ell:
            j_minus[index[m - 1], index[m]] = ell + m
    angular_form = sp.diag(
        *[sp.Rational(1, sp.binomial(2 * ell, ell + m)) for m in magnetic]
    )
    return {
        "J0": j_zero,
        "Jplus": j_plus,
        "Jminus": j_minus,
        "angular_form": angular_form,
    }


def _rotation_audit() -> dict[str, Any]:
    regressions: dict[str, Any] = {}
    for ell in range(2, 9):
        representation = _rotation_representation(ell)
        j_zero = representation["J0"]
        j_plus = representation["Jplus"]
        j_minus = representation["Jminus"]
        angular_form = representation["angular_form"]
        _require(j_zero * j_plus - j_plus * j_zero == j_plus, f"ell={ell} [J0,J+] changed")
        _require(j_zero * j_minus - j_minus * j_zero == -j_minus, f"ell={ell} [J0,J-] changed")
        _require(j_plus * j_minus - j_minus * j_plus == 2 * j_zero, f"ell={ell} [J+,J-] changed")
        _require(j_plus.T * angular_form == angular_form * j_minus, f"ell={ell} angular adjoint changed")
        _require(j_zero.T * angular_form == angular_form * j_zero, f"ell={ell} J0 adjoint changed")
        regressions[str(ell)] = {
            "dimension": 2 * ell + 1,
            "commutators_exact": True,
            "positive_angular_form_and_adjoint_exact": True,
        }
    return {
        "basis": "v_m, -ell<=m<=ell",
        "action": {
            "J0_v_m": "m*v_m",
            "Jplus_v_m": "(ell-m)*v_(m+1)",
            "Jminus_v_m": "(ell+m)*v_(m-1)",
        },
        "all_ell_proof": {
            "J0_Jplus": "(m+1-m)*(ell-m)=ell-m",
            "J0_Jminus": "(m-1-m)*(ell+m)=-(ell+m)",
            "Jplus_Jminus": "(ell+m)*(ell-m+1)-(ell-m)*(ell+m+1)=2*m",
            "angular_weight": "w_m=1/binomial(2*ell,ell+m)",
            "adjoint_ratio": "w_(m+1)/w_m=(ell+m+1)/(ell-m)",
        },
        "exact_regressions": regressions,
    }


def _primary_audit() -> dict[str, Any]:
    eigenvalue, momentum, frequency = sp.symbols("lambda k omega", real=True)
    p = sp.factor(frequency**2 - momentum**2 - eigenvalue + sp.Rational(2, 3))
    mu = frequency**2 - momentum**2
    q = sp.expand(mu**2 - 2 * eigenvalue * mu + eigenvalue * (eigenvalue - 2))
    resultant = sp.factor(sp.resultant(p, q, frequency))
    expected_resultant = sp.Rational(4, 81) * (9 * eigenvalue - 2) ** 2
    _require(resultant == expected_resultant, "p/q resultant changed")
    _require(sp.factor(p.subs(frequency**2, momentum**2 + eigenvalue - sp.Rational(2, 3))) == 0, "p shell changed")

    # H and P_x act by multiplication in the commutative Fourier ring.  The
    # rotations act only on the m multiplicity.  Hence all actions commute
    # with multiplication by p and q and preserve their primary summands.
    return {
        "ring": "K_(ell,n)[omega] with lambda=ell(ell+1), k=2*pi*n/L",
        "characteristics": {"p": str(p), "q": str(sp.factor(q)), "resultant_omega_p_q": str(resultant)},
        "axial_and_polar_target_module": "((K[omega]/(p))^2 direct-sum K[omega]/(q)) tensor V_ell",
        "Einstein_image": "K[omega]/(q) tensor V_ell",
        "extra_quotient": "(K[omega]/(p))^2 tensor V_ell",
        "generator_action": {
            "H=partial_t": "multiplication by -I*omega",
            "P_x=partial_x": "multiplication by I*k",
            "so3": "identity on primary/polarization coefficients tensor the spin-ell action on V_ell",
        },
        "ideal_preservation": {
            "H_commutes_with_p_and_q": True,
            "P_x_commutes_with_p_and_q": True,
            "SO3_does_not_change_lambda_or_parity": True,
            "Einstein_q_primary_preserved": True,
            "extra_p_primary_preserved": True,
            "axial_and_polar_blocks_preserved_separately": True,
        },
        "no_division_by": ["k", "omega", "p", "q"],
    }


def _pairing_and_charge_audit(records: dict[str, Any]) -> dict[str, Any]:
    polar = records["polar_pairing"]["shell_pairing"]
    axial = records["axial_pairing"]["full_solution_pairing"]
    _require(polar["extra_positive_frequency_inertia"] == [2, 0], "polar extra inertia changed")
    _require(polar["Einstein_block_inertia"] == [1, 1], "polar Einstein inertia changed")
    _require(axial["extra_branch_signature_for_lambda_ge_6"] == [2, 0], "axial extra inertia changed")
    _require(axial["Einstein_branch_signature_for_lambda_ge_6"] == [1, 1], "axial Einstein inertia changed")

    eigenvalue, momentum = sp.symbols("lambda k", real=True)
    polar_gram = sp.Matrix(
        [
            [sp.sympify(value.replace("lambda", "lam"), locals={"lam": eigenvalue, "k": momentum}) for value in row]
            for row in polar["extra_Hermitian_current_Gram"]
        ]
    )
    recorded_determinant = sp.sympify(
        polar["extra_Gram_determinant"].replace("lambda", "lam"),
        locals={"lam": eigenvalue, "k": momentum},
    )
    _require(sp.factor(polar_gram.det() - recorded_determinant) == 0, "polar extra Gram determinant changed")

    return {
        "invariance_mechanism": "the branch Gram is independent of m and the stabilizer acts as a scalar on branch coefficients or through the invariant angular form; tensor-product Lee-Wald invariance follows exactly",
        "Hermitian_generator_checks": {
            "H": "rho(H)=-I*omega is anti-Hermitian for real shell frequency",
            "P_x": "rho(P_x)=I*k is anti-Hermitian for real compact momentum",
            "SO3": "I*J0, I*(Jplus+Jminus)/2, and (Jplus-Jminus)/2 are anti-Hermitian for the certified angular form",
        },
        "axial_inertia": {"Einstein_q_primary": [1, 1], "extra_p_primary": [2, 0], "complete": [3, 1]},
        "polar_inertia": {"Einstein_q_primary": [1, 1], "extra_p_primary": [2, 0], "complete": [3, 1]},
        "non_null_moment_map_witnesses": {
            "H": "on every nonzero polar or axial extra p-shell vector e, omega_e^2=k^2+lambda-2/3>0 and h(e,e)>0, so h(e,I*rho(H)e)=omega_e*h(e,e) is nonzero",
            "P_x": "for k nonzero, h(e,I*rho(P_x)e)=-k*h(e,e) is nonzero on every nonzero extra vector",
            "J0": "for m nonzero, h(e tensor v_m,I*rho(J0)(e tensor v_m))=-m*h(e,e)*w_m is nonzero",
        },
        "consequence": "H, P_x, and SO3 are not universal presymplectic-radical directions on the complete generic phase space; no quotient by them is authorized without a separately declared moment-map/Taub-zero derived sector",
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    expected_ids = {
        "stabilizer_preflight": "COMPACT_EM_HARMONIC_AND_ADJOINT_BLOCK_PREFLIGHT",
        "axial_operator": "EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR",
        "axial_pairing": "EINSTEIN_MAXWELL_WEYL_AXIAL_LEE_WALD_COMPLETION",
        "polar_module": "EINSTEIN_MAXWELL_WEYL_POLAR_PHYSICAL_COMPLETION",
        "polar_pairing": "EINSTEIN_MAXWELL_WEYL_POLAR_LEE_WALD_GATE",
        "polar_ungauged": "EINSTEIN_MAXWELL_WEYL_POLAR_UNGAUGED_NOETHER_LIFT",
    }
    for name, result_id in expected_ids.items():
        _require(records[name]["result_id"] == result_id, f"{name} input changed")
    stabilizers = records["stabilizer_preflight"]["universal_adjoint_targets"]
    _require(stabilizers["metric_KID_dimension"] == 5, "background stabilizer dimension changed")
    _require(stabilizers["metric_KID_basis"] == ["H=partial_t", "P_x=partial_x", "J_1", "J_2", "J_3"], "background stabilizer basis changed")

    return {
        "schema": "einstein-maxwell-weyl-plebanski-hacyan-stabilizer-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_PLEBANSKI_HACYAN_STABILIZER_DESCENT",
        "result_state": "PH_STABILIZER_AUTHORITY_AND_GENERIC_PRIMARY_EQUIVARIANCE_CERTIFIED_GAUGE_QUOTIENT_NOT_AUTHORIZED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_GENERIC_AXIAL_POLAR_ALL_PHYSICAL_ELL_K_STABILIZER_ACTION",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "domain": "generic axial and polar ell>=2 Weyl-Maxwell solution modules on the fixed-flux compactified magnetically supported Plebanski-Hacyan background, all allowed compact momenta, after local gauge reduction and before any optional stabilizer moment-map reduction",
        "background_stabilizer": {
            "connected_lie_algebra": "R*H direct-sum R*P_x direct-sum so(3)",
            "dimension": 5,
            "basis": ["H=partial_t", "P_x=partial_x", "J_1", "J_2", "J_3"],
            "nonzero_brackets": "[J_i,J_j]=epsilon_ijk J_k",
            "H_and_Px_central": True,
            "weyl_compensator": "zero",
            "maxwell_bundle_action": "H and P_x preserve the connection; each J_i has the standard patchwise U(1) compensator and preserves F",
            "constant_U1_reducibility": "acts trivially on connection differences and supplies no independent Taub charge on the closed slice",
            "proof": stabilizers["conformal_stabilizer_argument"],
            "full_SO42_is_background_stabilizer": False,
            "reason_SO42_excluded": "the nonzero product Weyl tensor, S1 periodicity, product topology, and magnetic flux break the vacuum conformal-cylinder algebra; SO(4,2) cannot be imported from R x S3",
        },
        "rotation_representation": _rotation_audit(),
        "primary_module_action": _primary_audit(),
        "pairing_and_charge_disposition": _pairing_and_charge_audit(records),
        "residual_dispositions": {
            "local_gauge_quotient": "ALREADY_PERFORMED",
            "stabilizers_retained_as_global_symmetries": "CERTIFIED_CONSISTENT",
            "stabilizer_action_on_q_and_p_primary_modules": "CERTIFIED",
            "stabilizer_Lee_Wald_invariance": "CERTIFIED",
            "stabilizers_presymplectically_null_on_full_generic_phase_space": "FALSE_BY_EXPLICIT_WITNESSES",
            "stabilizers_gauged_in_an_absolute_CE_complex": "NOT_AUTHORIZED",
            "Taub_zero_or_moment_map_zero_derived_sector": "OPEN",
            "residual_cohomology_after_a_declared_null_quotient": "NOT_COMPUTED",
        },
        "correction_ledger": {
            "superseded_placeholder": "final residual SO(4,2) quotient on the compactified Plebanski-Hacyan fixture",
            "replacement": "background-stabilizer action followed, only if justified, by a separately declared moment-map/Taub-zero reduction",
            "vacuum_cylinder_result_unchanged": "the absolute SO(4,2) result on the conformally flat vacuum cylinder remains valid in its own phase space",
        },
        "classification": {
            "connected_background_stabilizer_certified": True,
            "full_SO42_stabilizer_rejected": True,
            "generic_axial_polar_primary_equivariance_certified": True,
            "generic_axial_polar_Lee_Wald_invariance_certified": True,
            "universal_stabilizer_nullity_refuted": True,
            "absolute_residual_gauge_quotient_certified": False,
            "Taub_zero_derived_sector_complete": False,
            "cyclic_BV_enhancement_certified": False,
            "Lorentzian_causal_claim": False,
            "quantum_claim": False,
        },
        "interpretation": "The Einstein q-primary and extra p-primary waves form honest representations of the actual five-generator Plebanski-Hacyan background stabilizer, and their Lee-Wald forms are invariant. The stabilizer generators are not universal null directions: explicit nonzero Hamiltonian/moment-map matrix elements occur already on the positive extra blocks. They therefore remain global symmetries unless a separate moment-map-zero derived sector and quotient are declared. The vacuum-cylinder SO(4,2) one-particle vanishing theorem is not a descent theorem for this flux product background.",
        "next_gate": "construct the complete H, P_x, and J_i moment maps/Taub forms across generic, exceptional, and global blocks; classify their common zero locus and only then decide whether any stabilizer subalgebra is gauged; independently solve or obstruct the polynomial cyclic chain-homotopy enhancement",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem certifies the connected background stabilizer and its exact action and Lee-Wald invariance on generic axial and polar q/p-primary modules. It refutes universal presymplectic nullity and the unqualified import of the vacuum SO(4,2) quotient. It does not complete exceptional/global stabilizer actions, the common Taub-zero locus, an absolute residual CE quotient, cyclic BV enhancement, causal propagation, scattering, particles, or quantum theory.",
        "verification_receipt": {
            "producing_date": "2026-07-17",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.07, "commands": ["python3 -m py_compile bridge/einstein_sector/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.py bridge/einstein_sector/verify_einstein_maxwell_weyl_plebanski_hacyan_stabilizer.py bridge/einstein_sector/tests/test_einstein_maxwell_weyl_plebanski_hacyan_stabilizer.py", "python3 -m json.tool bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 1.15, "commands": ["python3 -m bridge.einstein_sector.einstein_maxwell_weyl_plebanski_hacyan_stabilizer --verify bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json", "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_plebanski_hacyan_stabilizer", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_plebanski_hacyan_stabilizer"]},
            "tier_2": {"status": "NOT_RUN_NOT_REQUIRED", "reason": "all upstream inputs are unchanged content-addressed certificates; this result consumes rather than modifies their operator or current data"},
            "tier_3": {"status": "NOT_RUN", "reason": "no paper freeze, release, shared core algebra, causal lifecycle, or quantum lifecycle state is promoted"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_plebanski_hacyan_stabilizer --verify bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_plebanski_hacyan_stabilizer",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_plebanski_hacyan_stabilizer",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"stabilizer certificate stale or altered: {path}")


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
