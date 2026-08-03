"""Provenance record for the torus G1 result, which is COMPUTED IN FORGE.

This module deliberately computes no physics. The G1 dimensions are decided by
`forge/examples/reverse_physics_torus_gate.forge` in the tango repo, using
`math/qmat` exact rational rank, and its evidence is that gate's exit code under
`forge verify -full`. What lives here is the weyl-gravity side of the import
gate: the gate's content-addressed identity, the numbers it reported, the exact
commands that reproduce them, and the claim boundary.

It FAILS CLOSED. If the pinned Forge gate is reachable and its bytes no longer
hash to the recorded digest, `--check` refuses rather than silently accepting a
drifted source. If the gate is not reachable (this repo may be checked out
without tango beside it), that is recorded as UNVERIFIED_LOCALLY — never as a
pass.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.torus_g1_provenance --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_HAMILTONIAN_PRIVILEGE_TORUS_G1_V1.json"

RESULT_ID = "REVERSE_PHYSICS_HAMILTONIAN_PRIVILEGE_TORUS_G1_V1"
SCHEMA_NAME = "reverse-physics-hamiltonian-privilege-torus-g1-v1"

# The pinned upstream computation.
FORGE_REPO = "https://github.com/area9innovation/tango"
FORGE_COMMIT = "a6945d0e50c06ab970f5957fb56f18146c72e4d9"
FORGE_PATH = "forge/examples/reverse_physics_torus_gate.forge"
FORGE_SHA256 = "3e9261a958eb720ea4c9415d10435bb280a5c27dec35ea60bf3f51c04550bdc7"
FORGE_EXPECT = 37

# Default sibling checkout; overridden only for verification, never for content.
LOCAL_TANGO = Path("/home/alstrup/area9/tango")

# What the gate reported. These are TRANSCRIBED from the gated run, not
# recomputed here -- the gate is the authority and its hash is pinned above.
SWEEP = [
    {"N": 0, "modes": 1, "vol": 4, "marg": 4, "symp": 4, "ham": 0},
    {"N": 1, "modes": 41, "vol": 244, "marg": 180, "symp": 84, "ham": 80},
    {"N": 2, "modes": 313, "vol": 1876, "marg": 1300, "symp": 628, "ham": 624},
    {"N": 3, "modes": 1201, "vol": 7204, "marg": 4900, "symp": 2404, "ham": 2400},
]


def verify_pinned_gate() -> dict[str, object]:
    """Fail-closed check of the pinned Forge source."""
    local = LOCAL_TANGO / FORGE_PATH
    if not local.exists():
        return {
            "state": "UNVERIFIED_LOCALLY",
            "reason": f"pinned Forge gate not reachable at {local}; hash not confirmed in this checkout",
            "hash_matches": False,
        }
    digest = hashlib.sha256(local.read_bytes()).hexdigest()
    if digest != FORGE_SHA256:
        raise AssertionError(
            f"pinned Forge gate DRIFTED: {local} hashes to {digest}, expected {FORGE_SHA256}"
        )
    return {"state": "VERIFIED_LOCALLY", "reason": "", "hash_matches": True}


def derived() -> dict[str, object]:
    rows = []
    for s in SWEEP:
        rows.append(
            {
                **s,
                "gap_symp_minus_ham": s["symp"] - s["ham"],
                "local_gap_marg_minus_symp": s["marg"] - s["symp"],
                "local_gap_vol_minus_marg": s["vol"] - s["marg"],
            }
        )
    return rows


def build() -> dict[str, object]:
    rows = derived()
    gaps = {r["gap_symp_minus_ham"] for r in rows}
    if gaps != {4}:
        raise AssertionError(f"transcribed sweep does not show a constant gap of 4: {gaps}")
    local_marg = [r["local_gap_marg_minus_symp"] for r in rows]
    local_vol = [r["local_gap_vol_minus_marg"] for r in rows]
    if not all(a < b for a, b in zip(local_marg, local_marg[1:])):
        raise AssertionError("the marginal/symplectic gap is not strictly growing")
    if not all(a < b for a, b in zip(local_vol, local_vol[1:])):
        raise AssertionError("the volume/marginal gap is not strictly growing")

    return {
        "schema": SCHEMA_NAME,
        "result_id": RESULT_ID,
        "result_state": "SYMPLECTIC_TO_HAMILTONIAN_OBSTRUCTION_IS_TOPOLOGICAL_AND_LOCALLY_INVISIBLE",
        "generality_level": "G1_TRIGONOMETRIC_POLYNOMIAL_VECTOR_FIELDS_ON_T4_TRUNCATION_0_TO_3",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "SEPARATION_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": "PROVENANCE_IMPORT — the computation is upstream in Forge; this file computes no physics",
        "assumption_tags": {
            "consumed": ["RP-DETERMINISTIC", "RP-REVERSIBLE"],
            "under_test": ["RP-INFORMATION-CONSERVING", "RP-MARGINAL-INFORMATION-CONSERVING"],
            "namespace_note": "RP-* names physical postulates; disjoint from the computational-regime tags in dependency_tags.",
            "note": "RP-LINEAR-CARRIER is NOT consumed here -- that is the point of the G1 carrier.",
        },
        "upstream_computation": {
            "repo": FORGE_REPO,
            "commit": FORGE_COMMIT,
            "path": FORGE_PATH,
            "sha256": FORGE_SHA256,
            "expect_exit_code": FORGE_EXPECT,
            "kernel": "math/qmat exact rational rank (no floating point)",
            "verify_result": "forge verify -full: exit 37, c==native, asan clean (c+native)",
        },
        "pinned_gate_check": verify_pinned_gate(),
        "carrier": {
            "manifold": "T^4 = R^4/Z^4, coordinates (q1, p1, q2, p2)",
            "symplectic_form": "omega = dq1^dp1 + dq2^dp2",
            "fields": "trigonometric-polynomial vector fields, real Fourier basis, |k|_inf <= N",
            "truncations": [0, 1, 2, 3],
            "why_a_manifold_matters": "on a vector space H^1 vanishes, which collapses the symplectic and Hamiltonian conditions into one; the torus separates them",
        },
        "sweep": rows,
        "theorem": {
            "four_level_chain": "Hamiltonian <= symplectic <= marginal <= volume-preserving. The linear carrier of the G0/G2 certificates has only THREE levels because H^1(R^4) = 0.",
            "topological_gap": "dim symplectic - dim Hamiltonian = 4 at every truncation computed, and the contribution from every nonzero Fourier mode is 0. The whole obstruction sits in the zero mode.",
            "identification": "4 = b_1(T^4). The gate compares against math/comb::binom(4,1); nothing in the gate mentions cohomology, so the Betti number is reproduced rather than assumed.",
            "local_gaps_grow": "marginal - symplectic = 0, 96, 672, 2496 and volume - marginal = 0, 64, 576, 2304 across N = 0..3: strictly increasing, hence genuinely local.",
            "reverse_physics_payload": "The gap between information conservation and Hamiltonian structure SPLITS. One part is local and visible to differential conditions. The other is topological: it is invisible to any assumption formulated pointwise, per degree of freedom, or differentially, at any resolution.",
            "witness": "Uniform translation X = d/dq1 on T^4: deterministic, reversible, volume preserving globally and per degree of freedom, preserves omega -- and admits no global Hamiltonian.",
        },
        "exact_checks": {
            "upstream_uses_exact_rational_rank": True,
            "no_floating_point": True,
            "betti_number_reproduced_not_assumed": True,
            "per_mode_closed_forms_checked_at_every_mode": True,
            "witnesses_decided_by_residual_not_rank": True,
            "positive_control_present": True,
            "gap_constant_and_local_gaps_strictly_growing": True,
        },
        "claim_flags": {
            "TOPOLOGICAL_OBSTRUCTION_EXHIBITED": True,
            "NONLINEAR_CARRIER_COVERED": True,
            "ALL_TRUNCATIONS_PROVED": False,
            "GENERAL_MANIFOLD_COVERED": False,
            "FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT": False,
            "EQUIVALENCE_OVER_A_BASE_THEORY_ESTABLISHED": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": (
            "On T^4 with trigonometric-polynomial vector fields truncated at |k|_inf <= N for N = 0,1,2,3, the "
            "symplectic-to-Hamiltonian gap is exactly 4, carried entirely by the zero mode, while the two local "
            "gaps grow strictly with N. Every dimension is an exact rational rank computed upstream in Forge and "
            "gated on both backends under ASan."
        ),
        "does_not_establish": [
            "the gap for ALL truncations N: four values of N were computed, and constancy in N is not proved. This is the open gate and it is the natural Rocq target.",
            "anything about a general symplectic manifold; only T^4 with its flat structure was computed",
            "anything about non-polynomial (general smooth) vector fields; the carrier is a finite-dimensional truncation at each N",
            "that the G0/G2 linear-carrier witnesses descend to the torus -- they do not, and no claim here depends on them",
            "a reproduction, confirmation or refutation of Carcassi--Aidala's own derivation",
            "an equivalence in the reverse-mathematics sense; still no reversal over a base theory",
            "any quantum, causal, or field-theoretic claim",
        ],
        "next_gate": "REVERSE_PHYSICS_TORUS_ALL_TRUNCATIONS: prove in Rocq that the symplectic/Hamiltonian gap is b_1 for every N, replacing four computed values with an induction over the truncation.",
        "verification_commands": [
            "PYTHONPATH=. python3 -m reverse_physics.torus_g1_provenance --check",
            "# upstream, in the tango repo at the pinned commit:",
            "cd forge && FORGE_LIB=$PWD/lib /tmp/forgebin -run examples/reverse_physics_torus_gate.forge   # exit 37",
            "cd forge && FORGE_LIB=$PWD/lib /tmp/forgebin verify -full examples/reverse_physics_torus_gate.forge",
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
    elif not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
        raise AssertionError(f"{RESULT_ID} provenance record is stale")
    state = payload["pinned_gate_check"]["state"]
    print(f"{RESULT_ID}: PASS (pinned Forge gate {state})")


if __name__ == "__main__":
    main()
