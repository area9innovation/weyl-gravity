# Polar cross-covector: universal-quantifier repair (fail-closed)

**Certificate:** `certificates/BH2_POLAR_QUANTIFIER_REPAIR.json`
**Result token:** `BH2_POLAR_CROSS_COVECTOR_NINE_FIXTURE_THEOREM_UNIVERSAL_SHORTFALL`
**Dependency tags:** `LOCAL-ALGEBRAIC` + `REDUCED-MODE`. **Lifecycle:** `CLASSIFIED`.
**Disposition:** `NINE_FIXTURE_THEOREM + UNIVERSAL_SHORTFALL`.
**Producer:** `bh2_polar_quantifier_repair.py` ·
**Verifier:** `verify_bh2_polar_quantifier_repair.py` (four independent rails) ·
**Fast rail:** `tests/test_bh2_polar_quantifier_repair.py`

## What was repaired

`BH2_POLAR_CROSS_COVECTOR` concluded, from **nine** exact rational
frequencies, that the polar `l=2` extra-block Gram `K_phys = i K` is Hermitian
of inertia `(2,1)`, nondegenerate, that the nonzero cross covector `a` is K-null
(`S = a K^{-1} a^H = 0`), and that **"there is no real exceptional frequency"**.
The last clause is a **universal** statement over real `omega != 0` inferred
from a finite sample; its `no_real_exceptional_frequency_certified` flag was an
unsupported quantifier. This repair decides the quantifier by the one route the
available machinery supports and fail-closes the rest. The nine-frequency
null-cone structure is valuable and is **retained in full**.

## What is preserved (the valid fixture theorem, re-derived independently)

Importing the nine exact `(a, K)` from `BH2_POLAR_CROSS_COVECTOR` by content
hash, at each recorded `omega` in `{1/2, 1/3, 1/4, 2/3, 2/7, 3/4, 3/5, 4/5, 5/7}`:

- `K_phys = i K` Hermitian, `det K != 0`, **inertia `(2,1)`** — re-derived by
  the Jacobi leading-principal-minor sign rule (producer) **and** by Hermitian
  eigenvalue signs (verifier);
- `a != 0` and `a K^{-1} a^H = 0` — `S` re-derived by solving `K x = a^H`
  (producer) **and** by the explicit inverse (verifier).

## What is upgraded to a genuine all-real-frequency theorem

**`a(omega) != 0` for all real `omega != 0`.** The one component that is rational
in the tower's native frame,

```
E|X1 = 48 (64 w^3 - 200 i w^2 - 240 w + 49 i) / (35 (4 w + i)),
```

has numerator `48 (P + i Q)` with `P = 64 w^3 - 240 w` and `Q = 49 - 200 w^2`
two **real** polynomials whose resultant is nonzero
(`res(P, Q) = 98626146304`), so `P` and `Q` share no common root (their real
roots `{0, ±sqrt(15)/2}` and `{±7 sqrt(2)/20}` are disjoint); the denominator
`4 w + i` has no real zero. Hence `E|X1 != 0` at every real `omega`, so the
covector `a` is nonzero there — `a = 0` is basis-invariant, so one nonzero
component in any frame forces `a != 0`. This uses one rational component only as
a **non-vanishing witness**, never as a degree bound for the covector or Gram.

## Why the universal signature / no-exceptional-frequency statement does not close

Only **frame-invariant** scalars may be reconstructed across the nine
independently normalized samples. Under a change of additional-mode basis
`X -> X B(omega)` (`B` in `GL(3, C)`) one has `a -> a B*`, `K -> B^T K B*`, so

- `S = a K^{-1} a^H` is **invariant** (reconstructible; `0` at all nine) and
  `a = 0` is invariant, but
- `det K` and the char-poly coefficients `t1, t2, t3` of `K_phys` are
  frame-**covariant** (`det K -> |det B|^2 det K`; the `t_i` change under
  congruence), so they form a single rational function of `omega` **only if**
  `B(omega)` does.

The sampler builds `X0, X1, X2` from an independent numeric nullspace at each
`omega`, which is **not** a canonical rational frame: `E|X0` and `E|X2` are
non-rational in it (no rational fit up to degree `(6,6)` over 24 exact points,
recorded in the polar report), and here `t1, t2, t3` admit **no** rational fit up
to total degree 8 (seven-point fit, two disjoint held-out points; reproduced by
the verifier on a disjoint split). Therefore `det K(omega)` and the inertia are
**not** reconstructible from this data, the real zeros of `det K` cannot be
isolated, and "no real exceptional frequency" is **not** established for generic
`omega`.

