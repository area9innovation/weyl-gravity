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
a common Einstein--matter/Weyl--matter background and prove that its
stress/source realization intertwines its full BV differential with the
universal Ward complex while preserving `ker Q`.

The Berger imports have advanced to the complete support-local cyclic 26-row
retained minimal `q1`.  The separate exact incidence theorem nevertheless
rules this background out as a common Einstein base point: it is neither
Einstein, conformally Einstein, nor Einstein with the same clock stress for
any constant `kappa,Lambda`.  Its proportionality obstruction is
`-q(1-q)/(8a^6)`.  Thus the Berger result is a genuine non-Einstein
Weyl--matter branch and its same-base-point Einstein tangent gate is
`NOT_APPLICABLE`; nonminimal and causal rows remain open.  No Berger operator
is inserted into the flat chain map.

## Claim boundary

The fixed-source field solution locus remains affine.  The representative
kernel dimensions are local symbol fibers, not global matter solution spaces.
No physical Cauchy pairing, nonminimal gauge fixing, retarded/advanced
propagation, nonlinear closure, scattering, or quantum result is asserted.

## Provenance

Input base commit: `bb86c011d66440bf3b204125a655189e511d6615`.

| Artifact | SHA-256 |
|---|---|
| generator | `def3f4f512beeeae7dfcb115f8b3861976485520cc90748415230db66e8e82c4` |
| schema | `fabe7924ecc4b4ae9cfda7fa85ea3ec356938b6571fb341b15626e6e06d30b83` |
| certificate | `c4a25b0610b869d9d8c82c19bc85005cbce20186700149d1d9cd212689eefc56` |
| tests | `da6d558fe485265be9398d6c6494e00ab3fce950b9af4c31e86d013e0e5f4f84` |
| theorem note | `40a199f1bf62984be4f8e472ec0a6f0847026379843a8bbf916a142586c73bec` |
| Einstein-sector aggregator | `b772968483020e28c1a7b2abae6a8ed86e0c85666bc5fa76531279ac601401fb` |
| Einstein-sector theorem certificate | `c4ed958ad7db67296039a573afbec5e5338d496bbbf1eecc43111a2d105b0896` |
| refreshed asymptotic bootstrap | `1dc398b3f553f6f8d87ffa43f6cedf02ca3c4ed4e7e1e4d10596a470c9af56df` |
| refreshed D-quotient asymptotic seed | `ce1a6d0ac020eea9ddc95261f6f5003dbce03d8f007e44258b398f05febb2685` |
| contextual Berger minimal BV SDR | `9e7503ed7fd6082b4164ae7b03d350c753f941cc45d639ffb02598ba8f262422` |
| contextual Berger retained typed layout | `3eccbcc1076eaf29ab1dc540440f8f2d3ffd5c9aa5be9265443db2997f68b1ba` |
| contextual complete Berger retained operator | `296bd46e4d94320a6a5b227167d722da1793d1f81891dcf2e494f9b631dcdd77` |
| Berger Einstein-incidence certificate | `6ab941dbf3312bcc991dc0de59be30853f876e4599414196a3ae21c967c863b4` |

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | Python compile, JSON parse, and `git diff --check` | under 0.1 s | PASS |
| 1 | sourced-defect chain-map verifier | 14 s | PASS |
| 1 | scoped chain-map tests | 17 s | PASS (9 tests) |
| 1/2 | complete Einstein-sector test discovery | 70.18 s | PASS (124 tests) |
| 2 | independent compensated operator-export consumer | 9 s | PASS |
| 2 | preflight plus characteristic snapshot verifiers | 17 s | PASS |
| 2 | Einstein aggregator/asymptotic/D-seed affected tests | 15.8 s | PASS (32 tests) |
| coordination | classical D-quotient status guards | under 0.1 s | PASS (13/13) |
| coordination | cross-programme status check and mutation guards | under 0.1 s | PASS |
| coordination | retained Berger layout generator, independent verifier, and tests | 0.35 s | PASS (4 tests) |

Tier 3 was not run because the global classical freeze, shared core algebra,
causal lifecycle, quantum lifecycle, and release status remain unpromoted.

The cross-programme verifier was temporarily mid-update while the classical
team registered the Berger minimal-BV SDR, then passed after that owner landed
the registration.  Unrelated quantum import edits were not modified or staged
here.

The retained operator is now registered as complete minimal `q1`.  The shared
classical gate has moved to nonminimal completion and causal construction;
the Einstein-side incidence gate is closed negatively at this Berger base
point without changing any causal claim.
