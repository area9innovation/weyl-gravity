# Generic ghost nonzero-momentum three-insertion triangle

Dependency tag: `EUCLIDEAN-SPECTRAL`.

## Result

For generic Euclidean external momenta (k_1+k_2+k_3=0), the three-Ricci
ghost row is reduced exactly to an eight-sector Feynman-simplex/Wick kernel.
With

\[
q_0=p,\qquad q_1=p+k_1,\qquad q_2=p-k_3,
\qquad
\Pi(q)=I-\frac13\frac{qq^T}{q^2},
\]

the direct integrand is

\[
\frac{\operatorname{tr}[\Pi(q_0)R_1\Pi(q_1)R_2\Pi(q_2)R_3]}
{q_0^2q_1^2q_2^2}.
\]

Expanding the three projectors gives exactly (2^3=8) sectors with
multiplicities `(1,3,3,1)`. After Feynman parametrization and shifting the
loop momentum, the sector with (s) longitudinal projectors has Wick rows
(m=0,\ldots,s). The exact coefficient per metric pairing and denominator are

\[
c_{s,m}=\frac{(s-m)!}{2^m},
\qquad
\Delta^{m-s-1},
\]

where

\[
\Delta=\alpha_0\alpha_1k_1^2+
\alpha_1\alpha_2k_2^2+
\alpha_2\alpha_0k_3^2.
\]

There are twenty Wick rows in total. Including (W=-2\operatorname{Ric}) and
the cubic Tr-log coefficient gives the overall multiplier (-8/3)(4\pi)^{-2}.

## Verification and boundary

The independent verifier evaluates the direct projector integrand and all
eight expanded sectors on exact rational momenta and noncommuting symmetric
endomorphisms. It also verifies cyclic covariance and reconstructs every
simplex/Wick coefficient from the gamma-function formula.

This is a full parametric labelled-Ricci triangle kernel, but it is not yet a
repository five-carrier decomposition. Its zero-derivative sector can feed
(I_{10}); the longitudinal projector sectors carry two, four, and six
external derivatives and can also feed (I_{24},I_{25},I_{28},I_{29}). The
frozen scalar-flat (K_{\mu\nu}) crosswalk and tensor-basis projection have not
been applied. The curved-Endo one- and two-insertion rows also remain open.

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_ghost_n3_triangle_kernel --emit
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_ghost_n3_triangle_kernel
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_ghost_n3_triangle_kernel
```
