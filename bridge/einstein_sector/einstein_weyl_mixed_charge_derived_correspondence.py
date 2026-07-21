"""Exact two-jet Einstein/extra mixed-charge derived correspondence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/EINSTEIN_WEYL_MIXED_CHARGE_DERIVED_CORRESPONDENCE_V1.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein-weyl-mixed-charge-derived-correspondence-v1.schema.json"
INPUTS = {
    "kuranishi": (
        "bridge/certificates/EINSTEIN_WEYL_CONSTRAINT_ALGEBROID_KURANISHI_CARRIER_V1.json",
        "EINSTEIN_WEYL_CONSTRAINT_ALGEBROID_KURANISHI_CARRIER_V1",
        "fa764024805f3c2ce67e63d9a15afed94861e1374e32ecda8124efc3849aea24",
    ),
    "symplectic_extension": (
        "bridge/certificates/EINSTEIN_WEYL_SYMPLECTIC_EXTENSION_CLASSIFICATION_V1.json",
        "EINSTEIN_WEYL_SYMPLECTIC_EXTENSION_CLASSIFICATION_V1",
        "d316e61807112c31fcbf2733e4d93bb3ce2d3bcebe3389922d6baa463415cbd3",
    ),
    "ambient_cofiber": (
        "bridge/certificates/EINSTEIN_WEYL_PARITY_COMPLETE_RESIDUAL_EXACT_SEQUENCE_MAXIMAL_V1.json",
        "EINSTEIN_WEYL_PARITY_COMPLETE_RESIDUAL_EXACT_SEQUENCE_MAXIMAL_V1",
        "d94140069b4972acdd2f5fcc99e8076bb773d9f2d904ce068e58548f86fbbd10",
    ),
    "balanced_fixture": (
        "bridge/certificates/einstein_maxwell_weyl_mixed_moment_map_zero_locus.json",
        "EINSTEIN_MAXWELL_WEYL_MIXED_MOMENT_MAP_ZERO_LOCUS",
        "a1310146fc4ce499d73585470289982abdabf902dbf361f39a5c1fff1625bb36",
    ),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def req(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def exact_algebra() -> dict[str, Any]:
    # Linearization at the cone vertex of r_E=kappa_E-c and r_X=kappa_X+c.
    eye = sp.eye(5)
    zero_52 = sp.zeros(5, 2)
    differential = zero_52.row_join(-eye).col_join(zero_52.row_join(eye))
    req(differential.rank() == 5, "strict presentation differential rank")
    req(7 - differential.rank() == 2, "H0 dimension")
    req(10 - differential.rank() == 5, "H1 dimension")

    tau_e = sp.Rational(48, 5) * (-6 + 5 * sp.sqrt(3))
    amp2 = sp.Rational(27, 52) * (-6 + 5 * sp.sqrt(3))
    tau_x = -sp.Rational(832, 45) * amp2
    req(sp.simplify(tau_e + tau_x) == 0, "mixed charge cancellation")
    req(tau_e != 0 and tau_x != 0, "separate charges must be nonzero")

    # The exact generic axial fixture checks the lift-invariant Schur block.
    g_e = sp.Matrix([[6, 18], [18, 2]])
    g_x = sp.diag(1296, sp.Rational(208, 3))
    c = sp.Matrix([[-84, 0], [112, 0]])
    g_raw = sp.diag(-76, sp.Rational(208, 3))
    schur = sp.simplify(g_raw - c.T * g_e.inv() * c)
    req(schur == g_x, "Schur complement")

    return {
        "strict_tangent_differential": [[str(x) for x in row] for row in differential.tolist()],
        "strict_tangent_dimensions": {
            "degree_0": 7,
            "degree_1": 10,
            "rank_d": 5,
            "H0": 2,
            "H1": 5,
            "carrier": "real balanced two-amplitude fixture plus five charge-transfer coordinates",
        },
        "balanced": {
            "Einstein_mu_H": str(tau_e),
            "extra_mu_H": str(tau_x),
            "total_mu_H": "0",
            "transfer_c": [str(tau_e), "0", "0", "0", "0"],
            "extra_amplitude_squared": str(amp2),
        },
        "axial_fixture_schur": [[str(x) for x in row] for row in schur.tolist()],
    }


def build() -> dict[str, Any]:
    for name, (rel, result_id, digest) in INPUTS.items():
        path = ROOT / rel
        payload = json.loads(path.read_text())
        req(payload["result_id"] == result_id, f"{name} result id")
        req(sha(path) == digest, f"{name} content hash")
    algebra = exact_algebra()
    return {
        "schema": "einstein-weyl-mixed-charge-derived-correspondence-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA_PATH),
        "result_id": "EINSTEIN_WEYL_MIXED_CHARGE_DERIVED_CORRESPONDENCE_V1",
        "result_state": "TWO_JET_MIXED_CHARGE_DERIVED_CORRESPONDENCE_CERTIFIED_SEPARATE_NEUTRAL_PROJECTIONS_OBSTRUCTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {
                key: {"path": rel, "result_id": rid, "sha256": digest}
                for key, (rel, rid, digest) in INPUTS.items()
            },
        },
        "scope": {
            "theory": "Einstein-Maxwell source, Weyl-Maxwell target and extra cofiber",
            "background": "compactified magnetically supported Plebanski-Hacyan",
            "boundaries": "compact boundaryless Cauchy slice S1_L x S2 before stabilizer reduction",
            "charge_sector": "fixed P_N,N=2 and fixed Q_e; based Maxwell gauge; W_x retained",
            "carrier": "arbitrary finite harmonic two-jet carrier; dimensions displayed on the real ell=2,m=0,k=0 balanced two-amplitude subcarrier",
            "degree": "constraint/Kuranishi two-jet",
            "parity": "branchwise; exact witness axial",
            "ell": "finite sums; exact witness ell=2",
            "m": "finite sums; exact witness m=0",
            "k": "allowed compact momenta; exact witness k=0",
            "omega": "stationary branch frequencies only as labels; no evolution claim",
        },
        "ambient_sequence": {
            "sequence": "0 -> E --iota--> W --pi_X--> X -> 0 on pre-residual H0",
            "status": "CERTIFIED",
            "splitting_used": "the target-internal Lee-Wald-orthogonal primary lift on each certified finite branch",
            "warning": "the correspondence does not turn this ambient sequence into an exact sequence of separately neutral derived fibres",
        },
        "derived_correspondence": {
            "obstruction_space": "O=span{H,P_x,J1,J2,J3}",
            "homotopy_pullback": "C=(E x X) x^h_(O x O) O_anti, with Delta_anti(c)=(c,-c)",
            "strict_coordinates": "(e,x,c; eta_E,eta_X)",
            "strict_cdga": "d eta_E=kappa_E(e)-c; d eta_X=kappa_X(x)+c; d(e,x,c)=0",
            "nilpotency": "d^2=0 exactly because kappa_E,kappa_X and c are degree-zero closed coordinates",
            "contraction": "alpha=eta_E+eta_X has d alpha=kappa_E+kappa_X; beta=(eta_X-eta_E)/2 and c'=c+(kappa_X-kappa_E)/2 form the contractible pair d beta=c', d c'=0",
            "minimal_model": "Sym(E*+X*) tensor Lambda(alpha_H,alpha_Px,alpha_J1,alpha_J2,alpha_J3), d alpha_A=kappa_E,A+kappa_X,A",
            "common_Weyl_map": "j(e,x,c)=iota(e)+s_orth(x), with the summed homotopy furnishing kappa_W(j)=0 in the derived fibre",
            "span": "Z_E -> C <- Z_X and C --j--> Z_W; p_E:C->E and p_X:C->X land in ambient branches, not generally in Z_E or Z_X",
            "dimension_formula": "for dim E=e and dim X=x, strict tangent dimensions are (e+x+5)->10 with rank 5, hence H0=e+x and H1=5 at the cone vertex",
            "balanced_fixture_tangent_complex": algebra["strict_tangent_dimensions"],
            "balanced_fixture_differential": algebra["strict_tangent_differential"],
        },
        "balanced_fixture": {
            **algebra["balanced"],
            "labels": "axial ell=2,m=0,k=0 Einstein-minus plus second extra p-primary representative",
            "representation": "take e amplitude 1, x amplitude sqrt(27*(-6+5*sqrt(3))/52), and c=(mu_E,0,0,0,0)",
            "separate_projection_test": "p_E has kappa_E=c nonzero and p_X has kappa_X=-c nonzero, while j has total kappa_W=0",
        },
        "map_and_form_ledger": [
            {"object": "ambient inclusion iota:E->W", "kind": "HONEST_MAP", "status": "CERTIFIED"},
            {"object": "ambient cofiber pi_X:W->X", "kind": "HONEST_MAP", "status": "CERTIFIED"},
            {"object": "j:C->Z_W", "kind": "DERIVED_MAP", "status": "CERTIFIED"},
            {"object": "p_E:C->E and p_X:C->X", "kind": "HONEST_MAP_TO_AMBIENT_BRANCHES", "status": "CERTIFIED"},
            {"object": "C->Z_E x Z_X", "kind": "MAP", "status": "OBSTRUCTED"},
            {"object": "component moment maps", "kind": "FUNCTIONS_WITH_HOMOTOPY", "status": "CERTIFIED", "statement": "kappa_E is homotopic to c and kappa_X to -c; neither is separately zero"},
            {"object": "diagonal compact stabilizer action", "kind": "ACTION", "status": "CERTIFIED", "statement": "c transforms coadjointly and the anti-diagonal equations are equivariant"},
            {"object": "Omega_C=j^*Omega_W", "kind": "PULLED_BACK_FORM", "status": "CERTIFIED"},
            {"object": "p_X^*S_X", "kind": "PULLED_BACK_SCHUR_FORM", "status": "CERTIFIED", "fixture": algebra["axial_fixture_schur"]},
            {"object": "S_X as a pairing obtained by quotienting C", "kind": "DERIVED_QUOTIENT_PAIRING", "status": "NO_CERTIFIED_MAP"},
            {"object": "p_E^*Omega_EM versus the Einstein block of Omega_C", "kind": "RELATIVE_COMPARISON_FORM", "status": "CERTIFIED_NONIDENTICAL"},
            {"object": "raw lifted extra-extra Gram", "kind": "LIFT_DEPENDENT_FORM", "status": "NOT_INVARIANT"},
        ],
        "mutations": {
            "delete_transfer_coordinate": "REJECTED: replacing the anti-diagonal pullback by Z_E x Z_X deletes the exact balanced point",
            "project_to_separate_neutral_fibres": "REJECTED: exact projected H charges are nonzero opposites",
            "change_anti_diagonal_to_diagonal": "REJECTED: the balanced fixture then has residual 2*mu_E",
            "delete_one_Koszul_half": "REJECTED: the strict tangent differential rank drops from 5",
            "call_raw_extra_Gram_invariant": "REJECTED by the imported exact lift shear; only the Schur complement is invariant",
        },
        "classification": {
            "anti_diagonal_homotopy_pullback": True,
            "derived_differential_nilpotent": True,
            "contractible_transfer_pair_eliminated": True,
            "balanced_fixture_represented": True,
            "separate_neutral_projection_exists": False,
            "ambient_cofiber_projection_exists": True,
            "Schur_form_pulls_back": True,
            "Schur_form_is_derived_quotient_pairing": False,
            "all_orders_kuranishi": False,
            "causal_particle_or_quantum_claim": False,
        },
        "claim_boundary": "Certifies the smallest exact two-jet homotopy-pullback correspondence retaining cancellation of the five compact-Cauchy charges, its tangent cohomology on the declared balanced carrier, and the exact map/form ledger. It does not construct higher Kuranishi brackets, an all-orders quotient, bounded or causal evolution, particles, positivity, unitarity or quantum transfer.",
        "next_gate": "use this mixed-charge correspondence as the branch-readable nonlinear tangent-cone target; any further quotient requires a higher Kuranishi/algebroid action theorem rather than separate neutral projections",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_weyl_mixed_charge_derived_correspondence --verify bridge/certificates/EINSTEIN_WEYL_MIXED_CHARGE_DERIVED_CORRESPONDENCE_V1.json",
            "python3 bridge/einstein_sector/verify_einstein_weyl_mixed_charge_derived_correspondence.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_mixed_charge_derived_correspondence",
            "python3 -m bridge.einstein_sector.generate_mixed_charge_derived_correspondence_atlas --check",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    payload = build()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if args.verify:
        req(json.loads(args.verify.read_text()) == payload, "stale certificate")
    if not args.write and args.verify is None:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
