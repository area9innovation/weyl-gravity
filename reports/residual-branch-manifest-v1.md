# Residual branch manifest v1

Pinned source snapshot: `ba746d608a86ffb8ce7d8d1adf8503e29e8db9b1`.

| Stable branch | Kind | Linear | Causal | Lee–Wald | Taub | Second order | Interaction | Observer | Quantum |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `branch.ph.em.q.generic` | EINSTEIN_IMAGE | CERTIFIED | OPEN | CERTIFIED | CERTIFIED | OPEN | OPEN | OPEN | OPEN |
| `branch.ph.wm.p.generic` | ADDITIONAL_WEYL | CERTIFIED | OPEN | CERTIFIED | CERTIFIED | OBSTRUCTED | OPEN | OPEN | OPEN |
| `branch.ph.em.ell1.standard` | EINSTEIN_IMAGE | CERTIFIED | OPEN | CERTIFIED | CERTIFIED | OPEN | CERTIFIED | NO_CERTIFIED_MAP | NO_CERTIFIED_MAP |
| `branch.ph.wm.ell1.extra.k0` | ADDITIONAL_WEYL | CERTIFIED | OPEN | CERTIFIED | CERTIFIED | OBSTRUCTED | CERTIFIED | OPEN | OPEN |
| `branch.ph.wm.ell1.extra.knonzero` | ADDITIONAL_WEYL | CERTIFIED | OPEN | CERTIFIED | CERTIFIED | OBSTRUCTED | OPEN | NO_CERTIFIED_MAP | NO_CERTIFIED_MAP |
| `branch.ph.global.homogeneous` | GLOBAL_GENERALIZED_ZERO | CERTIFIED | NO_CERTIFIED_MAP | CERTIFIED | CERTIFIED | CERTIFIED | CERTIFIED | OPEN | OPEN |
| `branch.ph.global.twist` | GLOBAL_GENERALIZED_ZERO | CERTIFIED | NO_CERTIFIED_MAP | CERTIFIED | CERTIFIED | CERTIFIED | CERTIFIED | OPEN | OPEN |
| `branch.ph.maxwell.electric_wilson` | MAXWELL_GLOBAL | CERTIFIED | NO_CERTIFIED_MAP | CERTIFIED | CERTIFIED | CERTIFIED | CERTIFIED | OPEN | OPEN |
| `branch.cylinder.e` | ONE_PARTICLE_FAMILY | CERTIFIED | CERTIFIED | CERTIFIED | CERTIFIED | OPEN | OPEN | NOT_APPLICABLE | CERTIFIED |
| `branch.cylinder.a` | ONE_PARTICLE_FAMILY | CERTIFIED | CERTIFIED | CERTIFIED | CERTIFIED | OPEN | OPEN | NOT_APPLICABLE | CERTIFIED |
| `branch.cylinder.l` | ONE_PARTICLE_FAMILY | CERTIFIED | CERTIFIED | CERTIFIED | CERTIFIED | OPEN | OPEN | NOT_APPLICABLE | CERTIFIED |
| `branch.cylinder.w_plus_squared` | NONPARTICLE_RESIDUAL_CLASS | NOT_APPLICABLE | CERTIFIED | CERTIFIED | CERTIFIED | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | OBSTRUCTED |
| `branch.cylinder.w_minus_squared` | NONPARTICLE_RESIDUAL_CLASS | NOT_APPLICABLE | CERTIFIED | CERTIFIED | CERTIFIED | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | OBSTRUCTED |
| `branch.berger.retained.unsplit` | UNSPLIT_MIXED | OPEN | CERTIFIED | CERTIFIED | CERTIFIED | OPEN | OBSTRUCTED | NO_CERTIFIED_MAP | OPEN |
| `branch.black_hole.axial.einstein` | BLACK_HOLE_BRANCH | CERTIFIED | OPEN | CERTIFIED | NO_CERTIFIED_MAP | OPEN | OPEN | OPEN | OPEN |
| `branch.black_hole.axial.extra` | BLACK_HOLE_BRANCH | CERTIFIED | OPEN | CERTIFIED | NO_CERTIFIED_MAP | OPEN | OPEN | OPEN | CERTIFIED |
| `branch.black_hole.polar.einstein` | BLACK_HOLE_BRANCH | CERTIFIED | OPEN | CERTIFIED | NO_CERTIFIED_MAP | OPEN | OPEN | OPEN | OPEN |
| `branch.black_hole.polar.extra` | BLACK_HOLE_BRANCH | CERTIFIED | CERTIFIED | CERTIFIED | NO_CERTIFIED_MAP | OPEN | OPEN | OPEN | CERTIFIED |

## Explicit crosswalk boundary

- `crosswalk.ph_to_vacuum_cylinder` — **NO_CERTIFIED_MAP**: No dispersion-preserving cross-background map is certified.
- `crosswalk.ph_to_black_hole` — **NO_CERTIFIED_MAP**: native axial and polar exterior Ricci carriers exist, but no certified identification with compact-product modes exists
- `crosswalk.berger_unsplit_to_ph_branches` — **OBSTRUCTED**: The canonical support-local same-bundle projector is obstructed by the certified subprincipal witness.
- `crosswalk.ph_exceptional_to_berger_observer` — **NO_CERTIFIED_MAP**: carrier=background/carrier mode identification map; omega=n/a; NO_CERTIFIED_MAP
- `crosswalk.berger_branch_to_detector` — **NO_CERTIFIED_MAP**: carrier=same-background Berger physical-branch dictionary to relational detector, redshift, memory and recoil records; omega=all; NO_CERTIFIED_MAP

The JSON manifest retains the full scope tuple, exact source rows and field paths, observed source statuses and statements, committed fragment hashes, and complete source-row inventory digest.

This generated ledger traces only explicit committed same-carrier rows and explicit crosswalk/no-crosswalk witnesses. It does not identify similarly named modes across backgrounds, infer empty cells as zero, turn reduced current signs into quantum norms, or promote absent causal, observer, interaction or quantum maps.

CLOSE-OUT: DONE — the complete stop condition is met
EVIDENCE: residual_atlas/residual-branch-manifest-v1.json
