# G1: part of the missing assumption is topological, not physical

**Certificate** `REVERSE_PHYSICS_HAMILTONIAN_PRIVILEGE_TORUS_G1_V1` (provenance import)
**Computation** `forge/examples/reverse_physics_torus_gate.forge` — tango `a6945d0e5`
**Generality** `G1_TRIGONOMETRIC_POLYNOMIAL_VECTOR_FIELDS_ON_T4_TRUNCATION_0_TO_3`
**Evidence** `forge verify -full`: exit 37, `c==native`, asan clean (c+native)

## The question G0 could not ask

The G0 and G2 certificates live on a vector space. There, `H¹(ℝ⁴) = 0`, which
silently collapses two different conditions into one: *preserving ω* and *being
Hamiltonian*. The linear carrier therefore cannot see the distinction at all.

`T⁴` separates them. The chain has **four** levels, not three:

| condition | meaning |
|---|---|
| Hamiltonian | `ι_X ω` is **exact** — `X = X_H` for a global `H` |
| symplectic | `ι_X ω` is **closed** — locally Hamiltonian |
| marginal | each DOF's partial divergence vanishes |
| volume-preserving | the total divergence vanishes |

## Result

Everything block-diagonalises over real Fourier modes, so each mode is an exact
8-parameter rational rank problem (4 at the zero mode), decided by `math/qmat`.

| N | modes | vol | marg | symp | ham | **symp−ham** | marg−symp | vol−marg |
|---|---|---|---|---|---|---|---|---|
| 0 | 1 | 4 | 4 | 4 | 0 | **4** | 0 | 0 |
| 1 | 41 | 244 | 180 | 84 | 80 | **4** | 96 | 64 |
| 2 | 313 | 1876 | 1300 | 628 | 624 | **4** | 672 | 576 |
| 3 | 1201 | 7204 | 4900 | 2404 | 2400 | **4** | 2496 | 2304 |

**The gap splits.** `marg−symp` and `vol−marg` grow strictly with resolution —
they are local, differential conditions and refinement sees more of them.
`symp−ham` is **4 at every truncation**, and the contribution from every nonzero
Fourier mode is **0**. The entire symplectic→Hamiltonian obstruction sits in the
zero mode.

That 4 is `b₁(T⁴)`. The gate compares it against `math/comb::binom(4,1)`, and
nothing in the gate mentions cohomology — the Betti number is **reproduced, not
assumed**.

## The reverse-physics payload

The gap between "conserves information" and "is Hamiltonian" has two parts of
different kinds:

- a **local** part, which per-DOF and pointwise conditions can address (this is
  what G0/G2 measured, and what marginal information conservation partly closes);
- a **topological** part, which they cannot — invisible to any assumption
  formulated pointwise, per degree of freedom, or differentially, **at any
  resolution**.

So a reverse-physics account of Hamiltonian privilege cannot be completed by
physical postulates alone. Some of the missing hypothesis is a property of the
state space, not of the dynamics.

The witness is physically plain: **uniform translation** `X = ∂_{q₁}` on `T⁴`.
Deterministic, reversible, volume preserving globally and per degree of freedom,
preserves `ω` — and admits no global Hamiltonian.

## Independent rails

Per FORGE-CONTRIB rule 3, the gate's checks are independent of the code under
test:

- hand-derived per-mode closed forms, checked at **every** mode (`vol=6`,
  `symp=ham=2`, `marg = 8 − 2·(active DOFs)` at `k ≠ 0`; `4,4,4,0` at `k = 0`);
- the mode count `1 + ((2N+1)⁴ − 1)/2`, counted separately;
- the de Rham rail comparing the gap against the stdlib binomial;
- witnesses decided by **residual evaluation** (`qm_mul_vec`) rather than by rank
  — a different mechanism from the dimension count;
- a positive control at the same mode as the negative witness, so the symplectic
  predicate is shown to be discriminating rather than constantly false.

The gate earned this: it **caught a wrong control** during development. The first
candidate (`X = cos(2πq₂)∂_{q₂}`) is itself non-symplectic; closedness at mode
`k = e_{q₂}` forces `α ∥ k`, which selects `X = cos(2πq₂)∂_{p₂}`.

## What this does not establish

- **Not all truncations.** Four values of N were computed; constancy in N is not
  proved. This is the open gate.
- Nothing about a general symplectic manifold — only `T⁴` with its flat structure.
- Nothing about non-polynomial vector fields; each N is a finite-dimensional
  truncation.
- The G0/G2 linear witnesses **do not descend** to the torus, and no claim here
  depends on them.
- Not a reproduction, confirmation, or refutation of Carcassi–Aidala's derivation.
- Still no reversal over a base theory, so still no equivalence in the
  reverse-mathematics sense.
- No quantum, causal, or field-theoretic claim.

## Next gate

`REVERSE_PHYSICS_TORUS_ALL_TRUNCATIONS` — prove in Rocq that the gap is `b₁` for
**every** N, replacing four computed values with an induction over the
truncation. This is the same shape as the open gate on the general-n certificate:
exhaustive exact computation gets finitely many cases; the quantifier needs a
proof.

## Verification

```bash
PYTHONPATH=. python3 -m reverse_physics.torus_g1_provenance --check
# upstream, in tango at a6945d0e5:
cd forge && FORGE_LIB=$PWD/lib /tmp/forgebin -run examples/reverse_physics_torus_gate.forge      # exit 37
cd forge && FORGE_LIB=$PWD/lib /tmp/forgebin verify -full examples/reverse_physics_torus_gate.forge
```

The provenance record **fails closed**: if the pinned Forge gate is reachable and
its bytes no longer match the recorded digest, `--check` refuses. If tango is not
checked out beside this repo, that is recorded as `UNVERIFIED_LOCALLY` — never as
a pass.

## Tier receipt

- **Toolchain** — `mise exec` → go 1.25.12; forgebin rebuilt from tango master
  `8c4cb3a72`. Baseline `tools/claimlang/run.sh` confirmed green (`GATE: PASS`,
  61 s) **before** any change, so nothing here is confused with pre-existing drift.
- **Upstream (tango)** — `forge verify -full`: exit 37, `c==native`, asan clean on
  both backends, 17 s. Committed by explicit pathspec (1 file); the shared dirty
  tree was left untouched. Husky pre-commit hook ran and passed.
- **Tier 0/1 (weyl-gravity)** — provenance record generated, byte-determinism
  confirmed by `--write` then `--check`, pinned hash `VERIFIED_LOCALLY`.
- **Tier 2 — not run, and not required.** Nothing outside `reverse_physics/`
  imports or is imported by this tree.
- **Tier 3 — not run, and not required.** No freeze, tag, or paper promotion.
