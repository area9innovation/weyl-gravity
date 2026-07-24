# RW/Maxwell simplicity and rational endomorphisms

This exact `LOCAL-ALGEBRAIC` package classifies the scalar Schwarzschild
spin-two Regge--Wheeler and spin-one Maxwell differential modules over
`C(r)[D]`, with `D=((r-2)/r)d/dr`.

For every integer `ell>=2` and every real `omega>0`, it certifies:

- both scalar modules are simple;
- both rational endomorphism rings are the scalars;
- the same-sign Jost reduction produces the exact algebraically special
  controls `omega=±i(ell-1)ell(ell+1)(ell+2)/12`;
- a separate exhaustive `ell=2` audit shows that the selected-frame events
  `i/4`, `i/2`, and `i` are not rational reducibility points;
- the old axial `ell=2` projective-cocycle witness zero at `omega^2=3` is not
  a splitting point: fixed coefficient and augmented minors certify
  nonsplitting throughout the positive real axis;
- consequently the only rational differential-module involutions on the
  certified axial repeated-spin-two Bach block are `+I` and `-I`.

The exhaustive step is analytic: local exponents, ordinary-point regularity,
Jost-sign matching, and infinity balance reduce the Riccati and
symmetric-square searches to finite rational ansätze. The producer and
verifier independently check the resulting exact substitutions and rank
minors.

The package does **not** classify the complete complex-frequency reducibility
locus or exclude nonlocal, spectral, scattering-dependent, or BRST `C`
operators. It does not prove an all-`ell` Bach lift or nonsplitting theorem,
select a physical QNM Smith type, or establish a Green-resolvent double pole.

Run:

```bash
python3 produce.py
python3 verify.py
python3 -m unittest -v test_simplicity.py
```
