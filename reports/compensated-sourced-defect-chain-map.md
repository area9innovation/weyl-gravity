# Compensated sourced-defect chain-map receipt

Date: 2026-07-15

## Established

The theorem constructs the universal external-source Ward complex for
`(T_mn,J_phi)` in the flat constant-compensator phase and exports all maps as
canonical exact sparse matrices.

Two squares commute over
`Q(c1,alpha,v,v^-1)[p0,p1,p2,p3]`:

```text
W_B Q_ext = diag((p_squared/2) I4,0) W_source,
div Delta = -(1/c1) projection_div W_source.
```

The affine Einstein defect is Diff gauge invariant, and the full sourced
Einstein--Weyl residual obeys

```text
E_EW=(c1 I+2 alpha Q)Delta+(2 alpha/c1)Q(T).
```

Thus same-source Einstein closure is exactly `Q(T)=0`, now at chain-map level.
The independently consumed compensated operator export verifies the operator
factorization `K_EW=c1 G1+2 alpha Q G1` used in the proof.

The compatible-source fibers have:

| Fiber | Ward cycles | Ward cycles in `ker Q` |
|---|---:|---:|
| generic `p=(2,1,0,0)` | 6 | 1 |
| null `p=(1,0,0,1)` | 6 | 5 |
| zero `p=0` | 10 | 10, ledger only |

Exact inclusion matrices for all three kernels are included.  The dressed
source `T_EW=T+(2 alpha/c1)Q(T)`, `J_EW=J` is separately proved to be a Ward
complex endomorphism; it remains a changed coupling.

Verdict:

```text
SOURCE_WARD_TO_EINSTEIN_DEFECT_CHAIN_MAP_EXACT_GENERIC_MATTER_BV_NOT_UNIVERSAL
```

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

## Improvement to the requested formulation

An external source Ward complex is not a matter BV complex.  External
spurions have no selected action, kinetic equations, matter gauge symmetry,
ghosts, antifields, Noether rows, or BV pairing.  Promoting them would hide
the main model-dependent obligation.

Accordingly, this result certifies the universal chain map and leaves
`matter_inclusive_bv_complex_constructed=false`.  The next theorem must choose
a matter action and prove that its stress/source realization intertwines its
full BV differential with the universal Ward complex while preserving
`ker Q`.

The newly landed Berger theorem is imported contextually.  It certifies an
eight-row support-local cyclic minimal clock SDR and leaves a retained 26-row
minimal complex.  Its follow-on typed-layout certificate freezes all 26 rows,
bundle types, pairings, allowed `q1` blocks, support rules, and order ceilings.
The coefficientwise retained operator, nonminimal rows, Green homotopies, and
stability remain open, so it is not yet a complete matter-inclusive input for
this theorem.  No Berger operator is inserted into the flat chain map.

## Claim boundary

The fixed-source field solution locus remains affine.  The representative
kernel dimensions are local symbol fibers, not global matter solution spaces.
No physical Cauchy pairing, nonminimal gauge fixing, retarded/advanced
propagation, nonlinear closure, scattering, or quantum result is asserted.

## Provenance

Input base commit: `46d95a1f6f04e446a4d5290ec5666af3af6cd392`.

| Artifact | SHA-256 |
|---|---|
| generator | `89f0302f7029a76daa98800b6497b90620af238b7341cbece5b660ef2e1c9e0f` |
| schema | `fabe7924ecc4b4ae9cfda7fa85ea3ec356938b6571fb341b15626e6e06d30b83` |
| certificate | `8d3da8f3a81384b365f4b3be7ec639ba7304e91e6e764c0579b8c6193e761c51` |
| tests | `89dc776c91ab64734bd8b6d478f938e59f62bf703c8768731115a4fe064f7731` |
| theorem note | `c0aa3e610511269dfb6fe21cd9530d616789eb3bb22ea0fdd4485cfd11fc96db` |
| Einstein-sector aggregator | `0fb582bbdef80608d08dcc5c04fbff1d9f22832fc08caacd3e81423d0843cfde` |
| Einstein-sector theorem certificate | `e75d5b9e926207b5b02502f7dc9b65092e3edcdf85db63fcf7d59c7178a72bf8` |
| refreshed asymptotic bootstrap | `c56267e8bd81b556d4099a407379cda5d683e094411bc845c6fa56d131b55ee9` |
| refreshed D-quotient asymptotic seed | `e39cff26bc6b6037eb6d0063899d6612e0c293b6c154aca42ce70881ef009796` |
| contextual Berger minimal BV SDR | `9e7503ed7fd6082b4164ae7b03d350c753f941cc45d639ffb02598ba8f262422` |
| contextual Berger retained typed layout | `3eccbcc1076eaf29ab1dc540440f8f2d3ffd5c9aa5be9265443db2997f68b1ba` |

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | Python compile, JSON parse, and `git diff --check` | under 0.1 s | PASS |
| 1 | sourced-defect chain-map verifier | 14 s | PASS |
| 1 | scoped chain-map tests | 17 s | PASS (9 tests) |
| 1/2 | complete Einstein-sector test discovery | 61.73 s | PASS (118 tests) |
| 2 | independent compensated operator-export consumer | 9 s | PASS |
| 2 | preflight plus characteristic snapshot verifiers | 17 s | PASS |
| 2 | Einstein aggregator/asymptotic/D-seed affected tests | 15.8 s | PASS (32 tests) |
| coordination | classical D-quotient status guards | under 0.1 s | PASS (13/13) |
| coordination | cross-programme status check and mutation guards | under 0.1 s | PASS |

Tier 3 was not run because the global classical freeze, shared core algebra,
causal lifecycle, quantum lifecycle, and release status remain unpromoted.

The cross-programme verifier was temporarily mid-update while the classical
team registered the Berger minimal-BV SDR, then passed after that owner landed
the registration.  Concurrent programme and quantum import edits were not
modified or staged here.
