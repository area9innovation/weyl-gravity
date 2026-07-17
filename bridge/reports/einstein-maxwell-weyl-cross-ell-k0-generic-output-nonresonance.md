# Unbounded cross-ell `k=0` generic-output nonresonance

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

For every distinct pair of generic input harmonics `ell_1,ell_2>=2`, every
nonzero quadratic sum/difference frequency misses every angularly allowed
generic Weyl--Maxwell target shell `L>=2`.

Write each primary frequency as

```text
omega_branch(ell)=ell+u_branch(ell).
```

Exact squared inequalities give

```text
-1/2 < u_minus < -1/5,
 3/10 < u_extra < 1/2,
 1 < u_plus < 5/4.
```

The angular triangle condition then reduces every possible equation
`omega_1+omega_2=omega_3` to five unordered saturated families.  Three are
strictly sign-separated by sharper rational bounds.  The two remaining
families are

```text
minus(a)+minus(b) = extra(a+b-1),
minus(a)+extra(b) = plus(a+b-1).
```

After squaring, their resonance polynomials lie in a multiquadratic field.
For distinct nonrational squarefree parts, the product-root coefficient is
uniquely nonzero.  When squarefree parts coincide, the merged irrational
coefficient has a strict sign.  If one inner root is rational, the remaining
irrational coefficient still has a strict sign.  If both are rational, the
extra shell's `2/3` denominator contradicts the squared frequency equation.
Thus the Pell-type degeneracies do not create exceptions.

This is the unbounded `G3` generic-output theorem.  It leaves one spectral
gate: adjacent input harmonics can couple to exceptional `L=1`, whose roots
must be checked separately.  It also does not compute the mixed quadratic
source.  Once `L=1` is closed, any cross-`ell` failure must be an actual
source/cokernel obstruction rather than a nonzero-frequency pole.

## Verification receipt

Date: 2026-07-18.  Tier 0 scoped compilation, JSON, and diff checks passed
in `0.06 s`.  Tier 1 producer replay, independent symbolic verifier, and
four tests passed in `1.1 s`.  Tier 2 was unnecessary because the imported
shell data and bounded audit are unchanged and content-addressed.  Tier 3 was
not run because exceptional `L=1` and the mixed source remain open.
