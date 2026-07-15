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
minimal complex.  Its coefficientwise retained `q1`, nonminimal rows, Green
homotopies, and stability remain open, so it is not yet a complete
matter-inclusive input for this theorem.  No Berger operator is inserted into
the flat chain map.

## Claim boundary

The fixed-source field solution locus remains affine.  The representative
kernel dimensions are local symbol fibers, not global matter solution spaces.
No physical Cauchy pairing, nonminimal gauge fixing, retarded/advanced
propagation, nonlinear closure, scattering, or quantum result is asserted.

## Provenance

Input base commit: `0cf75919f37b03328720fa86653ce245f2cfe365`.

| Artifact | SHA-256 |
|---|---|
| generator | `c6c206b38d8afc9a1884721b4f3a78514a518da39e79f0cc2e507441a35fef65` |
| schema | `fabe7924ecc4b4ae9cfda7fa85ea3ec356938b6571fb341b15626e6e06d30b83` |
| certificate | `42215bce4769fb49d336a85e94225af01043944e609dea62e8bf58eecfda49f4` |
| tests | `13349b6cbc99b8b42dd2acd38ae0c74e69d9e920fc61aa748d41ee45416cbdc6` |
| theorem note | `e42db262b7a18d523dc1cd8a0cc8bb836dd39416f35f5e66f6d207bbcbed3788` |
| Einstein-sector aggregator | `9892fef7ca707bf23ce35a4b362fa0d62d4e1aa0cefb6114019c0b720b41cb00` |
| Einstein-sector theorem certificate | `622bb7c2501e501660d4896577248f7438223c7bb8b3d4ca98e1b8f1009c1005` |
| refreshed asymptotic bootstrap | `3251ce2a1da809d8ef1518fde71a59eaf92871b34b5f5f9a2f38eece6841bae4` |
| refreshed D-quotient asymptotic seed | `15531aa7e3605979ff237ad2bbc064248254e8d8ad262f1e92a020006df0c70b` |
| contextual Berger minimal BV SDR | `552b7fc975e1c98be909fe9082e2781d60bbe70f0cc6cf19f45ea0e28c154ffd` |

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | Python compile, JSON parse, and `git diff --check` | under 0.1 s | PASS |
| 1 | sourced-defect chain-map verifier | 14 s | PASS |
| 1 | scoped chain-map tests | 17 s | PASS (9 tests) |
| 1/2 | complete Einstein-sector test discovery | 54.92 s | PASS (118 tests) |
| 2 | independent compensated operator-export consumer | 9 s | PASS |
| 2 | preflight plus characteristic snapshot verifiers | 17 s | PASS |
| 2 | Einstein aggregator/asymptotic/D-seed affected tests | 12.4 s | PASS (32 tests) |
| coordination | classical D-quotient status guards | under 0.1 s | PASS (13/13) |
| coordination | cross-programme status check and mutation guards | under 0.1 s | PASS |

Tier 3 was not run because the global classical freeze, shared core algebra,
causal lifecycle, quantum lifecycle, and release status remain unpromoted.

The cross-programme verifier was temporarily mid-update while the classical
team registered the Berger minimal-BV SDR, then passed after that owner landed
the registration.  Concurrent programme and quantum import edits were not
modified or staged here.
