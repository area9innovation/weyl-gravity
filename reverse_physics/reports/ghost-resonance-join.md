# The ghost and the resonance are one object

**Certificate** `REVERSE_PHYSICS_GHOST_RESONANCE_JOIN_V1`
**Rail** Forge, `tango/forge/examples/ghost_resonance_join_gate.forge` — 8/8, 1.80 s
**Dependency tag** `LOCAL-ALGEBRAIC`

> The mathematics is elementary. The contribution is the identification — that two lines of
> this repository proved things about the same object without noticing, and that their two
> conclusions are therefore one conclusion. §5 is what this does *not* say, and it matters
> more than usual here.

---

## 1. Two lines that agreed and did not cite each other

`REVERSE_PHYSICS_WEYL_GHOST_DIPOLE_V1` proves, in zero-axiom Rocq over `ℚ`, that a rank-two
Jordan block admits **no positive-definite invariant inner product** — the commutant is
`aI + bN`, the flux determinant is `−g²a²`, the first basis vector is null.

`black_hole_programme/phase4/axial_qnm_causal_laplace_bridge_v1` proves,
`LORENTZIAN_CERTIFIED`, that the meromorphic continuation of an *actual retarded causal
transfer operator* has a **second-order resonance pole**, arising from the same non-split
extension. The mechanism is pretty: the Weyl-branch response is the **mass-derivative** of the
Einstein–Weyl parent Green operator, and differentiating a moving simple pole in the mass
produces a double pole —

```
−∂_m [ P/(z − νm) ]|₀  =  −νP/z²
```

so the ghost branch is the *confluence* of the massive branch with the Einstein branch.

**Neither cites the other.** A grep for `REVERSE_PHYSICS` inside `black_hole_programme`
returns nothing, and the dipole certificate does not import the resonance-pole theorem. The
dipole certificate files the situation honestly as a **convergence** — *"evidence about where
to look, not a theorem about the Lorentzian theory."* This is the theorem it was pointing at.

## 2. The identity

Let `N` be the nilpotent part of the Jordan block and `v` its eigenvector, so
`ker N = im N = span{v}`.

**Analytically.** `N² = 0`, so `(sI − N)(sI + N) = s²I` and the resolvent is

```
(sI − N)⁻¹ = I/s + N/s²        exactly — the Laurent expansion terminates
```

The coefficient of `1/s²` is `(sI + N)` at `s = 0`, which is **`N`**, nonzero. So the pole is
genuinely second order, and the direction it acts in is `im N = span{v}`.

**Metrically.** For `N` to be self-adjoint in a symmetric form `η` — which is what an
*invariant inner product* means — the condition is `ηN = Nᵀη`. Computed on the general
nilpotent and the general symmetric form, that commutator has **vanishing diagonal**, is
**antisymmetric**, and its single independent entry is

```
(ηN − Nᵀη)₀₁  =  t · (vᵀ η v)
```

**Those are the same equation.** `t` is a free scale, so *"N is self-adjoint in η"* holds
exactly when *"v is null in η"* holds. Nullity is not a **consequence** of self-adjointness —
it is the **same polynomial**.

## 3. What that says about the physics of the ghost

The ghost is **not a mode of negative energy you could weigh.** It is a **direction** that
simultaneously

- rings at **second order** in the resolvent, and
- carries **no norm** in every invariant form,

and those are not two properties of the direction. They are one property described twice.

The practical consequence: **the ghost's signature is an order, not a sign.** A healthy sector
gives a simple pole; the defective one gives a double pole. That is a different kind of thing
to look for than a negative residue.

## 4. Why the checks are built the way they are

**Symbolic, not sampled.** `N = t·v uᵀ` with `u = (−v₁, v₀)` is the *general* 2×2 nilpotent:
every nonzero one has rank one and is `v uᵀ` with `u` annihilating the kernel, and nilpotency
forces `u ⊥ v`, which in two dimensions leaves exactly this family. `η` is the general
symmetric form. Every identity is a polynomial identity over `ℚ` in `(v₀, v₁, t, e₀, e₁, e₂,
s)` — every Jordan block and every symmetric form at once.

**The negative control isolates the cause.** A repeated eigenvalue alone does *not* give a
double pole: for the **semisimple** matrix with the same repeated eigenvalue (`N → 0`) the
`s⁰` coefficient is the zero matrix and the pole is simple. So pole order tracks
**defectiveness**, not degeneracy.

**Non-vacuity, four ways.** `N` must be nonzero; `im N` nontrivial; `vᵀηv` **not** identically
zero as a polynomial (or "v is null" would hold for every `η` and say nothing); and the
commutator not identically zero (or self-adjointness would be automatic). A shared equation
has to cut something out to be a join.

**Mutation tested.** Taking the norm on `u` instead of `v` breaks **only** check 7 — precisely
targeted. Making `u` non-perpendicular to `v` breaks checks 1, 3, 4 and 7 — the nilpotency
chain collapses. The gate discriminates.

## 5. What this does **not** establish

- **The mathematics is not new.** Elementary 2×2 linear algebra; anyone writing it down gets
  the same identity. The algebra is the *evidence*, not the result.
- **Not that any particular Schwarzschild QNM is defective.** The Smith-dichotomy package
  explicitly does not evaluate its selector `β_n` and says *"no actual QNM is promoted to a
  double pole."* The causal Laplace bridge certifies the double pole for **one** enclosed
  simple `ℓ = 2` axial spin-two QNM. This is conditional on defectiveness: it says what
  defectiveness *means*, not where it occurs.
- **Nothing `LORENTZIAN-CAUSAL`.** This carries `LOCAL-ALGEBRAIC`, and nothing is promoted.
- **It does not vindicate the unstable-resonance reading, and points the other way.** A
  **double** pole's time-domain reading is `t·e^{iωt}` — **secular growth**, not decay. So a
  second-order pole is not by itself a finite-lifetime mode. That reading is listed in
  `does_not_establish` across *five* black-hole certificates, along with time-domain
  stability. Donoghue–Menezes treat the ghost as an unstable resonance *with a width*;
  `paper/06` places that prescription outside this programme's assumptions and nothing here
  changes it.
- **Not that the ghost is harmless.** The dipole reading stands: the ghost is unavoidable and
  locally incurable, and what it costs is that **positivity becomes nonlocal**. This says what
  the ghost *is*, not that it is benign.

## 6. What is open

Evaluating `β_n` is what turns *"conditional on defectiveness"* into *"this QNM is
defective."* The black-hole package names exactly what is missing: a certified QNM germ, an
adjoint cokernel germ, and a boundary-convergent or regularised pairing.

And the **dynamical** content of the second-order pole is open **in both directions** — the
branch-cut and contour control that five certificates list as unestablished is what stands
between the local residue and any statement about the waveform. Neither decay nor growth is
established today.

---

## Verification

```bash
cd tango/forge && export FORGE_LIB=$PWD/lib
forge -run examples/ghost_resonance_join_gate.forge   # 8/8, 1.80 s
```

Exact rational arithmetic throughout. No floating point, no tolerance, no sampling.
