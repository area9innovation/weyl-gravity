# BT logarithmic-shell Møller limit

**Result:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

The physical leading-log shell can be represented in

\[
 \mathbb C h\oplus
 L^2((0,\infty),dy)\otimes\mathbb C^3,\qquad y=-\log r .
\]

For \(\ell=\log c>0\), let \(u_{n,i}\) be the normalized indicator of
\([2n\ell,(2n+1)\ell]\) in pair channel \(i\).  These vectors are orthonormal
and move to \(r=0\) as \(n\to\infty\).  The certified physical real column is

\[
 A_nh=\frac{\sqrt3}{12}
 (u_{n,12}+u_{n,13}+u_{n,23}),\qquad
 \lVert A_nh\rVert^2=\frac1{16}.
\]

For distinct shells,

\[
 \lVert A_nh-A_mh\rVert^2
 =\frac1{16}+\frac1{16}=\frac18 .
\]

Thus \(A_nh\) is not Cauchy.  The regulated shell isometries cannot have a
strong Møller limit on the ordinary logarithmic \(L^2\) carrier, already at
their first perturbative coefficient.

The obstruction also holds for the exact finite-shell exponential.  With
\(v_n=4A_nh\),

\[
 e^{xA_n}h=\cos(x/4)h+\sin(x/4)v_n,\qquad
 \lVert e^{xA_n}h-e^{xA_m}h\rVert^2=2\sin^2(x/4).
\]

Hence no strong limit exists whenever \(\sin(x/4)\ne0\), including every
sufficiently small nonzero perturbative \(x\).

The shell vectors converge weakly to zero.  With \(B_n=A_n^2/2\), the weak
coefficient limits are

\[
 A_{\rm weak}=0,\qquad
 B_{\rm weak}=-\frac1{32}|h\rangle\langle h|.
\]

Therefore

\[
 S_{\rm weak}^\dagger S_{\rm weak}
 =1-\frac{x^2}{16}|h\rangle\langle h|+O(x^3).
\]

The weak limit is a contraction, not an isometry: the \(+1/16\) real
probability has escaped to the endpoint.

For the exact finite-shell exponential the weak limit is

\[
 S_{\rm weak}
 =1+\bigl(\cos(x/4)-1\bigr)|h\rangle\langle h|,\qquad
 S_{\rm weak}^\dagger S_{\rm weak}-1
 =-\sin^2(x/4)|h\rangle\langle h|.
\]

There is an exact reduced-mode dressed completion.  Let a fixed abstract fibre
have basis \((h,e_{12},e_{13},e_{23})\), and define \(J_ne_i=u_{n,i}\).
Then

\[
 J_n^\dagger A_nJ_n=A_*,\qquad
 J_n^\dagger B_nJ_n=\frac12A_*^2
\]

for every \(n\).  The pulled-back isometry \(e^{xA_*}\) is
regulator-independent and retains hard response \(-1/16\), real response
\(+1/16\), and inclusive response zero.
At all orders in the finite-shell parameter its hard and endpoint
probabilities are \(\cos^2(x/4)\) and \(\sin^2(x/4)\), whose sum is one.

This distinguishes two statements: an ordinary LSZ/Fock Møller limit is
exactly obstructed, while a leading-log dressed boundary-fibre bundle exists.
The abstract endpoint fibre has not been affiliated with a local detector
algebra or derived from the BT asymptotic Hamiltonian.  It is therefore not
yet the full physical S-matrix, a beyond-tree positivity theorem, or all-order
Eq. (19).

All verification ran sequentially under `ulimit -v 500000` except Git.
Certificate generation and the 22/22 producer each passed in 0.04 s
(20,864 KB and 20,432 KB peak RSS); the independent verifier passed 16/16 in
0.11 s (30,292 KB), and nine tests with seven decisive mutations passed in
0.98 s (30,476 KB).  Python compilation and JSON parsing passed in 0.19 s
(16,244 KB), the event reproduced FNV-1a `3b69d341bcae60f3`, and
`git diff --check` passed uncapped in 0.01 s (11,028 KB).  Papers V and VI
compiled twice; final passes took 0.43 s and 0.46 s with at most 50,840 KB
peak RSS.  Tier 2 was not run because all mathematical inputs are unchanged
and content-addressed and no shared interface changed.  Tier 3 was not run
because this is not a freeze or release and promotes neither a local physical
S-matrix nor all-order Eq. (19).