## Fail-closed disposition

`generic_real_frequency_certified` and `no_real_exceptional_frequency_certified`
are set **FALSE**. The result is an exact **nine-fixture classification** with a
**universal shortfall**. The `BH2_POLAR_CROSS_COVECTOR` universal reading of
`no_real_exceptional_frequency_certified` is superseded by this certificate; its
producer's `claim_flags` are narrowed in the same commit, and the atlas wording
is narrowed to the fixture scope. Paper 14 does **not** cite the covector
certificate, so no paper wording overclaims.

## Minimal missing object (either closes the universal statement)

- **Route A — canonical rational frame.** A canonical rational/meromorphic
  `omega`-frame for `X0, X1, X2` (equivalently a rational nullspace
  normalization of the `compose`/`einstein_mode` step of
  `bh2b_polar_cross_flux`) in which `a(omega)` and `K(omega)` are exact rational
  matrices. Then `det K` factors, its real zeros are Sturm-isolable, and inertia
  is constant on each sign of `omega` between them. Direct symbolic construction
  is presently intractable: the `NORD = 16` Frobenius recursion with a per-order
  nullspace at symbolic `omega` does not terminate in usable time.
- **Route B — structural identity.** `S = 0` is equivalent to the full `4x4`
  Gram `G = [[E|E, a], [a^H, K]]` (with `E|E = 0`) being degenerate, i.e. the
  modified Einstein direction `Z = E - (K^{-1} a^H) . X` lying in the radical of
  `F^r` on `span(E, X0, X1, X2)`. Proving `Z` is symplectically null / pure
  gauge for all real `omega != 0`, with a separate nondegeneracy and
  inertia-constancy argument, closes the quantifier structurally. This is the
  natural even-parity twin of the axial RW-null theorem and is the recommended
  successor route; it also feeds the general-`l` invariant cross pairing.

## Evidence and verification

- **Independent verifier** (`verify_bh2_polar_quantifier_repair.py`, 19/19):
  fixture theorem by eigenvalue signs + explicit inverse; `a != 0` by
  `gcd(P, Q)` constant and disjoint real-root isolation (independent of the
  resultant); frame obstruction reproduced on a disjoint fit/hold split;
  provenance hashes and schema.
- **Fast rail** (`tests/test_bh2_polar_quantifier_repair.py`, 9/9, sub-second):
  fail-closed flags, `a != 0` theorem, preserved fixture theorem, `S = 0`
  re-derived from the polar records, obstruction, provenance, named missing
  object, BH-3 vocabulary lock.

## What is NOT claimed

Generic-`omega` inertia constancy and absence of real exceptional frequencies
(fail closed); an all-`omega` proof of `S = 0` (it is an exact frame-invariant
fact at nine frequencies only); general `l`; `omega = 0` (excluded); complex-`omega`
continuation; any finite-flux, scattering, quasinormal, ringdown, stability,
positivity, or particle statement.

CLOSE-OUT: DONE — the unsupported universal quantifier is repaired. The
nine-frequency null-cone fixture theorem is preserved and re-derived on
independent rails; `a != 0` is upgraded to a genuine all-real-`omega` theorem via
the resultant/GCD argument on `E|X1`; the universal inertia / no-exceptional-
frequency claim is fail-closed because the sampler's numeric-nullspace frame is
provably not a single rational function of `omega` (no rational fit for the
char-poly invariants over the nine samples on held-out splits), so `det K` and
the inertia are not reconstructible; and the minimal missing object is named on
both routes (canonical rational frame; gauge-radical identity). The
`BH2_POLAR_CROSS_COVECTOR` universal flag is superseded and its producer flags +
the atlas wording are narrowed in the same commit.
EVIDENCE: black_hole_programme/certificates/BH2_POLAR_QUANTIFIER_REPAIR.json
(nine-fixture inertia (2,1)/S=0 on two independent rails; a!=0 all real omega via
res(P,Q)=98626146304 and disjoint real roots; frame obstruction on held-out
splits; fail-closed universal flags; missing object named routes A and B).
Dependency tags LOCAL-ALGEBRAIC + REDUCED-MODE; lifecycle CLASSIFIED; disposition
NINE_FIXTURE_THEOREM + UNIVERSAL_SHORTFALL.
