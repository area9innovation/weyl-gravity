"""Provenance record: THE OPEN SCATTERING QUESTION, REDUCED TO A FINITE TEST.

The black-hole programme certifies that a compatible fundamental symmetry C_out
exists on the combined future space and flags as OPEN whether it FACTORISES,
C_out = C_+ (+) C_H, over null infinity and the horizon. The reverse-physics
assumption lattice identified that as the decisive remaining question about the
ghost.

This record answers it as far as it can be answered today:

  1. THE QUESTION IS FINITE. It reduces to a 3x3 generalised eigenvalue problem.
  2. THE INPUT IS MISSING. Explicit T_+ is not certified; T_-'s determinant
     involves Jost amplitudes with no closed form.
  3. NOTHING WEAKER WILL DO. Two witnesses matching every certified inertia give
     opposite answers, so the structural data cannot settle it.

Computes no mathematics. The witnesses live in
`rocq/WeylScatteringCFactorisation.v`; the matrix algebra lives in tango
`forge/examples/weyl_scattering_c_factorisation_gate.forge`.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.scattering_c_factorisation --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_SCATTERING_C_FACTORISATION_V1.json"

RESULT_ID = "REVERSE_PHYSICS_SCATTERING_C_FACTORISATION_V1"
SCHEMA_NAME = "reverse-physics-scattering-c-factorisation-v1"

PINNED = {
    "witnesses": ROOT / "rocq/WeylScatteringCFactorisation.v",
    "dipole": ROOT / "rocq/WeylGhostDipole.v",
}

UPSTREAM_GATE = {
    "path": "tango forge/examples/weyl_scattering_c_factorisation_gate.forge",
    "sha256": "a737f18a49d1273313bb18f2a74dfa6e140be5e1ebb05bd2ab5c8afa8a04d027",
    "result": "exit 28, 28/28 checks; forge verify -full: 1 verified, 0 failed",
    "what_it_certifies": (
        "the matrix algebra of the reduction, in exact rational arithmetic: the pullback identity "
        "T_-^T G_- T_- = T_+^T G_+ T_+ + H_out on two independent instances; the intertwining "
        "reduction C_+ = T_+ C_H T_+^{-1} AND its necessity (a perturbed C_+ is shown NOT to "
        "intertwine); the inertia of all five witness matrices by Jacobi's leading-minor rule; and "
        "the pencil cubic by exact Lagrange interpolation with its discriminant."
    ),
}

# What the black-hole programme certifies, read and hashed.
IMPORTED = {
    "black_hole_programme/phase4/axial_local_commutant_spectral_c_v1/certificate.json":
        None,  # filled at build time
    "black_hole_programme/phase4/axial_explicit_tplus_band_v1/certificate.json":
        None,
    "black_hole_programme/phase3/axial_incoming_connection_analytic/certificate.json":
        None,
    "black_hole_programme/phase3/axial_global_finite_flux_channel_classification_v3/certificate.json":
        None,
}

THE_REDUCTION = {
    "setup": "S = (R, A)^T with R = T_+ T_-^{-1}, A = T_-^{-1}; oriented Stokes identity G_- = R^dag G_+ R + A^dag H_out A",
    "step_1_intertwining": (
        "C_+ (+) C_H preserves ran(S) with a COMMON C_- if and only if C_+ = T_+ C_H T_+^{-1}. "
        "The two boundary symmetries are NOT independently choosable -- the horizon one determines "
        "the null-infinity one. This is the structural reason the question is nontrivial, and the "
        "Forge rail checks both that the conjugate intertwines and that a perturbation of it does not."
    ),
    "step_2_pullback": (
        "Pulling the Stokes identity back by T_- gives, with NO new input, "
        "T_-^dag G_- T_- = T_+^dag G_+ T_+ + H_out, i.e. N = M + H_out with M := T_+^dag G_+ T_+."
    ),
    "step_3_criterion": (
        "Requiring C_+ and C_H to be fundamental symmetries of their own boundary forms and "
        "congruing by T_+, the question becomes whether (H_out, M) carry a COMMON FUNDAMENTAL "
        "DECOMPOSITION -- equivalently whether det(M - lambda H_out) has all roots real and positive "
        "with H_out^{-1}M diagonalisable. By step 2 that is: spectrum of H_out^{-1}N inside "
        "(1, infinity)."
    ),
    "why_the_criterion_is_right": (
        "If a common decomposition exists, both forms are block-diagonal for it, so H^{-1}M is too, "
        "and on each block M = lambda H with both definite of the same sign -- hence lambda > 0. "
        "Conversely, if H^{-1}M is diagonalisable with positive spectrum, its eigenspaces are "
        "H-orthogonal, M = lambda H on each, exactly one eigenspace carries the single positive "
        "H-direction, and taking L_+ inside it with L_- its H-complement gives a decomposition that "
        "is simultaneously fundamental for both."
    ),
    "outcome": "an open scattering condition becomes a 3x3 generalised eigenvalue problem",
}

WHY_IT_CANNOT_BE_RUN = {
    "T_plus": (
        "phase4/axial_explicit_tplus_band_v1 carries explicit_Tplus_certified = false, "
        "does_not_establish 'the outgoing trace map T_plus', lifecycle NUMERIC-ENCLOSURE, and status "
        "CORRELATED_OUTGOING_SUCCESSOR_PASS_R4_OPEN -- the radial transport has reached r = 487/16 "
        "and is still heading for r = 4."
    ),
    "T_minus": (
        "phase3/axial_incoming_connection_analytic proves T_- exists globally and is invertible, "
        "with determinant -(2w-i)(4w-i)^2 A_in_2^2 A_in_1 / (4(w-i)). The Jost amplitudes A_in_s "
        "have no closed form for the Regge-Wheeler potential, so this is not an explicit matrix."
    ),
    "the_grams_ARE_explicit": (
        "phase3/axial_null_flux_gram gives the endpoint Grams exactly as functions of omega. The "
        "missing input is the connection, not the forms."
    ),
}

NO_SHORTCUT = {
    "what_is_certified_structurally": "the inertia (1,2,0) of each of G_-, G_+, H_out -- and nothing finer",
    "the_two_witnesses": {
        "H": "diag(1,-1,-1); leading minors 1, -1, 1",
        "YES": "M = diag(2,-3,-5); minors 2, -6, 30; M+H = diag(3,-4,-6), minors 3, -12, 72; pencil (x-2)(x-3)(x-5), three distinct POSITIVE roots",
        "NO": "M = [[1,2,0],[2,1,0],[0,0,-1]]; minors 1, -3, 3; M+H minors 2, -4, 8; the (+,-) block of H^{-1}M is [[1,2],[-2,-1]], trace 0, determinant 3, characteristic factor x^2 + 3 -- a NON-REAL pair",
    },
    "the_point": (
        "All five matrices have leading-minor sign pattern (+,-,+), i.e. inertia (1,2,0) by Jacobi's "
        "rule. The witnesses therefore match EVERY structural fact the programme certifies, and they "
        "give opposite answers. Explicit T_+ is not a convenience; it is logically required."
    ),
    "scope_note": (
        "the witnesses are real symmetric, a special case of Hermitian, which is enough: realising "
        "both outcomes inside the certified inertia class establishes that the class does not decide."
    ),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    manifest = {}
    for name, path in PINNED.items():
        if not path.exists():
            raise AssertionError(f"pinned {name} missing at {path}")
        manifest[str(path.relative_to(ROOT))] = sha(path)

    imported = {}
    for rel in IMPORTED:
        p = ROOT / rel
        if not p.exists():
            raise AssertionError(f"imported source missing: {rel}")
        imported[rel] = sha(p)

    return {
        "schema": SCHEMA_NAME,
        "result_id": RESULT_ID,
        "result_state": "OPEN_QUESTION_REDUCED_TO_A_FINITE_TEST_INPUT_STILL_MISSING",
        "generality_level": "G4_ALL_HERMITIAN_PAIRS_OF_INERTIA_ONE_TWO",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "NECESSITY_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": (
            "PROVENANCE_IMPORT -- the witnesses are in rocq/WeylScatteringCFactorisation.v and the "
            "matrix algebra in tango weyl_scattering_c_factorisation_gate.forge; this file computes "
            "nothing"
        ),
        "answers": {
            "question": "does the scattering fundamental symmetry factorise as C_out = C_+ (+) C_H over null infinity and the horizon?",
            "raised_by": "black_hole_programme/phase4/axial_local_commutant_spectral_c_v1 (endpoint_block_diagonal_scattering_c_established = false)",
            "why_it_matters": (
                "the assumption lattice says a C that factorises is a positivity statement one could "
                "plausibly call physical, and one that does not is a formal device. Everything else "
                "about the ghost is settled."
            ),
            "answer_today": (
                "NOT YET DECIDABLE, and now precisely so. The question is a 3x3 generalised "
                "eigenvalue problem whose single missing input is explicit T_+; and no weaker data "
                "can answer it, because two witnesses matching every certified inertia give opposite "
                "answers."
            ),
        },
        "the_reduction": THE_REDUCTION,
        "why_it_cannot_be_run_yet": WHY_IT_CANNOT_BE_RUN,
        "no_shortcut": NO_SHORTCUT,
        "ledger": {
            "print_assumptions_closed": "14/14 in WeylScatteringCFactorisation.v; 212/212 across the twenty-two modules the shared gate drives",
            "coqchk_axiom_section": "<none>",
            "declared_assumptions_in_source": "none -- no Axiom, Parameter, Hypothesis, Conjecture, Admitted or admit",
            "hygiene_note": (
                "the source-hygiene rail rejected an earlier draft because its PROSE contained the "
                "bare a-d-m-i-t verb; the regex cannot tell a comment from a tactic. The bluntness is "
                "deliberate and the file was reworded rather than the check relaxed."
            ),
        },
        "gate_result": "RESULT: 27 green (0 red) -- GATE: PASS",
        "upstream_gate": UPSTREAM_GATE,
        "gate_negative_controls": [
            "twenty-six inherited from the earlier modules, all rejected",
            "a FALSE claim that the NO witness has a real pencil root is REJECTED -- if it did, both witnesses would answer YES and the no-shortcut theorem would be empty",
            "the Forge rail carries its own necessity control: a perturbed C_+ is asserted NOT to intertwine, so the reduction C_+ = T_+ C_H T_+^{-1} is shown necessary and not merely sufficient",
        ],
        "provenance": {
            "source_manifest": manifest,
            "imported_black_hole_certificates": imported,
            "gate_script_not_pinned": "rocq/run.sh is harness, deliberately not hash-pinned",
        },
        "exact_checks": {
            "zero_axiom_development": True,
            "kernel_rechecked_by_coqchk": True,
            "no_floating_point": True,
            "reduction_algebra_checked_on_two_independent_instances": True,
            "intertwining_necessity_checked": True,
        },
        "claim_flags": {
            "QUESTION_REDUCED_TO_A_FINITE_TEST": True,
            "NO_INERTIA_LEVEL_SHORTCUT_EXISTS": True,
            "REDUCTION_ALGEBRA_VERIFIED_EXACTLY": True,
            "FACTORISATION_DECIDED": False,
            "EXPLICIT_T_PLUS_AVAILABLE": False,
            "GENERAL_PENCIL_EQUIVALENCE_FORMALISED_IN_ROCQ": False,
            "LORENTZIAN_CLAIM": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": (
            "The factorisation question reduces, by the intertwining relation C_+ = T_+ C_H T_+^{-1} "
            "and the pullback identity T_-^dag G_- T_- = T_+^dag G_+ T_+ + H_out, to whether the pair "
            "(H_out, T_+^dag G_+ T_+) carries a common fundamental decomposition -- a 3x3 generalised "
            "eigenvalue problem. The reduction's matrix algebra is verified in exact rational "
            "arithmetic on independent instances, including the necessity of the intertwining "
            "relation. Two witnesses whose forms, partners and sums all carry inertia (1,2,0) give "
            "opposite answers, so the certified structural data does not decide the question."
        ),
        "does_not_establish": [
            "the answer. Explicit T_+ is not available, so the test cannot be run",
            "the general equivalence 'common fundamental decomposition iff the pencil is diagonalisable with positive spectrum' as a formal Rocq theorem. It is argued in the module header and its consequences are computed exactly on the Forge rail; the Rocq module proves the WITNESSES, which is the part the no-shortcut conclusion rests on",
            "any claim about the physical meaning of a factorising C. That a factorising C would be 'physical' is the assumption lattice's reading, not a theorem",
            "any LORENTZIAN-CAUSAL statement. The black-hole certificates read here carry REDUCED-MODE and none is promoted",
            "anything about the BV-BFV complex, the residual classes, the physical spectrum, or the quantum theory. The two scoped Lorentzian no-go theorems are neither used nor affected",
        ],
        "next_gate": (
            "EXPLICIT_T_PLUS: the single missing input. It is already the declared objective of "
            "black_hole_programme/phase4/axial_explicit_tplus_band_v1, whose radial transport stands "
            "at r = 487/16 heading for r = 4. When that lands, the test in the_reduction.step_3 is a "
            "few lines of exact linear algebra and the question is settled either way."
        ),
        "verification_commands": [
            "cd rocq && ./run.sh",
            "PYTHONPATH=. python3 -m reverse_physics.scattering_c_factorisation --check",
            "cd forge && FORGE_LIB=$PWD/lib forge -run examples/weyl_scattering_c_factorisation_gate.forge   # exit 28",
            "cd forge && FORGE_LIB=$PWD/lib forge verify -full examples/weyl_scattering_c_factorisation_gate.forge",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = build()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered, encoding="utf-8")
    else:
        if not OUTPUT.exists():
            raise AssertionError(f"{RESULT_ID} record missing")
        recorded = json.loads(OUTPUT.read_text(encoding="utf-8"))
        for path, digest in recorded["provenance"]["source_manifest"].items():
            actual = sha(ROOT / path)
            if actual != digest:
                raise AssertionError(f"pinned source DRIFTED: {path} is {actual}, expected {digest}")
        for path, digest in recorded["provenance"]["imported_black_hole_certificates"].items():
            p = ROOT / path
            if not p.exists():
                raise AssertionError(f"imported source MISSING: {path}")
            actual = sha(p)
            if actual != digest:
                raise AssertionError(
                    f"imported black-hole source DRIFTED: {path} -- if T_+ has since been certified, "
                    "the test in the_reduction.step_3 can now be RUN; re-read before relying on this"
                )
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            raise AssertionError(f"{RESULT_ID} record is stale")
    print(f"{RESULT_ID}: PASS (witnesses and imported black-hole certificates hash-verified)")


if __name__ == "__main__":
    main()
