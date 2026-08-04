"""Provenance record: the DEGENERATE ghost case, and the cross-programme join.

REVERSE_PHYSICS_WEYL_GHOST_FORCED_V1 proved that two or more DISTINCT simple
poles always include a negative residue, and flagged its one load-bearing gap:
Weyl gravity's actual kinetic operator is Box^2, a DOUBLE pole, and that the
degenerate case is no better was CITED (Riegert 1984), not proved.

This record closes that gap -- and the interesting part is where the statement
came from. It was already in this repository, computed by the BLACK-HOLE
PROGRAMME on the Schwarzschild exterior in the odd-parity spin-two sector. The
abstract assumption lattice and the concrete scattering analysis had converged on
the same object without either knowing it.

Computes no mathematics. The theorems live in `rocq/WeylGhostDipole.v`. The
black-hole side is imported by content hash AND independently re-run (its
verifiers need sympy, which is under the mise Python 3.12 toolchain, not the
system interpreter). Re-running a producer is reproduction, not verification --
the independent check is the Rocq module, which reaches the same conclusion by a
different route.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.weyl_ghost_dipole --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_WEYL_GHOST_DIPOLE_V1.json"

RESULT_ID = "REVERSE_PHYSICS_WEYL_GHOST_DIPOLE_V1"
SCHEMA_NAME = "reverse-physics-weyl-ghost-dipole-v1"

PINNED = {
    "dipole": ROOT / "rocq/WeylGhostDipole.v",
    "ghost_forced": ROOT / "rocq/WeylGhostForced.v",
}

# The black-hole side: read, hashed, quoted, and re-run (see reruns below).
IMPORTED = {
    "black_hole_programme/phase4/axial_local_nonlocal_positivity_v1/certificate.json":
        "29cd53300a892424ec5b901ba08c994efc7d66a27cea5447e8d8200fe67c9356",
    "black_hole_programme/phase4/axial_all_ell_threshold_structure_v1/certificate.json":
        "4c0ef500671231ddf8501d061921c3fc37f46c70d4d08bc2f5e80f915c560c4d",
    "black_hole_programme/phase4/axial_qnm_conserved_source_overlap_v1/certificate.json":
        "914312759dfb77c59c188a4e2c1d7d75357993fc7f18e9d76d8afa8aeb3b99fc",
    "black_hole_programme/phase3/axial_global_finite_flux_channel_classification_v3/report.md":
        "cbe6aa1cf769e1db10e38b91506f4e37c369ee8f35e50b4b7456298fc4c707bf",
}

THEOREMS = [
    {
        "name": "commutant_of_the_jordan_block",
        "statement": "the commutant of a rank-two nilpotent is a*I + b*N -- TWO parameters, not four",
        "role": "WHY THE OBSTRUCTION CANNOT BE EVADED. A redefinition of the inner product must commute with the dynamics, so this exhausts the available freedom.",
    },
    {
        "name": "flux_determinant / flux_determinant_is_never_positive",
        "statement": "det(G*eta) = -g^2 a^2, which is never positive",
        "role": "THE OBSTRUCTION. A 2x2 symmetric form with nonpositive determinant is never positive definite, for ANY (a, b).",
    },
    {
        "name": "first_basis_vector_is_null / never_definite",
        "statement": "the first basis vector is null for every admissible eta",
        "role": "kills definiteness of EITHER sign before any case analysis, without needing the determinant at all",
    },
    {
        "name": "indefinite_when_a_is_nonzero",
        "statement": "explicit rational vectors giving the values +1 and -1",
        "role": "INDEFINITENESS WITH WITNESSES, not merely a determinant sign. x = (1 - g b)/(2 g a) and x = (-1 - g b)/(2 g a) at y = 1.",
    },
    {
        "name": "degenerate_when_a_is_zero / the_bilinear_form_is_not_trivial",
        "statement": "at a = 0 the first basis vector lies in the radical, and the form is not identically zero",
        "role": "the other half of the dichotomy, with its own non-vacuity control so 'degenerate' is a statement about a direction and not about a form that vanishes anyway",
    },
    {
        "name": "a_dipole_admits_no_positive_inner_product / indefinite_or_degenerate",
        "statement": "indefinite when a != 0, degenerate when a = 0; never positive",
        "role": "THE DIPOLE GHOST THEOREM -- the statement WeylGhostForced.v had to cite as O3.",
    },
]

THE_JOIN = {
    "what_converged": (
        "REVERSE_PHYSICS_WEYL_GHOST_FORCED_V1 argues at the level of ACTIONS, kinematically, in "
        "every even dimension, and concludes that the ghost is forced and that only RP-LOCAL and "
        "RP-METRIC can remove it. The black-hole package argues at the level of on-shell SCATTERING "
        "DATA on Schwarzschild and concludes that no LOCAL positive metric exists while a compatible "
        "fundamental symmetry DOES exist on the combined future space -- a nonlocal one. Different "
        "objects, different methods, different tags, same verdict: LOCALITY is the load-bearing "
        "assumption."
    ),
    "why_it_matters": (
        "An assumption ledger is worth something only if its 'load-bearing' verdicts survive contact "
        "with hard analysis. The lattice named which of the five assumptions had to give BEFORE "
        "looking at the scattering data, and the scattering analysis found exactly that one giving."
    ),
    "tags_are_not_merged": (
        "The black-hole certificates carry REDUCED-MODE. Per this programme's claim boundary a "
        "REDUCED-MODE computation is never evidence for a LORENTZIAN-CAUSAL claim. What is recorded "
        "is a CONVERGENCE -- evidence about where to look, not a theorem about the Lorentzian theory. "
        "Neither result is promoted by the other."
    ),
    "the_resolution_of_the_apparent_tension": (
        "An indefinite metric makes NORMS indefinite; it does not make the DYNAMICS ill-posed. The "
        "black-hole analysis is about invertibility, analyticity and transport, none of which care "
        "about the sign of a Gram form. Concretely: no zero-energy resonance for EVERY ell >= 2 and "
        "spins 1 and 2, proved exactly by hypergeometric reduction -- clean threshold behaviour in a "
        "theory with a certified ghost sector. The ghost is unavoidable and locally incurable, and it "
        "is not fatal to the dynamics. What it costs is that positivity becomes NONLOCAL."
    ),
    "the_question_this_leaves": (
        "Whether the nonlocal C factorises over null infinity direct-sum the horizon. The black-hole "
        "package flags that as an open scattering condition; the assumption lattice explains why it "
        "is THE question -- a C that factorises is a positivity statement one could plausibly call "
        "physical, and one that does not is a formal device. Everything else about the ghost is "
        "settled."
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

    return {
        "schema": SCHEMA_NAME,
        "result_id": RESULT_ID,
        "result_state": "DEGENERATE_GHOST_CASE_CLOSED_AND_CROSS_PROGRAMME_JOIN_RECORDED",
        "generality_level": "G4_ALL_RANK_TWO_JORDAN_BLOCKS",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "NECESSITY_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": (
            "PROVENANCE_IMPORT -- the mathematics is in rocq/WeylGhostDipole.v; the black-hole side "
            "is imported by content hash and NOT re-run; this file computes nothing"
        ),
        "closes": {
            "gate": "WEYL_GHOST_DEGENERATE_LIMIT",
            "declared_in": "REVERSE_PHYSICS_WEYL_GHOST_FORCED_V1",
            "what_it_was": (
                "O3, the load-bearing citation: that the DEGENERATE double pole 1/k^4 -- the case "
                "that actually occurs in Weyl gravity -- is no better than two distinct simple poles. "
                "It is now a theorem."
            ),
        },
        "attribution": (
            "THE MATHEMATICS IS NOT NEW AND IS NOT THIS STREAM'S. The black-hole programme computed "
            "exactly this commutant, flux metric and determinant on the Schwarzschild exterior in the "
            "odd-parity spin-two sector, with the physics attached, at commit e72fd8b3. What this "
            "record adds is that the computation is now abstracted into the reverse-physics chain as "
            "a machine-checked zero-axiom theorem, and that its abstract form is visibly the object "
            "the assumption lattice had pointed at."
        ),
        "the_join": THE_JOIN,
        "theorems": THEOREMS,
        "imported_side": {
            "content_hashes": IMPORTED,
            "producing_commit": "e72fd8b3 (axial local/nonlocal positivity dichotomy)",
            "reruns": {
                "axial_local_nonlocal_positivity_v1": "EXACT_LOCAL_NONLOCAL_POSITIVITY_DICHOTOMY_VERIFIED",
                "axial_all_ell_threshold_structure_v1": "PASS: independent all-ell threshold verification",
                "axial_qnm_conserved_source_overlap_v1": "AXIAL_QNM_CONSERVED_SOURCE_OVERLAP_VERIFIED",
            },
            "interpreter_note": (
                "the verifiers need sympy, which lives under the mise Python 3.12 toolchain and NOT "
                "under /usr/bin/python3 (3.14). The first attempt used the system interpreter and "
                "failed with ModuleNotFoundError -- recorded because that is exactly how a step "
                "quietly becomes 'not verified' in a report."
            ),
            "rerun_is_not_verification": (
                "re-running a producer is REPRODUCTION. It establishes that the package still "
                "computes what it computed, not that the computation is right. The independent check "
                "on this side is rocq/WeylGhostDipole.v, which reaches the same conclusion by a "
                "different route."
            ),
            "consequence": (
                "this record INHERITS whatever those certificates got wrong. If a hash no longer "
                "matches, the reading is stale -- --check fails closed on that."
            ),
        },
        "ledger": {
            "print_assumptions_closed": "11/11 in WeylGhostDipole.v; 198/198 across the twenty-one modules the shared gate drives",
            "coqchk_axiom_section": "<none>",
            "declared_assumptions_in_source": "none -- no Axiom, Parameter, Hypothesis, Conjecture, Admitted or admit",
        },
        "gate_result": "RESULT: 26 green (0 red) -- GATE: PASS",
        "gate_negative_controls": [
            "twenty-five inherited from the earlier modules, all rejected",
            "a FALSE claim that a dipole admits a positive-definite metric is REJECTED -- if it did, the case Weyl gravity actually has would be curable by redefining the norm and the whole line collapses",
        ],
        "provenance": {
            "source_manifest": manifest,
            "gate_script_not_pinned": "rocq/run.sh is harness, deliberately not hash-pinned",
        },
        "exact_checks": {
            "zero_axiom_development": True,
            "kernel_rechecked_by_coqchk": True,
            "no_floating_point": True,
            "indefiniteness_shown_by_explicit_witnesses": True,
            "black_hole_side_rerun": True,
        },
        "claim_flags": {
            "DEGENERATE_CASE_PROVED": True,
            "O3_CITATION_DISCHARGED": True,
            "CROSS_PROGRAMME_CONVERGENCE_RECORDED": True,
            "MATHEMATICS_IS_NOVEL": False,
            "JORDAN_STRUCTURE_DERIVED_FROM_WEYL_GRAVITY": False,
            "BLACK_HOLE_CERTIFICATES_REPRODUCED": True,
            "BLACK_HOLE_CERTIFICATES_INDEPENDENTLY_VERIFIED": False,
            "NONLOCAL_C_SHOWN_PHYSICAL": False,
            "LORENTZIAN_CLAIM": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": (
            "In a zero-axiom Rocq development over Q: the commutant of a rank-two Jordan block is "
            "a*I + b*N; the resulting flux metric has determinant -g^2 a^2 and a null first basis "
            "vector; it is therefore indefinite when a is nonzero -- with explicit rational witnesses "
            "of both signs -- and degenerate when a is zero, and never positive definite for any "
            "(a, b). Separately, and NOT as a theorem, this record documents that the black-hole "
            "programme reached the same conclusion independently on the Schwarzschild exterior, and "
            "that the two lines therefore agree on which assumption is load-bearing."
        ),
        "does_not_establish": [
            "that a dipole ghost IS a rank-two Jordan block for Weyl gravity. That is the standing input; the black-hole package is where it was computed for a real background",
            "independent verification of the black-hole certificates. Their verifiers were RE-RUN and pass, but re-running a producer is reproduction, not verification. The independent route is rocq/WeylGhostDipole.v reaching the same conclusion differently",
            "novelty. The mathematics is the black-hole programme's, and the physical content is Ostrogradsky's. What is added is the abstraction into the chain and the recorded convergence",
            "that the nonlocal C is physical. Its existence is an extension-by-direct-sum argument, and whether it factorises over null infinity and the horizon is an open scattering condition the black-hole package explicitly does not claim",
            "any LORENTZIAN-CAUSAL statement. The black-hole certificates carry REDUCED-MODE and nothing is promoted. None of the five objects the quantum claim boundary lists as non-existent is asserted",
            "anything about the BV-BFV complex, the residual classes, the physical spectrum, or the quantum theory. The two scoped Lorentzian no-go theorems are neither used nor affected",
        ],
        "next_gate": (
            "C_FACTORISATION_OVER_THE_FUTURE_BOUNDARY: whether the compatible fundamental symmetry "
            "on the combined future space factorises as C_out = C_+ direct-sum C_H. The black-hole "
            "package flags it as open; the assumption lattice explains why it is the decisive one. A "
            "C that factorises is a positivity statement one could call physical; one that does not "
            "is a formal device. Everything else about the ghost is settled."
        ),
        "verification_commands": [
            "cd rocq && ./run.sh",
            "PYTHONPATH=. python3 -m reverse_physics.weyl_ghost_dipole --check",
            "sha256sum black_hole_programme/phase4/axial_local_nonlocal_positivity_v1/certificate.json",
            "# NOTE the interpreter: sympy is under the mise toolchain, not /usr/bin/python3",
            "P=~/.local/share/mise/installs/python/3.12.13/bin/python3",
            "PYTHONPATH=. $P -m black_hole_programme.phase4.axial_local_nonlocal_positivity_v1.verify",
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
        # the imported black-hole side is fail-closed on drift too
        for path, digest in recorded["imported_side"]["content_hashes"].items():
            p = ROOT / path
            if not p.exists():
                raise AssertionError(f"imported source MISSING: {path}")
            actual = sha(p)
            if actual != digest:
                raise AssertionError(
                    f"imported black-hole source DRIFTED: {path} is {actual}, expected {digest} "
                    "-- this record's reading of the black-hole side is stale"
                )
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            raise AssertionError(f"{RESULT_ID} record is stale")
    print(f"{RESULT_ID}: PASS (Rocq proofs and imported black-hole certificates hash-verified)")


if __name__ == "__main__":
    main()
