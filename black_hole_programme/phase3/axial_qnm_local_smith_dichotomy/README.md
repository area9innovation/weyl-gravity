# Axial QNM local Smith dichotomy

This package proves the exact local algebra governing a simple spin-two
Regge--Wheeler quasinormal frequency in the filtered axial pure-Weyl
connection.  In analytic factor frames,

\[
T_-=
\begin{pmatrix}
a&b&c\\
0&a&d\\
0&0&f
\end{pmatrix},
\qquad
a(\omega_n)=0,\quad a'(\omega_n)\ne0,\quad f(\omega_n)\ne0.
\]

Because \(f\) is a local unit, the spin-one row and column eliminate exactly.
The remaining \(2\times2\) problem has two and only two Smith types:

- \([b]\ne0\) in \(\mathcal O_{\omega_n}/(a)\): spin-two valuations
  \((0,2)\), one root vector, one length-two chain, and a double pole of
  the inverse connection matrix through \(-b/a^2\);
- \([b]=0\): spin-two valuations \((1,1)\), two independent root vectors,
  and only simple poles of the inverse connection matrix.

The certificate records both factor-ordered full valuations and conventionally
sorted Smith valuations.  Thus `(0,2,0)` is never confused with its sorted
form `(0,0,2)`.

The basis-independent selector is the Fredholm number

\[
\beta_n=\langle u_n^\#,\,\mathcal E(\omega_n)u_n\rangle.
\]

It is unchanged by
\(\mathcal E\mapsto\mathcal E+LQ-QL\).  Compatible normalizations give
\([b]\ne0\iff\beta_n\ne0\).

This package does **not** evaluate \(\beta_n\).  A certified QNM germ, an
adjoint cokernel germ, and a boundary-convergent or regularized pairing are
still missing.  Therefore no actual QNM is promoted to a double pole.
Promoting an inverse-connection double pole to a bulk Green-resolvent pole
also requires analytic horizon-to-bulk and infinity-to-bulk reconstruction
maps whose source/observable projections do not annihilate the rank-one
principal part.

Run:

```bash
PYTHONPATH=. python3 -m \
  black_hole_programme.phase3.axial_qnm_local_smith_dichotomy.produce
PYTHONPATH=. python3 -m \
  black_hole_programme.phase3.axial_qnm_local_smith_dichotomy.verify
PYTHONPATH=. python3 -m unittest -v \
  black_hole_programme.phase3.axial_qnm_local_smith_dichotomy.test_local_smith
```
