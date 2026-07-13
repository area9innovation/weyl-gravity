# C2g-W: the on-shell Weyl-curvature module

## Exact character identification

The `E/A/L` oscillator tower is the cylinder realization of the on-shell
Weyl-curvature module.  For the positive chirality, begin with the conformal
primary

\[
C_{\alpha(4)}:\qquad (\Delta;j_L,j_R)=(2;2,0).
\]

The equation of motion is the linearized Bach tensor

\[
B_{\alpha(2)\dot\alpha(2)}:\qquad (4;1,1),
\]

and its divergence identity transforms as

\[
\nabla^{\alpha\dot\alpha}
B_{\alpha\beta\dot\alpha\dot\beta}=0:
\qquad (5;\tfrac12,\tfrac12).
\]

Consequently the one-chirality character is

\[
\boxed{
\chi_{\mathcal H_+}
=\chi_{\mathcal V(2;2,0)}
-\chi_{\mathcal V(4;1,1)}
+\chi_{\mathcal V(5;\frac12,\frac12)}.}
\]

Unrefined, this is

\[
\chi_{\mathcal H_+}(q)
=\frac{5q^2-9q^4+4q^5}{(1-q)^4}.
\]

Parity completion gives

\[
\chi_{\mathcal H_+\oplus\mathcal H_-}(q)
=\frac{10q^2-18q^4+8q^5}{(1-q)^4},
\]

which is exactly the Weyl-graviton character already checked independently
from the cylinder determinants in `verify_conformal_cylinder_form.py`.

The primary-field interpretation is consistent with the conformal geometry
of higher-spin Weyl tensors on conformally flat backgrounds.  The character
resolution and counting modulo equations of motion and identities are also
the standard conformal-higher-spin operator-counting construction.  See
Kuzenko--Ponds, [arXiv:1902.08010](https://arxiv.org/abs/1902.08010), and
Beccaria--Bekaert--Tseytlin,
[arXiv:1406.3542](https://arxiv.org/abs/1406.3542).

## Refined tower theorem

The executable expands the three generalized-Verma characters in the full
`SU(2)_L x SU(2)_R` weight lattice and decomposes every checked level.  For
one chirality it obtains exactly

\[
E_n=\left(\frac{n+2}{2},\frac{n-2}{2}\right),\qquad n\geq2,
\]

\[
A_n=\left(\frac n2,\frac{n-2}{2}\right),\qquad n\geq3,
\]

\[
L_n=\left(\frac n2,\frac{n-4}{2}\right),\qquad n\geq4.
\]

Their dimensions are

\[
\dim E_n=(n+3)(n-1),\quad
\dim A_n=(n+1)(n-1),\quad
\dim L_n=(n+1)(n-3).
\]

At energy four, the unconstrained second descendant level contains

\[
(3,1)\oplus(2,1)\oplus(1,1)\oplus(2,0).
\]

The Bach equation removes precisely the missing nine-dimensional `(1,1)`
irrep, leaving the observed `E_4+A_4+L_4` inventory.

## Hard buffer predictions

At energy five, per chirality,

\[
E_5=(\tfrac72,\tfrac32)_{32},\qquad
A_5=(\tfrac52,\tfrac32)_{24},\qquad
L_5=(\tfrac52,\tfrac12)_{12}.
\]

At energy six,

\[
E_6=(4,2)_{45},\qquad
A_6=(3,2)_{35},\qquad
L_6=(3,1)_{21}.
\]

Thus the two-chirality dimensions at energies two through six are

\[
(10,40,82,136,202),
\]

and the cumulative buffer has dimension

\[
\boxed{470}.
\]

These are acceptance tests for the all-energy generator implementation.

## Scope

The rational character identity is exact, and the refined decomposition is
verified through an arbitrary requested finite energy.  Character equality
alone does not prove exactness of a differential sequence.  The Bach map and
its identity come from the linear field equation and its Noether identity;
the executable therefore refuses a request to infer exactness from counting
alone.

Run

```bash
python3 symbolic/verify_conformal_weyl_module.py --max-energy 12
```

The stronger character-only claim must fail:

```bash
python3 symbolic/verify_conformal_weyl_module.py --claim-exact-sequence
```
