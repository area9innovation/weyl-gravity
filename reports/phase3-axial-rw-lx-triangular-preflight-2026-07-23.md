# Phase 3 axial \(L_{\rm RW}\)–\(L_x\) triangular preflight

Date: 23 July 2026

## Question

The complete axial Bach module has local dimension six, while a scalar
Regge--Wheeler square has dimension four.  The excluded scalar-square
shortcut therefore leaves a dimensionally viable possibility:

\[
\ker(L_{\rm RW}^2)\oplus\ker(L_x),
\]

or a non-split triangular module with the same three two-dimensional
composition factors.

This preflight tests that possibility from the exact four-state Ricci
carrier \(A_4\).  Endpoint exponent and flux signatures are used only as
comparisons, never as factorization evidence.

## Exact scalar elimination

Write

\[
L(a,b)=D_r^2+aD_r+b.
\]

The Regge--Wheeler factor in ingoing Eddington--Finkelstein phase convention
\(\exp(i\omega v)\) is

\[
L_{\rm RW}
=D_r^2+
\left[
\frac{2}{r(r-2)}
+\frac{2i\omega r}{r-2}
\right]D_r
-\frac{6(r-1)}{r^2(r-2)}.
\]

The exact carrier coordinate \(P\) is cyclic.  The determinant of the four
rows \(P,D_rP,D_r^2P,D_r^3P\) is

\[
\det\mathcal O_P
=-\frac{4\omega^2}{r^2(r-2)^2},
\]

which is nonzero for \(r>2\) and
\(\omega\in[1/2,3/4]\).  Exact elimination gives an order-four scalar
operator that factors as

\[
\boxed{L_4=L_x\circ L_{\rm RW}},
\]

where

\[
L_x=D_r^2+
\frac{2i(\omega r^2-3ir+3i)}{r(r-2)}D_r
+\frac{2i(3\omega r^2-4\omega r-i)}{r(r-2)^2}.
\]

The two factors are not identical as printed.  In particular,

\[
a_x-a_{\rm RW}=\frac{2(3r-4)}{r(r-2)}\ne0.
\]

No gauge or Darboux equivalence between them is asserted.

### The \(L_x\) factor is spin-one type

The quotient factor has a simple exact geometric form.  Set

\[
Z=\frac{y}{r^2(r-2)},\qquad
f=\frac{r-2}{r},\qquad
D_{r_*}=fD_r.
\]

Then \(L_xZ=0\) becomes

\[
\boxed{
D_{r_*}^2y+2i\omega D_{r_*}y
-\frac{6(r-2)}{r^3}y=0.
}
\]

The potential is

\[
V_1=f\frac{\ell(\ell+1)}{r^2}
=\frac{6(r-2)}{r^3},
\qquad \ell=2,
\]

which is the standard spin-one/Maxwell Regge--Wheeler potential in the
ingoing-EF Fourier convention.  Thus \(L_x\) is an exactly certified
spin-one-type **differential factor**.  This does not identify a physical
Maxwell field, spin-one particle, or reconstruction assignment inside pure
Weyl gravity.

## Exact carrier submodule and quotient

For every \(L_{\rm RW}P=0\), define

\[
Q=-\frac{i(P+rP')}{\omega r}.
\]

Together with the differentiated \(Q'\), this gives a rational embedding

\[
J:M_{\rm RW}\hookrightarrow M_{A_4}
\]

obeying

\[
J'+JA_{\rm RW}=A_4J.
\]

Conversely define \(Z=L_{\rm RW}P\).  The exact two-row map

\[
K(P,P',Q,Q')=(Z,Z')
\]

satisfies

\[
K'+KA_4=A_xK,\qquad KJ=0.
\]

An explicit rational right inverse \(N\) has \(KN=I_2\).  The gauge
\(T=[J,N]\) has

\[
\det T=-\frac{r^2(r-2)^2}{4\omega^2},
\]

and produces

\[
T^{-1}(A_4T-T')
=
\begin{pmatrix}
0&1&0&0\\
-b_{\rm RW}&-a_{\rm RW}&1&0\\
0&0&0&1\\
0&0&-b_x&-a_x
\end{pmatrix}.
\]

Thus the carrier has the exact differential-module sequence

\[
\boxed{
0\longrightarrow M_{\rm RW}
\longrightarrow M_{A_4}
\longrightarrow M_x
\longrightarrow0.
}
\]

This is the canonical first-order form of
\(L_x\circ L_{\rm RW}\).

## The second Regge--Wheeler factor

The carrier-zero metric kernel is also the Regge--Wheeler module.  With

\[
\Psi=\frac{(1-2/r)H_1+H_0}{r},
\]

the exact rational map \(U:(H_1,F)\mapsto(\Psi,\Psi')\) satisfies

\[
U'+UK_2=A_{\rm RW}U,
\]

and

\[
\det U
=-\frac{i\omega^2(r-2)}
{2r(\omega r-2i)}.
\]

It is invertible throughout the real exterior pilot domain.

The complete six-state Bach module therefore has an exact filtration whose
diagonal factors, after reordering, are

\[
\boxed{
M_{\rm RW}^{\rm Einstein},\qquad
M_{\rm RW}^{\rm carrier},\qquad
M_x.
}
\]

This is the requested dimensionally viable **triangular equivalent**.

## First obstruction to the stronger direct decomposition

The result does not yet prove

\[
M_{\rm Bach}\cong
\ker(L_{\rm RW}^2)\oplus\ker(L_x).
\]

In the natural exact gauges above, the transformed full connection retains
nonzero extension terms.  For example, one \(M_x\)-to-metric-RW entry is

\[
-\frac{
r(3\omega^2r^4-4\omega^2r^3-10i\omega r^2
+12i\omega r+12r^2-40r+32)}
{8(\omega r-2i)^2},
\]

which is not the zero rational function.  This is the first exact
obstruction to reading off a direct sum in the natural gauge.  It is not a
gauge-invariant no-splitting theorem: a stronger result would require
solving the rational extension-splitting equations and identifying the two
RW factors with the canonical scalar-square extension.

## Endpoint and Jordan comparison

The carrier horizon exponents split into two pairs,

\[
\{0,-4i\omega\}\cup\{0,-2-4i\omega\},
\]

and its infinity rates have multiplicity two at both
\(0\) and \(-2i\omega\).  These multiplicities are compatible with the exact
\(2+2\) carrier filtration, but did not prove it.

Likewise the endpoint flux decomposition

\[
(1,1)\widehat\oplus(0,1)
\]

is dimensionally compatible with the three two-dimensional factors, but it
does not assign the endpoint Witt vectors to \(M_{\rm RW}\) or \(M_x\).
That assignment requires applying the exact quotient \(K\) to normalized
endpoint solutions.

Finally, a fixed-frequency radial sensitivity remains an inhomogeneous
variational column.  A genuine time-translation Jordan vector contains the
\(iv\,u\) term obtained by differentiating
\(\exp(i\omega v)u(r,\omega)\).  Neither the operator filtration nor the
endpoint Witt basis changes this distinction.

## Verification

```bash
python3 -m black_hole_programme.phase3.axial_rw_lx_triangular_preflight.verify
python3 -m unittest -v \
  black_hole_programme.phase3.axial_rw_lx_triangular_preflight.tests.test_preflight
```

The verifier imports the frozen six-state flow by content hash, derives the
cyclic order-four scalar operator, checks its exact noncommutative
factorization, verifies the embedding, quotient, right inverse and rational
triangular gauge, proves the independent Einstein-kernel RW conjugacy, and
checks the first nonzero extension witness and all claim boundaries.
