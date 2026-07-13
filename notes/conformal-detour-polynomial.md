# C2h-L: finite homogeneous-polynomial jet detour certificate

## Result

`symbolic/verify_conformal_detour_polynomial.py` constructs the actual
linear Diff x Weyl, Weyl-curvature, and Bach matrices on finite homogeneous
polynomial spaces over Euclidean `R4`:

\[
(\xi,\sigma)\mathop{\longrightarrow}^{K}h
\mathop{\longrightarrow}^{C_1}C_1[h],
\qquad
B_1[h]=\partial^a\partial^cC^{(1)}_{ab,cd}[h].
\]

The flat Euclidean model is locally conformal to the cylinder and is a useful
Cartesian homogeneous-jet certificate.  It is not identified here with the full
Lorentzian cylinder harmonic or BV complex.

For a homogeneous metric polynomial of degree `n`, the source spaces are

\[
\xi_a\in \operatorname{Sym}^{n+1}(\mathbb R^4)^*\otimes\mathbb R^4,
\qquad
\sigma\in\operatorname{Sym}^{n}(\mathbb R^4)^*,
\]

while `C1[h]` and `B1[h]` have degrees `n-2` and `n-4`.  The executable
uses ten independent electric/magnetic Weyl coordinates and all ten
symmetric Bach coordinates.  Every entry is rational.

The exact rank table is:

| homogeneous degree | dim gauge | dim `h` | dim Weyl coordinates | dim Bach target | rank `K` | rank `C1` | rank `B1` | dim `ker B1 / im K` |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 90 | 100 | 10 | 0 | 90 | 10 | 0 | 10 |
| 3 | 160 | 200 | 40 | 0 | 160 | 40 | 0 | 40 |
| 4 | 259 | 350 | 100 | 10 | 259 | 91 | 9 | 82 |
| 5 | 392 | 560 | 200 | 40 | 392 | 168 | 32 | 136 |
| 6 | 564 | 840 | 350 | 100 | 564 | 276 | 74 | 202 |

At each of these five levels the program checks independently that

\[
C_1K=0,
\qquad
B_1K=0,
\qquad
\ker C_1=\operatorname{im}K.
\]

It follows at these levels that `C1` is injective on

\[
\ker B_1/\operatorname{im}K.
\]

The quotient dimensions `(10,40,82,136,202)` agree exactly with the
parity-complete `E/A/L` character dimensions at compact weights two through
six.  This is a finite dimension match between two independently constructed objects;
it is not promoted to a Lorentzian harmonic intertwiner.

The five observed rows agree with the closed predictions

\[
\begin{aligned}
\operatorname{rank}K_n
 &=4\binom{n+4}{3}+\binom{n+3}{3},\\
\operatorname{rank}C_{1,n}
 &=\frac{(n+2)(n+3)(5n-7)}6,\\
\operatorname{rank}B_{1,n}
 &=\frac{(n-2)(n-3)(5n+7)}6,\\
\dim\frac{\ker B_{1,n}}{\operatorname{im}K_n}
 &=6n^2-14.
\end{aligned}
\]

The executable checks these formulas only for `2 <= n <= 6`.  Their
all-degree proof is the next analytic target; the finite agreement is not
used as such a proof.

## Conformal-Killing zero modes

The reducibility block is kept separate from the homogeneous physical-level
diagnostic.
On

\[
\xi_{\leq2}\oplus\sigma_{\leq1}
\mathop{\longrightarrow}^{K}h_{\leq1},
\]

the matrix has shape `50 x 65` and exact rank `50`.  Its kernel therefore
has dimension fifteen.  The script independently constructs

* four translations;
* six rotations and one dilation; and
* four special conformal transformations,

and verifies that these fifteen vectors are independent, lie in `ker K`,
and exhaust it.  Thus the residual conformal-Killing ghosts can be split
before applying any nonzero-mode local contraction.

## What is and is not certified

The finite calculation establishes actual operator ranks, rather than
deducing exactness from the Weyl-module character.  In particular, the
nine-dimensional rank of `B1` at degree four is an output: it is the
trace-free `(1,1)` equation block removed from the off-shell Weyl image.

The remaining blockers are substantive:

1. **Lorentzian cylinder map.**  No explicit Cartesian-jet-to-normalizable-cylinder
   harmonic intertwiner has been constructed.  The `E/A/L` statement is a
   finite count match, not equality of cohomology representations.
2. **All-level exactness.**  Degrees two through six do not prove the
   detour sequence exact at every homogeneous degree.
3. **Full local BV complex.**  Antifields, antighosts, multipliers, and
   nonminimal doublets are absent.  The calculation is the minimal
   field/gauge/equation symbol complex only.
4. **Pairing and cyclicity.**  The Euclidean rational matrices do not supply
   the Lorentzian action adjoint, the physical Krein pairing, or a cyclic
   strong deformation retract.
5. **Global cylinder reduction.**  Separating `ker K` does not decide whether
   the fifteen conformal transformations are gauged reducibilities or
   retained global charges, nor does it compute residual BRST cohomology.

The executable fails closed if asked to claim either the all-level theorem
or the Lorentzian `E/A/L` identification:

```bash
python3 symbolic/verify_conformal_detour_polynomial.py
python3 symbolic/verify_conformal_detour_polynomial.py --claim-all-levels
python3 symbolic/verify_conformal_detour_polynomial.py --claim-lorentzian-eal
```

The first command passes.  Each of the latter two exits nonzero by design.
