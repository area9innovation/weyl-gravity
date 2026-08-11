# BT physical-shell pseudo-unitary completion

**Result:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

This result concerns the regulated physical S-matrix, not the projector
pushforward \(R_t P R_t^\dagger\).  Put

\[
 x^2=\eta=\frac{\lambda^2\log c}{\pi^2},\qquad
 S_{\rm phys}(x)=1+xA+x^2B+O(x^3).
\]

On a positive hard-plus-collinear generalized-Born quotient, pseudo-unitarity
through this order is equivalent to

\[
 A^\dagger=-A,\qquad
 B+B^\dagger+A^\dagger A=0.
\]

The certified five-point process fixes the physical real-column norm:

\[
 \lVert Ah\rVert^2
 =3\left(\frac1{48}\right)=\frac1{16}.
\]

Taking the hard diagonal of the second pseudo-unitarity equation gives the
universal identity

\[
 2\,\operatorname{Re}B_{hh}
 =-\lVert Ah\rVert^2=-\frac1{16}.
\]

Thus \(\operatorname{Re}B_{hh}=-1/32\), while the hard survival-probability
response is \(-1/16\).  Multiplication by the Born coefficient \(3/32\)
produces

\[
 \Delta_{\rm hard}
 =\frac3{32}\left(-\frac1{16}\right)=-\frac3{512},
\]

which cancels the physical \(+3/512\) real response.  This coefficient is not
fitted.  Channel phases and an arbitrary anti-Hermitian addition to \(B\) drop
out of the hard probability.

An exact finite witness is obtained on
\((h,r_{12},r_{13},r_{23})\) by setting

\[
 Ah=\frac{\sqrt3}{12}(r_{12}+r_{13}+r_{23}),\qquad
 Ar_{ij}=-\frac{\sqrt3}{12}h,\qquad
 S_{\rm witness}(x)=e^{xA}.
\]

The producer verifies this over \(\mathbb Q(\sqrt3)\); the independent rail
reconstructs the real column from the source certificates, re-solves both
pseudo-unitarity equations, and derives the hard diagonal without importing
the producer.

The theorem is conditional at exactly one load-bearing point: a regulated
physical Møller/dressed S-matrix must exist on a complete
incoming-plus-outgoing degenerate trace domain and obey pseudo-unitarity
there.  The finite witness proves algebraic compatibility, not that BT
dynamics generates this completion.  Continuum resummation, the trace domain,
incoming degenerate sectors, the finite NLO constant, and beyond-tree
positivity remain `NOT_ESTABLISHED`.  Eq. (19) is a separate problem.

Verification ran sequentially under `ulimit -v 500000` except Git.  Certificate
generation and the 16/16 producer each passed in 0.04 s (20,376 KB and
20,536 KB peak RSS); the independent verifier passed 12/12 in 0.10 s
(30,116 KB), and eight tests with six decisive mutations passed in 0.88 s
(30,212 KB).  Python compilation and JSON parsing passed in 0.18 s
(15,704 KB), the append-only event reproduced FNV-1a
`febd69f7471d24b3`, and `git diff --check` passed uncapped in 0.01 s
(10,876 KB).  Papers V and VI compiled twice; final passes took 0.48 s and
0.51 s with at most 50,968 KB peak RSS.  The prose advisory remains
non-certifying.  Tier 2 was not run because every mathematical predecessor is
unchanged and content-addressed and no shared interface changed.  Tier 3 was
not run because this is neither a freeze nor a release and promotes no
continuum or beyond-tree theorem.
