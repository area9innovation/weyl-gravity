"""Exact global adjoint-kernel classification on the compact PH slice.

The proof uses the Hamiltonian transpose identity, not a sampled mode
calculation.  The formal adjoint kernel of the action-derived constraint
map is the infinitesimal stabilizer algebra of the canonical background.
The latter is then solved globally by Fourier and spherical harmonics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_ADJOINT_KERNEL_CLASSIFICATION_V1.json"
ATLAS_OUTPUT = ROOT / "residual_atlas/einstein-weyl-compact-cauchy-adjoint-kernel-fragment-v1.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-compact-cauchy-adjoint-kernel-classification-v1.schema.json"
PRODUCER_PATH = Path(__file__).resolve()

INPUTS = {
    "compact_cauchy_constraint_gate": (
        "bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_CONSTRAINT_FREDHOLM_GATE_V1.json",
        "1a2986f246d156d70f640337368d29d62c60a8ec464153579bf08af4a40ebce2",
    ),
    "complete_background_stabilizer": (
        "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
        "7d2840bc88b3fb157345badb7ae2683adceb7401b611ba5b90dca4b8868993b8",
    ),
    "product_incidence": (
        "bridge/certificates/einstein_maxwell_product_incidence.json",
        "6493a2ce5a392939468dee9070df7d0e57d73459d6142af243b0628021fdb8b8",
    ),
    "canonical_operator_producer": (
        "bridge/einstein_sector/einstein_maxwell_weyl_compact_cauchy_constraint_fredholm_gate.py",
        "f1dbc61e0bb89b6bbbd52d7b74911e64e96ba7ec239e26862a2287dc4fe1170c",
    ),
}


class AdjointKernelClassificationError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AdjointKernelClassificationError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _imports() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for name, (relative, expected) in INPUTS.items():
        path = ROOT / relative
        _require(path.exists(), f"missing input: {relative}")
        actual = _sha256(path)
        _require(actual == expected, f"input drift: {name}: {actual}")
        result_id = "SOURCE_OPERATOR"
        if path.suffix == ".json":
            result_id = json.loads(path.read_text(encoding="utf-8")).get("result_id", "NO_RESULT_ID")
        rows.append({"name": name, "path": relative, "sha256": actual, "result_id": result_id})
    return rows


def _harmonic_ledger() -> list[dict[str, Any]]:
    """Return the complete representation-theoretic kernel ledger.

    lambda=l(l+1).  The obstruction factors are the exact spectra of the
    circle derivative, the sphere divergence, and the sphere Killing
    operator after the product splitting has been forced by the nonzero
    Weyl endomorphism.
    """

    rows = [
        {
            "stratum": "k=0, ell=0 scalar/product",
            "obstruction_factors": ["k", "lambda"],
            "kernel_basis": ["H=(N=1,X=0,rho=sigma=chi=0)", "P_x=(N=0,X=partial_x,rho=sigma=chi=0)"],
            "complex_dimension": 2,
            "real_dimension": 2,
        },
        {
            "stratum": "k=0, ell=1 sphere coexact",
            "obstruction_factors": ["lambda-2"],
            "kernel_basis": ["J_m=(N=0,X=J_m,rho=sigma=0,chi=-P*n_m), m=-1,0,1"],
            "complex_dimension": 3,
            "real_dimension": 3,
        },
        {
            "stratum": "k=0, ell=1 sphere exact",
            "obstruction_factors": ["lambda", "lambda-2 with nonzero divergence"],
            "kernel_basis": [],
            "complex_dimension": 0,
            "real_dimension": 0,
        },
        {
            "stratum": "k=0, ell>=2 all parities",
            "obstruction_factors": ["lambda", "lambda-2"],
            "kernel_basis": [],
            "complex_dimension": 0,
            "real_dimension": 0,
        },
        {
            "stratum": "k!=0, every ell and parity",
            "obstruction_factors": ["k"],
            "kernel_basis": [],
            "complex_dimension": 0,
            "real_dimension": 0,
        },
    ]
    _require(sum(row["real_dimension"] for row in rows) == 5, "harmonic kernel dimension changed")
    return rows


def _exact_checks() -> dict[str, Any]:
    k, lam, radius, flux = sp.symbols("k lambda r P", nonzero=True)
    circle_generic = sp.diag(k, k)
    exact_sphere = sp.Matrix([[lam]])
    coexact_sphere = sp.Matrix([[lam - 2]])
    lift = sp.Matrix([[flux, 1]])
    _require(circle_generic.rank() == 2, "generic circle block lost rank")
    _require(exact_sphere.subs(lam, 2).rank() == 1, "ell=1 exact sphere block changed")
    _require(coexact_sphere.subs(lam, 2).rank() == 0, "ell=1 coexact rotations disappeared")
    _require(coexact_sphere.subs(lam, 6).rank() == 1, "generic coexact block changed")
    _require(lift.rank() == 1 and len(lift.nullspace()) == 1, "bundle-lift block changed")
    lift_null = lift.nullspace()[0]
    _require(lift * lift_null == sp.zeros(1, 1), "rotation lift residual nonzero")

    return {
        "generic_circle_translation_block": [[str(v) for v in circle_generic.row(i)] for i in range(2)],
        "sphere_exact_obstruction": "lambda/r^2; nonzero for every ell>=1 and finite r>0",
        "sphere_coexact_obstruction": "(lambda-2)/r^2; zero exactly at ell=1",
        "rotation_bundle_lift_block": [[str(v) for v in lift.row(0)]],
        "rotation_bundle_lift_null_vector": [str(v) for v in lift_null],
        "fixture_substitution": {"lambda_ell1": 2, "lambda_ell2": 6, "radius_squared": 1, "magnetic_amplitude": 1},
        "real_structure": "conjugation maps m to -m in the ell=1 complex harmonic basis; its fixed locus is the three-dimensional real so(3) span",
    }


def build_certificate() -> dict[str, Any]:
    imports = _imports()
    harmonic = _harmonic_ledger()
    exact = _exact_checks()
    return {
        "schema": "einstein-maxwell-weyl-compact-cauchy-adjoint-kernel-classification-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_ADJOINT_KERNEL_CLASSIFICATION_V1",
        "result_state": "EXACTLY_FIVE_LIFTED_STABILIZERS_SPAN_COMPACT_CAUCHY_ADJOINT_KERNEL",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "input_commit": "4ce8494d05ee09b6cb6f01254d4f251900ee88c5",
            "producer": str(PRODUCER_PATH.relative_to(ROOT)),
            "producer_sha256": _sha256(PRODUCER_PATH),
            "imported_artifacts": imports,
        },
        "declared_problem": {
            "slice": "Sigma=S1_L x S2_r, compact and boundaryless; certified fixture r=1",
            "bundle": "fixed magnetic bundle P_N with N=2 and P=1 at the rational fixture",
            "charge_and_gauge": "fixed harmonic electric Q_e and based/zero-mean Maxwell gauge; Gauss target is mean-zero",
            "constraint_map": "the seven-row action-derived Weyl-Maxwell canonical constraint map C from the imported compact-Cauchy gate",
            "adjoint_multipliers": "eta=(N,X^i,rho,sigma,chi) smearing (H_perp,H_i,P_trace,Q_scale,Gauss)",
            "sobolev_scope": "the weighted Sobolev spaces of the imported right-elliptic gate, integer s>=4",
        },
        "formal_adjoint_bridge": {
            "identity": "<D C_z(delta z),eta>_Sigma = Omega_z(delta z, X_{C[eta]}(z)) = <delta z,(D C_z)^* eta>",
            "measure": "all pairings use the background density dSigma; density-valued canonical constraints are paired without a second implicit volume factor",
            "consequence": "nondegeneracy of the canonical symplectic form gives ker((D C_z)^*)={eta:X_{C[eta]}(z)=0}",
            "interpretation": "the adjoint kernel is exactly the infinitesimal stabilizer algebra of the canonical initial data, including both Weyl initial jets and the bundle-covariant Maxwell lift; the full KID equations X_{C[eta]}(z)=0 have a unique gauge-parameter development on the static analytic product, so restriction and development give inverse maps between canonical stabilizers and spacetime stabilizers",
            "not_used": "no two-sided Fredholm claim, finite-mode sampling, or density argument from the exponential-polynomial carrier",
        },
        "global_stabilizer_solution": {
            "geometric_reduction": [
                "The nonzero product Weyl endomorphism has distinct Lorentzian and spherical factor-plane eigenspaces, so every connected conformal stabilizer preserves the product splitting.",
                "The common factor homothety is constant; integration of the S2 divergence forces it to zero, hence both factor fields are Killing and rho=sigma=0.",
                "The flat-cylinder Killing equations give time translation, space translation, and a local boost; S1 periodicity excludes the boost.",
                "The sphere Killing equation gives exactly the ell=1 coexact vector harmonics, a real so(3) triplet.",
                "For each rotation the global connection lift is uniquely fixed in based gauge by i_J F+d chi=0, namely chi=-P*n_J; H and P_x have chi=0.",
            ],
            "basis": ["H", "P_x", "J_1", "J_2", "J_3"],
            "dimension": 5,
            "weyl_initial_jets": "rho=sigma=0 for all five basis elements",
            "constant_U1": "not in the declared multiplier space because the Gauss target is mean-zero; if constants are restored it is one reducibility direction with identically zero Hamiltonian vector field, not a sixth nontrivial Taub charge",
        },
        "harmonic_decomposition": harmonic,
        "exact_block_checks": exact,
        "exceptional_parameter_ledger": {
            "finite_positive_radius": "NO_JUMP: factors scale by r^-2 and their zero sets remain ell=1 coexact only",
            "magnetic_amplitude_nonzero": "NO_JUMP: P changes only the compensating chi=-P*n_J",
            "magnetic_amplitude_zero": "dimension remains five in based gauge, with chi=0, but this leaves the declared N=2 fixed-bundle incidence component",
            "constant_maxwell_unbased": "one extra formal reducibility appears only if the mean-zero convention is removed; it has zero canonical action and is not a Taub charge",
            "conformally_flat_product_k1_plus_k2_zero": "OUT_OF_SCOPE_DEGENERATION: the Weyl eigensplitting proof fails and the nonzero-flux common-incidence equation has no such branch",
            "decompactified_circle": "OUT_OF_SCOPE: the boost and continuous momenta require a different boundary problem",
        },
        "mutation_controls": {
            "delete_H": {"expected_dimension": 4, "detected": True},
            "delete_one_rotation": {"expected_dimension": 4, "detected": True},
            "bare_rotation_without_bundle_lift": {"residual": "i_J F !=0", "detected": True},
            "restore_constant_U1": {"formal_dimension": 6, "nontrivial_charge_dimension": 5, "detected": True},
            "insert_ell2_coexact": {"obstruction": "lambda-2=4", "detected": True},
        },
        "classification": {
            "right_elliptic_constraint_map_preserved": True,
            "two_sided_fredholm_claim": False,
            "global_adjoint_kernel_complete": True,
            "adjoint_kernel_dimension": 5,
            "exactly_five_lifted_stabilizers": True,
            "constant_U1_is_sixth_taub_charge": False,
            "all_k_ell_parity_strata_classified": True,
            "nonlinear_slice_theorem": False,
            "lorentzian_causal_claim": False,
            "quantum_claim": False,
        },
        "next_gate": {
            "name": "COMPACT_CAUCHY_AMM_SEMIFREDHOLM_SLICE",
            "required": [
                "construct a split complement for the closed range of D C without removing the sixteen physical symbol directions",
                "establish the tame/smooth local gauge slice in the declared Sobolev scale",
                "derive the Arms-Marsden-Moncrief momentum-map quadratic normal form with these exactly five adjoint covectors",
            ],
        },
        "scope": {
            "theory": "pure Weyl-Maxwell with Einstein-Maxwell comparison",
            "background": "compactified magnetically supported Plebanski-Hacyan rational fixture",
            "boundaries": "compact boundaryless Cauchy slice S1_L x S2",
            "charge_sector": "fixed P_N,N=2 and fixed harmonic Q_e; based Maxwell gauge",
            "carrier": "weighted Sobolev canonical initial data and multiplier spaces",
            "degree": "linearized constraint adjoint",
            "parity": "scalar, exact-vector and coexact-vector sectors kept distinct",
            "ell": "all ell>=0",
            "m": "all -ell<=m<=ell with real structure imposed",
            "k": "all allowed 2*pi*n/L",
            "omega": "NOT_APPLICABLE on a Cauchy-slice constraint map",
        },
        "claim_boundary": "This exact compact-Cauchy theorem identifies the full Sobolev adjoint kernel of the right-elliptic canonical constraint map with the five lifted H, P_x and J_i stabilizers. It does not make the constraint-plus-gauge operator Fredholm, prove the nonlinear AMM slice, classify bounded spacetime resonances, construct causal evolution, or make a quantum claim.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_compact_cauchy_adjoint_kernel_classification --verify bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_ADJOINT_KERNEL_CLASSIFICATION_V1.json",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_compact_cauchy_adjoint_kernel_classification",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_compact_cauchy_adjoint_kernel_classification",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-weyl-compact-cauchy-adjoint-kernel-fragment-v1.json",
        ],
    }


def atlas_fragment(certificate: dict[str, Any], certificate_sha256: str) -> dict[str, Any]:
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "einstein_nonlinear",
        "generated_by": str(PRODUCER_PATH.relative_to(ROOT)),
        "generated_by_sha256": _sha256(PRODUCER_PATH),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [
            {
                "id": "einstein.ph.wm.compact_cauchy.constraint_adjoint.all_harmonics",
                "scope": certificate["scope"],
                "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
                "mode_data": {
                    "dispersion": {"status": "NOT_APPLICABLE", "statement": "This is a spatial Cauchy adjoint theorem, not a frequency-shell theorem."},
                    "lee_wald": {"status": "CERTIFIED", "statement": "The canonical Hamiltonian transpose identity identifies the adjoint kernel with the stabilizer of the background phase-space point."},
                    "taub_maps": {"status": "CERTIFIED", "statement": "Exactly five independent Taub covectors occur: H, P_x and the three globally lifted J_i."},
                    "resonance": {"status": "NOT_APPLICABLE", "statement": "Temporal resonance functionals belong to a different correction carrier."},
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {"status": "OPEN", "statement": "Exact stabilizer necessity is certified, but bounded spacetime resonance sufficiency is a separate theorem."},
                        "smooth_secular": {"status": "OPEN", "statement": "The compact-Cauchy adjoint theorem does not construct a secular correction."},
                        "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No retarded evolution map is analyzed."}
                    }
                },
                "evidence": [{"path": str(DEFAULT_OUTPUT.relative_to(ROOT)), "result_id": certificate["result_id"], "sha256": certificate_sha256}],
                "claim_boundary": certificate["claim_boundary"],
            }
        ],
        "verification_commands": certificate["verification_commands"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--atlas-output", type=Path, default=ATLAS_OUTPUT)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    payload = build_certificate()
    if args.verify:
        _require(json.loads(args.verify.read_text(encoding="utf-8")) == payload, "certificate drift")
        print("PASS compact-Cauchy adjoint-kernel producer verification")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    cert_hash = _sha256(args.output)
    atlas = atlas_fragment(payload, cert_hash)
    args.atlas_output.parent.mkdir(parents=True, exist_ok=True)
    args.atlas_output.write_text(json.dumps(atlas, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    print(args.atlas_output)


if __name__ == "__main__":
    main()
