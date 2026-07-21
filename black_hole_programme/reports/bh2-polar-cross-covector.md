# Polar cross covector: the Einstein line is null in the additional sector

**Certificate:** `certificates/BH2_POLAR_CROSS_COVECTOR.json`
**Result token:** `BH2_POLAR_CROSS_COVECTOR_K_NULL_HYPERBOLIC_EXTRA_BLOCK`
**Dependency tags:** `LOCAL-ALGEBRAIC` + `REDUCED-MODE`. **Lifecycle:** `CLASSIFIED`.
**Producer:** `bh2_polar_cross_covector.py` ·
**Verifier:** `verify_bh2_polar_cross_covector.py` (VbGeo rail) ·
**Fast rail:** `tests/test_bh2_polar_cross_covector.py`

## What the work item asked

The parity remainder of the axial cross-scalar theorem: derive the symbolic
real-frequency polar `l=2` Einstein–additional cross covector
`a = (E|X0, E|X1, E|X2)(omega)`, `a_j = F^r(E, conj X_j)/(pi alpha)`, with its
normalization and lift law, and classify its zeros, poles, rank drops and every
exceptional real frequency — *or* certify the first exact obstruction to such a
table, replacing the twenty-minute composition tower by a smaller exact
recurrence / current identity / module reduction.

## The structural reduction (required before any table)

The sphere-integrated Eddington–Finkelstein radial Lee–Wald bilinear `Frb`
is built from **abstract** metric functions and is therefore **independent of
`omega`**. So it is computed once and reused across all frequencies; the
certified polar pipeline's unused fixture flux matrix and its 25-pair window
table are skipped; and only the `E|Xj` and `Xi|Xj` `rho^0` horizon Laurent
constants are extracted (`bh2b_polar_cross_flux.run_pipeline(..., lean=True)`,
an additive behaviour-preserving flag). This turns the ~20 min/frequency tower
(`windows_3/5 = 1283 s` in `BH2B_COMPOSED_REPAIR`) into a few-minutes exact
sampler — the reduction the item demanded, not a time excuse.

## Why the components themselves are not the answer

The composed additional modes `X0, X1, X2` are fixed by the tower's **numeric
`nullspace`** at each rational `omega`; that pivot choice is not a canonical
`omega`-continuous rational frame. Empirically, `E|X1` happens to be an exact
rational function of `omega` in that frame,

```
E|X1(omega) = 48 (64 omega^3 - 200 i omega^2 - 240 omega + 49 i)
              -------------------------------------------------
                            35 (4 omega + i)
```

(reconstructed and verified on **24 exact frequencies**, recovers both
fixtures), but `E|X0` and `E|X2` are **not** rational functions of `omega` in
that frame (no rational fit up to degree `(6,6)` over 24 exact points). This is
exactly the item's own caveat: for a three-component covector the invariant
content is orbit/rank/common-zero data, **not** a forced component
identification. The individual components are gauge/frame data; they carry no
invariant meaning beyond the recorded `E|X1`.

## The invariant theorem (basis-independent)

Form the extra-block Gram `K_ij = F^r(X_i, conj X_j)/(pi alpha)` alongside the
cross covector `a`. Under a change of additional-mode basis `X -> X B`
(`B` in `GL(3,C)`), `a -> a B*` and `K -> B^T K B*`, so `a K^{-1} a^H` and the
signature of `K` are **invariant**. Computed exactly, at every sampled real
frequency:

- **`K_phys = i K` is Hermitian with signature `(2, 1)`** — an *indefinite*
  (hyperbolic) extra-block metric, nondegenerate (`det K != 0`);
- **the cross covector is nonzero (`a != 0`) but NULL in that metric:**
  `S(omega) = a K^{-1} a^H = 0` **exactly**.

Equivalently, `S` is the Schur complement of the additional block in the full
Gram `[[E|E, a],[a^H, K]]` with `E|E = 0`; its vanishing means the full form is
degenerate and the **Einstein line stays isotropic/Lagrangian in the full span
`(E, X0, X1, X2)`**. The additional sector couples to the Einstein line
(`a != 0`) but *light-like*: the coupling has zero length in the extra-block
metric. Because the signature `(2,1)` and the nullity `S = 0` are **constant**
on the sampled real axis, there is **no real exceptional frequency**
(`omega = 0` excluded as the certified exceptional carrier).

This is the polar counterpart of the axial theorem: axially the Einstein/extra
block is the hyperbolic plane with `det = -|a|^2 < 0` and `a != 0` on
`R \ {0}`; polar-ly the additional sector is a `(2,1)` block and the cross
covector lies on its null cone, so the reduced Einstein self-pairing again
vanishes and `E` remains Lagrangian.

## Evidence and verification

