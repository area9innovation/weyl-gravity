# Cylinder-wave foundational strength ladder

`FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1` answers a narrower and more
useful question than “what axioms does the wave equation need?”  It asks what
changes as one moves from a named finite Fourier fixture to a completed energy
solution, a spacetime distribution, and a causal Green operator.  Those are
different mathematical claims and they must not inherit one foundational label.

The conclusion is a separation result.  Finite mode evolution is exact finite
algebra.  A named infinite datum is also constructively controlled when it
comes with a tolerance-to-cutoff modulus.  A localized distribution and causal
support require additional analytic structure that cannot be read off from
finite Fourier evolution.

## The six levels

| Level | Object | Status | New mathematical commitment |
|---|---|---|---|
| L0 | finite Gaussian-rational Laurent wave | certified | finite sums, integer differentiation weights, rational equality |
| L1 | named energy sequence with `N(k)=2^k` | certified | explicit tolerance-to-cutoff data |
| L2 | arbitrary coded energy carrier with a supplied modulus | formalization target | coded completion and uniform tail control |
| L3 | coefficient-weak solution | formalization target | pairing against finite Fourier tests |
| L4 | localized spacetime distribution | open | test-function topology, integration, and continuity |
| L5 | causal Green operator | conditional import only | localized energy estimates, uniqueness, support, and globalization |

At L0 the checker constructs

```text
u_N = sum_{|n|<=N} (a_n z^n w^n + b_n z^{-n} w^n)
```

over `Q(i)` and proves exactly that
`(partial_t^2-partial_x^2)u_N=0`.  It also proves that projections are nested
and that the displayed energy is positive.  This is a `LOCAL-ALGEBRAIC` and
`REDUCED-MODE` result; no transcendental phase is sampled.

At L1, take `c_n=1/n^2`.  Its energy summand is `1/n^2`, and

```text
1/n^2 <= 1/(n-1) - 1/n       for n >= 2.
```

The telescoping bound gives a tail no larger than `1/N`.  Therefore
`N(k)=2^k` is an explicit energy-tail modulus.  For this named sequence, a
Cauchy name is produced rather than merely asserted to exist.

## The first physics-to-mathematics distinction

“Finite total energy” and “a cutoff can be produced for every requested error”
are classically close but constructively different inputs.  The latter already
contains a tail modulus.  The former does not uniformly provide one in this
audit.  Thus the physical content of an operational error-control postulate is
stronger than a bare bounded-energy statement at the level of representations.

This is not yet an `RCA_0` theorem.  The next formal task is to choose an exact
second-order-arithmetic coding and prove that the coordinate propagator maps an
input name with a supplied modulus to an output name in `RCA_0`.  Only then is
it meaningful to attempt a reversal after removing the modulus.

## Why finite spectral dynamics cannot prove causality

The sharpest exact negative result is very small.  Projecting a point source to
modes `-N,...,N` produces the Dirichlet kernel.  At the antipodal point,

```text
D_N(pi) = sum_{n=-N}^N (-1)^n = (-1)^N,
```

which is nonzero for every cutoff.  A finite spectral approximation is
therefore spatially global.  Its exact time evolution can approximate a causal
continuum solution, but the finite fixture itself cannot certify finite
propagation or support inclusion.  Causal support must enter through localized
energy/uniqueness arguments and a continuum comparison theorem.

This explains why the conditional biwave Green result needs normally
hyperbolic factor Green maps, Sobolev completions, energy estimates,
uniqueness, support propagation, and slab globalization in addition to its
finite resolvent algebra.

## Literature contrast

Weihrauch and Zhong prove computability of wave propagation for specified
continuously differentiable and Sobolev representations.  Pour-El and Richards
give a noncomputability result in another representation and regularity
setting.  The correct conclusion is representation dependence, not that the
two results conflict.  Neither paper supplies the missing
`RCA_0`/`WKL_0`/`ACA_0` reversal for this cylinder encoding.

The Weihrauch-Zhong publisher record was reviewed, but its direct PDF endpoint
returned an HTML redirect in the receipt environment.  It is therefore
`METADATA_ONLY`, as is the already recorded Pour-El-Richards source.  These
records block a literature freeze but not the exact local certificate.

## What is established

- Fixed finite cylinder waves and their Galerkin nesting are exact.
- The named `1/n^2` energy datum has an explicit primitive-recursive tail
  modulus.
- Finite Fourier truncations cannot themselves witness localized causal
  support.
- The first formal reverse-mathematics target is isolated: coded energy
  evolution with a supplied modulus.
- The relation graph distinguishes sufficient, conditional, representation-
  dependent, counterexample-to-method, and open edges.

## What is not established

No weakest base is proved.  There is no `RCA_0` upper-bound certificate, no
`WKL_0` or `ACA_0` reversal, no uniform modulus extractor, no constructed
spacetime distribution, no Green operator, and no new `LORENTZIAN-CAUSAL`
claim.  In particular, a coefficient-weak solution is not silently identified
with a localized distributional solution.

## Verification

```text
python3 foundations/check_cylinder_wave_strength_ladder.py
python3 foundations/verify_cylinder_wave_strength_ladder.py
python3 -m unittest foundations.tests.test_cylinder_wave_strength_ladder
```