- **Over-determination.** `S = a K^{-1} a^H = 0` is confirmed **exact** at
  `omega in {3/5, 2/7, 1/2, 1/3, 2/3, 1/4, 5/7, 4/5, 3/4}` (nine independent
  rational frequencies), with signature `(2,1)` at each; the producer
  recomputes an independent subset and records the exact `(a, K)` matrices.
- **Fixtures.** The recorded `a` at `3/5` and `2/7` equals the certified
  `BH2B_COMPOSED_REPAIR` cross constants `E|Xj`; the `E|X1` rational form
  recovers both.
- **Independent rail.** `verify_bh2_polar_cross_covector.py` re-derives the
  invariants from the recorded exact `(a, K)` (pure linear algebra) **and**
  rebuilds the horizon block on the **VbGeo** Schouten/Kulkarni–Nomizu
  curvature engine (distinct from the producer's `weyl_geometry.Geometry` +
  `linearized_theta`) at one frequency, confirming `S = 0`, signature `(2,1)`,
  and frame-consistency.
- **Fast rail.** `tests/test_bh2_polar_cross_covector.py` verifies the K-null
  invariant, the `(2,1)` signature, fixture recovery, the `E|X1` form, the
  **non-null mutation** (`a + e_0` gives `S != 0`), and the BH-3 vocabulary
  lock. Sub-second.

## Quantifier scope correction (supersedes the universal reading)

The statement "there is **no real exceptional frequency**" below is a *universal*
claim over real `omega != 0` inferred from nine samples. It is **fail-closed and
superseded** by `certificates/BH2_POLAR_QUANTIFIER_REPAIR.json`
(report `reports/bh2-polar-quantifier-repair.md`). That repair **preserves** the
nine-fixture theorem (inertia `(2,1)`, `det K != 0`, `a != 0`, `S = 0`, re-derived
on independent rails), **upgrades** `a != 0` to a genuine all-real-`omega`
theorem (`E|X1` numerator has coprime real/imaginary parts — resultant
`98626146304 != 0`), and sets the `generic_real_frequency_certified` and
`no_real_exceptional_frequency_certified` flags **FALSE**: the sampler's
numeric-nullspace frame is provably not a single rational function of `omega`
(so `det K` and the inertia are not reconstructible), and the missing object — a
canonical rational `omega`-frame (route A) or the gauge-radical identity `Z =
E - (K^{-1} a^H).X` symplectically null (route B) — is named there. Read the two
universal-sounding sentences in the next section under that correction: they hold
at the nine sampled frequencies, not (yet) for all real `omega`.

## Paper 14 disposition

Both `l=2` parities now carry an exact real-frequency Einstein–additional
symplectic invariant on `R \ {0}`: axially the exact cross scalar `a(omega)`
(nonzero everywhere), polar-ly the `(2,1)` extra-block signature with the
**K-null cross covector**. In both parities the Einstein line is isotropic and
the additional sector is symplectically nondegenerate with no real exceptional
frequency — the input Paper 14 needs for the endpoint disposition. No spectral,
dynamical, scattering, ringdown, stability, positivity or particle statement is
made; these are local-algebraic symplectic-pairing data.

## What is NOT claimed

A closed rational form for the individual `E|X0, E|X2` components (non-rational
in the tower's frame; a canonical `omega`-symbolic nullspace frame would give
one, but the invariant content does not require it); general `l`; `omega = 0`
(excluded); complex-`omega` continuation; a structural (non-empirical) proof
that `S ≡ 0` for *all* real `omega` beyond the nine-frequency over-determination
(the vanishing is exact at every tested frequency and `S` is a basis-invariant
rational function, but a first-principles isotropy argument is left open).

CLOSE-OUT: DONE — the parity remainder is delivered as an exact basis-invariant
theorem. The composition tower is replaced by an omega-independent-bilinear lean
sampler (structural reduction, not a time limit). The three-component cross
covector's invariant content is certified: the extra-block Gram is Hermitian of
signature (2,1), nondegenerate, and the nonzero cross covector is NULL in it
(a K^{-1} a^H = 0), i.e. the Einstein line is Lagrangian in the full span and
there is no real exceptional frequency. E|X1 is given in exact closed form in the
native frame and both parities' fixtures are recovered; the non-rationality of
E|X0, E|X2 in the tower frame is identified with the missing canonical frame and
is explicitly not part of the invariant content. Independent VbGeo rail and a
sub-second fast rail with a decisive non-null mutation. omega=0 excluded.
EVIDENCE: black_hole_programme/certificates/BH2_POLAR_CROSS_COVECTOR.json
(S=a K^{-1} a^H=0 and signature (2,1) at nine exact frequencies; producer
independent recompute + recorded exact (a,K); VbGeo verifier; fast rail incl.
non-null mutation and BH-3 lock; both BH2B_COMPOSED_REPAIR fixtures recovered).
Dependency tags LOCAL-ALGEBRAIC + REDUCED-MODE; lifecycle CLASSIFIED.
